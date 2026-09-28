## Tri thức chung của đội (canonical — Mike biên tập; MỌI agent phải nắm)
> Cập nhật 2026-07-30. Chi tiết: `kb/KNOWLEDGE.md`. Số liệu gốc: `data/results_registry.md`.
> Codebase: `/home/trido/thanhdt/WorkingClaude` (BigQuery `tav2_bq`).
> **Mục tiêu**: vận hành chiến lược **production V2.4**, **live từ 2026-07-01**, tài khoản SpaceX (DNSE), 1B VND.

### V2.4 — chiến lược trung tâm (đã verify, self-check 0 VND, threads=1)
- = **V2.3A + custom30V parking (NEUTRAL) + gated-overflow (bear-washout) + HAG eq_flag fix**.
- 2 book: **BAL** (momentum SIGNAL_V11, yieldcombo: 1/PE + 1/PCF) + **LAG** (PEAD/earnings drift).
- Allocator w_LAG: {CRISIS 50 / BEAR 0 / NEUTRAL-BULL-EXBULL 65}, band ±10pp.
- 🆕 **PIN DẢI 2 SỐ — user chốt 2026-09-28 08:02 ICT** (registry mục **"2026-09-28 (septies)"**):
  R3 @park 0,30 = **23,37% (`pin0%`, NGƯỠNG SÀN — tiền nhàn rỗi 0%/năm) … 25,71% (`pin1M`, NGƯỠNG
  TRẦN — lãi huy động 1 tháng Big-4 cá nhân PIT trả cho MỌI tiền nhàn rỗi)**. **CẢ HAI là số pin
  chính thức, không cái nào SUPERSEDE cái nào; CẤM trích 1 số mà không kèm quy ước.** Chênh
  +2,34pp trong đó **2,05pp (87,8%) là SỐ HỌC TRỰC TIẾP** (tiền nhàn rỗi 46,4% NAV, trước trả 0%
  nay ~3,5%/năm), chỉ 0,285pp là đường giao dịch — DƯỚI sàn nhiễu W2b 0,46pp ⇒ **KHÔNG đọc là
  "hệ tốt lên"**, đây là đổi thước đo áp đều mọi phương tiện. Quy đổi thực tế ~21,9% … ~24,2%.
  ⚠️ **Neo sizing DD vẫn lấy đầu SÀN −25,2%** (KHÔNG lấy −23,6% của đầu trần) — sizing đứng ở cận
  xấu, neo thực tế KHÔNG đổi. Điểm THẬN TRỌNG trong dải = chân `dep1m_21s` FIFO = **25,24%** /
  Sharpe 2,03 / MaxDD −14,4% / Calmar 1,75 (LIFO 24,95% độ nhạy; engine KHÔNG xếp hạng được
  fifo/lifo — chênh 0,289pp dưới sàn nhiễu). quant-skeptic **CONFIRMED (medium)** 2026-09-28,
  8/8 check. ⚠️ **KHÔNG gọi là "điểm thực tế"**: lập luận "không truy lĩnh vì truy lĩnh = nhìn
  trước" SAI — trả lãi tại phiên 22 cho kỳ hạn đã đi hết là NHÂN QUẢ, nên engine TRẢ THIẾU 1-21
  ngày mỗi lô đáo hạn ⇒ số trung thực nằm strictly trong (25,24%; 25,71%). ⚠️ Phần ĐƯỜNG ĐI của
  chân này = 0,758pp = **1,6× sàn nhiễu 0,46pp** ⇒ điểm giữa KÉM CHẮC hơn hai đầu dải, đọc là
  "gần đầu trần" chứ không phải một con số chính xác.
  quant-skeptic **CONFIRMED (high)** 2026-09-27 18:18Z, 8/8 check. ⚠️ Giới hạn của `pin1M`:
  53/150 tháng là SỐ DỰNG LẠI (FiinPro không có dữ liệu ≤2018-12, cầu = NHNN 12M-thấp −2,525pp);
  upstream FiinPro-X **đã hết hạn 28/09/2026**; đây là lãi thị trường, không phải carry egg DNSE.
