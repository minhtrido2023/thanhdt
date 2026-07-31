📋 **Paper Programs Daily Report — 2026-07-31**
Render 11:45 ICT · registry v3 · 8 chương trình · *vintage dữ liệu xem `asof`/nguồn từng mục (BQ chưa có close phiên T lúc 16:00)*
⏳ **Theo dõi** (1): #4 Fill-timing window (BUY 10:45-11:15 / SELL 09:15-09:45)

**TỔNG QUAN** — badge · chương trình · số hôm nay · giao dịch hôm nay:
✅ **1) DC-book NEUTRAL idle-cash Waterfall** — NAV 977,555,174đ · lũy kế -2.24% · phiên gần nhất +2.98% (as-of 2026-07-30) | 💱 **Không có giao dịch** — turnover 0.00% · rebalanced=False · deployed…
✅ **2) EXTREME-regime gate** — 17 phiên journal `main` (gần nhất in_2026-07-31) · marker hôm nay **0** / lũy kế **0** | 💱 **2 lệnh khớp** — SELL HPG 100@21750.0 · SELL VNM 100@61200.0 [đặt 2…
✅ **3) Vol-scale buy chase-cap (patch#3)** — 17 phiên journal `main` (gần nhất in_2026-07-31) | 💱 **2 lệnh khớp** — SELL HPG 100@21750.0 · SELL VNM 100@61200.0 [đặt 2…
⏳ **4) Fill-timing window (BUY 10:45-11:15 / SELL 09:15-09:45)** — ft-notes 154 placements | in-window 54% | out-of-window 46% --- B. ERRORS / REJECTS (must be 0… | 💱 **2 lệnh khớp** — SELL HPG 100@21750.0 · SELL VNM 100@61200.0 [đặt 2…
✅ **5) AlphaLens Paper (FPT/ACB/MBB/HDB vs VNINDEX)** — EW **-4.29%** vs VNINDEX -6.20% → **excess +1.91pp** (MTM as-of 2026-07-30) | 💱 **Không có giao dịch** — buy-and-hold theo thiết kế (equal-weight 25%…
✅ **6) ORB intraday VN30F (ring-fenced)** — asof 2026-07-30 | 38 phiên từ 2026-06-09 | NAV 1.063B (+6.32%) | WR 57.9% | phiên cuối +2.19%… | 💱 **CÓ giao dịch** — sig +1 · vào 1,849.1 → ra 1,890.0 · net +2.19% (1…
✅ **7) Capitulation-sleeve shadow (DT5G × 8L washout)** — asof 2026-07-29 | mode DEPLOYED | NAV 48.53B | tier NONCRISIS size=0.75 | entry 2026-07-20 | b… | 💱 **Không có giao dịch** — mode DEPLOYED · 5 mã · HOLDING 7/60td · 5 na…
✅ **8) Engine-room OOS panel (V11/V12/V4 vs V2.3-book vs VNINDEX)** — V2.3-book -5.28% vs VNINDEX -5.22% (cửa sổ chung, NAV rebase 50B) | 💱 **n/a theo thiết kế** — panel so sánh NAV của 5 sổ MÔ PHỎNG (V11/V12/…

── **1) DC-book NEUTRAL idle-cash Waterfall** · 👤 Taylor · ✅ GREEN
📈 NAV 977,555,174đ · lũy kế -2.24% · phiên gần nhất +2.98% (as-of 2026-07-30) · 📅 phiên ~20 từ 2026-07-06 · ⏱ nghiệm thu: event-anchored: chu kỳ reverse-unwind ĐẦU TIÊN + settle 4-6 tuần · trần 2026-10-06
💱 Giao dịch hôm nay: **Không có giao dịch** — turnover 0.00% · rebalanced=False · deployed=True · sleeve +2.98% · nguồn `data/dc_book_waterfall_paper_nav.csv` ⚠️ **chưa có dòng cho 2026-07-31** — số dưới đây là phiên gần nhất (2026-07-30), KHÔNG phải hôm nay
📊 Gate (bản đầy đủ, lần đầu ghi nhận):
  ⏳ Trọn 1 chu kỳ deploy → reverse-unwind → settle trên paper, đúng thứ tự ưu tiên thiết kế
  ⏳ P&L sleeve NET-of-TC không mâu thuẫn backtest (+5.0pp/năm sleeve parking kỳ vọng)
  ⏳ User sign-off sau review event-anchored (Mike + Taylor đề xuất ngày khi đủ điều kiện)
  ↳ charter đầy đủ: `mike/kb/paper_programs_charter/dc_waterfall.md`
