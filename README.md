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
- [ ] DATA-004 final CI validation
- [ ] Historical candle ingestion
- [ ] PostgreSQL market-data persistence
- [ ] Data-quality monitoring

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

Groww is the first broker/market-data integration for the India-first phase. Current official documentation provides live quote/LTP/OHLC APIs, a streaming feed, historical candles, instrument data, portfolio/position APIs and order lifecycle APIs. The integration is deliberately isolated behind an adapter so future providers can be added without changing strategy logic.

The first adapter milestone is deliberately **read-only**. The current implementation converts Groww `get_quote` data into the project's internal market-data model. Groww's current-day OHLC snapshot is explicitly labelled `1d_snapshot`; it is not treated as an interval candle. Historical interval candles will use a separate adapter path.

Groww's instrument master is now normalized into an internal `Instrument` model and `InstrumentMaster` registry. The registry supports lookup by internal ID, Groww symbol, exchange/trading symbol and exchange token. The first India-first operational scope is CASH/equity; derivative-specific fields are retained in the model so F&O can be added without redesigning the identity layer.

Groww currently documents rate limits by API type and supports up to 1,000 live-feed instrument subscriptions at a time. Its current trading-API guidance also requires API order placement to originate from a registered static IP. These limits and requirements are treated as provider configuration and must be re-verified before production.

## Development Phases

| Phase | Name | Status |
|---|---|---|
| 0 | Foundation & specifications | 🟢 Complete |
| 1 | Market Data Engine | 🟡 In Progress |
| 2 | Instrument Master & Data Storage | 🟡 Instrument identity implemented; persistence pending |
| 3 | Scanner & Signal Engine | ⚪ Planned |
| 4 | AI Analysis Engine | ⚪ Planned |
| 5 | Trade Planner & Risk Engine | ⚪ Planned |
| 6 | Paper Execution | ⚪ Planned |
| 7 | Backtesting | ⚪ Planned |
| 8 | Broker Integration | 🟡 Groww selected; implementation gated |
| 9 | Dashboard & Operations | ⚪ Planned |
| 10 | Controlled Live Deployment | ⚪ Planned |

## CI / Change Discipline

CI is intentionally **not triggered on every push to `main`**. Earlier development caused unnecessary red runs because multiple related files were committed sequentially while the repository was temporarily between implementation states.

The CI workflow now runs only when:

1. A pull request is opened/updated, or
2. A workflow run is explicitly started with `workflow_dispatch`.

For this project, development work is performed directly on `main`; pull requests and development branches are not part of the normal workflow.

Development therefore follows a **preflight → batch → CI** rule:

```text
Plan change
   ↓
Implement complete change set on main
   ↓
Review imports / contracts / tests / fixtures
   ↓
Update documentation
   ↓
Run CI once when the tree is expected to be internally consistent
   ↓
If green → proceed
If red → fix on main before adding more functionality
```

We do not intentionally create CI failures merely to discover obvious integration mistakes. CI is the verification gate, not the development loop.

## Immediate Next Step

### DATA-004 → final controlled CI validation

DATA-003 is complete: the instrument master model, CSV normalizer, lookup registry and mapping tests passed CI.

DATA-004 is implemented with deterministic candle validation, staleness detection, and a mandatory fail-closed `MarketDataService` quality gate. The implementation and documentation are now aligned for the final verification.

**Next action: run the existing CI workflow manually from GitHub Actions. Do not create a pull request or another branch.**

If CI is green, mark DATA-004 complete and advance to **DATA-005 — Historical Candle Ingestion**. If CI fails, fix the failure on `main` before adding new functionality.

### What you need to do now

You do **not** need to provide the Groww API key for DATA-004. Do not commit credentials, access tokens, secrets or TOTP values.

The project is being developed directly on `main`. No new branch or pull request is required for the next step.

**Rule:** We do not move to the Scanner phase until the market-data foundation passes its deterministic quality gates and the corresponding documentation is updated.

## Repository Structure

```text
AI-Trading/
├── brain/                 # authoritative specifications and rules
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
6. CI is run only after the complete change set has passed preflight review

This keeps the repository self-documenting and prevents the implementation from drifting away from the architecture.
