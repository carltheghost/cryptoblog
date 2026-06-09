from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.rfsam import generate_server_seed, hash_server_seed
from core.models import (
    CasinoWallet,
    OmniverseState,
    CefiAccount,
    CustodyAllocation,
    DaoProposal,
    DefiPool,
    DefiWallet,
    LivingRelic,
    MarketListing,
    TessAgent,
    TessLinkEdge,
    User,
    UserPreference,
)


async def seed_database(session: AsyncSession) -> None:
    result = await session.execute(select(User).where(User.username == "traderone"))
    if result.scalar_one_or_none():
        return

    user = User(
        username="traderone",
        display_name="TraderOne Pro",
        tess_id="TRD-8F7C-29D1",
        tier="verified",
    )
    session.add(user)
    await session.flush()

    session.add(
        CefiAccount(
            user_id=user.id,
            mganga_balance=24350.68,
            usd_balance=24350.68,
            staked_mganga=3652.60,
            earn_rewards=48.70,
            kyc_status="verified",
            aml_compliant=True,
            fraud_score=92,
        )
    )
    session.add(
        DefiWallet(
            user_id=user.id,
            mwanjesa_balance=18732.41,
            hyb_balance=1250.0,
            staked_trd=5000.0,
            staking_rewards=142.35,
            risk_score=88,
            token_balances={"ETH": 5.42, "USDC": 4200.0, "TRD": 12500.0},
        )
    )
    session.add(
        UserPreference(
            user_id=user.id,
            agent_plugins={"pricebot": True, "rebalancer": False},
            recovery_guardians=[],
            batch_queue=[],
        )
    )
    session.add(OmniverseState(user_id=user.id, dimension=3, quantum_superposition=True, hive_sync_percent=67.3, soul_resonance=41.0))
    seed = generate_server_seed()
    session.add(
        CasinoWallet(
            user_id=user.id,
            mganga_chips=5000.0,
            mwanjesa_chips=3000.0,
            server_seed=seed,
            server_seed_hash=hash_server_seed(seed),
        )
    )

    for asset, amount, storage in [
        ("BTC", 1.24, "cold"),
        ("ETH", 18.5, "cold"),
        ("USDT", 450000.0, "warm"),
        ("TRD", 2500000.0, "warm"),
    ]:
        session.add(
            CustodyAllocation(
                user_id=user.id,
                asset=asset,
                amount=amount,
                storage_type=storage,
            )
        )

    relics = [
        ("REL-001", "Living Relic Hero", "Legendary warrior from TribeChain Alpha", "character", "https://api.dicebear.com/7.x/avataaars/svg?seed=relic1"),
        ("REL-002", "Soul Blade", "Enchanted sword with soul reserve locked", "weapon", "https://api.dicebear.com/7.x/shapes/svg?seed=sword"),
        ("REL-003", "Dragon Egg", "Rare dragon hatchling NFT", "creature", "https://api.dicebear.com/7.x/bottts/svg?seed=dragon"),
        ("REL-004", "Land Parcel #42", "Metaverse land tile in TessMeta", "land", "https://api.dicebear.com/7.x/identicon/svg?seed=land42"),
    ]
    for token_id, name, desc, rtype, img in relics:
        session.add(
            LivingRelic(
                token_id=token_id,
                owner_id=user.id,
                name=name,
                description=desc,
                image_url=img,
                relic_type=rtype,
                status="minted",
                soul_reserve=500.0,
                metadata_json={"trait_type": rtype, "rarity": "legendary"},
            )
        )

    session.add(
        DaoProposal(
            title="TRD Emission Model v2",
            description="Adjust MWANJESA inflation curve and soul reserve allocation",
            status="active",
            votes_for=12450,
            votes_against=3200,
            ends_at=datetime.utcnow() + timedelta(days=5),
        )
    )

    for pair, tvl, apy in [("TRD/USDC", 215600000.0, 18.4), ("ETH/USDC", 890000000.0, 12.1), ("MGANGA/USDT", 45000000.0, 8.7)]:
        session.add(DefiPool(pair=pair, tvl=tvl, apy=apy, volume_24h=tvl * 0.05))

    listings = [
        ("Quantum Headset Pro", "Premium VR headset with TessChain integration", 299.99, "MGANGA"),
        ("TessAcademy Course Bundle", "Blockchain + AI certification package", 149.0, "MWANJESA"),
        ("Living Relic Frame", "Display frame for your NFT relics", 89.99, "MGANGA"),
    ]
    for title, desc, price, currency in listings:
        session.add(
            MarketListing(
                seller_id=user.id,
                title=title,
                description=desc,
                price=price,
                currency=currency,
                listing_type="sale",
            )
        )

    agents = [
        ("KYC Verifier", "administrative", "Validates identity attestations for MGANGA economy", 500.0),
        ("Price Oracle", "administrative", "Feeds real-time exchange rates to TessExchange", 1000.0),
        ("Pricebot", "autonomous", "Auto-rebalances portfolio based on market conditions", 250.0),
        ("Relic Validator", "autonomous", "Validates Living Relic authenticity and compliance", 150.0),
    ]
    for name, atype, desc, budget in agents:
        session.add(
            TessAgent(
                name=name,
                agent_type=atype,
                description=desc,
                budget=budget,
                stake=budget * 0.5,
                permissions={"read_wallet": True, "execute_trades": atype == "autonomous"},
            )
        )

    session.add(
        TessLinkEdge(
            source_type="user",
            source_id=user.tess_id,
            target_type="relic",
            target_id="REL-001",
            edge_type="owns",
            attributes={"since": datetime.utcnow().isoformat()},
        )
    )

    await session.commit()
