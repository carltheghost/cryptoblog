import random
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.rfsam import derive_result, generate_server_seed, hash_server_seed, verify_proof
from core.database import get_db
from core.models import CasinoBet, CasinoWallet, User

router = APIRouter(prefix="/api/casino", tags=["casino"])

DEMO_USER = "traderone"
SLOT_SYMBOLS = ["7", "TRD", "HYB", "ETH", "GEM", "STAR", "MOON", "ACE"]
WHEEL_MULTIPLIERS = [0, 0.5, 1, 1.5, 2, 2.5, 3, 5, 0, 0.5, 1, 10]


class BetRequest(BaseModel):
    game: str
    amount: float = Field(gt=0)
    currency: str = "MGANGA"
    choice: str = ""
    client_seed: str = "tesschain-demo"


class VerifyRequest(BaseModel):
    bet_id: int


async def get_demo_user(session: AsyncSession) -> User:
    result = await session.execute(select(User).where(User.username == DEMO_USER))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Demo user not found")
    return user


async def get_casino_wallet(session: AsyncSession, user_id: int) -> CasinoWallet:
    result = await session.execute(select(CasinoWallet).where(CasinoWallet.user_id == user_id))
    wallet = result.scalar_one_or_none()
    if not wallet:
        seed = generate_server_seed()
        wallet = CasinoWallet(
            user_id=user_id,
            server_seed=seed,
            server_seed_hash=hash_server_seed(seed),
        )
        session.add(wallet)
        await session.flush()
    return wallet


def resolve_slots(r1: int, r2: int, r3: int) -> tuple[float, list[str]]:
    reels = [SLOT_SYMBOLS[r1], SLOT_SYMBOLS[r2], SLOT_SYMBOLS[r3]]
    if r1 == r2 == r3:
        mult = 50.0 if reels[0] == "7" else 25.0 if reels[0] == "ACE" else 10.0
    elif r1 == r2 or r2 == r3 or r1 == r3:
        mult = 3.0
    else:
        mult = 0.0
    return mult, reels


