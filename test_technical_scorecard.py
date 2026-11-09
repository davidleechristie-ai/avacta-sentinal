import unittest
from datetime import date, timedelta
from technical_scorecard import assess_technicals

def sample():
    start = date(2026, 9, 1)
    return [{"date": (start + timedelta(days=i)).isoformat(),
             "open": 50, "high": 55, "low": 45, "close": 50, "volume": 100}
            for i in range(22)]

class TechnicalScorecardTests(unittest.TestCase):
    def test_not_enough_sessions(self):
        self.assertEqual(assess_technicals(sample()[:10])["price_reversal"], "INSUFFICIENT_DATA")

    def test_flat_market_not_reversal(self):
        result = assess_technicals(sample())
        self.assertEqual(result["price_reversal"], "NOT_CONFIRMED")
        self.assertEqual(result["sustained_volume"], "NOT_CONFIRMED")
        self.assertFalse(result["trade_signal"])

    def test_breakout_and_two_volume_sessions(self):
        rows = sample()
        for i in range(12, 22):
            rows[i]["low"] = 47
        rows[-1]["close"] = 57
        rows[-1]["high"] = 58
        rows[-1]["volume"] = 300
        rows[-2]["volume"] = 300
        result = assess_technicals(rows)
        self.assertEqual(result["price_reversal"], "CONFIRMED_TECHNICAL_PATTERN")
        self.assertEqual(result["sustained_volume"], "CONFIRMED_2_SESSIONS")
        self.assertFalse(result["trade_signal"])

    def test_zero_volume_rows_excluded(self):
        rows = sample()
        rows[-1]["volume"] = 0
        self.assertEqual(assess_technicals(rows)["price_reversal"], "INSUFFICIENT_DATA")
