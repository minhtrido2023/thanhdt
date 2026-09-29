📋 **Paper Programs Daily Report — 2026-09-22**
Render 07:30 ICT · registry v3 · 7 paper-trial đang theo dõi · *vintage dữ liệu xem `asof`/nguồn từng mục (BQ chưa có close phiên T lúc 16:00)*
ℹ️ **Đã chuyển khỏi báo cáo ngày**: EXTREME-regime gate · Fill-timing window (BUY 10:45-11:15 / SELL 09:15-09:45) · Vol-scale buy chase-cap (patch#3) · custom30V yield_floor — nhãn quan sát (Option C) · BAL signal shadow-track — hiệu suất gần đây (case VPI). Dữ liệu/cron không bị xóa; xem registry để biết lý do và mốc review.
⏳ **Theo dõi** (4): #1 DC-book NEUTRAL idle-cash Waterfall · #2 Capitulation-sleeve shadow (DT5G × 8L washout) · #4 Order-book execution shadow (10-level bid-ask) · #5 ORB intraday VN30F (ring-fenced)

**TỔNG QUAN** — trạng thái · paper-trial · chỉ số mới nhất · giao dịch hôm nay:
⏳ **1) DC-book NEUTRAL idle-cash Waterfall** — NAV 1,010,458,476đ · lũy kế +1.05% · phiên gần nhất -0.66% (as-of 2026-09-21) | 💱 **n/a — `data/dc_book_waterfall_paper_nav.csv` CHƯA có dòng cho phiên…
⏳ **2) Capitulation-sleeve shadow (DT5G × 8L washout)** — asof 2026-09-18 | mode DEPLOYED | NAV 51.94B | tier NONCRISIS size=0.75 | entry 2026-07-20 | b… | 💱 **n/a — `data/pt_capitulation_logs.csv` CHƯA có dòng cho phiên 2026-0…
✅ **3) AlphaLens Paper (FPT/ACB/MBB/HDB vs VNINDEX)** — EW **-0.96%** vs VNINDEX -3.24% → **excess +2.28pp** (MTM as-of 2026-09-21) | 💱 **Không có giao dịch** — buy-and-hold theo thiết kế (equal-weight 25%…
⏳ **4) Order-book execution shadow (10-level bid-ask)** — order-book opportunities N=287 · snapshot hợp lệ 267 | 💱 **n/a theo thiết kế** — Chương trình LOG-ONLY, không phát sinh lệnh r…
⏳ **5) ORB intraday VN30F (ring-fenced)** — asof 2026-09-21 | 71 phiên từ 2026-06-09 | NAV 1.074B (+7.37%) | WR 56.3% | phiên cuối +1.26%… | 💱 **n/a — `data/orb_pt_log.csv` CHƯA có dòng cho phiên 2026-09-22** (pi…
✅ **6) Engine-room OOS panel (V11/V12/V4 vs V2.3-book vs VNINDEX)** — V2.3-book -2.38% vs VNINDEX +0.95% (cửa sổ chung, NAV rebase 50B) | 💱 **n/a theo thiết kế** — panel so sánh NAV của 5 sổ MÔ PHỎNG (V11/V12/…
✅ **7) P2 — mẫu số pacing theo KL KỲ VỌNG (expected-volume pacing)** — 2 phiên có lệnh ADV20-paced · **order-day N=2** · 76 slice quan sát | 💱 **n/a theo thiết kế** — chương trình LOG-ONLY: không phát sinh lệnh r…

