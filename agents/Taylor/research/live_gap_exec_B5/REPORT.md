# Luồng B5 — sửa 3 mục skeptic B4 (KHÔNG merge, KHÔNG gửi báo cáo thật; chưa qua skeptic)

Nhánh `feat/savings-row-b3-20261113` (worktree `wt-savings-row-20261112`), commit mới **4b34e8303** trên 4e66d163e.
Files: `bin/period_table_32.py`, `bin/period_table_32_selfcheck.py`, `bin/report_v2/build.py`.

## 1. ALT đã duyệt + cổng chỉ nhận ĐÚNG 2 biến thể
- Provenance ghi tại `period_table_32.py` (comment trên `SAV_LABEL_ALT`): `decided_by: user, 2026-11-13 11:20 ICT`, câu NGUYÊN VĂN không đổi chữ.
- Cổng (`check_report`): nhãn phải là **đúng một dòng** bắt đầu "So với gửi tiết kiệm", khớp **từng byte** (sau `norm`) với V0 hoặc ALT; cắt/thêm/đổi chữ/hai nhãn cùng lúc ⇒ BLOCK. Thêm: V0 chỉ khi recv==0; ALT chỉ khi recv≠0 (ALT khi recv=0 là khẳng định sai ⇒ BLOCK — đổi so với B4, nơi ALT "luôn qua").
- Mutation (selfcheck): V0 ×6 (cắt cuối, thêm đuôi, 5%→3%, miễn→chịu thuế, chèn chữ, V0+ALT) và ALT ×5 (cắt, thêm đuôi, 5%→3%, cao hơn→thấp hơn, hai dòng) đều BLOCK.

## 2. recv=None không rơi sang ALT
- `div_receiving_ex()` → `(recv, used_date, evidence)`. `report_date` là cuối tuần/lễ (không có `dnse_raw`) ⇒ lùi từng ngày, CHỈ qua ngày không giao dịch (cuối tuần hoặc `trading_bot.vn_market.is_holiday`), tối đa 10 ngày; gặp ngày giao dịch mà thiếu dữ liệu ⇒ dừng, `None` (không nhảy qua lỗ hổng thật). Lọc `account_no` ở dòng đầu (§12) cả khi lùi.
- Đo thật (SpaceX): 2026-10-31 (Thứ Bảy) → đọc balances cuối 2026-10-30 = 0đ, recv=0 ⇒ V0; 2026-11-07 → 2026-11-06; 2026-08-14 → 9.775.000đ ⇒ ALT.
- Không có dữ kiện: `render()` in dòng `[CẦN XEM LẠI — nhãn tiết kiệm] …` kèm bằng chứng đã thử (§29); cổng BLOCK với bằng chứng ("KHÔNG tự rơi sang ALT") kể cả khi báo cáo chứa V0 hoặc ALT; `report_v2/build.py::savings_cols` raise thay vì dựng PDF/email với nhãn đoán.
- Selfcheck: ca Thứ Bảy/Chủ nhật → Thứ Sáu; thứ Hai lễ 2/9 → Thứ Sáu 30/8; thứ Hai giao dịch thiếu file → None; account khác → None; bằng chứng nêu đúng ngày đã thử.

## 3. e2e_gate trên worktree sạch từ master
`main` của repo mike không tồn tại — nhánh gốc là `master` (e86727ddb). Worktree `wt-b5-clean-20261113` (sparse `bin/` vì đĩa còn ~2,5GB) từ master, cherry-pick **cả 6 commit** nhánh (9246cd93e 418667a32 04fc4ce7f bfc3c068c 4e66d163e 4b34e8303 — master chưa có B1–B3 nên không thể chỉ 2+1).
- `E2E_ROOT_BRANCH=0` (ROOT = master canonical): **BLOCK, đúng kỳ vọng** — "CLI không có khối `savings` cho kỳ wtd": subprocess CLI của canonical là master, chưa có code savings ⇒ chỉ qua được sau khi merge. DELIVER_RC 1. Log `e2e0/gate_run.log`.
- `E2E_ROOT_BRANCH=1` (ROOT = worktree sạch): **COMPLETE**, DELIVER_RC 0; period-return, benchmark-table, artifact-lint, nav-flow PASS, bảng có cột tiết kiệm. Log `e2e1/gate_run.log`. (Run ROOT=0 đầu tiên với script cũ render từ master ⇒ không có cột tiết kiệm ⇒ không có giá trị; đã bỏ.)
- `state/report_delivery.json` thật không đụng (sổ tạm, notify/email giả).

## 4. Selfcheck 3 TZ (none / Pacific/Kiritimati / Asia/Ho_Chi_Minh), log trong `logs/`
| selfcheck | kết quả |
|---|---|
| period_table_32 | 136 PASS ×3 (B4: 104) |
| savings_hurdle | 61 PASS ×3 |
| nav_period_benchmark | 69 PASS ×3 |
| report_delivery_gate | 7/7 + 5/5 ×3 |
| report_v2 | 177 ok ×3, rc=0 (`logs/summary2.txt`; lần 1 rc=120 do đĩa đầy, đã chạy lại) |

## Không làm được / lưu ý
- Gate `ROOT=0` chỉ PASS sau khi merge (xem §3) — không thể chứng minh trước trên master thuần.
- Sự cố của tôi: lệnh `git worktree add` lần đầu fail do đĩa đầy (99%) và `cd` thất bại ⇒ 6 cherry-pick rơi vào **master** của mike. Đã hoàn nguyên: `git update-ref refs/heads/master e86727ddb` (không ai commit chen giữa), file working-tree trả về e86727ddb, `git diff e86727ddb -- bin mike` rỗng, master = e86727ddb. Không push.
- Đĩa `/` 99% (2,5GB trống) — đề nghị Mike dọn (vd `data/bq_cache_asof*` 2×2GB theo §8b cần quyết định riêng; tôi không xoá).
