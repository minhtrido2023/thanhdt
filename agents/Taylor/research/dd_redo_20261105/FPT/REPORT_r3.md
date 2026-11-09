# DD REDO VÒNG 3 — FPT · 09/11/2026 · job `Taylor_20261108_180128`

> Áp đính chính fundamental-skeptic (`TOP5D_CORRECTIONS_20261108.md` mục FPT) đã được user duyệt. Mô hình = `calc/fpt_r2.py` (hằng số BCTC chép nguyên văn) + công tắc cấu hình trong `calc_r3/model_r3.py`.
> Tái lập: `$DNA_PYEXE -I calc_r3/model_r3.py` (chạy 2 lần: `run1.txt` = `run2.txt` md5 51b85a47…, `model_r3_out.json` 17ddd898… cả 2 lần). Docstring ghi `python3 -I` nhưng python3 hệ thống thiếu numpy ⇒ chạy bằng `/home/trido/thanhdt/wc_venv/bin/python -I`; file .py không sửa sau LOCK.
> LOCK giả định ghi **TRƯỚC** lần chạy đầu: `calc_r3/LOCK_r3_prerun.txt` (2026-11-09T01:05:07+07:00, 25 file upstream). Minh bạch: giá 50.800 đã biết từ dòng 1 của TOP5D_CORRECTIONS và từ truy vấn BQ trước LOCK.

## 1. Kết luận
| | Tâm | P10 | P50 | P90 | Giá 06/11 | Nhãn | % trọng số dưới giá |
|---|---|---|---|---|---|---|---|
| **r3 headline (sau CK 5 tỷ)** | **57.312** | **45.270** | 58.124 | **68.466** | 50.800 | **TRONG vùng** | 27,0% |
| r3 cỡ sleeve 40 tr | 57.410 | 45.347 | 58.224 | 68.584 | 50.800 | TRONG vùng | 26,9% |
| r2 (giá 04/11 53.900) | 54.203 | 32.389 | 55.182 | 74.557 | 53.900 | TRONG vùng | 47,5% (ở giá 06/11: 41,5%) |

- Giá thấp hơn tâm 11,4%, cao hơn P10 12,2%. **Luật 4 (giá ≤ 0,85 × tâm): KHÔNG đạt ở cả hai cỡ** — ngưỡng 48.715 (5 tỷ) và 48.799 (40 tr); giá đang cao hơn ngưỡng 4,3%.
- Nhãn TRONG giữ nguyên qua mọi bản song song A–J và bản có trục r (§4).
- **Mong manh ở một phía:** nếu chặn RONIC 5 năm ở ROIC5Y 17,7% thì tâm còn 52.311; chặn ở Ke thì còn 50.652 ≈ giá (D5).
- **Không đủ điều kiện sleeve fear-buy §2.5** (trượt ĐK1 vì không có trạng thái sợ hãi/scandal; trượt ĐK4).

## 2. Kiểm từng đính chính bằng calc (cầu nối r2 → r3, cộng dồn)
| Bước | Tâm | Δ | P10 | P90 | % dưới giá | Kiểm |
|---|---|---|---|---|---|---|
| 0 r2 tái lập (04/11) | 54.203 | — | 32.389 | 74.557 | 47,5% | trùng byte r2 ✔ |
| 1 D4 giá FPT/FOX/FRT + thanh khoản 06/11 | 53.834 | −370 | 32.060 | 74.166 | 41,9% | skeptic −368 ✔ (−2 do CK thanh khoản FPT 0,1866%→0,1881%) |
| 2 D1 trọng số 0,275/0,45/0,275 | 56.700 | +2.866 | 33.418 | 77.546 | 34,4% | skeptic +2.866 ✔ |
| 3 D2 RONIC terminal = Ke cả 3 kịch bản | 56.488 | −212 | 43.005 | 69.084 | 27,5% | skeptic +847 khi áp riêng; sau D1 còn −212 (thứ tự: trọng số XẤU nhỏ hơn ⇒ phần XẤU 5%→Ke được cộng ít hơn) ✔ |
| 4 D3 trừ CĐKKS 1.165,8 tỷ | 55.871 | −617 | 42.388 | 68.466 | 27,9% | = **điểm skeptic 55.872 / P10 42.389 / P90 68.468** ✔ |
| 5 D7 CK FTEL [UL] → độ nhạy, base 0% | **57.312** | +1.441 | 45.270 | 68.466 | 27,0% | skeptic "bỏ: 57.313" ✔ |

