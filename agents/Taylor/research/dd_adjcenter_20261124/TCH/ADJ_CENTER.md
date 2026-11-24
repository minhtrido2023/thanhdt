# TCH — Tâm kỳ vọng điều chỉnh (24/11/2026, job Taylor_20261124_110049)

Phương pháp: `../PREREG_adj.md` (`ef5157cb…`) + `../PREREG_adj_v2.md` (`835dfc1e…`). `calc_adj.py` assert cả hai md5. Chạy 2 lần cho run1 = run2 (md5 `1efd7fc9…`). Output: `adj.json`.
Mù giá: không đọc giá thị trường. Tâm gốc = sổ rev5 (dd_date 2026-10-31) **15.864 đ/cp** (sau CK 5 tỷ). `skeptic_final` = REFUTED_OPEN.
Nguồn: recheck 24/11 (`REPORT_recheck_TCH.md`, skeptic `r1_raw.md`); độ lớn lấy từ các bản song song của mô hình r3b (`REPORT_r3b.md` §5) và stress của skeptic vòng 05/11 (`dd_redo_20261105/TCH/skeptic/r1_raw.md`).

## Kết luận
**Tâm kỳ vọng điều chỉnh: 15.152 đ/cp (Σ p×m = −4,49%). Dải theo cực trị (p, m): 14.369–15.780.**
Hiện không có cổ tức tiền nào đã công bố mà chưa GDKHQ (thưởng 10:1 đã thực hiện 10/09/2026), nên chỉ có một dòng kết luận.
`FLOOR_FAIL` (CF_OA_3Y −771,7 tỷ) vẫn loại TCH khỏi candidate, bất kể tâm.

Kiểm tương tác:
- Theo v2 §5, Σ = 4,49% ≤ 5% nên cộng tuyến tính.
- Tôi vẫn kiểm thêm một chiều. Khi biên 42,7%, hạng mục NOXH và dạng chính xác đều co theo hệ số 0,780 (m = 0,8(g − 0,10)). Tính lại theo cách này thì tâm ra 15.147 (−4,52%). Lệch 5 đ, không đổi kết luận.

## 1. Hạng mục vào tâm
| # | Hạng mục | Hướng | m (% tâm) [khoảng] | Bậc | p [thấp; cao] | p×m | Nguồn |
|---|---|---|---|---|---|---|---|
| 1 | Biên BĐS base 51,9% (6T FY26 chưa soát xét) → 42,7% kiểm toán | ↓ | −14,01 (song song mô hình r3b ⇒ 13.642) | B | 0,35 [0,15; 0,55] | −4,90 | r3b:92,103-104; recheck:46 |
| 2 | NOXH Green River hưởng biên thương mại trong mô hình | ↓ | −1,73 [−3,03; −1,73] ước lượng | C+ | 0,50 [0,25; 0,75] | −0,86 | notes_read:140,146; skeptic 05/11 r1:10-12 |
| 3 | Dạng chính xác C_unsold, thay dạng thận trọng | ↑ | +3,64 (song song r3b ⇒ 16.442) | B | 0,35 [0,15; 0,55] | +1,28 | r3b:91; recheck skeptic (symmetry) |
| | **Σ** | | | | | **−4,49** | |

Cơ sở chọn p:
- **#1.** Hai kỳ kiểm toán cùng hướng: FY24 42,7% và FY25 42,7%. Có quan sát ngược bằng số: 6T FY26 51,9% (chưa soát xét) và 6T FY25 51,0% (đã soát xét). Vì vậy dùng nhánh "ngược".
- **#2 (C+).** Hạng mục này vào được tâm vì hai lẽ:
  - Dấu chắc chắn. Green River có 441 căn NOXH trên 1.251 căn và đang thi công khu NOXH. Lợi nhuận NOXH có trần, nhưng mô hình áp biên 51,9% cho mọi chi phí còn lại.
  - Có cận bảo thủ: tỷ trọng 20% cho −274 đ. Cận cao 35% (≈ 441/1.251 căn) cho −480 đ.
  - Hai con số trên là stress của skeptic tính trên r3, nên là ước lượng. Chỉ có 1 nguồn, nên p theo B1.
- **#3.** Có 1 quan sát (k đo được). Quan sát ngược bằng số: k của H2 = 2,958, bất thường vì HTK mới bằng 25% TMĐT dù đã "xong thô". Điều này cho thấy k đo được kém tin cậy, nên dùng nhánh ngược.

