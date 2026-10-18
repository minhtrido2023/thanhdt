---
date: 2026-10-16
status: fixed
severity: medium
area: report-data-provenance
found_by: weekly-ops-audit (Mike_20261016_205556)
---

# EOD daily report 16/10 mất toàn bộ phần giao dịch — lệnh ATC khớp có `price=None`

## Triệu chứng
`logs/eod_trading_report.log` 16/10 (cả SpaceX lẫn ZaloPay):
`TypeError: unsupported operand type(s) for *: 'int' and 'NoneType'` tại heredoc `PYEOF` dòng 220
(`avg_price = sum(c['filled'] * c['price'] ...)`). Biến `REPORT` rỗng nhưng script vẫn chạy tiếp ⇒
báo cáo ngày 16/10 gửi Discord + email **thiếu toàn bộ khối lệnh/khớp** (SpaceX: 7 lệnh bán,
347,6M; ZaloPay: có NCT/SIP), chỉ còn khối NAV/DT5G. `report_delivery_gate` vẫn báo COMPLETE —
cổng không kiểm sự hiện diện của khối giao dịch.

## Root cause
Lệnh `SELL-*-AUTOEXIT-CAPIT` (hết hạn T+60 rổ CAPIT) đặt kiểu ATC ⇒ child trong
`exec_<acct>_2026-10-16_state.json` có `price: None` (bot không đặt giá) nhưng `filled > 0`.
Lần đầu tiên có fill ATC trong state (quét toàn bộ `exec_*_2026-*_state.json`: chỉ 16/10, 4 child).

## Fix
`bin/eod_trading_report.sh`: child không có giá ⇒ lấy `averagePrice` DNSE theo order id thật từ
`dnse_raw` (`latest_by_oid`, nay khởi tạo trước nhánh `if` để luôn tồn tại); không có nguồn giá
nào ⇒ bỏ child đó khỏi bình quân thay vì crash.

## Verify (chạy thật, không chỉ đọc)
Chạy heredoc đã vá trên input thật 16/10: rc=0 cả 2 account; SpaceX "Tổng giá trị giao dịch:
347.6M / kế hoạch 345.9M" — khớp ĐÚNG số Leg 3 statement DNSE độc lập (347,6M).

## Còn mở
- Báo cáo ngày 16/10 đã gửi thiếu khối giao dịch — gửi lại hay không là quyết định của user.
- `report_delivery_gate` không phát hiện báo cáo mất khối giao dịch khi có fill thật (lỗ hổng phủ).
