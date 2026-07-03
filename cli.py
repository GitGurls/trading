#!/usr/bin/env python3
"""
cli.py
------
Command-line entry point for the Simplified Trading Bot
(Binance USDT-M Futures Testnet).

Usage examples
--------------
Market order:
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01

Limit order:
    python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 65000

API credentials are read from environment variables (see README.md):
    BINANCE_API_KEY
    BINANCE_API_SECRET
Or passed explicitly with --api-key / --api-secret.
"""

import argparse
import os
import sys

from bot.client import BinanceFuturesTestnetClient
from bot.logging_config import setup_logger
from bot.orders import OrderService

logger = setup_logger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading-bot",
        description="Place MARKET or LIMIT orders on Binance Futures Testnet (USDT-M).",
    )
    parser.add_argument("--symbol", required=True, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side", required=True, choices=["BUY", "SELL", "buy", "sell"], help="Order side")
    parser.add_argument(
        "--type", dest="order_type", required=True,
        choices=["MARKET", "LIMIT", "market", "limit"], help="Order type",
    )
    parser.add_argument("--quantity", required=True, help="Order quantity")
    parser.add_argument("--price", required=False, default=None, help="Price (required for LIMIT orders)")
    parser.add_argument("--api-key", required=False, default=os.getenv("BINANCE_API_KEY"),
                         help="Binance Testnet API key (or set BINANCE_API_KEY env var)")
    parser.add_argument("--api-secret", required=False, default=os.getenv("BINANCE_API_SECRET"),
                         help="Binance Testnet API secret (or set BINANCE_API_SECRET env var)")
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.api_key or not args.api_secret:
        print(
            "ERROR: Missing API credentials. Set BINANCE_API_KEY / BINANCE_API_SECRET "
            "environment variables, or pass --api-key / --api-secret.",
            file=sys.stderr,
        )
        logger.error("Startup failed: missing API credentials.")
        return 1

    try:
        client = BinanceFuturesTestnetClient(api_key=args.api_key, api_secret=args.api_secret)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    service = OrderService(client)
    result = service.place_order(
        symbol=args.symbol,
        side=args.side,
        order_type=args.order_type,
        quantity=args.quantity,
        price=args.price,
    )

    print("\n--- RESULT ---")
    if result.success:
        print(f"SUCCESS: {result.message}")
        return 0
    else:
        print(f"FAILED: {result.message}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
