# Build Status / Development Tracker
**Version:** 0.3

| ID | Workstream | Design | Build | Test | Status |
|---|---|---:|---:|---:|---|
| DOC-001 | Master Project | 🟢 | — | — | Complete |
| DOC-002 | AI Rules | 🟢 | — | — | Complete |
| DOC-003 | SRS | 🟢 | — | — | Complete |
| DOC-004 | Architecture | 🟢 | — | — | Complete |
| DATA-001 | Market Data Provider Selection | 🟢 | 🟢 | 🟢 | Groww selected and approved |
| DATA-002 | Groww Market Data Adapter | 🟢 | 🟢 | 🟡 | Read-only skeleton implemented; CI test pending |
| DATA-003 | Instrument Master / Mapping | 🟡 | ⚪ | ⚪ | Next |
| DATA-004 | Data Validation / Staleness | 🟡 | ⚪ | ⚪ | Planned |
| DATA-005 | Historical Candle Ingestion | 🟡 | ⚪ | ⚪ | Planned |
| EXEC-001 | Groww Broker Adapter | 🟢 | ⚪ | ⚪ | Design complete; implementation later |
| EXEC-002 | Static-IP Production Runtime | 🟡 | ⚪ | ⚪ | Required before live orders |
| SIG-001 | Signal Engine | ⚪ | ⚪ | ⚪ | Not Started |
| AI-001 | AI Analyst | ⚪ | ⚪ | ⚪ | Not Started |
| RISK-001 | Risk Engine | ⚪ | ⚪ | ⚪ | Not Started |
| UI-001 | Dashboard | ⚪ | ⚪ | ⚪ | Not Started |
| TEST-001 | Backtesting | ⚪ | ⚪ | ⚪ | Not Started |

## Completed in this milestone
- Groww Trading API selected as the initial India-first broker/market-data provider.
- Groww API key approval confirmed by project owner; no credential value stored in GitHub.
- Groww adapter responsibilities and internal contracts documented.
- Groww Python SDK added as a project dependency.
- Read-only `GrowwMarketDataProvider` skeleton added.
- Groww quote normalization test added using a local fake client; the test does not call Groww.
- GitHub Actions CI added to run the Python test suite on pushes and pull requests.
- `.env.example` updated with a placeholder for the runtime Groww access token.
- Groww rate limits, live-feed subscription boundary and token lifecycle documented from current official provider documentation.
- Static-IP requirement recorded as a production execution prerequisite.
- Safety boundary preserved: no live order has been enabled or placed by this project.

## Immediate Next Step
**DATA-002 completion:** confirm the automated test workflow passes, then move to **DATA-003 Instrument Master / Mapping**. We need a reliable mapping between internal instruments and Groww's exchange/segment/trading-symbol/exchange-token identifiers before live streaming or strategy work.

## User Action Required
No Groww secret or access token is required for the current skeleton/test milestone. Do **not** commit credentials. When we reach real API connectivity, the token will be supplied through a secure runtime secret or GitHub Actions secret for testing—not in source files.

## Completion Rule
A feature is complete only after implementation, tests, documentation, and operational checks. The README and this tracker must be updated immediately after each milestone.
