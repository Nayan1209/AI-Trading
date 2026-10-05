# Build Status / Development Tracker
**Version:** 5.0

| ID | Workstream | Design | Build | Test | Status |
|---|---|---:|---:|---:|---|
| DOC-001 | Master Project | 🟢 | — | — | Complete |
| DOC-002 | AI Rules | 🟢 | — | — | Complete |
| DOC-003 | SRS | 🟢 | — | — | Complete |
| DOC-004 | Architecture | 🟢 | — | — | Complete |
| DATA-001 | Market Data Provider Selection | 🟢 | 🟢 | 🟢 | Complete; Groww selected and approved |
| DATA-002 | Groww Market Data Adapter | 🟢 | 🟢 | 🟢 | Complete; read-only adapter + normalization tests |
| DATA-003 | Instrument Master / Mapping | 🟢 | 🟢 | 🟢 | Complete; CI green |
| DATA-004 | Data Validation / Staleness | 🟢 | 🟢 | 🟢 | Complete; CI green |
| DATA-005 | Historical Candle Ingestion | 🟢 | 🟢 | 🟢 | Complete; CI green |
| DATA-006 | PostgreSQL Market-Data Persistence | 🟢 | 🟢 | 🟢 | Complete; CI green |
| DATA-007 | Data Quality Monitoring | 🟢 | 🟢 | 🟢 | Complete; CI green |
| DATA-008 | Real-Time LTP Feed Normalization | 🟢 | 🟢 | 🟢 | Complete; CI green |
| DATA-009 | Real-Time LTP Integration | 🟢 | 🟢 | 🟢 | Complete; CI green |
| DATA-010 | Real-Time LTP Read Path | 🟢 | 🟢 | 🟢 | Complete; CI green |
| DATA-011 | Scanner-Ready Market-Data Consumer | 🟢 | 🟢 | 🟢 | Complete; CI green |
| DATA-012 | Scanner Universe / Market-Data Window | 🟢 | 🟢 | 🟢 | Complete; CI green |
| DATA-013 | Scanner Feature Snapshot | 🟢 | 🟢 | 🟢 | Complete; CI green |
| DATA-014 | Scanner Feature Quality Gate | 🟢 | 🟢 | 🟢 | Complete; CI green after fixture correction |
| DATA-015 | Scanner Candidate Ranking | 🟢 | 🟢 | 🟢 | Complete; CI green |
| DATA-016 | Scanner Candidate Shortlist | 🟢 | 🟢 | 🟢 | Complete; CI green |
| SIG-001 | Signal Engine | 🟢 | 🟢 | 🟢 | Complete; momentum + reversal + breakout; CI green |
| AI-001 | AI Analyst | 🟢 | 🟢 | 🟢 | Complete; provider-independent structured contract |
| AI-002 | AI Context Builder | 🟢 | 🟢 | 🟢 | Complete; deterministic signal-to-analysis adapter |
| AI-003 | AI Analysis Orchestration | 🟢 | 🟢 | 🟢 | Complete; deterministic orchestration boundary, CI green |
| AI-004 | AI Prompt Construction | 🟢 | 🟢 | 🟢 | Complete; deterministic prompt artifact + revalidation, CI green |
| AI-005 | AI Model Adapter | 🟢 | 🟢 | 🟢 | Complete; provider-independent adapter boundary, CI green |
| AI-006 | AI Response Parsing | 🟢 | 🟢 | 🟢 | Complete; deterministic response parsing boundary, CI green |
| AI-007 | AI Analysis Integrity Gate | 🟢 | 🟢 | 🟢 | Complete; deterministic internal-consistency gate, CI green |
| RISK-001 | Risk Engine | 🟢 | 🟢 | 🟢 | Complete; deterministic risk budget and quantity gate, CI green |
| PLAN-001 | Trade Planner | 🟢 | 🟢 | 🟢 | Complete; deterministic broker-independent plan with explicit instrument and client-order identity, CI green |
| RISK-002 | Portfolio Risk Gate | 🟢 | 🟢 | 🟢 | Complete; deterministic exposure, concentration, and open-position gate, CI green |
| EXEC-001 | Groww Broker Adapter | 🟢 | 🟢 | 🟢 | Complete; safe provider boundary with submission disabled by default, CI green |
| EXEC-002 | Static-IP Production Runtime | 🟢 | 🟢 | 🟢 | Complete; deterministic production-runtime readiness gate, CI green |
| EXEC-003 | Controlled Deployment Authorization | 🟢 | 🟢 | 🟢 | Complete; deterministic deployment-evidence gate, CI green |
| PAPER-001 | Paper Execution Boundary | 🟢 | 🟢 | 🟢 | Complete; identity-bearing deterministic paper fills, CI green |
| PAPER-002 | Paper Order Ledger | 🟢 | 🟢 | 🟢 | Complete; deterministic in-process order history and duplicate protection, CI green |
| PAPER-003 | Paper Order Reconciliation | 🟢 | 🟢 | 🟢 | Complete; deterministic read-only ledger reconciliation, CI green |
| PAPER-004 | Paper Execution Session | 🟢 | 🟢 | 🟢 | Complete; deterministic execution → ledger → reconciliation orchestration, CI green |
| PAPER-005 | Paper Position Accounting | 🟢 | 🟢 | 🟢 | Complete; deterministic long-only position state, weighted-average pricing, realized P&L, and green CI |
| PAPER-006 | Paper Position Valuation | 🟢 | 🟢 | 🟢 | Complete; deterministic mark-to-market value, unrealized P&L, total P&L, and green CI |
| PAPER-007 | Paper Portfolio Valuation | 🟢 | 🟢 | 🟢 | Complete; aggregate immutable-position valuation; CI green on `main` commit `c4f9367` |
| PAPER-008 | Persistent Paper Order Journal | 🟢 | 🟢 | 🟢 | Complete; append-only PostgreSQL journal, idempotent replay, and deterministic history; CI green on `main` commit `2a66f4a` |
| TEST-001 | Historical Signal Backtesting | 🟢 | 🟢 | 🟢 | Complete; deterministic one-instrument candle replay for existing SIG-001 strategies; CI green on `main` commit `472d5a0` ([run](https://github.com/Nayan1209/AI-Trading/actions/runs/37269308234)) |
| UI-001 | Dashboard | 🟢 | 🟡 | 🟡 | Local read-only command center reads in-memory paper state plus optional PostgreSQL history and Groww account snapshots; signals, AI, risk, and authentication remain |

## Phase Status

- **Phase 0 — Foundation:** 🟢 Complete
- **Phase 1 — Market Data Engine:** 🟢 Complete through DATA-016
- **Phase 2 — Instrument Master & Data Storage:** 🟢 Complete through DATA-016
- **Phase 3 — Scanner & Signal Engine:** 🟢 Complete
- **Phase 4 — AI Analysis Engine:** 🟢 Complete through AI-007
- **Phase 5 — Trade Planner, Risk & Execution Controls:** 🟢 Complete through EXEC-003
- **Phase 6 — Paper Execution:** 🟢 PAPER-001 through PAPER-008 complete
- **Phase 7 — Backtesting:** 🟢 TEST-001 deterministic signal replay complete

## Previous milestone: PAPER-008 — Persistent Paper Order Journal

PAPER-008 adds durable, append-only PostgreSQL storage for completed immutable paper fills. The identity fields carried by `TradePlan` and `PaperOrder` provide stable lookup and duplicate-detection keys for this journal.

### Files added

- [`brain/51_PAPER_ORDER_PERSISTENCE_SPECIFICATION.md`](51_PAPER_ORDER_PERSISTENCE_SPECIFICATION.md)
- `src/storage/postgres_paper_orders.py`
- `database/migrations/003_paper_orders.sql`
- `tests/test_postgres_paper_order_journal.py`

### Safety

PAPER-008 does not call Groww, access credentials, submit orders, or enable live execution. It persists paper fills only; position snapshots and portfolio valuations remain in memory.

### Completion rule

PAPER-008 is complete: implementation, deterministic repository and migration tests, documentation, and automatic CI validation are green.

### CI evidence

The GitHub Actions run for `main` commit `2a66f4a` passed: [workflow run](https://github.com/Nayan1209/AI-Trading/actions/runs/37266152195).

All project development is performed directly on `main`. No pull request or separate development branch is required.

## Latest completed milestone: TEST-001 — Historical Signal Backtesting

TEST-001 replays one existing SIG-001 strategy over a validated, chronological OHLCV series. It uses only the trailing candle window to form each signal, enters at the next candle open, exits at the configured holding-bar close, and subtracts explicit per-side transaction costs. Tests use in-memory candle fixtures only.

The result reports individual gross/net trade returns and equal-notional summary statistics. It does not size positions, calculate a portfolio equity curve/drawdown, authorize risk, or execute trades. See [`52_BACKTESTING_SPECIFICATION.md`](52_BACKTESTING_SPECIFICATION.md).

### Safety

Backtesting does not call AI, a database, Groww, paper execution, or any network service. Simulated signals and returns are research outputs, not execution or risk approval.

### Completion rule

TEST-001 is complete after deterministic tests, the specification, the `main` push, and successful automatic CI.

### CI evidence

The GitHub Actions run for `main` commit `472d5a0` passed: [workflow run](https://github.com/Nayan1209/AI-Trading/actions/runs/37269308234).

## Completion Rule

A feature is complete only after implementation, deterministic tests, documentation, and operational checks. CI is the final verification gate.

## User Action Required

No Groww secret, access token, broker credential, model API key, or PostgreSQL service is required for TEST-001. Do not commit credentials. For UI-001, the ignored local `.env` file must receive a valid `DATABASE_URL` and `GROWW_ACCESS_TOKEN` before those optional account sources return live data.

## UI-001 — Dashboard Initial Delivery

The read-only dashboard is served at `/`. It shows application health, the latest mock candle, local in-memory paper state, optional PostgreSQL paper history, and optional Groww holdings/positions/current-day orders. The account snapshot APIs are limited to development mode and loopback clients. It exposes no trading actions and is not production-ready because login/MFA and role authorization are not implemented.

UI-001 remains in progress. Signal, AI, and risk read APIs are not connected. PostgreSQL and Groww remain inactive until `DATABASE_URL` with migration 003 and `GROWW_ACCESS_TOKEN` are configured locally. Unrealized paper P&L is not calculated without current price marks.

### CI evidence

The initial dashboard delivery passed GitHub Actions: [workflow run](https://github.com/Nayan1209/AI-Trading/actions/runs/37273027633). The current source integration passes 17 focused API, paper projection, Groww adapter, and accessibility checks locally; the embedded dashboard JavaScript also passes a syntax check. The full suite and CI for this update remain pending. The user supplied a screenshot confirming the initial dashboard loaded; automated inspection of localhost remains blocked by the in-app browser URL policy.
