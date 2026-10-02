# Data Quality Monitoring Specification
**Document ID:** DATA-007  
**Status:** Implementation complete; CI validation pending  
**Scope:** Deterministic monitoring of normalized market-data completeness, duplicates, gaps and persistence health

## Objective

Detect market-data quality problems before candles are consumed by scanner, signal or AI components. DATA-007 is deliberately deterministic and does not require live Groww credentials or a production database in CI.

## Quality Checks

The monitoring boundary evaluates a normalized `Candle` sequence for:

- **Validity:** every candle must pass the existing DATA-004 `validate_candle()` rules.
- **Duplicates:** candle identity is `(symbol, exchange, timeframe, timestamp)`; repeated identities are counted and fail the quality report.
- **Completeness:** when the caller supplies an expected timestamp set, observed expected timestamps are compared with that set.
- **Gaps:** missing expected timestamps are returned explicitly. The monitor does not invent a trading calendar because overnight, weekend and exchange-holiday gaps can be legitimate.
- **Persistence health:** a caller-supplied health check can be evaluated without coupling the monitor to a specific database implementation.

## Completeness Contract

Expected timestamps are supplied by the caller. This keeps market-session knowledge outside the generic monitor and prevents false gap alarms across non-trading periods.

`completeness_ratio` is the fraction of expected timestamps observed. If no expected timestamps are supplied, the monitor reports `1.0` rather than pretending to know the expected trading schedule.

## Failure Semantics

A quality report is unhealthy when any of the following is true:

- one or more candles are invalid;
- duplicate candle identities are present;
- expected timestamps are missing; or
- an explicitly evaluated persistence health check is unhealthy.

The report retains deterministic reason strings so later dashboard/alerting layers can consume the result without reimplementing validation logic.

## Safety

- No Groww access token is required.
- No live Groww API call is made by quality tests.
- No production PostgreSQL connection is required by CI.
- No order or execution functionality is involved.
- Quality monitoring is fail-closed for invalid, duplicate, incomplete or unhealthy persistence states.

## Acceptance Criteria

- A deterministic quality report model exists.
- Existing candle validation rules are reused rather than duplicated.
- Duplicate candle identities are detected.
- Caller-defined missing timestamps are detected and exposed as gaps.
- Completeness is measurable without assuming a trading calendar.
- Persistence health can be evaluated through a provider-independent callable.
- Unit tests cover healthy, duplicate, gap, invalid and persistence-health cases.
- Documentation and build status are updated with the milestone.

## Next Gate

After DATA-007 CI is green, the next market-data milestone is to integrate the quality report into the operational data pipeline before scanner/signal work begins. No live execution functionality is enabled by DATA-007.
