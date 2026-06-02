"""Trading strategies for the Kalshi short-term crypto markets.

Each strategy is just a decision function over a StrategyContext -> Signal. None
of them is assumed profitable; the backtest charges real fees + spread and ranks
them honestly. Three are provided so you can compare approaches:

  momentum  - the screenshot idea: ride the move, take small profits, churn.
  fade      - mean reversion: bet AGAINST overextended moves.
  spread    - disciplined: only enter on a strong signal when the spread is
              tight, then hold to settlement to avoid paying exit costs twice.

Pick via the web UI dropdown or the backtest's --strategy flag.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Signal:
    action: str          # "buy_yes", "buy_no", "take_profit", "hold"
    reason: str


@dataclass
class StrategyContext:
    velocity: float          # recent BTC index change in dollars (signed)
    seconds_left: int
    have_position: bool
    side_held: str | None    # "yes", "no", or None
    unrealized: float        # per-contract gain in dollars at current bid
    fair: float              # model fair "yes" price (0..1)
    spread: float            # current bid/ask spread in dollars


class Strategy:
    name = "base"
    # shared tunables; the UI/backtest set these
    entry_velocity: float = 25.0
    take_profit: float = 0.06
    min_seconds_left: int = 60

    def decide(self, ctx: StrategyContext) -> Signal:  # pragma: no cover
        raise NotImplementedError


class MomentumStrategy(Strategy):
    """Ride momentum, take small profits. High turnover -> high fee drag."""
    name = "momentum"

    def decide(self, ctx: StrategyContext) -> Signal:
        if ctx.have_position:
            if ctx.unrealized >= self.take_profit:
                return Signal("take_profit", f"unrealized {ctx.unrealized:+.2f} >= tp")
            return Signal("hold", "in position")
        if ctx.seconds_left < self.min_seconds_left:
            return Signal("hold", "too close to expiry")
        if ctx.velocity >= self.entry_velocity:
            return Signal("buy_yes", f"up-momentum {ctx.velocity:+.0f}")
        if ctx.velocity <= -self.entry_velocity:
            return Signal("buy_no", f"down-momentum {ctx.velocity:+.0f}")
        return Signal("hold", "no momentum")


class FadeExtremesStrategy(Strategy):
    """Mean reversion: a very large, fast move tends to pull back, so fade it."""
    name = "fade"

    def decide(self, ctx: StrategyContext) -> Signal:
        if ctx.have_position:
            if ctx.unrealized >= self.take_profit:
                return Signal("take_profit", f"reverted {ctx.unrealized:+.2f}")
            return Signal("hold", "waiting for reversion")
        if ctx.seconds_left < self.min_seconds_left:
            return Signal("hold", "too close to expiry")
        # require an *overextended* move: 1.5x the momentum threshold
        thresh = self.entry_velocity * 1.5
        if ctx.velocity >= thresh:
            return Signal("buy_no", f"fade spike {ctx.velocity:+.0f}")
        if ctx.velocity <= -thresh:
            return Signal("buy_yes", f"fade dump {ctx.velocity:+.0f}")
        return Signal("hold", "not overextended")


class SpreadAwareStrategy(Strategy):
    """Disciplined: only enter on a strong signal when the spread is tight, in
    the balanced part of the book, then HOLD to settlement. One entry, one exit
    (settlement) -> minimal cost. Trades rarely on purpose."""
    name = "spread"
    max_spread: float = 0.02     # skip if the book is wider than this

    def decide(self, ctx: StrategyContext) -> Signal:
        if ctx.have_position:
            return Signal("hold", "holding to settlement")
        if ctx.seconds_left < max(self.min_seconds_left, 120):
            return Signal("hold", "no time for thesis to play out")
        if ctx.spread > self.max_spread:
            return Signal("hold", f"spread {ctx.spread:.2f} too wide")
        if not (0.2 <= ctx.fair <= 0.8):
            return Signal("hold", "price too lopsided to pay")
        thresh = self.entry_velocity * 1.5   # demand a strong signal
        if ctx.velocity >= thresh:
            return Signal("buy_yes", f"strong up {ctx.velocity:+.0f}, tight book")
        if ctx.velocity <= -thresh:
            return Signal("buy_no", f"strong down {ctx.velocity:+.0f}, tight book")
        return Signal("hold", "signal not strong enough")


STRATEGIES = {
    "momentum": MomentumStrategy,
    "fade": FadeExtremesStrategy,
    "spread": SpreadAwareStrategy,
}


def make_strategy(name: str, entry_velocity: float = 25.0,
                  take_profit: float = 0.06) -> Strategy:
    cls = STRATEGIES.get(name, MomentumStrategy)
    s = cls()
    s.entry_velocity = entry_velocity
    s.take_profit = take_profit
    return s
