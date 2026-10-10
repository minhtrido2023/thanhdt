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
  Mốc được coi là giá CHỐT của `inception_date`. ZaloPay: mốc = balances `2026-07-06T21:45:43` (sau đóng
  cửa 07-06, `data/account_seed_capital.json`) ⇒ đúng, chỉ hở khe 21:45–24:00 ngày 07-06. SpaceX: mốc 1 tỷ
  là số dư SÁNG 2026-07-01 (09:30, trước phiên đầu) ⇒ tiền vào 07-01 sau 09:30 bị loại oan, và tiền vào
  07-02 trước lần chụp 09:46 được phát hành ở 10.000, thiếu biến động phiên 07-01 (~0,5%) mà không lỗi.
  Bản ghi bị loại hiện ở `dropped_flows`; code không tự sửa (arch-review lần 2 L10, đính chính lần 3 K1).
  Hiện không có bản ghi nào như vậy (0 bản ghi dòng tiền, đo 2026-10-11).
