# API Specification
**Version:** 0.1 | **Status:** Draft

REST/JSON control APIs use /api/v1. Real-time updates may use WebSockets/events. Use UUIDs and correlation IDs.

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

Example risk request:
{
  "symbol":"RELIANCE","side":"BUY","entry":1450,"stop_loss":1420,"target":1510,"quantity":100
}

Example error:
{
  "error":{"code":"RISK_LIMIT_EXCEEDED","message":"Trade rejected"},
  "correlation_id":"uuid"
}

Final broker schemas must be reconciled with current official broker documentation before implementation.
