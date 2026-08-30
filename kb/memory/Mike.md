# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.

## Margin đơn mã discretionary — LIVE, chuỗi hôm nay đóng
- Per-name 5% / sleeve 10% NAV, f≤1.3, %ADV≤10%, exit -20%. Commit 022c48e7 (30/08).
- Phễu candidate LIVE: bin/discretionary_candidate_funnel.py + bin/marginability_check.py,
  commit 31825348. Wired vào fearbuy_weekly_scan.sh --mode weekly. Selfcheck hôm nay: 355 universe
  -> 113 fear cohort -> 14 FULLY_QUALIFIED (VSC/YEG/HDG/DTD/VGS/ITC/DRC/NTL/LCG/HT1/SHB/HPX/SKG/TPB).
  Marginability verify LIVE đúng (TV1/DGC not-marginable, MBB marginable khớp thật).
- **CHỜ USER QUYẾT**: TV1/DGC (case QUALIFY cũ) không lọt phễu vì PB hiện tại >1.0 (1.084/1.005).
  Giữ nguyên PB<1 (theo chỉ đạo gốc, chấp nhận bỏ sót case tương lai giống TV1/DGC) hay nới riêng
  ngưỡng PB cho phễu này (rủi ro thêm nhiễu)? Taylor không tự đổi, để đúng nguyên tắc.
- Insider cluster-buy: NO-GO — spread ÂM có ý nghĩa đúng subset dd52<=-20% (ngược giả thuyết,
  t=-3.6 đến -4.73, cả 4 định nghĩa). Không đầu tư writer/reader.
- #4 (backtest phễu full universe kể cả mã chết) để sau, cần data mã huỷ niêm yết riêng.

## §16 gate tốt-nghiệp — ĐÓNG
- Review tay APPROVED (30/08 12:52), giữ nguyên trạng mike 83c50fc4, WC e66b0256. 20 test tự chạy
  PASS hết, gate LIVE. Không cần dispatch thêm.

## Chuỗi R&D 30/08 khác — đóng
- custom30V accrual-quality: 3/3 phép thử NO-GO, đóng hẳn trục này.
- NPL/CAR: không nguồn free — giữ proxy ROE_Min3Y/Gordon-PB.
- Sector sweep: đóng hẳn, coverage đủ 20/20.
- C1 (DC-swap): củng cố REFUTED.

## Đang chờ / mở nhỏ
1. capit-lever selfcheck 2 FAIL (Wags/capit-lever-selfcheck-2-remaining-fail-permission-blocked):
   Urgency THẤP-TRUNG BÌNH, user chưa cho ý kiến.
2. Security leak VM: user đã tạo VM riêng, theo dõi tiến độ khi có cập nhật.
3. bus question retro-pattern-recurring-checker-hardcode-diagnosis-3 (Pattern A, lần 3 checker
   hardcode chẩn đoán) — chờ Mike/user quyết biện pháp mạnh hơn.
4. dt5g-writer-la-1931-ngoai-moi-cua-so-20260828 — chờ data-ops truy JOBS_BY_PROJECT.
5. job_cancel_guard_selfcheck FLAKY — theo dõi.

## Macro watch
- Bobby BĐS VN report xong 08-26 (STRUCTURAL_ACCUMULATION/AMBIGUOUS). Review quý next ~2026-11-26.

- [2026-08-30T06:10:06Z] 30/08 13:09 user duyệt: nới PB riêng cho phễu candidate NHƯNG phải adaptive theo chu kỳ thị trường (không phải ngưỡng tuyệt đối cố định) -> dispatch Taylor_20260830_060950 thiết kế PB-percentile PIT thay PB<1 tuyệt đối, tôn trọng ràng buộc 08-22 (breadth-tercile mặc định, Value Radar display-only không gate), backtest ngược 7 episode xem có bắt TV1/DGC-style không mà không phình universe. Design + test sơ bộ, chưa sửa code.