- **R3 NEUTRAL-only @50B: CAGR 23.37% / Sharpe 1.88 / DD −14.6% / Calmar 1.60** = **`pin0%` (đầu SÀN của dải)** — pin CHÍNH THỨC từ
  **2026-09-27 (sexies)**, Final NAV 684,52B, ledger md5 `4707bcbe…`, IS 20,00% / OOS 26,50%,
  self-check 0 VND. **Số SẠCH đầu tiên trên CẢ HAI chiều**: nhãn edge-health causal (`known_date`,
  FAIL-C đã đóng) **và** đúng knob park live 0,30. Neo sizing DD (bootstrap 5th) = **−25,2%**;
  DSR 1,0000 · PBO(68) 0,2085.
  *~~23,43% / 1,88 / −14,4% / 1,63 / 688,77B (pin quinquies)~~ SUPERSEDED làm anchor 2026-09-27* —
  lý do: đo trên nhãn LOOK-AHEAD 25 phiên (`label_col=entry`), KHÔNG phải sai mô hình/sai knob;
  Δ gỡ look-ahead = −0,06pp CAGR. **Pin = `PARK_STATES=3:0.3` = ĐÚNG knob live** (user chốt park 30% lúc 15:48 ICT
  2026-09-27, `ae81bd47` đổi `trading_rules.json` + `ETF_PARK`); ledger byte-identical với leg lưới
  `parkgrid_030` ⇒ lệch 0,00pp. Neo sizing DD mới = **−25,2%** (bootstrap 5th-pct, nhãn as-of; @nhãn cũ −25,1% — neo thực tế không đổi).
  🚨 **ĐÍNH CHÍNH — pin cũ 24,42% mang nhãn "(production)" SAI**: production THẬT từ 2026-08-04 là
  park **0,8** (= 24,95% / 1,66 / −19,8% / 1,26, chưa từng được pin), trong khi registry pin
  `PARK_STATES=3:0.7` ⇒ **số pin lệch knob live suốt 54 ngày** (cùng lớp lỗi `LAG_ADV_BASIS` 08-03).
  24,42% và 24,95% GIỮ làm lịch sử, **không còn là anchor**.
  ✅ **Ba rail park ĐÃ ĐỒNG BỘ = 0,30** (commit mike `1f15139b`): R1 MUA `ETF_PARK={3:0.30}`, R2 BÁN `compute_park_trim.py PARK_TARGET_F1 = 0.30`, R3 policy `trading_rules.json` 0.30. Trước đó R2 còn hardcode 0,80 ⇒ bot MUA tới 30% nhưng chỉ TRIM khi vượt 80%, knob user chốt KHÔNG hiệu lực (đúng lớp lỗi im lặng 08-04, đảo chiều). Cổng cơ học `bin/park_rail_consistency_selfcheck.py` đọc giá trị 3 rail bằng AST, rc=1 khi lệch — live rc=0, selftest 6/6. ⚠️ R3 vẫn CHƯA có code path nào đọc (văn bản chính sách); việc wire R2 đọc R3 chờ arch-review.
  Nguồn: `data/results_registry.md` mục "2026-09-27 (quinquies)".
  *Bối cảnh bản 24,42% (lịch sử):* (Final NAV 761,11B, ledger md5 `2f9c3702…`; SUPERSEDE 24,38%/757,61B của
  sáng cùng ngày — chênh +0,04pp do ticket 1 "OShares bước tại EX-DATE" ở chân weight, merge `5c290848`), đo trên **`universe_pit`** (point-in-time, không look-ahead).
  ⚠️ **SỬA LỖI ĐO 2026-09-27, KHÔNG ĐỔI MÔ HÌNH** — không tune tham số nào, chân weight + membership
  byte-identical, đường tiền live không đụng. Chuỗi return rổ park custom30V từng chain trên
  `mcap = Close_adj × OShares`, nên mỗi bước số CP theo QUÝ thành một ngày return GIẢ trong khi
  `Close` đã điều chỉnh hồi tố cho cùng sự kiện ⇒ đếm hai lần. Gỡ ra = **−4,48pp**. Tái lập trên
  main: md5 `3f836927`, self-check 0 VND. Knob lùi `BASKET_RETURN_OSHARES=legacy`.
  **Số cũ 28.86% / 1.90 / −17.8% / 1.62 / 1.178,01B (pin 08-03) SUPERSEDED** — giữ làm lịch sử.
  ⇒ **V2.4 không còn là hệ ~29% CAGR; ở park 0,30 (production hiện hành) là ~23,4%** (quy đổi thực tế
  ≈ 21,9%); ~24,4% là bản @park 0,7 đã SUPERSEDED.
  Phần diễn giải `LAG_ADV_BASIS` dưới đây vẫn còn hiệu lực (nó nói về VÌ SAO mặc định là `price`):
  ⚠️ **KHÔNG phải "hệ tốt lên"** — KHÔNG có thay đổi mô hình nào. Đây là **đồng bộ registry theo
  code production**: mặc định `LAG_ADV_BASIS` (cơ sở giá của ADV book LAG) đã đổi `close`→`price`
  ngày 08-02 (commit `0062aa0`, để gỡ look-ahead + giữ bất biến "trần live == trần đã mô phỏng")
  nên số pin cũ không còn tái lập được bằng lệnh pin trên code hôm nay. Chân control (`close`) tái
  lập 27.24% TUYỆT ĐỐI cả 5 chỉ tiêu + cả 2 số IS/OOS ⇒ A/B hợp lệ. **Toàn bộ chênh nằm ở IS
  (+3,28pp), OOS chỉ +0,02pp** — hệ số `Close/Price` hội tụ về 1,00 gần đây nên chỉ khác ở nửa đầu
  mẫu; **KHÔNG trích +1,62pp như "edge mới"**. Chi tiết ở `data/results_registry.md` (mục
  **2026-08-03 RE-PIN R3 THEO ĐÚNG MẶC ĐỊNH PRODUCTION `LAG_ADV_BASIS=price`**), KHÔNG lặp lại ở đây.
  **Số lịch sử KHÁC VINTAGE / KHÁC CƠ SỞ / CÓ LỖI, không so trực tiếp**: 27.24%/1.81/−18.4%/1.48
  (pin 08-02, cơ sở ADV `close` — đúng với cơ sở đó, đã SUPERSEDED); 27.60%/1.84/−17.5%/1.58 (pin
  07-29, có look-ahead cơ sở giá rổ); 27.16%/1.81/−18.1%/1.50 (pin 07-22, đã mất, không tái lập
  được); 27.84%/1.84/−18.2%/1.53 (pin 07-12, `ticker_prune`).
  ⚠️ **MIXED-universe khi trích dẫn**: `universe_pit` cho cổng quyết định, `ticker_prune` vẫn cho
  CAPIT pool/maturity. Lỗi fidelity `liq<=0` — **cơ chế nay đã tách được (T1-T5, job
  `Taylor_20260803_021414`/`_045138`, quant-skeptic CONFIRMED cao)**: giả thuyết "hiện vật sức
  chứa" BỊ BÁC BỎ hai lần bằng hai knob trực giao (`%ADV/ngày` và NAV), cả hai lần bằng SAI DẤU
  đạo hàm — không phải "chưa loại trừ được". Nhưng **MỨC thì KHÔNG tách được**: cả hai chân đứng
  trên 1 tham số mô hình fill (trần 20% ADV/phiên) mà 90-96% số phiên-fill sống Ở TRẦN đó, trong
  khi fill THẬT (DNSE) mới chỉ xác nhận tới ~3,86% ADV/phiên — 2 thiên lệch NGƯỢC CHIỀU cùng bậc
  độ lớn (+4,08pp do sửa đúng nhóm mã không mua được vs. −4,0..4,5pp do giả định fill quá lỏng)
  gần **triệt tiêu nhau**. ⇒ **24,42% (cũ: 28,86%) ĐỌC LÀ ƯỚC LƯỢNG ĐIỂM có điều kiện vào 1 tham số chưa neo**,
  KHÔNG PHẢI cận dưới, không phải cận trên (đổi nhãn 2026-08-03, thay khoảng `[~27,2%;~31,3%]`
  đã hết hiệu lực) — **không trích +3,85pp/+4,08pp/+4,11pp như edge đã kiểm chứng** ở bất kỳ
  chiều nào. Follow-up 08-04 (gate động theo executability thật) củng cố thêm: giải quyết được
  vấn đề cơ học (vị thế kẹt 35%→0%) nhưng KHÔNG cho lợi nhuận bền (đổi dấu khi bỏ 2020-2021,
  PBO cao) — cùng chữ ký reshuffle-luck. Đóng hẳn câu hỏi CHỈ bằng tích luỹ fill thật, không
  bằng backtest thêm — sổ theo dõi + **mốc cứng 2026-12-15 / 2027-03-31**:
  `kb/projects/lag-adv-filter-tracking.md`, chi tiết cơ chế: `agents/Taylor/research/
  lag_fidelity_decomp_20260803/T5_DECISION.md`.
