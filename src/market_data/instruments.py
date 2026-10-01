"""Instrument master models and lookup registry.

The instrument master is the canonical mapping between our internal instrument
identity and broker/exchange identifiers. It is deliberately broker-aware but
strategy-agnostic: strategy code should consume ``Instrument`` objects instead
of hard-coding Groww symbols or exchange tokens.
"""

from __future__ import annotations

import csv
from datetime import date
from decimal import Decimal
from io import StringIO
from typing import Iterable

from pydantic import BaseModel, ConfigDict, Field


class Instrument(BaseModel):
    """Normalized representation of a tradable instrument."""

    model_config = ConfigDict(frozen=True)

    internal_id: str
    exchange: str
    exchange_token: str
    trading_symbol: str
    groww_symbol: str
    name: str | None = None
    instrument_type: str
    segment: str
    series: str | None = None
    isin: str | None = None
    underlying_symbol: str | None = None
    underlying_exchange_token: str | None = None
    expiry_date: date | None = None
    strike_price: Decimal | None = None
    lot_size: int | None = Field(default=None, ge=0)
    tick_size: Decimal | None = Field(default=None, ge=0)
    freeze_quantity: int | None = Field(default=None, ge=0)
    is_reserved: bool = False
    buy_allowed: bool = True
    sell_allowed: bool = True

    @classmethod
    def from_groww_row(cls, row: dict[str, str]) -> "Instrument":
        """Build an instrument from a Groww instrument-master CSV row."""
        exchange = _required(row, "exchange").upper()
        segment = _required(row, "segment").upper()
        trading_symbol = _required(row, "trading_symbol").upper()
        groww_symbol = _required(row, "groww_symbol")
        exchange_token = _required(row, "exchange_token")

        return cls(
            internal_id=f"{exchange}:{segment}:{trading_symbol}",
            exchange=exchange,
            exchange_token=exchange_token,
            trading_symbol=trading_symbol,
            groww_symbol=groww_symbol,
            name=_optional(row, "name"),
            instrument_type=_required(row, "instrument_type").upper(),
            segment=segment,
            series=_optional(row, "series"),
            isin=_optional(row, "isin"),
            underlying_symbol=_optional(row, "underlying_symbol"),
            underlying_exchange_token=_optional(row, "underlying_exchange_token"),
            expiry_date=_date(row.get("expiry_date")),
            strike_price=_decimal(row.get("strike_price")),
            lot_size=_int(row.get("lot_size")),
            tick_size=_decimal(row.get("tick_size")),
            freeze_quantity=_int(row.get("freeze_quantity")),
            is_reserved=_bool(row.get("is_reserved")),
            buy_allowed=_bool(row.get("buy_allowed"), default=True),
            sell_allowed=_bool(row.get("sell_allowed"), default=True),
        )


class InstrumentMaster:
    """In-memory canonical instrument registry used by data services."""

    def __init__(self, instruments: Iterable[Instrument] = ()) -> None:
        self._by_id: dict[str, Instrument] = {}
        self._by_groww: dict[str, Instrument] = {}
        self._by_symbol: dict[tuple[str, str], Instrument] = {}
        self._by_token: dict[tuple[str, str], Instrument] = {}
        for instrument in instruments:
            self.add(instrument)

    def add(self, instrument: Instrument) -> None:
        """Add an instrument, rejecting duplicate canonical identifiers."""
        if instrument.internal_id in self._by_id:
            raise ValueError(f"Duplicate internal instrument: {instrument.internal_id}")
        if instrument.groww_symbol in self._by_groww:
            raise ValueError(f"Duplicate Groww symbol: {instrument.groww_symbol}")

        symbol_key = (instrument.exchange, instrument.trading_symbol)
        token_key = (instrument.exchange, instrument.exchange_token)
        if symbol_key in self._by_symbol:
            raise ValueError(f"Duplicate exchange/trading symbol: {symbol_key}")
        if token_key in self._by_token:
            raise ValueError(f"Duplicate exchange/token: {token_key}")

        self._by_id[instrument.internal_id] = instrument
        self._by_groww[instrument.groww_symbol] = instrument
        self._by_symbol[symbol_key] = instrument
        self._by_token[token_key] = instrument

    def get(self, internal_id: str) -> Instrument:
        return self._by_id[internal_id]

    def by_groww_symbol(self, groww_symbol: str) -> Instrument:
        return self._by_groww[groww_symbol]

    def by_trading_symbol(self, exchange: str, trading_symbol: str) -> Instrument:
        return self._by_symbol[(exchange.upper(), trading_symbol.upper())]

    def by_exchange_token(self, exchange: str, exchange_token: str) -> Instrument:
        return self._by_token[(exchange.upper(), str(exchange_token))]

    def all(self) -> tuple[Instrument, ...]:
        return tuple(self._by_id.values())


def load_groww_csv(csv_text: str, *, cash_only: bool = False) -> InstrumentMaster:
    """Load Groww instrument-master CSV text into the canonical registry.

    ``cash_only=True`` is the default operational target for the first India
    phase when callers explicitly request an equity-only registry.
    """
    reader = csv.DictReader(StringIO(csv_text))
    instruments = (Instrument.from_groww_row(row) for row in reader)
    if cash_only:
        instruments = (item for item in instruments if item.segment == "CASH")
    return InstrumentMaster(instruments)


def _required(row: dict[str, str], key: str) -> str:
    value = (row.get(key) or "").strip()
    if not value:
        raise ValueError(f"Missing required instrument field: {key}")
    return value


def _optional(row: dict[str, str], key: str) -> str | None:
    value = (row.get(key) or "").strip()
    return value or None


def _int(value: str | None) -> int | None:
    value = (value or "").strip()
    return int(float(value)) if value else None


def _decimal(value: str | None) -> Decimal | None:
    value = (value or "").strip()
    return Decimal(value) if value else None


def _date(value: str | None) -> date | None:
    value = (value or "").strip()
    return date.fromisoformat(value) if value else None


def _bool(value: str | None, *, default: bool = False) -> bool:
    value = (value or "").strip().lower()
    if not value:
        return default
    return value in {"1", "true", "yes", "y"}
