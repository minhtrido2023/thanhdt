📋 **Paper Programs Daily Report — 2026-08-11**
Render 18:36 ICT · registry v3 · 7 paper-trial đang theo dõi · *vintage dữ liệu xem `asof`/nguồn từng mục (BQ chưa có close phiên T lúc 16:00)*
ℹ️ **Đã chuyển khỏi báo cáo ngày**: Vol-scale buy chase-cap (patch#3). Dữ liệu/cron không bị xóa; xem registry để biết lý do và mốc review.
⏳ **Theo dõi** (2): #1 DC-book NEUTRAL idle-cash Waterfall · #3 Fill-timing window (BUY 10:45-11:15 / SELL 09:15-09:45)

**TỔNG QUAN** — trạng thái · paper-trial · chỉ số mới nhất · giao dịch hôm nay:
⏳ **1) DC-book NEUTRAL idle-cash Waterfall** — NAV 1,036,779,362đ · lũy kế +3.68% · phiên gần nhất +2.49% (as-of 2026-08-10) | 💱 **n/a — `data/dc_book_waterfall_paper_nav.csv` CHƯA có dòng cho phiên…
✅ **2) EXTREME-regime gate** — 23 phiên journal `main` (gần nhất 2026-08-11) · marker hôm nay **0** / lũy kế **0** | 💱 **6 lệnh khớp** — SELL FPT 100@72,200 · SELL VNM 100@62,700 · BUY ACB…
⏳ **3) Fill-timing window (BUY 10:45-11:15 / SELL 09:15-09:45)** — ft-notes 185 placements | in-window 49% | out-of-window 51% | 💱 **6 lệnh khớp** — SELL FPT 100@72,200 · SELL VNM 100@62,700 · BUY ACB…
✅ **4) Capitulation-sleeve shadow (DT5G × 8L washout)** — asof 2026-08-10 | mode DEPLOYED | NAV 51.02B | tier NONCRISIS size=0.75 | entry 2026-07-20 | b… | 💱 **Không có giao dịch** — mode DEPLOYED · 5 mã · HOLDING 15/60td · 5 n…
✅ **5) AlphaLens Paper (FPT/ACB/MBB/HDB vs VNINDEX)** — EW **+0.69%** vs VNINDEX -4.48% → **excess +5.17pp** (MTM as-of 2026-08-10) | 💱 **Không có giao dịch** — buy-and-hold theo thiết kế (equal-weight 25%…
✅ **6) ORB intraday VN30F (ring-fenced)** — asof 2026-08-11 | 46 phiên từ 2026-06-09 | NAV 1.076B (+7.64%) | WR 58.7% | phiên cuối +0.16%… | 💱 **CÓ giao dịch** — sig -1 · vào 1,925.5 → ra 1,922.2 · net +0.16% (1…
✅ **7) Engine-room OOS panel (V11/V12/V4 vs V2.3-book vs VNINDEX)** — V2.3-book -0.55% vs VNINDEX -1.21% (cửa sổ chung, NAV rebase 50B) | 💱 **n/a theo thiết kế** — panel so sánh NAV của 5 sổ MÔ PHỎNG (V11/V12/…

── **1) DC-book NEUTRAL idle-cash Waterfall** · 👤 Taylor · ⏳ WATCH
📈 NAV 1,036,779,362đ · lũy kế +3.68% · phiên gần nhất +2.49% (as-of 2026-08-10) · 📅 phiên ~27 từ 2026-07-06 · ⏱ nghiệm thu: event-anchored: chu kỳ reverse-unwind ĐẦU TIÊN + settle 4-6 tuần · trần 2026-10-06
💱 Giao dịch hôm nay: **n/a — `data/dc_book_waterfall_paper_nav.csv` CHƯA có dòng cho phiên 2026-08-11** (pipeline sinh dữ liệu chạy 15:05/15:30 ICT; nếu đã quá giờ đó ⇒ pipeline chưa chạy/lỗi) · dòng gần nhất 2026-08-10: turnover 0.00% · rebalanced=False · deployed=True · sleeve +2.49%
📊 Gate: **0/3 PASS** · không đổi từ 2026-07-31 · chi tiết: `mike/kb/paper_programs_charter/dc_waterfall.md`
### 🪜 DC-book NEUTRAL Waterfall — Paper Sleeve (v2)
*Tiền rảnh NEUTRAL: BAL/LAG → DC book (double-confirm, liq≥3B) → custom30V, **continuous-residual** | cap gộp 0.15/tên · rebal q2m5 | flag `dc_book_waterfall_enabled`=ON (chỉ paper `main`) | as-of 2026-08-10 00:00:00*

