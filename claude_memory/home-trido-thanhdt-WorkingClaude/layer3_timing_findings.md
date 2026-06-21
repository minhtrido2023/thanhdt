---
name: Intraday BUY/SELL timing for BA-system (3-segment + slippage)
description: 29,260-session study (top30/midcap/penny × ~225 phiên, Aug25-May26, vnstock API only) — production-ready rules for entry/exit timing with Almgren-Chriss slippage model
type: project
originSessionId: 90878235-541c-4207-a725-44398117b136
---
Scripts: `layer3_full_analysis.py` (full analysis), `layer3_entry_timing.py` (top30 only), cache `intraday_full.pkl`, panel `layer3_full_panel.csv`.

**Universe (vnstock API only for intraday, BQ for liquidity ranking + daily forward):**
- TOP30: ADV ≥ 270B VND/day (n=6,737 sessions)
- MIDCAP: ADV 25-50B VND/day (n=9,469)
- PENNY: ADV 5-10B VND, price < 15k VND (n=13,054)

**BUY pattern (universal U-shape across segments):** giá rẻ nhất tại 11:15-13:00. Saving vs OPEN:
- TOP30: T1115 −0.22%
- MIDCAP: T1300 −0.30%
- PENNY: T1300 −0.27% (median; mean corrupted by limit-move outliers, ALWAYS use median for penny)

**SELL pattern (opposite — sell sớm):**
- TOP30/MIDCAP: bán 09:30-09:45 hoặc OPEN (mean_diff_vs_open ~0 vs −0.3% giữa phiên)
- PENNY: ATC (20.2% phiên ATC = day high, cao nhất trong các slot)

**Slippage model:** `impact_pct = sqrt(position_size / bar_volume_vnd).clip(0,5) × bar_range_pct/2`. Almgren-Chriss inspired.

**NET advantage = timing_save − expected_impact (per trade):**
- TOP30 @ 1B VND: **T1115 = +0.141%** ⭐ (timing 0.224 − impact 0.083)
- MIDCAP @ 500M: **T1430/ATC = +0.084%** (lunch slot 11:15-13:00 bị slippage ăn hết: timing 0.22% − impact 0.22% = net 0)
- PENNY @ 200M: ALL slots have impact >0.3%, fill_rate >1000% → must TWAP across 4-6 bars

**Why MIDCAP/PENNY different from TOP30:**
- Volume profile dips most at 11:00-11:15 (lunch break approach) — exactly where timing benefit peaks
- For thinly traded segments, single-bar fill impossible at lunch → must shift to ATC where volume rebuilds

**Production rules (proposed):**
- BUY TOP30: limit @ 11:15 close, fallback ATC market
- BUY MIDCAP: market @ ATC or 14:30 limit
- BUY PENNY: TWAP 10:30-13:30 (4-6 bars), never single-shot
- SELL TOP30/MIDCAP: market @ OPEN or limit @ 09:45
- SELL PENNY: ATC market
- Gap exception: gap < −1% → BUY @ OPEN; gap > +1% → BUY @ ATC

**Expected BA-system impact at 50B NAV:** ~+0.6pp CAGR (40 BUYs × 0.10% + 40 SELLs × 0.05%, each affecting 10% of portfolio). Modest but real.

**Caveats:** (a) 9 months only — pattern may shift across regimes; (b) limit-order fill risk not modeled; (c) Almgren-Chriss simplistic — no permanent impact or adverse selection; (d) PENNY mean corrupted by limit moves, [REDACTED] use median.
