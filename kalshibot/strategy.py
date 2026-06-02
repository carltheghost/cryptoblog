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

import math
import statistics
from dataclasses import dataclass, field


@dataclass
class Signal:
    action: str          # "buy_yes", "buy_no", "take_profit", "hold"
    reason: str
    size_frac: float = 1.0   # fraction of the configured trade size to use (Kelly)


@dataclass
class StrategyContext:
    velocity: float          # recent BTC index change in dollars (signed)
    seconds_left: int
    have_position: bool
    side_held: str | None    # "yes", "no", or None
    unrealized: float        # per-contract gain in dollars at current bid
    fair: float              # model fair "yes" price (0..1)
    spread: float            # current bid/ask spread in dollars
    imbalance: float = 0.0   # order-book imbalance, -1 (sell) .. +1 (buy)
    prices: tuple = ()       # recent underlying path (oldest..newest)
    price: float = 0.0       # current underlying price
    target: float = 0.0      # market target/strike
    seconds_total: int = 900 # full market duration in seconds


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


class OrderBookImbalanceStrategy(Strategy):
    """Trade a *real* predictive signal: order-book imbalance. Strong buy-side
    depth (positive imbalance) leans the next moves up, and vice versa. Enters in
    the imbalance direction when the book is tight, then holds to settlement
    (low turnover, same disciplined chassis as `spread`).

    This is the strategy to A/B for an actual edge. In the simulation its signal
    quality is governed by `signal_edge` (0 = pure noise -> still loses to fees;
    higher = more genuine predictive power). On live paper data the imbalance is
    computed from the real Kalshi order book, so the P&L tells you the truth."""
    name = "imbalance"
    entry_imbalance: float = 0.35    # |imbalance| needed to act
    max_spread: float = 0.02

    def decide(self, ctx: StrategyContext) -> Signal:
        if ctx.have_position:
            return Signal("hold", "holding to settlement")
        if ctx.seconds_left < max(self.min_seconds_left, 120):
            return Signal("hold", "no time for thesis to play out")
        if ctx.spread > self.max_spread:
            return Signal("hold", f"spread {ctx.spread:.2f} too wide")
        if ctx.imbalance >= self.entry_imbalance:
            return Signal("buy_yes", f"book imbalance {ctx.imbalance:+.2f}")
        if ctx.imbalance <= -self.entry_imbalance:
            return Signal("buy_no", f"book imbalance {ctx.imbalance:+.2f}")
        return Signal("hold", "book balanced")


