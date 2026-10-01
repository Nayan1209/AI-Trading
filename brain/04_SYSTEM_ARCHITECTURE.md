# System Architecture
**Version:** 0.1 | **Status:** Draft

## Logical Components
API Gateway; Authentication/Authorization; Market Data Service; Instrument Service; Scanner; Signal Engine; AI Analysis Service; Trade Planner; Risk Engine; Execution Service; Broker Adapters; Portfolio/Position Service; Monitoring; Learning/Journal; Notifications; Audit; PostgreSQL; Redis/Queue; Web Dashboard.

## Flow
Market Data → Normalization → Scanner → Signal Engine → AI → Trade Planner → Risk Engine → Execution → Broker → Reconciliation/Monitoring → Journal/Analytics.

## Rules
- Risk Engine is a mandatory gate.
- Execution is isolated from AI inference.
- Broker-specific code lives only in adapters.
- Critical state is persisted.
- Events use correlation IDs.
- Safety-critical services fail closed.

## Future Multi-Market Architecture
Market Adapter → Common Market Contract → Core Scanner/Signals/AI/Risk → Broker Adapter.
