import unittest
from forward_levels import map_levels
from isa_positioning_report import build_report,markdown
class ForwardLevelsTests(unittest.TestCase):
    def bars(self):
        closes=[65,64,63,62,61,60,59,58,56,53.8]
        return [{"date":f"2026-10-{i+10:02d}","open":v+1,"high":v+2,"low":v-1,"close":v,"volume":1000} for i,v in enumerate(closes)]
    def test_broken_support_not_downside_target(self):
        result=map_levels(self.bars())
        self.assertTrue(all(x["level_pence"]<53.8 for x in result["downside_candidates"]))
        self.assertTrue(all(x["level_pence"]>=53.8 for x in result["broken_support"]))
        self.assertFalse(result["auto_trade"])
    def test_no_bars(self):
        self.assertEqual(map_levels([])["status"],"INSUFFICIENT_DATA")
    def test_event_checks_and_markdown(self):
        decision={"as_of":"2026-11-09","isa_exit_deadline":"2027-01-29","observed_close":53.8,
                  "price_session_gate":"ACCEPTED","price_source_status":"OPENBB_YFINANCE_UNVERIFIED"}
        weekly={"weekly_trend_pattern":"LOWER_HIGHS_AND_LOWS","prior_eight_week_support_pence":60}
        report=build_report(decision,weekly,{"catalysts":[]},{},{"decision":"NO_ACTIONABLE_ORDERS"},{"severity":"CRITICAL"},map_levels(self.bars()))
        self.assertEqual(report["support_context"],"BROKEN_PREVIOUS_SUPPORT")
        self.assertIn("Event-specific positioning checks",markdown(report))
        self.assertFalse(report["auto_trade"])
