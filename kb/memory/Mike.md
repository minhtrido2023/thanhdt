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
- [2026-08-30T03:16:33Z] 30/08 10:16: #2 NPL/CAR feasibility XONG — dispatch của tôi dựa info lỗi thời, bank_lens_v3 đã tự fix cùng ngày 08-28 sau (vnstock migrate + OCR 9/18 bank NPL 1 quý). Kết luận: không nguồn free/scriptable cho CAR/CASA lịch sử; NPL chỉ live cross-section 9/18 bank, không backtest-usable. Khuyến nghị GIỮ proxy ROE_Min3Y/Gordon-PB. Muốn lịch sử thật -> quyết định ngân sách FiinGroup/VietstockXLS, cần user duyệt. #1 forensic combined-margin (Taylor_20260830_031004) vẫn đang chạy.
- [2026-08-30T03:18:54Z] 30/08 10:18: #1 forensic combined-margin XONG — margin ratio KHÔNG phải rào cản thật kể cả sleeve 15% (buffer ~3x loss-discipline cap, combined debt 27.05% NAV, equity ratio 75.36% tại arm 15%, cách maintenance +35.36pp). Nếu giữ 5% phải dựa correlation-risk không phải margin-math. Open item không chặn: T+2 lag chưa verify, capit_margin_lever tự nó có envelope rò 2.6x (vấn đề cũ khác). #1+#2 XONG cả hai. Dispatch #4 (Taylor_20260830_031818, accrual tiebreak) + #5 (Taylor_20260830_031841, accrual sector-neutral) song song. #6 sector sweep chờ #4/#5 xong.
- [2026-08-30T03:23:55Z] 30/08 10:24: #5 sector-neutral accrual XONG — GO cho full backtest cycle (double-sort +2.69pp/2m t=3.17 vs pooled +2.20pp t=2.35, LOO robust). CẢNH BÁO: panel mới không tái lập khớp bản gốc (IC EY 0.0316 t1.88 vs gốc 0.0697 t4.78, cùng dấu khác biên độ) — PHẢI đối soát trước khi tin số tiếp theo. Bắt buộc quant-skeptic trước khi wire. #4 accrual tiebreak (Taylor_20260830_031818) vẫn đang chạy.
