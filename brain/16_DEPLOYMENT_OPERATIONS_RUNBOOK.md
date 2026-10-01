# Deployment & Operations Runbook
**Version:** 0.1 | **Status:** Draft

## Environments
Development → Staging/Paper → Production.

## Principles
Secrets injected at runtime; migrations versioned; deployments reversible; production changes audited.

## Monitoring
Service health, market-data freshness, broker connectivity, order rejection rate, reconciliation mismatches, AI errors/latency, queue depth, database health, risk events, trading-halt state.

## Recovery
Stop new trading when critical dependencies fail. Reconcile broker state after recovery. Never assume order state after timeout. Resume only after consistency checks.