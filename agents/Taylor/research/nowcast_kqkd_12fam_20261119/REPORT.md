# A4 — Nowcast KQKD 12 họ: **5 họ đạt cổng khai trước** (heo, môi giới, sân bay, cảng, ô tô) — job Taylor_20261119_090443

## 0. KẾT LUẬN
1. **GO (5/12):** họ 2 biên heo (DBC, BAF) IC **0,83** · họ 8 môi giới (GTGD) IC **0,79** · họ 9 sân bay (khách quốc tế)
   IC **0,41** · họ 10 cảng (XNK) IC **0,46** · họ 11 ô tô (xe đăng ký) IC **0,46**. Cả 5 đều: IC ≥ 0,25, CI90 cận dưới
   > 0, hai nửa cùng dấu dương, BH q < 0,10 (q = 0,075–0,089). Đây là nowcast **KQKD** (np_d), KHÔNG phải tín hiệu giá.
2. **Không đạt (6):** họ 1 biên thép (IC 0,38 nhưng CI90 chứa 0, q 0,33) · họ 3 phốt pho vàng (0,43, CI chứa 0) · họ 5
   polyester (−0,05) · họ 6 PVC (0,50, CI > 0 nhưng q 0,17) · họ 7 bán lẻ (0,06) · họ 12 ngân hàng (**−0,29, ngược dấu**).
   Họ 4 xút: chỉ mô tả, n = 8 (không đủ N). Theo PREREG: không thử biến thể nào.
3. **Biên thắng mỏng — đọc với độ chắc vừa phải:** p dịch vòng có độ phân giải 1/n nên p nhỏ nhất ≈ 0,02–0,04; 5 họ qua
   BH nhờ cùng có p thấp (q 0,075). Đổi 1 họ sang p cao hơn là q cả nhóm nhích lên. Họ 9 (sân bay) dựa phần lớn vào cú
   sốc COVID 2020-22 (một episode); họ 2 có N = 27 từ 2020Q1 (chu kỳ ASF).
4. **Độ trễ công bố họ 9/10/11 là GIẢ ĐỊNH** (+10/+15/+20 ngày, `macro_indicator` chưa có vintage, giá trị có thể đã
   revise). Họ 8 (dữ liệu sàn, trễ 0) và họ 2 (giá heo/TACN theo ngày/tuần) không vướng giả định này.
5. **Khuyến nghị B1/PREREG-5: CÓ viết, nhưng chỉ SAU khi quant-skeptic CONFIRMED kết quả này**, và dạng forward/paper
   song song (không gộp PREREG-4). Phạm vi tác động nhỏ: 16 mã của 5 họ chiếm **42/695 lệnh LAG** (6,0%) và 19/299 lệnh
   BAL trong ledger pin0% (`lag_bal_discriminators_20261025/features.csv`, lọc abandoned=0 & mtm=0); 36/42 lệnh LAG là
   mã môi giới. Họ môi giới là ứng viên B1 tốt nhất: KQKD gần như suy được hoàn toàn từ GTGD công khai (rev_yoy IC 0,85)
   ⇒ đúng ca "SUE đã biết trước". Kỳ vọng thẳng: tác động NAV LAG bị chặn trên bởi ~6% lệnh.

## 1. Chân đối chứng
Tái lập B2 26/10 (8 họ tier A, c_yoy→np_d gộp): **0,460** vs pin 0,450, lệch 0,010 ≤ 0,02 ⇒ PASS (`ctrl_b2_pooled.json`).

