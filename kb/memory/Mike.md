# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike (cuối ngày 10/11 → 11/11)
## Đang chờ user
- Retro 10/11 ghi xong (kb/incidents/retro/retro-2026-11-10.md). Escalation đang mở, KHÔNG mở trùng: retro-pattern-recurring-bg-dispatch-wakeup-miss-gate-checks-declaration-only (khuyến nghị A: Stop hook kiểm ScheduleWakeup thật) và retro-pattern-recurring-anomaly-flags-stale-weekend-false-alarm (A: checker dùng lịch phiên; gộp luôn drift-check CANNOT_CHECK, bin/plan_position_drift_check.py:130 neo ngày plan).
- Câu hỏi mở: vgs-exit-max-sessions-can-chot (DollarBill, A/B/C: VGS không nêu hạn giữ vs auto_exit_inject cần max_sessions>0).
- Plan 11/11 (DollarBill rev2, có VGS+NNC) chờ user duyệt; drift-check 11/11 báo CANNOT_CHECK (lỗi ngày-lịch) ⇒ tự kiểm vị thế tay trước khi duyệt.
- LAG cache adjusted (A) ĐÃ merge+áp pkl 10/11; crontab dời orb_drift 15:50→15:55 BỊ classifier chặn ⇒ user tự chạy/cho phép, rồi cập nhật kb/cron_registry §11. Sáng 11/11 kiểm w_LAG live + papertrade 15:30 (lần đầu cache mới). GIỮ pin R3 22,12/25,42; re-pin mirror-live REFUTED.
- BAL edge gate tháng: nghiên cứu CONFIRMED gate hại CAGR ~2–2,8pp; code f103ae0fa CHƯA merge, chờ user quyết bật/không + cron 00:40.
- DD VGS đã email 1 lần (không gửi lại). HHS ex_basis_pending; SCL kiểm quyền sau 08/12. Winston: BQ Close SCL chưa điều chỉnh lùi 09/11.
- Fix chưa làm: close_bus_question --verified-by; wakeup gate kiểm hành động thật; dedupe APPROVAL_GATE_BLOCK; lệnh đối ứng cùng mã chưa guard; 2 cron work-tree/thẻ Livermore/macro TE Làn 2/pnj-bctc-q3 chờ user OK.
- LAG luật 5 (09/11): mua LAG cần DD + giá<=tâm; mốc 15/12; lag_gate_exit_check.py chưa cron.
## Mốc
nav-loss-brake 11-09 (đã qua); commodity 11-25; BĐS 11-26; Livermore H20 03/12; LAG 12-15; audit đo lường ~12-27; DT CRISIS sớm nhất ~11/10.

