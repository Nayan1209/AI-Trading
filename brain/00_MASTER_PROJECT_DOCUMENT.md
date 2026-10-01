# AI Trading System — Master Project Document
**Version:** 0.1  
**Status:** Draft / Pre-Development  
**Market:** Indian Equities (NSE/BSE)  
**Execution Model:** Autonomous trading, subject to deterministic safety/risk controls  
**Primary AI:** Claude initially, provider-agnostic architecture  
**Primary Broker:** To be finalized; initial adapter target: Upstox  

## Vision
Build an autonomous AI-powered trading platform that continuously scans Indian equity markets, identifies structured trading opportunities, analyzes context with AI, creates trade plans, validates risk deterministically, executes through a broker API, monitors positions, records every decision, and learns from outcomes.

## V1 Scope
- NSE/BSE cash equities
- Market data ingestion and normalization
- Instrument master
- Scanner
- Breakout, pullback, momentum, trend-continuation and reversal signals
- AI analysis
- Trade planning
- Position sizing and portfolio risk
- Broker execution adapter
- Position/order monitoring
- Dashboard
- Audit trail
- Backtesting and paper trading
- Operational kill switch

## Core Principle
AI may make autonomous trading decisions, but no AI component may bypass deterministic execution, risk, security, audit, or compliance controls.

## Expansion Strategy
V1 India equities → Indian derivatives → US equities → crypto → additional markets. Market-specific components must be adapters around a market-neutral core.

## Documentation Authority
The latest approved specification version is the source of truth. Code changes that alter behavior must update affected documentation.
