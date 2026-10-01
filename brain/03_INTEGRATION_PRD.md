# Integration Product Requirements Document
**Version:** 0.2 | **Status:** Active Draft

## Objective
Define how internal services and external providers collaborate without coupling trading logic to a specific broker.

## Initial Provider Decision
**Initial Indian broker + market-data provider: Groww Trading API.**

Selection is based on the current official Groww API documentation and the project's India-first requirement. The integration must remain adapter-based so the system can add another broker/data provider later without rewriting strategy logic.

## Groww Capabilities In Scope
- NSE and BSE equity/CASH support.
- F&O support for future expansion.
- Live quote/LTP/OHLC APIs.
- Live streaming feed for subscribed instruments.
- Historical candle data for development and backtesting.
- Instrument master / exchange-token mapping.
- User profile, holdings, positions and margin/account information where supported.
- Order placement, modification, cancellation, status and trade retrieval.

## Authentication
Groww documents access-token authentication and API-key-based flows. The current project account has an approved Groww API key. The actual key, secret, access token and TOTP values must never enter Git or project documentation.

Groww documents that API-key/secret token generation requires daily approval, and access tokens expire daily at 6:00 AM. The authentication layer must therefore treat credentials as short-lived runtime state and implement token refresh/recovery behavior.

## Market Data Requirements
The Data Engine must normalize Groww data into internal contracts for:
- instrument identity
- exchange and segment
- timestamp
- OHLC
- LTP
- volume
- market depth when available
- source/provider metadata
- freshness/staleness status

Live feed subscriptions must be bounded by provider limits and managed centrally. The current Groww documentation states that up to 1,000 instruments can be subscribed to at a time.

## Order Integration Requirements
The broker adapter must support, where permitted by the provider and enabled for the account:
- create order
- modify order
- cancel order
- order status
- order detail
- order list
- trade/fulfilment retrieval
- positions/holdings reconciliation

**No live order execution is enabled by this document.** Execution remains behind deterministic risk gates, environment controls and later deployment approval.

## Rate Limits
The adapter must respect provider limits rather than retry aggressively:
- Authentication: 5 requests/sec, 30 requests/minute.
- Orders: 10 requests/sec, 250 requests/minute.
- Live data: 10 requests/sec, 300 requests/minute.
- Non-trading APIs: 20 requests/sec, 500 requests/minute.
- Access-token endpoint: 150 requests/24 hours.

The exact limits must be treated as provider configuration and re-verified against official documentation before production.

## Network / Static IP
Groww's current API-trading guidance requires API order placement to originate from a registered static IP. The production architecture therefore requires a controlled runtime with a stable public IP before live order placement is considered.

A developer workstation/dynamic home IP must not be treated as the production trading endpoint.

## Core Integrations
1. Groww broker + market-data adapter
2. AI provider
3. News/context provider
4. PostgreSQL
5. Redis/queue
6. Notifications
7. Monitoring/logging
8. Optional identity provider

## Principles
- External providers are accessed through adapters.
- Strategy logic is broker-independent.
- Normalize external data into internal contracts.
- Every external call has timeout, retry, error, rate-limit, and audit behavior.
- Credentials stay outside source code.
- Provider failures must fail safe and must never cause guessed trading actions.

## Main Flow
Market Data → Data Engine → Scanner → Signal Engine → AI → Planner → Risk → Execution → Groww Adapter → Reconciliation → Monitor → Journal.
