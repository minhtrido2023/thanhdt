# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-18T17:40Z (retro finalize, dọn cuối ngày)

## Retro 08-18 — XONG
3 sự cố hôm nay, tất cả cùng họ §28 (checker so tín hiệu tức thời thay vì sự thật bền): check#10
mtime, hàng đợi cách ly không đóng vòng đời, Wags coi dispatch exit=5 là fail thật. 2/3 cùng file
`ops_health_check.sh` — gợi ý cần audit toàn bộ checker con trong file đó, chưa làm.
Wags verify CONFIRMED. Entry: `kb/incidents/retro/retro-2026-08-18.md`, commit `5f25f2fc`.
Wakeup-miss về 0,0% (12/12) sau ngày tệ nhất 08-17 (27,3%) — chưa đủ xác nhận xu hướng, KHÔNG
mở lại escalation (theo Option B user chốt 08-17).

## Đang mở — chuyển sang ngày mai
1. **BLOCKER top5-postearnings-sleeve-backtest**: Anthropic 529 Overloaded (status.claude.com
   "Degraded performance", từ 08-18 16:20 UTC, Unresolved lúc kiểm cuối). 3 dispatch Taylor liên
   tiếp đều fail (155835/163629/170217, job cuối fail hẳn attempt 2/2 lúc 17:15Z). Dữ liệu +
   engine.py đã kéo an toàn tại `agents/Taylor/research/top5_postearnings_sleeve_20260818/`.
   Việc ngày mai: kiểm status.claude.com trước, retry dispatch Taylor nếu đã phục hồi.
2. GDKHQ dry-run D1-D3 chưa setup — theo dõi trước VIX 08-20 (còn 2 phiên).
3. plan-dd-check-string fix (commit 9a9dbb1) — cần ngày có LAG/BAL entry để verify.
4. Order-book Pha 0 telemetry (commit d6346efd) — chờ phiên thật có giao dịch.
5. Push commit 0550e5d3 (cron_registry worktree, dịch giờ cron paper-reporting) — bị auto-mode
   block, cần user allow git push.
6. Đề xuất chưa quyết: audit toàn bộ checker con `ops_health_check.sh` theo khuôn §28 + cân nhắc
   1 selfcheck lint chung quét mẫu mtime-as-recency/exit-code-binary trong `bin/*.sh` (từ retro
   08-18, chưa ai giao việc này).

## Plan 08-19 (đã sinh, cần duyệt trước 08:45 ICT)
SpaceX + ZaloPay: HOLD ALL, 0 lệnh, approved_by=None.

## Bối cảnh còn hiệu lực
- yield_floor Option C WIRED (commits 9ed56854/a6ea3f06/133d9854), display-only, review milestone
  2027-02-10, forcing function `paper_checkpoint_escalation.sh`.
- cron paper-reporting đã dịch giờ (dc_book_waterfall→00:15, daily_report→07:30,
  checkpoint_escalation→07:40 ICT) — xem việc mở #5 (chưa push).
- TV1 Rule A LIVE từ 08-15, an toàn. CASH_VENDOR gate: ĐÓNG. CAPIT margin: enabled=false.
- park_holdings.py stdout lẫn dòng "[dnse] kết nối OK" trước JSON — cần tail -n +2 khi parse.
- dispatch-prompt-heredoc skill cho prompt có backtick.

- [2026-08-18T17:41:51Z] BLOCKER top5-postearnings-sleeve-backtest: kiểm tra 17:41 UTC (~1h20 sau lúc bắt đầu) — status.claude.com VẪN Unresolved, update mới nhất nói đang điều tra lỗi tăng cao trên Opus 5 cụ thể. Backoff cycle #1/3 (1800s) đã dùng, đang chờ cycle #2. Chưa retry dispatch.
- [2026-08-18T18:13:09Z] BLOCKER top5-postearnings-sleeve-backtest: kiểm tra 18:12 UTC (~1h52 sau khi bắt đầu) — status.claude.com VẪN Unresolved/Investigating. Backoff cycle #2/3 dùng xong, đang chờ cycle #3 (trần theo chỉ đạo trước) — nếu vẫn chưa fix ở lần tỉnh kế tiếp PHẢI hỏi user thay vì tự lặp cycle #4.
- [2026-08-18T18:45:37Z] BLOCKER top5-postearnings-sleeve-backtest RESOLVED (outage side): Anthropic status chuyển Monitoring ~18:44 UTC, retry lần 4 (job Taylor_20260818_184457) chạy bình thường qua vòng đầu, không gãy 529. Đang chờ kết quả backtest thật.
- [2026-08-18T18:56:21Z] top5-postearnings-sleeve-backtest XONG: NO-GO (job Taylor_20260818_184457, retry lần 4 sau outage Anthropic). 4/5 tiêu chí GO trượt, edge tập trung 2020-21, chết OOS 2022+, DSR/robust 5-vs-N_top đều fail. Lead chưa kết luận: value-vs-ngành trong DT5G BEAR (excSEC t=2,64 n=9, cần prereg riêng). Đã dispatch quant-skeptic verify (bg), chờ verdict.