- Trạng thái hôm nay: NEUTRAL → waterfall chạy LIÊN TỤC trên phần tiền dư (BAL/LAG rỗng)
- Nhịp rebal: giữ nguyên, trọng số drift (q2m5 — chưa tới kỳ)
- DC book (7): ACB, FPT, HAH, MBB, PVT, SSI, TCB @ 0.0%/tên (leg 0.0%) | custom30V 0.0% | cash 0.0%
- Due-diligence (informational, không tham gia chọn mã):
  DD ACB [DC] (data 2026-08-10): thanh khoản OK (ADV3T 350.37 tỷ/phiên) · ⚠ universe_pit: n/a (không đọc được)
  FA: ROE5Y 23.0% · ROE_Min3Y 17.6% · FSCORE 1 · D/E 9.75 · PE 8.39
  DD FPT [DC] (data 2026-08-10): thanh khoản OK (ADV3T 488.93 tỷ/phiên) · ⚠ universe_pit: n/a (không đọc được)
  FA: ROE5Y 26.6% · ROE_Min3Y 28.1% · FSCORE 5 · D/E 0.80 · PE 12.31
  DD HAH [DC] (data 2026-08-10): thanh khoản OK (ADV3T 25.75 tỷ/phiên) · ⚠ universe_pit: n/a (không đọc được)
  FA: ROE5Y 24.6% · ROE_Min3Y 15.5% · FSCORE 4 · D/E
… (cắt bớt, xem nguồn để đủ; exit=0)
_(lược 3 dòng phụ lục của probe — xem nguồn nếu cần)_
🔍 Nguồn: `data/dc_book_waterfall_paper_state.json` (+1 nguồn, xem charter)

── **2) EXTREME-regime gate** · 👤 Taylor · ✅ GREEN
📈 23 phiên journal `main` (gần nhất 2026-08-11) · marker hôm nay **0** / lũy kế **0** · 📅 20/20 phiên evidence · ⏱ nghiệm thu: 2026-08-04 (job Taylor_20260804_124404): CHƯA đủ điều kiện chuyển bước — 15/20 phiên evidence (trigger ii chỉ 12/20 sạch do M5), 0 marker/15 phiên. Evidence chạy lại từ 08-05 (đã gỡ bug netting) → ước đủ ~08-11. Gate 1+3 PASS, gate 2 pending vì thiếu phiên, gate 4 chờ user. KHÔNG flip live. Case PNJ của user KHÔNG xác nhận được (PNJ chưa bao giờ trong rổ probe).
💱 Giao dịch hôm nay: **6 lệnh khớp** — SELL FPT 100@72,200 · SELL VNM 100@62,700 · BUY ACB 100@22,600 · BUY HDB 100@27,050 · BUY HPG 100@22,150 · BUY MBB 100@20,500 [đặt 6 · khớp 6 · lỗi 0] · nguồn `data/execution_logs/exec_main_2026-08-11_journal.csv`
📊 Gate: **2/4 PASS** · không đổi từ 2026-08-05 · chi tiết: `mike/kb/paper_programs_charter/extreme_regime.md`
- Marker: EXTREME_PAUSE=0, EXTREME_FLOOR_GUARD=0, EXTREME_DOWN sell-to-floor=0
🔍 Nguồn: `data/execution_logs/exec_main_*_journal.csv` (+2 nguồn, xem charter)