## 2. Chỉ độ nhạy — KHÔNG vào tâm
| Hạng mục | Hướng | Độ nhạy | Vì sao không vào tâm |
|---|---|---|---|
| NOXH NC-II (TM19: đặt cọc thuê NOXH An Hải 57,2 tỷ) | ↓ | tỷ trọng 10–20% ⇒ −288…−576 đ (−1,82…−3,63%) | C: chưa có văn bản xác nhận NC-II có NOXH, dấu chưa chắc |
| Trích quỹ KTPL từ thặng dư tương lai | ↓ | ≈ −1,8% nếu 5%; mỗi 1pp ≈ −0,36% | C thuần. TM34 ghi "chưa trích", CĐKT không có dòng tồn quỹ, nên cận bảo thủ từ dữ liệu = 0 |
| HTM 678,3 tỷ "Sài Gòn Tài Lộc" chưa xác minh | ↓ | mất 100% ⇒ −670 đ (−4,22%) | C: không có dữ liệu về xác suất mất |
| H2 k = 2,958 (chặn k_H2 = 1) | ↓ | 15.568 (−1,87%) | Cùng trục k với #3 và đã dùng làm quan sát ngược ở #3, nên không đếm hai lần |
| Thu tiền theo tiến độ (người mua trả trước 5.599,8 tỷ); giá bán không tăng tới 2030; quỹ đất mới NPV0 | ↑ | chưa định lượng | C |
| [LUẬT] CK holding: dải 0…+20% (đo cho HHS), base 0% | ↓ | +20% ⇒ 14.294 (−9,90%) | Tham số house (Bước 0). User chưa chốt có áp cho TCH hay không |
| [LUẬT] r 13,5% so với dải Ke (E15) | ↑ | Ke 12,3% ⇒ 16.270 (+2,56%) | Tham số luật V1 |
| [LƯỚI] y = 4 mọi dự án, k = 0 | ↓ | 13.435 (−15,3%) | Trục/trọng số lưới = luật |

## 3. BẢNG ĐIỀU KIỆN ĐỔI SỐ
Δ tính trên tâm 15.864.

| Sự kiện / dữ kiện | Khi nào (ước lượng lịch) | Đổi gì | Δ tâm (đ/cp) | Δ % |
|---|---|---|---|---|
| **Báo cáo soát xét 6T FY26 (AASC) xác nhận biên BĐS ≈51,9%** | 11–12/2026 (chưa xác minh đã công bố chưa) | p#1 0,35 → 0,15 | +444 | +2,80 |
| **Báo cáo soát xét 6T FY26 điều chỉnh biên xuống ≤45%** | 11–12/2026 | mất quan sát ngược ⇒ p#1 → 0,90 | −1.222 | −7,70 |
| BCTC Q3 FY26 (quý đến 31/12/2026): biên BĐS quý | cuối 01/2027 | thêm 1 kỳ cho phía tương ứng. Cả hai phía đều có số nên nhánh p chưa đổi | 0 | 0 |
| BCTC FY26 kiểm toán (năm đến 31/03/2027): biên ≥50% | 06/2027 | p#1 → 0,15 | +444 | +2,80 |
| BCTC FY26 kiểm toán: biên ≤45% | 06/2027 | p#1 → 0,90 | −1.222 | −7,70 |
| QĐ đầu tư / BCTN: tỷ trọng chi phí NOXH Green River 35% | khi đọc được | #2 C+ → A, p 0,9 (ở 20%: −0,86%) | −295 | −1,86 |
| Văn bản xác nhận NC-II có quỹ NOXH 20% | khi có | C → A, mỗi 10% tỷ trọng | −259 | −1,63 |
| NQ ĐHĐCĐ (~06–07/2027): tỷ lệ trích KTPL 5% | 06–07/2027 | C → A | −257 | −1,62 |
| Xác minh đối tác HTM là TCTD được cấp phép | khi đọc PDF gốc | đóng hạng mục; nếu KHÔNG phải TCTD ⇒ thành hạng mục B | 0 | 0 |
| User chốt CK holding +20% áp cho TCH | khi user quyết | đổi luật ⇒ chạy lại mô hình | −1.570 | −9,90 |
| Lãi huy động 12T ±50bp (luật V1) | liên tục | r | −164 / +167 | −1,03 / +1,05 |

**Điều kiện đổi số quan trọng nhất:** biên BĐS trong báo cáo soát xét 6T FY26. Kết quả này làm tâm dao động từ −7,7% đến +2,8%, lớn hơn mọi hạng mục khác cộng lại.
