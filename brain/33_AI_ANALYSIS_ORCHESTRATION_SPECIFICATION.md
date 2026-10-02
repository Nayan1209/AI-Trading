# AI Analysis Orchestration Specification

**Document ID:** AI-003  
**Status:** Contract implementation started  
**Parent:** Phase 4 — AI Analysis Engine  
**Depends on:** AI-001, AI-002, SIG-001

## Objective

Create the deterministic orchestration boundary that connects a validated signal-engine `SignalCandidate` to the AI-001 analyst boundary through the AI-002 context builder.

## Required behavior

- Accept only a validated `SignalCandidate` and explicitly supplied context mappings.
- Use `AIAnalysisContextBuilder` to construct the exact AI-001 context.
- Use the injected `AIAnalyst` to validate provider input and output.
- Preserve the existing provider-independent AI boundary.
- Make no market-data, news, broker, risk, or execution calls.
- Never invent missing market/context values.
- Keep `NO_TRADE` and neutral signals valid.
- Keep provider/model selection outside this orchestration layer.

## Safety boundary

- No direct network or LLM calls.
- No broker or order execution access.
- No risk override capability.
- No secrets or credentials.
- External context remains caller-supplied and untrusted.
- Returned analysis remains downstream of deterministic risk controls.

## Acceptance criteria

1. A `SignalCandidate` plus explicit context deterministically reaches the AI-001 provider boundary.
2. The provider receives exactly the context produced by AI-002.
3. Provider output is returned only after AI-001 validation.
4. Empty timeframe and invalid AI output fail closed through the existing contracts.
5. Deterministic tests cover composition and propagation without network access.
