---
kind: changelog
group: _rules
title: Log thay đổi Cron Registry
note: >
  Đây là changelog BIÊN TẬP của lịch cron (dòng nào thêm/xoá/đổi giờ, ai làm, job nào, 4 câu hỏi
  §11 đã trả lời) — provenance + audit trail §11, KHÔNG phải narrative sự cố. Sự cố live-workflow
  ghi ở kb/incidents/ (C1 vintage-mismatch 2026-07-12; send_plan re-dispatch 2026-07-13). Mục cũ
  nhất ở dưới cùng.
authority_note: >
  CURRENT-STATE của mỗi cron = BẢNG CHÍNH (../cron_registry.md), KHÔNG phải changelog này. Đặc biệt
  entry 08:10 ngày 3 (refresh_deposit_rate_vn.sh): 2 mục 2026-07-20 dưới đây kể lại quá trình bật
  cơ chế auto-write; NHƯNG trạng thái HIỆN TẠI (bảng chính) = auto-write ĐÃ BỊ LOẠI BỎ, người thật
  chạy `append_deposit_rate.py --source manual_verify`. Khi mâu thuẫn → tin bảng chính. Full detail
  + review đối kháng deposit-rate: kb/projects/deposit-rate-autocheck.md.
preserve_verbatim: >
  Cố ý KHÔNG nén-semantic các mục dưới (theo tiền lệ data_registry/CHANGELOG.md + guardrail "đừng
  cắt cảnh báo an toàn nào"): mỗi mục chứa audit-trail §11 (4 câu hỏi/job) + buffer đo thật + gate
  formula — load-bearing, không phải fluff. Chỉ thêm pointer kb/incidents/, giữ nguyên nội dung.
---

# Log thay đổi Cron Registry

- 2026-08-20 (Wags, user duyệt tường minh ~11:17 ICT — đề xuất
  `agents/Mike/research/wakeup_architecture_redesign_20260820.md` Phase 1): **THÊM cron `*/5`**
  `/usr/bin/python3 /home/trido/thanhdt/WorkingClaude/mike/bin/wakeup_reconcile.py >>
  /home/trido/thanhdt/WorkingClaude/mike/logs/wakeup_reconcile_cron.log 2>&1`.
  Tầng LEVEL-TRIGGERED đầu tiên cho hệ wake-up: cưỡng chế bất biến *"job terminal `from=Mike`
  có `discord_thread_id`, chưa `replied_at`, `ended_at` quá 3' ⇒ thread phải còn ≥1 one-shot
  wakeup pending trong tasks.db HOẶC session đang running"*; vi phạm ⇒ gọi lại `wake_thread.sh`
  với prompt template §8.4 (an toàn vì `jobs.sh claim-reply` idempotent). Kiêm consumer DUY NHẤT
  của `logs/wake_thread_errors.log` (file này tồn tại từ 08-15 mà KHÔNG checker nào đọc ⇒ 3 lần
  push chết im lặng suốt 5 ngày). Root cause:
  `kb/incidents/2026-08/2026-08-20-wake-push-utf8-surrogate-deletes-ladder.md`.
  4 câu hỏi §11: (1) đọc `bus/jobs/*.json` (local live), `/workspace/ccdb-mike/data/tasks.db`
  (sqlite `mode=ro`, DB của service khác — TUYỆT ĐỐI không ghi), `127.0.0.1:8199/api/sessions`
  (live), `logs/wake_thread_errors.log`; KHÔNG chạm BQ/DNSE/web nên không có chuyện vintage/cache;
  (2) cả 3 nguồn tươi tức thời; (3) cần T — bất biến chỉ có nghĩa trên trạng thái hiện tại;
  (4) consumer = phiên Mike ở thread Discord (được đánh thức) + người đọc Trading Daily khi push
  lỗi + `daily_retro.sh` 00:30 (Phase 4 đọc log tính success-rate/số lần cứu).
  Chống xung đột: flock `state/locks/wakeup_reconcile.lock` (chạy đè ⇒ exit im lặng); state file
  ghi atomic tmp+rename; tối đa 1 wake/thread/chu kỳ (ccdb xoá one-shot pending trước khi tạo cái
  mới, bắn 2 phát liền là phát sau huỷ phát trước). Fail-safe: tasks.db/API không đọc được ⇒
  KHÔNG bắn wake nào, exit 2/3 (mandate user 2026-08-03 "ưu tiên quan sát tự nhiên").
  Chống bắn hàng loạt lần đầu: hằng số `MIN_EFFECTIVE_TS=1787199900` (mốc deploy 11:25 ICT) +
  look-back trần 48h — đo thật trên job board production: bỏ mốc ⇒ 7 job cũ bị bắn, có mốc ⇒ 0.
  ⚠️ **Sửa sau audit (arch-reviewer NEEDS_CHANGES, cùng ngày — 1 BLOCKER thật)**: bản đầu giả định
  "wake thành công ⇒ tasks.db có row pending ⇒ chu kỳ sau tự im". Đọc code ccdb thật
  (`SchedulerCog._claim_one_shot`) thì row one-shot bị XOÁ **trước khi** Claude chạy (guard F1/F3
  chống replay) ⇒ phiên được đánh thức mà không `claim-reply` sẽ bị bắn lại mỗi 5' vô tận (đo
  sandbox: 5 chu kỳ = 5 wake cùng 1 job; trần cũ duy nhất là look-back 48h = 576 lượt, mỗi lượt
  dựng 1 phiên Claude). Base rate thật: 4/5 job `--bg` chưa `replied_at` từ 08-17 ĐỀU đã có dòng
  SUCCESS trong `logs/wake_thread.log`. Đã vá bằng TRẦN CỨNG ghi bền vào state file (ghi TRƯỚC khi
  gọi wake, §5): `MAX_FIRES_PER_JOB=3` (hết ⇒ dừng hẳn + notify `trading_daily` đúng 1 lần),
  `REFIRE_COOLDOWN=900s`, `MAX_WAKES_PER_CYCLE=3`. Kèm 3 vá nữa cùng audit: (a) loại job dispatch
  ĐỒNG BỘ khỏi phạm vi (`pid` có trong record = chạy nền; 192/773 record là sync, mỗi lượt
  `wags_autofix.sh` sẽ là 1 false-positive đánh thức topic Architecture); (b) chỉ tiến
  `errlog_offset` khi `notify_thread.sh` trả 0 (gửi hỏng mà tiến offset = mất vĩnh viễn đúng dòng
  lỗi quan trọng nhất); (c) in 1 dòng heartbeat ra stdout mỗi lần chạy để
  `bin/cron_health_check.py` (đo bằng mtime log target, bucket `frequent` ngưỡng 2h) không báo
  STALE giả mỗi ngày.
  Phụ trợ cùng commit: neo `+07:00` tường minh cho dấu thời gian `wake_thread.sh` (§16 — log thật
  đã có 1 dòng `+00:00` lẫn giữa 33 dòng `+07:00` vì script chạy từ 2 nơi TZ khác nhau, làm lệch
  cửa sổ ngày của metric Phase 4); sửa câu "chưa checker nào đọc log này" trong header
  `wake_thread.sh` (giờ reconciler là consumer); `MIKE.md` §8 thêm mô tả tầng thứ 3 + cách xử lý
  prompt `[WAKEUP-RECONCILER]`.
  Verify: `bin/wakeup_reconcile_selfcheck.py` **49/49 PASS** (hermetic hoàn toàn: sqlite fixture,
  HTTP server fixture, stub `wake_thread.sh`/`notify_thread.sh`; chạy cả `env -u TZ`,
  `TZ=Pacific/Kiritimati`, `TZ=America/Anchorage`) + 6 mutation test đều bị bắt + dry-run trên
  dữ liệu production (0 wake, phát hiện đúng 3 dòng lỗi push lịch sử) + 11 mutation test (5 vòng đầu, 5 vòng sau audit,
  1 cho neo TZ) đều bị bắt. Selfcheck kèm theo: `bin/wake_thread_selfcheck.py` 16/16 (thêm 2 ca TZ),
  `bin/daily_retro_wake_metrics_selfcheck.sh` 13/13 (MỚI), `bin/dispatch_wake_selfcheck.sh` 12/12
  (thêm 2 ca hồi quy Phase 2).
  State file được SEED lúc deploy (`state/wakeup_reconcile_state.json`, offset = cuối
  `wake_thread_errors.log` hiện tại) để lần chạy đầu không báo lại 3 dòng lỗi lịch sử đã chẩn đoán.
  Backup crontab trước khi cài: `state/crontab_backup_20260820_wakeup_reconcile.txt`.

