import unittest
from datetime import datetime
from zoneinfo import ZoneInfo
from session_gate import session_gate
from risk_event import build_event
class DeliverySafetyTests(unittest.TestCase):
    def test_intraday_provisional(self):
        now=datetime(2026,11,9,12,0,tzinfo=ZoneInfo("Europe/London"))
        self.assertEqual(session_gate("2026-11-09",now)["status"],"PROVISIONAL")
    def test_completed_session(self):
        now=datetime(2026,11,9,18,0,tzinfo=ZoneInfo("Europe/London"))
        self.assertEqual(session_gate("2026-11-09",now)["status"],"ACCEPTED")
    def test_stale(self):
        now=datetime(2026,11,9,18,0,tzinfo=ZoneInfo("Europe/London"))
        self.assertEqual(session_gate("2026-11-01",now)["status"],"STALE")
    def test_event_deterministic(self):
        x={"severity":"HIGH","latest_session":"2026-11-06","warnings":["BREAK","DRAWDOWN"]}
        self.assertEqual(build_event(x)["event_id"],build_event(x)["event_id"])
    def test_unknown_cannot_create_event(self):
        self.assertEqual(build_event({"severity":"UNKNOWN"})["status"],"NO_ACTIONABLE_RISK_EVENT")
