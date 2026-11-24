# PRE-REGISTRATION — CK holding VN v3 (job Taylor_20261124_041821)

Ghi lúc **2026-11-24 11:22 ICT**, TRƯỚC khi chạy calc v3 (chưa có bất kỳ số v3 nào; số v2 đã biết — xem REPORT v2).
File này khoá md5 trong LOCK_md5.txt và được chép nguyên văn vào đầu REPORT_CK_HOLDING_v3.md. Không sửa sau khi chạy.

## A. Đặc tả chính (thay v2)
- Mẫu: TOÀN BỘ 116 holding qualify (≥1 con niêm yết lợi ích ≥20%); KHÔNG tiền lọc 1 ngày. Lọc độ phủ làm PIT
  theo từng tháng D trong calc, độ phủ tính bằng VCSH thuộc cổ đông MẸ (VCI CĐKT; thiếu VCI ⇒ fallback BQ có cờ).
- Giữ holding: độ phủ ≥60% ở ≥3 tháng (như v2). Giá con STALE ⇒ về sổ (như v2).
- Số CP: cầu nối ISS — với mỗi sự kiện thưởng / cổ tức CP (corporate_action ISS, method Bonus|DIV, tỷ lệ r) ex E:
  với mọi D ≥ E (tới trước sự kiện CP kế tiếp khác loại), số CP kỳ vọng = S_pre × Π(1+r) với S_pre = số CP dùng ở
  tháng cuối trước E. Lệch > 2% ⇒ dùng số kỳ vọng, gắn cờ ISS_FIX, liệt kê toàn bộ. (PIT: tỷ lệ thưởng công bố trước ex.)
- Con mỏng (thin) = ADV60 < 0,1 tỷ VND HOẶC số phiên khớp trong 60 phiên < 20. Đặc tả chính: giữ giá thị trường
  (như v2); độ nhạy: thin → sổ, thin trọng 50% (½ giá + ½ sổ).
- T_eff / tự tương quan: chỉ trên tháng có n ≥ 11.

## B. Ứng viên dải (khai trước)
(a) **Bất định trung tâm qua đặc tả**: lưới PIT = độ phủ {50,60,70%} × VIC {có, không} × con mỏng {giá, sổ}
    (12 đặc tả). Dải = [min … đặc tả chính … max] của trung vị holding. Đo: "trung tâm" nhạy thế nào với lựa chọn
    hợp lý. Bản tỷ lệ cố định (look-ahead) báo riêng, KHÔNG vào lưới.
(b) **IQR sau loại cấu trúc** — quy tắc chung, không theo kết quả:
    R1 free-float: tổng cổ đông lớn (KBS, mỗi cổ đông ≥5%) của MẸ ≥ 85% ⇒ loại (giá mẹ không phản ánh thị trường).
    R2 phần theo sổ âm: trung vị tháng của (E_mẹ − Σ s_i E_i) < 0 ⇒ loại (sổ âm của mảng không niêm yết lỗ
       không phải proxy giá trị hợp lý; SOTP mất nghĩa). Áp như nhau cho mọi holding.
    Dải = [q25 … trung vị … q75] cắt ngang holding còn lại. Đo: PHÂN TÁN liên-holding (một holding bất kỳ).
(c) **Có điều kiện giống HHS**: (c1) kiểm soát & cổ tức tiền con→mẹ < 1%/năm; (c2) tercile thấp nhất cổ tức
    con→mẹ; (c3) kiểm soát. Dải = [q25 … trung vị … q75]. N < 8 ⇒ ghi "không đủ", không dùng.
(d) **Theo thời gian**: trung vị cắt ngang mỗi tháng PIT có n ≥ 11 (đặc tả chính). Dải = [min … trung vị các tháng
    … max], kèm IQR của đường tháng. Đo: trung tâm trôi theo thời gian trong 1 chế độ.
Mỗi ứng viên báo: thấp/giữa/cao, độ rộng (pp), N, LOO-holding (min…max trung vị), ổn định theo tháng.

## C. Tiêu chí chọn dải tham chiếu cho HHS (khai trước, theo MỤC ĐÍCH không theo độ rộng)
1. Câu hỏi của HHS là "CK base hợp lý cho một holding kiểu HHS" ⇒ đại lượng cần là TRUNG TÂM, không phải phân tán.
   Ứng viên đo trung tâm: (a), (d), và (c) nếu N ≥ 8.
2. Dải tham chiếu = **bao (hull) của (a) và (d)** — vì cả bất định đặc tả lẫn trôi thời gian đều là bất định về
   trung tâm; chọn một trong hai sẽ giấu phần kia. Nếu (c) đạt N ≥ 8 thì dùng (c) thay cho (a) và ghi rõ.
3. Điều kiện "có nghĩa": độ rộng ≤ 20pp VÀ LOO-holding của trung vị chính nằm trong dải. Không đạt ⇒ nói thẳng
   "không có dải vừa hẹp vừa trung thực", báo dải trung thực rộng.
4. (b) LUÔN báo kèm như dải phân tán "một holding bất kỳ" — không dùng làm tham chiếu trung tâm.
5. Báo 0% nằm đâu trong dải được chọn (dưới / trong / trên; phân vị nếu trong).
