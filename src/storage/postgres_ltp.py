"""PostgreSQL persistence for instrument-resolved real-time LTP events."""

from typing import Any, Sequence

import psycopg

from src.market_data.realtime import ResolvedLtp


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


class PostgresLtpRepository:
    """Store only normalized and instrument-resolved LTP events."""

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

    def close(self) -> None:
        self._connection.close()
