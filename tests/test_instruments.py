from decimal import Decimal

import pytest

from src.market_data.instruments import Instrument, InstrumentMaster, load_groww_csv


CSV = """exchange,exchange_token,trading_symbol,groww_symbol,name,instrument_type,segment,series,isin,underlying_symbol,underlying_exchange_token,expiry_date,strike_price,lot_size,tick_size,freeze_quantity,is_reserved,buy_allowed,sell_allowed
NSE,2885,RELIANCE,NSE-RELIANCE,Reliance Industries,EQ,CASH,EQ,INE002A01018,,,,,1,0.05,100000,1,1,1
BSE,500325,RELIANCE,BSE-RELIANCE,Reliance Industries,EQ,CASH,A,INE002A01018,,,,,1,0.05,100000,1,1,1
NSE,35241,NIFTY25DEC27000PE,NSE-NIFTY-24Dec25-27000-PE,,PE,FNO,,,NIFTY,26009,2025-12-24,27000,65,0.05,601,1,1,1
"""


def test_load_cash_instruments_and_lookup() -> None:
    master = load_groww_csv(CSV, cash_only=True)

    reliance = master.by_trading_symbol("nse", "reliance")

    assert reliance.internal_id == "NSE:CASH:RELIANCE"
    assert reliance.groww_symbol == "NSE-RELIANCE"
    assert reliance.exchange_token == "2885"
    assert reliance.isin == "INE002A01018"
    assert reliance.tick_size == Decimal("0.05")
    assert len(master.all()) == 2


def test_lookup_by_groww_symbol_and_token() -> None:
    master = load_groww_csv(CSV)

    assert master.by_groww_symbol("NSE-RELIANCE").trading_symbol == "RELIANCE"
    assert master.by_exchange_token("NSE", "2885").groww_symbol == "NSE-RELIANCE"
    assert master.by_exchange_token("NSE", 2885).groww_symbol == "NSE-RELIANCE"


def test_duplicate_instrument_is_rejected() -> None:
    instrument = Instrument(
        internal_id="NSE:CASH:RELIANCE",
        exchange="NSE",
        exchange_token="2885",
        trading_symbol="RELIANCE",
        groww_symbol="NSE-RELIANCE",
        instrument_type="EQ",
        segment="CASH",
    )

    master = InstrumentMaster([instrument])

    with pytest.raises(ValueError, match="Duplicate internal instrument"):
        master.add(instrument)


def test_missing_required_field_is_rejected() -> None:
    with pytest.raises(ValueError, match="trading_symbol"):
        Instrument.from_groww_row(
            {
                "exchange": "NSE",
                "exchange_token": "2885",
                "groww_symbol": "NSE-RELIANCE",
                "instrument_type": "EQ",
                "segment": "CASH",
            }
        )
