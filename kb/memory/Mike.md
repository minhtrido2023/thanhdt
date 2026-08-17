# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật 2026-08-17T17:35Z (GDKHQ G5 fixed + live shadow PASS)

## Plan 08-18 — ĐÃ DUYỆT, cả 2 HOLD ALL (không đổi)
- approved_by ghi vào cả 2 file, 0 lệnh cả 2 account. TV1 đã đạt target.

## Đã đóng hôm nay 08-17 (đầy đủ)
- verify_account_snapshot legacy-majority guard → DONE (commit 0946c83d)
- BID ref price 35.800 vs 35.900 → CLOSED (lag_entry_anchor fix 08-15)
- book_breakdown_current SCL mislabel → FIXED (rule vào context_planning_mini.md)
- Order-book Pha 0 telemetry audit → VERIFIED (selfcheck PASS, data từ phiên đầu có lệnh ≥08-19)
- GDKHQ G5 root cause → FIXED (commit 1589fed1 + 49efb2ff):
    Root cause: shadow chạy sau 15:00, secdef đã lật sang phiên tiếp theo
    Fix: G6 gate mới (secdef.time ≥15:00 → INDETERMINATE), G2 band tol nới 1 tick trong D1-D3
    Live shadow 08-18 PASS (HHP/RAL/QNS/VGT × SpaceX+ZaloPay, 6/6 gates)
    acceptance_status = PENDING_ACCEPTANCE; gdkhq_rollout.enabled() = False

## Việc còn hở
1. **GDKHQ D1-D3: CHỜ USER ACCEPT** — shadow PASS, cần user gõ "accept GDKHQ" để enable
   VIX ex-date 08-20: chạy shadow TRONG PHIÊN (09:10-14:30 ICT), không sau 15:00
2. capit_lever_selfcheck K3 FAIL pre-existing (trước fix GDKHQ) — cần track riêng, thấp hơn
3. plan-dd-check-string fix (commit 9a9dbb1) — cần ngày có LAG/BAL entry
4. Order-book Pha 0 telemetry — chờ phiên thật có giao dịch ≥08-19

## Bối cảnh còn hiệu lực
- TV1 Rule A LIVE từ 08-15, an toàn, đã đạt target.
- CASH_VENDOR gate: giữ ĐÓNG. CAPIT margin: enabled=false.
- dispatch-prompt-heredoc skill cho prompt có backtick/code snippet.
- park_holdings.py stdout lẫn dòng "[dnse] kết nối OK" trước JSON → strip trước parse.

