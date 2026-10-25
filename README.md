



## How to Run



### Example Output
```
--- ORDER REQUEST SUMMARY ---
Symbol   : BTCUSDT
Side     : BUY
Type     : MARKET
Quantity : 0.01

--- ORDER RESPONSE ---
Order ID     : 3457891234
Status       : FILLED
Executed Qty : 0.01
Avg Price    : 64821.50

--- RESULT ---
SUCCESS: Order placed successfully.
```

On failure (e.g. insufficient testnet balance, bad symbol, network issue),
the CLI prints a clear `FAILED: ...` message and the full error detail
is written to `logs/trading_bot.log`.

## Logging

Every run appends to `logs/trading_bot.log`:
- Every outgoing API request (endpoint + params, signature excluded)
- Every raw API response
- Any validation errors, API errors (rejected orders), or network errors

The log file rotates automatically at 2MB (keeps 3 backups) so it never
grows unbounded. Console output stays concise (INFO level); the file
captures full DEBUG-level detail for auditing.

## Design Notes / Assumptions

- **REST calls over `python-binance`**: implemented with `requests` +
  manual HMAC-SHA256 signing directly against the documented Testnet
  REST endpoints. This keeps the dependency footprint minimal and makes
  the request/response/signing flow fully transparent for review.
- **Layered structure**: `client.py` is the only module that touches the
  network. `orders.py` handles business logic (validate → call → format).
  `cli.py` is a thin argument-parsing layer. This separation makes each
  piece independently testable and reusable (e.g. `OrderService` could be
  reused by a future web UI without touching the CLI code).
- **Validation happens before any network call** (`validators.py`), so
  bad input (invalid symbol format, non-numeric quantity, missing price
  for LIMIT orders, invalid side/type) fails fast with a clear message
  instead of wasting an API round-trip.
- Default `timeInForce` for LIMIT orders is `GTC` (Good-Till-Cancelled).
- `quantity`/`price` precision (lot size / tick size) is **not**
  auto-rounded to each symbol's exchange filters — the user is expected
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
