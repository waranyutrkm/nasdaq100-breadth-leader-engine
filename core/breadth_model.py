"""Market Breadth and Macro Regime Classification for Nasdaq-100.

Provides institutional breadth metrics (% > EMA50, EMA100, EMA200, return participation)
and macroeconomic gate conditions comparing the underlying universe to benchmark QQQ.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

REGIME_BROAD_BULL = "BROAD_BULL"
REGIME_NORMAL_BULL = "NORMAL_BULL"
REGIME_NARROW_BULL = "NARROW_BULL"
REGIME_CASH_GUARD = "CASH_GUARD"


def compute_breadth_indicators(
    close: pd.DataFrame,
    members: pd.DataFrame | None = None,
    benchmark_symbol: str = "QQQ",
) -> pd.DataFrame:
    """Compute market breadth across all available universe assets.

    Parameters
    ----------
    close : pd.DataFrame
        Adjusted close price matrix (dates x symbols).
    members : pd.DataFrame, optional
        Boolean membership mask (dates x symbols). If None, all non-benchmark columns are used.
    benchmark_symbol : str
        Ticker for benchmark (default: QQQ).

    Returns
    -------
    pd.DataFrame
        Time series of breadth percentages, dispersion, and regime indicators.
    """
    if benchmark_symbol not in close.columns:
        raise ValueError(f"Benchmark {benchmark_symbol} missing from close matrix.")

    symbols = [s for s in close.columns if s not in {benchmark_symbol, "BIL", "^NDX", "^IXIC"}]
    c_sub = close[symbols]

    if members is None:
        m_mask = pd.DataFrame(True, index=close.index, columns=symbols)
    else:
        m_mask = members.reindex(columns=symbols, fill_value=False)

    valid_mask = c_sub.notna() & m_mask

    # Calculate EMAs for each constituent
    ema50 = c_sub.ewm(span=50, adjust=False, min_periods=50).mean()
    ema100 = c_sub.ewm(span=100, adjust=False, min_periods=100).mean()
    ema200 = c_sub.ewm(span=200, adjust=False, min_periods=200).mean()

    # Returns
    r1 = c_sub.pct_change(fill_method=None)
    r21 = c_sub.pct_change(21, fill_method=None)
    r63 = c_sub.pct_change(63, fill_method=None)

    # Benchmark trend
    qqq_close = close[benchmark_symbol]
    qqq_ema100 = qqq_close.ewm(span=100, adjust=False, min_periods=100).mean()
    qqq_ema200 = qqq_close.ewm(span=200, adjust=False, min_periods=200).mean()
    qqq_trend_ok = qqq_close > qqq_ema100

    breadth = pd.DataFrame(index=close.index)

    # Eligible counts
    available_counts = valid_mask.sum(axis=1)
    breadth["universe_count"] = available_counts

    # % Above Moving Averages
    for span, ema_df in ((50, ema50), (100, ema100), (200, ema200)):
        above = (c_sub > ema_df) & valid_mask & ema_df.notna()
        breadth[f"breadth_ema{span}"] = above.sum(axis=1) / available_counts.replace(0, np.nan)

    # % Positive Returns
    for span, ret_df in ((21, r21), (63, r63)):
        pos = (ret_df > 0) & valid_mask & ret_df.notna()
        breadth[f"positive_ret{span}"] = pos.sum(axis=1) / available_counts.replace(0, np.nan)

    # Dispersion & Median Daily Return
    breadth["dispersion_daily"] = r1.where(valid_mask).std(axis=1)
    breadth["median_daily_return"] = r1.where(valid_mask).median(axis=1)

    # Benchmark metadata
    breadth["benchmark_close"] = qqq_close
    breadth["benchmark_ema100"] = qqq_ema100
    breadth["benchmark_ema200"] = qqq_ema200
    breadth["benchmark_trend_ok"] = qqq_trend_ok

    # Coverage sanity check
    breadth["coverage_ok"] = available_counts >= 70

    # Classify Regime
    regimes = []
    for dt, row in breadth.iterrows():
        regimes.append(classify_market_regime(row["benchmark_trend_ok"], row["breadth_ema50"]))
    breadth["regime"] = regimes

    return breadth


def classify_market_regime(benchmark_trend_ok: bool, breadth_ema50: float) -> str:
    """Classify regime into 4 institutional states based on trend gate and breadth.

    Parameters
    ----------
    benchmark_trend_ok : bool
        True if QQQ > EMA100.
    breadth_ema50 : float
        Fraction of constituents with Close > EMA50 (0.0 to 1.0).

    Returns
    -------
    str
        One of BROAD_BULL, NORMAL_BULL, NARROW_BULL, or CASH_GUARD.
    """
    if not benchmark_trend_ok or np.isnan(breadth_ema50) or breadth_ema50 < 0.20:
        return REGIME_CASH_GUARD
    if breadth_ema50 >= 0.55:
        return REGIME_BROAD_BULL
    if breadth_ema50 >= 0.35:
        return REGIME_NORMAL_BULL
    return REGIME_NARROW_BULL