── **3) Fill-timing window (BUY 10:45-11:15 / SELL 09:15-09:45)** · 👤 Taylor · ⏳ WATCH
📈 ft-notes 185 placements | in-window 49% | out-of-window 51% · 📅 phiên ~30/23 (2026-07-01→2026-07-31) · ⏱ nghiệm thu: 4/4 gate cơ học ĐẠT (2026-08-11). Chờ: burn-in HYBRID ~4 phiên nữa (→08-25) → quant-skeptic → user sign-off mới flip fill_timing_live_gate
💱 Giao dịch hôm nay: **6 lệnh khớp** — SELL FPT 100@72,200 · SELL VNM 100@62,700 · BUY ACB 100@22,600 · BUY HDB 100@27,050 · BUY HPG 100@22,150 · BUY MBB 100@20,500 [đặt 6 · khớp 6 · lỗi 0] · nguồn `data/execution_logs/exec_main_2026-08-11_journal.csv`
⚠️ Cảnh báo: journal FAIL/ERROR events: 431 → ⏳ cần theo dõi: 431 sự kiện lỗi này TOÀN BỘ thuộc 1 ngày 2026-07-30 (sự cố A: PaperBroker.place_order thiếu tham số cash_only → mọi lệnh paper-main crash), đã fix + verify cùng ngày; 0 lỗi trong journal 2026-07-31. Đây là số LŨY KẾ từ 2026-06-26 nên còn hiện cho tới khi cửa sổ trượt qua. Chi tiết: mike/kb/incidents/2026-07/2026-07-30-paper-trading-report-3-root-causes.md
📊 Gate **ĐỔI hôm nay** — bản đầy đủ:
  ✅ BUY window adherence cao (lệnh dồn 10:45-11:15) — ĐO 2026-08-11 (job Taylor_20260811_091002) bằng TIMESTAMP thật, không bằng string-match nhãn: 5 phiên probe 10:46 có lệnh MUA (07-14/07-16/07-21/07-23/08-11), 28/28 lệnh đặt trong 10:45-11:15, 28/28 khớp. ĐẠT ngưỡng ≥5 phiên. ⚠️ 08-11 là phiên HYBRID ĐẦU TIÊN — 4 phiên kia là cơ chế gom-cửa-sổ CŨ. 🔔 (trước: pending)
  ✅ SELL window adherence cao (lệnh tại open 09:15-09:45) — ĐO 2026-08-11 bằng timestamp: 10 phiên probe 09:15 có lệnh BÁN (07-13→08-05), 50/50 lệnh trong 09:15-09:45, 50/50 khớp. Vượt xa ngưỡng ≥5. 🔔 (trước: pending)
  ✅ 0 rejects/fails (hoặc từng cái được giải thích) — 431 lỗi = 386 PLACE_FAIL + 45 ATC_FAIL, TOÀN BỘ ngày 2026-07-30, 1 root cause (PaperBroker.place_order thiếu cash_only), fix+verify cùng ngày, incident 2026-07/2026-07-30-paper-trading-report-3-root-causes.md. 0 lỗi trong 9 phiên kể từ 07-31. Ngoài ra 18 GHOST_ORDER (07-08/07-09/08-07) = guard idempotency khi chạy LẠI harness trong cùng ngày với state mới — đúng thiết kế, không phải reject của broker. 🔔 (trước: pending)
  ✅ BUY fill không tệ hơn open đáng kể; SELL không thấp hơn open đáng kể — SANITY ĐẠT (KHÔNG phải bằng chứng edge). Đo 2026-08-11 từ journal fill + Open BQ ticker_1m: BUY in-window day-mean −1,7 bps vs open (n=4 ngày, sd_ngày 97,8, t=−0,03); SELL in-window −9,1 bps (n=9 ngày, sd_ngày 6,1) ≈ dưới 1 bước giá (tick 50/22.600 = 22 bps). Không có dấu hiệu fill tệ hơn open một cách hệ thống ⇒ đạt tiêu chí 'không tệ hơn đáng kể'. ⚠️ EDGE 17,6 bps KHÔNG đo được: se ngày 48,9 bps. ⚠️ Mục C của probe execution_quality_review.py KHÔNG BAO GIỜ tính được cái này (đọc dnse_raw_*.jsonl mà paper không bao giờ ghi) — số trên đo thủ công. 🔔 (trước: pending)
  ⏳ quant-skeptic → user sign-off mới flip fill_timing_live_gate — 4/4 gate cơ học ĐÃ ĐẠT 2026-08-11 ⇒ hết vướng về dữ liệu, chỉ còn quyết định. KHUYẾN NGHỊ Taylor: CHƯA flip. Cái sẽ lên live là HYBRID (bật paper 2026-08-10) nhưng mới có ĐÚNG 1 phiên paper (08-11), trong khi 5 phiên của gate 1 là 4 cũ + 1 hybrid; và qty probe (100 cp) quá nhỏ nên hybrid khớp trọn ở block đầu — cơ chế TRẢI BLOCK chưa từng được thực chứng trên paper. Đề xuất: gom thêm 4 phiên BUY hybrid (cron T3/T5: 08-13, 08-18, 08-20, 08-25) → quant-skeptic ~08-26 → user sign-off. User có quyền chốt sớm nếu coi gate cơ học là bất biến theo cơ chế.
  ↳ charter đầy đủ: `mike/kb/paper_programs_charter/fill_timing.md`
