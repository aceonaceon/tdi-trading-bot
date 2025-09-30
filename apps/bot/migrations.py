from __future__ import annotations

import sqlite3
from pathlib import Path

from apps.common.database import resolve_sqlite_path

SCHEMA_STATEMENTS = (
    """
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT NOT NULL,
        side TEXT NOT NULL,
        qty REAL NOT NULL,
        entry REAL NOT NULL,
        exit REAL,
        pnl REAL,
        fees REAL NOT NULL DEFAULT 0,
        r_multiple REAL,
        reason_in TEXT NOT NULL,
        reason_out TEXT,
        run_id TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS equity_curve (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT NOT NULL,
        equity REAL NOT NULL,
        dd REAL NOT NULL,
        run_id TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS metrics_daily (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        win_rate REAL NOT NULL,
        avg_r REAL NOT NULL,
        expectancy REAL NOT NULL,
        max_dd REAL NOT NULL,
        sharpe REAL NOT NULL,
        trades_count INTEGER NOT NULL,
        run_id TEXT NOT NULL,
        UNIQUE(date, run_id)
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_equity_curve_run_ts ON equity_curve(run_id, ts)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_trades_run_ts ON trades(run_id, ts)
    """,
)


def run_migrations(db_url: str) -> Path:
    db_path = resolve_sqlite_path(db_url)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        for statement in SCHEMA_STATEMENTS:
            cursor.execute(statement)
        conn.commit()
    finally:
        conn.close()
    return db_path


__all__ = ["run_migrations"]
