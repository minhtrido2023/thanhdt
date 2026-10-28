📋 **Paper Programs Daily Report — 2026-10-23**
Render 07:30 ICT · registry v3 · 7 paper-trial đang theo dõi · *vintage dữ liệu xem `asof`/nguồn từng mục (BQ chưa có close phiên T lúc 16:00)*
ℹ️ **Đã chuyển khỏi báo cáo ngày**: EXTREME-regime gate · Fill-timing window (BUY 10:45-11:15 / SELL 09:15-09:45) · Vol-scale buy chase-cap (patch#3) · custom30V yield_floor — nhãn quan sát (Option C) · BAL signal shadow-track — hiệu suất gần đây (case VPI) · Rating 8L G1 (≥4→≤3) — tích luỹ OOS đi tới. Dữ liệu/cron không bị xóa; xem registry để biết lý do và mốc review.
🔴 **CẦN CHÚ Ý NGAY** (1): #5 ORB intraday VN30F (ring-fenced)

**TỔNG QUAN** — trạng thái · paper-trial · chỉ số mới nhất · giao dịch hôm nay:
⏳ **1) DC-book NEUTRAL idle-cash Waterfall** — NAV 999,782,787đ · lũy kế -0.02% · phiên gần nhất +0.28% (as-of 2026-10-22) | 💱 **n/a — `data/dc_book_waterfall_paper_nav.csv` CHƯA có dòng cho phiên…
⏳ **2) Capitulation-sleeve shadow (DT5G × 8L washout)** — asof 2026-10-21 | mode CASH | NAV 51.16B | tier None | entry 2026-07-20 | basket 0 mã | 💱 **n/a — `data/pt_capitulation_logs.csv` CHƯA có dòng cho phiên 2026-1…
✅ **3) AlphaLens Paper (FPT/ACB/MBB/HDB vs VNINDEX)** — EW **-2.13%** vs VNINDEX -5.34% → **excess +3.21pp** (MTM as-of 2026-10-22, quy ước `terp`) ·… | 💱 **Không có giao dịch** — buy-and-hold theo thiết kế (equal-weight 25%…
⏳ **4) Order-book execution shadow (10-level bid-ask)** — order-book opportunities N=841 · snapshot hợp lệ 738 | 💱 **n/a theo thiết kế** — Chương trình LOG-ONLY, không phát sinh lệnh r…
🔴 **5) ORB intraday VN30F (ring-fenced)** — asof 2026-10-22 | 92 phiên từ 2026-06-09 | NAV 1.051B (+5.10%) | WR 54.3% | phiên cuối -0.03%… | 💱 **n/a — `data/orb_pt_log.csv` CHƯA có dòng cho phiên 2026-10-23** (pi…
✅ **6) Engine-room OOS panel (V11/V12/V4 vs V2.3-book vs VNINDEX)** — V2.3-book -6.16% vs VNINDEX -3.33% (cửa sổ chung, NAV rebase 50B) | 💱 **n/a theo thiết kế** — panel so sánh NAV của 5 sổ MÔ PHỎNG (V11/V12/…
✅ **7) P2 — mẫu số pacing theo KL KỲ VỌNG (expected-volume pacing)** — 2 phiên có lệnh ADV20-paced · **order-day N=2** · 76 slice quan sát | 💱 **n/a theo thiết kế** — chương trình LOG-ONLY: không phát sinh lệnh r…

── **1) DC-book NEUTRAL idle-cash Waterfall** · 👤 Taylor · ⏳ WATCH
📈 NAV 999,782,787đ · lũy kế -0.02% · phiên gần nhất +0.28% (as-of 2026-10-22) · 📅 phiên ~80 từ 2026-07-06 · ⏱ nghiệm thu: event-anchored (user 2026-10-09): state rời NEUTRAL HOẶC trigger park quay lại · không mốc ngày
💱 Giao dịch hôm nay: **n/a — `data/dc_book_waterfall_paper_nav.csv` CHƯA có dòng cho phiên 2026-10-23** (pipeline sinh dữ liệu chạy 15:05/15:30 ICT; nếu đã quá giờ đó ⇒ pipeline chưa chạy/lỗi) · dòng gần nhất 2026-10-22: turnover 0.00% · rebalanced=False · deployed=True · sleeve +0.28%
📊 Gate: **0/3 PASS** · không đổi từ 2026-07-31 · chi tiết: `mike/kb/paper_programs_charter/dc_waterfall.md`
[cpi_vn] CPI COVERAGE GAP: 4 month(s) 2026-09..2026-12 have NO real source. Tier 1 (live NSO) ends 2026-06; Tier 1.5 (FiinPro snapshot 2026-09-14, trial ended 2026-09-28 -> FROZEN) ends 2026-08. Those months are Tier 2's forward-fill of its last anchor, NOT a print. FIX = refresh NSO_CPI_YOY_REAL from the GSO monthly release; refreshing the FiinPro file is impossible.
### 🪜 DC-book NEUTRAL Waterfall — Paper Sleeve (v2)
*Tiền rảnh NEUTRAL: BAL/LAG → DC book (double-confirm, liq≥3B) → custom30V, **continuous-residual** | cap gộp 0.15/tên · rebal q2m5 | flag `dc_book_waterfall_enabled`=ON (chỉ paper `main`) | as-of 2026-10-22 00:00:00*

