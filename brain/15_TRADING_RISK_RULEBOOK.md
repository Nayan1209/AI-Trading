# Trading & Risk Rulebook
**Version:** 0.1 | **Status:** Draft

## Required Controls
Maximum risk per trade; maximum portfolio exposure; position concentration; maximum daily loss; maximum drawdown; maximum open positions; minimum liquidity; minimum R:R; correlated exposure; session constraints; data-quality constraints; broker-health constraints.

## Safety
If required input is missing, stale, contradictory, or unreliable, default to NO_TRADE / SAFE MODE.

## Autonomy
AI may choose permitted actions but cannot change this rulebook at runtime.

## Emergency
Global trading halt; block new orders; cancel eligible pending orders; reconcile positions; alert owner/operator; preserve audit trail.

Thresholds will be finalized after research, backtesting, operational testing, and appropriate compliance review.