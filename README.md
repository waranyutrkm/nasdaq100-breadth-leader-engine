# Nasdaq-100 Breadth & Leader Rotation Engine v1.0
### *ระบบสแกนเนอร์เชิงปริมาณ, สลับกลยุทธ์หมุนหุ้นผู้นำ Nasdaq-100, และจำลองการบริหารพอร์ตแบบ Causal Next-Open*

[![GitHub Pages](https://img.shields.io/badge/Live%20Terminal-GitHub%20Pages-blue?style=for-the-badge&logo=github)](https://waranyutrkm.github.io/nasdaq100-breadth-leader-engine/)
[![Index](https://img.shields.io/badge/Universe-Nasdaq--100%20(NDX)-0A2540?style=for-the-badge)](https://www.nasdaq.com/market-activity/quotes/nasdaq-ndx-index)
[![Python](https://img.shields.io/badge/Engine-Python%203.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Sharpe](https://img.shields.io/badge/Sharpe%20(Excess%20BIL)-1.13%20(Core--Satellite)-00d293?style=for-the-badge)](https://github.com/waranyutrkm/nasdaq100-breadth-leader-engine)
[![License](https://img.shields.io/badge/License-MIT-gray?style=for-the-badge)](LICENSE)

---

## สารบัญ (Table of Contents)
1. [ภาพรวมและปรัชญาของระบบ (Project Overview)](#1-ภาพรวมและปรัชญาของระบบ)
2. [ผลการทดสอบย้อนหลัง 15 ปี (2011–2026 Performance Track Record)](#2-ผลการทดสอบย้อนหลัง-15-ปี-20112026)
3. [กฎการเทรดภาคปฏิบัติ: ซื้อ ถือ ขาย (Trading Rulebook)](#3-กฎการเทรดภาคปฏิบัติ-ซื้อ-ถือ-ขาย)
4. [สมการคณิตศาสตร์และตรรกะระบบ (Formulas & Architecture)](#4-สมการคณิตศาสตร์และตรรกะระบบ)
5. [โครงสร้างโปรเจกต์ (Project Structure)](#5-โครงสร้างโปรเจกต์)
6. [วิธีเปิดใช้งาน (Quick Start Guide)](#6-วิธีเปิดใช้งาน)
7. [การ Deploy ขึ้น GitHub Pages (Step-by-Step)](#7-การ-deploy-ขึ้น-github-pages)
8. [คำเตือนความเสี่ยง (Risk Disclaimer)](#8-คำเตือนความเสี่ยง)

---

## 1. ภาพรวมและปรัชญาของระบบ

> **"Strong trends are sustainable only when market participation is broad."**  
> *เทรนด์ขาขึ้นที่แข็งแกร่งจะยั่งยืน ก็ต่อเมื่อหุ้นส่วนใหญ่ในตลาดปรับตัวขึ้นพร้อมกัน*

ระบบ **Nasdaq-100 Breadth & Leader Rotation Engine** ได้รับการพัฒนาขึ้นโดยนำสถาปัตยกรรมเชิงปริมาณจาก Crypto Engine มาปรับปรุงโครงสร้างเพื่อรองรับตลาดหุ้นสหรัฐฯ (TradFi / US Equities) อย่างสมบูรณ์:
- **Causal Next-Open Execution**: คำนวณสัญญาณหลังตลาดปิด ($Close_t$) และส่งคำสั่งเปิดตลาดวันทำการถัดไป ($Open_{t+1}$) ขจัด Lookahead Bias และรับมือกับ Overnight Gap อย่างสมจริง
- **Point-in-Time Market Breadth**: วัดความกว้างของตลาดผ่านสัดส่วนหุ้น Nasdaq-100 ที่ยืนเหนือเส้นค่าเฉลี่ย EMA50, EMA100 และ EMA200
- **Turnover Suppression**: ใช้รอบ Rebalance ทุก 21 วันทำการ (ประมาณ 1 เดือน) พร้อมเกราะหน่วงอันดับ (Rank Hysteresis Buffer) ช่วยลด Turnover จาก 53 เท่าต่อปี เหลือเพียง 8–12 เท่าต่อปี ประหยัดค่าธรรมเนียมและ Slippage
- **Company Risk Cap**: จำกัดสัดส่วนไม่เกิน 20% ต่อหนึ่งบริษัท โดยรวมหุ้น Alphabet ทั้ง 2 คลาส (`GOOG` และ `GOOGL`) เข้าเป็นบริษัทเดียวกัน
- **Cash Yield Management**: พักสภาพคล่องที่ไม่ได้ถือหุ้นใน **SPDR Bloomberg 1-3 Month T-Bill ETF (BIL)** เพื่อรับผลตอบแทนจากอัตราดอกเบี้ยระยะสั้น

---

## 2. ผลการทดสอบย้อนหลัง 15 ปี (2011–2026)

ผลการจำลองพอร์ตจริงแบบ Causal Mark-to-Market บนข้อมูล Nasdaq-100 (101 หุ้น + QQQ + BIL) ระหว่างวันที่ 3 มกราคม 2011 ถึง 9 กันยายน 2026 (หลังหักค่าธรรมเนียมและ Slippage 5 bps):

| ตัวชี้วัดเชิงปริมาณ | QQQ Buy & Hold (Benchmark) | Core-Satellite (50:50) [แนะนำ] | Fast-Alpha Leader | Adaptive Regime Guard |
| :--- | :---: | :---: | :---: | :---: |
| **CAGR (ผลตอบแทนทบต้นต่อปี)** | +18.83% | **+23.59%** | **+26.67%** | **+26.39%** |
| **Max Drawdown (ขาดทุนสูงสุด)** | -35.12% | **-26.84%** | -35.31% | **-26.30%** |
| **Sharpe Ratio (หักผลตอบแทน BIL)** | 0.87 | **1.13** (สูงสุด) | 1.01 | 1.04 |
| **Sortino Ratio (Downside Risk)** | 1.14 | **1.56** | 1.41 | 1.48 |
| **Calmar Ratio (CAGR / MaxDD)** | 0.54 | **0.88** | 0.76 | 1.00 |
| **Beta เทียบกับ QQQ** | 1.00 | **0.73** | 0.46 | 0.48 |
| **Win Rate vs QQQ (รอบ 63 วัน)** | — | **68.4%** | 62.1% | 64.2% |
| **สินทรัพย์ที่ใช้พักเงินสด** | — | 100% BIL | 100% BIL | 100% BIL |

> [!NOTE]
> **ทำไมโมเดล Core-Satellite ถึงเป็นตัวเลือกแนะนำสูงสุด?**  
> ตลาดหุ้นสหรัฐฯ มีลักษณะเด่นคือ Mega-Cap Concentration (กลุ่ม Magnificent 7 มีน้ำหนัก 40–50% ของดัชนี) ในช่วงตลาดขาขึ้นแบบแคบ (Narrow Rally เช่นปี 2023–2025) หากใช้ระบบ Pure Leader ที่รอให้ Breadth กว้าง พอร์ตอาจตกรอบการขึ้นได้ โมเดล Core-Satellite (50% QQQ Core + 50% Leader Satellite) ช่วยให้พอร์ตเกาะการขึ้นของดัชนีได้เสมอ ขณะเดียวกันก็สร้าง Alpha ส่วนเพิ่มจากหุ้นผู้นำ พร้อมลด Drawdown ลงกว่า 8%

---

## 3. กฎการเทรดภาคปฏิบัติ: ซื้อ ถือ ขาย

### 3.1 ซื้อเมื่อไหร่ (ENTRY)
ต้องผ่านเกณฑ์ครบทั้ง 3 มิติ:
1. **Macro Regime Gate**: $QQQ > EMA100$ และความกว้างตลาด $Breadth_{EMA50} \ge 35\%$
2. **Single-Asset Gate**: หุ้นผ่านเกณฑ์ $Close > EMA26$, $EMA12 > EMA26$, และ Momentum Score $> 0$ โดยมีผลตอบแทน $R_{30} > 0, R_{60} > 0$
3. **Allocation**: ติดอันดับ Top 5 ที่คะแนนโมเมนตัมสูงสุด จัดสรรตามน้ำหนัก **Inverse 63d Volatility** คุมเพดานไม่เกิน 20% ต่อบริษัท

### 3.2 ถือเมื่อไหร่ (HOLD)
* **เกราะหน่วงอันดับ (Hysteresis Buffer)**: หุ้นเดิมที่ถืออยู่อันดับหล่นไปที่ 6–8 แต่ยังไม่หลุดอันดับ 8 ($\lceil 5 \times 1.5 \rceil = 8$) ให้ถือต่อเพื่อหลีกเลี่ยงการสลับหุ้นไปมา
* **เทรนด์ยังไม่เสีย**: ราคายังยืนเหนือ $EMA26$
* **Holding Drift**: ปล่อยให้น้ำหนักขยับตามราคาตลาดในระหว่างรอบ 21 วันทำการ ไม่ปรับพอร์ตรายวันเพื่อประหยัดต้นทุน

### 3.3 ขายเมื่อไหร่ (EXIT)
1. `[EXIT_CASH_GUARD]`: ขายล้างพอร์ตทั้งหมดเข้าสู่ BIL (T-Bills) ทันทีเมื่อ $QQQ \le EMA100$ หรือ Breadth $< 20\%$
2. `[EXIT_TREND_FAIL]`: คัทลอสเฉพาะหุ้นที่ราคาหลุด $EMA26$
3. `[EXIT_HYSTERESIS_DROP]`: ขายเมื่อหุ้นเดิมคะแนนแผ่วจนหลุดอันดับ 8 เพื่อสลับไปซื้อตัวใหม่ที่ติด Top 5
4. `[EXIT_REGIME_PRUNING]`: ลดน้ำหนักหุ้นถือครองเมื่อ Breadth ลดลงจาก Broad สู่ Normal

---

## 4. สมการคณิตศาสตร์และตรรกะระบบ

### 4.1 Market Breadth
$$
Breadth_{EMA50, t} = \frac{\sum_{i \in NDX} \mathbb{I}(Close_{i,t} > EMA50_{i,t})}{N_{active}}
$$

### 4.2 Multi-Scale Momentum Score
$$
Score_t = (0.50 \times R_{30}) + (0.30 \times R_{60}) + (0.20 \times R_{120})
$$

### 4.3 Inverse Volatility Weighting
$$
w_i = \frac{1 / \sigma_{i, 63d}}{\sum_{j=1}^{K} (1 / \sigma_{j, 63d})} \quad \text{โดยที่} \quad w_i \le 0.20
$$

---

## 5. โครงสร้างโปรเจกต์

```text
nasdaq100-breadth-leader-engine/
├── .github/
│   └── workflows/
│       └── daily_update.yml        # GitHub Actions รันอัปเดตข้อมูลและ Deploy อัตโนมัติทุกวันทำการ
├── core/
│   ├── __init__.py
│   ├── engine.py                   # Causal Portfolio Engine (Next-Open fill, DRIFT, BIL yield)
│   ├── breadth_model.py            # Breadth Indicator & 4-Tier Regime Classifier
│   └── leader_selector.py          # Multi-Scale Momentum, Inverse Vol, 20% Company Cap
├── scripts/
│   ├── fetch_market_data.py        # ดึงราคา OHLCV สดผ่าน yfinance
│   ├── generate_signals.py         # คำนวณสัญญาณวันนี้, Regime และสัดส่วนพอร์ต
│   ├── run_backtest_audit.py       # รัน Backtest 15 ปีและคำนวณสถิติ
│   └── build_dashboard.py          # คอมไพล์ index.html พร้อมฝังข้อมูลสำหรับ GitHub Pages
├── data/
│   ├── open.csv, close.csv...      # เมทริกซ์ราคาและปริมาณการซื้อขายย้อนหลัง
│   ├── universe_constituents.csv   # รายชื่อ 101 หุ้น Nasdaq-100 พร้อมชื่อและ Sector
│   ├── latest_market_snapshot.json # ข้อมูล Snapshot สัญญาณสดประจำวัน
│   └── backtest_results.json       # ผลลัพธ์การตรวจสอบย้อนหลัง 2011–2026
├── docs/
│   ├── STRATEGY_RULEBOOK_TH.md     # คู่มือแม่บทและกฎการเทรดฉบับเต็ม
│   └── RESEARCH_AUDIT_REPORT_TH.md # รายงานการวิจัยเชิงปริมาณและการทดสอบความเค้น
├── tests/
│   └── test_engine.py              # ชุดการทดสอบ Unit Tests
├── index.html                      # Standalone Interactive Dashboard (Deploy ขึ้น GitHub Pages ได้ทันที)
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 6. วิธีเปิดใช้งาน (Quick Start Guide)

### วิธีที่ 1: เปิด Dashboard ทันที (Zero Install)
ดับเบิลคลิกเปิดไฟล์ `index.html` บนเว็บเบราว์เซอร์ (Chrome, Safari, Edge, Brave) ใช้งานได้ทันที 100% โดยไม่ต้องลง Database หรือ Backend

### วิธีที่ 2: รันผ่าน Local Web Server
```bash
cd nasdaq100-breadth-leader-engine
python3 -m http.server 8080
```
เปิดเบราว์เซอร์ไปที่: `http://localhost:8080`

### วิธีที่ 3: อัปเดตข้อมูลสดและคอมไพล์ใหม่
```bash
# ติดตั้ง Library
pip install -r requirements.txt

# รัน Unit Tests ตรวจสอบระบบ
python3 -m unittest discover -s tests -p 'test_*.py' -v

# อัปเดตข้อมูลราคาล่าสุดจาก Yahoo Finance
python3 scripts/fetch_market_data.py

# คำนวณสัญญาณสดประจำวัน
python3 scripts/generate_signals.py

# คอมไพล์ Dashboard ใหม่
python3 scripts/build_dashboard.py
```

---

## 7. การ Deploy ขึ้น GitHub Pages

1. สร้าง Repository ใหม่บน GitHub ในชื่อ: `nasdaq100-breadth-leader-engine`
2. อัปโหลดไฟล์ขึ้น GitHub:
   ```bash
   cd nasdaq100-breadth-leader-engine
   git init -b main
   git add .
   git commit -m "feat: Initial release of Nasdaq-100 Breadth & Leader Rotation Engine v1.0"
   git remote add origin https://github.com/<YOUR_USERNAME>/nasdaq100-breadth-leader-engine.git
   git push -u origin main
   ```
3. ไปที่เมนู **Settings** ของ Repository บน GitHub:
   - คลิกแท็บ **Pages** (ทางซ้ายมือ)
   - ใต้หัวข้อ **Build and deployment**:
     - Source: `Deploy from a branch`
     - Branch: `main` / Folder: `/ (root)`
     - กด **Save**
4. ภายใน 1–2 นาที แดชบอร์ดจะออนไลน์สดทันทีที่:  
   `https://<YOUR_USERNAME>.github.io/nasdaq100-breadth-leader-engine/`

---

## 8. คำเตือนความเสี่ยง

เอกสารและซอร์สโค้ดนี้จัดทำขึ้นเพื่อการศึกษาและการวิจัยเชิงปริมาณ (Quantitative Research & Educational Purposes) เท่านั้น ไม่ใช่คำแนะนำทางการเงินหรือการชักชวนให้ลงทุน การลงทุนในตราสารทุนและตลาดหุ้นสหรัฐฯ มีความเสี่ยง ผู้ลงทุนควรศึกษาข้อมูลอย่างรอบคอบและทดสอบ Paper Trade ก่อนตัดสินใจนำไปใช้งานจริง
