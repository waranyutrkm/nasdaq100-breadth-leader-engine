"""Leader Selection, Momentum Scoring, and Risk-Capped Weight Allocation.

Selects top-performing Nasdaq-100 constituents based on multi-scale momentum,
applies single-asset technical gates, rank hysteresis buffers, and calculates
inverse-volatility or equal-weight target allocations with strict 20% company caps.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

ANNUAL_TRADING_DAYS = 252


def compute_momentum_scores(
    close: pd.DataFrame,
    volume: pd.DataFrame | None = None,
    min_history: int = 150,
) -> dict[str, pd.DataFrame]:
    """Compute multi-scale momentum scores, technical gates, and realized volatility.

    Parameters
    ----------
    close : pd.DataFrame
        Adjusted close price matrix.
    volume : pd.DataFrame, optional
        Volume matrix for liquidity verification.
    min_history : int
        Minimum non-NaN sessions required for candidate consideration.

    Returns
    -------
    dict[str, pd.DataFrame]
        Dictionary with keys: 'multi_score', 'ret30', 'ret60', 'ret120', 'ret63', 'ret126',
        'vol63', 'trend_gate', 'eligible'.
    """
    valid = close.notna()
    history_ok = valid.rolling(min_history, min_periods=min_history).sum().eq(min_history)

    if volume is not None:
        eligible = history_ok & (volume > 0)
    else:
        eligible = history_ok

    # EMAs for technical gate
    ema12 = close.ewm(span=12, adjust=False, min_periods=12).mean()
    ema26 = close.ewm(span=26, adjust=False, min_periods=26).mean()
    trend_gate = (close > ema26) & (ema12 > ema26)

    # Returns
    r30 = close.pct_change(30, fill_method=None)
    r60 = close.pct_change(60, fill_method=None)
    r120 = close.pct_change(120, fill_method=None)
    r63 = close.pct_change(63, fill_method=None)
    r126 = close.pct_change(126, fill_method=None)

    # Multi-scale score: 50% R30 + 30% R60 + 20% R120
    multi_score = 0.50 * r30 + 0.30 * r60 + 0.20 * r120

    # 63-day realized volatility (annualized)
    daily_returns = close.pct_change(fill_method=None)
    vol63 = daily_returns.rolling(63, min_periods=40).std() * np.sqrt(ANNUAL_TRADING_DAYS)

    return {
        "multi_score": multi_score,
        "ret30": r30,
        "ret60": r60,
        "ret120": r120,
        "ret63": r63,
        "ret126": r126,
        "vol63": vol63,
        "trend_gate": trend_gate,
        "eligible": eligible,
        "ema12": ema12,
        "ema26": ema26,
    }


def select_top_leaders(
    scores_row: pd.Series,
    trend_gate_row: pd.Series,
    eligible_row: pd.Series,
    top_k: int = 5,
    prior_selected: list[str] | None = None,
    buffer_ratio: float = 0.50,
    r30_row: pd.Series | None = None,
    r60_row: pd.Series | None = None,
    excluded_symbols: set[str] | None = None,
) -> list[str]:
    """Select Top-K leaders applying technical gates and rank hysteresis buffer.

    Parameters
    ----------
    scores_row : pd.Series
        Momentum score for each symbol on the decision date.
    trend_gate_row : pd.Series
        Boolean gate (Close > EMA26 & EMA12 > EMA26).
    eligible_row : pd.Series
        Boolean eligibility (has history & volume).
    top_k : int
        Number of leaders to select.
    prior_selected : list[str], optional
        Symbols currently held from previous period.
    buffer_ratio : float
        Hysteresis buffer (e.g. 0.50 allows holding up to rank ceil(K * 1.5)).
    r30_row : pd.Series, optional
        30-day return filter (must be > 0).
    r60_row : pd.Series, optional
        60-day return filter (must be > 0).
    excluded_symbols : set[str], optional
        Symbols to exclude (e.g. QQQ, BIL, ^NDX).

    Returns
    -------
    list[str]
        Ordered list of selected leader symbols (length <= top_k).
    """
    if excluded_symbols is None:
        excluded_symbols = {"QQQ", "BIL", "^NDX", "^IXIC"}

    symbols = [s for s in scores_row.index if s not in excluded_symbols]

    mask = eligible_row[symbols] & trend_gate_row[symbols] & (scores_row[symbols] > 0)
    if r30_row is not None:
        mask &= (r30_row[symbols] > 0)
    if r60_row is not None:
        mask &= (r60_row[symbols] > 0)

    passing_symbols = [s for s in symbols if mask.get(s, False)]
    if not passing_symbols:
        return []

    # Sort passing symbols descending by momentum score
    passing_scores = scores_row[passing_symbols]
    ranked = passing_scores.sort_values(ascending=False).index.tolist()

    if not prior_selected:
        return ranked[:top_k]

    # Apply rank buffer: keep prior holdings if they remain in top buffer limit
    max_retained_rank = int(np.ceil(top_k * (1.0 + buffer_ratio)))
    retained_buffer = set(ranked[:max_retained_rank])

    kept = [s for s in prior_selected if s in retained_buffer]
    candidates = [s for s in ranked if s not in kept]

    selected = (kept + candidates)[:top_k]
    return selected


def compute_target_weights(
    selected_symbols: list[str],
    vol63_row: pd.Series,
    method: str = "invvol",
    max_company_cap: float = 0.20,
    total_leader_exposure: float = 1.0,
) -> dict[str, float]:
    """Compute risk-weighted target allocations with company-level capping.

    Parameters
    ----------
    selected_symbols : list[str]
        List of selected leader tickers.
    vol63_row : pd.Series
        Realized volatility for each symbol.
    method : str
        'invvol' (Inverse Volatility) or 'equal' (Equal Weighting).
    max_company_cap : float
        Maximum fraction of leader sleeve any single company may occupy (default: 0.20).
    total_leader_exposure : float
        Scalar multiplier for total sleeve exposure (e.g. 0.95 or 0.50).

    Returns
    -------
    dict[str, float]
        Dictionary of symbol -> target portfolio weight.
    """
    if not selected_symbols or total_leader_exposure <= 0:
        return {}

    weights: dict[str, float] = {}

    if method == "equal":
        w = 1.0 / len(selected_symbols)
        for s in selected_symbols:
            weights[s] = w
    else:
        # Inverse Volatility: w_i \propto 1 / max(vol, 0.05)
        raw_inv = {}
        for s in selected_symbols:
            v = vol63_row.get(s, np.nan)
            if np.isnan(v) or v <= 0:
                v = 0.30  # Default equity fallback volatility
            v = max(v, 0.05)
            raw_inv[s] = 1.0 / v

        tot_inv = sum(raw_inv.values())
        for s in selected_symbols:
            weights[s] = raw_inv[s] / tot_inv

    # Apply single-security cap
    for s in selected_symbols:
        weights[s] = min(weights[s], max_company_cap)

    # Check and aggregate Alphabet class shares (GOOG and GOOGL)
    goog_symbols = [s for s in selected_symbols if s in {"GOOG", "GOOGL"}]
    if len(goog_symbols) > 1:
        goog_sum = sum(weights[s] for s in goog_symbols)
        if goog_sum > max_company_cap:
            scale = max_company_cap / goog_sum
            for s in goog_symbols:
                weights[s] *= scale

    # Re-normalize only up to sum <= 1.0 while strictly enforcing max_company_cap
    # Residual unallocated weight will remain in cash/BIL
    for s in selected_symbols:
        weights[s] = min(weights[s], max_company_cap)

    # Scale by total leader exposure
    final_weights = {s: float(w * total_leader_exposure) for s, w in weights.items()}
    return final_weights
