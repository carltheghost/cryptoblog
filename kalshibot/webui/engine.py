"""Background simulation engine that powers the web UI.

Runs a synthetic 15-minute BTC target market in a thread, feeds the selected
strategy, books fills into a PaperAccount, and exposes a thread-safe snapshot of
everything for the browser to render. No real orders, ever.
"""

from __future__ import annotations

import random
import threading
import time
from collections import deque

from ..paper_account import PaperAccount
from ..strategy import StrategyContext, make_strategy, STRATEGIES
from ..backtest import _contract_price


class SimEngine:
    MARKET = "BTC-15MIN"
    DURATION = 15 * 60          # seconds per market
    VOL = 7.0                   # $/sqrt(sec), ~3% daily on $71k

    def __init__(self, start_balance: float = 21.0):
        self.lock = threading.Lock()
        self.rng = random.Random(42)
        self.start_balance = start_balance

        self.params = {
            "entry_velocity": 25.0,
            "take_profit": 0.06,
            "contracts": 10,
            "spread": 0.02,
            "speed": 8.0,         # simulated ticks per real second
            "signal_edge": 0.0,   # imbalance signal quality, 0..1
        }
        self.strategy_name = "momentum"

        self.history = deque(maxlen=180)        # recent prices
        self.equity_hist = deque(maxlen=180)    # equity curve
        self.fees_hist = deque(maxlen=180)      # cumulative fees
        self.events = deque(maxlen=40)
        self.agents = {
            "feed": 0.0, "momentum": 0.0, "risk": 0.0, "account": 0.0, "notifier": 0.0,
        }
        self.pulses = []

        self._running = False
        self._stop = False
        self._reset_state()

        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    # ---- lifecycle --------------------------------------------------------
    def _reset_state(self):
        self.acct = PaperAccount(cash=self.start_balance)
        self.strat = make_strategy(self.strategy_name,
                                   self.params["entry_velocity"], self.params["take_profit"])
        self.target = 71000.0
        self.price = self.target + self.rng.uniform(-50, 50)
        self.drift = 0.0
        self.imbalance = 0.0
        self.t = 0
        self.history.clear(); self.history.append(self.price)
        self.equity_hist.clear(); self.equity_hist.append(self.start_balance)
        self.fees_hist.clear(); self.fees_hist.append(0.0)
        self.last_signal = {"action": "hold", "reason": "idle"}
        for k in self.agents:
            self.agents[k] = 0.0

    def start(self):
        with self.lock:
            self._running = True
            self._log("agents started")

    def pause(self):
        with self.lock:
            self._running = False
            self._log("agents paused")

    def reset(self):
        with self.lock:
            self._reset_state()
            self._log("session reset")

    def set_params(self, **kw):
        with self.lock:
            name = kw.pop("strategy", None)
            if name in STRATEGIES and name != self.strategy_name:
                self.strategy_name = name
                self.strat = make_strategy(name, self.params["entry_velocity"],
                                           self.params["take_profit"])
                self._log(f"strategy -> {name}")
            for k, v in kw.items():
                if k in self.params:
                    try:
                        self.params[k] = float(v)
                    except (TypeError, ValueError):
                        pass
            self.strat.entry_velocity = self.params["entry_velocity"]
            self.strat.take_profit = self.params["take_profit"]

    # ---- main loop --------------------------------------------------------
    def _loop(self):
        while not self._stop:
            with self.lock:
                running = self._running
                speed = max(0.5, self.params["speed"])
            if running:
                self._tick()
            time.sleep(1.0 / speed)

    def _tick(self):
        with self.lock:
            p = self.params
            for k in self.agents:
                self.agents[k] *= 0.75
            self.pulses = [pulse for pulse in self.pulses if pulse["age"] < 6]
            for pulse in self.pulses:
                pulse["age"] += 1

            # 1) FEED: persistent drift + noise; imbalance partially reveals drift
            self.drift = self.drift * 0.92 + self.rng.gauss(0, 1.6)
            self.price += self.drift + self.rng.gauss(0, 6.0)
            true_sig = max(-1.0, min(1.0, self.drift / 8.0))
            edge = p["signal_edge"]
            self.imbalance = max(-1.0, min(1.0,
                              edge * true_sig + (1 - edge) * self.rng.uniform(-1, 1)))
            self.t += 1
            self.history.append(self.price)
            self.agents["feed"] = 1.0
            seconds_left = self.DURATION - self.t

            if seconds_left <= 0:
                won = self.price > self.target
                if f"{self.MARKET}:yes" in self.acct.positions:
                    self.acct.settle(self.MARKET, "yes", won=won)
                if f"{self.MARKET}:no" in self.acct.positions:
                    self.acct.settle(self.MARKET, "no", won=not won)
                self.agents["account"] = 1.0
                self._pulse("account", "notifier")
                self._log(f"market expired {'UP' if won else 'DOWN'} -> settled")
                self.t = 0
                self.target = round(self.price + self.rng.uniform(-40, 40), 2)
                self._record_curves()
                return

            velocity = self.price - self.history[max(0, len(self.history) - 11)]
            distance = self.price - self.target
            fair = _contract_price(distance, seconds_left, 7.3)
            yes_ask = min(0.99, fair + p["spread"] / 2)
            yes_bid = max(0.01, fair - p["spread"] / 2)
            no_ask = min(0.99, (1 - fair) + p["spread"] / 2)
            self.yes_bid, self.yes_ask = yes_bid, yes_ask
            self.velocity, self.seconds_left, self.fair = velocity, seconds_left, fair

            key_yes, key_no = f"{self.MARKET}:yes", f"{self.MARKET}:no"
            have_yes, have_no = key_yes in self.acct.positions, key_no in self.acct.positions
            side_held = "yes" if have_yes else "no" if have_no else None
            if have_yes:
                unreal = yes_bid - self.acct.positions[key_yes].avg_price
            elif have_no:
                unreal = (1 - yes_ask) - self.acct.positions[key_no].avg_price
            else:
                unreal = 0.0

            ctx = StrategyContext(velocity=velocity, seconds_left=seconds_left,
                                  have_position=side_held is not None, side_held=side_held,
                                  unrealized=unreal, fair=fair, spread=p["spread"],
                                  imbalance=self.imbalance)
            sig = self.strat.decide(ctx)
            self.agents["momentum"] = max(self.agents["momentum"], 0.5)

            n = int(p["contracts"])
            acted = False
            if sig.action == "buy_yes":
                acted = self.acct.buy(self.MARKET, "yes", n, yes_ask, sig.reason)
            elif sig.action == "buy_no":
                acted = self.acct.buy(self.MARKET, "no", n, no_ask, sig.reason)
            elif sig.action == "take_profit":
                if have_yes:
                    acted = self.acct.sell(self.MARKET, "yes",
                                           self.acct.positions[key_yes].contracts, yes_bid, sig.reason)
                elif have_no:
                    acted = self.acct.sell(self.MARKET, "no",
                                           self.acct.positions[key_no].contracts, 1 - yes_ask, sig.reason)

            if acted:
                self.last_signal = {"action": sig.action, "reason": sig.reason}
                self.agents["momentum"] = 1.0
                self.agents["risk"] = 1.0
                self.agents["account"] = 1.0
                self.agents["notifier"] = 1.0
                self._pulse("feed", "momentum"); self._pulse("momentum", "risk")
                self._pulse("risk", "account"); self._pulse("account", "notifier")
                self._log(f"{sig.action}  ({sig.reason})  fees=${self.acct.total_fees_paid:.2f}")

            self._record_curves()

    # ---- helpers ----------------------------------------------------------
    def _record_curves(self):
        self.equity_hist.append(round(self.acct.equity(), 2))
        self.fees_hist.append(round(self.acct.total_fees_paid, 2))

    def _pulse(self, src, dst):
        self.pulses.append({"src": src, "dst": dst, "age": 0})

    def _log(self, msg):
        self.events.appendleft(time.strftime("%H:%M:%S") + "  " + msg)

    def snapshot(self) -> dict:
        with self.lock:
            positions = [
                {"market": p.market, "side": p.side, "contracts": p.contracts,
                 "avg_price": round(p.avg_price, 3)}
                for p in self.acct.positions.values()
            ]
            return {
                "running": self._running,
                "strategy": self.strategy_name,
                "strategies": list(STRATEGIES.keys()),
                "tick": self.t,
                "seconds_left": getattr(self, "seconds_left", self.DURATION),
                "price": round(self.price, 2),
                "target": round(self.target, 2),
                "velocity": round(getattr(self, "velocity", 0.0), 1),
                "imbalance": round(getattr(self, "imbalance", 0.0), 2),
                "yes_bid": round(getattr(self, "yes_bid", 0.5), 2),
                "yes_ask": round(getattr(self, "yes_ask", 0.5), 2),
                "fair": round(getattr(self, "fair", 0.5), 3),
                "history": list(self.history),
                "equity_history": list(self.equity_hist),
                "fees_history": list(self.fees_hist),
                "account": {
                    "cash": round(self.acct.cash, 2),
                    "equity": round(self.acct.equity(), 2),
                    "realized_pnl": round(self.acct.realized_pnl, 2),
                    "fees": round(self.acct.total_fees_paid, 2),
                    "trades": len(self.acct.fills),
                    "positions": positions,
                },
                "last_signal": self.last_signal,
                "params": dict(self.params),
                "agents": dict(self.agents),
                "pulses": list(self.pulses),
                "events": list(self.events),
            }
