# TCH — DD redo vòng 3b (vòng cuối) · 09/11/2026 · job `Taylor_20261109_003030`

> Giá 06/11/2026 = **13.500** (BQ `tav2_bq.ticker`). Mô hình khoá trước khi so giá
> (`calc_r3b/LOCK_md5.txt`, 07:35:57 ICT, đủ md5 upstream). Model và compare đều chạy 2 lần, trùng byte.
> Không đặt lệnh, không sửa `kb/dd_price_zones.json`, không gửi email.

## 1. Kết luận

| | Tâm | P10 | P50 | P90 | Giá | Nhãn | % trọng số dưới giá |
|---|---|---|---|---|---|---|---|
| **r3b HEADLINE, cỡ 5 tỷ** (CK 0,63%) | **15.864** | 14.563 | 15.795 | 17.325 | 13.500 | **DƯỚI vùng** | 0% |
| r3b, sleeve 40 tr | 15.955 | 14.647 | — | 17.425 | 13.500 | **DƯỚI vùng** | 0% |
| r3 cũ (song song) | 16.244 | 15.578 | 16.208 | 16.950 | 13.500 | DƯỚI vùng | 0% |

Tâm giảm **−380 đ (−2,3%)** so với r3. Nhãn **DƯỚI vùng** giữ nguyên ở cả 2 cỡ, nhưng vùng rộng hơn
(P10 14.563 thay vì 15.578): biên an toàn từ giá lên P10 chỉ còn **+7,9%**.

**Nhãn KHÔNG chắc.** Ba lựa chọn riêng lẻ, lựa chọn nào cũng có cơ sở, đều đưa nhãn về **TRONG** (mục 5):
dùng biên gộp kiểm toán 42,7% thay cho 51,9%; dùng quy ước y=4 cho mọi dự án; hoặc coi k là chưa đo
với y=4. Headline đứng được là nhờ ba số **đo được**: biên 6T FY26 51,9%, mốc hoàn thành dự án,
và TMĐT. Cả ba đều không phải số kiểm toán.

**FLOOR_FAIL vẫn còn**: CF_OA_3Y = −771,7 tỷ (BQ `ticker_financial` 2026Q3). Mã không đủ điều kiện
sleeve fear-buy §2.5. Đây cũng là lý do lệnh MUA ngày 03/11 bị bỏ.

## 2. Lỗi sửa trong vòng này (skeptic cuối r3)

Ở `calc_r3/tch_r3.py:33`, `sur_me = rest×s×pv(4)`: r3 chiết khấu **chỉ phần thặng dư** của đất cũ
chưa bán. Phần giá vốn (C, phần của mẹ là 7.140,7 tỷ) vẫn tính theo giá sổ, dù tiền về cùng lúc với thặng dư.

Cách sửa (`calc_r3b/tch_r3b.py::nav`, mode `'b'`), áp cho từng dự án p:
`giá trị_p = σ_p·[C_p(1+k_p)(1+s)·pv(y_p) − k_p·C_p·pv(y_p/2)]`, thay cho `C_p + σ_p·C_p·s·pv(4)`.
- **Giá vốn và thặng dư cùng chiết khấu pv(y).**
- **k** = chi phí còn phải đầu tư / chi phí đã phát sinh. Phần chi phí tương lai k·C chi đều trong thời
  gian thi công (tâm y/2) và sinh biên s như chi phí đã phát sinh. Cách này nhất quán với g: giá vốn
  được trích trước theo dự toán toàn dự án (TM 2.25), nên biên 51,9% là biên trên tổng chi phí.

**Đối chiếu với skeptic.** Bản nhất quán với y=4, k=0 cho **13.435**, trùng số skeptic. Độ dốc theo k
(y=4, chi phí ở năm 2) là **+1.779 đ mỗi 1,0 k**, skeptic tính 1.742 (lệch +2%). Chỗ lệch có lẽ nằm ở
cách gán k cho nhóm sản phẩm đã hoàn thành; chưa đối chiếu chi tiết.

