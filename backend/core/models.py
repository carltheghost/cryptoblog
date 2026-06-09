from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True)
    display_name: Mapped[str] = mapped_column(String(128))
    tess_id: Mapped[str] = mapped_column(String(32), unique=True)
    tier: Mapped[str] = mapped_column(String(32), default="verified")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    cefi_account: Mapped["CefiAccount"] = relationship(back_populates="user", uselist=False)
    defi_wallet: Mapped["DefiWallet"] = relationship(back_populates="user", uselist=False)


class CefiAccount(Base):
    __tablename__ = "cefi_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    mganga_balance: Mapped[float] = mapped_column(Float, default=0.0)
    usd_balance: Mapped[float] = mapped_column(Float, default=0.0)
    staked_mganga: Mapped[float] = mapped_column(Float, default=0.0)
    earn_rewards: Mapped[float] = mapped_column(Float, default=0.0)
    kyc_status: Mapped[str] = mapped_column(String(32), default="pending")
    aml_compliant: Mapped[bool] = mapped_column(Boolean, default=False)
    fraud_score: Mapped[int] = mapped_column(Integer, default=85)

    user: Mapped[User] = relationship(back_populates="cefi_account")


class DefiWallet(Base):
    __tablename__ = "defi_wallets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    mwanjesa_balance: Mapped[float] = mapped_column(Float, default=0.0)
    hyb_balance: Mapped[float] = mapped_column(Float, default=0.0)
    staked_trd: Mapped[float] = mapped_column(Float, default=0.0)
    staking_rewards: Mapped[float] = mapped_column(Float, default=0.0)
    token_balances: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    risk_score: Mapped[int] = mapped_column(Integer, default=88)

    user: Mapped[User] = relationship(back_populates="defi_wallet")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    pair: Mapped[str] = mapped_column(String(16))
    side: Mapped[str] = mapped_column(String(8))
    order_type: Mapped[str] = mapped_column(String(16))
    price: Mapped[float] = mapped_column(Float)
    amount: Mapped[float] = mapped_column(Float)
    filled: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(16), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class FiatDeposit(Base):
    __tablename__ = "fiat_deposits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    method: Mapped[str] = mapped_column(String(32))
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(8), default="USD")
    status: Mapped[str] = mapped_column(String(16), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CustodyAllocation(Base):
    __tablename__ = "custody_allocations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    asset: Mapped[str] = mapped_column(String(16))
    amount: Mapped[float] = mapped_column(Float)
    storage_type: Mapped[str] = mapped_column(String(32), default="cold")


class LivingRelic(Base):
    __tablename__ = "living_relics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token_id: Mapped[str] = mapped_column(String(32), unique=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(128))
    description: Mapped[Optional[str]] = mapped_column(Text)
    image_url: Mapped[str] = mapped_column(String(256))
    relic_type: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), default="minted")
    soul_reserve: Mapped[float] = mapped_column(Float, default=0.0)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON)
    shadow_hash: Mapped[Optional[str]] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DaoProposal(Base):
    __tablename__ = "dao_proposals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(256))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="active")
    votes_for: Mapped[int] = mapped_column(Integer, default=0)
    votes_against: Mapped[int] = mapped_column(Integer, default=0)
    ends_at: Mapped[datetime] = mapped_column(DateTime)


class DaoVote(Base):
    __tablename__ = "dao_votes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    proposal_id: Mapped[int] = mapped_column(ForeignKey("dao_proposals.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    support: Mapped[bool] = mapped_column(Boolean)
    weight: Mapped[float] = mapped_column(Float, default=1.0)


class DefiPool(Base):
    __tablename__ = "defi_pools"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pair: Mapped[str] = mapped_column(String(32))
    tvl: Mapped[float] = mapped_column(Float)
    apy: Mapped[float] = mapped_column(Float)
    volume_24h: Mapped[float] = mapped_column(Float, default=0.0)


