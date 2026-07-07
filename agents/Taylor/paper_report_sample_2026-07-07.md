📋 **Paper Programs Daily Report — 2026-07-07**
Data as-of: 2026-07-07 14:07 ICT | registry: `mike/kb/paper_programs_registry.json` v1 (6 chương trình)

── **1) DC-book NEUTRAL idle-cash Waterfall** — owner: Taylor
🎯 Khi NEUTRAL và BAL/LAG rỗng, giải ngân tiền rảnh theo thứ tự BAL/LAG → DC book (double-confirm, ex-DHG) → custom30V có thắng để-nguyên-custom30V không? (backtest +5.0pp sleeve, DSR 0.775 = insurance-grade, chưa phải alpha tin cậy cao)
📅 Tiến độ: phiên ~2 từ 2026-07-06 — mốc review: Event-anchored: chu kỳ reverse-unwind ĐẦU TIÊN hoàn tất (LAG dự kiến refill cuối 07) + settle 4-6 tuần. Sàn ~2 tháng, trần 2026-10-06 (né mùa BCTC Q3). LAG refill trượt lịch → mốc trượt theo.
### 🪜 DC-book NEUTRAL Waterfall — Paper Sleeve
*Ưu tiên tiền rảnh NEUTRAL: BAL/LAG → DC book (double-confirm, ex-DHG) → custom30V | flag `dc_book_waterfall_enabled`=ON (chỉ paper `main`) | as-of 2026-07-06*

- Trạng thái hôm nay: NEUTRAL, **BAL/LAG rỗng** → waterfall DEPLOY
- DC book (8): ACB, CTR, FPT, HAH, MBB, PVT, SSI, TCB @ 12.5%/tên | custom30V 0.0% | cash 0.0%
- **P&L sleeve tích luỹ: -0.04%** (NAV 1.000B / cơ sở 1.000B, 2 phiên) | ret hôm nay -0.045% (sau TC 0.000%)
*PAPER — theo dõi/kiểm định, không phải lệnh thật. State: data/dc_book_waterfall_paper_state.json*
Gate GO/NO-GO:
  ⏳ Trọn 1 chu kỳ deploy → reverse-unwind → settle trên paper, đúng thứ tự ưu tiên thiết kế
  ⏳ P&L sleeve NET-of-TC không mâu thuẫn backtest (+5.0pp/năm sleeve parking kỳ vọng)
  ⏳ User sign-off sau review event-anchored (Mike + Taylor đề xuất ngày khi đủ điều kiện)
ℹ️ Sleeve clock chạy từ 2026-06-26 (backfill NAV cơ sở 1B); user duyệt paper 2026-07-06 (job Taylor_20260706_132553).
🔍 Nguồn: `data/dc_book_waterfall_paper_state.json` · `data/dc_book_waterfall_paper_nav.csv`

── **2) EXTREME-regime gate** — owner: Taylor
🎯 Gate phòng thủ intraday (arm 2-poll, sell-to-floor, buy-pause, cadence ×0.25) có ZERO false-trigger trong thị trường benign không? (stress-injection đã PASS 24/24)
📅 Tiến độ: phiên ~5/20 (từ 2026-07-01 → 2026-07-28, lịch T2-T6 ước tính) — ~2026-07-28 (~20 phiên benign)
- Phiên executor đã chạy trên account `main`: **0** (không có file khớp `exec_main_*_journal.csv`)
- → chưa tích lũy được evidence nào; flag bật nhưng chỉ có tác dụng khi executor thực sự chạy phiên trên account này
Gate GO/NO-GO:
  ✅ Stress-injection 24/24 PASS (arm 2-poll · sell-to-floor · buy-pause · cadence ×0.25 + negative controls) — stress_extreme_regime.py, week-1
  ⏳ ZERO false-trigger qua ~4 tuần benign trên account paper main
  ⏳ Không can thiệp NORMAL-path
  ⏳ User sign-off trước khi bật live
ℹ️ Evidence tích lũy CHỈ khi executor chạy phiên trên account main — 0 phiên = 0 evidence, không tính là PASS.
🔍 Nguồn: `data/execution_logs/exec_main_*_journal.csv` · `secrets/trading_bot_accounts.json (extreme_regime_enabled=true, chỉ paper main)` · `stress_extreme_regime.py`

