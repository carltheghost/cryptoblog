import random
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import FiatDepositCreate, OrderCreate
from core.database import get_db
from core.models import CefiAccount, CustodyAllocation, FiatDeposit, Order, User

router = APIRouter(prefix="/api/cefi", tags=["cefi"])

DEMO_USER = "traderone"
ORDER_BOOK = {
    "bids": [
        {"price": 68430.12, "amount": 0.4521},
        {"price": 68428.50, "amount": 1.2300},
        {"price": 68425.00, "amount": 0.8900},
        {"price": 68420.75, "amount": 2.1000},
        {"price": 68415.30, "amount": 0.5500},
    ],
    "asks": [
        {"price": 68432.18, "amount": 0.3200},
        {"price": 68435.00, "amount": 0.7800},
        {"price": 68438.50, "amount": 1.4500},
        {"price": 68442.00, "amount": 0.9200},
        {"price": 68448.75, "amount": 1.6700},
    ],
}


async def get_demo_user(session: AsyncSession) -> User:
    result = await session.execute(select(User).where(User.username == DEMO_USER))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Demo user not found")
    return user


@router.get("/account")
async def get_account(session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    result = await session.execute(select(CefiAccount).where(CefiAccount.user_id == user.id))
    account = result.scalar_one()
    return {
        "tess_id": user.tess_id,
        "display_name": user.display_name,
        "mganga_balance": account.mganga_balance,
        "usd_balance": account.usd_balance,
        "kyc_status": account.kyc_status,
        "aml_compliant": account.aml_compliant,
    }


@router.get("/orderbook/{pair}")
async def get_orderbook(pair: str):
    jitter = random.uniform(-5, 5)
    bids = [{**b, "price": round(b["price"] + jitter, 2)} for b in ORDER_BOOK["bids"]]
    asks = [{**a, "price": round(a["price"] + jitter, 2)} for a in ORDER_BOOK["asks"]]
    return {"pair": pair, "bids": bids, "asks": asks, "last_price": 68432.18 + jitter}


@router.get("/ticker")
async def get_ticker():
    return {
        "pairs": [
            {"symbol": "BTC/USDT", "price": 68432.18, "change": 1.92},
            {"symbol": "ETH/USDT", "price": 3456.72, "change": -0.45},
            {"symbol": "TRD/USDT", "price": 0.2457, "change": 3.88},
            {"symbol": "SOL/USDT", "price": 178.34, "change": 2.11},
            {"symbol": "BNB/USDT", "price": 612.50, "change": 0.78},
        ]
    }


@router.get("/chart/{pair}")
async def get_chart(pair: str, interval: str = "1h"):
    base = 68000 if "BTC" in pair else 3400
    candles = []
    for i in range(48):
        o = base + random.uniform(-200, 200)
        c = o + random.uniform(-150, 150)
        h = max(o, c) + random.uniform(0, 80)
        l = min(o, c) - random.uniform(0, 80)
        candles.append({"time": i, "open": o, "high": h, "low": l, "close": c})
    return {"pair": pair, "interval": interval, "candles": candles}


@router.post("/orders")
async def place_order(body: OrderCreate, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    order = Order(
        user_id=user.id,
        pair=body.pair,
        side=body.side,
        order_type=body.order_type,
        price=body.price,
        amount=body.amount,
        status="filled" if body.order_type == "market" else "open",
        filled=body.amount if body.order_type == "market" else 0.0,
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return {"id": order.id, "status": order.status, "message": f"{body.side.upper()} order placed"}


@router.get("/orders")
async def list_orders(session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    result = await session.execute(
        select(Order).where(Order.user_id == user.id).order_by(Order.created_at.desc()).limit(20)
    )
    orders = result.scalars().all()
    return [
        {
            "id": o.id,
            "pair": o.pair,
            "side": o.side,
            "type": o.order_type,
            "price": o.price,
            "amount": o.amount,
            "filled": o.filled,
            "status": o.status,
            "created_at": o.created_at.isoformat(),
        }
        for o in orders
    ]


@router.post("/fiat/deposit")
async def fiat_deposit(body: FiatDepositCreate, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    deposit = FiatDeposit(
        user_id=user.id,
        method=body.method,
        amount=body.amount,
        currency=body.currency,
        status="completed",
    )
    session.add(deposit)
    result = await session.execute(select(CefiAccount).where(CefiAccount.user_id == user.id))
    account = result.scalar_one()
    account.usd_balance += body.amount
    account.mganga_balance += body.amount
    await session.commit()
    return {"id": deposit.id, "status": "completed", "new_balance": account.mganga_balance}


@router.get("/compliance/status")
async def compliance_status(session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    result = await session.execute(select(CefiAccount).where(CefiAccount.user_id == user.id))
    account = result.scalar_one()
    return {
        "kyc_status": account.kyc_status,
        "aml_compliant": account.aml_compliant,
        "tier": user.tier,
        "documents": ["passport", "proof_of_address"],
        "verified_at": datetime.utcnow().isoformat(),
    }


@router.get("/fraud-score")
async def fraud_score(session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    result = await session.execute(select(CefiAccount).where(CefiAccount.user_id == user.id))
    account = result.scalar_one()
    return {
        "score": account.fraud_score,
        "risk_level": "low" if account.fraud_score >= 80 else "medium",
        "factors": [
            {"name": "Transaction Velocity", "score": 95, "status": "good"},
            {"name": "Geographic Consistency", "score": 88, "status": "good"},
            {"name": "Device Fingerprint", "score": 91, "status": "good"},
            {"name": "Behavioral Pattern", "score": 94, "status": "good"},
        ],
        "recommendation": "Low Risk - Good to trade",
    }


@router.get("/custody")
async def custody_vault(session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    result = await session.execute(select(CustodyAllocation).where(CustodyAllocation.user_id == user.id))
    allocations = result.scalars().all()
    total = sum(a.amount for a in allocations)
    return {
        "total_assets": len(allocations),
        "storage_type": "institutional_cold",
        "allocations": [
            {"asset": a.asset, "amount": a.amount, "storage": a.storage_type}
            for a in allocations
        ],
        "security_level": "maximum",
    }


@router.get("/stats")
async def cefi_stats():
    return {
        "volume_24h": 2.45e9,
        "open_interest": 1.12e9,
        "users_online": 23845,
        "uptime": 99.99,
    }