=== EXECUTION-QUALITY REVIEW (since 2026-06-26) ===

--- C. DIRECTIONAL FILL SANITY (needs day-open; bps EDGE itself needs weeks, not gated here) ---
   no completed fills yet
_(checklist GO/NO-GO tiếng Anh của probe đã lược — trùng gate tiếng Việt, xem charter)_
_(lược 4 dòng phụ lục của probe — xem nguồn nếu cần)_
🔍 Nguồn: `execution_quality_review.py` (+1 nguồn, xem charter)

── **4) Capitulation-sleeve shadow (DT5G × 8L washout)** · 👤 Taylor · ✅ GREEN
📈 asof 2026-08-10 | mode DEPLOYED | NAV 51.02B | tier NONCRISIS size=0.75 | entry 2026-07-20 | basket 5 mã · 📅 phiên ~45 từ 2026-06-10 · ⏱ nghiệm thu: EVENT-DRIVEN: sau sự kiện washout THẬT đầu tiên (chưa có deadline lịch)
💱 Giao dịch hôm nay: **Không có giao dịch** — mode DEPLOYED · 5 mã · HOLDING 15/60td · 5 names · MTM x1.020 (vintage T-1 theo thiết kế, phiên 2026-08-10) · nguồn `data/pt_capitulation_logs.csv`
📊 Gate: **0/3 PASS** · không đổi từ 2026-07-31 · chi tiết: `mike/kb/paper_programs_charter/capitulation_shadow.md`
🔍 Nguồn: `data/pt_capitulation_state.json` (+1 nguồn, xem charter)

── **5) AlphaLens Paper (FPT/ACB/MBB/HDB vs VNINDEX)** · 👤 DollarBill · ✅ GREEN
📈 EW **+0.69%** vs VNINDEX -4.48% → **excess +5.17pp** (MTM as-of 2026-08-10) · 📅 phiên ~30/66 (2026-07-01→2026-09-30) · ⏱ nghiệm thu: 2026-09-30 — audit độc lập bởi Taylor
💱 Giao dịch hôm nay: **Không có giao dịch** — buy-and-hold theo thiết kế (equal-weight 25%/tên, không rebalance, giữ tới 2026-09-30)
📊 Gate: **0/3 PASS** · không đổi từ 2026-07-31 · chi tiết: `mike/kb/paper_programs_charter/alphalens.md`
- Vị thế (MTM as-of 2026-08-10, BQ cache close phiên gần nhất):
  • FPT: 70,200 → 71,800 = **+2.28%** (entry 2026-07-01, PE vs PE_MA1Y)
  • ACB: 22,650 → 22,650 = **+0.00%** (entry 2026-07-01, P/B vs Gordon justified-PB)
  • MBB: 25,200 → 24,250 = **-3.77%** (entry 2026-07-01, P/B vs Gordon justified-PB)
  • HDB: 25,850 → 26,950 = **+4.26%** (entry 2026-07-01, P/B vs Gordon justified-PB)
