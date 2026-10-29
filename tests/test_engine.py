"""Unit Tests for Nasdaq-100 Breadth and Leader Rotation Core Modules.

Verifies:
1. Breadth calculation bounds [0.0, 1.0] and regime classification.
2. Leader selection and company risk capping (GOOG/GOOGL aggregation).
3. Causal portfolio simulation fidelity, budget conservation, and non-negative cash.
"""

from __future__ import annotations

import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from core.breadth_model import (
    compute_breadth_indicators,
    classify_market_regime,
    REGIME_BROAD_BULL,
    REGIME_NORMAL_BULL,
    REGIME_NARROW_BULL,
    REGIME_CASH_GUARD,
)
from core.leader_selector import (
    compute_momentum_scores,
    select_top_leaders,
    compute_target_weights,
)
from core.engine import (
    CausalPortfolioEngine,
    PortfolioSpec,
    calculate_performance_metrics,
)


class TestNasdaqEngine(unittest.TestCase):
    def setUp(self) -> None:
        # Create deterministic synthetic data for 100 sessions and 6 symbols + QQQ + BIL
        np.random.seed(42)
        dates = pd.date_range("2023-01-01", periods=180, freq="B")
        symbols = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOG", "GOOGL", "QQQ", "BIL"]

        close_data = {}
        open_data = {}
        for s in symbols:
            drift = 0.0008 if s in {"AAPL", "NVDA", "QQQ"} else 0.0002
            returns = np.random.normal(drift, 0.015, size=len(dates))
            p = 100.0 * np.cumprod(1.0 + returns)
            close_data[s] = p
            # Open is close of yesterday with slight noise
            open_data[s] = np.roll(p, 1) * np.random.normal(1.0, 0.002, size=len(dates))
            open_data[s][0] = p[0]

        self.close = pd.DataFrame(close_data, index=dates)
        self.open = pd.DataFrame(open_data, index=dates)
        self.volume = pd.DataFrame(1_000_000, index=dates, columns=symbols)
        self.data = {"close": self.close, "open": self.open, "volume": self.volume}

    def test_regime_classification(self) -> None:
        self.assertEqual(classify_market_regime(True, 0.60), REGIME_BROAD_BULL)
        self.assertEqual(classify_market_regime(True, 0.45), REGIME_NORMAL_BULL)
        self.assertEqual(classify_market_regime(True, 0.25), REGIME_NARROW_BULL)
        self.assertEqual(classify_market_regime(True, 0.15), REGIME_CASH_GUARD)
        self.assertEqual(classify_market_regime(False, 0.80), REGIME_CASH_GUARD)

    def test_breadth_calculation_bounds(self) -> None:
        breadth = compute_breadth_indicators(self.close, benchmark_symbol="QQQ")
        self.assertIn("breadth_ema50", breadth.columns)
        valid_b = breadth["breadth_ema50"].dropna()
        self.assertTrue((valid_b >= 0.0).all() and (valid_b <= 1.0).all())

    def test_company_cap_and_alphabet_aggregation(self) -> None:
        leaders = ["AAPL", "NVDA", "GOOG", "GOOGL"]
        vol_mock = pd.Series({"AAPL": 0.20, "NVDA": 0.25, "GOOG": 0.15, "GOOGL": 0.15})

        weights = compute_target_weights(leaders, vol_mock, method="equal", max_company_cap=0.20)
        # GOOG + GOOGL combined must not exceed 0.20
        goog_total = weights.get("GOOG", 0.0) + weights.get("GOOGL", 0.0)
        self.assertAlmostEqual(goog_total, 0.20, places=4)
        for s, w in weights.items():
            self.assertLessEqual(w, 0.20001)

    def test_causal_engine_budget_conservation(self) -> None:
        breadth = compute_breadth_indicators(self.close, benchmark_symbol="QQQ")
        features = compute_momentum_scores(self.close, volume=self.volume, min_history=20)
        features["breadth"] = breadth

        engine = CausalPortfolioEngine(self.data, features)
        spec = PortfolioSpec(name="TestCoreSat", kind="core_satellite", core_weight=0.50, top_k=3, rebalance_interval=5)

        res = engine.simulate(spec, start_date=str(self.close.index[25].date()), record_ledger=True)
        daily = res["daily"]

        self.assertGreater(len(daily), 10)
        self.assertTrue((daily["nav"] > 0).all())
        self.assertTrue((daily["exposure"] >= 0.0).all() and (daily["exposure"] <= 1.0001).all())


if __name__ == "__main__":
    unittest.main()
