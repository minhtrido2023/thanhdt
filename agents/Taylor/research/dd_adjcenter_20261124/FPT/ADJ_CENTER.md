# FPT — Tâm kỳ vọng điều chỉnh (pilot, 24/11/2026, job Taylor_20261124_104632)

Phương pháp: `../PREREG_adj.md`, khoá trước khi tính (md5 `ef5157cb…`, commit `e6b65e786`). Calc: `calc_adj.py` (assert md5 PREREG). Chạy 2 lần cho run1 = run2 (md5 `4e4f43a8…`). Output: `adj.json`.
Mù giá: không đọc giá thị trường. Tâm gốc = sổ rev4, 57.312 đ/cp (`skeptic_final` = REFUTED_OPEN, giữ nguyên nghĩa: đây là trạng thái phản biện, không phải quan điểm).

## Kết luận
**Tâm kỳ vọng điều chỉnh: 56.204 đ/cp (−1,93% so với tâm 57.312). Dải theo p: 55.092–57.345.**
**Sau GDKHQ cổ tức 1.000 đ (chốt quyền 30/11): 55.204, dải 54.092–56.345.**

Đây là dự báo tốt nhất trên thông tin đang có. Các hạng mục còn trống không làm "chưa kết luận" được. Chúng nằm ở bảng điều kiện đổi số (§4), mỗi dòng ghi sự kiện nào sẽ đổi tâm, đổi bao nhiêu.

## 1. Hạng mục vào tâm (bậc A/B)
| # | Hạng mục | Hướng | m (% tâm) | Bậc | p [thấp; cao] | p×m | Nguồn |
|---|---|---|---|---|---|---|---|
| 1 | Tồn quỹ KTPL 1.477 tỷ chưa trừ khỏi NC (783 đ/cp) | ↓ | −1,37 | A | 0,90 [0,75; 1,00] | −1,23 | notes_q3_bctc.md:69; r1_raw.md:14 |
| 2 | XDCB "Khác" 371 tỷ chưa cộng (197 đ/cp; NPV 0 như XDCB giáo dục) | ↑ | +0,34 | A | 0,90 [0,75; 1,00] | +0,31 | notes:344; r1_raw:24 |
| 3 | Pha loãng ESOP (108 tỷ mệnh giá 9T26) | ↓ | −2,50 (số skeptic) | B | 0,50 [0,25; 0,75] | −1,25 | notes:321; r1_raw:16 |
| 4 | conv CƠ SỞ 0,75 → 0,60 (FY25 0,60; 9T26 −0,12) | ↓ | −1,85 (probe model_r3) | B | 0,50 [0,25; 0,75] | −0,93 | r1_raw:17,47 |
| 5 | g CƠ SỞ 9% → 12% (LFL 9T26 +13,7%) | ↑ | +3,32 (probe model_r3) | B | 0,35 [0,15; 0,55] | +1,16 | r1_raw:22,47 |
| | **Σ** | | | | | **−1,93** | |

Lý do chọn p (theo thang PREREG §2):
- #3 có 1 quan sát ⇒ mặc định.
- #4 có 2 quan sát cùng hướng, chưa đủ 3 ⇒ mặc định.
- #5 chỉ có 1 quan sát: LNST và LNTT cùng kỳ tính là một. Lại có quan sát ngược (5F: Nhật Q3 giảm tốc, REPORT_recheck:56) ⇒ nhánh "ngược".

