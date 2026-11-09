# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike (cuối ngày 09/11 → 10/11)
## Đang chờ user
- Retro 09/11 ghi xong (kb/incidents/retro/retro-2026-11-09.md). Escalation đang mở: retro-pattern-recurring-anomaly-flags-stale-weekend-false-alarm (khuyến nghị A: checker dùng lịch phiên) — KHÔNG mở trùng.
- Cần kiểm: báo cáo tuần 02–06/11 đã gửi ĐỦ kênh chưa (`report_delivery_gate.py`; state/report_delivery.json không thấy key 2026-11-02) + file ZaloPay. Memory cũ "BQ Price chờ OK UPDATE" đã lỗi thời (Wags làm tươi cache G2).
- Fix chưa làm: (i) close_bus_question yêu cầu --verified-by theo measured_by; (ii) wakeup gate kiểm hành động thật (MISS 3 ngày liền, 25% hôm 09/11); (iii) dedupe APPROVAL_GATE_BLOCK theo (account, plan_date) (100 event/5h); (iv) anomaly-flags-stale + chuỗi park vòng CN lỗi lịch ngày-lịch vs ngày-phiên.
- LAG luật 5 (user 09/11): mua LAG cần DD + giá<=tâm; thoát = 1 tháng dương (known_date,n>=30) → user xét candidate quý; mốc 15/12; bin/lag_gate_exit_check.py CHƯA có cron (hỏi user). Plan 10/11 = 0 lệnh HOLD.
- DD: DGC không giảm (user), DCM r7 không làm, CK holding chốt C (base 0% + nhãn nhạy). Sổ dd_price_zones 73 entry CHƯA commit (backup cron gom). GVR/HTN/MZG/YEG/PHP chưa DD.
- Chờ user OK: 2 cron work-tree; thẻ tần suất Livermore; macro TE Làn 2; pnj-bctc-q3-review-trigger; approve_plan_simple.sh thiếu --dry-run. Lệnh đối ứng cùng mã: chưa guard code.
## Mốc
DT CRISIS ~11/10 sớm nhất; nav-loss-brake 11-09; commodity 11-25; BĐS 11-26; Livermore H20 03/12; LAG 12-15; audit đo lường ~12-27.

