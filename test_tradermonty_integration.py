import unittest
from datetime import date,timedelta
from tradermonty_weekly import weekly_review
from tradermonty_catalyst_overlay import assess_catalysts,combine
from tradermonty_pretrade import check
class SkillIntegrationTests(unittest.TestCase):
    def test_weekly_aggregation(self):
        bars=[{"date":"2026-11-02","open":60,"high":61,"low":58,"close":59,"volume":100},
              {"date":"2026-11-03","open":59,"high":60,"low":56,"close":57,"volume":200},
              {"date":"2026-11-06","open":55,"high":56,"low":53,"close":53.8,"volume":300}]
        result=weekly_review(bars)
        self.assertEqual(result["weeks_available"],1)
        self.assertEqual(result["last_week"]["volume"],600)
        self.assertEqual(result["last_week"]["low"],53)
        self.assertEqual(result["probabilities"],"NOT_CALIBRATED")
    def test_catalyst_issuer_not_verified(self):
        result=assess_catalysts({"sources":{}},as_of="2026-11-09")
        self.assertEqual(result["catalysts"][0]["status"],"UPCOMING")
        self.assertEqual(result["catalysts"][0]["actual_outcome"],"UNKNOWN")
        self.assertFalse(result["auto_trade"])
    def test_overlay_never_grants_entry(self):
        c=assess_catalysts({},as_of="2026-11-09")
        r=combine({"decision":"DEFENSIVE_HOLD_OR_REDUCE"},{"weekly_trend_pattern":"LOWER_HIGHS_AND_LOWS"},c)
        self.assertEqual(r["entry_permission"],"NOT_GRANTED")
    def test_no_private_candidate(self):
        self.assertEqual(check()["decision"],"NO_ACTIONABLE_ORDERS")
    def test_candidate_requires_independent_verification(self):
        candidate={"symbol":"AVCT.L","order_intent":"ENTRY_READY","entry_in_written_plan":True,
                   "stop_predefined":True,"size_within_plan":True,"planned_risk_gbp":100,"actual_risk_gbp":80}
        self.assertEqual(check(candidate)["decision"],"REVIEW_REQUIRED")
    def test_oversize_rejected(self):
        candidate={"symbol":"AVCT.L","order_intent":"ENTRY_READY","entry_in_written_plan":True,
                   "stop_predefined":True,"size_within_plan":True,"planned_risk_gbp":100,"actual_risk_gbp":150}
        result=check(candidate,{"independently_verified_price":True,"isa_exit_deadline_checked":True})
        self.assertEqual(result["decision"],"REVIEW_REQUIRED")
        self.assertIn("Actual risk exceeds planned risk",result["reasons"])
