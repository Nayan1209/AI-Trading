# Integration Specification
**Version:** 0.1 | **Status:** Draft

## Broker
Initial adapter target: Upstox, subject to final selection and account/API eligibility.

Responsibilities: authentication, instruments, orders, modifications/cancellations, status, positions, funds where supported, streaming updates, reconciliation.

## AI
Provider-agnostic interface for candidate analysis, news analysis, plan review and post-trade analysis.

## Market Data
Need live/near-live data suitable for strategy, historical candles, identifiers, session metadata, and quality/staleness indicators.

## Failure
Critical dependency failures must enter a defined safe state rather than create guessed trading actions.
