# RISK-001 Risk Engine Specification

**Document ID:** RISK-001  
**Status:** Contract implementation started  
**Parent:** Phase 5 — Trade Planner & Risk Engine  
**Depends on:** AI-007

## Objective

Provide the first deterministic safety gate after AI analysis. RISK-001 converts a coherent BUY/SELL analysis into a bounded quantity only when explicit account and risk constraints permit it.

## Required behavior

- Accept only an `AIAnalysis` that first passes AI-007 integrity validation.
- Reject WATCH and NO_TRADE.
- Require positive account equity and entry/stop prices.
- Calculate risk budget from explicit equity and risk percentage.
- Calculate per-unit risk from entry and stop-loss distance.
- Bound quantity by both risk budget and maximum notional exposure.
- Round quantity down to the supplied lot size.
- Reject zero resulting quantity.
- Never use leverage or hidden account state.
- Never place or modify orders.
- Never override a deterministic risk limit because of model confidence.

## Safety boundary

RISK-001 is the mandatory deterministic risk gate. Passing it authorizes only a bounded planning result; it does not execute an order. Broker validation and execution remain separate.

## Acceptance criteria

1. A valid BUY can produce a positive lot-aligned quantity.
2. A valid SELL can produce a positive lot-aligned quantity.
3. Risk budget is never exceeded by stop-loss risk.
4. Maximum notional exposure is never exceeded.
5. Quantity is rounded down to the lot size.
6. WATCH/NO_TRADE is rejected.
7. Invalid equity, risk limits, prices, or lot size are rejected.
8. A quantity that rounds to zero is rejected.
9. No broker, network, credential, or model provider is required.
