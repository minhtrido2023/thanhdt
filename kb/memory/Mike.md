# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
1. **plan-dd-check-string fix** (commit 9a9dbb1) — cần ngày có LAG/BAL entry để verify (đã trong master WC, chờ phiên trading thật có deal).
2. **Order-book Pha 0 telemetry** (commit d6346efd, trong WC main) — tích lũy bình thường. N=39 obs / 3 phiên, từ 08-19 valid=19/19. ERROR telemetry cũ (20 record) đã giải thích và đóng (Taylor_20260820_012218).
3. **Todo nhỏ (không urgent)**: 6 selfcheck teardown chưa glob `orderbook_shadow_*` → rác disk, không ảnh hưởng số liệu. Ghi nhận, chưa patch.
4. **Đề xuất chưa quyết**: audit toàn bộ checker con `ops_health_check.sh` theo khuôn §28 + lint mtime-as-recency.

## Bối cảnh còn hiệu lực
- **GDKHQ D1-D3 LIVE**: rollout ENABLED từ 08-17, accepted sau shadow 08-18 PASS.
- yield_floor Option C WIRED (commits 9ed56854/a6ea3f06/133d9854), review 2027-02-10.
- TV1 Rule A LIVE từ 08-15, an toàn. CASH_VENDOR gate: ĐÓNG.
- OKF split mandate: file vượt 40KB → tự split theo pattern MIKE_ext.md/coding_guidelines_ext.md.
- dispatch-prompt-heredoc skill cho prompt có backtick.
- P2 expvol_pacing: shadow log-only trên LIVE từ 08-17, review 2026-09-15.
- BAL signal shadow-track: bắt đầu theo dõi (case VPI), review 2026-09-16.
- Paper report 2026-08-20: DELIVERED (Discord + email, 2026-08-20 01:22 ICT).

