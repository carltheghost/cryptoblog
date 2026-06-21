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
from . import multiagent as ma

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
  start / stop / reset                 - run, pause, or reset the SIM agents
  start trading / collect data         - launch a LIVE paper session + data
                                         recorder to CSV (real prices, no money)
  use <strategy>                       - momentum | fade | spread | imbalance | chronos
  set <param> to <value>               - entry velocity, take profit, contracts,
                                         spread, speed, signal edge
  how am I doing? / status             - live P&L, fees, trades, positions
  backtest <strategy> [edge <0..1>]    - run an offline backtest
  compare / which is best              - rank all strategies
  spawn <N> agents [edge <0..1>]       - run a multi-agent arena + leaderboard
  models                               - list your local Ollama models
  doctor                               - check Python / Ollama / Hermes / backend
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
    if any(w in t for w in ("doctor", "diagnose", "troubleshoot", "health check",
                            "check setup", "is hermes", "is ollama", "llm working",
                            "why isn't", "why doesn't", "not working", "fix")):
        return {"cmd": "doctor"}
    if "model" in t and any(w in t for w in ("list", "models", "which", "available", "show")):
        return {"cmd": "models"}
    if any(w in t for w in ("show data", "check data", "peek", "see data",
                            "head", "csv", "is data", "data flowing", "recorded")):
        return {"cmd": "peek"}
    if (any(w in t for w in ("live", "record", "collect data", "gather data",
                             "real data", "go live", "perpetual", "perp"))
            or ("start" in t and "trad" in t) or ("paper" in t and "session" in t)):
        intent = {"cmd": "live"}
        for name in STRATEGIES:
            if name in t:
                intent["strategy"] = name
                break
        return intent
    if any(w in t for w in ("arena", "multiple agent", "more agent", "spawn",
                            "team", "agents", "ensemble", "army")):
        intent = {"cmd": "arena"}
        m = re.search(r"([0-9]+)\s*agent", t) or re.search(r"agents?\s*([0-9]+)", t)
        if m:
            intent["n"] = int(m.group(1))
        m2 = re.search(r"edge\s*(?:of|=|:)?\s*([0-9]*\.?[0-9]+)", t)
        if m2:
            intent["edge"] = float(m2.group(1))
        return intent
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
    if any(w in t for w in ("compare", "rank", "which is best", "best strategy",
                            "leaderboard", "best", "winner")):
        return {"cmd": "compare"}
    if any(w in t for w in ("dashboard", "web ui", "webui", "open ui", "browser",
                            "neural deck")):
        return {"cmd": "dashboard"}
    # status: note \bbalance\b so it does not fire on "im-balance"
    if any(w in t for w in ("status", "how am i", "how are we", "p&l", "pnl",
                            "doing", "positions")) or re.search(r"\bbalance\b", t):
        return {"cmd": "status"}
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
def ollama_models() -> list[str]:
    """Return the list of model names installed in the local Ollama, or []."""
    import urllib.request
    with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2) as r:
        return [m.get("name", "") for m in json.loads(r.read()).get("models", [])]


def choose_ollama_model() -> str:
    """Pick which local model to chat with. Respects OLLAMA_MODEL; otherwise
    prefers a Hermes model if you have one, else the first installed model."""
    env = os.environ.get("OLLAMA_MODEL")
    if env:
        return env
    try:
        names = [n for n in ollama_models() if n]
    except Exception:
        return "llama3.2"
    if not names:
        return "llama3.2"
    for n in names:
        if "hermes" in n.lower():
            return n
    return names[0]


def openai_local_base() -> str | None:
    """Detect an OpenAI-compatible local LLM server (LM Studio, Jan, llama.cpp,
    text-generation-webui, etc.). Respects OPENAI_BASE_URL; else tries LM Studio's
    default port 1234."""
    base = os.environ.get("OPENAI_BASE_URL")
    if base:
        return base.rstrip("/")
    try:
        import urllib.request
        url = os.environ.get("LMSTUDIO_URL", "http://localhost:1234/v1").rstrip("/")
        urllib.request.urlopen(url + "/models", timeout=0.6)
        return url
    except Exception:
        return None


def llm_backend() -> str:
    """Detect an available LLM backend, in preference order:
    'ollama' (Hermes etc.) -> 'lmstudio' (OpenAI-compatible local) -> 'anthropic' -> 'none'."""
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=0.6)
        return "ollama"
    except Exception:
        pass
    if openai_local_base():
        return "lmstudio"
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    return "none"


