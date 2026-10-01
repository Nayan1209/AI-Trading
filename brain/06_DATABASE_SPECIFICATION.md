# Database Specification
**Version:** 0.1 | **Status:** Draft

Database: PostgreSQL.

## Core Tables
users, roles, broker_accounts, instruments, instrument_mappings, market_ticks, candles, market_sessions, signals, trade_candidates, ai_decisions, trade_plans, risk_checks, orders, order_events, positions, trades, portfolio_snapshots, alerts, audit_logs, system_events, model_versions, prompt_versions, strategy_versions.

## Relationships
User → Broker Account → Orders → Positions → Trades.
Instrument → Market Data → Signals → Candidates → Plans.
AI Decision → Plan → Risk Check → Order → Trade.

## Rules
UTC timestamps; fixed-precision monetary values; no floating-point storage for quantities; append-oriented audit records; no plaintext credentials; indexes on high-frequency lookup fields.
