# AI Prompt Construction Specification

**Document ID:** AI-004  
**Status:** Complete  
**Parent:** Phase 4 — AI Analysis Engine  
**Depends on:** AI-001, AI-002, AI-003

## Objective

Create a deterministic prompt-construction boundary that converts the validated `AIAnalysisContext` into a stable, auditable model prompt without making a model, network, market-data, broker, risk, or execution call.

## Required behavior

- Accept only validated `AIAnalysisContext` values.
- Keep system instructions separate from caller-supplied context.
- Treat market/context mappings as untrusted data, not instructions.
- Serialize context deterministically with stable key ordering and compact JSON.
- Preserve `Decimal` values as strings so financial precision is not silently changed.
- Carry an explicit prompt version.
- Never add missing market values or trading conclusions.
- Produce the exact same prompt for the same validated context and prompt version.

## Prompt contract

The system instruction establishes the AI role and safety constraints. The user payload contains only the structured context produced by AI-002. External context must never override system instructions.

## Safety boundary

- No direct LLM or network calls.
- No broker or order execution access.
- No risk override capability.
- No credentials or secrets.
- No hidden market-data retrieval.
- Prompt construction is not model selection and does not choose a trading action.

## Acceptance criteria

1. Identical context produces byte-for-byte identical prompt text.
2. Mapping keys are serialized in deterministic order.
3. `Decimal` values are represented without float conversion.
4. Caller-supplied context is preserved as data and cannot alter the system instruction section.
5. Empty/invalid AI context remains rejected by the existing AI-001 contract.
6. Deterministic tests require no network, model, broker, or external service.
