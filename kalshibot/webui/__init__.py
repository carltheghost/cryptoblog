"""Web UI for kalshibot. Run:  python -m kalshibot.webui

Serves a localhost dashboard that visualizes the trading agents as a live
"neural network" graph, streams the simulated/paper market, and lets you control
the agents (start/pause/reset, tune the strategy) from the browser.

No real money. The default feed is a built-in simulation so it works offline;
where Kalshi is reachable you can wire the live paper feed in engine.py.
"""
