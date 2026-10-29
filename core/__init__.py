"""Nasdaq-100 Breadth & Leader Rotation Engine Core Package.

Institutional-grade quantitative momentum, market breadth, and causal portfolio engine
tailored for US equities and the Nasdaq-100 universe.
"""

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
    simulate_portfolio,
    calculate_performance_metrics,
)

__all__ = [
    "compute_breadth_indicators",
    "classify_market_regime",
    "REGIME_BROAD_BULL",
    "REGIME_NORMAL_BULL",
    "REGIME_NARROW_BULL",
    "REGIME_CASH_GUARD",
    "compute_momentum_scores",
    "select_top_leaders",
    "compute_target_weights",
    "CausalPortfolioEngine",
    "PortfolioSpec",
    "simulate_portfolio",
    "calculate_performance_metrics",
]
