# AI Trading System

> Autonomous AI trading platform — Indian equities first, multi-market architecture from day one.

## Current Status

**Phase 0 — Foundation: COMPLETE**  
**Phase 1 — Market Data Engine: 🟡 In Progress**

### Foundation completed

- [x] GitHub repository initialized
- [x] `brain/` specification layer created
- [x] Master project specification
- [x] AI development rules
- [x] SRS
- [x] Integration PRD
- [x] System architecture
- [x] API specification
- [x] Database specification
- [x] Integration specification
- [x] Security & privacy specification
- [x] UI/UX specification
- [x] Design system
- [x] User flows
- [x] Build-status tracker
- [x] Testing/QA strategy
- [x] AI model & prompt specification
- [x] Trading & risk rulebook
- [x] Deployment/operations runbook
- [x] Document control
- [x] Initial application skeleton
- [x] Market-data domain model
- [x] Mock market-data provider
- [x] Initial API and unit test
- [x] Development PostgreSQL container definition

### Phase 1 progress

- [x] Initial Indian provider selected: **Groww Trading API**
- [x] Groww API approval confirmed by project owner
- [x] Groww authentication lifecycle documented
- [x] Groww market-data capabilities documented
- [x] Groww broker/order capabilities documented
- [x] Groww rate limits documented
- [x] Static-IP production requirement documented
- [x] Groww Python SDK dependency added
- [x] Read-only Groww market-data adapter skeleton
- [x] Mock/fixture test for Groww response normalization
- [x] GitHub Actions test workflow
- [x] CI import-path configuration added (`pytest.ini`)
- [x] Instrument master model and lookup registry
- [x] Groww instrument CSV normalization
- [x] India-first CASH instrument filtering
- [x] Instrument mapping/validation tests
- [x] Instrument master specification (`brain/13_INSTRUMENT_MASTER_SPECIFICATION.md`)
- [x] Groww quantity validation updated to accept provider-supplied zero values
- [x] CASH and FNO instrument test fixtures aligned to the canonical CSV schema
- [x] DATA-003 CI validation — green
- [x] DATA-004 validation/staleness specification (`brain/14_DATA_VALIDATION_STALENESS_SPECIFICATION.md`)
- [x] Deterministic candle validation implementation
- [x] Deterministic staleness detection implementation
- [x] DATA-004 unit tests added
- [x] `MarketDataService` validation/staleness gate implemented
- [x] DATA-004 final CI validation — green
- [x] DATA-005 historical candle ingestion contract
- [x] Groww historical candle normalization
- [x] Historical candle service validation gate
- [x] Deterministic historical ingestion tests
- [x] DATA-005 final CI validation — green
- [x] DATA-006 PostgreSQL candle persistence contract
- [x] PostgreSQL candle schema migration
- [x] Validated candle repository with idempotent upsert
- [x] Historical candle range retrieval from PostgreSQL
- [x] Deterministic PostgreSQL repository tests without external services
- [x] DATA-006 automatic CI validation — green
- [x] DATA-007 deterministic data-quality monitoring implementation
- [x] DATA-007 tests for completeness, duplicates, gaps, invalid candles and persistence health
- [x] DATA-007 specification (`brain/17_DATA_QUALITY_MONITORING_SPECIFICATION.md`)
- [x] DATA-007 final automatic CI validation — green
- [x] DATA-008 real-time LTP feed normalization contract
- [x] DATA-008 deterministic LTP normalization and freshness tests
- [x] DATA-008 specification (`brain/18_REALTIME_LTP_FEED_SPECIFICATION.md`)
- [x] DATA-008 automatic CI validation — green
- [x] DATA-009 normalized LTP → instrument registry integration
- [x] DATA-009 fail-closed instrument and segment resolution
- [x] DATA-009 PostgreSQL LTP persistence boundary
- [x] DATA-009 deterministic integration and persistence tests
- [x] DATA-009 specification (`brain/19_REALTIME_LTP_INTEGRATION_SPECIFICATION.md`)
- [x] DATA-009 automatic CI validation — green
- [x] DATA-010 controlled real-time LTP read path
- [x] Latest LTP retrieval by canonical internal instrument ID
- [x] Bounded chronological LTP range retrieval
- [x] Timezone and invalid-range fail-closed checks
- [x] Deterministic DATA-010 repository read tests
- [x] DATA-010 specification (`brain/20_REALTIME_LTP_READ_PATH_SPECIFICATION.md`)
- [x] DATA-010 automatic CI validation — green
- [x] DATA-011 scanner-ready market-data consumer
- [x] DATA-011 deterministic scanner eligibility rules
- [x] DATA-011 scanner contract and tests (`brain/21_SCANNER_MARKET_DATA_SPECIFICATION.md`)
- [x] DATA-011 automatic CI validation — green
- [x] DATA-012 deterministic scanner universe construction
- [x] DATA-012 bounded market-data window contract
- [x] DATA-012 deterministic universe/window tests (`brain/22_SCANNER_UNIVERSE_WINDOW_SPECIFICATION.md`)
- [x] DATA-012 automatic CI validation — green
- [x] DATA-013 deterministic scanner feature snapshot
- [x] DATA-013 bounded LTP-history feature extraction
- [x] DATA-013 deterministic feature tests (`brain/23_SCANNER_FEATURE_SNAPSHOT_SPECIFICATION.md`)
- [x] DATA-013 automatic CI validation — green
- [x] DATA-014 deterministic scanner feature quality gate
- [x] DATA-014 fail-closed feature consistency validation
- [x] DATA-014 deterministic quality-gate tests (`brain/24_SCANNER_FEATURE_QUALITY_GATE_SPECIFICATION.md`)
- [x] DATA-014 automatic CI validation — green
- [x] DATA-015 deterministic scanner candidate ranking
- [x] DATA-015 ranking consumes only DATA-014-approved snapshots
- [x] DATA-015 deterministic ordering and tie-break tests (`brain/25_SCANNER_CANDIDATE_RANKING_SPECIFICATION.md`)
- [x] DATA-015 automatic CI validation — green
- [x] DATA-016 deterministic scanner candidate shortlist
- [x] DATA-016 bounded top-N selection from DATA-015-ranked candidates
- [x] DATA-016 fail-closed shortlist validation and deterministic tests (`brain/26_SCANNER_CANDIDATE_SHORTLIST_SPECIFICATION.md`)
- [x] DATA-016 automatic CI validation — green
- [x] SIG-001 deterministic signal-engine foundation
- [x] SIG-001 DATA-016 shortlist input boundary and deterministic orchestration
- [x] SIG-001 momentum strategy (`brain/28_MOMENTUM_SIGNAL_SPECIFICATION.md`)
- [x] SIG-001 momentum strategy wired into the signal engine
- [x] SIG-001 reversal strategy (`brain/29_REVERSAL_SIGNAL_SPECIFICATION.md`)
- [x] SIG-001 reversal strategy wired into the signal engine
- [x] SIG-001 breakout strategy (`brain/30_BREAKOUT_SIGNAL_SPECIFICATION.md`)
- [x] SIG-001 breakout strategy wired into the signal engine
- [x] SIG-001 deterministic engine, momentum, reversal and breakout tests
- [ ] SIG-001 automatic CI validation — pending for the breakout implementation commit