class MarketListing(Base):
    __tablename__ = "market_listings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(256))
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(16))
    listing_type: Mapped[str] = mapped_column(String(32), default="sale")
    image_url: Mapped[Optional[str]] = mapped_column(String(256))
    status: Mapped[str] = mapped_column(String(16), default="active")


class TessAgent(Base):
    __tablename__ = "tess_agents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    agent_type: Mapped[str] = mapped_column(String(32))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), default="active")
    budget: Mapped[float] = mapped_column(Float, default=100.0)
    stake: Mapped[float] = mapped_column(Float, default=0.0)
    permissions: Mapped[Optional[dict]] = mapped_column(JSON)


class TessLinkEdge(Base):
    __tablename__ = "tesslink_edges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_type: Mapped[str] = mapped_column(String(32))
    source_id: Mapped[str] = mapped_column(String(64))
    target_type: Mapped[str] = mapped_column(String(32))
    target_id: Mapped[str] = mapped_column(String(64))
    edge_type: Mapped[str] = mapped_column(String(32))
    attributes: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DefiTransaction(Base):
    __tablename__ = "defi_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    tx_type: Mapped[str] = mapped_column(String(32))
    from_token: Mapped[Optional[str]] = mapped_column(String(16))
    to_token: Mapped[Optional[str]] = mapped_column(String(16))
    amount: Mapped[float] = mapped_column(Float)
    output_amount: Mapped[Optional[float]] = mapped_column(Float)
    tx_hash: Mapped[Optional[str]] = mapped_column(String(66))
    status: Mapped[str] = mapped_column(String(16), default="confirmed")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    subject: Mapped[str] = mapped_column(String(256))
    message: Mapped[str] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(16), default="normal")
    status: Mapped[str] = mapped_column(String(16), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    kyc_visible: Mapped[bool] = mapped_column(Boolean, default=True)
    anonymous_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    two_factor: Mapped[bool] = mapped_column(Boolean, default=True)
    tor_routing: Mapped[bool] = mapped_column(Boolean, default=False)
    zk_disclosure: Mapped[bool] = mapped_column(Boolean, default=False)
    multisig_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    multisig_threshold: Mapped[int] = mapped_column(Integer, default=2)
    recovery_guardians: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    agent_plugins: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    batch_queue: Mapped[Optional[list]] = mapped_column(JSON, default=list)


class BarterOffer(Base):
    __tablename__ = "barter_offers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    offer_assets: Mapped[dict] = mapped_column(JSON)
    request_assets: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(16), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CasinoWallet(Base):
    __tablename__ = "casino_wallets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    mganga_chips: Mapped[float] = mapped_column(Float, default=5000.0)
    mwanjesa_chips: Mapped[float] = mapped_column(Float, default=3000.0)
    total_wagered: Mapped[float] = mapped_column(Float, default=0.0)
    total_won: Mapped[float] = mapped_column(Float, default=0.0)
    games_played: Mapped[int] = mapped_column(Integer, default=0)
    win_streak: Mapped[int] = mapped_column(Integer, default=0)
    server_seed: Mapped[str] = mapped_column(String(128))
    server_seed_hash: Mapped[str] = mapped_column(String(128))
    client_seed: Mapped[str] = mapped_column(String(64), default="tesschain-demo")
    nonce: Mapped[int] = mapped_column(Integer, default=0)


class CasinoBet(Base):
    __tablename__ = "casino_bets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    game: Mapped[str] = mapped_column(String(32))
    bet_amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(16), default="MGANGA")
    payout: Mapped[float] = mapped_column(Float, default=0.0)
    multiplier: Mapped[float] = mapped_column(Float, default=0.0)
    won: Mapped[bool] = mapped_column(Boolean, default=False)
    choice: Mapped[Optional[str]] = mapped_column(String(64))
    outcome_json: Mapped[dict] = mapped_column(JSON)
    proof_json: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class BridgeTransaction(Base):
    __tablename__ = "bridge_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    direction: Mapped[str] = mapped_column(String(16))
    amount: Mapped[float] = mapped_column(Float)
    rate: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(16), default="completed")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