- **D1 CHẤP NHẬN.** Bản r2 đếm hai lần dữ liệu conv: đã hạ conv XẤU 0,60→0,40 lại còn nâng trọng số XẤU 0,30→0,35 dựa trên cùng dữ liệu đó. Không có dữ liệu độc lập cho việc nghiêng ⇒ đặt đối xứng (tiền lệ MBB D2). Bản giữ trọng số r2: B = 55.721.
- **D2 CHẤP NHẬN.** `moat_durable=false` (ADDENDUM_5F) ⇒ RONIC terminal = Ke ⇒ conv_T = 1 − gT/Ke (CƠ SỞ/TỐT 0,704; XẤU 0,778). Sau bước này trục Δg chỉ còn tác dụng qua (1+g)/Ke. Bản giữ RONIC r2 (>Ke): C = 57.524.
- **D3 CHẤP NHẬN.** Mã 429 = 1.165.791.218.519 đ (`notes_q3_bctc.md:85`). LNST CĐKKS 9T26 chỉ −1,6 tỷ (dòng 143–145), nên LN trong mô hình ≈ LN của công ty mẹ, còn phần CĐKKS nằm trên tài sản ròng đang được cộng 100% ⇒ trừ theo sổ là đúng. Bản không trừ: D = 57.929.
- **D4 CHẤP NHẬN.** BQ 06/11: FOX 53.800, FRT 142.000, FPT 50.800 (`calc_r3/px_fpt_r3_20261106.csv`).
- **D5 GIỮ RONIC 5 năm** (có một phần dữ liệu: năm 2025 ~48%), báo độ nhạy: chặn 25,5% (ROE TTM) → 54.472; 17,7% (ROIC5Y) → 52.311; Ke → 50.652. Các số của skeptic (53.032/50.871/48.717) đo khi còn CK FTEL; hai bộ số lệch nhau đúng +1.441 = D7 ✔.
- **D6:** lãi liên kết Q4/25 600 tỷ **chưa kiểm** (GAPS G10). Độ nhạy 740 tỷ → 56.616 (−696; skeptic ước ~−0,5k).
- **D7 CHẤP NHẬN theo luật user**: độ lớn CK FTEL 30/15/0% là [UL] ⇒ base 0%. Lý do bổ sung: giá FOX vốn đã là giá của cổ phần thiểu số. Bản giữ CK: **A = 55.871** (= điểm skeptic). **Lưu ý:** skeptic đặt điểm 55.872 khi vẫn giữ CK FTEL, còn headline r3 bỏ CK theo luật dispatch; nhãn TRONG không đổi ở cả hai bản.
- Độ nhạy tiền khách ứng trước 2.370 tỷ: I = 56.058 (bản A trừ tiếp: 55.871 − 1.254 = 54.617 = số skeptic ✔).
- **D8:** giá 50.800; r2 tính ở giá mới có 41,5% trọng số dưới giá ✔. Không có đính chính nào sai.

## 3. Ba con số (điều 4)
- Tâm (kỳ vọng lưới) **57.312**; P50 58.124; giá trị tại tham số trung tâm (CƠ SỞ, dconv 0, dg 0, FRT thị giá, LK khác theo sổ) 57.556.
- P10 do riêng nhánh XẤU quyết định, P90 do riêng nhánh TỐT. Giá trị từng kịch bản trước CK: XẤU 45.521 / CƠ SỞ 57.665 / TỐT 66.773 (bản r2: 35.142 / 58.311 / 73.212).

## 4. Lưới & bản song song
540 kết cục = kịch bản (3) × dconv (5) × dg (3) × FRT ±20% (3) × LK khác/TPB/FTS (4); phân vị bằng `wpct` (mid-block); min 40.048, max 74.358.
| Bản | Tâm | P10 | P90 | % dưới | Nhãn |
|---|---|---|---|---|---|
| A giữ CK FTEL 30/15/0 | 55.871 | 42.388 | 68.466 | 27,9% | TRONG |
| B trọng số r2 | 55.721 | 44.254 | 67.196 | 34,4% | TRONG |
| C RONIC_T r2 (>Ke) | 57.524 | 35.683 | 76.928 | 33,4% | TRONG |
| D không trừ CĐKKS | 57.929 | 45.887 | 69.084 | 26,0% | TRONG |
| E RONIC 5 năm chặn 25,5% | 54.472 | 45.270 | 60.570 | 27,0% | TRONG |
| F chặn 17,7% (ROIC5Y) | 52.311 | 45.270 | 56.489 | 27,8% | TRONG |
| G chặn Ke | 50.652 | 45.270 | 54.528 | 42,2% | TRONG |
| H LK Q4/25 740 | 56.616 | 44.813 | 67.549 | 27,2% | TRONG |
| I trừ tiền khách ứng trước | 56.058 | 44.015 | 67.212 | 27,7% | TRONG |
| J FOX/FRT giá 04/11 | 57.739 | 45.691 | 68.891 | 26,1% | TRONG |
| có trục r ±1pp (n=1.620) | 57.426 | 45.048 | 68.808 | 26,8% | TRONG |
Độ nhạy r (tâm): −100bp 60.478 · −50bp 58.831 · +50bp 55.906 · +100bp 54.602.

## 5. Giá ngụ ý (giá 50.800 = tâm khi…)
- r ≈ **16,20%** (lãi huy động 12T hiệu dụng ≈ 10,1%, so với 7,40% hiện nay). Nếu giữ CK FTEL: r ≈ 15,51% (khớp ước ~15,5% của skeptic).
- Hoặc RONIC 5 năm bị chặn ở **13,9% ≈ Ke**, tức thị trường coi tăng trưởng 5 năm tới không tạo giá trị.
- Hoặc trọng số XẤU ≈ **0,69** (giữ tỷ lệ CƠ SỞ:TỐT 0,45:0,275; `implied_wx_check.txt`). Nếu giữ cố định CƠ SỞ 0,45 thì ngay cả XẤU 0,55 / TỐT 0 vẫn cho tâm 53.031 > giá. Con số ≈0,49 của skeptic đo trên bản A với cách phân bổ khác — chưa tái lập.

