# Rổ vs FZ-001/FZ-002 vs CAPIT — 2026-11-19, job Taylor_20261119_051521
CHỈ ĐỌC (không đụng production/live). PREREG: `PREREG.md` (md5 51f9b7a57b0041175bec01811a865c1b, khoá trước khi tính). Chạy lại: `$DNA_PYEXE basket_vs_fz.py` → `out/*.csv`, `out/log.txt`. Dữ liệu = `../intraday_cluster_audit_20261119/data` (md5 `data_md5.txt`). Cụm E5, seed 7, B=10000, chỉ `in_stats==1`.

## Kết luận (trước)
**FZ ≈ cược thời điểm hồi: một nửa đến hai phần ba lợi nhuận FZ là beta của rổ, phần còn lại không chứng minh được là edge. Tiêu chí "FZ thêm giá trị" = FAIL cả hai setup (cả vì thiếu cụm lẫn vì CI90 chạm 0).**
- Cấp cụm in-sample: rổ chiếm **53% lợi nhuận FZ-001** (CI90 14–100%) và **69% FZ-002** (CI90 34–101%); Mike tính tay cấp deal 55%/86% — cùng hướng, FZ-002 giảm khi tính cấp cụm.
- Excess cấp cụm: FZ-001 **+0,88%** CI90 [−0,01; +1,65]%; FZ-002 **+0,77%** [−0,03; +1,68]%. Cả hai **CI90 chứa 0**, và chỉ **17 / 15 cụm** (<20) ⇒ FAIL-bởi-N *và* FAIL-bởi-CI (không phải chỉ thiếu N). DSR(N=1000) = 0,11 / 0,01; placebo khối tháng p = 0,023 / 0,084 (FZ-001 qua cả khi nhân 2 setup = 0,047, nhưng DSR vẫn <0,95 và CI90 chứa 0 ⇒ không đủ).
- Edge mong manh: FZ-001 bỏ 5 cụm tốt nhất ⇒ excess còn +0,11%; FZ-002 ⇒ −0,39% (top-5 chiếm 60% / 93% tổng cụm dương). FZ-002 cụm 04/2025 (a=+12,8%, rổ +12,1%) là đợt hồi hậu bán tháo thuế quan — gần như thuần thời điểm.
- **CAPIT phủ một phần, không phải phần lớn theo cụm; phần lớn theo NGÀY CAPIT:** chỉ **4/17 (FZ-001)** và **6/15 (FZ-002)** cụm FZ có CAPIT fire trong cửa sổ [đầu cụm−5 phiên, cuối cụm] — nhưng các cụm đó là những cụm LỚN: a=+3,45% / +3,86% so với +1,42% / +1,66% ở cụm không có CAPIT. Ngược lại 56% (FZ-001) / 67% (FZ-002) ngày CAPIT fire có FZ signal cùng ngày; phi = 0,30 / 0,39. Tức CAPIT = tập con "đợt hiếm, mạnh" của FZ; FZ phần lớn là đợt bán tháo nhỏ hơn.
- **FZ-có-CAPIT-không: không đủ N** (13 và 9 cụm <15) — chỉ mô tả: excess +0,68% / +1,08% (so +1,52% / +0,31% khi có CAPIT); không kết luận.
- Hold-out: **không đủ N** (2 cụm/setup). Mô tả: FZ-001 a=+1,93% vs rổ +0,30%; FZ-002 a=+1,05% vs rổ −0,28% (khớp số Mike: rổ âm). Không suy luận.
- **Hàm ý**: không có cơ sở nói FZ có edge chọn mã ngoài thời điểm; giá trị còn lại của FZ là "cược hồi" mà CAPIT/breadth đã phủ ở các đợt lớn. Không đổi khuyến nghị "paper, không wire" của audit trước.

## 1. Self-check / hiệu chuẩn
`excess_ret == net_ret_total − market_drift_same_day` (assert, tol 1e-6) ✓ cho cả 4 tệp. Proxy rổ (dùng cho đường c) vs rổ engine (b) trên ngày signal FZ: corr cấp ngày **0,95 (FZ-001, 39 ngày) / 0,98 (FZ-002, 37 ngày)**, mean 1,47% vs 1,42% / 1,60% vs 1,59% ⇒ proxy dùng được. Excess raw khớp audit trước (+0,88%/+0,77%).