- 2026-08-18 (Mike/Codex, user duyệt 2026-08-18): **THÊM cron daily `0 20 * * *` =
  03:00 ICT** `/home/trido/thanhdt/WorkingClaude/mike/bin/worktree_cleanup_daily.sh --apply`,
  ghi log `logs/worktree_cleanup.log`. Script mới dọn worktree/branch session đã merge,
  mặc định DRY-RUN và chỉ xoá khi có `--apply`.
  4 câu hỏi §11: (1) đọc git local `worktree list --porcelain` + `for-each-ref
  refs/heads/session/*` + `merge-base --is-ancestor` với `master` + CCDB `/api/sessions`
  và `/api/claims` — không gọi BQ/DNSE/web, vintage không liên quan; (2) nguồn là git
  + CCDB local luôn tươi tại thời điểm chạy; (3) không cần T/T-1 vì job thuần dọn dẹp
  metadata local; (4) không có consumer có deadline; mục tiêu là giảm tải token/quản lý
  worktree, không ảnh hưởng tiến trình dữ liệu.
  An toàn bắt buộc: fail-closed nếu CCDB không đọc được, chỉ xoá worktree sạch + branch
  đã merge, không `--force`, bỏ qua dirty/unmerged/detached và mọi path/branch thuộc
  thread/claim CCDB đã biết; remote branch chỉ báo cáo.
  Chống xung đột: 03:00 nằm sau `kb_nightly.sh` 02:00 (hết cửa sổ git-lock KB) và trước
  `selfcheck_weekly_baseline_check.sh` 04:30; dùng `flock` riêng nên chạy lặp vô hại.
  Verify: `bash -n` + `shellcheck_gate.sh` + dry-run trên production root cả hai chế độ
  `CCDB_API_URL` (process env và fallback `http://127.0.0.1:8199`) đều PASS.

