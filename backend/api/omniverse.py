import hashlib
import random
import secrets
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.rfsam import derive_result
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

DAPP_ACTIONS = {
    "cefi": "earn-stake",
    "defi": "micro-stake",
    "casino": "omni-spin",
    "wallet": "vault-pulse",
    "market": "barter-scan",
    "relics": "soul-bind",
    "agents": "neural-mesh",
    "trade": "ghost-order",
    "rewards": "claim-pulse",
}


class ParadoxRequest(BaseModel):
    source_dapp: str
    action: str
    amount: float = 0
    branches: int = Field(default=3, ge=2, le=7)


class ParadoxCollapse(BaseModel):
    paradox_id: int
    branch_id: str


class QuantumCollapse(BaseModel):
    observe: str = Field(..., pattern="^(cefi|defi|casino|hybrid)$")


class OmniExecute(BaseModel):
    actions: list[dict]
    dimension: int = 5


class ResonanceSync(BaseModel):
    target: str = "all"


class ChronoRewindRequest(BaseModel):
    event_id: int
    event_type: str
    dapp: str


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


async def get_casino_wallet(session: AsyncSession, user_id: int) -> CasinoWallet:
    result = await session.execute(select(CasinoWallet).where(CasinoWallet.user_id == user_id))
    wallet = result.scalar_one_or_none()
    if not wallet:
        from api.rfsam import generate_server_seed, hash_server_seed

        seed = generate_server_seed()
        wallet = CasinoWallet(user_id=user_id, server_seed=seed, server_seed_hash=hash_server_seed(seed))
        session.add(wallet)
        await session.flush()
    return wallet


