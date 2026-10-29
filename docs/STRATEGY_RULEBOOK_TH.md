# คู่มือแม่บทกลยุทธ์เชิงปริมาณ (Strategy Rulebook): Nasdaq-100 Breadth & Leader Rotation Engine

---

## 1. ปรัชญาและโครงสร้างระบบ (System Philosophy)

ระบบ **Nasdaq-100 Breadth & Leader Rotation Engine** ได้รับการออกแบบขึ้นสำหรับบริหารพอร์ตหุ้นสหรัฐฯ ดัชนี Nasdaq-100 โดยสังเคราะห์ 3 เสาหลักเชิงปริมาณ:
1. **Market Breadth Regime**: ตรวจจับความกว้างของตลาดเพื่อวัดความแข็งแกร่งของเทรนด์ขาขึ้น
2. **Multi-Scale Momentum**: คัดเลือกหุ้นผู้นำที่มีโมเมนตัมเร็ว-กลาง-ยาวเด่นชัดที่สุดในกลุ่ม 101 หุ้น
3. **Risk-Aware Capped Allocation & Cash Yield**: จัดสรรน้ำหนักตามส่วนกลับของความผันผวน (**Inverse Realized Volatility**) คุมเพดานไม่เกิน 20% ต่อบริษัท และพักสภาพคล่องในกองทุนพันธบัตรระยะสั้นสหรัฐฯ (**BIL**) เพื่อรับผลตอบแทนดอกเบี้ย

---

## 2. กฎเกณฑ์การเทรด 4 ขั้นตอน (Four-Stage Execution Pipeline)

```
[ขั้นตอนที่ 1: ตรวจสอบ Macro Regime Gate (16:00 EST)]
QQQ > EMA100  AND  Breadth (สัดส่วนหุ้น > EMA50) >= Threshold
       │
       ├─► ตลาดหมี / Breadth อ่อนแอ (< 20%) ──► [EXIT_CASH_GUARD] พักเงินสด 100% ใน BIL
       │
       ▼ ผ่านเกณฑ์ (Regime Bull)
[ขั้นตอนที่ 2: สแกนจักรวาลหุ้น Nasdaq-100 (101 ตัว)]
คัดกรองเฉพาะหุ้นที่มีประวัติราคาอย่างน้อย 150 Sessions
       │
       ▼
[ขั้นตอนที่ 3: Single-Asset Technical Gate]
Close > EMA26  AND  EMA12 > EMA26
Momentum Score > 0  AND  R30 > 0  AND  R60 > 0
       │
       ▼
[ขั้นตอนที่ 4: คัดเลือก Top-K Leaders & คำนวณน้ำหนัก]
จัดอันดับตาม Momentum Score คัดเลือก Top 5 ผู้นำ
เกราะหน่วงอันดับ (Rank Hysteresis Buffer): ถือหุ้นเดิมต่อได้จนถึงอันดับ ⌈5 × 1.5⌉ = 8
จำกัดน้ำหนักไม่เกิน 20% ต่อบริษัท (รวม GOOG + GOOGL รวมกันไม่เกิน 20%)
ส่งคำสั่งเปิดตลาดในวันทำการถัดไป (09:30 EST Next-Open)
```

---

## 3. สมการคณิตศาสตร์และตัวแปรหลัก

### 3.1 ความกว้างของตลาด (Market Breadth Formula)
$$
Breadth_{EMA50, t} = \frac{\sum_{i \in NDX} \mathbb{I}(Close_{i,t} > EMA50_{i,t})}{N_{active}}
$$

### 3.2 การจำแนกสภาวะตลาด 4 ระดับ (Market Regimes)
1. **`[REGIME: BROAD BULL]`**: $QQQ > EMA100$ และ $Breadth_{EMA50} \ge 55\%$  
   *ตลาดกระทิงกระจายตัวกว้าง ถือครองหุ้นผู้นำเต็มอัตรา 95%–100%*
2. **`[REGIME: NORMAL BULL]`**: $QQQ > EMA100$ และ $35\% \le Breadth_{EMA50} < 55\%$  
   *ตลาดกระทิงปกติ กระจายตัวปานกลาง ถือครอง Top 3–5 หุ้นผู้นำ*
3. **`[REGIME: NARROW BULL]`**: $QQQ > EMA100$ และ $20\% \le Breadth_{EMA50} < 35\%$  
   *ตลาดขึ้นแบบกระจุกตัวในหุ้นขนาดใหญ่ แนะนำพึ่งพา QQQ Core เป็นแกนหลัก*
