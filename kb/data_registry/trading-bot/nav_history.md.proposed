---
kind: local-file
status: CANONICAL
source: data/execution_logs/nav_history_<account>.csv
group: trading-bot
role: chuỗi NAV ngày — nguồn duy nhất mọi báo cáo daily/weekly/monthly
writer: daily_nav_snapshot.py trong eod_trading_report.sh, 19:10 ICT
---

# data/execution_logs/nav_history_<account>.csv

**Status: CANONICAL (NAV series)**

## Là gì
Chuỗi NAV ngày — nguồn duy nhất mọi báo cáo daily/weekly/monthly.

## Ai ghi / cadence
`daily_nav_snapshot.py` trong `eod_trading_report.sh`, 19:10 ICT.

## Bẫy
MTM cùng ngày phải dùng giá DNSE, BQ chỉ cho ngày quá khứ (sự cố 07-06 đã vá); P&L cho vị thế legacy
(ZaloPay) chưa đúng — known gap.
- Dòng nav_history chỉ được sửa tay qua `fund_restatement.py apply` (nhật ký
  [`nav_history_corrections.md`](nav_history_corrections.md), sao lưu byte ở
  `data/execution_logs/restatement_backups/`). `apply` chỉ chạy 09:00–18:30 ICT: file này bị ghi lúc
  19:00–21:45 (`nav_sync_retry` mỗi 15'), 19:10 (EOD), 19:50 (+2 retry) và KHÔNG có khoá chung với
  `daily_nav_snapshot._write_nav_history`.
- **`balance_ts` của dòng ĐÃ ĐÍNH CHÍNH có thể là QUY ƯỚC, không phải giờ chụp thật** (từ 2026-10-14,
  nhánh feat/fund-history-lock-20261014). Dòng SpaceX 2026-07-02 sau đính chính mang
  `balance_ts = 2026-07-02T14:45:00` = "số dư TẠI GIỜ ĐÓNG CỬA" dựng lại (số dư chụp 09:46:35 trừ lệnh
  126631 bị khoá tiền sau lần chụp), KHÔNG phải lúc có bản ghi balances nào. 14:45:00 trùng đúng biên đóng
  cửa — cổng "chụp trước đóng cửa" của `nav_unit_ledger.py` so chặt `<` nên dòng này qua cổng KHÔNG cần
  `--accept-preclose`; đó là CHỦ ĐÍCH (giá trị dòng đã là số dư giờ đóng cửa), bằng chứng nằm ở
  `nav_history_corrections.jsonl` + file đính chính
  (`agents/Taylor/research/fund_history_lock_20261014/corrections/correction_SpaceX_AB.json`). Nhận
  diện: `nav_source` bắt đầu bằng `dinh chinh` và ngày có bản ghi trong nhật ký đính chính. Đừng dùng
  `balance_ts` của dòng như vậy để suy "lúc đó bot đang chạy" hay để ghép với bản ghi dnse_raw cùng giờ.
