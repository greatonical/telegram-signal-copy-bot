import unittest
import sys
import os

# Ensure the root path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from auto_trader.parser import SignalParser

class TestSignalParser(unittest.TestCase):
    def setUp(self):
        self.parser = SignalParser()
        
    def test_standard_format(self):
        text = "EURUSD - 5m - CALL"
        res = self.parser.parse(text)
        self.assertTrue(res["is_valid"])
        self.assertEqual(res["asset"], "EURUSD")
        self.assertEqual(res["direction"], "CALL")
        self.assertEqual(res["expiry"], 5)
        
    def test_slash_format(self):
        text = "Asset: EUR/USD\nDirection: PUT\nExpiry: 15 minutes"
        res = self.parser.parse(text)
        self.assertTrue(res["is_valid"])
        self.assertEqual(res["asset"], "EURUSD")
        self.assertEqual(res["direction"], "PUT")
        self.assertEqual(res["expiry"], 15)
        
    def test_otc_format(self):
        text = "OTC EURUSD BUY 5m"
        res = self.parser.parse(text)
        self.assertTrue(res["is_valid"])
        self.assertEqual(res["asset"], "EURUSD-OTC")
        self.assertEqual(res["direction"], "CALL")
        self.assertEqual(res["expiry"], 5)

    def test_m5_format(self):
        text = "Asset: GBPUSD\nDirection: DOWN\nExpiry: M5"
        res = self.parser.parse(text)
        self.assertTrue(res["is_valid"])
        self.assertEqual(res["asset"], "GBPUSD")
        self.assertEqual(res["direction"], "PUT")
        self.assertEqual(res["expiry"], 5)
        
    def test_invalid_signal(self):
        text = "Just some normal chat without signal details"
        res = self.parser.parse(text)
        self.assertFalse(res["is_valid"])

if __name__ == '__main__':
    unittest.main()
