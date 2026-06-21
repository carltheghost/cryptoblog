"""SwarmEngine: many agents trading one shared simulated market in real time.

This powers the "command center" dashboard -- the rich, multi-panel look of the
quant dashboards people post, but with HONEST numbers. Every agent is a real
strategy booking real paper fills against the same market, paying real modeled
fees. The leaderboard can (and does) go red. No real money, ever.
"""

from __future__ import annotations

import threading
import time
import random
from collections import deque

from ..paper_account import PaperAccount
from ..strategy import StrategyContext, make_strategy
from ..multiagent import default_roster, _contract_price

DURATION = 15 * 60
VOL = 7.3


class _Agent:
    def __init__(self, spec, start_balance):
        self.spec = spec
        self.acct = PaperAccount(cash=start_balance)
        self.strat = make_strategy(spec.strategy, spec.entry_velocity, spec.take_profit)
        self.equity_hist = deque(maxlen=120)
        self.equity_hist.append(start_balance)
        self.last_action = "hold"
        self.activity = 0.0


class SwarmEngine:
    def __init__(self, n_agents: int = 8, start_balance: float = 21.0):
        self.lock = threading.Lock()
        self.rng = random.Random(7)
        self.start_balance = start_balance
        self.params = {"spread": 0.02, "contracts": 10, "speed": 8.0, "signal_edge": 0.0}
        self.n_agents = n_agents
        self._running = False
        self._stop = False
        self._reset()
        threading.Thread(target=self._loop, daemon=True).start()

    def _reset(self):
        self.agents = [_Agent(s, self.start_balance) for s in default_roster(self.n_agents)]
        self.target = 71000.0
        self.price = self.target + self.rng.uniform(-50, 50)
        self.history = deque([self.price], maxlen=200)
        self.drift = 0.0
        self.imbalance = 0.0
        self.t = 0
        self.markets_done = 0
        self.events = deque(maxlen=30)

    # ---- controls ----
    def start(self):
        with self.lock:
            self._running = True

    def pause(self):
        with self.lock:
            self._running = False

    def reset(self):
        with self.lock:
            self._reset()

    def set_params(self, **kw):
        with self.lock:
            if "agents" in kw:
                try:
                    self.n_agents = max(1, min(25, int(kw.pop("agents"))))
                    self._reset()
                except (TypeError, ValueError):
                    kw.pop("agents", None)
            for k, v in kw.items():
                if k in self.params:
                    try:
                        self.params[k] = float(v)
                    except (TypeError, ValueError):
                        pass

    # ---- loop ----
    def _loop(self):
        while not self._stop:
            with self.lock:
                running, speed = self._running, max(0.5, self.params["speed"])
            if running:
                self._tick()
            time.sleep(1.0 / speed)

    def _tick(self):
        with self.lock:
            p = self.params
            self.drift = self.drift * 0.92 + self.rng.gauss(0, 1.6)
            self.price += self.drift + self.rng.gauss(0, 6.0)
            self.history.append(self.price)
            self.t += 1
            true_sig = max(-1.0, min(1.0, self.drift / 8.0))
            edge = p["signal_edge"]
            self.imbalance = max(-1.0, min(1.0,
                              edge * true_sig + (1 - edge) * self.rng.uniform(-1, 1)))
            seconds_left = DURATION - self.t

            for a in self.agents:
                a.activity *= 0.7

            if seconds_left <= 0:
                up = self.price > self.target
                for a in self.agents:
                    for side in ("yes", "no"):
                        key = f"M:{side}"
                        if key in a.acct.positions:
                            won = up if side == "yes" else not up
                            a.acct.settle("M", side, won=won)
                    a.equity_hist.append(round(a.acct.equity(), 2))
                self.markets_done += 1
                self.events.appendleft(f"market #{self.markets_done} settled "
                                       f"{'UP' if up else 'DOWN'}")
                self.t = 0
                self.target = round(self.price + self.rng.uniform(-40, 40), 2)
                return

            fair = _contract_price(self.price - self.target, seconds_left, VOL)
            yes_ask = min(0.99, fair + p["spread"] / 2)
            yes_bid = max(0.01, fair - p["spread"] / 2)
            no_ask = min(0.99, (1 - fair) + p["spread"] / 2)
            velocity = self.price - self.history[max(0, len(self.history) - 11)]
            path = tuple(self.history)[-90:]

            for a in self.agents:
                yk, nk = "M:yes", "M:no"
                hy, hn = yk in a.acct.positions, nk in a.acct.positions
                side = "yes" if hy else "no" if hn else None
                if hy:
                    unreal = yes_bid - a.acct.positions[yk].avg_price
                elif hn:
                    unreal = (1 - yes_ask) - a.acct.positions[nk].avg_price
                else:
                    unreal = 0.0
                ctx = StrategyContext(velocity=velocity, seconds_left=seconds_left,
                                      have_position=side is not None, side_held=side,
                                      unrealized=unreal, fair=fair, spread=p["spread"],
                                      imbalance=self.imbalance, prices=path,
                                      price=self.price, target=self.target,
                                      seconds_total=DURATION)
                sig = a.strat.decide(ctx)
                n = max(1, int(round(p["contracts"] * sig.size_frac)))
                acted = False
                if sig.action == "buy_yes":
                    acted = a.acct.buy("M", "yes", n, yes_ask, sig.reason)
                elif sig.action == "buy_no":
                    acted = a.acct.buy("M", "no", n, no_ask, sig.reason)
                elif sig.action == "take_profit":
                    if hy:
                        acted = a.acct.sell("M", "yes", a.acct.positions[yk].contracts, yes_bid)
                    elif hn:
                        acted = a.acct.sell("M", "no", a.acct.positions[nk].contracts, 1 - yes_ask)
                if acted:
                    a.last_action = sig.action
                    a.activity = 1.0
                a.equity_hist.append(round(a.acct.equity(), 2))

    def snapshot(self) -> dict:
        with self.lock:
            rows = []
            for a in self.agents:
                eq = a.acct.equity()
                rows.append({
                    "label": a.spec.label, "strategy": a.spec.strategy,
                    "equity": round(eq, 2), "pnl": round(eq - self.start_balance, 2),
                    "realized": round(a.acct.realized_pnl, 2),
                    "fees": round(a.acct.total_fees_paid, 2),
                    "trades": len(a.acct.fills),
                    "activity": round(a.activity, 2),
                    "spark": list(a.equity_hist),
                    "positions": len(a.acct.positions),
                })
            rows.sort(key=lambda r: r["equity"], reverse=True)
            total_eq = sum(r["equity"] for r in rows)
            total_fees = sum(r["fees"] for r in rows)
            invested = self.start_balance * len(rows)

            # SUPERVISOR: a monitor/allocator meta-agent. It aggregates per-strategy
            # performance and issues a directive. It reallocates attention toward
            # what is working -- it does NOT invent edge. On zero-edge data it just
            # surfaces the least-bad, honestly.
            by_strat: dict[str, list[float]] = {}
            for r in rows:
                by_strat.setdefault(r["strategy"], []).append(r["pnl"])
            strat_avg = {s: sum(v) / len(v) for s, v in by_strat.items()}
            ranked = sorted(strat_avg.items(), key=lambda kv: kv[1], reverse=True)
            best_s, best_v = ranked[0]
            worst_s, worst_v = ranked[-1]
            edge_on = self.params["signal_edge"] > 0
            if best_v > 0 and edge_on:
                directive = (f"Allocating toward '{best_s}' (+${best_v:.2f}/agent). "
                             f"NOTE: only profitable because signal_edge is assumed "
                             f"at {self.params['signal_edge']:.0%} — not proven.")
            elif best_v > 0:
                directive = (f"'{best_s}' leads (+${best_v:.2f}/agent), but at 0 edge this "
                             f"is noise/variance, not a real signal. Holding course.")
            else:
                directive = (f"All strategies net-negative. Least-bad: '{best_s}' "
                             f"(${best_v:.2f}). Cutting turnover, not adding agents.")
            supervisor = {
                "directive": directive,
                "best_strategy": best_s, "worst_strategy": worst_s,
                "ranking": [{"strategy": s, "avg_pnl": round(v, 2)} for s, v in ranked],
            }
            return {
                "running": self._running,
                "n_agents": len(rows),
                "price": round(self.price, 2), "target": round(self.target, 2),
                "imbalance": round(self.imbalance, 2),
                "seconds_left": DURATION - self.t,
                "markets_done": self.markets_done,
                "params": dict(self.params),
                "history": list(self.history),
                "agents": rows,
                "totals": {"equity": round(total_eq, 2), "invested": round(invested, 2),
                           "pnl": round(total_eq - invested, 2), "fees": round(total_fees, 2),
                           "winners": sum(1 for r in rows if r["pnl"] > 0)},
                "supervisor": supervisor,
                "events": list(self.events),
            }