- Bootstrap 5th-pct: **CAGR 15.6%, DD −25.1% (neo sizing DD −25,1%, KHÔNG phải −14,4%)** — trên
  ledger pin **park 0,30** (2026-09-27 quinquies); P(DD<−30%)=**1,0%**, P(SR<1,0)=1,0%; stationary
  15,4% / −24,8%. *Bản @park 0,7 SUPERSEDED: 15,5% / −30,3%; @park 0,8: DD 5th −32,0%.*
  Ghi chú cách chạy (không đổi) của bản @0,7: **theo LỊCH** (FAIL-F đã merge `3c944443`; cơ sở phiên cũ
  thổi cao giả ~+0,2-0,3pp). `bootstrap_nav.py` L=21/B=4000/seed 12345; P(DD<−30%)=5,5%,
  P(SR<1,0)=3,4%; stationary-bootstrap cross-check 15,3% / −30,0%.
  *Chuỗi số cũ SUPERSEDED: 18,6%/−28,6% (06-29) → 15,6% (cơ sở phiên) → 15,4% → **15,5%/−30,3%**.*
- **DSR/PBO đã hết trôi — họ trial nay GHIM bằng `DSR_FAMILY_MANIFEST`** (merge `f2cfb124`):
  **DSR 1,0000** (ann-SR R3 **1,815** trên ledger pin park 0,30; 1,616 ở bản @0,7). **Số pin của V2.4 là PBO = 0,2085** (chạy lại trên ledger pin park 0,30 — **không đổi**, vì CSCV
  đo trên HỌ TRIAL, ledger R3 không thuộc họ) trên họ gốc phục dựng
  68 file (`mike/research/dsr_family_manifest_20260927/man_2026_07_recon.json`, md5 `2cea9626…`) —
  khớp 0,2088 pin từ 2026-07 ⇒ phục dựng đúng. ⚠️ caveat: registry 2026-07 không lưu tên file,
  68 file này dựng lại theo `mtime`, không phải danh sách gốc.
  **PBO 0,5013 trên "họ hôm nay" (486 file) KHÔNG phải PBO của V2.4** — đó là **chỉ báo sức ép
  multiple-testing TÍCH LUỸ** của thư mục `data/` (80→0,2088 · 477→0,3993 · 486→0,5013): nó nói về
  tốc độ thử của đội, không nói về độ bền của config đang deploy. *0,3993 (bis) SUPERSEDED làm số pin.*
- **3 bản sửa đo lường ĐÃ LIVE trên main 2026-09-27** (user duyệt 13:38 ICT):
  **FAIL-F** annualize theo LỊCH 365,25 trong `bootstrap_nav.py` + `dsr_pbo_annex.py` (WC merge
  `3c944443`) — bỏ cơ sở "N/252 phiên" vốn thổi CAGR bootstrap cao giả ~+0,3pp.
  **FAIL-H** `nav_period_returns.py` có số hạng dòng tiền (TWR) + cổng NAV-jump 5% fail-closed
  (mike merge `2b6ab8ac`) — lần NẠP/RÚT đầu tiên không còn bị công bố thành lãi/lỗ giả.
  **egg** `reconcile_equity.py` cộng `egg.totalValue` (mike merge `6a89e51b`) — residual thật
  2026-09-27 còn **SpaceX +0,0281% / ZaloPay +0,0107% NAV** (trước: 9,58% / 11,96%).
