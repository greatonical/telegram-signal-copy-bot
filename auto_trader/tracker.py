import os
import csv
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ResultTracker:
    def __init__(self, filename="trades.csv"):
        self.filename = filename
        self._ensure_file_exists()
        
    def _ensure_file_exists(self):
        if not os.path.exists(self.filename):
            try:
                with open(self.filename, mode='w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "timestamp", "asset", "direction", "expiry", 
                        "status", "trade_id", "error_message", "raw_signal"
                    ])
            except Exception as e:
                logger.error(f"Failed to create tracker CSV: {e}")
                
    def log_trade(self, parsed_signal: dict, execution_result: dict, status: str):
        """
        status: e.g. 'EXECUTED', 'VALIDATION_FAILED', 'EXECUTION_FAILED', 'INVALID_FORMAT'
        """
        try:
            with open(self.filename, mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    parsed_signal.get("asset", ""),
                    parsed_signal.get("direction", ""),
                    parsed_signal.get("expiry", ""),
                    status,
                    execution_result.get("trade_id", ""),
                    execution_result.get("error", ""),
                    parsed_signal.get("raw_text", "").replace("\n", " ").strip()
                ])
        except Exception as e:
            logger.error(f"Failed to log trade to CSV: {e}")
