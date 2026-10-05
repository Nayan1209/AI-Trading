from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse

from .market_data.providers import MockMarketDataProvider
from .market_data.service import MarketDataService

app = FastAPI(title="AI Trading System", version="0.1.0")
market_data = MarketDataService(MockMarketDataProvider())
DASHBOARD_FILE = Path(__file__).parent / "static" / "dashboard.html"


@app.exception_handler(KeyError)
async def key_error_handler(request: Request, exc: KeyError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": "market-data resource not found"})


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    message = str(exc)
    status_code = 503 if "stale" in message.lower() else 422
    return JSONResponse(status_code=status_code, content={"detail": message})


@app.exception_handler(RuntimeError)
async def runtime_error_handler(request: Request, exc: RuntimeError) -> JSONResponse:
    return JSONResponse(status_code=503, content={"detail": "market-data service unavailable"})


@app.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    """Serve the read-only development command center."""
    return FileResponse(
        DASHBOARD_FILE,
        media_type="text/html",
        headers={"Cache-Control": "no-store"},
    )


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok", "environment": "development"}


@app.get("/api/v1/market-data/latest")
def latest_market_data(
    symbol: str, exchange: str = "NSE", timeframe: str = "15m"
):
    return market_data.latest(symbol, exchange, timeframe).model_dump(mode="json")
