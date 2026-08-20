# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
1. **Retro 2026-08-19 XONG** (`kb/incidents/retro/retro-2026-08-19.md`, commit 29764096) — 5 sự cố,
   2 pattern. Việc còn treo cần theo dõi:
   - `wags-fix-not-confirmed: coord-2026-08-20` (bus question, mở 01:29:03Z) — fix daily_retro.sh
     transport-error bị arch-reviewer NEEDS_CHANGES (gap fail_silent + long_term_ops), chưa đóng.
   - Pattern 2 (sửa chung working copy không cách ly, tái diễn từ 08-07) — draft ĐỀ XUẤT escalate
     (bắt buộc --write-scope + mở rộng commit_collision_gate_selfcheck.py) nhưng CHƯA post bus
     question, để Mike/user quyết có mở hay không.
   - 3 selfcheck đỏ (`nav_cum_dividend`, `corp_action_daily`, `lag_forensic_filter`) — cần chủ sở
     hữu xác nhận trước khi sửa.
   - `bot_prepare_plan.py` bug2 (plan phantom mirror sổ paper khác) — cần Taylor điều tra hoặc
     xác nhận tool dead/unused.
2. **plan-dd-check-string fix** (commit 9a9dbb1) — cần ngày có LAG/BAL entry để verify.
3. **Order-book Pha 0 telemetry** (commit d6346efd) — tích lũy bình thường, N=39 obs/3 phiên.

## Bối cảnh còn hiệu lực
- GDKHQ D1-D3 LIVE từ 08-17. yield_floor Option C WIRED, review 2027-02-10.
- TV1 Rule A LIVE từ 08-15. CASH_VENDOR gate: ĐÓNG.
- OKF split mandate: file vượt 40KB → tự split theo pattern MIKE_ext.md/coding_guidelines_ext.md.
- P2 expvol_pacing: shadow log-only trên LIVE từ 08-17, review 2026-09-15.
- BAL signal shadow-track (case VPI): bắt đầu theo dõi, review 2026-09-16.
- Paper report 2026-08-20: DELIVERED (Discord + email).

