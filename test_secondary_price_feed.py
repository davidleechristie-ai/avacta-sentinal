import io
import json
import unittest
from secondary_price_feed import fetch_secondary, SecondaryFeedUnavailable

class SecondaryPriceFeedTests(unittest.TestCase):
    def test_missing_key_fails_closed(self):
        with self.assertRaises(SecondaryFeedUnavailable):
            fetch_secondary(api_key="")
    def test_parses_and_sorts_daily_bars(self):
        payload={"meta":{"currency":"GBP"},"values":[
          {"datetime":"2026-11-09","open":"0.54","high":"0.55","low":"0.52","close":"0.53","volume":"1000"},
          {"datetime":"2026-11-06","open":"0.55","high":"0.56","low":"0.53","close":"0.538","volume":"2000"}]}
        class Response(io.BytesIO):
            def __enter__(self):return self
            def __exit__(self,*args):self.close()
        def opener(req,timeout):return Response(json.dumps(payload).encode())
        result=fetch_secondary(api_key="test",opener=opener)
        self.assertEqual(result["observations"][0]["date"],"2026-11-06")
        self.assertEqual(result["currency"],"GBP")
        self.assertFalse(result["validated_for_trading"])
    def test_provider_error_fails_closed(self):
        class Response(io.BytesIO):
            def __enter__(self):return self
            def __exit__(self,*args):self.close()
        def opener(req,timeout):return Response(b'{"status":"error","message":"quota"}')
        with self.assertRaises(SecondaryFeedUnavailable):
            fetch_secondary(api_key="test",opener=opener)
