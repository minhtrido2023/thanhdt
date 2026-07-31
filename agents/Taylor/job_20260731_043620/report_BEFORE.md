📋 **Paper Programs Daily Report — 2026-07-31**
Render lúc: 2026-07-31 11:37 ICT — *vintage dữ liệu xem `asof` từng mục* | registry: `mike/kb/paper_programs_registry.json` v2 (8 chương trình)

── **1) DC-book NEUTRAL idle-cash Waterfall** — owner: Taylor
🎯 Khi NEUTRAL và BAL/LAG rỗng, giải ngân tiền rảnh theo thứ tự BAL/LAG → DC book (double-confirm, ex-DHG) → custom30V có thắng để-nguyên-custom30V không? (backtest +5.0pp sleeve, DSR 0.775 = insurance-grade, chưa phải alpha tin cậy cao)
📅 Tiến độ: phiên ~20 từ 2026-07-06 — mốc review: Event-anchored: chu kỳ reverse-unwind ĐẦU TIÊN hoàn tất (LAG dự kiến refill cuối 07) + settle 4-6 tuần. Sàn ~2 tháng, trần 2026-10-06 (né mùa BCTC Q3). LAG refill trượt lịch → mốc trượt theo.
### 🪜 DC-book NEUTRAL Waterfall — Paper Sleeve (v2)
*Tiền rảnh NEUTRAL: BAL/LAG → DC book (double-confirm, liq≥3B) → custom30V, **continuous-residual** | cap gộp 0.15/tên · rebal q2m5 | flag `dc_book_waterfall_enabled`=ON (chỉ paper `main`) | as-of 2026-07-30 00:00:00*

- Trạng thái hôm nay: NEUTRAL → waterfall chạy LIÊN TỤC trên phần tiền dư (BAL/LAG có deal hôm nay — v2 KHÔNG tắt sleeve, chỉ phần dư nhỏ lại)
- Nhịp rebal: giữ nguyên, trọng số drift (q2m5 — chưa tới kỳ)
- DC book (8): ACB, CTR, FPT, HAH, MBB, PVT, SSI, TCB @ 0.0%/tên (leg 0.0%) | custom30V 0.0% | cash 0.0%
- DCF check (informational, không tham gia chọn mã): ACB NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 Gordon P/B (ngân hàng): P/B 1.31 vs hợp lý 2.25 (ROE5Y 23.0%, COE 13%/g 5%) — CHEAP [đã validate (bank_compounder_screen)] · CTR 🔴 RICH (giá trị hợp lý ~68,943đ vs giá 71,000đ, MoS -3.0%, không robust) · FPT 🟢 CHEAP (giá trị hợp lý ~79,333đ vs giá 67,000đ, MoS +15.6%, robust) · HAH NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 🟢 EV/EBITDA (cảng/hạ tầng): EV/EBITDA 3.8x (cheap <8x, benchmark mature 4-8x) — CHEAP [framework (n nhỏ — cần margin/ROIC xác nhận kèm)] · MBB NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 Gordon P/B (ngân hàng): P/B 1.21 vs hợp lý 2.21 (ROE5Y 22.7%, COE 13%/g 5%) — CHEAP [đã validate (bank_compounder_screen)] · PVT NOT_COMPUTED (fcfe_negative_buildout) → thay th
… (cắt bớt, xem nguồn để đủ; exit=0)
Gate GO/NO-GO:
  ⏳ Trọn 1 chu kỳ deploy → reverse-unwind → settle trên paper, đúng thứ tự ưu tiên thiết kế
  ⏳ P&L sleeve NET-of-TC không mâu thuẫn backtest (+5.0pp/năm sleeve parking kỳ vọng)
  ⏳ User sign-off sau review event-anchored (Mike + Taylor đề xuất ngày khi đủ điều kiện)
ℹ️ Sleeve clock chạy từ 2026-06-26 (backfill NAV cơ sở 1B); user duyệt paper 2026-07-06 (job Taylor_20260706_132553).
🔍 Nguồn: `data/dc_book_waterfall_paper_state.json` · `data/dc_book_waterfall_paper_nav.csv`

