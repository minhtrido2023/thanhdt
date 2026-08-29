# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.

## Chốt 29/08 tối — cả 2 việc XONG
- Margin đơn mã discretionary: per-name 5% NAV / sleeve 5% NAV / f hard-cap 1.3 / %ADV≤10% / exit -20%
  tự áp. LIVE — commit a19fc256. Code: bin/discretionary_margin_gate.py + selfcheck 21/21 PASS + cron
  15:20 ICT T2-T6. Không chạm plan.py/executor.py/trading_rules.json (arm = tay, checker read-only).
  Khoảng trống còn lại: forensic combined-margin account-level (capit lever + sleeve cùng gate
  dd52≤-20%) — bắt buộc trước khi xét lại sleeve 15%.
- Insider-sell shadow: duyệt tiếp tục (chấp nhận tần suất thật 7-9 mã/tháng), migrate snapshot table
  xong (commit 7f13e11d/3afec5bd), ngưỡng NGỪNG mới >9-10/tháng, review kế ~2026-09-29,
  quant-skeptic vẫn bắt buộc trước khi wire vào due-diligence report.

## Đang chờ / mở nhỏ
1. capit-lever selfcheck 2 FAIL (Wags/capit-lever-selfcheck-2-remaining-fail-permission-blocked):
   Urgency THẤP-TRUNG BÌNH, user chưa cho ý kiến.
2. Security leak VM: user đã tạo VM riêng, theo dõi tiến độ khi có cập nhật.
3. bus question retro-pattern-recurring-checker-hardcode-diagnosis-3 (Pattern A, lần 3 checker
   hardcode chẩn đoán) — chờ Mike/user quyết biện pháp mạnh hơn.
4. dt5g-writer-la-1931-ngoai-moi-cua-so-20260828 — writer LA ghi bảng DT5G production 19:31 ICT,
   dữ liệu không hỏng, chờ data-ops truy JOBS_BY_PROJECT.
5. job_cancel_guard_selfcheck FLAKY — theo dõi.

## Macro watch
- Bobby BĐS VN report xong 08-26 (STRUCTURAL_ACCUMULATION/AMBIGUOUS). Review quý next ~2026-11-26.

