# Historical Signal Backtesting Specification

**Document ID:** TEST-001<br />
**Status:** First deterministic replay implementation complete<br />
**Scope:** Offline single-instrument replay of an existing SIG-001 strategy over validated historical candles

## Objective

Provide a reproducible way to evaluate the existing observation-only signal rules against historical OHLCV data, without routing a signal through AI, trade planning, risk authorization, paper execution, or a broker.

## Input Contract

- One chronological series of validated internal `Candle` values.
- Every candle must share the same provider symbol, exchange, and timeframe.
- Timestamps must be timezone-aware, unique, and strictly increasing.
- The caller supplies canonical `internal_id` and `trading_symbol` values explicitly.
- One existing deterministic SIG-001 strategy is supplied per run.
- `lookback_bars`, `holding_bars`, and per-side transaction cost in basis points are explicit configuration; there are no implicit cost assumptions.

## Replay Rules

1. After each eligible candle is complete, construct the same scanner feature contract from the trailing `lookback_bars` only: first and latest close, highest candle high, lowest candle low, and close-to-close percentage change.
2. Evaluate the supplied existing signal strategy using that completed window. The window never includes a later candle.
3. If a LONG or SHORT observation is emitted, enter at the next candle's open.
4. Exit at the close of the configured holding bar. `holding_bars = 1` means enter at the next candle's open and exit at that candle's close.
5. Keep at most one position open. Resume signal evaluation at the exit candle close; the next possible entry is on the following candle.
6. Calculate the gross return as a percentage of entry price. Subtract twice the configured per-side basis-point cost to obtain net return. This cost is a caller-supplied aggregate friction estimate; the engine does not infer brokerage, taxes, spread, or slippage.
7. Do not evaluate a signal unless the full configured entry and exit candles exist.

## Output

The immutable result contains signal/entry/exit candle timestamps, strategy type, direction, raw fill prices, gross and net return percentages, and reason codes for each trade. Candle timestamps are preserved as labels from the input; bar order determines replay sequencing. Summary metrics include trade count, win/loss/flat counts, win rate, average net trade return, and the sum of net trade returns.

The return sum treats each trade as an equal-notional observation. It is not a compounded account return, equity curve, drawdown estimate, or risk-adjusted performance measure. The module does not size positions or model concurrent trades.

## Safety and Limitations

- Replay is local and deterministic; it makes no network, database, AI, or broker calls.
- Strategy signals remain observations. A backtest result is not an execution or risk approval.
- The first version supports one instrument and one strategy per run.
- Signals use only completed candles' closing prices and trailing OHLC values. Input candle timestamps are treated as labels, not as a separate source of close-time or fill-time information.
- Entry/exit assumptions are next-bar open and holding-bar close. Stop-losses, targets, partial fills, gaps within bars, market impact, and portfolio constraints are not modeled.
- Results depend on the caller's history, timeframe, lookback, holding period, and cost estimate; they do not predict future performance.

## Acceptance Criteria

- Replays existing momentum, reversal, or breakout strategy objects without duplicating their decision rules.
- Rejects invalid or mixed-instrument candle series and invalid configuration.
- Does not use future candles to form a signal.
- Uses deterministic next-open entries, timed close exits, and explicit two-sided cost deduction.
- Returns immutable trade and summary records, including correct empty-run metrics.
- Requires no credentials, external service, AI model, or live trading operation.
