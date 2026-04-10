import re
import logging

logger = logging.getLogger(__name__)

class SignalParser:
    """
    Parses Telegram messages to extract binary options trading signals.
    """
    def parse(self, text: str) -> dict:
        """
        Extracts structured fields from raw message text.
        Returns a dict with:
        - asset (e.g., EURUSD)
        - direction (CALL / PUT)
        - expiry (int in minutes)
        - is_valid (bool)
        """
        result = {
            "asset": None,
            "direction": None,
            "expiry": None,
            "execute_time": None,   # HH:MM as parsed from the signal (provider's local time)
            "is_valid": False,
            "raw_text": text
        }
        
        if not text:
            return result
            
        text_upper = text.upper()
            
        # 1. Parse Asset (e.g., EURUSD, EUR/USD, OTC EURUSD)
        # Look for 6 uppercase letters optionally separated by /
        asset_match = re.search(r'\b([A-Z]{3})/?([A-Z]{3})\b', text_upper)
        if asset_match:
            result["asset"] = asset_match.group(1) + asset_match.group(2)
            # Check for OTC keyword nearby in the text
            if "OTC" in text_upper:
                result["asset"] += "-OTC"
                
        # 2. Parse Direction (CALL/UP/BUY vs PUT/DOWN/SELL)
        if re.search(r'\b(CALL|UP|BUY)\b', text_upper):
            result["direction"] = "CALL"
        elif re.search(r'\b(PUT|DOWN|SELL)\b', text_upper):
            result["direction"] = "PUT"
            
        # 3. Parse Expiry (e.g. 5 min, 5m, 15 minutes, M5)
        expiry_match = re.search(r'\b(\d+)\s*(M|MIN|MINUTES|MINUTE)\b', text_upper)
        if expiry_match:
            result["expiry"] = int(expiry_match.group(1))
        else:
            # Maybe M5 format
            m_match = re.search(r'\bM(\d+)\b', text_upper)
            if m_match:
                result["expiry"] = int(m_match.group(1))
                
        # 4. Parse Execution Time  (e.g. ⏰ 10:23 or just 10:23)
        # Matches any HH:MM or H:MM pattern in the message.
        time_match = re.search(r'\b(\d{1,2}):(\d{2})\b', text)
        if time_match:
            result["execute_time"] = f"{int(time_match.group(1)):02d}:{time_match.group(2)}"

        # 5. Validation
        if result["asset"] and result["direction"] and result["expiry"]:
            result["is_valid"] = True
            
        return result
