import unittest
from datetime import date,timedelta
from technical_backtest import replay
class ReplayTests(unittest.TestCase):
    def test_no_data(self):
        r=replay([])
        self.assertEqual(r["signals"],0)
        self.assertIsNone(r["hit_rate"])
        self.assertFalse(r["trade_signal"])
    def test_flat_prices_no_signal(self):
        start=date(2026,9,1)
        rows=[{"date":(start+timedelta(days=i)).isoformat(),"open":50,"high":55,"low":45,"close":50,"volume":100} for i in range(35)]
        self.assertEqual(replay(rows)["signals"],0)
