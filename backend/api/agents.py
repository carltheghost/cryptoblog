import random
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import AgentCreate
from core.database import get_db
from core.models import CefiAccount, DefiWallet, LivingRelic, Order, TessAgent, User

router = APIRouter(prefix="/api/agents", tags=["agents"])

DEMO_USER = "traderone"


async def get_demo_user(session: AsyncSession) -> User:
    result = await session.execute(select(User).where(User.username == DEMO_USER))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Demo user not found")
    return user


def agent_list_item(a: TessAgent) -> dict:
    return {
        "id": a.id,
        "name": a.name,
        "type": a.agent_type,
        "description": a.description,
        "status": a.status,
        "budget": a.budget,
        "stake": a.stake,
        "permissions": a.permissions,
        "tasks_completed": a.tasks_completed,
        "accuracy": a.accuracy,
        "earnings": a.earnings,
    }


@router.get("/")
async def list_agents(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(TessAgent).order_by(TessAgent.id))
    return [agent_list_item(a) for a in result.scalars().all()]


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
        **agent_list_item(agent),
        "performance": {
            "tasks_completed": agent.tasks_completed,
            "accuracy": round(agent.accuracy, 1),
            "earnings": round(agent.earnings, 2),
            "last_run_at": agent.last_run_at.isoformat() if agent.last_run_at else None,
        },
    }


@router.post("/{agent_id}/execute")
async def execute_agent(agent_id: int, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    agent = (await session.execute(select(TessAgent).where(TessAgent.id == agent_id))).scalar_one_or_none()
    if not agent:
        raise HTTPException(404, "Agent not found")
    if agent.status != "active":
        raise HTTPException(400, "Agent is not active")

    result_detail = ""
    earning = 0.0

    if agent.agent_type == "autonomous":
        cefi = (await session.execute(select(CefiAccount).where(CefiAccount.user_id == user.id))).scalar_one()
        micro = min(0.01, cefi.mganga_balance * 0.0001, agent.budget * 0.01)
        if micro > 0 and cefi.mganga_balance >= micro * 0.2457:
            order = Order(
                user_id=user.id, pair="TRD/USDT", side="buy", order_type="limit",
                price=0.2457, amount=micro, status="open", filled=0.0,
            )
            lock = micro * 0.2457
            cefi.mganga_balance -= lock
            session.add(order)
            result_detail = f"Placed micro-order {micro:.6f} TRD @ 0.2457"
            earning = round(micro * 0.1, 4)
        else:
            result_detail = "Insufficient balance for autonomous trade"

    elif agent.agent_type == "administrative":
        pending = (await session.execute(
            select(LivingRelic).where(LivingRelic.owner_id == user.id, LivingRelic.status == "pending")
        )).scalars().all()
        validated = 0
        for relic in pending[:1]:
            relic.status = "minted"
            validated += 1
        result_detail = f"Validated {validated} pending relic(s)" if validated else "No pending relics to validate"
        earning = validated * 2.5

    else:
        defi = (await session.execute(select(DefiWallet).where(DefiWallet.user_id == user.id))).scalar_one()
        defi.staking_rewards += round(agent.budget * 0.001, 4)
        result_detail = "Accrued staking reward scan"
        earning = round(agent.budget * 0.001, 4)

    agent.tasks_completed += 1
    agent.accuracy = min(99.9, agent.accuracy + random.uniform(-0.5, 0.8))
    agent.earnings += earning
    agent.last_run_at = datetime.utcnow()
    await session.commit()

    return {
        "agent_id": agent.id,
        "action": agent.agent_type,
        "detail": result_detail,
        "earning": earning,
        "tasks_completed": agent.tasks_completed,
        "message": f"{agent.name} executed successfully",
    }
