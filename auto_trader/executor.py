import logging
import asyncio
from config import IQ_OPTION_EMAIL, IQ_OPTION_PASSWORD, TRADE_AMOUNT, USE_PRACTICE_ACCOUNT

logger = logging.getLogger(__name__)

# Note: The api-iqoption-faria library imports from iqoptionapi
try:
    from iqoptionapi.stable_api import IQ_Option
except ImportError:
    logger.warning("iqoptionapi not found. Executor will not work until installed.")
    IQ_Option = None

class TradeExecutor:
    def __init__(self):
        self.email = IQ_OPTION_EMAIL
        self.password = IQ_OPTION_PASSWORD
        self.api = None
        self.is_connected = False
        
    def connect(self):
        if not IQ_Option:
            logger.error("IQ_Option module is not installed.")
            return False
            
        if not self.email or not self.password:
            logger.error("IQ Option credentials missing in .env!")
            return False
            
        logger.info("Connecting to IQ Option...")
        # To avoid blocking the event loop on startup, this should be run in a thread 
        # normally, but since we connect lazily it's handled below.
        self.api = IQ_Option(self.email, self.password)
        check, reason = self.api.connect()
        
        if check:
            logger.info("Connected to IQ Option successfully.")
            self.is_connected = True
            
            # Set balance type
            balance_type = "PRACTICE" if USE_PRACTICE_ACCOUNT else "REAL"
            self.api.change_balance(balance_type)
            logger.info(f"Using {balance_type} account. Balance: {self.api.get_balance()}")
            return True
        else:
            logger.error(f"Failed to connect to IQ Option: {reason}")
            self.is_connected = False
            return False
            
    def execute_trade(self, parsed_signal: dict) -> dict:
        """
        Executes a binary options trade.
        Returns a dict with execution results.
        Runs synchronously.
        """
        if not self.is_connected:
            if not self.connect():
                return {"success": False, "error": "Not connected to broker"}
                
        asset = parsed_signal["asset"]
        direction = parsed_signal["direction"].lower() # iqoptionapi expects "call" or "put"
        expiry = parsed_signal["expiry"]
        amount = TRADE_AMOUNT
        
        logger.info(f"Executing Trade: {asset} | {direction.upper()} | {expiry}m | ${amount}")
        
        try:
            # iqoptionapi signature: buy(amount, active, action, expiries)
            check, id_or_error = self.api.buy(amount, asset, direction, expiry)
            if check:
                logger.info(f"Trade placed successfully! ID: {id_or_error}")
                return {"success": True, "trade_id": id_or_error}
            else:
                logger.error(f"Trade failed: {id_or_error}")
                return {"success": False, "error": id_or_error}
        except Exception as e:
            logger.error(f"Exception during trade execution: {e}")
            return {"success": False, "error": str(e)}
