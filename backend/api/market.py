import hashlib
import random
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import MarketListingCreate
from core.database import get_db
from core.models import BarterOffer, CefiAccount, DefiWallet, LivingRelic, MarketListing, User

router = APIRouter(prefix="/api/market", tags=["market"])


class BarterCreate(BaseModel):
    offer_assets: list[str]
    request_assets: list[str]


async def get_demo_user(session: AsyncSession) -> User:
    result = await session.execute(select(User).where(User.username == "traderone"))
    return result.scalar_one()


@router.get("/listings")
async def get_listings(session: AsyncSession = Depends(get_db)):
    result = await session.execute(
        select(MarketListing).where(MarketListing.status == "active").order_by(MarketListing.id.desc())
    )
    return [
        {
            "id": l.id, "title": l.title, "description": l.description, "price": l.price,
            "currency": l.currency, "type": l.listing_type, "image_url": l.image_url,
        }
        for l in result.scalars().all()
    ]


@router.post("/listings")
async def create_listing(body: MarketListingCreate, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    listing = MarketListing(
        seller_id=user.id, title=body.title, description=body.description,
        price=body.price, currency=body.currency, listing_type=body.listing_type,
        image_url=f"https://api.dicebear.com/7.x/shapes/svg?seed={body.title}",
    )
    session.add(listing)
    await session.commit()
    await session.refresh(listing)
    return {"id": listing.id, "status": "active"}


@router.post("/purchase/{listing_id}")
async def purchase_listing(listing_id: int, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    listing = (await session.execute(select(MarketListing).where(MarketListing.id == listing_id))).scalar_one_or_none()
    if not listing:
        raise HTTPException(404, "Listing not found")
    if listing.status != "active":
        raise HTTPException(400, "Listing already sold")

    currency = listing.currency.upper()
    if currency == "MGANGA":
        cefi = (await session.execute(select(CefiAccount).where(CefiAccount.user_id == user.id))).scalar_one()
        if cefi.mganga_balance < listing.price:
            raise HTTPException(400, "Insufficient MGANGA balance")
        cefi.mganga_balance -= listing.price
    else:
        defi = (await session.execute(select(DefiWallet).where(DefiWallet.user_id == user.id))).scalar_one()
        if defi.mwanjesa_balance < listing.price:
            raise HTTPException(400, "Insufficient MWANJESA balance")
        defi.mwanjesa_balance -= listing.price

    receipt_hash = hashlib.sha256(f"{listing_id}-{datetime.utcnow().isoformat()}".encode()).hexdigest()
    relic = LivingRelic(
        token_id=f"RCPT-{listing_id}-{random.randint(1000, 9999)}",
        owner_id=user.id,
        name=f"Receipt: {listing.title}",
        description="Blockchain-certified purchase receipt",
        image_url=f"https://api.dicebear.com/7.x/identicon/svg?seed=receipt{listing_id}",
        relic_type="receipt", status="minted", soul_reserve=0.0,
        metadata_json={"receipt_hash": receipt_hash, "listing_id": listing_id, "price": listing.price},
    )
    session.add(relic)
    listing.status = "sold"
    await session.commit()
    return {"listing_id": listing_id, "receipt_hash": receipt_hash, "relic_token_id": relic.token_id, "status": "completed"}




@router.post("/barter")
async def barter_swap(body: BarterCreate, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    offer = BarterOffer(
        user_id=user.id,
        offer_assets={"assets": body.offer_assets},
        request_assets={"assets": body.request_assets},
    )
    session.add(offer)
    await session.commit()
    await session.refresh(offer)
    return {
        "id": offer.id, "status": "pending",
        "offer": body.offer_assets, "request": body.request_assets,
        "message": "Barter swap created — awaiting counterparty",
    }


@router.get("/barter")
async def list_barters(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(BarterOffer).order_by(BarterOffer.created_at.desc()).limit(20))
    return [
        {
            "id": b.id, "offer": b.offer_assets, "request": b.request_assets,
            "status": b.status, "created_at": b.created_at.isoformat(),
        }
        for b in result.scalars().all()
    ]
