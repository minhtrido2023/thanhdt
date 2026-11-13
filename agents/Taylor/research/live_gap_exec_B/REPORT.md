# Luồng B — dòng "so với gửi tiết kiệm" (PR-note) · 2026-11-13
Nhánh `feat/savings-row-20261112` @ `9246cd93e`, worktree `/home/trido/thanhdt/WorkingClaude/wt-savings-row-20261112`. KHÔNG merge, không đổi production/cron, không gửi báo cáo.

## Diff (3 file)
- `bin/savings_hurdle.py` (mới): lãi = bậc thang theo ngày của `deposit_rate_vn.effective_deposit_events_df()` (max Big-4 12T online, CCTG 12T), lãi đơn act/365 trên [from,to). Cùng công thức `hurdle_pit.py` GĐ0. Không ném lỗi: thiếu mốc lãi / mốc >200 ngày / kỳ ≤0 ⇒ `hurdle_pct=None, status=unavailable, reason`. Kỳ <365 ngày không quy năm (qua `annualize_or_null`). Cờ `anchor_warning` luôn có trong code (kỳ chạm mốc neo ≤2026-06), báo cáo chỉ hiện khi true. KHÔNG nêu thuế (chưa xác minh với Wendy — không vào báo cáo NĐT).
- `bin/nav_period_returns.py`: tham số `savings=` (mặc định hàm `compute_period_returns` = None ⇒ đầu ra byte-identical; ⚠️ CLI `nav_period_returns.py` LUÔN truyền `savings=_savings_fn()` ⇒ JSON của CLI luôn có khối `savings` — xem B2); khối `savings` cạnh `benchmark` ở `inception/wtd/mtd/day`, mốc = đúng from/to sổ đơn vị; CLI bọc `_savings_fn()` (lỗi import ⇒ ô unavailable, không mất TWR). TWR không đổi.
- `bin/savings_hurdle_selfcheck.py` (mới): **56 assertion PASS** dưới `env -u TZ`, `TZ=Pacific/Kiritimati`, `TZ=Asia/Ho_Chi_Minh`. Ca: kỳ 1 ngày, vắt qua đổi mốc (đối chiếu brute-force từng ngày), thiếu dữ liệu, kỳ 365 ngày, cờ neo, MTD/WTD/inception thật, khớp GĐ0 (SpaceX 01/07→11/11 = 2,548%, ZaloPay 06/07→11/11 = 2,455%, ≠ 2,70% phẳng), TWR/trường cũ không đổi khi thêm savings.

## Selfcheck lõi chạy lại (§23), `env -u TZ`, interpreter wc_venv
| selfcheck | kết quả |
|---|---|
| nav_period_benchmark | 69 PASS |
| vnindex_total_return | 267 PASS |
| nav_unit_ledger | 4758 PASS |
| nav_flow_term | 230 PASS |
| report_delivery_gate (có period-return) | PASS 7/7 + 5/5 |
| report_return_gate_selfcheck | **FAIL, nhưng FAIL y hệt trên master** (kiểm cả hai): `newdeals_daily_report` → `sector_lens_monitor` không có `double_confirm_set`; lỗi có sẵn, không do nhánh này |
| report_v2_selfcheck | **CHƯA xong**: timeout >550s (lần 1 >600s), không có kết luận |
| send_report_email | không có selfcheck riêng; chỉ nhận file .md nên không chạm |

## Dry-run render (báo cáo tuần 02–06/11, SpaceX) — `dryrun_weekly_2026-11-06.md`
Tuần/MTD: SpaceX −0,26% vs tiết kiệm +0,14% (−0,41pp); từ đầu: −3,94% vs +2,45% (−6,39pp). Template CHƯA sửa.

## Rủi ro §21/§31, người tiêu thụ, rollback
- §31: số tiết kiệm lấy từ cùng JSON `nav_period_returns.py`; không tính tay. §21: không đụng tỉ suất per-position.
- Tiêu thụ trường mới: hiện CHƯA ai (chỉ thêm khóa JSON). Cần thêm ở bước sau, chờ duyệt: template weekly/monthly + `report_delivery_gate._check_benchmark_table` (khớp ±0,005pp). Chưa làm vì brief cấm sửa template khi chưa qua cổng.
- Cần user/Wendy duyệt trước khi lên báo cáo NĐT: cách diễn đạt "thua tiết kiệm", nhãn "mốc tham chiếu thượng cận"; thuế = chưa xác minh.
- Rollback: bỏ commit `9246cd93e` hoặc gọi hàm không truyền `savings=` (byte-identical chỉ ở mức hàm; CLI luôn có khối savings nên rollback CLI = bỏ commit).

> [B2 13/11] Đính chính: "byte-identical" chỉ đúng với default của hàm; CLI luôn phát khối `savings`. Xem `live_gap_exec_B2/REPORT.md`.
