# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy
  approve_margin_day.py TRƯỚC bot.
- KB weekly editorial review 2026-09-19 ĐÃ ĐÓNG (commit 8bd8ecd8 + bus decision/kb-weekly-editorial).

## Việc đang mở / cần theo dõi
1. **coord-2026-09-17 (Wags round 2)** vẫn hở — escalation tổng
   `retro-pattern-recurring-coord-09-17-arch-review-round2-2days` chờ user quyết build gate
   auto-escalate trong wags_autofix.sh. Rủi ro: zalopay-active-nav-excluded-ticker-dividend-
   receivable-option-c chưa xử lý, suppress đến ~09-25.
2. **universe-pit-migration G7/G8/G9** — escalated 09-18/19, ~8.4 tuần treo, chờ user chọn
   A (dispatch Taylor làm dứt điểm) hay B (đóng hẳn).
3. **selfcheck-red mới**: anomaly_gate_prod_parity_selfcheck.py — correctness PASS (0/60 diff),
   chỉ FAIL coverage-gate (không có ngày rỗng trong cửa sổ) — không phải regression, theo dõi.
4. 4 selfcheck-red khác của Wags (check_report_cadence/report_return_gate/production_manifest/
   wait_for_artifact) trong SLA, Wags đang xử.
5. Treasury buyback/corp_action mở rộng (Taylor branch feat/treasury-share-events-table) — chờ
   user duyệt chính thức, bảng BQ thật chưa tạo.
6. FiinPro/OShares harvest dừng 09-15 ở 4/59 lô — 2 bug vá chưa có selfcheck/commit xác nhận.
7. Code-quality Tầng 3 auto-dispatch wire vào code_quality_weekly.sh bước 7 (18/09) — theo dõi
   lần chạy tự động đầu tiên Chủ Nhật 2026-09-20 03:00 UTC.

## Còn mở không khẩn
- job_cancel_guard nhánh systemd luôn đỏ dưới cron (theo dõi, không escalate).
- append_event.sh JSON cách ly viết tay vẫn thỉnh thoảng tái diễn dạng nhỏ (theo dõi qua retro).

