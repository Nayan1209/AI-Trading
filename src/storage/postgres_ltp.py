"""PostgreSQL persistence and controlled reads for instrument-resolved LTP events."""

from datetime import datetime, timezone
from typing import Any, Sequence

import psycopg

from src.market_data.realtime import ResolvedLtp
from src.market_data.stream import LtpEvent


CREATE_LTP_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS ltp_events (
    id BIGSERIAL PRIMARY KEY,
    internal_id TEXT NOT NULL,
    trading_symbol TEXT NOT NULL,
    exchange TEXT NOT NULL,
    segment TEXT NOT NULL,
    exchange_token TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    ltp NUMERIC(28, 10) NOT NULL CHECK (ltp > 0),
    received_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (internal_id, timestamp)
)
"""

CREATE_LTP_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_ltp_events_lookup
    ON ltp_events (exchange, segment, exchange_token, timestamp)
"""

UPSERT_LTP_SQL = """
INSERT INTO ltp_events (
    internal_id, trading_symbol, exchange, segment,
    exchange_token, timestamp, ltp
) VALUES (%s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (internal_id, timestamp)
DO UPDATE SET
    trading_symbol = EXCLUDED.trading_symbol,
    exchange = EXCLUDED.exchange,
    segment = EXCLUDED.segment,
    exchange_token = EXCLUDED.exchange_token,
    ltp = EXCLUDED.ltp
"""

SELECT_LTP_RANGE_SQL = """
SELECT internal_id, trading_symbol, exchange, segment,
       exchange_token, timestamp, ltp
FROM ltp_events
WHERE internal_id = %s
  AND timestamp >= %s
  AND timestamp < %s
ORDER BY timestamp ASC
"""

SELECT_LATEST_LTP_SQL = """
SELECT internal_id, trading_symbol, exchange, segment,
       exchange_token, timestamp, ltp
FROM ltp_events
WHERE internal_id = %s
ORDER BY timestamp DESC
LIMIT 1
"""


class PostgresLtpRepository:
    """Store and read only normalized, instrument-resolved LTP events."""

    def __init__(self, connection: Any):
        self._connection = connection

    @classmethod
    def connect(cls, dsn: str) -> "PostgresLtpRepository":
        return cls(psycopg.connect(dsn))

    def initialize_schema(self) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(CREATE_LTP_TABLE_SQL)
            cursor.execute(CREATE_LTP_INDEX_SQL)
        self._connection.commit()

    def upsert_ltp(self, events: Sequence[ResolvedLtp]) -> int:
        if not events:
            return 0

        rows = [
            (
                item.internal_id,
                item.trading_symbol,
                item.event.exchange,
                item.event.segment,
                item.event.exchange_token,
                item.event.timestamp,
                item.event.ltp,
            )
            for item in events
        ]
        with self._connection.cursor() as cursor:
            cursor.executemany(UPSERT_LTP_SQL, rows)
        self._connection.commit()
        return len(rows)

    def get_ltp(
        self,
        internal_id: str,
        start_time: datetime,
        end_time: datetime,
    ) -> list[ResolvedLtp]:
        """Read persisted LTP events for one canonical instrument and time range."""
        self._validate_time_range(start_time, end_time)

        with self._connection.cursor() as cursor:
            cursor.execute(
                SELECT_LTP_RANGE_SQL,
                (
                    internal_id,
                    start_time.astimezone(timezone.utc),
                    end_time.astimezone(timezone.utc),
                ),
            )
            rows = cursor.fetchall()

        return [self._row_to_resolved_ltp(row) for row in rows]

    def get_latest_ltp(self, internal_id: str) -> ResolvedLtp | None:
        """Read the newest persisted LTP for one canonical instrument."""
        with self._connection.cursor() as cursor:
            cursor.execute(SELECT_LATEST_LTP_SQL, (internal_id,))
            row = cursor.fetchone()

        return None if row is None else self._row_to_resolved_ltp(row)

    @staticmethod
    def _validate_time_range(start_time: datetime, end_time: datetime) -> None:
        if start_time.tzinfo is None or start_time.utcoffset() is None:
            raise ValueError("start_time must be timezone-aware")
        if end_time.tzinfo is None or end_time.utcoffset() is None:
            raise ValueError("end_time must be timezone-aware")
        if end_time <= start_time:
            raise ValueError("end_time must be after start_time")

    @staticmethod
    def _row_to_resolved_ltp(row: Sequence[Any]) -> ResolvedLtp:
        timestamp = row[5]
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError("persisted LTP timestamp must be timezone-aware")
        return ResolvedLtp(
            internal_id=row[0],
            trading_symbol=row[1],
            event=LtpEvent(
                exchange=row[2],
                segment=row[3],
                exchange_token=row[4],
                timestamp=timestamp.astimezone(timezone.utc),
                ltp=row[6],
            ),
        )

    def close(self) -> None:
        self._connection.close()
