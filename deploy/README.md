# Deploying the PAPER loop on AWS (data collection, no real money)

The goal: run the paper loop continuously on an EC2 instance that *can* reach
Kalshi, so you gather days of real prices + simulated fills and find out whether
the strategy survives fees/spread **before** risking a cent.

This deploys **paper mode only**. No API keys are needed and no real orders are
placed. Live trading stays disabled in the code until a paper run proves an edge.

## 1. Launch a small EC2 instance

- A `t3.micro` in a US region is plenty (this is light polling, not HFT).
- Pick a region where Kalshi is reachable. If you still get HTTP 403, the block
  is account/eligibility-side, not the server — that's a signal to stop, not to
  route around it.

## 2. Run it with Docker

```bash
# on the instance, in the repo root
sudo yum install -y docker git || sudo apt-get update && sudo apt-get install -y docker.io git
sudo systemctl start docker

git clone <your-fork-url> cryptoblog && cd cryptoblog
sudo docker build -t kalshibot-paper -f deploy/Dockerfile .

# run detached, restart on reboot, log to file
sudo docker run -d --name kalshibot --restart unless-stopped \
  kalshibot-paper python -m kalshibot.run_paper --series KXBTC --minutes 10080 --poll 2

# watch it
sudo docker logs -f kalshibot
```

`--minutes 10080` = one week. Let it run, then read the FINAL P&L line in the
logs. If paper P&L is negative over a meaningful sample, that's your answer.

## 3. Without Docker

```bash
pip install -r requirements.txt
nohup python -m kalshibot.run_paper --series KXBTC --minutes 10080 --poll 2 > paper.log 2>&1 &
tail -f paper.log
```

## Cost / safety

- `t3.micro` is a few dollars a month; stop the instance when done.
- This image has no path to real-money trading. Going live is a separate,
  explicit decision that requires: a profitable paper run, RSA request signing,
  and hard risk limits (max position, max daily loss, kill-switch).
