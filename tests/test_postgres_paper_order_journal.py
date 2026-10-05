from dataclasses import replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from src.ai_analyst import AIDecision
from src.paper_execution import PaperOrder, PaperOrderStatus
from src.storage.postgres_paper_orders import (
    CREATE_PAPER_ORDERS_INDEX_SQL,
    CREATE_PAPER_ORDERS_TABLE_SQL,
    INSERT_PAPER_ORDER_SQL,
    SELECT_PAPER_ORDER_BY_CLIENT_ID_SQL,
    SELECT_PAPER_ORDER_BY_IDENTITY_SQL,
    SELECT_PAPER_ORDER_BY_ID_SQL,
    SELECT_PAPER_ORDER_HISTORY_SQL,
    PostgresPaperOrderJournal,
)


class FakeCursor:
    def __init__(self):
        self.executed = []
        self.fetchone_results = []
        self.fetchall_results = []
        self.execute_error = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params=None):
        self.executed.append((sql, params))
        if self.execute_error is not None:
            raise self.execute_error

    def fetchone(self):
        if not self.fetchone_results:
            return None
        return self.fetchone_results.pop(0)

    def fetchall(self):
        if not self.fetchall_results:
            return []
        return self.fetchall_results.pop(0)


class FakeConnection:
    def __init__(self):
        self.cursor_instance = FakeCursor()
        self.commit_count = 0
        self.rollback_count = 0
        self.closed = False

    def cursor(self):
        return self.cursor_instance

    def commit(self):
        self.commit_count += 1

    def rollback(self):
        self.rollback_count += 1

    def close(self):
        self.closed = True


def paper_order(**overrides) -> PaperOrder:
    values = {
        "order_id": "PAPER-abc123",
        "client_order_id": "CLIENT-001",
        "internal_id": "NSE:CASH:RELIANCE",
        "trading_symbol": "RELIANCE",
        "decision": AIDecision.BUY,
        "quantity": 10,
        "fill_price": Decimal("101.25"),
        "status": PaperOrderStatus.FILLED,
        "created_at": datetime(2026, 10, 4, 10, 0, tzinfo=timezone.utc),
    }
    values.update(overrides)
    return PaperOrder(**values)


def order_row(order: PaperOrder, *, created_at: datetime | None = None) -> tuple:
    return (
        order.order_id,
        order.client_order_id,
        order.internal_id,
        order.trading_symbol,
        order.decision.value,
        order.quantity,
        order.fill_price,
        order.status.value,
        created_at or order.created_at,
    )


def test_initialize_schema_executes_table_and_history_index():
    connection = FakeConnection()
    repository = PostgresPaperOrderJournal(connection)

    repository.initialize_schema()

    assert [sql for sql, _ in connection.cursor_instance.executed] == [
        CREATE_PAPER_ORDERS_TABLE_SQL,
        CREATE_PAPER_ORDERS_INDEX_SQL,
    ]
    assert connection.commit_count == 1


def test_migration_defines_append_only_order_identity_and_history_index():
    migration_path = Path(__file__).parents[1] / "database" / "migrations" / "003_paper_orders.sql"
    migration = migration_path.read_text(encoding="utf-8")

    assert "order_id TEXT PRIMARY KEY" in migration
    assert "client_order_id TEXT NOT NULL UNIQUE" in migration
    assert "fill_price NUMERIC(28, 10)" in migration
    assert "status = 'FILLED'" in migration
    assert "idx_paper_orders_history" in migration


def test_record_inserts_and_returns_filled_order():
    connection = FakeConnection()
    order = paper_order()
    connection.cursor_instance.fetchone_results = [order_row(order)]
    repository = PostgresPaperOrderJournal(connection)

    result = repository.record(order)

    sql, params = connection.cursor_instance.executed[0]
    assert sql == INSERT_PAPER_ORDER_SQL
    assert params[:4] == (
        order.order_id,
        order.client_order_id,
        order.internal_id,
        order.trading_symbol,
    )
    assert params[-1] == order.created_at
    assert result == order
    assert connection.commit_count == 1
    assert connection.rollback_count == 0


def test_identical_replay_returns_first_record_and_timestamp():
    connection = FakeConnection()
    stored = paper_order(created_at=datetime(2026, 10, 4, 10, 0, tzinfo=timezone.utc))
    replay = replace(stored, created_at=stored.created_at + timedelta(minutes=1))
    connection.cursor_instance.fetchone_results = [None]
    connection.cursor_instance.fetchall_results = [[order_row(stored)]]
    repository = PostgresPaperOrderJournal(connection)

    result = repository.record(replay)

    assert result == stored
    assert connection.cursor_instance.executed[1] == (
        SELECT_PAPER_ORDER_BY_IDENTITY_SQL,
        (replay.order_id, replay.client_order_id),
    )
    assert connection.commit_count == 1
    assert connection.rollback_count == 0


