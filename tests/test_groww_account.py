import sys
from types import ModuleType

from src.groww_account import GrowwAccountProvider


class FakeGrowwAccountClient:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def get_holdings_for_user(self, *, timeout):
        self.calls.append(f"holdings:{timeout}")
        return {
            "status": "SUCCESS",
            "payload": {
                "holdings": [
                    {
                        "trading_symbol": "RELIANCE",
                        "quantity": 10,
                        "average_price": 100,
                        "account_number": "must-not-be-returned",
                    }
                ]
            },
        }

    def get_positions_for_user(self, *, timeout):
        self.calls.append(f"positions:{timeout}")
        return {
            "status": "SUCCESS",
            "payload": {
                "positions": [
                    {
                        "trading_symbol": "INFY",
                        "exchange": "NSE",
                        "segment": "CASH",
                        "product": "CNC",
                        "quantity": 4,
                        "net_price": 1500,
                        "realised_pnl": 25,
                    }
                ]
            },
        }

    def get_order_list(self, *, page, timeout):
        self.calls.append(f"orders:{page}:{timeout}")
        return {
            "status": "SUCCESS",
            "payload": {
                "order_list": [
                    {
                        "trading_symbol": "TCS",
                        "transaction_type": "BUY",
                        "order_status": "OPEN",
                        "quantity": 2,
                        "filled_quantity": 0,
                    }
                ]
            },
        }

    def place_order(self, **kwargs):
        raise AssertionError("Groww dashboard provider must never place orders")


def test_groww_snapshot_uses_read_methods_and_allow_lists_account_fields() -> None:
    client = FakeGrowwAccountClient()
    snapshot = GrowwAccountProvider("not-a-real-token", client=client).snapshot()

    assert client.calls == ["holdings:5", "positions:5", "orders:0:5"]
    assert snapshot["holding_count"] == 1
    assert snapshot["position_count"] == 1
    assert snapshot["order_count"] == 1
    assert snapshot["holdings"] == [
        {"trading_symbol": "RELIANCE", "quantity": 10, "average_price": 100}
    ]
    assert "account_number" not in str(snapshot)
    assert "not-a-real-token" not in str(snapshot)


def test_groww_account_provider_exchanges_api_key_and_secret_for_access_token(monkeypatch) -> None:
    calls = []

    class FakeGrowwAPI:
        @staticmethod
        def get_access_token(*, api_key, secret):
            calls.append((api_key, secret))
            return "generated-access-token"

        def __init__(self, access_token):
            self.access_token = access_token

    fake_module = ModuleType("growwapi")
    fake_module.GrowwAPI = FakeGrowwAPI
    monkeypatch.setitem(sys.modules, "growwapi", fake_module)

    provider = GrowwAccountProvider(api_key="test-api-key", api_secret="test-api-secret")

    assert calls == [("test-api-key", "test-api-secret")]
    assert provider._client.access_token == "generated-access-token"