4. **`[REGIME: CASH GUARD]`**: $QQQ \le EMA100$ หรือ $Breadth_{EMA50} < 20\%$  
   *สัญญาณเตือนภัยตลาดหมี พักเงินสดในตั๋วเงินคลังสหรัฐฯ (100% BIL)*

### 3.3 คะแนนโมเมนตัมหลายกรอบเวลา (Multi-Scale Momentum Score)
$$
Score_t = (0.50 \times R_{30}) + (0.30 \times R_{60}) + (0.20 \times R_{120})
$$
*โดย $R_h = \frac{Close_t}{Close_{t-h}} - 1$*

### 3.4 การจัดสรรน้ำหนักผกผันตามความผันผวน (Inverse Volatility Weighting)
$$
w_i = \frac{1 / \sigma_{i, 63d}}{\sum_{j=1}^{K} (1 / \sigma_{j, 63d})}
$$
*โดย $\sigma_{i, 63d}$ คือ ส่วนเบี่ยงเบนมาตรฐานผลตอบแทนรายวัน 63 วัน แปลงเป็นค่ารายปี ($\times \sqrt{252}$)*

### 3.5 เพดานความเสี่ยงระดับบริษัท (Company-Level Risk Cap)
$$
w_i^* = \min(w_i, 0.20)
$$
*หมายเหตุ: กรณี Alphabet Inc. ถือทั้ง `GOOG` และ `GOOGL` ผลรวมของทั้งสองคลาสจะต้องไม่เกิน 20%*

---

## 4. กฎการ ซื้อ, ถือ, ขาย (Buy, Hold, Sell Criteria)

### 4.1 ซื้อเมื่อไหร่ (ENTRY)
* ผ่าน Macro Gate ($QQQ > EMA100$ และ Breadth $\ge$ Threshold ประจำกลยุทธ์)
* หุ้นผ่านเกณฑ์ Technical Gate ($Close > EMA26$, $EMA12 > EMA26$, $Score > 0$, $R_{30} > 0$, $R_{60} > 0$)
* ติดอันดับ Top 5 ที่คะแนนสูงสุด และยังไม่ได้ถือครอง

### 4.2 ถือเมื่อไหร่ (HOLD)
* หุ้นเดิมยังติดอันดับอยู่ในช่วงเกราะหน่วงอันดับ (อันดับ 1 ถึง 8)
* ราคายังยืนเหนือ $EMA26$ และ $EMA12 > EMA26$
* หากยังไม่ถึงรอบ Rebalance (21 Trading Sessions) และ Regime ไม่ได้เปลี่ยน ให้ถือต่อโดยปล่อยให้น้ำหนัก Drift ไปตามราคาตลาดเพื่อลดต้นทุนค่าคอมมิชชัน

### 4.3 ขายเมื่อไหร่ (EXIT)
1. **`EXIT_CASH_GUARD`**: ขายล้างพอร์ตทั้งหมดเข้าสู่ BIL เมื่อ $QQQ \le EMA100$ หรือ Breadth $< 20\%$
2. **`EXIT_TREND_FAIL`**: คัทลอสเฉพาะตัวที่ราคาหลุด $EMA26$
3. **`EXIT_HYSTERESIS_DROP`**: ขายเมื่อหุ้นเดิมคะแนนแผ่วจนหลุดอันดับ 8 เพื่อนำเงินไปซื้อหุ้นตัวใหม่ที่ติด Top 5
4. **`EXIT_REGIME_PRUNING`**: ลดจำนวนหุ้นถือครองเมื่อสภาวะตลาดเปลี่ยนจาก Broad Bull สู่ Normal Bull

---

## 5. การส่งคำสั่งและการบริหารต้นทุน (Execution Mechanics)

1. **จังหวะเวลา (Timing)**:  
   * **16:00 EST**: สัญญาณคำนวณจากราคาปิด (Market Close)  
   * **09:30 EST (วันรุ่งขึ้น)**: ส่งคำสั่งซื้อขายจริงที่ราคาเปิดตลาด (Market Open) เพื่อป้องกัน Lookahead Bias และรับมือกับ Overnight Gap
2. **ต้นทุนสมมติฐาน**: หักค่าคอมมิชชัน, สเปรด และ Slippage 5 bps (0.05%) ต่อทุก Notional ซื้อและขาย
3. **การแก้ปัญหาเงินสดติดลบ**: ใช้ขั้นตอน Fixed-Point Iteration คำนวณค่าธรรมเนียมล่วงหน้า ทำให้พอร์ตไม่มีการยืมมาร์จิ้นและเงินสดไม่ติดลบ
