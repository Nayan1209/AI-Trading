# AI Trading System

> Autonomous AI trading platform — Indian equities first, multi-market architecture from day one.

## Current Status

**Phase 0 — Foundation: COMPLETE**  
**Phase 1 — Market Data Engine: 🟡 In Progress**  
**Phase 3 — Scanner & Signal Engine: 🟢 Complete**  
**Phase 4 — AI Analysis Engine: 🟡 In Progress**

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

### Phase 1 / scanner / signal progress

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
- [x] DATA-003 through DATA-016 completed with automatic CI green
- [x] SIG-001 deterministic signal-engine foundation
- [x] SIG-001 momentum strategy
- [x] SIG-001 reversal strategy
- [x] SIG-001 breakout strategy
- [x] SIG-001 deterministic engine and strategy tests
- [x] SIG-001 automatic CI validation — green

## AI Analysis Engine

The AI layer is being built as deterministic boundaries first. The project does not connect to a live model, broker, or execution path merely because an AI interface exists.

- [x] AI-001 provider-independent analyst contract and structured output validation
- [x] AI-002 deterministic signal-to-analysis context builder
- [x] AI-003 deterministic analysis orchestration from signal → context → analyst
- [x] AI-004 deterministic prompt construction boundary
- [x] AI-005 provider-independent model adapter boundary
- [x] AI-006 deterministic response parsing boundary
- [ ] AI-007 deterministic analysis integrity gate — implementation in progress

### AI-007 target flow

```text
SignalCandidate
    ↓
AI-002 Context Builder
    ↓
AI-003 Analysis Orchestration
    ↓
AI-004 Prompt Builder
    ↓
AI-005 Model Adapter
    ↓
AI-006 Response Parser
    ↓
AI-001 validated AIAnalysis
    ↓
AI-007 Analysis Integrity Gate
    ↓
Trade Planner / RISK-001
```

AI-007 performs deterministic internal-consistency checks only. BUY/SELL analyses must have coherent entry, stop-loss, and target ordering; WATCH/NO_TRADE analyses cannot carry execution prices. Passing AI-007 does **not** approve a trade, calculate risk, or authorize execution.

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

Groww is the first broker/market-data integration for the India-first phase. The integration is deliberately isolated behind an adapter so future providers can be added without changing strategy logic. The first adapter milestone remains read-only.

## Development Phases

| Phase | Name | Status |
|---|---|---|
| 0 | Foundation & specifications | 🟢 Complete |
| 1 | Market Data Engine | 🟡 In Progress |
| 2 | Instrument Master & Data Storage | 🟢 Complete through DATA-016 |
| 3 | Scanner & Signal Engine | 🟢 Complete |
| 4 | AI Analysis Engine | 🟡 AI-001 → AI-007 in progress |
| 5 | Trade Planner & Risk Engine | ⚪ Planned |
| 6 | Paper Execution | ⚪ Planned |
| 7 | Backtesting | ⚪ Planned |
| 8 | Broker Integration | 🟡 Groww selected; implementation gated |
| 9 | Dashboard & Operations | ⚪ Planned |
| 10 | Controlled Live Deployment | ⚪ Planned |

## CI / Change Discipline

CI runs **automatically on every push to `main`** and can also be started with `workflow_dispatch`. There is no pull-request requirement for this project.

Development work is performed directly on `main`; pull requests and development branches are not part of the normal workflow.

Because CI is automatic, we do not intentionally push half-built changes. Development follows:

```text
Plan change
   ↓
Implement complete change set on main
   ↓
Review imports / contracts / tests / fixtures / docs
   ↓
Push once
   ↓
Automatic CI
   ↓
If green → proceed
If red → fix on main before adding more functionality
```

## Immediate Next Step

**AI-007 — deterministic analysis integrity gate.** Complete the integrity checks and deterministic tests, then let the automatic CI verify the coherent change set. If CI is green, mark AI-007 complete and define the next AI-analysis boundary.
