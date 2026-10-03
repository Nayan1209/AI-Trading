# EXEC-001 — Groww Broker Adapter Boundary

**Status:** Implementation started; provider-facing execution remains disabled by default.

## Purpose

Define a narrow adapter boundary between the deterministic trading core and Groww. The adapter consumes an already-approved PLAN-001 trade plan together with an approved RISK-002 portfolio decision. It must not calculate strategy, risk, or portfolio limits itself.

## Required invariants

1. PLAN-001 must already have produced the order intent.
2. RISK-002 approval is mandatory before any provider-facing submission path is considered.
3. Provider identifiers and request formatting stay inside the adapter.
4. Development and paper environments must not submit orders.
5. Production submission remains locked until EXEC-002 verifies the production runtime controls.
6. No credentials, access tokens, TOTP values, or secrets are stored in source control or documentation.
7. Broker failures, missing identifiers, and malformed responses fail closed; they are never converted into guessed requests.

## Adapter boundary

The implementation boundary should expose:

- a provider-shaped immutable order request
- an immutable result object
- a small transport protocol that can later be backed by the authenticated Groww client
- explicit environment and execution-control gates

The adapter must not expose Groww SDK objects to strategy, AI, scanner, risk, or planning code.

## Environment policy

| Environment | Provider submission |
|---|---|
| development | Disabled |
| paper | Disabled |
| staging | Disabled until explicitly approved by runtime controls |
| production | Locked until EXEC-002 verifies all required controls |

## Safety boundary

EXEC-001 is an integration boundary, not permission to place real-money orders. The next execution milestone, EXEC-002, is responsible for the controlled runtime/static-IP prerequisites documented by the project integration specification.

No broker credentials are required for deterministic tests of this boundary.