- Trạng thái hôm nay: NEUTRAL → waterfall chạy LIÊN TỤC trên phần tiền dư (BAL/LAG có deal hôm nay — v2 KHÔNG tắt sleeve, chỉ phần dư nhỏ lại)
- Nhịp rebal: giữ nguyên, trọng số drift (q2m5 — chưa tới kỳ)
- DC book (7): ACB, FPT, HAH, MBB, PVT, SSI, TCB (leg 0.0%) | custom30V 0.0% | cash 0.0%
- Due-diligence (informational, không tham gia chọn mã):
  DD ACB [DC] (data 2026-10-22): thanh khoản OK (ADV3T 161.24 tỷ/phiên) · ⚠ universe_pit: n/a (không đọc đư
… (cắt bớt, xem nguồn để đủ; exit=0)
_(lược 3 dòng phụ lục của probe — xem nguồn nếu cần)_
🔍 Nguồn: `data/dc_book_waterfall_paper_state.json` (+1 nguồn, xem charter)

── **2) Capitulation-sleeve shadow (DT5G × 8L washout)** · 👤 Taylor · ⏳ WATCH
📈 asof 2026-10-21 | mode CASH | NAV 51.16B | tier None | entry 2026-07-20 | basket 0 mã · 📅 phiên ~98 từ 2026-06-10 · ⏱ nghiệm thu: EVENT-DRIVEN: sau sự kiện washout THẬT đầu tiên (chưa có deadline lịch)
💱 Giao dịch hôm nay: **n/a — `data/pt_capitulation_logs.csv` CHƯA có dòng cho phiên 2026-10-22** (pipeline sinh dữ liệu chạy 15:05/15:30 ICT; nếu đã quá giờ đó ⇒ pipeline chưa chạy/lỗi) · dòng gần nhất 2026-10-21: mode CASH · 0 mã · dormant (oversold 2% < 30%)
📊 Gate: **0/3 PASS** · không đổi từ 2026-07-31 · chi tiết: `mike/kb/paper_programs_charter/capitulation_shadow.md`
🔍 Nguồn: `data/pt_capitulation_state.json` (+1 nguồn, xem charter)

── **3) AlphaLens Paper (FPT/ACB/MBB/HDB vs VNINDEX)** · 👤 DollarBill · ✅ GREEN
📈 EW **-2.13%** vs VNINDEX -5.34% → **excess +3.21pp** (MTM as-of 2026-10-22, quy ước `terp`) · accrue-only: excess +2.18pp · 📅 phiên ~83/66 (2026-07-01→2026-09-30) · ⏱ nghiệm thu: ✅ 3/3 gate PASS (audit Taylor 2026-10-01, quant-skeptic CONFIRMED/high): excess +3,82pp terp / +2,80pp accrue-only (vào 07-01 close: +2,01 / +1,00pp), 0 vi phạm exit. ⚠️ PASS THEO CHỮ ≠ BẰNG CHỨNG EDGE: N = 1 cửa sổ 3 tháng × 4 tên chọn TAY (không ghi lại bao nhiêu mã qua lens ngày 06-30) ⇒ kiểm tra 4 lựa chọn này, KHÔNG kiểm tra lens. KHUYẾN NGHỊ (chờ user): (A) ĐÓNG chương trình, không wire live; nếu muốn dùng lens ⇒ mở R&D backtest PIT walk-forward IS 2014-19/OOS 2020+, DSR/PBO, đo GIA TĂNG so với tilt giá trị custom30V/8L đang chạy + quant-skeptic. (B) gia hạn paper thêm 1 quý — giá trị thấp (+1 quan sát).
💱 Giao dịch hôm nay: **Không có giao dịch** — buy-and-hold theo thiết kế (equal-weight 25%/tên, không rebalance, giữ tới 2026-09-30)
📊 Gate: **3/3 PASS** · không đổi từ 2026-10-02 · chi tiết: `mike/kb/paper_programs_charter/alphalens.md`
- Vị thế (MTM as-of 2026-10-22, BQ cache close phiên gần nhất):
  • FPT: 70,200 → 57,400 = **-10.06%** (entry 2026-07-01, PE vs PE_MA1Y) [giá vào 70,200→63,820 do quyền]
  • ACB: 22,650 → 20,500 = **-9.49%** (entry 2026-07-01, P/B vs Gordon justified-PB)
  • MBB: 25,200 → 19,900 = **-1.39%** (entry 2026-07-01, P/B vs Gordon justified-PB) [giá vào 25,200→20,180 do quyền] · nếu BỎ quyền (accrue-only): vào 21,066 → **-5.54%**
  • HDB: 25,850 → 22,350 = **+12.42%** (entry 2026-07-01, P/B vs Gordon justified-PB) [giá vào 25,850→19,880 do quyền]
