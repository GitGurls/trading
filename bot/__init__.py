"""
trading_bot.bot
================
A simplified trading bot for Binance USDT-M Futures Testnet.

Modules:
    client.py          -> low-level REST API client (auth, signing, requests)
    orders.py           -> order placement / business logic layer
    validators.py       -> CLI input validation
    logging_config.py   -> centralized logging setup
"""

__version__ = "1.0.0"
