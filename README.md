# TDI Trading Bot

This repository hosts a paper-trading bot scaffold and a minimal metrics dashboard for the TDI strategy on Binance
UMFutures testnet. The current milestone delivers database bootstrapping, a paper-mode loop that records synthetic
equity samples, and a WSGI dashboard with a `/healthz` endpoint.

## Getting started

Install dependencies (no external packages are required for this milestone) and run the migrations:

```bash
python3 -m pip install --upgrade pip
./migrate
```

## Authoritative commands

Executable scripts matching the authoritative workflow in `AGENTS.md` are available at the repository root.

```bash
./fmt
./lint:bot
./lint:web
./test:unit
./test:backtest:smoke
./test:e2e:paper
./run:bot:paper
./run:web
```

The bot loop respects the `KILL_SWITCH_FILE` and stays in paper mode (`MODE=paper`). When the Binance testnet is not reachable,
the loop falls back to deterministic synthetic prices and continues recording telemetry for observability.