## 2. Bảng chính (in-sample, cấp cụm E5, `out/basket_vs_fz.csv`)
| | FZ-001 | FZ-002 |
|---|---|---|
| cụm / deal / ngày signal | 17 / 176 / 39 | 15 / 174 / 37 |
| (a) FZ deal-set mean | +1,90% [0,63; 3,10] | +2,54% [0,89; 4,22] |
| (b) rổ-ngày-signal-FZ mean | +1,02% [0,17; 1,79] | +1,76% [0,46; 3,33] |
| rổ / deal (cấp cụm) | 0,53 [0,14; 1,00] | 0,69 [0,34; 1,01] |
| excess (a−b) cấp cụm | +0,88% | +0,77% |
| CI90 bootstrap theo cụm | [−0,01; +1,65]% | [−0,03; +1,68]% |
| excess nếu rổ không tốn phí (như audit trước, −0,134%) | +0,75% [−0,15; +1,52] | +0,64% [−0,17; +1,53] |
| DSR N=1000 (65/250/30000) | 0,114 (0,29/0,19/0,03) | 0,013 (0,12/0,04/0,0005) |
| placebo khối tháng p | 0,023 | 0,084 |
| LOCO min/max; top-5 cụm; mean bỏ top-5 | +0,71/+1,24%; 60%; +0,11% | +0,40/+0,94%; 93%; −0,39% |
| cụm có CAPIT fire / tổng | 4/17 | 6/15 |
| a trung bình: cụm có CAPIT / không | +3,45% / +1,42% | +3,86% / +1,66% |
| rổ-CAPIT (c) trên cụm FZ có CAPIT | +3,70% (a +3,45%) | +2,92% (a +3,86%) |
| **PASS "FZ thêm giá trị vs rổ"** (excess>0 ∧ CI90 loại 0 ∧ ≥20 cụm) | **FAIL** (CI chứa 0; 17<20) | **FAIL** (CI chứa 0; 15<20) |

Phí: (a)(b) dùng engine 0,16%/vòng, điều chỉnh thật −0,134% cho CẢ HAI (0,097%/chiều + thuế 0,1%) ⇒ excess không đổi sau phí; rổ nhiều mã trả đúng % phí như từng mã (không giả định ETF rẻ hơn — ETF rẻ hơn chỉ làm excess FZ nhỏ hơn). Dòng "rổ không tốn phí" là cận thận trọng ngược lại, trùng số audit trước.

## 3. Ba đường: CAPIT (c) và tương quan
- Rổ-CAPIT-fire (proxy, 55 mã, entry D+1, exit 10 phiên): in-sample **+2,94%** CI90 [1,54; 4,28]% trên 6 cụm (11 ngày fire); holdout 1 cụm (7 ngày) +1,87% — chỉ mô tả. Trên 4–6 cụm FZ trùng CAPIT, rổ-CAPIT (+3,70% / +2,92%) ≈ mức FZ (+3,45% / +3,86%) ⇒ khi CAPIT fire, FZ không hơn rổ rõ ràng.
- Tương quan ngày (775 phiên 2023-09-11→2026-10-20, ngày `in_stats` signal): FZ-001 52 ngày, FZ-002 48, CAPIT 18; trùng 10 / 12; **phi 0,30 / 0,39**; P(CAPIT|FZ)=0,19 / 0,25; P(FZ|CAPIT)=0,56 / 0,67 (`out/day_correlation.csv`).

## 4. Caveat
- Rổ (b) = engine nhóm kia (top-50 mcap PIT), không độc lập với deal-set; rổ (c) = proxy 55 mã xấp xỉ (universe_pit_q, không phải ticker_prune) — hiệu chuẩn corr 0,95–0,98 nhưng TP/SL kiểm daily, SL ưu tiên.
- In-sample là cận trên (nhóm kia tìm setup trên chính đoạn này); excess dương nhỏ ở đây càng bị thổi phồng. Số cụm 15–17 thấp cho mọi CI; "CI chứa 0" không có nghĩa "không có edge" — chỉ là không chứng minh được; hướng điểm ước +0,8% vẫn dương.
- Cụm FZ-có/không-CAPIT (4–13) <15 ⇒ không kết luận. Holdout 2 cụm ⇒ không kết luận. CAPIT fire định nghĩa theo cửa sổ [đầu cụm−5 phiên, cuối cụm] (khai trước).
- Trial thêm: 2 (FZ-001/002 so rổ) trên nền N=1000; kết quả không phụ thuộc N.
- Nguồn số: `out/basket_vs_fz.csv`, `out/clusters_*`, `out/capit_basket.csv`, `out/day_correlation.csv`, `out/log.txt`.
