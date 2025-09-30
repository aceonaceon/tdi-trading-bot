from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

DEFAULT_DB_URL = "sqlite:///./tdi_bot.db"


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError as exc:
        raise ValueError(f"Environment variable {name} must be a float") from exc


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"Environment variable {name} must be an integer") from exc


def _env_str(name: str, default: str) -> str:
    return os.getenv(name, default)


def _default_kill_switch() -> Path:
    return Path(_env_str("KILL_SWITCH_FILE", str(Path(tempfile.gettempdir()) / "tdi_kill_switch")))


def _default_run_id() -> str:
    return _env_str("RUN_ID", datetime.now(UTC).strftime("%Y%m%d%H%M%S"))


def _default_db_url() -> str:
    return _env_str("DB_URL", DEFAULT_DB_URL)


def _default_mode() -> str:
    return _env_str("MODE", "paper")


def _default_dashboard_port() -> int:
    return _env_int("DASHBOARD_PORT", 8080)


def _default_symbol() -> str:
    return _env_str("SYMBOL", "BTCUSDT")


def _default_timeframe() -> str:
    return _env_str("TIMEFRAME", "1h")


def _default_price_source() -> str:
    return _env_str("PRICE_SOURCE", "binance-testnet")


def _default_poll_interval() -> int:
    return _env_int("POLL_INTERVAL_SECONDS", 60)


def _default_candles_limit() -> int:
    return _env_int("CANDLES_LIMIT", 500)


def _default_risk_per_trade() -> float:
    return _env_float("RISK_PER_TRADE", 0.005)


def _default_daily_max_dd() -> float:
    return _env_float("DAILY_MAX_DRAWDOWN", 0.02)


@dataclass(slots=True)
class BotConfig:
    symbol: str = field(default_factory=_default_symbol)
    timeframe: str = field(default_factory=_default_timeframe)
    risk_per_trade: float = field(default_factory=_default_risk_per_trade)
    daily_max_drawdown: float = field(default_factory=_default_daily_max_dd)
    mode: str = field(default_factory=_default_mode)
    db_url: str = field(default_factory=_default_db_url)
    dashboard_port: int = field(default_factory=_default_dashboard_port)
    kill_switch_file: Path = field(default_factory=_default_kill_switch)
    poll_interval_seconds: int = field(default_factory=_default_poll_interval)
    run_id: str = field(default_factory=_default_run_id)
    price_source: str = field(default_factory=_default_price_source)
    candles_limit: int = field(default_factory=_default_candles_limit)

    def ensure_paper_mode(self) -> None:
        if self.mode != "paper":
            raise ValueError("BotConfig.mode must remain 'paper' for this task")


@dataclass(slots=True)
class WebConfig:
    db_url: str = field(default_factory=_default_db_url)
    dashboard_port: int = field(default_factory=_default_dashboard_port)
    mode: str = field(default_factory=_default_mode)
    run_id: str | None = field(default_factory=lambda: os.getenv("RUN_ID"))


__all__ = ["BotConfig", "WebConfig", "DEFAULT_DB_URL"]
