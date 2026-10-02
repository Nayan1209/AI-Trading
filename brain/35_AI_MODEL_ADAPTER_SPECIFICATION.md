# AI Model Adapter Specification

**Document ID:** AI-005  
**Status:** Contract implementation started  
**Parent:** Phase 4 — AI Analysis Engine  
**Depends on:** AI-001, AI-003, AI-004

## Objective

Create a provider-independent model-adapter boundary that accepts the deterministic `AIPrompt` artifact and returns an immutable model response without coupling the trading system to a specific AI vendor.

## Required behavior

- Accept only an `AIPrompt` produced by AI-004.
- Keep provider-specific transport outside the core trading contracts.
- Return model text together with explicit model and prompt versions.
- Reject empty model responses.
- Require the response prompt version to match the prompt that was sent.
- Preserve the response as opaque text; structured parsing belongs to a later boundary.
- Remain deterministic and network-free in the core contract tests.

## Adapter contract

The core adapter exposes one operation: `complete(prompt) -> AIModelResponse`.

A future Claude, OpenAI, or other provider adapter may implement this protocol. Provider SDKs, HTTP calls, retries, credentials, rate limits, and provider-specific payload formats must remain outside this core boundary.

## Safety boundary

- No broker or order execution access.
- No risk override capability.
- No credentials or secrets in the contract.
- No market-data retrieval.
- No hidden network call in the core implementation.
- The model response is untrusted text and must not be treated as an approved trade decision.

## Acceptance criteria

1. Only an `AIPrompt` can enter the adapter boundary.
2. Empty model output is rejected.
3. A response with a mismatched prompt version is rejected.
4. Model version is explicit and non-empty.
5. Response content is preserved exactly; no trading interpretation is performed.
6. Deterministic tests require no network, model vendor, broker, or external service.
