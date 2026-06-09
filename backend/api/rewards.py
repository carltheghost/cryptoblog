from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.models import CefiAccount, DefiWallet, User

router = APIRouter(prefix="/api/rewards", tags=["rewards"])


def compute_pools(cefi: CefiAccount, defi: DefiWallet) -> dict:
    activity = round(2450.0 + cefi.fraud_score * 2, 2)
    trade = round(890.0 + cefi.mganga_balance * 0.001, 2)
    legacy = round(defi.staking_rewards, 2)
    earn = round(cefi.earn_rewards, 2)
    total = round(activity * 0.1 + trade * 0.05 + legacy + earn, 2)
    return {
        "pools": [
            {"name": "Activity Pool", "amount": activity, "claimable": round(activity * 0.1, 2), "token": "TRD", "description": "Earned from engagement"},
            {"name": "Trade Pool", "amount": trade, "claimable": round(trade * 0.05, 2), "token": "TRD", "description": "Trading fee rewards"},
            {"name": "Legacy Pool", "amount": legacy, "claimable": legacy, "token": "TRD", "description": "Staking rewards"},
            {"name": "CeFi Earn Pool", "amount": earn, "claimable": earn, "token": "MGANGA", "description": "CeFi earn accrued"},
        ],
        "total_claimable": total,
    }


@router.get("/")
async def get_rewards(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(User).where(User.username == "traderone"))
    user = result.scalar_one()
    cefi = (await session.execute(select(CefiAccount).where(CefiAccount.user_id == user.id))).scalar_one()
    defi = (await session.execute(select(DefiWallet).where(DefiWallet.user_id == user.id))).scalar_one()
    data = compute_pools(cefi, defi)
    return {
        **data,
        "cefi_earn_apy": 6.5,
        "defi_staking_apy": 12.84,
    }


@router.post("/claim")
async def claim_rewards(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(User).where(User.username == "traderone"))
    user = result.scalar_one()
    cefi = (await session.execute(select(CefiAccount).where(CefiAccount.user_id == user.id))).scalar_one()
    defi = (await session.execute(select(DefiWallet).where(DefiWallet.user_id == user.id))).scalar_one()

    pools = compute_pools(cefi, defi)
    trd_claim = round(pools["pools"][0]["claimable"] + pools["pools"][1]["claimable"] + pools["pools"][2]["claimable"], 2)
    mganga_claim = pools["pools"][3]["claimable"]

    if trd_claim <= 0 and mganga_claim <= 0:
        defi.staking_rewards = round(defi.staked_trd * 0.001, 4)
        cefi.earn_rewards = round(cefi.staked_mganga * 0.002, 4)
        pools = compute_pools(cefi, defi)
        trd_claim = round(pools["pools"][0]["claimable"] + pools["pools"][1]["claimable"] + pools["pools"][2]["claimable"], 2)
        mganga_claim = pools["pools"][3]["claimable"]

    defi.mwanjesa_balance += trd_claim
    defi.staking_rewards = 0.0
    cefi.mganga_balance += mganga_claim
    cefi.earn_rewards = 0.0

    total = round(trd_claim + mganga_claim, 2)
    await session.commit()
    return {
        "claimed_trd": trd_claim,
        "claimed_mganga": mganga_claim,
        "total_claimed": total,
        "new_defi_balance": defi.mwanjesa_balance,
        "new_cefi_balance": cefi.mganga_balance,
    }
