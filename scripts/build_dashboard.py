#!/usr/bin/env python3
"""Build Standalone, Interactive Nasdaq-100 Quantitative Breadth & Leader Dashboard.

Produces a zero-dependency, client-side reactive index.html deployable to GitHub Pages.
Strictly adheres to:
1. Ekasit's Law & DTCG Design Tokens (Primitive -> Semantic -> Component)
2. Anti-Slop Zero-Emoji Doctrine (No emojis; structured semantic badges, geometric glyphs, inline SVGs)
3. Tabular Numerics (tabular-nums) for zero layout jitter
4. WCAG 2.2 AA Contrast & Responsive Layout
5. Action-First Interactive Layout (What to do today, Past action timeline, and Full Scanner Matrix)
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
  <meta http-equiv="Pragma" content="no-cache" />
  <meta http-equiv="Expires" content="0" />
  <title>Nasdaq-100 Breadth & Leader Engine — วันนี้ต้องทำอะไร & ประวัติย้อนหลัง</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    :root {{
      --font-sans: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;

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

      --bg-canvas: var(--color-slate-950);
      --bg-surface: var(--color-slate-900);
      --bg-card: var(--color-slate-850);
      --border-default: var(--color-slate-700);
      --border-subtle: #1c2536;
      --border-focus: var(--color-cyan-400);

      --text-primary: var(--color-slate-100);
      --text-secondary: var(--color-slate-400);
    }}

    body {{
      font-family: var(--font-sans);
      background-color: var(--bg-canvas);
      color: var(--text-primary);
    }}

    .font-mono {{
      font-family: var(--font-mono);
    }}

    .tabular-nums {{
      font-variant-numeric: tabular-nums;
      font-family: var(--font-mono);
    }}

    ::-webkit-scrollbar {{
      width: 6px;
      height: 6px;
    }}
    ::-webkit-scrollbar-track {{
      background: #0d1117;
    }}
    ::-webkit-scrollbar-thumb {{
      background: #253147;
      border-radius: 3px;
    }}

    .card-dark {{
      background: var(--bg-card);
      border: 1px solid var(--border-default);
    }}

    .strat-card-active {{
      background: #152238 !important;
      border-color: #38bdf8 !important;
      box-shadow: 0 0 0 1px #38bdf8, 0 10px 25px -5px rgba(56, 189, 248, 0.2);
    }}

    @keyframes pulseFade {{
      0% {{ opacity: 0.4; transform: scale(0.99); }}
      50% {{ opacity: 1; transform: scale(1); }}
      100% {{ opacity: 1; transform: scale(1); }}
    }}
    .just-updated {{
      animation: pulseFade 0.35s ease-out;
    }}
  </style>
</head>
<body class="min-h-screen p-3 md:p-6 max-w-5xl mx-auto space-y-6">

  <!-- Header -->
  <header class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#253147] pb-4">
    <div class="flex items-center gap-3">
      <div class="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-blue-600 to-cyan-500 text-white font-black text-lg shadow-lg shadow-blue-500/20">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"></polyline>
          <polyline points="16 7 22 7 22 13"></polyline>
        </svg>
      </div>
      <div>
        <div class="flex items-center gap-2">
          <h1 class="text-xl font-extrabold text-white">Nasdaq-100 Leader Rotation Hub</h1>
          <span class="rounded-full bg-cyan-500/15 px-2.5 py-0.5 text-xs font-bold text-cyan-400 border border-cyan-500/30">Next-Open Daily</span>
        </div>
        <p class="text-xs text-slate-400">ระบบบอกจุดซื้อ-ถือ-ขายประจำวัน (คำนวณจากราคาปิดและเปิดจริงของตลาดหุ้นสหรัฐฯ)</p>
      </div>
    </div>

    <!-- Header Actions -->
    <div class="flex items-center gap-2">
      <button onclick="location.reload(true)" class="rounded-lg bg-[#161d2b] hover:bg-slate-700 border border-slate-700 px-3 py-1.5 text-xs font-semibold text-slate-300 transition flex items-center gap-1.5" title="ล้างแคชและรีเฟรชข้อมูลล่าสุด">
        รีเฟรชข้อมูล
      </button>
      <a href="https://github.com/waranyutrkm/nasdaq100-breadth-leader-engine" target="_blank" class="rounded-lg bg-[#161d2b] hover:bg-slate-700 border border-slate-700 px-3 py-1.5 text-xs font-semibold text-slate-300 transition flex items-center gap-1.5" title="อ่านคู่มือและสูตรคำนวณฉบับเต็มบน GitHub">
        คู่มือบน GitHub
      </a>
    </div>
  </header>

  <!-- ================================================================= -->
  <!-- SECTION 1: วันนี้ต้องทำอะไร? (WHAT TO DO TODAY) -->
  <!-- ================================================================= -->
  <section class="space-y-4">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
      <h2 class="text-lg font-extrabold text-white flex items-center gap-2">
        <span class="flex h-7 w-7 items-center justify-center rounded-lg bg-blue-600/20 text-cyan-400 font-bold">1</span>
        <span>วันนี้ต้องทำอะไร? (Today's Direct Action Plan)</span>
      </h2>
      <span class="text-xs font-mono text-slate-400 tabular-nums" id="today-date-text">DATE: --</span>
    </div>

    <!-- 3 Large Selectable Strategy Cards (คลิกเพื่อสลับแผนทันที) -->
    <div class="space-y-2">
      <div class="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center justify-between">
        <span>คลิกเลือกแผนการเทรดที่ต้องการ (คลิกเพื่อเปลี่ยนหุ้นและสัดส่วนคำนวณ):</span>
        <span class="text-[11px] text-cyan-400 font-mono" id="active-strat-indicator">กำลังใช้งาน: Core-Satellite (50:50)</span>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <!-- Card 1: Core-Satellite -->
        <div onclick="setStrategy('core_satellite')" id="card-strat-core_satellite" class="p-3.5 rounded-xl border border-[#253147] bg-[#111622] hover:border-slate-600 cursor-pointer transition flex flex-col justify-between strat-card-active">
          <div>
            <div class="flex items-center justify-between mb-1">
              <span class="text-[10px] px-2 py-0.5 rounded font-bold bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">แนะนำสำหรับทุกคน</span>
              <span class="text-[11px] font-bold text-cyan-400 checkmark">● เลือกอยู่</span>
            </div>
            <h3 class="text-xs font-bold text-white mb-0.5">1. แผนสถาบัน (Core-Satellite 50:50)</h3>
            <p class="text-[11px] text-slate-400 line-clamp-2">ถือ QQQ 50% เป็นแกนหลัก + 50% หมุนตาม 5 หุ้นผู้นำ เกาะบิ๊กแคปและลดความผันผวน</p>
          </div>
          <div class="pt-2 border-t border-[#1c2536] mt-2 flex justify-between text-[10px] font-mono tabular-nums">
            <span class="text-slate-400">CAGR: <strong class="text-teal-400">+23.59%</strong></span>
            <span class="text-slate-400">MaxDD: <strong class="text-rose-400">-26.84%</strong></span>
            <span class="text-slate-400">Sharpe: <strong class="text-cyan-400">1.13</strong></span>
          </div>
        </div>

        <!-- Card 2: Fast-Alpha Leader -->
        <div onclick="setStrategy('fast_alpha')" id="card-strat-fast_alpha" class="p-3.5 rounded-xl border border-[#253147] bg-[#111622] hover:border-slate-600 cursor-pointer transition flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-1">
              <span class="text-[10px] px-2 py-0.5 rounded font-bold bg-teal-500/20 text-teal-400 border border-teal-500/30">ผลตอบแทนสูงสุด</span>
              <span class="text-[11px] font-bold text-slate-500 checkmark hidden">● เลือกอยู่</span>
            </div>
            <h3 class="text-xs font-bold text-white mb-0.5">2. แผนคลื่นเร็ว (Fast-Alpha Leader)</h3>
            <p class="text-[11px] text-slate-400 line-clamp-2">100% หมุนถือเฉพาะหุ้น Top 5 ผู้นำที่แรงที่สุด ถ่วงน้ำหนักผกผันความผันผวน (Inverse Vol)</p>
          </div>
          <div class="pt-2 border-t border-[#1c2536] mt-2 flex justify-between text-[10px] font-mono tabular-nums">
            <span class="text-slate-400">CAGR: <strong class="text-teal-400">+26.67%</strong></span>
            <span class="text-slate-400">MaxDD: <strong class="text-rose-400">-35.31%</strong></span>
            <span class="text-slate-400">Sharpe: <strong class="text-cyan-400">1.01</strong></span>
          </div>
        </div>

        <!-- Card 3: Adaptive Regime Guard -->
        <div onclick="setStrategy('legacy_adaptive')" id="card-strat-legacy_adaptive" class="p-3.5 rounded-xl border border-[#253147] bg-[#111622] hover:border-slate-600 cursor-pointer transition flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-1">
              <span class="text-[10px] px-2 py-0.5 rounded font-bold bg-purple-500/20 text-purple-400 border border-purple-500/30">เกราะป้องกันเงินต้น</span>
              <span class="text-[11px] font-bold text-slate-500 checkmark hidden">● เลือกอยู่</span>
            </div>
            <h3 class="text-xs font-bold text-white mb-0.5">3. ปรับตามสภาวะ (Adaptive Guard)</h3>
            <p class="text-[11px] text-slate-400 line-clamp-2">ปรับพอร์ตถือหุ้นตามความกว้างตลาด (0%/70%/90%/95%) พักเงินสด 100% BIL เมื่อตลาดหมี</p>
          </div>
          <div class="pt-2 border-t border-[#1c2536] mt-2 flex justify-between text-[10px] font-mono tabular-nums">
            <span class="text-slate-400">CAGR: <strong class="text-teal-400">+26.39%</strong></span>
            <span class="text-slate-400">MaxDD: <strong class="text-rose-400">-26.30%</strong></span>
            <span class="text-slate-400">Sharpe: <strong class="text-cyan-400">1.04</strong></span>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Market Status Hero Card -->
    <div class="card-dark rounded-2xl p-5 relative overflow-hidden border border-cyan-500/30">
      <!-- Strategy Alert Toast Banner -->
      <div id="strategy-alert-toast" class="mb-4 p-2.5 rounded-xl bg-cyan-950/40 border border-cyan-500/40 text-cyan-300 text-xs font-bold flex items-center justify-between">
        <span class="flex items-center gap-2">
          <span class="h-2 w-2 rounded-full bg-cyan-400 animate-ping"></span>
          <span id="toast-text">กำลังใช้งาน แผนสถาบัน (Core-Satellite): ถือ QQQ 50% + กระจายลงทุนใน Top 5 ผู้นำ</span>
        </span>
        <span class="text-[10px] text-slate-400 font-mono">Real-Time Computed</span>
      </div>

      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#253147] pb-4 mb-4">
        <div>
          <div class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">สถานะตลาดภาพรวมวันนี้:</div>
          <div class="text-2xl font-black flex items-center gap-2.5" id="hero-regime-title">
            <span class="h-3 w-3 rounded-full bg-teal-400 animate-pulse"></span>
            <span class="text-white" id="hero-regime-name">--</span>
            <span class="text-xs px-2.5 py-0.5 rounded-full font-bold font-mono" id="hero-regime-badge">--</span>
          </div>
          <p class="text-xs text-slate-300 mt-1" id="hero-regime-desc">--</p>
        </div>

        <div class="grid grid-cols-2 gap-3 font-mono text-xs">
          <div class="p-2.5 rounded-xl bg-[#0d1117] border border-[#253147]">
            <span class="text-slate-400 text-[10px] block">Invesco QQQ (Trend Gate)</span>
            <strong class="text-white tabular-nums" id="hero-qqq-price">--</strong>
            <span class="text-[10px] text-teal-400 block" id="hero-qqq-status">● PASSED (> EMA100)</span>
          </div>
          <div class="p-2.5 rounded-xl bg-[#0d1117] border border-[#253147]">
            <span class="text-slate-400 text-[10px] block">ตลาดขึ้นพร้อมกัน (Breadth)</span>
            <strong class="text-teal-400 text-sm tabular-nums" id="hero-breadth-pct">--%</strong>
            <span class="text-[10px] text-slate-400 block" id="hero-breadth-count">-- stocks > EMA50</span>
          </div>
        </div>
      </div>

      <!-- 3 Direct Action Columns: SELL, BUY, HOLD -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <!-- Action 1: SELL -->
        <div class="rounded-xl border border-rose-500/30 bg-rose-950/10 p-4 flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-bold text-rose-400 uppercase tracking-wider flex items-center gap-1.5">
                ● 1. ต้องขาย (Sell Orders)
              </span>
              <span class="text-[10px] px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 font-bold font-mono" id="cnt-sell-badge">0 ตัว</span>
            </div>
            <p class="text-[11px] text-slate-400 mb-3">หุ้นที่หลุดเกณฑ์แนวโน้ม (EMA26) หรือตกอันดับบัฟเฟอร์ ต้องขายเพื่อดึงเงินสดกลับ</p>
            <div id="sell-coins-list" class="space-y-1.5 font-mono text-xs">
              <!-- Injected by JS -->
            </div>
          </div>
          <div class="text-[10px] text-slate-500 mt-3 pt-2 border-t border-rose-900/30">
            * ส่งคำสั่งขายที่ราคาเปิด (Next-Open) เพื่อให้มีเงินสดพร้อมซื้อ
          </div>
        </div>

        <!-- Action 2: BUY -->
        <div class="rounded-xl border border-teal-500/30 bg-teal-950/10 p-4 flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-bold text-teal-400 uppercase tracking-wider flex items-center gap-1.5">
                ● 2. ต้องซื้อ (Buy Orders)
              </span>
              <span class="text-[10px] px-2 py-0.5 rounded bg-teal-500/20 text-teal-300 font-bold font-mono" id="cnt-buy-badge">0 หุ้น</span>
            </div>
            <p class="text-[11px] text-slate-400 mb-3" id="buy-column-desc">หุ้นผู้นำที่แข็งแกร่งที่สุดตามเกณฑ์ของแผนนี้</p>
            <div id="buy-coins-list" class="space-y-1.5 font-mono text-xs">
              <!-- Injected by JS -->
            </div>
          </div>
          <div class="text-[10px] text-slate-500 mt-3 pt-2 border-t border-teal-900/30" id="buy-column-footer">
            * คำนวณสัดส่วนตามอัลกอริทึมของกลยุทธ์ คุมเพดาน 20%
          </div>
        </div>

        <!-- Action 3: HOLD -->
        <div class="rounded-xl border border-cyan-500/30 bg-cyan-950/10 p-4 flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-1.5">
                ● 3. ถือต่อ (Hold / Run)
              </span>
              <span class="text-[10px] px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 font-bold font-mono" id="hold-buffer-badge">Buffer</span>
            </div>
            <p class="text-[11px] text-slate-400 mb-3">หุ้นที่ถืออยู่เดิมและยังอยู่ในเกราะ Buffer (อันดับ 6–8) ปล่อยให้กำไรวิ่งต่อ</p>
            <div id="hold-coins-list" class="space-y-1.5 font-mono text-xs">
              <!-- Injected by JS -->
            </div>
          </div>
          <div class="text-[10px] text-slate-500 mt-3 pt-2 border-t border-cyan-900/30">
            * ไม่หลุดอันดับบัฟเฟอร์ ไม่ต้องรีบขายหมู ช่วยประหยัดค่าคอม
          </div>
        </div>
      </div>

      <!-- Quick Money Calculator & Breakdown -->
      <div class="rounded-xl bg-[#0d1117] border border-[#253147] p-4 space-y-4">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div class="flex items-center gap-3">
            <div class="text-xs font-bold text-slate-300 whitespace-nowrap">คำนวณเงินทุนของคุณ:</div>
            <div class="relative w-44">
              <input type="number" id="quick-nav-input" value="100000" step="5000" oninput="updateQuickCalc()" class="w-full rounded-lg bg-[#161d2b] border border-[#253147] px-3 py-1.5 text-xs font-bold font-mono text-white focus:outline-none focus:border-cyan-400 tabular-nums">
              <span class="absolute right-2.5 top-1.5 text-[10px] font-bold text-slate-400">USD</span>
            </div>
          </div>

          <!-- Recalculate Button -->
          <div class="flex items-center gap-2">
            <button onclick="recalculateAll()" class="px-4 py-1.5 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white font-bold text-xs transition shadow-lg shadow-blue-600/20 flex items-center gap-1.5">
              กดรันคำนวณยอดเงินใหม่ (Recalculate)
            </button>
          </div>
        </div>

        <!-- Top Totals Bar -->
        <div class="grid grid-cols-3 gap-2 text-xs font-mono p-3 rounded-lg bg-[#111622] border border-[#253147] tabular-nums">
          <div>
            <span class="text-slate-400 text-[10px] block">ยอดซื้อรวม (Equities):</span>
            <strong class="text-teal-400 font-bold text-sm" id="calc-total-equity">$0.00 USD</strong>
          </div>
          <div class="border-l border-slate-700 pl-3">
            <span class="text-slate-400 text-[10px] block">สำรองเงินสด (T-Bills BIL):</span>
            <strong class="text-amber-400 font-bold text-sm" id="calc-cash-reserve">$0.00 USD</strong>
          </div>
          <div class="border-l border-slate-700 pl-3">
            <span class="text-slate-400 text-[10px] block">ประมาณการค่าคอม (0.05%):</span>
            <strong class="text-slate-300 font-bold text-sm" id="calc-fee-est">~$0.00 USD</strong>
          </div>
        </div>

        <!-- Individual Stock Order Breakdown Table -->
        <div>
          <div class="text-[11px] font-bold text-slate-400 mb-2 uppercase tracking-wider flex items-center justify-between">
            <span>ตารางแจกแจงยอดเงินที่ต้องซื้อรายหุ้น (Exact Order Breakdown):</span>
            <span class="text-teal-400 font-mono" id="breakdown-strategy-name">--</span>
          </div>
          <div class="overflow-x-auto rounded-lg border border-[#253147] bg-[#111622]">
            <table class="w-full text-left text-xs font-mono">
              <thead class="bg-[#0d1117] text-slate-400 border-b border-[#253147]">
                <tr>
                  <th class="py-2 px-3">ลำดับ</th>
                  <th class="py-2 px-3">หุ้น (Symbol)</th>
                  <th class="py-2 px-3 text-right">ราคา ($)</th>
                  <th class="py-2 px-3 text-right">สัดส่วน (%)</th>
                  <th class="py-2 px-3 text-right text-teal-400 font-bold">ยอดเงินที่ต้องซื้อ (USD)</th>
                  <th class="py-2 px-3 text-right">จำนวนหุ้น</th>
                  <th class="py-2 px-3 text-center">คำสั่งที่ต้องส่งในโบรกเกอร์</th>
                </tr>
              </thead>
              <tbody id="calculator-breakdown-tbody" class="divide-y divide-[#1c2536] text-slate-200">
                <!-- Injected by JS -->
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ================================================================= -->
  <!-- SECTION 2: ก่อนหน้านี้ทำอะไรมาบ้าง? (PAST ACTION TIMELINE) -->
  <!-- ================================================================= -->
  <section class="space-y-4">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <h2 class="text-lg font-extrabold text-white flex items-center gap-2">
        <span class="flex h-7 w-7 items-center justify-center rounded-lg bg-purple-600/20 text-purple-400 font-bold">2</span>
        <span>ก่อนหน้านี้ทำอะไรมาบ้าง? (Past Action History & Timeline)</span>
      </h2>

      <!-- Search Filter -->
      <div class="relative w-full sm:w-64">
        <input type="text" id="timeline-search-input" oninput="renderPastTimeline()" placeholder="ค้นหาชื่อหุ้น (เช่น NVDA, AAPL, MRNA)..." class="w-full rounded-lg bg-[#0d1117] border border-[#253147] px-3 py-1.5 pl-8 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400 font-mono">
        <svg class="absolute left-2.5 top-2 h-3.5 w-3.5 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
      </div>
    </div>

    <!-- Timeline List Container -->
    <div class="card-dark rounded-2xl p-5 space-y-3 max-h-[500px] overflow-y-auto" id="past-timeline-container">
      <!-- Injected by JS -->
    </div>
  </section>

  <!-- ================================================================= -->
  <!-- SECTION 3: ตรวจสอบข้อมูลเชิงลึก (COLLAPSIBLE ADVANCED DATA) -->
  <!-- ================================================================= -->
  <section class="pt-2">
    <details class="group card-dark rounded-2xl p-4 border border-[#253147] transition">
      <summary class="flex items-center justify-between cursor-pointer font-bold text-xs text-slate-400 hover:text-white uppercase tracking-wider select-none">
        <span class="flex items-center gap-2">
          <svg class="h-4 w-4 text-cyan-400 group-open:rotate-90 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
          ดูตารางสแกนและค่าทางเทคนิคทั้งหมด 101 หุ้นใน Nasdaq-100 (คลิกเพื่อขยาย)
        </span>
        <span class="text-[11px] text-cyan-400 font-mono">Full Scanner Matrix</span>
      </summary>

      <div class="mt-4 pt-4 border-t border-[#253147] space-y-4">
        <!-- Filter inside matrix -->
        <div class="flex items-center justify-between gap-4">
          <input type="text" id="matrix-search-input" oninput="renderRawStocksTable()" placeholder="กรองค้นหา Ticker หรือชื่อบริษัท..." class="rounded-lg bg-[#0d1117] border border-[#253147] px-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400 font-mono w-64">
          <span class="text-xs text-slate-400 font-mono" id="matrix-count-badge">แสดง 101 หุ้น</span>
        </div>

        <div class="overflow-x-auto rounded-lg border border-[#253147] bg-[#111622] max-h-96">
          <table class="w-full text-left text-xs font-mono border-collapse">
            <thead class="bg-[#0d1117] text-slate-400 border-b border-[#253147] sticky top-0 z-10">
              <tr>
                <th class="py-2.5 px-3"># Rank</th>
                <th class="py-2.5 px-3">Symbol</th>
                <th class="py-2.5 px-3">ชื่อบริษัท</th>
                <th class="py-2.5 px-3 text-center">Signal</th>
                <th class="py-2.5 px-3 text-right">Price ($)</th>
                <th class="py-2.5 px-3 text-right">30d %</th>
                <th class="py-2.5 px-3 text-right">60d %</th>
                <th class="py-2.5 px-3 text-right">Score</th>
                <th class="py-2.5 px-3 text-center">Trend Gate</th>
                <th class="py-2.5 px-3">เหตุผล</th>
              </tr>
            </thead>
            <tbody id="raw-stocks-tbody" class="divide-y divide-[#1c2536] text-slate-200">
              <!-- Injected by JS -->
            </tbody>
          </table>
        </div>
      </div>
    </details>
  </section>

  <!-- Footer -->
  <footer class="text-center text-xs text-slate-500 pt-6 border-t border-[#253147]">
    Nasdaq-100 Quantitative Breadth & Leader Rotation Engine • Auto-updated daily at 16:30 EST via GitHub Actions • MIT License
  </footer>

  <!-- ================================================================= -->
  <!-- JAVASCRIPT LOGIC & REACTIVE DATA BINDING -->
  <!-- ================================================================= -->
  <script>
    const MASTER_DATA = {embedded_json};

    let activeStrategy = 'core_satellite';

    function initHub() {{
      const snapshot = MASTER_DATA.snapshot;

      // Date & Header
      document.getElementById('today-date-text').textContent = `DATE: ${{snapshot.metadata.last_updated_date}} (COMPLETED US SESSIONS)`;

      // Macro Regime
      const regime = snapshot.market_macro.regime;
      const rTitle = snapshot.market_macro.regime_title;
      const rDesc = snapshot.market_macro.regime_desc;

      document.getElementById('hero-regime-name').textContent = rTitle;
      document.getElementById('hero-regime-desc').textContent = rDesc;

      const rBadge = document.getElementById('hero-regime-badge');
      rBadge.textContent = `[${{regime}}]`;
      if (regime === 'CASH_GUARD') {{
        rBadge.className = 'text-xs px-2.5 py-0.5 rounded-full font-bold bg-rose-500/20 text-rose-300 border border-rose-500/40';
      }} else if (regime === 'BROAD_BULL') {{
        rBadge.className = 'text-xs px-2.5 py-0.5 rounded-full font-bold bg-teal-500/20 text-teal-300 border border-teal-500/40';
      }} else {{
        rBadge.className = 'text-xs px-2.5 py-0.5 rounded-full font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/40';
      }}

      // QQQ Trend Gate
      document.getElementById('hero-qqq-price').textContent = `$${{snapshot.market_macro.qqq_close.toFixed(2)}}`;
      const qTrendOk = snapshot.market_macro.qqq_trend_ok;
      const qStatusEl = document.getElementById('hero-qqq-status');
      if (qTrendOk) {{
        qStatusEl.textContent = '● PASSED (> EMA100)';
        qStatusEl.className = 'text-[10px] text-teal-400 block';
      }} else {{
        qStatusEl.textContent = '▲ FAILED (<= EMA100)';
        qStatusEl.className = 'text-[10px] text-rose-400 block';
      }}

      // Breadth
      document.getElementById('hero-breadth-pct').textContent = `${{snapshot.breadth.breadth_ema50_pct}}%`;
      document.getElementById('hero-breadth-count').textContent = `${{Math.round(snapshot.breadth.breadth_ema50_pct * snapshot.metadata.total_constituents / 100)}} / ${{snapshot.metadata.total_constituents}} stocks > EMA50`;

      // Set active strategy
      setStrategy(activeStrategy);

      // Render Past Timeline
      renderPastTimeline();

      // Render Raw Stocks Matrix
      renderRawStocksTable();
    }}

    function setStrategy(stratKey) {{
      activeStrategy = stratKey;

      // Update Card Highlights
      ['core_satellite', 'fast_alpha', 'legacy_adaptive'].forEach(k => {{
        const card = document.getElementById(`card-strat-${{k}}`);
        const chk = card.querySelector('.checkmark');
        if (k === stratKey) {{
          card.classList.add('strat-card-active');
          chk.classList.remove('hidden');
          chk.classList.add('text-cyan-400');
        }} else {{
          card.classList.remove('strat-card-active');
          chk.classList.add('hidden');
        }}
      }});

      const strat = MASTER_DATA.snapshot.strategies[stratKey];
      document.getElementById('active-strat-indicator').textContent = `กำลังใช้งาน: ${{strat.name}}`;
      document.getElementById('toast-text').textContent = `กำลังใช้งาน ${{strat.name}}: ${{strat.description}}`;
      document.getElementById('breakdown-strategy-name').textContent = strat.name;

      // Update Action Columns (SELL, BUY, HOLD)
      const actions = strat.actions || {{ buy: [], hold: [], sell: [] }};

      // 1. SELL Column
      const sellContainer = document.getElementById('sell-coins-list');
      sellContainer.innerHTML = '';
      document.getElementById('cnt-sell-badge').textContent = `${{actions.sell.length}} ตัว`;
      if (actions.sell.length === 0) {{
        sellContainer.innerHTML = '<div class="p-2 rounded bg-[#0d1117] text-slate-400 text-center text-[11px]">ไม่มีคำสั่งขายวันนี้ พอร์ตสมบูรณ์</div>';
      }} else {{
        actions.sell.forEach(item => {{
          sellContainer.innerHTML += `
            <div class="p-2 rounded-lg bg-[#0d1117] border border-rose-950/40 flex items-center justify-between">
              <div>
                <strong class="text-rose-400 text-xs">${{item.ticker}}</strong>
                <span class="text-[10px] text-slate-400 block">${{item.name}}</span>
              </div>
              <span class="text-[10px] px-1.5 py-0.5 rounded font-bold bg-rose-500/20 text-rose-300 font-mono">${{item.badge}}</span>
            </div>
          `;
        }});
      }}

      // 2. BUY Column
      const buyContainer = document.getElementById('buy-coins-list');
      buyContainer.innerHTML = '';
      document.getElementById('cnt-buy-badge').textContent = `${{actions.buy.length}} รายการ`;
      if (actions.buy.length === 0) {{
        buyContainer.innerHTML = '<div class="p-2 rounded bg-[#0d1117] text-slate-400 text-center text-[11px]">ตลาดปิด Risk-Off ถือเงินสด 100%</div>';
      }} else {{
        actions.buy.forEach(item => {{
          const wtStr = item.weight ? `${{(item.weight * 100).toFixed(1)}}%` : '';
          buyContainer.innerHTML += `
            <div class="p-2 rounded-lg bg-[#0d1117] border border-teal-950/40 flex items-center justify-between">
              <div>
                <strong class="text-teal-400 text-xs">${{item.ticker}}</strong>
                <span class="text-[10px] text-slate-400 block">${{item.name}}</span>
              </div>
              <div class="text-right">
                <span class="text-[11px] font-bold text-cyan-400 block tabular-nums">${{wtStr}}</span>
                <span class="text-[9px] text-slate-400 font-mono">${{item.badge}}</span>
              </div>
            </div>
          `;
        }});
      }}

      // 3. HOLD Column
      const holdContainer = document.getElementById('hold-coins-list');
      holdContainer.innerHTML = '';
      if (actions.hold.length === 0) {{
        holdContainer.innerHTML = '<div class="p-2 rounded bg-[#0d1117] text-slate-400 text-center text-[11px]">ไม่มีหุ้นค้างในเกราะ Buffer</div>';
      }} else {{
        actions.hold.forEach(item => {{
          holdContainer.innerHTML += `
            <div class="p-2 rounded-lg bg-[#0d1117] border border-cyan-950/40 flex items-center justify-between">
              <div>
                <strong class="text-cyan-400 text-xs">${{item.ticker}}</strong>
                <span class="text-[10px] text-slate-400 block">${{item.name}}</span>
              </div>
              <span class="text-[10px] px-1.5 py-0.5 rounded font-bold bg-cyan-500/20 text-cyan-300 font-mono">${{item.badge}}</span>
            </div>
          `;
        }});
      }}

      // Trigger Money Calculation
      recalculateAll();
    }}

    function recalculateAll() {{
      const inputEl = document.getElementById('quick-nav-input');
      let capital = parseFloat(inputEl.value);
      if (isNaN(capital) || capital <= 0) capital = 100000;

      const strat = MASTER_DATA.snapshot.strategies[activeStrategy];
      const allocations = strat.allocations;
      const tbody = document.getElementById('calculator-breakdown-tbody');
      tbody.innerHTML = '';

      let totalEquity = 0;
      let cashReserve = 0;

      const meta = MASTER_DATA.snapshot.stock_rankings.reduce((acc, x) => {{
        acc[x.ticker] = x;
        return acc;
      }}, {{}});

      meta['QQQ'] = {{ name: 'Invesco QQQ Trust (Nasdaq-100 Core)', price: MASTER_DATA.snapshot.market_macro.qqq_close }};
      meta['BIL'] = {{ name: 'SPDR 1-3 Month T-Bill (Cash Reserve)', price: MASTER_DATA.snapshot.market_macro.bil_close }};

      let idx = 1;
      for (const [ticker, weight] of Object.entries(allocations)) {{
        if (weight <= 0) continue;
        const info = meta[ticker] || {{ name: `${{ticker}} Corp`, price: 100.0 }};
        const dollars = capital * weight;
        const shares = Math.floor(dollars / info.price);

        if (ticker === 'BIL') {{
          cashReserve += dollars;
        }} else {{
          totalEquity += dollars;
        }}

        let actionText = '<span class="text-teal-400 font-bold">● ซื้อเปิดตลาด (Market Open)</span>';
        if (ticker === 'QQQ') {{
          actionText = '<span class="text-cyan-400 font-bold">● ถือครองแกนหลัก (Core)</span>';
        }} else if (ticker === 'BIL') {{
          actionText = '<span class="text-amber-400 font-bold">● พักเงินสดรับดอกเบี้ย</span>';
        }}

        tbody.innerHTML += `
          <tr class="hover:bg-[#161d2b]">
            <td class="py-2 px-3 text-slate-400 tabular-nums">${{idx++}}</td>
            <td class="py-2 px-3">
              <strong class="text-white">${{ticker}}</strong>
              <span class="text-[10px] text-slate-400 block">${{info.name}}</span>
            </td>
            <td class="py-2 px-3 text-right text-slate-300 tabular-nums">$${{info.price.toFixed(2)}}</td>
            <td class="py-2 px-3 text-right text-cyan-400 font-bold tabular-nums">${{(weight * 100).toFixed(1)}}%</td>
            <td class="py-2 px-3 text-right text-teal-400 font-bold tabular-nums">$${{dollars.toLocaleString('en-US', {{minimumFractionDigits: 2, maximumFractionDigits: 2}})}}</td>
            <td class="py-2 px-3 text-right text-slate-300 tabular-nums">${{shares.toLocaleString()}} หุ้น</td>
            <td class="py-2 px-3 text-center text-[11px]">${{actionText}}</td>
          </tr>
        `;
      }}

      document.getElementById('calc-total-equity').textContent = `$${{totalEquity.toLocaleString('en-US', {{minimumFractionDigits: 2, maximumFractionDigits: 2}})}} USD`;
      document.getElementById('calc-cash-reserve').textContent = `$${{cashReserve.toLocaleString('en-US', {{minimumFractionDigits: 2, maximumFractionDigits: 2}})}} USD`;
      document.getElementById('calc-fee-est').textContent = `~$${{(totalEquity * 0.0005).toFixed(2)}} USD`;

      // Visual pulse
      tbody.classList.remove('just-updated');
      void tbody.offsetWidth;
      tbody.classList.add('just-updated');
    }}

    function updateQuickCalc() {{
      recalculateAll();
    }}

    function renderPastTimeline() {{
      const container = document.getElementById('past-timeline-container');
      const query = (document.getElementById('timeline-search-input').value || '').trim().toUpperCase();

      const stratMap = {{
        core_satellite: 'Core_Satellite_50_50',
        fast_alpha: 'Fast_Alpha_Leader',
        legacy_adaptive: 'Adaptive_Regime_Guard',
      }};

      const stratKey = stratMap[activeStrategy] || 'Core_Satellite_50_50';
      const logs = MASTER_DATA.backtest.trade_logs[stratKey] || [];

      const filtered = logs.filter(item => {{
        if (!query) return true;
        return item.symbol.includes(query) || (item.reason && item.reason.includes(query));
      }}).slice(-60).reverse();

      container.innerHTML = '';
      if (filtered.length === 0) {{
        container.innerHTML = '<div class="text-center text-slate-500 py-6 text-xs">ไม่พบประวัติการส่งคำสั่งที่ค้นหา</div>';
        return;
      }}

      filtered.forEach(trade => {{
        const isBuy = trade.action === 'BUY';
        const badgeClass = isBuy
          ? 'bg-teal-500/20 text-teal-300 border-teal-500/40'
          : 'bg-rose-500/20 text-rose-300 border-rose-500/40';

        container.innerHTML += `
          <div class="p-3 rounded-xl bg-[#0d1117] border border-[#253147] flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs font-mono">
            <div class="flex items-center gap-3">
              <span class="px-2 py-0.5 rounded font-bold border ${{badgeClass}}">${{trade.action}}</span>
              <div>
                <strong class="text-white text-sm">${{trade.symbol}}</strong>
                <span class="text-slate-400 text-[11px] block mt-0.5">${{trade.reason || '--'}}</span>
              </div>
            </div>
            <div class="text-right tabular-nums text-[11px]">
              <span class="text-slate-400 block">${{trade.fill_date}} (ราคา fill: $${{trade.price.toFixed(2)}})</span>
              <strong class="text-white">$${{trade.notional.toLocaleString('en-US', {{minimumFractionDigits: 2, maximumFractionDigits: 2}})}}</strong>
            </div>
          </div>
        `;
      }});
    }}

    function renderRawStocksTable() {{
      const tbody = document.getElementById('raw-stocks-tbody');
      const query = (document.getElementById('matrix-search-input').value || '').trim().toUpperCase();
      const stocks = MASTER_DATA.snapshot.stock_rankings || [];

      const filtered = stocks.filter(s => {{
        if (!query) return true;
        return s.ticker.includes(query) || s.name.toUpperCase().includes(query);
      }});

      document.getElementById('matrix-count-badge').textContent = `แสดง ${{filtered.length}} / ${{stocks.length}} หุ้น`;
      tbody.innerHTML = '';

      filtered.forEach(s => {{
        let badgeColor = 'bg-slate-700/40 text-slate-400';
        if (s.signal === 'BUY') badgeColor = 'bg-teal-500/20 text-teal-300 border border-teal-500/30';
        else if (s.signal === 'HOLD') badgeColor = 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30';
        else if (s.signal === 'WATCHLIST') badgeColor = 'bg-amber-500/20 text-amber-300 border border-amber-500/30';
        else badgeColor = 'bg-rose-500/20 text-rose-300 border border-rose-500/30';

        tbody.innerHTML += `
          <tr class="hover:bg-[#161d2b]">
            <td class="py-2 px-3 text-slate-400 tabular-nums">${{s.rank}}</td>
            <td class="py-2 px-3"><strong class="text-white">${{s.ticker}}</strong></td>
            <td class="py-2 px-3 text-slate-300">${{s.name}}</td>
            <td class="py-2 px-3 text-center">
              <span class="px-2 py-0.5 rounded text-[10px] font-bold ${{badgeColor}}">${{s.signal_badge || s.signal}}</span>
            </td>
            <td class="py-2 px-3 text-right tabular-nums text-white">$${{s.price.toFixed(2)}}</td>
            <td class="py-2 px-3 text-right tabular-nums ${{s.ret30 >= 0 ? 'text-teal-400' : 'text-rose-400'}}">${{s.ret30 >= 0 ? '+' : ''}}${{s.ret30.toFixed(1)}}%</td>
            <td class="py-2 px-3 text-right tabular-nums ${{s.ret60 >= 0 ? 'text-teal-400' : 'text-rose-400'}}">${{s.ret60 >= 0 ? '+' : ''}}${{s.ret60.toFixed(1)}}%</td>
            <td class="py-2 px-3 text-right tabular-nums text-cyan-400 font-bold">${{s.momentum_score >= 0 ? '+' : ''}}${{s.momentum_score.toFixed(1)}}</td>
            <td class="py-2 px-3 text-center tabular-nums">
              <span class="text-[10px] font-bold ${{s.trend_gate ? 'text-teal-400' : 'text-rose-400'}}">${{s.trend_gate ? '● PASS' : '▲ FAIL'}}</span>
            </td>
            <td class="py-2 px-3 text-[11px] text-slate-400">${{s.action_reason || '--'}}</td>
          </tr>
        `;
      }});
    }}

    window.addEventListener('DOMContentLoaded', initHub);
  </script>
</body>
</html>
"""

    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[+] Successfully compiled interactive action-first terminal dashboard: {INDEX_HTML}")


if __name__ == "__main__":
    build_dashboard()
