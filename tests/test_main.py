from types import SimpleNamespace

from fastapi.testclient import TestClient

from src import main


client = TestClient(main.app)


def test_health_endpoint() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "environment": "development"}


def test_latest_market_data_endpoint() -> None:
    response = client.get("/api/v1/market-data/latest", params={"symbol": "RELIANCE"})
    assert response.status_code == 200
    assert response.json()["symbol"] == "RELIANCE"


def test_expected_stale_error_maps_to_503(monkeypatch) -> None:
    def stale_latest(*args, **kwargs):
        raise ValueError("market-data candle is stale")

    monkeypatch.setattr(main.market_data, "latest", stale_latest)
    response = client.get("/api/v1/market-data/latest", params={"symbol": "RELIANCE"})
    assert response.status_code == 503
    assert response.json()["detail"] == "market-data candle is stale"


def test_expected_validation_error_maps_to_422(monkeypatch) -> None:
    def invalid_latest(*args, **kwargs):
        raise ValueError("invalid candle")

    monkeypatch.setattr(main.market_data, "latest", invalid_latest)
    response = client.get("/api/v1/market-data/latest", params={"symbol": "RELIANCE"})
    assert response.status_code == 422
    assert response.json()["detail"] == "invalid candle"


def test_expected_missing_resource_maps_to_404(monkeypatch) -> None:
    def missing_latest(*args, **kwargs):
        raise KeyError("RELIANCE")

    monkeypatch.setattr(main.market_data, "latest", missing_latest)
    response = client.get("/api/v1/market-data/latest", params={"symbol": "RELIANCE"})
    assert response.status_code == 404
    assert response.json()["detail"] == "market-data resource not found"


def test_in_memory_paper_snapshot_is_read_only_and_starts_empty() -> None:
    response = client.get("/api/v1/paper/in-memory")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.json()["status"] == "available"
    assert response.json()["orders"] == []
    assert response.json()["positions"] == []


def test_persistent_paper_snapshot_reports_unconfigured_without_a_database(monkeypatch) -> None:
    monkeypatch.setattr(
        main,
        "settings",
        SimpleNamespace(app_env="development", database_url=None, groww_access_token=None),
    )

    response = client.get("/api/v1/paper/persistent")

    assert response.status_code == 200
    assert response.json()["status"] == "unconfigured"
    assert response.json()["orders"] == []


def test_groww_snapshot_reports_unconfigured_without_a_token(monkeypatch) -> None:
    monkeypatch.setattr(
        main,
        "settings",
        SimpleNamespace(app_env="development", database_url=None, groww_access_token=None),
    )

    response = client.get("/api/v1/groww/account")

    assert response.status_code == 200
    assert response.json()["status"] == "unconfigured"
    assert response.json()["orders"] == []


def test_account_snapshot_routes_are_hidden_outside_development(monkeypatch) -> None:
    monkeypatch.setattr(
        main,
        "settings",
        SimpleNamespace(app_env="production", database_url=None, groww_access_token=None),
    )

    response = client.get("/api/v1/groww/account")

    assert response.status_code == 404
    assert response.json() == {"detail": "not found"}