- VNINDEX 1,860.01 → 1,776.77
🔍 Nguồn: `data/alphalens_paper.json` (+1 nguồn, xem charter)

── **6) ORB intraday VN30F (ring-fenced)** · 👤 Taylor · ✅ GREEN
📈 asof 2026-08-11 | 46 phiên từ 2026-06-09 | NAV 1.076B (+7.64%) | WR 58.7% | phiên cuối +0.16% (sig -1) | Sharpe report 2.75 (mẫu nhỏ — đọc thận trọng) · 📅 phiên ~46 từ 2026-06-09 · ⏱ nghiệm thu: ≥60 phiên GỒM chop/bear → re-eval quant-skeptic (điều kiện REGIME, không có deadline lịch)
💱 Giao dịch hôm nay: **CÓ giao dịch** — sig -1 · vào 1,925.5 → ra 1,922.2 · net +0.16% (1 lượt/phiên theo thiết kế ORB) · nguồn `data/orb_pt_log.csv`
📊 Gate: **0/4 PASS** · không đổi từ 2026-07-31 · chi tiết: `mike/kb/paper_programs_charter/orb_intraday.md`
🔍 Nguồn: `data/orb_pt_status.json` (+1 nguồn, xem charter)

── **7) Engine-room OOS panel (V11/V12/V4 vs V2.3-book vs VNINDEX)** · 👤 Taylor · ✅ GREEN
📈 V2.3-book -0.55% vs VNINDEX -1.21% (cửa sổ chung, NAV rebase 50B) · 📅 phiên ~44 từ 2026-06-11 · ⏱ nghiệm thu: 2026-12-01 (~6 tháng OOS trên cửa sổ chung từ 2026-06-11)
💱 Giao dịch hôm nay: **n/a theo thiết kế** — panel so sánh NAV của 5 sổ MÔ PHỎNG (V11/V12/V4/V23/VNI_BH) — panel không giữ nhật ký lệnh tách bạch; giao dịch THẬT của sổ production V2.3 nằm ở báo cáo EOD live, không phải ở đây
📊 Gate: **0/2 PASS** · không đổi từ 2026-07-31 · chi tiết: `mike/kb/paper_programs_charter/engine_room_oos.md`
Cửa sổ so sánh CHUNG 2026-06-11 → 2026-08-10 (43 phiên), NAV rebase 50B tại đầu cửa sổ (không phải NAV thô từ inception gốc):
  V11       -1.41%  (NAV 49.29B)
  V12       -1.30%  (NAV 49.35B)
  V4_DT5G   -0.93%  (NAV 49.54B)
  V23       -0.55%  (NAV 49.73B)
  VNI_BH    -1.21%  (NAV 49.39B)
🔍 Nguồn: `data/papertrade_compare5.csv (papertrade_compare.py)` (+1 nguồn, xem charter)

───
📎 *Badge: 🔴 RED = probe lỗi / cảnh báo chưa được giải thích / có gate FAIL · ⏳ WATCH = có cảnh báo đã giải thích hoặc thiếu khai báo giao dịch · ✅ GREEN = còn lại. Mục đích + phương pháp + tiêu chí nghiệm thu đầy đủ: `mike/kb/paper_programs_charter/<id>.md` (tự sinh từ registry). Mục hoàn tất hoặc thuộc vận hành được giữ trong registry nhưng không lặp ở đây. Gate chỉ in đầy đủ khi có thay đổi — trạng thái so sánh lưu ở `data/paper_report_state.json`.*
⚠️ *PAPER TRADING — không phải tiền thật; toàn bộ số liệu là mô phỏng/quan sát, không phải khuyến nghị đầu tư. Số không trace được về file nguồn = n/a.*
