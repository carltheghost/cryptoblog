import hashlib
import random
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.models import (
    CasinoBet,
    CasinoWallet,
    CefiAccount,
    DefiTransaction,
    DefiWallet,
    LivingRelic,
    OmniverseState,
    Order,
    ParadoxBranch,
    User,
)

router = APIRouter(prefix="/api/omniverse", tags=["omniverse"])

DEMO_USER = "traderone"


class ParadoxRequest(BaseModel):
    source_dapp: str
    action: str
    amount: float = 0
    branches: int = Field(default=3, ge=2, le=7)


class QuantumCollapse(BaseModel):
    observe: str = Field(..., pattern="^(cefi|defi|casino|hybrid)$")


class OmniExecute(BaseModel):
    actions: list[dict]
    dimension: int = 5


class ResonanceSync(BaseModel):
    target: str = "all"


async def get_demo_user(session: AsyncSession) -> User:
    result = await session.execute(select(User).where(User.username == DEMO_USER))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Demo user not found")
    return user


async def get_omniverse(session: AsyncSession, user_id: int) -> OmniverseState:
    result = await session.execute(select(OmniverseState).where(OmniverseState.user_id == user_id))
    state = result.scalar_one_or_none()
    if not state:
        state = OmniverseState(user_id=user_id)
        session.add(state)
        await session.flush()
    return state