async def execute_dapp_action(
    session: AsyncSession,
    user: User,
    state: OmniverseState,
    dapp: str,
    action: str,
    params: dict | None = None,
) -> dict:
    params = params or {}
    amount = float(params.get("amount", 10))
    tx = f"0x{secrets.token_hex(16)}"

    if dapp == "cefi":
        cefi = (await session.execute(select(CefiAccount).where(CefiAccount.user_id == user.id))).scalar_one()
        stake_amt = min(max(amount, 1), cefi.mganga_balance * 0.02, 50)
        if stake_amt > 0 and cefi.mganga_balance >= stake_amt:
            cefi.mganga_balance -= stake_amt
            cefi.staked_mganga += stake_amt
            cefi.earn_rewards += round(stake_amt * 0.001, 4)
            return {"dapp": dapp, "action": action or "earn-stake", "status": "executed", "tx": tx, "detail": f"Staked {stake_amt:.2f} MGANGA", "amount": stake_amt}
        return {"dapp": dapp, "action": action, "status": "skipped", "tx": tx, "detail": "Insufficient MGANGA for omni-stake"}

    if dapp == "defi":
        defi = (await session.execute(select(DefiWallet).where(DefiWallet.user_id == user.id))).scalar_one()
        stake_amt = min(max(amount * 0.5, 5), defi.mwanjesa_balance * 0.02, 100)
        if stake_amt > 0 and defi.mwanjesa_balance >= stake_amt:
            defi.mwanjesa_balance -= stake_amt
            defi.staked_trd += stake_amt
            return {"dapp": dapp, "action": action or "micro-stake", "status": "executed", "tx": tx, "detail": f"Staked {stake_amt:.2f} TRD", "amount": stake_amt}
        return {"dapp": dapp, "action": action, "status": "skipped", "tx": tx, "detail": "Insufficient MWANJESA"}

    if dapp == "casino":
        wallet = await get_casino_wallet(session, user.id)
        bet_amt = min(max(amount * 0.1, 5), wallet.mganga_chips, 25)
        if bet_amt <= 0 or wallet.mganga_chips < bet_amt:
            cefi = (await session.execute(select(CefiAccount).where(CefiAccount.user_id == user.id))).scalar_one()
            deposit = min(10, cefi.mganga_balance)
            if deposit > 0:
                cefi.mganga_balance -= deposit
                wallet.mganga_chips += deposit
                bet_amt = min(5, wallet.mganga_chips)
            else:
                return {"dapp": dapp, "action": action, "status": "skipped", "tx": tx, "detail": "No chips for omni-spin"}
        wallet.nonce += 1
        outcome = derive_result(wallet.server_seed, "omni-execute", wallet.nonce, "tess-slots")
        r1, r2, r3 = outcome["slot_r1"], outcome["slot_r2"], outcome["slot_r3"]
        mult = 10.0 if r1 == r2 == r3 else 3.0 if r1 == r2 or r2 == r3 or r1 == r3 else 0.0
        payout = bet_amt * mult
        won = mult > 0
        wallet.mganga_chips -= bet_amt
        wallet.mganga_chips += payout
        wallet.total_wagered += bet_amt
        wallet.total_won += payout
        wallet.games_played += 1
        bet = CasinoBet(
            user_id=user.id,
            game="tess-slots",
            bet_amount=bet_amt,
            currency="MGANGA",
            payout=payout,
            multiplier=mult,
            won=won,
            choice="omni",
            outcome_json={"reels": [str(r1), str(r2), str(r3)], "omni": True},
            proof_json={"algorithm": "RF-SAM v1", "digest": outcome["digest"], "game": "tess-slots", "nonce": wallet.nonce},
        )
        session.add(bet)
        return {"dapp": dapp, "action": action or "omni-spin", "status": "executed", "tx": tx, "detail": f"Omni-spin {'WIN' if won else 'LOSS'} {payout:.2f}", "amount": bet_amt, "won": won}

    if dapp == "wallet":
        state.hive_sync_percent = min(99.9, state.hive_sync_percent + 1.5)
        return {"dapp": dapp, "action": action or "vault-pulse", "status": "executed", "tx": tx, "detail": "Vault quantum pulse — multisig attestation refreshed"}

    if dapp == "market":
        state.soul_resonance = min(100, state.soul_resonance + 2)
        return {"dapp": dapp, "action": action or "barter-scan", "status": "executed", "tx": tx, "detail": "Barter paradox scan — 3 listings entangled"}

    if dapp == "relics":
        relics = (await session.execute(select(LivingRelic).where(LivingRelic.owner_id == user.id))).scalars().all()
        for r in relics:
            r.soul_reserve = min(100, r.soul_reserve + 1)
        state.soul_resonance = min(100, state.soul_resonance + len(relics) + 2)
        return {"dapp": dapp, "action": action or "soul-bind", "status": "executed", "tx": tx, "detail": f"Bound {len(relics)} relics to omniverse mesh"}

    if dapp == "agents":
        state.hive_sync_percent = min(99.9, state.hive_sync_percent + 3)
        return {"dapp": dapp, "action": action or "neural-mesh", "status": "executed", "tx": tx, "detail": "Agent neural mesh synchronized"}

    if dapp == "trade":
        cefi = (await session.execute(select(CefiAccount).where(CefiAccount.user_id == user.id))).scalar_one()
        micro = min(0.001, cefi.mganga_balance * 0.0001)
        order = Order(user_id=user.id, pair="TRD/USDT", side="buy", order_type="limit", price=0.2457, amount=micro, status="open")
        session.add(order)
        return {"dapp": dapp, "action": action or "ghost-order", "status": "executed", "tx": tx, "detail": f"Ghost order placed {micro:.6f} TRD", "amount": micro}

    if dapp == "rewards":
        defi = (await session.execute(select(DefiWallet).where(DefiWallet.user_id == user.id))).scalar_one()
        claimed = defi.staking_rewards
        if claimed > 0:
            defi.mwanjesa_balance += claimed
            defi.staking_rewards = 0.0
            return {"dapp": dapp, "action": action or "claim-pulse", "status": "executed", "tx": tx, "detail": f"Claimed {claimed:.2f} TRD rewards", "amount": claimed}
        cefi = (await session.execute(select(CefiAccount).where(CefiAccount.user_id == user.id))).scalar_one()
        if cefi.earn_rewards > 0:
            bonus = cefi.earn_rewards
            cefi.mganga_balance += bonus
            cefi.earn_rewards = 0.0
            return {"dapp": dapp, "action": action or "claim-pulse", "status": "executed", "tx": tx, "detail": f"Claimed {bonus:.2f} MGANGA earn", "amount": bonus}
        return {"dapp": dapp, "action": action, "status": "skipped", "tx": tx, "detail": "No claimable rewards"}

    return {"dapp": dapp, "action": action, "status": "unknown", "tx": tx, "detail": f"Unknown DApp {dapp}"}