## 6. Thanh khoản (điều 6)
ADV250 564,8 tỷ, ADV60 346,0 tỷ. CK ở cỡ 5 tỷ: 0,188% (theo ADV60: 0,221%), lệnh chiếm 0,885% ADV250 nên nằm trong vùng hiệu chỉnh. Cỡ sleeve 40 tr: 0,017%; 10 tr: 0,008% — cả hai dưới vùng hiệu chỉnh, CK thật ≈ nửa spread (chưa đo). Nhãn tính theo cỡ 5 tỷ; cỡ sleeve cũng TRONG vùng.

## 7. Đối chiếu Gordon (RONIC = Ke, trước CK)
Phương án A (lõi không gồm lãi tiền gửi + tiền ròng): g 4% 50.852 · g 5% 51.115. Phương án B (lõi + lãi tiền gửi ròng sau thuế, không cộng tiền ròng): 47.471 · 47.764. Gordon không tính 5 năm tăng trưởng vượt (RONIC 36–93%), nên dải này xấp xỉ bản G (50.652).

## 8. Giả định [UL] / tự đặt (đầy đủ trong `calc_r3/assumptions_r3.json`, mỗi dòng có basis + nguồn)
Trọng số đối xứng [UL] · conv 5 năm 0,40/0,75/0,85 ±0,2 · g 3/9/14% · trục FRT ±20% [UL] · trục LK khác −1.300/0/+1.100/+2.600 (0,2/0,3/0,3/0,2) [UL; T6a/T6b, kỳ vọng +590 đ/cp, chưa được phản biện ở vòng này] · LK khác 1.500 tỷ theo sổ (ước lượng) · LK Q4/25 600 [UL, chưa kiểm] · core_op trừ lãi tiền gửi ròng ×0,85 (ước lượng) · free float 80% (ước lượng).

## 9. Mốc HAI chiều + HARD ABANDON
Mốc nâng/hạ trọng số giữ như r2 §8 (CFO 2026, ký mới NN, JPY, cổ tức FTEL, lãi huy động ±100bp). Thêm 2 mốc:
- **Hạ:** LN mẹ 2026 tăng < +10% trong khi conv < 0,5 (RONIC thực tế tiến về Ke) ⇒ dùng bản F/G.
- **Nâng:** ROIC5Y BQ ≥ 20% hai quý liên tiếp.
HARD ABANDON giữ như r2 (kiểm toán ngoại trừ; khoản 618,8 tỷ không thu hồi; FTEL bị chuyển giao ngoài giá thị trường; CFO 2026 âm cả năm). **Ngưỡng nhãn mới:** DƯỚI vùng < 45.270; TRÊN vùng > 68.466. Luật 4 đạt khi giá ≤ 48.715.

## 10. WARNING pháp lý / quản trị (chỉ WARNING, không vào tâm)
Mang theo nguyên r2 §9 (FTEL / Bộ Công an / FOX free float; khoản 618,77 tỷ; vay ngoại tệ 30/09 trùng 30/06 [G15]; giao dịch bên liên quan 9T; BC quản trị 6T chưa đọc [G7]; ETR 11,1→15,2% [G11]; QĐ 1053 đã nộp — ĐÓNG). **Chưa quét pháp lý sau 01/11/2026** (ssc/gdt chưa tra trực tiếp). Tạm ứng cổ tức 1.000 đ chốt 30/11: giá 06/11 còn quyền và tiền ròng chưa trừ, hai bên nhất quán.

## 11. Thay đổi so với r2
Tâm 54.203 → **57.312 (+3.109)**; P10 32.389 → 45.270 (vùng hẹp lại vì XẤU được nâng lên RONIC = Ke); P90 74.557 → 68.466; % dưới giá 47,5% → 27,0%. Nhãn **TRONG → TRONG (không đổi)**. Đóng góp: D1 +2.866, D7 +1.441, D2 −212, D3 −617, D4 −370.

## 12. File
`REPORT_r3.md` · `SUMMARY.json` (r3; bản r2 cũ = `SUMMARY_r2.json`, trùng byte md5 1d14cc2f…) · `calc_r3/` (model, assumptions, LOCK_r3_prerun.txt, LOCK_r3_post_md5.txt, run1/run2, grid 540 kết cục, giá BQ) · ADDENDUM_5F.md / SUMMARY_5F.json được gắn ghi chú đồng bộ r3 (bản trước = `*_pre_r3.*`, trùng byte với hash trong LOCK). Không sửa `kb/dd_price_zones.json` (md5 ghi chỉ-đọc trong LOCK_post), không đặt lệnh, không email/PDF. Chưa qua phản biện cuối (Mike chạy).