@router.get("/status")
async def omniverse_status(session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    state = await get_omniverse(session, user.id)
    return {
        "tess_id": user.tess_id,
        "dimension": state.dimension,
        "overdrive": state.overdrive_active,
        "quantum_locked": state.quantum_superposition,
        "paradox_count": state.paradox_count,
        "hive_sync": state.hive_sync_percent,
        "soul_resonance": state.soul_resonance,
        "chrono_depth": state.chrono_depth,
        "omega_tier": state.omega_tier,
        "reality_stability": round(100 - state.paradox_count * 2.5, 1),
        "impossibility_index": round(state.hive_sync_percent * 0.4 + state.soul_resonance * 0.3 + state.dimension * 8, 1),
        "tagline": "Beyond human standard · Unreachable tier",
    }


@router.post("/overdrive")
async def activate_overdrive(session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    state = await get_omniverse(session, user.id)
    state.overdrive_active = not state.overdrive_active
    state.dimension = 5 if state.overdrive_active else min(state.dimension, 4)
    state.hive_sync_percent = min(99.9, state.hive_sync_percent + 12)
    await session.commit()
    return {
        "overdrive": state.overdrive_active,
        "dimension": state.dimension,
        "message": "TESS OVERDRIVE ENGAGED — reality constraints dissolved" if state.overdrive_active else "Overdrive disengaged",
    }


@router.post("/dimension")
async def shift_dimension(body: dict, session: AsyncSession = Depends(get_db)):
    dim = int(body.get("dimension", 3))
    if dim not in (1, 2, 3, 4, 5, 99):
        raise HTTPException(400, "Dimension must be 1-5 or 99 (infinite)")
    user = await get_demo_user(session)
    state = await get_omniverse(session, user.id)
    state.dimension = dim
    if dim >= 5:
        state.overdrive_active = True
    await session.commit()
    labels = {1: "Linear", 2: "Planar", 3: "Spatial", 4: "Temporal", 5: "Hyper", 99: "Infinite ∞"}
    return {"dimension": dim, "label": labels.get(dim, "Unknown"), "overdrive": state.overdrive_active}


@router.post("/paradox/branch")
async def create_paradox(body: ParadoxRequest, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    state = await get_omniverse(session, user.id)
    branches = []
    for i in range(body.branches):
        outcome_roll = random.uniform(-body.amount * 0.5, body.amount * 2.5)
        branches.append({
            "branch_id": f"PX-{secrets.token_hex(4).upper()}",
            "timeline": chr(65 + i),
            "probability": round(100 / body.branches + random.uniform(-5, 5), 1),
            "outcome": round(outcome_roll, 2),
            "status": "superposed" if i > 0 else "primary",
        })
    primary = branches[0]
    record = ParadoxBranch(
        user_id=user.id,
        source_dapp=body.source_dapp,
        action=body.action,
        amount=body.amount,
        branches_json=branches,
        collapsed_branch=primary["branch_id"],
    )
    session.add(record)
    state.paradox_count += 1
    state.soul_resonance = min(100, state.soul_resonance + 3)
    await session.commit()
    await session.refresh(record)
    return {
        "paradox_id": record.id,
        "branches": branches,
        "collapsed": primary,
        "message": f"{body.branches} parallel realities spawned — only one collapses on observation",
        "proof_hash": hashlib.sha256(str(branches).encode()).hexdigest()[:16],
    }


@router.get("/chrono/timeline")
async def chrono_timeline(session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    events = []

    orders = (await session.execute(select(Order).where(Order.user_id == user.id).order_by(Order.created_at.desc()).limit(8))).scalars().all()
    for o in orders:
        events.append({"t": o.created_at.isoformat(), "dapp": "cefi", "type": "trade", "label": f"{o.side.upper()} {o.pair}", "amount": o.amount, "rewindable": True})

    txs = (await session.execute(select(DefiTransaction).where(DefiTransaction.user_id == user.id).order_by(DefiTransaction.created_at.desc()).limit(8))).scalars().all()
    for tx in txs:
        events.append({"t": tx.created_at.isoformat(), "dapp": "defi", "type": tx.tx_type, "label": f"{tx.tx_type} {tx.from_token or ''}", "amount": tx.amount, "rewindable": True})

    bets = (await session.execute(select(CasinoBet).where(CasinoBet.user_id == user.id).order_by(CasinoBet.created_at.desc()).limit(8))).scalars().all()
    for b in bets:
        events.append({"t": b.created_at.isoformat(), "dapp": "casino", "type": "bet", "label": f"{b.game} {'WIN' if b.won else 'LOSS'}", "amount": b.bet_amount, "rewindable": b.won})

    paradoxes = (await session.execute(select(ParadoxBranch).where(ParadoxBranch.user_id == user.id).order_by(ParadoxBranch.created_at.desc()).limit(5))).scalars().all()
    for p in paradoxes:
        events.append({"t": p.created_at.isoformat(), "dapp": "omniverse", "type": "paradox", "label": f"Branch {p.source_dapp}/{p.action}", "amount": p.amount, "rewindable": False})

    events.sort(key=lambda e: e["t"], reverse=True)
    return {"events": events[:20], "depth": len(events), "can_rewind": sum(1 for e in events if e["rewindable"])}


@router.post("/chrono/rewind")
async def chrono_rewind(body: dict, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    state = await get_omniverse(session, user.id)
    state.chrono_depth += 1
    state.paradox_count = max(0, state.paradox_count - 1)
    await session.commit()
    return {
        "rewound": True,
        "chrono_depth": state.chrono_depth,
        "message": "Timeline branch rewound — causality re-stitched via TessChrono",
        "stability_restored": round(random.uniform(2, 8), 1),
    }


@router.get("/quantum/superposition")
async def quantum_state(session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    state = await get_omniverse(session, user.id)
    cefi = (await session.execute(select(CefiAccount).where(CefiAccount.user_id == user.id))).scalar_one()
    defi = (await session.execute(select(DefiWallet).where(DefiWallet.user_id == user.id))).scalar_one()
    casino = (await session.execute(select(CasinoWallet).where(CasinoWallet.user_id == user.id))).scalar_one_or_none()
    chip = casino.mganga_chips if casino else 0

    spread = random.uniform(0.02, 0.08)
    return {
        "superposed": state.quantum_superposition,
        "states": [
            {"realm": "cefi", "value": cefi.mganga_balance, "alt_low": round(cefi.mganga_balance * (1 - spread), 2), "alt_high": round(cefi.mganga_balance * (1 + spread), 2), "probability": 33.3},
            {"realm": "defi", "value": defi.mwanjesa_balance, "alt_low": round(defi.mwanjesa_balance * (1 - spread), 2), "alt_high": round(defi.mwanjesa_balance * (1 + spread), 2), "probability": 33.3},
            {"realm": "casino", "value": chip, "alt_low": round(chip * (1 - spread), 2), "alt_high": round(chip * (1 + spread), 2), "probability": 33.4},
        ],
        "observation_pending": state.quantum_superposition,
        "collapse_cost_hyb": 0.001,
    }


@router.post("/quantum/collapse")
async def quantum_collapse(body: QuantumCollapse, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    state = await get_omniverse(session, user.id)
    state.quantum_superposition = False
    jitter = random.uniform(-0.03, 0.05)
    state.soul_resonance = min(100, state.soul_resonance + 5)
    await session.commit()
    return {
        "observed": body.observe,
        "collapsed": True,
        "wave_function": "collapsed",
        "jitter_applied": round(jitter * 100, 2),
        "message": f"Quantum state collapsed to {body.observe} realm — all other probabilities annihilated",
    }


@router.post("/quantum/entangle")
async def quantum_entangle(session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    state = await get_omniverse(session, user.id)
    state.quantum_superposition = True
    await session.commit()
    return {"entangled": True, "realms": ["cefi", "defi", "casino", "hybrid"], "message": "All balances now exist in superposition until observed"}


@router.get("/hive/mind")
async def hive_mind(session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    state = await get_omniverse(session, user.id)
    return {
        "sync_percent": state.hive_sync_percent,
        "nodes_online": random.randint(12847, 23845),
        "collective_intelligence": round(state.hive_sync_percent * 1.12, 1),
        "consensus_latency_ms": round(random.uniform(0.3, 1.2), 2),
        "shared_predictions": [
            {"asset": "BTC", "direction": "up", "confidence": 87.2},
            {"asset": "TRD", "direction": "up", "confidence": 94.1},
            {"asset": "ETH", "direction": "neutral", "confidence": 62.5},
        ],
        "your_contribution": round(state.soul_resonance * 0.1, 1),
        "tagline": "Human minds linked — decisions amplified beyond individual capacity",
    }


@router.post("/resonance/sync")
async def soul_resonance(body: ResonanceSync, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    state = await get_omniverse(session, user.id)
    relics = (await session.execute(select(LivingRelic).where(LivingRelic.owner_id == user.id))).scalars().all()
    soul_total = sum(r.soul_reserve for r in relics)
    state.soul_resonance = min(100, state.soul_resonance + len(relics) * 2 + 5)
    state.hive_sync_percent = min(99.9, state.hive_sync_percent + 4)
    await session.commit()
    return {
        "resonance": state.soul_resonance,
        "relics_synced": len(relics),
        "soul_energy": soul_total,
        "target": body.target,
        "message": "Soul resonance propagated across wallet · casino · relics · agents",
    }


@router.post("/omni/execute")
async def omni_execute(body: OmniExecute, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    state = await get_omniverse(session, user.id)
    results = []
    for action in body.actions[:5]:
        results.append({
            "dapp": action.get("dapp", "unknown"),
            "action": action.get("action", "pulse"),
            "status": "executed",
            "tx": f"0x{secrets.token_hex(16)}",
            "dimension": body.dimension,
        })
    state.paradox_count += 1
    state.hive_sync_percent = min(99.9, state.hive_sync_percent + 2)
    await session.commit()
    return {
        "atomic": True,
        "actions_executed": len(results),
        "results": results,
        "dimension": body.dimension,
        "message": f"Omni-executor fired {len(results)} cross-DApp actions in dimension-{body.dimension} singularity",
    }


@router.get("/omega/proof")
async def omega_proof(session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    state = await get_omniverse(session, user.id)
    payload = f"{user.tess_id}:{state.paradox_count}:{state.dimension}:{datetime.utcnow().isoformat()}"
    digest = hashlib.sha3_256(payload.encode()).hexdigest()
    return {
        "tier": state.omega_tier,
        "algorithm": "RF-SAM-Ω (SHA3-256 + TessSoul binding)",
        "digest": digest,
        "attestations": [
            "RF-SAM v1 casino proofs",
            "Paradox branch hashes",
            "Chrono-ledger merkle root",
            "Quantum collapse receipts",
            "Hive consensus signature",
        ],
        "unreachable": True,
        "human_standard_exceeded_by": f"{round(state.hive_sync_percent * 0.4 + state.soul_resonance * 0.3 + state.dimension * 8, 1)}x",
    }
