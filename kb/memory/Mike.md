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

- [2026-08-20T04:14:05Z] Wakeup redesign 2026-08-20: hotfix sanitize UTF-8 wake_thread.sh ĐÃ merge (886d9158). Đề xuất Phase 1-4 (reconciler cron 5' + bỏ preview khỏi wake prompt + vá ccdb atomic/409 + sửa detector wakeup_audit) đang CHỜ USER DUYỆT — file agents/Mike/research/wakeup_architecture_redesign_20260820.md. Nếu user gật: Phase1+2 giao Wags + arch-reviewer, Phase 3 cần hẹn restart ccdb ngoài giờ giao dịch.
- [2026-08-20T04:24:08Z] Oshares anchor policy 2026-08-20 XONG END-TO-END: nguyên tắc user (BCTC mới nhất = tươi nhất trừ khi có event giữa 2 kỳ, corp-action chủ động cập nhật) đã wire — oshares_live.py nhánh live=True (WC merge 675c34a1) + corp_action_daily.py MODEL_REBASE + crosscheck semantics (mike merge ef91e5af). Skeptic vòng 1 REFUTED (chỉ vì chưa merge), vòng 2 CONFIRMED high. Post-merge real run: gate3 4→0, MBB 10.068.749.885/VRE 2.272.318.410/EVF 760.565.802 (FIN_FALLBACK)/TCB AIS_EXACT/HHV 574.511.888. RESIDUAL: (1) HHV crosscheck 'không đối soát được' tại ngày dòng quý 07-31 sẽ còn tới BCTC quý sau ~2026-10 (điều kiện 2 AIS<=90d, giữ nguyên theo thiết kế); (2) follow-up nhẹ chưa làm: defensive import trong corp_action_daily.py fail rõ ràng nếu oshares_at thiếu kwarg live (khuyến nghị skeptic, cross-repo coupling).
- [2026-08-20T04:26:27Z] Wakeup redesign THI CÔNG (user duyệt 08-20 ~11:17): (1) Wags job Wags_20260820_042255 đang chạy Phase1+2+4 (reconciler+bỏ preview+detector, opus/high, timeout 5400s, thread 1539844704991060060). (2) Phase 3 ccdb bridge ĐÃ COMMIT a333954 (atomic replace_thread_one_shot + 409 chỉ cho IntegrityError + sanitize server-side, 379/379 test PASS) — CHƯA HIỆU LỰC, cần restart ccdb-mike.service SAU 15:00 ICT hôm nay (báo lounge trước khi restart, verify sau restart bằng test POST /api/tasks surrogate). (3) Claim đang giữ: repo:claude-code-discord-bridge. (4) Sau khi cả Wags xong + restart xong: cập nhật MIKE.md §8 mô tả tầng reconciler + đóng vòng báo user.
