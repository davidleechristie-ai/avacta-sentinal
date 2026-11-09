import unittest
from isa_positioning_report import build_report,markdown
class PositioningTests(unittest.TestCase):
    def fixture(self,**kwargs):
        d={"as_of":"2026-11-09","isa_exit_deadline":"2027-01-29","decision":"DEFENSIVE_HOLD_OR_REDUCE",
           "observed_close":53.8,"price_session_gate":"ACCEPTED","price_source_status":"OPENBB_YFINANCE_UNVERIFIED"}
        d.update(kwargs)
        w={"weekly_trend_pattern":"LOWER_HIGHS_AND_LOWS","prior_eight_week_support_pence":52,
           "prior_eight_week_resistance_pence":70,"relative_weekly_volume":1.1}
        c={"catalysts":[{"id":"AVA6207","status":"UPCOMING","within_isa_horizon":True,
                         "days_until_start":9,"source":"https://avacta.com/news/","surprise_assessment":"NOT_VERIFIED"}]}
        return d,w,c
    def test_unverified_critical_defensive(self):
        d,w,c=self.fixture()
        r=build_report(d,w,c,{},{"decision":"NO_ACTIONABLE_ORDERS"},{"severity":"CRITICAL"})
        self.assertEqual(r["stance"],"DEFENSIVE_REVIEW_DATA_UNVERIFIED")
        self.assertEqual(r["next_catalyst"]["id"],"AVA6207")
        self.assertFalse(r["auto_trade"])
        self.assertTrue(r["owner_approval_required"])
        self.assertIn("AVCT Sentinel",markdown(r))
    def test_deadline_precedence(self):
        d,w,c=self.fixture(as_of="2027-01-20")
        r=build_report(d,w,c,{},{"decision":"NO_ACTIONABLE_ORDERS"},{"severity":"NORMAL"})
        self.assertEqual(r["stance"],"PRIORITISE_MANDATORY_EXIT")
    def test_no_unverified_add(self):
        d,w,c=self.fixture()
        w.update(weekly_trend_pattern="HIGHER_HIGHS_AND_LOWS",weekly_breakout=True)
        r=build_report(d,w,c,{},{"decision":"NO_ACTIONABLE_ORDERS"},{"severity":"NORMAL"})
        self.assertEqual(r["stance"],"WAIT_FOR_VERIFIED_EVIDENCE")
    def test_verified_bull_still_requires_approval(self):
        d,w,c=self.fixture(price_source_status="INDEPENDENTLY_VERIFIED",independent_price_evidence={"status":"MATCHED","independent_providers":2})
        w.update(weekly_trend_pattern="HIGHER_HIGHS_AND_LOWS",weekly_breakout=True)
        r=build_report(d,w,c,{},{"decision":"WAIT_FOR_CONFIRMATION"},{"severity":"NORMAL"})
        self.assertEqual(r["stance"],"CONSIDER_ADD_ONLY_AFTER_MANUAL_CHECKS")
        self.assertFalse(r["trade_signal"])
    def test_stale_session_blocks_add(self):
        d,w,c=self.fixture(price_session_gate="STALE",price_source_status="INDEPENDENTLY_VERIFIED")
        r=build_report(d,w,c,{},{"decision":"WAIT_FOR_VERIFIED_SESSION"},{"severity":"NORMAL"})
        self.assertEqual(r["stance"],"WAIT_FOR_VERIFIED_EVIDENCE")
