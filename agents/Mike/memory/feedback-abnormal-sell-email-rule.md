---
name: feedback-abnormal-sell-email-rule
description: Default hold khi không duyệt plan; bán bất thường phải có due diligence + email ngay
metadata:
  type: feedback
---

Nếu user không hoặc quên duyệt plan → **mặc định HOLD** (không giao dịch). Preflight 08:45 tự chặn bot nếu plan chưa approved.

Nếu có **case bán bất thường** → phải:
1. Làm due diligence trước khi đặt lệnh
2. Gửi email báo cáo ngay sau khi bán (dùng `send_report_email.py`), KHÔNG đợi EOD report

**Why:** user muốn kiểm soát mọi hành động bán ngoài quy trình thường. Bán bình thường (PARK trim, LAG exit theo plan đã duyệt) không cần email riêng — chỉ EOD report là đủ.

**Định nghĩa "bán bất thường":**
- CAPIT exit (regime change kích hoạt)
- LAG exit sớm ngoài plan
- Stop-loss / emergency sell bất kỳ loại
- Bất kỳ lệnh bán nào KHÔNG có trong plan đã được user duyệt

**How to apply:** khi DollarBill lập plan có lệnh bán bất thường, hoặc bot trigger bán emergency — Mike phải dispatch risk-auditor review + gửi email trước EOD report thường.

Chốt: 2026-08-26 (user directive).
