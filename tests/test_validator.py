import unittest
import time
import sys
import os

# Ensure the root path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from auto_trader.validator import SignalValidator
from config import MAX_DAILY_LOSS

class TestSignalValidator(unittest.TestCase):
    def setUp(self):
        self.validator = SignalValidator()
        self.validator.duplicate_cooldown_seconds = 10 # Short cooldown for tests
        
    def test_valid_signal(self):
        signal = {
            "asset": "EURUSD",
            "direction": "CALL",
            "expiry": 5,
            "is_valid": True
        }
        self.assertTrue(self.validator.validate(signal))
        
    def test_duplicate_signal(self):
        signal = {
            "asset": "EURUSD",
            "direction": "CALL",
            "expiry": 5,
            "is_valid": True
        }
        # First time passes
        self.assertTrue(self.validator.validate(signal))
        # Second time fails
        self.assertFalse(self.validator.validate(signal))
        
    def test_daily_loss_limit(self):
        signal = {
            "asset": "GBPUSD",
            "direction": "PUT",
            "expiry": 5,
            "is_valid": True
        }
        self.validator.current_daily_loss = MAX_DAILY_LOSS + 1
        self.assertFalse(self.validator.validate(signal))

    def test_invalid_signal_format(self):
        signal = {
            "is_valid": False
        }
        self.assertFalse(self.validator.validate(signal))

if __name__ == '__main__':
    unittest.main()
