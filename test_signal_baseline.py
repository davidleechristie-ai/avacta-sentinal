import unittest
from datetime import date,timedelta
from signal_baseline import compare
class BaselineTests(unittest.TestCase):
    def bars(self,values):
        return [{"date":(date(2026,7,1)+timedelta(days=i)).isoformat(),
                 "open":v,"high":v+1,"low":v-1,"close":v,"volume":100} for i,v in enumerate(values)]
    def test_flat_market_baseline_zero(self):
        result=compare(self.bars([70]*20),horizons=(1,))
        self.assertEqual(result["horizons"]["1"]["all_sessions_mean_return_pct"],0)
        self.assertEqual(result["horizons"]["1"]["signal_events"],0)
    def test_downtrend_baseline_is_negative(self):
        result=compare(self.bars([70]*12+[65,64,63,62,61,60]),horizons=(1,5))
        self.assertLess(result["horizons"]["1"]["all_sessions_mean_return_pct"],0)
        self.assertEqual(result["horizons"]["5"]["signal_events"],1)
        self.assertFalse(result["auto_trade"])
