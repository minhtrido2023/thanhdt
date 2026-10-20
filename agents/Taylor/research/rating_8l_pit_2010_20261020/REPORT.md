# Khả thi dựng lại `fa_ratings_8l` PIT 2010-2014 — job Taylor_20261020_054959 (2026-10-20)

Read-only. Không sửa code production, không ghi `tav2_bq.fa_ratings_8l`, không pin. Mọi số dưới đây
đo trong phiên này bằng file `q*.sql` cùng thư mục (CSV kết quả cạnh nó), trừ chỗ gắn **ước lượng**.
Nguồn: `tav2_bq.ticker_financial` (LIVE, không thuộc sự cố 243 mã), giá/ICB từ
`tav2_pin.ticker_pin_202610` (1294 mã, **không** đọc `tav2_bq.ticker` đang hỏng), universe từ
`tav2_mike.universe_pit` (ruleset v1). Registry đã tra: `data_registry/price-volume/universe_pit.md`,
`config-meta/bq_pin_snapshots.md`, `rating-8l/fa_ratings.md`.

## 0. Kết luận

**DỰNG ĐƯỢC CÓ ĐIỀU KIỆN — nhưng mẫu thêm vào yếu và KHÔNG sạch như nửa IS hiện tại.**
Dữ liệu đầu vào có đủ để chạy code 8L (cột NULL vừa phải từ 2012), nhưng có 3 khuyết tật không sửa được
bằng code: (1) **survivorship 100%** — bảng giá lẫn tài chính không có mã nào ngừng dữ liệu trước 2025;
(2) **Release_Date 2012-13 là ngày batch tổng hợp** (~94% = cuối quý + 32 ngày), không có nguồn độc lập
nào để kiểm (stock_news bắt đầu 2015); (3) cột `_Min3Y/_Min5Y/3Y/5Y` 2010-12 tính trên lịch sử cụt.
Thêm 2010Q2-2014Q2 cho G1 khoảng **218 sự kiện / 17 quý (ước lượng)**; nếu hiệu ứng thật bằng điểm IS cũ
(+0,75%) thì p gộp chỉ xuống ~0,07 (**ước lượng**) — vừa qua ngưỡng 0,10, không phải bằng chứng mạnh.
Muốn dùng phải **đăng ký trước một tiêu chí mới** (không được ghép vào (b) của PREREG P2v2 sau khi đã
thấy kết quả).

## 1. Vì sao `fa_ratings_8l` bắt đầu 2014-06-30

