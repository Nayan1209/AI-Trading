"""Append-only PostgreSQL journal for completed paper orders."""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Sequence

import psycopg

from src.ai_analyst import AIDecision
from src.paper_execution import PaperOrder, PaperOrderStatus


CREATE_PAPER_ORDERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS paper_orders (
    order_id TEXT PRIMARY KEY,
    client_order_id TEXT NOT NULL UNIQUE,
    internal_id TEXT NOT NULL,
    trading_symbol TEXT NOT NULL,
    decision TEXT NOT NULL CHECK (decision IN ('BUY', 'SELL')),
    quantity BIGINT NOT NULL CHECK (quantity > 0),
    fill_price NUMERIC(28, 10) NOT NULL CHECK (fill_price > 0),
    status TEXT NOT NULL CHECK (status = 'FILLED'),
    created_at TIMESTAMPTZ NOT NULL
)
"""

CREATE_PAPER_ORDERS_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_paper_orders_history
    ON paper_orders (created_at, order_id)
"""

INSERT_PAPER_ORDER_SQL = """
INSERT INTO paper_orders (
    order_id, client_order_id, internal_id, trading_symbol,
    decision, quantity, fill_price, status, created_at
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT DO NOTHING
RETURNING order_id, client_order_id, internal_id, trading_symbol,
          decision, quantity, fill_price, status, created_at
"""

SELECT_PAPER_ORDER_BY_IDENTITY_SQL = """
SELECT order_id, client_order_id, internal_id, trading_symbol,
       decision, quantity, fill_price, status, created_at
FROM paper_orders
WHERE order_id = %s OR client_order_id = %s
ORDER BY order_id
"""

SELECT_PAPER_ORDER_BY_ID_SQL = """
SELECT order_id, client_order_id, internal_id, trading_symbol,
       decision, quantity, fill_price, status, created_at
FROM paper_orders
WHERE order_id = %s
"""

SELECT_PAPER_ORDER_BY_CLIENT_ID_SQL = """
SELECT order_id, client_order_id, internal_id, trading_symbol,
       decision, quantity, fill_price, status, created_at
FROM paper_orders
WHERE client_order_id = %s
"""

SELECT_PAPER_ORDER_HISTORY_SQL = """
SELECT order_id, client_order_id, internal_id, trading_symbol,
       decision, quantity, fill_price, status, created_at
FROM paper_orders
ORDER BY created_at ASC, order_id ASC
"""


