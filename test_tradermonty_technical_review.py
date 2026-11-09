import unittest
from tradermonty_technical_review import report
class TraderMontyTechnicalTests(unittest.TestCase):
    def test_no_chart_no_fake_probability(self):
        bars=[{"date":"2026-11-06","open":54,"high":55,"low":53,"close":53.8,"volume":100000}]
        r=report(bars,{"severity":"CRITICAL","price_data_provenance":"OPENBB_YFINANCE_UNVERIFIED"},{"decision":"DEFENSIVE_HOLD_OR_REDUCE"})
        self.assertEqual(r["weekly_chart_review"]["status"],"NOT_PERFORMED")
        self.assertEqual(r["probabilities"],"NOT_CALIBRATED")
        self.assertEqual(r["technical_observations"]["twenty_session_low_pence"],53)
        self.assertFalse(r["auto_trade"])
    def test_empty_bars_fail_closed(self):
        r=report([],{},{"decision":"WAIT_FOR_CONFIRMATION"})
        self.assertIsNone(r["last_completed_session"])
        self.assertEqual(r["completed_sessions"],0)
