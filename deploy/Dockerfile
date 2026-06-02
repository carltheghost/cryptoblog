# Paper-mode only. This image never places real orders.
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY kalshibot ./kalshibot

# Default: run the live PAPER loop (real prices in, simulated fills out).
# Override CMD args at `docker run` time, e.g. --series KXETH --minutes 1440
ENV PYTHONUNBUFFERED=1
CMD ["python", "-m", "kalshibot.run_paper", "--series", "KXBTC", "--minutes", "1440", "--poll", "2"]
