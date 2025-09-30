from __future__ import annotations

import asyncio
import sqlite3

from apps.bot.loop import PaperBot
from apps.bot.migrations import run_migrations
from apps.common.config import BotConfig
from apps.common.database import create_database, resolve_sqlite_path


def test_paper_bot_tick_writes_equity(monkeypatch, tmp_path) -> None:
    db_path = tmp_path / "loop.db"
    monkeypatch.setenv("DB_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("MODE", "paper")
    config = BotConfig()
    run_migrations(config.db_url)
    db = create_database(config.db_url)
    bot = PaperBot(config=config, database=db)

    asyncio.run(bot._on_tick(price=100.0, tick=1))

    conn = sqlite3.connect(resolve_sqlite_path(config.db_url))
    try:
        cursor = conn.execute("SELECT COUNT(*) FROM equity_curve")
        rows = cursor.fetchone()[0]
    finally:
        conn.close()
    assert rows == 1
