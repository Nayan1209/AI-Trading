# API Specification
**Version:** 0.3 | **Status:** Active Draft

## Internal API
REST/JSON control APIs use `/api/v1`. Real-time internal updates may use WebSockets/events. Use UUIDs and correlation IDs.

GET /api/v1/health
GET /api/v1/paper/in-memory
GET /api/v1/paper/persistent
GET /api/v1/groww/account
GET /api/v1/instruments
GET /api/v1/signals
POST /api/v1/analysis
POST /api/v1/trade-plans
POST /api/v1/risk/check
POST /api/v1/orders
GET /api/v1/orders/{id}
POST /api/v1/orders/{id}/cancel
GET /api/v1/positions
GET /api/v1/system/status
POST /api/v1/system/trading-halt

## Dashboard

`GET /` serves the read-only development dashboard as HTML. It uses health, latest market data, and read-only paper/account snapshot routes; it does not create or expose trading actions.

The paper and Groww account snapshot routes are development-only, accept loopback clients only, and return `Cache-Control: no-store`. `GET /api/v1/paper/in-memory` projects the current process's immutable paper fills into positions and pre-fee realized P&L. `GET /api/v1/paper/persistent` reads the optional PostgreSQL `paper_orders` journal and reconstructs positions from its fills. Unrealized P&L remains unavailable until current price marks are attached.

`GET /api/v1/groww/account` calls only Groww's read methods for holdings, positions, and the current-day order page. It returns an allow-listed subset of account fields and never returns the access token. Configure `GROWW_ACCESS_TOKEN` locally. No order placement, modification, or cancellation method is exposed.

The method names and returned fields follow Groww's official [Python SDK portfolio guide](https://groww.in/trade-api/docs/python-sdk/portfolio) and [orders guide](https://groww.in/trade-api/docs/python-sdk/orders).

## Broker Adapter Contract
The internal execution layer must not expose Groww-specific request objects to strategy or AI services.

Required adapter capabilities:
- authenticate / refresh runtime session
- get instruments
- get live quote / LTP / OHLC
- subscribe/unsubscribe live feed
- get historical candles
- get positions / holdings / margin where supported
- place order
- modify order
- cancel order
- get order status/detail/list
- get trades for order
- reconcile broker state

## Groww Mapping Notes
Groww's current Python SDK is installed as `growwapi` and initializes with a runtime access token. The documented SDK methods used by the first read-only milestone are:

- `GrowwAPI(access_token)` — client initialization
- `get_quote(exchange, segment, trading_symbol)` — complete live quote snapshot
- `get_ltp(segment, exchange_trading_symbols)` — batched LTP, up to 50 instruments per call
- `get_ohlc(segment, exchange_trading_symbols)` — current-time OHLC snapshot, up to 50 instruments per call
- `GrowwFeed` — streaming market data; exchange tokens come from the Groww instrument master

The adapter must translate provider responses into internal domain objects. Groww-specific constants, payloads and exceptions must not leak into strategy, signal, AI, risk or UI layers.

**Important distinction:** Groww's `get_ohlc` is a real-time/current-day snapshot, not an interval candle. Interval candles must use the historical-data adapter. This prevents the system from accidentally treating daily snapshots as 1-minute/5-minute candles.

## Market Data Contract
Internal normalized market-data event:

```json
{
  "instrument_id": "internal-id",
  "exchange": "NSE",
  "segment": "CASH",
  "symbol": "RELIANCE",
  "timestamp": "ISO-8601",
  "ltp": 0.0,
  "open": 0.0,
  "high": 0.0,
  "low": 0.0,
  "close": 0.0,
  "volume": 0,
  "source": "groww",
  "is_stale": false
}
```

Fields unavailable from a specific provider are nullable rather than fabricated.

## Current Implementation Boundary
`src/market_data/groww_provider.py` is **read-only**. It converts Groww `get_quote` output into the project's `Candle` model for the initial connectivity milestone. It does not import or expose order-placement methods.

The current normalized `Candle` uses `timeframe="1d_snapshot"` for this Groww quote path. This label is deliberate: it must not be interpreted as an interval candle.

The application entry point currently implements health and latest-market-data APIs only; portfolio, order, AI, risk, and broker status APIs are not wired in.

## Example Risk Request
```json
{
  "symbol":"RELIANCE",
  "side":"BUY",
  "entry":1450,
  "stop_loss":1420,
  "target":1510,
  "quantity":100
}
```

## Example Error
```json
{
  "error":{"code":"RISK_LIMIT_EXCEEDED","message":"Trade rejected"},
  "correlation_id":"uuid"
}
```

## Safety
No API route may directly bypass the Risk Engine. Broker execution is unavailable in development unless an explicit environment and safety gate permits it.

No credential value, access token, API secret or TOTP is stored in source control. Real credentials must be supplied through a secure runtime secret mechanism.

Final broker schemas must always be reconciled with current official Groww documentation before implementation or production deployment.