Do **hằng số viết cứng**, không phải dữ liệu hay luật rating: `rating_8l_history.py:139`
`WHERE f.time >= '2014-06-01'` trong `HIST_SQL`. Có từ commit baseline `c9cc670ca` ("Checkpoint: code +
docs baseline"), `git log -S"2014-06-01"` không tìm thấy lý do nào được ghi lại. Các chú thích trong file
đều nói "panel 2014→nay" — khớp với cửa sổ backtest chuẩn (IS 2014-19), nên nhiều khả năng là chủ ý
chọn cửa sổ, không phải vì thiếu dữ liệu.

Rating 1-5 tính **chỉ từ dòng của chính quý đó** (không có `shift`/`rolling`/trạng thái giữa các quý —
grep `shift(|rolling|ffill|prev_` không trúng); chỉ `tier` của COMPOUNDER là percentile theo `q_time`.
⇒ Kéo mốc về sớm hơn **không thể đổi rating 1-5 của các dòng ≥2014-06** (sự kiện G1/G2 dựa trên rating).

## 2. Cột đầu vào 2010-2014 (`q2_null_by_year.csv`, `q2b_history_depth.csv`, `q2c_icb_coverage.csv`)

Tỉ lệ NULL theo năm `time` (chỉ các cột `HIST_SQL` dùng; PE/PCF/PS KHÔNG có trong 8L history):

| Cột | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 |
|---|---|---|---|---|---|---|
| ROIC3Y / ROIC_Min3Y / ROIC5Y / ROIC_Min5Y | 0,224 | 0,144 | 0,114 | 0,101 | 0,001 | 0,001 |
| ROE_Min3Y / ROE3Y / ROE5Y | 0,085 | 0,024 | 0,006 | 0,003 | 0,000 | 0,001 |
| ROE_Trailing | 0,140 | 0,128 | 0,114 | 0,084 | 0,077 | 0,102 |
| Debt_Eq_P0 / P4 | 0,092 / 0,302 | 0,083 / 0,208 | 0,065 / 0,106 | 0,048 / 0,083 | 0,067 / 0,063 | 0,100 / 0,138 |
| FSCORE | 0,232 | 0,163 | 0,088 | 0,067 | 0,081 | 0,138 |
| CF_OA_P0 / P3 | 0,322 / 0,825 | 0,327 / 0,351 | 0,176 / 0,231 | 0,131 / 0,185 | 0,135 / 0,143 | 0,161 / 0,197 |
| CF_OA_5Y | 0,132 | 0,034 | 0,016 | 0,011 | 0,000 | 0,004 |
| NP_P0 / NP_P4 / NP_P7 | 0,099 / 0,272 / 0,438 | 0,097 / 0,188 / 0,332 | 0,079 / 0,110 / 0,174 | 0,054 / 0,089 / 0,115 | 0,067 / 0,068 / 0,103 | 0,082 / 0,131 / 0,136 |
| GPM_P7 / Revenue_P7 | 0,439 / 0,449 | 0,334 / 0,357 | 0,177 / 0,207 | 0,111 / 0,152 | 0,101 / 0,142 | 0,154 / 0,136 |
| Release_Date | 0,070 | 0,072 | 0,051 | 0,043 | 0,065 | 0,080 |
| (tham khảo, không dùng trong 8L) PCF | 0,964 | 0,849 | 0,604 | 0,176 | 0,075 | 0,166 |

Số mã có dòng tài chính: 2010 545 · 2011 607 · 2012 627 · 2013 642 · 2014 660 (khớp số sơ bộ của Mike).
ICB trong `ticker_pin_202610`: NULL ≤0,3% dòng mọi năm 2009-2015.

**Độ sâu lịch sử thật** (`n_prior` = số dòng `ticker_financial` trước đó của cùng mã):

| Năm | TB quý trước | % dòng <12 quý | % có ROIC_Min3Y dù <12 quý | % có Min3Y dù <4 quý | % có ROIC_Min5Y dù <20 quý | ROIC_Min5Y = Min3Y |
|---|---|---|---|---|---|---|
| 2010 | 7,9 | 69,5% | 48,8% | 18,3% | 73,8% | 96,4% |
| 2011 | 10,3 | 62,1% | 49,5% | 10,6% | 76,5% | 92,2% |
| 2012 | 13,8 | 48,9% | 40,4% | 3,1% | 65,4% | 78,0% |
| 2013 | 17,3 | 22,2% | 18,5% | 2,1% | 56,4% | 75,9% |
| 2014 (đã trong bảng) | 20,8 | 9,7% | 9,6% | 2,6% | 51,8% | 82,8% |

⇒ Vendor tính `_Min3Y/_Min5Y/3Y/5Y` trên **bao nhiêu lịch sử có được**, không để NULL khi chưa đủ cửa sổ.
2010-11 gần như "Min5Y ≡ Min3Y ≡ min của 2-3 năm". Rating 2010-12 vì thế đo "sàn chất lượng" trên cửa sổ
ngắn hơn hẳn ⇒ ngưỡng 8L không cùng nghĩa với 2014+. Lưu ý: chính panel 2014 cũng có 51,8% Min5Y trên
<20 quý — vấn đề không mới, chỉ nặng hơn trước 2013.

## 3. Release_Date 2010-2014 (`q3_release_date.csv`, `q3b_top_batch_dates.csv`, `q3d_lag_vs_32.csv`, `q3c_stock_news_coverage.csv`)

| Năm | NULL | RD = `time` | RD < cuối quý | RD ≤ RD quý trước | Trong batch ≥100 dòng/ngày | Trễ p10 / p50 / p90 (ngày sau cuối quý) |
|---|---|---|---|---|---|---|
| 2010 | 7,0% | 93,4% | 0 | 0,15% | 69,8% | 27 / 32 / 34 |
| 2011 | 7,2% | 97,8% | 0 | 0,13% | 71,9% | 27 / 32 / 39 |
| 2012 | 5,1% | 99,2% | 0 | 0 | 84,9% | **32 / 32 / 32** |
| 2013 | 4,3% | 99,5% | 0 | 0 | 94,8% | **32 / 32 / 32** |
| 2014 | 6,5% | 99,4% | 0 | 0 | 62,5% | 21 / 34 / 37 |

Tỉ lệ RD đúng bằng cuối quý + 32 ngày: 2010-11 35-40% · **2012-13 93-95%** · 2014-19 31-36% · 2020+ 8-16%.
Ngày batch lớn nhất: 2013-08-01 612 dòng, 2013-11-01 606, 2013-05-02 602, 2013-02-01 588… Có ca RD trễ
rất xa (2011-02-08 cho 2010Q3, 473 dòng) — vendor nạp bù, an toàn (muộn), không nhìn trộm.

**`stock_news` không phủ 2010-2014**: năm sớm nhất 2015 (874 tin, 8 tin BCTC); dày từ 2019. ⇒ **không
có nguồn độc lập nào** kiểm RD giai đoạn này; các kiểm P3 so-với-tin không làm được.

Đánh giá: 2010-11 RD có biến thiên (nhưng 70% rơi vào ngày batch); **2012-13 RD là hằng số tổng hợp
cuối quý + 32**, không phải ngày công bố. Hệ quả:
- Mã công bố SAU +32 ngày (BCTC hợp nhất; Q4 lần đầu) ⇒ eff = RD **nhìn trộm** tới khi công bố thật.
  Hạn luật: theo hiểu biết của tôi BCTC quý riêng 20 ngày, hợp nhất 45 ngày — **giả định, chưa xác minh
  với Wendy**. Tỉ lệ RD > +45 ngày trong dữ liệu chỉ 0,6-4% mọi giai đoạn, nhưng đó là RD của vendor, không
  phải sự thật.
- Mã công bố TRƯỚC +32 ngày ⇒ eff muộn ⇒ cửa sổ CAR bỏ lỡ phần drift sớm ⇒ lệch về 0 (bảo thủ).

**Luật đề xuất cho bản dựng lại**: chính: `eff = max(RD, cuối quý + 45)`; Q4 nhạy cảm thêm
`cuối quý + 90`; NULL RD → `cuối quý + 45`. Không dùng `NULL_RD_EFF_OFFSET_DAYS = 0` (luật live, dựa trên
đo 2014+ với RD có biến thiên — không áp được cho dữ liệu batch). Đổi lại: eff giai đoạn này không cùng
định nghĩa với IS/OOS hiện tại (eff = RD) ⇒ đây là một khác biệt thiết kế phải khai trong PREREG.

## 4. Universe & số sự kiện (`q4_universe_by_quarter.csv`, `est_events.py`, `power_estimate.py`)

`universe_pit` in_universe tại phiên cuối mỗi quý (100% có dòng tài chính cùng quý):

| | Q1 | Q2 | Q3 | Q4 |
|---|---|---|---|---|
| 2010 | 290 | 343 | 384 | 382 |
| 2011 | 337 | 282 | 230 | 196 |
| 2012 | 191 | 234 | 198 | 159 |
| 2013 | 165 | 173 | 162 | 187 |
| 2014 | 214 | 227 | 239 | 258 |

So với IS hiện tại 2014Q3-2019Q4: 22 quý, 6.145 mã·quý. 2010Q2-2014Q2: 17 quý, 4.064 mã·quý;
2012Q1-2014Q2: 10 quý, 1.910 mã·quý. (2010Q1 là quý rating đầu, chưa có "prev" ⇒ không có sự kiện.)

Số sự kiện — **ước lượng** (giả định tỉ lệ đổi hạng 2010-14 bằng 2014-19; nửa IS P2v2 có SUE: G1 330,
G2 330 trên 6.145 mã·quý = 0,054/mã·quý): G1 ≈ **218** (2010Q2-14Q2) hoặc ≈ **103** (2012Q1-14Q2);
G2 tương tự. Sẽ ít hơn sau khi khớp ô SUE vì NP_P7 2010-11 NULL 33-44% (SUE cần ≥6/8 quý).

Sức mạnh — **ước lượng** (SE bootstrap-quý ∝ 1/√số quý; G1 [2,20] IS cũ +0,75% p=0,18 ⇒ SE ≈ 0,56%):

| Gộp IS | Nếu δ thật = +0,75% (IS cũ) | Nếu δ thật = +1,06% (cả mẫu) |
|---|---|---|
| 22+17 = 39 quý | p ≈ 0,074 | p ≈ 0,012 |
| 22+10 = 32 quý | p ≈ 0,106 | p ≈ 0,022 |

⇒ Thêm 2010-14 chỉ đủ đẩy G1 qua p<0,10 nếu hiệu ứng thật ≥ điểm IS cũ VÀ lấy cả 2010-11 (phần dữ liệu
tệ nhất). N độc lập là số quý (17 hoặc 10), không phải số sự kiện.

## 5. Giá 2010-2014 (`q5_corp_action_adj.csv`, `q5b_top_events.csv`, `q5c_unadjusted_in_universe.csv`)

Nguồn `tav2_pin.ticker_pin_202610` (vintage đầu 10/2026). Close đã điều chỉnh tốt cho mã lớn: ngày `Price`
rơi >20% (corp action) mà `Close` đi ≤7%: DHG 2011-06-28 Price −56,3% / Close +4,8%; REE 2010-06-23
−52,4% / +4,8%; SSI 2010-03-25 −47,5% / +5,1%; VNM 2011-11-29 −32,0% / +2,0% và 2012-12-19 −31,9% /
+2,2%; HPG 2010-04-27 −30,0% / +5,3%; VIC, FPT, PNJ, KDC, HAG, MWG tương tự (19 ca, không ca nào Close lỗi).
Toàn thị trường: ngày Price < −20% 2010-14 = 107/96/56/82/62 mỗi năm, trong đó Close cũng < −20%:
18/23/19/25/22. **Trong universe** chỉ 3 phiên |ΔClose| > 20% cả 2010-14: HIG 2010-02-05 (+20,3%, nghỉ 9
ngày), UNI 2010-06-28 (+24,8%), VBC 2010-09-13 (Price và Close cùng −30,9% ⇒ nghi chưa điều chỉnh).
⇒ Giá đủ dùng; loại hoặc winsorize 3 phiên trên.

## 6. Look-ahead / restatement / survivorship riêng của giai đoạn (`q6_survivorship.csv`, `q6b_restate_pins.csv`)

- **Survivorship — nặng nhất, không sửa được bằng code.** `ticker_pin_202610`: 1.294 mã, ngày cuối sớm
  nhất 2025-05-15, **0 mã** có dữ liệu dừng trước 2020. `ticker_financial`: 1.291 mã, dòng cuối sớm nhất
  2025-04-15, 0 mã dừng trước 2020. ⇒ Mọi mã hủy niêm yết trước ~2025 đã bị xoá khỏi toàn bộ lịch sử;
  `universe_pit` (dựng từ `ticker`) cũng chỉ chứa mã sống sót. Số mã bị mất 2010-14: **chưa đo** (không có
  danh sách hủy niêm yết trong kho). Lỗi này CŨNG có ở IS 2014-19, nhưng 2011-13 là giai đoạn khủng hoảng
  nên tỉ lệ mất nhiều khả năng cao hơn (suy luận, chưa đo). Chiều lệch: mã chết phần lớn là xấu ⇒ thiếu
  G2/G0 có lợi suất tệ; G1 − G0 lệch không rõ dấu.
- **Restatement**: so `ticker_financial_pin_202607` với `_pin_202610` trên 11.989 dòng 2010-14: 0 dòng đổi
  NP_P0/ROIC3Y/CF_OA_P0/FSCORE/Release_Date. Chỉ chứng minh ổn định 3 tháng gần đây; KHÔNG chứng minh
  là số công bố gốc 2010-14 (không có vintage nào trước 2026-07; BQ time-travel bị xoá hằng ngày).
- **Đổi chuẩn kế toán**: theo hiểu biết của tôi, VN không áp IFRS giai đoạn này; chế độ kế toán DN đổi từ
  QĐ 15/2006 sang TT 200/2014 từ 2015 — **giả định, chưa xác minh với Wendy**. Rủi ro là các cột tỉ số
  vendor quy đổi về khung hiện tại (không đo được).
- **`_Min3Y/_Min5Y` cửa sổ cụt** (mục 2) — không phải nhìn trộm, nhưng đổi nghĩa ngưỡng.
- **Bank AQ** (FiinPro 2010Q1+) đã có PIT lag 45/90 ngày trong code — dùng được.

## 7. Đề xuất kế hoạch dựng (nếu user muốn đi tiếp)

Công sức **ước lượng**: ~0,5-1 ngày Taylor + 1 vòng quant-skeptic.

1. **PREREG mới trước khi tính CAR** (bắt buộc): tiêu chí (b′) cho mẫu 2010Q2-2014Q2 (riêng) và cho IS gộp,
   cửa sổ chính [2012Q1-2014Q2] vs nhạy cảm [2010Q2-2014Q2], luật eff `max(RD, qend+45)`, Q4 +90 nhạy cảm.
   Ghi rõ (b) của P2v2 KHÔNG được chấm lại.
2. Script nghiên cứu (bản sao, không sửa `rating_8l_history.py`): mốc `HIST_SQL` tham số hoá; ICB đọc
   `tav2_pin.ticker_pin_202610` thay `tav2_bq.ticker`; chạy với `R8L_HIST_OUT=<thư mục này>/exp_r8l_2010.csv`
   + `R8L_HIST_NO_BQ_REFRESH=1` (code đã tự bỏ refresh khi đích không canonical — 2 lớp an toàn).
   Nếu cần bảng BQ: `tav2_mike._exp_fa_ratings_8l_2010`, không đụng `tav2_bq`.
3. **Kiểm ngược**: các dòng `q_time ≥ 2014-07-01` của bản dựng phải trùng rating/route 100% với
   `tav2_pin.fa_ratings_8l_pin_202610` (rating là hàm của dòng ⇒ kỳ vọng trùng tuyệt đối; lệch chỉ có thể
   từ nguồn ICB pin vs live — liệt kê từng ca). Bỏ 2014Q2 khỏi so (quý đầu bị cắt `>= 2014-06-01`).
4. Chạy lại event study P2v2 với cùng code, đổi cửa sổ; báo N quý, N sự kiện sau khớp SUE, p riêng 2010-14.

**Cần từ bq_admin/user**: (a) user duyệt PREREG mới + chấp nhận survivorship 100% là giới hạn đã biết;
(b) bq_admin: vendor có giữ dữ liệu giá + BCTC của mã đã hủy niêm yết không — chỉ cách này sửa được
survivorship (cũng có lợi cho IS 2014-19); (c) không cần `tav2_bq.ticker` (dùng pin), nên không phụ thuộc
sự cố 243 mã.

## File
`q2_null_by_year.sql/.csv` · `q2b_history_depth` · `q2c_icb_coverage` · `q3_release_date` ·
`q3b_top_batch_dates` · `q3c_stock_news_coverage` · `q3d_lag_vs_32` · `q4_universe_by_quarter` ·
`q5_corp_action_adj` · `q5b_top_events` · `q5c_unadjusted_in_universe` · `q6_survivorship` ·
`q6b_restate_pins` · `est_events.py` (+`_stdout.txt`) · `power_estimate.py` (+`_stdout.txt`).
Chạy lại: `source wc_env.sh; bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 --format=csv < qX.sql`
(lưu ý `wc_env.sh` tự `cd` về `WorkingClaude/` — dùng đường dẫn tuyệt đối).
