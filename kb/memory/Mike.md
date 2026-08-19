# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
1. **plan-dd-check-string fix** (commit 9a9dbb1) — cần ngày có LAG/BAL entry để verify.
2. **Order-book Pha 0 telemetry** (commit d6346efd) — chờ phiên thật có giao dịch.
3. **Push worktree branch** `session/1521113190405247057-orderbook` — bị auto-mode block.
   Commit đang chờ:
   - `0550e5d3`: cron_registry timing update (dc_book_waterfall→00:15, daily_report→07:30)
   - `1f893f1d`: MIKE.md OKF split (43KB→37KB, tạo MIKE_ext.md)
   User merge thủ công: `git merge session/1521113190405247057-orderbook` tại mike root.
4. **Đề xuất chưa quyết**: audit toàn bộ checker con `ops_health_check.sh` theo khuôn §28 +
   cân nhắc lint chung quét mẫu mtime-as-recency trong `bin/*.sh` (từ retro 08-18).

## Bối cảnh còn hiệu lực
- **GDKHQ D1-D3 LIVE (đã đóng)**: rollout ENABLED từ 08-17, accepted sau shadow 08-18 PASS
  (HHP/QNS/RAL/VGT, 6/6 gates). VIX 08-20 sẽ được xử lý tự động bởi bot live sáng mai.
- yield_floor Option C WIRED (commits 9ed56854/a6ea3f06/133d9854), review 2027-02-10.
- TV1 Rule A LIVE từ 08-15, an toàn. CASH_VENDOR gate: ĐÓNG.
- OKF split mandate: file vượt 40KB → tự split theo pattern MIKE_ext.md/coding_guidelines_ext.md.
- dispatch-prompt-heredoc skill cho prompt có backtick.

