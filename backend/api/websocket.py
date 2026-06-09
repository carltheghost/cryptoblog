import asyncio
import json
import random

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

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

    async def broadcast(self, message: dict):
        dead = []
        for ws in self.active:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


manager = ConnectionManager()


@router.websocket("/ws/ticker")
async def ticker_ws(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            data = {
                "type": "ticker",
                "pairs": [
                    {"symbol": "BTC/USDT", "price": round(68432.18 + random.uniform(-50, 50), 2), "change": round(random.uniform(-2, 3), 2)},
                    {"symbol": "ETH/USDT", "price": round(3456.72 + random.uniform(-20, 20), 2), "change": round(random.uniform(-2, 3), 2)},
                    {"symbol": "TRD/USDT", "price": round(0.2457 + random.uniform(-0.01, 0.01), 4), "change": round(random.uniform(-2, 5), 2)},
                    {"symbol": "SOL/USDT", "price": round(178.34 + random.uniform(-5, 5), 2), "change": round(random.uniform(-2, 3), 2)},
                    {"symbol": "BNB/USDT", "price": round(612.50 + random.uniform(-10, 10), 2), "change": round(random.uniform(-2, 3), 2)},
                ],
            }
            await ws.send_json(data)
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        manager.disconnect(ws)


@router.websocket("/ws/orderbook/{pair}")
async def orderbook_ws(ws: WebSocket, pair: str):
    await manager.connect(ws)
    try:
        while True:
            jitter = random.uniform(-3, 3)
            data = {
                "type": "orderbook",
                "pair": pair,
                "bids": [
                    {"price": round(68430.12 + jitter - i, 2), "amount": round(random.uniform(0.1, 2.5), 4)}
                    for i in range(5)
                ],
                "asks": [
                    {"price": round(68432.18 + jitter + i, 2), "amount": round(random.uniform(0.1, 2.5), 4)}
                    for i in range(5)
                ],
            }
            await ws.send_json(data)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(ws)