- VNINDEX 1,860.01 → 1,760.63
- ⚖️ **Hai quy ước quyền mua** (MBB có đợt quyền mua trong cửa sổ). Dẫn dắt ở trên = `terp` (THỰC HIỆN 100% quyền — chỉ đạo user 2026-09-23). Quy ước cũ `accrue_only` (giả định BỎ quyền) cho: EW **-3.17%** vs VNINDEX -5.34% → **excess +2.18pp** (chênh +1.04pp so với số dẫn dắt).
🔍 Nguồn: `data/alphalens_paper.json` (+1 nguồn, xem charter)

── **4) Order-book execution shadow (10-level bid-ask)** · 👤 Taylor · ⏳ WATCH
📈 order-book opportunities N=841 · snapshot hợp lệ 738 · 📅 phiên ~49/42 (2026-08-18→2026-10-14) · ⏱ nghiệm thu: [ĐÓNG 2026-10-14 — user duyệt đóng sớm, decided_by=user, theo khuyến nghị checkpoint job Taylor_20261014_020345] CHECKPOINT 2026-10-14 (job Taylor_20261014_020345, user duyệt checkpoint 10-14): tầng REAL 160 hợp lệ/233 thô (14 phiên) ⇒ tiêu chí N≥30 ĐẠT, KHÔNG gia hạn. Gate 1 PASS · gate 2 PASS · gate 3 PENDING (so sánh OOS đã chạy = NULL, thiếu lực: 14 lệnh REDUCE/DEFER chỉ là 10 cụm phiên×mã / 4 phiên) · gate 4 PENDING (chưa kích hoạt). 73 bản ghi REAL 'ERROR telemetry' = 73/73 source_age>5s do SỔ ĐỨNG YÊN ở mã mỏng (không phải feed hỏng), fail-open đúng thiết kế, nhưng làm mẫu hợp lệ lệch về lệnh PARK mega-cap. KHÔNG đề xuất đổi child size/lịch HYBRID. Dự kiến 10-21: đóng chương trình mẹ với kết luận 'telemetry dùng được, policy spread_depth_v2 không có bằng chứng phân biệt'; nhánh opening_cycle (mốc 2027-01-25) giữ nguyên. | TRƯỚC ĐÓ: CHECKPOINT 2026-09-23 ĐÃ QUYẾT: user chọn phương án (A) SỬA rồi CHẠY LẠI (job Taylor_20260923_051148, decided_by=user). Đã triển khai xong: tách 2 tầng PROBE (churn tổng hợp, N=295, không cần thêm)/REAL (lệnh thật, N=26 thô) + đọc thêm probe_ticks_*.csv làm nguồn markout (coverage hậu kiểm 1,6%→93,2%) + ngưỡng spread_depth_v2 phân biệt được 44% khác-baseline ở tầng REAL (trước đó 0% vì gộp lẫn 2 tầng). Cửa sổ mới 2026-10-21, tiêu chí = N≥30 quan sát hợp lệ ở TẦNG REAL (không phải số phiên) — hiện đang tích luỹ, chưa đạt. Nếu tới 10-21 vẫn <30 ⇒ đó là câu trả lời về tần suất cơ hội (~1,8 quan sát hợp lệ/phiên có lệnh thật), đóng chương trình, KHÔNG gia hạn lần 4. Dù kết quả gì cũng KHÔNG go-live (đúng phạm vi đã chốt).
💱 Giao dịch hôm nay: **n/a theo thiết kế** — Chương trình LOG-ONLY, không phát sinh lệnh riêng; activity đọc từ probe theo child-order opportunity. N=0 nghĩa là chưa có opportunity, không phải policy không có giá trị.
⚠️ Cảnh báo: ERROR telemetry: 103 → 🔴 nghiêm trọng: CẬP NHẬT 2026-10-14 (job Taylor_20261014_020345): 'ERROR telemetry: 79' = 73 REAL + 6 PROBE. 73 REAL KHÔNG phải lỗi telemetry: 73/73 là source_age_ms>5s vì SỔ ĐỨNG YÊN ở mã mỏng/đầu khung giờ (TV1/SCL/CSV/VPI), cấu trúc sổ đầy đủ, policy fail-open về KEEP đúng thiết kế, không ảnh hưởng đặt lệnh. Hệ quả cần nhớ khi đọc số: mẫu hợp lệ lệch về lệnh PARK mega-cap (BAL/LAG bị loại 59% vs PARK 26%). Chi tiết agents/Taylor/research/orderbook_shadow_checkpoint_20261014/README.md. | LỊCH SỬ: RÀ SOÁT 2026-08-20 (job Taylor_20260820_012218): 'ERROR telemetry: 20' hôm 08-20 là BUG THẬT trong probe, ĐÃ VÁ (mike/bin/order_book_shadow_probe.py, `_TEST_ACCOUNT_PREFIXES`). Nguyên nhân: 14/20 record 'invalid' là RÁC — 6 selfcheck (capit_participation_cap_selfcheck.py, discretionary_participation_cap_selfcheck.py, extreme_regime_selfcheck.py, expected_volume_pacing_selfcheck.py, t2_settlement_selfcheck.py, tick_retry_selfcheck.py, churn_guard_selfcheck.py) dựng Executor với account='selfcheck-*'/'tickcheck-*' + plan_date sentinel '2099-01-01' mà quên set ORDER_BOOK_TEST_SINK, nên ghi thẳng vào EXEC_DIR thật; probe lọc theo plan_date>=START nên '2099-01-01' luôn lọt qua. Đã sửa probe lọc theo prefix account (không phụ thuộc tên file), N tụt 39→25, ERROR 20→6. 6 record ERROR CÒN LẠI là THẬT nhưng ĐÃ GIẢI THÍCH, không phải bug đang sống: toàn bộ thuộc phiên 2026-08-18 (ngày đầu trial) trước commit 0a684683 (17:32 ICT cùng ngày, 'fix(orderbook-shadow): PHSBroker.get_quote() now sets l2_snapshot for paper-trading') — 6 lệnh 10:46-11:00 ICT chạy TRƯỚC fix nên l2_snapshot rỗng ⇒ fail-open đúng thiết kế (KEEP, reason=invalid_or_stale_snapshot_fail_open, không ảnh hưởng hành vi đặt lệnh). Toàn bộ 19 record 2026-08-19 trở đi valid=True — không tái diễn từ đó. 6 file selfcheck có cleanup gap (glob chỉ xoá exec_{TAG}_*, không xoá orderbook_shadow_{TAG}_*) — TODO thứ yếu, chưa vá (rủi ro thấp: rác đĩa, không ảnh hưởng số liệu nữa vì probe đã lọc theo account). 12 file rác đã dọn khỏi data/execution_logs/.
📊 Gate: **2/4 PASS** · không đổi từ 2026-10-15 · chi tiết: `mike/kb/paper_programs_charter/order_book_execution_shadow.md`
order-book observations N=841 · valid=738 · sessions=44
  [PROBE] N=567 · policy KEEP=567 REDUCE=0 DEFER=0 · khác-baseline=0.0% · touch_depth_ratio median=768.0x
  [REAL] N=274 · policy KEEP=254 REDUCE=19 DEFER=1 · khác-baseline=7.3% · touch_depth_ratio median=20.8x