- ✅ **FAIL-C ĐÓNG 2026-09-27**: CSV sinh lại có `known_date`, `asof_label_selfcheck.py` PASS 0 vi
  phạm (bản cũ FAIL 5.488/5.488, sớm 25 phiên), Δ pin = **−0,06pp CAGR / −0,2pp MaxDD / −0,03
  Calmar / −4,25B NAV** (A/B một biến, chân control byte-identical với pin ⇒ Δ đọc được). Anchor R3
  đổi 23,43% → **23,37%**; xem registry mục "2026-09-27 (sexies)". Tồn dư KHÔNG gấp, không ảnh
  hưởng số: đường LIVE `golive_recommend_v23.py:293` và `edge_health_monitor.py:188` (`neg_streak`)
  vẫn index trên `entry` — benign hôm nay (live luôn lấy dòng cuối ⇒ cùng `w_LAG=0,50`), nhưng
  `neg_streak` chạm ngưỡng sớm ~1,2 tháng.
  2026-09-27 trên ledger pin mới (`bootstrap_nav.py`, L=21/B=4000/seed 12345); stationary-bootstrap
  cross-check 15.5% / −30.1%. ⚠️ **Annualize theo LỊCH (FAIL-F, sửa 2026-09-27 job Taylor_20260927_045241, branch `fix/nav-flow-term-annualize` CHƯA merge)**: bootstrap 5th-pct CAGR theo lịch = **15,4%** (theo phiên 15,6% — cao giả +0,18pp), Sharpe R3 1,61 (hiển thị 1,62); MaxDD −30,4% / P(DD<−30%) 5,35% KHÔNG đổi; **DSR và PBO KHÔNG phụ thuộc annualize** (đính chính framing audit). ⚠️ PBO đo ở 2 cây khác nhau cho **0,40 (main) vs 0,50 (worktree)** vì họ trial là glob động ⇒ PBO KHÔNG có nghĩa cho tới khi pin `family_manifest`. *Số cũ 18.6% / −28.6% SUPERSEDED (bản chạy 06-29, pin khác).*
- **NEUTRAL parking custom30V @0,30 (production) = +1.06pp CAGR** (23.43% vs 22.37% park=0) — và ở
  30% parking làm **TỐT hơn** rủi ro: DD −16,1%→−14,4%, Calmar 1,39→**1,63**, Sharpe 1,95→1,88.
  ⚠️ 0,30 vs 0,0 **không phân biệt được bằng dữ liệu** (paired block bootstrap P=0,479) ⇒ 0,30 là
  sở thích rủi ro user chốt, không phải mức thắng có ý nghĩa thống kê.
  *Bản @park 0,7 (SUPERSEDED làm production, giữ lịch sử):* **+2.05pp CAGR** (24.42% có park vs 22.37% park=0, cùng lệnh pin,
  đổi đúng 1 biến `PARK_STATES`; 30 mã, cap 0.10). ⚠️ **"+7.4pp Full" SUPERSEDED** — lệnh gốc của số
  đó không tồn tại trong registry; ở chân return LỖI delta là +6,49pp ⇒ **~2/3 của "+7,4pp" là return
  giả từ tăng trưởng số CP.** ⚠️ **Và chiều rủi ro ĐẢO DẤU**: parking làm Sharpe 1.95→1.69,
  DD −16.1%→−18.8%, Calmar 1.39→1.30. Ở pin mới parking **mua ~2pp CAGR bằng cách làm xấu mọi chỉ
  tiêu risk-adjusted** ⇒ câu "phần tin cậy nhất" KHÔNG còn đứng trên cơ sở risk-adjusted. Giữ/bỏ
  parking là **quyết định của user**, Taylor không tự đảo.
- Bull parking: NAV ≥150B. **(30, 0.15) = OVERFIT**, walk-forward bác.
- **V2.5** (future) = V2.4 + lever MGE=1.5, account sẵn sàng, DISABLED, reminder 2026-07-07.

### ⚠️ `*_screen.py` — "8L top-25" TRƯỚC 2026-09-27 là 25 mã XẤU NHẤT (đã vá, nhưng số cũ HẾT HIỆU LỰC)

**Lỗi**: `sort_values([rating, tv], ascending=False).head(25)` rồi gọi kết quả là "8L top-25".
`fa_ratings_8l.rating` là thang **1-5 kiểu xếp hạng tín nhiệm — 1 = AAA = TỐT NHẤT** (cổng
production là `rating<=3`), nên `ascending=False` lấy đúng nhóm rating **xấu nhất**. Lặp ở
**16/20 file**; sửa = `ascending=[True, False]` (tie-break thanh khoản giảm dần vốn đã ĐÚNG).
Merge `ec9750f2` (user duyệt 19:25 ICT 2026-09-27); selfcheck `screen_sort_direction_selfcheck.py`
bằng **AST** — 20 file · 107 lệnh sort · 0 vi phạm · 0 mơ hồ, giống nhau trên 4 môi trường TZ,
**7/7 mutation bị giết**, và chạy trên bản CHƯA sửa ra đúng 16 vi phạm ⇒ bắt bug thật, không tautology.

