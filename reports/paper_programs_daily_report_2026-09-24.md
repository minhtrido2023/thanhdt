📋 **Paper Programs Daily Report — 2026-09-24**
Render 07:30 ICT · registry v3 · 7 paper-trial đang theo dõi · *vintage dữ liệu xem `asof`/nguồn từng mục (BQ chưa có close phiên T lúc 16:00)*
ℹ️ **Đã chuyển khỏi báo cáo ngày**: EXTREME-regime gate · Fill-timing window (BUY 10:45-11:15 / SELL 09:15-09:45) · Vol-scale buy chase-cap (patch#3) · custom30V yield_floor — nhãn quan sát (Option C) · BAL signal shadow-track — hiệu suất gần đây (case VPI). Dữ liệu/cron không bị xóa; xem registry để biết lý do và mốc review.
⏳ **Theo dõi** (4): #1 DC-book NEUTRAL idle-cash Waterfall · #2 Capitulation-sleeve shadow (DT5G × 8L washout) · #4 Order-book execution shadow (10-level bid-ask) · #5 ORB intraday VN30F (ring-fenced)

**TỔNG QUAN** — trạng thái · paper-trial · chỉ số mới nhất · giao dịch hôm nay:
⏳ **1) DC-book NEUTRAL idle-cash Waterfall** — NAV 1,015,603,997đ · lũy kế +1.56% · phiên gần nhất -0.52% (as-of 2026-09-23) | 💱 **n/a — `data/dc_book_waterfall_paper_nav.csv` CHƯA có dòng cho phiên…
⏳ **2) Capitulation-sleeve shadow (DT5G × 8L washout)** — asof 2026-09-22 | mode DEPLOYED | NAV 52.65B | tier NONCRISIS size=0.75 | entry 2026-07-20 | b… | 💱 **n/a — `data/pt_capitulation_logs.csv` CHƯA có dòng cho phiên 2026-0…
✅ **3) AlphaLens Paper (FPT/ACB/MBB/HDB vs VNINDEX)** — EW **≥ +1.81%** vs VNINDEX -3.14% → **excess ≥ +4.95pp** (MTM as-of 2026-09-23, quy ước `terp`… | 💱 **Không có giao dịch** — buy-and-hold theo thiết kế (equal-weight 25%…
⏳ **4) Order-book execution shadow (10-level bid-ask)** — order-book opportunities N=321 · snapshot hợp lệ 298 | 💱 **n/a theo thiết kế** — Chương trình LOG-ONLY, không phát sinh lệnh r…
⏳ **5) ORB intraday VN30F (ring-fenced)** — asof 2026-09-23 | 73 phiên từ 2026-06-09 | NAV 1.062B (+6.18%) | WR 54.8% | phiên cuối -0.30%… | 💱 **n/a — `data/orb_pt_log.csv` CHƯA có dòng cho phiên 2026-09-24** (pi…
✅ **6) Engine-room OOS panel (V11/V12/V4 vs V2.3-book vs VNINDEX)** — V2.3-book -2.22% vs VNINDEX +1.02% (cửa sổ chung, NAV rebase 50B) | 💱 **n/a theo thiết kế** — panel so sánh NAV của 5 sổ MÔ PHỎNG (V11/V12/…
✅ **7) P2 — mẫu số pacing theo KL KỲ VỌNG (expected-volume pacing)** — 2 phiên có lệnh ADV20-paced · **order-day N=2** · 76 slice quan sát | 💱 **n/a theo thiết kế** — chương trình LOG-ONLY: không phát sinh lệnh r…