── **1) DC-book NEUTRAL idle-cash Waterfall** · 👤 Taylor · ⏳ WATCH
📈 NAV 1,010,458,476đ · lũy kế +1.05% · phiên gần nhất -0.66% (as-of 2026-09-21) · 📅 phiên ~57 từ 2026-07-06 · ⏱ nghiệm thu: event-anchored: chu kỳ reverse-unwind ĐẦU TIÊN + settle 4-6 tuần · trần 2026-10-06
💱 Giao dịch hôm nay: **n/a — `data/dc_book_waterfall_paper_nav.csv` CHƯA có dòng cho phiên 2026-09-22** (pipeline sinh dữ liệu chạy 15:05/15:30 ICT; nếu đã quá giờ đó ⇒ pipeline chưa chạy/lỗi) · dòng gần nhất 2026-09-21: turnover 0.00% · rebalanced=False · deployed=True · sleeve -0.66%
📊 Gate: **0/3 PASS** · không đổi từ 2026-07-31 · chi tiết: `mike/kb/paper_programs_charter/dc_waterfall.md`
### 🪜 DC-book NEUTRAL Waterfall — Paper Sleeve (v2)
*Tiền rảnh NEUTRAL: BAL/LAG → DC book (double-confirm, liq≥3B) → custom30V, **continuous-residual** | cap gộp 0.15/tên · rebal q2m5 | flag `dc_book_waterfall_enabled`=ON (chỉ paper `main`) | as-of 2026-09-21 00:00:00*

- Trạng thái hôm nay: NEUTRAL → waterfall chạy LIÊN TỤC trên phần tiền dư (BAL/LAG rỗng)
- Nhịp rebal: giữ nguyên, trọng số drift (q2m5 — chưa tới kỳ)
- DC book (7): ACB, FPT, HAH, MBB, PVT, SSI, TCB (leg 0.0%) | custom30V 0.0% | cash 0.0%
- Due-diligence (informational, không tham gia chọn mã):
  DD ACB [DC] (data 2026-09-21): thanh khoản OK (ADV3T 229.85 tỷ/phiên) · ⚠ universe_pit: n/a (không đọc được)
  FA: ROE5Y 23.0% · ROE_Min3Y 17.6% · FSCORE 1 · D/E 9.75 · PE 8.29
  DD FPT [DC] (data 2026-09-21): thanh khoản OK (ADV3T 417.82 tỷ/phiên) · ⚠ universe_pit: n/a (không đọc được)
  FA: ROE5Y 26.6% · ROE_Min3Y 28.1% · FSCORE 5 · D/E 0.79 · PE 11.38
  DD HAH [DC] (data 2026-09-21): thanh khoản OK (ADV3T 26.74 tỷ/phiên) · ⚠ universe_pit: n/a (không đọc được)
  FA: ROE5Y 24.6% · ROE_Min3Y 15.5% · FSCORE 5 · D/E 0.69 · PE 
… (cắt bớt, xem nguồn để đủ; exit=0)
_(lược 3 dòng phụ lục của probe — xem nguồn nếu cần)_
🔍 Nguồn: `data/dc_book_waterfall_paper_state.json` (+1 nguồn, xem charter)

── **2) Capitulation-sleeve shadow (DT5G × 8L washout)** · 👤 Taylor · ⏳ WATCH
📈 asof 2026-09-18 | mode DEPLOYED | NAV 51.94B | tier NONCRISIS size=0.75 | entry 2026-07-20 | basket 5 mã · 📅 phiên ~75 từ 2026-06-10 · ⏱ nghiệm thu: EVENT-DRIVEN: sau sự kiện washout THẬT đầu tiên (chưa có deadline lịch)
💱 Giao dịch hôm nay: **n/a — `data/pt_capitulation_logs.csv` CHƯA có dòng cho phiên 2026-09-21** (pipeline sinh dữ liệu chạy 15:05/15:30 ICT; nếu đã quá giờ đó ⇒ pipeline chưa chạy/lỗi) · dòng gần nhất 2026-09-18: mode DEPLOYED · 5 mã · HOLDING 41/60td · 5 names · MTM x1.039
📊 Gate: **0/3 PASS** · không đổi từ 2026-07-31 · chi tiết: `mike/kb/paper_programs_charter/capitulation_shadow.md`
🔍 Nguồn: `data/pt_capitulation_state.json` (+1 nguồn, xem charter)

