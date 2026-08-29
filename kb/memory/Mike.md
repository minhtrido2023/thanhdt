# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.

## Chốt 29/08 tối — 4 việc XONG
- Margin đơn mã discretionary: per-name 5% NAV / sleeve 5% NAV / f hard-cap 1.3 / %ADV≤10% / exit -20%
  tự áp. LIVE — commit a19fc256. Khoảng trống còn lại: forensic combined-margin account-level (capit
  lever + sleeve cùng gate dd52≤-20%) — bắt buộc trước khi xét lại sleeve 15%.
- Insider-sell shadow: duyệt tiếp tục (7-9 mã/tháng), migrate snapshot xong. Review kế ~2026-09-29.
- C1 rolling IS/OOS windows (Taylor_20260829_173433): CỦNG CỐ REFUTED, không mở lại C1. 1 episode
  COVID 2020 = 90% tổng DC-LAG OOS, 6 episode khác triệt tiêu nhau. Đóng hẳn nhánh này.
- custom30V cash-flow-quality selector roadmap (Taylor_20260829_173455): done, xem
  discord_thread_id 1521735922066919515 cho chi tiết — chưa đọc kỹ kết quả, cần Mike review lượt tới.
- Retro 2026-08-29 finalize xong: 6 sự cố (SIGPIPE dispatch >64KB, bq CLI lỗi ra stdout tái diễn
  lần 4, 4 selfcheck-FP khác nguyên nhân cùng 1 lần weekly audit). Wags verify GAPS FOUND 2 major
  (bus question hardcode-chẩn-đoán thực đã đóng 08-28 chứ không còn mở; nguồn 6 sự cố là Mike tự
  chạy chứ không phải job Taylor) — đã sửa trong kb/incidents/retro/retro-2026-08-29.md, commit
  cad0fa58. Pattern A (đọc nhầm kênh bằng chứng §29) nay ĐÃ ĐÓNG, không còn treo.

## Đang chờ / mở nhỏ
1. capit-lever selfcheck 2 FAIL (Wags/capit-lever-selfcheck-2-remaining-fail-permission-blocked):
   Urgency THẤP-TRUNG BÌNH, user chưa cho ý kiến.
2. Security leak VM: user đã tạo VM riêng, theo dõi tiến độ khi có cập nhật.
3. dt5g-writer-la-1931-ngoai-moi-cua-so-20260828 — writer LA ghi bảng DT5G production 19:31 ICT,
   dữ liệu không hỏng, chờ data-ops truy JOBS_BY_PROJECT.
4. job_cancel_guard_selfcheck FLAKY — theo dõi.
5. Wags/wags-fix-not-confirmed: coord-2026-08-29 (round-3 diagnosis_evidence_gate +
   ops_health_check owner-hint) — chờ arch-reviewer round tiếp theo.

## Macro watch
- Bobby BĐS VN report xong 08-26 (STRUCTURAL_ACCUMULATION/AMBIGUOUS). Review quý next ~2026-11-26.

## Lịch — phiên kế tiếp
- HOSE đóng cửa cuối tuần, phiên kế tiếp Thứ Năm 03/09 09:00 ICT (nghỉ bù Quốc khánh 31/08+01/09).

