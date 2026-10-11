# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại (dọn cuối ngày 2026-10-11, sau retro)
- Retro 10-11 ghi xong: kb/incidents/retro/retro-2026-10-11.md. Pattern I MỚI = cổng fail-closed (get_gated_state→DT4_only) chạy đúng thiết kế nhưng suy giảm kéo dài không cảnh báo. Fix tz đã merge (7db41261+2175a0fa).
- Chính sách "tài khoản = quỹ mở" đã duyệt; bước 1 sổ đơn vị quỹ (branch feat/fund-unit-ledger-20261011 @feaa33b5) XONG, CHƯA merge. Next: arch-reviewer 1 lần (dặn liệt kê trọn bộ lỗi) → merge → bước 2 (tự phát hiện dòng tiền).
- Dashboard strategy-fit + email EOD: đã merge 10-11 (user duyệt).
## Đang chờ / mốc ngày mai (12/10)
- 08:05 ICT: SBV nguồn B fetch — kiểm kết quả.
- 18:30 ICT daily_refresh: xác nhận vnindex_5state_dt5g_live ghi DT5G (không DT4_only).
- Trình user (chưa tự cài): (1) ops_health_check thêm check get_gated_state nguồn DT4_only; (2) macro_health_contract_selfcheck.py gắn pre-commit; (3) prompt cq-fix bắt grep consumer; (4) wakeup_audit loại job tự báo.
- Bus question cq-2026-10-11-hard-boundary: đã ack triaged-needs-human (14 ngày), cần người quyết.
## Giữ nguyên (không đổi)
- Cutloss shadow v2, corp-action broker-primary SHADOW (xem lại 2026-12-15), 4 call-site corp-action + 3 selfcheck hardcode path chưa vá, park=0 live, Instructions-dedup.

