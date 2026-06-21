---
name: edge_health_monitor_amh1_2026
description: Edge Health Monitor (AMH proposal
metadata: 
  node_type: memory
  type: project
  originSessionId: c20741c2-d11c-4052-813a-f3c503120558
---

Built **Edge Health Monitor** (`edge_health_monitor.py`, [REDACTED]09) — first of 5 sequential AMH (Andrew Lo Adaptive Markets) applications. Measures whether each 8L lens/signal is in the *efficiency* (edge dead) or *inefficiency* (edge alive) phase of the AMH cycle, via rolling-12M cross-sectional Spearman IC of signal[T] vs forward-3M return.

**Method**: panel from `ticker_prune` (440 liquid mã, 148 months 2014-01→2026-03), forward return = clean `LEAD(Close,60)` NOT corrupted profit_*. Monthly IC per signal, classify HEALTHY/FADING/DECAYED/FLIPPED/WEAK from full-history vs recent-12M IC + t-stat. Outputs `data/edge_health_ic.csv`, `data/edge_health_verdict.csv`, `edge_health_ic.png`. (scipy absent → manual pandas-rank Spearman.)

**Key findings (fwd-3M IC, universe-wide)**:
- **VALUE bền nhất & sống**: PE IC −0.089 (t=−11.4, HEALTHY), PB −0.092 (t=−7.3). Single most robust edge.
- **🔴 MOMENTUM FLIPPED last-12M**: mom_200 (Close/MA200) +0.052 full → −0.062 recent; D_RSI +0.055 → −0.036. Trend-following inverted to mean-reversion — the AMH inefficiency phase. Explains V4/V5 (momentum books) bleeding in grind 9/2025-3/2026; matches "2025 bull costs DT5G −0.89pp". Likely CYCLICAL (regime choppy) not permanent → motivates #3 regime-conditional fitness.
- **QUALITY splits**: FSCORE DECAYED (full +0.049→recent +0.005, crowded out), ROIC5Y FADING (0.46×), but ROE_Min5Y HEALTHY & strengthening (+0.048→+0.065). Quality ≠ one block: quality-FLOOR persists, accounting-score decays.
- **pb_z = WEAK/NOISE universe-wide** (t=1.27) despite being the "golden" discriminator in [[cheap_pb_floor_quality_crisis_2026]] — because its power is CONDITIONAL (abs-PB<1 & z<−1, in crisis/panic), not unconditional-linear. Directly proves the need for #3 Fitness Matrix (many edges are conditional).

**Caveats**: single 3M horizon under-states slow value edges (QT v4 value peaks at 3Y per [[qt_v4_eventstudy_2026]]).

**REFINEMENT ([REDACTED]09) — per-sector IC + alerts + daily cadence (all DONE):**
Super-sector from ICB_Code first digit (FIN 8xxx split BANK/REALEST/FINSVC, CYCLICAL 1/2, CONSUMER 3/5, UTILITY 7). Per-sector IC matrix is FAR richer than universe-wide — confirms AMH point #1 that "value"/"momentum" are NOT single edges:
- **VALUE is sector-OPPOSITE-signed**: PB recent IC STRENGTHENING in BANK (−0.101→−0.186) & CYCLICAL (−0.090→−0.120) = cheap wins; but FLIPPED in CONSUMER (−0.081→**+0.109**) & REALEST = expensive/growth wins. **pb_z = WEAK universe-wide but −0.238 in BANK** — resolves the v1 "noise" puzzle: pb_z is a BANK/financials edge, washed out pooled.
- **MOMENTUM flip is CYCLICAL+FINANCIAL, not consumer**: mom_200 FLIPPED in ALL/CYCLICAL/REALEST/FINSVC but still +0.021 in CONSUMER → V4/V5 momentum-bleed is a cyclical/financial phenomenon.
- **QUALITY lives in CONSUMER** (ROE/ROIC/FSCORE all ≈+0.09), DECAYED/neg in CYCLICAL & REALEST. ROE_Min5Y the one quality metric broadly STRENGTHENING (ALL/CYCLICAL/CONSUMER).
Alert tiers: RED=FLIPPED (sign-inverted, |t|≥2), ORANGE=DECAYED (<33% of full), GREEN=STRENGTHENING (>130%). Artifacts: `data/edge_health_matrix.csv`, `edge_health_status.json`, `edge_health_block.md` (compact block for 18:00 Telegram report — artifact ready, report-script wiring not yet done). Wired into `papertrade_daily.bat` step [11] `python edge_health_monitor.py --refresh` (idempotent; forward-3M IC only moves monthly so daily run is cheap-redundant-safe). `--refresh` re-pulls panel from BQ via bash subprocess.

AMH roadmap (sequential, user-directed): **#1 Edge Health Monitor ✅** → #2 Vol-target sizing layer → #3 Fitness Matrix (5-state × strategy) → #4 Ecology Dashboard (dispersion+breadth+sentiment) → #5 Biodiversity test for new strategies.

**🚨 LAG/PEAD edge ADDED ([REDACTED]10, sau khi V2.2 thành champion)** — EHM trước đó KHÔNG có family cho edge LAG earnings-drift (giờ là NỬA book V2.2). Rolling-12M health của e_hl3 entries (fwd-25td open→open): full-period +6.69%/64% win (n=2,321) NHƯNG **latest 12M = +0.26% mean / 42% win (n=261) = 3rd percentile lịch sử** — decay rõ: 2024 đỉnh (+9.8%/80% win) → trượt đều 2025 → 2026 sụp. KHÔNG phải chưa từng có: 2023Q1 cũng ~+1.0%/49% rồi hồi về +9.8% trong 12 tháng — cyclical theo AMH; cơ chế nghi = megacap-led 2025-26 starve mid-cap drift (cùng style-divergence giết momentum). **HÀNH ĐỘNG: (1) V2.2 go-live = paper-trade trước, KHÔNG xoay vốn thật mạnh khi engine chính đang ở đáy chu kỳ edge; (2) theo dõi `data/lag_edge_health.csv` — tín hiệu hồi = 12M-mean vượt ~+4-5%; (3) `biodiversity_test.py` incumbent vẫn = "MOMENTUM" (V4/V5 cũ) — PHẢI re-base sang V2.2 faithful NAV + corr BOOK-level (bài học corr signal≠book trong [[v4-faithful-reproduction-2026]]).** Carry-over matrix cho V2.2: EHM/Fitness/Ecology = tầng tín hiệu → giữ; vol-target verdict (redundant) transfers; biodiversity = re-base.


**WIRED VÒNG KÍN ([REDACTED]11)**: thêm `lag_edge_health()` vào edge_health_monitor.py — tự rebuild cohort e3 (NP_R≥15/prior4/pa_HL3≥5) từ cache daily (earnings_px.pkl), đo đúng hold 25 phiên của book, trailing-12M mean/win, ghi đè data/lag_edge_health.csv (trước đó là artifact tĩnh KHÔNG ai update). Ngưỡng→hành động pre-commit: ≥+4% HEALTHY (w_LAG .65 OK) / +1..4% NEUTRAL (giữ, không tăng) / 0..1% TROUGH (không tăng; vốn mới paper-trade) / <0 NEGATIVE (hạ .65→.50; âm 3 tháng liên tiếp → treo entry LAG mới). Thêm dòng momentum-FLIPPED → action hint (không nới slot/size; EXBULL-suppression dormant fix). NOW: LAG NEUTRAL +1.05%/win42%/pctile14 (asof 2026-05-06, trễ ~5 tuần do hold 25 phiên). ⚠️ Cohort mới = TOÀN BỘ e3 không lọc thanh khoản → n12=606 ≠ series nghiên cứu cũ n=261 (+0.26%) — mức tuyệt đối lệch nhẹ, percentile in kèm để đối chiếu; điều chỉnh w_LAG vẫn là quyết định NGƯỜI (monitor→shadow→commit).
