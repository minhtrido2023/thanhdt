📋 **Paper Programs Daily Report — 2026-08-19**
Render 07:30 ICT · registry v3 · 7 paper-trial đang theo dõi · *vintage dữ liệu xem `asof`/nguồn từng mục (BQ chưa có close phiên T lúc 16:00)*
ℹ️ **Đã chuyển khỏi báo cáo ngày**: EXTREME-regime gate · Fill-timing window (BUY 10:45-11:15 / SELL 09:15-09:45) · Vol-scale buy chase-cap (patch#3) · custom30V yield_floor — nhãn quan sát (Option C). Dữ liệu/cron không bị xóa; xem registry để biết lý do và mốc review.
🔴 **CẦN CHÚ Ý NGAY** (1): #4 Order-book execution shadow (10-level bid-ask)

**TỔNG QUAN** — trạng thái · paper-trial · chỉ số mới nhất · giao dịch hôm nay:
⏳ **1) DC-book NEUTRAL idle-cash Waterfall** — NAV 972,407,419đ · lũy kế -2.76% · phiên gần nhất -0.35% (as-of 2026-08-18) | 💱 **n/a — `data/dc_book_waterfall_paper_nav.csv` CHƯA có dòng cho phiên…
⏳ **2) Capitulation-sleeve shadow (DT5G × 8L washout)** — asof 2026-08-17 | mode DEPLOYED | NAV 51.14B | tier NONCRISIS size=0.75 | entry 2026-07-20 | b… | 💱 **n/a — `data/pt_capitulation_logs.csv` CHƯA có dòng cho phiên 2026-0…
✅ **3) AlphaLens Paper (FPT/ACB/MBB/HDB vs VNINDEX)** — EW **-1.79%** vs VNINDEX -6.88% → **excess +5.09pp** (MTM as-of 2026-08-18) | 💱 **Không có giao dịch** — buy-and-hold theo thiết kế (equal-weight 25%…
🔴 **4) Order-book execution shadow (10-level bid-ask)** — order-book opportunities N=8 · snapshot hợp lệ 0 | 💱 **n/a theo thiết kế** — Chương trình LOG-ONLY, không phát sinh lệnh r…
⏳ **5) ORB intraday VN30F (ring-fenced)** — asof 2026-08-18 | 51 phiên từ 2026-06-09 | NAV 1.091B (+9.09%) | WR 60.8% | phiên cuối +0.44%… | 💱 **n/a — `data/orb_pt_log.csv` CHƯA có dòng cho phiên 2026-08-19** (pi…
✅ **6) Engine-room OOS panel (V11/V12/V4 vs V2.3-book vs VNINDEX)** — V2.3-book -2.14% vs VNINDEX -3.96% (cửa sổ chung, NAV rebase 50B) | 💱 **n/a theo thiết kế** — panel so sánh NAV của 5 sổ MÔ PHỎNG (V11/V12/…
✅ **7) P2 — mẫu số pacing theo KL KỲ VỌNG (expected-volume pacing)** — 1 phiên có lệnh ADV20-paced · **order-day N=1** · 1 slice quan sát | 💱 **n/a theo thiết kế** — chương trình LOG-ONLY: không phát sinh lệnh r…

── **1) DC-book NEUTRAL idle-cash Waterfall** · 👤 Taylor · ⏳ WATCH
📈 NAV 972,407,419đ · lũy kế -2.76% · phiên gần nhất -0.35% (as-of 2026-08-18) · 📅 phiên ~33 từ 2026-07-06 · ⏱ nghiệm thu: event-anchored: chu kỳ reverse-unwind ĐẦU TIÊN + settle 4-6 tuần · trần 2026-10-06
💱 Giao dịch hôm nay: **n/a — `data/dc_book_waterfall_paper_nav.csv` CHƯA có dòng cho phiên 2026-08-19** (pipeline sinh dữ liệu chạy 15:05/15:30 ICT; nếu đã quá giờ đó ⇒ pipeline chưa chạy/lỗi) · dòng gần nhất 2026-08-18: turnover 0.00% · rebalanced=False · deployed=True · sleeve -0.35%
📊 Gate: **0/3 PASS** · không đổi từ 2026-07-31 · chi tiết: `mike/kb/paper_programs_charter/dc_waterfall.md`
### 🪜 DC-book NEUTRAL Waterfall — Paper Sleeve (v2)
*Tiền rảnh NEUTRAL: BAL/LAG → DC book (double-confirm, liq≥3B) → custom30V, **continuous-residual** | cap gộp 0.15/tên · rebal q2m5 | flag `dc_book_waterfall_enabled`=ON (chỉ paper `main`) | as-of 2026-08-18 00:00:00*