── **3) AlphaLens Paper (FPT/ACB/MBB/HDB vs VNINDEX)** · 👤 DollarBill · ✅ GREEN
📈 EW **-0.96%** vs VNINDEX -3.24% → **excess +2.28pp** (MTM as-of 2026-09-21) · 📅 phiên ~60/66 (2026-07-01→2026-09-30) · ⏱ nghiệm thu: 2026-09-30 — audit độc lập bởi Taylor
💱 Giao dịch hôm nay: **Không có giao dịch** — buy-and-hold theo thiết kế (equal-weight 25%/tên, không rebalance, giữ tới 2026-09-30)
📊 Gate: **0/3 PASS** · không đổi từ 2026-07-31 · chi tiết: `mike/kb/paper_programs_charter/alphalens.md`
- Vị thế (MTM as-of 2026-09-21, BQ cache close phiên gần nhất):
  • FPT: 70,200 → 66,400 = **-5.41%** (entry 2026-07-01, PE vs PE_MA1Y)
  • ACB: 22,650 → 22,400 = **-1.10%** (entry 2026-07-01, P/B vs Gordon justified-PB)
  • MBB: 25,200 → 20,200 = **-4.11%** (entry 2026-07-01, P/B vs Gordon justified-PB) [giá vào 25,200→21,066 do quyền]
  • HDB: 25,850 → 27,600 = **+6.77%** (entry 2026-07-01, P/B vs Gordon justified-PB)
- VNINDEX 1,860.01 → 1,799.67
🔍 Nguồn: `data/alphalens_paper.json` (+1 nguồn, xem charter)

── **4) Order-book execution shadow (10-level bid-ask)** · 👤 Taylor · ⏳ WATCH
📈 order-book opportunities N=287 · snapshot hợp lệ 267 · 📅 phiên ~26/27 (2026-08-18→2026-09-23) · ⏱ nghiệm thu: Review 2026-09-23 09:30 ICT (gia hạn từ 09-16, xem end_or_trigger) — cần >=20 phiên evidence; chỉ quyết định sang paper A/B hay dừng, không go-live
💱 Giao dịch hôm nay: **n/a theo thiết kế** — Chương trình LOG-ONLY, không phát sinh lệnh riêng; activity đọc từ probe theo child-order opportunity. N=0 nghĩa là chưa có opportunity, không phải policy không có giá trị.
⚠️ Cảnh báo: ERROR telemetry: 20 → 🔴 nghiêm trọng: RÀ SOÁT 2026-08-20 (job Taylor_20260820_012218): 'ERROR telemetry: 20' hôm 08-20 là BUG THẬT trong probe, ĐÃ VÁ (mike/bin/order_book_shadow_probe.py, `_TEST_ACCOUNT_PREFIXES`). Nguyên nhân: 14/20 record 'invalid' là RÁC — 6 selfcheck (capit_participation_cap_selfcheck.py, discretionary_participation_cap_selfcheck.py, extreme_regime_selfcheck.py, expected_volume_pacing_selfcheck.py, t2_settlement_selfcheck.py, tick_retry_selfcheck.py, churn_guard_selfcheck.py) dựng Executor với account='selfcheck-*'/'tickcheck-*' + plan_date sentinel '2099-01-01' mà quên set ORDER_BOOK_TEST_SINK, nên ghi thẳng vào EXEC_DIR thật; probe lọc theo plan_date>=START nên '2099-01-01' luôn lọt qua. Đã sửa probe lọc theo prefix account (không phụ thuộc tên file), N tụt 39→25, ERROR 20→6. 6 record ERROR CÒN LẠI là THẬT nhưng ĐÃ GIẢI THÍCH, không phải bug đang sống: toàn bộ thuộc phiên 2026-08-18 (ngày đầu trial) trước commit 0a684683 (17:32 ICT cùng ngày, 'fix(orderbook-shadow): PHSBroker.get_quote() now sets l2_snapshot for paper-trading') — 6 lệnh 10:46-11:00 ICT chạy TRƯỚC fix nên l2_snapshot rỗng ⇒ fail-open đúng thiết kế (KEEP, reason=invalid_or_stale_snapshot_fail_open, không ảnh hưởng hành vi đặt lệnh). Toàn bộ 19 record 2026-08-19 trở đi valid=True — không tái diễn từ đó. 6 file selfcheck có cleanup gap (glob chỉ xoá exec_{TAG}_*, không xoá orderbook_shadow_{TAG}_*) — TODO thứ yếu, chưa vá (rủi ro thấp: rác đĩa, không ảnh hưởng số liệu nữa vì probe đã lọc theo account). 12 file rác đã dọn khỏi data/execution_logs/.
📊 Gate: **0/4 PASS** · không đổi từ 2026-08-17 · chi tiết: `mike/kb/paper_programs_charter/order_book_execution_shadow.md`
order-book observations N=287 · valid=267 · sessions=21
policy KEEP=286 REDUCE=1 DEFER=0
latency snapshot→order median=70ms
fill-linked children=256/287 · fill-rate=89.2%
time-to-first-fill median=19.606s · fill-vs-limit slippage median=0.0bps
outcome coverage 1m=4/239 · 5m=4/239 · 15m=2/239
adverse-selection median 1m=+18.4bps · 5m=+20.6bps · 15m=+45.7bps
ERROR telemetry: 20
scope v1: spread + displayed depth + adverse selection; resilience EXCLUDED (60s cadence).
🔍 Nguồn: `data/execution_logs/orderbook_shadow_<account>_<date>.jsonl — schema orderbook_execution_v1: trace_id parent/child, baseline, KEEP/REDUCE/DEFER, latency và snapshot immutable` (+2 nguồn, xem charter)

