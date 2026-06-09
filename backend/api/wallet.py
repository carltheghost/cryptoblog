import random
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import AgentPluginsUpdate, BatchTransaction, MultisigSetup, RecoverySetup
from core.database import get_db
from core.models import User, UserPreference

router = APIRouter(prefix="/api/wallet", tags=["wallet"])

DEMO_USER = "traderone"
DEFAULT_PLUGINS = {"pricebot": True, "rebalancer": False}


async def get_demo_user(session: AsyncSession) -> User:
    result = await session.execute(select(User).where(User.username == DEMO_USER))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Demo user not found")
    return user


async def get_prefs(session: AsyncSession, user_id: int) -> UserPreference:
    result = await session.execute(select(UserPreference).where(UserPreference.user_id == user_id))
    prefs = result.scalar_one_or_none()
    if not prefs:
        prefs = UserPreference(user_id=user_id, agent_plugins=DEFAULT_PLUGINS.copy())
        session.add(prefs)
        await session.flush()
    if not prefs.agent_plugins:
        prefs.agent_plugins = DEFAULT_PLUGINS.copy()
    if prefs.recovery_guardians is None:
        prefs.recovery_guardians = []
    if prefs.batch_queue is None:
        prefs.batch_queue = []
    return prefs


@router.get("/config")
async def wallet_config(session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    prefs = await get_prefs(session, user.id)
    return {
        "tess_id": user.tess_id,
        "multisig": {
            "enabled": prefs.multisig_enabled,
            "threshold": prefs.multisig_threshold,
            "keys_required": 3,
        },
        "recovery": {
            "configured": len(prefs.recovery_guardians or []) >= 3,
            "guardians": prefs.recovery_guardians or [],
        },
        "agent_plugins": prefs.agent_plugins or DEFAULT_PLUGINS,
        "batch_queue": prefs.batch_queue or [],
        "privacy": {
            "pseudonym_mode": prefs.anonymous_mode,
            "zk_disclosure": prefs.zk_disclosure,
            "tor_routing": prefs.tor_routing,
        },
    }


@router.post("/multisig")
async def setup_multisig(body: MultisigSetup, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    prefs = await get_prefs(session, user.id)
    if body.threshold < 2 or body.threshold > 5:
        raise HTTPException(400, "Threshold must be between 2 and 5")
    prefs.multisig_enabled = True
    prefs.multisig_threshold = body.threshold
    await session.commit()
    keys = body.device_keys or [f"device-{random.randint(1000, 9999)}" for _ in range(3)]
    return {
        "status": "configured",
        "threshold": f"{body.threshold}-of-3",
        "device_keys": keys,
        "message": "Multisig wallet activated — transactions require multiple signatures",
    }


@router.post("/recovery")
async def setup_recovery(body: RecoverySetup, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    prefs = await get_prefs(session, user.id)
    guardians = body.guardians or [
        "TRD-A1B2-C3D4",
        "TRD-E5F6-G7H8",
        "TRD-I9J0-K1L2",
    ]
    if len(guardians) < 3:
        raise HTTPException(400, "At least 3 guardians required")
    prefs.recovery_guardians = guardians[:5]
    await session.commit()
    return {
        "status": "configured",
        "guardians": prefs.recovery_guardians,
        "message": "Social recovery enabled — guardians can help restore access",
    }


@router.put("/agent-plugins")
async def update_agent_plugins(body: AgentPluginsUpdate, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    prefs = await get_prefs(session, user.id)
    plugins = dict(prefs.agent_plugins or DEFAULT_PLUGINS)
    for field, value in body.model_dump(exclude_none=True).items():
        plugins[field] = value
    prefs.agent_plugins = plugins
    await session.commit()
    return {"agent_plugins": plugins, "status": "saved"}


@router.post("/batch")
async def add_batch_tx(body: BatchTransaction, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    prefs = await get_prefs(session, user.id)
    queue = list(prefs.batch_queue or [])
    entry = {
        "id": len(queue) + 1,
        "action": body.action,
        "amount": body.amount,
        "token": body.token,
        "target": body.target,
        "status": "queued",
        "created_at": datetime.utcnow().isoformat(),
    }
    queue.append(entry)
    prefs.batch_queue = queue[-10:]
    await session.commit()
    return {"queued": entry, "queue_length": len(prefs.batch_queue)}


@router.post("/batch/execute")
async def execute_batch(session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    prefs = await get_prefs(session, user.id)
    queue = list(prefs.batch_queue or [])
    if not queue:
        raise HTTPException(400, "Batch queue is empty")
    executed = []
    for item in queue:
        item["status"] = "executed"
        item["tx_hash"] = f"0x{random.randbytes(8).hex()}"
        executed.append(item)
    prefs.batch_queue = []
    await session.commit()
    return {
        "executed": len(executed),
        "transactions": executed,
        "message": f"Atomic batch of {len(executed)} transactions confirmed",
    }
