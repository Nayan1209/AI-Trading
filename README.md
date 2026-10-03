# AI Trading System

> Autonomous AI trading platform — Indian equities first, multi-market architecture from day one.

## Current Status

**Phase 0 — Foundation: COMPLETE**  
**Phase 1 — Market Data Engine: 🟢 Complete through DATA-016**  
**Phase 2 — Instrument Master & Data Storage: 🟢 Complete through DATA-016**  
**Phase 3 — Scanner & Signal Engine: 🟢 Complete**  
**Phase 4 — AI Analysis Engine: 🟢 Complete through AI-007**  
**Phase 5 — Trade Planner, Risk & Execution Controls: 🟢 Complete through EXEC-003**  
**Phase 6 — Paper Execution: 🟡 In Progress — PAPER-005**

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

### Phase 1 / market-data progress

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
- [x] DATA-001 through DATA-016 completed with automatic CI green
- [x] SIG-001 deterministic signal-engine foundation
- [x] SIG-001 momentum strategy
- [x] SIG-001 reversal strategy
- [x] SIG-001 breakout strategy
- [x] SIG-001 deterministic engine and strategy tests
- [x] SIG-001 automatic CI validation — green

## AI Analysis Engine

The AI layer is built as deterministic boundaries first. No live model, broker, or execution path is connected merely because an AI interface exists.

- [x] AI-001 provider-independent analyst contract and structured output validation
- [x] AI-002 deterministic signal-to-analysis context builder
- [x] AI-003 deterministic analysis orchestration
- [x] AI-004 deterministic prompt construction boundary
- [x] AI-005 provider-independent model adapter boundary
- [x] AI-006 deterministic response parsing boundary
- [x] AI-007 deterministic analysis integrity gate

### AI flow

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
Trade Planner
    ↓
RISK-001 Risk Engine
    ↓
RISK-002 Portfolio Risk Gate
```

AI-007 performs deterministic internal-consistency checks only. Passing AI-007 does not approve a trade or calculate risk.

## Phase 5 — Trade Planner, Risk & Execution Controls

### RISK-001 — Risk Engine

- [x] Explicit equity and risk-budget inputs
- [x] Stop-loss based per-unit risk calculation
- [x] Maximum notional exposure cap
- [x] Lot-size aligned quantity rounding
- [x] Zero-quantity rejection
- [x] BUY/SELL-only planning gate
- [x] Automatic CI validation — green

RISK-001 never places an order and never lets AI confidence override deterministic limits.

### PLAN-001 — Deterministic Trade Planner

- [x] Preserve validated BUY/SELL entry, stop-loss, and target
- [x] Consume bounded quantity from RISK-001
- [x] Preserve deterministic risk budget and notional values
- [x] Reject WATCH/NO_TRADE through the risk gate
- [x] Immutable planning result
- [x] No broker, network, credential, or model dependency
- [x] Automatic CI validation — green

PLAN-001 creates order intent only. It does not authorize or execute a live order.

### RISK-002 — Portfolio Exposure & Concentration Gate

- [x] Explicit portfolio exposure limit
- [x] Explicit single-symbol concentration limit
- [x] Maximum open-position count
- [x] Conservative gross exposure semantics
- [x] Existing-symbol position-slot handling
- [x] Duplicate/malformed position rejection
- [x] Automatic CI validation — green

RISK-002 does not execute orders, access broker credentials, or infer hidden portfolio state.

### EXEC-001 — Groww Broker Adapter Boundary

- [x] Immutable provider-shaped order intent
- [x] Explicit development/paper/staging/production environment boundary
- [x] Mandatory RISK-002 approval before submission path
- [x] Explicit execution-control lock
- [x] Broker transport isolated behind a small protocol
- [x] No credentials or access tokens in source control
- [x] Automatic CI validation — green

### EXEC-002 — Static-IP Production Runtime

- [x] Production environment requirement
- [x] Registered static-IP evidence
- [x] Observed public-IP match validation
- [x] Execution lock remains enabled during readiness evaluation
- [x] Independent kill-switch readiness
- [x] Credential reference presence without storing credentials
- [x] Automatic CI validation — green

### EXEC-003 — Controlled Deployment Authorization

- [x] EXEC-002 runtime readiness evidence
- [x] Paper/simulation verification evidence
- [x] Explicit operator approval
- [x] Rollback plan readiness
- [x] Independent kill-switch readiness
- [x] Execution lock remains enabled through controlled handoff
- [x] Automatic CI validation — green

EXEC-003 does not call Groww, read credentials, enable live trading, or submit orders. A passing result means the controlled-deployment evidence boundary is complete.

## Phase 6 — Paper Execution

### PAPER-001 — Deterministic Paper Execution Boundary

PAPER-001 is the first paper/simulation execution layer. It consumes an existing immutable `TradePlan` and produces a deterministic simulated fill without any broker/network access.

- [x] Explicit `paper` environment requirement
- [x] BUY/SELL-only execution boundary
- [x] Positive quantity validation
- [x] Positive simulated fill-price validation
- [x] Deterministic simulated order ID
- [x] Immutable simulated order/fill result
- [x] No broker credentials or network transport
- [x] Automatic CI validation — green

PAPER-001 deliberately does not implement live Groww orders, exchange matching, slippage, partial fills, portfolio persistence, or reconciliation.

### PAPER-002 — Deterministic Paper Order Ledger

PAPER-002 adds an in-process ledger for completed PAPER-001 simulated orders. It creates an auditable, deterministic order history without introducing a database or external state.

- [x] Accept only valid immutable `PaperOrder` records
- [x] Preserve insertion order
- [x] Deterministic order-ID lookup
- [x] Duplicate order-ID rejection
- [x] Immutable tuple snapshots
- [x] No broker/network access
- [x] No credentials or secrets
- [x] Automatic CI validation — green

PAPER-002 does not implement database persistence, exchange matching, slippage, partial fills, portfolio/P&L accounting, reconciliation, or live broker submission.

### PAPER-003 — Deterministic Paper Order Reconciliation

PAPER-003 adds a read-only reconciliation boundary over the PAPER-002 ledger. It compares expected immutable `PaperOrder` records with the recorded ledger snapshot and produces a deterministic result.

- [x] Accept only a `PaperOrderLedger` and immutable expected-order tuple
- [x] Require unique expected order IDs
- [x] Detect missing order IDs
- [x] Detect unexpected recorded orders
- [x] Detect mismatched recorded order values
- [x] Preserve deterministic result ordering
- [x] Return an immutable reconciliation result
- [x] No ledger mutation during reconciliation
- [x] No broker/network access
- [x] No credentials or secrets
- [x] Automatic CI validation — green

PAPER-003 does not implement exchange matching, slippage, partial fills, portfolio/P&L accounting, database persistence, or live broker submission.

### PAPER-004 — Deterministic Paper Execution Session

PAPER-004 composes the existing paper boundaries into one complete deterministic session. It executes an approved `TradePlan`, records the immutable simulated order, and reconciles the complete expected session history.

- [x] Execute through the PAPER-001 boundary
- [x] Preserve the immutable simulated `PaperOrder`
- [x] Record exactly once through the PAPER-002 ledger
- [x] Build expected history from the pre-session ledger snapshot plus the new order
- [x] Reconcile through the read-only PAPER-003 boundary
- [x] Return an immutable `PaperExecutionSessionResult`
- [x] No broker/network access
- [x] No credentials or secrets
- [x] Automatic CI validation — green

PAPER-004 does not implement exchange matching, slippage, partial fills, portfolio/P&L accounting, database persistence, or live broker submission.

### PAPER-005 — Deterministic Paper Position Accounting

PAPER-005 adds deterministic in-process position accounting on top of completed paper fills. It maintains explicit long-only position state, weighted-average entry pricing, realized P&L, duplicate-order protection, and immutable snapshots.

- [x] Explicit caller-supplied position key
- [x] Accept only filled `PaperOrder` records
- [x] Weighted-average entry price for BUY accumulation
- [x] SELL only against an existing long position
- [x] Reject SELL quantities larger than the current position
- [x] Deterministic realized P&L calculation
- [x] Duplicate order-ID protection
- [x] Immutable deterministic position snapshots
- [x] No broker/network access
- [x] No credentials or secrets
- [ ] Automatic CI validation — pending for current milestone

PAPER-005 does not implement exchange matching, slippage, fees/taxes, partial fills, short selling, mark-to-market valuation, unrealized P&L, database persistence, or live broker submission.

## Safety Boundary

This repository currently has **no enabled real-money broker execution path**. Development and paper environments cannot place live orders. Provider-facing execution remains disabled until the required execution and production-runtime controls are separately verified.

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
Portfolio Risk Gate
    ↓
Execution Boundary
    ↓
Paper Execution
    ↓
Paper Order Ledger
    ↓
Paper Order Reconciliation
    ↓
Paper Execution Session
    ↓
Paper Position Accounting
    ↓
Reconciliation / Monitoring
    ↓
Trade Journal / Analytics
    ↓
Controlled Live Execution (future)
```

