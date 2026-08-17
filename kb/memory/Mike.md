# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật 2026-08-17T17:45Z (retro 08-17 finalize xong)

## Plan 08-18 — ĐÃ DUYỆT, cả 2 HOLD ALL (không đổi)
- approved_by ghi vào cả 2 file, 0 lệnh cả 2 account. TV1 đã đạt target.

## Retro 08-17 — ĐÃ XONG (4 sự cố, 2 pattern), entry: kb/incidents/retro/retro-2026-08-17.md
- Wags verify: GAPS FOUND → đã sửa (sự cố #2 "HOÀN CHỈNH"→"HỞ" vì round-2 fix 4435b3e0
  CHƯA merge vào master; ops_health_check.sh production vẫn bản NEEDS_CHANGES)
- Pattern B (wakeup-miss) escalate lại: topic wakeup-miss-recurring-post-push-2026-08-17
  (đã mở ở bước 1, KHÔNG mở trùng) — 27,3% miss, cao nhất từng đo, mâu thuẫn giả thuyết
  "push đã ổn định hoá" của 08-16. Chờ user quyết hướng A/B/C.

## Việc còn hở
1. **GDKHQ D1-D3: CHỜ USER ACCEPT** — shadow PASS, cần user gõ "accept GDKHQ" để enable.
   VIX ex-date 08-20: chạy shadow TRONG PHIÊN (09:10-14:30 ICT), không sau 15:00.
2. **question-checker round-2 (schedule-aware grace, commit 4435b3e0) cần MERGE vào master**
   — hiện chỉ nằm trên branch session/1522519012066721923-coord-20260817. Việc thuần túy
   merge, không phải quyết định user.
3. **Pattern B wakeup-miss** — escalation mở, chờ user chọn A (cưỡng chế cơ chế)/B (chấp
   nhận baseline)/C (tiếp tục đo — không khuyến nghị).
4. capit_lever_selfcheck K3 FAIL pre-existing (trước fix GDKHQ) — track riêng, ưu tiên thấp.
5. plan-dd-check-string fix (commit 9a9dbb1) — cần ngày có LAG/BAL entry để verify sống.
6. Order-book Pha 0 telemetry — chờ phiên thật có giao dịch ≥08-19.
7. `lag_entry_anchor.py:105` vẫn chưa vá bẫy ticker.Price đông cứng ex-date (đã vá riêng ở
   update_shares_live.py 08-17, nhưng đây là nạn nhân khác cùng bẫy).

## Bối cảnh còn hiệu lực
- TV1 Rule A LIVE từ 08-15, an toàn, đã đạt target.
- CASH_VENDOR gate: giữ ĐÓNG. CAPIT margin: enabled=false.
- dispatch-prompt-heredoc skill cho prompt có backtick/code snippet.
- park_holdings.py stdout lẫn dòng "[dnse] kết nối OK" trước JSON → strip trước parse.

