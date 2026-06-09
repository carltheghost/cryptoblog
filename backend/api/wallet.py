import random
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import AgentPluginsUpdate, BatchTransaction, MultisigSetup, RecoverySetup
from core.database import get_db
from core.models import CefiAccount, DefiTransaction, DefiWallet, User, UserPreference

router = APIRouter(prefix="/api/wallet", tags=["wallet"])

DEMO_USER = "traderone"
DEFAULT_PLUGINS = {"pricebot": True, "rebalancer": False}


async def get_demo_user(session: AsyncSession) -> User:
    result = await session.execute(select(User).where(User.username == DEMO_USER))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Demo user not found")
    return user


async def get_prefs(session: AsyncSession, user_id: int) -> UserPreference:
    result = await session.execute(select(UserPreference).where(UserPreference.user_id == user_id))
    prefs = result.scalar_one_or_none()
    if not prefs:
        prefs = UserPreference(user_id=user_id, agent_plugins=DEFAULT_PLUGINS.copy())
        session.add(prefs)
        await session.flush()
    if not prefs.agent_plugins:
        prefs.agent_plugins = DEFAULT_PLUGINS.copy()
    if prefs.recovery_guardians is None:
        prefs.recovery_guardians = []
    if prefs.batch_queue is None:
        prefs.batch_queue = []
    return prefs


async def execute_batch_action(session: AsyncSession, user: User, item: dict) -> dict:
    action = item.get("action", "")
    amount = float(item.get("amount", 0))
    token = (item.get("token") or "MGANGA").upper()
    tx_hash = f"0x{random.randbytes(16).hex()}"

    if action == "bridge":
        cefi = (await session.execute(select(CefiAccount).where(CefiAccount.user_id == user.id))).scalar_one()
        defi = (await session.execute(select(DefiWallet).where(DefiWallet.user_id == user.id))).scalar_one()
        direction = item.get("target") or "cefi_to_defi"
        rate = 0.98
        if direction == "cefi_to_defi":
            if amount > cefi.mganga_balance:
                raise ValueError("Insufficient CeFi balance for bridge")
            cefi.mganga_balance -= amount
            defi.mwanjesa_balance += amount * rate
        else:
            if amount > defi.mwanjesa_balance:
                raise ValueError("Insufficient DeFi balance for bridge")
            defi.mwanjesa_balance -= amount
            cefi.mganga_balance += amount * rate
        session.add(DefiTransaction(user_id=user.id, tx_type="hyb_bridge", amount=amount, tx_hash=tx_hash, status="confirmed"))
        return {"action": action, "status": "executed", "tx_hash": tx_hash, "detail": f"Bridged {amount} via HYB"}

    if action == "stake":
        defi = (await session.execute(select(DefiWallet).where(DefiWallet.user_id == user.id))).scalar_one()
        if amount > defi.mwanjesa_balance:
            raise ValueError("Insufficient MWANJESA for stake")
        defi.mwanjesa_balance -= amount
        defi.staked_trd += amount
        session.add(DefiTransaction(user_id=user.id, tx_type="stake", from_token="MWANJESA", amount=amount, tx_hash=tx_hash, status="confirmed"))
        return {"action": action, "status": "executed", "tx_hash": tx_hash, "detail": f"Staked {amount} TRD"}

    if action == "earn":
        cefi = (await session.execute(select(CefiAccount).where(CefiAccount.user_id == user.id))).scalar_one()
        if amount > cefi.mganga_balance:
            raise ValueError("Insufficient MGANGA for earn stake")
        cefi.mganga_balance -= amount
        cefi.staked_mganga += amount
        return {"action": action, "status": "executed", "tx_hash": tx_hash, "detail": f"Staked {amount} MGANGA in CeFi earn"}

    if action == "swap":
        defi = (await session.execute(select(DefiWallet).where(DefiWallet.user_id == user.id))).scalar_one()
        from api.defi_helpers import swap_tokens
        try:
            output, _ = swap_tokens(defi, token, "TRD", amount)
        except ValueError as e:
            raise ValueError(str(e))
        session.add(DefiTransaction(
            user_id=user.id, tx_type="swap", from_token=token, to_token="TRD",
            amount=amount, output_amount=output, tx_hash=tx_hash, status="confirmed",
        ))
        return {"action": action, "status": "executed", "tx_hash": tx_hash, "detail": f"Swapped {amount} {token} → {output:.4f} TRD"}

    if action == "transfer":
        cefi = (await session.execute(select(CefiAccount).where(CefiAccount.user_id == user.id))).scalar_one()
        if amount > cefi.mganga_balance:
            raise ValueError("Insufficient balance for transfer")
        cefi.mganga_balance -= amount
        return {"action": action, "status": "executed", "tx_hash": tx_hash, "detail": f"Transferred {amount} {token}"}

    return {"action": action, "status": "skipped", "tx_hash": tx_hash, "detail": f"Unknown action {action}"}


