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

The implementation does not open a live Groww connection and requires no credentials in CI. Groww-specific feed nesting remains isolated at the normalization boundary.

The specifications are versioned under `brain/18_REALTIME_LTP_FEED_SPECIFICATION.md`, `brain/19_REALTIME_LTP_INTEGRATION_SPECIFICATION.md` and `brain/20_REALTIME_LTP_READ_PATH_SPECIFICATION.md`.

## Development Phases

| Phase | Name | Status |
|---|---|---|
| 0 | Foundation & specifications | 🟢 Complete |
| 1 | Market Data Engine | 🟡 In Progress |
| 2 | Instrument Master & Data Storage | 🟢 Instrument identity, persistence and data-quality monitoring complete |
| 3 | Scanner & Signal Engine | ⚪ Planned |
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

Because CI is automatic, we do not intentionally push half-built changes. Development follows a **preflight → batch → push** rule:

```text
Plan change
   ↓
Implement complete change set on main
   ↓
Review imports / contracts / tests / fixtures
   ↓
Update documentation
   ↓
Push once
   ↓
Automatic CI
   ↓
If green → proceed
If red → fix on main before adding more functionality
```

We do not use CI as the development loop. It is the final verification gate for a coherent commit.

## Immediate Next Step

### DATA-011 → scanner-ready market-data consumer

DATA-009 and DATA-010 are complete and green. The persisted real-time LTP stream now has a controlled, provider-independent read boundary.

**Next action: define and implement the first scanner-ready market-data consumer using the DATA-010 read contract.** Scanner eligibility rules must be deterministic and must operate only on validated, instrument-resolved market data.

No signal-generation, AI decision, order, withdrawal or live execution functionality should be introduced in this step.

### What you need to do now

You do **not** need to provide the Groww API key for deterministic market-data tests. Do not commit credentials, access tokens, secrets or TOTP values.

The project is being developed directly on `main`. No new branch or pull request is required.

**Rule:** We do not move into trading decisions or execution until the market-data foundation and scanner inputs pass their deterministic quality gates and the corresponding documentation is updated.

## Repository Structure

```text
AI-Trading/
├── brain/                 # authoritative specifications and rules
├── database/              # versioned database migrations
├── src/                   # application code
├── tests/                 # automated tests
├── infrastructure/       # local/dev infrastructure
├── scripts/               # developer utilities
├── README.md              # live project status + next step
└── BUILD_STATUS.md        # implementation tracker
```

## Change Discipline

Every completed development step must update:

1. Code
2. Tests
3. `README.md` — current status + immediate next step
4. Relevant `brain/` specification
5. `brain/12_BUILD_STATUS.md`
6. Push the complete change set once so automatic CI verifies the commit

This keeps the repository self-documenting and prevents the implementation from drifting away from the architecture.
