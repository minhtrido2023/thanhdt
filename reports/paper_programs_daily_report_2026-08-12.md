📋 **Paper Programs Daily Report — 2026-08-12**
Render 16:00 ICT · registry v3 · 5 paper-trial đang theo dõi · *vintage dữ liệu xem `asof`/nguồn từng mục (BQ chưa có close phiên T lúc 16:00)*
ℹ️ **Đã chuyển khỏi báo cáo ngày**: EXTREME-regime gate · Fill-timing window (BUY 10:45-11:15 / SELL 09:15-09:45) · Vol-scale buy chase-cap (patch#3). Dữ liệu/cron không bị xóa; xem registry để biết lý do và mốc review.
⏳ **Theo dõi** (1): #1 DC-book NEUTRAL idle-cash Waterfall

**TỔNG QUAN** — trạng thái · paper-trial · chỉ số mới nhất · giao dịch hôm nay:
⏳ **1) DC-book NEUTRAL idle-cash Waterfall** — NAV 1,012,271,100đ · lũy kế +1.23% · phiên gần nhất -2.36% (as-of 2026-08-11) | 💱 **n/a — `data/dc_book_waterfall_paper_nav.csv` CHƯA có dòng cho phiên…
✅ **2) Capitulation-sleeve shadow (DT5G × 8L washout)** — asof 2026-08-11 | mode DEPLOYED | NAV 50.96B | tier NONCRISIS size=0.75 | entry 2026-07-20 | b… | 💱 **Không có giao dịch** — mode DEPLOYED · 5 mã · HOLDING 16/60td · 5 n…
✅ **3) AlphaLens Paper (FPT/ACB/MBB/HDB vs VNINDEX)** — EW **-3.44%** vs VNINDEX -4.66% → **excess +1.22pp** (MTM as-of 2026-08-11) | 💱 **Không có giao dịch** — buy-and-hold theo thiết kế (equal-weight 25%…
✅ **4) ORB intraday VN30F (ring-fenced)** — asof 2026-08-12 | 47 phiên từ 2026-06-09 | NAV 1.083B (+8.34%) | WR 59.6% | phiên cuối +0.65%… | 💱 **CÓ giao dịch** — sig +1 · vào 1,924.1 → ra 1,937.0 · net +0.65% (1…
✅ **5) Engine-room OOS panel (V11/V12/V4 vs V2.3-book vs VNINDEX)** — V2.3-book -0.95% vs VNINDEX -1.40% (cửa sổ chung, NAV rebase 50B) | 💱 **n/a theo thiết kế** — panel so sánh NAV của 5 sổ MÔ PHỎNG (V11/V12/…

── **1) DC-book NEUTRAL idle-cash Waterfall** · 👤 Taylor · ⏳ WATCH
📈 NAV 1,012,271,100đ · lũy kế +1.23% · phiên gần nhất -2.36% (as-of 2026-08-11) · 📅 phiên ~28 từ 2026-07-06 · ⏱ nghiệm thu: event-anchored: chu kỳ reverse-unwind ĐẦU TIÊN + settle 4-6 tuần · trần 2026-10-06
💱 Giao dịch hôm nay: **n/a — `data/dc_book_waterfall_paper_nav.csv` CHƯA có dòng cho phiên 2026-08-12** (pipeline sinh dữ liệu chạy 15:05/15:30 ICT; nếu đã quá giờ đó ⇒ pipeline chưa chạy/lỗi) · dòng gần nhất 2026-08-11: turnover 0.00% · rebalanced=False · deployed=True · sleeve -2.36%
📊 Gate: **0/3 PASS** · không đổi từ 2026-07-31 · chi tiết: `mike/kb/paper_programs_charter/dc_waterfall.md`
### 🪜 DC-book NEUTRAL Waterfall — Paper Sleeve (v2)
*Tiền rảnh NEUTRAL: BAL/LAG → DC book (double-confirm, liq≥3B) → custom30V, **continuous-residual** | cap gộp 0.15/tên · rebal q2m5 | flag `dc_book_waterfall_enabled`=ON (chỉ paper `main`) | as-of 2026-08-11 00:00:00*

