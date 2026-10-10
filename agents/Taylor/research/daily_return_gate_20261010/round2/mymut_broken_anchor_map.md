# Đối chiếu `/tmp/archrev_k1_evidence/mymut.py` (60 đột biến của reviewer) trên cây vòng 2

Lượt chạy: `mymut_reviewer_final.txt` (2026-10-10 20:54→21:00 ICT, cây = mọi file `bin/` mtime ≤ 20:34:56,
đúng cây được commit). Lượt trước đó `mymut_reviewer_out.txt` (20:32) còn 1 "chỉ sập" (B07) — đã thêm
assertion ở `eod_trading_report_account_filter_selfcheck.py`, lượt cuối B07 chết bằng assertion rc=1.

| Kết quả | Số | Ghi chú |
|---|---|---|
| CHẾT bằng assertion | 56 | gồm đủ 15 cái reviewer báo SỐNG + 2 cái "chỉ sập" (R25, P03) ở 53b48b76 |
| SỐNG | 0 | |
| chỉ SẬP | 0 | |
| HỎNG neo | 3 | dòng nguồn đã đổi ở vòng 2 — bản tương đương bên dưới, đều CHẾT |

## 3 neo hỏng → bản tương đương trong `bin/total_return_mutants.py` (kết quả ở `total_return_mutants_final.txt`)

| Đột biến reviewer | Vì sao neo hỏng | Bản tương đương (cùng ý đột biến, neo mới) | Kết quả |
|---|---|---|---|
| `R03_stale_never_applied` — `if stale:` → `if False:` (report_return_gate.py) | F4: biến đổi tên `stale` → `tk_stale` (gộp giá trễ của RIÊNG mã) | `K1_stale_not_applied` — `if tk_stale:` → `if False:` | CHẾT rc=1 |
| `D06_first_from_series_rows` — `"first"` dựng từ dòng per-mã (dividend_adjusted_return.py) | F1: `"first"` nay = `rec_ts[0]`, `"ts"` = `witness_record_ts(series)` | `F1_ledger_ts_from_ticker_rows` (`"ts": rec_ts` → dựng từ dòng per-mã) + `F1_ts_from_ticker_rows` (trong `witness_record_ts`) + `F1_first_ignores_witness_rule` (`"first"` quay về `min(record_ts)`) | CHẾT rc=1 (cả 3) |
| `P11_stop_blind_all_sleeves` — bỏ lọc `STOP_LOSS_PCT_BY_SLEEVE` ở `stop_blind` (portfolio_status.py) | F2: điều kiện tách dòng, thêm `and sl not in AUTO_STOP_SLEEVES` | `F2_stop_blind_all_sleeves` (bỏ lọc `STOP_LOSS_PCT_BY_SLEEVE`) + `F2_stop_blind_counts_auto_sleeves` (bỏ lọc sleeve tự động) | CHẾT rc=1 (cả 2) |

## Bộ của nhánh
`total_return_mutants_final.txt`: **302 đột biến — 302 chết bằng ASSERTION, 0 sống, 0 chỉ sập, 0 hỏng neo**
(vòng 1: 239). 63 cái mới gồm toàn bộ danh sách F5 của reviewer + F1/F2/F4/F6/F7.
