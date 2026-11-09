import unittest
from datetime import date,timedelta
from downside_guard import assess
from retrospective import replay
def rows(closes):
    start=date(2026,10,1)
    return [{"date":(start+timedelta(days=i)).isoformat(),"open":v,"high":v+1,
             "low":v-1,"close":v,"volume":1000} for i,v in enumerate(closes)]
class DownsideTests(unittest.TestCase):
    def test_insufficient_data_does_not_claim_safety(self):
        self.assertEqual(assess(rows([60,59]))["severity"],"UNKNOWN")
    def test_support_break_and_drawdown_critical(self):
        r=assess(rows([70]*12+[68,66,63,60,56,53]))
        self.assertEqual(r["severity"],"CRITICAL")
        self.assertIn("CLOSE_BELOW_PRIOR_10_SESSION_SUPPORT",r["warnings"])
        self.assertFalse(r["auto_trade"])
    def test_flat_series_normal(self):
        self.assertEqual(assess(rows([60]*20))["severity"],"NORMAL")
    def test_replay_has_no_future_lookahead(self):
        series=rows([70]*12+[69,67,65,60,55])
        earlier=replay(series[:-1])
        full=replay(series)
        self.assertEqual(earlier["timeline"],full["timeline"][:-1])
    def test_replay_does_not_claim_alert_delivery(self):
        self.assertFalse(replay(rows([60]*20))["trade_signal"])
