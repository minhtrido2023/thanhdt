---
kind: local-file
status: CANONICAL
source: data/account_inception.json
group: trading-bot
role: mốc khởi điểm (ngày + vốn) của từng account cho tỉ suất "từ khi bắt đầu hoạt động" và sổ đơn vị quỹ
writer: tay (user duyệt từng mốc)
---

# data/account_inception.json

**Status: CANONICAL** — `inception_date` + `starting_capital` mỗi account. Sổ đơn vị quỹ lấy đây làm
dòng đầu: giá 10.000 đ, số đơn vị = `starting_capital` / 10.000.

Đo 2026-10-11: SpaceX 2026-07-01 / 1.000.000.000 · ZaloPay 2026-07-06 / 987.865.567 (user duyệt
2026-09-27, Option A).

## Ai đọc
`nav_unit_ledger.py` (`load_inception`), và qua nó `nav_period_returns.py`, `portfolio_status.py`,
`daily_nav_snapshot.py` (dòng "Từ go-live" và "% so với hôm trước" của báo cáo ngày — từ 2026-10-11).

## Bẫy
- KHÁC `data/account_seed_capital.json` ([`account_seed_capital.md`](account_seed_capital.md)) — file kia
  phục vụ đẳng thức của `reconcile_equity.py`.
- Dòng đầu của `nav_history_<account>.csv` là snapshot SAU phiên đầu tiên, không phải vốn khởi điểm
  (coding_guidelines_ext §31).
- **Đây là mốc DUY NHẤT cho mọi phần trăm hiệu suất.** Trước 2026-10-11 dòng "Từ go-live" của
  `daily_nav_snapshot.py` dùng `--starting-capital` mặc định 1 tỷ (không caller nào truyền) ⇒ 28/28 báo
  cáo ngày ZaloPay có dòng đó in thấp hơn số chuẩn 1,127–1,220 điểm % (vd 2026-10-09: −6,06% so với
  −4,907%). Báo cáo cũ KHÔNG được sửa/gửi lại. `--starting-capital` giờ chỉ còn là mốc cho cổng bước
  nhảy 15% của phiên đầu tiên.
- Đổi `starting_capital` hay `inception_date` làm đổi MỌI giá đơn vị ⇒ lệch toàn bộ sổ đã chốt.
- **Bản ghi dòng tiền bị loại theo NGÀY, không theo giờ** (`date` <= `inception_date` ⇒ `dropped_flows`).
  Mốc ZaloPay là NAV đêm TRƯỚC phiên 2026-07-06, nên tiền vào trong/tối 07-06 KHÔNG nằm trong vốn khởi
  điểm mà vẫn bị loại — nó hiện ở `dropped_flows` để người đọc thấy; code không tự sửa (arch-review lần 2,
  L10). Hiện không có bản ghi nào như vậy (0 bản ghi dòng tiền, đo 2026-10-11).