── **1) DC-book NEUTRAL idle-cash Waterfall** · 👤 Taylor · ⏳ WATCH
📈 NAV 1,015,603,997đ · lũy kế +1.56% · phiên gần nhất -0.52% (as-of 2026-09-23) · 📅 phiên ~59 từ 2026-07-06 · ⏱ nghiệm thu: event-anchored: chu kỳ reverse-unwind ĐẦU TIÊN + settle 4-6 tuần · trần 2026-10-06
💱 Giao dịch hôm nay: **n/a — `data/dc_book_waterfall_paper_nav.csv` CHƯA có dòng cho phiên 2026-09-24** (pipeline sinh dữ liệu chạy 15:05/15:30 ICT; nếu đã quá giờ đó ⇒ pipeline chưa chạy/lỗi) · dòng gần nhất 2026-09-23: turnover 0.00% · rebalanced=False · deployed=True · sleeve -0.52%
📊 Gate: **0/3 PASS** · không đổi từ 2026-07-31 · chi tiết: `mike/kb/paper_programs_charter/dc_waterfall.md`
### 🪜 DC-book NEUTRAL Waterfall — Paper Sleeve (v2)
*Tiền rảnh NEUTRAL: BAL/LAG → DC book (double-confirm, liq≥3B) → custom30V, **continuous-residual** | cap gộp 0.15/tên · rebal q2m5 | flag `dc_book_waterfall_enabled`=ON (chỉ paper `main`) | as-of 2026-09-23 00:00:00*

- Trạng thái hôm nay: NEUTRAL → waterfall chạy LIÊN TỤC trên phần tiền dư (BAL/LAG rỗng)
- Nhịp rebal: giữ nguyên, trọng số drift (q2m5 — chưa tới kỳ)
- DC book (7): ACB, FPT, HAH, MBB, PVT, SSI, TCB (leg 0.0%) | custom30V 0.0% | cash 0.0%
- Due-diligence (informational, không tham gia chọn mã):
  DD ACB [DC] (data 2026-09-23): thanh khoản OK (ADV3T 222.75 tỷ/phiên) · ⚠ universe_pit: n/a (không đọc được)
  FA: ROE5Y 23.0% · ROE_Min3Y 17.6% · FSCORE 1 · D/E 9.75 · PE 8.07
  DD FPT [DC] (data 2026-09-23): thanh khoản OK (ADV3T 409.98 tỷ/phiên) · ⚠ universe_pit: n/a (không đọc được)
  FA: ROE5Y 26.6% · ROE_Min3Y 28.1% · FSCORE 5 · D/E 0.79 · PE 12.47
  DD HAH [DC] (data 2026-09-23): thanh khoản OK (ADV3T 29.29 tỷ/phiên) · ⚠ universe_pit: n/a (không đọc được)
  FA: ROE5Y 24.6% · ROE_Min3Y 15.5% · FSCORE 5 · D/E 0.69 · PE 
… (cắt bớt, xem nguồn để đủ; exit=0)
_(lược 3 dòng phụ lục của probe — xem nguồn nếu cần)_
🔍 Nguồn: `data/dc_book_waterfall_paper_state.json` (+1 nguồn, xem charter)

── **2) Capitulation-sleeve shadow (DT5G × 8L washout)** · 👤 Taylor · ⏳ WATCH
📈 asof 2026-09-22 | mode DEPLOYED | NAV 52.65B | tier NONCRISIS size=0.75 | entry 2026-07-20 | basket 5 mã · 📅 phiên ~77 từ 2026-06-10 · ⏱ nghiệm thu: EVENT-DRIVEN: sau sự kiện washout THẬT đầu tiên (chưa có deadline lịch)
💱 Giao dịch hôm nay: **n/a — `data/pt_capitulation_logs.csv` CHƯA có dòng cho phiên 2026-09-23** (pipeline sinh dữ liệu chạy 15:05/15:30 ICT; nếu đã quá giờ đó ⇒ pipeline chưa chạy/lỗi) · dòng gần nhất 2026-09-22: mode DEPLOYED · 5 mã · HOLDING 43/60td · 5 names · MTM x1.053
📊 Gate: **0/3 PASS** · không đổi từ 2026-07-31 · chi tiết: `mike/kb/paper_programs_charter/capitulation_shadow.md`
🔍 Nguồn: `data/pt_capitulation_state.json` (+1 nguồn, xem charter)

