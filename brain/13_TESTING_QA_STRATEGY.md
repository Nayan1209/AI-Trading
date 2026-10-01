# Testing & QA Strategy
**Version:** 0.1 | **Status:** Draft

Test levels: static analysis; unit tests; contract/API tests; integration tests; database tests; AI schema/prompt tests; strategy backtests; broker sandbox/paper tests; failure injection; end-to-end paper trading; controlled production validation.

Critical tests: position sizing, risk limits, duplicate order prevention, partial fills, reconciliation, stale data, broker outage, malformed AI output, prompt injection, kill switch, restart recovery.

No live release without mandatory safety, reconciliation, risk, and operational tests.