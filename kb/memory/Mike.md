# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Plan 08-18 — ĐÃ DUYỆT, cả 2 HOLD ALL (không đổi)
- approved_by ghi vào cả 2 file, 0 lệnh cả 2 account. TV1 đã đạt target.

## Đã đóng hôm nay 08-17
- verify_account_snapshot legacy-majority guard → DONE (commit 0946c83d, Taylor).
- BID ref price 35.800 vs 35.900 → CLOSED: lag_entry_anchor đã fix từ 08-15 (job Taylor_20260815_054822), không còn đọc ticker.Price thô làm trần.
- GDKHQ price-frame pipeline: vẫn shadow rollout, chưa fully live (ghi chú từ Taylor).

## Việc còn hở (ưu tiên giảm dần)
1. **GDKHQ dry-run D1-D3 chưa setup** — cần quyết trước VIX 08-20 (còn 3 phiên). KHẨN.
2. book_breakdown_current trong plan_SpaceX_2026-08-17.json ghi nhãn SCL sai (cosmetic, không đổi lệnh).
3. plan-dd-check-string fix (commit 9a9dbb1) — cần ngày có LAG/BAL entry mới để verify code path.
4. Order-book Pha 0 telemetry (commit d6346efd) — chờ phiên thật có giao dịch.

## Bối cảnh còn hiệu lực
- TV1 Rule A LIVE từ 08-15, an toàn, đã đạt target.
- CASH_VENDOR gate: giữ ĐÓNG. CAPIT margin: enabled=false.
- dispatch-prompt-heredoc skill cho prompt có backtick/code snippet.

