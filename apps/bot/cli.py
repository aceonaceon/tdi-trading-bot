from __future__ import annotations

import argparse
import asyncio
import logging

from apps.bot.loop import PaperBot
from apps.bot.migrations import run_migrations
from apps.common.config import BotConfig

logger = logging.getLogger(__name__)


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def cmd_migrate(args: argparse.Namespace) -> None:
    config = BotConfig()
    run_migrations(config.db_url)
    logger.info("Migrations applied", extra={"db_url": config.db_url})


def cmd_run(args: argparse.Namespace) -> None:
    config = BotConfig()
    config.ensure_paper_mode()
    run_migrations(config.db_url)
    configure_logging(args.verbose)
    logger.info("Starting paper bot", extra={"symbol": config.symbol, "mode": config.mode})
    asyncio.run(PaperBot.run_from_env(max_ticks=args.max_ticks))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="TDI paper trading bot CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    migrate_parser = subparsers.add_parser("migrate", help="Run database migrations")
    migrate_parser.set_defaults(func=cmd_migrate)

    run_parser = subparsers.add_parser("run", help="Start the paper trading loop")
    run_parser.add_argument(
        "--max-ticks", type=int, default=None, help="Number of ticks before exit"
    )
    run_parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    run_parser.set_defaults(func=cmd_run)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
