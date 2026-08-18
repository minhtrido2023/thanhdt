# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-18T14:15Z

## Hôm nay 08-18 — XONG

### yield_floor Option C — WIRED (commits 9ed56854 + a6ea3f06 + 133d9854)
- `custom30_yield_labels.py` (mới) + `custom30_history.py`: thêm 2 cột `yield_floor_note` +
  `is_stable_payer` vào `custom30v_8l` — thuần observational, selection logic UNCHANGED (A/B verify).
- Nhãn có trong bảng thật từ cron 15:30 ICT hôm nay trở đi.
- Review milestone: **2027-02-10** (sau 2 kỳ rebalance 11-05 + 02-05).
- Forcing function: `paper_checkpoint_escalation.sh` tự escalate 2027-02-06 nếu gate còn pending.

### cron paper-reporting — DỊCH (commit 0550e5d3 worktree, crontab đã đổi)
- dc_book_waterfall: 15:05 → 00:15 ICT (sau BQ sync 23:45)
- paper_programs_daily_report: 16:00 → 07:30 ICT sáng hôm sau
- paper_checkpoint_escalation: 16:10 → 07:40 ICT sáng hôm sau
- ⚠️ Commit worktree chưa push (git push bị auto-mode block lần trước)

## Plan 08-19 — cần duyệt trước 08:45 ICT
- SpaceX + ZaloPay: HOLD ALL, 0 lệnh, approved_by=None

## Việc còn hở (ưu tiên giảm dần)
1. GDKHQ dry-run D1-D3 chưa setup — theo dõi trước VIX 08-20 (còn 2 phiên).
2. plan-dd-check-string fix (commit 9a9dbb1) — cần ngày có LAG/BAL entry để verify.
3. Order-book Pha 0 telemetry (commit d6346efd) — chờ phiên thật có giao dịch.
4. Push commit 0550e5d3 (cron_registry worktree) — bị block, cần user allow git push.

## Bối cảnh còn hiệu lực
- TV1 Rule A LIVE từ 08-15, an toàn. CASH_VENDOR gate: ĐÓNG.
- CAPIT margin: enabled=false. dispatch-prompt-heredoc skill cho prompt có backtick.
- park_holdings.py stdout lẫn dòng "[dnse] kết nối OK" trước JSON — cần tail -n +2 khi parse.
- yield_floor: H2 CONFIRMED (downside protection), H1 REFUTED. Option C deployed. B sau 2027-02.

- [2026-08-18T17:10:36Z] BLOCKER 08-18 17:15Z: dispatch Taylor cho top5-postearnings-sleeve-backtest bị chặn bởi sự cố Anthropic thật (status.claude.com: 'Degraded performance for multiple models', từ 16:20 UTC, Unresolved). 6/6 attempt liên tiếp (3 dispatch: Taylor_20260818_155835/163629/170217) đều 529 Overloaded. Dữ liệu+engine.py đã kéo an toàn tại agents/Taylor/research/top5_postearnings_sleeve_20260818/. Đang backoff dài (~30min/lần) trước khi retry lần 4, kiểm tra status page mỗi lần tỉnh. KHÔNG phải bug của mình.
