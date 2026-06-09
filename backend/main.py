from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import agents, cefi, defi, identity, market, storage, websocket
from core.config import settings
from core.database import async_session, init_db
from core.seed import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    async with async_session() as session:
        await seed_database(session)
    yield


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

origins = [o.strip() for o in settings.cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cefi.router)
app.include_router(defi.router)
app.include_router(identity.router)
app.include_router(market.router)
app.include_router(agents.router)
app.include_router(storage.router)
app.include_router(websocket.router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "platform": "TessChain", "version": settings.app_version}
