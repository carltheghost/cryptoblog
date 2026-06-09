from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
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


class TicketUpdate(BaseModel):
    status: str | None = None


async def get_demo_user(session: AsyncSession) -> User:
    result = await session.execute(select(User).where(User.username == "traderone"))
    return result.scalar_one()


AUTO_RESPONSES = {
    "withdrawal": "Our compliance team is reviewing your withdrawal. Typical resolution: 2-4 hours.",
    "kyc": "KYC documents received. Verification tier upgrade processing within 24h.",
    "casino": "RF-SAM proofs are verifiable on-chain. Share your bet_id for instant audit.",
    "default": "TessChain support received your ticket. A specialist will respond within 24h. Ticket queued in Hive priority mesh.",
}


def auto_reply(subject: str, message: str) -> str:
    text = f"{subject} {message}".lower()
    for key, reply in AUTO_RESPONSES.items():
        if key != "default" and key in text:
            return reply
    return AUTO_RESPONSES["default"]


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
    await session.flush()
    ticket.response = auto_reply(body.subject, body.message)
    ticket.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(ticket)
    return {
        "id": ticket.id,
        "status": "open",
        "response": ticket.response,
        "message": "Ticket submitted — auto-response generated",
    }


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
            "response": t.response,
            "created_at": t.created_at.isoformat(),
            "updated_at": t.updated_at.isoformat() if t.updated_at else None,
        }
        for t in tickets
    ]


@router.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: int, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    ticket = (await session.execute(
        select(SupportTicket).where(SupportTicket.id == ticket_id, SupportTicket.user_id == user.id)
    )).scalar_one_or_none()
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    return {
        "id": ticket.id,
        "subject": ticket.subject,
        "message": ticket.message,
        "priority": ticket.priority,
        "status": ticket.status,
        "response": ticket.response,
        "created_at": ticket.created_at.isoformat(),
        "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else None,
    }


@router.patch("/tickets/{ticket_id}")
async def update_ticket(ticket_id: int, body: TicketUpdate, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    ticket = (await session.execute(
        select(SupportTicket).where(SupportTicket.id == ticket_id, SupportTicket.user_id == user.id)
    )).scalar_one_or_none()
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    if body.status:
        if body.status not in ("open", "in_progress", "resolved", "closed"):
            raise HTTPException(400, "Invalid status")
        ticket.status = body.status
    ticket.updated_at = datetime.utcnow()
    await session.commit()
    return {"id": ticket.id, "status": ticket.status}