── **3) AlphaLens Paper (FPT/ACB/MBB/HDB vs VNINDEX)** · 👤 DollarBill · ✅ GREEN
📈 EW **≥ +1.81%** vs VNINDEX -3.14% → **excess ≥ +4.95pp** (MTM as-of 2026-09-23, quy ước `terp`) · accrue-only: excess ≥ +3.91pp · ⚠️ đã áp CHẶN TRÊN hệ số vendor ⇒ số này là CHẶN DƯỚI · 📅 phiên ~62/66 (2026-07-01→2026-09-30) · ⏱ nghiệm thu: 2026-09-30 — audit độc lập bởi Taylor
💱 Giao dịch hôm nay: **Không có giao dịch** — buy-and-hold theo thiết kế (equal-weight 25%/tên, không rebalance, giữ tới 2026-09-30)
📊 Gate: **0/3 PASS** · không đổi từ 2026-07-31 · chi tiết: `mike/kb/paper_programs_charter/alphalens.md`
- Vị thế (MTM as-of 2026-09-23, BQ cache close phiên gần nhất):
  • FPT: 70,200 → 66,100 = **+3.58%** (entry 2026-07-01, PE vs PE_MA1Y) [⚠ ĐÃ ÁP CHẶN TRÊN hệ số vendor 0.909066: giá vốn 70,200→63,816 ⇒ số trên là CHẶN DƯỚI]
  • ACB: 22,650 → 21,800 = **-3.75%** (entry 2026-07-01, P/B vs Gordon justified-PB)
  • MBB: 25,200 → 20,000 = **-0.89%** (entry 2026-07-01, P/B vs Gordon justified-PB) [giá vào 25,200→20,180 do quyền] · nếu BỎ quyền (accrue-only): vào 21,066 → **-5.06%**
  • HDB: 25,850 → 28,000 = **+8.32%** (entry 2026-07-01, P/B vs Gordon justified-PB)
- VNINDEX 1,860.01 → 1,801.65
- ⚖️ **Hai quy ước quyền mua** (MBB có đợt quyền mua trong cửa sổ). Dẫn dắt ở trên = `terp` (THỰC HIỆN 100% quyền — chỉ đạo user 2026-09-23). Quy ước cũ `accrue_only` (giả định BỎ quyền) cho: EW **+0.77%** vs VNINDEX -3.14% → **excess +3.91pp** (chênh +1.04pp so với số dẫn dắt).
- 🚨 **Hệ số vendor chưa hồi tố đủ — số dẫn dắt ĐÃ được sửa bằng CHẶN TRÊN.** FPT: `Close/Price` = 1.000000 tại 2026-06-30 nhưng chỉ còn 0.909066 tại 2026-09-18 — đại lượng này KHÔNG được phép giảm theo thời gian (nó là tích hệ số của các sự kiện CÒN Ở TƯƠNG LAI). Hệ số tại ngày vào lệnh vì thế QUÁ CAO ⇒ giá vốn rebase THIẾU. **ĐÃ ÁP chặn trên 0.909066** (phương án B, user duyệt 2026-09-23): giá vốn 70,200 → 63,816, tỉ suất -5.84% → **+3.58%**. Đây là CHẶN DƯỚI, không phải giá trị đúng chính xác — vendor hồi tố sâu hơn thì tỉ suất thật CAO HƠN nữa. Đã verify thẳng trên `tav2_bq.ticker` (không chỉ cache) — đây là lỗi hồi tố của vendor. Cách xử lý = **phương án B** (user duyệt 2026-09-23, bus question `alphalens-fpt-vendor-factor-stale-gate-0930`): áp chặn trên đã xác minh vào số dẫn dắt ⇒ mọi tỉ suất/excess ở trên là **CHẶN DƯỚI**, giá trị thật có thể CAO HƠN nếu vendor hồi tố sâu hơn.
🔍 Nguồn: `data/alphalens_paper.json` (+1 nguồn, xem charter)

