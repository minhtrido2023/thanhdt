---
kind: local-file
status: CANONICAL
source: data/account_cash_flows.json
group: trading-bot
role: dòng tiền ngoại sinh (nạp/rút vốn) theo account — đầu vào của sổ đơn vị quỹ và của cổng NAV-jump
writer: "tay (người ghi kèm bằng chứng); mẫu: mike/templates/account_cash_flows.json"
---

# data/account_cash_flows.json

**Status: CANONICAL** — nguồn DUY NHẤT của nạp/rút. DNSE OpenAPI không có sổ nạp/rút (đã quét
`dnse_api.py` + 86 file `dnse_raw_*.jsonl`, 2026-09-27) nên file này do người ghi.

## Là gì
`{"<account>": [{date, amount_vnd, kind, evidence, timing?, time_ict?}, ...]}`. `amount_vnd` dương = nạp,
âm = rút. `kind` ∈ deposit | withdraw | market_only. Schema đầy đủ + kiểm lỗi: `mike/bin/account_cash_flows.py`.
Đo 2026-10-11: cả SpaceX và ZaloPay đều 0 bản ghi.

## Ai đọc
`nav_unit_ledger.py`, `nav_period_returns.py` (thiếu file ⇒ từ chối), `report_delivery_gate.py` (cổng
bước nhảy NAV 5%), `daily_nav_snapshot.py` (cổng bước nhảy NAV 15%).

## Bẫy
- **`timing` mặc định là `eod` từ 2026-10-10** (trước đó `bod`): tiền ngày T giao dịch ở giá đơn vị chốt
  cuối ngày T, và dòng nav_history ngày T phải ĐÃ chứa khoản tiền đó. Tiền vào SAU lúc chụp NAV ngày T
  (xem `balance_ts`, thường 19:10 ICT) thì NAV ngày T chưa chứa nó — khai `eod` sẽ trừ một khoản không có
  trong NAV. `nav_unit_ledger.py` chỉ bắt được ca này khi bản ghi có `time_ict`.
- `bod` phải khai kèm `time_ict`. `eod` rơi vào ngày không có dòng nav_history ⇒ bị từ chối.
- Vốn khởi điểm KHÔNG ghi ở đây (nó ở [`account_inception.md`](account_inception.md)); bản ghi có ngày
  <= ngày khởi điểm bị loại.
- File rỗng nghĩa là "chưa ai GHI", không phải "chưa có nạp/rút" — khoản nhỏ hơn ~5% NAV lọt cả hai cổng.
