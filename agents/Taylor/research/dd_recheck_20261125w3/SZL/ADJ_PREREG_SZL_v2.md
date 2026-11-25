# SZL — phụ lục kiểm kê E17 v2 (khoá TRƯỚC lần chạy lại; đính chính theo skeptic `skeptic/r1.json` INCONCLUSIVE medium)
Kế thừa nguyên văn `ADJ_PREREG_SZL.md` (md5 c43c1873805cb9c7386a4e535964c2bd); CHỈ đổi/thêm các điểm dưới, mỗi điểm truy về một mục của `skeptic/r1_raw.md`. Không đổi gì vì kết quả tính (chưa chạy v2). MÙ GIÁ.

1. **Luật vốn lưu động t=0 (nêu rõ, FU#2):** E17 chỉ cộng/trừ khoản t=0 PHI VẬN HÀNH (không sinh ra từ chu kỳ kinh doanh lặp lại đã nằm trong N0): tồn kho BĐS dự án đứng yên (S1), ứng trước capex (S2), cổ tức dự thu (S3), và nợ gắn với chúng (S5). Vốn lưu động vận hành (phải thu/phải trả người bán, thuế, lương, VAT, chi phí trả trước, thuế hoãn lại) KHÔNG vào cả hai phía — skeptic r1 tự tính hai phía gần triệt tiêu (nợ ≈63,7 vs tài sản ≈58,4 ⇒ ròng ≈ −5,3 tỷ ≈ −0,4%, dưới ngưỡng); ghi ở độ nhạy C8.
2. **S1 hạ bậc A → B (FU#3):** số dư là số BCTC nhưng giá trị thu hồi (NRV, chi phí hoàn thành, thuế khi bán) không có bằng chứng bán hàng ⇒ B, 1 quan sát ⇒ p 0,50 [0,25; 0,75]; m giữ +116,58.
3. **S5 mới — Người mua trả trước 14,54 tỷ (NH 2,95 + DH 11,58, mặt BCĐKT tr.3 — đính chính C7 "chưa đọc" là SAI):** xuống, B (gắn với Tam An chưa kiểm; 1 quan sát) p 0,50 [0,25; 0,75]; m −14,54 [−2,95 (chỉ phần ngắn hạn); −14,54] tại t=0. C7 bỏ (gộp vào S5).
4. **Thuế truy thu ~14 tỷ:** giữ WARNING pháp lý (luật HANDOFF "Pháp lý chỉ WARNING"), thêm vào bảng điều kiện đổi số (≈ −1,06% nếu xác nhận chưa hạch toán).
5. **V8 (FU#6):** sửa ở REPORT: trần theo thanh khoản ADV250 0,461 tỷ/phiên (`rev5/calc/model_rev5_out.json`), tham gia ≤20% ⇒ ≈ 92 triệu/phiên.
S2, S3, S4 giữ nguyên.