## 3. y: thời gian thu tiền đất cũ (có dữ liệu)

Nguồn là mốc hoàn thành trong BCTN 2025, tr.30–33 (`src/gaps/bctn25.txt:1372–1426`). Giả định thận trọng:
**toàn bộ tiền bán phần chưa bán về đúng ở mốc hoàn thành**. Thực tế bán nhà hình thành trong tương lai
thu tiền theo tiến độ, nên tiền về sớm hơn.

| Dự án | Mốc | y (từ 06/11/26) | C chưa bán (tỷ, hợp nhất) |
|---|---|---|---|
| Green River | hết Q4/2028 | 2,15 | 2.498,6 |
| H2 | hết Q4/2027 | 1,15 | 280,3 |
| NC-II (CRV 68,02%) | muộn nhất 11/2030 | 4,07 | 6.010,1 |
| SP đã hoàn thành (H1, Gold Tower, N01…) | — | 1,0 | 339,9 + 1,7 |

## 4. k: ĐO được từ TMĐT (không phải số kiểm toán)

`k_p = (TMĐT_p − HTK_p − GV đã kết chuyển_p) / (HTK_p + GV đã kết chuyển_p)`. TMĐT lấy từ BCTN25,
HTK lấy tại 30/09/26 (TM9). GV kết chuyển lũy kế theo dự án không được công bố, nên dùng hai cận:
từ 0 đến toàn bộ GV BĐS FY25 (275,27) cho GR, và từ 0 đến toàn bộ GV BĐS 6T FY26 (940,37) cho NC-II.

| Dự án | TMĐT | HTK | k (khoảng) | k tâm |
|---|---|---|---|---|
| NC-II | 15.076,26 (gồm tiền SDĐ) | 7.390,37 | 0,81–1,04 | 0,918 |
| Green River | 4.050 | 3.317,07 | 0,13–0,22 | 0,172 |
| H2 | 2.199 | 555,53 | 2,96 | 2,958 ⚠ |
| SP đã hoàn thành | — | — | 0 | 0 |

**k bình quân, trọng số C phần mẹ: 0,702.** Con số này vượt ngưỡng 0,4 mà skeptic nêu. Có thêm trục
F ±25% (k×0,75/1/1,25, trọng số 1/4–1/2–1/4, [UL] đối xứng) vì TMĐT là dự toán pháp lý và có thể gồm dự phòng.
⚠ H2 bất thường: đã "xong thô" mà HTK mới bằng 25% TMĐT, có thể TMĐT H2 gồm đất hoặc hạng mục đã ghi
ở H1. Chặn k_H2 = 1,0 thì tâm còn **15.568**, vẫn DƯỚI.

## 5. Cầu r3 → r3b (sau CK 5 tỷ) và các bản song song

| Bước | Tâm | Δ |
|---|---|---|
| r3 tái lập (control, trùng 16.346,83 trước CK) | 16.244 | |
| Nhất quán giá vốn + thặng dư, y=4, k=0 (= skeptic) | 13.435 | −2.809 |
| y theo mốc hoàn thành dự án | 14.321 | +886 |
| + k đo (tâm) | 15.864 | +1.543 |
| + trục F ±25% = **HEADLINE** | **15.864** | 0 |