## 2. Kết quả chính (np_d, `a4_main_np_d.csv`)
| Họ | n họ×quý | khoảng | IC | CI90 | p dịch vòng | IC nửa 1 / nửa 2 | BH q | Kết luận |
|---|---|---|---|---|---|---|---|---|
| 1 biên thép HPG | 36 | 2017Q4–2026Q3 | 0,380 | [−0,018; 0,690] | 0,250 | 0,34 / 0,35 | 0,333 | không đạt |
| 2 biên heo DBC, BAF | 27 | 2020Q1–2026Q3 | 0,827 | [0,646; 0,911] | 0,037 | 0,75 / 0,72 | 0,089 | **GO** |
| 3 phốt pho vàng DGC, PAT | 31 | 2019Q1–2026Q3 | 0,427 | [−0,158; 0,777] | 0,129 | 0,15 / 0,41 | 0,194 | không đạt |
| 4 xút CSV | 8 | — | — | — | — | — | (p=1) | mô tả, không đủ N |
| 5 polyester STK | 16 | 2021Q4–2025Q3 | −0,047 | [−0,486; 0,268] | 0,812 | −0,60 / 0,29 | 0,886 | không đạt |
| 6 PVC BMP, NTP | 36 | 2017Q4–2026Q3 | 0,495 | [0,175; 0,682] | 0,083 | 0,38 / 0,09 | 0,167 | không đạt |
| 7 bán lẻ | 56 | 2012Q4–2026Q3 | 0,061 | [−0,194; 0,357] | 0,750 | 0,24 / −0,04 | 0,886 | không đạt |
| 8 môi giới | 51 | 2014Q1–2026Q3 | 0,788 | [0,640; 0,877] | 0,020 | 0,67 / 0,91 | 0,075 | **GO** |
| 9 sân bay ACV, SCS, SAS | 40 | 2016Q4–2026Q3 | 0,414 | [0,045; 0,722] | 0,025 | 0,49 / 0,31 | 0,075 | **GO** |
| 10 cảng GMD, VSC, PHP | 56 | 2012Q4–2026Q3 | 0,455 | [0,252; 0,583] | 0,018 | 0,37 / 0,55 | 0,075 | **GO** |
| 11 ô tô VEA, HAX | 43 | 2016Q1–2026Q3 | 0,460 | [0,267; 0,582] | 0,023 | 0,39 / 0,54 | 0,075 | **GO** |
| 12 ngân hàng (28 mã) | 55 | 2012Q4–2026Q3 | −0,290 | [−0,492; −0,034] | 0,127 | −0,19 / −0,31 | 0,194 | không đạt (ngược dấu) |

Mô tả (không kiểm định): IC với rev_yoy — h8 0,85, h10 0,60, h9 0,54, h11 0,51, h2 0,45; gpm_d — h4 0,93 (n=8), h2 0,68,
h9 0,67. HVN/VJC (banned, chỉ mô tả): IC np_d 0,42, n 39. Ngân hàng ngược dấu: chi phí vốn tăng đi CÙNG LN tăng — nhiều
khả năng chu kỳ tín dụng/lãi suất đồng pha với lợi nhuận, không phải "NIM bị ép"; không diễn giải thêm (không thử biến thể).

## 3. Giới hạn
- p dịch vòng liệt kê đủ n−1 độ dịch ⇒ p_min = 1/n; đã khai trong PREREG §2 trước khi chạy.
- Hệ số chênh lệch (thép 1,6/0,5; polyester 0,86/0,34; heo FCR 2,8, khẩu phần 65/25) là giả định khoá trước.
- BCTC là bản ingest (dedupe giữ Release_Date sớm nhất), không phải vintage công bố đầu.
- Ngân hàng: dùng 28 mã ICB 8355 từng có trong universe_pit (REPORT kiến trúc ghi 25); thành viên kiểm PIT tại ngày tín hiệu.
- Tổng trial tích luỹ dòng hàng hoá/ngành: 17 + 12 = **29**.

## 4. Tái lập / artifact
- A3: `map_v2.csv` md5 `91bffcc87cf1bb307c646737c7390ef5`, commit `a968cc098`.
- PREREG.md md5 `556059d1b4bfe693dcd6fbee176eb7f0` (commit `740d17139`); PREREG_ADDENDUM.md md5 `6d30494832b2458a4aef0e65e2cf9e0d`
  (ngưỡng giá heo tuần, trước khi tính IC; commit `ef45520b0`); sửa dòng sed `5f1b97496`; `a4_nowcast.py` md5 `0a51c805dd057774b9d3de48a7f260d5`.
- Lệnh: `cd agents/Taylor/research/nowcast_kqkd_12fam_20261119 && /home/trido/thanhdt/wc_venv/bin/python a4_nowcast.py`
  (dữ liệu: `fetch_data.py` → 2 parquet chụp 19/11, bị .gitignore nên KHÔNG trong git — md5 `commodity_snapshot_20261119.parquet` 79617a2c65777f648263c808d7f072a7, `macro_snapshot_20261119.parquet` f45dbe9e0b6356e43fc016509309b8e7; chạy lại fetch sẽ lấy bản revise mới hơn).
