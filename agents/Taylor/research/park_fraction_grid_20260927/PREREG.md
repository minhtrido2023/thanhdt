# PREREG — quét lưới PARK FRACTION custom30V (NEUTRAL) trên bản CANONICAL đã sửa 2 chân

**Viết TRƯỚC khi chạy leg nào.** Job `Taylor_20260927_064747`. Paper-only, **không** đổi
`trading_rules.json`. Cây đo = **main canonical @`f2cfb124`** (đã merge ticket 1 = chân weight
`OShares` bước tại ex-date; chân return `OShares` đã merge ở `a808a613` trước đó).

## 1. Câu hỏi
`trading_rules.json` v2.3 `neutral_parking.default_park_of_idle_pct = 0.8` (user chốt 2026-08-04).
Căn cứ gốc của 0.8 = "80% thắng Calmar cả dải (1,63 vs 70%=1,62 vs 85%=1,62)" — **biên 0,01 Calmar,
đo trên chân return LỖI**. Registry `## 2026-09-27 (bis) §7` đã cho thấy ở chân return ĐÚNG, Calmar
**đơn điệu giảm** theo park% (0%:1,39 → 70%:1,30 → 80%:1,24 → 85%:1,20) ⇒ đỉnh cũ không còn tồn tại.
User (13:38 ICT 27/09) yêu cầu **MỘT CON SỐ CỤ THỂ** thay cho 0.8.

## 2. Mục tiêu chọn — KHAI BÁO TRƯỚC, không đổi sau khi thấy số
1. **Hàm mục tiêu chính: tối đa Calmar** (quy ước KB `§Quy chuẩn backtest`).
2. **Ràng buộc rủi ro:** bootstrap **5th-pct MaxDD** của mức được chọn **không xấu hơn mức park=0
   quá 2,0pp** (tuyệt đối, ví dụ park=0 cho −28,0% ⇒ trần cho phép −30,0%). Mức vi phạm ràng buộc
   bị loại KHỎI tập ứng viên trước khi so Calmar.
3. **Tie-break:** Sharpe (cao hơn thắng). Nếu vẫn ngang → mức park THẤP hơn thắng (ít can thiệp hơn,
   ít phụ thuộc vào một thành phần kiến trúc hơn).
4. **Công bố thêm (không phải hàm mục tiêu):** *"CAGR mua được mỗi 1pp DD"* = ΔCAGR / Δ|MaxDD| giữa
   hai mức KỀ NHAU trên lưới. Đây là số để user tự chọn nếu user coi trọng CAGR tuyệt đối hơn Calmar.

## 3. Lưới
`PARK_STATES="3:x"` với **x ∈ {0, 0,3, 0,5, 0,6, 0,7, 0,75, 0,8, 0,9, 1,0}** — 9 leg.
Bước lưới cố ý **không đều**: dày 0,05-0,10 trong vùng 0,6-0,8 (vùng quyết định, chứa cả 0,7 và 0,8
đang tranh chấp), thưa 0,2-0,3 ở hai đầu (chỉ cần biết hình dạng). `x` = tỷ lệ TIỀN NHÀN RỖI được
park vào rổ custom30V khi state = 3 (NEUTRAL).

## 4. Phân biệt ĐỈNH THẬT vs NHIỄU — tiêu chí đặt trước
- **(a) Tiêu chí đơn điệu.** Nếu Calmar đơn điệu (không đổi dấu độ dốc) trên toàn lưới ⇒ **không có
  đỉnh nội** ; "đỉnh" là một trong hai đầu lưới và kết luận là hướng, không phải điểm. Khi đó
  KHÔNG chạy leave-one-year-out để "tìm đỉnh" (không có gì để tìm) — chỉ báo hướng + trình 2 phương
  án cho user như dispatch yêu cầu.
