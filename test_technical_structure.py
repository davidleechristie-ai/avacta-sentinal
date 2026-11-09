import unittest
from technical_structure import assess_structure

class StructureTests(unittest.TestCase):
    def bars(self,values,volumes=None):
        return [{"date":f"2026-10-{i+1:02d}","close":v,"volume":(volumes[i] if volumes else 100)} for i,v in enumerate(values)]
    def test_breakout_volume_and_next_session_failure(self):
        vals=[50]*10+[55,49]
        result=assess_structure(self.bars(vals,[100]*10+[250,100]))
        event=next(e for e in result["events"] if e["date"]=="2026-10-11")
        self.assertEqual(event["kind"],"CLOSE_ABOVE_PRIOR_RANGE")
        self.assertEqual(event["volume_confirmation"],"SUPPORTED")
        self.assertEqual(event["next_session_status"],"FAILED_NEXT_SESSION")
        self.assertFalse(result["auto_trade"])
    def test_latest_signal_has_no_future_knowledge(self):
        result=assess_structure(self.bars([50]*10+[55]))
        self.assertEqual(result["events"][-1]["next_session_status"],"PENDING")
    def test_short_history_fails_closed(self):
        self.assertEqual(assess_structure(self.bars([50]*3))["status"],"INSUFFICIENT_DATA")
