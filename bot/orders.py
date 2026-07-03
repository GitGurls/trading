"""
orders.py
---------
Business-logic layer sitting between the CLI and the API client.

Responsible for:
  - validating input (via validators.py)
  - calling the client
  - formatting request/response summaries for the user
  - translating low-level exceptions into a consistent result object
"""

from dataclasses import dataclass
from typing import Optional

from bot.client import BinanceAPIError, BinanceFuturesTestnetClient, BinanceNetworkError
from bot.logging_config import setup_logger
from bot.validators import validate_order_params

logger = setup_logger(__name__)


@dataclass
class OrderResult:
    success: bool
    message: str
    raw_response: Optional[dict] = None


class OrderService:
    """High-level order operations used by the CLI layer."""

    def __init__(self, client: BinanceFuturesTestnetClient):
        self.client = client

    def place_order(self, symbol, side, order_type, quantity, price=None) -> OrderResult:
        # 1. Validate & normalize input
        try:
            clean = validate_order_params(symbol, side, order_type, quantity, price)
        except ValueError as exc:
            logger.warning("Validation failed: %s", exc)
            return OrderResult(success=False, message=f"Invalid input: {exc}")

        # 2. Print/log a clear request summary before sending
        summary = self._format_request_summary(clean)
        logger.info("Order request summary:\n%s", summary)
        print("\n--- ORDER REQUEST SUMMARY ---")
        print(summary)

        # 3. Call the API
        try:
            response = self.client.place_order(
                symbol=clean["symbol"],
                side=clean["side"],
                order_type=clean["order_type"],
                quantity=clean["quantity"],
                price=clean["price"],
            )
        except BinanceAPIError as exc:
            logger.error("Order failed (API error): %s", exc)
            return OrderResult(
                success=False,
                message=f"Order REJECTED by Binance. Status={exc.status_code}, Detail={exc.payload}",
            )
        except BinanceNetworkError as exc:
            logger.error("Order failed (network error): %s", exc)
            return OrderResult(success=False, message=f"Network error while placing order: {exc}")
        except Exception as exc:  # noqa: BLE001 - final safety net, always log unexpected errors
            logger.exception("Unexpected error while placing order")
            return OrderResult(success=False, message=f"Unexpected error: {exc}")

        # 4. Format response summary
        response_summary = self._format_response_summary(response)
        logger.info("Order response summary:\n%s", response_summary)
        print("\n--- ORDER RESPONSE ---")
        print(response_summary)

        return OrderResult(success=True, message="Order placed successfully.", raw_response=response)

    @staticmethod
    def _format_request_summary(clean: dict) -> str:
        lines = [
            f"Symbol   : {clean['symbol']}",
            f"Side     : {clean['side']}",
            f"Type     : {clean['order_type']}",
            f"Quantity : {clean['quantity']}",
        ]
        if clean["order_type"] == "LIMIT":
            lines.append(f"Price    : {clean['price']}")
        return "\n".join(lines)

    @staticmethod
    def _format_response_summary(response: dict) -> str:
        order_id = response.get("orderId", "N/A")
        status = response.get("status", "N/A")
        executed_qty = response.get("executedQty", "N/A")
        avg_price = response.get("avgPrice", "N/A")
        return (
            f"Order ID     : {order_id}\n"
            f"Status       : {status}\n"
            f"Executed Qty : {executed_qty}\n"
            f"Avg Price    : {avg_price}"
        )
