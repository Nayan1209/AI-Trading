from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from src.backtesting import BacktestConfig, BacktestEngine
from src.market_data.models import Candle
from src.signal_engine import SignalDirection, SignalType
from src.signal_strategies import (
    BreakoutSignalStrategy,
    MomentumSignalStrategy,
    ReversalSignalStrategy,
)


START = datetime(2026, 10, 1, 9, 15, tzinfo=timezone.utc)


def candle(
    index: int,
    *,
    open_price: str,
    high: str,
    low: str,
    close: str,
    symbol: str = "RELIANCE",
    exchange: str = "NSE",
) -> Candle:
    return Candle(
        symbol=symbol,
        exchange=exchange,
        timeframe="1m",
        timestamp=START + timedelta(minutes=index),
        open=Decimal(open_price),
        high=Decimal(high),
        low=Decimal(low),
        close=Decimal(close),
        volume=100,
    )


def engine(*, holding_bars: int = 1, cost_bps_per_side: str = "0") -> BacktestEngine:
    return BacktestEngine(
        MomentumSignalStrategy(),
        BacktestConfig(
            lookback_bars=2,
            holding_bars=holding_bars,
            cost_bps_per_side=Decimal(cost_bps_per_side),
        ),
    )


def run(candles: list[Candle], *, backtest: BacktestEngine | None = None):
    return (backtest or engine()).run(
        candles,
        internal_id="NSE:CASH:RELIANCE",
        trading_symbol="RELIANCE",
    )


def test_long_signal_enters_next_open_exits_holding_bar_close_and_charges_costs() -> None:
    result = run(
        [
            candle(0, open_price="100", high="100", low="99", close="100"),
            candle(1, open_price="100", high="102", low="100", close="102"),
            candle(2, open_price="103", high="105", low="102", close="104"),
        ],
        backtest=engine(cost_bps_per_side="10"),
    )

    trade = result.trades[0]
    assert trade.direction is SignalDirection.LONG
    assert trade.signal_type is SignalType.MOMENTUM
    assert trade.signal_candle_timestamp == START + timedelta(minutes=1)
    assert trade.entry_candle_timestamp == START + timedelta(minutes=2)
    assert trade.exit_candle_timestamp == START + timedelta(minutes=2)
    assert trade.entry_price == Decimal("103")
    assert trade.exit_price == Decimal("104")
    assert trade.gross_return_pct == Decimal("100") / Decimal("103")
    assert trade.net_return_pct == trade.gross_return_pct - Decimal("0.2")
    assert result.metrics.trade_count == 1
    assert result.metrics.winning_trades == 1


def test_short_return_is_positive_when_price_falls() -> None:
    result = run(
        [
            candle(0, open_price="100", high="101", low="100", close="100"),
            candle(1, open_price="100", high="100", low="98", close="98"),
            candle(2, open_price="97", high="98", low="95", close="96"),
        ]
    )

    assert len(result.trades) == 1
    assert result.trades[0].direction is SignalDirection.SHORT
    assert result.trades[0].gross_return_pct == Decimal("100") / Decimal("97")


def test_signal_uses_only_the_trailing_window_and_next_bar_prices_set_the_result() -> None:
    past = [
        candle(0, open_price="100", high="100", low="99", close="100"),
        candle(1, open_price="100", high="102", low="100", close="102"),
    ]
    first = run(past + [candle(2, open_price="103", high="104", low="102", close="104")])
    changed_future = run(
        past + [candle(2, open_price="103", high="110", low="101", close="101")]
    )

    assert first.trades[0].signal_candle_timestamp == changed_future.trades[0].signal_candle_timestamp
    assert first.trades[0].direction is changed_future.trades[0].direction
    assert first.trades[0].reason_codes == changed_future.trades[0].reason_codes
    assert first.trades[0].exit_price != changed_future.trades[0].exit_price


