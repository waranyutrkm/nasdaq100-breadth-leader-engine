#!/usr/bin/env python3
"""Build Standalone Nasdaq-100 Quantitative Breadth & Leader Dashboard.

Produces a zero-dependency, self-contained index.html deployable to GitHub Pages.
Strictly adheres to:
1. Ekasit's Law & DTCG Design Tokens (Primitive -> Semantic -> Component)
2. Anti-Slop Zero-Emoji Doctrine (No emojis; structured semantic badges, geometric glyphs, inline SVGs)
3. Tabular Numerics (tabular-nums) for zero layout jitter
4. WCAG 2.2 AA Contrast & Responsive Layout
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SNAPSHOT_PATH = DATA_DIR / "latest_market_snapshot.json"
BACKTEST_PATH = DATA_DIR / "backtest_results.json"
INDEX_HTML = ROOT / "index.html"


def build_dashboard() -> None:
    if not SNAPSHOT_PATH.exists():
        raise FileNotFoundError(f"{SNAPSHOT_PATH} does not exist. Run generate_signals.py first.")
    if not BACKTEST_PATH.exists():
        raise FileNotFoundError(f"{BACKTEST_PATH} does not exist. Run run_backtest_audit.py first.")

    with open(SNAPSHOT_PATH, "r", encoding="utf-8") as f:
        snapshot_data = json.load(f)

    with open(BACKTEST_PATH, "r", encoding="utf-8") as f:
        backtest_data = json.load(f)

    combined_payload = {
        "snapshot": snapshot_data,
        "backtest": backtest_data,
    }

    embedded_json = json.dumps(combined_payload, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="th" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
  <title>Nasdaq-100 Breadth & Leader Engine — Institutional Terminal</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    :root {{
      /* 1. Primitive Tokens */
      --color-slate-950: #07090e;
      --color-slate-900: #0d1117;
      --color-slate-850: #111622;
      --color-slate-800: #161d2b;
      --color-slate-750: #1c2536;
      --color-slate-700: #253147;
      --color-slate-600: #374663;
      --color-slate-400: #8899b5;
      --color-slate-300: #b2c0d8;
      --color-slate-100: #f0f4fc;
      --color-teal-400: #00d293;
      --color-rose-400: #ff5252;
      --color-cyan-400: #38bdf8;
      --color-amber-400: #f59e0b;
      --color-blue-500: #2563eb;

      /* 2. Semantic Tokens */
      --bg-canvas: var(--color-slate-950);
      --bg-surface: var(--color-slate-900);
      --bg-card: var(--color-slate-850);
      --bg-card-hover: var(--color-slate-800);
      --bg-subtle: var(--color-slate-750);
      --border-default: var(--color-slate-700);
      --border-subtle: #1c2536;
      --border-active: var(--color-cyan-400);
      --border-focus: var(--color-cyan-400);

      --text-primary: var(--color-slate-100);
      --text-secondary: var(--color-slate-400);
      --text-muted: #5e7090;

      --color-bull: var(--color-teal-400);
      --color-bear: var(--color-rose-400);
      --color-squeeze: var(--color-cyan-400);
      --color-warning: var(--color-amber-400);

      --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      --font-mono: 'JetBrains Mono', SFMono-Regular, Menlo, Monaco, Consolas, monospace;

      --radius-sm: 4px;
      --radius-md: 8px;
      --radius-lg: 12px;
      --radius-full: 9999px;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: var(--font-sans);
      background-color: var(--bg-canvas);
      color: var(--text-primary);
      line-height: 1.5;
      min-height: 100vh;
      padding: 1.25rem;
      -webkit-font-smoothing: antialiased;
    }}

    .tabular-nums {{
      font-variant-numeric: tabular-nums;
      font-family: var(--font-mono);
    }}

    .container {{
      max-width: 1240px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }}

    /* Header */
    .terminal-header {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 1rem;
      padding-bottom: 1.25rem;
      border-bottom: 1px solid var(--border-default);
    }}

    .terminal-title-group {{
      display: flex;
      align-items: center;
      gap: 0.875rem;
    }}

    .terminal-icon-box {{
      width: 44px;
      height: 44px;
      border-radius: var(--radius-md);
      background: linear-gradient(135deg, #1e293b, #0f172a);
      border: 1px solid var(--border-default);
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--color-squeeze);
    }}

    .terminal-title {{
      font-size: 1.25rem;
      font-weight: 800;
      letter-spacing: -0.02em;
      color: var(--text-primary);
    }}

    .terminal-subtitle {{
      font-size: 0.75rem;
      color: var(--text-secondary);
      margin-top: 0.125rem;
    }}

    .header-badges {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      flex-wrap: wrap;
    }}

    /* Badges */
    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.375rem;
      padding: 0.25rem 0.625rem;
      font-size: 0.6875rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      border-radius: var(--radius-sm);
      font-family: var(--font-mono);
    }}

    .badge-bull {{
      background: rgba(0, 210, 147, 0.12);
      color: var(--color-bull);
      border: 1px solid rgba(0, 210, 147, 0.3);
    }}

    .badge-bear {{
      background: rgba(255, 82, 82, 0.12);
      color: var(--color-bear);
      border: 1px solid rgba(255, 82, 82, 0.3);
    }}

    .badge-squeeze {{
      background: rgba(56, 189, 248, 0.12);
      color: var(--color-squeeze);
      border: 1px solid rgba(56, 189, 248, 0.3);
    }}

    .badge-neutral {{
      background: rgba(136, 153, 181, 0.12);
      color: var(--text-secondary);
      border: 1px solid var(--border-default);
    }}

    /* Macro Action Card */
    .action-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-default);
      border-radius: var(--radius-lg);
      padding: 1.25rem;
      display: grid;
      grid-template-columns: 1fr;
      gap: 1.25rem;
    }}

    @media (min-width: 840px) {{
      .action-card {{
        grid-template-columns: 2.2fr 1fr;
        align-items: center;
      }}
    }}

    .regime-status-title {{
      font-size: 1.125rem;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 0.75rem;
      color: var(--text-primary);
    }}

    .regime-desc {{
      font-size: 0.8125rem;
      color: var(--text-secondary);
      margin-top: 0.375rem;
      line-height: 1.6;
    }}

    .macro-metrics-strip {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 0.75rem;
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 0.875rem;
      text-align: center;
    }}

    .macro-metric-label {{
      font-size: 0.6875rem;
      color: var(--text-secondary);
      text-transform: uppercase;
      font-weight: 600;
    }}

    .macro-metric-val {{
      font-size: 1.125rem;
      font-weight: 700;
      margin-top: 0.125rem;
    }}

    /* Strategy Selector Cards */
    .section-label {{
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-secondary);
      margin-bottom: 0.75rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .strategies-grid {{
      display: grid;
      grid-template-columns: 1fr;
      gap: 1rem;
    }}

    @media (min-width: 768px) {{
      .strategies-grid {{
        grid-template-columns: repeat(3, 1fr);
      }}
    }}

    .strat-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-default);
      border-radius: var(--radius-lg);
      padding: 1.125rem;
      cursor: pointer;
      transition: all 0.2s ease;
      position: relative;
    }}

    .strat-card:hover {{
      background: var(--bg-card-hover);
      border-color: var(--color-slate-600);
    }}

    .strat-card.active {{
      background: rgba(56, 189, 248, 0.05);
      border-color: var(--border-active);
      box-shadow: 0 0 0 1px var(--border-active);
    }}

    .strat-tag {{
      position: absolute;
      top: -9px;
      right: 12px;
      background: var(--color-blue-500);
      color: #fff;
      font-size: 0.5625rem;
      font-weight: 800;
      padding: 0.125rem 0.5rem;
      border-radius: var(--radius-sm);
      letter-spacing: 0.05em;
      text-transform: uppercase;
    }}

    .strat-name {{
      font-size: 0.9375rem;
      font-weight: 700;
      color: var(--text-primary);
      margin-top: 0.25rem;
    }}

    .strat-desc {{
      font-size: 0.75rem;
      color: var(--text-secondary);
      margin-top: 0.375rem;
      line-height: 1.45;
      min-height: 2.2rem;
    }}

    .strat-stats-row {{
      display: flex;
      justify-content: space-between;
      border-top: 1px solid var(--border-subtle);
      margin-top: 0.875rem;
      padding-top: 0.625rem;
      font-size: 0.75rem;
    }}

    /* Execution Planner & Capital Sizer */
    .execution-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-default);
      border-radius: var(--radius-lg);
      padding: 1.25rem;
    }}

    .input-group {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      flex-wrap: wrap;
      margin-bottom: 1rem;
    }}

    .input-field {{
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      color: var(--text-primary);
      padding: 0.5rem 0.875rem;
      border-radius: var(--radius-sm);
      font-size: 0.875rem;
      outline: none;
      font-family: var(--font-mono);
      min-width: 180px;
    }}

    .input-field:focus {{
      outline: 2px solid var(--border-focus);
      border-color: transparent;
    }}

    .calc-btn {{
      background: var(--bg-subtle);
      border: 1px solid var(--border-default);
      color: var(--text-primary);
      font-size: 0.8125rem;
      font-weight: 600;
      padding: 0.5rem 1rem;
      border-radius: var(--radius-sm);
      cursor: pointer;
      transition: background 0.15s ease;
    }}

    .calc-btn:hover {{
      background: var(--color-slate-700);
    }}

    /* Tables */
    .table-container {{
      width: 100%;
      overflow-x: auto;
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      background: var(--bg-surface);
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 0.8125rem;
    }}

    th {{
      background: var(--bg-subtle);
      color: var(--text-secondary);
      font-size: 0.6875rem;
      text-transform: uppercase;
      font-weight: 700;
      letter-spacing: 0.05em;
      padding: 0.625rem 0.875rem;
      border-bottom: 1px solid var(--border-default);
    }}

    td {{
      padding: 0.625rem 0.875rem;
      border-bottom: 1px solid var(--border-subtle);
      color: var(--text-primary);
    }}

    tr:last-child td {{
      border-bottom: none;
    }}

    tr:hover td {{
      background: rgba(255, 255, 255, 0.02);
    }}

    .text-right {{
      text-align: right;
    }}

    .text-center {{
      text-align: center;
    }}

    .text-bull {{
      color: var(--color-bull);
    }}

    .text-bear {{
      color: var(--color-bear);
    }}

    .text-squeeze {{
      color: var(--color-squeeze);
    }}

    /* Performance Grid */
    .perf-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 0.75rem;
    }}

    .perf-stat-box {{
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 0.875rem;
    }}

    .perf-stat-label {{
      font-size: 0.6875rem;
      text-transform: uppercase;
      font-weight: 600;
      color: var(--text-secondary);
    }}

    .perf-stat-value {{
      font-size: 1.25rem;
      font-weight: 700;
      margin-top: 0.25rem;
    }}

    /* Footer */
    .terminal-footer {{
      border-top: 1px solid var(--border-default);
      padding-top: 1.25rem;
      font-size: 0.75rem;
      color: var(--text-secondary);
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 1rem;
    }}
  </style>
</head>
<body>

  <div class="container">

    <!-- Terminal Header -->
    <header class="terminal-header">
      <div class="terminal-title-group">
        <div class="terminal-icon-box">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"></polyline>
            <polyline points="16 7 22 7 22 13"></polyline>
          </svg>
        </div>
        <div>
          <h1 class="terminal-title">Nasdaq-100 Breadth & Leader Engine</h1>
          <p class="terminal-subtitle">ระบบสแกนเนอร์เชิงปริมาณ & หมุนพอร์ตหุ้นผู้นำ Nasdaq-100 (Daily Causal Terminal)</p>
        </div>
      </div>

      <div class="header-badges">
        <span id="market-status-badge" class="badge badge-bull">● MARKET OPEN</span>
        <span id="last-updated-badge" class="badge badge-neutral tabular-nums">DATA: --</span>
        <a href="https://github.com/waranyutrkm/crypto-breadth-leader-engine" target="_blank" class="badge badge-squeeze" style="text-decoration:none;">
          [DOCS & CODE]
        </a>
      </div>
    </header>

    <!-- Macro Regime Banner -->
    <section class="action-card">
      <div>
        <div class="regime-status-title">
          <span id="regime-badge" class="badge badge-bull">[REGIME: NORMAL BULL]</span>
          <span id="regime-heading">ตลาดกระทิงปกติ (Normal Bull)</span>
        </div>
        <p id="regime-detail" class="regime-desc">
          ดัชนี QQQ ยืนเหนือเส้น EMA100 และความกว้างตลาด (สัดส่วนหุ้นยืนเหนือ EMA50) อยู่ในระดับปานกลาง ควรถือครองหุ้นผู้นำ Top 3-5 ตัว
        </p>
      </div>

      <div class="macro-metrics-strip">
        <div>
          <div class="macro-metric-label">QQQ Price</div>
          <div id="metric-qqq-price" class="macro-metric-val tabular-nums">$0.00</div>
        </div>
        <div>
          <div class="macro-metric-label">Breadth >50</div>
          <div id="metric-breadth-ema50" class="macro-metric-val tabular-nums text-bull">0.0%</div>
        </div>
        <div>
          <div class="macro-metric-label">Gate State</div>
          <div id="metric-gate-state" class="macro-metric-val tabular-nums text-squeeze">PASS</div>
        </div>
      </div>
    </section>

    <!-- Strategy Preset Cards -->
    <section>
      <div class="section-label">
        <span>เลือกสถาปัตยกรรมกลยุทธ์ (Strategy Architecture)</span>
        <span class="tabular-nums" style="font-size:0.6875rem;">REBALANCE: 21 SESSIONS</span>
      </div>

      <div class="strategies-grid">
        <!-- 1. Core-Satellite -->
        <div id="card-core_satellite" class="strat-card active" onclick="switchStrategy('core_satellite')">
          <span class="strat-tag">RECOMMENDED</span>
          <div class="badge badge-squeeze">[MODEL 1]</div>
          <h3 class="strat-name">Core-Satellite (50:50)</h3>
          <p class="strat-desc">ถือ QQQ 50% เป็นแกนหลัก + 50% หมุนตามหุ้นผู้นำ Top 5 ตัว ช่วยเกาะดัชนีบิ๊กแคปและลดความผันผวน</p>
          <div class="strat-stats-row tabular-nums">
            <span>CAGR: <strong class="text-bull" id="stat-core-cagr">+23.59%</strong></span>
            <span>MaxDD: <strong class="text-bear" id="stat-core-dd">-26.84%</strong></span>
            <span>Sharpe: <strong id="stat-core-sharpe">1.13</strong></span>
          </div>
        </div>

        <!-- 2. Fast-Alpha Leader -->
        <div id="card-fast_alpha" class="strat-card" onclick="switchStrategy('fast_alpha')">
          <div class="badge badge-bull">[MODEL 2]</div>
          <h3 class="strat-name">Fast-Alpha Leader</h3>
          <p class="strat-desc">หมุนถือเฉพาะหุ้นผู้นำ Top 5 ที่แรงที่สุด ถ่วงน้ำหนัก Inverse Volatility พักเงินสด 100% BIL เมื่อหลุดเกณฑ์</p>
          <div class="strat-stats-row tabular-nums">
            <span>CAGR: <strong class="text-bull" id="stat-fast-cagr">+26.67%</strong></span>
            <span>MaxDD: <strong class="text-bear" id="stat-fast-dd">-35.31%</strong></span>
            <span>Sharpe: <strong id="stat-fast-sharpe">1.01</strong></span>
          </div>
        </div>

        <!-- 3. Adaptive Regime Guard -->
        <div id="card-legacy_adaptive" class="strat-card" onclick="switchStrategy('legacy_adaptive')">
          <div class="badge badge-neutral">[MODEL 3]</div>
          <h3 class="strat-name">Adaptive Regime Guard</h3>
          <p class="strat-desc">ปรับสัดส่วนการถือหุ้นตามขั้นความกว้างตลาด (0% / 70% / 90% / 95%) ล้างพอร์ตเข้า BIL 100% เมื่อตลาดหมี</p>
          <div class="strat-stats-row tabular-nums">
            <span>CAGR: <strong class="text-bull" id="stat-adapt-cagr">+26.39%</strong></span>
            <span>MaxDD: <strong class="text-bear" id="stat-adapt-dd">-26.30%</strong></span>
            <span>Sharpe: <strong id="stat-adapt-sharpe">1.04</strong></span>
          </div>
        </div>
      </div>
    </section>

    <!-- Execution Plan & Capital Sizer -->
    <section class="execution-card">
      <div class="section-label">
        <span>ตั๋วคำสั่งซื้อขายและจัดสรรเงินทุน (Execution Plan & Sizing)</span>
        <span id="active-strategy-label" class="badge badge-squeeze">CORE-SATELLITE ACTIVE</span>
      </div>

      <div class="input-group">
        <label for="portfolio-capital" style="font-size:0.8125rem; font-weight:600; color:var(--text-secondary);">เงินทุนพอร์ตทั้งหมด (USD):</label>
        <input type="number" id="portfolio-capital" class="input-field" value="100000" step="5000" min="1000" oninput="recalculateSizing()">
        <button class="calc-btn" onclick="recalculateSizing()">คำนวณคำสั่งใหม่</button>
      </div>

      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>สัญลักษณ์ (Ticker)</th>
              <th>ชื่อบริษัท / ประเภท</th>
              <th class="text-right">ราคาล่าสุด</th>
              <th class="text-right">น้ำหนักเป้าหมาย</th>
              <th class="text-right">มูลค่าจัดสรร (USD)</th>
              <th class="text-right">จำนวนหุ้นประมาณการ</th>
              <th class="text-center">คำสั่งปฏิบัติการ</th>
            </tr>
          </thead>
          <tbody id="allocation-table-body">
            <!-- Rendered by JS -->
          </tbody>
        </table>
      </div>
    </section>

    <!-- Leaderboard & Constituents Table -->
    <section class="execution-card">
      <div class="section-label">
        <span>ตารางจัดอันดับหุ้นผู้นำ Nasdaq-100 (Momentum & Breadth Leaderboard)</span>
        <span class="badge badge-neutral" id="total-constituents-badge">101 ASSETS SCANNED</span>
      </div>

      <div class="table-container" style="max-height: 480px; overflow-y: auto;">
        <table>
          <thead style="position: sticky; top: 0; z-index: 10;">
            <tr>
              <th class="text-center">อันดับ</th>
              <th>สัญลักษณ์</th>
              <th>ชื่อบริษัท</th>
              <th>กลุ่มอุตสาหกรรม</th>
              <th class="text-right">ราคา</th>
              <th class="text-right">Momentum Score</th>
              <th class="text-right">R30</th>
              <th class="text-right">R60</th>
              <th class="text-right">ความผันผวน (63d)</th>
              <th class="text-center">Technical Gate</th>
              <th class="text-center">สถานะ</th>
            </tr>
          </thead>
          <tbody id="leaderboard-table-body">
            <!-- Rendered by JS -->
          </tbody>
        </table>
      </div>
    </section>

    <!-- Historical Performance Audit -->
    <section class="execution-card">
      <div class="section-label">
        <span>การตรวจสอบผลลัพธ์ย้อนหลังเชิงสถาบัน (Historical Backtest Audit 2011–2026)</span>
        <span class="badge badge-neutral">UNLEVERAGED NEXT-OPEN EXECUTION</span>
      </div>

      <div class="perf-grid">
        <div class="perf-stat-box">
          <div class="perf-stat-label">กลยุทธ์ CAGR</div>
          <div id="audit-cagr" class="perf-stat-value text-bull tabular-nums">--</div>
        </div>
        <div class="perf-stat-box">
          <div class="perf-stat-label">QQQ Benchmark CAGR</div>
          <div id="audit-qqq-cagr" class="perf-stat-value text-secondary tabular-nums">--</div>
        </div>
        <div class="perf-stat-box">
          <div class="perf-stat-label">กลยุทธ์ Max Drawdown</div>
          <div id="audit-max-dd" class="perf-stat-value text-bear tabular-nums">--</div>
        </div>
        <div class="perf-stat-box">
          <div class="perf-stat-label">QQQ Max Drawdown</div>
          <div id="audit-qqq-dd" class="perf-stat-value text-bear tabular-nums">--</div>
        </div>
        <div class="perf-stat-box">
          <div class="perf-stat-label">Sharpe Ratio (Excess BIL)</div>
          <div id="audit-sharpe" class="perf-stat-value text-squeeze tabular-nums">--</div>
        </div>
        <div class="perf-stat-box">
          <div class="perf-stat-label">Beta vs QQQ</div>
          <div id="audit-beta" class="perf-stat-value tabular-nums">--</div>
        </div>
      </div>
    </section>

    <!-- Terminal Footer -->
    <footer class="terminal-footer">
      <div>
        <p><strong>Nasdaq-100 Breadth & Leader Rotation Engine</strong> | Causal Next-Open Architecture</p>
        <p style="margin-top:0.25rem;">อ้างอิงข้อมูลดัชนีและหุ้นสหรัฐฯ ปรับสิทธิประโยชน์เงินปันผลแล้ว พักสภาพคล่องใน SPDR Bloomberg 1-3 Month T-Bill (BIL)</p>
      </div>
      <div>
        <p>Zero-Emoji Doctrine & Ekasit's Law Enforced</p>
        <p style="margin-top:0.25rem;">Quantitative Research & Educational Terminal</p>
      </div>
    </footer>

  </div>

  <!-- Embedded Data Payload -->
  <script>
    const ENGINE_PAYLOAD = {embedded_json};

    let activeStrategyKey = 'core_satellite';

    function initTerminal() {{
      const snapshot = ENGINE_PAYLOAD.snapshot;
      const backtest = ENGINE_PAYLOAD.backtest;

      // 1. Meta & Header
      document.getElementById('last-updated-badge').textContent = `DATA: ${{snapshot.metadata.last_updated_date}}`;
      document.getElementById('metric-qqq-price').textContent = `$${{snapshot.market_macro.qqq_close.toFixed(2)}}`;
      document.getElementById('metric-breadth-ema50').textContent = `${{snapshot.breadth.breadth_ema50_pct}}%`;

      const gatePass = snapshot.market_macro.qqq_trend_ok && snapshot.breadth.breadth_ema50_pct >= 20.0;
      const gateEl = document.getElementById('metric-gate-state');
      if (gatePass) {{
        gateEl.textContent = 'PASS';
        gateEl.className = 'macro-metric-val tabular-nums text-bull';
      }} else {{
        gateEl.textContent = 'FAIL';
        gateEl.className = 'macro-metric-val tabular-nums text-bear';
      }}

      // 2. Regime Status
      const regime = snapshot.market_macro.regime;
      const regBadge = document.getElementById('regime-badge');
      regBadge.textContent = `[REGIME: ${{snapshot.market_macro.regime_title}}]`;
      if (regime === 'CASH_GUARD') {{
        regBadge.className = 'badge badge-bear';
      }} else if (regime === 'BROAD_BULL') {{
        regBadge.className = 'badge badge-bull';
      }} else {{
        regBadge.className = 'badge badge-squeeze';
      }}
      document.getElementById('regime-heading').textContent = snapshot.market_macro.regime_title;
      document.getElementById('regime-detail').textContent = snapshot.market_macro.regime_desc;

      // 3. Render Leaderboard
      renderLeaderboard(snapshot.stock_rankings);

      // 4. Render Active Strategy Sizing
      switchStrategy(activeStrategyKey);

      // 5. Render Audit Metrics
      updateAuditMetrics();
    }}

    function switchStrategy(key) {{
      activeStrategyKey = key;
      document.querySelectorAll('.strat-card').forEach(el => el.classList.remove('active'));
      const activeEl = document.getElementById(`card-${{key}}`);
      if (activeEl) activeEl.classList.add('active');

      const names = {{
        core_satellite: 'CORE-SATELLITE ACTIVE (50:50)',
        fast_alpha: 'FAST-ALPHA LEADER ACTIVE',
        legacy_adaptive: 'ADAPTIVE REGIME GUARD ACTIVE',
      }};
      document.getElementById('active-strategy-label').textContent = names[key] || 'STRATEGY ACTIVE';

      recalculateSizing();
      updateAuditMetrics();
    }}

    function recalculateSizing() {{
      const capitalInput = document.getElementById('portfolio-capital');
      let capital = parseFloat(capitalInput.value);
      if (isNaN(capital) || capital <= 0) capital = 100000;

      const strat = ENGINE_PAYLOAD.snapshot.strategies[activeStrategyKey];
      const allocations = strat.allocations;
      const tbody = document.getElementById('allocation-table-body');
      tbody.innerHTML = '';

      const meta = ENGINE_PAYLOAD.snapshot.stock_rankings.reduce((acc, x) => {{
        acc[x.ticker] = x;
        return acc;
      }}, {{}});

      // Always include benchmark/cash info
      meta['QQQ'] = {{ name: 'Invesco QQQ Trust (Nasdaq-100 Core)', sector: 'Index ETF', price: ENGINE_PAYLOAD.snapshot.market_macro.qqq_close }};
      meta['BIL'] = {{ name: 'SPDR 1-3 Month T-Bill (Cash Reserve)', sector: 'Cash Equivalent', price: ENGINE_PAYLOAD.snapshot.market_macro.bil_close }};

      for (const [ticker, weight] of Object.entries(allocations)) {{
        if (weight <= 0) continue;
        const info = meta[ticker] || {{ name: `${{ticker}} Corp`, sector: 'Equity', price: 100.0 }};
        const dollars = capital * weight;
        const shares = Math.floor(dollars / info.price);

        const tr = document.createElement('tr');
        let actionBadge = '<span class="badge badge-bull">[BUY / HOLD]</span>';
        if (ticker === 'BIL') {{
          actionBadge = '<span class="badge badge-neutral">[CASH YIELD]</span>';
        }} else if (ticker === 'QQQ') {{
          actionBadge = '<span class="badge badge-squeeze">[CORE HOLD]</span>';
        }}

        tr.innerHTML = `
          <td><strong class="tabular-nums">${{ticker}}</strong></td>
          <td>
            <div style="font-weight:600;">${{info.name}}</div>
            <div style="font-size:0.6875rem; color:var(--text-secondary);">${{info.sector}}</div>
          </td>
          <td class="text-right tabular-nums">$${{info.price.toFixed(2)}}</td>
          <td class="text-right tabular-nums font-bold text-squeeze">${{(weight * 100).toFixed(1)}}%</td>
          <td class="text-right tabular-nums font-bold">$${{dollars.toLocaleString('en-US', {{minimumFractionDigits: 2, maximumFractionDigits: 2}})}}</td>
          <td class="text-right tabular-nums">${{shares.toLocaleString()}} หุ้น</td>
          <td class="text-center">${{actionBadge}}</td>
        `;
        tbody.appendChild(tr);
      }}
    }}

    function renderLeaderboard(stocks) {{
      const tbody = document.getElementById('leaderboard-table-body');
      tbody.innerHTML = '';

      stocks.slice(0, 40).forEach(s => {{
        const tr = document.createElement('tr');
        const gateBadge = s.trend_gate
          ? '<span class="badge badge-bull">PASS</span>'
          : '<span class="badge badge-bear">FAIL</span>';

        let statusBadge = '<span class="badge badge-neutral">WATCH</span>';
        if (s.passes_all && s.rank <= 5) {{
          statusBadge = '<span class="badge badge-bull">[ALPHA BUY]</span>';
        }} else if (s.passes_all && s.rank <= 10) {{
          statusBadge = '<span class="badge badge-squeeze">[LEADER 10]</span>';
        }}

        tr.innerHTML = `
          <td class="text-center tabular-nums font-bold" style="color:var(--text-secondary);">${{s.rank}}</td>
          <td><strong class="tabular-nums">${{s.ticker}}</strong></td>
          <td>${{s.name}}</td>
          <td style="color:var(--text-secondary);">${{s.sector}}</td>
          <td class="text-right tabular-nums font-bold">$${{s.price.toFixed(2)}}</td>
          <td class="text-right tabular-nums font-bold text-squeeze">${{s.momentum_score > 0 ? '+' : ''}}${{s.momentum_score.toFixed(1)}}</td>
          <td class="text-right tabular-nums ${{s.ret30 >= 0 ? 'text-bull' : 'text-bear'}}">${{s.ret30 >= 0 ? '+' : ''}}${{s.ret30.toFixed(1)}}%</td>
          <td class="text-right tabular-nums ${{s.ret60 >= 0 ? 'text-bull' : 'text-bear'}}">${{s.ret60 >= 0 ? '+' : ''}}${{s.ret60.toFixed(1)}}%</td>
          <td class="text-right tabular-nums">${{s.vol63.toFixed(1)}}%</td>
          <td class="text-center">${{gateBadge}}</td>
          <td class="text-center">${{statusBadge}}</td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    function updateAuditMetrics() {{
      const summary = ENGINE_PAYLOAD.backtest.summary_table;
      const qqq = summary['QQQ_Buy_Hold'] || {{}};

      const keyMapping = {{
        core_satellite: 'Core_Satellite_50_50',
        fast_alpha: 'Fast_Alpha_Leader',
        legacy_adaptive: 'Adaptive_Regime_Guard',
      }};

      const stratKey = keyMapping[activeStrategyKey] || 'Core_Satellite_50_50';
      const strat = summary[stratKey] || {{}};

      document.getElementById('audit-cagr').textContent = `+${{strat.cagr_pct || 0}}%`;
      document.getElementById('audit-qqq-cagr').textContent = `+${{qqq.cagr_pct || 0}}%`;
      document.getElementById('audit-max-dd').textContent = `${{strat.max_dd_pct || 0}}%`;
      document.getElementById('audit-qqq-dd').textContent = `${{qqq.max_dd_pct || 0}}%`;
      document.getElementById('audit-sharpe').textContent = `${{strat.sharpe_excess_bil || 0}}`;
      document.getElementById('audit-beta').textContent = `${{strat.beta_vs_qqq || 1.0}}`;
    }}

    window.addEventListener('DOMContentLoaded', initTerminal);
  </script>
</body>
</html>
"""

    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[+] Successfully compiled standalone terminal dashboard: {INDEX_HTML}")


if __name__ == "__main__":
    build_dashboard()
