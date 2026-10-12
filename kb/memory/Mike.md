# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại (12/10 sáng, topic dashboard 1558645322085826593)
- User 08:16 ICT: "làm nốt các việc mở" ⇒ 2 job Taylor opus --bg: Taylor_20261012_011913 (repo ngoài, nhánh fix/dt5g-gate-followups-20261012: macro_healthcheck ghi atomic + 2 ca ghim 5 phút + CHỈ ĐỌC signal_v11_sql.py:109 + chế độ selector custom30V) và Taylor_20261012_011934 (repo mike, nhánh fix/dashboard-dt5g-followups-20261012: gửi trùng email, staleness_watch tz, cq hard-boundary macro_healthcheck, ops_health_check check DT4_only).
- Next: job xong → verify artifact → arch-reviewer 1 lần/nhánh (dặn liệt kê trọn bộ) → merge nhánh mike; nhánh repo ngoài (file ghi đầu vào cổng) CHỈ merge SAU khi 18:30 xác nhận DT5G.
- Tầng 3 dashboard: đã trả lời user = làm bản hẹp (drawdown so neo −25,2% + trượt giá so ngưỡng 22bps), HOÃN ô NAV-so-dải-backtest. Chờ user duyệt.
- Sổ đơn vị quỹ: nhánh feat/fund-unit-ledger-20261011 không còn commit lệch master, bin/nav_unit_ledger.py đã ở master — kiểm lại trạng thái merge trước khi làm bước 2.
## Mốc hôm nay 12/10 (CronCreate trong phiên — MẤT nếu phiên restart)
- 18:47 ICT: xác nhận vnindex_5state_dt5g_live ghi DT5G → báo Trading Daily.
- 19:23 ICT: xác nhận email EOD kèm strategy_fit html (lần gửi thật đầu) → báo topic dashboard.
- 08:05 SBV nguồn B fetch — chưa kiểm kết quả.
- Còn trình user: macro_health_contract_selfcheck gắn pre-commit; prompt cq-fix bắt grep consumer; wakeup_audit loại job tự báo.
- Bus question cq-2026-10-11-hard-boundary: chờ user quyết mục cctg_rate_vn.py:129.
## Giữ nguyên (không đổi)
- Cutloss shadow v2, corp-action broker-primary SHADOW (xem lại 2026-12-15), 4 call-site corp-action + 3 selfcheck hardcode path chưa vá, park=0 live, Instructions-dedup.

- [2026-10-12T01:20:56Z] [12/10 08:20 ICT, thread 1559007710136246294] User duyệt A cho cq-2026-10-11-hard-boundary #2: Taylor job Taylor_20261012_012032 sửa asof ICT ở cctg_rate_vn.py:129 + deposit_rate_vn.py:195/280/306, nhánh fix/cctg-deposit-asof-ict-20261012 (repo /home/trido/thanhdt). Next: verify artifact → arch-reviewer 1 lần (liệt kê trọn bộ) → merge → close_bus_question.py code-reviewer/cq-2026-10-11-hard-boundary --decided-by-user (#1 đã vá 7db41261+2175a0fa) → nhả claim file. Câu hỏi MỚI chưa trình xong: Winston/deposit-cctg-weekly-question (sbv_policy nguồn B, 08:09 ICT 12/10).
