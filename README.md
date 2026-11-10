








  
  to pass values valid for the chosen symbol (e.g. BTCUSDT commonly
  accepts 0.001 quantity steps). This was a deliberate scope cut to keep
  the task within the ~60 minute estimate; `exchangeInfo` lookups would
  be the natural next addition.
- Base URL is hardcoded to the Futures Testnet
  (`https://testnet.binancefuture.com`) per the task spec — this bot is
  **not** wired to mainnet.

## Possible Extensions (not implemented)

- Stop-Limit / OCO / TWAP order types (bonus)
- Exchange-info-based quantity/price precision auto-rounding
- Interactive (menu-driven) CLI mode using `Typer`/`Click` with prompts
- Unit tests with a mocked `requests.Session`
