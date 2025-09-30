from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from random import random

from apps.bot.binance import fetch_latest_price
from apps.common.config import BotConfig
from apps.common.database import Database, create_database

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class LoopState:
    last_price: float | None = None
    equity: float = 0.0
    peak_equity: float = 0.0


class PaperBot:
    def __init__(self, config: BotConfig, database: Database) -> None:
        config.ensure_paper_mode()
        self.config = config
        self.database = database
        self.state = LoopState(equity=100_000.0, peak_equity=100_000.0)

    async def run(self, *, max_ticks: int | None = None) -> None:
        tick = 0
        while True:
            if self._should_stop():
                logger.info("Kill switch detected; stopping bot loop")
                break

            price = await fetch_latest_price(self.config.symbol)
            tick += 1
            await self._on_tick(price, tick)

            if max_ticks is not None and tick >= max_ticks:
                break

            await asyncio.sleep(self.config.poll_interval_seconds)

    def _should_stop(self) -> bool:
        kill_file = Path(self.config.kill_switch_file)
        return kill_file.exists()

    async def _on_tick(self, price: float, tick: int) -> None:
        now = datetime.now(UTC)
        self.state.last_price = price
        drift = (random() - 0.5) * 50  # noqa: S311 - deterministic drift is sufficient for paper
        self.state.equity = max(self.state.equity + drift, 0)
        self.state.peak_equity = max(self.state.peak_equity, self.state.equity)
        drawdown = 0.0
        if self.state.peak_equity > 0:
            drawdown = (self.state.equity - self.state.peak_equity) / self.state.peak_equity

        logger.info(
            "paper_tick",
            extra={
                "run_id": self.config.run_id,
                "tick": tick,
                "symbol": self.config.symbol,
                "price": price,
                "equity": self.state.equity,
                "drawdown": drawdown,
            },
        )

        self.database.insert_equity_point(
            run_id=self.config.run_id,
            ts=now,
            equity=self.state.equity,
            drawdown=drawdown,
        )

        self.database.upsert_daily_metrics(
            run_id=self.config.run_id,
            day=date.today(),
            win_rate=0.0,
            avg_r=0.0,
            expectancy=0.0,
            max_dd=abs(drawdown),
            sharpe=0.0,
            trades_count=0,
        )

    @classmethod
    async def run_from_env(cls, *, max_ticks: int | None = None) -> None:
        config = BotConfig()
        database = create_database(config.db_url)
        bot = cls(config=config, database=database)
        await bot.run(max_ticks=max_ticks)


__all__ = ["PaperBot", "LoopState"]
