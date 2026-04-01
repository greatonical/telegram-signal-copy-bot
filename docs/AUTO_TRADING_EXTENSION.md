# Binary Options Auto-Trading Extension

## Overview
The Auto-Trading Extension is a modular addition to the Telegram Signal Copy Bot. While the core bot forwards messages between Telegram groups and channels, this extension specifically listens for trading signals (e.g., from "Gilly Options Signals"), parses them, validates them against your risk management rules, and automatically executes the trades on IQ Option.

Crucially, this system runs in a non-blocking asynchronous manner alongside the Telegram message loops. It is entirely decoupled, ensuring that the primary message forwarding speed is unaffected.

## Architecture & How It Works

The extension is isolated within the `auto_trader/` directory and consists of five main components:

### 1. Engine (`auto_trader/engine.py`)
This is the master orchestrator. When a new message arrives from a designated signal group (defined in `.env` via `AUTO_TRADE_SOURCES`), the message text is passed to the `AutoTraderEngine`. It pipelines the string through the Parser, Validator, Executor, and Tracker.

### 2. Signal Parser (`auto_trader/parser.py`)
Uses Regular Expressions (Regex) to structure unstructured text like `"Asset: EUR/USD\nDirection: PUT\nExpiry: 5 minutes"` or `"EURUSD - 5m - CALL"`. 
It extracts:
- **Asset**: The trading pair (e.g., `EURUSD`, `EURUSD-OTC`).
- **Direction**: `CALL` (buy/up) or `PUT` (sell/down).
- **Expiry**: The option duration in minutes (e.g., `5`).

### 3. Validator (`auto_trader/validator.py`)
Acts as the risk management layer. Before any trade touches the broker API, the validator checks:
- **Duplicate Signals**: Is this the exact same asset we just traded seconds ago? If yes, it drops the signal to prevent double-entry scaling errors.
- **Daily Loss Limit**: Ensures that running trades haven't breached the `MAX_DAILY_LOSS` configuration threshold.

### 4. Trade Executor (`auto_trader/executor.py`)
Wraps the `api-iqoption-faria` library. It initializes the connection to IQ Option securely. 
- It actively checks the `USE_PRACTICE_ACCOUNT` setting. If `true`, it switches the API to trade entirely with dummy funds (PRACTICE balance). 
- It maps the requested trade amount (`TRADE_AMOUNT`) and submits the binary options contract to the broker synchronously. 

### 5. Result Tracker (`auto_trader/tracker.py`)
Logs the lifetime execution sequence of the signal directly to a locally managed `trades.csv` file. It records timestamps, the parsed variables, the final action (`EXECUTED`, `VALIDATION_FAILED`, `EXECUTION_FAILED`, `INVALID_FORMAT`), and the unique trade ID returned by IQ Option.

---

## Integration with the Main Bot (`bot.py`)

The extension is stitched into the Telegram event loop inside `bot.py` via an asynchronous fire-and-forget task. 

Inside the `handle_new_message` function (which listens to all incoming Telegram messages), we simply added:
```python
# Auto-Trading Integration branch (non-blocking)
if source_id in AUTO_TRADE_SOURCES:
    text_to_process = message.message or ""
    if text_to_process:
        asyncio.create_task(auto_trader_engine.process_signal(text_to_process))
```

By wrapping `process_signal` in `asyncio.create_task()`, the Telegram bot immediately returns to copying and forwarding incoming messages to your other channels. It does not wait for the IQ Option tradeoff to complete, making it highly scalable and responsive.

---

## Configuration Variables

You must supply these in your active `.env` file to empower the engine.

| Variable | Description |
|-----------|------------|
| `IQ_OPTION_EMAIL` | Your registered IQ Option email address |
| `IQ_OPTION_PASSWORD`| Your registered IQ Option password |
| `TRADE_AMOUNT` | Dollar amount to commit per individual trade (e.g., `1.0`) |
| `MAX_DAILY_LOSS` | Monetary limit to halt trades locally (e.g., `10.0`) |
| `AUTO_TRADE_SOURCES` | Comma-separated target Chat IDs to listen for signals (e.g., `-1003108945324`) |
| `USE_PRACTICE_ACCOUNT`| `true` or `false` to switch between REAL and PRACTICE trading funds |

---

## How to Test

### 1. Unit Testing (No API calls)
You can test the parsing and validation logic in isolation without risking real API calls or connections. We wrote unit tests powered by standard Python `unittest` library.

Run this terminal command from the root of the project:
```bash
venv/bin/python -m unittest discover tests/
```
You should see output similar to `Ran 9 tests in 0.000s OK`, confirming the logic handles edge cases correctly.

### 2. Live Testing (Practice Account)
To test the bot securely using Telegram:

1. Ensure `.env` is populated with your IQ Option credentials and `USE_PRACTICE_ACCOUNT=true`.
2. Add a test Telegram group/channel ID you control to `AUTO_TRADE_SOURCES`. Make sure to include the negative sign if applicable (e.g., `-1003108945324`).
3. Start the bot: `python bot.py` (ensure you activate your virtual environment).
4. In your Telegram test group, send a message formatted like a signal, for example: `EURUSD - 5m - CALL`.
5. Check your console. You should see logs confirming parsing, validation, and a successful trade ID from IQ Option.
6. Check `trades.csv` in your root directory. The trade result is automatically saved.
7. Open your IQ Option dashboard (Practice Balance) and verify the 5-minute position is currently open for EURUSD!
