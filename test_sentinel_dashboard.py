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

    def test_evidence_audit_renders_live_data(self):
        scorecard={"decision_intelligence":{"independent_price_evidence":{
            "status":"NOT_VERIFIED","independent_providers":0,
            "reason":"No second provider configured"}}}
        html=render(self.report(),scorecard)
        self.assertIn("Evidence audit",html)
        self.assertIn("No second provider configured",html)
        self.assertIn("NOT_VERIFIED",html)
    def test_evidence_audit_escapes_untrusted_reason(self):
        scorecard={"decision_intelligence":{"independent_price_evidence":{
            "reason":"<script>alert(1)</script>"}}}
        html=render(self.report(),scorecard)
        self.assertIn("&lt;script&gt;",html)
        self.assertNotIn("<script>",html)

    def test_historical_outcomes_render_without_strategy_claims(self):
        scorecard={"forward_signal_audit":{"summary":{
            "1":{"evaluated_events":2,"subsequent_decline_fraction":0.5,"mean_forward_return_pct":-1.25},
            "3":{"evaluated_events":0,"subsequent_decline_fraction":None,"mean_forward_return_pct":None}}}}
        html=render(self.report(),scorecard)
        self.assertIn("Historical warning outcomes",html)
        self.assertIn("50.0%",html)
        self.assertIn("-1.25%",html)
        self.assertIn("not a backtested trading strategy",html)
    def test_no_matured_warning_outcomes(self):
        self.assertIn("No matured historical warning outcomes",render(self.report()))

    def test_chart_is_embedded_in_published_html(self):
        report=self.report()
        scorecard={"technical_chart_html":'<svg viewBox="0 0 850 370"><polyline points="0,0 1,1"/></svg>'}
        html=render(report,scorecard)
        self.assertIn("Annotated price and volume",html)
        self.assertIn('<svg viewBox="0 0 850 370">',html)
        self.assertIn("<polyline",html)
        self.assertNotIn("{{CHART}}",html)
    def test_chart_unavailable_message_is_visible(self):
        html=render(self.report())
        self.assertIn("Chart unavailable until completed-session data is processed",html)
