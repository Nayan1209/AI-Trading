# Signal Engine Specification
**Document ID:** SIG-001  
**Status:** Foundation implementation started  
**Scope:** Deterministic strategy orchestration over the DATA-016 scanner shortlist

## Objective

Create the first signal-engine boundary after the deterministic scanner shortlist. SIG-001 separates scanner selection from strategy observations and from later AI analysis, trade planning, risk and execution.

## Input Contract

The signal engine accepts only DATA-015 `ScannerRankedCandidate` values that satisfy the DATA-016 shortlist contract. Candidate order and one-based ranks are preserved.

## Signal Contract

A `SignalCandidate` contains:

- DATA-016 rank;
- canonical internal instrument ID;
- trading symbol;
- strategy type;
- directional bias (`long`, `short`, or `neutral`);
- strategy score constrained to `0..100`;
- non-empty deterministic reason codes.

The initial contract reserves five strategy families: breakout, pullback, momentum, trend continuation, and reversal.

## Strategy Boundary

Strategies implement a small evaluation protocol and return either a `SignalCandidate` or `None`. The engine rejects duplicate strategy types and rejects strategy output that does not match the candidate identity, rank, symbol, or strategy type supplied to it.

This milestone intentionally does **not** define predictive thresholds for the five strategy families. Those rules require their own deterministic specifications and tests rather than being invented inside the orchestration layer.

## Determinism

Given the same ordered shortlist and the same deterministic strategies, the engine evaluates candidates and strategies in stable input order and returns a stable tuple.

## Safety Boundary

SIG-001 does not call an AI model, create an executable trade plan, override risk controls, connect to Groww, place orders, withdraw funds, or perform live trading. A signal observation is not an execution instruction.

## Acceptance Criteria

- DATA-016 ranked candidates are the only input boundary.
- Empty input returns an empty tuple.
- No configured strategies produces no signals.
- Strategy types must be unique.
- Signal scores are constrained to `0..100`.
- Strategy output must match the input candidate identity and rank.
- Tests require no Groww credentials or production PostgreSQL service.
- Concrete strategy rules are added only with their own deterministic acceptance criteria.
