#!/usr/bin/env python3
"""Signal Generator & Daily Market Snapshot Engine for Nasdaq-100.

Computes the latest market breadth, macro regime, candidate stock rankings,
technical gate filters, and target portfolio allocations across 3 strategy presets:
1. Core-Satellite (50% QQQ Core + 50% Leader Satellite) [Recommended for US Equities]
2. Fast-Alpha Leader (100% Leader Top 5 Inverse-Vol)
3. Legacy Adaptive Regime (Dynamic 0/70/90/95% exposure + BIL Cash Guard)
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.breadth_model import (
    compute_breadth_indicators,
    REGIME_BROAD_BULL,
    REGIME_NORMAL_BULL,
    REGIME_NARROW_BULL,
    REGIME_CASH_GUARD,
)
from core.leader_selector import (
    compute_momentum_scores,
    compute_target_weights,
    select_top_leaders,
)

DATA_DIR = ROOT / "data"


def load_market_data() -> dict[str, pd.DataFrame]:
    """Load local CSV matrices."""
    fields = {}
    for key in ("close", "open", "volume"):
        p = DATA_DIR / f"{key}.csv"
        if not p.exists():
            raise FileNotFoundError(f"Required matrix {p} not found.")
        fields[key] = pd.read_csv(p, index_col=0, parse_dates=True)
    return fields


def load_universe_info() -> dict[str, dict[str, str]]:
    """Load constituent company names and sectors."""
    p = DATA_DIR / "universe_constituents.csv"
    if not p.exists():
        return {}
    df = pd.read_csv(p)
    return {
        row["ticker"]: {"name": str(row["name"]), "sector": str(row["sector"])}
        for _, row in df.iterrows()
    }


def generate_daily_snapshot() -> dict:
    """Generate complete daily signal payload."""
    data = load_market_data()
    close = data["close"]
    open_p = data["open"]
    volume = data["volume"]
    meta_info = load_universe_info()

    # Calculate breadth and features
    breadth_df = compute_breadth_indicators(close, benchmark_symbol="QQQ")
    features = compute_momentum_scores(close, volume=volume)

    latest_date = close.index[-1]
    latest_str = str(latest_date.date())

    # Extract latest row values
    latest_breadth = breadth_df.iloc[-1]
    b_ema50 = float(latest_breadth["breadth_ema50"])
    b_ema100 = float(latest_breadth["breadth_ema100"])
    b_ema200 = float(latest_breadth["breadth_ema200"])
    b_pos21 = float(latest_breadth["positive_ret21"])
    b_pos63 = float(latest_breadth["positive_ret63"])
    regime = str(latest_breadth["regime"])
    qqq_trend_ok = bool(latest_breadth["benchmark_trend_ok"])
    qqq_close = float(close["QQQ"].iloc[-1])
    qqq_ema100 = float(latest_breadth["benchmark_ema100"])
    qqq_ema200 = float(latest_breadth["benchmark_ema200"])
    bil_close = float(close["BIL"].iloc[-1]) if "BIL" in close else 1.0

    # Stock rankings on latest date
    scores_row = features["multi_score"].iloc[-1]
    trend_gate_row = features["trend_gate"].iloc[-1]
    eligible_row = features["eligible"].iloc[-1]
    vol63_row = features["vol63"].iloc[-1]
    r30_row = features["ret30"].iloc[-1]
    r60_row = features["ret60"].iloc[-1]
    r120_row = features["ret120"].iloc[-1]
    ema12_row = features["ema12"].iloc[-1]
    ema26_row = features["ema26"].iloc[-1]

    # Collect candidate stock table
    universe_symbols = [
        s for s in close.columns
        if s not in {"QQQ", "BIL", "^NDX", "^IXIC"}
        and eligible_row.get(s, False)
        and pd.notna(close[s].iloc[-1])
    ]

    stock_items = []
    for s in universe_symbols:
        c_price = float(close[s].iloc[-1])
        score_val = float(scores_row.get(s, np.nan))
        r30_val = float(r30_row.get(s, np.nan))
        r60_val = float(r60_row.get(s, np.nan))
        r120_val = float(r120_row.get(s, np.nan))
        vol_val = float(vol63_row.get(s, np.nan))
        tr_gate = bool(trend_gate_row.get(s, False))
        info = meta_info.get(s, {"name": f"{s} Corp", "sector": "Technology"})

        # Pass criteria: trend_gate + positive score + positive 30d/60d
        passes_all = tr_gate and (score_val > 0) and (r30_val > 0) and (r60_val > 0)

        stock_items.append({
            "ticker": s,
            "name": info["name"],
            "sector": info["sector"],
            "price": round(c_price, 2),
            "momentum_score": round(score_val * 100, 2) if np.isfinite(score_val) else 0.0,
            "ret30": round(r30_val * 100, 2) if np.isfinite(r30_val) else 0.0,
            "ret60": round(r60_val * 100, 2) if np.isfinite(r60_val) else 0.0,
            "ret120": round(r120_val * 100, 2) if np.isfinite(r120_val) else 0.0,
            "vol63": round(vol_val * 100, 2) if np.isfinite(vol_val) else 0.0,
            "ema12": round(float(ema12_row.get(s, 0)), 2),
            "ema26": round(float(ema26_row.get(s, 0)), 2),
            "trend_gate": tr_gate,
            "passes_all": passes_all,
            "above_ema50": bool(c_price > close[s].ewm(span=50).mean().iloc[-1]),
        })

    # Sort: passing stocks first by score descending, then remaining by score
    stock_items.sort(key=lambda x: (1 if x["passes_all"] else 0, x["momentum_score"]), reverse=True)
    for rank_idx, item in enumerate(stock_items, start=1):
        item["rank"] = rank_idx

    # Strategy 1: Core-Satellite (50% QQQ Core + 50% Leader Satellite Top 5)
    core_selected = [x["ticker"] for x in stock_items if x["passes_all"]][:5]
    if qqq_trend_ok and b_ema50 >= 0.35:
        sat_exp = 0.50
    elif qqq_trend_ok and b_ema50 >= 0.20:
        sat_exp = 0.30
    else:
        sat_exp = 0.0

    sat_weights = compute_target_weights(core_selected, vol63_row, method="invvol", max_company_cap=0.20, total_leader_exposure=sat_exp)
    core_allocations = {"QQQ": 0.50}
    for s, w in sat_weights.items():
        core_allocations[s] = round(w, 4)
    core_cash = round(max(0.0, 1.0 - sum(core_allocations.values())), 4)
    if core_cash > 0:
        core_allocations["BIL"] = core_cash

    # Strategy 2: Fast-Alpha Leader (100% Leader Top 5 Inverse-Vol)
    fast_selected = [x["ticker"] for x in stock_items if x["passes_all"]][:5]
    fast_risk_on = qqq_trend_ok and b_ema50 >= 0.50
    fast_exp = 1.0 if fast_risk_on else 0.0
    fast_weights = compute_target_weights(fast_selected, vol63_row, method="invvol", max_company_cap=0.20, total_leader_exposure=fast_exp)
    fast_allocations = {}
    for s, w in fast_weights.items():
        fast_allocations[s] = round(w, 4)
    fast_cash = round(max(0.0, 1.0 - sum(fast_allocations.values())), 4)
    if fast_cash > 0:
        fast_allocations["BIL"] = fast_cash

    # Strategy 3: Legacy Adaptive Regime (Dynamic 0/70/90/95% exposure)
    if not qqq_trend_ok or b_ema50 < 0.20:
        legacy_exp = 0.0
        legacy_k = 0
    elif b_ema50 >= 0.55:
        legacy_exp = 0.95
        legacy_k = 5
    elif b_ema50 >= 0.35:
        legacy_exp = 0.90
        legacy_k = 3
    else:
        legacy_exp = 0.70
        legacy_k = 2

    legacy_selected = [x["ticker"] for x in stock_items if x["passes_all"]][:legacy_k]
    legacy_weights = compute_target_weights(legacy_selected, vol63_row, method="invvol", max_company_cap=0.20, total_leader_exposure=legacy_exp)
    legacy_allocations = {}
    for s, w in legacy_weights.items():
        legacy_allocations[s] = round(w, 4)
    legacy_cash = round(max(0.0, 1.0 - sum(legacy_allocations.values())), 4)
    if legacy_cash > 0:
        legacy_allocations["BIL"] = legacy_cash

    # Today's Action Summary
    regime_labels = {
        REGIME_BROAD_BULL: ("BROAD BULL", "ตลาดกระทิงเต็มรูปแบบ หุ้นผู้นำขึ้นกระจายตัวกว้าง ถือหุ้นตามน้ำหนักเต็มอัตรา"),
        REGIME_NORMAL_BULL: ("NORMAL BULL", "ตลาดกระทิงปกติ กระจายตัวปานกลาง ถือหุ้นผู้นำ Top 3-5 คุมความผันผวน"),
        REGIME_NARROW_BULL: ("NARROW BULL", "ตลาดขึ้นแบบกระจุกตัวในหุ้นขนาดใหญ่ แนะนำเน้น QQQ Core เพื่อเกาะดัชนี"),
        REGIME_CASH_GUARD: ("CASH GUARD", "ตลาดมีสัญญาณเตือนหรือหลุดเทรนด์ ปรับพอร์ตถือ BIL (T-Bills) 100% ป้องกันเงินต้น"),
    }
    regime_title, regime_desc = regime_labels.get(regime, ("NEUTRAL", "รอดูความชัดเจนของสัญญาณ"))

    snapshot = {
        "metadata": {
            "last_updated_date": latest_str,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "total_constituents": len(universe_symbols),
        },
        "market_macro": {
            "qqq_close": round(qqq_close, 2),
            "qqq_ema100": round(qqq_ema100, 2),
            "qqq_ema200": round(qqq_ema200, 2),
            "qqq_trend_ok": qqq_trend_ok,
            "bil_close": round(bil_close, 2),
            "regime": regime,
            "regime_title": regime_title,
            "regime_desc": regime_desc,
        },
        "breadth": {
            "breadth_ema50_pct": round(b_ema50 * 100, 1),
            "breadth_ema100_pct": round(b_ema100 * 100, 1),
            "breadth_ema200_pct": round(b_ema200 * 100, 1),
            "positive_ret21_pct": round(b_pos21 * 100, 1),
            "positive_ret63_pct": round(b_pos63 * 100, 1),
        },
        "strategies": {
            "core_satellite": {
                "name": "Core-Satellite (50:50)",
                "description": "50% QQQ Core + 50% Top Leader Satellite (โมเดลแนะนำสำหรับตลาดหุ้นสหรัฐฯ)",
                "allocations": core_allocations,
                "selected_tickers": core_selected,
                "exposure_pct": round((1.0 - core_allocations.get("BIL", 0.0)) * 100, 1),
            },
            "fast_alpha": {
                "name": "Fast-Alpha Leader",
                "description": "100% หมุนถือเฉพาะหุ้น Top 5 ผู้นำที่แรงที่สุด ถ่วงน้ำหนัก Inverse Volatility",
                "allocations": fast_allocations,
                "selected_tickers": fast_selected,
                "exposure_pct": round((1.0 - fast_allocations.get("BIL", 0.0)) * 100, 1),
            },
            "legacy_adaptive": {
                "name": "Adaptive Regime Guard",
                "description": "ปรับสัดส่วนถือครองตามเกณฑ์ความกว้างตลาด (0% / 70% / 90% / 95%)",
                "allocations": legacy_allocations,
                "selected_tickers": legacy_selected,
                "exposure_pct": round((1.0 - legacy_allocations.get("BIL", 0.0)) * 100, 1),
            },
        },
        "stock_rankings": stock_items,
    }

    out_json = DATA_DIR / "latest_market_snapshot.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)

    print(f"[+] Successfully generated latest daily snapshot! Date: {latest_str} | Regime: {regime} | Breadth EMA50: {round(b_ema50*100, 1)}%")
    return snapshot


if __name__ == "__main__":
    generate_daily_snapshot()
