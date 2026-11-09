import unittest
from price_bars import clean_bars
class PriceBarsTests(unittest.TestCase):
    def test_invalid_high_low_excluded(self):
        good={"date":"2026-11-06","open":55,"high":56,"low":53,"close":54,"volume":100}
        bad={**good,"date":"2026-11-05","high":52}
        rows,rejected=clean_bars([bad,good])
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["date"],"2026-11-06")
        self.assertEqual(len(rejected),1)
    def test_zero_volume_excluded(self):
        rows,rejected=clean_bars([{"date":"2026-11-06","open":54,"high":55,"low":53,"close":54,"volume":0}])
        self.assertEqual(rows,[])
        self.assertEqual(len(rejected),1)
