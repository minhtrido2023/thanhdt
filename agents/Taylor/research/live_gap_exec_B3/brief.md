# Luồng B3 — đưa dòng "so với gửi tiết kiệm" vào báo cáo (user DUYỆT câu chữ + nhãn thuế 13/11/2026 09:1x ICT; chủ TK SpaceX = CÁ NHÂN)
Nền: nhánh feat/savings-row-20261112 @418667a32 (skeptic B/B2 CONFIRMED). Báo cáo SpaceX gửi nhà đầu tư ngoài ⇒ không nhắc ZaloPay/liên tài khoản; không nhắc lỗi đã sửa. KHÔNG gửi báo cáo thật, KHÔNG sửa cron.
Nhãn 1 đã duyệt (Wendy, TK cá nhân; lãi tiền gửi miễn TNCN theo Luật 109/2025 Đ4 k6; TWR từ tiền thật nên đã sau phí và thuế khấu trừ nguồn 0,1% bán/5% cổ tức — Taylor kiểm lại điều này trong code/log trước khi ghi, nếu sai dùng câu thay thế "chưa trừ thuế"):
"So với gửi tiết kiệm: mức lãi tham chiếu lấy theo lãi suất 12 tháng cao nhất trong Big-4 (kênh online) và chứng chỉ tiền gửi 12 tháng, tính lãi đơn theo số ngày thực tế/365. Đây là mốc THƯỢNG CẬN, chỉ để tham khảo, không phải lợi suất bảo đảm của bất kỳ kênh nào. Lãi tiền gửi cá nhân được miễn thuế TNCN (Luật Thuế TNCN 109/2025/QH15, Điều 4); lợi suất danh mục đã trừ phí giao dịch và thuế TNCN khấu trừ tại nguồn (0,1% giá bán, 5% cổ tức)."
Cảnh báo: "Kết quả trong quá khứ không bảo đảm kết quả trong tương lai. Thông tin này không phải cam kết hay dự báo về thu nhập hoặc lợi nhuận; đầu tư cổ phiếu có thể thua lỗ vốn, khác với tiền gửi."
Lưu ý: lãi chứng chỉ tiền gửi chưa xác minh miễn thuế ⇒ nhãn nói rõ cơ sở hurdle; nếu cần thì ghi "chưa xác minh miễn thuế đối với chứng chỉ tiền gửi".
Việc:
1. Thêm cột/dòng tiết kiệm + chênh (pp) + nhãn 1 + cảnh báo vào template weekly/monthly SpaceX (mike/reports/ mẫu, §31 bảng "Hiệu suất lũy kế"), số lấy từ nav_period_returns.py (savings), KHÔNG tự tính tay. Tên cột phải khớp quy ước cổng ('tiết kiệm'/'chênh').
2. Cổng: thêm selfcheck fail nếu có cột giống tiết kiệm mà không được nhận diện theo tên (skeptic B2).
3. Chạy report_delivery_gate end-to-end trên một báo cáo tuần THẬT (render tuần gần nhất, vd 06/11) có cột tiết kiệm — ghi PASS/FAIL thật.
4. Xử symlink mike→main trong worktree để selfcheck không test nhầm master.
Nhánh mới từ feat/savings-row-20261112; không merge. REPORT.md + bus finding live-gap-exec-B3-20261113; selfcheck dưới env -u TZ và TZ lạ.
