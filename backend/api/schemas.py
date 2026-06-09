from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    pair: str = "BTC/USDT"
    side: str = Field(..., pattern="^(buy|sell)$")
    order_type: str = Field("limit", pattern="^(limit|market)$")
    price: float
    amount: float


class FiatDepositCreate(BaseModel):
    method: str = "bank_transfer"
    amount: float
    currency: str = "USD"


class SwapQuoteRequest(BaseModel):
    from_token: str
    to_token: str
    amount: float


class SwapExecuteRequest(BaseModel):
    from_token: str
    to_token: str
    amount: float
    slippage: float = 0.5


class StakeRequest(BaseModel):
    amount: float
    lock_days: int = 30


class VoteRequest(BaseModel):
    proposal_id: int
    support: bool


class BridgeRequest(BaseModel):
    direction: str = Field(..., pattern="^(cefi_to_defi|defi_to_cefi)$")
    amount: float


class RelicMintRequest(BaseModel):
    name: str
    description: str
    relic_type: str
    image_url: str = ""


class MarketListingCreate(BaseModel):
    title: str
    description: str
    price: float
    currency: str = "MGANGA"
    listing_type: str = "sale"


class AgentCreate(BaseModel):
    name: str
    agent_type: str
    description: str
    budget: float = 100.0


class CrossChainBridgeRequest(BaseModel):
    from_chain: str = "Ethereum"
    to_chain: str = "TribeChain"
    token: str = "USDC"
    amount: float


class PreferenceUpdate(BaseModel):
    kyc_visible: Optional[bool] = None
    anonymous_mode: Optional[bool] = None
    two_factor: Optional[bool] = None
    tor_routing: Optional[bool] = None
    zk_disclosure: Optional[bool] = None


class EarnStakeRequest(BaseModel):
    amount: float


class MultisigSetup(BaseModel):
    threshold: int = 2
    device_keys: list[str] = Field(default_factory=list)


class RecoverySetup(BaseModel):
    guardians: list[str] = Field(default_factory=list)


class AgentPluginsUpdate(BaseModel):
    pricebot: Optional[bool] = None
    rebalancer: Optional[bool] = None


class BatchTransaction(BaseModel):
    action: str
    amount: float
    token: str = "MGANGA"
    target: str = "hybrid"