── **2) EXTREME-regime gate** — owner: Taylor
🎯 Gate phòng thủ intraday (arm 2-poll, sell-to-floor, buy-pause, cadence ×0.25) có ZERO false-trigger trong thị trường benign không? (stress-injection đã PASS 24/24)
📅 Tiến độ: **14/20 phiên evidence** (đếm phiên executor thật có journal trên `main`, từ 2026-07-07, gần nhất 2026-07-31) — 20 phiên EVIDENCE (executor chạy thật trên paper main) từ phiên thật đầu tiên 2026-07-07 → ước ~2026-08-03. Mốc cũ 2026-07-28 bỏ — 07-01→07-06 flag bật nhưng 0 phiên executor = 0 evidence, không đếm.
- Phiên executor account `main`: **17** file journal (gần nhất: exec_main_2026-07-31_journal.csv)
- Marker hits: hôm nay **0**, lũy kế **0** (EXTREME_PAUSE=0, EXTREME_SELL=0, EXTREME_DOWN=0, EXTREME_UP=0)
Gate GO/NO-GO:
  ✅ Stress-injection 24/24 PASS (arm 2-poll · sell-to-floor · buy-pause · cadence ×0.25 + negative controls) — stress_extreme_regime.py, week-1
  ⏳ ZERO false-trigger qua ~4 tuần benign trên account paper main
  ⏳ Không can thiệp NORMAL-path
  ⏳ User sign-off trước khi bật live
ℹ️ Evidence tích lũy CHỈ khi executor chạy phiên trên account main — 0 phiên = 0 evidence, không tính là PASS. Từ 2026-07-07: probe harness chạy paper main mỗi ngày T2-T6 (cron 08:52 sinh plan mike/bin/paper_main_probe_plan.py, executor 09:10 + 13:05, log mike/logs/run_bot_main_*.log).
🔍 Nguồn: `data/execution_logs/exec_main_*_journal.csv` · `secrets/trading_bot_accounts.json (extreme_regime_enabled=true, chỉ paper main)` · `stress_extreme_regime.py`

── **3) Vol-scale buy chase-cap (patch#3)** — owner: Taylor
🎯 Nới trần đuổi mua theo realised vol 20d (clamp(k·rvol, static, ceil), k=2.0/ceil=0.04, monotone-safe, fail-safe về static) có wiring đúng trên quote thật không? (executor-path stress đã PASS 15/15)
📅 Tiến độ: **14/10 phiên evidence** (đếm phiên executor thật có journal trên `main`, từ 2026-07-07, gần nhất 2026-07-31) — 10 phiên EVIDENCE (executor chạy thật trên paper main) từ phiên thật đầu tiên 2026-07-07 → ước ~2026-07-20. Mốc cũ 2026-07-14 bỏ — 07-01→07-06 flag bật nhưng 0 phiên executor = 0 evidence, không đếm.
- Phiên executor account `main`: **17** file journal (gần nhất: exec_main_2026-07-31_journal.csv)
Gate GO/NO-GO:
  ✅ Executor-path stress 15/15 PASS (wiring · WIDEN clamp-to-ceil · MONOTONE · fail-safe rvol absent/0/<0 · NEG-control) — stress_vol_scale_chase_cap.py
  ⏳ Paper sạch: wiring đúng trên quote thật + fail-safe khi thiếu rvol cache
  ⏳ Không can thiệp NORMAL-path ngày non-gap
  ⏳ Skeptic rerun REAL-fill vs min(open,L) proxy trên correlated gap-up @NAV target
  ⏳ User sign-off trước khi bật live
ℹ️ Cap-widen KHÔNG có marker riêng trong journal (áp silent trong _buy_chase_pct) — đo qua stress script + so limit price ngày gap-up; cần phiên executor paper + ngày gap mới có evidence tự động. Từ 2026-07-07: probe harness chạy paper main mỗi ngày (6 BUY/phiên trên quote thật — xem entry extreme_regime cho cron).
🔍 Nguồn: `data/execution_logs/exec_main_*_journal.csv` · `secrets/trading_bot_accounts.json (chase_cap_vol_scale_enabled=true, chỉ paper main)` · `stress_vol_scale_chase_cap.py`

── **4) Fill-timing window (BUY 10:45-11:15 / SELL 09:15-09:45)** — owner: Taylor
🎯 Edge backtest (BUY 11:15 rẻ hơn open +17.6bps t=12.0; SELL tại open +11.8bps vs ATC) có capture được NET-of-noise trên fill thật không? (noise 110-220bps >> edge 17bps → cần nhiều tuần)
📅 Tiến độ: phiên ~23/23 (từ 2026-07-01 → 2026-07-31, lịch T2-T6 ước tính) — Checkpoint ~cuối tháng 7 (cần ~3-4 tuần fill tích lũy)
⚠️ **CẦN CHÚ Ý** — journal FAIL/ERROR events: 431
=== EXECUTION-QUALITY REVIEW (since 2026-06-26) ===

