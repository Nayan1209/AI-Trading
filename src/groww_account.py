"""Read-only Groww account snapshots for the local dashboard."""

from collections.abc import Mapping
from datetime import date, datetime, timezone
import math
from typing import Any


class GrowwAccountProvider:
    """Read holdings, positions, and the current-day order page from Groww."""

    def __init__(
        self,
        access_token: str | None = None,
        client: Any | None = None,
        *,
        api_key: str | None = None,
        api_secret: str | None = None,
    ) -> None:
        if access_token is not None and not access_token.strip():
            access_token = None
        if access_token is None and not (api_key and api_secret):
            raise ValueError("Groww access token or API key and secret are required")
        if client is not None:
            self._client = client
            return

        try:
            from growwapi import GrowwAPI
        except ImportError as exc:  # pragma: no cover - dependency/environment guard
            raise RuntimeError("growwapi is not installed") from exc

        if access_token is None:
            access_token = GrowwAPI.get_access_token(api_key=api_key, secret=api_secret)
            if isinstance(access_token, Mapping):
                access_token = access_token.get("token")
            if not isinstance(access_token, str) or not access_token.strip():
                raise RuntimeError("Groww did not return an access token")

        self._client = GrowwAPI(access_token)

    def snapshot(self) -> dict[str, object]:
        """Fetch read-only account data and return an allow-listed projection."""
        holdings = _rows(self._client.get_holdings_for_user(timeout=5), "holdings")
        positions = _rows(self._client.get_positions_for_user(timeout=5), "positions")
        # The installed SDK defaults this read endpoint to 25 rows per page.
        orders = _rows(
            self._client.get_order_list(page=0, timeout=5),
            "order_list",
        )

        return {
            "status": "available",
            "source": "Groww read-only API",
            "detail": "Holdings and positions are account snapshots; orders are the first current-day page.",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "holding_count": len(holdings),
            "position_count": len(positions),
            "order_count": len(orders),
            "holdings": [
                _allow_fields(row, ("trading_symbol", "quantity", "average_price"))
                for row in holdings
            ],
            "positions": [
                _allow_fields(
                    row,
                    (
                        "trading_symbol",
                        "exchange",
                        "segment",
                        "product",
                        "quantity",
                        "net_price",
                        "realised_pnl",
                    ),
                )
                for row in positions
            ],
            "orders": [
                _allow_fields(
                    row,
                    (
                        "trading_symbol",
                        "exchange",
                        "segment",
                        "order_status",
                        "transaction_type",
                        "quantity",
                        "filled_quantity",
                        "average_fill_price",
                        "created_at",
                    ),
                )
                for row in orders
            ],
        }


def _rows(response: object, key: str) -> list[Mapping[str, Any]]:
    if not isinstance(response, Mapping):
        raise ValueError("Groww returned an unexpected response")
    payload = response.get("payload", response)
    if not isinstance(payload, Mapping):
        raise ValueError("Groww returned an unexpected response")
    rows = payload.get(key)
    if not isinstance(rows, list) or any(not isinstance(row, Mapping) for row in rows):
        raise ValueError("Groww returned an unexpected response")
    return rows


def _allow_fields(row: Mapping[str, Any], fields: tuple[str, ...]) -> dict[str, object]:
    return {field: _safe_value(row.get(field)) for field in fields}


def _safe_value(value: object) -> object:
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)
