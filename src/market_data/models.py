from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel

class Candle(BaseModel):
    symbol: str
    exchange: str
    timeframe: str
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
