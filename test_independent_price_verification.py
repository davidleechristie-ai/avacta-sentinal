import unittest
from independent_price_verification import verify
class IndependentVerificationTests(unittest.TestCase):
    def bar(self):
        return {"date":"2026-11-06","open":55,"high":56,"low":53,"close":53.8,"volume":100000}
    def test_matching_distinct_providers(self):
        x=verify([self.bar()],[self.bar()],"primary","secondary")
        self.assertEqual(x["status"],"MATCHED")
        self.assertFalse(x["validated_for_trading"])
    def test_same_provider_not_independent(self):
        self.assertNotEqual(verify([self.bar()],[self.bar()],"Yahoo","yahoo")["status"],"MATCHED")
    def test_volume_disagreement(self):
        other=self.bar();other["volume"]=50000
        self.assertNotEqual(verify([self.bar()],[other],"one","two")["status"],"MATCHED")
    def test_missing_provider(self):
        self.assertEqual(verify([self.bar()],None,"one",None)["status"],"NOT_VERIFIED")
    def test_session_mismatch(self):
        other=self.bar();other["date"]="2026-11-05"
        self.assertNotEqual(verify([self.bar()],[other],"one","two")["status"],"MATCHED")
