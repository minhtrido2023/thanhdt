# Mike fleet — context pack (v1410)
> Snapshot tự sinh bởi consolidator. Nguồn chuẩn tắc: kb/KNOWLEDGE.md.

<!--RECENT-START-->
## MỚI NHẤT — kết quả gần đây từ toàn fleet
- [2026-07-24T02:32:08] Taylor/finding — Chien luoc thuc thi cho co phieu thanh khoan RAT THAP (ADV<1ty) — case TV1: doi lich tranche co dinh sang lenh cho dai dang + playbook tai su dung: {"job": "Taylor_20260724_022702", "trace_id": "Taylor_20260724_022702", "loai": "RESEARCH — de Mike/user quyet, KHONG tu sua code/plan; ap cho tranche 2 (07-27) …
- [2026-07-24T02:55:19] Taylor/finding — Low-Liquidity Discretionary Accumulation playbook — CODE XONG + selfcheck 33/33, CHUA CAI cron, cho verify truoc tranche2 07-27: {"job": "Taylor_20260724_024201", "trace_id": "Taylor_20260724_024201", "loai": "EXECUTION mechanism (giam chi phi GD), KHONG phai alpha/edge — cham lenh that S …
- [2026-07-24T03:00:18] quant-skeptic/verification — ✅ CONFIRMED VERIFY: Low-Liquidity Discretionary Accumulation playbook — CODE XONG + selfcheck 33/33, CHUA CAI cron, cho verify truoc tranche2 07-27: {"finding_topic": "Low-Liquidity Discretionary Accumulation playbook — CODE XONG + selfcheck 33/33, CHUA CAI cron, cho verify truoc tranche2 07-27", "verdict":  …
- [2026-07-24T03:14:26] Taylor/finding — Discretionary injector pre-cron verify: dry-run DNSE THAT OK + session-guard + fix account_id bug — selfcheck 33/33: {"job": "Taylor_20260724_030732", "trace_id": "Taylor_20260724_030732", "loai": "EXECUTION mechanism hardening truoc khi cai cron — KHONG cai cron (Mike hoi use …
- [2026-07-24T05:47:42] Wags/finding — wags-fix: coord-2026-07-24 — DGC ZaloPay question triage (NO-FIX, re-escalate): {"root_cause": "KHONG PHAI loi dieu phoi. Checker ops_health_check §5 fire dung: question Taylor_20260724_012433 (topic \"DGC ZaloPay legacy (46,8% NAV) — GIU/T …
- [2026-07-24T05:51:11] arch-reviewer/verification — ✅ CONFIRMED ARCH-REVIEW: wags-fix: coord-2026-07-24 — DGC ZaloPay question triage (NO-FIX, re-escalate): {"finding_topic": "wags-fix: coord-2026-07-24 — DGC ZaloPay question triage (NO-FIX, re-escalate)", "verdict": "CONFIRMED", "confidence": "high", "summary": "Xá …
- [2026-07-24T08:00:40] Winston/finding — sbv-weekly-check-2026-07-24: {"date": "2026-07-24", "current_rate": 4.5, "fetch_status": "fetch_failed", "rate_changed": false, "note": "fetch_failed_assumed_unchanged", "verify_log": "/hom …
- [2026-07-24T11:11:21] Winston/finding — new-listings-daily: {"date": "2026-07-24", "lookback_days": 90, "total_new": 1, "needs_manual_rating": 0, "fresh_ipo": 0, "research_queue": [], "snapshot": "/home/trido/thanhdt/Wor …
<!--RECENT-END-->

# Current Operations — Mike fleet
> Mike cập nhật thủ công khi có thay đổi trạng thái quan trọng. Đọc trước mọi thứ khác khi restart.
> Cập nhật lần cuối: 2026-07-23

## Sleeve "mua khi sợ hãi có tính toán" — quét chủ động HÀNG TUẦN (mandate user 2026-07-23)
Sau chuỗi case TV1 + DGC (cả 2 lần đầu bị đánh giá quá thận trọng, user tự phát hiện + sửa —
xem 2 mục trên/bên dưới) — user chỉ đạo: đừng chỉ chờ user tình cờ để ý, chủ động dò tìm THÊM
case hàng tuần. Đã cài `bin/fearbuy_weekly_scan.sh` (cron Friday 08:10 ICT, dispatch Taylor,
đăng ký `kb/cron_registry.md`) — kết hợp refresh `anomaly_scan.py` + WebSearch tin khởi tố/bắt
lãnh đạo DN niêm yết 7-14 ngày qua, áp bộ lọc QUALIFY/NON/AMBIGUOUS trong
`calculated_fear_state_backstop.md`. Luôn báo cáo (kể cả 0 case mới — quy tắc quiet-heartbeat).
Đây là recon, KHÔNG tự mua — mọi case đáng chú ý vẫn cần due-diligence sâu + user duyệt riêng
như TV1/DGC.

## DGC re-do: DAO NGUOC downgrade -> QUALIFIED YES (asset-backed deep value, downside bao ve manh); user dung phan lon
**Job `Taylor_20260723_112707`** — user phản biện downgrade "gần-NON" (§6, 17/07) bằng data thật,
Taylor verify từng claim, đảo ngược kết luận. Phát hiện quyết định: **Q2/2026 CF_OA đã dương lại
~+1.083 tỷ** (Q1 âm -1.093 tỷ chủ yếu là ONE-TIME — 331 tỷ khắc phục + timing vốn lưu động, không
phải lõi mất khả năng tạo tiền). Verify claims: LN kế hoạch 1.600 tỷ ✅ đúng, "chưa lỗ bao giờ" ✅
48 quý 0 quý lỗ, cổ tức 2026 ✅ 30%=3.000đ + 50% treo 2025=5.000đ (yield tổng ~21%), "book value
4x" ✅ PB 0,91x (dưới sổ sách), "gần bằng tiền mặt" ⚠️ MỘT PHẦN đúng — cash thật ~10.922 tỷ (không
phải 13.000 như user nói, đã giảm 17% YTD), EV thật ~3.472 tỷ (không phải ~1.400 như suy ra từ số
user) — user overstate ~2.000 tỷ nhưng luận điểm vẫn đứng vững. Thận trọng còn giá trị: mỏ 25
KHÔNG có lộ trình mở lại rõ ràng (có thể dead-money vài quý), 2 quý liên tiếp DT giảm YoY, vụ án
dính đúng tài sản lõi (khác TV1 — thuỷ điện chưa 1 ngày dừng). **Khuyến nghị: QUALIFIED YES vị thế
NHỎ ≤0,5-1,0% NAV**, chân trời 1-2 năm, khung carry-cổ-tức + deep-value (giống TV1 discretionary,
ngoài book V2.4) — KHÔNG đặt cược re-rating +100% kiểu PNJ làm base case. `calculated_fear_state_
backstop.md` §6 đã RE-DO. **Cần user quyết định cuối** có mua discretionary hay không.

## TV1 (PECC1) — due-diligence lần 1 (KHÔNG mua) → lần 2 SOTP ĐẢO NGƯỢC (QUALIFIED YES)
Lần 1 (job `Taylor_20260723_091219`) kết luận NO cho fear-buy sleeve: TV1 lệch khỏi khung
calculated-fear PNJ/VEA — vụ án EVNNPT dính đấu thầu tư vấn điện = lõi kinh doanh (không phải
scandal cá nhân tách rời tài sản), Big4 từ chối kiểm toán FY2026, 2 catalyst đang theo dõi (cổ
tức 15%/2025, bỏ phiếu chọn kiểm toán 10/08) đều không còn giá trị thực.

**⚠️ TV1 SOTP re-do (2026-07-23, job `Taylor_20260723_093559`) — ĐẢO NGƯỢC "NO" ở trên →
QUALIFIED YES (deep-value, asset-backed).** User chỉ ra due-diligence lần 1 bỏ sót tài sản lõi:
TV1/PECC1 sở hữu 100% thủy điện **Sông Bung 5 (57MW)**, nợ dự án đã trả gần hết (257 tỷ→0,4
tỷ), NP TTM 151,9 tỷ trên vốn hoá chỉ 531 tỷ (PE 3,5/PB 0,98). Verify bằng comp M&A thật (Nậm
Nơn 32 tỷ/MW → SB5 ~1.824 tỷ) + đấu giá SB5 2018 (1.390-1.688 tỷ gồm nợ, nay đã hết nợ) → SOTP
bảo thủ (hydro đáy DCF, tư vấn=0): equity ~883 tỷ = 33.100đ/cp (+66% từ giá 19.900đ). **Đính
chính quan trọng lần 1 sai:** BCTC FY2025 đã kiểm toán bởi A&C (sạch); Big4 từ chối là cho FY2026
(tương lai) — lần 1 đánh đồng 2 việc khác nhau. Vẫn giữ 2 ràng buộc thật (không phải lệnh sạch):
thanh khoản ADV chỉ ~1 tỷ/ngày (fail sàn custom30V, sát biên LAG), overhang pháp lý FY2026 audit
chưa xong (tiền lệ DGC hạn chế giao dịch). Đề xuất: **ngoài book V2.4, discretionary special-
situation** ≤0,5-1,0% NAV, gom chậm ≤15-20%ADV, giữ 2-3 năm chờ SOTP đóng/catalyst bán tài sản.
Chi tiết: `agents/Taylor/research/tv1_pecc1_sotp_20260723.md`. **Cần user quyết định cuối** có
mua discretionary hay không — Mike/Taylor không tự đặt lệnh ngoài V2.4.

## Dự án thay thế `ticker_prune` → `universe_pit` — ĐÃ DUYỆT Q1-Q9, đang triển khai G1 (2026-07-22)
bq_admin xác nhận `ticker_prune` không có hệ thống quản trị (3 đường ghi độc lập chồng lấn, curation
`hit_ticker_list` suy từ chính kết quả backtest cũ = circular bias, membership không tái lập được).
Team (Taylor kiến trúc + Winston vận hành) đề xuất xây `universe_pit` — bảng team tự sở hữu, append-
only, tính point-in-time trực tiếp từ `tav2_bq.ticker`. quant-skeptic REFUTED 1 luận điểm phụ (test
recall 97-99% là tautology, đại số trùng công thức gốc) → Taylor sửa lại + chạy test thay thế: **43
mã "rule-only" (lọt rule thanh khoản nhưng bị `ticker_prune` loại) có chất lượng KÉM RÕ RỆT** (ROE_
Min3Y âm TB, nhất quán 4/4 mốc lịch sử) — **curation CÓ mang thông tin thật**, nhưng cũng SAI theo
hướng bỏ sót mã tốt mới niêm yết (FOX/VPL/VGI). User đã DUYỆT toàn bộ Q1-Q9 (2026-07-22):
- Q1-Q2: xây `universe_pit` độc lập, ngưỡng B3=1,0 tỷ VND/ngày (hằng số production có sẵn).
- **Q9 (mới, cổng cứng)**: cấm cutover các bước chạm tiền thật (P2 custom30V, P4 CAPIT) tới khi đo
  xong độ rò chất lượng qua golden floor hiện có (G2b) + xuất cờ chất lượng cho tầng chiến lược đọc
  — **KHÔNG** thêm ngưỡng ROE cứng vào tầng universe (tránh bẫy tự-tune). User tin hệ thống rating
  8L/golden floor hiện có đã đủ lọc chất lượng độc lập với `ticker_prune`.
- Q3-Q8: đánh dấu R3 27,84% PROVISIONAL, chấp nhận re-pin, CAPIT breadth giữ đọc `ticker_prune` có
  chủ ý tới khi hiệu chuẩn lại (cấm cutover khi `capit_fired=true`), B8 integrity gate bắt buộc
  (bq_admin xác nhận `max_bad_records=10` áp cho MỌI bảng gồm `ticker`).
Timeline ước tính ~2,5-3 tuần lịch (8-11 phiên + 2 tuần shadow). Tài liệu đầy đủ:
`mike/agents/Taylor/research/ticker_prune_replacement_plan.md` (kiến trúc/migration) +
`mike/agents/Winston/universe_pit_ops_feasibility_20260722.md` (vận hành) +
`mike/agents/Taylor/research/ticker_prune_universe_QA_bq_admin_20260722.md` (Q&A gốc bq_admin).
Đang triển khai G1 (`bin/build_universe_pit.py`) — theo dõi tiến độ qua bus finding Taylor.

## CAPIT (bear-washout) — ĐÃ FIRE từ 07-20/07-21, đang giải ngân dở (cập nhật 2026-07-22)
**Trạng thái thật** (`data/golive_v23_status.json`, xác nhận qua job `Taylor_20260722_084953`):
`capit_fired=true` từ ít nhất 07-20 (breadth_oversold 07-20: 42,9%, 07-21/22: 46,2% — vượt xa
washout_gate=0,3). SAB/SIP/VNM đã khớp; PVT/NCT còn vướng (chờ trần giá/quota). Nguồn vốn: công
thức `NAV_book_LAG × capit_size` (user chốt 07-20), user tự rút Trứng vàng khi fire — note đã wire
vào `bin/bq_freshness_check.sh`, DollarBill tự thấy khi lập plan.
2 điểm cần biết: (a) sát biên "grind" (91 vs cửa sổ 20-90 phiên — lệch 1 phiên khiến size full 0,75
thay vì 0,375); (b) dd52w lúc fire (~-7%) là mức nông nhất từng fire trong lịch sử 2014-2026 (kỷ
lục cũ -7,4%) — ngoài rìa mẫu dữ liệu đã biết. Theo dõi tiếp PVT/NCT khớp nốt qua EOD report.

**PNJ EXCLUDED khỏi rổ CAPIT — due-diligence gate đã wire + verify (2026-07-20, job
`Taylor_20260720_081359`).** PNJ đang khủng hoảng thật (P-Lab bị bắt vì buôn lậu kim cương, scandal
02/07, giá sập ~-32%, team đã kết luận AMBIGUOUS trong `agents/Taylor/research/
calculated_fear_state_backstop.md` §7, cổng xác nhận thật là BCTC Q3/2026 ~cuối tháng 10 — KHÔNG
phải case sạch như PNJ-2015). quant-skeptic CONFIRMED (cao): PNJ pbz=-2,699, xếp HẠNG 1 trong pool
CAPIT ngày 07-17 — nếu không có gate, CAPIT sẽ mua PNJ full size đúng lúc khủng hoảng. Cơ chế:
`anomaly_scan.py` (build từ ground-truth DGC+PNJ) ghi `data/anomaly_flags.json` (cờ 30 ngày, TTL
verify không rò rỉ), CAPIT basket-selection lọc bỏ mọi ticker có cờ active TRƯỚC bước chọn pbz —
gate CHUNG, không hardcode tên, tự áp dụng cho case tương lai. Đã wire vào `ops_health_check.sh`
08:20+12:45 (tier-H alert Trading Daily, tier-W ghi cờ im lặng). Rổ hiện tại (nếu fire hôm nay):
NCT, PVT, SAB, VNM (PNJ đã loại). **Giới hạn thật cần nhớ**: gate KHÔNG backtest được (n=1, không
có lịch sử point-in-time), coi là bảo hiểm chi phí chưa đo được, đừng trích dẫn như alpha đã kiểm
chứng; sau khi loại PNJ (mã thanh khoản nhất), rổ neo vào NCT (ADV 2,18 tỷ/ngày, sát sàn 2 tỷ) —
vấn đề sizing NCT có sẵn từ trước, gate làm nặng thêm chút, cần theo dõi nếu fire thật.
> ⚠️ File này inject vào MỌI phiên/dispatch — giữ NHỎ. Chỉ để mục LIVE/đang-mở. Dự án ĐÓNG (NO-GO/
> KHÉP KÍN/XONG) → chuyển thành 1 file `kb/projects/<slug>.md` + thêm 1 dòng vào `kb/projects/INDEX.md`
> (INDEX được inject, chi tiết chỉ `cat` khi cần). Đừng để nhật ký dự án đã đóng tích lại ở đây.
> ⚠️ Sự cố ĐÃ GIẢI QUYẾT (fix xong + verify) → rút về **1-2 câu + pointer `kb/INCIDENTS.md`**
> ngay khi đóng, KHÔNG giữ nguyên play-by-play ở đây "cho chắc" (bài học sự cố model-drift/
> context-bloat 2026-07-17 — file này phình 0→36KB trong 3 tuần chủ yếu vì narrative sự cố đã
> đóng không được rút gọn, đè phí token lên MỌI dispatch qua `context_pack.md`).

## LAG 07-24 (IVS/TMG/TRC) — user chốt phương án C, chỉ mua TRC (2026-07-21)
Chuỗi điều tra hôm nay (job `Taylor_20260721_130404` + `_133858`) phát hiện: (a) đường live
LAG **thiếu trần %ADV** mà chính backtest R3 pinned đang giả định (≤20%ADV/phiên, ≤5 phiên,
huỷ nếu <30% filled) — lỗ hổng thật, chưa fix; (b) **TMG** `Volume_3M_P50=0` (ngoài
`ticker_prune`, ~20tr VND/ngày) → đóng góp ĐÚNG 0 vào backtest, mua live = ngoài mô hình; (c)
**IVS** (ICB 8777, CTCK) surprise +136,7% phồng cơ học do nền 2025Q4 lỗ, ROE_Trailing chỉ
1,89%, ADV 39% lệnh fleet, ngoài `ticker_prune`; PEAD nhóm CTCK edge trung bình cao hơn sản
xuất NHƯNG không dự báo được (IC=+0,051 p=0,35 vs manuf +0,136 p<1e-4) và chỉ là hiện tượng
kỷ nguyên 2020-24 bull/retail-boom (IS 2014-19 âm), 12m gần nhất đã âm. **User CHỐT: phương án
C — chỉ mua TRC ngày 07-24, bỏ IVS và TMG.** DollarBill lập plan riêng tối 07-23 — PHẢI áp
đúng quyết định này (không tự ý mua lại IVS/TMG theo tier gốc). Việc còn treo (chưa làm, cần
duyệt riêng): wire trần %ADV cho lệnh LAG trong `plan.py` mirror `cap_capit_orders`.

**✅ ĐÃ XONG 2026-07-22 (job `Taylor_20260721_162243`) — gate LAG %ADV LIVE + baseline được
đính chính.** (a) `trading_bot.plan.cap_lag_orders` đã COMMIT và wire VÔ ĐIỀU KIỆN trong
`bot_execute.py` (không feature-flag) ⇒ **ACTIVE từ phiên kế tiếp**, áp cho MỌI account
(SpaceX/ZaloPay/paper `main`). Cơ chế: trần 20%ADV/phiên chia đều theo số account live,
TRIM (phần dư tự mua tiếp phiên sau qua diff target-vs-thật), fail-CLOSED khi không đo được
ADV. Đo trên rổ 07-24: TRC trần 279tr/phiên (1 account) hoặc 140tr (2 account) — plan TRC
bình thường KHÔNG bị chạm; TMG sẽ bị CHẶN HẲN (ADV=0) nếu ai đó đưa lại vào plan.
(b) Baseline: engine backtest có lỗi cho phép mua TRỌN size mã `Volume_3M_P50<=0` (12,8%
vốn quay vòng LAG, nhóm này LỖ) — đã sửa (default OFF, canonical không đổi). A/B
contemporaneous **27,22% → 31,33% CAGR (+4,11pp)**, LOO 13/13 dương, quant-skeptic
CONFIRMED/high. ⚠️ **Số chính thức VẪN là 27,84%**; con số trung thực để kỳ vọng là **khoảng
[~27,2% ; 31,3%]**. Re-pin chuẩn còn chờ `data/bq_cache` trở lại `verified:true` (phụ thuộc
`ticker_prune` corruption còn treo). Anchor drawdown mới nên dùng ~−30% (bootstrap 5th-pct),
không phải −19%.

**✅ ĐÃ XONG 2026-07-22 (job `Taylor_20260721_172103`) — lọc thanh khoản LAG ở TẦNG TÍN HIỆU
(user quyết 2026-07-21), commit `4b7aaa1`.** `golive_recommend_v23.py` gọi `lag_filter_illiquid()`
(module mới `lag_liquidity_filter.py`) NGAY TRƯỚC bước chọn/xếp hạng ứng viên LAG ⇒ mã ADV≤0/
thiếu/cũ >30 ngày không còn thành mục tiêu, vốn tự chảy sang event LAG kế tiếp thay vì nằm im.
Phạm vi = **CHỈ book LAG** (đo thật: BAL đã có `liq>=1e9` cứng; CAPIT pool 0/26.277 dòng ADV≤0
+ `capit_adv_caps` fail-closed; PARK custom30V min ADV 13,1 tỷ). Self-check 13/13 offline +
19/19 live (TMG loại, TRC giữ); quant-skeptic **CONFIRMED/high** (`logs/verify_20260721_175346.log`,
sau 2 vòng REFUTED — cả 2 chỉ refute phần DIỄN GIẢI, code không đổi).

⚠️ **CON SỐ CAGR KỲ VỌNG: GIỮ NGUYÊN KHOẢNG [~27,2%; ~31,3%], KHÔNG chốt về 31,33%.** Lý do (quan
trọng, đừng bỏ qua): quant-skeptic đo được TREAT vào lệnh **+30,1%** nhưng vị thế HOÀN TẤT lại
**−16,3%**, tỷ lệ ABANDONED_REFUND **59,2% → 73,8%**. "Vốn chảy sang event kế tiếp" và "book không
fill nổi mã LAG ở quy mô 25B" để lại **cùng dấu vết CSV** — chưa tách được. Nếu vế sau đúng thì
+4,11pp là hiện vật mô hình fill, không phải edge. Bộ lọc vẫn đúng logic (không mua được thì đừng
đặt mục tiêu) nhưng **đừng dùng +4,11pp làm cơ sở kỳ vọng**. Số chính thức VẪN **27,84%**.

**✅ ĐÃ TRẢ LỜI 2026-07-22 (job `Taylor_20260722_030015`) — trần vị thế LAG.** Số đúng theo logic
production = **12**, nhưng KHÔNG phải tham số rủi ro độc lập — là nghịch đảo số học của tier
weight (LAG_HI 10%/LAG_LO 8% NAV book LAG ⇒ 1/0,09≈11,1⇒12 = "book đầy"). Cơ chế enforce THẬT là
TIỀN (`target_value = NAV_book × tier_weight`), không phải bộ đếm — trần đếm-tên và trần tiền là
dual của nhau. Con số "16-17" đo trước đó là ảo giác từ cổng rò (chỉ đếm vị thế ĐÃ hoàn tất, bỏ
sót lệnh đang khớp dở); đếm đúng theo size thật (≥4% book) ra **max 13 / p95 11** — khớp hằng số
12. **Kết luận: LIVE KHÔNG CẦN thêm trần cứng nào** — trần kinh tế đã bị ép bởi tiền, thêm
`MAX_POS_LAG=12` sẽ là code chết (không bao giờ bind trước ràng buộc tiền), chỉ tạo ảo giác an
toàn. Backtest đã vá cổng rò (`count_inflight_slots`, commit `f974459`, default OFF = byte-
identical, không cần quant-skeptic vì không đổi hành vi live).

**✅ ĐÃ XÁC MINH 2026-07-22 (job `Taylor_20260722_034554`) — `weight_base` KHÔNG có rủi ro thật,
ĐÓNG, không sửa gì.** Trace đủ 3 kênh tiêu thụ `weight_pct` LAG: hiển thị/telegram (đúng, có ghi
chú base), archive-BQ (trung tính, không nhân NAV), DollarBill (đúng — MD tự ghi rõ base 2 chỗ).
Bằng chứng thật: plan `SpaceX_2026-07-22.json` tính đúng LAG book ~463M = active_nav × w_lag_target,
không phải NAV tổng. Không có code nào khác đọc thẳng CSV rồi nhân NAV — thêm field sẽ chỉ gây
rối không cần thiết.

## Due-diligence MẶC ĐỊNH cho MỌI ứng cử viên mua — mandate mới (user, 2026-07-21)
User chỉ đạo: bất kỳ mã nào trở thành ứng cử viên mua (mọi book: BAL/LAG/CAPIT/DC-book/
custom30V rotation) phải qua bước due-diligence — không chỉ để bảo vệ giao dịch đó, mà còn
để LỘ RA điểm hệ thống cần cải thiện (như lỗ hổng %ADV cho LAG vừa phát hiện ở trên). **Mặc
định trong quy trình cho CẢ production lẫn paper-trading**, không phải opt-in/chỉ khi có cờ
đặc biệt. Đây là mở rộng của due-diligence trigger hiện có (forensic_flags, >7% NAV,
first-time-buy, DCF=RICH+robust override, anomaly Tier-H — vẫn giữ nguyên làm HARD gate) sang
diện rộng hơn: MỌI candidate, không chỉ các case có cờ. Đã dispatch Taylor thiết kế + triển
khai (xem bus finding sau 2026-07-21 13:xx) — theo dõi kết quả trước khi coi mandate này đã
xong.

## Vận hành/kiến trúc daemon — trạng thái ổn định (không đổi gần đây)
Remote-control daemon `mike@Mike.service` tắt hẳn từ 07-07 (user chỉ dùng Discord qua
`ccdb-mike.service`, 2 service độc lập; bật lại: `systemctl --user enable --now mike@Mike.service`).
Model mặc định Mike = Sonnet 5, đồng bộ ở 3 tầng config (`.claude/settings.json` +
`ccdb-mike/.env` + `sessions.db` bảng `settings` — DB là nguồn ưu tiên cao nhất; sự cố malformed
model-string qua `/model` command đã fix ở tầng validation, xem [[reference-ccdb-model-config-layers]]
+ [[project-discord-only-workflow-remote-control-disabled]] trong memory Mike).

## Vận hành hàng ngày = TỰ PHÁT HIỆN → TỰ SỬA → BÁO CÁO (mandate user 2026-07-07)
User chỉ đạo: lỗi vận hành phát sinh thì TỰ FIX rồi báo cáo, không chờ user báo/nhắc việc.
Tài liệu chuẩn tắc: **`kb/ops_runbook.md`** (timeline ngày, mỗi bước check gì, ranh giới tự
sửa). Cơ chế: `bin/ops_autofix.sh` — checker phát hiện lỗi → dispatch Winston (opus, hạ từ
fable 2026-07-17 — xem `kb/INCIDENTS.md` "Model-tier drift") chẩn đoán + sửa + verify + báo
Trading Daily; đã wire vào `ops_health_check.sh` (08:20/12:45) và
`sync_bq_cache_daily.sh` (23:45). Cooldown 1h/vấn đề chống bão dispatch. **Ranh giới cứng
(không bao giờ tự sửa, escalate question + Telegram):** trade plan, trading_rules.json,
logic đặt lệnh, crontab dòng thực thi, xoá dữ liệu, BOT_STOP. Mike trong phiên sống thấy
lỗi ops → tự sửa trực tiếp cùng ranh giới đó, không cần chờ checker.

## Onboarding account mới cho team Mike (thêm 2026-07-06, user yêu cầu chuẩn hoá quy trình)
Khi user nói "giao quyền quản lý tài khoản X cho team Mike" → làm theo
`kb/account_onboarding_runbook.md` theo đúng thứ tự, không tự bịa quy trình. Tóm tắt: cron
dùng-chung (preflight/ops-health-check/send-plan-report/eod-report/dispatch-DollarBill) đã
tổng quát hoá qua `trading_bot.config.live_dnse_labels()` + `bin/for_each_live_account.sh` —
account mới `enabled:true/mode:live/broker:dnse` trong `trading_bot_accounts.json` tự động
được các bước này nhận, KHÔNG cần sửa cron. Riêng 4 dòng cron THỰC THI THẬT (`run_bot.sh`,
`bot_heartbeat.sh`, lunch-pkill) KHÔNG tự động — luôn hỏi user xác nhận trước khi thêm (điểm
không thể đảo ngược: bot tự đặt lệnh thật lần đầu, không người duyệt giữa chừng).

## Đang trading (LIVE)
- **SpaceX** (DNSE 0002023347): V2.4 LIVE từ 2026-07-01, có margin. NEUTRAL parking target
  **70%** của phần idle cash khi BAL/LAG rỗng (`trading_rules.json` v2.1 `neutral_parking`,
  đổi ≠0.70 cần `risk_dial_override` xác nhận, không thì Mafee tự block plan) — chọn 70% thay
  vì 93.8% go-live gốc vì backtest risk-adjusted thắng rõ (Sharpe 1.78 vs 1.66, job
  `Taylor_20260703_130720`, quant-skeptic CONFIRMED). run_bot.sh 09:05 ICT mỗi T2-T6. NAV/vị
  thế hiện tại: đọc `nav_history_SpaceX.csv` hoặc EOD report mới nhất (Trading report topic),
  đừng dùng số hardcode cũ ở đây. Chuỗi sự cố go-live tuần đầu (trim 07-06, bug tên file plan
  `_v2`, T+2 sellable-chiều, giá EOD sai nguồn) đều đã fix+verify — chi tiết: `kb/INCIDENTS.md`
  (tìm "2026-07-06").
- **ZaloPay** (DNSE 0001743768, tên cũ `dnse_main`): V2.4 LIVE từ 2026-07-06, **CASH-ONLY**
  (không margin) — cơ hội so sánh V2.4 có/không margin. **DGC (vị thế legacy) EXCLUDED khỏi
  rebalancing** qua `excluded_tickers` (`secrets/trading_bot_accounts.json`, enforce cứng ở
  `bot_execute.py`) — lý do: HOSE hạn chế giao dịch (lãnh đạo bị khởi tố 17/03/2026, ước gỡ
  hạn chế ~11-12/2026); Taylor giữ vì lý do đầu tư riêng, không phải kẹt thanh khoản. Sizing
  V2.4 dùng `active_nav` (`bin/compute_active_nav.py --account ZaloPay`), không dùng NAV tổng.
  Cơ chế `excluded_tickers` viết tổng quát cho account tương lai có vị thế legacy tương tự —
  `kb/coding_guidelines.md` §7. Transition 5 ngày (07-07→07-13, bán dần vị thế cũ sang
  custom30V) đã XONG — `kb/projects/zalopay-transition-0713.md`. Known gap: `daily_nav_snapshot.py`
  chưa tính đúng P&L cho vị thế legacy (NAV/active_nav đã đúng, chỉ breakdown P&L báo cáo còn thiếu).
- **AlphaLens Paper**: FPT/ACB/MBB/HDB, tracking vs VNINDEX đến 2026-09-30. DollarBill phụ trách.

### Trứng vàng DNSE (idle-cash off-book) — cả 2 account (thêm 2026-07-17)
User chuyển tiền rảnh sang sản phẩm tiền gửi "Trứng vàng" DNSE — **hoàn toàn ngoài phạm vi
OpenAPI** (cạn 19 endpoint pattern + SDK chính thức, xác nhận Mafee_20260716_170856). Số dư
hiện biết (user tự báo, **CẦN CẬP NHẬT LẠI mỗi lần nạp/rút**): SpaceX 302.108.211đ, ZaloPay
147.473.247đ (asof 2026-07-16) — lưu ở `manual_offbook_assets_vnd/_asof/_note` trong
`secrets/trading_bot_accounts.json` (default field mới ở `trading_bot/config.py`
ACCOUNT_DEFAULTS). Đã wire vào `daily_nav_snapshot.py` (NAV += offbook, KHÔNG cộng vào cash)
và `compute_active_nav.py` (active_nav += offbook, cơ sở sizing cho DollarBill) — quant-skeptic
CONFIRMED 2026-07-17. `bq_freshness_check.sh`'s DollarBill dispatch tự thêm note khi
`manual_offbook_assets_vnd≠0`.
⚠️ **QUY TẮC BẮT BUỘC — không tự động**: khi user báo đã RÚT tiền từ Trứng vàng ra (vd để
DollarBill lên plan mua), Mike PHẢI cập nhật/giảm `manual_offbook_assets_vnd` NGAY trong cùng
lượt — nếu quên, NAV/active_nav sẽ bị đếm trùng (cash tăng lại + offbook vẫn giữ số cũ). Không
rủi ro tiền thật (executor chỉ check cash/ppse live khi đặt lệnh — quant-skeptic xác nhận
fail-safe), nhưng sẽ làm sai NAV báo cáo + sizing plan. Staleness WARN tự in khi asof >21 ngày
chưa cập nhật (cả 2 script trên) — không tự block, chỉ nhắc.
⚠️ Chưa xác minh: SpaceX có dấu hiệu ppse/pp0Buy báo sức mua cao dù availableCash≈0 sau khi
chuyển Trứng vàng (Mafee_20260716_164743) — CHƯA rõ DNSE có tự tính gộp không, đừng giả định.

## Đang R&D
- **Taylor · EXTREME-regime gate PAPER-TRADING** (bắt đầu 2026-07-01, user duyệt trực tiếp): `extreme_regime_enabled=True` CHỈ trên account paper `main` (override trong `trading_bot_accounts.json`); global default + SpaceX/live GIỮ `False`. Week-1 stress-injection PASS 24/24 (`stress_extreme_regime.py`: arm 2-poll · sell-to-floor · buy-pause · cadence ×0.25 + negative controls). **Target kết thúc ~2026-07-28 (~20 phiên).** 3 điều kiện còn lại trước LIVE: (a) ZERO false-trigger qua ~4 tuần benign, (b) không can thiệp NORMAL-path, (c) user sign-off. **KHÔNG bật gì ở live.**
- **Taylor · vol-scale buy chase-cap (patch#3) PAPER-TRADING** (bắt đầu 2026-07-01, user duyệt trực tiếp): `chase_cap_vol_scale_enabled=True` CHỈ trên account paper `main` (override trong `trading_bot_accounts.json`, k=2.0/ceil=0.04); global default + SpaceX/live GIỮ `False`. Executor-path stress PASS 15/15 (`stress_vol_scale_chase_cap.py`: wiring · WIDEN clamp-to-ceil · MONOTONE · fail-safe rvol absent/0/<0 · paper limit > static + NEG-control live→static). **Target kết thúc ~2026-07-14 (~10 phiên — ngắn hơn EXTREME vì fire trên gap-up thường, tích event nhanh).** Điều kiện trước LIVE: (a) paper sạch (wiring đúng trên quote thật + fail-safe khi thiếu rvol cache), (b) không can thiệp NORMAL-path ngày non-gap, (c) skeptic rerun REAL-fill vs `min(open,L)` proxy trên correlated gap-up @NAV target, (d) user sign-off. **KHÔNG bật gì ở live.**
- **Taylor**: sector sweep #10+ (chờ Mike dispatch)
- **Taylor · fill-timing khung giờ (BUY 10:45-11:15 / SELL 09:15-09:45)**: ĐÃ xử lý xong 2026-07-02 (job Taylor_20260702_031608, note cũ ở dòng này lỗi thời). Edge THẬT & IS/OOS-stable (BUY tại 11:15 rẻ hơn open +17.6bps/lệnh, t=12.0; SELL tại open đúng, +11.8bps vs ATC) nhưng **KHÔNG flip `fill_timing_live_gate` ngay** — cần paper tích lũy ~3-4 tuần fill (từ go-live 2026-07-01, mới ~3-4 phiên) để `execution_quality_review.py` xác nhận NET-of-noise capture (noise 110-220bps >> edge 17bps) → quant-skeptic → user sign-off mới flip. Checkpoint tự nhiên: ~cuối tháng 7.
- **V2.5**: R&D-complete, DISABLED. Reminder: 2026-07-07 Mike hỏi user go-ahead integration.
- **Taylor · DC-book (ConvergePort) NEUTRAL idle-cash waterfall PAPER-TRADING** (bắt đầu 2026-07-06,
  user duyệt trực tiếp, job `Taylor_20260706_125540` + `Taylor_20260706_131247`): khi NEUTRAL và
  BAL/LAG rỗng (đúng tình trạng SpaceX từ ~04/2026), thứ tự ưu tiên giải ngân phần tiền rảnh:
  **BAL/LAG (full trước, không đổi) → DC book/ConvergePort (double-confirm sector-lens BUY ∧ 8L
  rating≤2, capacity ~10-15B ex-DHG) → custom30V (phần còn lại)**. Khi BAL/LAG có deal trở lại → rút
  ưu tiên ngược lại, bán custom30V trước rồi mới đến DC book (reverse-unwind). Backtest xác nhận: DC
  làm top-priority (thay BAL/LAG) = REFUTE mạnh (12.05% CAGR/DD-38.4% vs R3 28.05%/DD-18.8%); DC làm
  lớp giữa (đúng thứ tự trên) = +5.0pp trên sleeve parking, ước tính +3.5pp/năm cho SpaceX-now. **Caveat
  quan trọng: DSR phần excess này chỉ 0.775 (<0.95 ngưỡng an toàn) — bảo hiểm hợp lý, CHƯA phải alpha
  tin cậy cao** → lý do bắt buộc phải paper trước, không wire live ngay. Chạy CHỈ trên account paper
  `main` (override trong `trading_bot_accounts.json`), global default + SpaceX/live GIỮ nguyên (không
  đổi gì). **Đã thêm vào EOD daily report** (theo yêu cầu user 2026-07-06) — xem section paper sleeve
  trong `eod_trading_report.sh` output.
  **Review = EVENT-ANCHORED, KHÔNG PHẢI ngày cố định** (user quyết định 2026-07-06, sau khi Taylor tự
  đính chính lý do "3 tháng" không phải vì DSR mà vì chu-kỳ cơ chế): mốc review = khi chu kỳ
  reverse-unwind ĐẦU TIÊN (LAG dự kiến refill cuối 07, job `Taylor_20260704_033932`) hoàn tất + settle
  4-6 tuần sau đó. Sàn ~2 tháng (đủ thấy trọn unwind+settle), trần ~2026-10-06 (tránh mùa BCTC Q3).
  Nếu LAG refill trượt lịch → mốc review trượt theo, KHÔNG giữ cứng 10-06. **Mike + Taylor cùng theo
  sát diễn biến portfolio để đề xuất ngày review cụ thể khi đủ điều kiện** — không tự động, không
  phải 1 con số đã chốt sẵn.

  **⚠️ AGENDA SỬA tại mốc review (thêm 2026-07-13, job `Taylor_20260713_100550`, user xác nhận CHƯA
  sửa ngay — để tự nhiên chạy sai thêm một thời gian nhằm quan sát whipsaw thật qua đúng đợt LAG
  refill, rồi sửa gộp 1 lần tại mốc review).** Phát hiện quan trọng: **paper sleeve ĐANG CHẠY SAI so
  với chính spec đã backtest/pin** — dùng trigger NHỊ PHÂN (BAL/LAG có deal → tắt hẳn DC book) thay vì
  spec đúng là DC book chạy LIÊN TỤC trên phần tiền dư (residual). Hậu quả đo được: 57.8% ngày
  NEUTRAL-có-✓✓ vẫn có deal BAL/LAG mới trong khi tiền park còn ~38% NAV → bản nhị phân đang chạy hiện
  tại **TỆ HƠN CẢ baseline không có DC book** (CAGR 27.26% / DD −17.8% / Calmar 1.53 / turnover 20.7×,
  so với spec đúng 27.56% / −15.5% / 1.77 / 3.18× và baseline R3 27.35% / −17.6% / 1.55). 4 việc cần
  làm tại mốc review, theo đúng thứ tự ưu tiên:
  1. **Đổi trigger sang continuous-residual** (quan trọng nhất — đây là bug thực chất, không phải tối ưu thêm).
  2. Đồng bộ lịch rebalance DC book vào q2m5 (giống custom30V) — tự giảm whipsaw ~4 lần, đã backtest (job `Taylor_20260706_173317`).
  3. Cap gộp 0.15/tên (chống trùng mã DC↔custom30V vượt trần name_cap 10% NAV khi sleeve lớn — job `Taylor_20260707_042827`).
  4. Liquidity floor 3B thay hard-exclude DHG đơn thuần (job `Taylor_20260707_042827`).
  Đã kiểm tra kỹ 4 góc còn lại (sizing/depth-weight, ✓✓ làm tiebreaker BAL/LAG, mở rộng CRISIS/BEAR,
  sector-lens đứng riêng) — **không còn không gian cải thiện thật**, không cần backtest thêm cho các
  góc đó khi tới review, chỉ cần làm đúng 4 việc trên.

## Workflow ngày trading (SpaceX, T2-T6, giờ ICT)
1. **17:30** — `bq_freshness_check.sh`: BQ fresh → dispatch DollarBill lập plan T+1
2. **19:30** — `send_plan_report.sh`: gửi plan T+1 vào Trading Daily thread (duyệt trước 08:45 sáng mai)
3. **08:20** — `ops_health_check.sh --label "Trước phiên sáng"` (thêm 2026-07-06, theo yêu cầu user) —
   kiểm tra vận hành tự động TRƯỚC preflight: xung đột file plan (bài học sự cố 07-06), lỗi lặp lại
   bất thường trong journal (loại trừ WAIT_T2_SETTLEMENT/mẫu T+2 đã biết), circuit breaker, câu hỏi
   (question) chưa trả lời trong 48h — post tóm tắt vào **Trading Daily** (vận hành sống, không phải
   Trading report). Script: `bin/ops_health_check.sh`.
4. **08:45** — `preflight_check.sh`: kiểm tra sẵn sàng trước giờ mở cửa (GREEN/RED)
5. **09:05** — `run_bot.sh --auto-otp`: thực thi plan (phiên sáng)
6. **09:00-14:55** — `bot_heartbeat.sh` mỗi 5': giám sát liveness + digest fill mới
7. **11:30** — dừng bot giờ nghỉ trưa (`pkill -f "[b]ot_execute.py --account SpaceX"`, sửa 2026-07-06
   tối — pattern cũ tự khớp luôn dòng lệnh gọi chính nó qua `sh -c`, xem `kb/INCIDENTS.md`; vô hại
   vì `session_phase()` đã tự idle đúng qua trưa dù pkill không hiệu quả, nhưng vẫn cần fix cho đúng)
8. **12:45** — `ops_health_check.sh --label "Trước phiên chiều"` (thêm 2026-07-06) — kiểm tra lại toàn
   bộ khâu vận hành sau phiên sáng, trước khi resume phiên chiều — cùng nội dung kiểm tra như bước 3,
   chạy lại để bắt vấn đề phát sinh trong phiên sáng trước khi vào phiên chiều.
9. **13:00** — `run_bot.sh --auto-otp`: resume phiên chiều
10. **~14:50** — phiên đóng (ATC), bot tự cancel lệnh treo, ghi `exec_*_report.md`
11. **15:00** — `eod_trading_report.sh`: **báo cáo tổng kết EOD** (thêm 2026-07-01) — đọc `state.json`
   (giá khớp thực từng lệnh), tính tổng lệnh/mua-bán/khớp đủ-một phần-chưa khớp/tổng giá trị VND,
   post vào **Trading report topic** (đổi từ Trading Daily 2026-07-03, xem dưới). **Thêm 2026-07-03**:
   gọi `bin/daily_nav_snapshot.py` để in kèm NAV thật cuối ngày + biến động so hôm trước (MTM cổ phiếu
   từ BQ, cash/nợ margin từ balances API thật) — ghi vào `data/execution_logs/nav_history_SpaceX.csv`,
   nguồn duy nhất mọi báo cáo ngày/tuần/tháng dùng chung. Xem `kb/coding_guidelines.md` §6 "Standing
   pipeline" cho quy trình xác minh bắt buộc + phân biệt độ sâu nội dung theo từng loại báo cáo.

**3 Discord topic tách biệt (cập nhật 2026-07-03 — thêm Trading report):**
- **Trading Daily (1521470705563340910)** — nội dung VẬN HÀNH SỐNG trong ngày: preflight, run_bot,
  heartbeat, BQ freshness, `ops_health_check.sh` (08:20 + 12:45, thêm 2026-07-06). (EOD report đã
  CHUYỂN sang Trading report — xem dưới.)
- **DollarBill plan channel (1521183164364754974)** — riêng cho việc LẬP KẾ HOẠCH của DollarBill
  (`send_plan_report.sh`, và mọi `dispatch.sh DollarBill ...` khác dù cron hay ad-hoc). Root cause
  thread-leak (dispatch notify theo thread Mike đang active) đã fix ở tầng `dispatch.sh` qua hàm
  `_agent_thread_override` — route CỐ ĐỊNH cho DollarBill bất kể Mike gọi từ topic nào.
- **Per-job thread routing tổng quát (thêm 2026-07-06)** — `_agent_thread_override` chỉ đúng cho
  agent LUÔN thuộc 1 topic cố định (DollarBill). Nhưng Taylor phục vụ NHIỀU topic song song (vd
  user tách riêng "nghiên cứu 8L" và "nghiên cứu vĩ mô", cả 2 đều dispatch Taylor) — báo cáo hoàn
  thành từng job phải về ĐÚNG topic đã yêu cầu job đó, không phải topic Mike đang hoạt động lúc
  job xong. Fix: `dispatch.sh` giờ ghi `discord_thread_id` NGAY vào job record lúc dispatch (chụp
  1 lần, không đổi), mọi thông báo (nhận việc/xong/fail/circuit-breaker/usage-limit) đọc lại field
  này qua `_job_thread_id <job_id>` thay vì suy ra "topic hiện tại". Xem `kb/INCIDENTS.md`.
- **Trading report (1522576692638388364, thêm 2026-07-03, user chỉ đạo)** — kênh DUY NHẤT cho
  **báo cáo tổng hợp** trading ngày/tuần/tháng (khác với alert vận hành sống ở Trading Daily). Đã
  chuyển đích `eod_trading_report.sh` (báo cáo EOD + cảnh báo đối soát mismatch) sang topic này.
  Báo cáo tuần/tháng (khi Mike tự soạn thủ công theo yêu cầu user, vd báo cáo tuần go-live SpaceX
  2026-07-03) cũng đích đến topic này. User cũng dùng topic này để giao các yêu cầu vận hành liên
  quan đến báo cáo trading.

**Duyệt plan — LUÔN mirror vào DollarBill plan channel (thêm 2026-07-02, user chỉ đạo):** khi
user duyệt/thảo luận duyệt plan trực tiếp với Mike ở BẤT KỲ topic Discord nào khác (không riêng
plan channel), Mike vẫn xử lý ngay tại chỗ (không ép user đổi topic), NHƯNG phải
`notify_thread.sh` xác nhận vào **1521183164364754974** ngay sau đó — channel này luôn là bản ghi
đầy đủ mọi lần duyệt, dù hội thoại thật diễn ra ở đâu. Lý do: tránh rải rác/loãng topic khác.

**Escalation khi plan T+1 không sẵn sàng (thêm 2026-07-01, sau sự cố DollarBill "timeout" nhưng
plan thực ra đã ghi xong — dispatch.sh job status không đáng tin 100%):** `send_plan_report.sh`
19:30 ICT giờ verify ARTIFACT thật (file `plan_<account>_<T+1 date>.json` đúng ngày kỳ vọng qua
`next_trading_day()`, có field `orders`) — KHÔNG tin job status. Nếu thiếu/sai ngày/hỏng schema →
**ESCALATE thật**: Telegram + Discord (như cũ) VÀ ghi bus event `question` (`plan-t1-not-ready`) để
Mike tự đọc được ở phiên sau, không chỉ trông chờ user thấy Telegram rồi tới hỏi. KHÔNG tự động
retry/re-dispatch (an toàn hơn — con người quyết định bước tiếp theo, đúng nguyên tắc human-in-the-loop
của toàn hệ thống).

## Cron quan trọng khác (ICT)
| Giờ | Lịch | Việc |
|---|---|---|
| 23:45 | T2-T6 | sync_bq_cache_daily.sh |
| 02:00 | Daily | kb_nightly.sh — archive events, trim memory |
| 02:00 | Thứ 6 | kb_nightly.sh → dispatch Mike editorial KB review |
| 00:00 | Daily | backup.sh → GitHub |

## Kill-switches
- `data/BOT_STOP`: tạo file = dừng mọi giao dịch tức thì
- `state/NOTIFY_OFF`: tắt Telegram push tạm thời
- V2.5: `trading_rules.json v1.7` → v25_leverage STATUS=DISABLED

## Sự cố đã đóng, chỉ còn 2 mục thật sự CÒN TREO (rút gọn 2026-07-17, chi tiết đầy đủ `kb/INCIDENTS.md`)
Audit cron 07-12 (C1 DT5G-cache-bug + H2 freshness-false-block) — cả 2 **FIXED+VERIFIED**
(commit `4995262`, `6459b6d`, quant-skeptic CONFIRMED). BQ cache monolith 07-13 (27 file đọc
nhầm `ticker_prune.parquet` chết) — **FIXED** (Winston_20260713_143546, archived). 2026-07-14
HOLD — 1 ngày đã qua, không còn ảnh hưởng vận hành (DollarBill tự tính lại plan mỗi ngày).
Cross-account contamination trong `reconcile_equity.py`/`verify_account_snapshot.py` (phát
hiện 2026-07-19 khi Taylor soạn báo cáo tuần 07-13→07-17, job `Taylor_20260719_055139`) —
**FIXED** cả 2 file (mirror đúng fix `daily_nav_snapshot.py` 07-06/07: filter theo account_no
tự tra config, raise nếu không lọc được thay vì âm thầm dùng nhầm account); thiếu 1 dòng NAV
ZaloPay 07-14 (no-plan day, không có journal) — backfill bằng vị thế THẬT từ `dnse_raw`
`kind=positions` + giá đóng cửa BQ 07-14 (963.451.542đ), verify khớp broker positions record.

**Còn treo thật** (2 mục):
1. Dọn crontab paper-trading lạc hậu — diff đã có (`Winston_20260712_151206`), **chưa áp dụng**
   (chờ Mike review). Ưu tiên thấp, không khẩn.
2. **`ticker_financial`/`ticker_prune` corruption 07-14/15** (rows 07-08→07-14 bị xóa/ghi đè
   upstream) — mitigations đã xong (depth-check gate commit `1b66428`, backup time-travel
   `*_ttbackup_fresh_20260714`), nhưng **quyết định khôi phục dữ liệu từ backup vẫn CHỜ USER**
   (đang hỏi BQ admin upstream). Mike KHÔNG tự khôi phục/tạm dừng cron cho tới khi có quyết
   định. Kiểm tra nhanh còn treo hay đã xong: `kb/INCIDENTS.md` (tìm "ticker_prune cũng bị
   corruption") + hỏi lại user nếu > vài ngày chưa thấy cập nhật ở đây.

## Tri thức chung của đội (canonical — Mike biên tập; MỌI agent phải nắm)
> Cập nhật 2026-07-01. Chi tiết: `kb/KNOWLEDGE.md`. Số liệu gốc: `data/results_registry.md`.
> Codebase: `/home/trido/thanhdt/WorkingClaude` (BigQuery `tav2_bq`). **Live từ 2026-07-01.**

### Mục tiêu
Vận hành chiến lược **production V2.4**, **go-live 2026-07-01**, tài khoản SpaceX (DNSE), 1B VND.

### V2.4 — chiến lược trung tâm (đã verify, self-check 0 VND, threads=1)
- = **V2.3A + custom30V parking (NEUTRAL) + gated-overflow (bear-washout) + HAG eq_flag fix**.
- 2 book: **BAL** (momentum SIGNAL_V11, yieldcombo: 1/PE + 1/PCF) + **LAG** (PEAD/earnings drift).
- Allocator w_LAG: {CRISIS 50 / BEAR 0 / NEUTRAL-BULL-EXBULL 65}, band ±10pp.
- **R3 NEUTRAL-only @50B: CAGR 27.16% / Sharpe 1.81 / DD −18.1% / Calmar 1.50** — pin CHÍNH THỨC từ
  **2026-07-22**, đo trên **`universe_pit`** (bảng đội tự sở hữu, point-in-time, không look-ahead;
  `UNIVERSE_SRC` default = `pit` trong `pt_v23_audit_2014.py`). threads=1, self-check 0 VND.
  **Số lịch sử (KHÔNG dùng để trích dẫn mới)**: 27.84%/1.84/−18.2%/1.53 (pin 07-12, `ticker_prune`);
  cùng vintage cache 07-22 `ticker_prune` cho 27.95%/1.85/−18.4%/1.52 ⇒ Δ universe = **−0,79pp CAGR**,
  đúng hướng pre-register (khử curation/look-ahead bias của `ticker_prune`). quant-skeptic **CONFIRMED
  (high)**. ⚠️ Nhãn đúng khi trích dẫn: **MIXED-universe** — `universe_pit` cho *cổng quyết định*,
  `ticker_prune` vẫn cho *CAPIT pool / breadth / maturity* (~10 vị trí, cutover riêng). Lỗi fidelity
  `liq<=0` vẫn MỞ ⇒ khoảng kỳ vọng trung thực vẫn **[~27,2%; ~31,3%]**, anchor DD **~−30%**. Chi tiết:
  `data/results_registry.md` (mục 2026-07-22 CUTOVER R3 CHÍNH THỨC).
- Bootstrap 5th-pct: CAGR 18.6%, DD −28.6% (anchor DD ~−29%, KHÔNG phải −18%).
- **NEUTRAL parking custom30V = phần tin cậy nhất: +7.4pp Full.** (30 mã, cap 0.10)
- Bull parking: NAV ≥150B. **(30, 0.15) = OVERFIT**, walk-forward bác.
- **V2.5** (future) = V2.4 + lever MGE=1.5, account sẵn sàng, DISABLED, reminder 2026-07-07.

### Đã thử, BỊ LOẠI — không wire
custom30V permanent-exclude 7 tên (−1.0pp); LAG SUE-tilt 3 tầng (−0.66pp); hold-neutral exit (−47B);
stability floor ROE_Min<0 (−0.45pp); liq-tilt custom30 (REFUTED); deep-discount sleeve (PARKED);
pbcombo dual-vehicle (Calmar 1.48→1.37); gq_score growth gate (−IC); composite v3 as entry-selector (NO).

### MOM_N/MOM_S ĐÃ ĐÓNG (2026-07-12) — không phải "thử bị loại", là thay đổi production chính thức
Sau chuỗi R&D đầy đủ (momdeal Phase 1 CP1 NO-GO 0/13 feature → nhánh DVR-8L-sizing CP-DVR1 NO-GO →
đo tác động Scope A/B → kiểm tra tách MOM_N-vs-MOM_S, tất cả quant-skeptic CONFIRMED), user duyệt
đóng `MOMENTUM_N`+`MOMENTUM_S` khỏi `TIER_BAL` (giữ nguyên `MOMENTUM`/`MEGA` generic — Scope B đóng
cả họ bị số đo bác, generic vẫn đóng góp thật). Lý do: thành công lịch sử của 2 tier này chủ yếu do
dồn mẫu regime 2020-21, không phải pattern lặp lại được; hậu-2021 gần như hoà vốn. Chi tiết đầy đủ:
`plan_close_mom_20260712.md`, `plan_dvr_8l_sizing_20260712.md`, `plan_momentum_deals_20260711.md`.

### DT5G — market regime gate
- Production: `tav2_bq.vnindex_5state_dt5g_live` qua `get_gated_state()`.
- **KHÔNG đọc** `vnindex_5state` — đó là v3.4b BASE (153 transitions ≠ DT5G 49 transitions).
- Gate phòng thủ (insurance), KHÔNG phải return-enhancer.
- State hiện tại 2026-07-01: **NEUTRAL(3)**, DT5G_macro HEALTHY.

### 8L Rating & Composite
- Composite v3 LIVE (`rating_8l.py`): value = ey(1/PE) + cfy(1/PCF) + ps(1/PS). Golden floor: ROE_Min3Y≥0 ∧ CF_OA_3Y>0.
- **1/PE dominant factor** (IC +0.125, 94% hit). Rating = binary gate ≤3, KHÔNG phải return-tilt.
- Value dominates ALL regimes kể cả BULL. Moat governance: chỉ WIDE (đã audit 5F) mới notch.

### Hạ tầng giao dịch
- `bot_execute.py --auto-otp`: execution deterministic (Python, không phải LLM headless).
- `bin/run_bot.sh`: wrapper gọi bot_execute.py, Discord notify, publish bus event.
- **`data/BOT_STOP`** = kill-switch tức thì.
- BQ Local Cache (DuckDB, threads=1): `data/bq_cache/`, ~100ms vs 5-15s BQ. Sync 23:45 ICT.
- Auto-OTP Gmail: `gmail_otp_reader.py` dùng `internalDate` filter (KHÔNG `newer_than`).
- PHS: **BLOCKED** (lỗi -700003, chờ credential) → paper only.
- **Workflow ngày trading đầy đủ** (T2-T6): BQ freshness(17:30) → plan T+1(19:30) → preflight(08:45)
  → execute sáng(09:05) → resume chiều(13:00) → **EOD report(15:00, `eod_trading_report.sh`, thêm
  2026-07-01)**. Toàn bộ post vào 1 Discord thread — Trading Daily (1521470705563340910).

### Kiến trúc fleet
- Companion daemon: **CHỈ Mike**. Mọi agent khác (Taylor, Bill, Mafee, v.v.) headless/native on-demand.
- Winston/Spyros/Wendy = native subagent `Agent(subagent_type=...)`, không còn daemon.
- Dispatch đúng: `bin/dispatch.sh`. Directive = mandate dài hạn only (deprecated cho task).
- Self-dispatch chặn. Agent → Mike phải escalate (event `question`), KHÔNG spawn Mike headless.
- **quant-skeptic**: REFUTED/INCONCLUSIVE = KHÔNG wire. Bắt buộc trước mọi thay đổi production.
- **Execution**: bot_execute.py (Python) cho đặt lệnh thật. LLM headless bị classifier block khi thao tác tiền.

### Quy chuẩn làm việc
1. Backtest: self-check 0 VND + walk-forward IS(2014–19)/OOS(2020+) + threads=1. Edge rớt OOS = loại.
2. No look-ahead: `profit_*` chỉ train, KHÔNG filter live.
3. Pin kết quả: `data/results_registry.md`. Ghi bus ngay (`append_event.sh`).
4. Human-in-the-loop: Taylor (rules) → Bill (plan, user duyệt) → Mafee (plan-bound only).
5. **Multiple-testing discipline (chốt 2026-07-05, R&D Q3 program H2, Bailey-López de Prado):** mọi
   wire production khai báo **N trials** (số config đã so sánh để tới đó) + **DSR** (Deflated Sharpe
   Ratio) trên NAV daily của config sắp deploy. **DSR < 0.95 → RED FLAG**, không wire nếu chưa có
   sign-off rõ ràng (bổ sung cho, không thay thế, gate quant-skeptic + walk-forward IS/OOS hiện có).
   Khi wire được chọn từ 1 họ ≥~8 biến thể (parking/lever/basket sweep): báo thêm **PBO** (Probability
   of Backtest Overfitting, CSCV) — PBO≥0.5 = ưu tiên config robust-trung vị thay vì IS-best. Kèm
   **per-year leave-one-out** khi edge OOS mỏng năm — 1-2 năm carry hết edge = reshuffle-luck, không
   phải signal bền (bài học Wave1/H8a-tiebreaker 2026-07-05: OOS CAGR/Calmar tăng đúng luật nhưng
   toàn bộ đến từ 2021+2023, LOO rớt → route qua skeptic trước khi wire). V2.4/R3 đã qua chuẩn DSR/PBO
   (DSR≈1.0, PBO≈0.20 — xem `data/results_registry.md` mục "DSR / PBO Robustness Annex", script
   `dsr_pbo_annex.py`).

### Cổ phiếu — quy tắc nhanh
- **BANNED vĩnh viễn**: PC1, VVS, KSF, NKG, HSG, HVN, VJC, NVL, GEG, SBA, DMC/IMP/TRA, TOS, VTP.
- Banking (MBB/ACB/HDB): Tier 1. FPT: Tier 1. CTR: Tier 2. Pharma: buy-and-hold only (timing phá alpha).
- DGC: 2 nhánh tách biệt — compounder-screen (exclude) ≠ special-situation case.
- Sector sweeps #1–9 xong: tất cả = lens/tilt, không phải standalone book (banking có OOS edge nhưng 74% trong custom30V).

### Backup / DR
`~/thanhdt/backup.sh` → GitHub `minhtrido2023/thanhdt` (private). Daily 00:00 ICT.

## Dự án đã đóng — chi tiết theo yêu cầu (đọc khi cần: `cat kb/projects/<file>.md`)
- 2026-07-20 **Deposit-rate auto-crosscheck automation** → `kb/projects/deposit-rate-autocheck.md` — DONE — refresh_deposit_rate_vn.sh tự dispatch Winston xác nhận + ghi (không cần người), 10 vòng quant-skeptic REFUTED→fix→re-review (mỗi vòng 1 lỗi thật, khác nhau) rồi CONFIRMED — kể cả 1 bug thật trong `deposit_rate_vn.current_deposit_rate()` (consumer, không phải chỉ writer).
- 2026-07-17 **DCF upgrade (earning-power · GDP terminal-g · refresh-gate)** → `kb/projects/dcf-earning-power-upgrade.md` — TRIỂN KHAI XONG — Việc1 earning-power NO-GO (giữ FCFE); Việc3 `cap_rf` = default hiển thị `dcf_valuation.py` (level fix, không alpha, DCF non-decisional); Việc2 refresh-gate cron LIVE ngày 11. quant-skeptic CONFIRMED.
- 2026-07-13 **World Cup + rổ lãi suất huy động (Pillar A′)** → `kb/projects/wc-deposit-rate-gate.md` — ĐÓNG cả 2 hướng — N quá mỏng / 0-4 GO, không wire production.
- 2026-07-13 **Plan-approval gate (second-chance cron + code-gate)** → `kb/projects/plan-approval-gate.md` — XONG — second-chance re-send 23:00 + code-gate bot_execute.py, hiệu lực 09:05 07-14 (commits 4216295/27e1282/54d488c).
- 2026-07-13 **Plan ZaloPay transition day 5/5 (FINAL)** → `kb/projects/zalopay-transition-0713.md` — XONG — bán VIB + mua BID, ngày cuối chuỗi transition 07-07→07-13.
- 2026-07-13 **DT5G BULL-giả bug → audit freshness toàn hệ thống** → `kb/projects/dt5g-bull-fake-freshness-audit.md` — KHÉP KÍN — EW-leg path fix + CRITICAL custom30V basket fix + F3 re-pin; live không sai.
- 2026-07-13 **Báo cáo tuần 07-06→07-10 + chống tái diễn** → `kb/projects/weekly-report-mechanism.md` — XONG — đã gửi + WARN check báo cáo tuần/tháng quá hạn (commit 7147ac3).
- 2026-07-13 **Audit dữ liệu 8L (mùa BCTC Q2)** → `kb/projects/8l-data-audit.md` — XONG — 8L đầy đủ; 3 fix cache/cadence/doc dispatch (Winston_20260713_103213).
- 2026-07-12 **lag_edge_health.csv staleness** → `kb/projects/lag-edge-health-staleness.md` — KHÔNG phải bug — mtime-tươi/content-cũ đọc nhầm; falsifiable check ~08-25.
- 2026-07-12 **fa_ratings/8L re-tune + rebuild builder** → `kb/projects/fa-ratings-rebuild.md` — Re-tune 8L NO-GO (16/16); rebuild fa_ratings builder HOÀN TẤT, BQ-write-identity fixed.
- 2026-07-12 **V2.5 leverage verification** → `kb/projects/v2.5-leverage-nogo.md` — NO-GO, giữ DISABLED — edge là IS-artifact (OOS âm), DSR<0.95.
- 2026-07-12 **LAG-weight (tăng tỷ trọng PEAD)** → `kb/projects/lag-weight.md` — ĐÓNG — chấp nhận kết luận mô tả, không tăng trần w_LAG.
- 2026-07-12 **Dự án momentum-deals (đóng kênh MOM_N/MOM_S)** → `kb/projects/momentum-deals.md` — KHÉP KÍN — production LIVE, re-pin R3 27.84%/1.84/-18.2/1.53 (commit 4fbd492+9df396d).
- 2026-07-12 **Dự án Q-sleeve (rổ nhỏ chất lượng cao)** → `kb/projects/q-sleeve.md` — NO-GO cả 2 trục, quant-skeptic CONFIRMED.
- 2026-07-12 **Audit sẵn sàng mùa BCTC Q2/2026** → `kb/projects/bctc-q2-readiness-audit.md` — KHÉP KÍN — fix CRITICAL LAG-blind + MEDIUM freshness + 3 mục nhỏ, đều verified.
- 2026-07-03 **Usage-limit auto-resume** → `kb/projects/usage-limit-auto-resume.md` — XONG — dispatch.sh phát hiện usage-limit → pending_resumes → resume_pending.py cron.
- 2026-07-02 **Reliability hardening (4 việc AgentOps)** → `kb/projects/reliability-hardening.md` — XONG — circuit breaker + idempotency guard + trace_id + INCIDENTS.md (commit e1d9b7c).

## Nguồn chuẩn tắc đầy đủ
Chi tiết: kb/KNOWLEDGE.md (§1-9). Dự án đã đóng: kb/projects/ (index ở trên). Events: kb/events_buffer.md. Fleet: kb/fleet_status.md.