- **(b) Ngưỡng phân giải.** Với 9 điểm, không có CI, cùng một vintage dữ liệu, coi hai mức là
  **KHÔNG phân biệt được** nếu |ΔCalmar| ≤ **0,03** (bằng cỡ biên mà quyết định 08-04 đã dựa vào và
  đã chứng minh là nhiễu: 0,01-0,02). Mọi mức trong dải ±0,03 Calmar quanh mức đề xuất phải được
  công bố là "không phân biệt được" = khoảng tin cậy thô.
- **(c) Leave-one-year-out** (chỉ chạy nếu có đỉnh NỘI): tại 3 mức quanh đỉnh Calmar, tính lại
  Calmar khi **bỏ lần lượt từng năm lịch** (2014…2026; chuỗi return nối liền, bỏ toàn bộ phiên của
  năm bị bỏ). Nếu vị trí đỉnh **đổi sang mức khác >1 lần** trong 13 lần bỏ ⇒ đỉnh là
  **reshuffle-luck** ⇒ khuyến nghị **mức robust-trung vị** (mức thắng ở nhiều lần bỏ nhất / mức
  trung vị của các mức thắng), KHÔNG phải đỉnh IS.

## 5. Lệnh pin — bắt buộc giống hệt mọi leg, đổi ĐÚNG MỘT biến `PARK_STATES`
`run_leg.sh` (bản sao `c30v_hau_kiem_20260927/run_main2.sh`, `"$@"` đứng **CUỐI** — `run_main.sh`
đặt `PARK_STATES` sau `env "$@"` nên override của caller là **no-op im lặng**, đã cắn thật ở job
`_043541`; xác minh bằng dòng log `parking policy (cash_etf_states)`):
```
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate  BQ_CACHE_THREADS=1
NAV_TOTAL_B=50  ETF_LIQ=custompitg  BASKET_WT=namecap  BASKET_SELECT=yieldcombo
AUDIT_END=2026-06-19  BASKET_CA_SNAPSHOT=data/snapshots/corp_action_share_20260927.parquet
EXP_TAG=parkgrid_<xxx>  PARK_STATES=3:<x>
$DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge
```
`EXP_TAG` không canonical (§8 coding_guidelines) ⇒ CSV ra
`..._exp_parkgrid_<xxx>_univpit.csv`. `BASKET_OSHARES_STEP` để mặc định = `exdate` (production sau
ticket 1). `BASKET_CA_SNAPSHOT` ghim vintage corp-action ⇒ tái lập được về sau.

## 6. Cổng chất lượng mỗi leg (fail ⇒ leg bị loại, báo thẳng, KHÔNG ước lượng bù)
- `self-check BAL+LAG = 0 VND`.
- Log phải in `parking policy (cash_etf_states) {3: <x>}` **đúng bằng x** (chống no-op im lặng).
- **Neo đồng vintage:** leg `x=0` phải cho CAGR **22,37%** (bis §7, chân rổ không được dùng khi
  park=0 ⇒ phải trùng khít); `x=0,7` và `x=0,8` phải khớp bis §7 **+0,00…+0,05pp** (ticket 1 chỉ
  +0,04pp ở x=0,7). Lệch lớn hơn ⇒ có biến khác đã đổi, DỪNG và điều tra, không báo số.

## 7. Đo thêm cho mỗi leg
- CAGR / Sharpe / MaxDD / Calmar / Final NAV (quy ước lịch, `simulate_holistic_nav.metrics`).
- Walk-forward **IS 2014-2019 / OOS 2020+** (`extract_peryear.py` trên chính CSV của leg).
- **Bootstrap** `bootstrap_nav.py` (circular block L=21, B=4000, seed 12345, quy ước LỊCH sau
  FAIL-F): 5th-pct CAGR & 5th-pct MaxDD. Đây là input cho ràng buộc §2.2.
- **Haircut thuế cổ tức FAIL-D áp SỐ HỌC** (không chạy lại backtest): `k = 5,095%`
  (thuế 5% + phí 0,1%×(1−thuế)), drag = `1 − Π(1 − k·DY_kỳ·park_share_kỳ)^(1/yrs)`, với `DY_kỳ` lấy
  nguyên từ `part2/dy_by_rebal.csv` (49 kỳ) và `park_share_kỳ` **đo THẬT trên CSV của chính leg đó**
  (`(bal_etf_ref + lag_etf_ref)/combined_nav`, trung bình trong cửa sổ hiệu lực của kỳ) — KHÔNG giả
  định park_share tỷ lệ tuyến tính với x.