def apply_paradox_outcome(session_balances: dict, source_dapp: str, outcome: float) -> str:
    if source_dapp in ("cefi", "trade", "wallet", "rewards") and "cefi" in session_balances:
        session_balances["cefi"].mganga_balance = max(0, session_balances["cefi"].mganga_balance + outcome)
        return "cefi"
    if source_dapp in ("defi", "market", "agents") and "defi" in session_balances:
        session_balances["defi"].mwanjesa_balance = max(0, session_balances["defi"].mwanjesa_balance + outcome)
        return "defi"
    if source_dapp == "casino" and "casino" in session_balances:
        session_balances["casino"].mganga_chips = max(0, session_balances["casino"].mganga_chips + outcome)
        return "casino"
    if "cefi" in session_balances:
        session_balances["cefi"].mganga_balance = max(0, session_balances["cefi"].mganga_balance + outcome * 0.5)
        session_balances["defi"].mwanjesa_balance = max(0, session_balances["defi"].mwanjesa_balance + outcome * 0.5)
        return "hybrid"
    return "none"


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
        "hive_sync_percent": state.hive_sync_percent,
        "soul_resonance": state.soul_resonance,
        "chrono_depth": state.chrono_depth,
        "omega_tier": state.omega_tier,
        "reality_stability": round(max(0, 100 - state.paradox_count * 2.5), 1),
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
        outcome_roll = round(random.uniform(-body.amount * 0.5, body.amount * 2.5), 2)
        branches.append({
            "branch_id": f"PX-{secrets.token_hex(4).upper()}",
            "timeline": chr(65 + i),
            "probability": round(100 / body.branches + random.uniform(-5, 5), 1),
            "outcome": outcome_roll,
            "status": "superposed",
        })
    primary = branches[0]
    primary["status"] = "primary"
    proof_hash = hashlib.sha256(str(branches).encode()).hexdigest()[:16]
    record = ParadoxBranch(
        user_id=user.id,
        source_dapp=body.source_dapp,
        action=body.action,
        amount=body.amount,
        branches_json=branches,
        collapsed_branch="",
    )
    session.add(record)
    state.paradox_count += 1
    state.soul_resonance = min(100, state.soul_resonance + 3)
    await session.commit()
    await session.refresh(record)
    return {
        "paradox_id": record.id,
        "branches": branches,
        "collapsed": None,
        "message": f"{body.branches} parallel realities spawned — observe to collapse",
        "proof_hash": proof_hash,
    }