📌 Charter vừa cập nhật hôm nay (mục đích/tiêu chí đổi trong registry) — `mike/kb/paper_programs_charter/dc_waterfall.md`
### 🪜 DC-book NEUTRAL Waterfall — Paper Sleeve (v2)
*Tiền rảnh NEUTRAL: BAL/LAG → DC book (double-confirm, liq≥3B) → custom30V, **continuous-residual** | cap gộp 0.15/tên · rebal q2m5 | flag `dc_book_waterfall_enabled`=ON (chỉ paper `main`) | as-of 2026-07-30 00:00:00*

- Trạng thái hôm nay: NEUTRAL → waterfall chạy LIÊN TỤC trên phần tiền dư (BAL/LAG có deal hôm nay — v2 KHÔNG tắt sleeve, chỉ phần dư nhỏ lại)
- Nhịp rebal: giữ nguyên, trọng số drift (q2m5 — chưa tới kỳ)
- DC book (8): ACB, CTR, FPT, HAH, MBB, PVT, SSI, TCB @ 0.0%/tên (leg 0.0%) | custom30V 0.0% | cash 0.0%
- DCF check (informational, không tham gia chọn mã): ACB NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 Gordon P/B (ngân hàng): P/B 1.31 vs hợp lý 2.25 (ROE5Y 23.0%, COE 13%/g 5%) — CHEAP [đã validate (bank_compounder_screen)] · CTR 🔴 RICH (giá trị hợp lý ~68,943đ vs giá 71,000đ, MoS -3.0%, không robust) · FPT 🟢 CHEAP (giá trị hợp lý ~79,333đ vs giá 67,000đ, MoS +15.6%, robust) · HAH NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 🟢 EV/EBITDA (cảng/hạ tầng): EV/EBITDA 3.8x (cheap <8x, benchmark mature 4-8x) — CHEAP [framework (n nhỏ — cần margin/ROIC xác nhận kèm)] · MBB NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 Gordon P/B (ngân hàng): P/B 1.21 vs hợp lý 2.21 (ROE5Y 22.7%, COE 13%/g 5%) — CHEAP [đã validate (bank_compounder_screen)] · PVT NOT_COMPUTED (fcfe_negative_buildout) → thay th
… (cắt bớt, xem nguồn để đủ; exit=0)
🔍 Nguồn: `data/dc_book_waterfall_paper_state.json` · `data/dc_book_waterfall_paper_nav.csv`

── **2) EXTREME-regime gate** · 👤 Taylor · ✅ GREEN
📈 17 phiên journal `main` (gần nhất in_2026-07-31) · marker hôm nay **0** / lũy kế **0** · 📅 14/20 phiên evidence · ⏱ nghiệm thu: đủ 20 phiên evidence benign + 0 false-trigger → user sign-off (ước ~2026-08-03)
💱 Giao dịch hôm nay: **2 lệnh khớp** — SELL HPG 100@21750.0 · SELL VNM 100@61200.0 [đặt 2 · khớp 2 · lỗi 0] · nguồn `data/execution_logs/exec_main_2026-07-31_journal.csv`
📊 Gate (bản đầy đủ, lần đầu ghi nhận):
  ✅ Stress-injection 24/24 PASS (arm 2-poll · sell-to-floor · buy-pause · cadence ×0.25 + negative controls) — stress_extreme_regime.py, week-1
  ⏳ ZERO false-trigger qua ~4 tuần benign trên account paper main
  ⏳ Không can thiệp NORMAL-path
  ⏳ User sign-off trước khi bật live
  ↳ charter đầy đủ: `mike/kb/paper_programs_charter/extreme_regime.md`
📌 Charter vừa cập nhật hôm nay (mục đích/tiêu chí đổi trong registry) — `mike/kb/paper_programs_charter/extreme_regime.md`
- Marker: EXTREME_PAUSE=0, EXTREME_SELL=0, EXTREME_DOWN=0, EXTREME_UP=0
🔍 Nguồn: `data/execution_logs/exec_main_*_journal.csv` · `secrets/trading_bot_accounts.json (extreme_regime_enabled=true, chỉ paper main)` · `stress_extreme_regime.py`