## Development Phases

| Phase | Name | Status |
|---|---|---|
| 0 | Foundation & specifications | 🟢 Complete |
| 1 | Market Data Engine | 🟢 Complete through DATA-016 |
| 2 | Instrument Master & Data Storage | 🟢 Complete through DATA-016 |
| 3 | Scanner & Signal Engine | 🟢 Complete |
| 4 | AI Analysis Engine | 🟢 Complete through AI-007 |
| 5 | Trade Planner, Risk & Execution Controls | 🟢 Complete through EXEC-003 |
| 6 | Paper Execution | 🟡 PAPER-005 in progress |
| 7 | Backtesting | ⚪ Planned |
| 8 | Broker Integration | 🟡 Groww selected; execution gated |
| 9 | Dashboard & Operations | ⚪ Planned |
| 10 | Controlled Live Deployment | ⚪ Planned |

## Development Progress

### Completed milestone chain

```text
DATA-001 → DATA-016 🟢
        ↓
SIG-001 🟢
        ↓
AI-001 → AI-007 🟢
        ↓
RISK-001 🟢
        ↓
PLAN-001 🟢
        ↓
RISK-002 🟢
        ↓
EXEC-001 🟢
        ↓
EXEC-002 🟢
        ↓
EXEC-003 🟢
        ↓
PAPER-001 🟢
        ↓
PAPER-002 🟢
        ↓
PAPER-003 🟢
        ↓
PAPER-004 🟢
        ↓
PAPER-005 🟡
```

The deterministic data, scanner, signal, AI, risk, planning, portfolio-risk, broker-adapter, runtime-readiness, controlled-deployment, paper-execution, paper-order-ledger, paper-order-reconciliation, and paper-execution-session boundaries are complete. The current milestone is the deterministic paper-position accounting boundary.

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

**PAPER-005 — deterministic paper-position accounting.** Wait for automatic CI to turn green, then proceed to the next paper-execution boundary.