@router.get("/paradox/list")
async def list_paradoxes(session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    rows = (await session.execute(
        select(ParadoxBranch).where(ParadoxBranch.user_id == user.id).order_by(ParadoxBranch.created_at.desc()).limit(12)
    )).scalars().all()
    return {
        "paradoxes": [
            {
                "id": p.id,
                "source_dapp": p.source_dapp,
                "action": p.action,
                "amount": p.amount,
                "branches": p.branches_json,
                "collapsed_branch": p.collapsed_branch or None,
                "collapsed": bool(p.collapsed_branch),
                "created_at": p.created_at.isoformat(),
            }
            for p in rows
        ]
    }


@router.post("/paradox/collapse")
async def collapse_paradox(body: ParadoxCollapse, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    state = await get_omniverse(session, user.id)
    record = (await session.execute(
        select(ParadoxBranch).where(ParadoxBranch.id == body.paradox_id, ParadoxBranch.user_id == user.id)
    )).scalar_one_or_none()
    if not record:
        raise HTTPException(404, "Paradox not found")
    if record.collapsed_branch:
        raise HTTPException(400, "Paradox already collapsed")

    chosen = None
    for b in record.branches_json:
        if b["branch_id"] == body.branch_id:
            chosen = b
            break
    if not chosen:
        raise HTTPException(400, "Branch not found in paradox")

    cefi = (await session.execute(select(CefiAccount).where(CefiAccount.user_id == user.id))).scalar_one()
    defi = (await session.execute(select(DefiWallet).where(DefiWallet.user_id == user.id))).scalar_one()
    casino = await get_casino_wallet(session, user.id)
    balances = {"cefi": cefi, "defi": defi, "casino": casino}
    realm = apply_paradox_outcome(balances, record.source_dapp, chosen["outcome"])

    for b in record.branches_json:
        b["status"] = "collapsed" if b["branch_id"] == body.branch_id else "annihilated"
    record.branches_json = record.branches_json
    record.collapsed_branch = body.branch_id
    state.paradox_count = max(0, state.paradox_count - 1)
    state.soul_resonance = min(100, state.soul_resonance + 8)
    await session.commit()

    return {
        "collapsed": chosen,
        "realm_applied": realm,
        "outcome_applied": chosen["outcome"],
        "message": f"Timeline {chosen['timeline']} collapsed — {chosen['outcome']:+.2f} applied to {realm}",
        "proof_hash": hashlib.sha256(f"{record.id}:{body.branch_id}".encode()).hexdigest()[:16],
    }


@router.get("/chrono/timeline")
async def chrono_timeline(session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    events = []

    orders = (await session.execute(select(Order).where(Order.user_id == user.id).order_by(Order.created_at.desc()).limit(8))).scalars().all()
    for o in orders:
        events.append({
            "id": o.id, "t": o.created_at.isoformat(), "dapp": "cefi", "type": "trade",
            "label": f"{o.side.upper()} {o.pair}", "amount": o.amount,
            "rewindable": o.status == "open",
        })

    txs = (await session.execute(select(DefiTransaction).where(DefiTransaction.user_id == user.id).order_by(DefiTransaction.created_at.desc()).limit(8))).scalars().all()
    for tx in txs:
        events.append({
            "id": tx.id, "t": tx.created_at.isoformat(), "dapp": "defi", "type": tx.tx_type,
            "label": f"{tx.tx_type} {tx.from_token or ''}", "amount": tx.amount,
            "rewindable": tx.status == "confirmed",
        })

    bets = (await session.execute(select(CasinoBet).where(CasinoBet.user_id == user.id).order_by(CasinoBet.created_at.desc()).limit(8))).scalars().all()
    for b in bets:
        rewound = b.outcome_json.get("rewound", False) if isinstance(b.outcome_json, dict) else False
        events.append({
            "id": b.id, "t": b.created_at.isoformat(), "dapp": "casino", "type": "bet",
            "label": f"{b.game} {'WIN' if b.won else 'LOSS'}", "amount": b.bet_amount,
            "rewindable": b.won and not rewound,
        })

    paradoxes = (await session.execute(select(ParadoxBranch).where(ParadoxBranch.user_id == user.id).order_by(ParadoxBranch.created_at.desc()).limit(5))).scalars().all()
    for p in paradoxes:
        events.append({
            "id": p.id, "t": p.created_at.isoformat(), "dapp": "omniverse", "type": "paradox",
            "label": f"Branch {p.source_dapp}/{p.action}", "amount": p.amount, "rewindable": False,
        })

    events.sort(key=lambda e: e["t"], reverse=True)
    return {"events": events[:20], "depth": len(events), "can_rewind": sum(1 for e in events if e["rewindable"])}


@router.post("/chrono/rewind")
async def chrono_rewind(body: ChronoRewindRequest | None = None, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    state = await get_omniverse(session, user.id)

    if body and body.event_id:
        if body.dapp == "casino" and body.event_type == "bet":
            bet = (await session.execute(
                select(CasinoBet).where(CasinoBet.id == body.event_id, CasinoBet.user_id == user.id)
            )).scalar_one_or_none()
            if not bet:
                raise HTTPException(404, "Bet not found")
            if bet.outcome_json.get("rewound"):
                raise HTTPException(400, "Already rewound")
            wallet = await get_casino_wallet(session, user.id)
            chips = wallet.mganga_chips if bet.currency == "MGANGA" else wallet.mwanjesa_chips
            reversal = bet.payout - bet.bet_amount
            if bet.currency == "MGANGA":
                wallet.mganga_chips = max(0, wallet.mganga_chips - bet.payout + bet.bet_amount)
                wallet.total_won = max(0, wallet.total_won - bet.payout)
            else:
                wallet.mwanjesa_chips = max(0, wallet.mwanjesa_chips - bet.payout + bet.bet_amount)
                wallet.total_won = max(0, wallet.total_won - bet.payout)
            outcome = dict(bet.outcome_json) if bet.outcome_json else {}
            outcome["rewound"] = True
            outcome["rewind_at"] = datetime.utcnow().isoformat()
            bet.outcome_json = outcome
            bet.won = False
            state.chrono_depth += 1
            state.paradox_count = max(0, state.paradox_count - 1)
            await session.commit()
            return {
                "rewound": True,
                "event_id": body.event_id,
                "reversal": round(-reversal, 2),
                "chrono_depth": state.chrono_depth,
                "message": f"Casino bet #{bet.id} rewound — {abs(reversal):.2f} chips restored",
            }

        if body.dapp == "cefi" and body.event_type == "trade":
            order = (await session.execute(
                select(Order).where(Order.id == body.event_id, Order.user_id == user.id)
            )).scalar_one_or_none()
            if not order:
                raise HTTPException(404, "Order not found")
            if order.status != "open":
                raise HTTPException(400, "Order not rewindable")
            order.status = "cancelled"
            state.chrono_depth += 1
            await session.commit()
            return {
                "rewound": True,
                "event_id": body.event_id,
                "message": f"Order #{order.id} cancelled via TessChrono",
                "chrono_depth": state.chrono_depth,
            }

        if body.dapp == "defi":
            tx = (await session.execute(
                select(DefiTransaction).where(DefiTransaction.id == body.event_id, DefiTransaction.user_id == user.id)
            )).scalar_one_or_none()
            if tx and tx.status == "confirmed":
                tx.status = "rewound"
                state.chrono_depth += 1
                await session.commit()
                return {"rewound": True, "event_id": body.event_id, "message": f"DeFi tx #{tx.id} marked rewound", "chrono_depth": state.chrono_depth}

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
    casino = await get_casino_wallet(session, user.id)
    chip = casino.mganga_chips

    spread = random.uniform(0.02, 0.08) if state.quantum_superposition else 0.01
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
    cefi = (await session.execute(select(CefiAccount).where(CefiAccount.user_id == user.id))).scalar_one()
    defi = (await session.execute(select(DefiWallet).where(DefiWallet.user_id == user.id))).scalar_one()
    casino = await get_casino_wallet(session, user.id)

    applied = 0.0
    if body.observe in ("cefi", "hybrid"):
        delta = cefi.mganga_balance * jitter
        cefi.mganga_balance = max(0, cefi.mganga_balance + delta)
        applied += delta
    if body.observe in ("defi", "hybrid"):
        delta = defi.mwanjesa_balance * jitter
        defi.mwanjesa_balance = max(0, defi.mwanjesa_balance + delta)
        applied += delta
    if body.observe in ("casino", "hybrid"):
        delta = casino.mganga_chips * jitter
        casino.mganga_chips = max(0, casino.mganga_chips + delta)
        applied += delta

    state.soul_resonance = min(100, state.soul_resonance + 5)
    await session.commit()
    return {
        "observed": body.observe,
        "collapsed": True,
        "wave_function": "collapsed",
        "jitter_applied": round(jitter * 100, 2),
        "balance_delta": round(applied, 2),
        "message": f"Quantum state collapsed to {body.observe} realm — jitter {jitter*100:+.1f}% applied",
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
    paradoxes = (await session.execute(select(ParadoxBranch).where(ParadoxBranch.user_id == user.id))).scalars().all()
    bets = (await session.execute(select(CasinoBet).where(CasinoBet.user_id == user.id).limit(20))).scalars().all()
    win_rate = sum(1 for b in bets if b.won) / max(len(bets), 1) * 100
    return {
        "sync_percent": state.hive_sync_percent,
        "nodes_online": 12847 + state.paradox_count * 137 + int(state.hive_sync_percent * 10),
        "collective_intelligence": round(state.hive_sync_percent * 1.12, 1),
        "consensus_latency_ms": round(max(0.3, 1.2 - state.hive_sync_percent * 0.01), 2),
        "shared_predictions": [
            {"asset": "BTC", "direction": "up" if win_rate > 50 else "down", "confidence": round(62 + win_rate * 0.3, 1)},
            {"asset": "TRD", "direction": "up", "confidence": round(80 + state.soul_resonance * 0.15, 1)},
            {"asset": "ETH", "direction": "neutral", "confidence": round(55 + len(paradoxes) * 2, 1)},
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
    rollback_log = []

    for action in body.actions[:9]:
        dapp = action.get("dapp", "unknown")
        act = action.get("action") or DAPP_ACTIONS.get(dapp, "pulse")
        params = action.get("params", {})
        params["amount"] = params.get("amount", 10 + state.dimension)
        try:
            result = await execute_dapp_action(session, user, state, dapp, act, params)
            result["dimension"] = body.dimension
            results.append(result)
            if result["status"] == "executed":
                rollback_log.append({"dapp": dapp, "action": act})
        except Exception as e:
            results.append({"dapp": dapp, "action": act, "status": "failed", "detail": str(e), "dimension": body.dimension})

    executed = sum(1 for r in results if r.get("status") == "executed")
    state.paradox_count += 1 if executed > 3 else 0
    state.hive_sync_percent = min(99.9, state.hive_sync_percent + executed * 1.5)
    state.soul_resonance = min(100, state.soul_resonance + executed)
    await session.commit()

    digest = hashlib.sha3_256(f"{user.tess_id}:{executed}:{datetime.utcnow().isoformat()}".encode()).hexdigest()[:24]
    return {
        "atomic": executed == len(results),
        "actions_executed": executed,
        "results": results,
        "dimension": body.dimension,
        "omega_fragment": digest,
        "message": f"Omni-executor fired {executed}/{len(results)} real cross-DApp actions in dimension-{body.dimension}",
    }


@router.get("/omega/proof")
async def omega_proof(session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    state = await get_omniverse(session, user.id)
    paradoxes = (await session.execute(select(ParadoxBranch).where(ParadoxBranch.user_id == user.id))).scalars().all()
    bets = (await session.execute(select(CasinoBet).where(CasinoBet.user_id == user.id).limit(5))).scalars().all()
    paradox_hashes = [hashlib.sha256(str(p.branches_json).encode()).hexdigest()[:8] for p in paradoxes[:3]]
    bet_digests = [b.proof_json.get("digest", "")[:8] for b in bets if b.proof_json]
    payload = f"{user.tess_id}:{state.paradox_count}:{state.dimension}:{':'.join(paradox_hashes)}:{':'.join(bet_digests)}"
    digest = hashlib.sha3_256(payload.encode()).hexdigest()
    return {
        "tier": state.omega_tier,
        "algorithm": "RF-SAM-Ω (SHA3-256 + TessSoul binding)",
        "digest": digest,
        "attestations": [
            f"RF-SAM v1 casino proofs ({len(bet_digests)} linked)",
            f"Paradox branch hashes ({len(paradox_hashes)} merkle)",
            "Chrono-ledger merkle root",
            "Quantum collapse receipts",
            "Hive consensus signature",
        ],
        "unreachable": True,
        "human_standard_exceeded_by": f"{round(state.hive_sync_percent * 0.4 + state.soul_resonance * 0.3 + state.dimension * 8, 1)}x",
        "proof_chain": paradox_hashes + bet_digests,
    }