── **5) ORB intraday VN30F (ring-fenced)** · 👤 Taylor · ⏳ WATCH
📈 asof 2026-09-21 | 71 phiên từ 2026-06-09 | NAV 1.074B (+7.37%) | WR 56.3% | phiên cuối +1.26% (sig -1) | Sharpe report 1.75 (mẫu nhỏ — đọc thận trọng) · 📅 phiên ~76 từ 2026-06-09 · ⏱ nghiệm thu: ≥60 phiên GỒM chop/bear → re-eval quant-skeptic (điều kiện REGIME, không có deadline lịch)
💱 Giao dịch hôm nay: **n/a — `data/orb_pt_log.csv` CHƯA có dòng cho phiên 2026-09-22** (pipeline sinh dữ liệu chạy 15:05/15:30 ICT; nếu đã quá giờ đó ⇒ pipeline chưa chạy/lỗi) · dòng gần nhất 2026-09-21: sig -1 · vào 1,959.0 → ra 1,934.0 · net +1.26% (1 lượt/phiên theo thiết kế ORB)
📊 Gate: **0/4 PASS** · không đổi từ 2026-07-31 · chi tiết: `mike/kb/paper_programs_charter/orb_intraday.md`
🔍 Nguồn: `data/orb_pt_status.json` (+1 nguồn, xem charter)

── **6) Engine-room OOS panel (V11/V12/V4 vs V2.3-book vs VNINDEX)** · 👤 Taylor · ✅ GREEN
📈 V2.3-book -2.38% vs VNINDEX +0.95% (cửa sổ chung, NAV rebase 50B) · 📅 phiên ~74 từ 2026-06-11 · ⏱ nghiệm thu: 2026-12-01 (~6 tháng OOS trên cửa sổ chung từ 2026-06-11)
💱 Giao dịch hôm nay: **n/a theo thiết kế** — panel so sánh NAV của 5 sổ MÔ PHỎNG (V11/V12/V4/V23/VNI_BH) — panel không giữ nhật ký lệnh tách bạch; giao dịch THẬT của sổ production V2.3 nằm ở báo cáo EOD live, không phải ở đây
📊 Gate: **0/2 PASS** · không đổi từ 2026-07-31 · chi tiết: `mike/kb/paper_programs_charter/engine_room_oos.md`
Cửa sổ so sánh CHUNG 2026-06-11 → 2026-09-18 (69 phiên), NAV rebase 50B tại đầu cửa sổ (không phải NAV thô từ inception gốc):
  V11       +1.96%  (NAV 50.98B)
  V12       +0.28%  (NAV 50.14B)
  V4_DT5G   +2.01%  (NAV 51.00B)
  V23       -2.38%  (NAV 48.81B)
  VNI_BH    +0.95%  (NAV 50.47B)
