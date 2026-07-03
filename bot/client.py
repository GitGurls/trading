"""
client.py
---------
Thin wrapper around the Binance USDT-M Futures Testnet REST API.

This is the ONLY module that talks to the network. Everything else in the
bot (orders.py, cli.py) goes through this client, which keeps the
API/auth/signing logic in one reusable, testable place.

Docs: https://binance-docs.github.io/apidocs/testnet/en/
Base URL (Futures Testnet): https://testnet.binancefuture.com
"""

import hashlib
import hmac
import logging
import time
from urllib.parse import urlencode

import requests

from bot.logging_config import setup_logger

logger = setup_logger(__name__)


class BinanceAPIError(Exception):
    """Raised when Binance returns a non-2xx / error-coded response."""

    def __init__(self, status_code, payload):
        self.status_code = status_code
        self.payload = payload
        super().__init__(f"Binance API error [{status_code}]: {payload}")


class BinanceNetworkError(Exception):
    """Raised for connection/timeout issues talking to Binance."""


class BinanceFuturesTestnetClient:
    """
    Minimal REST client for placing orders on Binance Futures Testnet
    (USDT-M). Handles request signing, headers, and error handling.
    """

    BASE_URL = "https://testnet.binancefuture.com"
    ORDER_ENDPOINT = "/fapi/v1/order"
    ACCOUNT_ENDPOINT = "/fapi/v2/account"

    def __init__(self, api_key: str, api_secret: str, timeout: int = 10):
        if not api_key or not api_secret:
            raise ValueError("API key and secret must be provided.")
        self.api_key = api_key
        self.api_secret = api_secret.encode()
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _sign(self, params: dict) -> str:
        query_string = urlencode(params)
        signature = hmac.new(self.api_secret, query_string.encode(), hashlib.sha256).hexdigest()
        return signature

    def _signed_request(self, method: str, path: str, params: dict = None) -> dict:
        params = dict(params or {})
        params["timestamp"] = int(time.time() * 1000)
        params["recvWindow"] = 5000
        params["signature"] = self._sign(params)

        url = f"{self.BASE_URL}{path}"
        logger.debug("REQUEST %s %s | params=%s", method, url, {k: v for k, v in params.items() if k != "signature"})

        try:
            response = self.session.request(method, url, params=params, timeout=self.timeout)
        except requests.exceptions.Timeout as exc:
            logger.error("Network timeout calling %s: %s", url, exc)
            raise BinanceNetworkError(f"Request to {url} timed out.") from exc
        except requests.exceptions.ConnectionError as exc:
            logger.error("Connection error calling %s: %s", url, exc)
            raise BinanceNetworkError(f"Could not connect to {url}.") from exc
        except requests.exceptions.RequestException as exc:
            logger.error("Unexpected request error calling %s: %s", url, exc)
            raise BinanceNetworkError(str(exc)) from exc

        logger.debug("RESPONSE status=%s body=%s", response.status_code, response.text)

        try:
            payload = response.json()
        except ValueError:
            payload = {"raw": response.text}

        if not response.ok:
            logger.error("API error status=%s payload=%s", response.status_code, payload)
            raise BinanceAPIError(response.status_code, payload)

        return payload

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: float = None,
        time_in_force: str = "GTC",
    ) -> dict:
        """
        Places a MARKET or LIMIT order on Futures Testnet.

        Returns the raw JSON response from Binance on success.
        Raises BinanceAPIError / BinanceNetworkError on failure.
        """
        params = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }

        if order_type == "LIMIT":
            params["price"] = price
            params["timeInForce"] = time_in_force

        logger.info(
            "Placing order -> symbol=%s side=%s type=%s qty=%s price=%s",
            symbol, side, order_type, quantity, price if price else "N/A",
        )

        return self._signed_request("POST", self.ORDER_ENDPOINT, params)

    def get_account_info(self) -> dict:
        """Fetch account balances/positions (useful for sanity checks)."""
        return self._signed_request("GET", self.ACCOUNT_ENDPOINT)