@router.get("/config")
async def wallet_config(session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    prefs = await get_prefs(session, user.id)
    return {
        "tess_id": user.tess_id,
        "multisig": {
            "enabled": prefs.multisig_enabled,
            "threshold": prefs.multisig_threshold,
            "keys_required": 3,
        },
        "recovery": {
            "configured": len(prefs.recovery_guardians or []) >= 3,
            "guardians": prefs.recovery_guardians or [],
        },
        "agent_plugins": prefs.agent_plugins or DEFAULT_PLUGINS,
        "batch_queue": prefs.batch_queue or [],
        "privacy": {
            "pseudonym_mode": prefs.anonymous_mode,
            "zk_disclosure": prefs.zk_disclosure,
            "tor_routing": prefs.tor_routing,
        },
    }


@router.post("/multisig")
async def setup_multisig(body: MultisigSetup, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    prefs = await get_prefs(session, user.id)
    if body.threshold < 2 or body.threshold > 5:
        raise HTTPException(400, "Threshold must be between 2 and 5")
    prefs.multisig_enabled = True
    prefs.multisig_threshold = body.threshold
    await session.commit()
    keys = body.device_keys or [f"device-{random.randint(1000, 9999)}" for _ in range(3)]
    return {
        "status": "configured",
        "threshold": f"{body.threshold}-of-3",
        "device_keys": keys,
        "message": "Multisig wallet activated — transactions require multiple signatures",
    }


@router.post("/recovery")
async def setup_recovery(body: RecoverySetup, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    prefs = await get_prefs(session, user.id)
    guardians = body.guardians or [
        "TRD-A1B2-C3D4",
        "TRD-E5F6-G7H8",
        "TRD-I9J0-K1L2",
    ]
    if len(guardians) < 3:
        raise HTTPException(400, "At least 3 guardians required")
    prefs.recovery_guardians = guardians[:5]
    await session.commit()
    return {
        "status": "configured",
        "guardians": prefs.recovery_guardians,
        "message": "Social recovery enabled — guardians can help restore access",
    }


@router.put("/agent-plugins")
async def update_agent_plugins(body: AgentPluginsUpdate, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    prefs = await get_prefs(session, user.id)
    plugins = dict(prefs.agent_plugins or DEFAULT_PLUGINS)
    for field, value in body.model_dump(exclude_none=True).items():
        plugins[field] = value
    prefs.agent_plugins = plugins
    await session.commit()
    return {"agent_plugins": plugins, "status": "saved"}


@router.post("/batch")
async def add_batch_tx(body: BatchTransaction, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    prefs = await get_prefs(session, user.id)
    queue = list(prefs.batch_queue or [])
    entry = {
        "id": len(queue) + 1,
        "action": body.action,
        "amount": body.amount,
        "token": body.token,
        "target": body.target,
        "status": "queued",
        "created_at": datetime.utcnow().isoformat(),
    }
    queue.append(entry)
    prefs.batch_queue = queue[-10:]
    await session.commit()
    return {"queued": entry, "queue_length": len(prefs.batch_queue)}


@router.post("/batch/execute")
async def execute_batch(session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    prefs = await get_prefs(session, user.id)
    queue = list(prefs.batch_queue or [])
    if not queue:
        raise HTTPException(400, "Batch queue is empty")
    executed = []
    for item in queue:
        try:
            result = await execute_batch_action(session, user, item)
            item["status"] = result["status"]
            item["tx_hash"] = result.get("tx_hash")
            item["detail"] = result.get("detail")
            executed.append(item)
        except ValueError as e:
            item["status"] = "failed"
            item["error"] = str(e)
            executed.append(item)
    prefs.batch_queue = []
    await session.commit()
    success = sum(1 for e in executed if e.get("status") == "executed")
    return {
        "executed": success,
        "failed": len(executed) - success,
        "transactions": executed,
        "message": f"Batch: {success}/{len(executed)} transactions confirmed on-chain",
    }
