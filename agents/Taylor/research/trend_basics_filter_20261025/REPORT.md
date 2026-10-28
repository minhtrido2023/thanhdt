# REPORT — "Trending basics" (xu hướng liên tục + tương tác value) lọc lệnh LAG/BAL (Giai đoạn 1, PAPER-ONLY)
Job `Taylor_20261025_131054` · 2026-10-25 · PREREG `PREREG.md` (commit `5736fe68f`, sửa đổi S0/S1 commit `4b837d082` — cả hai TRƯỚC khi chạy) · code `analyze.py` · số `results.csv` (md5 `ca435da0…`), `trend{,_pin1M}.csv`, `interact_desc.csv`, `corr.csv`; chẩn đoán hậu kiểm `diag.py` → `diag.txt`.
Ledger R3-park0-pin0pct-SAN md5 `537e349b5589408c994f8aceafeb9a39` (độ nhạy: pin1M md5 `a6ba34d83a4d374a73293d897c0b43d9`); vị thế từ job `ta_trend_entry_filter_20261025` (gộp holding_id, loại ABANDONED_REFUND/MTM) ⇒ **695 LAG / 299 BAL**. Không replay NAV, không wire.

## Kết luận thẳng
**Xu hướng — kể cả dạng liên tục và kết hợp với value — KHÔNG lọc được lệnh LAG/BAL.** 1/39 ô qua đủ tiêu chí khai trước, và ô đó **không phải xu hướng**:
- **LAG × up60** (tỉ lệ phiên tăng 60 phiên): +7,6pp T3−T1, q=0,016 (cụm quý), trong năm +4,2pp p=0,023, IS/OOS +4,3/+10,4, kiểm soát 1/PE p=0,002, pin1M +6,8pp, PIT-tertile +7,6pp p=0,002. Đạt hết trên giấy — nhưng **chẩn đoán hậu kiểm cho thấy nó đo "mã đóng băng giá"**: ρ(up60, tỉ lệ phiên ĐỨNG GIÁ 60 phiên) = **−0,88**; tertile thấp có trung vị **83% phiên không đổi giá** (tertile cao 7%). Tỉ lệ phiên GIẢM tertile cao cũng tốt hơn +8,2pp (p=0,0002) — tức "mã có giao dịch thật" thắng "mã đứng im", bất kể hướng. Biến xu hướng đúng nghĩa (tỉ lệ tăng TRONG các phiên có đổi giá) **ngược dấu** −3,3pp (p=0,08). Hồi quy up60 + flat60 + ADV + 1/PE: hệ số up60 còn +2,5pp **p=0,64**. ⇒ Đây là tín hiệu **thanh khoản/khả năng khớp**, trùng chủ đề dự án LAG ADV filter (mốc 2026-12-15) và job `lag_capacity_floor_20261025` — chuyển sang đó, **không** phải bằng chứng cho lọc xu hướng.
- **Tương tác value × xu hướng (giả thuyết chính của user): không đạt, LAG còn ngược.** Trong tertile 1/PE cao của LAG (231 lệnh, ret 8,3% vs tertile thấp 2,7% ⇒ value tự nó +5,6pp), tách theo xu hướng không thêm gì: RS120 trên/dưới trung vị +2,6pp (q=0,92, trong năm −0,6pp); trên/dưới MA200 −0,3pp; **"dao rơi" (dưới MA200 & MA200 dốc xuống) lại TỐT hơn** 10,3% vs 7,7% (−2,6pp, ngược hướng tránh dao rơi). BAL: mọi ô tương tác thiếu mẫu (≤100 lệnh value cao, nhóm xấu 12–50).
- **BAL**: mọi ô "thiếu mẫu" (tertile 99–100 < ngưỡng 100). Ô lớn nhất BAL × RS120 +9,2pp (q=0,19, trong năm +3,7pp p=0,16, IS chỉ 83 lệnh) — giả thuyết, không đủ; và vì BAL đã chọn theo momentum (SIGNAL_V11) nên đây là phần dư trong bộ chọn, không phải bộ lọc mới.

