from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
import psycopg

from .core.config import settings
from .dashboard_sources import paper_snapshot
from .groww_account import GrowwAccountProvider
from .market_data.groww_provider import GrowwMarketDataProvider
from .market_data.service import MarketDataService
from .paper_execution_session import PaperExecutionSession

app = FastAPI(title="AI Trading System", version="0.1.0")
market_data: MarketDataService | None = None
paper_session = PaperExecutionSession()
DASHBOARD_FILE = Path(__file__).parent / "static" / "dashboard.html"
LOCAL_CLIENTS = {"127.0.0.1", "::1", "testclient"}
PRIVATE_DATA_PATHS = {
    "/api/v1/paper/in-memory",
    "/api/v1/paper/persistent",
    "/api/v1/groww/account",
    "/api/v1/market-data/latest",
}


@app.middleware("http")
async def disable_private_data_caching(request: Request, call_next):
    response = await call_next(request)
    if request.url.path in PRIVATE_DATA_PATHS:
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
    return response


def _require_local_development(request: Request) -> None:
    """Keep unauthenticated account snapshots local to a development server."""
    client_host = request.client.host if request.client is not None else None
    if settings.app_env.lower() != "development" or client_host not in LOCAL_CLIENTS:
        raise HTTPException(status_code=404, detail="not found")


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
    token, api_key, api_secret = _groww_credentials()
    configured = bool(token or (api_key and api_secret))
    return {
        "status": "ok",
        "environment": settings.app_env,
        "market_data_provider": "Groww Trading API" if configured else "Not configured",
        "market_data_status": "configured" if configured else "unconfigured",
    }


def _groww_credentials() -> tuple[str, str, str]:
    token = (
        settings.groww_access_token.get_secret_value().strip()
        if settings.groww_access_token is not None
        else ""
    )
    api_key = (
        settings.groww_api_key.get_secret_value().strip()
        if settings.groww_api_key is not None
        else ""
    )
    api_secret = (
        settings.groww_api_secret.get_secret_value().strip()
        if settings.groww_api_secret is not None
        else ""
    )
    return token, api_key, api_secret


def _get_market_data_service() -> MarketDataService:
    global market_data
    if market_data is not None:
        return market_data

    token, api_key, api_secret = _groww_credentials()
    if not token and not (api_key and api_secret):
        raise HTTPException(
            status_code=503,
            detail="Groww market-data credentials are not configured.",
        )
    try:
        provider = GrowwMarketDataProvider(
            token or None,
            api_key=api_key or None,
            api_secret=api_secret or None,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Groww market-data provider could not be initialized.",
        ) from exc
    market_data = MarketDataService(provider)
    return market_data


@app.get("/api/v1/market-data/latest")
def latest_market_data(
    symbol: str, exchange: str = "NSE", timeframe: str = "live"
):
    try:
        return _get_market_data_service().latest(symbol, exchange, timeframe).model_dump(mode="json")
    except HTTPException:
        raise
    except (KeyError, ValueError):
        raise
    except Exception as exc:
        if str(getattr(exc, "code", "")) == "403":
            raise HTTPException(
                status_code=503,
                detail="Groww denied live quote access (HTTP 403). Check the active Trading API subscription and live market-data permissions for this account.",
            ) from exc
        raise HTTPException(
            status_code=503,
            detail="Groww market data could not be retrieved. Check credentials, instrument symbol, and market-data API access.",
        ) from exc


@app.get("/api/v1/paper/in-memory")
def in_memory_paper_state(request: Request) -> dict[str, object]:
    """Return this process's paper fills and positions without changing them."""
    _require_local_development(request)
    return paper_snapshot(
        paper_session.ledger.snapshot(),
        source="In-memory paper ledger",
        detail="Session-only fills; price-difference realized P&L excludes fees, and session data resets when the app restarts.",
    )


@app.get("/api/v1/paper/persistent")
def persistent_paper_state(request: Request) -> dict[str, object]:
    """Read the append-only PostgreSQL paper-order journal when configured."""
    _require_local_development(request)
    if settings.database_url is None or not settings.database_url.get_secret_value().strip():
        return {
            "status": "unconfigured",
            "source": "PostgreSQL paper journal",
            "detail": "Set DATABASE_URL locally and apply migration 003 to connect paper history.",
            "order_count": None,
            "position_count": None,
            "realized_pnl": None,
            "unrealized_pnl": None,
            "positions": [],
            "orders": [],
        }

    try:
        connection = psycopg.connect(
            settings.database_url.get_secret_value(),
            connect_timeout=3,
        )
        try:
            from .storage.postgres_paper_orders import PostgresPaperOrderJournal

            orders = PostgresPaperOrderJournal(connection).snapshot()
        finally:
            connection.close()
    except Exception:
        return {
            "status": "unavailable",
            "source": "PostgreSQL paper journal",
            "detail": "Could not read the database or paper_orders table; check the connection and migration 003.",
            "order_count": None,
            "position_count": None,
            "realized_pnl": None,
            "unrealized_pnl": None,
            "positions": [],
            "orders": [],
        }

    return paper_snapshot(
        orders,
        source="PostgreSQL paper journal",
        detail="Positions and pre-fee realized P&L are reconstructed from immutable fills; unrealized P&L needs current price marks.",
    )


@app.get("/api/v1/groww/account")
def groww_account_state(request: Request) -> dict[str, object]:
    """Read Groww holdings, positions, and current-day orders when configured."""
    _require_local_development(request)
    token, api_key, api_secret = _groww_credentials()
    if not token and not (api_key and api_secret):
        return {
            "status": "unconfigured",
            "source": "Groww read-only API",
            "detail": "Set GROWW_ACCESS_TOKEN or both GROWW_API_KEY and GROWW_API_SECRET locally; credentials are never returned by this API.",
            "holding_count": None,
            "position_count": None,
            "order_count": None,
            "holdings": [],
            "positions": [],
            "orders": [],
        }

    try:
        return GrowwAccountProvider(
            token or None,
            api_key=api_key or None,
            api_secret=api_secret or None,
        ).snapshot()
    except Exception:
        return {
            "status": "unavailable",
            "source": "Groww read-only API",
            "detail": "Groww data could not be read; check local credentials, daily API-key approval, network, and account API access.",
            "holding_count": None,
            "position_count": None,
            "order_count": None,
            "holdings": [],
            "positions": [],
            "orders": [],
        }
