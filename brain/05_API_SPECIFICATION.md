# API Specification
**Version:** 0.2 | **Status:** Active Draft

## Internal API
REST/JSON control APIs use `/api/v1`. Real-time internal updates may use WebSockets/events. Use UUIDs and correlation IDs.

GET /api/v1/health
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
Groww currently exposes REST endpoints under `https://api.groww.in/v1/...` and a Python SDK. Authentication uses a runtime access token. The exact endpoint schemas must be implemented behind the adapter and must not leak into the core domain model.

Groww order fields include trading symbol, quantity, price, trigger price, validity, exchange, segment, product, order type, transaction type and an optional order reference ID. The adapter must generate and persist an internal correlation ID and provider reference separately.

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

Final broker schemas must always be reconciled with current official Groww documentation before implementation or production deployment.
