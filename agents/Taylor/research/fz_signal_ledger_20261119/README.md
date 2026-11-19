# Sổ tín hiệu paper FZ-001 / FZ-002 (+ C-CEIL, C-NFLOOR) — job Taylor_20261119_052906

Chương trình `intraday_fz_signal_ledger` (registry `kb/paper_programs_registry.json`). **PAPER-ONLY, `LOG_ONLY_NO_BROKER_PATH`, không tiền thật.** User duyệt 2026-11-19 (plan E mục #8).
Đây là **GIÁM SÁT**, không phải phép thử sắp có kết quả: ~15 ngày signal/năm ⇒ đủ ≥20 cụm khó trước 2028.

Nền: `agents/Taylor/research/intraday_cluster_audit_20261119/README.md` (NO-GO, 0/5 setup PASS) và `agents/Taylor/research/basket_vs_fz_capit_20261119/README.md` (FZ ≈ cược thời điểm hồi).

## Thành phần
| File | Vai trò |
|---|---|
| `bin/fz_signal_ledger.py` | `ingest <deals_<setup>.csv>` và `summary` |
| `bin/fz_signal_ledger_selfcheck.py` | 26 kiểm tra (idempotent, atomic, trùng id, thiếu cột, xung đột, cụm, stop-early) |
| `data/fz_signal_ledger.csv` | sổ append-only (chưa tồn tại — tạo ở lần ingest đầu có signal ≥ 2026-11-04) |

## Dòng sổ
`signal_id, setup, signal_day, symbol, entry_date, exit_date, exit_reason, hold_sessions, gross_ret_adj, net_ret_total, basket_ret, excess_vs_basket, dep1m_rate_pct, dep_prorata, excess_vs_dep, fee_side, tax_sell, export_net_ret_total, ingested_at, source_file, source_md5`

- `net_ret_total` dựng lại từ giá điều chỉnh (`entry_px/f_entry`, `exit_px/f_exit`) với phí THẬT 0,097%/chiều + thuế bán 0,1%. Export cũ dùng 0,03%/chiều nên KHÔNG dùng số export; script đối chiếu tái dựng bằng phí cũ với `net_ret_total` của file (lệch >1e-5 ⇒ từ chối cả file).
- `basket_ret` = `market_drift_same_day` nhân hệ số phí (không cộng xấp xỉ) ⇒ `excess_vs_basket` cùng cơ sở phí.
- `dep_prorata` = lãi `dep1m` Big-4 (PIT, `idle_rate_proxy.r_idle(entry_date,'dep1m')`) × ngày lịch entry→exit / 365.
- Chỉ ghi dòng `status=closed` & `in_stats=1`, setup ∈ {FZ-001, FZ-002, C-CEIL, C-NFLOOR}, `signal_day ≥ 2026-11-04` (sau holdout của nhóm kia). Dòng `open` sẽ vào sổ ở lần ingest sau khi đóng (khoá theo `signal_id`).

## Đơn vị = cụm
Cụm dựng lúc đọc (`summary`), theo từng setup: 2 ngày signal liền nhau cách ≤5 phiên ⇒ cùng cụm (E5). Giá trị cụm = trung bình excess các dòng trong cụm. Chỉ đếm cụm "đóng" (signal cuối cách `--asof` >5 phiên).

## Luật khai trước (khoá 2026-11-19)
1. Sau 10 cụm MỚI của một setup, mean `excess_vs_basket` ≤ 0 ⇒ `summary` gắn cờ `STOP_EARLY` ⇒ **báo user** (script không tự tắt).
2. Chỉ xét GO khi ≥20 cụm mới + DSR(T=cụm) ≥ 0,95 + quant-skeptic CONFIRMED + user duyệt (+ cổng biodiversity nếu mở sleeve tiền thật). Script không tính DSR.
3. Mốc xem lại (đề xuất, Mike/user chỉnh): **2027-03-31** checkpoint đầu; **2028-06-30** đánh giá đủ N. Nằm trong registry (`review_date`, `end`).

## Fail-closed
Thiếu cột bắt buộc, `signal_id` rỗng/trùng trong file, số NaN/≤0, tái dựng net lệch, lãi dep1m lỗi, cùng `signal_id` mà giá trị khác sổ ⇒ `rc=2`, **không ghi gì**. Ghi nguyên tử (tmp + `os.fsync` + `os.replace`), khoá `flock`, sổ cũ phải là tiền tố của sổ mới.

## KHÔNG làm (có chủ đích)
- Không cron, không nối live. **Nguồn signal hằng ngày từ nhóm nghiên cứu kia CHƯA có** — hiện chỉ có file deal_export tĩnh (đến 2026-11-03). **Việc user phải xin:** nhóm kia xuất `deals_<setup>.csv` cùng định dạng mỗi phiên (hoặc mỗi tuần); có rồi mới thêm cron (đăng ký `kb/cron_registry.md`, §11).
- Không mở job nghiên cứu mới trên các setup này — xem mục ĐÓNG BĂNG trong `kb/projects/rnd-pipeline-tracker.md`.

## Chạy
```
python3 bin/fz_signal_ledger.py ingest /path/deals_fz-001.csv     # lặp cho fz-002, c-ceil, c-nfloor
python3 bin/fz_signal_ledger.py summary [--asof YYYY-MM-DD]
env -u TZ python3 bin/fz_signal_ledger_selfcheck.py
```
Smoke trên dữ liệu thật (holdout, `--forward-from 2026-01-01`, sổ tạm): 148/148 dòng qua đối chiếu tái dựng phí cũ; chỉ để kiểm đường ống, KHÔNG phải kết quả forward (mẫu đó là holdout đã dùng).
