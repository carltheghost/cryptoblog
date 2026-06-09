import random
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.defi_helpers import SWAP_RATES, get_token_balances, set_token_balance, swap_tokens
from api.schemas import BridgeRequest, CrossChainBridgeRequest, RelicMintRequest, StakeRequest, SwapExecuteRequest, SwapQuoteRequest, VoteRequest
from core.database import get_db
from core.models import BridgeTransaction, CefiAccount, DaoProposal, DaoVote, DefiPool, DefiTransaction, DefiWallet, LivingRelic, User

router = APIRouter(prefix="/api/defi", tags=["defi"])

DEMO_USER = "traderone"


async def get_demo_user(session: AsyncSession) -> User:
    result = await session.execute(select(User).where(User.username == DEMO_USER))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Demo user not found")
    return user


def wallet_response(tess_id: str, wallet: DefiWallet) -> dict:
    balances = get_token_balances(wallet)
    tokens = [
        {"symbol": sym, "balance": bal, "usd_value": round(bal * SWAP_RATES.get(sym, 1.0), 2)}
        for sym, bal in balances.items()
    ]
    return {
        "tess_id": tess_id,
        "mwanjesa_balance": wallet.mwanjesa_balance,
        "hyb_balance": wallet.hyb_balance,
        "staked_trd": wallet.staked_trd,
        "staking_rewards": wallet.staking_rewards,
        "risk_score": wallet.risk_score,
        "chains": [
            {"name": "Ethereum", "balance_usd": round(wallet.mwanjesa_balance * 0.6, 2)},
            {"name": "TribeChain Alpha", "balance_usd": round(wallet.mwanjesa_balance * 0.4, 2)},
        ],
        "tokens": tokens,
    }


