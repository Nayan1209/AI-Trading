# Build Status / Development Tracker
**Version:** 3.3

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
| PLAN-001 | Trade Planner | 🟢 | 🟢 | 🟢 | Complete; deterministic broker-independent trade plan, CI green |
| RISK-002 | Portfolio Risk Gate | 🟢 | 🟢 | 🟢 | Complete; deterministic exposure, concentration, and open-position gate, CI green |
| EXEC-001 | Groww Broker Adapter | 🟢 | ⚪ | ⚪ | Design complete; implementation later |
| EXEC-002 | Static-IP Production Runtime | 🟡 | ⚪ | ⚪ | Required before live orders |
| UI-001 | Dashboard | ⚪ | ⚪ | ⚪ | Not Started |
| TEST-001 | Backtesting | ⚪ | ⚪ | ⚪ | Not Started |

## Current milestone: EXEC-001

RISK-002 is complete. The deterministic portfolio-level safety gate now sits after RISK-001 and PLAN-001 and evaluates projected gross notional exposure, single-symbol concentration, and maximum open-position count using explicit caller-supplied limits.

### RISK-002 completion

- `brain/40_RISK_PORTFOLIO_EXPOSURE_SPECIFICATION.md`
- `src/portfolio_risk.py`
- `tests/test_portfolio_risk.py`
- Implementation, deterministic tests, documentation, and automatic CI are green.

### Next milestone: EXEC-001

EXEC-001 is the Groww broker adapter boundary. It should remain isolated from strategy, AI, and risk logic. It must not bypass RISK-001, PLAN-001, or RISK-002, and it must not place live orders until the required execution safety and production-runtime controls are satisfied.

## Safety

RISK-002 uses conservative gross exposure semantics and never assumes positions will net. Missing, malformed, duplicate, or unsafe inputs are rejected. It does not call a broker, access credentials, or execute orders.

All project development is performed directly on `main`. No pull request or separate development branch is required.

## Completion Rule

A feature is complete only after implementation, deterministic tests, documentation, and operational checks. CI is the final verification gate and should receive only one coherent, preflight-reviewed commit for each milestone.

## User Action Required

No Groww secret, access token, broker credential, or model API key is required for the completed RISK-002 milestone. Do not commit credentials.
