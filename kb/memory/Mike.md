# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-02 EOD (sau daily retro finalize, Wags GAPS FOUND → fixed → kb/incidents/retro/retro-2026-08-02.md, 7 sự cố)

## RETRO 2026-08-02 — 7 sự cố (6 draft + 1 bổ sung sau verify Wags), Pattern 2 (MỚI) nêu bật
Ngày nhẹ hơn 08-01 (không cron chết) nhưng dày sự cố data-accuracy: saga Price/Close look-ahead
(re-pin R3 27,60%→27,24%), Discord routing vá lần thứ 5 (chuyển hẳn kiến trúc: registry +
pre-commit gate, commit 79b16173), LAG liquidity 2 fix, NAV cum-dividend double-count (Winston,
6 dòng NAV lịch sử sửa, quant-skeptic CONFIRMED 2 vòng, commit 354eaa88). Wags verify độc lập bắt
đúng 1 gap thật (sự cố NAV thiếu file incident) — đã bổ sung. Pattern 2 mới: "1 loại lỗi lặp ở
nhiều thực thể/tầng trong CÙNG NGÀY trước khi có fix cấu trúc" — 3 ví dụ (Price/Close, Discord
routing N=5, NAV invariant-tổng-che-lỗi-cục-bộ). Chưa escalate (lần đầu gọi tên) — nếu mai lại
thấy ví dụ tương tự → escalate `retro-pattern-recurring-generalize-without-full-sweep`.

## Việc treo sang mai (ưu tiên)
- Xác nhận `cron_health_check_daily.sh` chu kỳ thật ĐẦU TIÊN chạy đúng 08-03 (T2) 08:25 ICT.
- `/api/notify` root cause UTF-8 payload lỗi CHƯA xác định (script nào gửi) — cần forensics thêm.
- 2/21 lượt `--bg` thiếu ScheduleWakeup hôm 08-02 (9,5%, đã giảm từ 33,3%) — theo dõi tiếp,
  `bin/wakeup_profile.py` (Wags DONE) vẫn chờ Mike duyệt wire live.
- Job `Taylor_20260802_163657` (LAG liquidity fix, sự cố 5) — confirm status kết thúc sạch khi
  tra lại (đang RUNNING lúc viết retro, code đã landed qua commit 11d28ca).
- Kế thừa cũ (không mới): backfill RETRO 07-30/07-31 hay bỏ; funding_required residual risk; PNJ
  TTL anomaly_flags (~08-23); dt5g-live-2-writer A/B/C (bus question 07-29, vẫn PENDING).

