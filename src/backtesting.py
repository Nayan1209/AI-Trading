"""Deterministic historical replay for the existing observation-only signals."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Sequence

from src.market_data.models import Candle
from src.market_data.scanner_features import ScannerFeatureSnapshot
from src.market_data.scanner_ranking import ScannerRankedCandidate
from src.market_data.validation import validate_candle
from src.signal_engine import SignalDirection, SignalEngine, SignalStrategy, SignalType


@dataclass(frozen=True)
class BacktestConfig:
    """Explicit replay assumptions. Costs are charged on each side of a trade."""

    lookback_bars: int
    holding_bars: int
    cost_bps_per_side: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.lookback_bars, int) or isinstance(self.lookback_bars, bool):
            raise ValueError("lookback_bars must be an integer")
        if self.lookback_bars < 2:
            raise ValueError("lookback_bars must be at least 2")
        if not isinstance(self.holding_bars, int) or isinstance(self.holding_bars, bool):
            raise ValueError("holding_bars must be an integer")
        if self.holding_bars < 1:
            raise ValueError("holding_bars must be positive")
        if not isinstance(self.cost_bps_per_side, Decimal):
            raise ValueError("cost_bps_per_side must be a Decimal")
        if not self.cost_bps_per_side.is_finite() or self.cost_bps_per_side < 0:
            raise ValueError("cost_bps_per_side must be finite and non-negative")


@dataclass(frozen=True)
class BacktestTrade:
    """One signal replayed with next-bar-open entry and timed close exit."""

    signal_candle_timestamp: datetime
    entry_candle_timestamp: datetime
    exit_candle_timestamp: datetime
    signal_type: SignalType
    direction: SignalDirection
    entry_price: Decimal
    exit_price: Decimal
    gross_return_pct: Decimal
    net_return_pct: Decimal
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class BacktestMetrics:
    """Equal-notional per-trade summaries; not a portfolio equity curve."""

    trade_count: int
    winning_trades: int
    losing_trades: int
    flat_trades: int
    win_rate_pct: Decimal
    average_net_return_pct: Decimal
    sum_net_return_pct: Decimal


@dataclass(frozen=True)
class BacktestResult:
    """Immutable, reproducible output for one instrument and one strategy."""

    internal_id: str
    trading_symbol: str
    exchange: str
    candle_symbol: str
    timeframe: str
    strategy_type: SignalType
    config: BacktestConfig
    trades: tuple[BacktestTrade, ...]
    metrics: BacktestMetrics


class BacktestEngine:
    """Replay an existing deterministic signal strategy against validated candles.

    A signal is evaluated using only the trailing close known at that candle's
    timestamp. Entry is the following bar's open; exit is the close of the
    configured holding bar. Only one position is open at a time.
    """

    def __init__(self, strategy: SignalStrategy, config: BacktestConfig) -> None:
        self._strategy = strategy
        self._config = config
        self._signal_engine = SignalEngine((strategy,))

    def run(
        self,
        candles: Sequence[Candle],
        *,
        internal_id: str,
        trading_symbol: str,
    ) -> BacktestResult:
        """Replay a chronological, single-instrument candle series."""
        internal_id = internal_id.strip()
        trading_symbol = trading_symbol.strip()
        if not internal_id:
            raise ValueError("internal_id must not be empty")
        if not trading_symbol:
            raise ValueError("trading_symbol must not be empty")

        rows = tuple(candles)
        if not rows:
            raise ValueError("candles must not be empty")
        self._validate_series(rows)

        first = rows[0]
        trades: list[BacktestTrade] = []
        signal_index = self._config.lookback_bars - 1
        last_executable_signal = len(rows) - self._config.holding_bars - 1

        while signal_index <= last_executable_signal:
            window_start = signal_index - self._config.lookback_bars + 1
            window = rows[window_start : signal_index + 1]
            snapshot = self._snapshot(
                window,
                internal_id=internal_id,
                trading_symbol=trading_symbol,
            )
            signals = self._signal_engine.generate((ScannerRankedCandidate(1, snapshot),))

            if not signals:
                signal_index += 1
                continue
            signal = signals[0]
            if signal.direction not in (SignalDirection.LONG, SignalDirection.SHORT):
                raise ValueError("backtesting requires a LONG or SHORT signal")

            entry_index = signal_index + 1
            exit_index = signal_index + self._config.holding_bars
            entry_price = rows[entry_index].open
            exit_price = rows[exit_index].close
            if signal.direction is SignalDirection.LONG:
                gross_return_pct = (exit_price - entry_price) / entry_price * Decimal("100")
            else:
                gross_return_pct = (entry_price - exit_price) / entry_price * Decimal("100")
            round_trip_cost_pct = self._config.cost_bps_per_side / Decimal("100") * Decimal("2")
            trades.append(
                BacktestTrade(
                    signal_candle_timestamp=rows[signal_index].timestamp,
                    entry_candle_timestamp=rows[entry_index].timestamp,
                    exit_candle_timestamp=rows[exit_index].timestamp,
                    signal_type=signal.signal_type,
                    direction=signal.direction,
                    entry_price=entry_price,
                    exit_price=exit_price,
                    gross_return_pct=gross_return_pct,
                    net_return_pct=gross_return_pct - round_trip_cost_pct,
                    reason_codes=signal.reason_codes,
                )
            )
            # The exit candle close is known before a new signal is evaluated.
            signal_index = exit_index

        immutable_trades = tuple(trades)
        return BacktestResult(
            internal_id=internal_id,
            trading_symbol=trading_symbol,
            exchange=first.exchange,
            candle_symbol=first.symbol,
            timeframe=first.timeframe,
            strategy_type=self._strategy.signal_type,
            config=self._config,
            trades=immutable_trades,
            metrics=self._metrics(immutable_trades),
        )

    @staticmethod
    def _snapshot(
        candles: Sequence[Candle], *, internal_id: str, trading_symbol: str
    ) -> ScannerFeatureSnapshot:
        first_close = candles[0].close
        latest = candles[-1]
        return ScannerFeatureSnapshot(
            internal_id=internal_id,
            trading_symbol=trading_symbol,
            sample_count=len(candles),
            first_ltp=first_close,
            latest_ltp=latest.close,
            high_ltp=max(candle.high for candle in candles),
            low_ltp=min(candle.low for candle in candles),
            change_pct=(latest.close - first_close) / first_close * Decimal("100"),
        )

    @staticmethod
    def _validate_series(candles: tuple[Candle, ...]) -> None:
        identity = (candles[0].symbol, candles[0].exchange, candles[0].timeframe)
        previous_timestamp = None
        for candle in candles:
            validate_candle(candle)
            if (candle.symbol, candle.exchange, candle.timeframe) != identity:
                raise ValueError("all candles must have the same symbol, exchange, and timeframe")
            if previous_timestamp is not None and candle.timestamp <= previous_timestamp:
                raise ValueError("candles must be strictly chronological without duplicate timestamps")
            previous_timestamp = candle.timestamp

    @staticmethod
    def _metrics(trades: tuple[BacktestTrade, ...]) -> BacktestMetrics:
        winners = sum(trade.net_return_pct > 0 for trade in trades)
        losers = sum(trade.net_return_pct < 0 for trade in trades)
        flats = len(trades) - winners - losers
        sum_return = sum((trade.net_return_pct for trade in trades), Decimal("0"))
        count = len(trades)
        return BacktestMetrics(
            trade_count=count,
            winning_trades=winners,
            losing_trades=losers,
            flat_trades=flats,
            win_rate_pct=Decimal(winners) * Decimal("100") / count if count else Decimal("0"),
            average_net_return_pct=sum_return / count if count else Decimal("0"),
            sum_net_return_pct=sum_return,
        )
