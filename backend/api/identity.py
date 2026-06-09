from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import PreferenceUpdate
from core.database import get_db
from core.models import CefiAccount, DefiWallet, User, UserPreference

router = APIRouter(prefix="/api/identity", tags=["identity"])


async def get_user_by_tess(tess_id: str, session: AsyncSession) -> User:
    result = await session.execute(select(User).where(User.tess_id == tess_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "TessID not found")
    return user


@router.get("/{tess_id}")
async def get_identity(tess_id: str, session: AsyncSession = Depends(get_db)):
    user = await get_user_by_tess(tess_id, session)
    cefi = (await session.execute(select(CefiAccount).where(CefiAccount.user_id == user.id))).scalar_one_or_none()
    defi = (await session.execute(select(DefiWallet).where(DefiWallet.user_id == user.id))).scalar_one_or_none()
    prefs = (await session.execute(select(UserPreference).where(UserPreference.user_id == user.id))).scalar_one_or_none()
    return {
        "tess_id": user.tess_id,
        "display_name": user.display_name,
        "tier": user.tier,
        "cefi_balance": cefi.mganga_balance if cefi else 0,
        "defi_balance": defi.mwanjesa_balance if defi else 0,
        "attestations": [
            {"type": "KYC", "issuer": "TessChain Authority", "verified": cefi.kyc_status == "verified" if cefi else False},
            {"type": "AML", "issuer": "Compliance Council", "verified": cefi.aml_compliant if cefi else False},
            {"type": "DeFi", "issuer": "Tessalink", "verified": True},
        ],
        "privacy_vault": {"enabled": True, "fields_encrypted": 12},
        "preferences": {
            "kyc_visible": prefs.kyc_visible if prefs else True,
            "anonymous_mode": prefs.anonymous_mode if prefs else False,
            "two_factor": prefs.two_factor if prefs else True,
            "tor_routing": prefs.tor_routing if prefs else False,
            "zk_disclosure": prefs.zk_disclosure if prefs else False,
        } if prefs else {
            "kyc_visible": True, "anonymous_mode": False, "two_factor": True,
            "tor_routing": False, "zk_disclosure": False,
        },
    }


@router.put("/{tess_id}/preferences")
async def update_preferences(tess_id: str, body: PreferenceUpdate, session: AsyncSession = Depends(get_db)):
    user = await get_user_by_tess(tess_id, session)
    result = await session.execute(select(UserPreference).where(UserPreference.user_id == user.id))
    prefs = result.scalar_one_or_none()
    if not prefs:
        prefs = UserPreference(user_id=user.id)
        session.add(prefs)
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(prefs, field, value)
    await session.commit()
    return {"status": "saved", "preferences": {
        "kyc_visible": prefs.kyc_visible, "anonymous_mode": prefs.anonymous_mode,
        "two_factor": prefs.two_factor, "tor_routing": prefs.tor_routing, "zk_disclosure": prefs.zk_disclosure,
    }}


@router.get("/hybrid/balances")
async def hybrid_balances(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(User).where(User.username == "traderone"))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")
    cefi = (await session.execute(select(CefiAccount).where(CefiAccount.user_id == user.id))).scalar_one()
    defi = (await session.execute(select(DefiWallet).where(DefiWallet.user_id == user.id))).scalar_one()
    return {
        "tess_id": user.tess_id,
        "cefi_balance": cefi.mganga_balance,
        "defi_balance": defi.mwanjesa_balance,
        "hyb_balance": defi.hyb_balance,
        "dag_finality_ms": 850,
        "settlement_secure": True,
    }