## 8. Giới hạn phải công bố kèm (không được bỏ)
- Cả 9 leg **cùng một vintage** `bq_cache_asof20260729_postrestate` và cùng một tham số fill chưa
  neo (trần 20% ADV/phiên — `kb/projects/lag-adv-filter-tracking.md`).
- 9 điểm, **một đường đi lịch sử duy nhất**; bootstrap chỉ đo bất định LẤY MẪU trên chính phân phối
  đó, không mô hình hoá đổi chế độ ⇒ CI là **biên DƯỚI** của bất định thật.
- **KHÔNG tự đổi quyết định user.** Đầu ra là MỘT SỐ đề xuất + khoảng không-phân-biệt-được; áp vào
  LIVE cần user duyệt + quant-skeptic (Mike chạy sau).

---

## AMENDMENT 1 — 27/09/2026 ~14:25 ICT, viết TRƯỚC khi chạy 3 leg mới
**Sự việc:** 6/9 leg đầu (x = 0 / 0,3 / 0,5 / 0,6 / 0,7 / 0,8) cho một **ĐỈNH NỘI ở x = 0,3**
(Calmar 1,63 vs 1,39 ở x=0 và 1,45 ở x=0,5; MaxDD thực **−14,4%**, TỐT HƠN cả park=0 là −16,1%).
Lưới gốc §3 cố ý thưa ở đầu thấp (0 → 0,3 → 0,5) vì bis §7 gợi ý Calmar đơn điệu giảm — **giả định
đó SAI**, nên chính vùng quyết định giờ lại là vùng lưới thưa nhất.

**Bổ sung 3 leg, khai báo trước khi biết kết quả:** x ∈ {**0,1 · 0,2 · 0,4**} — thuần **làm dày lưới
quanh đỉnh nội**, cùng lệnh pin, đổi đúng `PARK_STATES`. KHÔNG thêm biến nào khác, KHÔNG đổi hàm mục
tiêu §2, KHÔNG đổi ngưỡng phân giải §4b (0,03 Calmar) hay ràng buộc §2.2 (2,0pp trên 5th-pct MaxDD).
Lưới cuối = 12 điểm. Đỉnh nội ⇒ **kích hoạt leave-one-year-out §4c** ở 3 mức quanh đỉnh.

## AMENDMENT 2 — cùng lúc: cổng NEO §6 FAIL ở x=0,8, phải phân tách trước khi báo số
`x=0,8` cho CAGR **24,95%** so với bis §7 **24,66%** = **+0,29pp**, vượt trần +0,05pp của §6.
(`x=0` khớp KHÍT 22,37%/1,39; `x=0,7` cho md5 CSV `2f9c3702…` **trùng byte** với leg
`wexd2_new_exdate` của ticket 1 ⇒ hai neo kia PASS.) Giả thuyết: biên của ticket 1 (chân weight
`OShares` ex-date) **không hằng số theo x** — ở x=0,7 là +0,04pp, ở x=0,8 có thể lớn hơn vì tỷ trọng
rổ lớn hơn. **Kiểm bằng control, không bằng suy luận:** chạy thêm `parkgrid_070q` / `parkgrid_080q`
với `BASKET_OSHARES_STEP=quarter` (hành vi TRƯỚC ticket 1). Nếu chúng tái lập 24,38% / 24,66% (và
md5 `parkgrid_080q` trùng `..._exp_c30vpark80_univpit.csv`) ⇒ +0,29pp là biên THẬT của ticket 1 tại
x=0,8, cổng neo được giải thích và lưới dùng được. Nếu KHÔNG tái lập ⇒ có biến thứ ba đã đổi, DỪNG
và báo, không công bố lưới.
