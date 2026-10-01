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
- [ ] DATA-003 CI run for instrument master
- [ ] Data validation/stale-data detection
- [ ] Historical candle ingestion
- [ ] PostgreSQL market-data persistence
- [ ] Data-quality tests/monitoring

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

## Immediate Next Step

### DATA-003 → CI validation

The Groww instrument master model, CSV normalizer, canonical lookup registry and local validation tests are implemented. The production model permits provider-supplied zero values for `lot_size` and `freeze_quantity`. The test fixture has now been corrected for both CASH and FNO rows so all fields align with the canonical Groww CSV schema.

The next gate is the **new GitHub Actions CI run** triggered by the final fixture-alignment correction. Once the instrument-master tests pass, DATA-003 is complete and we move to deterministic market-data validation and stale-data detection (DATA-004).

The instrument identity contract is:

```text
Internal Instrument ID
        ↓
Exchange (NSE/BSE)
        ↓
Segment (CASH/FNO)
        ↓
Trading Symbol
        ↓
Groww Symbol
        ↓
Exchange Token
```

This mapping is the single source of truth for future market-data subscriptions, historical candles and—later—order execution.

### What you need to do now

**Do not provide or commit your Groww API key, secret, access token or TOTP.** DATA-003 does not require live credentials.

Open the repository's **Actions** tab and look for the workflow run triggered by the latest fixture-correction commit. If it is green, tell me **“DATA-003 CI is green.”** If it fails, send the failure screenshot/log and we will fix it before proceeding.

**Rule:** We do not move to the Scanner phase until the market-data foundation passes its tests and the corresponding documentation is updated.

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

This keeps the repository self-documenting and prevents the implementation from drifting away from the architecture.
