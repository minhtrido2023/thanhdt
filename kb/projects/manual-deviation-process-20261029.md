# Quy trình LỆNH TAY / DÒNG TIỀN NGOÀI PLAN — khai một lần, mọi consumer biết (user yêu cầu 29/10/2026 20:20 ICT)

## Vấn đề (đo 29/10)
User bán tay SCL 14:26 (SpaceX 800cp @29.600, ZaloPay 500cp @29.600) + rút Trứng vàng 18.023.489đ SpaceX→ZaloPay 09:04. Hệ thống chỉ biết lệnh bot + statement DNSE (email ~16:30, hôm nay CHƯA về lúc 20:20):
- `daily_nav_snapshot` chặn **rc=5** cả 2 TK (`qty_change_block`: SCL −800 / ZaloPay tương tự "chưa giải thích") ⇒ **NAV 29/10 = null** ⇒ dòng tiền 18,02tr cũng KẸT ở `pending_flows` (cần dòng NAV sau 09:04).
- EOD report in 🚨 "CẦN NGƯỜI XỬ LÝ" cho đúng việc user đã chủ động làm; DollarBill/plan-drift cũng "KHÔNG KIỂM ĐƯỢC".
Tiền lệ: DRI 21/10 (vá riêng đọc statement — chỉ chạy khi email về).

## Quy trình (hiệu lực NGAY, thủ công cho tới khi code xong)
1. **Mike ghi sổ ngay khi user báo** lệnh tay / rút-nạp ngoài plan: ngày, giờ ICT, TK, mã, side, KL, giá, mã lệnh broker nếu có, nguồn (tin user + DNSE đọc sống). Nơi ghi tạm: mục "Lệnh tay đã khai" của `kb/current_ops.md` + dòng tiền → `data/account_cash_flows.json`; (code xong ⇒ `data/user_manual_actions.json`, xem dưới).
2. **Mike xác nhận bằng broker** (DNSE read-only: order_history/positions) — KHÔNG tin riêng lời nói; KL broker khác KL khai ⇒ hỏi lại user.
3. **Báo DollarBill**: dispatch plan T+1 phải có dòng "Lệnh tay đã khai hôm nay (đã xác nhận broker): …" — dùng KL broker thật, không coi là drift/bất thường.
4. **Báo EOD report**: lệnh tay đã khai ⇒ mục "ℹ️ Lệnh tay đã khai" (KHÔNG 🚨); chỉ 🚨 khi phần dư KHÁC khai.
5. NAV gate chỉ chấp nhận lệnh tay đã khai nếu **order-history broker xác nhận đúng KL** (khai ≠ bằng chứng; chỉ là chỉ mục tới bằng chứng). Fail-closed giữ nguyên với mọi phần dư còn lại.

## Code (giao Taylor, arch-review Opus, merge cần user — chạm cổng NAV)
Spec: sổ `data/user_manual_actions.json` + `bin/manual_actions.py` (add/list/verify-với-DNSE-order-history); nguồn fill thứ 3 (order-history DNSE) cho `broker_fill_confirm` ⇒ cổng KL (`daily_nav_snapshot`, `compute_active_nav`, `park_holdings`, `exdate_frame`) nhận; EOD report + `plan_position_drift_check` + prompt DollarBill (`bq_freshness_check.sh`) đọc sổ. Selfcheck: phần dư KHÁC khai vẫn chặn; khai không có bằng chứng broker không mở cổng.

## Lệnh tay đã khai — 29/10/2026 (đã xác nhận broker 14:30, `kb/projects/scl-dd-20261029.md`)
- SpaceX SELL SCL 800 @29.600 (lệnh 344271, 14:26:56). ZaloPay SELL SCL 500 @29.600 (14:28:29).
- Dòng tiền: Trứng vàng 18.023.489đ rút SpaceX → nạp ZaloPay, 09:04 (`data/account_cash_flows.json`, ảnh DNSE).
