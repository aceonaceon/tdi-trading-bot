from __future__ import annotations

import sqlite3

from apps.bot.migrations import run_migrations


def test_run_migrations_creates_tables(tmp_path) -> None:
    db_path = tmp_path / "test.db"
    url = f"sqlite:///{db_path}"
    run_migrations(url)
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        names = {row[0] for row in cursor.fetchall()}
    finally:
        conn.close()
    assert {"trades", "equity_curve", "metrics_daily"}.issubset(names)
