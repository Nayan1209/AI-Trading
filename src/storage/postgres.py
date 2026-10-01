"""PostgreSQL persistence for validated market candles."""

from datetime import datetime, timezone
from typing import Any, Sequence

import psycopg

from src.market_data.models import Candle
from src.market_data.validation import validate_candle


CREATE_CANDLES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS candles (
    id BIGSERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    exchange TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    open NUMERIC(28, 10) NOT NULL,
    high NUMERIC(28, 10) NOT NULL,
    low NUMERIC(28, 10) NOT NULL,
    close NUMERIC(28, 10) NOT NULL,
    volume BIGINT NOT NULL CHECK (volume >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (symbol, exchange, timeframe, timestamp)
)
"""

CREATE_CANDLES_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_candles_lookup
    ON candles (exchange, symbol, timeframe, timestamp)
"""

UPSERT_CANDLE_SQL = """
INSERT INTO candles (
    symbol, exchange, timeframe, timestamp,
    open, high, low, close, volume
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (symbol, exchange, timeframe, timestamp)
DO UPDATE SET
    open = EXCLUDED.open,
    high = EXCLUDED.high,
    low = EXCLUDED.low,
    close = EXCLUDED.close,
    volume = EXCLUDED.volume
"""

SELECT_CANDLES_SQL = """
SELECT symbol, exchange, timeframe, timestamp,
       open, high, low, close, volume
FROM candles
WHERE symbol = %s
  AND exchange = %s
  AND timeframe = %s
  AND timestamp >= %s
  AND timestamp < %s
ORDER BY timestamp ASC
"""


class PostgresCandleRepository:
    """Store only validated candles in PostgreSQL."""

    def __init__(self, connection: Any):
        self._connection = connection

    @classmethod
    def connect(cls, dsn: str) -> "PostgresCandleRepository":
        return cls(psycopg.connect(dsn))

    def initialize_schema(self) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(CREATE_CANDLES_TABLE_SQL)
            cursor.execute(CREATE_CANDLES_INDEX_SQL)
        self._connection.commit()

    def upsert_candles(self, candles: Sequence[Candle]) -> int:
        rows = []
        for candle in candles:
            validate_candle(candle)
            timestamp = candle.timestamp.astimezone(timezone.utc)
            rows.append(
                (
                    candle.symbol,
                    candle.exchange,
                    candle.timeframe,
                    timestamp,
                    candle.open,
                    candle.high,
                    candle.low,
                    candle.close,
                    candle.volume,
                )
            )

        if not rows:
            return 0

        with self._connection.cursor() as cursor:
            cursor.executemany(UPSERT_CANDLE_SQL, rows)
        self._connection.commit()
        return len(rows)

    def get_candles(
        self,
        symbol: str,
        exchange: str,
        timeframe: str,
        start_time: datetime,
        end_time: datetime,
    ) -> list[Candle]:
        if start_time.tzinfo is None or start_time.utcoffset() is None:
            raise ValueError("start_time must be timezone-aware")
        if end_time.tzinfo is None or end_time.utcoffset() is None:
            raise ValueError("end_time must be timezone-aware")
        if end_time <= start_time:
            raise ValueError("end_time must be after start_time")

        with self._connection.cursor() as cursor:
            cursor.execute(
                SELECT_CANDLES_SQL,
                (
                    symbol,
                    exchange,
                    timeframe,
                    start_time.astimezone(timezone.utc),
                    end_time.astimezone(timezone.utc),
                ),
            )
            rows = cursor.fetchall()

        return [
            Candle(
                symbol=row[0],
                exchange=row[1],
                timeframe=row[2],
                timestamp=row[3],
                open=row[4],
                high=row[5],
                low=row[6],
                close=row[7],
                volume=row[8],
            )
            for row in rows
        ]

    def close(self) -> None:
        self._connection.close()
