import unittest
from decision_engine import build_decision
class DecisionTests(unittest.TestCase):
    def base(self):
        return {"severity":"CRITICAL","latest_close":53.8,"prior_10_session_support":55,
                "session_gate":{"status":"ACCEPTED"},
                "risk_transition":{"status":"PERSISTENT_RISK"},
                "price_data_provenance":"OPENBB_YFINANCE_UNVERIFIED"}
    def test_persistent_critical_is_defensive_not_automatic_exit(self):
        d=build_decision(self.base(),as_of="2026-11-09")
        self.assertEqual(d["decision"],"DEFENSIVE_HOLD_OR_REDUCE")
        self.assertFalse(d["auto_trade"])
    def test_fresh_escalation(self):
        a=self.base()
        a["risk_transition"]["status"]="NEW_ESCALATION"
        self.assertEqual(build_decision(a,as_of="2026-11-09")["decision"],"REVIEW_REDUCTION_URGENTLY")
    def test_exit_deadline_overrides_technicals(self):
        self.assertEqual(build_decision(self.base(),as_of="2027-01-20")["decision"],"PLAN_FULL_EXIT")
    def test_stale_session_blocks_price_decision(self):
        a=self.base()
        a["session_gate"]={"status":"STALE"}
        self.assertEqual(build_decision(a,as_of="2026-11-09")["decision"],"WAIT_FOR_VERIFIED_SESSION")