def _phi(x: float) -> float:
    """Standard normal CDF."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _ols_slope(ys) -> float:
    """Least-squares slope of ys against its index (drift per second)."""
    n = len(ys)
    if n < 2:
        return 0.0
    xm = (n - 1) / 2.0
    ym = sum(ys) / n
    num = sum((i - xm) * (ys[i] - ym) for i in range(n))
    den = sum((i - xm) ** 2 for i in range(n)) or 1.0
    return num / den


def _autocorr1(r) -> float:
    """Lag-1 autocorrelation of returns: >0 trending, <0 mean-reverting."""
    n = len(r)
    if n < 3:
        return 0.0
    m = sum(r) / n
    num = sum((r[i] - m) * (r[i - 1] - m) for i in range(1, n))
    den = sum((x - m) ** 2 for x in r) or 1.0
    return num / den


class ChronosBridgeStrategy(Strategy):
    """Bidirectional Brownian-bridge strategy.

    Anchored at *now* (the middle of the 15-min window), it reasons in both time
    directions and trades only on a cost-adjusted edge, sized by fractional Kelly:

      backward (now -> start): estimate drift (OLS slope), regime (return lag-1
        autocorrelation -> trend vs revert), and realized volatility from the path.
      forward  (now -> expiry): Brownian-bridge settlement probability
        Phi(distance / (sigma*sqrt(time_left))), bent by the regime and nudged by
        live order-book imbalance.
      vice versa (expiry -> now): every tick it re-derives the edge and EXITS if
        the bridge flips against the held side -- the future overruling the present.

    Trades only when expected value beats the round-trip cost (spread + entry fee),
    then holds. This is principled complexity, not complexity for its own sake --
    and it competes in the same honest backtest as everything else.
    """
    name = "chronos"
    drift_kappa: float = 0.6     # how much estimated drift bends the forward prob
    micro_lambda: float = 0.20   # order-book imbalance weight
    kelly_fraction: float = 0.4  # fraction of full Kelly to actually size at
    edge_buffer: float = 0.025   # required EV cushion above modeled cost
    max_spread: float = 0.03
    exit_flip: float = 0.06      # exit only on a decisive adverse flip
    cooldown: int = 120          # min seconds between entries (anti-churn)

    def _estimate(self, ctx: StrategyContext) -> float:
        """Return the fused fair 'yes' probability p_hat (0..1)."""
        prices = ctx.prices
        # Without an underlying path (e.g. live paper with only quotes), fall back
        # to the market's own fair plus a microstructure nudge. No path = no edge.
        if len(prices) < 6:
            return min(0.99, max(0.01, ctx.fair + self.micro_lambda * ctx.imbalance * 0.25))

        tau = max(1, ctx.seconds_left)
        S = prices[-1]
        d = S - ctx.target
        rets = [prices[i + 1] - prices[i] for i in range(len(prices) - 1)]
        sigma = statistics.pstdev(rets) or 1.0

        # backward leg: drift + regime
        mu = _ols_slope(prices)
        rho = _autocorr1(rets)
        trend = 1.0 if rho >= 0 else -1.0           # persist vs revert
        eff_mu = self.drift_kappa * mu * trend

        # forward leg: regime-adjusted Brownian-bridge settlement probability
        p_dyn = _phi((d + eff_mu * tau) / (sigma * math.sqrt(tau)))
        # microstructure nudge (matters more as the book tightens)
        p_hat = p_dyn + self.micro_lambda * ctx.imbalance * 0.25
        return min(0.99, max(0.01, p_hat))

    def decide(self, ctx: StrategyContext) -> Signal:
        p_hat = self._estimate(ctx)
        edge = p_hat - ctx.fair   # signed: >0 favors yes, <0 favors no

        if ctx.have_position:
            if ctx.unrealized >= self.take_profit:
                self._cd = self.cooldown
                return Signal("take_profit", f"tp {ctx.unrealized:+.2f}")
            held_yes = ctx.side_held == "yes"
            against = (held_yes and edge < -self.exit_flip) or \
                      (not held_yes and edge > self.exit_flip)
            if against:
                self._cd = self.cooldown
                return Signal("take_profit", f"bridge flipped (edge {edge:+.2f})")
            return Signal("hold", "bridge intact")

        cd = getattr(self, "_cd", 0)
        if cd > 0:
            self._cd = cd - 1
            return Signal("hold", "cooldown")
        if ctx.seconds_left < max(self.min_seconds_left, 120):
            return Signal("hold", "too late for the bridge")
        if ctx.spread > self.max_spread:
            return Signal("hold", "book too wide to pay")

        # cost gate: entry fee (~0.07*p*(1-p)) + half-spread crossing
        fee = 0.07 * ctx.fair * (1 - ctx.fair)
        ev_yes = p_hat - (ctx.fair + ctx.spread / 2) - fee
        ev_no = (ctx.fair - p_hat) - ctx.spread / 2 - fee
        ev, action = (ev_yes, "buy_yes") if ev_yes >= ev_no else (ev_no, "buy_no")
        if ev <= self.edge_buffer:
            return Signal("hold", f"EV {ev:+.3f} below cost")

        # fractional Kelly sizing on the implied edge, bounded 0.2..1.0
        size = max(0.2, min(1.0, self.kelly_fraction * ev / 0.05))
        self._cd = self.cooldown
        return Signal(action, f"EV {ev:+.3f}, p_hat {p_hat:.2f} vs {ctx.fair:.2f}", size)


STRATEGIES = {
    "momentum": MomentumStrategy,
    "fade": FadeExtremesStrategy,
    "spread": SpreadAwareStrategy,
    "imbalance": OrderBookImbalanceStrategy,
    "chronos": ChronosBridgeStrategy,
}


def make_strategy(name: str, entry_velocity: float = 25.0,
                  take_profit: float = 0.06) -> Strategy:
    cls = STRATEGIES.get(name, MomentumStrategy)
    s = cls()
    s.entry_velocity = entry_velocity
    s.take_profit = take_profit
    return s
