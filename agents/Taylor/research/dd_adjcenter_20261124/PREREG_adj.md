# PREREG — Tâm kỳ vọng điều chỉnh (dd_adjcenter_20261124) — khoá TRƯỚC khi tính

Job: Taylor_20261124_104632 (pilot FPT). Chỉ đạo user 24/11: không dừng ở nhãn INCONCLUSIVE; dự báo tốt nhất trên thông tin đang có, cập nhật khi có dữ kiện mới.
MÙ GIÁ: không đọc giá thị trường / forward return khi dựng. Tâm gốc = `center` của rev mới nhất trong `kb/dd_price_zones.json` (chỉ đọc).

## 1. Bậc bằng chứng (cố định)
- **A** — số trực tiếp từ BCTC / văn bản công ty (dòng thuyết minh, NQ, CBTT). → p vào tâm.
- **B** — suy từ lịch sử của chính mã hoặc peer, CÓ dữ liệu trong tay (file:dòng). → p vào tâm, dải theo p.
- **C** — không có cơ sở dữ liệu cho độ lớn (chỉ là "có thể", "nếu tỷ lệ là X"). → CHỈ độ nhạy, KHÔNG vào tâm (khớp V4).

## 2. Thang p (cố định, áp cơ học)
- A: p = 0,90, dải [0,75; 1,00]. Hạ dưới mặc định chỉ khi nêu rõ lý do quyền sở hữu/quy đổi.
- B: mặc định p = 0,50 [0,25; 0,75] (1 quan sát độc lập).
  - ≥3 quan sát độc lập cùng hướng: 0,65 [0,40; 0,90].
  - Có quan sát trong tay đi ngược hướng: 0,35 [0,15; 0,55].
  - Hai số cùng kỳ (vd LNST và LNTT của cùng 9 tháng) tính là MỘT quan sát.
- C: p không định nghĩa (không vào tâm).

## 3. Công thức
- tâm_adj = tâm × (1 + Σ p_i × m_i), chỉ i thuộc A/B. m_i = % tâm (dấu theo hướng).
- range_low/high = tâm × (1 + Σ cực trị p_i × m_i) — với mỗi hạng mục, chọn đầu p cho tích nhỏ nhất / lớn nhất. m giữ nguyên số nguồn.
- Cộng tuyến tính các probe độc lập (bỏ qua tương tác) — ghi rõ là xấp xỉ.

## 4. Chống đếm hai lần + phân loại
- **Tham số do luật house chốt KHÔNG phải hạng mục**: r neo V1 (13,5% = neo lãi huy động + β×Δ), RONIC terminal = Ke, trọng số kịch bản, moat. Đổi chúng là đổi luật, không phải bổ sung bằng chứng. Áp ĐỐI XỨNG: chiều lên (r > dải Ke ⇒ E15) và chiều xuống (chặn RONIC 5 năm) đều chỉ hiển thị ở mục "tâm thay thế theo luật", không vào Σ. r vs dải Ke vs E15 = MỘT dòng.
- Cổ tức tiền đã công bố, chưa GDKHQ: xử lý CƠ HỌC riêng, CỘNG TRỪ theo đ/cp (không nhân %), báo hai số: tâm_adj (có quyền) và tâm_adj (sau GDKHQ).
- Hạng mục chồng nhau (vd cam kết capex vs hệ số chuyển đổi conv): phần có dữ liệu lịch sử vào hạng mục conv (B); phần VƯỢT lịch sử (cam kết mới chưa đọc) = C riêng. Không đưa cùng một dòng tiền vào hai hạng mục.
- Tồn quỹ (stock) và trích quỹ hằng năm (flow) là hai hạng mục khác nhau.

## 5. Mỗi hạng mục phải ghi
Tên, hướng, m (% tâm; số skeptic/báo cáo; không có số ⇒ khoảng gắn nhãn "ước lượng" + cơ sở), bậc, p (theo thang §2) + lý do chọn nhánh thang, nguồn file:dòng, counted_in_center.

## 6. Chiều lên tính ngang hàng chiều xuống
Mọi hạng mục `too_low` của skeptic (symmetry) đều được kiểm kê và xếp bậc như hạng mục chiều xuống.

## 7. Bảng điều kiện đổi số (bắt buộc)
Mỗi hạng mục B/C ⇒ sự kiện/dữ kiện cụ thể sẽ đổi bậc hoặc p, hướng, Δ tâm (đ/cp và %). Thay cho câu "thiếu dữ kiện".

## 8. Kiểm kê FPT (khoá trước khi tính; nguồn `dd_recheck_20261124/FPT/skeptic/r1_raw.md` = S, `dd_FPT_20261101/calc/notes_q3_bctc.md` = N)
| # | Hạng mục | Hướng | Bậc | Nhánh thang p |
|---|---|---|---|---|
| 1 | Tồn quỹ KTPL 1.477 tỷ chưa trừ khỏi NC (S:14, N:69) | xuống | A | mặc định A |
| 2 | XDCB "Khác" 371 tỷ chưa cộng (S:24, N:344) | lên | A | mặc định A |
| 3 | Pha loãng ESOP (108 tỷ mệnh giá 9T26; S:16, N:321) | xuống | B | 1 quan sát |
| 4 | conv CƠ SỞ 0,75 vs thực tế (FY25 0,60; 9T26 −0,12; S:17) | xuống | B | 2 quan sát cùng hướng ⇒ mặc định (chưa đủ 3) |
| 5 | g CƠ SỞ 9% vs LFL 9T26 +13,7% / LNTT CN +16,6% (S:22) | lên | B | 1 quan sát (cùng kỳ); có quan sát ngược (5F: Nhật Q3 giảm tốc) ⇒ nhánh ngược |
| 6 | Cam kết capex DC/AI/giáo dục chưa đọc (S:13) — phần vượt lịch sử conv | xuống | C | — |
| 7 | Trích quỹ KTPL hằng năm (tỷ lệ chưa kiểm; N không có dòng trích KTPL 9T26) | xuống | C | — |
| 8 | OTHER_ASSOC_BOOK 1.500 tỷ [UL] (S:23,39) | hai chiều | C | — |
| 9 | Lãi LK Q4/25 600 tỷ [UL] G10 (REPORT_recheck:62) | hai chiều | C | — |
| L1 | r 13,5% > dải Ke 12,3–13,4% (E15) | lên | luật | không vào Σ |
| L2 | Chặn RONIC pha 5 năm ở Ke (bản G) | xuống | luật | không vào Σ |
| D | Cổ tức tiền 1.000 đ chốt quyền 30/11 (S:18) | xuống | cơ học | tách riêng |