## 2. Chỉ độ nhạy (bậc C / tham số luật) — KHÔNG vào tâm
| Hạng mục | Hướng | Độ nhạy | Vì sao không vào tâm |
|---|---|---|---|
| Cam kết capex DC/AI/giáo dục vượt lịch sử conv | ↓ | Mỗi 1.000 tỷ cam kết NPV âm toàn phần: −0,93% (−530 đ/cp) | C: chưa đọc thuyết minh, không có số. Phần capex đã hiện trong lịch sử nằm ở #4 (không đếm hai lần) |
| Trích quỹ KTPL hằng năm từ LNST | ↓ | 5% ⇒ −3% (skeptic); mỗi 1pp ≈ −0,59% | C: BCTC 9T26 không có dòng trích KTPL; tỷ lệ chưa kiểm |
| OTHER_ASSOC_BOOK 1.500 tỷ [UL] | ↕ | −1.300…+2.600 đ/cp (−2,27…+4,54%) | C: thuyết minh không tách giá trị từng liên kết (notes:277) |
| Lãi LK Q4/25 600 tỷ [UL] G10 | ↕ | 740 tỷ ⇒ 56.616 (−1,21%) | C |
| [LUẬT] r 13,5% so với dải Ke (E15) | ↑ | Ke 12,3%: 61.176 (+6,74%); Ke 13,4%: +0,51% | Tham số luật V1, không phải bằng chứng thiếu; áp đối xứng với dòng dưới |
| [LUẬT] Chặn RONIC pha 5 năm ở Ke (bản G) | ↓ | 50.652 (−11,62%) | Tham số luật moat/V5 |
| Cổ tức 1.000 đ chốt 30/11 | ↓ | −1.000 đ (−1,74%), cơ học, chắc chắn | Tách riêng, trừ theo đ/cp; có hai dòng kết luận ở trên |