latency snapshot→order median=80.0ms
fill-linked children=754/841 · fill-rate=89.7%
time-to-first-fill median=19.755499999999998s · fill-vs-limit slippage median=0.0bps
outcome coverage 1m=591/658 · 5m=591/658 · 15m=513/658 · basis mid=155 last=503 none=0
adverse-selection median 1m=+9.1bps · 5m=+8.7bps · 15m=-0.0bps
markout artifact: /home/trido/thanhdt/WorkingClaude/data/execution_logs/orderbook_markout.jsonl (658 bản ghi, schema orderbook_markout_v1)
ERROR telemetry: 103
scope v1: spread + displayed depth + adverse selection; resilience EXCLUDED (60s cadence).
🔍 Nguồn: `data/execution_logs/orderbook_shadow_<account>_<date>.jsonl — schema orderbook_execution_v1: trace_id parent/child, baseline, KEEP/REDUCE/DEFER, latency và snapshot immutable` (+5 nguồn, xem charter)

── **5) ORB intraday VN30F (ring-fenced)** · 👤 Taylor · 🔴 RED
📈 asof 2026-10-22 | 92 phiên từ 2026-06-09 | NAV 1.051B (+5.10%) | WR 54.3% | phiên cuối -0.03% (sig +1) | Sharpe report 1.04 (mẫu nhỏ — đọc thận trọng) · 📅 phiên ~99 từ 2026-06-09 · ⏱ nghiệm thu: QUYẾT ĐỊNH B (user, 2026-09-25, decided_by=user): TẠM DỪNG R&D hướng "chờ tích lũy N"; cron paper 15:30 + orb_drift_monitor 15:50 VẪN CHẠY (dữ liệu vẫn tích lũy, chi phí ~0). Mở lại CHỈ khi có lý do mới VỀ CHẤT: cơ chế kinh tế thật cho edge dấu-OR trên VN30F, HOẶC biến thể effect size ≥×1,3–1,9 (SR/obs ≥0,075–0,107). Không phải "cùng edge, N lớn hơn". Lý do: power 80% cần 2.510 phiên (thiếu ~1.381 ≈5,5 năm); DSR(N=20)≥0,95 cần 4.075 phiên (16,2 năm) > cả đời hợp đồng VN30F1M (9,13 năm, ở đó DSR chỉ 0,779). Gate #2 = FAIL (giữ nguyên), gate #3 (hạ tầng phái sinh) = hard blocker độc lập. Chương trình KHÔNG xoá, cron KHÔNG dừng.
💱 Giao dịch hôm nay: **n/a — `data/orb_pt_log.csv` CHƯA có dòng cho phiên 2026-10-23** (pipeline sinh dữ liệu chạy 15:05/15:30 ICT; nếu đã quá giờ đó ⇒ pipeline chưa chạy/lỗi) · dòng gần nhất 2026-10-22: sig +1 · vào 1,892.2 → ra 1,892.0 · net -0.03% (1 lượt/phiên theo thiết kế ORB)
📊 Gate: **0/4 PASS** · ❌ 1 FAIL · không đổi từ 2026-09-25 · chi tiết: `mike/kb/paper_programs_charter/orb_intraday.md`
🔍 Nguồn: `data/orb_pt_status.json` (+1 nguồn, xem charter)

