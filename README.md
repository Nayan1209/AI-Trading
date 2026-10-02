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
- [ ] DATA-007 final automatic CI validation

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

## Development Phases

| Phase | Name | Status |
|---|---|---|
| 0 | Foundation & specifications | 🟢 Complete |
| 1 | Market Data Engine | 🟡 In Progress |
| 2 | Instrument Master & Data Storage | 🟡 Persistence + data-quality monitoring implemented; DATA-007 CI gate pending |
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

### DATA-007 → final controlled CI validation

DATA-006 is complete: PostgreSQL persistence is implemented and its automatic CI validation is green.

DATA-007 is now implemented as a deterministic data-quality monitoring boundary. It checks candle validity, duplicates, caller-defined completeness/gaps and persistence health without requiring live services.

**Next action: push this complete DATA-007 change set to `main` and let the automatic GitHub Actions workflow verify it. Do not create a pull request or another branch.**

If CI is green, mark DATA-007 complete and proceed to the next market-data integration milestone before scanner/signal work. If CI fails, fix the failure on `main` before adding new functionality.

### What you need to do now

You do **not** need to provide the Groww API key for DATA-007 unit tests. Do not commit credentials, access tokens, secrets or TOTP values.

The project is being developed directly on `main`. No new branch or pull request is required.

**Rule:** We do not move to the Scanner phase until the market-data foundation passes its deterministic quality gates and the corresponding documentation is updated.

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
