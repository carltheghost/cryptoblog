from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.models import SupportTicket, User

router = APIRouter(prefix="/api/support", tags=["support"])


class TicketCreate(BaseModel):
    subject: str
    message: str
    priority: str = "normal"


async def get_demo_user(session: AsyncSession) -> User:
    result = await session.execute(select(User).where(User.username == "traderone"))
    return result.scalar_one()


@router.post("/tickets")
async def create_ticket(body: TicketCreate, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    ticket = SupportTicket(
        user_id=user.id,
        subject=body.subject,
        message=body.message,
        priority=body.priority,
    )
    session.add(ticket)
    await session.commit()
    await session.refresh(ticket)
    return {"id": ticket.id, "status": "open", "message": "Ticket submitted — we'll respond within 24h"}


@router.get("/tickets")
async def list_tickets(session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    result = await session.execute(
        select(SupportTicket).where(SupportTicket.user_id == user.id).order_by(SupportTicket.created_at.desc())
    )
    tickets = result.scalars().all()
    return [
        {
            "id": t.id,
            "subject": t.subject,
            "message": t.message,
            "priority": t.priority,
            "status": t.status,
            "created_at": t.created_at.isoformat(),
        }
        for t in tickets
    ]
