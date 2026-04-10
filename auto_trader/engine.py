import logging
import asyncio
from datetime import datetime
from .parser import SignalParser
from .validator import SignalValidator
from .executor import TradeExecutor
from .tracker import ResultTracker
from config import SIGNAL_MAX_WAIT_SECONDS, ENABLE_AUTO_TRADING

logger = logging.getLogger(__name__)


def _seconds_until_signal_minute(signal_minute: int) -> float:
    """
    Calculate how many seconds until the local clock reaches `signal_minute`.

    The minute number is timezone-agnostic: `:23` is `:23` everywhere, so we
    simply compare it to the current local minute without any UTC conversion.

    Returns:
        positive float  → seconds to wait (we're before the target minute)
        0.0             → already inside the target minute, execute now
        negative float  → target minute has already passed, caller should skip
    """
    now = datetime.now()
    current_minute = now.minute
    current_second = now.second

    if current_minute == signal_minute:
        # Already inside the target minute — execute immediately
        return 0.0

    if current_minute < signal_minute:
        # Target minute is still ahead this hour
        wait = (signal_minute - current_minute) * 60 - current_second
        return float(wait)

    # current_minute > signal_minute → target minute has passed this hour
    return float((signal_minute - current_minute) * 60 - current_second)  # negative


class AutoTraderEngine:
    """
    Main orchestrator for the Binary Options Auto-Trading Extension.
    Pipeline: parser → scheduler (minute-based) → validator → executor → tracker.
    """

    def __init__(self):
        self.parser = SignalParser()
        self.validator = SignalValidator()
        self.executor = TradeExecutor()
        self.tracker = ResultTracker()

        # Pre-connect to IQ Option eagerly at startup (in a background thread).
        # This ensures the WebSocket and asset list are ready BEFORE the first
        # signal arrives, so actual trade execution is instant.
        if ENABLE_AUTO_TRADING:
            self._schedule_preconnect()

    def _schedule_preconnect(self):
        """Schedule the IQ Option connection to run in the background at startup."""
        try:
            loop = asyncio.get_event_loop()
            loop.run_in_executor(None, self.executor.connect)
        except RuntimeError:
            # No event loop yet (e.g., imported at module level before loop starts)
            # Connection will happen lazily on first trade instead.
            pass

    async def process_signal(self, text: str):
        """
        Processes a raw telegram message.
        Waits (if necessary) until the signal's scheduled minute before trading.
        """
        logger.info("AutoTrader received new signal text. Processing...")

        # 1. Parse
        parsed = self.parser.parse(text)
        if not parsed.get("is_valid"):
            logger.debug("AutoTrader: Signal could not be parsed or is invalid.")
            self.tracker.log_trade(parsed, {"error": "Parse failed"}, "INVALID_FORMAT")
            return

        logger.info(
            f"AutoTrader Parsed Signal: {parsed['asset']} {parsed['direction']} "
            f"{parsed['expiry']}m | Scheduled: {parsed.get('execute_time', 'N/A')}"
        )

        # 2. Minute-based timing check
        execute_time = parsed.get("execute_time")
        if execute_time:
            signal_minute = int(execute_time.split(":")[1])
            wait = _seconds_until_signal_minute(signal_minute)

            if 0 < wait <= SIGNAL_MAX_WAIT_SECONDS:
                logger.info(
                    f"AutoTrader: Current minute is :{datetime.now().minute:02d}, "
                    f"signal minute is :{signal_minute:02d}. "
                    f"Sleeping {wait:.1f}s..."
                )
                await asyncio.sleep(wait)
                logger.info("AutoTrader: Scheduled minute reached. Executing trade now.")

            elif wait > SIGNAL_MAX_WAIT_SECONDS:
                logger.warning(
                    f"AutoTrader: Signal minute :{signal_minute:02d} is {wait:.0f}s away "
                    f"(>{SIGNAL_MAX_WAIT_SECONDS}s limit). Skipping."
                )
                self.tracker.log_trade(parsed, {"error": "Too far in the future"}, "SKIPPED_TIMING")
                return

            elif wait < 0:
                # Minute has already passed
                logger.warning(
                    f"AutoTrader: Signal minute :{signal_minute:02d} has already passed "
                    f"(current :{datetime.now().minute:02d}). Skipping."
                )
                self.tracker.log_trade(parsed, {"error": "Signal minute expired"}, "SKIPPED_EXPIRED")
                return

            else:
                # wait == 0.0 → already in the correct minute
                logger.info(
                    f"AutoTrader: Already in signal minute :{signal_minute:02d}. Executing immediately."
                )
        else:
            logger.info("AutoTrader: No execution time in signal. Executing immediately.")

        # 3. Validate
        if not self.validator.validate(parsed):
            logger.info("AutoTrader: Signal failed validation.")
            self.tracker.log_trade(parsed, {"error": "Validation failed"}, "VALIDATION_FAILED")
            return

        # 4. Execute (in a separate thread since api-iqoption-faria is synchronous)
        logger.info("AutoTrader: Signal validated. Handing off to executor...")
        execution_result = await asyncio.to_thread(self.executor.execute_trade, parsed)

        # 5. Track
        if execution_result.get("success"):
            logger.info(
                f"AutoTrader: Trade successfully executed! ID: {execution_result.get('trade_id')}"
            )
            self.tracker.log_trade(parsed, execution_result, "EXECUTED")
        else:
            logger.error(
                f"AutoTrader: Trade execution failed: {execution_result.get('error')}"
            )
            self.tracker.log_trade(parsed, execution_result, "EXECUTION_FAILED")


# Provide a global instance for easy import
auto_trader_engine = AutoTraderEngine()
