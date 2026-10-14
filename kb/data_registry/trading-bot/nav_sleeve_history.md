---
kind: local-file
status: CANONICAL — đã merge, dựng thật 2026-10-14 (ZaloPay 06/07→13/10 = −0,790%, khớp nguyên mẫu), cron 00:50 ICT T3-T7 đã cài; sleeve_scope.json/sleeve_transfers.json tạo 2026-10-14 (user xác nhận Q6)
source: data/execution_logs/nav_sleeve_history_<account>.csv (+ data/sleeve_scope.json, data/sleeve_transfers.json)
group: trading-bot
role: chuỗi "phần bot quản lý" (chính sách quỹ mở điểm 2b) — NAV tài khoản trừ vị thế ngoài bot
writer: mike/bin/nav_sleeve.py --write (cron 00:50 ICT T3–T7, sau BQ sync — giá mã ngoài bot)
---

# nav_sleeve_history_<account>.csv

## Là gì
`NAV_b = NAV_a − Σ KL × giá của mã trong sleeve_scope − cổ tức phải thu (gộp) của các mã đó`. Tiền, Trứng
vàng, nợ thuộc trọn phần bot. Tỉ suất = `nav_unit_ledger.build_ledger` trên chuỗi NAV_b với dòng tiền
ở `sleeve_transfers.json` (cổ tức ròng về tiền, tiền bán/mua mã ngoài bot).

## Bẫy
- Phạm vi lấy từ `sleeve_scope.json`, KHÔNG từ `excluded_tickers` (danh sách cấm giao dịch; có PNJ vị thế 0).
- `positions` của DNSE có nhiều lô cùng mã ⇒ CỘNG (đọc ghi đè thiếu 24,4tr ở ZaloPay 11/08–28/09).
- Tối trước ngày GDKHQ, DNSE ghi sẵn KL mới (VHM 05/08, VPB 23/09) ⇒ KL × giá còn quyền sai hệ quy chiếu.
- Cổ tức DGC 80tr: phải thu ghi 11/09 (nav_history đã loại khỏi NAV ngày đó), nằm trong tiền 14/09–24/09,
  về tiền 25/09 (ròng 76tr).
- Số tham chiếu ZaloPay 06/07 → 13/10: (a) −6,199% · (b) −0,790% · mốc (b) 525.365.567.

## Consumer
`nav_period_returns.py --account ZaloPay --sleeve bot` (CHỈ đọc file đã dựng; freshness thật: mọi dòng
nav_history ≤ report_date phải có trong lịch sử b với `nav_a` bằng đúng `nav` hiện tại, scope md5 trùng) ⇒
không có số: rc=3 + JSON `status: unavailable` ⇒ dòng "Phần bot quản lý (không gồm DGC)" của bảng 3.2 ghi
`chưa có số (lý do)`, KHÔNG chặn gửi (số chính thức là chuỗi a).

## Khởi tạo trên cây thật (cần user/Mike — Q4–Q7 user chốt mặc định 2026-10-14)
1. `data/sleeve_scope.json`: `{"ZaloPay": [{"ticker": "DGC", "from": "2026-07-06", "to": null, "note": "legacy (Q4)"}]}`
2. `data/sleeve_transfers.json`: bản ghi cổ tức DGC (Q6: ròng 76.000.000 ngày tiền về 25/09, trước đóng cửa) với
   `decision: confirmed`, `confirmed_by: <user>` — mẫu ở `/tmp/step4_sbx/data/sleeve_transfers.json` (nhãn SANDBOX,
   PHẢI thay `confirmed_by` bằng người xác nhận thật). Khi DGC bán (Q7): `nav_sleeve.py --propose` ⇒ Mike trình ⇒
   user xác nhận ⇒ thêm bản ghi.
3. `nav_sleeve.py --account ZaloPay --write` ⇒ đối chiếu −0,790% (06/07 → 13/10) trước khi bật cron.