--- A. WINDOW ADHERENCE (mechanics: did orders release in the right time-of-day?) ---
   journal ft-notes: 154 placements | in-window 54% | out-of-window 46%

--- B. ERRORS / REJECTS (must be 0 or explained) ---
   journal FAIL/ERROR events: 431

--- C. DIRECTIONAL FILL SANITY (needs day-open; bps EDGE itself needs weeks, not gated here) ---
   no completed fills yet

=== GO/NO-GO CHECKLIST (30-06) ===
  [ ] BUY window adherence high (orders concentrating 10:45-11:15)
  [ ] SELL window adherence high (orders at open 09:15-09:45)
  [ ] 0 rejects/fails (or each explained)
  [ ] BUY fill not materially > open; SELL not materially < open
  -> if mechanics clean: flip fill_timing_live_gate=false. EDGE (+5-17bps) validates over weeks.
Gate GO/NO-GO:
  ⏳ BUY window adherence cao (lệnh dồn 10:45-11:15)
  ⏳ SELL window adherence cao (lệnh tại open 09:15-09:45)
  ⏳ 0 rejects/fails (hoặc từng cái được giải thích)
  ⏳ BUY fill không tệ hơn open đáng kể; SELL không thấp hơn open đáng kể
  ⏳ quant-skeptic → user sign-off mới flip fill_timing_live_gate
ℹ️ Mechanics (window adherence) đo được sớm; EDGE bps cần nhiều tuần — không gate sớm trên bps.
🔍 Nguồn: `execution_quality_review.py` · `data/execution_logs/exec_*_journal.csv (ft-notes)`

── **5) AlphaLens Paper (FPT/ACB/MBB/HDB vs VNINDEX)** — owner: DollarBill
🎯 4 tên Tier-1 chọn bằng lens định giá (PE vs PE_MA1Y; PB vs Gordon justified-PB) có beat VNINDEX qua 3 tháng không? Buy-and-hold, equal-weight 25%/tên.
📅 Tiến độ: phiên ~23/66 (từ 2026-07-01 → 2026-09-30, lịch T2-T6 ước tính) — 2026-09-30 (audit: Taylor)
- MTM as-of **2026-07-30** (BQ cache, close phiên gần nhất đã sync):
  • FPT: 70,200 → 67,000 = **-4.56%** (entry 2026-07-01, PE vs PE_MA1Y)
  • ACB: 22,650 → 22,350 = **-1.32%** (entry 2026-07-01, P/B vs Gordon justified-PB)
  • MBB: 25,200 → 22,500 = **-10.71%** (entry 2026-07-01, P/B vs Gordon justified-PB)
  • HDB: 25,850 → 25,700 = **-0.58%** (entry 2026-07-01, P/B vs Gordon justified-PB)
- Portfolio EW: **-4.29%** | VNINDEX 1,860.01 → 1,744.66 = -6.20% | **Excess +1.91pp**
- Hôm nay: không có giao dịch (buy-and-hold, quan sát đến 2026-09-30)
Gate GO/NO-GO:
  ⏳ Excess return dương vs VNINDEX qua full window 3 tháng
  ⏳ Exit conditions per-name không bị vi phạm sớm (PE > PE_MA1Y / PB > justPB)
  ⏳ Audit độc lập bởi Taylor tại 2026-09-30