def test_trades_do_not_overlap_and_metrics_count_flat_trades() -> None:
    result = run(
        [
            candle(0, open_price="100", high="100", low="99", close="100"),
            candle(1, open_price="100", high="102", low="100", close="102"),
            candle(2, open_price="103", high="104", low="102", close="104"),
            candle(3, open_price="104", high="105", low="103", close="104"),
        ]
    )

    assert len(result.trades) == 2
    assert result.trades[0].exit_candle_timestamp <= result.trades[1].signal_candle_timestamp
    assert result.metrics.trade_count == 2
    assert result.metrics.winning_trades == 1
    assert result.metrics.flat_trades == 1
    assert result.metrics.win_rate_pct == Decimal("50")


def test_existing_breakout_strategy_can_be_replayed_without_reimplementing_its_rule() -> None:
    backtest = BacktestEngine(
        BreakoutSignalStrategy(),
        BacktestConfig(lookback_bars=2, holding_bars=1, cost_bps_per_side=Decimal("0")),
    )
    result = run(
        [
            candle(0, open_price="100", high="100", low="99", close="100"),
            candle(1, open_price="100", high="102", low="100", close="102"),
            candle(2, open_price="103", high="104", low="102", close="103"),
        ],
        backtest=backtest,
    )

    assert result.strategy_type is SignalType.BREAKOUT
    assert result.trades[0].direction is SignalDirection.LONG


def test_existing_reversal_strategy_can_be_replayed() -> None:
    backtest = BacktestEngine(
        ReversalSignalStrategy(),
        BacktestConfig(lookback_bars=2, holding_bars=1, cost_bps_per_side=Decimal("0")),
    )
    result = run(
        [
            candle(0, open_price="100", high="100", low="99", close="100"),
            candle(1, open_price="100", high="103", low="100", close="103"),
            candle(2, open_price="102", high="104", low="101", close="102"),
        ],
        backtest=backtest,
    )

    assert result.strategy_type is SignalType.REVERSAL
    assert result.trades[0].direction is SignalDirection.SHORT


def test_no_signal_returns_zeroed_metrics() -> None:
    result = run(
        [
            candle(0, open_price="100", high="101", low="99", close="100"),
            candle(1, open_price="100", high="101", low="99", close="100"),
            candle(2, open_price="100", high="101", low="99", close="100"),
        ]
    )

    assert result.trades == ()
    assert result.metrics.trade_count == 0
    assert result.metrics.win_rate_pct == 0
    assert result.metrics.average_net_return_pct == 0


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("lookback_bars", 1, "at least 2"),
        ("lookback_bars", True, "integer"),
        ("holding_bars", 0, "positive"),
        ("holding_bars", 1.5, "integer"),
        ("cost_bps_per_side", Decimal("-1"), "non-negative"),
        ("cost_bps_per_side", Decimal("NaN"), "finite"),
    ],
)
def test_config_rejects_invalid_replay_assumptions(field: str, value: object, message: str) -> None:
    values: dict[str, object] = {
        "lookback_bars": 2,
        "holding_bars": 1,
        "cost_bps_per_side": Decimal("0"),
    }
    values[field] = value

    with pytest.raises(ValueError, match=message):
        BacktestConfig(**values)  # type: ignore[arg-type]


def test_backtest_rejects_invalid_candle_series() -> None:
    valid = candle(0, open_price="100", high="101", low="99", close="100")
    duplicate_time = valid.model_copy()
    wrong_symbol = candle(
        1,
        open_price="100",
        high="101",
        low="99",
        close="100",
        symbol="INFY",
    )

    with pytest.raises(ValueError, match="strictly chronological"):
        run([valid, duplicate_time])
    with pytest.raises(ValueError, match="same symbol"):
        run([valid, wrong_symbol])
    with pytest.raises(ValueError, match="OHLC prices"):
        run(
            [
                valid,
                candle(1, open_price="100", high="101", low="0", close="100"),
            ]
        )
    with pytest.raises(ValueError, match="must not be empty"):
        run([])
