# Quỹ mở bước 2 — đẳng thức tiền (job Taylor_20261012_124854)

Nhánh `feat/fund-cashflow-detect-20261012`, commit `ea9d6969a` (base master `fa6d36c8b`), worktree
`agents/Taylor/wt-fundcf-1012`. CHƯA merge, CHƯA push, không sửa data/ thật, không sửa crontab.

| Nghiệm thu | Bằng chứng | Kết quả |
|---|---|---|
| 1. Số không đổi | `acceptance/1_numbers_unchanged.txt`, `control/compare_all_dates.txt` | 12.663 giá trị / 201 (tài khoản, ngày) so master: 0 lệch |
| 2. Đẳng thức toàn lịch sử | `acceptance/2_history_residuals.txt`, `history_residuals.py` | 135 cửa sổ; ngưỡng 0,05% NAV; 2 vượt (SpaceX 07-03, 08-28); 0 không kiểm được |
| 3. Dòng tiền giả lập | `acceptance/3_simulated_flows.txt`, `3_demo.py` | 12 ca (nạp/rút × trên/dưới ngưỡng × trong phiên/sau đóng cửa/cuối tuần): 6 trên ngưỡng bắt đủ, 6 dưới ngưỡng không báo; ZaloPay 0 ở mọi ca |
| 4. Cổng tỉ suất fail-closed | `acceptance/4_gate_fail_closed.txt`, `4_gate_rc.py` | master: báo cáo QUA cổng khi CLI rc=1 (đỏ); nhánh: BLOCK (xanh) |
| 5. Mutant | `mut/out_ar3.txt`, `mut/out_step2.txt`, `mut/run.py` | 157 bị giết (152 assertion + 5 crash), 0 sống; 5 mutant cũ B01/B02/B03/B08/B09 không áp được vì K3 viết lại dòng đó — thay bằng B01n/B02n/B03n/B08n/B09n (đều bị giết) |
| Selfcheck 3 TZ | `acceptance/5_selfcheck_3tz.txt` | 7 selfcheck × {không TZ, America/New_York, Pacific/Kiritimati}: rc=0; `report_return_gate_selfcheck.py` rc=1 trong sandbox vì cần git (master cũng rc=1) |
| Quét rộng §23 | `broad_scan_branch/summary.txt` vs `broad_scan_master/summary.txt` | 27 selfcheck: 10 rc=1 ở CẢ nhánh lẫn master (log giống nhau, chỉ khác tên thư mục /tmp), 17 rc=0; khác duy nhất `cash_identity_selfcheck.py` (file mới: nhánh 0, master 2) |
| Mục B | `B_result.md`, `B_dnse_email_probe.txt` | DNSE KHÔNG gửi email nạp/rút |

Việc của người: `proposed_acks.json` (2 bản ghi market_only đề xuất cho SpaceX — KHÔNG phải sổ thật).