── **3) Vol-scale buy chase-cap (patch#3)** — owner: Taylor
🎯 Nới trần đuổi mua theo realised vol 20d (clamp(k·rvol, static, ceil), k=2.0/ceil=0.04, monotone-safe, fail-safe về static) có wiring đúng trên quote thật không? (executor-path stress đã PASS 15/15)
📅 Tiến độ: phiên ~5/10 (từ 2026-07-01 → 2026-07-14, lịch T2-T6 ước tính) — ~2026-07-14 (~10 phiên — fire trên gap-up thường, tích event nhanh)
- Phiên executor đã chạy trên account `main`: **0** (không có file khớp `exec_main_*_journal.csv`)
- → chưa tích lũy được evidence nào; flag bật nhưng chỉ có tác dụng khi executor thực sự chạy phiên trên account này
Gate GO/NO-GO:
  ✅ Executor-path stress 15/15 PASS (wiring · WIDEN clamp-to-ceil · MONOTONE · fail-safe rvol absent/0/<0 · NEG-control) — stress_vol_scale_chase_cap.py
  ⏳ Paper sạch: wiring đúng trên quote thật + fail-safe khi thiếu rvol cache
  ⏳ Không can thiệp NORMAL-path ngày non-gap
  ⏳ Skeptic rerun REAL-fill vs min(open,L) proxy trên correlated gap-up @NAV target
  ⏳ User sign-off trước khi bật live
ℹ️ Cap-widen KHÔNG có marker riêng trong journal (áp silent trong _buy_chase_pct) — đo qua stress script + so limit price ngày gap-up; cần phiên executor paper + ngày gap mới có evidence tự động.
🔍 Nguồn: `data/execution_logs/exec_main_*_journal.csv` · `secrets/trading_bot_accounts.json (chase_cap_vol_scale_enabled=true, chỉ paper main)` · `stress_vol_scale_chase_cap.py`

── **4) Fill-timing window (BUY 10:45-11:15 / SELL 09:15-09:45)** — owner: Taylor
🎯 Edge backtest (BUY 11:15 rẻ hơn open +17.6bps t=12.0; SELL tại open +11.8bps vs ATC) có capture được NET-of-noise trên fill thật không? (noise 110-220bps >> edge 17bps → cần nhiều tuần)
📅 Tiến độ: phiên ~5/23 (từ 2026-07-01 → 2026-07-31, lịch T2-T6 ước tính) — Checkpoint ~cuối tháng 7 (cần ~3-4 tuần fill tích lũy)
=== EXECUTION-QUALITY REVIEW (since 2026-06-26) ===

--- A. WINDOW ADHERENCE (mechanics: did orders release in the right time-of-day?) ---
   journal ft-notes: 396 placements | in-window 97% | out-of-window 3%

--- B. ERRORS / REJECTS (must be 0 or explained) ---
   rejected/failed orders: 0
   journal FAIL/ERROR events: 6938

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
📅 Tiến độ: phiên ~5/66 (từ 2026-07-01 → 2026-09-30, lịch T2-T6 ước tính) — 2026-09-30 (audit: Taylor)
- MTM as-of **2026-07-06** (BQ cache, close phiên gần nhất đã sync):
  • FPT: 70,200 → 73,000 = **+3.99%** (entry 2026-07-01, PE vs PE_MA1Y)
  • ACB: 22,650 → 22,200 = **-1.99%** (entry 2026-07-01, P/B vs Gordon justified-PB)
  • MBB: 25,200 → 25,300 = **+0.40%** (entry 2026-07-01, P/B vs Gordon justified-PB)
  • HDB: 25,850 → 27,200 = **+5.22%** (entry 2026-07-01, P/B vs Gordon justified-PB)
- Portfolio EW: **+1.91%** | VNINDEX 1,860.01 → 1,843.50 = -0.89% | **Excess +2.79pp**
- Hôm nay: không có giao dịch (buy-and-hold, quan sát đến 2026-09-30)
Gate GO/NO-GO:
  ⏳ Excess return dương vs VNINDEX qua full window 3 tháng
  ⏳ Exit conditions per-name không bị vi phạm sớm (PE > PE_MA1Y / PB > justPB)
  ⏳ Audit độc lập bởi Taylor tại 2026-09-30
ℹ️ Giá MTM từ BQ cache (close phiên gần nhất đã sync) — trong phiên sẽ trễ 1 ngày, đúng thiết kế EOD.
🔍 Nguồn: `data/alphalens_paper.json` · `data/bq_cache/ticker_1m.parquet (Close + VNINDEX, sync 23:45 ICT)`

── **6) A/B cross-mode (ab_cross vs ab_dip)** — owner: Taylor
🎯 So sánh 2 chế độ đặt lệnh (cross ngay vs chờ dip) trên cùng plan — chế độ nào cho fill price tốt hơn NET?
📅 Tiến độ: chưa bắt đầu / chưa xác định ngày start — Chưa chốt — cần account ab_cross/ab_dip chạy phiên trước đã
❌ chưa có /home/trido/thanhdt/WorkingClaude/data/bot_paper_ab_cross.json — account ab_cross chưa chạy phiên nào
⚠️ lệnh exit=1 — output ở trên có thể không đầy đủ
Gate GO/NO-GO:
  ⏳ Cả 2 account A/B có phiên chạy song song đủ mẫu
  ⏳ Khác biệt fill price có ý nghĩa thống kê trước khi kết luận
ℹ️ Tính đến 2026-07-07 account ab_cross chưa chạy phiên nào — report sẽ nói thẳng điều đó.
🔍 Nguồn: `bot_ab_report.py` · `data/bot_paper_ab_cross.json` · `data/bot_paper_ab_dip.json`

⚠️ *PAPER TRADING — không phải tiền thật; toàn bộ số liệu là mô phỏng/quan sát, không phải khuyến nghị đầu tư. Số không trace được về file nguồn = n/a.*
