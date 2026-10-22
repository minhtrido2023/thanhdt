# PREREG — Livermore blind screen (ghi 2026-10-22 ~13:55 ICT, TRƯỚC khi sinh case / chạy agent)

Mục đích: sàng LOẠI THÔ xem một người đọc kỹ thuật độc lập (agent `livermore`) có hơn 3 baseline
đơn giản không. n nhỏ ⇒ chỉ loại được vô dụng rõ rệt, KHÔNG đủ để khẳng định có edge.

## Case
- 8 điểm chuyển DT5G THẬT (`tav2_bq.vnindex_5state_dt5g_live`, ngày COMMIT của transition) có |Δstate|>=2,
  lấy ngẫu nhiên (seed=20261022) từ danh sách các transition đó.
- 8 ngày ĐỐI CHỨNG ngẫu nhiên (seed=20261022), cách MỌI transition DT5G >= 40 phiên và cách nhau
  >= 40 phiên, trong [2014-06-01, 2026-09-15].
- Trộn thứ tự, nhãn C01-C16; agent KHÔNG biết case nào là transition.

## Dữ liệu agent được thấy (ẩn danh để giảm nhớ lịch sử — model biết lịch sử VN tới 2026-06)
- 400 phiên VNINDEX kết thúc tại ngày as-of D. Giá OHL C rebase = 100 ở phiên đầu cửa sổ (cùng một hệ
  số); Volume chia cho median của cửa sổ; thay ngày bằng chỉ số phiên 0..399 (D = 399). KHÔNG có ngày
  lịch, KHÔNG có DT5G, KHÔNG có thông tin sau D.

## Câu hỏi (cố định) — FORECAST khoá trước khi so DT5G
H20_DIR (UP/DOWN: dấu của Close[D+20] so Close[D]), H20_P_UP (0-1), LEVEL + HOLD/BREAK, INVALIDATION.
Cuối bài: CONTAMINATION = có nhận ra chuỗi là giai đoạn lịch sử cụ thể nào không (nêu nếu có; KHÔNG dùng
vào dự báo). Case nhận ra đúng giai đoạn ⇒ gắn cờ, báo kết quả có/không có case đó.

## Chấm điểm (cơ khí)
- Outcome: dấu Close[D+20]-Close[D] (VNINDEX gốc). Hit = H20_DIR đúng dấu. Brier = (P_UP - 1[UP])^2.
- Baseline: B0 = 50% (Brier 0,25) · B1 = động lượng (dấu lợi suất 20 phiên trước D) · B2 = DT5G-implied,
  CHỈ trên 8 case transition: dấu (state_mới − state_cũ) (tăng ⇒ UP, giảm ⇒ DOWN).
- Tiêu chí (n=16, thô):
  · SỐNG THÊM = Brier tổng < 0,25 VÀ hit tổng >= max(hit B1, hit B2 trên 8 case, hit B1 trên 16).
  · LOẠI SỚM = hit tổng <= 8/16 HOẶC Brier tổng >= 0,25.
  · Còn lại = INCONCLUSIVE ⇒ cần mẫu forward (đọc sống, ghi registry, chấm sau +20 phiên).
- Báo cáo riêng transition vs đối chứng, KHÔNG suy luận thống kê giữa hai nhóm (n=8).
- Không chọn lại case, không chạy lại, không đổi prompt sau khi thấy outcome. Một lượt chạy duy nhất
  (agent lỗi kỹ thuật được chạy lại CÙNG prompt, nêu rõ).
- READ-ONLY: không sửa production, không pin registry kết quả.
