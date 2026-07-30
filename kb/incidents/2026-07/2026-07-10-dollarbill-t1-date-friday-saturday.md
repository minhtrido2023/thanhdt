---
kind: incident
date: 2026-07-10
topic: dollarbill-t1-date-friday-saturday
title: >-
  2026-07-10 (chiều) — DollarBill tự tính sai ngày T+1: thứ Sáu → "ngày mai" = thứ Bảy (không phải ngày giao dịch), đáng lẽ phải là thứ Hai — 2 lần dispatch cùng ngày đều sai
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-10 (chiều) — DollarBill tự tính sai ngày T+1: thứ Sáu → "ngày mai" = thứ Bảy (không phải ngày giao dịch), đáng lẽ phải là thứ Hai — 2 lần dispatch cùng ngày đều sai

**Phát hiện (retro cron 22:00, đối chiếu artifact thật — không tin lời câu hỏi bus):**
2 sự kiện `question` (`plan-t1-not-ready-SpaceX`/`-ZaloPay`, 2026-07-10T14:00 UTC = 21:00
ICT, do `send_plan_report.sh` tự phát hiện) báo `plan_date` trong file mới nhất là
`2026-07-11` nhưng kỳ vọng `2026-07-13`. Verify trực tiếp bằng cách đọc 2 file JSON thật
(`plan_SpaceX_2026-07-11.json`, `plan_ZaloPay_2026-07-11.json`, ghi lúc 19:03-19:04 ICT):
`plan_date` đúng là `"2026-07-11"` — **thứ Bảy, không phải ngày giao dịch**. Hôm nay
2026-07-10 là thứ Sáu → T+1 đúng phải là thứ Hai 2026-07-13 (`next_trading_day()` xác nhận
đúng giá trị này khi chạy tay). Log dispatch của chính DollarBill còn tự mâu thuẫn thêm:
`dispatch_DollarBill_20260710_120059.log` ghi "Plan ngày: 2026-07-11 (**thứ Sáu**)" —
gán sai luôn cả tên thứ cho ngày nó tự chọn, xác nhận đây là lỗi tính lịch thuần của LLM,
không phải lỗi đọc dữ liệu.

**Root cause:** `bin/bq_freshness_check.sh` dispatch DollarBill với chỉ dẫn
`Ghi plan vào data/plan_${ACCT}_<ngày_mai>.json` — để NGUYÊN cho LLM tự suy ra "ngày mai"
là gì, thay vì truyền thẳng giá trị đã tính sẵn bằng `next_trading_day()` (hàm đã tồn tại
sẵn, đúng, đang được `send_plan_report.sh` dùng để verify). Bug này **luôn tiềm ẩn từ
go-live** (prompt y hệt từ commit đầu tiên) nhưng chỉ lộ ra hôm nay — kiểm tra lại
`plan_SpaceX_2026-07-03.json` (dispatch thứ Sáu 07-03 trước đó) cho thấy LẦN ĐÓ DollarBill
tính ĐÚNG (plan cho thứ Hai 07-06, bỏ qua cuối tuần) — nghĩa là đây là lỗi suy luận
KHÔNG ỔN ĐỊNH của LLM (đúng 1 lần, sai 1 lần, cùng 1 dạng bài, cùng prompt), không phải
lỗi logic tất định — càng củng cố lý do KHÔNG được để LLM tự làm phép tính có thể tính
bằng code. Bị dispatch lặp lại 2 lần trong ngày (17:31 ICT dưới cron cũ + 19:04 ICT dưới
cron mới sau khi giờ cron được cập nhật giữa chừng — xem entry cron-order phía trên) —
CẢ HAI LẦN đều tính sai giống nhau.

**Tác động thật:** cả 2 account (SpaceX, ZaloPay) KHÔNG có plan hợp lệ cho phiên thứ Hai
2026-07-13 tính đến hết ngày thứ Sáu — vì `bq_freshness_check.sh` (nguồn DUY NHẤT sinh
plan T+1 tự động) không chạy cuối tuần (cron `1-5`), nếu không tự phát hiện+sửa thì
preflight sáng thứ Hai sẽ RED vì thiếu file đúng ngày.

**Fix (commit `e3001fa`, cùng phiên retro):** `bq_freshness_check.sh` giờ tính
`NEXT_TRADING_DAY` bằng chính `next_trading_day()` NGAY TRONG BASH trước khi dispatch,
truyền thẳng giá trị literal vào prompt (thay `<ngày_mai>` mơ hồ), kèm câu cấm tường minh
"TUYỆT ĐỐI KHÔNG tự suy ra ngày mai bằng cách cộng 1 vào hôm nay" + ví dụ sự cố thật. Thêm
fail-safe: `NEXT_TRADING_DAY` rỗng (python lỗi) → dừng hẳn (exit 1), không dispatch với
ngày rỗng. Verify: `bash -n` PASS; chạy tay `next_trading_day()` cho hôm nay → đúng
`2026-07-13`. **Đã re-dispatch DollarBill ngay trong phiên retro này** (job
`DollarBill_20260710_150834` SpaceX, `DollarBill_20260710_150924` ZaloPay) với ngày đã sửa
để có plan đúng cho thứ Hai — kết quả tự báo qua bus/Telegram khi xong, retro này không
chờ đồng bộ. File cũ sai ngày (`plan_SpaceX/ZaloPay_2026-07-11.json`) **CỐ Ý giữ nguyên,
KHÔNG rename/xoá** — thử rename bị chính permission classifier của harness CHẶN (lý do:
chạm "trade plan" trong danh sách ranh giới cứng "không bao giờ tự sửa" của user) — đây là
tín hiệu ĐÚNG, không phải lỗi, ghi lại làm bằng chứng ranh giới hoạt động như thiết kế.
**Cần user xác nhận/dọn 2 file `_2026-07-11.json` cũ khi thuận tiện** (vô hại nếu để
nguyên — không ngày thật nào khớp tên file đó để bot đọc nhầm, nhưng nên dọn cho sạch).

**Bài học:** cùng 1 category lỗi với Pattern B tối qua ("đọc/tính sai một sự kiện thời
gian") nhưng khác giống — không phải đọc nhầm NGUỒN dữ liệu (BQ vs DNSE), mà là để MỘT
LLM tự làm phép TOÁN LỊCH mà code đã có sẵn hàm đúng, tất định, đang dùng ở nơi khác trong
cùng codebase. Nguyên tắc chung: bất cứ giá trị nào có thể tính bằng code tất định (ngày,
số lượng, tỷ lệ) thì PHẢI tính bằng code và truyền literal vào prompt — không giao cho LLM
suy luận, kể cả khi LLM "thường tính đúng" (bằng chứng hôm nay: đúng 07-03, sai 07-10,
cùng 1 dạng bài).