| Song song (cỡ 5 tỷ) | Tâm | P10 | P90 | Nhãn | % dưới giá |
|---|---|---|---|---|---|
| HEADLINE, 2 trục g **tương quan hoàn toàn** | 15.864 | 14.490 | 17.417 | DƯỚI | 0% |
| r3 cũ, 2 trục g tương quan hoàn toàn (skeptic 15.439) | 16.244 | **15.439** | 17.130 | DƯỚI | 0% |
| k chưa đo: trục đối xứng {0;0,2;0,4;0,6}, y dự án | 15.027 | 13.931 | 16.292 | DƯỚI | 2,0% |
| k chưa đo: trục đối xứng, **y=4** | 13.968 | 13.021 | 15.114 | **TRONG** | 31,6% |
| k đo, **y=4** | 14.683 | 13.528 | 15.986 | DƯỚI (sát, +0,2%) | 9,8% |
| k cận dưới / cận trên | 15.709 / 16.037 | 14.473 / 14.693 | 17.081 / 17.543 | DƯỚI | 0% |
| Dạng chính xác (backlog chỉ chiếm cost_bl/(1+k) trong HTK) | 16.442 | 14.930 | 18.130 | DƯỚI | 0% |
| **g kiểm toán 42,7% ±5pp** + k đo | 13.642 | 12.741 | 14.667 | **TRONG** | 44,5% |
| g 42,7% ±5pp, k=0 (cận dưới kết hợp) | 12.893 | 12.361 | 13.488 | TRÊN (sát) | 90,6% |
| y=4, k=0 (skeptic) | 13.435 | 12.731 | 14.213 | TRONG | 56,3% |

Sleeve 40 tr cho cùng nhãn ở mọi dòng, trừ dòng "g 42,7%, k=0": 40 tr ra TRONG (P90 13.566).
Chi tiết ở `calc_r3b/compare_r3b_out.txt`.

## 6. Biên gộp BĐS đã kiểm toán (đọc ảnh pdf tr.42, `calc_r3b/evidence_FY25_audited_pdfp42_TM24_TM25.png`)

| | DT bán BĐS | GV bán BĐS | GPM |
|---|---|---|---|
| FY25 (01/04/25–31/03/26), kiểm toán AASC | 480,49 | 275,27 | **42,7%** (38,7% nếu tính cả tổn thất giảm giá BĐS 19,11) |
| FY24, kiểm toán | 3.899,17 | 2.235,88 | **42,7%** |
| 6T FY26, **chưa soát xét** | 1.954,52 | 940,37 | 51,9% (6T FY25 có soát xét: 51,0%) |

Base giữ g 51,9% ±5pp. Lý do: quỹ đất còn lại phần lớn là NC-II (C 6.010 / 9.130), và NC-II mới bắt đầu
bàn giao ở Q2 FY26. FY24 nhiều khả năng chủ yếu là H1/Commerce (Đại Lộc LNST FY24 709 tỷ). Đây là
**suy luận, không phải số tách theo dự án**. Biên theo dự án không được công bố. Nếu biên thật của
NC-II/GR gần 42,7% thì nhãn là **TRONG**. Đây là rủi ro lớn nhất của headline.

## 7. Cảnh báo (giữ từ r3, thêm mới)
- FLOOR_FAIL: CF_OA_3Y −771,7 tỷ (chi mua quỹ đất 150 Tô Hiệu + I.14).
- Danh tính NH "Sài Gòn Tài Lộc" (678,3 tỷ) chưa xác minh. Stress mất 100% tiền gửi này trừ khoảng −670 đ khỏi tâm (r3).
- CK holding/quản trị không vào base, chỉ chạy song song ở r3: holding 27% → 13.933, quản trị 15% → 13.807, cả hai đều TRONG.
  Bản r3b chưa chạy lại các trục này; theo mức trượt tương đối, dự kiến (ước lượng) các bản đó sẽ ra TRONG/TRÊN.
- TMĐT ≠ dự toán nội bộ dùng để trích trước giá vốn, chưa đối chiếu.

## 8. File
`calc_r3b/assumptions_r3b.json` · `tch_r3b.py` → `tch_r3b_out.json/.txt`, `grid_tch_r3b.csv` (run1=run2 md5) ·
`LOCK_md5.txt` (prerun) · `tch_r3b_compare.py` → `compare_r3b_out.txt`, `../SUMMARY.json` (cmp1=cmp2) ·
`../SUMMARY_r3.json` (backup r3, md5 trùng LOCK) · `../SYNC_NOTE_r3b.md` (SUMMARY_5F/ADDENDUM_5F lạc hậu, không sửa vì có hash).
