# r4 — mục đã áp (job Taylor_20261122_094712) — TRUNG THỰC
assumptions md5 `85d41e08f834127e57cd740ed88dd931` (r3: `55731df5…`). calc.py chạy lại → `calc_r4_output.txt`. Số dòng = REPORT.md sau r4 (tự định vị theo nội dung).
Tâm KHÔNG đổi: 35.497. Đổi: bear 30.359→28.958, có trọng số 39.137→38.787, thêm số cổ tức tiền/ROE 2025.

| # | Trạng thái | Chi tiết / vị trí |
|---|---|---|
| 1 | ÁP đủ | §0 dòng 16 ("hai nguồn": ROE bền + Ke, ROE giải thích ~58% khoảng chênh 35.497→52.100, giá trị 45.071 ở ROE 16,65%) và "Đọc nhanh" ~:32 |
| 2 | ÁP đủ, nguồn pháp lý do dispatch cung cấp | §4 ~:118 (tên cũ CBBank + QĐ 2299, QĐ 30, B02 tr.7, TM1 tr.15), bỏ "[NỀN…]" và "skeptic R2"; calc.py bỏ comment "skeptic R2/chưa tự đối chiếu"; §10 viết lại. **Các nguồn BCTC KT 2025 chưa render lại từ PDF scan trong phiên này** (theo dispatch) |
| 3 | ÁP MỘT PHẦN | Bảo lãnh 287→5.885→9.549 và ×2,37 (138.449/58.339, ~55% VCSH) ghi WARNING ngoại bảng, không nhân vào mô hình (§3 ~:90); +72% Xây dựng, top-10 không công bố (~:89); ý kiến EY toàn phần ở §0 header, §8, §10. **Các số Q3/Xây dựng/bảo lãnh ghi "theo kiểm tra độc lập, chưa render lại"** — chưa đối chiếu với src/ (PDF scan, tôi không OCR). Cụm "môi trường không có công cụ" đã bỏ khỏi header và §10 |
| 4 | ÁP đủ | §4 bảng CAR (~:102) và §5 ROE-CET1 (~:139) |
| 5 | ÁP đủ | §6 ~:208: bỏ phép so 14,6% < ROE_Min5Y; thêm ROE chuẩn hoá 13,2% < Ke 13,5% làm điều kiện (i) yếu đi |
| 6 | ÁP đủ | §4 ~:113-114: cổ tức tiền 2.433 đ/cp, sau GDKHQ 32.652 (−8,0%), tổng cổ đông 35.085 (−1,2%), trừ ~2.845 (`calc.py` `val_post_gdkhq`); thêm dòng nhắc trước "Vùng đọc" §5 |
| 7 | ÁP đủ | assumptions `scenarios.bear.roe` 0,135→0,132; REPORT §0 :16/:26, bảng kịch bản (xấu 29.000, P/B 0,95; trọng số 38.800), md5. Lưu ý: 13,2% là ROE 2025 chuẩn hoá (trần trên mô tả), mô tả "NIM −30bp + CC 1% ⇒ ~12,3%" ghi kèm, KHÔNG tự tính lại 12,3% trong calc.py |
| KHÔNG chặn | ÁP | 56%→52% (§5 hai giai đoạn); VCSH đầu kỳ → BCTC kiểm toán (§5 lịch sử); calc.py khối `is_2025_audited` → ROE 2025 chuẩn hoá 13,21%; dòng CC cho vay 0,473% (§3 bảng + `cc_loans_9m_ann`) |

## Chưa làm / hạn chế
- VCSH cuối 2025 trong khối is_2025 = 224.487,2 (theo dispatch) khác 224.516 (= 224.587,75 − NCI 71,5 từ bs_31_12_2025_restated): chênh ~29 tỷ (khớp "VCSH riêng lẻ +29 tỷ" Phụ lục II?) — chưa xác minh; ảnh hưởng ROE 2025 <0,01pp.
- Không dựng PDF, không email, không ghi dd_price_zones.json.