── **6) Engine-room OOS panel (V11/V12/V4 vs V2.3-book vs VNINDEX)** · 👤 Taylor · ✅ GREEN
📈 V2.3-book -6.16% vs VNINDEX -3.33% (cửa sổ chung, NAV rebase 50B) · 📅 phiên ~97 từ 2026-06-11 · ⏱ nghiệm thu: 2026-12-01 (~6 tháng OOS trên cửa sổ chung từ 2026-06-11)
💱 Giao dịch hôm nay: **n/a theo thiết kế** — panel so sánh NAV của 5 sổ MÔ PHỎNG (V11/V12/V4/V23/VNI_BH) — panel không giữ nhật ký lệnh tách bạch; giao dịch THẬT của sổ production V2.3 nằm ở báo cáo EOD live, không phải ở đây
📊 Gate: **0/2 PASS** · không đổi từ 2026-09-26 · chi tiết: `mike/kb/paper_programs_charter/engine_room_oos.md`
Cửa sổ so sánh CHUNG 2026-06-11 → 2026-10-21 (92 phiên), NAV rebase 50B tại đầu cửa sổ (không phải NAV thô từ inception gốc):
  V11       -3.42%  (NAV 48.29B)
  V12       -2.14%  (NAV 48.93B)
  V4_DT5G   -1.92%  (NAV 49.04B)
  V23       -6.16%  (NAV 46.92B)
  VNI_BH    -3.33%  (NAV 48.33B)
