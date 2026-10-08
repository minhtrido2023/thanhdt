# `*_screen.py` sort-direction bug ("8L top-25" = 25 mã xấu nhất) — vá 2026-09-27
> Chuyển nguyên văn từ `kb/canonical.md` (trim context_pack 2026-10-08). Mục CÒN PHẢI LÀM vẫn ở file gốc.

## Chuyển từ kb/canonical.md L140-158 (trim 2026-10-08, Wags_20261008_133659) — Lỗi + mức độ sai + hệ quả nghiên cứu

**Lỗi**: `sort_values([rating, tv], ascending=False).head(25)` rồi gọi kết quả là "8L top-25".
`fa_ratings_8l.rating` là thang **1-5 kiểu xếp hạng tín nhiệm — 1 = AAA = TỐT NHẤT** (cổng
production là `rating<=3`), nên `ascending=False` lấy đúng nhóm rating **xấu nhất**. Lặp ở
**16/20 file**; sửa = `ascending=[True, False]` (tie-break thanh khoản giảm dần vốn đã ĐÚNG).
Merge `ec9750f2` (user duyệt 19:25 ICT 2026-09-27); selfcheck `screen_sort_direction_selfcheck.py`
bằng **AST** — 20 file · 107 lệnh sort · 0 vi phạm · 0 mơ hồ, giống nhau trên 4 môi trường TZ,
**7/7 mutation bị giết**, và chạy trên bản CHƯA sửa ra đúng 16 vi phạm ⇒ bắt bug thật, không tautology.

**Mức độ sai**: 146 kỳ rebal 2014-08→2026-09 — rating trung bình rổ **4,504 → 1,252**;
**145/146 kỳ hai rổ RỜI NHAU HOÀN TOÀN** (overlap 0,01/25); số kỳ rổ **không có mã nào `rating<=3`**:
**145/146 → 0**. Ví dụ 2026-09-25: bản cũ chọn rổ `rating {4:15, 5:10}` — **có cả NVL và HAG là
BANNED vĩnh viễn**; bản sửa chọn `rating {1:8, 2:17}` (ACB CTG FPT GAS MBB VCB VNM…).

🔴 **HỆ QUẢ NGHIÊN CỨU — đừng trích số cũ nữa**: **7/9 screen từng được báo là TRỰC GIAO với
8L top-25 (0-5%) thật ra TRÙNG 21-83%** (bank_compounder 4,9→64,1% · tech G_VN 0,0→83,3% ·
pharma 0,0→69,0% · aviation INFRA 0,0→53,4% · logistics PORT 0,0→37,1% · compounder 4,0→25,8% ·
retail_compounder 0,0→21,1%). ⇒ **kết luận "sleeve này bổ sung alpha mới, không lặp 8L" KHÔNG
còn suy được từ những con số cũ.** Muốn kết luận lại thì phải đo lại, không phải đọc lại.

