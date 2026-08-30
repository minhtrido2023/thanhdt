# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.

## Chốt cuối tuần 29-30/08 — 5 việc XONG
1. Margin đơn mã discretionary: per-name 5% NAV / sleeve 5% NAV / f hard-cap 1.3 / %ADV≤10% /
   exit -20% tự áp. LIVE — commit a19fc256. Khoảng trống: forensic combined-margin account-level
   (capit lever + sleeve cùng gate dd52≤-20%) bắt buộc trước khi xét lại sleeve 15%.
2. Insider-sell shadow: duyệt tiếp tục, migrate snapshot table xong (commit 7f13e11d/3afec5bd),
   ngưỡng NGỪNG mới >9-10/tháng, review kế ~2026-09-29.
3. C1 rolling windows: CỦNG CỐ REFUTED — 1 episode COVID 59 ngày = 90% tổng DC-LAG OOS. Không mở lại.
4→5. custom30V accrual-quality gate: preliminary IC test (p=0.013) → user duyệt full backtest →
   **NO-GO, quant-skeptic CONFIRMED high**. Pre-registered agate33: IS -0.08pp, OOS -0.13pp (cả 2
   XẤU đi), DSR 0.52 (gần coin-flip), PBO 0.607. Cùng nhóm lỗi eyrisk NO-GO cũ (proxy IC dương chết
   khi vào full production pipeline + TC thật). custom_basket.py KHÔNG đụng, đã đưa vào BỊ LOẠI.
   Bug phụ tìm thấy lúc verify (dropna() accrual history, ~11.2% ticker-quý lỗ) đã fix, kết quả
   byte-identical. Đóng hẳn hướng này. Fix kèm: bigquery_schema.md CF_OA_P0-P4 doc.

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

- [2026-08-30T03:10:38Z] 30/08 10:10 user duyệt thứ tự: #1 (Taylor_20260830_031004, forensic combined-margin account-level) + #2 (Taylor_20260830_031023, NPL/CAR data source feasibility) dispatch song song TRƯỚC. SAU KHI CẢ 2 XONG -> dispatch #4 (accrual tiebreak variant) + #5 (accrual sector-neutral) + #6 (sector sweep #10).
