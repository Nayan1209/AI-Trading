from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from src.market_data.realtime import ResolvedLtp
from src.market_data.stream import LtpEvent
from src.storage.postgres_ltp import (
    CREATE_LTP_INDEX_SQL,
    CREATE_LTP_TABLE_SQL,
    PostgresLtpRepository,
)


class FakeCursor:
    def __init__(self):
        self.executed = []
        self.executemany_calls = []
        self.fetchall_result = []
        self.fetchone_result = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params=None):
        self.executed.append((sql, params))

    def executemany(self, sql, rows):
        self.executemany_calls.append((sql, list(rows)))

    def fetchall(self):
        return self.fetchall_result

    def fetchone(self):
        return self.fetchone_result


class FakeConnection:
    def __init__(self):
        self.cursor_instance = FakeCursor()
        self.commit_count = 0
        self.closed = False

    def cursor(self):
        return self.cursor_instance

    def commit(self):
        self.commit_count += 1

    def close(self):
        self.closed = True


def event(timestamp: datetime | None = None, ltp: str = "149.5") -> ResolvedLtp:
    return ResolvedLtp(
        internal_id="NSE:CASH:RELIANCE",
        trading_symbol="RELIANCE",
        event=LtpEvent(
            exchange="NSE",
            segment="CASH",
            exchange_token="2885",
            timestamp=timestamp
            or datetime(2026, 10, 2, 9, 15, tzinfo=timezone.utc),
            ltp=Decimal(ltp),
        ),
    )


def test_initialize_schema_executes_table_and_index():
    connection = FakeConnection()
    repository = PostgresLtpRepository(connection)

    repository.initialize_schema()

    sql = [statement for statement, _ in connection.cursor_instance.executed]
    assert sql == [CREATE_LTP_TABLE_SQL, CREATE_LTP_INDEX_SQL]
    assert connection.commit_count == 1


def test_upsert_writes_resolved_ltp_idempotently():
    connection = FakeConnection()
    repository = PostgresLtpRepository(connection)

    assert repository.upsert_ltp([event()]) == 1

    sql, rows = connection.cursor_instance.executemany_calls[0]
    assert "ON CONFLICT (internal_id, timestamp)" in sql
    assert rows[0][0:5] == (
        "NSE:CASH:RELIANCE",
        "RELIANCE",
        "NSE",
        "CASH",
        "2885",
    )
    assert rows[0][5].tzinfo is not None
    assert rows[0][6] == Decimal("149.5")
    assert connection.commit_count == 1


def test_empty_upsert_does_not_touch_database():
    connection = FakeConnection()
    repository = PostgresLtpRepository(connection)

    assert repository.upsert_ltp([]) == 0
    assert connection.cursor_instance.executemany_calls == []
    assert connection.commit_count == 0


def test_get_ltp_reads_chronological_events_for_internal_id():
    connection = FakeConnection()
    repository = PostgresLtpRepository(connection)
    first = event(datetime(2026, 10, 2, 9, 15, tzinfo=timezone.utc), "149.5")
    second = event(datetime(2026, 10, 2, 9, 16, tzinfo=timezone.utc), "150.0")
    connection.cursor_instance.fetchall_result = [
        (
            first.internal_id,
            first.trading_symbol,
            first.event.exchange,
            first.event.segment,
            first.event.exchange_token,
            first.event.timestamp,
            first.event.ltp,
        ),
        (
            second.internal_id,
            second.trading_symbol,
            second.event.exchange,
            second.event.segment,
            second.event.exchange_token,
            second.event.timestamp,
            second.event.ltp,
        ),
    ]

    start = datetime(2026, 10, 2, 9, 0, tzinfo=timezone.utc)
    end = start + timedelta(hours=1)
    result = repository.get_ltp(first.internal_id, start, end)

    sql, params = connection.cursor_instance.executed[-1]
    assert "ORDER BY timestamp ASC" in sql
    assert params[0] == first.internal_id
    assert params[1] == start
    assert params[2] == end
    assert result == [first, second]


def test_get_latest_ltp_returns_newest_event():
    connection = FakeConnection()
    repository = PostgresLtpRepository(connection)
    latest = event()
    connection.cursor_instance.fetchone_result = (
        latest.internal_id,
        latest.trading_symbol,
        latest.event.exchange,
        latest.event.segment,
        latest.event.exchange_token,
        latest.event.timestamp,
        latest.event.ltp,
    )

    result = repository.get_latest_ltp(latest.internal_id)

    sql, params = connection.cursor_instance.executed[-1]
    assert "ORDER BY timestamp DESC" in sql
    assert "LIMIT 1" in sql
    assert params == (latest.internal_id,)
    assert result == latest


def test_get_latest_ltp_returns_none_when_no_event_exists():
    connection = FakeConnection()
    repository = PostgresLtpRepository(connection)

    assert repository.get_latest_ltp("NSE:CASH:RELIANCE") is None


def test_get_ltp_requires_valid_timezone_aware_range():
    connection = FakeConnection()
    repository = PostgresLtpRepository(connection)
    start = datetime(2026, 10, 2, 9, 0, tzinfo=timezone.utc)

    with pytest.raises(ValueError, match="start_time must be timezone-aware"):
        repository.get_ltp("NSE:CASH:RELIANCE", start.replace(tzinfo=None), start + timedelta(minutes=1))

    with pytest.raises(ValueError, match="end_time must be after start_time"):
        repository.get_ltp("NSE:CASH:RELIANCE", start, start)


def test_get_ltp_rejects_naive_persisted_timestamp():
    connection = FakeConnection()
    repository = PostgresLtpRepository(connection)
    connection.cursor_instance.fetchall_result = [
        (
            "NSE:CASH:RELIANCE",
            "RELIANCE",
            "NSE",
            "CASH",
            "2885",
            datetime(2026, 10, 2, 9, 15),
            Decimal("149.5"),
        )
    ]
    start = datetime(2026, 10, 2, 9, 0, tzinfo=timezone.utc)
    end = start + timedelta(minutes=30)

    with pytest.raises(ValueError, match="persisted LTP timestamp must be timezone-aware"):
        repository.get_ltp("NSE:CASH:RELIANCE", start, end)