- Trạng thái hôm nay: NEUTRAL → waterfall chạy LIÊN TỤC trên phần tiền dư (BAL/LAG rỗng)
- Nhịp rebal: giữ nguyên, trọng số drift (q2m5 — chưa tới kỳ)
- DC book (7): ACB, FPT, HAH, MBB, PVT, SSI, TCB @ 0.0%/tên (leg 0.0%) | custom30V 0.0% | cash 0.0%
- Due-diligence (informational, không tham gia chọn mã):
  DD ACB [DC] (data 2026-08-11): thanh khoản OK (ADV3T 346.22 tỷ/phiên) · ⚠ universe_pit: n/a (không đọc được)
  FA: ROE5Y 23.0% · ROE_Min3Y 17.6% · FSCORE 1 · D/E 9.75 · PE 8.39
  DD FPT [DC] (data 2026-08-11): thanh khoản OK (ADV3T 484.84 tỷ/phiên) · ⚠ universe_pit: n/a (không đọc được)
  FA: ROE5Y 26.6% · ROE_Min3Y 28.1% · FSCORE 5 · D/E 0.80 · PE 12.21
  DD HAH [DC] (data 2026-08-11): thanh khoản OK (ADV3T 25.35 tỷ/phiên) · ⚠ universe_pit: n/a (không đọc được)
  FA: ROE5Y 24.6% · ROE_Min3Y 15.5% · FSCORE 4 · D/E
… (cắt bớt, xem nguồn để đủ; exit=0)
_(lược 3 dòng phụ lục của probe — xem nguồn nếu cần)_
🔍 Nguồn: `data/dc_book_waterfall_paper_state.json` (+1 nguồn, xem charter)

── **2) Capitulation-sleeve shadow (DT5G × 8L washout)** · 👤 Taylor · ✅ GREEN
📈 asof 2026-08-11 | mode DEPLOYED | NAV 50.96B | tier NONCRISIS size=0.75 | entry 2026-07-20 | basket 5 mã · 📅 phiên ~46 từ 2026-06-10 · ⏱ nghiệm thu: EVENT-DRIVEN: sau sự kiện washout THẬT đầu tiên (chưa có deadline lịch)
💱 Giao dịch hôm nay: **Không có giao dịch** — mode DEPLOYED · 5 mã · HOLDING 16/60td · 5 names · MTM x1.019 (vintage T-1 theo thiết kế, phiên 2026-08-11) · nguồn `data/pt_capitulation_logs.csv`
📊 Gate: **0/3 PASS** · không đổi từ 2026-07-31 · chi tiết: `mike/kb/paper_programs_charter/capitulation_shadow.md`
🔍 Nguồn: `data/pt_capitulation_state.json` (+1 nguồn, xem charter)

── **3) AlphaLens Paper (FPT/ACB/MBB/HDB vs VNINDEX)** · 👤 DollarBill · ✅ GREEN
📈 EW **-3.44%** vs VNINDEX -4.66% → **excess +1.22pp** (MTM as-of 2026-08-11) · 📅 phiên ~31/66 (2026-07-01→2026-09-30) · ⏱ nghiệm thu: 2026-09-30 — audit độc lập bởi Taylor
💱 Giao dịch hôm nay: **Không có giao dịch** — buy-and-hold theo thiết kế (equal-weight 25%/tên, không rebalance, giữ tới 2026-09-30)
📊 Gate: **0/3 PASS** · không đổi từ 2026-07-31 · chi tiết: `mike/kb/paper_programs_charter/alphalens.md`
- Vị thế (MTM as-of 2026-08-11, BQ cache close phiên gần nhất):
  • FPT: 70,200 → 71,200 = **+1.42%** (entry 2026-07-01, PE vs PE_MA1Y)
  • ACB: 22,650 → 22,650 = **+0.00%** (entry 2026-07-01, P/B vs Gordon justified-PB)
  • MBB: 25,200 → 20,350 = **-19.25%** (entry 2026-07-01, P/B vs Gordon justified-PB)
  • HDB: 25,850 → 26,900 = **+4.06%** (entry 2026-07-01, P/B vs Gordon justified-PB)