## Bảng chính (ret = lợi suất ròng/vị thế tới thoát thật; d = T3−T1 theo phân vị trong book; T10 = BẬT−TẮT; p,q = bootstrap cụm QUÝ, BH trên 39)
| Ô (hướng khai) | N T3/T1 | N quý | ret T3 / T1 | d | IS / OOS | p_q / q | trong năm d, p | bỏ 20-21 / cắt 2% | pin1M | kiểm soát 1/PE b, p | Đạt |
|---|---|---|---|---|---|---|---|---|---|---|---|
| LAG up60 (+) | 232/231 | 50 | 9,2% / 1,6% | **+7,6** | +4,3 / +10,4 | 0,0004 / **0,016** | +4,2, 0,023 | +3,5 / +7,8 | +6,8 | +10,4, 0,002 | có* |
| LAG vol_tr (+, chỉ khi giá tăng) | 104/103 | 49 | 8,6% / 2,0% | +6,6 | +8,8 / +4,7 | 0,019 / 0,19 | +5,7, 0,027 | +8,0 / +4,0 | +6,4 | +9,0, 0,022 | không (q) |
| LAG dd120 (+) | 232/231 | 50 | 4,1% / 8,0% | −3,9 | −3,4 / −1,7 | 0,037 / 0,29 | −2,3, 0,22 | −3,7 / −2,9 | −4,3 | — | không (ngược) |
| LAG atr_ratio (−) | 232/231 | 50 | 7,5% / 5,1% | +2,3 | +2,1 / +4,6 | 0,28 / 0,92 | — | — | +2,6 | — | không (ngược) |
| LAG rs60 / rs120 (+) | 232/231 | 50 | — | −0,5 / +1,4 | IS/OOS trái dấu | ≥0,57 / 0,92 | −3,4 / −0,7 | — | — | — | không |
| LAG d_ma50 / d_ma200 / slope200 (+) | 232/231 | 50 | — | −2,1 / +0,3 / +1,5 | — | ≥0,27 / ≥0,92 | — | — | — | — | không |
| LAG knife (−) | 152/543 | 50 | 7,3% / 5,8% | +1,5 (BẬT tốt hơn) | +6,6 / −1,7 | 0,47 / 0,92 | — | — | +1,7 | — | không |
| BAL rs120 (+) | 100/99 | 40 | 14,6% / 5,5% | +9,2 | +2,8 / +10,2 | 0,016 / 0,19 | +3,7, 0,16 | +6,4 / +6,0 | +8,9 | +11,1, 0,028 | không (thiếu mẫu, q, p_y) |
| BAL pos52 / rs60 (+) | 99/98 | 40 | — | +6,0 / +4,5 | IS âm | ≥0,18 / 0,92 | ~0 | — | — | — | không |
| 12 ô còn lại (adx, di, hhhl, r2s60, up60 BAL…) | | | | \|d\| ≤ 3,8 | | q ≥ 0,92 | | | | | không |
\*đạt theo PREREG nhưng chẩn đoán hậu kiểm bác bỏ cách đọc "xu hướng" (xem trên). Đầy đủ 39 ô + CI95, p cụm tháng, ρ: `results.csv`.

## Cảnh báo / giới hạn
- `diag.py` là **hậu kiểm, không khai trước** — dùng để bác cách đọc, không dùng để đẻ ứng viên mới. Không đề xuất flat60/up60 làm bộ lọc ở đây; nếu đi tiếp thì thuộc dự án ADV/capacity của LAG, với PREREG riêng.
- Chênh LAG×up60 tập trung 2020–21 (năm +23,8 / +13,9pp; LOO bỏ 2020 hoặc 2021 vẫn +5,6pp); 2016 và 2025 âm.
- Thiếu mẫu là cấu trúc: BAL 299 lệnh ⇒ tertile ≈100; ô tương tác BAL 12–85 lệnh/nhóm. "Không thấy" ở BAL = "không đo được", không phải "không có".
- 39 trials tương quan mạnh với nhau (`corr.csv`) ⇒ BH bảo thủ. PREREG sửa S0 (đếm sai 13→15 biến, N trials 35→39) và S1 (gộp nhóm (G,năm) <6 lệnh) trước khi chạy.
- T9 chỉ có trên lệnh có giá tăng 20 phiên (LAG 310, BAL 244 lệnh).

## Tự kiểm
- ΣP&L vị thế = TX cash: lệch ≤ 14 VND trên 4,0e11 (LAG pin0), ≤ 12 VND (BAL) — sai số làm tròn của `positions.csv` (ghi `%.10g`); job nguồn đã khớp 0,0007 VND trên dữ liệu chưa làm tròn. pin1M: ≤ 1,5 VND.
- Tính tay Python thuần `rs60, d_ma200, pos52, atr_ratio, up60` cho 4 vị thế (HPG_20140509_1, DPM_20150825_6, KDH_20230608_4387, GMX_20160127_391): sai số tương đối tối đa **3,3e-10** (`selfcheck_hand.txt`).
- PIT: 0 vị thế có ngày chỉ báo > phiên tín hiệu; chạy lại dưới `env -u TZ` và `TZ=America/New_York`: `results.csv`, `trend.csv` byte-identical. Chạy: `$DNA_PYEXE analyze.py` (~13s); `$DNA_PYEXE diag.py`.
