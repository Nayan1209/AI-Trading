# Integration Specification
**Version:** 0.2 | **Status:** Active Draft

## Initial Broker / Market Data Provider
**Groww Trading API** is the initial India-first provider.

The integration is implemented through adapters so the core trading system remains broker-independent and can later support multiple providers/markets.

## Groww Adapter Responsibilities
### Authentication
- Manage runtime access-token creation/refresh.
- Never persist API secrets or access tokens in source control.
- Detect expired/invalid sessions and fail safely.
- Respect Groww authentication rate limits.

### Instruments
- Consume Groww instrument master data.
- Map exchange + segment + exchange token + trading symbol to an internal `instrument_id`.
- Preserve provider identifiers for reconciliation.

### Market Data
- REST quote/LTP/OHLC retrieval.
- Streaming feed subscription for equity/index/derivative instruments.
- Historical candle retrieval.
- Normalize timestamps, prices, volumes and source metadata.
- Detect stale, missing, duplicated or out-of-order events.

### Trading
- Place, modify and cancel orders.
- Retrieve order status/details/list.
- Retrieve trade/fulfilment details.
- Retrieve positions, holdings and margin where supported.
- Reconcile local state with broker state.

## Provider Limits
Current documented Groww limits:

| API type | Per second | Per minute |
|---|---:|---:|
| Authentication | 5 | 30 |
| Orders | 10 | 250 |
| Live Data | 10 | 300 |
| Non-Trading | 20 | 500 |

The access-token endpoint also has a documented 150 requests/24h limit. Live feed supports up to 1,000 instrument subscriptions at a time.

The adapter must use bounded retries, exponential backoff where appropriate, and circuit-breaking/safe-state behavior instead of uncontrolled retry loops.

## Static IP / Production Network
Groww's current trading-API guidance states that API order placement must originate from a registered static IP. Production order execution therefore requires a controlled runtime with a stable public IP that is registered with Groww.

The static-IP requirement is an **execution deployment prerequisite**, not a reason to expose the database or application publicly.

## Environment Separation
- `development`: mock provider / fixtures; no broker orders.
- `paper`: real market data may be consumed, but no live broker order is allowed.
- `staging`: provider connectivity tests with execution disabled unless explicitly approved.
- `production`: live execution only after all deterministic safety gates and operational checks pass.

## Failure Handling
Any of the following must put execution into a safe state:
- expired/invalid authentication
- provider outage
- stale market data
- instrument mapping failure
- rate-limit exhaustion
- network instability
- reconciliation mismatch
- risk-service unavailable
- unexpected broker response

A failure must never be converted into a guessed order.

## AI Boundary
The AI may propose analysis or a trade plan. It does not receive direct credentials or unrestricted broker API access. The execution path remains deterministic and policy-controlled.

## Current State
Groww account/API key approval has been confirmed by the project owner. No secret values are stored in the repository. No live order has been placed by this project.
