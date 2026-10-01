# Build Status / Development Tracker
**Version:** 0.2

| ID | Workstream | Design | Build | Test | Status |
|---|---|---:|---:|---:|---|
| DOC-001 | Master Project | 🟢 | — | — | Complete |
| DOC-002 | AI Rules | 🟢 | — | — | Complete |
| DOC-003 | SRS | 🟢 | — | — | Complete |
| DOC-004 | Architecture | 🟢 | — | — | Complete |
| DATA-001 | Market Data Provider Selection | 🟢 | ⚪ | ⚪ | Groww selected; adapter next |
| DATA-002 | Groww Market Data Adapter | 🟢 | ⚪ | ⚪ | Not Started |
| DATA-003 | Instrument Master / Mapping | 🟡 | ⚪ | ⚪ | Planned after adapter skeleton |
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
- Groww rate limits, live-feed subscription boundary and token lifecycle documented from current official provider documentation.
- Static-IP requirement recorded as a production execution prerequisite.
- Safety boundary preserved: no live order has been enabled or placed by this project.

## Immediate Next Step
Build the **Groww adapter skeleton and provider-agnostic interfaces** with mock/fixture tests. The first implementation milestone must be read-only market-data connectivity and normalization; it must not place live orders.

## Completion Rule
A feature is complete only after implementation, tests, documentation, and operational checks. The README and this tracker must be updated immediately after each milestone.