@router.get("/wallet/{tess_id}")
async def get_wallet(tess_id: str, session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(User).where(User.tess_id == tess_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Wallet not found")
    wresult = await session.execute(select(DefiWallet).where(DefiWallet.user_id == user.id))
    wallet = wresult.scalar_one()
    return wallet_response(tess_id, wallet)


@router.get("/risk-score")
async def defi_risk_score(session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    wallet = (await session.execute(select(DefiWallet).where(DefiWallet.user_id == user.id))).scalar_one()
    return {
        "score": wallet.risk_score,
        "risk_level": "low" if wallet.risk_score >= 80 else "medium",
        "factors": [
            {"name": "Smart Contract Exposure", "score": 91, "status": "good"},
            {"name": "Wallet Age", "score": 85, "status": "good"},
            {"name": "Transaction Pattern", "score": 90, "status": "good"},
            {"name": "MEV Protection", "score": 86, "status": "good"},
        ],
        "recommendation": "Low Risk - Safe to interact",
    }


@router.post("/swap/quote")
async def swap_quote(body: SwapQuoteRequest):
    from_rate = SWAP_RATES.get(body.from_token.upper(), 1.0)
    to_rate = SWAP_RATES.get(body.to_token.upper(), 1.0)
    output = (body.amount * from_rate / to_rate) * 0.997
    return {
        "from_token": body.from_token,
        "to_token": body.to_token,
        "input_amount": body.amount,
        "output_amount": round(output, 6),
        "rate": round(from_rate / to_rate, 6),
        "route": [body.from_token, "WETH", body.to_token],
        "provider": "1inch",
        "gas_estimate": 0.002,
        "price_impact": round(random.uniform(0.05, 0.25), 2),
    }


@router.post("/swap/execute")
async def swap_execute(body: SwapExecuteRequest, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    wallet = (await session.execute(select(DefiWallet).where(DefiWallet.user_id == user.id))).scalar_one()
    try:
        output, rate = swap_tokens(wallet, body.from_token, body.to_token, body.amount)
    except ValueError as e:
        raise HTTPException(400, str(e))
    tx_hash = f"0x{random.randbytes(16).hex()}"
    tx = DefiTransaction(
        user_id=user.id,
        tx_type="swap",
        from_token=body.from_token.upper(),
        to_token=body.to_token.upper(),
        amount=body.amount,
        output_amount=output,
        tx_hash=tx_hash,
    )
    session.add(tx)
    await session.commit()
    return {
        "tx_hash": tx_hash,
        "status": "confirmed",
        "user": user.tess_id,
        "from_token": body.from_token,
        "to_token": body.to_token,
        "input_amount": body.amount,
        "output_amount": round(output, 6),
        "rate": round(rate, 6),
        "wallet": wallet_response(user.tess_id, wallet),
    }


@router.get("/staking")
async def get_staking(session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    wallet = (await session.execute(select(DefiWallet).where(DefiWallet.user_id == user.id))).scalar_one()
    return {
        "staked_amount": wallet.staked_trd,
        "rewards": wallet.staking_rewards,
        "apy": 12.84,
        "lock_period_days": 30,
        "available_balance": wallet.mwanjesa_balance,
        "next_reward": datetime.utcnow().isoformat(),
    }


@router.post("/stake")
async def stake(body: StakeRequest, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    wallet = (await session.execute(select(DefiWallet).where(DefiWallet.user_id == user.id))).scalar_one()
    if body.amount <= 0:
        raise HTTPException(400, "Amount must be positive")
    if body.amount > wallet.mwanjesa_balance:
        raise HTTPException(400, "Insufficient MWANJESA balance")
    wallet.mwanjesa_balance -= body.amount
    wallet.staked_trd += body.amount
    tx = DefiTransaction(user_id=user.id, tx_type="stake", from_token="MWANJESA", amount=body.amount, status="confirmed")
    session.add(tx)
    await session.commit()
    return {"staked": body.amount, "total_staked": wallet.staked_trd, "apy": 12.84, "available": wallet.mwanjesa_balance}


@router.post("/unstake")
async def unstake(body: StakeRequest, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    wallet = (await session.execute(select(DefiWallet).where(DefiWallet.user_id == user.id))).scalar_one()
    if body.amount > wallet.staked_trd:
        raise HTTPException(400, "Insufficient staked amount")
    wallet.staked_trd -= body.amount
    wallet.mwanjesa_balance += body.amount
    await session.commit()
    return {"unstaked": body.amount, "total_staked": wallet.staked_trd}


@router.get("/dao/proposals")
async def get_proposals(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(DaoProposal).order_by(DaoProposal.id.desc()))
    return [
        {
            "id": p.id, "title": p.title, "description": p.description, "status": p.status,
            "votes_for": p.votes_for, "votes_against": p.votes_against, "ends_at": p.ends_at.isoformat(),
        }
        for p in result.scalars().all()
    ]


@router.post("/dao/vote")
async def cast_vote(body: VoteRequest, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    proposal = (await session.execute(select(DaoProposal).where(DaoProposal.id == body.proposal_id))).scalar_one_or_none()
    if not proposal:
        raise HTTPException(404, "Proposal not found")
    session.add(DaoVote(proposal_id=body.proposal_id, user_id=user.id, support=body.support, weight=1.0))
    if body.support:
        proposal.votes_for += 1
    else:
        proposal.votes_against += 1
    await session.commit()
    return {"voted": body.support, "proposal_id": body.proposal_id}


@router.get("/pools")
async def get_pools(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(DefiPool))
    return [{"pair": p.pair, "tvl": p.tvl, "apy": p.apy, "volume_24h": p.volume_24h} for p in result.scalars().all()]


@router.get("/relics")
async def get_relics(session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    result = await session.execute(select(LivingRelic).where(LivingRelic.owner_id == user.id))
    return [
        {
            "token_id": r.token_id, "name": r.name, "description": r.description,
            "image_url": r.image_url, "type": r.relic_type, "status": r.status,
            "soul_reserve": r.soul_reserve, "shadow_hash": r.shadow_hash,
        }
        for r in result.scalars().all()
    ]


@router.post("/relics/mint")
async def mint_relic(body: RelicMintRequest, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    token_id = f"REL-{random.randint(100, 999)}"
    soul_reserve = 250.0
    relic = LivingRelic(
        token_id=token_id, owner_id=user.id, name=body.name, description=body.description,
        image_url=body.image_url or f"https://api.dicebear.com/7.x/shapes/svg?seed={token_id}",
        relic_type=body.relic_type, status="pending", soul_reserve=soul_reserve,
        metadata_json={"trait_type": body.relic_type},
    )
    session.add(relic)
    await session.commit()
    return {"token_id": relic.token_id, "status": "pending_validation", "soul_reserve_locked": soul_reserve}


@router.post("/relics/{token_id}/validate")
async def validate_relic(token_id: str, session: AsyncSession = Depends(get_db)):
    relic = (await session.execute(select(LivingRelic).where(LivingRelic.token_id == token_id))).scalar_one_or_none()
    if not relic:
        raise HTTPException(404, "Relic not found")
    relic.status = "minted"
    await session.commit()
    return {"token_id": token_id, "status": "minted"}


@router.post("/bridge")
async def bridge_assets(body: BridgeRequest, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    cefi = (await session.execute(select(CefiAccount).where(CefiAccount.user_id == user.id))).scalar_one()
    defi = (await session.execute(select(DefiWallet).where(DefiWallet.user_id == user.id))).scalar_one()
    rate = 0.98
    if body.amount <= 0:
        raise HTTPException(400, "Amount must be positive")
    if body.direction == "cefi_to_defi":
        if body.amount > cefi.mganga_balance:
            raise HTTPException(400, "Insufficient CeFi balance")
        cefi.mganga_balance -= body.amount
        defi.mwanjesa_balance += body.amount * rate
    else:
        if body.amount > defi.mwanjesa_balance:
            raise HTTPException(400, "Insufficient DeFi balance")
        defi.mwanjesa_balance -= body.amount
        cefi.mganga_balance += body.amount * rate
    session.add(BridgeTransaction(user_id=user.id, direction=body.direction, amount=body.amount, rate=rate))
    session.add(DefiTransaction(user_id=user.id, tx_type="hyb_bridge", amount=body.amount, status="confirmed"))
    await session.commit()
    return {
        "direction": body.direction, "amount": body.amount, "rate": rate,
        "cefi_balance": cefi.mganga_balance, "defi_balance": defi.mwanjesa_balance, "status": "completed",
    }


@router.post("/cross-chain")
async def cross_chain_bridge(body: CrossChainBridgeRequest, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    wallet = (await session.execute(select(DefiWallet).where(DefiWallet.user_id == user.id))).scalar_one()
    balances = get_token_balances(wallet)
    token = body.token.upper()
    if balances.get(token, 0) < body.amount:
        raise HTTPException(400, f"Insufficient {token}")
    fee = body.amount * 0.003
    net = body.amount - fee
    set_token_balance(wallet, token, balances[token] - body.amount)
    tx_hash = f"0x{random.randbytes(16).hex()}"
    session.add(DefiTransaction(
        user_id=user.id, tx_type="cross_chain", from_token=token, amount=body.amount,
        output_amount=net, tx_hash=tx_hash,
    ))
    await session.commit()
    return {
        "tx_hash": tx_hash, "from_chain": body.from_chain, "to_chain": body.to_chain,
        "token": token, "amount": body.amount, "fee": round(fee, 4), "received": round(net, 4), "status": "confirmed",
    }


@router.get("/transactions")
async def get_transactions(session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    result = await session.execute(
        select(DefiTransaction).where(DefiTransaction.user_id == user.id).order_by(DefiTransaction.created_at.desc()).limit(50)
    )
    return [
        {
            "id": t.id, "type": t.tx_type, "from_token": t.from_token, "to_token": t.to_token,
            "amount": t.amount, "output_amount": t.output_amount, "tx_hash": t.tx_hash,
            "status": t.status, "created_at": t.created_at.isoformat(),
        }
        for t in result.scalars().all()
    ]


@router.get("/stats")
async def defi_stats():
    return {
        "tvl": 1.32e9,
        "volume_24h": 890e6,
        "active_pools": 12,
        "validators": 128,
        "avg_apy": 14.2,
    }


@router.get("/child-chain")
async def child_chain_info():
    return {
        "name": "TribeChain Alpha", "tvl": 215600000.0, "block_time": 1.2,
        "consensus": "PoS", "validators": 128, "status": "active",
    }
