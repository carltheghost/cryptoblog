from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.models import CefiAccount, DefiWallet, User

router = APIRouter(prefix="/api/identity", tags=["identity"])


@router.get("/{tess_id}")
async def get_identity(tess_id: str, session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(User).where(User.tess_id == tess_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "TessID not found")
    cefi_result = await session.execute(select(CefiAccount).where(CefiAccount.user_id == user.id))
    cefi = cefi_result.scalar_one_or_none()
    defi_result = await session.execute(select(DefiWallet).where(DefiWallet.user_id == user.id))
    defi = defi_result.scalar_one_or_none()
    return {
        "tess_id": user.tess_id,
        "display_name": user.display_name,
        "tier": user.tier,
        "cefi_balance": cefi.mganga_balance if cefi else 0,
        "defi_balance": defi.mwanjesa_balance if defi else 0,
        "attestations": [
            {"type": "KYC", "issuer": "TessChain Authority", "verified": True},
            {"type": "AML", "issuer": "Compliance Council", "verified": True},
        ],
        "privacy_vault": {"enabled": True, "fields_encrypted": 12},
    }


@router.get("/hybrid/balances")
async def hybrid_balances(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(User).where(User.username == "traderone"))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")
    cefi_result = await session.execute(select(CefiAccount).where(CefiAccount.user_id == user.id))
    cefi = cefi_result.scalar_one()
    defi_result = await session.execute(select(DefiWallet).where(DefiWallet.user_id == user.id))
    defi = defi_result.scalar_one()
    return {
        "tess_id": user.tess_id,
        "cefi_balance": cefi.mganga_balance,
        "defi_balance": defi.mwanjesa_balance,
        "hyb_balance": defi.hyb_balance,
        "dag_finality_ms": 850,
        "settlement_secure": True,
    }
