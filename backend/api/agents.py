from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import AgentCreate
from core.database import get_db
from core.models import TessAgent

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("/")
async def list_agents(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(TessAgent).order_by(TessAgent.id))
    agents = result.scalars().all()
    return [
        {
            "id": a.id,
            "name": a.name,
            "type": a.agent_type,
            "description": a.description,
            "status": a.status,
            "budget": a.budget,
            "stake": a.stake,
            "permissions": a.permissions,
        }
        for a in agents
    ]


@router.post("/")
async def create_agent(body: AgentCreate, session: AsyncSession = Depends(get_db)):
    agent = TessAgent(
        name=body.name,
        agent_type=body.agent_type,
        description=body.description,
        budget=body.budget,
        stake=body.budget * 0.5,
        permissions={"read_wallet": True, "execute_trades": body.agent_type == "autonomous"},
    )
    session.add(agent)
    await session.commit()
    await session.refresh(agent)
    return {"id": agent.id, "name": agent.name, "status": "active"}


@router.get("/{agent_id}")
async def get_agent(agent_id: int, session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(TessAgent).where(TessAgent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(404, "Agent not found")
    return {
        "id": agent.id,
        "name": agent.name,
        "type": agent.agent_type,
        "description": agent.description,
        "status": agent.status,
        "budget": agent.budget,
        "stake": agent.stake,
        "permissions": agent.permissions,
        "performance": {"tasks_completed": 142, "accuracy": 97.2, "earnings": 45.6},
    }
