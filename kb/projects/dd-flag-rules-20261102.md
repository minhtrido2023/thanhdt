# 4 quy tắc user chốt 02/11/2026 23:01 ICT (`decided_by: user`)
Nguyên văn: "Khi lên plan, mã nào có cờ thì bị loại khỏi candidate của tất cả các book hiện có. DRI theo DD report giá thị trường cao hơn fair price khá nhiều nên quyết định bán hết số còn lại. TV1 hiện tại chưa có biên an toàn nên cũng quyết định không giữ. Mã nào có DD report mà giá rơi dưới tâm 15% có thể đưa vào xem xét dưới dạng candidate của discretionary sleeve."

## Đã làm đêm 02/11
- Plan T+1 03/11 (cả 2 TK) sửa tay: bỏ BUY TCH (cờ FLOOR_FAIL); thêm SELL DRI + SELL TV1 hết KL broker (book DISCRETIONARY_SPECIAL, play DISCRETIONARY_EXIT, ref = broker marketPrice 22:00). Bản gốc `data/trade_plans/plan_*_2026-11-03.json.bak_20261102_2315`. send_plan_report --second-chance đã gửi lại bản cập nhật. approved_by vẫn None — chờ user duyệt.
- Diễn giải "cờ" (Mike chọn, chờ user xác nhận nếu muốn rộng hơn): 🔴 RED_FLAG_CODES + ⚠ quality_flag≠QUALITY_OK trong `trading_bot/due_diligence.py`. KHÔNG gồm: ⚠ thanh khoản mỏng, quý lỗ, anomaly tier, insider-sell 90 ngày, `forensic watch` (forensic exclude đã bị loại sẵn).

## Việc code giao Taylor (xem bus/job): cổng cơ học tầng lệnh (mọi book mua trừ DISCRETIONARY*) + ứng viên sleeve từ sổ DD.

## Nguyên văn các khối dời khỏi kb/current_ops.md (gate kích thước)
## DRI — user DUYỆT GIẢM 50% CHỦ ĐỘNG (`decided_by: user`, 27/10 12:14 ICT) — DollarBill đưa vào PLAN T+1 28/10, KHÔNG hỏi lại
- SELL DRI: **SpaceX 1.250cp (→1.250), ZaloPay 650cp (→650)**; bán discretionary của user (không phải auto-exit); vào plan nháp, user duyệt plan như thường. User đã bán tay trước ⇒ dùng KL broker thật. Chi tiết: `kb/projects/dri-triggers-20261027.md`.

## LAG — SCL THOÁI HẾT + CẢNH BÁO TĂNG VỐN (`decided_by: user`, 29/10 14:2x ICT) — AGENT KHÔNG HỎI LẠI
- **SCL: THOÁI toàn bộ cả 2 TK** (KL broker thật) qua **DollarBill đưa SELL vào plan T+1 30/10** (như DRI; không chờ T+25/ex-date). Căn cứ: `kb/projects/scl-dd-20261029.md`. Đã bán tay 29/10 @29.600: SpaceX 800 + ZaloPay 500; còn SpaceX 300 + ZaloPay 200 (lô 28/10: chiều 30/10).
- **LUẬT MỚI**: BẤT KỲ tăng vốn nào (quyền mua, riêng lẻ/công chúng, ESOP, TPCĐ; cổ tức/thưởng CP = INFO) trong chu kỳ đầu tư của mã ⇒ **WARNING user** (không tự bán). Taylor dựng + arch-review; merge cần user. Luật 21/10 (mã LAG có quyền mua: KHÔNG bán trước ex-date, user tự mua đủ; lô quyền kế thừa entry gốc `771daf4ea`) GIỮ cho mã LAG KHÁC — SCL là ngoại lệ. Bản 21/10 của SCL: `kb/projects/scl-dd-research-20261021.md`.