- Trạng thái hôm nay: NEUTRAL → waterfall chạy LIÊN TỤC trên phần tiền dư (BAL/LAG rỗng)
- Nhịp rebal: giữ nguyên, trọng số drift (q2m5 — chưa tới kỳ)
- DC book (7): ACB, FPT, HAH, MBB, PVT, SSI, TCB @ 0.0%/tên (leg 0.0%) | custom30V 0.0% | cash 0.0%
- Due-diligence (informational, không tham gia chọn mã):
  DD ACB [DC] (data 2026-08-18): thanh khoản OK (ADV3T 286.53 tỷ/phiên) · ⚠ universe_pit: n/a (không đọc được)
  FA: ROE5Y 23.0% · ROE_Min3Y 17.6% · FSCORE 1 · D/E 9.75 · PE 8.02
  DD FPT [DC] (data 2026-08-18): thanh khoản OK (ADV3T 456.05 tỷ/phiên) · ⚠ universe_pit: n/a (không đọc được)
  FA: ROE5Y 26.6% · ROE_Min3Y 28.1% · FSCORE 5 · D/E 0.80 · PE 11.83
  DD HAH [DC] (data 2026-08-18): thanh khoản OK (ADV3T 26.23 tỷ/phiên) · ⚠ universe_pit: n/a (không đọc được)
  FA: ROE5Y 24.6% · ROE_Min3Y 15.5% · FSCORE 4 · D/E
… (cắt bớt, xem nguồn để đủ; exit=0)
_(lược 3 dòng phụ lục của probe — xem nguồn nếu cần)_
🔍 Nguồn: `data/dc_book_waterfall_paper_state.json` (+1 nguồn, xem charter)

── **2) Capitulation-sleeve shadow (DT5G × 8L washout)** · 👤 Taylor · ⏳ WATCH
📈 asof 2026-08-17 | mode DEPLOYED | NAV 51.14B | tier NONCRISIS size=0.75 | entry 2026-07-20 | basket 5 mã · 📅 phiên ~51 từ 2026-06-10 · ⏱ nghiệm thu: EVENT-DRIVEN: sau sự kiện washout THẬT đầu tiên (chưa có deadline lịch)
💱 Giao dịch hôm nay: **n/a — `data/pt_capitulation_logs.csv` CHƯA có dòng cho phiên 2026-08-18** (pipeline sinh dữ liệu chạy 15:05/15:30 ICT; nếu đã quá giờ đó ⇒ pipeline chưa chạy/lỗi) · dòng gần nhất 2026-08-17: mode DEPLOYED · 5 mã · HOLDING 20/60td · 5 names · MTM x1.023
📊 Gate: **0/3 PASS** · không đổi từ 2026-07-31 · chi tiết: `mike/kb/paper_programs_charter/capitulation_shadow.md`
🔍 Nguồn: `data/pt_capitulation_state.json` (+1 nguồn, xem charter)

── **3) AlphaLens Paper (FPT/ACB/MBB/HDB vs VNINDEX)** · 👤 DollarBill · ✅ GREEN
📈 EW **-1.79%** vs VNINDEX -6.88% → **excess +5.09pp** (MTM as-of 2026-08-18) · 📅 phiên ~36/66 (2026-07-01→2026-09-30) · ⏱ nghiệm thu: 2026-09-30 — audit độc lập bởi Taylor
💱 Giao dịch hôm nay: **Không có giao dịch** — buy-and-hold theo thiết kế (equal-weight 25%/tên, không rebalance, giữ tới 2026-09-30)
📊 Gate: **0/3 PASS** · không đổi từ 2026-07-31 · chi tiết: `mike/kb/paper_programs_charter/alphalens.md`
- Vị thế (MTM as-of 2026-08-18, BQ cache close phiên gần nhất):
  • FPT: 70,200 → 69,000 = **-1.71%** (entry 2026-07-01, PE vs PE_MA1Y)
  • ACB: 22,650 → 21,650 = **-4.42%** (entry 2026-07-01, P/B vs Gordon justified-PB)
  • MBB: 25,200 → 19,950 = **-5.30%** (entry 2026-07-01, P/B vs Gordon justified-PB) [giá vào 25,200→21,066 do quyền]
  • HDB: 25,850 → 26,950 = **+4.26%** (entry 2026-07-01, P/B vs Gordon justified-PB)
