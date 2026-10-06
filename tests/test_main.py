from types import SimpleNamespace

from fastapi.testclient import TestClient
from pydantic import SecretStr

from src import main


client = TestClient(main.app)


def test_health_endpoint(monkeypatch) -> None:
    monkeypatch.setattr(
        main,
        "settings",
        SimpleNamespace(
            app_env="development",
            groww_access_token=SecretStr("test-token"),
            groww_api_key=None,
            groww_api_secret=None,
        ),
    )
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["market_data_status"] == "configured"
    assert response.json()["market_data_provider"] == "Groww Trading API"


def test_latest_market_data_endpoint() -> None:
    class FixedService:
        def latest(self, symbol, exchange, timeframe):
            from datetime import datetime, timezone
            from decimal import Decimal
            from src.market_data.models import Candle

            return Candle(
                symbol=symbol,
                exchange=exchange,
                timeframe=timeframe,
                timestamp=datetime.now(timezone.utc),
                open=Decimal("100"),
                high=Decimal("102"),
                low=Decimal("99"),
                close=Decimal("101"),
                volume=5,
                last_price=Decimal("101.5"),
            )

    main.market_data = FixedService()
    response = client.get("/api/v1/market-data/latest", params={"symbol": "RELIANCE"})
    assert response.status_code == 200
    assert response.json()["symbol"] == "RELIANCE"
    assert response.json()["timeframe"] == "live"
    assert response.json()["last_price"] == "101.5"


def test_expected_stale_error_maps_to_503(monkeypatch) -> None:
    def stale_latest(*args, **kwargs):
        raise ValueError("market-data candle is stale")

    monkeypatch.setattr(main, "market_data", SimpleNamespace(latest=stale_latest))
    response = client.get("/api/v1/market-data/latest", params={"symbol": "RELIANCE"})
    assert response.status_code == 503
    assert response.json()["detail"] == "market-data candle is stale"


def test_expected_validation_error_maps_to_422(monkeypatch) -> None:
    def invalid_latest(*args, **kwargs):
        raise ValueError("invalid candle")

    monkeypatch.setattr(main, "market_data", SimpleNamespace(latest=invalid_latest))
    response = client.get("/api/v1/market-data/latest", params={"symbol": "RELIANCE"})
    assert response.status_code == 422
    assert response.json()["detail"] == "invalid candle"


def test_expected_missing_resource_maps_to_404(monkeypatch) -> None:
    def missing_latest(*args, **kwargs):
        raise KeyError("RELIANCE")

    monkeypatch.setattr(main, "market_data", SimpleNamespace(latest=missing_latest))
    response = client.get("/api/v1/market-data/latest", params={"symbol": "RELIANCE"})
    assert response.status_code == 404
    assert response.json()["detail"] == "market-data resource not found"


def test_market_data_reports_unconfigured_without_credentials(monkeypatch) -> None:
    monkeypatch.setattr(main, "market_data", None)
    monkeypatch.setattr(
        main,
        "settings",
        SimpleNamespace(
            app_env="development",
            groww_access_token=None,
            groww_api_key=None,
            groww_api_secret=None,
        ),
    )

    response = client.get("/api/v1/market-data/latest", params={"symbol": "ABC"})

    assert response.status_code == 503
    assert response.json()["detail"] == "Groww market-data credentials are not configured."


def test_market_data_explains_groww_forbidden_access_without_leaking_provider_payload(monkeypatch) -> None:
    class GrowwForbidden(Exception):
        code = "403"

    def forbidden_latest(*args, **kwargs):
        raise GrowwForbidden("provider payload must not reach the client")

    monkeypatch.setattr(main, "market_data", SimpleNamespace(latest=forbidden_latest))

    response = client.get("/api/v1/market-data/latest", params={"symbol": "ABC"})

    assert response.status_code == 503
    assert "active Trading API subscription" in response.json()["detail"]
    assert "provider payload" not in response.text


def test_in_memory_paper_snapshot_is_read_only_and_starts_empty() -> None:
    response = client.get("/api/v1/paper/in-memory")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.json()["status"] == "available"
    assert response.json()["orders"] == []
    assert response.json()["order_count"] == 0
    assert response.json()["positions"] == []


def test_persistent_paper_snapshot_reports_unconfigured_without_a_database(monkeypatch) -> None:
    monkeypatch.setattr(
        main,
        "settings",
        SimpleNamespace(
            app_env="development",
            database_url=None,
            groww_access_token=None,
            groww_api_key=None,
            groww_api_secret=None,
        ),
    )

    response = client.get("/api/v1/paper/persistent")

    assert response.status_code == 200
    assert response.json()["status"] == "unconfigured"
    assert response.json()["orders"] == []
    assert response.json()["order_count"] is None


def test_groww_snapshot_reports_unconfigured_without_a_token(monkeypatch) -> None:
    monkeypatch.setattr(
        main,
        "settings",
        SimpleNamespace(
            app_env="development",
            database_url=None,
            groww_access_token=None,
            groww_api_key=None,
            groww_api_secret=None,
        ),
    )

    response = client.get("/api/v1/groww/account")

    assert response.status_code == 200
    assert response.json()["status"] == "unconfigured"
    assert response.json()["orders"] == []
    assert response.json()["holding_count"] is None


def test_groww_snapshot_uses_api_key_and_secret_without_returning_them(monkeypatch) -> None:
    calls = []

    class StubProvider:
        def __init__(self, access_token, *, api_key, api_secret):
            calls.append((access_token, api_key, api_secret))

        def snapshot(self):
            return {"status": "available", "orders": []}

    monkeypatch.setattr(
        main,
        "settings",
        SimpleNamespace(
            app_env="development",
            database_url=None,
            groww_access_token=None,
            groww_api_key=SecretStr("test-api-key"),
            groww_api_secret=SecretStr("test-api-secret"),
        ),
    )
    monkeypatch.setattr(main, "GrowwAccountProvider", StubProvider)

    response = client.get("/api/v1/groww/account")

    assert response.status_code == 200
    assert response.json() == {"status": "available", "orders": []}
    assert calls == [(None, "test-api-key", "test-api-secret")]
    assert "test-api-key" not in response.text
    assert "test-api-secret" not in response.text


def test_account_snapshot_routes_are_hidden_outside_development(monkeypatch) -> None:
    monkeypatch.setattr(
        main,
        "settings",
        SimpleNamespace(
            app_env="production",
            database_url=None,
            groww_access_token=None,
            groww_api_key=None,
            groww_api_secret=None,
        ),
    )

    response = client.get("/api/v1/groww/account")

    assert response.status_code == 404
    assert response.json() == {"detail": "not found"}
