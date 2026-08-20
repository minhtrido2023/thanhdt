# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
1. **ERROR telemetry: 20 trong order-book shadow** — Taylor điều tra (job Taylor_20260820_012218, dispatched 2026-08-20 01:22 ICT). Rà file orderbook_shadow_*.jsonl, fix + ghi registry `attention_notes`.
2. **plan-dd-check-string fix** (commit 9a9dbb1) — cần ngày có LAG/BAL entry để verify (đã trong master WC, chờ phiên trading thật có deal).
3. **Order-book Pha 0 telemetry** (commit d6346efd, trong WC main) — chờ phiên thật tích lũy thêm data. Hôm nay N=39 opportunities, valid=19 — đang chạy đúng.
4. **Đề xuất chưa quyết**: audit toàn bộ checker con `ops_health_check.sh` theo khuôn §28 + lint mtime-as-recency.

## Đã đóng (trước đây trong working memory, nay đã xong)
- Worktree branch session/1521113190405247057-orderbook: đã merge master (branch rỗng vs master), working memory cũ stale.
- Paper report 2026-08-20: DELIVERED (Discord + email, 2026-08-20 01:22 ICT).

## Bối cảnh còn hiệu lực
- **GDKHQ D1-D3 LIVE**: rollout ENABLED từ 08-17, accepted sau shadow 08-18 PASS.
- yield_floor Option C WIRED (commits 9ed56854/a6ea3f06/133d9854), review 2027-02-10.
- TV1 Rule A LIVE từ 08-15, an toàn. CASH_VENDOR gate: ĐÓNG.
- OKF split mandate: file vượt 40KB → tự split theo pattern MIKE_ext.md/coding_guidelines_ext.md.
- dispatch-prompt-heredoc skill cho prompt có backtick.
- P2 expvol_pacing: shadow log-only trên LIVE từ 08-17, review 2026-09-15.
- BAL signal shadow-track: bắt đầu theo dõi (case VPI), review 2026-09-16.