ℹ️ Giá MTM từ BQ cache (close phiên gần nhất đã sync) — trong phiên sẽ trễ 1 ngày, đúng thiết kế EOD.
🔍 Nguồn: `data/alphalens_paper.json` · `data/bq_cache/ticker_1m.parquet (Close + VNINDEX, sync 23:45 ICT)`

── **6) ORB intraday VN30F (ring-fenced)** — owner: Taylor
🎯 Chiến lược opening-range-breakout VN30F (sign OR 09:00-09:30 → giữ tới 14:30, no stop) có sống sót qua regime BẤT LỢI không? Verdict quant-skeptic 2026-07-01: NO-integrate — n≈17-21 phiên toàn NEUTRAL uptrend benign, Sharpe cao là artifact mẫu nhỏ; walk-forward 2024 lỗ cả năm chưa được giải quyết. Paper tích lũy tiếp để có bằng chứng đủ mạnh.
📅 Tiến độ: phiên ~39 từ 2026-06-09 — mốc review: ≥60 phiên GỒM ít nhất một giai đoạn chop/bear → re-eval quant-skeptic. Không có deadline lịch — điều kiện là REGIME, không phải số ngày.
asof 2026-07-30 | 38 phiên từ 2026-06-09 | NAV 1.063B (+6.32%) | WR 57.9% | phiên cuối +2.19% (sig +1) | Sharpe report 2.82 (mẫu nhỏ — đọc thận trọng)
Gate GO/NO-GO:
  ⏳ ≥60 phiên paper GỒM giai đoạn chop/bear (hiện toàn benign uptrend — chưa đủ điều kiện đánh giá)
  ⏳ Walk-forward 2024 full-year loss được giải thích/không lặp lại trong forward window
  ⏳ Hạ tầng phái sinh: tài khoản VSD margin + đường thực thi VN30F (bot hiện CASH-EQUITY ONLY — chưa thể live dù edge có thật)
  ⏳ Nếu tích hợp: sleeve RIÊNG vốn riêng ≤5% NAV + quant-skeptic + user sign-off
ℹ️ Section ORB trong Telegram 18:00 (telegram_recommend.py) đã GỠ 2026-07-07 để hết trùng — report này là kênh duy nhất. Verdict đầy đủ: bus event Taylor 2026-07-01 (job Taylor_20260701_113638).
🔍 Nguồn: `data/orb_pt_status.json` · `data/orb_pt_log.csv (orb_pt.py, papertrade_daily.sh 15:30 ICT)`

── **7) Capitulation-sleeve shadow (DT5G × 8L washout)** — owner: Taylor
🎯 Sleeve dự trữ 50B nằm CASH, deploy vào rổ 8L quality+golden khi có tín hiệu washout (rule v2 2026-06-10, crisis_playbook.md §0b/§1), giữ 60 phiên rồi về cash — forward NAV là bằng chứng OOS cho overlay khi có khủng hoảng thật. Point-in-time: basket FREEZE tại ngày signal, không hindsight.
📅 Tiến độ: phiên ~38 từ 2026-06-10 — mốc review: EVENT-DRIVEN — đánh giá sau sự kiện washout THẬT đầu tiên (đến nay chưa có: mode CASH liên tục). Không có deadline lịch; sleeve rẻ, chạy chờ event.
asof 2026-07-29 | mode DEPLOYED | NAV 48.53B | tier NONCRISIS size=0.75 | entry 2026-07-20 | basket 5 mã
Gate GO/NO-GO:
  ⏳ Sự kiện washout đầu tiên được xử lý đúng point-in-time (basket freeze tại signal date, entry price log đủ)
  ⏳ Fwd NAV sleeve qua trọn chu kỳ deploy→60 phiên→cash beat cash (kỳ vọng nghiên cứu: fwd60 +7%/81% winrate vùng WASHED-OUT)
  ⏳ Audit độc lập sau event trước khi cân nhắc wire overlay live
