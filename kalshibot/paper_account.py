"""A simulated (paper) Kalshi account.

Tracks cash, open positions, realized P&L and a full trade log. Fills are
modeled honestly: you buy at the ask, sell at the bid, and pay the trading fee
on every leg. No fill is ever free.

Contracts settle at $1.00 if the side wins and $0.00 if it loses.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from . import fees


@dataclass
class Fill:
    ts: str
    market: str
    side: str            # "yes" or "no"
    action: str          # "buy" or "sell"
    contracts: int
    price: float         # dollars, 0..1
    fee: float
    note: str = ""


@dataclass
class Position:
    market: str
    side: str
    contracts: int
    avg_price: float     # average cost basis in dollars


@dataclass
class PaperAccount:
    cash: float = 21.0
    fee_rate: float = fees.DEFAULT_FEE_RATE
    positions: dict[str, Position] = field(default_factory=dict)
    fills: list[Fill] = field(default_factory=list)
    total_fees_paid: float = 0.0
    realized_pnl: float = 0.0

    def _key(self, market: str, side: str) -> str:
        return f"{market}:{side}"

    def buy(self, market: str, side: str, contracts: int, ask: float, note: str = "") -> bool:
        """Buy `contracts` of (market, side) at the ask. Returns False if too poor."""
        fee = fees.trading_fee(ask, contracts, self.fee_rate)
        cost = ask * contracts + fee
        if cost > self.cash + 1e-9:
            return False
        self.cash -= cost
        self.total_fees_paid += fee
        key = self._key(market, side)
        pos = self.positions.get(key)
        if pos is None:
            self.positions[key] = Position(market, side, contracts, ask)
        else:
            total = pos.contracts + contracts
            pos.avg_price = (pos.avg_price * pos.contracts + ask * contracts) / total
            pos.contracts = total
        self._log(market, side, "buy", contracts, ask, fee, note)
        return True

    def sell(self, market: str, side: str, contracts: int, bid: float, note: str = "") -> bool:
        """Sell (close) up to `contracts` of an existing position at the bid."""
        key = self._key(market, side)
        pos = self.positions.get(key)
        if pos is None or pos.contracts < contracts:
            return False
        fee = fees.trading_fee(bid, contracts, self.fee_rate)
        proceeds = bid * contracts - fee
        self.cash += proceeds
        self.total_fees_paid += fee
        self.realized_pnl += (bid - pos.avg_price) * contracts - fee
        pos.contracts -= contracts
        if pos.contracts == 0:
            del self.positions[key]
        self._log(market, side, "sell", contracts, bid, fee, note)
        return True

    def settle(self, market: str, side: str, won: bool) -> None:
        """Settle an open position at expiration: $1 if won else $0."""
        key = self._key(market, side)
        pos = self.positions.get(key)
        if pos is None:
            return
        payout = (1.0 if won else 0.0) * pos.contracts
        self.cash += payout
        self.realized_pnl += payout - pos.avg_price * pos.contracts
        self._log(market, side, "settle", pos.contracts,
                  1.0 if won else 0.0, 0.0, f"settled {'WON' if won else 'LOST'}")
        del self.positions[key]

    def equity(self, marks: dict[str, float] | None = None) -> float:
        """Cash plus mark-to-market value of open positions."""
        marks = marks or {}
        value = self.cash
        for key, pos in self.positions.items():
            value += marks.get(key, pos.avg_price) * pos.contracts
        return value

    def _log(self, market, side, action, contracts, price, fee, note):
        self.fills.append(Fill(
            ts=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            market=market, side=side, action=action,
            contracts=contracts, price=price, fee=fee, note=note,
        ))

    def summary(self) -> str:
        return (
            f"cash=${self.cash:.2f}  realized_pnl=${self.realized_pnl:+.2f}  "
            f"fees_paid=${self.total_fees_paid:.2f}  trades={len(self.fills)}  "
            f"open_positions={len(self.positions)}"
        )
