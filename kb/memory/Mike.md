# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.

## Chốt cuối tuần 29-30/08 — 4 việc XONG
1. Margin đơn mã discretionary: per-name 5% NAV / sleeve 5% NAV / f hard-cap 1.3 / %ADV≤10% /
   exit -20% tự áp. LIVE — commit a19fc256. Khoảng trống: forensic combined-margin account-level
   (capit lever + sleeve cùng gate dd52≤-20%) bắt buộc trước khi xét lại sleeve 15%.
2. Insider-sell shadow: duyệt tiếp tục, migrate snapshot table xong (commit 7f13e11d/3afec5bd),
   ngưỡng NGỪNG mới >9-10/tháng, review kế ~2026-09-29.
3. C1 rolling windows: CỦNG CỐ REFUTED — 1 episode COVID 59 ngày = 90% tổng DC-LAG OOS, 2 episode
   gần nhất 2025 đều LAG thắng DC. Không đề xuất mở lại C1.
4. custom30V accrual-ratio gate (cash-flow-quality): TÍN HIỆU THẬT — double-sort trong nhóm EY rẻ
   nhất, tercile accrual tốt nhất fwd2M +9.14% vs xấu nhất +7.09%, +2.05pp/2m t=2.59 p=0.013 N=47Q.
   Đề xuất: GATE/tiebreak trong ey-only top-30 (không phải leg cộng vào composite — bài học eyrisk
   NO-GO). CHỜ USER DUYỆT full backtest IS/OOS+DSR/PBO+quant-skeptic trước khi wire custom_basket.py.
   Research: agents/Taylor/research/custom30v_cashflow_quality_selector_20260830.md.
   Phụ: bigquery_schema.md sai CF_OA_P0-P4 (ghi là ratio, thực RAW VND) — cần sửa doc.

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

