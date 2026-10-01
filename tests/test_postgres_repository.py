from datetime import datetime, timezone
from decimal import Decimal

import pytest

from src.market_data.models import Candle
from src.storage.postgres import (
    CREATE_CANDLES_INDEX_SQL,
    CREATE_CANDLES_TABLE_SQL,
    PostgresCandleRepository,
)


class FakeCursor:
    def __init__(self, rows=None):
        self.rows = rows or []
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

    def fetchall(self):
        return self.rows


class FakeConnection:
    def __init__(self, rows=None):
        self.cursor_instance = FakeCursor(rows)
        self.commit_count = 0
        self.closed = False

    def cursor(self):
        return self.cursor_instance

    def commit(self):
        self.commit_count += 1

    def close(self):
        self.closed = True


def candle(**overrides) -> Candle:
    values = {
        "symbol": "RELIANCE",
        "exchange": "NSE",
        "timeframe": "15m",
        "timestamp": datetime(2026, 10, 1, 10, 0, tzinfo=timezone.utc),
        "open": Decimal("100.00"),
        "high": Decimal("102.00"),
        "low": Decimal("99.00"),
        "close": Decimal("101.00"),
        "volume": 1000,
    }
    values.update(overrides)
    return Candle(**values)


def test_initialize_schema_executes_table_and_index():
    connection = FakeConnection()
    repository = PostgresCandleRepository(connection)

    repository.initialize_schema()

    sql = [statement for statement, _ in connection.cursor_instance.executed]
    assert sql == [CREATE_CANDLES_TABLE_SQL, CREATE_CANDLES_INDEX_SQL]
    assert connection.commit_count == 1


def test_upsert_validates_and_writes_candles():
    connection = FakeConnection()
    repository = PostgresCandleRepository(connection)

    count = repository.upsert_candles([candle()])

    assert count == 1
    sql, rows = connection.cursor_instance.executemany_calls[0]
    assert "ON CONFLICT (symbol, exchange, timeframe, timestamp)" in sql
    assert rows[0][0:3] == ("RELIANCE", "NSE", "15m")
    assert rows[0][3].tzinfo is not None
    assert connection.commit_count == 1


def test_upsert_rejects_invalid_candle_before_database_write():
    connection = FakeConnection()
    repository = PostgresCandleRepository(connection)

    with pytest.raises(ValueError, match="non-negative"):
        repository.upsert_candles([candle(volume=-1)])

    assert connection.cursor_instance.executemany_calls == []
    assert connection.commit_count == 0


def test_get_candles_reconstructs_internal_model():
    timestamp = datetime(2026, 10, 1, 10, 0, tzinfo=timezone.utc)
    connection = FakeConnection(
        rows=[
            (
                "RELIANCE",
                "NSE",
                "15m",
                timestamp,
                Decimal("100.00"),
                Decimal("102.00"),
                Decimal("99.00"),
                Decimal("101.00"),
                1000,
            )
        ]
    )
    repository = PostgresCandleRepository(connection)

    result = repository.get_candles(
        "RELIANCE",
        "NSE",
        "15m",
        datetime(2026, 10, 1, 9, 0, tzinfo=timezone.utc),
        datetime(2026, 10, 1, 11, 0, tzinfo=timezone.utc),
    )

    assert result == [candle()]


def test_get_candles_requires_valid_range_and_timezone():
    repository = PostgresCandleRepository(FakeConnection())
    start = datetime(2026, 10, 1, 9, 0, tzinfo=timezone.utc)

    with pytest.raises(ValueError, match="timezone-aware"):
        repository.get_candles("RELIANCE", "NSE", "15m", start.replace(tzinfo=None), start)

    with pytest.raises(ValueError, match="after"):
        repository.get_candles("RELIANCE", "NSE", "15m", start, start)
