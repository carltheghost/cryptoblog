from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.models import CefiAccount, DefiWallet, User

router = APIRouter(prefix="/api/rewards", tags=["rewards"])


@router.get("/")
async def get_rewards(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(User).where(User.username == "traderone"))
    user = result.scalar_one()
    cefi = (await session.execute(select(CefiAccount).where(CefiAccount.user_id == user.id))).scalar_one()
    defi = (await session.execute(select(DefiWallet).where(DefiWallet.user_id == user.id))).scalar_one()

    activity = 2450.0 + (cefi.fraud_score * 2)
    trade = 890.0 + (cefi.mganga_balance * 0.001)
    legacy = defi.staking_rewards
    staking_claimable = defi.staking_rewards

    return {
        "pools": [
            {"name": "Activity Pool", "amount": round(activity, 2), "token": "TRD", "description": "Earned from engagement"},
            {"name": "Trade Pool", "amount": round(trade, 2), "token": "TRD", "description": "Trading fee rewards"},
            {"name": "Legacy Pool", "amount": round(legacy, 2), "token": "TRD", "description": "Staking rewards"},
        ],
        "total_claimable": round(activity * 0.1 + trade * 0.05 + staking_claimable, 2),
        "cefi_earn_apy": 6.5,
        "defi_staking_apy": 12.84,
    }


@router.post("/claim")
async def claim_rewards(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(User).where(User.username == "traderone"))
    user = result.scalar_one()
    defi = (await session.execute(select(DefiWallet).where(DefiWallet.user_id == user.id))).scalar_one()
    claimed = defi.staking_rewards
    defi.mwanjesa_balance += claimed
    defi.staking_rewards = 0.0
    await session.commit()
    return {"claimed": claimed, "new_balance": defi.mwanjesa_balance}
