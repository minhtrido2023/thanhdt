# Mục B — DNSE có gửi email xác nhận nạp/rút không? (đo 2026-10-12, chỉ đọc)

Cách đo: OAuth `gmail.readonly` dùng chung với auto-OTP (cùng đường `fetch_dnse_khoplenh_email.py`), script
`B_dnse_email_probe.py`, đầu ra `B_dnse_email_probe.txt`. Chỉ đọc tiêu đề; riêng báo cáo tháng có mở PDF của
HAI tiểu khoản fleet quản lý (0002023347, 0001743768) trong /tmp rồi xoá — KHÔNG mở 0002023348.

**Kết luận: KHÔNG.** 251 email từ `dnse.com.vn` kể từ 2026-06-01, không thư nào là xác nhận nạp/rút:
| Số thư | Mẫu tiêu đề |
|---|---|
| 134 | Xác thực với Email OTP |
| 45 | DNSE_Báo cáo giao dịch khớp lệnh tài khoản <số>C<số> ngày <ngày> |
| 44 | DNSE thông báo phát hành hóa đơn điện tử |
| 14 | DNSE_Thông báo Sự kiện quyền Họp đại hội đồng cổ đông |
| 5 | DNSE kính gửi Quý khách Báo cáo tài khoản Chứng khoán tháng MM/YYYY (ngày 1 hằng tháng) |
| 9 | thông báo lẻ (nghỉ lễ, nâng cấp hệ thống, mở tiểu khoản, quảng bá) |
Truy vấn "nạp tiền"/"rút tiền"/"nộp tiền"/"chuyển tiền"/"biến động số dư" trên toàn hộp thư chỉ ra thư của
ngân hàng và công ty chứng khoán KHÁC (MB, VPBank, PHS, KBSV…), không có thư DNSE.

**Nguồn gần nhất có giá trị: báo cáo tháng (PDF mỗi tiểu khoản), nhưng không ổn định.**
| Tháng | Có mục "V. Sao kê chứng khoán - tiền" (từng dòng tiền) |
|---|---|
| 07/2026 | CÓ (cả 2 tiểu khoản) |
| 08/2026 | KHÔNG |
| 09/2026 | KHÔNG |
Sao kê tháng 07 liệt kê từng dòng: mua/bán, phí, thuế, "Giải ngân margin", "Trả nợ DNSE", "UTTB/Hoàn trả
ƯTTB" (ZaloPay, 15 lần), "Lãi tài khoản không ngủ", "Chuyen tien TT Cho vay"/"Hoàn trả TT Cho vay" (khoản
302.108.211 mà nav_history ghi là off-book 07-17 → 07-21), "Cổ tức bằng tiền sau thuế TNCN", "Phí lưu ký".
**Tháng 07 không có dòng nộp/rút tiền nào ở cả hai tiểu khoản** — xác nhận độc lập kết quả đẳng thức tiền.

Không wire nguồn nào ở bước 2: không có nguồn theo ngày; nguồn theo tháng trễ tới 31 ngày và 2/3 tháng gần
nhất không có mục tiền. Email ngân hàng (MB "Thong bao giao dich thanh cong") là thư cá nhân của chủ tài
khoản, không thuộc phạm vi.
