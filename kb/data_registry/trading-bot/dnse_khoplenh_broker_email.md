---
kind: local-file
status: CANONICAL
source: "email Gmail 'DNSE_Báo cáo giao dịch khớp lệnh tài khoản 064C988901 ngày DD/MM/YYYY' + data/execution_logs/dnse_khoplenh_broker_confirm_<DD-MM-YYYY>.csv"
group: trading-bot
role: broker statement chính thức — KHỚP LỆNH THẬT (khác lệnh ĐẶT), nguồn đối soát độc lập với dnse_raw_*.jsonl
writer: fetch_dnse_khoplenh_email.py (WorkingClaude root), chạy tay hoặc dispatch — CHƯA có cron
---

# DNSE email "Báo cáo giao dịch khớp lệnh" (thêm 2026-08-11, user cung cấp)

**Status: CANONICAL cho fill THẬT** — độc lập hoàn toàn với `dnse_raw_*.jsonl` (khác API call,
khác thời điểm, khác đường dữ liệu: đây là file DNSE tự phát hành cuối phiên, không phải response
của app đọc trực tiếp).

## Là gì
DNSE tự động gửi 1 email/phiên (~16:30 ICT, cả 2 tài khoản GỘP CHUNG 1 file — customer number
`064C988901` bao cả 2 tiểu khoản `0001743768`=ZaloPay + `0002023347`=SpaceX) với file đính kèm
`.xlsx` liệt kê **từng dòng khớp lệnh thật** (không phải lệnh đặt): mã, tiểu khoản, khối lượng,
giá khớp, giá trị khớp, tỷ lệ phí, phí trả sở (exchange), phí DNSE (broker), thuế.

## Ai ghi / cadence
DNSE tự gửi email cuối mỗi phiên giao dịch thật (T2-T6). `fetch_dnse_khoplenh_email.py` (root
WorkingClaude, dùng chung Gmail OAuth readonly có sẵn cho auto-OTP — không cần credential mới) tải
+ parse thành CSV sạch tại `data/execution_logs/dnse_khoplenh_broker_confirm_<DD-MM-YYYY>.csv`.
**Chưa wire vào cron/pipeline báo cáo tự động** — hiện chạy tay khi cần đối soát.

## Vì sao quan trọng — phát hiện thật 2026-08-11
Dùng nguồn này phát hiện: DRI (SpaceX 3.700cp + ZaloPay 1.900cp) khớp ĐỦ đúng plan, nhưng **TV1
khớp gần như KHÔNG** (SpaceX chỉ 100/2.000cp đặt thêm, ZaloPay 0/1.300cp) — dù cả 2 lệnh đều đã
"đặt đúng" theo plan đã duyệt. Nếu chỉ nhìn `orders[]` trong plan JSON (số ĐẶT) sẽ kết luận sai là
"đã đạt 5% NAV" — phải đối chiếu KHỚP THẬT (email này, hoặc `positions` snapshot mới nhất trong
`dnse_raw_*.jsonl`) mới thấy đúng. Bài học trực tiếp cho §6: "lệnh đã đặt" ≠ "lệnh đã khớp", đặc
biệt với mã thanh khoản mỏng (TV1 ADV ~0,634 tỷ/ngày).

## Bẫy
- File GỘP CHUNG 2 tiểu khoản trong 1 email — luôn `groupby(tieu_khoan, ma)` trước khi dùng
  (giống nguyên tắc §12 cho `dnse_raw_*.jsonl`), đừng cộng gộp nhầm 2 account.
- Chỉ có DÒNG KHỚP — mã/lệnh không khớp gì trong phiên (0 fill) sẽ KHÔNG xuất hiện trong email này
  (không phải "không có dữ liệu" = "không có lệnh", mà đúng là "không khớp gì"). Muốn biết lệnh đã
  đặt nhưng chưa khớp, phải đối chiếu ngược với `plan_<account>_<date>.json` hoặc `place_order`
  records trong `dnse_raw_*.jsonl`.
- Email chỉ có phiên đã ĐÓNG (~16:30 ICT) — không dùng để tra fill giữa phiên (dùng `dnse_raw` live
  cho việc đó, theo bright-line rule §6).
- Layout XLSX có 2 dòng header (`STT|Ngày GD|...` rồi `Khối lượng|Giá khớp|...`) và dòng
  `Tổng cộng` cuối bảng — script tìm động bằng nội dung ô, không hardcode số dòng.
