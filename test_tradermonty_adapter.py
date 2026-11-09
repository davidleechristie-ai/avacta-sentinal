import unittest
from tradermonty_adapter import size_proposal
class TraderMontyAdapterTests(unittest.TestCase):
    def test_pence_to_gbp_conversion(self):
        result=size_proposal(10000,60,55,1)
        self.assertEqual(result["status"],"RESEARCH_PROPOSAL")
        self.assertEqual(result["currency"],"GBP")
        self.assertFalse(result["auto_trade"])
        self.assertEqual(result["result"]["final_recommended_shares"],2000)
    def test_invalid_stop_rejected(self):
        self.assertEqual(size_proposal(10000,55,60)["status"],"REVIEW_REQUIRED")
    def test_over_two_percent_risk_rejected(self):
        self.assertEqual(size_proposal(10000,60,55,3)["status"],"REVIEW_REQUIRED")