- 2026-08-17 (Mike/Codex, user duyệt 2026-08-17 04:06 UTC): **THÊM cron `late_plan_catchup.sh`**
  3 mốc tối: `45 14 * * 1-5` (21:45 ICT), `0 15 * * 1-5` (22:00 ICT), `30 16 * * 1-5`
  (23:30 ICT), cùng chạy `/home/trido/thanhdt/WorkingClaude/mike/bin/late_plan_catchup.sh`.
  Script mới `mike/bin/late_plan_catchup.sh`: tự no-op trước 21:00 ICT / ngày không giao dịch;
  per-account chỉ chạy nếu plan T+1 hợp lệ, chưa duyệt, chưa có dấu merge; chạy đúng 1 lần
  chuỗi L1→L2→merge→inject→`send_plan_report.sh --account <acct> --second-chance`.
  4 câu hỏi §11: (1) DNSE live same-day + cache parquet T-1 (qua L1/L2) + file plan local do
  DollarBill ghi tối hôm đó — đo thật 08-05→08-14 có 2/5 phiên plan ghi sau 21:00 (muộn nhất
  23:25 ICT); (2) plan tươi khi ghi xong, DNSE tươi sau 14:45; (3) cần T (giá đóng cửa + vị thế
  hôm nay) — ràng buộc ≥15:00 ICT kế thừa từ L1/L2 guard; (4) consumer = user duyệt qua đêm,
  deadline `preflight_check.sh` 08:45 sáng sau.
  Chống xung đột: 21:45/22:00 cách send_plan_report 21:00 và second-chance 23:00; 23:30 trước
  `sync_bq_cache_daily.sh` 23:45 (15' đệm, runtime toàn chain đo <60s + gửi báo cáo);
  idempotent 2 lớp (trạng thái plan + lock per-account) nên 3 lần chạy/đêm không trùng việc,
  không bao giờ chạm plan đã duyệt (APPROVED/INVALID → REFUSE rc=1).

- 2026-08-16 (Mike/Codex, user yêu cầu tự động hóa gửi báo cáo tuần sáng chủ nhật 09:00
  không miss): **THÊM cron `0 2 * * 0` = Sun 09:00 ICT**
  `/home/trido/thanhdt/WorkingClaude/mike/bin/spend_report_weekly.sh >> .../mike/logs/spend_report_weekly.log 2>&1`.
  Script mới `mike/bin/spend_report_weekly.py` dùng lại logic `spend_report.py`, sinh report
  Markdown có bảng so sánh WoW, 4 PNG charts (bar/pie), nhận xét kiểu manager, và gửi email
  HTML + `.md` đính kèm qua `send_report_email.py`.
  4 câu hỏi §11: (1) đọc `bus/jobs/*.json` + `git log` 7 ngày + `state/spend_history.csv`
  tuần trước — đều local live, không gọi BQ/DNSE/web; (2) nguồn tươi sau khi tuần đã đóng,
  chủ nhật 09:00 ICT đủ điều kiện; (3) cần T-1/tuần đã đóng, không cần same-day; (4) consumer
  là CEO/user qua email, deadline chủ nhật 09:00 ICT theo yêu cầu user.
  Chống xung đột: Sunday 09:00 không trùng job nặng; `fleet_housekeeping.sh --apply` chạy
  22:00 CN sau đó, chỉ dọn log/registry archive cũ.
  Verify trước khi cài: dry-run chạy trên root production (`--root /home/trido/thanhdt/WorkingClaude/mike
  --dry-run`) sinh đủ report + 4 PNG; HTML render nhúng 4 ảnh base64 (không còn ảnh thiếu);
  `py_compile` 3 file Python + `bash -n` wrapper đều OK.

- 2026-08-14 (Taylor, job `Taylor_20260814_142151`; user duyệt §6 `agents/Taylor/research/
  park_merge_wire_20260811.md`): **THÊM 3 dòng** dựng chuỗi PARK-merge — `30 12` (19:30 ICT)
  `park_trim_daily.sh` (L1), `40 12` (19:40) `jit_unpark_daily.sh` (L2), `20 13` (20:20)
  `merge_park_daily.sh --write`. Cả 3 đều T2-T6, đều là wrapper MỚI trong `mike/bin/` theo khuôn
  `inject_discretionary_orders.sh`/`compute_active_nav_all.sh` (tự lặp `live_dnse_labels()`) —
  **không** dùng được `for_each_live_account.sh` vì 3 script này cần tham số per-account-per-date
  (`--out park_trim_<acct>_<T+1>.json`, `--plan-date`) mà wrapper đó không dựng được.
  Bối cảnh: L1/L2 **chưa từng có cron**; artifact tới nay chỉ có nhờ DollarBill chạy tay trong
  dispatch EOD, nên `merge_park_orders.py` (đã ship + quant-skeptic CONFIRMED `high` 08-11, commit
  `2633eb44`) không có gì để gộp vào ngày thường.
  4 câu hỏi §11 — chi tiết đầy đủ nằm ở 3 dòng tương ứng của bảng chính, tóm tắt:
  (1) L1/L2 đọc **DNSE LIVE same-day** (bắt buộc, §6 bright-line) + `bq_cache/ticker` T-1 chỉ để
  tính ADV lịch sử + rổ `custom30v_8l_publish.csv` + sổ lô local; merge **thuần file local, không
  gọi DNSE, không chạm BQ**. (2) DNSE tươi ngay sau đóng cửa 14:45; cache từ sync 23:45 đêm trước;
  plan T+1 do DollarBill ghi ~19:0x. (3) L1/L2 cần **T** ⇒ **ràng buộc cứng sau 15:00 ICT**, cưỡng
  chế **bằng code** trong wrapper (`now_ict().hour < 15` ⇒ rc=1) chứ không chỉ bằng giờ cron —
  `close_price()` trả 0 khi phiên chưa đóng, đúng sự cố 2026-08-07. (4) Consumer: L1→L2→merge→
  `inject_discretionary_orders.sh` 20:30 → `send_plan_report.sh` 21:00, deadline cuối là user duyệt
  trước `preflight_check.sh` 08:45 sáng sau.
  Chống xung đột: 19:30 lệch 10' với `pt_8l_daily` 19:20 và 5' với `telegram_run_daily` 19:35;
  20:20 nằm sau `compute_active_nav_all.sh` 20:15 (5') nhưng **không tranh tài nguyên** vì merge
  không gọi DNSE, và trước `inject_discretionary_orders.sh` 20:30 (10'). Runtime đo thật: L1/L2
  <60s, merge <5s cho cả 2 account.
  Verify trước khi cài: ShellCheck 0 finding/3 file; 5 selfcheck liên quan xanh (merge 120/120 ·
  park_trim 63/63 · jit_unpark + ma trận TZ · approve_plan_with_jit 27/27 · preflight 16/16);
  E2E **trên dữ liệu SỐNG hôm nay** trong sandbox `PARK_CHAIN_PLAN_DIR` (dry-run ⇒ plan y hệt từng
  byte; `--write` ⇒ `orders[]` không đổi, `approved_by=None` giữ nguyên); chứng minh ngược 2 nhánh
  fail-closed của L2 (thiếu L1 / thiếu plan ⇒ rc=1, 0 artifact) và 4 nhánh guard giờ/ngày bằng đồng
  hồ giả; ma trận TZ `{-u TZ, NY, UTC, env -i}` 4/4.
  ⚠️ Ghi nhận khi cài, KHÔNG do 3 dòng này gây ra: (a) plan T+1 **2/5 phiên gần đây được ghi SAU
  21:00** (08-11 lúc 23:25, 08-13 lúc 21:31) ⇒ những ngày đó L2 no-op fail-closed và chuỗi không
  giao gì — an toàn nhưng vô ích, không phải hồi quy; (b) tối 08-14 L1 trả `BLOCKED_RECONCILE` cả
  2 account (sổ lô BID lệch broker: SpaceX 1.100 vs 1.175, ZaloPay 400 vs 427, cùng tỷ lệ ~6,8%) —
  lúc 19:04 còn `NO_TRIM`, tức broker ghi có thêm CP trong buổi tối; chuỗi sẽ chạy nhưng không sinh
  lệnh nào tới khi sổ lô được đối soát lại.
  Rollback 1 lệnh: `crontab -l | grep -v park_trim_daily.sh | grep -v jit_unpark_daily.sh | grep -v
  merge_park_daily.sh | crontab -`; bản crontab trước khi đổi lưu ở
  `agents/Taylor/research/crontab_backup_20260814_before_park_chain.txt`.
  📌 **Quy chiếu commit — CÙNG JOB nhưng ĐÚNG RA LÀ HAI COMMIT LIỀN KỀ, không phải một**
  (quant-skeptic bắt được 2026-08-14, đính chính ngay tại đây): 3 wrapper `.sh` + bản sao lưu
  crontab nằm ở **`f44b5e23`** (21:38:30 +0700); 2 file tài liệu này (`kb/cron_registry.md` +
  `kb/cron_registry/CHANGELOG.md`) thực tế đã bị **`3a807740`** (21:38:16 +0700, commit
  `consolidate` KB v2192) gom mất **14 giây trước** — `consolidate.sh` chạy tự động ngay sau
  `append_event.sh` và commit TOÀN BỘ `kb/`, nên tới lượt commit của job thì 2 path đó không còn
  gì để stage. Nội dung khớp đúng ý định §11 (cùng job, cùng phút, đều trên `master`) nhưng ai
  truy vết bằng một hash duy nhất sẽ hụt. **Bài học cho cron/registry sau này**: ở repo `mike`,
  hễ job có `append_event.sh` chạy trước `git commit` thì file `kb/` gần như chắc chắn đi theo
  commit của consolidator — muốn "cùng commit" theo nghĩa đen phải commit `kb/` TRƯỚC khi ghi bus,
  còn không thì khai báo cả hai hash như dòng này.

- 2026-08-11 (Mike, user mandate): cron 16:00 ICT `paper_programs_daily_report.sh` thêm cờ
  `--email`, vẫn giữ `--post` để Discord và email dùng cùng một lần render. Wrapper lưu artifact
  `reports/paper_programs_daily_report_YYYY-MM-DD.md`, gửi HTML + file Markdown đính kèm qua
  Gmail SMTP hiện có. Không thêm cron, không ảnh hưởng papertrade pipeline hay giao dịch.

- 2026-08-01 (Mike, việc #3 đã duyệt trong review kiến trúc fleet — nghiên cứu Paseo + phản biện
  Fable-plan/Opus-critique, 2026-07-31→08-01): thêm dòng `TZ=Asia/Ho_Chi_Minh` làm biến môi trường
  TOÀN CỤC ở đầu crontab (sau dòng `PATH=`, trước mọi job) — 4 câu hỏi §11: (1) đọc gì+vintage —
  không đọc gì, đây là biến môi trường ambient; (2) nguồn tươi lúc nào — N/A, không phải job có
  lịch; (3) cần T hay T-1 — N/A; (4) ai tiêu thụ+deadline — MỌI job cron kế thừa biến này làm TZ
  mặc định, đóng đúng lỗ hổng khiến bug TZ trong `bin/dt5g_writer_watch.py` (host chạy `Etc/UTC`,
  code giả định ICT) chỉ latent chứ chưa live — trước đó chỉ 8/66 dòng có `TZ=Asia/Ho_Chi_Minh`
  prefix riêng, còn lại trông cậy script tự source `wc_env.sh`. **Không đổi giờ/lịch dòng nào**,
  backup trước khi sửa: `mike/logs/crontab_backup_before_tz_default_20260801.txt`; verify `diff`
  xác nhận đúng 1 dòng thêm, không dòng nào khác đổi. Chi tiết + rule chung:
  `kb/coding_guidelines.md` §16.
- 2026-08-01 (Mike, user mandate sau 2 sự cố cùng ngày — `kb_nightly.sh`/`daily_retro.sh` quoting
  bug chết lặng 2 tuần/2 đêm mà không ai biết): audit TOÀN BỘ 64 dòng crontab bằng công cụ mới
  `mike/bin/cron_health_check.py` (parse crontab thật, đối chiếu mtime + tail log tìm dấu hiệu
  crash cho từng job). Kết quả: 1 bug thật mới tìm thấy + sửa (`kb_nightly.sh:584` gọi
  `$ROOT/bin/backup.sh` — file KHÔNG TỒN TẠI từ khi thêm 2026-06-30, `|| true` nuốt lỗi mỗi đêm
  hơn 1 tháng; đích đúng là `/home/trido/thanhdt/backup.sh`, đã sửa + verify bằng cách chạy thật).
  **Không đổi giờ/lịch dòng nào** — chỉ THÊM `>> mike/logs/<name>.log 2>&1` cho 9 dòng script
  WorkingClaude-root trước đó không có log target khai báo (`papertrade_daily.sh`,
  `pt_8l_daily.sh`, `telegram_run_daily.sh`, `daily_refresh_v34b_linux.sh`,
  `auto_update_commodity_wb.sh` ×2, `rubber_weekly.sh`, `update_shares_live.sh`,
  `fetch_new_listings_daily.sh`) — output trước đây đi vào cron mail mặc định (postfix có chạy
  nhưng KHÔNG có mailbox local `/var/mail/trido`, tức mail không ai đọc được — tương đương mất).
  Hầu hết các script này đã tự quản log riêng (`data/refresh_v34b_linux_<date>.log` v.v.) nên rủi
  ro thực tế thấp hơn `kb_nightly.sh`/`daily_retro.sh`, nhưng vẫn thêm redirect làm lớp phòng thủ
  thứ 2 bắt crash SỚM (trước khi script tự log kịp khởi tạo) — đúng lớp lỗi vừa xảy ra hôm nay.
  **Không đụng** `discord_bot/start.sh` (hệ thống khác, không thuộc sở hữu fleet Mike). 4 câu hỏi
  §11: không áp dụng (không đổi lịch/nguồn đọc — chỉ thêm observability). Cài `cron_health_check.py`
  làm job DAILY ĐỘC LẬP (`cron_health_check_daily.sh`, 08:25 T2-T6) — CỐ Ý KHÔNG nhét vào
  `ops_health_check.sh` vì đó là fleet-wide, nhét vào loop `for_each_live_account.sh` sẽ chạy
  lặp theo số account (đúng bẫy "Job board:" đã ghi nhận coord-2026-07-22). Xem bảng chính dòng
  08:25 + `kb/incidents/2026-08/`.
- 2026-07-30 (Winston, job `Winston_20260730_014022` — user duyệt sau khi Taylor phát hiện trong job
  re-pin R3 2026-07-29): **KHÔNG đổi lịch cron nào**, chỉ đổi HÀNH VI của script mà cron 23:45
  (`sync_bq_cache_daily.sh`) gọi — ghi ở đây vì operator cần biết. `sync_bq_cache.py` trước đây không
  có khoá và ghi `to_parquet` đè TRỰC TIẾP lên file đích: 23:45 `--delta` khởi động đè lên cùng
  `data/bq_cache` với một full re-sync thủ công đang chạy (đúng tình huống 2026-07-29, né được chỉ vì
  MAY về thứ tự ghi manifest) → cache có thể TRỘN VINTAGE mà manifest vẫn `verified=true`.
  Nay: (1) `fcntl` **trylock** trên `data/bq_cache/.sync.lock`, bao cả download + verify + ghi manifest
  (kể cả `--verify`, vì nó cũng ghi lại manifest) — lần sync đến sau **BỎ QUA sạch, exit 75**
  (EX_TEMPFAIL, không ghi gì); non-blocking là chủ đích vì `ticker` full chạy ~2h, bắt cron chờ sẽ dồn
  job; (2) mọi parquet + `manifest.json` ghi qua file tạm cùng thư mục rồi `os.replace` (atomic).
  **Ảnh hưởng operator**: exit 75 KHÔNG phá wrapper (`... || true`) và thông báo "BỎ QUA" không khớp
  grep `FAILED|FAIL —|RESULT: FAIL` nên KHÔNG kích `ops_autofix` giả; một đêm sync bị bỏ qua vẫn phát
  hiện được vì `preflight_bq_cache.py` trong cùng wrapper chạy độc lập và cảnh báo khi `verified_at`
  cũ >36h. Self-check `sync_cache_lock_selfcheck.py` 20/20 PASS (gồm đối chứng: cách ghi CŨ bị SIGKILL
  → file đích hỏng thật) + smoke thật trên BQ; quant-skeptic **CONFIRMED (high)**, killer-objection duy
  nhất (flock trên NFS không đảm bảo) đã đóng: `data/bq_cache` nằm trên ext4 local
  (`/dev/mapper/pve-vm--102--disk--2`), 1 host duy nhất.

- 2026-07-29 (Winston, job `Winston_20260729_152037` — user CHỐT sau khi 2 job cùng ngày
  (`Winston_20260729_132257` + `Taylor_20260729_132056`) phát hiện production BQ bị restate ÂM THẦM
  ba lần: `ticker_prune` TRUNCATE+rebuild 07:27 xoá 58 mã khỏi TOÀN BỘ lịch sử, `VNINDEX_PE` backfill
  ngược tới 2006, corp-action restate ~2-3%/tuần trên `ticker`/`ticker_financial` — cả ba đều phát hiện
  do TÌNH CỜ, và BQ time-travel bị xoá mỗi sáng nên KHÔNG tái tạo được vintage cũ):
  **CÀI MỚI `mike/bin/bq_monthly_pin.sh` 22:00 ICT ngày 1 hàng tháng** (`0 15 1 * *`, máy chạy giờ UTC).
  Chụp BQ table SNAPSHOT 11 bảng dễ bị restate vào dataset RIÊNG `tav2_pin` (`<table>_pin_YYYYMM`),
  rồi diff pin-mới vs pin-tháng-trước theo từng `ticker` và cảnh báo khi vượt ngưỡng.
  Chọn **BQ snapshot thay vì export CSV**: metadata-only (bảng `ticker` 4,8 GB pin xong trong ~10 s),
  chỉ tính phí phần BYTE LỆCH so bảng gốc, read-only nên bất biến, và vẫn là bảng BQ hạng nhất nên
  `SELECT ... FROM tav2_pin.ticker_pin_202608` chạy được ngay — CSV mất kiểu dữ liệu và khó diff.
  4 câu hỏi §11:
  (1) *Đọc gì + vintage*: BQ **LIVE** qua `bq cp --snapshot` + `bq query` CLI thuần — không import
  python nào của repo nên không có đường dính `BQ_LOCAL_CACHE` (bài học C1);
  (2) *Nguồn tươi lúc nào*: mọi bảng đích ổn định sau chuỗi ghi trong ngày — ingest tav2 ~17:2x,
  `daily_refresh` 18:30 (state), pipeline 19:00 (`universe_pit`/`universe_pit_quality`),
  `fa_ratings*` 20:00 mùa BCTC, `inject` 20:30. Thêm một mốc MỚI đo được hôm nay: bq_admin có
  cửa sổ rebuild **buổi sáng ~07:27** — snapshot là atomic nhưng pin rơi vào giữa TRUNCATE...INSERT
  sẽ chụp bảng RỖNG và bắn CRITICAL giả, nên **cố ý không đặt job này buổi sáng**;
  (3) *Cần T hay T-1*: cần một trạng thái **ỔN ĐỊNH**, không cần same-day — nên chạy cuối ngày 1
  thay vì đầu ngày; ngày 1 rơi vào cuối tuần vẫn hợp lệ (bảng đứng yên, không có gì để chờ);
  (4) *Ai tiêu thụ + deadline*: **không có consumer tự động nào** — đích là người (tra lại vintage khi
  cần audit) + cảnh báo Discord Trading Daily `1521470705563340910`. Không job nào chặn sau nó, nên
  giờ chạy chỉ cần tránh xung đột: 22:00 trống (21:00 send_plan, 23:00 second-chance, 23:45 sync),
  đệm 105' trước sync 23:45 với `timeout 4500` (runtime baseline đo thật ~7').
  **Retention = GIỮ TẤT CẢ** (11 pin = 6,27 GB logical ≈ $0,16/tháng nếu không dedup — thực tế rẻ hơn;
  xoá 1 pin = huỷ bản sao DUY NHẤT của một vintage để tiết kiệm vài cent). Xem lại chỉ khi
  `--cost` báo dataset vượt ~100 GB. Baseline `*_pin_202607` đã tạo ngay trong job này để tháng 8
  có cái mà so. Test: `--selftest` 6/6 + diff thật trên `fa_ratings_8l` (dựng pin giả tháng trước
  bằng cách xoá VNM/FPT + đổi rating AAA → diff bắt đúng cả 3 loại thay đổi).
- 2026-07-29 (Winston, job `Winston_20260729_103816` — user yêu cầu "dời TẤT CẢ paper report/pipeline
  sang 19:00 để có dữ liệu cuối ngày"): **CÀI MỚI `mike/bin/paper_late_feeds.sh` 20:05 ICT** (`5 13 * * 1-5`),
  tách `[19] crisis_alert_push` ra khỏi `papertrade_daily.sh` 15:30 và chạy LẠI `[21] fetch_bdi_daily`.
  **KHÔNG dời chuỗi 15:30** — yêu cầu gốc đã kiểm chứng và bác bỏ một phần: đo thật cho thấy 11/15 step
  active đọc `BQ_LOCAL_CACHE` (`data/bq_cache/*.parquet`, chỉ sync 23:45) nên thấy T-1 dù chạy 15:30 hay
  19:00 — dời chỉ làm báo cáo muộn hơn mà không tươi hơn. Bảng phân loại A/B/C từng step + sơ đồ thứ tự:
  [papertrade_daily_steps.md](papertrade_daily_steps.md).
  4 câu hỏi §11 cho dòng mới:
  (1) *Đọc gì + vintage*: `[19]` query BQ **LIVE** (`ticker_prune` JOIN `dt5g_live` qua `dna_report._bq`
  subprocess, KHÔNG qua cache) → asof = min(2 bảng); `[21]` scrape handybulk.com, lấy ngày mới nhất trên trang.
  (2) *Nguồn tươi lúc nào — ĐO THẬT 2026-07-29*: ingest tav2 ghi xong `ticker` 17:23 / `ticker_prune` 17:17 /
  `ticker_financial` 17:21 / `ticker_1m` 16:02 ICT; `dt5g_live` có phiên T sau `publish_gated_state`
  19:00-19:03 (log: `EOD PIPELINE DONE — 19:03 ICT`). Baltic công bố ~13:00 London ≈ 19-20:00 ICT — kiểm
  chứng: chạy thử lúc 17:47 ICT vẫn chỉ lấy được 07-28.
  (3) *Cần T hay T-1*: cần **T** — `[19]` là cảnh báo capitulation cho người đọc; cảnh báo theo regime hôm qua
  là vô nghĩa đúng vào ngày cần nó nhất.
  (4) *Ai tiêu thụ + deadline*: `[19]` → user qua Telegram, cần trước `send_plan_report` 21:00 (thấy cảnh báo
  trước khi duyệt plan); `[21]` → `freight_map.py` ad-hoc, không deadline. Chọn 20:05 = sau publish 19:03
  (buffer 1h), sau `telegram_run_daily` 19:35, trước 20:30 inject + 21:00 send_plan.
  **Giữ `[21]` ở CẢ 15:30 lẫn 20:05** (không phải dư thừa): script chỉ lấy ngày MỚI NHẤT trên trang → nếu chỉ
  chạy 1 lần muộn mà hôm đó trang chưa cập nhật thì ngày đó mất vĩnh viễn; 2 lần/ngày + dedup theo `date`
  (`drop_duplicates keep=last`) = idempotent, không bao giờ thủng chuỗi.
  **KHÔNG đổi** (có lý do, đừng "tối ưu" lại): `[20] pt_capitulation_shadow` giữ ở 15:30 vì `bq_freshness_check`
  19:00 đọc `pt_capitulation_state.json` cho note CAPIT_FIRED của dispatch DollarBill (đường plan tiền thật) —
  đề xuất chuyển `[20]` vào chính chuỗi 19:00 (sau pipeline-1, trước pipeline-2) đang **chờ user duyệt**;
  `[17] orb_pt` đã asof T sẵn (vnstock live, VN đóng cửa 14:45); `[22]` panel theo THÁNG + bị 19:00 check tuổi
  file `lag_edge_health.csv`; `[1] pull_us_market` phiên US chưa mở ở mọi giờ ICT trong ngày; `[26]` dữ liệu
  theo quý. Test: chạy thật `paper_late_feeds.sh` 17:47 → rc=0, cả 2 step `[ok]`, không side-effect (DORMANT
  → không push, BDI dedup no-op). Backup crontab `/tmp/cron_bak_20260729.txt`, diff xác nhận chỉ THÊM 1 dòng.

- 2026-07-29 (Winston, job `Winston_20260729_084600` — user phát hiện report hiển thị dữ liệu cũ):
  **ĐỔI GIỜ `paper_programs_daily_report.sh --post` 15:20 → 16:00 ICT** (`20 8` → `0 9`, T2-T6).
  *Triệu chứng:* report ngày 07-29 hiển thị mục (7) Capitulation + (8) Engine-room asof **07-27**
  (trễ 2 phiên) trong khi mục (6) ORB asof 07-28 (trễ 1 phiên) — cùng nguồn `papertrade_daily.sh`.
  *Root cause = HAI lag ĐỘC LẬP cộng dồn, không phải một:* **(A)** report chạy 15:20 = **TRƯỚC**
  chain 15:30 cùng ngày → luôn đọc artifact do chain **hôm trước** ghi (+1 phiên, áp dụng cho MỌI
  mục — đây là phần đã sửa); **(B)** riêng mục 7/8, bản thân artifact được gắn nhãn T-1 vì
  `pt_capitulation_shadow.py` query BQ LIVE (`ticker_prune`/`dt5g_live`) và các sim sinh
  `papertrade_compare5.csv` chạy trên giá tới T-1 — BQ chưa có close phiên T lúc 15:30 (ingest
  ~17:30 / sync 23:45) → **sàn cấu trúc**, không sửa được nếu giữ report trong khung 15-16h. Mục 6
  KHÔNG dính (B) vì `orb_pt.py` kéo bar 1m VN30F **LIVE từ vnstock**, phiên đã đóng 14:30 → nhãn T.
  Vậy 2+1 = đúng chênh lệch quan sát được. *Sau fix:* ORB asof **T**, Capitulation/Engine-room asof
  **T-1** (sàn). Ghi chú cũ ở dòng 15:30 ("consumer = 15:20 report **hôm sau**") mô tả đúng hậu quả
  nhưng KHÔNG phải thiết kế có chủ đích — chain idempotent, không có lý do data-integrity nào bắt
  phải đọc artifact hôm trước; đã sửa thành "report 16:00 CÙNG NGÀY".
  **4 câu hỏi §11:** (1) *Đọc gì/vintage?* file artifact local do chain 15:30 ghi — `orb_pt_status.json`
  (T), `pt_capitulation_state.json` + `papertrade_compare5.csv` (T-1); không đọc BQ/cache trực tiếp.
  (2) *Nguồn tươi lúc nào?* đo thật 10 log `papertrade_run_*.log`: chain START 15:30 → DONE **15:38-15:42**
  (worst 15:42, 12'). (3) *Cần T hay T-1?* report EOD paper — cần bản MỚI NHẤT chain vừa sinh; asof=T
  chỉ khả thi cho ORB, mục BQ chấp nhận T-1 (muốn T phải dời sang sau 23:45 = đổi bản chất báo cáo).
  (4) *Ai tiêu thụ/deadline?* user đọc Discord "Trading report", không có job downstream → không
  deadline cứng. **Buffer** 15:30+12'+18' = 16:00 (policy đòi runtime + ≥10'). **Xung đột:** không có
  cron nào trong khe 15:35-16:15 ICT. **Degrade an toàn:** chain chậm bất thường → report đọc artifact
  hôm trước = đúng hành vi cũ, không tạo failure mode mới; mỗi mục tự in `asof` nên đọc ra ngay.
  Kèm theo (cùng commit): nhãn header report đổi `Data as-of: <giờ chạy>` → `Render lúc: … — vintage
  dữ liệu xem asof từng mục` (nhãn cũ dễ khiến người đọc tưởng mọi số là của hôm nay); thêm trường
  `notes` VINTAGE vào registry entry `capitulation_shadow` + `engine_room_oos` giải thích sàn T-1.
  Cron đổi giữa ngày lúc 15:49 ICT → 16:00 hôm nay VẪN nổ (không nhảy khe), report 07-29 chạy 2 lần
  (15:20 bản cũ trễ + 16:00 bản đúng) — cố ý, để xác minh fix ngay trong ngày.

- 2026-07-20 (Mike, user approved trực tiếp): sau entry gốc bên dưới, cơ chế trải qua thêm 7 vòng
  quant-skeptic REFUTED→fix (tổng 10 vòng, chi tiết `kb/projects/deposit-rate-autocheck.md`) — luật
  "1 bài liệt kê đủ 4 ngân hàng = đối chiếu chéo" ở entry gốc đã bị loại bỏ (lỗ hổng N=1), thay bằng
  kiểm tra domain cơ học (`--sources` JSON, ≥2 nhóm sở hữu độc lập). Giữa chừng bị 1 phiên song song
  revert về chỉ-nhắc (lo ngại chi phí review), rồi user xem lại thiết kế CONFIRMED cuối + bug thật
  tìm được (`current_deposit_rate()` ghim sai khi có ngày tương lai/gõ nhầm) → quyết định bật lại
  (commit `49481e7`), kèm yêu cầu MỚI: Winston giờ LUÔN báo Trading Daily cùng ngày có kết quả (đổi
  hay không đổi), có dòng 🆕 highlight rõ đây là số mới — không còn quiet-heartbeat cho mục này.
  (⚠️ current-state bảng chính: auto-write sau đó lại bị loại bỏ, xem `authority_note` frontmatter.)
- 2026-07-20 (Mike, user approved trực tiếp — "để bạn tự động cập nhật thông tin mà không phụ
  thuộc tôi"): nâng cấp `refresh_deposit_rate_vn.sh` từ CHỈ-NHẮC sang tự-xác-nhận-và-ghi. Không
  còn dừng ở "nhắc con người chạy `append_deposit_rate.py`" — giờ tự dispatch Winston mỗi tháng để
  WebSearch-crosscheck lãi suất Big-4 12M kênh online qua ≥2 nguồn độc lập (hoặc 1 bài báo liệt kê
  đủ 4 ngân hàng cùng ngày, tự nó là đối chiếu chéo), CHỈ ghi khi đủ bằng chứng — nếu mâu thuẫn/thiếu
  bằng chứng thì escalate y hệt luồng cũ, không tự đoán. Thêm `--source web_crosscheck_auto` vào
  `append_deposit_rate.py` (bắt buộc `--note` non-empty, tách biệt khỏi `manual_verify` để giữ đúng
  provenance — không phải người trực tiếp xác nhận). Test end-to-end thật ngay trong phiên (không
  đợi cron ngày 3): Winston tìm được 3 nguồn (CafeF 18/7, Kenh14 16/7, CafeF 13/7) đều xác nhận
  6.8% — khớp record đã có sẵn cùng ngày (do Mike tự tay append trước đó) nên tự SKIP đúng
  (idempotent), không ghi trùng. 4 câu hỏi §11 không đổi so với entry gốc bên dưới (vẫn đọc
  `current_deposit_rate()` KHÔNG BQ/cache, vẫn chạy ngày 3 trước DCF gate ngày 11, vẫn KHÔNG cần T
  chính xác, vẫn consumer = `rating_8l.py` NEUTRAL tilt + `dcf_refresh_gate.py`) — chỉ đổi CƠ CHẾ
  ghi (agent-driven crosscheck thay vì chờ người), không đổi lịch/nguồn/consumer. Chi tiết đầy đủ +
  review đối kháng: `kb/projects/deposit-rate-autocheck.md`.
- 2026-07-17 (Taylor, job `Taylor_20260717_074106`, **user approved trực tiếp**): thêm 1 dòng cron
  `10 1 11 * *` (08:10 ICT ngày 11 hàng tháng) gọi `dcf_refresh_gate.py` — cổng refresh có điều kiện:
  recompute DCF **chỉ khi** lãi suất Big-4 12M dịch ≥1.0pp so lần dùng trước (boundary =1.0pp
  **INCLUSIVE** — CHỐT, flag `THRESHOLD_INCLUSIVE=True`, không còn "chờ user"); else giữ số cũ (SKIP).
  Gate chỉ QUYẾT ĐỊNH + PERSIST, không tự chạy recompute. 4 câu hỏi §11: (1) đọc
  `deposit_rate_vn.current_deposit_rate()` (as-of, step series) + prior state JSON — **KHÔNG BQ/cache**,
  granularity tháng nên không vintage-sensitive; (2) nguồn tươi phụ thuộc deposit-rate ngày 3 đã cập
  nhật (con người xác nhận số) → chạy ngày 11 để nằm SAU ngày 3; (3) KHÔNG cần T chính xác
  (`_now_ict_date` dùng UTC date, monthly-granularity vô hại); (4) consumer = whoever tái tạo số DCF
  cho report/dashboard, gọi `run_gate()` trước rồi chỉ recompute fair value khi `refresh=True` —
  reference tool, KHÔNG deadline pipeline hàng ngày. **Fail-safe:** mọi lỗi → `refresh=True` (recompute
  thay vì phục vụ stale trên gate hỏng). Ngày 11 > ngày 3 deposit; cùng phút 08:10 nhưng khác ngày →
  không trùng thực thi. First-run/no-state → REFRESH init. Selfcheck `dcf_refresh_gate_selfcheck.py`
  24/24 PASS. Đi kèm Việc A cùng job: default terminal-growth DISPLAY của `dcf_valuation.py` đổi
  CPI→`cap_rf` (level fix, không alpha — DCF non-decisional trong prod).
- 2026-07-17 (Winston, job `Winston_20260717_072420`, **user approved trực tiếp**): thêm 1 dòng cron
  `10 1 3 * *` (08:10 ICT ngày 3 hàng tháng) gọi `refresh_deposit_rate_vn.sh` — Layer A của
  `proposal_deposit_rate_monthly_refresh_20260713.md`. Script chỉ NHẮC (best-effort fetch CafeF/VCB
  timeout 15s hay fail, KHÔNG tự ghi) + post Discord + status bus; con người xác nhận số rồi chạy
  `append_deposit_rate.py` append vào `data/deposit_rate_vn_events.csv` (append-only, chỉ mốc
  effective_date > 2026-06-01 mới có hiệu lực). 4 câu hỏi §11: (1) đọc web external best-effort
  (CafeF/VCB, có thể fail) + `current_deposit_rate()` — **KHÔNG BQ/cache**; (2) nguồn Big-4 posted
  rate đổi bất thường, thường đầu tháng → chạy ngày 3 hợp lý, không cần T thật trong ngày; (3)
  KHÔNG cần T chính xác (tilt tần suất tháng, sai vài ngày vô hại); (4) consumer = `rating_8l.py`
  NEUTRAL tilt LIVE (đọc bất kỳ lúc nào có, không deadline cứng) + `dcf_refresh_gate.py` (dùng
  quanh ngày 11 → ngày 3 nằm trước). Không trùng phút với cron nào (08:00 commodity ngày 5/10 khác
  phút+ngày; 08:15 vcb_fx T2-T6). Freshness WARN >45 ngày ở `ops_health_check.sh` §8.
- 2026-07-15 (Winston, job `Winston_20260715_061920`, user duyệt dispatch): đổi giờ 3 cron đọc `dt5g_live` để luôn đọc regime HÔM NAY thay vì hôm qua (fix M3 audit `Winston_20260712_142100`): (1) `eod_trading_report.sh` 15:00→19:10 ICT (`0 8` → `10 12` UTC); (2) `pt_8l_daily.sh` 17:45→19:20 ICT (`45 10` → `20 12` UTC); (3) `telegram_run_daily.sh` 18:00→19:35 ICT (`0 11` → `35 12` UTC). Buffer sau publish DT5G ~19:01: eod 9', pt_8l 19', telegram 34'. Không trùng phút với nhau hoặc với bq_freshness 19:00. sector_lens_monitor.py step [9] vẫn đọc cache T-1 — user xác nhận KHÔNG CẦN SỬA, known limitation, chỉ ảnh hưởng công cụ nghiên cứu nội bộ, không chạm trading production.
- 2026-07-14 (Winston, job `Winston_20260714_160739`, **user directive trực tiếp — quy tắc vĩnh
  viễn mỗi quý**; **SỬA 2026-07-23, user directive trực tiếp**): thay 2 dòng T3 tạm thời (hết hạn
  08-04) bằng **1 dòng cron DAILY 20:00 ICT** gọi `mike/bin/fa_ratings_earnings_window_daily.sh`
  — wrapper tự gate: chỉ chạy thật khi **tháng ∈ {1,4,7,10} ∧ ngày ≥ 15 ∧ không lễ VN** (đã BỎ
  điều kiện T2-T6 ngày 2026-07-23 — user xác nhận qua bq_admin rằng `ticker_financial` vẫn được
  cập nhật kể cả Thứ Bảy/Chủ Nhật trong mùa BCTC, nên loại cuối tuần chỉ làm cohort chậm oan; công
  thức cửa sổ = từ 15 của tháng đầu quý đến hết tháng đó; điều kiện "ngày ≥ 15" là đủ vì date hợp
  lệ không vượt số ngày thật của tháng — không cần bảng số-ngày-từng-tháng/năm nhuận; lễ VN =
  `vn_market.is_holiday` fixed-list, lễ biến động Tết ÂL chưa encode → best-effort, ngày Tết chạy
  thừa vô hại). Trong cửa sổ: `refresh_fa_ratings_8l.sh` 20:00 → `refresh_fa_ratings.sh` 20:45
  (spacing 45' giữ nguyên mẫu Sat/T3-tạm). Ngoài cửa sổ: no-op im lặng (log skip-reason). Dòng Sat
  08:30/09:15 GIỮ NGUYÊN (baseline quanh năm) — **từ 2026-07-23, trong cửa sổ mùa BCTC, Thứ Bảy
  sẽ chạy CẢ 2 lần trong ngày (08:30/09:15 baseline + 20:00/20:45 window-run)**, vô hại (idempotent
  DELETE+INSERT/re-rank, khác giờ nên không trùng phút) chỉ tốn thêm 1 lượt BQ query/tuần trong
  cửa sổ; Chủ Nhật chỉ có window-run (20:00/20:45), không có baseline. Cửa sổ đầu tiên áp dụng đủ
  cuối tuần: **2026-07-23 → 2026-07-31** (07-15→07-22 đã chạy dưới gate cũ, bỏ lỡ 2 cuối tuần
  07-18/19). Gate test lại 2026-07-23 qua `--check YYYY-MM-DD`: 07-18/07-19/07-25/07-26 (cuối
  tuần trong cửa sổ) = RUN đúng; 07-14 (<15)/08-01 (ngoài quý)/04-30 (lễ VN) = SKIP đúng.
  4 câu hỏi §11: (1) đọc `ticker_financial` BQ live qua 2 wrapper con đã source `wc_env.sh`
  (identity fix `a9716f6`), ghi BQ `fa_ratings_8l`+`fa_ratings`; (2) nguồn tươi same-day ~17:30
  ICT → 20:00 bắt được filings trong ngày; (3) cần T same-day trong mùa cao điểm BCTC; (4)
  consumer = custom30 builder/DC-book/golive sizing/as-of joins, deadline = rebalance quý +
  cohort đầy dần từng ngày; trước sync cache 23:45 nên cache vớt bản mới ngay đêm đó.
- 2026-07-13 (Winston, job `Winston_20260713_103213`, user approved): thêm 2 dòng cron **TẠM THỜI
  mùa BCTC Q2** — refresh `fa_ratings_8l` (T3 20:00 ICT) + `fa_ratings` (T3 20:45 ICT), guard
  `[ $(date +%Y%m%d) -le 20260804 ]` ngay trong dòng cron → **tự no-op sau 2026-08-04**, xoá dòng
  chết khi tiện. Lịch chạy: 07-14, 07-21, 07-28, 08-04 — lần cuối đúng tối trước rebalance quý
  ~08-05 (đóng điểm nóng audit `Winston_20260713_100733` q6: mã công bố 08-02..08-04 sẽ kịp có Q2
  rating tại rebalance). 4 câu hỏi: (1) đọc `ticker_financial` BQ live, ghi BQ qua wrapper đã
  source `wc_env.sh` (identity fix `a9716f6`); (2) nguồn tươi same-day ~17:30 ICT → 20:00 bắt được
  filings trong ngày (hơn hẳn 08:30 sáng); (3) cần T same-day trong mùa cao điểm; (4) consumer =
  custom30 builder/DC-book/as-of joins, deadline rebalance ~08-05 15:30. Slot 20:00 trống (giữ chỗ
  cũ), tránh hẳn khung giao dịch sáng, trước sync cache 23:45 → cache (giờ full_only, cùng commit)
  vớt bản mới ngay đêm đó. Kèm cùng commit: `sync_bq_cache.py` chuyển `fa_ratings`/`fa_ratings_8l`
  sang `full_only` (delta-append không tương thích refresh DELETE+INSERT/re-rank — hết alert
  count-mismatch giả mỗi thứ Bảy).
- 2026-08-14: **thêm 1 dòng cron** `0 1 * * 1` = **08:00 ICT thứ Hai** —
  `fearbuy_weekly_scan.sh --mode monday` (job `Taylor_20260814_041116`, user duyệt §G
  `agents/Taylor/research/portfolio_wide_badnews_protection_20260814.md`). Cùng script với lượt
  thứ Sáu (thêm `--mode`), KHÔNG dựng script thứ hai. **Lý do phải ghi đúng kẻo hiểu nhầm về sau:
  bảo vệ PHÍA MUA, không phải "bán kịp"** — đo 10 năm cho thấy sau cú sập riêng lẻ thứ Hai thì
  fwd1 trung bình +0,02% (bán không cứu được gì), trong khi bot 09:05 thứ Hai lại đang đặt lệnh
  theo plan duyệt từ cuối tuần, tức trước khi tin cuối tuần tồn tại. 4 câu hỏi §11 trả lời đầy đủ
  trong ô "Đọc" của bảng chính. Cùng commit: cổng độ tươi `active_nav_*.json` trong
  `anomaly_scan.load_universe()` (§14 — cặp producer 20:15 / consumer 08:20 trước nay KHÔNG có
  precheck, producer chết 1 tối là quét sổ cũ trong im lặng) + watchlist sống thay danh sách mã
  chép cứng trong prompt lượt thứ Sáu.
- 2026-07-13: thêm second-chance 23:00 cho `send_plan_report.sh` (sự cố kb/INCIDENTS.md 2026-07-13
  root-cause 1: plan sửa/re-dispatch sau 21:00 không bao giờ được gửi lại duyệt). Script đã hỗ trợ
  `--second-chance`/`--dry-run` + marker idempotent `state/plan_report_sent/` (Winston, job
  `Winston_20260713_014816`). 4 câu hỏi §11: (1) đọc file plan local + marker, không BQ/cache;
  (2) plan tươi sau pipeline 19:00, re-dispatch muộn đo thật 22:17 (07-13); (3) cần bản mới nhất
  trên đĩa lúc chạy; (4) consumer = user duyệt qua đêm, deadline preflight 08:45. Dòng cron đề xuất
  (CHƯA cài, chờ Mike): `0 16 * * 1-5 /home/trido/thanhdt/WorkingClaude/mike/bin/for_each_live_account.sh /home/trido/thanhdt/WorkingClaude/mike/bin/send_plan_report.sh --second-chance >> /home/trido/thanhdt/WorkingClaude/mike/logs/send_plan_report.log 2>&1   # 23:00 ICT — second-chance gui lai plan T+1 bi sua sau 21:00 (idempotent, su co 2026-07-13)`
- 2026-07-12: seed v1 từ audit `Winston_20260712_142100` + `Winston_20260712_151206`. Xoá 1 dòng
  crontab dangling comment (`# V2.4 go-live flip`). Fix C1 (publish DT5G đọc live, commit `4995262`,
  quant-skeptic CONFIRMED — chi tiết sự cố: kb/incidents/2026-07/2026-07-12-audit-cron-order-publish-cache-t1.md). Fix H2 (shares_outstanding_live BLOCK→WARN, commit `6459b6d`). Điều tra
  `lag_edge_health.csv` "staleness" → kết luận KHÔNG phải bug (job `Taylor_20260712_155038`, xem
  `kb/current_ops.md`).

↩ [Về cron_registry (bảng chính)](../cron_registry.md) · [index nhóm _rules](index.md)
