# AI Analyst Specification

**Document ID:** AI-001  
**Status:** Contract implementation started  
**Parent:** Phase 4 — AI Analysis Engine

## Objective

Create a provider-independent boundary between deterministic signal output and any future AI model. The boundary must accept only structured context and return only validated structured analysis.

## Required input

- instrument
- timeframe
- market features
- signal features
- relevant context
- portfolio constraints

## Required output

```json
{"decision":"BUY|SELL|WATCH|NO_TRADE","confidence":0.0,"setup":"string","reason_codes":["string"],"entry":0,"stop_loss":0,"target":0,"invalidation":"string"}
```

The implementation additionally records `model_version` and `prompt_version` so model/prompt provenance is never lost.

## Safety boundary

- No broker or order execution access.
- No risk override capability.
- No secret or credential handling.
- No fabricated market/news data.
- `NO_TRADE` is always a valid outcome.
- External web/news content remains untrusted and cannot override system instructions.
- The AI output is not an execution instruction; deterministic risk controls remain downstream.

## Implementation

`src/ai_analyst.py` implements the validation boundary and provider protocol. It intentionally does not select an LLM provider or make network calls. `tests/test_ai_analyst.py` provides deterministic provider-stub coverage.
