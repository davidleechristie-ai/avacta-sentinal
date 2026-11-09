import unittest
from datetime import date
from data_quality import assess_history

def bar(day, volume=100):
    return {"date": day, "open": 50, "high": 55, "low": 49, "close": 53, "volume": volume}

class QualityTests(unittest.TestCase):
    def test_zero_volume_flagged(self):
        result = assess_history([bar("2026-11-06", 0)], as_of=date(2026, 11, 9))
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
        self.assertIn("zero_volume", [x["issue"] for x in result["flags"]])
        self.assertFalse(result["validated_for_trading"])

    def test_missing_rows_blocked(self):
        self.assertEqual(assess_history([], as_of=date(2026, 11, 9))["status"], "BLOCKED")

    def test_recent_history_is_preliminary_not_trade_ready(self):
        rows = [bar(f"2026-10-{d:02d}") for d in range(20, 31)] + [bar("2026-11-06")]
        result = assess_history(rows, as_of=date(2026, 11, 9))
        self.assertEqual(result["status"], "PRELIMINARY")
        self.assertEqual(result["fca_short_exposure"], "NOT_ASSESSED")
        self.assertFalse(result["validated_for_trading"])
