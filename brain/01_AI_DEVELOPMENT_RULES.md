# AI Development Rules
**Version:** 0.1 | **Status:** Draft

1. Never invent APIs, credentials, database fields, broker behavior, regulatory requirements, or library behavior.
2. Verify assumptions against authoritative documentation before implementation.
3. Do not expose secrets in code, logs, screenshots, prompts, tests, commits, or documentation.
4. Prefer small, reversible changes.
5. AI must never bypass the Risk Engine.
6. AI must never modify withdrawal, bank-account, or security controls.
7. AI-generated order instructions must pass schema validation and deterministic risk validation.
8. No live order capability may be enabled in development or test environments.
9. Every live decision must be traceable through audit records.
10. A kill switch must stop new trading activity.
11. Use typed interfaces and explicit schemas.
12. Fail closed for safety-critical operations.
13. Never silently swallow broker or market-data errors.
14. Add tests for trading-critical changes.
15. Prompts, models, strategies, and schemas are versioned.
16. AI must be allowed to return NO_TRADE.
17. Change flow: requirement → design → implementation → tests → documentation → review → deployment.
