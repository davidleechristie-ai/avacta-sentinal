import unittest
from datetime import date
from evidence_scorecard import build,short_exposure,catalyst,financing
class EvidenceTests(unittest.TestCase):
    def test_no_fca_match_is_unknown_not_zero(self):
        r=short_exposure({"fca_current":{"status":"NOT_LISTED","rows":[]}})
        self.assertEqual(r["status"],"UNKNOWN")
    def test_fca_matched_requires_trend_review(self):
        r=short_exposure({"fca_current":{"status":"MATCHED","rows":[{"Position":"1.11%"}]}})
        self.assertEqual(r["status"],"REVIEW_REQUIRED")
        self.assertEqual(r["reported_fields"][0][1],1.11)
    def test_financing_headline_not_confirmed(self):
        r=financing({"avacta_news":{"items":[{"title":"Avacta announces placing","url":"https://avacta.com/test"}]}})
        self.assertEqual(r["status"],"REVIEW_REQUIRED")
    def test_exit_deadline(self):
        r=catalyst({},{"catalysts":[]},as_of=date(2027,1,30))
        self.assertEqual(r["days_to_isa_deadline"],1)
    def test_no_trade_signal_even_when_technicals_positive(self):
        r=build({"quality":{"price_reversal":"CONFIRMED_TECHNICAL_PATTERN","sustained_volume":"CONFIRMED_2_SESSIONS"}},{})
        self.assertIsNone(r["score_0_100"])
        self.assertFalse(r["trade_signal"])