── **3) Vol-scale buy chase-cap (patch#3)** · 👤 Taylor · ✅ GREEN
📈 17 phiên journal `main` (gần nhất in_2026-07-31) · 📅 14/10 phiên evidence · ⏱ nghiệm thu: paper sạch + skeptic rerun REAL-fill + user sign-off (checkpoint ~2026-07-14 đã qua, CHƯA xác nhận)
💱 Giao dịch hôm nay: **2 lệnh khớp** — SELL HPG 100@21750.0 · SELL VNM 100@61200.0 [đặt 2 · khớp 2 · lỗi 0] · nguồn `data/execution_logs/exec_main_2026-07-31_journal.csv`
📊 Gate (bản đầy đủ, lần đầu ghi nhận):
  ✅ Executor-path stress 15/15 PASS (wiring · WIDEN clamp-to-ceil · MONOTONE · fail-safe rvol absent/0/<0 · NEG-control) — stress_vol_scale_chase_cap.py
  ⏳ Paper sạch: wiring đúng trên quote thật + fail-safe khi thiếu rvol cache
  ⏳ Không can thiệp NORMAL-path ngày non-gap
  ⏳ Skeptic rerun REAL-fill vs min(open,L) proxy trên correlated gap-up @NAV target
  ⏳ User sign-off trước khi bật live
  ↳ charter đầy đủ: `mike/kb/paper_programs_charter/vol_scale_chase_cap.md`
📌 Charter vừa cập nhật hôm nay (mục đích/tiêu chí đổi trong registry) — `mike/kb/paper_programs_charter/vol_scale_chase_cap.md`
🔍 Nguồn: `data/execution_logs/exec_main_*_journal.csv` · `secrets/trading_bot_accounts.json (chase_cap_vol_scale_enabled=true, chỉ paper main)` · `stress_vol_scale_chase_cap.py`

── **4) Fill-timing window (BUY 10:45-11:15 / SELL 09:15-09:45)** · 👤 Taylor · ⏳ WATCH
📈 ft-notes 154 placements | in-window 54% | out-of-window 46%

--- B. ERRORS / REJECTS (must be 0 or explained) ---
   journal FAIL/ERROR events: 431

--- C. DIRECTIONAL FILL SANITY (needs day-open; bps EDGE itself needs weeks, not gated here) ---
   no completed fills yet
_(checklist GO/NO-GO tiếng Anh của probe đã lược — trùng gate tiếng Việt, xem charter)_ · 📅 phiên ~23/23 (2026-07-01→2026-07-31) · ⏱ nghiệm thu: ≥5 phiên có BUY fill trong cửa sổ + 0 reject → quant-skeptic → user sign-off
💱 Giao dịch hôm nay: **2 lệnh khớp** — SELL HPG 100@21750.0 · SELL VNM 100@61200.0 [đặt 2 · khớp 2 · lỗi 0] · nguồn `data/execution_logs/exec_main_2026-07-31_journal.csv`
⚠️ Cảnh báo: journal FAIL/ERROR events: 431 → ⏳ cần theo dõi: 431 sự kiện lỗi này TOÀN BỘ thuộc 1 ngày 2026-07-30 (sự cố A: PaperBroker.place_order thiếu tham số cash_only → mọi lệnh paper-main crash), đã fix + verify cùng ngày; 0 lỗi trong journal 2026-07-31. Đây là số LŨY KẾ từ 2026-06-26 nên còn hiện cho tới khi cửa sổ trượt qua. Chi tiết: mike/kb/incidents/2026-07/2026-07-30-paper-trading-report-3-root-causes.md
📊 Gate (bản đầy đủ, lần đầu ghi nhận):
  ⏳ BUY window adherence cao (lệnh dồn 10:45-11:15)
  ⏳ SELL window adherence cao (lệnh tại open 09:15-09:45)
  ⏳ 0 rejects/fails (hoặc từng cái được giải thích)
  ⏳ BUY fill không tệ hơn open đáng kể; SELL không thấp hơn open đáng kể
  ⏳ quant-skeptic → user sign-off mới flip fill_timing_live_gate
  ↳ charter đầy đủ: `mike/kb/paper_programs_charter/fill_timing.md`
📌 Charter vừa cập nhật hôm nay (mục đích/tiêu chí đổi trong registry) — `mike/kb/paper_programs_charter/fill_timing.md`
=== EXECUTION-QUALITY REVIEW (since 2026-06-26) ===

--- A. WINDOW ADHERENCE (mechanics: did orders release in the right time-of-day?) ---
   journal ft-notes: 154 placements | in-window 54% | out-of-window 46%

--- B. ERRORS / REJECTS (must be 0 or explained) ---
   journal FAIL/ERROR events: 431

--- C. DIRECTIONAL FILL SANITY (needs day-open; bps EDGE itself needs weeks, not gated here) ---
   no completed fills yet
_(checklist GO/NO-GO tiếng Anh của probe đã lược — trùng gate tiếng Việt, xem charter)_
🔍 Nguồn: `execution_quality_review.py` · `data/execution_logs/exec_*_journal.csv (ft-notes)`

