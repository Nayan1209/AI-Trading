# Build Status / Development Tracker
**Version:** 0.8

| ID | Workstream | Design | Build | Test | Status |
|---|---|---:|---:|---:|---|
| DOC-001 | Master Project | 🟢 | — | — | Complete |
| DOC-002 | AI Rules | 🟢 | — | — | Complete |
| DOC-003 | SRS | 🟢 | — | — | Complete |
| DOC-004 | Architecture | 🟢 | — | — | Complete |
| DATA-001 | Market Data Provider Selection | 🟢 | 🟢 | 🟢 | Groww selected and approved |
| DATA-002 | Groww Market Data Adapter | 🟢 | 🟢 | 🟢 | Read-only adapter skeleton + normalization test complete |
| DATA-003 | Instrument Master / Mapping | 🟢 | 🟢 | 🟢 | Complete; CI green after CASH/FNO fixture alignment |
| DATA-004 | Data Validation / Staleness | 🟢 | 🟢 | 🟡 | Validator, staleness detection and MarketDataService gate implemented; final CI validation pending |
| DATA-005 | Historical Candle Ingestion | 🟡 | ⚪ | ⚪ | Planned — blocked until DATA-004 CI is green |
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
- GitHub Actions CI configured for controlled execution rather than every push to `main`.
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
- `MarketDataService.latest()` now applies `validate_candle()` as a mandatory fail-closed quality gate and rejects stale candles.

## Immediate Next Step
**DATA-004 CI gate:** the implementation and documentation are now aligned for the final verification. Run the existing GitHub Actions workflow manually from the repository's **Actions** tab only after this complete change set is present on `main`. Do not create a pull request or another development branch.

If CI is green, mark DATA-004 complete and advance to DATA-005 Historical Candle Ingestion. If CI fails, fix the failure on `main` before adding any new functionality.

## User Action Required
No Groww secret or access token is required for DATA-004. Do **not** commit credentials. The validation tests are deterministic and do not call Groww.

The user does not need to create branches or pull requests. All project development is performed directly on `main`.

## Completion Rule
A feature is complete only after implementation, tests, documentation, and operational checks. The README and this tracker must be updated immediately after each milestone. CI is a verification gate and is run only when the complete change set is expected to pass.
