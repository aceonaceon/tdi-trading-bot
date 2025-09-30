from __future__ import annotations

from apps.bot.backtest import BacktestResult, Candle, run_backtest


def test_backtest_smoke() -> None:
    candles = [Candle(close=100 + i, atr=2 + (i % 3)) for i in range(50)]
    result = run_backtest(candles)
    assert isinstance(result, BacktestResult)
    assert result.trades > 0
