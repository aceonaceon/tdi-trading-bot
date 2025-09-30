from __future__ import annotations

from pathlib import Path

from apps.common.config import DEFAULT_DB_URL, BotConfig, WebConfig


def test_bot_config_defaults(monkeypatch) -> None:
    monkeypatch.delenv("DB_URL", raising=False)
    monkeypatch.delenv("MODE", raising=False)
    cfg = BotConfig()
    assert cfg.symbol == "BTCUSDT"
    assert cfg.mode == "paper"
    assert cfg.db_url == DEFAULT_DB_URL
    assert isinstance(cfg.kill_switch_file, Path)


def test_web_config_reads_env(monkeypatch) -> None:
    monkeypatch.setenv("DB_URL", "sqlite:///test.db")
    monkeypatch.setenv("MODE", "paper")
    cfg = WebConfig()
    assert cfg.db_url == "sqlite:///test.db"
    assert cfg.mode == "paper"