class PostgresPaperOrderJournal:
    """Persist immutable filled paper orders in one paper execution context."""

    def __init__(self, connection: Any):
        self._connection = connection

    @classmethod
    def connect(cls, dsn: str) -> "PostgresPaperOrderJournal":
        return cls(psycopg.connect(dsn))

    def initialize_schema(self) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(CREATE_PAPER_ORDERS_TABLE_SQL)
            cursor.execute(CREATE_PAPER_ORDERS_INDEX_SQL)
        self._connection.commit()

    def record(self, order: PaperOrder) -> PaperOrder:
        """Insert an order once; return the original record on an identical replay."""
        self._validate_order(order)
        parameters = self._order_parameters(order)

        try:
            with self._connection.cursor() as cursor:
                cursor.execute(INSERT_PAPER_ORDER_SQL, parameters)
                inserted_row = cursor.fetchone()
                if inserted_row is not None:
                    result = self._row_to_order(inserted_row)
                else:
                    cursor.execute(
                        SELECT_PAPER_ORDER_BY_IDENTITY_SQL,
                        (order.order_id, order.client_order_id),
                    )
                    existing_rows = cursor.fetchall()
                    if len(existing_rows) != 1:
                        raise ValueError("paper order identity conflicts with an existing record")

                    existing = self._row_to_order(existing_rows[0])
                    if not self._same_business_payload(existing, order):
                        raise ValueError("paper order identity conflicts with a different payload")
                    result = existing

            self._connection.commit()
            return result
        except Exception:
            self._connection.rollback()
            raise

    def get_by_order_id(self, order_id: str) -> PaperOrder | None:
        with self._connection.cursor() as cursor:
            cursor.execute(SELECT_PAPER_ORDER_BY_ID_SQL, (order_id,))
            row = cursor.fetchone()
        return None if row is None else self._row_to_order(row)

    def get_by_client_order_id(self, client_order_id: str) -> PaperOrder | None:
        with self._connection.cursor() as cursor:
            cursor.execute(SELECT_PAPER_ORDER_BY_CLIENT_ID_SQL, (client_order_id,))
            row = cursor.fetchone()
        return None if row is None else self._row_to_order(row)

    def snapshot(self) -> tuple[PaperOrder, ...]:
        """Return immutable order history in deterministic timestamp order."""
        with self._connection.cursor() as cursor:
            cursor.execute(SELECT_PAPER_ORDER_HISTORY_SQL)
            rows = cursor.fetchall()
        return tuple(self._row_to_order(row) for row in rows)

    @staticmethod
    def _validate_order(order: PaperOrder) -> None:
        if not isinstance(order, PaperOrder):
            raise TypeError("order must be a PaperOrder")
        for name in ("order_id", "client_order_id", "internal_id", "trading_symbol"):
            value = getattr(order, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must not be empty")
        if not isinstance(order.decision, AIDecision) or order.decision not in (
            AIDecision.BUY,
            AIDecision.SELL,
        ):
            raise ValueError("paper order decision must be BUY or SELL")
        if type(order.quantity) is not int or order.quantity <= 0:
            raise ValueError("paper order quantity must be a positive integer")
        if order.status is not PaperOrderStatus.FILLED:
            raise ValueError("paper order must be FILLED")
        if not isinstance(order.fill_price, Decimal) or not order.fill_price.is_finite():
            raise ValueError("paper order fill_price must be a finite Decimal")
        if order.fill_price <= 0:
            raise ValueError("paper order fill_price must be positive")
        if order.fill_price.adjusted() >= 18:
            raise ValueError("paper order fill_price exceeds NUMERIC(28, 10) precision")
        if order.fill_price != order.fill_price.quantize(Decimal("0.0000000001")):
            raise ValueError("paper order fill_price supports at most 10 decimal places")
        if not isinstance(order.created_at, datetime):
            raise TypeError("paper order created_at must be a datetime")
        if order.created_at.tzinfo is None or order.created_at.utcoffset() is None:
            raise ValueError("paper order created_at must be timezone-aware")

    @staticmethod
    def _order_parameters(order: PaperOrder) -> tuple[Any, ...]:
        return (
            order.order_id,
            order.client_order_id,
            order.internal_id,
            order.trading_symbol,
            order.decision.value,
            order.quantity,
            order.fill_price,
            order.status.value,
            order.created_at.astimezone(timezone.utc),
        )

    @staticmethod
    def _same_business_payload(existing: PaperOrder, candidate: PaperOrder) -> bool:
        return (
            existing.order_id == candidate.order_id
            and existing.client_order_id == candidate.client_order_id
            and existing.internal_id == candidate.internal_id
            and existing.trading_symbol == candidate.trading_symbol
            and existing.decision is candidate.decision
            and existing.quantity == candidate.quantity
            and existing.fill_price == candidate.fill_price
            and existing.status is candidate.status
        )

    @staticmethod
    def _row_to_order(row: Sequence[Any]) -> PaperOrder:
        timestamp = row[8]
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError("persisted paper-order timestamp must be timezone-aware")
        return PaperOrder(
            order_id=row[0],
            client_order_id=row[1],
            internal_id=row[2],
            trading_symbol=row[3],
            decision=AIDecision(row[4]),
            quantity=row[5],
            fill_price=row[6],
            status=PaperOrderStatus(row[7]),
            created_at=timestamp.astimezone(timezone.utc),
        )

    def close(self) -> None:
        self._connection.close()
