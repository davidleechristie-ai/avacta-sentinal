import unittest
from technical_chart import render_chart, weekly_bars

class TechnicalChartTests(unittest.TestCase):
    def test_renders_prices_volume_and_levels(self):
        bars=[{"date":f"2026-11-{i:02d}","close":50+i,"volume":100*i} for i in range(1,5)]
        html=render_chart(bars,{"overhead_resistance":[{"level_pence":60}]})
        self.assertIn("<svg",html)
        self.assertIn("Overhead 60.0p",html)
        self.assertIn("<rect",html)
        self.assertNotIn("<script",html)
    def test_missing_data_fails_closed(self):
        self.assertIn("Insufficient",render_chart([]))
    def test_bad_level_ignored(self):
        bars=[{"date":f"2026-11-{i:02d}","close":50+i,"volume":100} for i in range(1,5)]
        html=render_chart(bars,{"overhead_resistance":[{"level_pence":"not-a-number"}]})
        self.assertIn("<svg",html)

    def test_weekly_aggregation_uses_last_close_and_sums_volume(self):
        bars=[{"date":"2026-11-02","close":60,"volume":100},
              {"date":"2026-11-06","close":55,"volume":200},
              {"date":"2026-11-09","close":56,"volume":300}]
        weeks=weekly_bars(bars)
        self.assertEqual(len(weeks),2)
        self.assertEqual(weeks[0]["close"],55)
        self.assertEqual(weeks[0]["volume"],300)
        self.assertEqual(weeks[1]["sessions"],1)
