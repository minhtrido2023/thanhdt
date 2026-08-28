# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.
- Thứ Bảy 2026-08-29: implement code chính sách margin đơn mã discretionary.

## Retro 2026-08-28 — đã đóng (kb/incidents/retro/retro-2026-08-28.md, Wags CONFIRMED)
- 4 sự cố: #1 append_event JSON guard hardcode (FIXED, commit 55b3f34c); #2 DT5G MERGE bỏ sót
  asof_date NULL 26 phiên (FIXED, commit 4bc6d2f4 repo WorkingClaude + user duyệt UPDATE dòng
  SEALED 07-24, verify n_null=0); #3 MBB rights-issue ledger gap (FIXED, journal bổ sung, hết
  BLOCKED_RECONCILE); #4 Wags fix cho routing câu hỏi -needs-taylor bị arch-reviewer NEEDS_CHANGES
  (CÒN HỞ — chưa round 2).
- **Pattern A escalate mở**: bus question `retro-pattern-recurring-checker-hardcode-diagnosis-3`
  (lần 3 checker hardcode chẩn đoán thay vì đọc bằng chứng) — chờ Mike/user quyết biện pháp mạnh
  hơn (lint rule/review checklist), KHÔNG chỉ thêm dòng khuyến nghị.
- **Theo dõi tiếp**: nếu sang 08-29 vẫn chưa có round-2 fix cho
  `Wags/wags-fix-not-confirmed: coord-2026-08-28` → escalate Pattern B ở retro kế tiếp.

## Đang chờ / mở nhỏ
1. **capit-lever selfcheck 2 FAIL còn lại** (bus: Wags/capit-lever-selfcheck-2-remaining-fail-permission-blocked): L2/L3 bị chặn permission classifier; Taylor đề xuất patch cụ thể. Urgency=THẤP-TRUNG BÌNH. User chưa cho ý kiến.
2. **Security leak VM**: user báo tạo máy ảo riêng trong server thay cho repo private/sudo revoke. Bus đóng DEFERRED. Theo dõi tiến độ VM khi có cập nhật.
3. **wags-fix-not-confirmed: coord-2026-08-28** — Wags round 1 NEEDS_CHANGES (arch-reviewer), chưa round 2. Xem Pattern B ở trên.

## Macro watch
- Bobby BĐS VN report xong 08-26 (STRUCTURAL_ACCUMULATION/AMBIGUOUS). Review quý next ~2026-11-26.

- [2026-08-28T18:07:12Z] Retro Pattern B (wags-fix-not-confirmed coord-2026-08-28): round 2 xong (Taylor, commit 7a2328c7, 3/3 required_changes round 1 verify đúng bằng mutation test), nhưng arch-reviewer round 2 lại NEEDS_CHANGES vì bug MỚI lộ ra khi mở rộng >48h coverage (triaged-needs-human convention không được nhận diện, thiếu _acked() filter ở nhánh aged). Bus question 'ops-health-check-owner-hint-round3-continue' đang chờ user chọn A (làm round 3 ngay) hay B (dừng). Rủi ro thấp (WARN-only, không auto-dispatch).
