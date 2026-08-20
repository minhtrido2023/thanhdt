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
- [2026-08-20T08:28:36Z] Wakeup redesign 2026-08-20 HOÀN TẤT toàn bộ 4 Phase: Phase 1 (wakeup_reconcile.py reconciler, commit 3100f525), Phase 2 (bỏ preview wake prompt, 91fdb04b), Phase 3 (ccdb bridge atomic+sanitize, commit a333954, RESTART XONG lúc 08:27 UTC, verify sống bằng POST /api/tasks surrogate → 201), Phase 4 (đo lường daily_retro, 035e9597). 7 commit tổng, 109 selfcheck assertion PASS qua 4 vòng arch-reviewer. Không còn việc mở nào cho dự án này — chỉ còn TODO dated 2026-08-22 (rà lớp cron-origin có bị cứu oan không) đã ghi trong code, và theo dõi rescued>0/daily_retro tự nhiên.
- [2026-08-20T12:58:54Z] 2026-08-20 RCA 3 lỗi pipeline plan T+1 (research/plan_pipeline_3loi_rca_20260820.md): (1) fan-out N account → N wake push → N phiên Mike song song (ccdb chỉ dedupe task PENDING, không dedupe session RUNNING; tái diễn 08-18 31s + 08-20 83s); (2) bất đối xứng prompt bq_freshness_check.sh:602 — chỉ account có excluded_tickers mới được trỏ tới compute_active_nav.py nơi lộ egg → ZaloPay thấy egg mua VPI, SpaceX không thấy egg nói 'thiếu tiền'; (3) ranh giới VPI paper-track chỉ nằm ở kb/current_ops.md mà DollarBill KHÔNG import (nó đọc context_planning_mini.md), registry khai feature_flag N/A = không cưỡng chế gì. ĐANG CHỜ USER: gỡ lệnh VPI khỏi plan ZaloPay 2026-08-21 (chưa duyệt, approved_by=None) + duyệt thi công P1-P3.
- [2026-08-20T13:21:06Z] RCA 3 lỗi plan pipeline 2026-08-20 THI CÔNG: P0 gỡ VPI khỏi plan ZaloPay 08-21 (deferred) XONG. P1 XONG+COMMIT: F2.1 egg vô điều kiện (mike cd2f66f5) + F3.1 signal_holds 2 tầng gate (WC 3955e59b bot_execute + mike cd2f66f5 send_plan_report/prompt). signal_holds_selfcheck 18/18 PASS 2TZ, scoped plan.py 15/15 PASS. data/signal_holds.json seed book=BAL side=buy until 2026-09-16 (runtime, gitignored như trading_rules.json). ĐANG: arch-reviewer audit money-path gate + dispatch Wags P2 batch-aware wake (dispatch.sh _bg_wrapper). CÒN: P2 (Wags), P3 ccdb session-dedupe (cần restart), F2.3 bảng §25, F3.3 checker ngược.
- [2026-08-20T13:30:18Z] RCA plan pipeline: P1 + arch-reviewer vòng 1 XONG. arch-reviewer NEEDS_CHANGES 4 lỗi (killer: enforce_plan gỡ oan order thiếu id) → đã fix hết + commit (mike: cd2f66f5 gốc + commit fix mới; WC 3955e59b). signal_holds_selfcheck 23/23 PASS 2 TZ. data/signal_holds.json giờ có 2 hold: book=BAL + ticker=VPI (defense-in-depth), until 2026-09-16. P2 Wags job Wags_20260820_132135 ĐANG CHẠY (batch-aware wake, thread architecture). LƯU Ý: dispatch Wags vào cùng mike working copy đã trigger commit-collision gate (Pattern 2) — commit surgical explicit-path + warn qua được. CÒN LẠI: P2 chờ Wags, P3 ccdb session-dedupe (cần restart ngoài giờ), F2.3 bảng §25 coding_guidelines, F3.3 checker ngược khi hold hết hạn.