**Mức độ sai**: 146 kỳ rebal 2014-08→2026-09 — rating trung bình rổ **4,504 → 1,252**;
**145/146 kỳ hai rổ RỜI NHAU HOÀN TOÀN** (overlap 0,01/25); số kỳ rổ **không có mã nào `rating<=3`**:
**145/146 → 0**. Ví dụ 2026-09-25: bản cũ chọn rổ `rating {4:15, 5:10}` — **có cả NVL và HAG là
BANNED vĩnh viễn**; bản sửa chọn `rating {1:8, 2:17}` (ACB CTG FPT GAS MBB VCB VNM…).

🔴 **HỆ QUẢ NGHIÊN CỨU — đừng trích số cũ nữa**: **7/9 screen từng được báo là TRỰC GIAO với
8L top-25 (0-5%) thật ra TRÙNG 21-83%** (bank_compounder 4,9→64,1% · tech G_VN 0,0→83,3% ·
pharma 0,0→69,0% · aviation INFRA 0,0→53,4% · logistics PORT 0,0→37,1% · compounder 4,0→25,8% ·
retail_compounder 0,0→21,1%). ⇒ **kết luận "sleeve này bổ sung alpha mới, không lặp 8L" KHÔNG
còn suy được từ những con số cũ.** Muốn kết luận lại thì phải đo lại, không phải đọc lại.

⚠️ **CÒN PHẢI LÀM (§8, chưa làm — cần user duyệt vì chạm artifact đã pin)**: mọi file output
`data/*_verdict.json` / `*_monthly.csv` (chứa `ortho_8l`) **hiện vẫn mang số THEO BUG**. Phải
**sinh lại 16 screen** rồi cập nhật, cho tới lúc đó đọc các file đó là đọc số sai. Đường tiền
LIVE **không** ảnh hưởng: `*_screen.py` là lens nghiên cứu/discretionary, không nuôi V2.4/park.

### Đã thử, BỊ LOẠI — không wire
custom30V permanent-exclude 7 tên (−1.0pp); LAG SUE-tilt 3 tầng (−0.66pp); hold-neutral exit (−47B);
stability floor ROE_Min<0 (−0.45pp); liq-tilt custom30 (REFUTED); deep-discount sleeve (PARKED);
pbcombo dual-vehicle (Calmar 1.48→1.37); gq_score growth gate (−IC); composite v3 as entry-selector (NO).

**MOM_N/MOM_S ĐÃ ĐÓNG (2026-07-12)** — thay đổi production chính thức, không phải "thử bị loại":
`MOMENTUM_N`+`MOMENTUM_S` gỡ khỏi `TIER_BAL` (giữ `MOMENTUM`/`MEGA` generic — vẫn đóng góp thật).
Lý do + chuỗi R&D: `kb/projects/momentum-deals.md`, `plan_close_mom_20260712.md`.

### DT5G — market regime gate
- Production: `tav2_bq.vnindex_5state_dt5g_live` qua `get_gated_state()`.
- **KHÔNG đọc** `vnindex_5state` — đó là v3.4b BASE (153 transitions ≠ DT5G 49 transitions).
- Gate phòng thủ (insurance), KHÔNG phải return-enhancer.
- State live hôm nay = `kb/current_ops.md` / `golive_state_today` (fact động, KHÔNG pin ở đây).

### 8L Rating & Composite
- Composite v3 LIVE (`rating_8l.py`): value = ey(1/PE) + cfy(1/PCF) + ps(1/PS). Golden floor: ROE_Min3Y≥0 ∧ CF_OA_3Y>0.
- **1/PE dominant factor** (IC +0.125, 94% hit). Rating = binary gate ≤3, KHÔNG phải return-tilt.
  ⚠️ **+0.125 ĐÚNG, đừng hạ** — đề xuất +0.096/+0.034 (nhân `Price/Close` "khử look-ahead") ĐÃ BỊ
  BÁC BỎ 2026-08-02: `PE` vốn đã ở cơ sở `Price` thô PIT đúng; nhân vào là ĐƯA look-ahead VÀO
  (R3 xấu −1,70pp). Xem `kb/data_registry/fundamentals/valuation_pe_pb_pcf_ps.md` "Bẫy (4)".
- Value dominates ALL regimes kể cả BULL. Moat governance: chỉ WIDE (đã audit 5F) mới notch.

### Hạ tầng giao dịch
- `bot_execute.py --auto-otp`: execution deterministic (Python, không phải LLM headless).
- **`data/BOT_STOP`** = kill-switch tức thì.
- Giờ chuẩn tắc chuỗi ngày trading (T2-T6) + xử lý khi lỗi: `kb/ops_runbook.md`. Routing Discord:
  `kb/current_ops.md`. BQ cache / auto-OTP / PHS: `kb/KNOWLEDGE.md` §4.

### Kiến trúc fleet
- **quant-skeptic**: REFUTED/INCONCLUSIVE = KHÔNG wire. Bắt buộc trước mọi thay đổi production.
- **Execution**: bot_execute.py (Python) cho đặt lệnh thật. LLM headless bị classifier block khi thao tác tiền.
- Daemon / dispatch / escalate (cơ chế đầy đủ): `MIKE.md` + `kb/KNOWLEDGE.md` §3.

