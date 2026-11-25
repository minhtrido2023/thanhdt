# NT2 — Tâm kỳ vọng điều chỉnh (E17 / V9) · 25/11/2026 · job Taylor_20261125_032446

**Tâm kỳ vọng điều chỉnh: 25.038 đ/cp (dải 21.938–29.039; +4,31% so với tâm base 24.003); căn cứ 4 hạng mục bậc A/B/C+ (1 A, 2 B, 1 C+)**

- Lý do áp V9: skeptic DD_GENERAL `skeptic/r1.json` = **REFUTED (medium)** ⇒ sổ đề xuất `REFUTED_OPEN`.
- Phương pháp khoá trước: `PREREG_adj.md` (md5 `ef5157cb3f762d58623ed550ebc214c7`) + `PREREG_adj_v2.md` (md5 `835dfc1e07f9c67ac7f6c3028b529d13`); kiểm kê hạng mục mã này khoá TRƯỚC khi tính ở `ADJ_PREREG_NT2.md` (md5 `9cf0946d4f00d8a66c1a36400555e097`, assert trong code).
- Tính: `calc/calc_adj.py` — mọi hạng mục chạy QUA mô hình r3 (`np_shift`/`fcf_shift` của lưới 225 kết cục; khoản t=0 cộng vào net cash, sau CK 0,92%), CONTROL stdout md5 `f2c6788a…` = r3. Hai lần chạy trùng byte (`calc/adj_run1.txt` = `adj_run2.txt`, md5 `8ba93695…`). Mô hình tuyến tính theo dịch chuyển dòng tiền ⇒ tổ hợp = tổng tuyến tính (+4,312% cả hai cách). |Σ| = 4,31% < 5% ⇒ không bắt buộc chạy tổ hợp riêng (đã chạy qua mô hình dù sao).
- MÙ GIÁ: không đọc giá thị trường khi dựng.

## Hạng mục vào tâm
| # | Hạng mục | Hướng | Bậc | Đầu vào (tỷ) [dải] | m % tâm | p [dải] | p×m | Nguồn |
|---|---|---|---|---|---|---|---|---|
| N1 | Biên LNST thời kỳ đã hết khấu hao máy chính: FY2025 14,2%, 9T/26 11,6% vs base 11,2% (800/7.137) | lên | B (2 kỳ cùng hướng) | LNST +121 [+29; +214]/năm | +9,04% | 0,50 [0,25; 0,75] | **+4,52%** | S killer; BS 420b (1.130,28 FY25; 906,36 9T/26); DT BQ |
| N2 | FCF − LNST thời kỳ hết khấu hao: FY2025 −136, 9T/26 +252 ⇒ +66/năm (base 0) | lên | B (có quan sát ngược) | +66 [−136; +252]/năm | +4,93% | 0,35 [0,15; 0,55] | **+1,73%** | S; `fin_nt2_r3.csv` |
| N3 | Nợ ngắn hạn ngoài net cash/NWC (thuế phải nộp 113,26 + NLĐ 26,37 + phải trả khác 0,86 + quỹ KTPL 37,90) trừ tài sản ngắn hạn ngoài (VAT 77,45 + trả trước NB 2,81 + phải thu khác 0,23 + CP trả trước NH 6,02) | xuống | A | −91,88 tại t=0 | −1,32% | 0,90 [0,75; 1,00] | **−1,19%** | BS 30/09/2026 mã 314/315/320/323/132/135/161/162 (`img/p06.png`, `p07.png`) |
| N4 | Trích quỹ KTPL hằng năm từ LNST — cận bảo thủ ≥2,5% LNST (quỹ tăng ròng 28,39 trong 9T/26 ÷ LNST 2025 1.130,28) | xuống | C+ | LNST −20 [−40 (5%, ước lượng); −20]/năm | −1,49% | 0,50 [0,25; 0,75] | **−0,75%** | BS mã 323 (9,51 → 37,90) |
| | **Σ** | | | | | | **+4,31%** | |

Dải 21.938–29.039 = tổ hợp chạy qua mô hình, mỗi hạng mục ở cực trị (p, m) cho tích nhỏ nhất / lớn nhất. Đóng góp cực trị: N1 [+0,54%; +11,99%], N2 [−5,59%; +10,35%], N3 [−1,32%; −0,99%], N4 [−2,24%; −0,37%].

