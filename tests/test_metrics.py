"""Synthetic calculation examples; these are NOT market prices."""
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from clean import clean_prices


def fixture(values=(100, 110, 99), symbol="TEST"):
    return pd.DataFrame([dict(symbol=symbol, date=date, open=p, high=p + 1,
                              low=p * 0.9, close=p, adj_close=p, volume=100)
        for date, p in zip(pd.bdate_range("2025-01-01", periods=len(values)), values)])


class MetricsTests(unittest.TestCase):
    def test_returns_and_risk(self):
        daily, summary, _ = clean_prices(fixture())
        self.assertTrue(pd.isna(daily.daily_return.iloc[0]))
        np.testing.assert_allclose(daily.daily_return.iloc[1:], [0.1, -0.1])
        self.assertAlmostEqual(summary.period_return.iloc[0], -0.01)
        self.assertAlmostEqual(summary.max_drawdown.iloc[0], -0.1)
        self.assertAlmostEqual(summary.annualized_volatility.iloc[0], np.std([.1, -.1], ddof=1) * np.sqrt(252))

    def test_grouping_sorting_and_exact_duplicates(self):
        raw = pd.concat([fixture(), fixture((10, 20, 40), "OTHER"), fixture().iloc[[0]]])
        daily, _, report = clean_prices(raw.sample(frac=1, random_state=3))
        self.assertEqual(report["exact_duplicates_removed"], 1)
        self.assertTrue(daily.groupby("symbol").head(1).daily_return.isna().all())
        np.testing.assert_allclose(daily[daily.symbol == "OTHER"].daily_return.iloc[1:], [1, 1])

    def test_full_moving_average_window(self):
        daily, _, _ = clean_prices(fixture(tuple(range(1, 32))))
        self.assertTrue(daily.ma30.iloc[:29].isna().all())
        self.assertAlmostEqual(daily.ma30.iloc[29], 15.5)
        self.assertAlmostEqual(daily.ma30.iloc[30], 16.5)

    def test_rejects_missing_price_conflict_and_bad_range(self):
        missing = fixture()
        missing.loc[0, "adj_close"] = np.nan
        conflict = pd.concat([fixture(), fixture().iloc[[0]].assign(volume=101)])
        bad_range = fixture()
        bad_range.loc[0, "high"] = 50
        for raw in (missing, conflict, bad_range):
            with self.subTest():
                with self.assertRaises(ValueError):
                    clean_prices(raw)

    def test_rejects_mismatched_dates(self):
        with self.assertRaisesRegex(ValueError, "different dates"):
            clean_prices(pd.concat([fixture(), fixture(symbol="OTHER").iloc[1:]]))


if __name__ == "__main__":
    unittest.main()