## Safety Boundary

This repository currently has **no live broker connection, live order execution, withdrawal capability, or real-money trading functionality**.

The AI is never allowed to bypass deterministic risk and execution controls.

Groww credentials, access tokens, secrets and TOTP values are never stored in GitHub.

## Architecture Direction

```text
Market Data
    ↓
Instrument Master
    ↓
Normalization / Validation
    ↓
PostgreSQL Persistence
    ↓
Data Quality Monitoring
    ↓
Scanner
    ↓
Signal Engine
    ↓
AI Analysis
    ↓
Trade Planner
    ↓
Risk Engine  ← mandatory safety gate
    ↓
Execution Engine
    ↓
Broker Adapter (Groww first)
    ↓
Reconciliation / Monitoring
    ↓
Trade Journal / Analytics
```

## Initial Provider: Groww

Groww is the first broker/market-data integration for the India-first phase. Current official documentation provides live quote/LTP/OHLC APIs, streaming data, historical candles, instrument data, portfolio/position APIs and order lifecycle APIs. The integration is deliberately isolated behind an adapter so future providers can be added without changing strategy logic.

The first adapter milestone is deliberately **read-only**. The current implementation converts Groww `get_quote` data into the project's internal market-data model. Groww's current-day OHLC snapshot is explicitly labelled `1d_snapshot`; it is not treated as an interval candle. Historical interval candles use the separate historical-data adapter path.