── **4) Order-book execution shadow (10-level bid-ask)** · 👤 Taylor · ⏳ WATCH
📈 order-book opportunities N=321 · snapshot hợp lệ 298 · 📅 phiên ~28/47 (2026-08-18→2026-10-21) · ⏱ nghiệm thu: CHECKPOINT 2026-09-23 (job Taylor_20260923_005911) — ĐỦ MẪU nhưng KHÔNG QUYẾT ĐƯỢC, và KHÔNG phải vì thiếu mẫu. Đếm ĐỘC LẬP từ jsonl thô (không tin self-report của probe): 22 phiên có record từ 2026-08-18, **21 phiên có ≥1 snapshot hợp lệ** ⇒ vượt mốc 20 ⇒ KHÔNG áp công thức gia hạn Wilson (công thức đó dành cho ca thiếu MẪU). Chặn thật nằm ở INSTRUMENTATION: (1) `shadow.recommendation` = KEEP 300 / REDUCE 1 / DEFER 0 trên N=301 — policy `spread_depth_v1` lệch khỏi baseline đúng 1 lần (0,33%), nên gate 3 ('so sánh ngoài mẫu theo slippage / fill-rate / time-to-fill / adverse selection') không có độ tương phản để so, thêm phiên cũng không sinh ra. (2) Schema `orderbook_execution_v1` KHÔNG có trường hậu kiểm nào; probe báo outcome coverage 1m=4/249 · 5m=4/249 · 15m=2/249 (~1,6%) ⇒ gate 1 ('hậu kiểm 1/5/15 phút') CHƯA đạt dù là gate instrumentation. (3) Mẫu lệch: 275/301 record (91%) từ `account=main`, `book=PROBE` — harness churn tổng hợp, không phải lệnh chiến lược thật; lệnh tài khoản THẬT chỉ 26 record trên 5 phiên (09-14→09-22). END dời 09-23 → 2026-10-07 CHỈ để có thời gian cho quyết định dưới đây, KHÔNG phải để gom thêm mẫu. CẦN USER CHỐT 1 trong 2: (A) SỬA rồi chạy lại — thêm trường hậu kiểm 1/5/15' vào schema + nới policy để sinh tỉ lệ khuyến nghị khác-baseline đo được, rồi đặt cửa sổ mới; (B) DỪNG và ghi nhận KẾT QUẢ NULL — một policy spread+depth gần như không bao giờ bất đồng với baseline qua 301 cơ hội thật là một câu trả lời hợp lệ: không có edge execution để hái ở nhịp này. Dù chọn gì, KHÔNG go-live (đúng phạm vi đã chốt: chỉ quyết paper A/B hay dừng).
💱 Giao dịch hôm nay: **n/a theo thiết kế** — Chương trình LOG-ONLY, không phát sinh lệnh riêng; activity đọc từ probe theo child-order opportunity. N=0 nghĩa là chưa có opportunity, không phải policy không có giá trị.
⚠️ Cảnh báo: ERROR telemetry: 23 → 🔴 nghiêm trọng: RÀ SOÁT 2026-08-20 (job Taylor_20260820_012218): 'ERROR telemetry: 20' hôm 08-20 là BUG THẬT trong probe, ĐÃ VÁ (mike/bin/order_book_shadow_probe.py, `_TEST_ACCOUNT_PREFIXES`). Nguyên nhân: 14/20 record 'invalid' là RÁC — 6 selfcheck (capit_participation_cap_selfcheck.py, discretionary_participation_cap_selfcheck.py, extreme_regime_selfcheck.py, expected_volume_pacing_selfcheck.py, t2_settlement_selfcheck.py, tick_retry_selfcheck.py, churn_guard_selfcheck.py) dựng Executor với account='selfcheck-*'/'tickcheck-*' + plan_date sentinel '2099-01-01' mà quên set ORDER_BOOK_TEST_SINK, nên ghi thẳng vào EXEC_DIR thật; probe lọc theo plan_date>=START nên '2099-01-01' luôn lọt qua. Đã sửa probe lọc theo prefix account (không phụ thuộc tên file), N tụt 39→25, ERROR 20→6. 6 record ERROR CÒN LẠI là THẬT nhưng ĐÃ GIẢI THÍCH, không phải bug đang sống: toàn bộ thuộc phiên 2026-08-18 (ngày đầu trial) trước commit 0a684683 (17:32 ICT cùng ngày, 'fix(orderbook-shadow): PHSBroker.get_quote() now sets l2_snapshot for paper-trading') — 6 lệnh 10:46-11:00 ICT chạy TRƯỚC fix nên l2_snapshot rỗng ⇒ fail-open đúng thiết kế (KEEP, reason=invalid_or_stale_snapshot_fail_open, không ảnh hưởng hành vi đặt lệnh). Toàn bộ 19 record 2026-08-19 trở đi valid=True — không tái diễn từ đó. 6 file selfcheck có cleanup gap (glob chỉ xoá exec_{TAG}_*, không xoá orderbook_shadow_{TAG}_*) — TODO thứ yếu, chưa vá (rủi ro thấp: rác đĩa, không ảnh hưởng số liệu nữa vì probe đã lọc theo account). 12 file rác đã dọn khỏi data/execution_logs/.
📊 Gate: **0/4 PASS** · không đổi từ 2026-08-17 · chi tiết: `mike/kb/paper_programs_charter/order_book_execution_shadow.md`
order-book observations N=321 · valid=298 · sessions=23
  [PROBE] N=295 · policy KEEP=295 REDUCE=0 DEFER=0 · khác-baseline=0.0% · touch_depth_ratio median=763.0x
  [REAL] N=26 · policy KEEP=25 REDUCE=1 DEFER=0 · khác-baseline=3.8% · touch_depth_ratio median=7.0x
