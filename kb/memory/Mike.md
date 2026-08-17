# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật 2026-08-17T17:48Z (GDKHQ D1-D3 ENABLED)

## Plan 08-18 — ĐÃ DUYỆT, cả 2 HOLD ALL (không đổi)

## Đã đóng hôm nay 08-17
- verify_account_snapshot legacy-majority guard → DONE (commit 0946c83d)
- BID ref price 35.800 vs 35.900 → CLOSED
- book_breakdown_current SCL mislabel → FIXED (context_planning_mini.md)
- Order-book Pha 0 telemetry audit → VERIFIED (selfcheck PASS)
- GDKHQ G5 root cause → FIXED + ACCEPTED (commits 1589fed1 + 49efb2ff)
  enabled() = True, accepted_at = 2026-08-17T17:47Z by user

## Việc còn hở
1. **question-checker round-2 cần MERGE vào master** (branch session/1522519012066721923-coord-20260817, commit 4435b3e0) — ops_health_check.sh production vẫn bản cũ NEEDS_CHANGES
2. **Pattern B wakeup-miss** — escalation mở (topic wakeup-miss-recurring-post-push-2026-08-17), chờ user chọn A/B/C.
3. **VIX ex-date 08-20**: chạy shadow TRONG PHIÊN (09:10-14:30 ICT), sau đó shadow có thể cần confirm tiếp (hoặc auto-accept nếu PASS sạch)
4. capit_lever_selfcheck K3 FAIL pre-existing — ưu tiên thấp
5. plan-dd-check-string fix (commit 9a9dbb1) — cần ngày có LAG/BAL entry
6. Order-book Pha 0 telemetry — chờ phiên có giao dịch ≥08-19

## Bối cảnh còn hiệu lực
- TV1 Rule A LIVE từ 08-15, an toàn.
- CASH_VENDOR gate: giữ ĐÓNG. CAPIT margin: enabled=false.
- dispatch-prompt-heredoc skill cho prompt có backtick/code snippet.