### Quy chuẩn làm việc
1. Backtest: self-check 0 VND + walk-forward IS(2014–19)/OOS(2020+) + threads=1. Edge rớt OOS = loại.
2. No look-ahead: `profit_*` chỉ train, KHÔNG filter live.
3. Pin kết quả: `data/results_registry.md`. Ghi bus ngay (`append_event.sh`).
4. Human-in-the-loop: Taylor (rules) → Bill (plan, user duyệt) → Mafee (plan-bound only).
5. **Multiple-testing discipline (chốt 2026-07-05, Bailey-López de Prado):** mọi
   wire production khai báo **N trials** (số config đã so sánh để tới đó) + **DSR** (Deflated Sharpe
   Ratio) trên NAV daily của config sắp deploy. **DSR < 0.95 → RED FLAG**, không wire nếu chưa có
   sign-off rõ ràng (bổ sung cho, không thay thế, gate quant-skeptic + walk-forward IS/OOS hiện có).
   Khi wire được chọn từ 1 họ ≥~8 biến thể: báo thêm **PBO** (Probability
   of Backtest Overfitting, CSCV) — PBO≥0.5 = ưu tiên config robust-trung vị thay vì IS-best. Kèm
   **per-year leave-one-out** khi edge OOS mỏng năm — 1-2 năm carry hết edge = reshuffle-luck, không
   phải signal bền (ca Wave1/H8a-tiebreaker 2026-07-05: `kb/KNOWLEDGE.md` §8). V2.4/R3 đã qua chuẩn
   DSR/PBO — **cập nhật 2026-09-27: DSR 1.0000 (vẫn ≥0.95), PBO 0.3993 (cũ 0.2088)**. PBO tăng
   KHÔNG do bug return mà do HỌ TRIAL nở **80 → 477 CSV** (`family_paths()` là glob động ⇒ mỗi
   backtest R&D mới tự nhập họ). ⇒ **PBO đã pin KHÔNG tái lập được theo thời gian**; muốn so sánh
   được phải pin danh sách file (`family_manifest`) — CHƯA LÀM. Nguồn: `data/results_registry.md`
   mục "DSR / PBO Robustness Annex" + "2026-09-27 (bis) HẬU KIỂM SAU MERGE `a808a613`".

### Cổ phiếu — quy tắc nhanh
- **BANNED vĩnh viễn**: PC1, VVS, KSF, NKG, HSG, HVN, VJC, NVL, GEG, SBA, DMC/IMP/TRA, TOS, VTP, BAF
  (thêm 2026-08-26 — leverage trap + capital market extraction, xem `kb/KNOWLEDGE.md` §6).
- Banking (MBB/ACB/HDB): Tier 1. FPT: Tier 1. CTR: Tier 2. Pharma: buy-and-hold only (timing phá alpha).
- DGC: 2 nhánh tách biệt — compounder-screen (exclude) ≠ special-situation case.
- Sector sweeps #1–9 (đã đóng, kết luận lens/tilt): `kb/KNOWLEDGE.md` §7.

## Mandate — Margin crisis sleeve Loại-2 adaptive (chốt 2026-08-25, user duyệt)

**Thị trường VN có 90%+ nhà đầu tư cá nhân → overreaction là đặc trưng CẤU TRÚC, không phải noise.**
Framework margin cho khủng hoảng phải ADAPTIVE theo loại crisis, không phải rigid policy chỉ đúng cho thị trường đã trưởng thành.

**Phân loại Bobby (real-time BLIND):**
- **Loại 1** — STRUCTURAL/MULTI_YEAR: tự củng cố, giải quyết lâu (VN 2008-2012) → KHÔNG margin
- **Loại 2** — CONFIDENCE_LIQUIDITY/CONTAINABLE: có policy anchor rõ, phục hồi nhanh hơn (2020, 2022-23) → CÓ THỂ margin với 3 điều kiện

**3 điều kiện bắt buộc (ANĐ — thiếu 1 = KHÔNG escalate):**
1. Bobby Loại-2 **real-time BLIND** (chạy TRƯỚC khi biết forward return — tránh hindsight)
2. PIT filter PASS (universe_pit — không dùng ticker_prune cho quyết định này)
3. ≥1 chỉ báo overreaction xác nhận (VIX spike / intermarket dislocate / breadth collapse cực đoan)
→ Kết quả: ESCALATE lên Mike + user — KHÔNG auto-trade, KHÔNG bypass human-in-the-loop

**Statistical significance sai tool cho N=3-5 crisis** — dùng causal framework + human judgment.
Observable indicators + escalation process là deliverable đúng, không phải auto-trade rule.

**Trần (xác nhận 2026-08-25, Spyros CONDITIONAL-APPROVE):**
- Equity sleeve: ≤5% NAV vốn tự có (cơ sở: 1% NAV max loss / 20% exit kỷ luật = 5%)
- Exposure: ≤6,5% NAV (≠ ≤5% — f=1,3 của RocketX thật, không phải f=2,0 giả định)
- Bobby confidence "ambiguous" (vd 2018): size −50% = ≤2,5% NAV equity

**Chi tiết framework + payload escalate:** `agents/Taylor/research/crisis_margin_framework_adaptive_20260825.md`
**Chính sách đầy đủ (đơn mã + sleeve Loại-2):** `kb/projects/discretionary-margin-policy-20260823.md`

## Quy ước phân tích conditional — trục 2 mặc định (chốt 2026-08-22, user duyệt)

**Breadth-tercile PIT thay Value Radar zone làm trục 2 mặc định cho mọi phân tích conditional.**

