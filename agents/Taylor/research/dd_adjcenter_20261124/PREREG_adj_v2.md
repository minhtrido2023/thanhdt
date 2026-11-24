# PREREG_adj v2 — phụ lục khoá TRƯỚC khi fan-out (Mike, 24/11/2026 sau pilot FPT)
Kế thừa nguyên văn PREREG_adj.md (md5 ef5157cb…); CHỈ thêm/đổi các điểm dưới (từ mục "Rút kinh nghiệm pilot" của Taylor, job Taylor_20261124_104632):
1. **Bậc C+** (mới): hạng mục có DẤU chắc chắn + cận bảo thủ tính được từ dữ liệu trong tay (vd tồn quỹ ÷ LNST năm trước; không cần đoán tỷ lệ tương lai) ⇒ VÀO tâm ở cận bảo thủ đó, p theo thang bậc B, nêu rõ "C+ — cận bảo thủ" + cơ sở. Bậc C thuần (không dấu/không cận) vẫn chỉ độ nhạy.
2. **Dải theo cực trị (p, m)**: khi m là "ước lượng" (số skeptic/probe, không phải số trực tiếp BCTC) phải có khoảng m [thấp; cao] và dải tâm lấy cực trị theo cả p lẫn m.
3. **Quan sát độc lập** (thang p): 1 quan sát = 1 KỲ BÁO CÁO khác nhau; LNST và LNTT cùng kỳ = 1; "quan sát ngược" phải có SỐ (định tính 5F không tính).
4. **Giữ quy tắc pilot**: r 13,5% vs dải Ke (E15) và chặn RONIC (V2/V5) là THAM SỐ LUẬT, KHÔNG vào Σ ở cả hai chiều; báo ở mục độ nhạy [LUẬT]. (Đây là quyết định thiết kế — trình user ở topic; nếu user đổi thì chạy lại, không chạy lại tay.)
5. **|Σ p×m| > 5%** ⇒ chạy lại mô hình với tổ hợp (không cộng tuyến tính các probe).
6. **Cổ tức/quyền**: mỗi mã in HAI dòng (có quyền / sau GDKHQ) nếu còn quyền chưa chốt; ghi rõ mã nào đã GDKHQ.
7. **adj.json schema bắt buộc** (validator sổ `_center_adj_errs` sẽ đọc): `ticker`, `dd_date`, `rev` (của entry sổ mới nhất mà tâm gốc lấy từ), `center_base` (= `center` entry), `center_adj`, `range_low`, `range_high` (số dương, low ≤ adj ≤ high), + các trường cũ (items, sensitivity_only, trigger_table, prereg_md5).
8. Calc gốc bị TRIM: khôi phục theo ghi chú SUMMARY.md từng mã (`git archive 14ad1c925^ …` vào /tmp), KHÔNG ghi đè repo.
