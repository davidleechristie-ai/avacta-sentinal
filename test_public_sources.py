import unittest
from unittest.mock import patch
from public_sources import fca_report,issuer_news,clinical_trials
from catalyst_tracker import build
class PublicSourceTests(unittest.TestCase):
    def test_fca_isin_match(self):
        with patch("public_sources.fetch",return_value="Company,ISIN,Position\nAvacta,GB00BYYW9G87,0.91\n"):
            self.assertEqual(fca_report("https://example.com")["status"],"MATCHED")
    def test_fca_not_listed_not_zero(self):
        with patch("public_sources.fetch",return_value="Company,ISIN\nOther,XX123\n"):
            r=fca_report("https://example.com")
            self.assertEqual(r["status"],"NOT_LISTED")
            self.assertIn("does not mean zero",r["note"])
    def test_html_rejected(self):
        with patch("public_sources.fetch",return_value="<html>error</html>"):
            with self.assertRaises(ValueError):fca_report("https://example.com")
    def test_news(self):
        with patch("public_sources.fetch",return_value='<a href="/ava6207-update/">Avacta AVA6207 results announced</a>'):
            self.assertEqual(issuer_news()["status"],"RETRIEVED")
    def test_registry(self):
        with patch("public_sources.fetch",return_value='{"studies":[{"protocolSection":{"identificationModule":{"nctId":"NCT12345678"}}}]}'):
            self.assertEqual(clinical_trials()["items"][0]["nct_id"],"NCT12345678")
    def test_catalyst_not_auto_verified(self):
        r=build({"avacta_news":{"items":[{"title":"AVA6207 results","url":"https://avacta.com/test"}]}})
        self.assertEqual(r["catalysts"][0]["outcome"],"UNVERIFIED")
        self.assertFalse(r["trade_signal"])
