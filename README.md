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
- [ ] Confirm CI passes
- [ ] Instrument master mapping
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

Groww currently documents rate limits by API type and supports up to 1,000 live-feed instrument subscriptions at a time. Its current trading-API guidance also requires API order placement to originate from a registered static IP. These limits and requirements are treated as provider configuration and must be re-verified before production.

## Development Phases

| Phase | Name | Status |
|---|---|---|
| 0 | Foundation & specifications | 🟢 Complete |
| 1 | Market Data Engine | 🟡 In Progress |
| 2 | Instrument Master & Data Storage | ⚪ Next |
| 3 | Scanner & Signal Engine | ⚪ Planned |
| 4 | AI Analysis Engine | ⚪ Planned |
| 5 | Trade Planner & Risk Engine | ⚪ Planned |
| 6 | Paper Execution | ⚪ Planned |
| 7 | Backtesting | ⚪ Planned |
| 8 | Broker Integration | 🟡 Groww selected; implementation gated |
| 9 | Dashboard & Operations | ⚪ Planned |
| 10 | Controlled Live Deployment | ⚪ Planned |

## Immediate Next Step

### DATA-002 → DATA-003: Instrument Master / Mapping

The Groww adapter skeleton is now in the repository. Before connecting to real market data, the next job is to build a reliable **instrument master**.

We will map:

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

This mapping becomes the single source of truth for market-data subscriptions, historical candles and—later—order execution.

### What you need to do now

**Nothing with your Groww credentials yet.** Do not paste the API key, secret, access token or TOTP into GitHub, chat, README files or source code.

For this step, simply open the repository's **Actions** tab and check whether the new **CI** workflow passes. If it fails, send me the failure screenshot/log and I will fix it before we proceed.

If CI is green, our next implementation step is **DATA-003: Groww instrument master ingestion and mapping**.

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
