import random
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.cefi_helpers import PAIR_PRICES, apply_buy, apply_sell, order_notional, pair_price
from api.schemas import EarnStakeRequest, FiatDepositCreate, OrderCreate
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
async def get_orderbook(pair: str, session: AsyncSession = Depends(get_db)):
    base = pair_price(pair)
    jitter = random.uniform(-2, 2)
    open_orders = (await session.execute(
        select(Order).where(Order.pair == pair, Order.status == "open").order_by(Order.price.desc()).limit(20)
    )).scalars().all()
    bid_orders = [{"price": o.price, "amount": o.amount - o.filled} for o in open_orders if o.side == "buy"]
    ask_orders = [{"price": o.price, "amount": o.amount - o.filled} for o in open_orders if o.side == "sell"]
    seed_bids = [{**b, "price": round(b["price"] + jitter, 2)} for b in ORDER_BOOK["bids"]]
    seed_asks = [{**a, "price": round(a["price"] + jitter, 2)} for a in ORDER_BOOK["asks"]]
    bids = (bid_orders + seed_bids)[:8]
    asks = (ask_orders + seed_asks)[:8]
    return {"pair": pair, "bids": bids, "asks": asks, "last_price": round(base + jitter, 4)}


@router.get("/ticker")
async def get_ticker(session: AsyncSession = Depends(get_db)):
    since = datetime.utcnow() - timedelta(hours=24)
    pairs = []
    for symbol, base in PAIR_PRICES.items():
        filled = (await session.execute(
            select(func.count(Order.id)).where(Order.pair == symbol, Order.status == "filled", Order.created_at >= since)
        )).scalar() or 0
        change = round((filled * 0.15) + random.uniform(-1, 2), 2)
        pairs.append({"symbol": symbol, "price": round(base + random.uniform(-base * 0.002, base * 0.002), 4), "change": change})
    return {"pairs": pairs}


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
    account = (await session.execute(select(CefiAccount).where(CefiAccount.user_id == user.id))).scalar_one()
    if body.amount <= 0:
        raise HTTPException(400, "Invalid amount")
    exec_price = body.price if body.order_type == "limit" else pair_price(body.pair)
    if exec_price <= 0:
        raise HTTPException(400, "Invalid price")

    try:
        if body.side == "buy":
            cost = order_notional(body.amount, exec_price)
            if body.order_type == "market":
                apply_buy(account, body.amount, exec_price, True)
                status, filled = "filled", body.amount
            else:
                if account.mganga_balance < cost:
                    raise HTTPException(400, "Insufficient MGANGA for limit buy")
                account.mganga_balance -= cost
                status, filled = "open", 0.0
        else:
            if body.order_type == "market":
                apply_sell(account, body.amount, exec_price)
                status, filled = "filled", body.amount
            else:
                status, filled = "open", 0.0
    except ValueError as e:
        raise HTTPException(400, str(e))

    order = Order(
        user_id=user.id,
        pair=body.pair,
        side=body.side,
        order_type=body.order_type,
        price=exec_price,
        amount=body.amount,
        status=status,
        filled=filled,
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return {
        "id": order.id,
        "status": order.status,
        "filled": order.filled,
        "notional": order_notional(order.amount, exec_price),
        "message": f"{body.side.upper()} {body.order_type} order {'filled' if status == 'filled' else 'placed'}",
    }


@router.post("/orders/{order_id}/cancel")
async def cancel_order(order_id: int, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    account = (await session.execute(select(CefiAccount).where(CefiAccount.user_id == user.id))).scalar_one()
    order = (await session.execute(
        select(Order).where(Order.id == order_id, Order.user_id == user.id)
    )).scalar_one_or_none()
    if not order:
        raise HTTPException(404, "Order not found")
    if order.status != "open":
        raise HTTPException(400, "Only open orders can be cancelled")
    if order.side == "buy":
        refund = order_notional(order.amount - order.filled, order.price)
        account.mganga_balance += refund
    order.status = "cancelled"
    await session.commit()
    return {"id": order.id, "status": "cancelled", "refunded": order.side == "buy"}


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
    fee_rate = 0.025 if body.method == "card" else 0.0
    fee = round(body.amount * fee_rate, 2)
    net = body.amount - fee
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
    account.usd_balance += net
    account.mganga_balance += net
    await session.commit()
    return {"id": deposit.id, "status": "completed", "fee": fee, "credited": net, "new_balance": account.mganga_balance}


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
async def cefi_stats(session: AsyncSession = Depends(get_db)):
    since = datetime.utcnow() - timedelta(hours=24)
    volume = (await session.execute(
        select(func.coalesce(func.sum(Order.amount * Order.price), 0)).where(
            Order.status == "filled", Order.created_at >= since
        )
    )).scalar() or 0
    open_count = (await session.execute(
        select(func.count(Order.id)).where(Order.status == "open")
    )).scalar() or 0
    open_notional = (await session.execute(
        select(func.coalesce(func.sum(Order.amount * Order.price), 0)).where(Order.status == "open")
    )).scalar() or 0
    return {
        "volume_24h": round(float(volume), 2),
        "open_interest": round(float(open_notional), 2),
        "open_orders": open_count,
        "users_online": 23845 + open_count * 12,
        "uptime": 99.99,
    }


@router.get("/earn")
async def cefi_earn(session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    account = (await session.execute(select(CefiAccount).where(CefiAccount.user_id == user.id))).scalar_one()
    return {
        "staked_mganga": round(account.staked_mganga, 2),
        "available_mganga": round(account.mganga_balance, 2),
        "apy": 6.5,
        "rewards_accrued": round(account.earn_rewards, 2),
        "products": [
            {"name": "MGANGA Savings", "apy": 6.5, "min": 100},
            {"name": "CeFi Liquidity Pool", "apy": 8.7, "min": 500},
            {"name": "Institutional Vault", "apy": 4.2, "min": 10000},
        ],
    }


@router.post("/earn/stake")
async def cefi_stake(body: EarnStakeRequest, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    account = (await session.execute(select(CefiAccount).where(CefiAccount.user_id == user.id))).scalar_one()
    if body.amount > account.mganga_balance:
        raise HTTPException(400, "Insufficient balance")
    if body.amount <= 0:
        raise HTTPException(400, "Invalid amount")
    account.mganga_balance -= body.amount
    account.staked_mganga += body.amount
    await session.commit()
    return {
        "staked": body.amount,
        "total_staked": account.staked_mganga,
        "available": account.mganga_balance,
        "apy": 6.5,
        "message": "MGANGA staked in CeFi earn product",
    }


@router.post("/earn/claim")
async def cefi_claim_earn(session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    account = (await session.execute(select(CefiAccount).where(CefiAccount.user_id == user.id))).scalar_one()
    claimed = account.earn_rewards
    if claimed <= 0:
        account.earn_rewards = round(account.staked_mganga * 0.002, 2)
        claimed = account.earn_rewards
    account.mganga_balance += claimed
    account.earn_rewards = 0.0
    await session.commit()
    return {"claimed": claimed, "new_balance": account.mganga_balance}
