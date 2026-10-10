---
kind: local-file
status: CANONICAL (cơ chế có từ 2026-10-11; file thật CHƯA được chốt lần đầu — xem "Trạng thái")
source: data/execution_logs/nav_unit_ledger_<account>.csv
group: trading-bot
role: sổ đơn vị quỹ — chuỗi "giá một đơn vị quỹ" chốt theo ngày, nguồn duy nhất cho tỉ suất theo kỳ
writer: "mike/bin/nav_unit_ledger.py --account <account> --seal (chạy TAY; chưa có cron)"
---

# data/execution_logs/nav_unit_ledger_<account>.csv

**Status: CANONICAL** cho tỉ suất gia quyền thời gian của tài khoản thật (chính sách "tài khoản = quỹ
mở", user duyệt 2026-10-10 — `kb/projects/fund-unit-performance-policy-20261010.md`).

## Là gì
Mỗi dòng = một ngày chốt. Cột: `date, nav, flow_bod_vnd, flow_eod_vnd, units_issued, units,
unit_price, nav_is_estimate`. Dòng đầu = mốc khởi điểm (`data/account_inception.json`): giá 10.000 đ,
số đơn vị = vốn khởi điểm / 10.000. Nạp ⇒ phát hành đơn vị, rút ⇒ huỷ đơn vị ở giá chốt; giá đơn vị
chỉ đổi vì lãi/lỗ. Bất biến: `units × unit_price = nav` từng dòng.

Dựng từ ĐÚNG ba nguồn: [`nav_history.md`](nav_history.md) (NAV + cờ `nav_is_estimate`),
[`account_cash_flows.md`](account_cash_flows.md) (nạp/rút), [`account_inception.md`](account_inception.md)
(mốc khởi điểm). Công thức ở MỘT chỗ: `nav_unit_ledger.build_ledger`.

## Ai ghi / ai đọc
- Ghi: `nav_unit_ledger.py --seal` — CHỈ-GHI-THÊM (byte cũ giữ nguyên, ghi qua file tạm + `os.replace`).
- Đọc: `nav_period_returns.py` (đường CLI) đối chiếu chuỗi nó vừa dựng với các dòng đã chốt; lệch ⇒ rc=1,
  không in số. `portfolio_status.py` gọi `compute_period_returns` trong tiến trình và KHÔNG đối chiếu sổ.

## Trạng thái (2026-10-11)
File thật trong `data/execution_logs/` CHƯA tồn tại — lần chốt đầu tiên là thao tác sau khi merge, và
chưa có cron chốt hằng ngày (bước 3 của chính sách: rà các ngày `nav_is_estimate` rồi khoá lịch sử).
File chưa có ⇒ `nav_period_returns.py` in `"unit_ledger": {"sealed_through": null}` và vẫn tính từ chuỗi
dựng trong bộ nhớ (cùng công thức).

## Bẫy
- **Dòng đã chốt không được đổi.** Sửa `nav_history` của một ngày đã chốt, khai dòng tiền lùi ngày, xoá
  hay chen một dòng quá khứ ⇒ `nav_unit_ledger.py` rc=2, in từng dòng lệch bao nhiêu, KHÔNG ghi. Chưa
  có đường tính lại lịch sử có chủ đích (đính chính) — đừng xoá file để "dựng lại cho khớp".
- `daily_nav_snapshot.py` GHI ĐÈ dòng nav_history của chính ngày chạy khi chạy lại (và `--from-raw` vá
  lùi ngày) ⇒ chốt một ngày trước khi NAV ngày đó ổn định sẽ tự gây lệch sổ.
- **File KHÔNG nằm trong git** (`.gitignore` của repo ngoài chặn `*.csv`, giống `nav_history`): tính
  "chỉ-ghi-thêm" do công cụ cưỡng chế, không có lịch sử git chống lưng. Mất/sửa tay file thì không có
  bản đối chứng độc lập.
- `nav_is_estimate=True` được MANG THEO nguyên trạng, không phải dấu hiệu dòng đó đã được rà.
- Giá đơn vị là của TOÀN tài khoản. ZaloPay còn DGC + vị thế legacy trong NAV — chuỗi "phần bot quản lý"
  là chuỗi khác, chưa có (bước 4).
