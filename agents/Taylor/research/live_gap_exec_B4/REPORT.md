# Luồng B4 — B3 đủ điều kiện merge (KHÔNG merge, KHÔNG gửi báo cáo thật)

Nhánh `feat/savings-row-b3-20261113`, worktree `wt-savings-row-20261112`, 2 commit mới trên 04fc4ce7f:
- `bfc3c068c` — nhãn tiết kiệm có điều kiện `cashDividendReceiving` (việc 3): `bin/period_table_32.py` + selfcheck.
- `4e66d163e` — PDF/email v2 (weekly+monthly) có 2 cột tiết kiệm + nhãn/cảnh báo: `bin/report_v2/build.py`, `data_sources.py` (việc 1).

## 1. Render v2 từ nhánh + e2e gate (đo trong phiên)
- Dựng PDF/HTML v2 báo cáo tuần SpaceX 02→06/11 từ code nhánh (`logs/build_weekly.log`; 4 trang, 419 từ, draft).
  HTML có đủ "Gửi tiết kiệm (tham chiếu)", "Chênh so tiết kiệm", "5% cổ tức", cảnh báo "Kết quả trong quá khứ…"; PDF (PyMuPDF): 4 lần "tiết kiệm", 1 câu 5% cổ tức, 1 cảnh báo.
- `e2e_gate.py` (ROOT = cây nhánh, sổ tạm, notify/email giả): `DELIVER_RC 0`, gate tỉ suất PASS, period-return PASS (-3,94% vs -3,944%), benchmark-table PASS (wtd/mtd/inception khớp CLI), artifact-lint PASS trên bảng có cột mới, nav-flow PASS → COMPLETE. Log: `e2e/gate_run.log`.
- ROOT bị trỏ sang nhánh (bắt buộc để CLI = code nhánh); gate đã chạy với code nhánh nên không cần cherry-pick sang main. Khi merge, cổng trên main cùng logic vì nhánh không đổi `report_delivery_gate.py`.
- Cảnh báo "GHI SỔ THẬT" của gate in ra vẫn đúng tên nhưng e2e dùng sổ tạm (`state.json` trong tmp); không đụng `state/report_delivery.json` thật (git status sạch).

## 2. report_v2_selfcheck chạy hết (nền, log ra file)
| TZ | Kết quả |
|---|---|
| `env -u TZ` | ✅ PASS 177/177 (0 lỗi) |
| Pacific/Kiritimati | ✅ PASS 177/177 (0 lỗi) |
| Asia/Ho_Chi_Minh | ✅ PASS 177/177 (0 lỗi) |
Master trước đó: 177/177 → không đổi.

Selfcheck khác (3 TZ: none / Kiritimati / ICT, mỗi cái rc=0):
| selfcheck | kết quả |
|---|---|
| period_table_32 | 104 assertion PASS ×3 |
| savings_hurdle | 61 PASS ×3 |
| nav_period_benchmark | 69 PASS ×3 |
| report_delivery_gate | 7/7 delivery + 5/5 period-return ×3 |

## 3. Câu "5% cổ tức" có điều kiện — CẦN USER DUYỆT câu thay thế
Cơ chế: đọc `cashDividendReceiving` của bản ghi `balances` cuối ngày chốt (lọc account). `=0` → biến thể đã duyệt (V0); `≠0` hoặc không đọc được → biến thể thay thế (ALT). Cổng chấp nhận đúng 2 biến thể nguyên văn, chặn V0 khi dữ kiện ≠0 (selfcheck có mutation). SpaceX 06/11: `cashDividendReceiving=0` → V0, đúng.

Câu thay thế cần user duyệt (phần sau "(0,1%)" thay cho "…, 5% cổ tức)"):
> "…lợi suất danh mục đã trừ phí giao dịch và thuế TNCN khấu trừ tại nguồn trên giá bán (0,1%). Cổ tức tiền mặt đang chờ về tài khoản vào cuối kỳ, chưa được trừ thuế TNCN 5% khấu trừ tại nguồn, nên lợi suất danh mục có thể cao hơn thực nhận một khoản nhỏ."

(Đầu câu `_SAV_HEAD` giữ nguyên bản đã duyệt; hằng `SAV_LABEL_ALT` ở `period_table_32.py:48`.) Chưa duyệt thì ALT không được dùng trong báo cáo gửi thật — kỳ nào có cổ tức chờ về sẽ cần user chốt câu trước khi gửi.

## 4. Chứng chỉ tiền gửi
Không đổi gì. Không thấy ảnh hưởng mới tới hurdle (nhãn vẫn nêu "lãi 12T cao nhất Big-4 online và chứng chỉ tiền gửi 12T"; chờ legal-vn trả lời Mike).

