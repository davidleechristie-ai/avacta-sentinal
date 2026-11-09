import unittest
from technical_chart import render_chart

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
