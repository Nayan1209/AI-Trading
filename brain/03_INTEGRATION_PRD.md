# Integration Product Requirements Document
**Version:** 0.1 | **Status:** Draft

## Objective
Define how internal services and external providers collaborate.

## Core Integrations
1. Broker API
2. Market-data provider(s)
3. AI provider
4. News/context provider
5. PostgreSQL
6. Redis/queue
7. Notifications
8. Monitoring/logging
9. Optional identity provider

## Principles
- External providers are accessed through adapters.
- Strategy logic is broker-independent.
- Normalize external data into internal contracts.
- Every external call has timeout, retry, error, and audit behavior.
- Credentials stay outside source code.

## Main Flow
Market Data → Data Engine → Scanner → Signal Engine → AI → Planner → Risk → Execution → Broker → Reconciliation → Monitor → Journal.