- VNINDEX 1,860.01 → 1,732.02
🔍 Nguồn: `data/alphalens_paper.json` (+1 nguồn, xem charter)

── **4) Order-book execution shadow (10-level bid-ask)** · 👤 Taylor · 🔴 RED
📈 order-book opportunities N=8 · snapshot hợp lệ 0 · 📅 phiên ~2/20 (2026-08-18→2026-09-14) · ⏱ nghiệm thu: Review 2026-09-16 09:30 ICT — cần >=20 phiên evidence; chỉ quyết định sang paper A/B hay dừng, không go-live
💱 Giao dịch hôm nay: **n/a theo thiết kế** — Chương trình LOG-ONLY, không phát sinh lệnh riêng; activity đọc từ probe theo child-order opportunity. N=0 nghĩa là chưa có opportunity, không phải policy không có giá trị.
🔴 Cảnh báo: ERROR telemetry: 8 → **CHƯA CÓ GIẢI THÍCH** — Taylor phải rà nguồn bên dưới trong hôm nay rồi khai báo `attention_notes` trong registry (không để con số trần).
📊 Gate: **0/4 PASS** · không đổi từ 2026-08-17 · chi tiết: `mike/kb/paper_programs_charter/order_book_execution_shadow.md`
order-book observations N=8 · valid=0 · sessions=2
policy KEEP=8 REDUCE=0 DEFER=0
latency snapshot→order median=n/ams
fill-linked children=6/8 · fill-rate=75.0%
time-to-first-fill median=n/as · fill-vs-limit slippage median=n/abps
outcome coverage 1m=0/0 · 5m=0/0 · 15m=0/0
adverse-selection median n/a — chưa đủ snapshot hậu kiểm
ERROR telemetry: 8
scope v1: spread + displayed depth + adverse selection; resilience EXCLUDED (60s cadence).
🔍 Nguồn: `data/execution_logs/orderbook_shadow_<account>_<date>.jsonl — schema orderbook_execution_v1: trace_id parent/child, baseline, KEEP/REDUCE/DEFER, latency và snapshot immutable` (+2 nguồn, xem charter)

── **5) ORB intraday VN30F (ring-fenced)** · 👤 Taylor · ⏳ WATCH
📈 asof 2026-08-18 | 51 phiên từ 2026-06-09 | NAV 1.091B (+9.09%) | WR 60.8% | phiên cuối +0.44% (sig -1) | Sharpe report 2.92 (mẫu nhỏ — đọc thận trọng) · 📅 phiên ~52 từ 2026-06-09 · ⏱ nghiệm thu: ≥60 phiên GỒM chop/bear → re-eval quant-skeptic (điều kiện REGIME, không có deadline lịch)
💱 Giao dịch hôm nay: **n/a — `data/orb_pt_log.csv` CHƯA có dòng cho phiên 2026-08-19** (pipeline sinh dữ liệu chạy 15:05/15:30 ICT; nếu đã quá giờ đó ⇒ pipeline chưa chạy/lỗi) · dòng gần nhất 2026-08-18: sig -1 · vào 1,881.1 → ra 1,872.6 · net +0.44% (1 lượt/phiên theo thiết kế ORB)
📊 Gate: **0/4 PASS** · không đổi từ 2026-07-31 · chi tiết: `mike/kb/paper_programs_charter/orb_intraday.md`
🔍 Nguồn: `data/orb_pt_status.json` (+1 nguồn, xem charter)

