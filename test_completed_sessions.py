import unittest
from datetime import datetime
from zoneinfo import ZoneInfo
from completed_sessions import completed_rows
from downside_guard import assess
class CompletedSessionTests(unittest.TestCase):
    def test_provisional_does_not_hide_prior_critical(self):
        now=datetime(2026,11,9,12,tzinfo=ZoneInfo("Europe/London"))
        values=[70]*12+[68,66,63,60,56,53]
        rows=[{"date":f"2026-10-{i+10:02d}","open":v,"high":v+1,"low":v-1,"close":v,"volume":1000} for i,v in enumerate(values)]
        rows.append({"date":"2026-11-09","open":54,"high":56,"low":50,"close":55,"volume":1000})
        completed,latest,gate=completed_rows(rows,now)
        self.assertEqual(latest,"2026-11-09")
        self.assertEqual(gate["status"],"PROVISIONAL")
        self.assertEqual(len(completed),len(values))
        self.assertEqual(assess(completed)["severity"],"CRITICAL")
    def test_all_provisional_returns_no_confirmed_rows(self):
        now=datetime(2026,11,9,10,tzinfo=ZoneInfo("Europe/London"))
        completed,_,_=completed_rows([{"date":"2026-11-09"}],now)
        self.assertEqual(completed,[])