Groww's instrument master is normalized into an internal `Instrument` model and `InstrumentMaster` registry. The registry supports lookup by internal ID, Groww symbol, exchange/trading symbol and exchange token. The first India-first operational scope is CASH/equity; derivative-specific fields are retained in the model so F&O can be added without redesigning the identity layer.

Groww's historical-candle API returns OHLCV rows and, for FNO, optional open interest. The current internal `Candle` model intentionally stores the common OHLCV fields; open interest will be added when the derivative data model requires it. Historical timestamps without an explicit timezone are normalized as India Standard Time before entering the deterministic validation gate.

Groww currently documents request-duration/history limits by candle interval. These provider constraints are treated as ingestion configuration and must be re-verified before production backfill jobs are designed.

## PostgreSQL Market-Data Persistence

Validated internal `Candle` objects now have a dedicated persistence boundary. `PostgresCandleRepository` stores candles in a PostgreSQL `candles` table using `TIMESTAMPTZ`, fixed-precision `NUMERIC` OHLC values and `BIGINT` volume. Candle identity is unique across symbol, exchange, timeframe and timestamp, making repeated historical ingestion idempotent.

The persistence layer validates every candle before writing and never accepts raw Groww payloads. CI uses deterministic fake database connections, so no production database or Groww credential is required for repository tests.

The SQL schema is versioned under `database/migrations/001_candles.sql`.

## Data Quality Monitoring

DATA-007 adds a provider-independent deterministic quality boundary around normalized candles. `assess_candles()` reuses the existing validation rules and reports invalid candles, duplicate identities, caller-defined missing timestamps and completeness ratio. The monitor deliberately does not invent a market calendar, so overnight, weekend and exchange-holiday gaps are not falsely classified as missing data.

`assess_persistence_health()` provides a small persistence-independent health contract. Both quality reporting and persistence-health checks are deterministic and require no Groww credentials or production database in CI.

The specification is versioned under `brain/17_DATA_QUALITY_MONITORING_SPECIFICATION.md`.

## Real-Time LTP Feed

DATA-008 adds the first controlled real-time market-data boundary. Groww LTP feed payloads are normalized into immutable provider-independent `LtpEvent` objects with exchange, segment, exchange token, UTC timestamp and `Decimal` LTP. The boundary rejects malformed events and provides a deterministic freshness gate for future-dated or stale events.

DATA-009 connects those normalized events to the canonical `InstrumentMaster`. `RealtimeLtpService` resolves each event by exchange/token, rejects unknown instruments and segment mismatches, reuses the freshness gate, and persists only resolved events through `PostgresLtpRepository`.

Real-time events are stored in the PostgreSQL `ltp_events` table with an idempotent `(internal_id, timestamp)` identity. The migration is versioned under `database/migrations/002_ltp_events.sql`.

DATA-010 exposes a controlled read path through `PostgresLtpRepository`. Consumers retrieve the latest event or a bounded chronological range by canonical `internal_id`, receiving provider-independent `ResolvedLtp` objects rather than database rows or Groww SDK objects. Read ranges require timezone-aware timestamps and invalid ranges fail closed.

DATA-011 adds the first scanner-ready consumer on top of that read boundary. `ScannerMarketDataService` accepts canonical instrument IDs, retrieves only the latest persisted `ResolvedLtp`, and returns deterministic `ScannerCandidate` values only for fresh, non-future, positive-LTP CASH instruments. Missing or stale data is excluded rather than invented.

DATA-012 adds the deterministic scanner input envelope on top of DATA-011. `ScannerUniverse` enforces a non-empty, duplicate-free, CASH-only canonical instrument set in stable order. `MarketDataWindow` defines an explicit timezone-aware inclusive window from `reference_time - max_age` through `reference_time`. `ScannerUniverseService` composes these boundaries without generating signals or making execution decisions.

