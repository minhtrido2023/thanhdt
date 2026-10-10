---
kind: local-file
status: NOT-YET-SEALED (cơ chế có từ 2026-10-11; KHÔNG chốt sổ thật trước bước 3 — xem "Trạng thái")
source: data/execution_logs/nav_unit_ledger_<account>.csv
group: trading-bot
role: sổ đơn vị quỹ — chuỗi "giá một đơn vị quỹ" chốt theo ngày; BẢN ĐỐI CHỨNG của chuỗi dựng trong bộ nhớ
writer: "mike/bin/nav_unit_ledger.py --account <account> --ledger-dir <dir> --seal (chạy TAY; từ chối thư mục dữ liệu thật)"
---

# data/execution_logs/nav_unit_ledger_<account>.csv

**Status: CHƯA TỒN TẠI, CHƯA ĐƯỢC PHÉP TẠO.** Chính sách "tài khoản = quỹ mở" (user duyệt 2026-10-10 —
`kb/projects/fund-unit-performance-policy-20261010.md`) có 4 bước; đây mới là bước 1.

## Là gì
Mỗi dòng = một ngày chốt. Cột: `date, nav, flow_bod_vnd, flow_eod_vnd, units_issued, units,
unit_price, nav_is_estimate`. Dòng đầu = mốc khởi điểm (`data/account_inception.json`): giá 10.000 đ,
số đơn vị = vốn khởi điểm / 10.000. Nạp ⇒ phát hành đơn vị, rút ⇒ huỷ đơn vị ở giá chốt; giá đơn vị
chỉ đổi vì lãi/lỗ. Bất biến: `units × unit_price = nav` từng dòng.

Dựng từ ĐÚNG ba nguồn: [`nav_history.md`](nav_history.md) (NAV + cờ `nav_is_estimate` + `balance_ts`),
[`account_cash_flows.md`](account_cash_flows.md) (nạp/rút), [`account_inception.md`](account_inception.md)
(mốc khởi điểm). Công thức ở MỘT chỗ: `nav_unit_ledger.build_ledger`.

**File trên đĩa là BẢN ĐỐI CHỨNG, không phải nguồn của tỉ suất.** Tỉ suất theo kỳ luôn tính từ chuỗi
`build_ledger` dựng trong bộ nhớ; file chỉ để phát hiện lịch sử bị đổi sau khi đã chốt.

## Ai ghi / ai đọc
- Ghi: `nav_unit_ledger.py --ledger-dir <dir> --seal` — CHỈ-GHI-THÊM (đọc file một lần dưới khoá
  `fcntl.flock` trên `<file>.lock`, ghi qua file tạm + `os.replace`). Ghi vào thư mục dữ liệu thật ⇒
  **rc=3, từ chối**.
- Đọc: KHÔNG consumer nào. `nav_period_returns.py` (CLI lẫn hàm) không đọc sổ trên đĩa ở bước này.

## Trạng thái (2026-10-11)
**KHÔNG chốt sổ thật trước bước 3.** Lý do (arch-review @feaa33b5, K2): `daily_nav_snapshot.py` ghi đè
dòng nav_history của chính ngày chạy khi chạy lại, nên một sổ đã chốt sẽ tự lệch; nếu đường công bố
đối chiếu sổ thì lệch ⇒ `nav_period_returns.py` rc=1 ⇒ cổng tỉ suất của `report_delivery_gate.py`
fail-open ⇒ báo cáo ghi số sai KHÔNG bị chặn. Bước 3 (rà các ngày `nav_is_estimate`, có đường đính chính,
quyết định cổng xử lý lệch sổ thế nào) phải xong trước khi có file thật và trước khi bất kỳ consumer
nào đọc nó.

## Bẫy
- **Dòng đã chốt không được đổi.** Sửa `nav_history` của một ngày đã chốt, khai dòng tiền lùi ngày, xoá
  hay chen một dòng quá khứ ⇒ `nav_unit_ledger.py` rc=2, in từng dòng lệch bao nhiêu, KHÔNG ghi. Chưa
  có đường tính lại lịch sử có chủ đích (đính chính) — đừng xoá file để "dựng lại cho khớp".
- `daily_nav_snapshot.py` GHI ĐÈ dòng nav_history của chính ngày chạy khi chạy lại (và `--from-raw` vá
  lùi ngày) ⇒ chốt một ngày trước khi NAV ngày đó ổn định sẽ tự gây lệch sổ.
- **File KHÔNG nằm trong git** (`.gitignore` của repo ngoài chặn `*.csv`, giống `nav_history`): tính
  "chỉ-ghi-thêm" do công cụ cưỡng chế, không có lịch sử git chống lưng.
- `nav_is_estimate=True` được MANG THEO nguyên trạng, không phải dấu hiệu dòng đó đã được rà.
- Giá đơn vị là của TOÀN tài khoản. ZaloPay còn DGC + vị thế legacy trong NAV — chuỗi "phần bot quản lý"
  là chuỗi khác, chưa có (bước 4).
