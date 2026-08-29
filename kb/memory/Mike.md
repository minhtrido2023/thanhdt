# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.
- Thứ Bảy 2026-08-29: implement code chính sách margin đơn mã discretionary (chưa bắt đầu).

## Đóng đêm qua (2026-08-28→29, weekly ops audit)
- ops_health_check owner-hint: round 3 CONFIRMED (commit 0557e643) — 8/8 mutation đối kháng bị giết,
  tái lập hành vi lỗi trước-fix, quét 214 câu hỏi xác nhận cả 2 bug round-2 chưa từng bắn ở
  production. Cả 2 bus question liên quan đã đóng. XONG HẲN, không còn round nào mở.
- diagnosis_evidence_gate round 2: CONFIRMED (commit 68675ba7 + vá 9efac948 PASS-giả do
  MIKE_DIAG_GATE_TARGET rò rỉ). XONG.
- 3 follow-up nhỏ cố ý chưa làm (không khẩn): OPS_HEALTH_CHECK_SRC thiếu guard chống PASS-giả
  (khác diagnosis_evidence_gate đã có); --mutations của 2 selfcheck chưa gắn lịch chạy định kỳ
  (kb_nightly.sh chỉ chạy suite thường); topic "-needs-approval" sinh WARN nhẹ chưa đủ đáng sửa.

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

- [2026-08-29T15:41:05Z] 29/08 tối: #2 insider-shadow review XONG — verdict NGỪNG (2/3 FAIL: volume 7-9 mã/tháng > ngưỡng 5, selftest FAIL do insider_flags.py đọc bảng live mutable thay vì insider_transaction_snapshots; điều kiện xét lại đã ghi bus insider-shadow-review-20260829, chờ user quyết đầu tư tiếp hay đóng). #1 ĐANG CHẠY: Taylor_20260829_154054 (effort high, timeout 2400s) — nghiên cứu tham số margin đơn mã: sleeve 5/10/15% NAV (user nghiêng 15%), per-name 3% vs 5%, exit -20% giữ; 5 trục: risk math correlated, capacity ADV, tương tác capit_margin_lever, stress 2022-11, mâu thuẫn mandate Loại-2 ≤5%. Sau Taylor → risk-auditor phản biện → user chốt → mới code.
- [2026-08-29T15:55:20Z] 29/08 ~23:00: #1 research+phản biện XONG, ĐANG CHỜ USER CHỐT: đề xuất per-name 3->5% CONDITIONAL-APPROVE (6 điều kiện: cơ sở EXPOSURE thống nhất 2 tài liệu + sửa lỗi A5 Loại-2 thiếu 30% loss, hard-cap f=1.3, thêm %ADV per-name <=10% ADV-3m, max-loss công bố ~1.5% NAV mã mỏng, Mafee verify marginability, re-sync Loại-2); sleeve 15% REJECT thời điểm này (không bind - chỉ 2 case, mở lại khi >=3 case marginable + forensic combined-margin + Loại-2 re-sync). Risk-auditor tìm 3 gap Taylor: bỏ lãi margin+slippage (max loss 15% thật ~4-5% NAV), 33.4% là lower bound, Trứng vàng ~10% NAV có thể không phải collateral. User chốt xong mới: sửa 2 policy file + code + forensic job.
- [2026-08-29T16:04:43Z] 29/08 23:05 user chốt: #1 per-name 3->5% NAV (sleeve GIỮ 5%, 6 điều kiện conditional-approve) -> Taylor_20260829_160408 implement (policy sync + code gate/checker); #2 insider duyệt đầu tư tiếp (chấp nhận 7-9 mã/tháng) -> Taylor_20260829_160426 migrate snapshot + fixture + selftest, ngưỡng NGỪNG mới >9-10/tháng, review ~09-29. User hiểu đúng cơ chế: per-name 5% = 1 mã ăn trọn sleeve hoặc nhiều mã chia (đã confirm, %ADV co mã mỏng khi NAV tăng).
- [2026-08-29T16:12:15Z] 29/08 23:12: #2 insider migration XONG (commit 7f13e11d/3afec5bd/16e9ddaf), snapshot table wired cả insider_flags.py + due_diligence.py, selftest+27/27 PASS. #1 margin policy implement (Taylor_20260829_160408) vẫn đang chạy.
