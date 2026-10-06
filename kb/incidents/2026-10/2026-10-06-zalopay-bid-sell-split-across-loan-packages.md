# 2026-10-06 — `zalopay-bid-sell-split-across-loan-packages`: lệnh BÁN 27 BID bị DNSE từ chối `HTTP 400: Trade quantity not enough` vì vị thế nằm ở 2 gói vay (1258:20 · 1826:7), không gói nào đủ 27

**Trạng thái:** CHẨN ĐOÁN XONG, **CHƯA VÁ** — root cause nằm trong `trading_bot/brokers.py`
(logic đặt lệnh = ranh giới CỨNG của Winston). Escalate bus question
`ops-autofix-unresolved: ops-health-ZaloPay` (job `Winston_20261006_054508`).

## Triệu chứng
`data/execution_logs/exec_ZaloPay_2026-10-06_journal.csv`: 5 `PLACE_FAIL` liên tiếp
`PARKMERGE-SELL-BID` (sell 27 @34.700, PARK_TRIM) 09:20:26→09:21:06, note
`HTTP 400: Trade quantity not enough`, rồi `PLACE_FAIL_STOPPED` 09:21:06 (cơ chế chặn per-process
hoạt động đúng — chỉ 5 lượt, không bão retry như 09-29). `child_oid` rỗng ⇒ broker chưa tạo lệnh,
không orphan/dup.

## Root cause (đo, không đoán)
`dnse_raw_2026-10-06.jsonl` (lọc `accountNo=0001743768`), bản ghi `sell_loan_package_resolve`
mỗi lần đặt: `{"symbol":"BID","qty":27,"resolved":1258,"by_package":{"1826":7,"1258":20},
"any_pkg_covers_qty":false,"rule":"sellable-lớn-nhất (KHÔNG gói nào đủ qty — qty KHÔNG bị clamp…)"}`.
Positions 04:55: deal 2697547 gói 1258 `tradeQuantity=20`, deal 2766555 gói 1826 `tradeQuantity=7`.
DNSE khớp lệnh bán vào deal theo gói ⇒ gói 1258 chỉ có 20 < 27 ⇒ 400.

Đây chính là giới hạn ĐÃ BIẾT ghi trong docstring `_resolve_sell_loan_package_id` (vá 09-29):
hàm chỉ chọn MỘT gói, không clamp/tách `qty`; "clamp qty là ĐỔI HÀNH VI đặt lệnh ⇒ cần bằng
chứng hành vi DNSE trước". 10-06 là ca thật đầu tiên chạm nhánh đó (lệnh THOÁT HẾT mà lô lẻ còn
lại rải 2 gói).

## Ảnh hưởng
~934.200đ (27 BID) không huy động được. Cờ chặn tự xoá khi bot restart 13:00 ⇒ dự kiến thêm ≤5
`PLACE_FAIL` + 1 lượt ATC cùng lỗi. Không ảnh hưởng lệnh khác.

## Đề xuất cho người sở hữu execution (Mafee/Taylor/user quyết)
Lệnh BÁN khi `any_pkg_covers_qty=false`: tách thành N lệnh con theo từng gói (ở đây 20@1258 +
7@1826), mỗi lệnh `qty ≤ sellable` của gói đó. Nằm ở `_place_slices`/`place_order`.

**Lesson:** lệnh "thoát hết" một mã có deal mua ở nhiều ngày khác gói sẽ luôn chạm ca này; vá
09-29 khép bất đối xứng gói nhưng cố ý chưa xử lý ca đa gói.
