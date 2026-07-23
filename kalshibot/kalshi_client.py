"""Read-only Kalshi market-data client (+ a clearly gated live-trading note).

Credentials are read from the environment, NEVER hardcoded:
    KALSHI_API_KEY_ID      - your API key UUID
    KALSHI_PRIVATE_KEY     - path to your RSA private key .pem (live trading only)

Market-data reads below need no auth. Placing orders does, and is intentionally
left as a guarded method that raises unless you explicitly opt in. Do a paper
run first.

NOTE: From some networks/data centers Kalshi returns HTTP 403 (Cloudflare /
geo / policy). If so, run this from your own machine.
"""

from __future__ import annotations

import os
import requests

BASE_URL = os.environ.get(
    "KALSHI_BASE_URL", "https://api.elections.kalshi.com/trade-api/v2"
)

# The 7 crypto underlyings Kalshi runs short-term markets on. The LIQUID ones are
# the 15-minute up/down markets, series "<COIN>15M". The bare "KX<COIN>" series are
# longer-dated strike ladders that are mostly illiquid (all-zero quotes).
CRYPTO_15M_SERIES = ["KXBTC15M", "KXETH15M", "KXSOL15M", "KXXRP15M",
                     "KXDOGE15M", "KXBNB15M", "KXHYPE15M"]
DEFAULT_CRYPTO_SERIES = CRYPTO_15M_SERIES

# Perpetual futures launched 2026-05-29 but use a SEPARATE API (perps_openapi.yaml)
# that is NOT the /markets/{ticker} endpoint -- bare tickers 404 there. Endpoint
# unverified, so perps probing is opt-in and self-stops on 404.
PERPS_BASE_URL = "https://external-api.kalshi.com/trade-api/v2"
PERP_TICKERS = ["BTCPERP", "ETHPERP", "XRPPERP", "SOLPERP", "DOGEPERP"]


class KalshiClient:
    def __init__(self, base_url: str = BASE_URL, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    # ---- read-only market data (no auth) ----------------------------------
    def _get(self, path: str, **params):
        r = self.session.get(f"{self.base_url}{path}", params=params, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def exchange_status(self) -> dict:
        return self._get("/exchange/status")

    def list_markets(self, series_ticker: str | None = None, status: str = "open",
                     limit: int = 100) -> list[dict]:
        params = {"status": status, "limit": limit}
        if series_ticker:
            params["series_ticker"] = series_ticker
        return self._get("/markets", **params).get("markets", [])

    def get_market(self, ticker: str) -> dict:
        return self._get(f"/markets/{ticker}").get("market", {})

    def get_orderbook(self, ticker: str, depth: int = 5) -> dict:
        return self._get(f"/markets/{ticker}/orderbook", depth=depth).get("orderbook", {})

    @staticmethod
    def best_bid_ask(market: dict) -> tuple[float, float]:
        """Return (yes_bid, yes_ask) in dollars from a market dict.

        Kalshi's current API returns prices as `*_dollars` STRING fields
        (e.g. "0.6900"). Older responses used integer cents (yes_bid 1..99).
        This reads the new fields, falls back to legacy cents, and derives the
        yes side from the no side when only the no book is quoted (binary
        complement: yes_bid = 1 - no_ask, yes_ask = 1 - no_bid)."""
        def f(*keys):
            for k in keys:
                v = market.get(k)
                if v not in (None, ""):
                    try:
                        return float(v)
                    except (TypeError, ValueError):
                        pass
            return 0.0

        yb = f("yes_bid_dollars")
        ya = f("yes_ask_dollars")
        nb = f("no_bid_dollars")
        na = f("no_ask_dollars")
        if yb == 0 and ya == 0:                      # legacy integer-cent fields
            cb, ca = market.get("yes_bid"), market.get("yes_ask")
            if cb or ca:
                yb, ya = (cb or 0) / 100.0, (ca or 0) / 100.0
        if yb == 0 and na > 0:                       # derive yes from no side
            yb = round(1.0 - na, 4)
        if ya == 0 and nb > 0:
            ya = round(1.0 - nb, 4)
        return yb, ya

    # ---- live trading (intentionally disabled) ----------------------------
    def place_order(self, *args, **kwargs):
        raise PermissionError(
            "Live order placement is disabled in this client. Real-money "
            "trading requires RSA request signing and an explicit opt-in. "
            "Run a paper/backtest and confirm a positive edge first."
        )
