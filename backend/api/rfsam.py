"""RF-SAM: Random Fair Seed Attestation Module — provably fair casino proofs."""

import hashlib
import hmac
import secrets
from typing import Optional


def generate_server_seed() -> str:
    return secrets.token_hex(32)


def hash_server_seed(server_seed: str) -> str:
    return hashlib.sha256(server_seed.encode()).hexdigest()


def derive_result(server_seed: str, client_seed: str, nonce: int, game: str) -> dict:
    """Derive deterministic game outcome from seeds."""
    message = f"{client_seed}:{nonce}:{game}"
    digest = hmac.new(server_seed.encode(), message.encode(), hashlib.sha256).hexdigest()
    raw = int(digest[:16], 16)

    return {
        "digest": digest,
        "raw": raw,
        "float_0_1": (raw % 10_000_000) / 10_000_000,
        "dice_a": (raw % 6) + 1,
        "dice_b": ((raw >> 8) % 6) + 1,
        "roulette": raw % 37,
        "slot_r1": (raw % 8),
        "slot_r2": ((raw >> 4) % 8),
        "slot_r3": ((raw >> 8) % 8),
        "crash_point": max(1.0, round(1 + (raw % 9900) / 100, 2)),
        "wheel_segment": raw % 12,
        "lottery_4d": [
            (raw % 10),
            ((raw >> 4) % 10),
            ((raw >> 8) % 10),
            ((raw >> 12) % 10),
        ],
        "card_rank": (raw % 13) + 2,
        "card_suit": (raw >> 4) % 4,
    }


def verify_proof(
    server_seed: str,
    server_seed_hash: str,
    client_seed: str,
    nonce: int,
    game: str,
    claimed_digest: Optional[str] = None,
) -> dict:
    if hash_server_seed(server_seed) != server_seed_hash:
        return {"valid": False, "error": "Server seed does not match committed hash"}
    result = derive_result(server_seed, client_seed, nonce, game)
    if claimed_digest and result["digest"] != claimed_digest:
        return {"valid": False, "error": "Digest mismatch"}
    return {
        "valid": True,
        "server_seed_hash": server_seed_hash,
        "client_seed": client_seed,
        "nonce": nonce,
        "game": game,
        "digest": result["digest"],
        "outcome": result,
        "algorithm": "RF-SAM v1 (HMAC-SHA256)",
    }