── **5) AlphaLens Paper (FPT/ACB/MBB/HDB vs VNINDEX)** · 👤 DollarBill · ✅ GREEN
📈 EW **-4.29%** vs VNINDEX -6.20% → **excess +1.91pp** (MTM as-of 2026-07-30) · 📅 phiên ~23/66 (2026-07-01→2026-09-30) · ⏱ nghiệm thu: 2026-09-30 — audit độc lập bởi Taylor
💱 Giao dịch hôm nay: **Không có giao dịch** — buy-and-hold theo thiết kế (equal-weight 25%/tên, không rebalance, giữ tới 2026-09-30)
📊 Gate (bản đầy đủ, lần đầu ghi nhận):
  ⏳ Excess return dương vs VNINDEX qua full window 3 tháng
  ⏳ Exit conditions per-name không bị vi phạm sớm (PE > PE_MA1Y / PB > justPB)
  ⏳ Audit độc lập bởi Taylor tại 2026-09-30
  ↳ charter đầy đủ: `mike/kb/paper_programs_charter/alphalens.md`
📌 Charter vừa cập nhật hôm nay (mục đích/tiêu chí đổi trong registry) — `mike/kb/paper_programs_charter/alphalens.md`
- Vị thế (MTM as-of 2026-07-30, BQ cache close phiên gần nhất):
  • FPT: 70,200 → 67,000 = **-4.56%** (entry 2026-07-01, PE vs PE_MA1Y)
  • ACB: 22,650 → 22,350 = **-1.32%** (entry 2026-07-01, P/B vs Gordon justified-PB)
  • MBB: 25,200 → 22,500 = **-10.71%** (entry 2026-07-01, P/B vs Gordon justified-PB)
  • HDB: 25,850 → 25,700 = **-0.58%** (entry 2026-07-01, P/B vs Gordon justified-PB)
- VNINDEX 1,860.01 → 1,744.66
🔍 Nguồn: `data/alphalens_paper.json` · `data/bq_cache/ticker_1m.parquet (Close + VNINDEX, sync 23:45 ICT)`

── **6) ORB intraday VN30F (ring-fenced)** · 👤 Taylor · ✅ GREEN
📈 asof 2026-07-30 | 38 phiên từ 2026-06-09 | NAV 1.063B (+6.32%) | WR 57.9% | phiên cuối +2.19% (sig +1) | Sharpe report 2.82 (mẫu nhỏ — đọc thận trọng) · 📅 phiên ~39 từ 2026-06-09 · ⏱ nghiệm thu: ≥60 phiên GỒM chop/bear → re-eval quant-skeptic (điều kiện REGIME, không có deadline lịch)
💱 Giao dịch hôm nay: **CÓ giao dịch** — sig +1 · vào 1,849.1 → ra 1,890.0 · net +2.19% (1 lượt/phiên theo thiết kế ORB) · nguồn `data/orb_pt_log.csv` ⚠️ **chưa có dòng cho 2026-07-31** — số dưới đây là phiên gần nhất (2026-07-30), KHÔNG phải hôm nay
📊 Gate (bản đầy đủ, lần đầu ghi nhận):
  ⏳ ≥60 phiên paper GỒM giai đoạn chop/bear (hiện toàn benign uptrend — chưa đủ điều kiện đánh giá)
  ⏳ Walk-forward 2024 full-year loss được giải thích/không lặp lại trong forward window
  ⏳ Hạ tầng phái sinh: tài khoản VSD margin + đường thực thi VN30F (bot hiện CASH-EQUITY ONLY — chưa thể live dù edge có thật)
  ⏳ Nếu tích hợp: sleeve RIÊNG vốn riêng ≤5% NAV + quant-skeptic + user sign-off
  ↳ charter đầy đủ: `mike/kb/paper_programs_charter/orb_intraday.md`
📌 Charter vừa cập nhật hôm nay (mục đích/tiêu chí đổi trong registry) — `mike/kb/paper_programs_charter/orb_intraday.md`
🔍 Nguồn: `data/orb_pt_status.json` · `data/orb_pt_log.csv (orb_pt.py, papertrade_daily.sh 15:30 ICT)`

