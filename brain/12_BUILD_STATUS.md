# Build Status / Development Tracker
**Version:** 0.9

| ID | Workstream | Design | Build | Test | Status |
|---|---|---:|---:|---:|---|
| DOC-001 | Master Project | 🟢 | — | — | Complete |
| DOC-002 | AI Rules | 🟢 | — | — | Complete |
| DOC-003 | SRS | 🟢 | — | — | Complete |
| DOC-004 | Architecture | 🟢 | — | — | Complete |
| DATA-001 | Market Data Provider Selection | 🟢 | 🟢 | 🟢 | Groww selected and approved |
| DATA-002 | Groww Market Data Adapter | 🟢 | 🟢 | 🟢 | Read-only adapter skeleton + normalization test complete |
| DATA-003 | Instrument Master / Mapping | 🟢 | 🟢 | 🟢 | Complete; CI green after CASH/FNO fixture alignment |
| DATA-004 | Data Validation / Staleness | 🟢 | 🟢 | 🟢 | Complete; deterministic validation, staleness detection and service gate verified by CI |
| DATA-005 | Historical Candle Ingestion | 🟢 | 🟢 | 🟡 | Implementation complete; final automatic CI validation pending |
| DATA-006 | PostgreSQL Market-Data Persistence | 🟡 | ⚪ | ⚪ | Planned — starts after DATA-005 CI |
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
- GitHub Actions CI configured to run automatically on pushes to `main`.
- `.env.example` updated with a placeholder for the runtime Groww access token.
- Groww rate limits, live-feed subscription boundary and token lifecycle documented from current official provider documentation.
- Static-IP requirement recorded as a production execution prerequisite.
- Safety boundary preserved: no live order has been enabled or placed by this project.
- Instrument master model and lookup registry implemented without requiring live Groww credentials.
- Groww instrument CSV normalization and India-first CASH filtering implemented.
- Instrument lookup paths implemented for internal ID, Groww symbol, exchange/trading symbol and exchange token.
- Instrument validation tests added for mapping, filtering, duplicate detection and required fields.
- Instrument-master specification added under `brain/13_INSTRUMENT_MASTER_SPECIFICATION.md`.
- Groww CASH and FNO instrument fixture rows corrected and CI validated.
- Instrument model permits provider-supplied zero values for `lot_size` and `freeze_quantity`.
- DATA-004 validation/staleness specification added under `brain/14_DATA_VALIDATION_STALENESS_SPECIFICATION.md`.
- Deterministic candle validation added for identity, timezone, positive OHLC, OHLC relationships and non-negative volume.
- Deterministic staleness detection added using caller-supplied freshness thresholds.
- DATA-004 unit tests added without live Groww credentials.
- `MarketDataService.latest()` applies `validate_candle()` as a mandatory fail-closed quality gate and rejects stale candles.
- DATA-004 final CI validation passed.
- DATA-005 historical candle ingestion contract added under `brain/15_HISTORICAL_CANDLE_INGESTION_SPECIFICATION.md`.
- Groww `get_historical_candles()` response normalization implemented for OHLCV rows.
- Groww historical timestamps are normalized to timezone-aware India Standard Time when the provider response omits timezone information.
- `MarketDataService.historical()` validates every returned historical candle before downstream use.
- Historical ingestion tests use a fake Groww client and deterministic fixtures; no live credential is required.

## Immediate Next Step
**DATA-005 CI gate:** push the complete DATA-005 change set to `main`. The automatic GitHub Actions workflow will run once for that coherent commit.

If CI is green, mark DATA-005 complete and advance to **DATA-006 — PostgreSQL Market-Data Persistence**. If CI fails, fix the failure on `main` before adding any new functionality.

## User Action Required
No Groww secret or access token is required for DATA-005 unit tests. Do **not** commit credentials. The historical ingestion tests use a fake provider client and do not call Groww.

The user does not need to create branches or pull requests. All project development is performed directly on `main`.

## Completion Rule
A feature is complete only after implementation, tests, documentation, and operational checks. The README and this tracker must be updated immediately after each milestone. CI is an automatic verification gate and should receive only coherent, preflight-reviewed commits.
