# Build Status / Development Tracker
**Version:** 1.6

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
| DATA-005 | Historical Candle Ingestion | 🟢 | 🟢 | 🟢 | Complete; automatic CI green |
| DATA-006 | PostgreSQL Market-Data Persistence | 🟢 | 🟢 | 🟢 | Complete; automatic CI green |
| DATA-007 | Data Quality Monitoring | 🟢 | 🟢 | 🟢 | Complete; automatic CI green |
| DATA-008 | Real-Time LTP Feed Normalization | 🟢 | 🟢 | 🟢 | Complete; automatic CI green |
| DATA-009 | Real-Time LTP Integration | 🟢 | 🟢 | 🟢 | Complete; automatic CI green |
| DATA-010 | Real-Time LTP Read Path | 🟢 | 🟢 | 🟢 | Complete; controlled latest/range reads with deterministic CI coverage |
| DATA-011 | Scanner-Ready Market-Data Consumer | 🟢 | 🟢 | 🟢 | Complete; automatic CI green |
| DATA-012 | Scanner Universe / Market-Data Window | 🟢 | 🟢 | 🟡 | Implementation complete; automatic CI validation pending |
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
- DATA-005 automatic CI validation passed.
- DATA-006 PostgreSQL persistence specification added under `brain/16_POSTGRES_MARKET_DATA_PERSISTENCE_SPECIFICATION.md`.
- PostgreSQL `candles` schema migration added with fixed-precision OHLC values, non-negative volume, `TIMESTAMPTZ`, uniqueness and lookup indexing.
- `CandleRepository` persistence boundary added so storage is independent of provider implementations.
- `PostgresCandleRepository` added with validated idempotent upsert and chronological range retrieval.
- PostgreSQL driver dependency added without storing database credentials.
- Deterministic repository tests added with fake database connections; no live database is required by CI.
- DATA-006 automatic CI validation passed.
- DATA-007 specification added under `brain/17_DATA_QUALITY_MONITORING_SPECIFICATION.md`.
- Deterministic quality report added for candle validity, duplicates, caller-defined completeness and gaps.
- Persistence health check boundary added without coupling monitoring to PostgreSQL implementation.
- DATA-007 tests added using deterministic in-memory fixtures only.
- DATA-007 automatic CI validation passed.
- DATA-008 specification added under `brain/18_REALTIME_LTP_FEED_SPECIFICATION.md`.
- Provider-independent `LtpEvent` model added for Groww real-time LTP data.
- Groww nested LTP payload normalization added for multi-instrument feed responses.
- Deterministic LTP validation rejects empty identity, missing fields and non-positive prices.
- Deterministic freshness gate rejects future-dated and stale LTP events.
- DATA-009 specification added under `brain/19_REALTIME_LTP_INTEGRATION_SPECIFICATION.md`.
- `RealtimeLtpService` resolves normalized LTP events through `InstrumentMaster` by exchange/token.
- Segment mismatches and unknown instruments fail closed before persistence.
- `PostgresLtpRepository` added as the provider-independent persistence boundary for resolved real-time LTP events.
- `ltp_events` PostgreSQL migration added with positive-LTP validation, UTC-capable timestamps and idempotent event identity.
- Deterministic integration and PostgreSQL persistence tests added without live Groww or production PostgreSQL services.
- DATA-009 automatic CI validation completed successfully on `main`.
- DATA-010 controlled read path added to `PostgresLtpRepository` for latest and bounded time-range LTP retrieval by canonical internal instrument ID.
- DATA-010 read results return provider-independent `ResolvedLtp` values; raw database rows are not exposed downstream.
- DATA-010 deterministic tests cover latest reads, chronological range reads, empty reads, invalid time ranges and naive persisted timestamps.
- DATA-010 specification added under `brain/20_REALTIME_LTP_READ_PATH_SPECIFICATION.md`.
- DATA-010 automatic CI validation completed successfully.
- DATA-011 specification added under `brain/21_SCANNER_MARKET_DATA_SPECIFICATION.md`.
- `ScannerMarketDataService` consumes only the DATA-010 `get_latest_ltp()` read contract.
- DATA-011 scanner eligibility is deterministic: canonical identity match, CASH segment, positive LTP, timezone-aware non-future timestamp and caller-defined freshness.
- Missing and stale market data is excluded rather than invented.
- DATA-011 deterministic tests added using an in-memory fake reader; no Groww credentials or PostgreSQL service required.
- DATA-011 automatic CI validation completed successfully.
- DATA-012 specification added under `brain/22_SCANNER_UNIVERSE_WINDOW_SPECIFICATION.md`.
- `ScannerUniverse` enforces non-empty, duplicate-free, CASH-only canonical internal IDs and deterministic ordering.
- `MarketDataWindow` enforces timezone-aware reference time and non-negative freshness with explicit inclusive bounds.
- `ScannerUniverseService` composes DATA-012 boundaries with `ScannerMarketDataService` without introducing signal or execution logic.
- DATA-012 deterministic tests added for universe validation, ordering, window boundaries and service integration.
- DATA-012 automatic CI validation is pending.

## Immediate Next Step
**DATA-012 automatic CI validation:** verify the complete scanner universe/window change set on `main` before advancing to the next scanner milestone.

## User Action Required
No Groww secret or access token is required for the deterministic market-data tests. **Do not commit credentials.**

The user does not need to create branches or pull requests. All project development is performed directly on `main`.

## Completion Rule
A feature is complete only after implementation, tests, documentation, and operational checks. The README and this tracker must be updated immediately after each milestone. CI is an automatic verification gate and should receive only coherent, preflight-reviewed commits.
