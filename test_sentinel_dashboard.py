import unittest
from sentinel_dashboard import render
class DashboardTests(unittest.TestCase):
    def report(self):
        return {"as_of":"2026-11-09","stance":"DEFENSIVE_REVIEW_DATA_UNVERIFIED",
                "downside_severity":"CRITICAL","rationale":"Price feed unverified",
                "observed_close_pence":53.8,"days_to_exit":81,"isa_exit_deadline":"2027-01-29",
                "weekly_trend":"LOWER_HIGHS_AND_LOWS","weekly_relative_volume":2.32,
                "weekly_support_pence":60,"weekly_resistance_pence":70,
                "support_context":"BROKEN_PREVIOUS_SUPPORT",
                "forward_levels":{"downside_candidates":[{"level_pence":51.2}],"overhead_resistance":[{"level_pence":60}]},
                "data_quality":{"independently_verified_price":False,"completed_session_accepted":True,"catalyst_outcomes_verified":False},
                "next_catalyst":{"id":"AVA6207","days_until_start":9,"source":"https://avacta.com/news/"},
                "event_positioning_rules":{"before_event":"Verify price"},
                "scenario_matrix":{"bull":{"condition":"Higher low","review":"Manual review"},
                                   "base":{"condition":"Mixed","review":"Wait"},
                                   "bear":{"condition":"Breakdown","review":"Review reduce"}},
                "change_to_consider_add":["Verify OHLCV"],"change_to_review_reduction":["Support breaks"],
                "pretrade_gate":"NO_ACTIONABLE_ORDERS"}
    def test_dashboard_is_readable_and_offline(self):
        html=render(self.report())
        self.assertIn("<!doctype html>",html)
        self.assertIn("53.8p",html)
        self.assertIn("51.2p",html)
        self.assertIn("Manual approval",html) if "Manual approval" in html else self.assertIn("Owner approval required",html)
        self.assertNotIn("<script",html)
        self.assertNotIn("fetch(",html)
    def test_escapes_untrusted_headlines(self):
        r=self.report();r["rationale"]="<script>alert(1)</script>"
        html=render(r)
        self.assertNotIn("<script>",html)
        self.assertIn("&lt;script&gt;",html)
    def test_missing_optional_data(self):
        r=self.report();r["next_catalyst"]=None;r["forward_levels"]={}
        html=render(r)
        self.assertIn("No upcoming registry event",html)
        self.assertIn("No historical level established",html)