## 3. Không đếm hai lần
- r 13,5% > dải Ke, E15 và skeptic "đến +6,7%" là **một** dòng luật, không vào Σ.
- Capex: phần đã thể hiện qua conv lịch sử nằm ở #4 (B). Chỉ phần cam kết mới, vượt lịch sử, là C.
- Quỹ KTPL: tồn quỹ (stock, #1) và trích hằng năm (flow, C) là hai hạng mục khác nhau.
- Cổ tức không nằm trong Σ%.

## 4. BẢNG ĐIỀU KIỆN ĐỔI SỐ (thay cho "thiếu dữ kiện")
Δ tính trên tâm 57.312. Mỗi dòng là một sự kiện độc lập; các dòng cộng được với nhau (xấp xỉ tuyến tính).

| Sự kiện / dữ kiện | Khi nào | Đổi gì | Δ tâm (đ/cp) | Δ % |
|---|---|---|---|---|
| GDKHQ cổ tức tiền 1.000 đ (chốt 30/11; ngày GDKHQ cần xác nhận CBTT) | cuối 11/2026 | Cơ học | −1.000 | −1,74 |
| BCTC Q4 + năm 2026: thuyết minh cam kết vốn DC/AI/giáo dục | ước lượng cuối 01/2027* | C→A; mỗi 1.000 tỷ cam kết NPV âm. Growth NPV≈0 ⇒ 0 | −530 / 1.000 tỷ | −0,93 / 1.000 tỷ |
| BCTC năm 2026: conv FY26 ≤ 0,60 | ước lượng cuối 01/2027* | p#4 0,50→0,90 | −424 | −0,74 |
| BCTC năm 2026: conv FY26 ≥ 0,75 | ước lượng cuối 01/2027* | p#4 0,50→0,10 | +424 | +0,74 |
| LNST LFL cả năm 2026 ≥ 12% và Nhật không giảm tốc tiếp | ước lượng cuối 01/2027* | p#5 0,35→0,65 | +571 | +1,00 |
| LNST LFL cả năm 2026 < 9% | ước lượng cuối 01/2027* | p#5 0,35→0 | −666 | −1,16 |
| Tài liệu/NQ ĐHĐCĐ 2027: tỷ lệ trích KTPL (ví dụ 5%) | ước lượng 03–04/2027* | C→A, p 0,9 | −1.547 | −2,70 |
| NQ ĐHĐCĐ 2027: ESOP cùng cỡ 2026 | ước lượng 03–04/2027* | p#3 0,50→0,90 | −573 | −1,00 |
| NQ ĐHĐCĐ 2027: KHÔNG có ESOP | ước lượng 03–04/2027* | p#3 0,50→0 | +716 | +1,25 |
| BCTC kiểm toán 2026 / BCTN25 điều chỉnh: lãi LK Q4/25 (ví dụ 740 tỷ) | ước lượng 03/2027* | C→A | −696 | −1,21 |
| Thuyết minh LK chi tiết: giá trị liên kết khác | ước lượng 03/2027* | C→A | −1.300…+2.600 | −2,27…+4,54 |
| Lãi huy động 12T hiệu dụng đổi (luật V1, β=1) | liên tục | r ±50bp | −1.406 / +1.519 | −2,45 / +2,65 |
| Số dư quỹ KTPL mới (mỗi BCTC quý) | mỗi quý | Tính lại m#1 = −số dư/SH/tâm | theo số | — |
| Pháp lý FTEL/Bộ Công an (quét sau 01/11) | khi có | Chỉ WARNING (luật 19), không vào tâm | 0 | 0 |

\* Lịch công bố là ước lượng theo nhịp thông thường, chưa xác minh với lịch CBTT của FPT.

Kịch bản gộp (chỉ để minh hoạ, tính tuyến tính, KHÔNG phải tâm): giả sử ĐHĐCĐ trích KTPL 5%, có ESOP, conv ≤ 0,60, LFL < 9% và không có cam kết NPV âm. Khi đó tâm (có quyền) ≈ 56.204 − 1.547 − 573 − 424 − 666 ≈ 52.994. Chiều ngược: không ESOP, conv ≥ 0,75, LFL ≥ 12% ⇒ ≈ 56.204 + 716 + 424 + 571 ≈ 57.915.

## 5. Rút kinh nghiệm pilot — đề xuất sửa PREREG trước khi fan-out 7 mã
1. **Bậc C quá chặt với hạng mục BIẾT CHẮC dấu.** Trích quỹ KTPL từ LNST hầu như chắc chắn âm, nhưng chưa có tỷ lệ nên bị loại khỏi tâm. Hệ quả: tâm lệch lên một cách có hệ thống, và đây là hạng mục lớn nhất (−2,7% nếu 5%). Đề xuất bậc **C+**: dấu chắc chắn + có cận bảo thủ từ dữ liệu trong tay (vd tồn quỹ ÷ LNST năm trước) ⇒ vào tâm ở cận đó với p bậc B. Nếu áp cho FPT, tâm sẽ thấp hơn 56.204, chưa tính.
2. **Dải chỉ theo p là quá hẹp.** m của ESOP (−2,5%) là ước lượng của skeptic. PV của pha loãng vĩnh viễn ~0,6%/năm có thể lớn hơn đáng kể (tôi chưa tính chặt). Đề xuất: dải = cực trị theo (p, m); m có khoảng khi nguồn là "ước".
3. **Đếm "quan sát độc lập" còn mơ hồ.** Hai năm conv có phải độc lập không? LNST/LNTT cùng kỳ? "Quan sát ngược" định tính (5F) có tính không? Cần định nghĩa cứng: 1 quan sát = 1 kỳ báo cáo; quan sát ngược phải có số.
4. **Phân loại tham số luật và hạng mục.** Tôi đã loại r/RONIC khỏi Σ theo cả hai chiều (PREREG §4). Đây là lựa chọn thiết kế lớn nhất: nếu tính r vào tâm ở giữa dải Ke, tâm +3–4% (ước lượng). Cần Mike/user chốt có giữ quy tắc này cho 7 mã còn lại không.
5. **Cộng tuyến tính các probe bỏ qua tương tác** (g↑ thường đi với conv↓). Với FPT, Σ nhỏ nên sai số chấp nhận được. Mã có |Σ| > 5% nên chạy lại model với tổ hợp.
6. **Nguồn calc gốc bị TRIM** (calc_r3 khôi phục từ `/tmp/ddrestore_B`). Fan-out cần bước khôi phục, hoặc chỉ dùng số probe skeptic như ở đây.
7. Cổ tức: phải ghi rõ mã nào có tâm "có quyền" và mã nào đã GDKHQ. Đã làm ở FPT bằng hai dòng kết luận.