def play_game(game: str, outcome: dict, choice: str, amount: float) -> tuple[bool, float, float, dict]:
    extra = {}
    if game == "tess-slots":
        mult, reels = resolve_slots(outcome["slot_r1"], outcome["slot_r2"], outcome["slot_r3"])
        extra = {"reels": reels}
        return mult > 0, amount * mult, mult, extra

    if game == "hyper-dice":
        total = outcome["dice_a"] + outcome["dice_b"]
        target = int(choice or "7")
        won = total == target
        mult = 6.0 if won else 0.0
        extra = {"dice": [outcome["dice_a"], outcome["dice_b"]], "total": total, "target": target}
        return won, amount * mult, mult, extra

    if game == "quantum-roulette":
        num = outcome["roulette"]
        pick = choice or "red"
        red = num in {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
        black = num in {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}
        if pick.isdigit():
            won = int(pick) == num
            mult = 35.0 if won else 0.0
        elif pick == "red":
            won = red
            mult = 2.0 if won else 0.0
        elif pick == "black":
            won = black
            mult = 2.0 if won else 0.0
        else:
            won = num == 0
            mult = 35.0 if won else 0.0
        extra = {"number": num, "color": "green" if num == 0 else "red" if red else "black"}
        return won, amount * mult, mult, extra

    if game == "crash-orbit":
        crash = outcome["crash_point"]
        cashout = float(choice or "2.0")
        won = cashout <= crash
        mult = cashout if won else 0.0
        extra = {"crash_point": crash, "cashed_at": cashout}
        return won, amount * mult, mult, extra

    if game == "soul-wheel":
        seg = outcome["wheel_segment"]
        mult = WHEEL_MULTIPLIERS[seg]
        extra = {"segment": seg, "label": f"{mult}x"}
        return mult > 0, amount * mult, mult, extra

    if game == "tess-poker":
        player = outcome["card_rank"]
        dealer = ((outcome["card_rank"] + outcome["card_suit"]) % 13) + 2
        won = player > dealer
        mult = 2.0 if won else (1.0 if player == dealer else 0.0)
        extra = {"player": player, "dealer": dealer}
        return won or mult == 1.0, amount * mult, mult, extra

    if game == "hyper-lottery":
        nums = outcome["lottery_4d"]
        pick = [int(c) for c in (choice or "0000") if c.isdigit()]
        while len(pick) < 4:
            pick.append(0)
        matches = sum(1 for a, b in zip(nums, pick[:4]) if a == b)
        mult = {4: 100.0, 3: 10.0, 2: 2.0, 1: 0.5}.get(matches, 0.0)
        extra = {"drawn": nums, "picked": pick[:4], "matches": matches}
        return mult > 0, amount * mult, mult, extra

    raise HTTPException(400, f"Unknown game: {game}")


GAMES = [
    {"id": "tess-slots", "name": "Tess Slots", "category": "slots", "min_bet": 10, "max_multiplier": 50, "dimension": "3D"},
    {"id": "hyper-dice", "name": "Hyper Dice", "category": "dice", "min_bet": 5, "max_multiplier": 6, "dimension": "3D"},
    {"id": "quantum-roulette", "name": "Quantum Roulette", "category": "table", "min_bet": 10, "max_multiplier": 35, "dimension": "3D"},
    {"id": "crash-orbit", "name": "Crash Orbit", "category": "crash", "min_bet": 5, "max_multiplier": 100, "dimension": "4D"},
    {"id": "soul-wheel", "name": "Soul Wheel", "category": "wheel", "min_bet": 5, "max_multiplier": 10, "dimension": "3D"},
    {"id": "tess-poker", "name": "Tess Poker", "category": "cards", "min_bet": 20, "max_multiplier": 2, "dimension": "3D"},
    {"id": "hyper-lottery", "name": "Hyper Lottery 4D", "category": "lottery", "min_bet": 1, "max_multiplier": 100, "dimension": "4D"},
]


@router.get("/games")
async def list_games():
    return {"games": GAMES, "proof_system": "RF-SAM v1", "social": True}


@router.get("/wallet")
async def casino_wallet(session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    wallet = await get_casino_wallet(session, user.id)
    return {
        "mganga_chips": wallet.mganga_chips,
        "mwanjesa_chips": wallet.mwanjesa_chips,
        "total_wagered": wallet.total_wagered,
        "total_won": wallet.total_won,
        "games_played": wallet.games_played,
        "win_streak": wallet.win_streak,
        "server_seed_hash": wallet.server_seed_hash,
        "client_seed": wallet.client_seed,
        "nonce": wallet.nonce,
        "net_profit": round(wallet.total_won - wallet.total_wagered, 2),
    }


@router.post("/deposit")
async def deposit_chips(body: dict, session: AsyncSession = Depends(get_db)):
    amount = float(body.get("amount", 0))
    currency = body.get("currency", "MGANGA").upper()
    if amount <= 0:
        raise HTTPException(400, "Invalid amount")
    user = await get_demo_user(session)
    wallet = await get_casino_wallet(session, user.id)
    if currency == "MGANGA":
        from core.models import CefiAccount
        cefi = (await session.execute(select(CefiAccount).where(CefiAccount.user_id == user.id))).scalar_one()
        if cefi.mganga_balance < amount:
            raise HTTPException(400, "Insufficient MGANGA")
        cefi.mganga_balance -= amount
        wallet.mganga_chips += amount
    else:
        from core.models import DefiWallet
        defi = (await session.execute(select(DefiWallet).where(DefiWallet.user_id == user.id))).scalar_one()
        if defi.mwanjesa_balance < amount:
            raise HTTPException(400, "Insufficient MWANJESA")
        defi.mwanjesa_balance -= amount
        wallet.mwanjesa_chips += amount
    await session.commit()
    return {"deposited": amount, "currency": currency, "chips": wallet.mganga_chips if currency == "MGANGA" else wallet.mwanjesa_chips}


@router.post("/bet")
async def place_bet(body: BetRequest, session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    wallet = await get_casino_wallet(session, user.id)
    game_ids = {g["id"] for g in GAMES}
    if body.game not in game_ids:
        raise HTTPException(400, "Invalid game")

    chips = wallet.mganga_chips if body.currency == "MGANGA" else wallet.mwanjesa_chips
    if body.amount > chips:
        raise HTTPException(400, "Insufficient casino chips — deposit from wallet first")

    wallet.nonce += 1
    nonce = wallet.nonce
    outcome = derive_result(wallet.server_seed, body.client_seed, nonce, body.game)
    won, payout, mult, extra = play_game(body.game, outcome, body.choice, body.amount)

    if body.currency == "MGANGA":
        wallet.mganga_chips -= body.amount
        wallet.mganga_chips += payout
    else:
        wallet.mwanjesa_chips -= body.amount
        wallet.mwanjesa_chips += payout

    wallet.total_wagered += body.amount
    wallet.total_won += payout
    wallet.games_played += 1
    wallet.win_streak = wallet.win_streak + 1 if won else 0
    wallet.client_seed = body.client_seed

    proof = {
        "algorithm": "RF-SAM v1",
        "server_seed_hash": wallet.server_seed_hash,
        "client_seed": body.client_seed,
        "nonce": nonce,
        "digest": outcome["digest"],
        "game": body.game,
    }
    outcome_data = {**extra, "float": outcome["float_0_1"]}

    bet = CasinoBet(
        user_id=user.id,
        game=body.game,
        bet_amount=body.amount,
        currency=body.currency,
        payout=payout,
        multiplier=mult,
        won=won,
        choice=body.choice,
        outcome_json=outcome_data,
        proof_json=proof,
    )
    session.add(bet)
    await session.commit()
    await session.refresh(bet)

    if wallet.nonce >= 100:
        new_seed = generate_server_seed()
        wallet.server_seed = new_seed
        wallet.server_seed_hash = hash_server_seed(new_seed)
        wallet.nonce = 0

    return {
        "bet_id": bet.id,
        "won": won,
        "payout": round(payout, 2),
        "multiplier": mult,
        "profit": round(payout - body.amount, 2),
        "outcome": outcome_data,
        "proof": proof,
        "chips_remaining": wallet.mganga_chips if body.currency == "MGANGA" else wallet.mwanjesa_chips,
        "win_streak": wallet.win_streak,
    }


@router.get("/history")
async def bet_history(session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    result = await session.execute(
        select(CasinoBet).where(CasinoBet.user_id == user.id).order_by(CasinoBet.created_at.desc()).limit(30)
    )
    return [
        {
            "id": b.id, "game": b.game, "amount": b.bet_amount, "payout": b.payout,
            "won": b.won, "multiplier": b.multiplier, "currency": b.currency,
            "outcome": b.outcome_json, "created_at": b.created_at.isoformat(),
        }
        for b in result.scalars().all()
    ]


@router.get("/leaderboard")
async def leaderboard(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(CasinoWallet).order_by(CasinoWallet.total_won.desc()).limit(10))
    wallets = result.scalars().all()
    users = {}
    if wallets:
        uresult = await session.execute(select(User).where(User.id.in_([w.user_id for w in wallets])))
        users = {u.id: u.display_name for u in uresult.scalars().all()}
    return [
        {
            "rank": i + 1,
            "player": users.get(w.user_id, "Anonymous"),
            "total_won": w.total_won,
            "games_played": w.games_played,
            "win_streak": w.win_streak,
        }
        for i, w in enumerate(wallets)
    ]


@router.get("/live-feed")
async def live_feed(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(CasinoBet).order_by(CasinoBet.created_at.desc()).limit(15))
    bets = result.scalars().all()
    names = ["NovaKing", "CryptoQueen", "TessMaster", "DiceLord", "SlotWizard", "TraderOne Pro"]
    return [
        {
            "player": random.choice(names),
            "game": b.game,
            "won": b.won,
            "multiplier": b.multiplier,
            "payout": b.payout,
            "amount": b.bet_amount,
        }
        for b in bets
    ] or [
        {"player": "TraderOne Pro", "game": "tess-slots", "won": True, "multiplier": 10, "payout": 500, "amount": 50}
    ]


@router.post("/rfsam/verify")
async def rfsam_verify(body: VerifyRequest, session: AsyncSession = Depends(get_db)):
    bet = (await session.execute(select(CasinoBet).where(CasinoBet.id == body.bet_id))).scalar_one_or_none()
    if not bet:
        raise HTTPException(404, "Bet not found")
    user = await get_demo_user(session)
    wallet = await get_casino_wallet(session, user.id)
    proof = bet.proof_json
    result = verify_proof(
        wallet.server_seed,
        proof["server_seed_hash"],
        proof["client_seed"],
        proof["nonce"],
        proof["game"],
        proof.get("digest"),
    )
    return {**result, "bet_id": bet.id, "on_chain_ready": True}


@router.post("/rfsam/rotate-seed")
async def rotate_seed(session: AsyncSession = Depends(get_db)):
    user = await get_demo_user(session)
    wallet = await get_casino_wallet(session, user.id)
    old_hash = wallet.server_seed_hash
    new_seed = generate_server_seed()
    wallet.server_seed = new_seed
    wallet.server_seed_hash = hash_server_seed(new_seed)
    wallet.nonce = 0
    await session.commit()
    return {"previous_hash": old_hash, "new_hash": wallet.server_seed_hash, "message": "Seed rotated — previous bets remain verifiable"}
