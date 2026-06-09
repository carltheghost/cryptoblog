import asyncio
import random

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import func, select

from api.cefi_helpers import PAIR_PRICES, pair_price
from core.database import async_session
from core.models import Order

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)


manager = ConnectionManager()


async def build_ticker():
    async with async_session() as session:
        pairs = []
        for symbol, base in PAIR_PRICES.items():
            filled = (await session.execute(
                select(func.count(Order.id)).where(Order.pair == symbol, Order.status == "filled")
            )).scalar() or 0
            jitter = random.uniform(-base * 0.002, base * 0.002)
            pairs.append({
                "symbol": symbol,
                "price": round(base + jitter, 4),
                "change": round((filled * 0.1) + random.uniform(-1, 2), 2),
            })
        return {"type": "ticker", "pairs": pairs}


async def build_orderbook(pair: str):
    async with async_session() as session:
        base = pair_price(pair)
        jitter = random.uniform(-2, 2)
        open_orders = (await session.execute(
            select(Order).where(Order.pair == pair, Order.status == "open").order_by(Order.price.desc()).limit(10)
        )).scalars().all()
        bids = [{"price": o.price, "amount": round(o.amount - o.filled, 6)} for o in open_orders if o.side == "buy"]
        asks = [{"price": o.price, "amount": round(o.amount - o.filled, 6)} for o in open_orders if o.side == "sell"]
        if not bids:
            bids = [{"price": round(base + jitter - i, 2), "amount": round(random.uniform(0.1, 2.5), 4)} for i in range(5)]
        if not asks:
            asks = [{"price": round(base + jitter + i, 2), "amount": round(random.uniform(0.1, 2.5), 4)} for i in range(5)]
        return {"type": "orderbook", "pair": pair, "bids": bids[:8], "asks": asks[:8]}


@router.websocket("/ws/ticker")
async def ticker_ws(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.send_json(await build_ticker())
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        manager.disconnect(ws)


@router.websocket("/ws/orderbook/{pair}")
async def orderbook_ws(ws: WebSocket, pair: str):
    await manager.connect(ws)
    try:
        while True:
            await ws.send_json(await build_orderbook(pair))
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(ws)
