from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from apps.common.config import DEFAULT_DB_URL


@dataclass(slots=True)
class Database:
    path: Path

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def insert_equity_point(
        self, run_id: str, ts: datetime, equity: float, drawdown: float
    ) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO equity_curve (ts, equity, dd, run_id) VALUES (?, ?, ?, ?)",
                (ts.isoformat(), float(equity), float(drawdown), run_id),
            )

    def upsert_daily_metrics(
        self,
        run_id: str,
        day: date,
        *,
        win_rate: float,
        avg_r: float,
        expectancy: float,
        max_dd: float,
        sharpe: float,
        trades_count: int,
    ) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO metrics_daily (
                    date, win_rate, avg_r, expectancy, max_dd, sharpe, trades_count, run_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(date, run_id) DO UPDATE SET
                    win_rate = excluded.win_rate,
                    avg_r = excluded.avg_r,
                    expectancy = excluded.expectancy,
                    max_dd = excluded.max_dd,
                    sharpe = excluded.sharpe,
                    trades_count = excluded.trades_count
                """,
                (
                    day.isoformat(),
                    float(win_rate),
                    float(avg_r),
                    float(expectancy),
                    float(max_dd),
                    float(sharpe),
                    int(trades_count),
                    run_id,
                ),
            )

    def insert_trade(
        self,
        *,
        run_id: str,
        ts: datetime,
        side: str,
        qty: float,
        entry: float,
        exit: float | None,
        pnl: float | None,
        fees: float,
        r_multiple: float | None,
        reason_in: str,
        reason_out: str | None,
    ) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO trades (
                    ts, side, qty, entry, exit, pnl, fees, r_multiple, reason_in, reason_out, run_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ts.isoformat(),
                    side,
                    float(qty),
                    float(entry),
                    None if exit is None else float(exit),
                    None if pnl is None else float(pnl),
                    float(fees),
                    None if r_multiple is None else float(r_multiple),
                    reason_in,
                    reason_out,
                    run_id,
                ),
            )


def resolve_sqlite_path(db_url: str) -> Path:
    if db_url.startswith("sqlite:///"):
        return Path(db_url.replace("sqlite:///", ""))
    if db_url == DEFAULT_DB_URL:
        return Path("tdi_bot.db")
    raise ValueError(f"Unsupported database URL: {db_url}")


def create_database(db_url: str) -> Database:
    return Database(path=resolve_sqlite_path(db_url))


__all__ = ["Database", "create_database", "resolve_sqlite_path"]
