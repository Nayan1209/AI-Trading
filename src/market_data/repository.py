from datetime import datetime
from typing import Protocol, Sequence

from .models import Candle


class CandleRepository(Protocol):
    """Persistence boundary for validated market candles."""

    def upsert_candles(self, candles: Sequence[Candle]) -> int:
        """Insert candles or update an existing candle at the same identity/time."""
        ...

    def get_candles(
        self,
        symbol: str,
        exchange: str,
        timeframe: str,
        start_time: datetime,
        end_time: datetime,
    ) -> list[Candle]:
        """Return candles ordered chronologically for the requested range."""
        ...
