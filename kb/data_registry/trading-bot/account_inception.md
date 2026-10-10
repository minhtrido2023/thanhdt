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
`nav_unit_ledger.py` (`load_inception`), và qua nó `nav_period_returns.py`, `portfolio_status.py`.

## Bẫy
- KHÁC `data/account_seed_capital.json` ([`account_seed_capital.md`](account_seed_capital.md)) — file kia
  phục vụ đẳng thức của `reconcile_equity.py`.
- Dòng đầu của `nav_history_<account>.csv` là snapshot SAU phiên đầu tiên, không phải vốn khởi điểm
  (coding_guidelines_ext §31).
- Đổi `starting_capital` hay `inception_date` làm đổi MỌI giá đơn vị ⇒ lệch toàn bộ sổ đã chốt.
