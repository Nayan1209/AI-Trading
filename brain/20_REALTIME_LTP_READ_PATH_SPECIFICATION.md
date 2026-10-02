# Real-Time LTP Read Path Specification
**Document ID:** DATA-010  
**Status:** Implementation complete; automatic CI validation pending  
**Scope:** Expose a controlled read boundary for persisted, instrument-resolved real-time LTP data

## Objective

Expose persisted DATA-009 LTP events to downstream market-data consumers without allowing scanners or signal logic to depend directly on PostgreSQL tables or raw provider payloads.

## Read Flow

```text
PostgreSQL ltp_events
        ↓
PostgresLtpRepository
        ↓
ResolvedLtp
        ↓
Scanner-ready market-data consumer
```

## Controlled Queries

`PostgresLtpRepository.get_latest_ltp(internal_id)` returns the newest persisted event for one canonical instrument, or `None` when no event exists.

`PostgresLtpRepository.get_ltp(internal_id, start_time, end_time)` returns persisted events for one canonical instrument in chronological order using a half-open `[start_time, end_time)` range.

Consumers query by canonical `internal_id`; they do not query arbitrary symbols, provider tokens, or raw Groww payloads. This preserves the DATA-009 instrument-resolution boundary.

## Time Safety

Read ranges require timezone-aware start and end timestamps, with `end_time` strictly after `start_time`. Persisted timestamps must also be timezone-aware and are normalized to UTC when returned as `LtpEvent` values.

## Data Boundary

The read path returns immutable provider-independent `ResolvedLtp` objects. It does not expose database rows, SQL cursors, or Groww SDK objects to downstream consumers.

This milestone does not add scanner logic, signal generation, trading decisions, order execution, or live broker connectivity.

## Acceptance Criteria

- Latest LTP can be retrieved by canonical instrument identity.
- Historical persisted LTP events can be retrieved for a validated time range.
- Results are returned as `ResolvedLtp` objects in chronological order for range reads.
- Empty latest reads return `None` without inventing market data.
- Naive timestamps and invalid ranges fail closed.
- Persisted naive timestamps are rejected rather than silently interpreted.
- Deterministic tests cover latest, range, empty and invalid-read behavior without PostgreSQL or Groww services.
- README and build-status documentation are updated.

## Safety Boundary

DATA-010 remains read-only. No live Groww connection, API credential, order, withdrawal or execution path is introduced.

## Next Gate

After DATA-010 is green, the next market-data step is to consume this controlled read boundary from scanner-ready logic. Scanner/signal generation remains downstream of validated and persisted market data.
