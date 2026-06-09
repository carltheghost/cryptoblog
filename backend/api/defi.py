import random
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import BridgeRequest, RelicMintRequest, StakeRequest, SwapExecuteRequest, SwapQuoteRequest, VoteRequest
from core.database import get_db
from core.models import BridgeTransaction, CefiAccount, DaoProposal, DaoVote, DefiPool, DefiWallet, LivingRelic, User

router = APIRouter(prefix="/api/defi", tags=["defi"])

DEMO_USER = "traderone"
SWAP_RATES = {"ETH": 3456.72, "USDC": 1.0, "TRD": 0.2457, "MGANGA": 1.0, "MWANJESA": 0.98}


async def get_demo_user(session: AsyncSession) -> User:
    result = await session.execute(select(User).where(User.username == DEMO_USER))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Demo user not found")
    return user


@router.get("/wallet/{tess_id}")
async def get_wallet(tess_id: str, session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(User).where(User.tess_id == tess_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Wallet not found")
    wresult = await session.execute(select(DefiWallet).where(DefiWallet.user_id == user.id))
    wallet = wresult.scalar_one()
    return {
        "tess_id": tess_id,
        "mwanjesa_balance": wallet.mwanjesa_balance,
        "hyb_balance": wallet.hyb_balance,
        "staked_trd": wallet.staked_trd,
        "staking_rewards": wallet.staking_rewards,
        "chains": [
            {"name": "Ethereum", "balance_usd": wallet.mwanjesa_balance * 0.6},
            {"name": "TribeChain Alpha", "balance_usd": wallet.mwanjesa_balance * 0.4},
        ],
        "tokens": [
            {"symbol": "ETH", "balance": 5.42, "usd_value": 18734.22},
            {"symbol": "USDC", "balance": 4200.0, "usd_value": 4200.0},
            {"symbol": "TRD", "balance": 12500.0, "usd_value": 3071.25},
            {"symbol": "MWANJESA", "balance": wallet.mwanjesa_balance, "usd_value": wallet.mwanjesa_balance},
        ],
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
        "price_impact": 0.12,
    }


@router.post("/swap/execute")
async def swap_execute(body: SwapExecuteRequest, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    quote = await swap_quote(SwapQuoteRequest(from_token=body.from_token, to_token=body.to_token, amount=body.amount))
    return {
        "tx_hash": f"0x{random.randbytes(16).hex()}",
        "status": "confirmed",
        "user": user.tess_id,
        **quote,
    }


@router.get("/staking")
async def get_staking(session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    result = await session.execute(select(DefiWallet).where(DefiWallet.user_id == user.id))
    wallet = result.scalar_one()
    return {
        "staked_amount": wallet.staked_trd,
        "rewards": wallet.staking_rewards,
        "apy": 12.84,
        "lock_period_days": 30,
        "next_reward": datetime.utcnow().isoformat(),
    }


@router.post("/stake")
async def stake(body: StakeRequest, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    result = await session.execute(select(DefiWallet).where(DefiWallet.user_id == user.id))
    wallet = result.scalar_one()
    if body.amount > wallet.mwanjesa_balance:
        raise HTTPException(400, "Insufficient balance")
    wallet.mwanjesa_balance -= body.amount
    wallet.staked_trd += body.amount
    await session.commit()
    return {"staked": body.amount, "total_staked": wallet.staked_trd, "apy": 12.84}


@router.get("/dao/proposals")
async def get_proposals(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(DaoProposal).order_by(DaoProposal.id.desc()))
    proposals = result.scalars().all()
    return [
        {
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "status": p.status,
            "votes_for": p.votes_for,
            "votes_against": p.votes_against,
            "ends_at": p.ends_at.isoformat(),
        }
        for p in proposals
    ]


@router.post("/dao/vote")
async def cast_vote(body: VoteRequest, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    result = await session.execute(select(DaoProposal).where(DaoProposal.id == body.proposal_id))
    proposal = result.scalar_one_or_none()
    if not proposal:
        raise HTTPException(404, "Proposal not found")
    vote = DaoVote(proposal_id=body.proposal_id, user_id=user.id, support=body.support, weight=1.0)
    session.add(vote)
    if body.support:
        proposal.votes_for += 1
    else:
        proposal.votes_against += 1
    await session.commit()
    return {"voted": body.support, "proposal_id": body.proposal_id}


@router.get("/pools")
async def get_pools(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(DefiPool))
    pools = result.scalars().all()
    return [
        {"pair": p.pair, "tvl": p.tvl, "apy": p.apy, "volume_24h": p.volume_24h}
        for p in pools
    ]


@router.get("/relics")
async def get_relics(session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    result = await session.execute(select(LivingRelic).where(LivingRelic.owner_id == user.id))
    relics = result.scalars().all()
    return [
        {
            "token_id": r.token_id,
            "name": r.name,
            "description": r.description,
            "image_url": r.image_url,
            "type": r.relic_type,
            "status": r.status,
            "soul_reserve": r.soul_reserve,
        }
        for r in relics
    ]


@router.post("/relics/mint")
async def mint_relic(body: RelicMintRequest, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    token_id = f"REL-{random.randint(100, 999)}"
    soul_reserve = 250.0
    relic = LivingRelic(
        token_id=token_id,
        owner_id=user.id,
        name=body.name,
        description=body.description,
        image_url=body.image_url or f"https://api.dicebear.com/7.x/shapes/svg?seed={token_id}",
        relic_type=body.relic_type,
        status="pending",
        soul_reserve=soul_reserve,
        metadata_json={"trait_type": body.relic_type},
    )
    session.add(relic)
    await session.commit()
    await session.refresh(relic)
    return {
        "token_id": relic.token_id,
        "status": "pending_validation",
        "soul_reserve_locked": soul_reserve,
        "message": "Relic submitted for validation",
    }


@router.post("/bridge")
async def bridge_assets(body: BridgeRequest, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    cefi_result = await session.execute(select(CefiAccount).where(CefiAccount.user_id == user.id))
    cefi = cefi_result.scalar_one()
    defi_result = await session.execute(select(DefiWallet).where(DefiWallet.user_id == user.id))
    defi = defi_result.scalar_one()

    rate = 0.98
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

    tx = BridgeTransaction(
        user_id=user.id,
        direction=body.direction,
        amount=body.amount,
        rate=rate,
        status="completed",
    )
    session.add(tx)
    await session.commit()
    return {
        "tx_id": tx.id,
        "direction": body.direction,
        "amount": body.amount,
        "rate": rate,
        "cefi_balance": cefi.mganga_balance,
        "defi_balance": defi.mwanjesa_balance,
        "status": "completed",
    }


@router.get("/child-chain")
async def child_chain_info():
    return {
        "name": "TribeChain Alpha",
        "tvl": 215600000.0,
        "block_time": 1.2,
        "consensus": "PoS",
        "validators": 128,
        "status": "active",
    }
