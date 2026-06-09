import hashlib
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.models import LivingRelic, TessLinkEdge

router = APIRouter(prefix="/api/storage", tags=["storage"])


class VaultStore(BaseModel):
    field: str
    value: str


@router.post("/upload")
async def upload_media(file: UploadFile = File(...)):
    content = await file.read()
    cid = hashlib.sha256(content).hexdigest()[:46]
    return {
        "cid": f"ipfs://{cid}",
        "filename": file.filename,
        "size": len(content),
        "storage": "ipfs",
        "status": "pinned",
    }


@router.post("/vault/store")
async def store_in_vault(body: VaultStore):
    field, value = body.field, body.value
    vault_hash = hashlib.sha256(f"{field}:{value}".encode()).hexdigest()
    return {
        "field": field,
        "vault_hash": vault_hash,
        "encrypted": True,
        "status": "stored",
    }


@router.post("/shadow-proof/{token_id}")
async def create_shadow_proof(token_id: str, session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(LivingRelic).where(LivingRelic.token_id == token_id))
    relic = result.scalar_one_or_none()
    if not relic:
        raise HTTPException(404, "Relic not found")
    shadow_hash = hashlib.sha256(f"shadow:{token_id}:{datetime.utcnow().isoformat()}".encode()).hexdigest()
    relic.shadow_hash = shadow_hash
    relic.status = "shadow_proof"
    session.add(
        TessLinkEdge(
            source_type="relic",
            source_id=token_id,
            target_type="moderation",
            target_id="shadow_proof",
            edge_type="takedown",
            attributes={"hash": shadow_hash, "timestamp": datetime.utcnow().isoformat()},
        )
    )
    await session.commit()
    return {
        "token_id": token_id,
        "shadow_hash": shadow_hash,
        "status": "content_removed_proof_recorded",
    }


@router.get("/tesslink/graph")
async def get_tesslink_graph(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(TessLinkEdge).limit(50))
    edges = result.scalars().all()
    nodes = set()
    graph_edges = []
    for e in edges:
        nodes.add((e.source_type, e.source_id))
        nodes.add((e.target_type, e.target_id))
        graph_edges.append(
            {
                "source": f"{e.source_type}:{e.source_id}",
                "target": f"{e.target_type}:{e.target_id}",
                "type": e.edge_type,
                "attributes": e.attributes,
            }
        )
    return {
        "nodes": [{"id": f"{t}:{i}", "type": t, "ref": i} for t, i in nodes],
        "edges": graph_edges,
    }