── **6) Engine-room OOS panel (V11/V12/V4 vs V2.3-book vs VNINDEX)** · 👤 Taylor · ✅ GREEN
📈 V2.3-book -2.14% vs VNINDEX -3.96% (cửa sổ chung, NAV rebase 50B) · 📅 phiên ~50 từ 2026-06-11 · ⏱ nghiệm thu: 2026-12-01 (~6 tháng OOS trên cửa sổ chung từ 2026-06-11)
💱 Giao dịch hôm nay: **n/a theo thiết kế** — panel so sánh NAV của 5 sổ MÔ PHỎNG (V11/V12/V4/V23/VNI_BH) — panel không giữ nhật ký lệnh tách bạch; giao dịch THẬT của sổ production V2.3 nằm ở báo cáo EOD live, không phải ở đây
📊 Gate: **0/2 PASS** · không đổi từ 2026-07-31 · chi tiết: `mike/kb/paper_programs_charter/engine_room_oos.md`
Cửa sổ so sánh CHUNG 2026-06-11 → 2026-08-17 (48 phiên), NAV rebase 50B tại đầu cửa sổ (không phải NAV thô từ inception gốc):
  V11       -3.39%  (NAV 48.31B)
  V12       -2.00%  (NAV 49.00B)
  V4_DT5G   -2.51%  (NAV 48.75B)
  V23       -2.14%  (NAV 48.93B)
  VNI_BH    -3.96%  (NAV 48.02B)
🔍 Nguồn: `data/papertrade_compare5.csv (papertrade_compare.py)` (+1 nguồn, xem charter)

── **7) P2 — mẫu số pacing theo KL KỲ VỌNG (expected-volume pacing)** · 👤 Taylor · ✅ GREEN
📈 1 phiên có lệnh ADV20-paced · **order-day N=1** · 1 slice quan sát · 📅 phiên ~3/22 (2026-08-17→2026-09-15) · ⏱ nghiệm thu: Bắt đầu 2026-08-17 · review 2026-09-15 (≥20 phiên VÀ ≥25 order-day). Đang chạy SHADOW log-only trên live; LIVE chưa đổi hành vi, flip gate cần quant-skeptic + user sign-off
💱 Giao dịch hôm nay: **n/a theo thiết kế** — chương trình LOG-ONLY: không phát sinh lệnh riêng nào (P2 chưa được phép đổi hành vi trên live). Hoạt động trong ngày đọc ở dòng cuối output probe ('hôm nay: N order-day · M slice')
📊 Gate: **0/5 PASS** · không đổi từ 2026-08-14 · chi tiết: `mike/kb/paper_programs_charter/expvol_pacing.md`
1 phiên có lệnh ADV20-paced · **order-day N=1** · 1 slice quan sát
bind=ceil 1/1 (100.0%) — chỉ nhóm này P2 mới nới được
delta allowance khi bind=ceil (cp): trung vị +0 · tb +0 · max +0 · 0/1 slice có delta>0
an toàn: %tape tối đa nếu P2 khớp trọn allowance = 23.1% (trần 50%) · vi phạm clamp **0** · EXPVOL_SHADOW_ERR **0**
hôm nay (2026-08-19): 0 order-day · 0 slice · bind=ceil 0
🔍 Nguồn: `data/execution_logs/exec_{SpaceX,ZaloPay,RocketX}_*_journal.csv — event EXPVOL_SHADOW / EXPVOL_SHADOW_ERR` (+3 nguồn, xem charter)

───
📎 *Badge: 🔴 RED = probe lỗi / cảnh báo chưa được giải thích / có gate FAIL · ⏳ WATCH = có cảnh báo đã giải thích hoặc thiếu khai báo giao dịch · ✅ GREEN = còn lại. Mục đích + phương pháp + tiêu chí nghiệm thu đầy đủ: `mike/kb/paper_programs_charter/<id>.md` (tự sinh từ registry). Mục hoàn tất hoặc thuộc vận hành được giữ trong registry nhưng không lặp ở đây. Gate chỉ in đầy đủ khi có thay đổi — trạng thái so sánh lưu ở `data/paper_report_state.json`.*
⚠️ *PAPER TRADING — không phải tiền thật; toàn bộ số liệu là mô phỏng/quan sát, không phải khuyến nghị đầu tư. Số không trace được về file nguồn = n/a.*
