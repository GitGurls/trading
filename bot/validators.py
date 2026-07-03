"""
validators.py
--------------
Input validation for CLI-supplied order parameters.

Raising ValueError here (rather than letting bad input reach the API)
gives fast, clear feedback and avoids wasting API calls on requests
that are guaranteed to fail.
"""

import re

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}

# Basic pattern: 4-20 uppercase letters/digits, e.g. BTCUSDT, ETHUSDT
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{4,20}$")


def validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not SYMBOL_PATTERN.match(symbol):
        raise ValueError(
            f"Invalid symbol '{symbol}'. Expected format like 'BTCUSDT' "
            f"(uppercase letters/digits, 4-20 chars)."
        )
    return symbol


def validate_side(side: str) -> str:
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValueError(f"Invalid side '{side}'. Must be one of {sorted(VALID_SIDES)}.")
    return side


def validate_order_type(order_type: str) -> str:
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Invalid order type '{order_type}'. Must be one of {sorted(VALID_ORDER_TYPES)}."
        )
    return order_type


def validate_quantity(quantity) -> float:
    try:
        qty = float(quantity)
    except (TypeError, ValueError):
        raise ValueError(f"Quantity must be a number, got '{quantity}'.")
    if qty <= 0:
        raise ValueError(f"Quantity must be greater than 0, got {qty}.")
    return qty


def validate_price(price, order_type: str):
    """
    Price is required for LIMIT orders and must be > 0.
    Ignored (returns None) for MARKET orders even if supplied.
    """
    if order_type == "MARKET":
        return None

    if price is None:
        raise ValueError("Price is required for LIMIT orders.")
    try:
        price_val = float(price)
    except (TypeError, ValueError):
        raise ValueError(f"Price must be a number, got '{price}'.")
    if price_val <= 0:
        raise ValueError(f"Price must be greater than 0, got {price_val}.")
    return price_val


def validate_order_params(symbol, side, order_type, quantity, price=None):
    """
    Runs all validators together and returns a clean, normalized dict.
    Raises ValueError with a descriptive message on the first failure.
    """
    clean_symbol = validate_symbol(symbol)
    clean_side = validate_side(side)
    clean_type = validate_order_type(order_type)
    clean_qty = validate_quantity(quantity)
    clean_price = validate_price(price, clean_type)

    return {
        "symbol": clean_symbol,
        "side": clean_side,
        "order_type": clean_type,
        "quantity": clean_qty,
        "price": clean_price,
    }
