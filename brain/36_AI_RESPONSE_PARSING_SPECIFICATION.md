# AI Response Parsing Specification

**Document ID:** AI-006  
**Status:** Contract implementation started  
**Parent:** Phase 4 — AI Analysis Engine  
**Depends on:** AI-001, AI-004, AI-005

## Objective

Create a deterministic boundary that converts the untrusted opaque text returned by AI-005 into the validated `AIAnalysis` contract defined by AI-001.

## Required behavior

- Accept only an `AIModelResponse` from AI-005.
- Parse model output as JSON; free-form prose is not accepted.
- Require a JSON object rather than an array, scalar, or null value.
- Allow only the fields required by the AI-001 analysis contract.
- Reject missing or unsupported fields instead of silently ignoring them.
- Preserve financial numeric values as `Decimal` values during parsing.
- Take `model_version` and `prompt_version` from the trusted AI-005 response metadata rather than from model-generated content.
- Run the complete AI-001 Pydantic validation before returning an analysis.
- Never execute orders, call a broker, override risk controls, fetch market data, or make network calls.

## Expected model payload

The model response content must contain exactly these fields:

```text
{
  "decision": "BUY | SELL | WATCH | NO_TRADE",
  "confidence": 0..1,
  "setup": "...",
  "reason_codes": ["..."],
  "entry": number | null,
  "stop_loss": number | null,
  "target": number | null,
  "invalidation": "..."
}
```

Version metadata is supplied by AI-005 and is not trusted when embedded in model content.

## Safety boundary

The parser does not decide whether a trade is safe or executable. It only establishes that the model output conforms to the deterministic AI-001 schema. Later deterministic planning and risk stages remain mandatory.

## Acceptance criteria

1. Valid JSON produces a validated `AIAnalysis`.
2. Invalid JSON is rejected.
3. Non-object JSON is rejected.
4. Missing required fields are rejected.
5. Unsupported fields are rejected.
6. Invalid AI-001 values are rejected.
7. Decimal prices and confidence remain exact after parsing.
8. Model and prompt versions come from the AI-005 response metadata.
9. Tests require no model provider, network, broker, credentials, or external service.