── **7) Capitulation-sleeve shadow (DT5G × 8L washout)** · 👤 Taylor · ✅ GREEN
📈 asof 2026-07-29 | mode DEPLOYED | NAV 48.53B | tier NONCRISIS size=0.75 | entry 2026-07-20 | basket 5 mã · 📅 phiên ~38 từ 2026-06-10 · ⏱ nghiệm thu: EVENT-DRIVEN: sau sự kiện washout THẬT đầu tiên (chưa có deadline lịch)
💱 Giao dịch hôm nay: **Không có giao dịch** — mode DEPLOYED · 5 mã · HOLDING 7/60td · 5 names · MTM x0.971 · nguồn `data/pt_capitulation_logs.csv` ⚠️ **chưa có dòng cho 2026-07-31** — số dưới đây là phiên gần nhất (2026-07-29), KHÔNG phải hôm nay
📊 Gate (bản đầy đủ, lần đầu ghi nhận):
  ⏳ Sự kiện washout đầu tiên được xử lý đúng point-in-time (basket freeze tại signal date, entry price log đủ)
  ⏳ Fwd NAV sleeve qua trọn chu kỳ deploy→60 phiên→cash beat cash (kỳ vọng nghiên cứu: fwd60 +7%/81% winrate vùng WASHED-OUT)
  ⏳ Audit độc lập sau event trước khi cân nhắc wire overlay live
  ↳ charter đầy đủ: `mike/kb/paper_programs_charter/capitulation_shadow.md`
📌 Charter vừa cập nhật hôm nay (mục đích/tiêu chí đổi trong registry) — `mike/kb/paper_programs_charter/capitulation_shadow.md`
🔍 Nguồn: `data/pt_capitulation_state.json` · `data/pt_capitulation_logs.csv + baskets.csv (pt_capitulation_shadow.py, papertrade_daily.sh)`

── **8) Engine-room OOS panel (V11/V12/V4 vs V2.3-book vs VNINDEX)** · 👤 Taylor · ✅ GREEN
📈 V2.3-book -5.28% vs VNINDEX -5.22% (cửa sổ chung, NAV rebase 50B) · 📅 phiên ~37 từ 2026-06-11 · ⏱ nghiệm thu: 2026-12-01 (~6 tháng OOS trên cửa sổ chung từ 2026-06-11)
💱 Giao dịch hôm nay: **n/a theo thiết kế** — panel so sánh NAV của 5 sổ MÔ PHỎNG (V11/V12/V4/V23/VNI_BH) — panel không giữ nhật ký lệnh tách bạch; giao dịch THẬT của sổ production V2.3 nằm ở báo cáo EOD live, không phải ở đây
📊 Gate (bản đầy đủ, lần đầu ghi nhận):
  ⏳ V2.3-book không bị hệ đã loại dominate risk-adjusted qua 6 tháng OOS chung (so trên CỬA SỔ CHUNG — NAV thô khác inception là apples-oranges)
  ⏳ pt_v22 artifacts fresh mỗi phiên (PRODUCTION DEPENDENCY — plan live scale từ sổ này; stale = sự cố ops, đã có tiền lệ 2026-07-07)
  ↳ charter đầy đủ: `mike/kb/paper_programs_charter/engine_room_oos.md`
📌 Charter vừa cập nhật hôm nay (mục đích/tiêu chí đổi trong registry) — `mike/kb/paper_programs_charter/engine_room_oos.md`
Cửa sổ so sánh CHUNG 2026-06-11 → 2026-07-29 (35 phiên), NAV rebase 50B tại đầu cửa sổ (không phải NAV thô từ inception gốc):
  V11       -4.79%  (NAV 47.61B)
  V12       -2.51%  (NAV 48.75B)
  V4_DT5G   -2.78%  (NAV 48.61B)
  V23       -5.28%  (NAV 47.36B)
  VNI_BH    -5.22%  (NAV 47.39B)
🔍 Nguồn: `data/papertrade_compare5.csv (papertrade_compare.py)` · `data/pt_v22_dt5g_*.csv (V2.3-book = production signal), data/pt_v4_dt5g_logs.csv, data/pt_v11_tq34b_logs.csv, data/pt_v12_macro_logs.csv`

───
📎 *Badge: 🔴 RED = probe lỗi / cảnh báo chưa được giải thích / có gate FAIL · ⏳ WATCH = có cảnh báo đã giải thích hoặc thiếu khai báo giao dịch · ✅ GREEN = còn lại. Mục đích + phương pháp + tiêu chí nghiệm thu đầy đủ: `mike/kb/paper_programs_charter/<id>.md` (tự sinh từ registry). Gate chỉ in đầy đủ khi có thay đổi — trạng thái so sánh lưu ở `data/paper_report_state.json`.*
⚠️ *PAPER TRADING — không phải tiền thật; toàn bộ số liệu là mô phỏng/quan sát, không phải khuyến nghị đầu tư. Số không trace được về file nguồn = n/a.*
