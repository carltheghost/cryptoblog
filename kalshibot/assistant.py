"""kalshibot personal assistant -- a local, natural-language control deck.

Run it on your own PC:

    python -m kalshibot.assistant

Talk to it in plain English: "start the spread strategy", "how am I doing?",
"run a backtest of chronos at edge 0.5", "compare everything", "open the
dashboard", "switch to momentum and set speed to 20".

It works with ZERO setup (a deterministic command understander). If you want
real conversational replies it auto-detects, in order:
  * a local Ollama server   (http://localhost:11434)         -> fully offline LLM
  * ANTHROPIC_API_KEY in env (uses the Claude API)           -> cloud LLM
Otherwise it stays in fast, rule-based mode. Either way it controls the same
in-process simulation engine. It is paper/sim only -- it never places real orders.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

from .webui.engine import SimEngine
from .strategy import STRATEGIES
from . import backtest as bt

PARAM_ALIASES = {
    "entry velocity": "entry_velocity", "velocity": "entry_velocity",
    "entry_velocity": "entry_velocity",
    "take profit": "take_profit", "tp": "take_profit", "take_profit": "take_profit",
    "contracts": "contracts", "size": "contracts",
    "spread": "spread",
    "speed": "speed",
    "signal edge": "signal_edge", "edge": "signal_edge", "signal_edge": "signal_edge",
}

HELP = """I'm your local kalshibot assistant. Things you can say:
  start / stop / reset                 - run, pause, or reset the agents
  use <strategy>                       - momentum | fade | spread | imbalance | chronos
  set <param> to <value>               - entry velocity, take profit, contracts,
                                         spread, speed, signal edge
  how am I doing? / status             - live P&L, fees, trades, positions
  backtest <strategy> [edge <0..1>]    - run an offline backtest
  compare / which is best              - rank all strategies
  dashboard                            - open the web UI in your browser
  help                                 - this message
  quit                                 - leave
