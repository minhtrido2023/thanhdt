# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.

## Margin đơn mã discretionary — LIVE
- Per-name 5% / sleeve 10% NAV, f≤1.3, %ADV≤10%, exit -20%. Commit 022c48e7.
- Phễu candidate LIVE (PB<1 tuyệt đối hiện tại): bin/discretionary_candidate_funnel.py +
  bin/marginability_check.py, commit 31825348. 355 universe -> 113 fear cohort -> 14 FULLY_QUALIFIED.

## PB-adaptive threshold — 3 VÒNG QUANT-SKEPTIC, VÒNG 3 CONFIRMED, CHỜ USER QUYẾT WIRE
- V1 (job _060950): REFUTED — data-snoop 2 bậc (cơ sở percentile + cutoff/trần đều chọn sau khi
  biết TV1/DGC).
- V2 (job _075523): REFUTED nhưng hẹp hơn — cutoff 70% PASS (min-CV algorithm, độc lập thật),
  chỉ trần PB<1.5 (giữ nguyên từ V1) chưa kiểm định (dao động 38% khi quét thử).
- V3 (job _085015, verify quant-skeptic_20260830_085357): **CONFIRMED high**. Trần khoá bằng
  CÙNG min-CV mechanical rule = **1.2** (không phải 1.5). Kết quả cuối: 113->136 (+20.4%, 23 mã
  mới, hẹp hơn V2's 152/39). TV1(50.28%)/DGC(46.05%) vẫn lọt. Sector: CTCK=5, hoá chất=4 (cân
  bằng hơn V2's 8-vs-6). Recompute độc lập khớp tuyệt đối + leave-one-out robustness pass.
  Hạn chế công khai: N=7 episode mỏng, 5/7 đóng góp 0 vào min-CV pick.
- **CHỜ USER CHỐT**: (1) wire trần=1.2/cutoff=70% vào bin/discretionary_candidate_funnel.py thật
  (cần thêm: chạy quality floor/insider/marginability cho 23 mã mới trước — chưa làm; risk-auditor
  review lại cụm CTCK=5/hoá chất=4 thay điều kiện cũ cap≤1 CTCK), hay (2) giữ nguyên PB<1 tuyệt đối.
- Research 3 vòng: discretionary_funnel_adaptive_pb_20260830.md (V1, bài học data-snoop, giữ lại
  làm lịch sử) → discretionary_funnel_adaptive_pb_redo_20260830.md (V2) → round3 file mới (V3).
- Note vận hành: job quant-skeptic_20260830_085357 có bug bookkeeping (process chết sau khi ghi
  xong verdict CONFIRMED nhưng job record không tự cập nhật status=done, kẹt "running"/OVERDUE) —
  đã verify bằng đọc trực tiếp log file (well-formed, END_VERDICT, mtime khớp), không phải lỗi
  substance. Không sửa được record (bị classifier chặn ghi trạng thái force), không quan trọng.

## §16 gate tốt-nghiệp — ĐÓNG
- Review tay APPROVED (30/08 12:52), gate LIVE. Không cần dispatch thêm.

## Chuỗi R&D 30/08 khác — đóng
- custom30V accrual-quality: 3/3 phép thử NO-GO, đóng hẳn trục này.
- NPL/CAR: không nguồn free — giữ proxy ROE_Min3Y/Gordon-PB.
- Sector sweep: đóng hẳn, coverage đủ 20/20.
- C1 (DC-swap): củng cố REFUTED.
- Insider cluster-buy: NO-GO — spread ÂM có ý nghĩa đúng subset dd52<=-20%.

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

- [2026-08-30T09:21:16Z] 30/08 16:21 user duyệt hướng 1 (wire) -> dispatch Taylor_20260830_092103: bước 1 quality/insider/marginability 23 mã mới, bước 2 risk-auditor review lại cả 2 cụm CTCK+hoá chất, bước 3 sửa bin/discretionary_candidate_funnel.py CHỈ SAU bước 1+2 pass. Dừng nếu risk-auditor reject.