latency snapshot→order median=75.0ms
fill-linked children=285/321 · fill-rate=88.8%
time-to-first-fill median=19.617s · fill-vs-limit slippage median=-0.0bps
outcome coverage 1m=247/265 · 5m=247/265 · 15m=218/265 · basis mid=6 last=259 none=0
adverse-selection median 1m=+13.8bps · 5m=+8.0bps · 15m=-0.0bps
markout artifact: /home/trido/thanhdt/WorkingClaude/data/execution_logs/orderbook_markout.jsonl (265 bản ghi, schema orderbook_markout_v1)
ERROR telemetry: 23
scope v1: spread + displayed depth + adverse selection; resilience EXCLUDED (60s cadence).
🔍 Nguồn: `data/execution_logs/orderbook_shadow_<account>_<date>.jsonl — schema orderbook_execution_v1: trace_id parent/child, baseline, KEEP/REDUCE/DEFER, latency và snapshot immutable` (+4 nguồn, xem charter)

── **5) ORB intraday VN30F (ring-fenced)** · 👤 Taylor · ⏳ WATCH
📈 asof 2026-09-23 | 73 phiên từ 2026-06-09 | NAV 1.062B (+6.18%) | WR 54.8% | phiên cuối -0.30% (sig +1) | Sharpe report 1.46 (mẫu nhỏ — đọc thận trọng) · 📅 phiên ~78 từ 2026-06-09 · ⏱ nghiệm thu: ≥60 phiên GỒM chop/bear → re-eval quant-skeptic (điều kiện REGIME, không có deadline lịch)
💱 Giao dịch hôm nay: **n/a — `data/orb_pt_log.csv` CHƯA có dòng cho phiên 2026-09-24** (pipeline sinh dữ liệu chạy 15:05/15:30 ICT; nếu đã quá giờ đó ⇒ pipeline chưa chạy/lỗi) · dòng gần nhất 2026-09-23: sig +1 · vào 1,961.8 → ra 1,956.3 · net -0.30% (1 lượt/phiên theo thiết kế ORB)
📊 Gate: **0/4 PASS** · không đổi từ 2026-07-31 · chi tiết: `mike/kb/paper_programs_charter/orb_intraday.md`
🔍 Nguồn: `data/orb_pt_status.json` (+1 nguồn, xem charter)

── **6) Engine-room OOS panel (V11/V12/V4 vs V2.3-book vs VNINDEX)** · 👤 Taylor · ✅ GREEN
📈 V2.3-book -2.22% vs VNINDEX +1.02% (cửa sổ chung, NAV rebase 50B) · 📅 phiên ~76 từ 2026-06-11 · ⏱ nghiệm thu: 2026-12-01 (~6 tháng OOS trên cửa sổ chung từ 2026-06-11)
💱 Giao dịch hôm nay: **n/a theo thiết kế** — panel so sánh NAV của 5 sổ MÔ PHỎNG (V11/V12/V4/V23/VNI_BH) — panel không giữ nhật ký lệnh tách bạch; giao dịch THẬT của sổ production V2.3 nằm ở báo cáo EOD live, không phải ở đây
📊 Gate: **0/2 PASS** · không đổi từ 2026-07-31 · chi tiết: `mike/kb/paper_programs_charter/engine_room_oos.md`
Cửa sổ so sánh CHUNG 2026-06-11 → 2026-09-22 (71 phiên), NAV rebase 50B tại đầu cửa sổ (không phải NAV thô từ inception gốc):
  V11       +0.97%  (NAV 50.48B)
  V12       +0.12%  (NAV 50.06B)
  V4_DT5G   +1.25%  (NAV 50.62B)
  V23       -2.22%  (NAV 48.89B)
  VNI_BH    +1.02%  (NAV 50.51B)
