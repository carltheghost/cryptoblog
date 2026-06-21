#!/usr/bin/env bash
# One-step setup for kalshibot (macOS / Linux). Run:  bash setup.sh
set -e
cd "$(dirname "$0")"

echo "== kalshibot setup =="
echo

# 1) Python deps
PY=python3; command -v python3 >/dev/null 2>&1 || PY=python
echo "[1/3] Installing Python dependencies with $PY ..."
$PY -m pip install -r requirements.txt

# 2) Optional local LLM (Hermes via Ollama)
echo
echo "[2/3] Checking for a local LLM (optional) ..."
if command -v ollama >/dev/null 2>&1; then
  echo "  Ollama is installed. Models you have:"
  ollama list 2>/dev/null || echo "  (could not list; is 'ollama serve' running?)"
  if ! ollama list 2>/dev/null | grep -iq hermes; then
    echo "  No Hermes model found. To use Hermes:  ollama pull hermes3"
  else
    echo "  Hermes detected — the assistant will use it automatically."
  fi
else
  echo "  Ollama not installed (optional). Get it at https://ollama.com to enable chat."
  echo "  The assistant works fine without it (rule-based mode)."
fi

# 3) Self-check + how to start
echo
echo "[3/3] Running the assistant's self-check ..."
$PY -c "import sys; sys.argv=['']; \
from kalshibot.assistant import Assistant; \
a=Assistant(); print(a.handle('doctor')[0])" || true

echo
echo "== Done. Start it with: =="
echo "  $PY -m kalshibot.launch         # EVERYTHING: swarm dashboard + data recording"
echo "  $PY -m kalshibot.assistant      # talk to it; type: doctor   (or: spawn 11 agents)"
echo "  $PY -m kalshibot.webui          # just the dashboards (/  and  /swarm)"