def _openai_chat(base: str, prompt: str) -> str | None:
    """Call any OpenAI-compatible /chat/completions endpoint (LM Studio etc.)."""
    import urllib.request
    model = os.environ.get("LMSTUDIO_MODEL")
    if not model:
        try:
            with urllib.request.urlopen(base + "/models", timeout=2) as r:
                model = json.loads(r.read())["data"][0]["id"]
        except Exception:
            model = "local-model"
    body = json.dumps({"model": model, "max_tokens": 160,
                       "messages": [{"role": "user", "content": prompt}]}).encode()
    key = os.environ.get("OPENAI_API_KEY", "lm-studio")
    req = urllib.request.Request(base + "/chat/completions", data=body,
                                 headers={"Content-Type": "application/json",
                                          "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read())["choices"][0]["message"]["content"].strip()


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
                data=json.dumps({"model": choose_ollama_model(),
                                 "prompt": prompt, "stream": False}).encode(),
                headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read()).get("response", "").strip()
        if backend == "lmstudio":
            base = openai_local_base()
            if base:
                return _openai_chat(base, prompt)
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

        if cmd == "doctor":
            self.backend = llm_backend()   # re-detect in case you just started Ollama
            lines = ["self-check:", f"  python: {sys.version.split()[0]}"]
            try:
                names = ollama_models()
                lines.append(f"  ollama: UP — models: {', '.join(names) or '(none pulled)'}")
                lines.append(f"  chat model in use: {choose_ollama_model()}")
                if not any("hermes" in n.lower() for n in names) and not os.environ.get("OLLAMA_MODEL"):
                    lines.append("  note: no Hermes model seen. Pull one: `ollama pull hermes3`"
                                 " (or set OLLAMA_MODEL=<your model name>).")
            except Exception:
                lines.append("  ollama: DOWN — start it in another terminal: `ollama serve`,"
                             " then pull a model, e.g. `ollama pull hermes3`.")
            base = openai_local_base()
            lines.append(f"  LM Studio / OpenAI-compatible: {base if base else 'not detected (start LM Studio server on :1234)'}")
            lines.append(f"  ANTHROPIC_API_KEY: {'set' if os.environ.get('ANTHROPIC_API_KEY') else 'not set'}")
            lines.append(f"  active chat backend: {self.backend}"
                         + ("  (rule-based — everything still works, just no free-form chat)"
                            if self.backend == "none" else ""))
            return "\n".join(lines), True

        if cmd == "models":
            try:
                import urllib.request
                with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2) as r:
                    tags = json.loads(r.read()).get("models", [])
                if not tags:
                    return "Ollama is running but has no models. Try: ollama pull llama3.2", True
                names = ", ".join(m.get("name", "?") for m in tags)
                return (f"Local Ollama models: {names}. "
                        f"Set OLLAMA_MODEL=<name> to pick one for chat.", True)
            except Exception:
                return ("No local Ollama detected at http://localhost:11434. "
                        "Start it with `ollama serve` and pull a model, e.g. `ollama pull llama3.2`.", True)

        if cmd == "peek":
            from . import peek
            return peek.summary("kalshi_data.csv"), True

        if cmd == "live":
            strat = intent.get("strategy", self.engine.snapshot()["strategy"])
            jobs = [
                [sys.executable, "-m", "kalshibot.run_paper", "--series", "KXBTC",
                 "--strategy", strat, "--minutes", "120", "--record", "kalshi_ticks.csv"],
                [sys.executable, "-m", "kalshibot.record", "--series", "KXBTC",
                 "--minutes", "120", "--out", "kalshi_market.csv"],
            ]
            launched = 0
            for c in jobs:
                try:
                    subprocess.Popen(c)
                    launched += 1
                except Exception:
                    pass
            return (f"Launched a LIVE PAPER session + read-only recorder ({launched}/2), "
                    "no real money:\n"
                    f"  paper trades ({strat}) -> kalshi_ticks.csv\n"
                    "  market data            -> kalshi_market.csv\n"
                    "On a Kalshi-reachable network they'll collect for 2 hours; otherwise "
                    "they exit with 403. For perpetuals, tell me the ticker and I'll add it.", True)

        if cmd == "arena":
            n = intent.get("n", 8)
            edge = intent.get("edge", 0.0)
            results = ma.run_arena(n_agents=n, n_markets=60, signal_edge=edge)
            return ma.format_leaderboard(results, 60, edge), True

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
