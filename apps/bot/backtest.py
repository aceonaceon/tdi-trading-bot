from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(slots=True)
class Candle:
    close: float
    atr: float


@dataclass(slots=True)
class BacktestResult:
    trades: int
    wins: int
    losses: int
    expectancy: float


def run_backtest(candles: Iterable[Candle]) -> BacktestResult:
    balance = 1.0
    wins = 0
    losses = 0
    for candle in candles:
        if candle.atr == 0:
            continue
        risk = min(0.005, candle.atr / max(candle.close, 1))
        move = (candle.close % 2 - 0.5) * risk * 10
        balance *= 1 + move
        if move > 0:
            wins += 1
        elif move < 0:
            losses += 1
    trades = wins + losses
    expectancy = ((balance - 1.0) / trades) if trades else 0.0
    return BacktestResult(trades=trades, wins=wins, losses=losses, expectancy=expectancy)


__all__ = ["Candle", "BacktestResult", "run_backtest"]
