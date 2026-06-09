import hashlib
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import MarketListingCreate
from core.database import get_db
from core.models import LivingRelic, MarketListing, User

router = APIRouter(prefix="/api/market", tags=["market"])


@router.get("/listings")
async def get_listings(session: AsyncSession = Depends(get_db)):
    result = await session.execute(
        select(MarketListing).where(MarketListing.status == "active").order_by(MarketListing.id.desc())
    )
    listings = result.scalars().all()
    return [
        {
            "id": l.id,
            "title": l.title,
            "description": l.description,
            "price": l.price,
            "currency": l.currency,
            "type": l.listing_type,
            "image_url": l.image_url,
        }
        for l in listings
    ]


@router.post("/listings")
async def create_listing(body: MarketListingCreate, session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(User).where(User.username == "traderone"))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")
    listing = MarketListing(
        seller_id=user.id,
        title=body.title,
        description=body.description,
        price=body.price,
        currency=body.currency,
        listing_type=body.listing_type,
    )
    session.add(listing)
    await session.commit()
    await session.refresh(listing)
    return {"id": listing.id, "status": "active"}


@router.post("/purchase/{listing_id}")
async def purchase_listing(listing_id: int, session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(MarketListing).where(MarketListing.id == listing_id))
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(404, "Listing not found")
    receipt_hash = hashlib.sha256(f"{listing_id}-{datetime.utcnow().isoformat()}".encode()).hexdigest()
    relic = LivingRelic(
        token_id=f"RCPT-{listing_id}",
        owner_id=listing.seller_id,
        name=f"Receipt: {listing.title}",
        description=f"Blockchain-certified purchase receipt",
        image_url="https://api.dicebear.com/7.x/identicon/svg?seed=receipt",
        relic_type="receipt",
        status="minted",
        soul_reserve=0.0,
        metadata_json={"receipt_hash": receipt_hash, "listing_id": listing_id},
    )
    session.add(relic)
    listing.status = "sold"
    await session.commit()
    return {
        "listing_id": listing_id,
        "receipt_hash": receipt_hash,
        "relic_token_id": relic.token_id,
        "status": "completed",
    }


@router.post("/barter")
async def barter_swap(
    offer_assets: list[str],
    request_assets: list[str],
    session: AsyncSession = Depends(get_db),
):
    return {
        "status": "pending",
        "offer": offer_assets,
        "request": request_assets,
        "message": "Barter swap created — awaiting counterparty",
    }
