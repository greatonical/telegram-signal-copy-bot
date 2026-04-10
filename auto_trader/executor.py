import logging
from config import IQ_OPTION_EMAIL, IQ_OPTION_PASSWORD, TRADE_AMOUNT, USE_PRACTICE_ACCOUNT

logger = logging.getLogger(__name__)

# Note: The api-iqoption-faria library imports from iqoptionapi
try:
    from iqoptionapi.stable_api import IQ_Option
    from iqoptionapi import constants as OP_code
except ImportError:
    logger.warning("iqoptionapi not found. Executor will not work until installed.")
    IQ_Option = None
    OP_code = None


class TradeExecutor:
    def __init__(self):
        self.email = IQ_OPTION_EMAIL
        self.password = IQ_OPTION_PASSWORD
        self.api = None
        self.is_connected = False

    def connect(self) -> bool:
        """
        Establish a fresh connection to IQ Option.

        After authenticating, calls get_ALL_Binary_ACTIVES_OPCODE() which fetches
        the live binary + turbo asset list from IQ Option's servers and populates
        the OP_code.ACTIVES dict. This dict is what api.buy() reads from, so it
        must be up-to-date before any trade is placed.

        The hardcoded constants.py that ships with the library is outdated and
        missing most OTC pairs (EURAUD-OTC, USDMXN-OTC, CADCHF-OTC, etc.).
        get_ALL_Binary_ACTIVES_OPCODE() fetches the current live list and
        patches ACTIVES at runtime, solving the KeyError entirely.
        """
        if not IQ_Option:
            logger.error("IQ_Option module is not installed.")
            return False

        if not self.email or not self.password:
            logger.error("IQ Option credentials missing in .env!")
            return False

        logger.info("Connecting to IQ Option...")
        self.api = IQ_Option(self.email, self.password)
        check, reason = self.api.connect()

        if check:
            logger.info("Connected to IQ Option successfully.")
            self.is_connected = True
            balance_type = "PRACTICE" if USE_PRACTICE_ACCOUNT else "REAL"
            self.api.change_balance(balance_type)
            logger.info(f"Using {balance_type} account. Balance: {self.api.get_balance()}")
            self._load_asset_list()
            return True
        else:
            logger.error(f"Failed to connect to IQ Option: {reason}")
            self.is_connected = False
            return False

    def _load_asset_list(self) -> None:
        """
        Fetch the live binary + turbo asset list from IQ Option and patch
        OP_code.ACTIVES so api.buy() can resolve all asset names, including
        OTC pairs that are missing from the stale hardcoded constants.py.

        Uses get_ALL_Binary_ACTIVES_OPCODE() — the officially supported method
        in the stable_api.py for this purpose.
        """
        try:
            logger.info("Fetching live asset list from IQ Option...")
            self.api.get_ALL_Binary_ACTIVES_OPCODE()
            otc_count = sum(1 for k in OP_code.ACTIVES if "OTC" in str(k))
            logger.info(
                f"Asset list loaded: {len(OP_code.ACTIVES)} total assets "
                f"({otc_count} OTC). Ready to trade."
            )
        except Exception as e:
            logger.error(f"Failed to load asset list: {e}. Trades may fail for unlisted assets.")

    def _ensure_connected(self) -> bool:
        """
        Verify the WebSocket session is still alive before every trade.
        Uses api.check_connect() to query the live socket, not just the in-memory flag.
        """
        if not self.is_connected or self.api is None:
            return self.connect()

        try:
            still_alive = self.api.check_connect()
        except Exception:
            still_alive = False

        if not still_alive:
            logger.warning("IQ Option WebSocket dropped. Reconnecting...")
            self.is_connected = False
            return self.connect()

        return True

    def _check_asset_available(self, asset: str) -> bool:
        """
        Check if the asset is in OP_code.ACTIVES before calling buy().

        OP_code.ACTIVES is the dict that api.buy() reads from. If the asset
        isn't there, buy() raises a KeyError. We check here first so we can
        log a clear reason and avoid a misleading traceback.
        """
        if OP_code is None:
            return False

        if asset in OP_code.ACTIVES:
            return True

        otc_assets = sorted(k for k in OP_code.ACTIVES if "OTC" in str(k))
        logger.warning(
            f"Asset '{asset}' not found in ACTIVES. "
            f"Known OTC assets ({len(otc_assets)}): {otc_assets}"
        )
        return False

    def execute_trade(self, parsed_signal: dict) -> dict:
        """
        Executes a binary options trade.

        Error handling:
          - Stale connection  → reconnect via _ensure_connected()
          - Asset not listed  → log clearly and skip (not a connection issue)
          - Other errors      → log and mark disconnected for safety
        """
        # 1. Ensure WebSocket is alive
        if not self._ensure_connected():
            return {"success": False, "error": "Not connected to broker"}

        asset = parsed_signal["asset"]
        direction = parsed_signal["direction"].lower()  # buy() expects "call" or "put"
        expiry = parsed_signal["expiry"]
        amount = TRADE_AMOUNT

        # 2. Verify asset is in the live ACTIVES dict before calling buy()
        if not self._check_asset_available(asset):
            return {
                "success": False,
                "error": f"Asset '{asset}' not in IQ Option asset list",
            }

        logger.info(f"Executing Trade: {asset} | {direction.upper()} | {expiry}m | ${amount}")

        try:
            check, id_or_error = self.api.buy(amount, asset, direction, expiry)
            if check:
                logger.info(f"Trade placed successfully! ID: {id_or_error}")
                return {"success": True, "trade_id": id_or_error}
            else:
                logger.error(f"Trade rejected by broker: {id_or_error}")
                return {"success": False, "error": str(id_or_error)}

        except KeyError as e:
            logger.error(
                f"KeyError on buy({asset}): {e}. "
                "Asset may have been removed from ACTIVES. Reloading asset list..."
            )
            self._load_asset_list()
            self.is_connected = False
            return {"success": False, "error": f"Asset lookup error: {e}"}

        except Exception as e:
            logger.error(f"Exception during trade execution: {e}", exc_info=True)
            self.is_connected = False
            return {"success": False, "error": str(e)}