⚠️ **RANH GIỚI HIỆU LỰC — đọc trước khi dùng (bổ sung 2026-09-27, job `Taylor_20260927_022338`).**
Trục này được chọn **CHỈ vì CẤU TRÚC MẪU**, không vì nó tách được lợi suất hay IC:
- **KHÔNG có bằng chứng trục này tách tín hiệu.** 08-22: **0/27 ô** qua BH FDR 10% (radar: 0/24 —
  hai trục HOÀ). Chính báo cáo gốc §7 viết **"KHÔNG wire"** và §6.3 "tốt hơn để **MÔ TẢ**, không
  phải để wire". Job E 2026-09-27 đo lại bằng thước khác (IC cross-sectional momentum/value) trên
  **12,6 năm** (IS 72 tháng / OOS 80 tháng): **0/4** — `ic_mom` đảo dấu IS +0,057 → OOS −0,038;
  `ic_ey` từ −0,082 (p_BH 0,0030, CI loại 0, đơn điệu) về +0,003 (p 0,886) = **artifact IS**.
  Không phải lỗi cửa sổ ngắn: hỏng y hệt trên cửa sổ dài gấp 1,6×.
- ⇒ Dùng để **MÔ TẢ / phân tầng mẫu**. **Đừng suy ra tín hiệu từ nhãn ô**, đừng coi "trục mặc
  định" là "trục có thông tin". (H5 2026-09-26 đã đọc quá nghĩa đúng theo hướng này rồi báo
  "trục mặc định trượt 4/4" — nó trượt một tiêu chí 08-22 chưa bao giờ tuyên bố đạt.)
- **Không trục nào khác qua được cùng chuẩn**: job E so 3 trục cùng khuôn (breadth / retail_net_share
  / DT5G state) = **0/12**. `retail_net_share` giữ được cùng dấu IS&OOS nhưng IS chỉ 9/7/5 tháng và
  **nguồn chết 28/09/2026** ⇒ không phải ứng viên thay thế.

Lý do (nguyên văn 08-22, vẫn đúng — tái lập CHÍNH XÁC 2026-09-27):
- Value Radar zone ≈ kỷ nguyên: 54% số năm bị 1 nhãn chiếm ≥90% phiên → n_effective ~2-3 chu kỳ, không bao giờ đủ sức thống kê
- Breadth-tercile PIT: **0%** năm bị 1 nhãn chiếm ≥90%; **2,0×** số episode so với radar (262 vs 131)

Cách tính breadth chuẩn — **định nghĩa đầy đủ, 3 chi tiết dưới đây từng làm tái lập lệch**:
- Nguồn: `tav2_mike.universe_pit` (CANONICAL)
- breadth_t = COUNT(Close_t > MA200_t | in_universe=True) / COUNT(in_universe=True)
  **Mẫu số chỉ đếm mã có `MA200` KHÔNG NULL.** Tính từ `data/bq_cache/ticker` mà không lọc
  `MA200 IS NOT NULL` → breadth 2016 ra **0,243 thay vì 0,730** (`bq-cache` registry, bẫy MA200 NULL
  2015-2017). Lọc đúng: corr 0,999954 với chuỗi gốc.
- Phân loại phiên t: dùng breadth_{t-1} (PIT, không look-ahead cùng phiên).
  ⚠️ **Đây KHÔNG phải biến thể sinh ra bảng §4 của báo cáo gốc** — bảng đó dùng breadth CÙNG PHIÊN
  (look-ahead corr **+0,109**, báo cáo tự thừa nhận) và §5a của chính nó cho thấy **trễ 1 phiên là
  mất tính đơn điệu**. Hai chuỗi cho số khác nhau đáng kể (ô HIGH excess **+5,5pp vs +16,6pp**, thứ
  tự tercile ĐẢO). Trích số 08-22 thì phải nói rõ biến thể nào.
- Tercile: phân vị rolling **252 phiên trước** (không phân vị toàn mẫu). Quy ước tie của bản gốc:
  `(# trong 252 phiên trước < breadth_t) / 253` — 4 quy ước hợp lý khác cho LOW 1.224-1.226 thay vì
  **1.232**. Và `pd.cut([0,1/3,2/3,1])` **ném mất `pct==0,0`** (63 phiên breadth thấp nhất lịch sử,
  tức các phiên VNI xấu nhất) ⇒ excess ô LOW tụt +27,4pp → +14,7pp. Dùng ngưỡng tường minh.

Value Radar vẫn giữ vai trò DISPLAY-ONLY trong báo cáo (§6b coding_guidelines). Không wire vào sizing.

Kết quả dẫn tới quyết định: breadth-vs-radar-matrix-20260822 (Taylor, B2) + user confirm 2026-08-22.
Tái kiểm + ranh giới hiệu lực: `agents/Taylor/research/breadth_tercile_recheck_20260927/report.md`
(bus `finding:breadth-tercile-08-22-recheck`, verdict **A — quy ước ĐỨNG, không đổi trục**).

## QUY TẮC — DNSE điều chỉnh giá vị thế TỐI TRƯỚC ngày ex-date (user chốt 2026-09-12, bài học lặp ≥3 lần)
**Sự thật broker:** DNSE cập nhật `marketPrice` của vị thế theo giá đã điều chỉnh corp-action vào
**tối hôm trước ex-date** (T−1 evening), trong khi `close_price` BQ tới lúc đó vẫn là giá CHƯA
điều chỉnh. ⇒ xcheck NAV lệch đúng bằng giá trị quyền là **KỲ VỌNG, không phải stuck, không cần
verify DNSE, không escalate**. Ca chuẩn: DGC 11/09/2026 tối T6 — BQ 46.750 vs broker 38.750, cổ
tức tiền 8.000đ (2 đợt 3.000+5.000) ex-date T2 14/09 ⇒ 46.750−8.000 = 38.750 khớp chính xác.