## Chỉ độ nhạy (bậc C — KHÔNG vào tâm)
- C1 Giá công suất PPA điều chỉnh giảm khi hết khấu hao (xuống): chưa có số hợp đồng. Đây là phản lực chính của N1 — biên 9T/26 11,6% thấp hơn FY25 14,2% gợi ý lợi ích khấu hao chỉ chuyển một phần.
- C2 Hàng tồn kho 346,40 tỷ (lên): không có cơ sở giá trị thu hồi; chưa tính, chỉ ghi hướng.
- C3 Nghĩa vụ hoàn nguyên/môi trường cuối đời nhà máy (xuống): chưa đọc thuyết minh.
- C4 Q3/26 chưa soát xét (xuống): tiền lệ H1 −94 tỷ, không có số cho Q3.
- C5 Rủi ro đối tác tiền gửi SHB (xuống): không có thuyết minh theo ngân hàng.
- X1 Ưu đãi thuế TNDN: ĐÓNG — thuế TNDN Q3/26 20,1% đã ở mức phổ thông (`dd_redo_20261105/NT2/REPORT.md:33`), m = 0.

## Tham số luật (KHÔNG vào Σ)
- L1 r 13,5% > dải Ke: Tâm @ Ke 12,3% = 24.638 (+2,64%) — dòng E15 ở REPORT_recheck §0.
- L2 Giá trị sau thời hạn = 0 (moat NONE); độ nhạy WIDE +19,7% (khung r2, ADDENDUM_5F) chỉ hiển thị.
- Cổ tức: 1.000 đ đã GDKHQ 29/10/2026; không còn quyền chưa chốt ⇒ chỉ một dòng tâm.

## Bảng điều kiện đổi số
| Sự kiện / dữ kiện | Ngày dự kiến | Hướng | Δ tâm điều chỉnh |
|---|---|---|---|
| BCTC Q4/2026 + kiểm toán FY2026: biên LNST năm ≥ 11,2% (quan sát thứ 3 cùng hướng ⇒ N1 p 0,65) | 31/01 & ~03/2027 | lên | +1,36% (≈ +326 đ) |
| — ngược lại biên FY2026 < 11,2% (quan sát ngược ⇒ N1 p 0,35) | như trên | xuống | −1,36% (≈ −326 đ) |
| Kiểm toán FY2026 điều chỉnh giảm 9T (kiểu H1 −94 tỷ) | ~03/2027 | xuống | qua N1: biên 9T/26 (906−94)/7.803 = 10,4% ⇒ N1 TB +78 thay +121 ⇒ −1,6% (≈ −384 đ); nếu coi là quan sát ngược (p 0,35) thêm ≈ −0,6% |
| NQ ĐHĐCĐ 2027 công bố tỷ lệ trích KTPL (N4 lên A, p 0,90) | ~04/2027 | xuống | 2,5% ⇒ −0,60% (≈ −143 đ); 5% ⇒ −1,94% (≈ −466 đ) |
| Hợp đồng/PPA cho thấy giá công suất giảm sau khi hết khấu hao (C1 lên A/B) | khi đọc được | xuống | chạy lại mô hình (rev mới); nếu biên về 10,4% lịch sử ⇒ N1 về ≈ 0 ⇒ ≈ −4,5% |
| Phụ lục 13 GSA / BCTN: thời hạn PPA-GSA | khi đọc được | hai chiều | chạy lại trục thời hạn (rev mới); song song A (khí cạn 2030) base −3,6% |
| Lịch sử chi phí trả trước đại tu 2015–25 (đại tu tiền mặt ≈ phân bổ ⇒ N2 rõ chiều lên) | BCTC năm | lên | N2 p 0,50 ⇒ +0,74% (≈ +178 đ) |
| Thuyết minh nghĩa vụ hoàn nguyên X tỷ (C3 lên A) | BCTC năm | xuống | −X/287,9 × 1.000 × (1/(1,135)^thời hạn) đ/cp |

Nhãn `skeptic_final` = REFUTED_OPEN là trạng thái phản biện, KHÔNG phải quan điểm đầu tư. Tâm điều chỉnh KHÔNG thay tâm base trong sổ/luật 0,85×tâm/luật 4; watch chỉ dùng để SIẾT đáy.
