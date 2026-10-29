#!/usr/bin/env python3
"""Run Comprehensive Historical Backtest & Institutional Audit for Nasdaq-100.

Simulates 2011–2026 performance across:
1. QQQ Buy & Hold (Benchmark)
2. BIL Buy & Hold (Risk-free Cash Benchmark)
3. Core-Satellite (50% QQQ + 50% Leader Satellite)
4. Fast-Alpha Leader (100% Top 5 Leader Rotation)
5. Legacy Adaptive Regime (Dynamic 0/70/90/95% with BIL Cash Guard)

Generates comparative performance metrics, annual returns, drawdown statistics,
and daily NAV curves, outputting to data/backtest_results.json.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.engine import (
    CausalPortfolioEngine,
    PortfolioSpec,
    calculate_performance_metrics,
)
from core.breadth_model import compute_breadth_indicators
from core.leader_selector import compute_momentum_scores

DATA_DIR = ROOT / "data"


def load_matrices() -> dict[str, pd.DataFrame]:
    fields = {}
    for key in ("close", "open", "volume"):
        fields[key] = pd.read_csv(DATA_DIR / f"{key}.csv", index_col=0, parse_dates=True)
    return fields


def run_audit(start_date: str = "2011-01-03", end_date: str = "2026-09-09") -> dict:
    print(f"[*] Running institutional backtest from {start_date} to {end_date}...")
    data = load_matrices()
    close = data["close"]
    volume = data["volume"]

    breadth = compute_breadth_indicators(close, benchmark_symbol="QQQ")
    features = compute_momentum_scores(close, volume=volume)
    features["breadth"] = breadth

    engine = CausalPortfolioEngine(data, features)

    specs = [
        PortfolioSpec(name="QQQ_Buy_Hold", kind="benchmark", benchmark_symbol="QQQ", rebalance_interval=252),
        PortfolioSpec(name="BIL_Cash", kind="benchmark", benchmark_symbol="BIL", rebalance_interval=252),
        PortfolioSpec(name="Core_Satellite_50_50", kind="core_satellite", core_weight=0.50, top_k=5, rebalance_interval=21),
        PortfolioSpec(name="Fast_Alpha_Leader", kind="leader", top_k=5, threshold=0.50, rebalance_interval=21),
        PortfolioSpec(name="Adaptive_Regime_Guard", kind="legacy_adaptive", rebalance_interval=1),
    ]

    results = {}
    nav_series = {}
    trade_logs_by_strat = {}

    for spec in specs:
        print(f"    Evaluating strategy: {spec.name}...")
        sim_res = engine.simulate(spec, start_date=start_date, end_date=end_date, cost_bps=5.0, record_ledger=True)
        daily_df = sim_res["daily"]
        metrics = sim_res["metrics"]
        trade_logs = sim_res.get("trades", [])

        # Calculate annual returns
        daily_df["year"] = daily_df.index.year
        annual_rets = {}
        for yr, grp in daily_df.groupby("year"):
            cum_yr = (1.0 + grp["daily_return"]).prod() - 1.0
            annual_rets[str(yr)] = round(cum_yr * 100, 2)

        results[spec.name] = {
            "name": spec.name,
            "cagr_pct": round(metrics.get("cagr", 0.0) * 100, 2),
            "max_dd_pct": round(metrics.get("max_drawdown", 0.0) * 100, 2),
            "sharpe_excess_bil": round(metrics.get("sharpe_excess_bil", 0.0), 3),
            "sortino": round(metrics.get("sortino", 0.0), 3),
            "calmar": round(metrics.get("calmar", 0.0), 3),
            "volatility_pct": round(metrics.get("annualized_vol", 0.0) * 100, 2),
            "alpha_vs_qqq_pct": round(metrics.get("alpha_cagr", 0.0) * 100, 2),
            "beta_vs_qqq": round(metrics.get("beta", 1.0), 2),
            "win_rate_63d_pct": round(metrics.get("win_rate_63d_vs_qqq", 0.0) * 100, 1),
            "annual_returns": annual_rets,
        }

        # Keep recent 250 trades for web timeline
        trade_logs_by_strat[spec.name] = trade_logs[-250:] if len(trade_logs) > 250 else trade_logs

        # Store downsampled NAV curve for web rendering (1 point per week to keep payload lean)
        nav_weekly = daily_df["nav"].resample("W-FRI").last().dropna()
        nav_series[spec.name] = [
            {"date": str(d.date()), "nav": round(val, 2)}
            for d, val in nav_weekly.items()
        ]

    output_payload = {
        "metadata": {
            "start_date": start_date,
            "end_date": end_date,
            "annual_trading_sessions": 252,
            "friction_bps": 5.0,
        },
        "summary_table": results,
        "nav_series": nav_series,
        "trade_logs": trade_logs_by_strat,
    }

    out_file = DATA_DIR / "backtest_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=2, ensure_ascii=False)

    print(f"[+] Successfully completed backtest audit! Saved to {out_file}")
    return output_payload


if __name__ == "__main__":
    run_audit()