⚠️ **PHẢI TÁCH HAI LỚP — sửa 2026-09-12 sau arch-review (job Wags_20260912_052122), bản trước gộp
chung và sẽ dạy làm SAI:**
- **Cổ tức TIỀN MẶT** (DGC 09-11): broker chỉ đổi GIÁ. NAV vẫn mark **giá CUM của phiên đó**
  (không phải giá broker đã điều chỉnh) — vì `cum_dividend_double_count` (§21) đã loại khoản
  phải thu ra khỏi tiền; lấy giá broker mà vẫn loại khoản phải thu thì NAV **hụt đúng bằng cổ
  tức** (ca DGC: 80 triệu = −8,1% NAV ZaloPay). Đây là ca DUY NHẤT được tự động cho qua.
- **Cổ tức bằng CỔ PHIẾU / thưởng / tách** (VHM 08-05, MBB 08-11, VIB 09-09): broker đổi **CẢ giá
  LẪN khối lượng** cùng lúc — đo thật trên `dnse_raw_2026-09-09.jsonl` 19:07: VIB openQuantity
  500→547 **và** marketPrice 15.050→13.700 trong cùng bản ghi. Vị thế LIVE (qty MỚI) nhân giá CUM
  ⇒ NAV thổi phồng (VIB +711.100đ; VHM 1:1 sẽ là +100% giá trị vị thế). ⇒ **VẪN CHẶN, cần người
  xử lý** — không có ngoại lệ tự động.
**Cách xử lý khi gặp:** tra ex-date mã đó (`tav2_bq.corporate_action` qua
`corp_action_lib.pricing_events` — KHÔNG dùng `events()` executed_only, nó trả rỗng đúng ngày cần).
⛔ **Cơ chế tự nhận diện CHƯA được wire — tới 2026-09-12 việc này vẫn làm TAY.** Bản nháp
(`expected_exdate_adjustment` trong `daily_nav_snapshot.py`, selfcheck 29/29) bị arch-review vòng 2
trả NEEDS_CHANGES và đã được GỠ khỏi cây làm việc, cất ở
`agents/Wags/research/nav_exdate_xcheck_wip_20260912.patch`. Lý do đáng nhớ: cổng ghép cặp của nó
kiểm PROXY (`cum_div["warnings"]`) chứ không kiểm BẤT BIẾN "khoản cổ tức phải thu của chính mã được
miễn đã bị trừ khỏi tiền" — mà `cum_dividend_double_count` có nhánh `delta<=0` trả `amount=0,
warnings=[]` IM LẶNG (đo thật `--date 2026-09-12`: 80 triệu vẫn nằm trong `totalCash`) ⇒ nới cổng
trong trạng thái đó sẽ đếm 2 lần đúng 80 triệu (+8,15% NAV, lọt cổng sanity ±15%) và ghi thẳng vào
`nav_history`. Nghĩa là: **tự động hoá SAI ở đây còn tệ hơn tự tay xử lý mỗi quý vài lần.**
Runbook thao tác tay: `kb/ops_runbook.md` § PRICE_XCHECK.

## QUY TẮC — Case có vấn đề PHÁP LÝ: vẫn phân tích như bình thường, chỉ WARNING tình trạng pháp lý (user chốt 2026-09-27 23:51 ICT)

**Chỉ đạo nguyên văn:** *"Những case pháp lý, nếu có báo cáo tài chính thì cứ dựa báo cáo phân
tích như bình thường, chỉ warning về tình trạng pháp lý nếu có thôi."*

Áp dụng cho MỌI agent làm định giá / due-diligence / báo cáo (Taylor, DollarBill, Wendy,
fundamental-skeptic):
- Có BCTC ⇒ **phân tích bình thường** trên số liệu đó (định giá, dự báo quý, DCF, nhận định).
  KHÔNG tự từ chối phân tích, KHÔNG tự hạ kết luận, KHÔNG tự loại mã chỉ vì có yếu tố pháp lý.
- Tình trạng pháp lý đi vào báo cáo dưới dạng **WARNING tường minh** (nêu sự việc + nguồn +
  ảnh hưởng đã biết), KHÔNG phải một cổng chặn ngầm.
- **Không đổi** 3 cổng đã có, chúng độc lập với luật này: `BANNED` vĩnh viễn (hằng số trong
  code), `excluded_tickers` per-account (vd DGC ở ZaloPay), và `data/forensic_flags.csv`
  `severity=exclude`. Luật này nói về **cách VIẾT phân tích**, không nới cổng nào.
- Rủi ro pháp lý của việc **lưu trữ/công bố** ghi chú pháp lý (vd đưa `forensic_flags.csv` vào
  mirror GitHub): **user tự đánh giá và tự báo khi có thông tin** — không cần Mike chặn chờ
  legal-vn soát trước.

Liên quan: `kb/current_ops.md` (DGC 2 nhánh tách biệt), §21 (UNVERIFIED thì CẤM công bố tỉ suất
— đó là cổng SỐ LIỆU, không phải cổng pháp lý).