DATA-013 adds descriptive scanner features on top of DATA-010 and DATA-012. `ScannerFeatureService` reads bounded persisted LTP history and produces deterministic `ScannerFeatureSnapshot` values for sample count, first/latest price, high/low and percentage change. It uses Decimal arithmetic and excludes missing, future, out-of-window, non-CASH and non-positive observations. It remains descriptive only and does not rank or generate signals.

DATA-014 adds a fail-closed quality gate on DATA-013 snapshots. `ScannerFeatureQualityGate` validates feature identity, uniqueness, minimum sample count, positive prices, high/low consistency and exact Decimal percentage-change arithmetic, then returns deterministic lexical ordering for downstream scanner consumers. It does not rank instruments or generate signals.

DATA-015 adds deterministic scanner candidate ranking after the DATA-014 quality boundary. `ScannerRankingService` ranks validated snapshots by descriptive percentage change descending, then sample count descending, then canonical internal ID ascending. The result is one-based and deterministic; it introduces no predictive score or trading signal.

DATA-016 adds a deterministic scanner candidate shortlist after DATA-015. `ScannerCandidateShortlistService` accepts only DATA-015-ranked candidates, validates their contiguous one-based ranks and unique canonical identities, and returns a caller-defined positive top-N prefix without reordering or inventing candidates. It remains scanner infrastructure only and does not generate trading signals.

## Signal Engine

SIG-001 adds the deterministic signal-engine boundary after the DATA-016 scanner shortlist. The engine accepts only DATA-016-ranked candidates, preserves candidate identity and rank, validates strategy output, and evaluates configured strategies in stable order. It does not call AI, create trade plans, bypass risk controls, connect to Groww, or execute trades.

The first concrete strategy is deterministic momentum. `MomentumSignalStrategy` uses the DATA-013 percentage-change feature carried through the DATA-014 quality gate, DATA-015 ranking and DATA-016 shortlist. A change above the strict positive threshold produces a LONG observation, a change below the negative threshold produces a SHORT observation, and changes inside the threshold produce no signal. The strategy score is the absolute change capped at 100.

The second concrete strategy is deterministic reversal. `ReversalSignalStrategy` uses the same validated percentage-change feature as a deliberately contrasting mean-reversion observation: a change above the strict positive threshold produces a SHORT observation, a change below the negative threshold produces a LONG observation, and changes inside the threshold produce no signal. Its default threshold is 2%, and its score is the absolute change capped at 100.

The third concrete strategy is deterministic breakout. `BreakoutSignalStrategy` requires the percentage-change threshold to be crossed and the latest LTP to be exactly at the corresponding observed high or low. Positive threshold-crossing changes at the high produce LONG observations; negative threshold-crossing changes at the low produce SHORT observations. Its default threshold is 1%, and its score is the absolute change capped at 100.

The strategy rules are versioned under `brain/28_MOMENTUM_SIGNAL_SPECIFICATION.md`, `brain/29_REVERSAL_SIGNAL_SPECIFICATION.md` and `brain/30_BREAKOUT_SIGNAL_SPECIFICATION.md`, while the signal-engine contract is versioned under `brain/27_SIGNAL_ENGINE_SPECIFICATION.md`.

The implementation does not open a live Groww connection and requires no credentials in CI. Groww-specific feed nesting remains isolated at the normalization boundary.

## Development Phases

| Phase | Name | Status |
|---|---|---|
| 0 | Foundation & specifications | 🟢 Complete |
| 1 | Market Data Engine | 🟡 In Progress |
| 2 | Instrument Master & Data Storage | 🟢 Instrument identity, persistence and data-quality monitoring complete |
| 3 | Scanner & Signal Engine | 🟡 Signal engine with momentum + reversal + breakout strategies implemented; CI pending |
| 4 | AI Analysis Engine | ⚪ Planned |
| 5 | Trade Planner & Risk Engine | ⚪ Planned |
| 6 | Paper Execution | ⚪ Planned |
| 7 | Backtesting | ⚪ Planned |
| 8 | Broker Integration | 🟡 Groww selected; implementation gated |
| 9 | Dashboard & Operations | ⚪ Planned |
| 10 | Controlled Live Deployment | ⚪ Planned |

## CI / Change Discipline

CI runs **automatically on every push to `main`** and can also be started with `workflow_dispatch`. There is no pull-request requirement for this project.

Development work is performed directly on `main`; pull requests and development branches are not part of the normal workflow.
