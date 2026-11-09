import unittest
from fca_trends import parse,trend
def sources(current,historic):
    return {"fca_current":{"status":"MATCHED","rows":current,"headers":["Date","Position"],"source":"FCA"},"fca_historic":{"status":"MATCHED","rows":historic}}
class FcaTrendTests(unittest.TestCase):
    def test_falling(self):
        result=trend(sources([{"Date":"2026-11-06","Position":"1.11%"}],[{"Date":"2026-11-05","Position":"1.20%"}]))
        self.assertEqual(result["direction"],"FALLING")
        self.assertAlmostEqual(result["change_percentage_points"],-0.09)
    def test_rising(self):
        result=trend(sources([{"Date":"2026-11-06","Position":"1.30"}],[{"Date":"2026-11-05","Position":"1.20"}]))
        self.assertEqual(result["direction"],"RISING")
    def test_missing_previous_no_direction(self):
        result=trend(sources([{"Date":"2026-11-06","Position":"1.11"}],[]))
        self.assertEqual(result["status"],"REVIEW_REQUIRED")
    def test_missing_current_not_zero(self):
        self.assertEqual(trend({"fca_current":{"status":"NOT_LISTED"}})["status"],"UNKNOWN")
    def test_ambiguous_columns_rejected(self):
        self.assertEqual(parse([{"Date":"2026-11-06","Position":"1.11","Aggregate":"2.22"}]),[])
    def test_uk_date(self):
        self.assertEqual(parse([{"Position Date":"06/11/2026","Net Position":"1.11%"}])[0]["date"],"2026-11-06")

    def test_historic_classification_date_ignored(self):
        result=trend(sources(
            [{"Position Date":"26/10/2026","Net Position":"1.11%"}],
            [{"Position Date":"15/09/2026","Historical Date":"12/10/2026","Net Position":"0.80%"}]))
        self.assertEqual(result["direction"],"RISING")
        self.assertEqual(result["previous"]["date"],"2026-09-15")
    def test_two_unrelated_dates_without_position_date_rejected(self):
        self.assertEqual(parse([{"Report Date":"2026-11-01","Historical Date":"2026-11-05","Net Position":"1.0"}]),[])
