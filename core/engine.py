"""Causal Portfolio Engine for Nasdaq-100 Breadth and Leader Rotation.

Implements realistic point-in-time institutional accounting:
1. Causal timing: Signals generated at Close[t] -> Filled at Next Open[t+1].
2. Overnight drift: Opening gaps earned only by existing positions.
3. Realistic frictions: Bid-ask spread, commissions, and slippage on both buy and sell notionals.
4. Cash reserve: Residual liquidity stored in BIL (US Treasury Bill ETF) earning risk-free yield.
5. Strict constraints: Zero leverage, non-negative cash, 20% company-level caps.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ANNUAL_SESSIONS = 252
INITIAL_CAPITAL = 100_000.0


@dataclass(frozen=True)
class PortfolioSpec:
    name: str
    kind: str = "leader"          # 'leader', 'core_satellite', 'legacy_adaptive', 'timing', 'benchmark'
    benchmark_symbol: str = "QQQ"
    cash_symbol: str = "BIL"
    top_k: int = 5
    threshold: float = 0.50       # Breadth threshold for macro gate
    rebalance_interval: int = 21  # Trading sessions between periodic rebalances
    weighting: str = "invvol"     # 'invvol' or 'equal'
    core_weight: float = 0.0      # E.g. 0.50 for 50% QQQ Core + 50% Satellite
    buffer_ratio: float = 0.50    # Hysteresis rank buffer ratio
    company_cap: float = 0.20     # Max weight per company
    cost_bps: float = 5.0         # 5 bps one-way trading friction


class CausalPortfolioEngine:
    """Institutional-grade backtest and simulation engine."""

    def __init__(self, data: dict[str, pd.DataFrame], features_dict: dict[str, Any]) -> None:
        self.open = data["open"]
        self.close = data["close"]
        self.symbols = list(self.close.columns)
        self.dates = self.close.index
        self.features = features_dict
        self.ix = {s: i for i, s in enumerate(self.symbols)}

    def simulate(
        self,
        spec: PortfolioSpec,
        start_date: str = "2011-01-03",
        end_date: str | None = None,
        cost_bps: float | None = None,
        record_ledger: bool = True,
    ) -> dict[str, Any]:
        """Run daily simulation step-by-step."""
        cost = spec.cost_bps if cost_bps is None else cost_bps
        cost_rate = cost / 10_000.0

        dates = self.dates
        symbols = self.symbols
        n_symbols = len(symbols)

        o = self.open.to_numpy()
        c = self.close.to_numpy()

        cash_ix = self.ix[spec.cash_symbol]
        bench_ix = self.ix[spec.benchmark_symbol]

        breadth_df = self.features["breadth"]
        breadth_ema50 = breadth_df["breadth_ema50"].to_numpy()
        bench_trend = breadth_df["benchmark_trend_ok"].to_numpy()
        coverage_ok = breadth_df["coverage_ok"].to_numpy()

        scores = self.features["multi_score"].to_numpy()
        trend_gate = self.features["trend_gate"].to_numpy()
        eligible = self.features["eligible"].to_numpy()
        vols = self.features["vol63"].to_numpy()
        r30 = self.features["ret30"].to_numpy()
        r60 = self.features["ret60"].to_numpy()

        start_i = max(int(dates.searchsorted(pd.Timestamp(start_date))), 1)
        stop_i = len(dates) if end_date is None else int(dates.searchsorted(pd.Timestamp(end_date), side="right"))

        values = np.zeros(n_symbols, dtype=float)
        free_cash = INITIAL_CAPITAL
        previous_nav = INITIAL_CAPITAL

        daily_rows: list[dict[str, Any]] = []
        trade_logs: list[dict[str, Any]] = []
        prior_selected: list[int] = []
        prior_exposure: float = 0.0

        for i in range(start_i, stop_i):
            s = i - 1  # Signal evaluated at Close of yesterday (s)

            # 1. Determine Target Exposure & Macro Regime
            is_risk_on = bool(bench_trend[s] and coverage_ok[s] and breadth_ema50[s] >= spec.threshold)

            if spec.kind == "benchmark":
                target_exposure = 1.0
                k = 0
            elif spec.kind == "timing":
                target_exposure = float(bench_trend[s] and coverage_ok[s])
                k = 0
            elif spec.kind == "legacy_adaptive":
                # Adaptive 4-tiered regime exposure
                if not bench_trend[s] or not coverage_ok[s] or breadth_ema50[s] < 0.20:
                    target_exposure = 0.0
                    k = 0
                elif breadth_ema50[s] >= 0.55:
                    target_exposure = 0.95
                    k = 5
                elif breadth_ema50[s] >= 0.35:
                    target_exposure = 0.90
                    k = 3
                else:
                    target_exposure = 0.70
                    k = 2
            elif spec.kind == "core_satellite":
                # E.g. 50% QQQ Core + 50% Leader Satellite
                target_satellite = float(is_risk_on)
                target_exposure = spec.core_weight + (1.0 - spec.core_weight) * target_satellite
                k = spec.top_k
            else:  # 'leader' pure
                target_exposure = float(is_risk_on)
                k = spec.top_k

            # 2. Holdings gap from overnight close[i-1] -> open[i]
            gap = np.divide(o[i], c[s], out=np.ones_like(values), where=np.isfinite(o[i]) & np.isfinite(c[s]))
            values *= gap
            nav_open = values.sum() + free_cash

            # 3. Check Rebalance Trigger
            is_regular_rebal = (s % spec.rebalance_interval == 0)
            exposure_changed = abs(target_exposure - prior_exposure) > 1e-4
            needs_rebalance = is_regular_rebal or exposure_changed or (i == start_i)

            fee = 0.0
            turnover = 0.0

            if needs_rebalance:
                target = np.zeros(n_symbols, dtype=float)

                if spec.kind == "benchmark":
                    target[bench_ix] = 1.0
                elif spec.kind == "timing":
                    target[bench_ix] = target_exposure
                elif spec.kind == "core_satellite":
                    # Core portion
                    target[bench_ix] = spec.core_weight
                    # Satellite portion
                    satellite_exp = (1.0 - spec.core_weight) * (1.0 if is_risk_on else 0.0)
                    if satellite_exp > 0 and k > 0:
                        tradable = np.isfinite(o[i]) & (o[i] > 0)
                        valid = eligible[s] & trend_gate[s] & (scores[s] > 0) & (r30[s] > 0) & (r60[s] > 0) & tradable
                        candidates = np.flatnonzero(valid)
                        if len(candidates) > 0:
                            ranked = candidates[np.argsort(-scores[s, candidates], kind="stable")].tolist()
                            buffer_limit = int(np.ceil(k * (1.0 + spec.buffer_ratio)))
                            kept = [j for j in prior_selected if j in ranked[:buffer_limit]]
                            selected = (kept + [j for j in ranked if j not in kept])[:k]
                            prior_selected = selected

                            if selected:
                                raw = np.zeros(n_symbols, dtype=float)
                                if spec.weighting == "equal":
                                    raw[selected] = 1.0
                                else:
                                    raw[selected] = 1.0 / np.maximum(vols[s, selected], 0.05)

                                tot_r = raw.sum()
                                if tot_r > 0:
                                    w = np.minimum(raw / tot_r, spec.company_cap)
                                    # GOOG/GOOGL combination check
                                    goog_ix = [self.ix[x] for x in ("GOOG", "GOOGL") if x in self.ix]
                                    if len(goog_ix) > 1 and w[goog_ix].sum() > spec.company_cap:
                                        w[goog_ix] *= spec.company_cap / w[goog_ix].sum()
                                    target += w * satellite_exp
                    else:
                        prior_selected = []
                elif target_exposure > 0 and k > 0:
                    # Pure leader or legacy adaptive
                    tradable = np.isfinite(o[i]) & (o[i] > 0)
                    valid = eligible[s] & trend_gate[s] & (scores[s] > 0) & (r30[s] > 0) & (r60[s] > 0) & tradable
                    candidates = np.flatnonzero(valid)
                    if len(candidates) > 0:
                        ranked = candidates[np.argsort(-scores[s, candidates], kind="stable")].tolist()
                        buffer_limit = int(np.ceil(k * (1.0 + spec.buffer_ratio)))
                        kept = [j for j in prior_selected if j in ranked[:buffer_limit]]
                        selected = (kept + [j for j in ranked if j not in kept])[:k]
                        prior_selected = selected

                        if selected:
                            raw = np.zeros(n_symbols, dtype=float)
                            if spec.weighting == "equal":
                                raw[selected] = 1.0
                            else:
                                raw[selected] = 1.0 / np.maximum(vols[s, selected], 0.05)

                            tot_r = raw.sum()
                            if tot_r > 0:
                                w = np.minimum(raw / tot_r, spec.company_cap)
                                goog_ix = [self.ix[x] for x in ("GOOG", "GOOGL") if x in self.ix]
                                if len(goog_ix) > 1 and w[goog_ix].sum() > spec.company_cap:
                                    w[goog_ix] *= spec.company_cap / w[goog_ix].sum()
                                target = w * target_exposure
                else:
                    prior_selected = []

                # Cash allocated to BIL
                target[cash_ix] = max(0.0, 1.0 - target.sum())
                if target.sum() > 0:
                    target /= target.sum()

                # Solve post-fee NAV using fixed point
                nav_after = nav_open
                for _ in range(8):
                    delta = target * nav_after - values
                    fee = float(np.abs(delta).sum() * cost_rate)
                    nav_after = nav_open - fee

                delta = target * nav_after - values
                fee = float(np.abs(delta).sum() * cost_rate)
                turnover = float(np.abs(delta).sum() / nav_open) if nav_open > 0 else 0.0

                values = target * nav_after
                free_cash = float(nav_open - fee - values.sum())

                if record_ledger:
                    regime_str = str(breadth_df["regime"].iloc[s])
                    for j in np.flatnonzero(np.abs(delta) > 5.0):
                        sym = symbols[j]
                        is_buy = delta[j] > 0
                        if is_buy:
                            if sym == spec.benchmark_symbol:
                                reason = "BUY_CORE (ถือครองแกนหลักตามสัดส่วน Core 50%)"
                            elif sym == spec.cash_symbol:
                                reason = "PARK_CASH (พักสภาพคล่องใน BIL รับดอกเบี้ยระยะสั้น)"
                            else:
                                reason = f"BUY_LEADER (เข้าซื้อหุ้นผู้นำตามคะแนนโมเมนตัมและ Inverse Vol)"
                        else:
                            if target_exposure <= 0.05:
                                reason = "EXIT_CASH_GUARD (ขายล้างพอร์ตเข้า BIL เพื่อป้องกันเงินต้น)"
                            elif sym not in (selected if 'selected' in locals() and selected else []):
                                reason = "EXIT_HYSTERESIS_DROP (ขายออกหลังหุ้นเดิมตกอันดับเกินขอบเขตบัฟเฟอร์)"
                            else:
                                reason = "REBALANCE_TRIM (ปรับลดสัดส่วนตามรอบคำนวณความผันผวน)"

                        trade_logs.append({
                            "fill_date": str(dates[i].date()),
                            "signal_date": str(dates[s].date()),
                            "symbol": sym,
                            "action": "BUY" if is_buy else "SELL",
                            "notional": float(abs(delta[j])),
                            "price": float(o[i, j]),
                            "weight": float(values[j] / (nav_after if nav_after > 0 else 1.0)),
                            "fee": float(abs(delta[j]) * cost_rate),
                            "reason": reason,
                            "regime": regime_str,
                            "nav": float(nav_after),
                        })

                prior_exposure = target_exposure

            # 4. Intraday price movement open[i] -> close[i]
            intraday = np.divide(c[i], o[i], out=np.ones_like(values), where=np.isfinite(c[i]) & np.isfinite(o[i]))
            values *= intraday
            nav = float(values.sum() + free_cash)

            daily_return = (nav / previous_nav - 1.0) if previous_nav > 0 else 0.0
            equity_exposure = float(1.0 - values[cash_ix] / nav) if nav > 0 else 0.0

            daily_rows.append({
                "date": dates[i],
                "nav": nav,
                "daily_return": daily_return,
                "exposure": equity_exposure,
                "fee": fee,
                "turnover": turnover,
                "breadth_ema50": float(breadth_ema50[s]),
                "regime": breadth_df["regime"].iloc[s],
            })
            previous_nav = nav

        daily_df = pd.DataFrame(daily_rows).set_index("date")
        metrics = calculate_performance_metrics(
            daily_df["daily_return"],
            self.close[spec.benchmark_symbol].pct_change().reindex(daily_df.index).fillna(0.0),
            self.close[spec.cash_symbol].pct_change().reindex(daily_df.index).fillna(0.0),
        )

        return {
            "spec": asdict(spec),
            "daily": daily_df,
            "metrics": metrics,
            "trades": trade_logs,
        }


def calculate_performance_metrics(
    daily_returns: pd.Series,
    benchmark_returns: pd.Series,
    cash_returns: pd.Series,
) -> dict[str, Any]:
    """Calculate institutional performance, risk, and drawdowns."""
    r = daily_returns.dropna().astype(float)
    bench_r = benchmark_returns.reindex(r.index).fillna(0.0).astype(float)
    cash_r = cash_returns.reindex(r.index).fillna(0.0).astype(float)

    n_days = len(r)
    if n_days < 5:
        return {}

    years = n_days / ANNUAL_SESSIONS
    cum = (1.0 + r).cumprod()
    cagr = float(cum.iloc[-1] ** (1.0 / years) - 1.0) if years > 0 and cum.iloc[-1] > 0 else 0.0

    peak = cum.cummax()
    dd = (cum - peak) / peak
    max_dd = float(dd.min())

    excess_cash = r - cash_r
    excess_mean = float(excess_cash.mean() * ANNUAL_SESSIONS)
    vol = float(r.std() * np.sqrt(ANNUAL_SESSIONS))
    sharpe_excess_bil = float(excess_mean / vol) if vol > 1e-8 else 0.0

    downside = r[r < 0]
    downside_vol = float(downside.std() * np.sqrt(ANNUAL_SESSIONS)) if len(downside) > 1 else vol
    sortino = float(excess_mean / downside_vol) if downside_vol > 1e-8 else 0.0

    calmar = float(cagr / abs(max_dd)) if abs(max_dd) > 1e-6 else 0.0

    # Benchmark metrics
    bench_cum = (1.0 + bench_r).cumprod()
    bench_cagr = float(bench_cum.iloc[-1] ** (1.0 / years) - 1.0) if years > 0 and bench_cum.iloc[-1] > 0 else 0.0
    bench_peak = bench_cum.cummax()
    bench_dd = (bench_cum - bench_peak) / bench_peak
    bench_max_dd = float(bench_dd.min())

    # Beta vs Benchmark
    cov_matrix = np.cov(r, bench_r)
    beta = float(cov_matrix[0, 1] / cov_matrix[1, 1]) if cov_matrix[1, 1] > 1e-8 else 1.0

    # Win rate vs Benchmark on 63-day rolling
    roll_strat = cum.pct_change(63).dropna()
    roll_bench = bench_cum.pct_change(63).dropna()
    common_idx = roll_strat.index.intersection(roll_bench.index)
    win_rate_63d = float((roll_strat.loc[common_idx] > roll_bench.loc[common_idx]).mean()) if len(common_idx) > 0 else 0.0

    return {
        "cagr": cagr,
        "max_drawdown": max_dd,
        "sharpe_excess_bil": sharpe_excess_bil,
        "sortino": sortino,
        "calmar": calmar,
        "annualized_vol": vol,
        "benchmark_cagr": bench_cagr,
        "benchmark_max_drawdown": bench_max_dd,
        "alpha_cagr": cagr - bench_cagr,
        "beta": beta,
        "win_rate_63d_vs_qqq": win_rate_63d,
        "total_trading_days": n_days,
    }


def simulate_portfolio(data: dict[str, pd.DataFrame], spec: PortfolioSpec, **kwargs: Any) -> dict[str, Any]:
    """Convenience helper to compute features and run engine."""
    from core.breadth_model import compute_breadth_indicators
    from core.leader_selector import compute_momentum_scores

    close = data["close"]
    volume = data.get("volume")
    breadth = compute_breadth_indicators(close, benchmark_symbol=spec.benchmark_symbol)
    scores = compute_momentum_scores(close, volume=volume)
    scores["breadth"] = breadth

    engine = CausalPortfolioEngine(data, scores)
    return engine.simulate(spec, **kwargs)
