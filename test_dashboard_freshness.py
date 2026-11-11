"""Regression tests for the published market-data freshness banner."""
import unittest
from sentinel_dashboard import render

class DashboardFreshnessTests(unittest.TestCase):
    def test_stale_probe_is_visible(self):
        report={"as_of":"2026-11-11","observed_close_pence":54,"data_quality":{"completed_session_accepted":"2026-11-10"}}
        scorecard={"market_probe":{"status":"STALE_BLOCKED","generated_at_utc":"2026-11-11T16:00:00+00:00","quality":{"last_completed_session_date":"2026-11-10","is_stale":True}}}
        html=render(report,scorecard)
        self.assertIn("STALE / UNAVAILABLE",html)
        self.assertIn("Last completed session: 2026-11-10",html)
        self.assertIn("Probe generated: 2026-11-11T16:00:00+00:00",html)
        self.assertIn("Historical completed close",html)
        self.assertIn("not a current signal",html)
    def test_missing_probe_never_appears_current(self):
        html=render({"as_of":"2026-11-11"}, {})
        self.assertIn("STALE / UNAVAILABLE",html)
        self.assertIn("Last completed session: Unknown",html)
if __name__=="__main__":
    unittest.main()