@pytest.mark.parametrize(
    "candidate",
    [
        lambda stored: replace(stored, quantity=11),
        lambda stored: replace(stored, client_order_id="CLIENT-OTHER"),
        lambda stored: replace(stored, order_id="PAPER-OTHER"),
    ],
)
def test_identity_collision_with_different_payload_is_rejected(candidate):
    connection = FakeConnection()
    stored = paper_order()
    proposed = candidate(stored)
    connection.cursor_instance.fetchone_results = [None]
    connection.cursor_instance.fetchall_results = [[order_row(stored)]]
    repository = PostgresPaperOrderJournal(connection)

    with pytest.raises(ValueError, match="identity conflicts"):
        repository.record(proposed)

    assert connection.commit_count == 0
    assert connection.rollback_count == 1


def test_multiple_identity_matches_are_rejected():
    connection = FakeConnection()
    proposed = paper_order()
    conflicting_order = replace(proposed, client_order_id="CLIENT-OTHER")
    conflicting_client = replace(proposed, order_id="PAPER-OTHER")
    connection.cursor_instance.fetchone_results = [None]
    connection.cursor_instance.fetchall_results = [
        [order_row(conflicting_order), order_row(conflicting_client)]
    ]
    repository = PostgresPaperOrderJournal(connection)

    with pytest.raises(ValueError, match="identity conflicts"):
        repository.record(proposed)

    assert connection.rollback_count == 1


@pytest.mark.parametrize(
    "invalid_order, error",
    [
        (replace(paper_order(), order_id=" "), "order_id must not be empty"),
        (replace(paper_order(), internal_id=" "), "internal_id must not be empty"),
        (replace(paper_order(), decision="BUY"), "decision must be BUY or SELL"),
        (replace(paper_order(), quantity=0), "positive integer"),
        (replace(paper_order(), quantity=True), "positive integer"),
        (replace(paper_order(), fill_price=Decimal("NaN")), "finite Decimal"),
        (replace(paper_order(), fill_price=Decimal("0")), "must be positive"),
        (replace(paper_order(), fill_price=Decimal("1.12345678901")), "10 decimal places"),
        (replace(paper_order(), fill_price=Decimal("1000000000000000000")), "exceeds NUMERIC"),
        (replace(paper_order(), created_at=datetime(2026, 10, 4, 10, 0)), "timezone-aware"),
        (replace(paper_order(), status="REJECTED"), "must be FILLED"),
    ],
)
def test_invalid_order_is_rejected_before_database_write(invalid_order, error):
    connection = FakeConnection()
    repository = PostgresPaperOrderJournal(connection)

    with pytest.raises(ValueError, match=error):
        repository.record(invalid_order)

    assert connection.cursor_instance.executed == []
    assert connection.commit_count == 0
    assert connection.rollback_count == 0


def test_non_paper_order_type_is_rejected_before_database_write():
    connection = FakeConnection()
    repository = PostgresPaperOrderJournal(connection)

    with pytest.raises(TypeError, match="PaperOrder"):
        repository.record(object())

    assert connection.cursor_instance.executed == []


def test_database_failure_rolls_back_insert():
    connection = FakeConnection()
    connection.cursor_instance.execute_error = RuntimeError("database unavailable")
    repository = PostgresPaperOrderJournal(connection)

    with pytest.raises(RuntimeError, match="database unavailable"):
        repository.record(paper_order())

    assert connection.commit_count == 0
    assert connection.rollback_count == 1


def test_lookups_and_snapshot_restore_utc_order_history():
    connection = FakeConnection()
    first = paper_order()
    second = replace(
        first,
        order_id="PAPER-second",
        client_order_id="CLIENT-002",
        created_at=first.created_at + timedelta(minutes=1),
    )
    first_row = order_row(first)
    second_row = order_row(second)
    connection.cursor_instance.fetchone_results = [first_row, second_row, None]
    connection.cursor_instance.fetchall_results = [[first_row, second_row]]
    repository = PostgresPaperOrderJournal(connection)

    assert repository.get_by_order_id(first.order_id) == first
    assert repository.get_by_client_order_id(second.client_order_id) == second
    assert repository.get_by_order_id("PAPER-missing") is None
    assert repository.snapshot() == (first, second)
    assert [sql for sql, _ in connection.cursor_instance.executed] == [
        SELECT_PAPER_ORDER_BY_ID_SQL,
        SELECT_PAPER_ORDER_BY_CLIENT_ID_SQL,
        SELECT_PAPER_ORDER_BY_ID_SQL,
        SELECT_PAPER_ORDER_HISTORY_SQL,
    ]
    assert "ORDER BY created_at ASC, order_id ASC" in SELECT_PAPER_ORDER_HISTORY_SQL


def test_persisted_order_requires_timezone_aware_timestamp():
    connection = FakeConnection()
    order = paper_order()
    connection.cursor_instance.fetchone_results = [
        order_row(order, created_at=datetime(2026, 10, 4, 10, 0))
    ]
    repository = PostgresPaperOrderJournal(connection)

    with pytest.raises(ValueError, match="persisted paper-order timestamp must be timezone-aware"):
        repository.record(order)

    assert connection.rollback_count == 1
