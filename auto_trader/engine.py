import logging
import asyncio
from typing import Optional
from .parser import SignalParser
from .validator import SignalValidator
from .executor import TradeExecutor
from .tracker import ResultTracker

logger = logging.getLogger(__name__)

class AutoTraderEngine:
    """
    Main orchestrator for the Binary Options Auto-Trading Extension.
    Pipelines messages through parser -> validator -> executor -> tracker.
    """
    def __init__(self):
        self.parser = SignalParser()
        self.validator = SignalValidator()
        self.executor = TradeExecutor()
        self.tracker = ResultTracker()
        
    async def process_signal(self, text: str):
        """
        Processes a raw telegram message.
        Runs the trade execution in a separate thread so the asyncio loop isn't blocked.
        """
        logger.info("AutoTrader received new signal text. Processing...")
        
        # 1. Parse
        parsed = self.parser.parse(text)
        if not parsed.get("is_valid"):
            logger.debug("AutoTrader: Signal could not be parsed or is invalid.")
            self.tracker.log_trade(parsed, {"error": "Parse failed"}, "INVALID_FORMAT")
            return
            
        logger.info(f"AutoTrader Parsed Signal: {parsed['asset']} {parsed['direction']} {parsed['expiry']}m")
        
        # 2. Validate
        if not self.validator.validate(parsed):
            logger.info("AutoTrader: Signal failed validation.")
            self.tracker.log_trade(parsed, {"error": "Validation failed"}, "VALIDATION_FAILED")
            return
            
        # 3. Execute (in a separate thread since api-iqoption-faria is synchronous)
        logger.info("AutoTrader: Signal validated. Handing off to executor...")
        execution_result = await asyncio.to_thread(self.executor.execute_trade, parsed)
        
        # 4. Track
        if execution_result.get("success"):
            logger.info(f"AutoTrader: Trade successfully executed! ID: {execution_result.get('trade_id')}")
            self.tracker.log_trade(parsed, execution_result, "EXECUTED")
        else:
            logger.error(f"AutoTrader: Trade execution failed: {execution_result.get('error')}")
            self.tracker.log_trade(parsed, execution_result, "EXECUTION_FAILED")

# Provide a global instance for easy import
auto_trader_engine = AutoTraderEngine()
