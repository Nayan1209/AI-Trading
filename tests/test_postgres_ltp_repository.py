from datetime import datetime, timezone
from decimal import Decimal

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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params=None):
        self.executed.append((sql, params))

    def executemany(self, sql, rows):
        self.executemany_calls.append((sql, list(rows)))


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


def event() -> ResolvedLtp:
    return ResolvedLtp(
        internal_id="NSE:CASH:RELIANCE",
        trading_symbol="RELIANCE",
        event=LtpEvent(
            exchange="NSE",
            segment="CASH",
            exchange_token="2885",
            timestamp=datetime(2026, 10, 2, 9, 15, tzinfo=timezone.utc),
            ltp=Decimal("149.5"),
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
