import logging
import time
from config import MAX_DAILY_LOSS

logger = logging.getLogger(__name__)

class SignalValidator:
    def __init__(self):
        # Keeps track of recently traded assets to avoid duplicates
        # Format: { asset: timestamp }
        self.recent_trades = {}
        self.duplicate_cooldown_seconds = 300 # 5 minutes
        self.current_daily_loss = 0.0
        
    def validate(self, parsed_signal: dict) -> bool:
        if not parsed_signal.get("is_valid"):
            logger.warning("Signal invalid or incomplete.")
            return False
            
        asset = parsed_signal["asset"]
        
        # 1. Check duplicate signals
        now = time.time()
        if asset in self.recent_trades:
            last_time = self.recent_trades[asset]
            if now - last_time < self.duplicate_cooldown_seconds:
                logger.warning(f"Duplicate signal for {asset} within {self.duplicate_cooldown_seconds}s. Skipping.")
                return False
                
        # 2. Check daily loss limit
        if self.current_daily_loss >= MAX_DAILY_LOSS:
            logger.warning(f"Max daily loss ({MAX_DAILY_LOSS}) reached! Skipping trade.")
            return False
            
        # 3. Check Trading Hours (Optional)
        # Add checks for weekends or specific non-trading hours if needed
        
        # Validated!
        self.recent_trades[asset] = now
        return True
