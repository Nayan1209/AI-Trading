# AI Analysis Integrity Gate Specification

**Document ID:** AI-007  
**Status:** Contract implementation started  
**Parent:** Phase 4 — AI Analysis Engine  
**Depends on:** AI-001, AI-004, AI-005, AI-006

## Objective

Create a deterministic post-parsing integrity boundary that checks whether a validated `AIAnalysis` is internally coherent before it can enter later planning and risk stages.

## Required behavior

- Accept only the validated `AIAnalysis` contract from AI-006.
- Preserve the analysis as immutable data; do not rewrite model output.
- Require BUY and SELL analyses to contain entry, stop-loss, and target prices.
- For BUY, require `stop_loss < entry < target`.
- For SELL, require `target < entry < stop_loss`.
- Allow WATCH and NO_TRADE analyses without execution prices.
- Reject execution prices on WATCH and NO_TRADE so an advisory response cannot silently become an order plan.
- Preserve model and prompt versions for downstream auditability.
- Do not calculate position size, risk budget, leverage, or order quantity.
- Do not approve execution or override the future deterministic risk engine.

## Safety boundary

AI-007 is an integrity check, not a risk engine. Passing this gate does not mean a trade is safe, profitable, or executable. Deterministic planning and the RISK-001 safety gate remain mandatory.

## Acceptance criteria

1. Valid BUY analysis with ordered prices is accepted.
2. Valid SELL analysis with ordered prices is accepted.
3. BUY/SELL without complete execution prices is rejected.
4. BUY with incorrect price ordering is rejected.
5. SELL with incorrect price ordering is rejected.
6. WATCH/NO_TRADE without prices is accepted.
7. WATCH/NO_TRADE carrying execution prices is rejected.
8. The returned analysis is the same validated immutable contract.
9. Tests require no model provider, network, broker, credentials, or external service.