🔍 Nguồn: `data/papertrade_compare5.csv (papertrade_compare.py)` (+1 nguồn, xem charter)

── **7) P2 — mẫu số pacing theo KL KỲ VỌNG (expected-volume pacing)** · 👤 Taylor · ✅ GREEN
📈 2 phiên có lệnh ADV20-paced · **order-day N=2** · 76 slice quan sát · 📅 phiên ~50/62 (2026-08-17→2026-11-10) · ⏱ nghiệm thu: Bắt đầu 2026-08-17 · checkpoint LẶP LẠI ~4 tuần (09-15✔, 09-23✔ ngoài lịch, 10-13✔ làm 10-14, 11-10, 12-08, ...) tới khi ≥25 order-day HOẶC safety_ceiling 2027-02-17 (xem end_or_trigger). CHECKPOINT 2026-10-14: gate an toàn (1) và gate LIVE-không-đổi (2) = PASS (đo lại thật: recompute độc lập 0 vi phạm, %tape tối đa 0,5000; 2 selfcheck rc=0 ở 3 múi giờ; `_expvol_active` tính lại từ cấu hình thật); gate 3/4 THIẾU MẪU N=2/25 KHÔNG ĐỔI từ 09-14, gate 5 chưa đủ điều kiện. Vắng mặt verify bằng 2 artifact: 20 journal live sau 09-14 chỉ có BAL/LAG/PARK, và quét plan từ 08-17 ra đúng 2 plan có lệnh mua CAPIT/DISCRETIONARY_SPECIAL = 2 order-day đã log. Nhịp đo 19 phiên/order-day (38 phiên → 2) ⇒ ~85 phiên còn lại tới ceiling chỉ sinh thêm ~4-5 order-day (tổng ~6-7/25) ⇒ GẦN NHƯ CHẮC ĐÓNG Ở CEILING vì 'thiếu cơ hội', KHÔNG PHẢI NO-GO trên edge — trừ khi có đợt gom CAPIT/DISC mới (nhịp là theo ĐỢT, không đều). Không flip gate, không tạo lệnh giả. Checkpoint kế: 2026-11-10. LƯU Ý CƠ CHẾ: `end` dời 10-13→11-10 theo lịch lặp đã duyệt 09-06 — `end` quá hạn là thứ khiến paper_checkpoint_escalation.sh escalate lại mỗi chu kỳ.
💱 Giao dịch hôm nay: **n/a theo thiết kế** — chương trình LOG-ONLY: không phát sinh lệnh riêng nào (P2 chưa được phép đổi hành vi trên live). Hoạt động trong ngày đọc ở dòng cuối output probe ('hôm nay: N order-day · M slice')
📊 Gate: **2/5 PASS** · không đổi từ 2026-09-16 · chi tiết: `mike/kb/paper_programs_charter/expvol_pacing.md`
2 phiên có lệnh ADV20-paced · **order-day N=2** · 76 slice quan sát
bind=ceil 76/76 (100.0%) — chỉ nhóm này P2 mới nới được
delta allowance khi bind=ceil (cp): trung vị +28 · tb +58 · max +418 · 75/76 slice có delta>0
an toàn: %tape tối đa nếu P2 khớp trọn allowance = 50.0% (trần 50%) · vi phạm clamp **0** · EXPVOL_SHADOW_ERR **0**
hôm nay (2026-10-23): 0 order-day · 0 slice · bind=ceil 0
🔍 Nguồn: `data/execution_logs/exec_{SpaceX,ZaloPay,RocketX}_*_journal.csv — event EXPVOL_SHADOW / EXPVOL_SHADOW_ERR` (+3 nguồn, xem charter)

───
📎 *Badge: 🔴 RED = probe lỗi / cảnh báo chưa được giải thích / có gate FAIL · ⏳ WATCH = có cảnh báo đã giải thích hoặc thiếu khai báo giao dịch · ✅ GREEN = còn lại. Mục đích + phương pháp + tiêu chí nghiệm thu đầy đủ: `mike/kb/paper_programs_charter/<id>.md` (tự sinh từ registry). Mục hoàn tất hoặc thuộc vận hành được giữ trong registry nhưng không lặp ở đây. Gate chỉ in đầy đủ khi có thay đổi — trạng thái so sánh lưu ở `data/paper_report_state.json`.*
⚠️ *PAPER TRADING — không phải tiền thật; toàn bộ số liệu là mô phỏng/quan sát, không phải khuyến nghị đầu tư. Số không trace được về file nguồn = n/a.*
