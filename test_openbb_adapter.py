import unittest
from unittest.mock import patch
import openbb_adapter

class AdapterTests(unittest.TestCase):
    def test_sdk_unavailable_fails_closed(self):
        with patch.dict("sys.modules", {"openbb": None}):
            with self.assertRaises(openbb_adapter.ProviderUnavailable):
                openbb_adapter.fetch_avct_history()
    def test_default_instrument_is_avct_l(self):
        self.assertEqual(openbb_adapter.fetch_avct_history.__defaults__[0], "2026-10-01")

if __name__ == "__main__":
    unittest.main()
