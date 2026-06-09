from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.models import (
    BridgeTransaction,
    CasinoBet,
    CasinoWallet,
    CefiAccount,
    DefiPool,
    DefiTransaction,
    DefiWallet,
    MarketListing,
    Order,
    TessLinkEdge,
    User,
)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

DEMO_USER = "traderone"


async def get_demo_user(session: AsyncSession) -> User:
    return (await session.execute(select(User).where(User.username == DEMO_USER))).scalar_one()


@router.get("/overview")
async def analytics_overview(session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    since = datetime.utcnow() - timedelta(hours=24)

    order_count = (await session.execute(
        select(func.count(Order.id)).where(Order.user_id == user.id, Order.created_at >= since)
    )).scalar() or 0

    order_volume = (await session.execute(
        select(func.coalesce(func.sum(Order.amount * Order.price), 0)).where(
            Order.user_id == user.id, Order.status == "filled", Order.created_at >= since
        )
    )).scalar() or 0

    defi_tx_count = (await session.execute(
        select(func.count(DefiTransaction.id)).where(DefiTransaction.user_id == user.id, DefiTransaction.created_at >= since)
    )).scalar() or 0

    bridge_volume = (await session.execute(
        select(func.coalesce(func.sum(BridgeTransaction.amount), 0)).where(
            BridgeTransaction.user_id == user.id, BridgeTransaction.created_at >= since
        )
    )).scalar() or 0

    casino_bets = (await session.execute(
        select(func.count(CasinoBet.id)).where(CasinoBet.user_id == user.id, CasinoBet.created_at >= since)
    )).scalar() or 0

    casino_wagered = (await session.execute(
        select(func.coalesce(func.sum(CasinoBet.bet_amount), 0)).where(
            CasinoBet.user_id == user.id, CasinoBet.created_at >= since
        )
    )).scalar() or 0

    pools = (await session.execute(select(DefiPool))).scalars().all()
    pool_tvl = sum(p.tvl for p in pools)
    pool_volume = sum(p.volume_24h for p in pools)

    listings_sold = (await session.execute(
        select(func.count(MarketListing.id)).where(MarketListing.status == "sold")
    )).scalar() or 0

    edges = (await session.execute(select(func.count(TessLinkEdge.id)))).scalar() or 0

    cefi = (await session.execute(select(CefiAccount).where(CefiAccount.user_id == user.id))).scalar_one()
    defi = (await session.execute(select(DefiWallet).where(DefiWallet.user_id == user.id))).scalar_one()
    casino = (await session.execute(select(CasinoWallet).where(CasinoWallet.user_id == user.id))).scalar_one_or_none()

    return {
        "volume_24h": round(float(order_volume) + float(bridge_volume) + float(casino_wagered), 2),
        "cefi_volume_24h": round(float(order_volume), 2),
        "defi_tx_24h": defi_tx_count,
        "bridge_volume_24h": round(float(bridge_volume), 2),
        "casino_bets_24h": casino_bets,
        "casino_wagered_24h": round(float(casino_wagered), 2),
        "orders_24h": order_count,
        "pool_tvl": round(pool_tvl, 2),
        "pool_volume_24h": round(pool_volume, 2),
        "market_sales": listings_sold,
        "tesslink_edges": edges,
        "balances": {
            "cefi_mganga": cefi.mganga_balance,
            "defi_mwanjesa": defi.mwanjesa_balance,
            "casino_chips": casino.mganga_chips if casino else 0,
            "hyb": defi.hyb_balance,
        },
        "chains": [
            {"name": "CeFi Exchange", "status": "active", "load": min(99, 40 + order_count * 3)},
            {"name": "DeFi Mesh", "status": "active", "load": min(99, 35 + defi_tx_count * 2)},
            {"name": "TribeChain Alpha", "status": "active", "load": min(99, 50 + int(pool_tvl / 1e6))},
            {"name": "Casino RF-SAM", "status": "active", "load": min(99, 30 + casino_bets * 4)},
        ],
    }