ℹ️ crisis_alert_push.py (cùng pipeline 15:30) là CÒI Telegram của cùng signal — chỉ kêu khi WATCH/STRONG, im lặng ngày thường → là alert vận hành, KHÔNG phải report trùng, giữ nguyên. VINTAGE: pt_capitulation_shadow.py query BQ LIVE (ticker_prune + dt5g_live), mà BQ chưa có close phiên T lúc 15:30 → last_date LUÔN = T-1. Đây là SÀN CẤU TRÚC, không phải stale: muốn asof=T phải chờ ingest ~17:30 / sync 23:45, tức dời report sang tối hoặc sáng hôm sau.
🔍 Nguồn: `data/pt_capitulation_state.json` · `data/pt_capitulation_logs.csv + baskets.csv (pt_capitulation_shadow.py, papertrade_daily.sh)`

── **8) Engine-room OOS panel (V11/V12/V4 vs V2.3-book vs VNINDEX)** — owner: Taylor
🎯 V2.3-book (NGUỒN TÍN HIỆU của live V2.4 — trading_bot/strategies.py đọc pt_v22_dt5g_open_positions.csv để build plan thật) có tiếp tục thắng các kiến trúc BỊ LOẠI (V11 Song Sinh, V12 Âm Dương, V4 switched-allocator) trên OOS forward không? = validation liên tục của lựa chọn V2.4. Nếu một hệ bị loại dominate BỀN risk-adjusted → mở lại câu hỏi rotation (qua quant-skeptic + DSR/PBO, không tự wire).
📅 Tiến độ: phiên ~37 từ 2026-06-11 — mốc review: Review 2026-12-01 (~6 tháng OOS trên cửa sổ chung từ 2026-06-11) — Taylor trình bảng + khuyến nghị giữ panel / thu gọn / mở câu hỏi rotation.
Cửa sổ so sánh CHUNG 2026-06-11 → 2026-07-29 (35 phiên), NAV rebase 50B tại đầu cửa sổ (không phải NAV thô từ inception gốc):
  V11       -4.79%  (NAV 47.61B)
  V12       -2.51%  (NAV 48.75B)
  V4_DT5G   -2.78%  (NAV 48.61B)
  V23       -5.28%  (NAV 47.36B)
  VNI_BH    -5.22%  (NAV 47.39B)
Gate GO/NO-GO:
  ⏳ V2.3-book không bị hệ đã loại dominate risk-adjusted qua 6 tháng OOS chung (so trên CỬA SỔ CHUNG — NAV thô khác inception là apples-oranges)
  ⏳ pt_v22 artifacts fresh mỗi phiên (PRODUCTION DEPENDENCY — plan live scale từ sổ này; stale = sự cố ops, đã có tiền lệ 2026-07-07)
ℹ️ pt_v22_dt5g KHÔNG PHẢI paper thí nghiệm — là sổ tín hiệu production, KHÔNG BAO GIỜ retire khi V2.4 còn live. V11/V12/V4 giữ chạy làm control arms (chi phí ~0, không gửi kênh nào). Inception khác nhau (V11/V12 cũ hơn, V4 06-01, V23 06-11) — probe tự rebase về cửa sổ chung. VINTAGE: các sim sinh papertrade_compare5.csv chạy trên giá đến T-1 lúc 15:30 → dòng cuối cửa sổ LUÔN = T-1 (sàn cấu trúc như capitulation_shadow, không phải stale).
🔍 Nguồn: `data/papertrade_compare5.csv (papertrade_compare.py)` · `data/pt_v22_dt5g_*.csv (V2.3-book = production signal), data/pt_v4_dt5g_logs.csv, data/pt_v11_tq34b_logs.csv, data/pt_v12_macro_logs.csv`

⚠️ *PAPER TRADING — không phải tiền thật; toàn bộ số liệu là mô phỏng/quan sát, không phải khuyến nghị đầu tư. Số không trace được về file nguồn = n/a.*
