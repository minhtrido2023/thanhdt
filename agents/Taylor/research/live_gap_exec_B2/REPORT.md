# Luồng B vòng 2 — hoàn tất dòng "so với gửi tiết kiệm" · 2026-11-13
Nhánh `feat/savings-row-20261112` @ `418667a32` (trên `9246cd93e`), worktree `wt-savings-row-20261112`. KHÔNG merge, không sửa template/cron, không gửi báo cáo. Chờ user/Wendy duyệt câu chữ + thuế.

## 1. report_v2_selfcheck chạy xong (detached, `env -u TZ`, log `logs/`)
| Cây | Kết quả | Log |
|---|---|---|
| master `4b9b1e354` (worktree sparse) | **PASS 177 ok, 0 lỗi, rc=0** | `v2_master.log` |
| nhánh @`9246cd93e` | **PASS 177 ok, 0 lỗi, rc=0** | `v2_branch_at_9246cd93e.log` |
| nhánh @`418667a32` (HEAD, sau B2) | **PASS 177 ok, 0 lỗi, rc=0** | `v2_branch_head.log` |
Ba lượt khớp nhau (177/177) ⇒ khối savings luôn-bật trong CLI **không làm gãy** `report_v2`. Lý do cơ khí (đã đọc code, không chỉ suy từ PASS): `report_v2/data_sources.periods()` gọi thẳng `compute_period_returns(..., benchmark=...)` KHÔNG truyền `savings=` ⇒ không thấy khối mới; consumer đọc JSON CLI (`period_table_32.run_cli`, `report_delivery_gate` period-return) chỉ lấy khoá có tên (`return_pct`, `benchmark.*`) ⇒ khoá thừa vô hại. Còn lại `daily_nav_snapshot`, `portfolio_status`, `fund_restatement` import hàm, không qua CLI.
Cũng lưu ý: `--sleeve bot` KHÔNG phát khối savings (chỉ chuỗi chính) ⇒ cổng bỏ qua cột tiết kiệm ở dòng (b).

## 2. anchor_warning siết (`bin/savings_hurdle.py`)
Bật khi BẤT KỲ ngày tích luỹ dùng lãi của một dòng bậc thang có `time` ∈ ngày `DEPOSIT_EVENTS` (neo tay), không còn `from_date <= neo cuối`. `accrual_pct` trả thêm `used_anchor` (tuple 3 phần tử; 1 caller ngoài selfcheck, đã grep). Đo thật: 01/07→19/07 = **cờ BẬT** (code cũ bỏ sót, vì from > 06-01); 01/07→11/11 và 06/07→11/11 cờ BẬT (Jul–Sep dùng neo 06-01 = 6,8%); 01/10→11/11 và 02/11→06/11 cờ TẮT. ⇒ báo cáo hiện tại (kỳ từ đầu) sẽ phải hiện cảnh báo neo cho tới khi chuỗi công bố phủ cả kỳ.
Selfcheck: ca synthetic (kỳ mang neo, kỳ chỉ mốc công bố, vắt qua 09-30, không khai anchors ⇒ không cờ) + ca thật. **61 assertion PASS** (trước 56).

## 3. Kiểm chéo cổng (`bin/period_table_32.py::check_report`, gọi bởi `report_delivery_gate._check_benchmark_table`)
Template KHÔNG đổi ⇒ bảng hiện tại không có cột tiết kiệm ⇒ hành vi cũ nguyên. Khi bảng CÓ cột chứa "tiết kiệm" (cột có "chênh" = excess, còn lại = hurdle): ô phải khớp khối `savings` của CLI ±0,005pp; excess ≈ TWR − hurdle (±0,01 vì hai ô làm tròn); CLI thiếu khối / `unavailable` mà bảng có số ⇒ CHẶN, thông điệp trích cột + số CLI.
Selfcheck mới (`period_table_32_selfcheck.py`, **68 assertion PASS**, 3 TZ): dương (khớp; không cột ⇒ không đổi; lệch 0,004 qua); âm (hurdle +0,02, excess +0,02, hurdle +0,007 > tol, CLI thiếu khối, CLI unavailable, excess tự bịa).
⚠️ Tên cột là QUY ƯỚC của cổng, template thật chưa tồn tại — khi duyệt template phải dùng tên chứa "tiết kiệm"/"chênh" (hoặc chỉnh cổng cho khớp).

## 4. Đính chính REPORT B
"byte-identical" chỉ đúng với default của hàm; CLI luôn phát khối savings. Đã sửa `live_gap_exec_B/REPORT.md` (2 chỗ + ghi chú cuối).

## Selfcheck lõi lại (`env -u TZ`, wc_venv)
savings_hurdle 61 · nav_period_benchmark 69 · vnindex_total_return 267 · nav_unit_ledger 4758 · nav_flow_term 230 · report_delivery_gate PASS 7/7 + 5/5 · period_table_32 68 (TZ unset / Pacific/Kiritimati / Asia/Ho_Chi_Minh) — tất cả PASS. `report_return_gate_selfcheck` đỏ có sẵn trên master (đã nêu ở B), không chạy lại.

## Còn treo
Duyệt câu chữ "thua tiết kiệm"/nhãn thượng cận + thuế (Wendy); tên cột template; 2 bẫy môi trường: đĩa `/` còn 4,8GB/233GB (98%) — worktree đầy đủ của mike (161k file) không dựng nổi ở /tmp, dùng sparse.