Everything is paper/simulation. No real money, ever."""


# ----------------------------- intent parsing ------------------------------
def parse(text: str) -> dict:
    """Deterministic natural-language -> intent. Always available, no LLM needed."""
    t = text.strip().lower()
    if not t:
        return {"cmd": "noop"}
    if any(w in t for w in ("quit", "exit", "bye", "goodbye")):
        return {"cmd": "quit"}
    if t in ("help", "?") or "what can you" in t or "how do i" in t:
        return {"cmd": "help"}
    if any(w in t for w in ("status", "how am i", "how are we", "p&l", "pnl",
                            "balance", "doing", "positions")):
        return {"cmd": "status"}
    if any(w in t for w in ("compare", "rank", "which is best", "best strategy",
                            "leaderboard", "best", "winner")):
        return {"cmd": "compare"}
    if any(w in t for w in ("dashboard", "web ui", "webui", "open ui", "browser",
                            "neural deck")):
        return {"cmd": "dashboard"}
    if any(w in t for w in ("backtest", "back test", "simulate", "sim test", "run a test")):
        intent = {"cmd": "backtest"}
        for name in STRATEGIES:
            if name in t:
                intent["strategy"] = name
                break
        m = re.search(r"edge\s*(?:of|=|:)?\s*([0-9]*\.?[0-9]+)", t)
        if m:
            intent["edge"] = float(m.group(1))
        return intent
    if any(w in t for w in ("reset", "clear", "start over")):
        return {"cmd": "reset"}
    if any(w in t for w in ("stop", "pause", "halt", "freeze")):
        return {"cmd": "pause"}
    # set a parameter:  "set speed to 20", "edge 0.5", "entry velocity 30"
    for alias, key in PARAM_ALIASES.items():
        if alias in t:
            m = re.search(r"(-?[0-9]*\.?[0-9]+)", t)
            if m:
                return {"cmd": "set", "param": key, "value": float(m.group(1))}
    # switch strategy
    for name in STRATEGIES:
        if name in t:
            return {"cmd": "strategy", "name": name}
    if any(w in t for w in ("start", "go", "begin", "run", "launch", "trade")):
        return {"cmd": "start"}
    return {"cmd": "unknown", "text": text}


# ------------------------------ optional LLM -------------------------------
def llm_backend() -> str:
    """Detect an available LLM backend: 'ollama', 'anthropic', or 'none'."""
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=0.6)
        return "ollama"
    except Exception:
        pass
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    return "none"


def llm_reply(text: str, snapshot: dict, backend: str) -> str | None:
    """Optional friendly natural-language reply describing what just happened."""
    context = (f"strategy={snapshot['strategy']} running={snapshot['running']} "
               f"equity=${snapshot['account']['equity']:.2f} "
               f"pnl=${snapshot['account']['realized_pnl']:+.2f} "
               f"fees=${snapshot['account']['fees']:.2f} "
               f"trades={snapshot['account']['trades']}")
    prompt = (f"You are a terse local trading-sim assistant. Bot state: {context}. "
              f"User said: '{text}'. Reply in one or two helpful sentences. "
              f"Never claim real money is involved.")
    try:
        if backend == "ollama":
            import urllib.request
            req = urllib.request.Request(
                "http://localhost:11434/api/generate",
                data=json.dumps({"model": os.environ.get("OLLAMA_MODEL", "llama3.2"),
                                 "prompt": prompt, "stream": False}).encode(),
                headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read()).get("response", "").strip()
        if backend == "anthropic":
            from anthropic import Anthropic
            client = Anthropic()
            msg = client.messages.create(
                model="claude-haiku-4-5-20251001", max_tokens=120,
                messages=[{"role": "user", "content": prompt}])
            return "".join(b.text for b in msg.content if b.type == "text").strip()
    except Exception:
        return None
    return None


# ------------------------------- assistant ---------------------------------
class Assistant:
    def __init__(self):
        self.engine = SimEngine()
        self.backend = llm_backend()

    def status_line(self) -> str:
        s = self.engine.snapshot()
        a = s["account"]
        pos = ", ".join(f"{p['contracts']}x {p['side']}@{p['avg_price']*100:.0f}c"
                        for p in a["positions"]) or "none"
        run = "RUNNING" if s["running"] else "paused"
        return (f"[{s['strategy']} · {run}] equity ${a['equity']:.2f} | "
                f"P&L ${a['realized_pnl']:+.2f} | fees ${a['fees']:.2f} | "
                f"trades {a['trades']} | positions: {pos}")

    def handle(self, text: str) -> tuple[str, bool]:
        """Return (reply, keep_going)."""
        intent = parse(text)
        cmd = intent["cmd"]

        if cmd == "quit":
            return "Shutting down. Nothing was ever real money. Bye.", False
        if cmd == "noop":
            return "", True
        if cmd == "help":
            return HELP, True
        if cmd == "status":
            return self.status_line(), True
        if cmd == "start":
            self.engine.start()
            return "Agents started. " + self.status_line(), True
        if cmd == "pause":
            self.engine.pause()
            return "Paused. " + self.status_line(), True
        if cmd == "reset":
            self.engine.reset()
            return "Reset to a fresh $21.00 paper balance.", True
        if cmd == "strategy":
            self.engine.set_params(strategy=intent["name"])
            return f"Strategy -> {intent['name']}. " + self.status_line(), True
        if cmd == "set":
            self.engine.set_params(**{intent["param"]: intent["value"]})
            return f"Set {intent['param']} = {intent['value']}.", True
        if cmd == "dashboard":
            try:
                subprocess.Popen([sys.executable, "-m", "kalshibot.webui"])
                return "Opening the dashboard at http://localhost:8765 ...", True
            except Exception as e:
                return f"Could not launch dashboard: {e}", True
        if cmd == "backtest":
            name = intent.get("strategy", self.engine.snapshot()["strategy"])
            edge = intent.get("edge", 0.0)
            r = bt.evaluate(name, n_markets=200, spread=0.02, contracts=20,
                            entry_velocity=25.0, take_profit=0.06,
                            start_balance=21.0, signal_edge=edge)
            return (f"Backtest {name} (edge {edge:.0%}, 200 markets): "
                    f"P&L ${r['total_pnl']:+.2f}, {r['avg_trades']:.1f} trades/mkt, "
                    f"${r['fees']:.2f} fees, {r['win_rate']:.0f}% win.", True)
        if cmd == "compare":
            rows = [bt.evaluate(n, n_markets=200, spread=0.02, contracts=20,
                                entry_velocity=25.0, take_profit=0.06,
                                start_balance=21.0, signal_edge=0.0)
                    for n in STRATEGIES]
            rows.sort(key=lambda r: r["total_pnl"], reverse=True)
            lines = ["Strategy ranking (edge 0%, 200 markets):"]
            for i, r in enumerate(rows, 1):
                lines.append(f"  {i}. {r['strategy']:<9} ${r['total_pnl']:+8.2f}  "
                             f"{r['avg_trades']:>4.1f} trades/mkt  ${r['fees']:.0f} fees")
            lines.append("Lesson holds: the strategy that trades least loses least.")
            return "\n".join(lines), True

        # unknown -> let the optional LLM help, else nudge to help
        if self.backend != "none":
            reply = llm_reply(text, self.engine.snapshot(), self.backend)
            if reply:
                return reply, True
        return "Not sure what you meant. Type 'help' for what I can do.", True

    def repl(self):
        print("=" * 60)
        print(" kalshibot personal assistant  ·  local · paper-only")
        print(f" LLM backend: {self.backend}"
              + ("  (rule-based mode — set up Ollama or ANTHROPIC_API_KEY for chat)"
                 if self.backend == "none" else ""))
        print("=" * 60)
        print(HELP)
        while True:
            try:
                text = input("\nyou > ")
            except (EOFError, KeyboardInterrupt):
                print("\nbye.")
                break
            reply, keep = self.handle(text)
            if reply:
                print("bot > " + reply)
            if not keep:
                break


def main():
    Assistant().repl()


if __name__ == "__main__":
    main()
