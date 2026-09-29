# Bước 1 KẾT QUẢ — cluster relative-strength momentum, PVN-family + Viettel-family

Job `Taylor_20260910_152624`. Thiết kế khoá TRƯỚC ở `PREREG_step1.md` (không sửa sau khi thấy
số). Code: `step1_backtest.py` (tự chứa, self-check thủ công khớp 100% — xem log).

## VERDICT: **NO-GO** — dừng, không tiến bước 2

## Số liệu (Newey-West lag=12, khớp overlap 200d lookback + 60d forward theo tháng)

| Cụm | OOS corr (2020-2026, n) | Sign-consistency theo năm | IS pre-2020 (tham khảo, n quá mỏng) |
|---|---|---|---|
| PVN-family | **−0,357*** (n=76, CONCLUDE, t_nw=−2,16) | 5/7 năm — nhưng dấu ÂM ổn định | +0,275 (n=12, THIN) |
| Viettel-family | +0,073 (n=75, CONCLUDE, t_nw=+0,64, không đáng kể) | 2/7 năm | −0,955 (n=3, TOO-THIN, không dùng) |

## Đọc kết quả — tại sao NO-GO dù PVN-family có t-stat |2,16|>2

Quy tắc quyết định khoá trước (§6 pre-reg) đòi: **CẢ HAI cụm** phải có OOS corr **DƯƠNG** và
sign-consistent đa số năm mới được GO — kiểm định giả thuyết A (continuation: RS cao → fwd return
cao). Kết quả thật:
- **PVN-family**: corr ÂM, có ý nghĩa thống kê (|t_nw|=2,16≥2) và sign-consistent (5/7 năm cùng
  dấu âm: 2021/22/23/25/26). Nhưng đây là **mean-reversion (giả thuyết B đã loại, không test)**,
  KHÔNG PHẢI continuation (giả thuyết A) — cụm đang mạnh (RS cao) có xu hướng SUY YẾU tiếp theo
  chứ không tiếp tục mạnh. Không thoả điều kiện GO (yêu cầu dương).
- **Viettel-family**: corr gần 0, không có ý nghĩa thống kê (t_nw=0,64), sign KHÔNG ổn định
  (chỉ 2/7 năm cùng dấu với full-OOS) — không có tín hiệu.
- Hai cụm không đồng thuận chiều hướng (PVN âm mạnh, Viettel≈0) → ngay cả khi nới lỏng thành "1/2
  cụm đạt" cũng KHÔNG đạt vì PVN đạt sai CHIỀU (âm, không phải dương theo giả thuyết đã chọn).

## Ý nghĩa — không phải "không có gì", mà là "đúng loại tín hiệu đã biết sẽ chết"

Kết quả PVN-family (RS cao → fwd return thấp, có ý nghĩa OOS) thực chất là bằng chứng **MEAN-
REVERSION cấp cụm**, không phải momentum. Đây KHÔNG PHẢI câu hỏi bước 1 được thiết kế để trả lời
(giả thuyết B — within/across-cluster rotation về phía trung bình — đã bị loại khỏi scope ở §2
pre-reg để tránh multiple-testing). Không tự động mở rộng sang test giả thuyết B ở đây (đó sẽ là
quét thêm sau khi thấy số — đúng loại lỗi coding_guidelines cảnh báo tránh); nếu muốn theo hướng
này phải qua một pre-registration MỚI, riêng, với rào chắn tương tự.

Về câu hỏi gốc của user (rotation nhóm mạnh/yếu theo giai đoạn thị trường = continuation-style):
**KHÔNG có bằng chứng ủng hộ** ở cả 2 cụm premise mạnh nhất đã xác nhận ở bước 0. Khớp đúng tiền
lệ: Rule 3 (20/20 sector sweep — mọi cách gộp nhóm chỉ là LENS, không phải BOOK sinh lời) + AMH
cùng ngày (momentum cá lẻ chết cấu trúc toàn bộ ô test hậu-2020). Cluster-level momentum **CÙNG
SỐ PHẬN** với momentum cá lẻ — không có bằng chứng cơ chế "dòng vốn/sở hữu chung" tạo ra continuation
edge độc lập với price momentum thuần.

## Giới hạn phải nêu (đã nói trước ở pre-reg, không phải biện minh sau)
- IS pre-2020 quá mỏng để đối chiếu (PVN n=12 THIN, Viettel n=3 TOO-THIN) — do 2/9 mã PVN
  (BSR/OIL) và toàn bộ Viettel-family (CTR muộn nhất 2018, VGI 2018-09, VTP 2018-11) chỉ có đủ dữ
  liệu 9-mã/3-mã đồng thời từ 2018. Không có cách khắc phục (không phải lỗi query, là thực tế
  niêm yết) — quyết định GO/NO-GO dựa hoàn toàn vào OOS (đúng thiết kế đã khoá).
- Cụm được xác định (bước 0) bằng tương quan full-sample 2018-2026 — bao gồm cả giai đoạn OOS. Đây
  không phải look-ahead trong bài test RS→fwd-return (đã walk-forward đúng nghĩa), nhưng không
  phải test "liệu 2020 có tìm ra đúng cụm này ex-ante" — không ảnh hưởng tới kết luận NO-GO vì
  ngay cả với ưu thế này (biết trước 2 cụm mạnh nhất) vẫn không tìm ra continuation edge.

## Không làm
Không wire gì vào production. Không mở rộng sang cụm khác. Không tự chuyển sang test giả thuyết B
mà chưa có pre-registration riêng + duyệt của user.

## Đề xuất
Đóng nghiên cứu correlation-cluster tại đây (bước 0+1). Nếu user muốn tiếp tục, hướng khả dĩ DUY
NHẤT còn mở là within-cluster mean-reversion (giả thuyết B) — cần pre-reg mới, và nên đặt kỳ vọng
thấp trước khi bắt đầu: đây lại là một dạng "gộp nhóm" khác, cùng nhóm rủi ro Rule 3 (LENS-not-
BOOK) đã thất bại 20/20 lần trước.
