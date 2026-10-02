# AI Context Builder Specification

**Document ID:** AI-002  
**Status:** Contract implementation started  
**Parent:** Phase 4 — AI Analysis Engine  
**Depends on:** AI-001, SIG-001

## Objective

Create the deterministic adapter between the existing signal-engine output and the AI-001 analyst boundary. It converts a validated `SignalCandidate` plus explicitly supplied market/context data into `AIAnalysisContext` without making model, web, broker, risk, or execution calls.

## Required behavior

- Preserve candidate identity and trading symbol.
- Preserve signal rank, type, direction, strategy score, and reason codes.
- Require an explicit timeframe.
- Accept market features, relevant context, and portfolio constraints only as caller-supplied structured mappings.
- Never invent market, news, portfolio, or price data.
- Produce the exact `AIAnalysisContext` contract consumed by AI-001.
- Keep AI output downstream of deterministic signal generation; this stage makes no trade decision.

## Safety boundary

- No LLM/network calls.
- No broker or order execution access.
- No risk override capability.
- No secrets or credentials.
- External context is passed through as untrusted data and does not control system behavior.

## Acceptance criteria

1. A valid `SignalCandidate` deterministically produces one `AIAnalysisContext`.
2. Signal identity and strategy metadata are preserved exactly.
3. Empty timeframe is rejected by the AI-001 context contract.
4. No-trade or neutral signals remain representable without special-case execution behavior.
5. Deterministic tests cover mapping, preservation, and invalid input boundaries.
