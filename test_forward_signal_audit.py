import unittest
from datetime import date,timedelta
from forward_signal_audit import audit
class ForwardAuditTests(unittest.TestCase):
    def bars(self,values):
        return [{"date":(date(2026,7,1)+timedelta(days=i)).isoformat(),
                 "open":v,"high":v+1,"low":v-1,"close":v,"volume":100} for i,v in enumerate(values)]
    def test_future_returns_not_used_for_signal(self):
        past=self.bars([70]*12+[65])
        a=audit(past)
        b=audit(past+self.bars([]))
        self.assertEqual(a["events"],b["events"])
        self.assertEqual(len(a["events"]),1)
        self.assertIsNone(a["events"][0]["future"]["5"])
    def test_forward_horizon_is_observational(self):
        a=audit(self.bars([70]*12+[65,64,63,62,61,60]))
        self.assertEqual(a["events"][0]["future"]["5"]["forward_close_return_pct"],-7.69)
        self.assertFalse(a["auto_trade"])
