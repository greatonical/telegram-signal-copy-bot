import logging
from auto_trader.executor import TradeExecutor
from config import USE_PRACTICE_ACCOUNT, IQ_OPTION_EMAIL

# Set up simple logging to see what's happening
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def test_connection():
    print("========================================")
    print("   IQ Option Connection & Trade Test    ")
    print("========================================")

    # Check if credentials exist at all
    if not IQ_OPTION_EMAIL or "example.com" in IQ_OPTION_EMAIL:
        print(
            "\n[WARNING] It looks like you still have the default example email in your .env file."
        )
        print("Please update IQ_OPTION_EMAIL and IQ_OPTION_PASSWORD first.")
        return

    print(f"Target Email: {IQ_OPTION_EMAIL}")
    print(f"Using Practice Account: {USE_PRACTICE_ACCOUNT}")
    print("----------------------------------------\n")

    executor = TradeExecutor()

    # 1. Test Connection
    print("1. Testing connection to IQ Option Servers...")
    if executor.connect():
        print("-> [SUCCESS] Connected and logged in!\n")

        # 2. Test Trade Execution
        # We will attempt a 1-minute CALL order on EURUSD
        test_signal = {
            "asset": "EURUSD-OTC",
            "direction": "CALL",
            "expiry": 1,
            "is_valid": True,
        }

        print("2. Attempting a 1-minute CALL test trade on EURUSD...")
        result = executor.execute_trade(test_signal)

        if result.get("success"):
            print(
                f"-> [SUCCESS] Test trade executed! Trade ID: {result.get('trade_id')}"
            )
            print(
                "\nPlease log in to your IQ Option dashboard (Practice balance) to see the live trade!"
            )
        else:
            print(f"-> [ERROR] Trade failed. Reason: {result.get('error')}")
            print(
                "Note: If the error says 'active is closed', the market for EURUSD might be closed right now (e.g., weekend)."
            )
    else:
        print(
            "-> [ERROR] Failed to connect. Please double check your credentials in .env and verify your connection."
        )


if __name__ == "__main__":
    test_connection()
