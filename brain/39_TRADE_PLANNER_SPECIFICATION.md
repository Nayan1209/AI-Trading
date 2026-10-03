# PLAN-001 Deterministic Trade-Planning Specification

**Document ID:** PLAN-001  
**Status:** Implementation started  
**Parent:** Phase 5 — Trade Planner & Risk Engine  
**Depends on:** AI-007, RISK-001

## Objective

Create a deterministic, broker-independent trade plan from a validated AI analysis and the RISK-001 bounded quantity result.

## Required behavior

- Accept only BUY/SELL analyses that pass the existing AI integrity and risk gates.
- Preserve entry, stop-loss, and target exactly from the validated analysis.
- Use RISK-001 for quantity, risk budget, estimated risk, and notional limits.
- Produce an immutable planning result suitable for a later execution boundary.
- Reject WATCH/NO_TRADE through the risk gate.
- Never calculate a new discretionary price or override deterministic risk limits.
- Never place, modify, or cancel an order.
- Never call a broker, model provider, network service, or credential store.

## Safety boundary

PLAN-001 creates an order intent only. It is not execution authorization. Broker validation, order submission, reconciliation, and live credentials remain outside this boundary.

## Acceptance criteria

1. BUY analysis produces a complete BUY trade plan with bounded quantity.
2. SELL analysis produces a complete SELL trade plan with bounded quantity.
3. Entry, stop-loss, and target are preserved from AIAnalysis.
4. Quantity and risk values come from RISK-001.
5. Invalid AI analysis is rejected before a plan is produced.
6. WATCH/NO_TRADE cannot become an executable plan.
7. No broker or network dependency is required.
8. The result is immutable and deterministic for identical inputs.
