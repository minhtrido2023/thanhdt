# R3 / V2.4 — lịch sử pin, số SUPERSEDED, diễn giải đo lường
> Chuyển nguyên văn từ `kb/canonical.md` (trim context_pack 2026-10-08). Dải pin hiện hành
> 23,37%…25,71%, neo DD −25,2%, luật cấm trích 1 số vẫn ở `kb/canonical.md`. Nguồn chuẩn: `data/results_registry.md`.

## Chuyển từ kb/canonical.md L18-36 (trim 2026-10-08, Wags_20261008_133659) — Dải pin — điểm thận trọng 25,24%, chân maturity 25,34%, min_age, giới hạn pin1M
  xấu, neo thực tế KHÔNG đổi. Điểm THẬN TRỌNG trong dải = chân `dep1m_21s` FIFO = **25,24%** /
  Sharpe 2,03 / MaxDD −14,4% / Calmar 1,75 (LIFO 24,95% độ nhạy; engine KHÔNG xếp hạng được
  fifo/lifo — chênh 0,289pp dưới sàn nhiễu). quant-skeptic **CONFIRMED (medium)** 2026-09-28,
  8/8 check. ⚠️ **KHÔNG gọi là "điểm thực tế"**: lập luận "không truy lĩnh vì truy lĩnh = nhìn
  trước" SAI — trả lãi tại phiên 22 cho kỳ hạn đã đi hết là NHÂN QUẢ, nên engine TRẢ THIẾU 1-21
  ngày mỗi lô đáo hạn ⇒ số trung thực nằm strictly trong (25,24%; 25,71%). ⚠️ Phần ĐƯỜNG ĐI của
  chân này = 0,758pp = **1,6× sàn nhiễu 0,46pp** ⇒ điểm giữa KÉM CHẮC hơn hai đầu dải, đọc là
  "gần đầu trần" chứ không phải một con số chính xác.
  ✅ **Chân TRẢ KHI ĐÁO HẠN = điểm TRUNG THỰC của luật user = 25,34%** (FIFO; LIFO 25,42%), nằm
  strictly trong dải, quant-skeptic **CONFIRMED (high)** 2026-09-28 06:11Z 8/8. Chênh với 25,24%
  chỉ **+0,10pp = 1/5 sàn nhiễu** ⇒ **GIỮ 25,24% làm số chính, KHÔNG re-pin** (cận dưới đã verify,
  sizing đứng cận xấu). ⚠️ Đổi sang quy ước đúng làm SỐ HỌC tăng (+1,116→+1,520pp) nhưng ĐƯỜNG ĐI
  GIẢM (+0,758→**+0,448pp, DƯỚI sàn nhiễu**) ⇒ **cảnh báo "1,6× sàn nhiễu" KHÔNG áp dụng cho chân
  maturity**. ✅ **min_age là CAO NGUYÊN**: 20/21/22/23 = 25,35/25,24/25,22/25,21 — biên độ toàn
  dải 0,14pp = 30% sàn nhiễu ⇒ pin KHÔNG nhạy tham số (KHÔNG chứng minh 21 tối ưu, chỉ chứng minh
  chọn trong 20-23 không quan trọng). Chi tiết: registry §4b + §4c.
  quant-skeptic **CONFIRMED (high)** 2026-09-27 18:18Z, 8/8 check. ⚠️ Giới hạn của `pin1M`:
  53/150 tháng là SỐ DỰNG LẠI (FiinPro không có dữ liệu ≤2018-12, cầu = NHNN 12M-thấp −2,525pp);
  upstream FiinPro-X **đã hết hạn 28/09/2026**; đây là lãi thị trường, không phải carry egg DNSE.

## Chuyển từ kb/canonical.md L42-89 (trim 2026-10-08, Wags_20261008_133659) — Pin quinquies SUPERSEDED, đính chính 24,42%, ba rail park 0,30, bối cảnh 24,42%, sửa lỗi đo 09-27, LAG_ADV_BASIS, số lịch sử khác vintage, MIXED-universe, fidelity liq<=0
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

## Chuyển từ kb/canonical.md L93-99 (trim 2026-10-08, Wags_20261008_133659) — Bootstrap 5th-pct (quinquies) + chuỗi SUPERSEDED
- Bootstrap 5th-pct: **CAGR 15.6%, DD −25.1% (neo sizing DD −25,1%, KHÔNG phải −14,4%)** — trên
  ledger pin **park 0,30** (2026-09-27 quinquies); P(DD<−30%)=**1,0%**, P(SR<1,0)=1,0%; stationary
  15,4% / −24,8%. *Bản @park 0,7 SUPERSEDED: 15,5% / −30,3%; @park 0,8: DD 5th −32,0%.*
  Ghi chú cách chạy (không đổi) của bản @0,7: **theo LỊCH** (FAIL-F đã merge `3c944443`; cơ sở phiên cũ
  thổi cao giả ~+0,2-0,3pp). `bootstrap_nav.py` L=21/B=4000/seed 12345; P(DD<−30%)=5,5%,
  P(SR<1,0)=3,4%; stationary-bootstrap cross-check 15,3% / −30,0%.
  *Chuỗi số cũ SUPERSEDED: 18,6%/−28,6% (06-29) → 15,6% (cơ sở phiên) → 15,4% → **15,5%/−30,3%**.*

