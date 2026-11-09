import unittest
from risk_transition import transition
class TransitionTests(unittest.TestCase):
    def bars(self,closes):
        from datetime import date,timedelta
        return [{"date":(date(2026,10,1)+timedelta(days=i)).isoformat(),
                 "open":v,"high":v+1,"low":v-1,"close":v,"volume":100} for i,v in enumerate(closes)]
    def test_first_break_is_escalation(self):
        r=transition(self.bars([70]*12+[65]))
        self.assertEqual(r["status"],"NEW_ESCALATION")
    def test_persistent_break_is_not_new_escalation(self):
        r=transition(self.bars([70]*12+[65,64]))
        self.assertEqual(r["status"],"PERSISTENT_RISK")
