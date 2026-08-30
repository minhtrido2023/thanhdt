# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.

## Chốt 30/08 — chuỗi 6 việc XONG
1. Forensic combined-margin: margin ratio KHÔNG chặn sleeve kể cả 15% (buffer ~3x loss-discipline,
   combined debt 27.05% NAV, equity ratio 75.36% tại arm, cách maintenance +35.36pp). Nếu giữ 5%
   phải dựa correlation-risk, không phải margin-math. Open item không chặn: T+2 lag chưa verify.
2. NPL/CAR feasibility: không nguồn free/scriptable cho lịch sử CAR/CASA. Giữ proxy ROE_Min3Y/
   Gordon-PB. Muốn lịch sử thật -> quyết định ngân sách FiinGroup/VietstockXLS (cần user duyệt).
3-4-5. custom30V accrual: GATE pooled NO-GO (08-30 sáng) -> TIEBREAK NO-GO (IS -0.07/OOS -0.85pp,
   tổng quát hoá tiebreak-within-band không giúp selector family) -> SECTOR-NEUTRAL GO cho full
   backtest (+2.69pp t=3.17 double-sort) NHƯNG có panel reconciliation gap CHƯA giải quyết
   (IC EY mới 0.0316 t1.88 vs gốc 0.0697 t4.78) — PHẢI đối soát + quant-skeptic trước bước tiếp.
   Việc còn mở duy nhất của chuỗi này.
6. Sector sweep: ĐÓNG hẳn, coverage đủ (20/20 sector, LENS not BOOK). Tracker đã sửa lỗi thời.
- Cần nhớ: 2 lần dispatch dựa info lỗi thời (NPL/CAR, sector sweep #10) — cơ chế verify-artifact
  của agent tự phát hiện + sửa đúng cả 2 lần. Cũng gặp 1 lần job status="done" nhưng backtest nền
  chưa xong thật (#4 accrual tiebreak) — đã verify artifact trước khi tin, xử lý đúng quy trình.

## Đang chờ / mở nhỏ
1. capit-lever selfcheck 2 FAIL (Wags/capit-lever-selfcheck-2-remaining-fail-permission-blocked):
   Urgency THẤP-TRUNG BÌNH, user chưa cho ý kiến.
2. Security leak VM: user đã tạo VM riêng, theo dõi tiến độ khi có cập nhật.
3. bus question retro-pattern-recurring-checker-hardcode-diagnosis-3 (Pattern A, lần 3 checker
   hardcode chẩn đoán) — chờ Mike/user quyết biện pháp mạnh hơn.
4. dt5g-writer-la-1931-ngoai-moi-cua-so-20260828 — writer LA ghi bảng DT5G production 19:31 ICT,
   dữ liệu không hỏng, chờ data-ops truy JOBS_BY_PROJECT.
5. job_cancel_guard_selfcheck FLAKY — theo dõi.
6. §16 gate tốt-nghiệp — dispatch Wags_20260830_033008 (opus/high) đang chạy: lint chặn
   datetime.now() trần vào pre-commit + ratchet + baseline audit 2 repo + arch-reviewer. Chưa xong.

## Macro watch
- Bobby BĐS VN report xong 08-26 (STRUCTURAL_ACCUMULATION/AMBIGUOUS). Review quý next ~2026-11-26.

- [2026-08-30T03:58:49Z] 30/08 10:58 user duyệt 2 hướng: A (Taylor_20260830_035805) định lượng correlation-risk thật cho sleeve 5%/10%/15%, sau đó risk-auditor phản biện; B (Taylor_20260830_035832) accrual sector-neutral - bước 1 đối soát panel gap BẮT BUỘC trước, bước 2 full backtest cycle. Cả 2 bắt buộc quant-skeptic trước wire. Song song, đang chạy.