- VNINDEX 1,860.01 → 1,773.41
🔍 Nguồn: `data/alphalens_paper.json` (+1 nguồn, xem charter)

── **4) ORB intraday VN30F (ring-fenced)** · 👤 Taylor · ✅ GREEN
📈 asof 2026-08-12 | 47 phiên từ 2026-06-09 | NAV 1.083B (+8.34%) | WR 59.6% | phiên cuối +0.65% (sig +1) | Sharpe report 2.94 (mẫu nhỏ — đọc thận trọng) · 📅 phiên ~47 từ 2026-06-09 · ⏱ nghiệm thu: ≥60 phiên GỒM chop/bear → re-eval quant-skeptic (điều kiện REGIME, không có deadline lịch)
💱 Giao dịch hôm nay: **CÓ giao dịch** — sig +1 · vào 1,924.1 → ra 1,937.0 · net +0.65% (1 lượt/phiên theo thiết kế ORB) · nguồn `data/orb_pt_log.csv`
📊 Gate: **0/4 PASS** · không đổi từ 2026-07-31 · chi tiết: `mike/kb/paper_programs_charter/orb_intraday.md`
🔍 Nguồn: `data/orb_pt_status.json` (+1 nguồn, xem charter)

── **5) Engine-room OOS panel (V11/V12/V4 vs V2.3-book vs VNINDEX)** · 👤 Taylor · ✅ GREEN
📈 V2.3-book -0.95% vs VNINDEX -1.40% (cửa sổ chung, NAV rebase 50B) · 📅 phiên ~45 từ 2026-06-11 · ⏱ nghiệm thu: 2026-12-01 (~6 tháng OOS trên cửa sổ chung từ 2026-06-11)
💱 Giao dịch hôm nay: **n/a theo thiết kế** — panel so sánh NAV của 5 sổ MÔ PHỎNG (V11/V12/V4/V23/VNI_BH) — panel không giữ nhật ký lệnh tách bạch; giao dịch THẬT của sổ production V2.3 nằm ở báo cáo EOD live, không phải ở đây
📊 Gate: **0/2 PASS** · không đổi từ 2026-07-31 · chi tiết: `mike/kb/paper_programs_charter/engine_room_oos.md`
Cửa sổ so sánh CHUNG 2026-06-11 → 2026-08-11 (44 phiên), NAV rebase 50B tại đầu cửa sổ (không phải NAV thô từ inception gốc):
  V11       -1.38%  (NAV 49.31B)
  V12       -1.29%  (NAV 49.36B)
  V4_DT5G   -1.04%  (NAV 49.48B)
  V23       -0.95%  (NAV 49.52B)
  VNI_BH    -1.40%  (NAV 49.30B)
🔍 Nguồn: `data/papertrade_compare5.csv (papertrade_compare.py)` (+1 nguồn, xem charter)

───
📎 *Badge: 🔴 RED = probe lỗi / cảnh báo chưa được giải thích / có gate FAIL · ⏳ WATCH = có cảnh báo đã giải thích hoặc thiếu khai báo giao dịch · ✅ GREEN = còn lại. Mục đích + phương pháp + tiêu chí nghiệm thu đầy đủ: `mike/kb/paper_programs_charter/<id>.md` (tự sinh từ registry). Mục hoàn tất hoặc thuộc vận hành được giữ trong registry nhưng không lặp ở đây. Gate chỉ in đầy đủ khi có thay đổi — trạng thái so sánh lưu ở `data/paper_report_state.json`.*
⚠️ *PAPER TRADING — không phải tiền thật; toàn bộ số liệu là mô phỏng/quan sát, không phải khuyến nghị đầu tư. Số không trace được về file nguồn = n/a.*
