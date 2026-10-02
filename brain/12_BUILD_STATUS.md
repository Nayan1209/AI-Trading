# Build Status / Development Tracker
**Version:** 3.0

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
| AI-002 | AI Context Builder | 🟢 | 🟢 | 🟢 | Complete; deterministic signal-to-context adapter |
| AI-003 | AI Analysis Orchestration | 🟢 | 🟢 | 🟢 | Complete; deterministic orchestration boundary, CI green |
| AI-004 | AI Prompt Construction | 🟢 | 🟢 | 🟢 | Complete; deterministic prompt artifact + revalidation, CI green |
| AI-005 | AI Model Adapter | 🟢 | 🟢 | 🟢 | In progress; provider-independent adapter boundary |
| RISK-001 | Risk Engine | ⚪ | ⚪ | ⚪ | Not Started |
| EXEC-001 | Groww Broker Adapter | 🟢 | ⚪ | ⚪ | Design complete; implementation later |
| EXEC-002 | Static-IP Production Runtime | 🟡 | ⚪ | ⚪ | Required before live orders |
| UI-001 | Dashboard | ⚪ | ⚪ | ⚪ | Not Started |
| TEST-001 | Backtesting | ⚪ | ⚪ | ⚪ | Not Started |

## Current milestone: AI-005

AI-005 introduces a provider-independent model-adapter boundary after deterministic prompt construction. The core contract accepts only the immutable `AIPrompt` artifact and returns opaque `AIModelResponse` text with explicit model and prompt versions. No provider SDK, network call, credentials, trading interpretation, risk override, broker access, or execution is introduced.

### Files added

- `brain/35_AI_MODEL_ADAPTER_SPECIFICATION.md`
- `src/ai_model.py`
- `tests/test_ai_model.py`

### Safety

The model response is untrusted text. AI-005 does not interpret it as a trade decision and does not execute orders. Provider-specific network and credential handling remain outside the core contract.

## Immediate Next Step

Run the automatic GitHub Actions CI for the complete AI-005 change set. If green, mark AI-005 complete and define the next AI-analysis boundary before implementing further functionality.

## User Action Required

No Groww secret, access token, broker credential, or model API key is required for AI-005. Do not commit credentials.

All project development is performed directly on `main`. No pull request or separate development branch is required.

## Completion Rule

A feature is complete only after implementation, deterministic tests, documentation, and operational checks. CI is the final verification gate and should receive only one coherent, preflight-reviewed commit for each milestone.