🔍 Nguồn: `data/papertrade_compare5.csv (papertrade_compare.py)` (+1 nguồn, xem charter)

── **7) P2 — mẫu số pacing theo KL KỲ VỌNG (expected-volume pacing)** · 👤 Taylor · ✅ GREEN
📈 2 phiên có lệnh ADV20-paced · **order-day N=2** · 76 slice quan sát · 📅 phiên ~29/42 (2026-08-17→2026-10-13) · ⏱ nghiệm thu: Bắt đầu 2026-08-17 · checkpoint LẶP LẠI ~4 tuần (09-15✔, 09-23✔ ngoài lịch, 10-13, 11-10, ...) tới khi ≥25 order-day HOẶC safety_ceiling 2027-02-17 (xem end_or_trigger). CHECKPOINT 2026-09-23: gate an toàn (1) và gate LIVE-không-đổi (2) = PASS (đo lại thật: recompute độc lập 0 vi phạm + 2 selfcheck rc=0 + cấu hình _expvol_active kiểm lại); gate 3/4 THIẾU MẪU N=2/25 KHÔNG ĐỔI từ 09-16, gate 5 chưa đủ điều kiện. Vắng mặt đã verify bằng artifact: 6 phiên live sau 09-14 có journal, 0 lệnh CAPIT/DISCRETIONARY_SPECIAL (toàn BAL/PARK). Nhịp đo 12,5 phiên/order-day ⇒ 106 phiên còn lại tới ceiling chỉ sinh thêm ~8-9 order-day (tổng ~11/25) ⇒ NHIỀU KHẢ NĂNG ĐÓNG Ở CEILING vì 'thiếu cơ hội', KHÔNG PHẢI NO-GO trên edge. Không flip gate, không tạo lệnh giả. Checkpoint kế: 2026-10-13. LƯU Ý CƠ CHẾ: `end` đã dời 09-15→10-13 — trước đó end quá hạn khiến paper_checkpoint_escalation.sh escalate lặp mỗi chu kỳ dù checkpoint 09-16 đã làm xong.
💱 Giao dịch hôm nay: **n/a theo thiết kế** — chương trình LOG-ONLY: không phát sinh lệnh riêng nào (P2 chưa được phép đổi hành vi trên live). Hoạt động trong ngày đọc ở dòng cuối output probe ('hôm nay: N order-day · M slice')
📊 Gate: **2/5 PASS** · không đổi từ 2026-09-16 · chi tiết: `mike/kb/paper_programs_charter/expvol_pacing.md`
2 phiên có lệnh ADV20-paced · **order-day N=2** · 76 slice quan sát
bind=ceil 76/76 (100.0%) — chỉ nhóm này P2 mới nới được
delta allowance khi bind=ceil (cp): trung vị +28 · tb +58 · max +418 · 75/76 slice có delta>0
an toàn: %tape tối đa nếu P2 khớp trọn allowance = 50.0% (trần 50%) · vi phạm clamp **0** · EXPVOL_SHADOW_ERR **0**
hôm nay (2026-09-24): 0 order-day · 0 slice · bind=ceil 0
🔍 Nguồn: `data/execution_logs/exec_{SpaceX,ZaloPay,RocketX}_*_journal.csv — event EXPVOL_SHADOW / EXPVOL_SHADOW_ERR` (+3 nguồn, xem charter)

───
📎 *Badge: 🔴 RED = probe lỗi / cảnh báo chưa được giải thích / có gate FAIL · ⏳ WATCH = có cảnh báo đã giải thích hoặc thiếu khai báo giao dịch · ✅ GREEN = còn lại. Mục đích + phương pháp + tiêu chí nghiệm thu đầy đủ: `mike/kb/paper_programs_charter/<id>.md` (tự sinh từ registry). Mục hoàn tất hoặc thuộc vận hành được giữ trong registry nhưng không lặp ở đây. Gate chỉ in đầy đủ khi có thay đổi — trạng thái so sánh lưu ở `data/paper_report_state.json`.*
⚠️ *PAPER TRADING — không phải tiền thật; toàn bộ số liệu là mô phỏng/quan sát, không phải khuyến nghị đầu tư. Số không trace được về file nguồn = n/a.*
