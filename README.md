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
- [x] `MarketDataService` validation/staleness gate integrated
- [x] Service-level fresh/stale gate tests added
- [ ] DATA-004 CI validation
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

Groww is the first broker/market-data integration for the India-first phase. The integration is isolated behind an adapter so future providers can be added without changing strategy logic.

The first adapter milestone is deliberately **read-only**. Groww quote data is normalized into the project's internal market-data model. Current-day OHLC snapshots are not treated as interval candles; historical interval candles will use a separate adapter path.

Groww's instrument master is normalized into an internal `Instrument` model and `InstrumentMaster` registry. The registry supports lookup by internal ID, Groww symbol, exchange/trading symbol and exchange token. The first operational scope is CASH/equity; derivative-specific fields are retained for future F&O support.

Provider limits and the static-IP requirement are treated as provider configuration and must be re-verified before production.

## Development Phases

| Phase | Name | Status |
|---|---|---|
| 0 | Foundation & specifications | 🟢 Complete |
| 1 | Market Data Engine | 🟡 In Progress |
| 2 | Instrument Master & Data Storage | 🟡 Identity implemented; persistence pending |
| 3 | Scanner & Signal Engine | ⚪ Planned |
| 4 | AI Analysis Engine | ⚪ Planned |
| 5 | Trade Planner & Risk Engine | ⚪ Planned |
| 6 | Paper Execution | ⚪ Planned |
| 7 | Backtesting | ⚪ Planned |
| 8 | Broker Integration | 🟡 Groww selected; implementation gated |
| 9 | Dashboard & Operations | ⚪ Planned |
| 10 | Controlled Live Deployment | ⚪ Planned |

## CI / Change Discipline

CI is intentionally **not triggered on every push to `main`**. Related implementation files are developed as a complete change set so CI does not repeatedly test temporary intermediate states.

The CI workflow runs on pull requests or explicit `workflow_dispatch` runs.

```text
Plan change
   ↓
Implement complete change set
   ↓
Review imports / contracts / tests / fixtures
   ↓
Update documentation
   ↓
Preflight review
   ↓
CI once
   ↓
Green → next milestone
Red → fix before adding functionality
```

**CI is the verification gate, not the development loop.**

## Immediate Next Step

### DATA-004 → controlled CI validation

DATA-004 now contains deterministic candle validation, staleness detection, and a fail-closed `MarketDataService` gate. The service returns provider data only after validation and freshness checks pass.

The complete DATA-004 implementation and tests have been reviewed for obvious contract/import/test consistency. The next action is the **single CI verification gate**. If green, DATA-004 becomes complete and we start **DATA-005 — Historical Candle Ingestion**. If red, we fix the failure before adding anything else.

### What you need to do now

**Nothing.** No Groww API key is required for this CI gate. Do not commit credentials, access tokens, secrets or TOTP values.

I will control when CI is run. You do not need to manually start it.

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
6. CI only after the complete change set has passed preflight review

This keeps the repository self-documenting and prevents implementation drift.