🔍 Nguồn: `data/papertrade_compare5.csv (papertrade_compare.py)` (+1 nguồn, xem charter)

── **7) P2 — mẫu số pacing theo KL KỲ VỌNG (expected-volume pacing)** · 👤 Taylor · ✅ GREEN
📈 2 phiên có lệnh ADV20-paced · **order-day N=2** · 76 slice quan sát · 📅 phiên ~27/22 (2026-08-17→2026-09-15) · ⏱ nghiệm thu: Bắt đầu 2026-08-17 · checkpoint LẶP LẠI ~4 tuần (09-15✔, 10-13, 11-10, ...) tới khi ≥25 order-day HOẶC safety_ceiling 2027-02-17 (xem end_or_trigger). CHECKPOINT 2026-09-16: gate an toàn (1) và gate LIVE-không-đổi (2) = PASS (đo thật, recompute độc lập + 2 selfcheck xanh); gate 3/4 THIẾU MẪU N=2/25 order-day, gate 5 chưa đủ điều kiện. Nhịp thực tế ~1 order-day/15 phiên ⇒ nếu giữ nhịp này cần ~370 phiên để đạt 25 — nhiều khả năng chạm safety_ceiling trước. Không flip gate, không tạo lệnh giả. Checkpoint kế: 2026-10-13.
💱 Giao dịch hôm nay: **n/a theo thiết kế** — chương trình LOG-ONLY: không phát sinh lệnh riêng nào (P2 chưa được phép đổi hành vi trên live). Hoạt động trong ngày đọc ở dòng cuối output probe ('hôm nay: N order-day · M slice')
📊 Gate: **2/5 PASS** · không đổi từ 2026-09-16 · chi tiết: `mike/kb/paper_programs_charter/expvol_pacing.md`
2 phiên có lệnh ADV20-paced · **order-day N=2** · 76 slice quan sát
bind=ceil 76/76 (100.0%) — chỉ nhóm này P2 mới nới được
delta allowance khi bind=ceil (cp): trung vị +28 · tb +58 · max +418 · 75/76 slice có delta>0
an toàn: %tape tối đa nếu P2 khớp trọn allowance = 50.0% (trần 50%) · vi phạm clamp **0** · EXPVOL_SHADOW_ERR **0**
hôm nay (2026-09-22): 0 order-day · 0 slice · bind=ceil 0
🔍 Nguồn: `data/execution_logs/exec_{SpaceX,ZaloPay,RocketX}_*_journal.csv — event EXPVOL_SHADOW / EXPVOL_SHADOW_ERR` (+3 nguồn, xem charter)

───
📎 *Badge: 🔴 RED = probe lỗi / cảnh báo chưa được giải thích / có gate FAIL · ⏳ WATCH = có cảnh báo đã giải thích hoặc thiếu khai báo giao dịch · ✅ GREEN = còn lại. Mục đích + phương pháp + tiêu chí nghiệm thu đầy đủ: `mike/kb/paper_programs_charter/<id>.md` (tự sinh từ registry). Mục hoàn tất hoặc thuộc vận hành được giữ trong registry nhưng không lặp ở đây. Gate chỉ in đầy đủ khi có thay đổi — trạng thái so sánh lưu ở `data/paper_report_state.json`.*
⚠️ *PAPER TRADING — không phải tiền thật; toàn bộ số liệu là mô phỏng/quan sát, không phải khuyến nghị đầu tư. Số không trace được về file nguồn = n/a.*