## Chuyển từ kb/canonical.md L102-105 (trim 2026-10-08, Wags_20261008_133659) — DSR/PBO — họ gốc 68 file + caveat mtime
  đo trên HỌ TRIAL, ledger R3 không thuộc họ) trên họ gốc phục dựng
  68 file (`mike/research/dsr_family_manifest_20260927/man_2026_07_recon.json`, md5 `2cea9626…`) —
  khớp 0,2088 pin từ 2026-07 ⇒ phục dựng đúng. ⚠️ caveat: registry 2026-07 không lưu tên file,
  68 file này dựng lại theo `mtime`, không phải danh sách gốc.

## Chuyển từ kb/canonical.md L116-118 (trim 2026-10-08, Wags_20261008_133659) — FAIL-C đóng — A/B
- ✅ **FAIL-C ĐÓNG 2026-09-27**: CSV sinh lại có `known_date`, `asof_label_selfcheck.py` PASS 0 vi
  phạm (bản cũ FAIL 5.488/5.488, sớm 25 phiên), Δ pin = **−0,06pp CAGR / −0,2pp MaxDD / −0,03
  Calmar / −4,25B NAV** (A/B một biến, chân control byte-identical với pin ⇒ Δ đọc được). Anchor R3

## Chuyển từ kb/canonical.md L123-124 (trim 2026-10-08, Wags_20261008_133659) — Ghi chú bootstrap/FAIL-F branch/PBO 2 cây (viết trước merge 3c944443/f2cfb124)
  2026-09-27 trên ledger pin mới (`bootstrap_nav.py`, L=21/B=4000/seed 12345); stationary-bootstrap
  cross-check 15.5% / −30.1%. ⚠️ **Annualize theo LỊCH (FAIL-F, sửa 2026-09-27 job Taylor_20260927_045241, branch `fix/nav-flow-term-annualize` CHƯA merge)**: bootstrap 5th-pct CAGR theo lịch = **15,4%** (theo phiên 15,6% — cao giả +0,18pp), Sharpe R3 1,61 (hiển thị 1,62); MaxDD −30,4% / P(DD<−30%) 5,35% KHÔNG đổi; **DSR và PBO KHÔNG phụ thuộc annualize** (đính chính framing audit). ⚠️ PBO đo ở 2 cây khác nhau cho **0,40 (main) vs 0,50 (worktree)** vì họ trial là glob động ⇒ PBO KHÔNG có nghĩa cho tới khi pin `family_manifest`. *Số cũ 18.6% / −28.6% SUPERSEDED (bản chạy 06-29, pin khác).*

## Chuyển từ kb/canonical.md L129-135 (trim 2026-10-08, Wags_20261008_133659) — Parking @0,7 SUPERSEDED + +7.4pp Full SUPERSEDED
  *Bản @park 0,7 (SUPERSEDED làm production, giữ lịch sử):* **+2.05pp CAGR** (24.42% có park vs 22.37% park=0, cùng lệnh pin,
  đổi đúng 1 biến `PARK_STATES`; 30 mã, cap 0.10). ⚠️ **"+7.4pp Full" SUPERSEDED** — lệnh gốc của số
  đó không tồn tại trong registry; ở chân return LỖI delta là +6,49pp ⇒ **~2/3 của "+7,4pp" là return
  giả từ tăng trưởng số CP.** ⚠️ **Và chiều rủi ro ĐẢO DẤU**: parking làm Sharpe 1.95→1.69,
  DD −16.1%→−18.8%, Calmar 1.39→1.30. Ở pin mới parking **mua ~2pp CAGR bằng cách làm xấu mọi chỉ
  tiêu risk-adjusted** ⇒ câu "phần tin cậy nhất" KHÔNG còn đứng trên cơ sở risk-adjusted. Giữ/bỏ
  parking là **quyết định của user**, Taylor không tự đảo.

## Chuyển từ kb/canonical.md L212-216 (trim 2026-10-08, Wags_20261008_133659) — Quy chuẩn #5 — cập nhật DSR/PBO 2026-09-27 (bis), trước manifest
   DSR/PBO — **cập nhật 2026-09-27: DSR 1.0000 (vẫn ≥0.95), PBO 0.3993 (cũ 0.2088)**. PBO tăng
   KHÔNG do bug return mà do HỌ TRIAL nở **80 → 477 CSV** (`family_paths()` là glob động ⇒ mỗi
   backtest R&D mới tự nhập họ). ⇒ **PBO đã pin KHÔNG tái lập được theo thời gian**; muốn so sánh
   được phải pin danh sách file (`family_manifest`) — CHƯA LÀM. Nguồn: `data/results_registry.md`
   mục "DSR / PBO Robustness Annex" + "2026-09-27 (bis) HẬU KIỂM SAU MERGE `a808a613`".

