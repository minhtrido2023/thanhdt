# Working memory — Wags
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Wags.

## Vai trò
Fleet Ops Coordinator (COO) — điều phối & độ tin cậy vận hành GIỮA các agent team Mike.
KHÔNG phải daemon — chỉ chạy khi Mike dispatch (kiến trúc 1-daemon, xem MIKE.md).

## Công cụ chính
- bin/jobs.sh list — cột HB_AGE (mới 2026-07-07): heartbeat bus cuối của job đang chạy.
  HB_AGE nhỏ = agent SỐNG dù LOG_AGE lớn (log chỉ ghi khi claude thoát). HB_AGE '-' hoặc
  >180s trên job running = nghi treo THẬT → bin/trace.sh <job_id> xem timeline.
- bin/trace.sh <job_id> — gộp job record + mọi bus event cùng trace_id.
- state/circuit/<id>.json — circuit breaker per-agent; bus/pending_resumes/ — usage-limit queue.

## Bài học nền (2026-07-07, lý do sinh ra Wags)
User hỏi "task Winston treo rồi phải không?" — thực tế job SỐNG (heartbeat mỗi phút) nhưng
log 0-byte 11 phút nhìn như treo. Root cause: LOG_AGE là tín hiệu sai cho liveness; đã fix
bằng cột HB_AGE. Pattern cần theo dõi tiếp: job chẩn đoán sâu (ops_autofix 900s) hay cần
attempt 2 — cân nhắc đề xuất timeout dài hơn cho label autofix hay chia nhỏ prompt.

- [2026-07-07T08:01:38Z] Vai trò: Fleet Ops Coordinator — điều phối & độ tin cậy vận hành GIỮA agent (không đụng trading). Công cụ: jobs.sh list (HB_AGE = liveness thật, LOG_AGE vô dụng khi đang chạy), trace.sh <job_id>, state/circuit/, bus/pending_resumes/.
XONG 2026-07-07: ops-autofix-timeout-sizing (job Wags_20260707_075643) — ops_autofix.sh 900s cứng → AUTOFIX_TIMEOUT env default 1800 (commit 0b2e46a, sandbox test 3/3 PASS, finding trên bus, chờ arch-reviewer audit). Bằng chứng: Winston_20260707_072729 attempt1 kill đúng 900s khi heartbeat còn tươi, attempt2 làm lại 694s.
Pattern theo dõi tiếp: (1) nếu kill-agent-đang-sống tái diễn → cân nhắc heartbeat-aware deadline trong dispatch.sh (đã ghi deferred_idea trong finding); (2) DollarBill 2 lần treo/timeout khi lập plan transition ZaloPay 07-06 tối — chưa điều tra, ứng viên việc kế tiếp nếu Mike dispatch.
- [2026-07-07T14:36:28Z] Vai trò: Fleet Ops Coordinator — điều phối & độ tin cậy vận hành GIỮA agent (không đụng trading). Công cụ: jobs.sh list (HB_AGE = liveness thật), trace.sh, state/circuit/, bus/pending_resumes/.
XONG 2026-07-07 (job Wags_20260707_142752): agent-wrapper-monitor-gap — root cause 2 tầng: isolation:worktree ≠ background (agent đồng bộ, msg cuối là kênh duy nhất) + harness Fable-5 đã BỎ run_in_background khỏi Agent schema trong khi MIKE.md §8/dispatch.sh vẫn in template đó. Fix commit fb15ac0: snippet dispatch.sh viết lại (CHÍNH=ScheduleWakeup poll 240-270s; wrapper chỉ khi schema thật có tham số nền; self-check jobs.sh status trước mọi phát ngôn), MIKE.md §8 SỬA 2026-07-07, INCIDENTS.md entry. Chờ arch-reviewer audit.
XONG trước đó cùng ngày: ops-autofix-timeout-sizing (commit 0b2e46a, đã CONFIRMED).
Pattern theo dõi tiếp: (1) schema-drift harness = nguồn lỗi mới — sau mỗi lần Mike restart/đổi model, soát các template tool-call in sẵn trong tooling (dispatch.sh, runbook); (2) DollarBill 2 lần treo/timeout khi lập plan transition ZaloPay 07-06 tối — chưa điều tra, ứng viên việc kế tiếp.
- [2026-07-08T01:24:47Z] Vai trò: Fleet Ops Coordinator — điều phối & độ tin cậy vận hành GIỮA agent (không đụng trading). Công cụ: jobs.sh list (HB_AGE = liveness thật), trace.sh, state/circuit/, bus/pending_resumes/.
XONG 2026-07-08 (job Wags_20260708_012007): coord-ZaloPay-2026-07-08 — 2 question wags-fix-not-confirmed hoá ra BÁO ĐỘNG GIẢ: notify_thread.sh leak {status:sent} ra stdout, pipeline wags_autofix tail -1 parse nhầm thành verdict '?' dù arch-reviewer đã CONFIRMED 2s trước. Fix commit c9ac96c (_notify_arch câm stdout cả 2 chỗ + parser chọn dòng JSON có key verdict thay tail -1), test 4/4, đã post 2 answer dọn question giả, checker section-5 pending_q=[] sạch. Chờ arch-reviewer audit.
Pattern theo dõi tiếp: (1) stdout-hygiene trong tooling — script nào echo JSON làm giao thức PHẢI silence stdout của mọi lệnh phụ (notify/append_event); rà thêm chỗ khác dùng tail -1 parse output nếu gặp lỗi tương tự; (2) DollarBill 2 lần treo/timeout khi lập plan transition ZaloPay tối 07-06 — chưa điều tra, ứng viên việc kế tiếp.
- [2026-07-08T01:27:26Z] Vai trò: Fleet Ops Coordinator — điều phối & độ tin cậy vận hành GIỮA agent (không đụng trading). Công cụ: jobs.sh list (HB_AGE = liveness thật), trace.sh, state/circuit/, bus/pending_resumes/.
XONG 2026-07-08 (job Wags_20260708_012013, coord-SpaceX): 2 question wags-fix-not-confirmed = FALSE ALARM — notify_thread.sh stdout {status:sent} lẫn vào tail -1 verdict parse của wags_autofix.sh (job song song 012007/coord-ZaloPay đã vá commit c9ac96c + answer 2 question). Job này vá lỗi tầng 2: ops_health_check.sh label coord-${ACCOUNT}-${TODAY} → coord-${TODAY} (COORD_WARN là fleet-wide, label per-account lách cooldown gây 2 job Wags song song đụng độ edit) — commit 61ecb98 (bị consolidator quét vào commit consolidate).
Pattern theo dõi tiếp: (1) consolidator auto-commit quét working-tree change chưa commit của tooling — attribution lẫn + rủi ro commit code dở tay, ứng viên đề xuất giới hạn consolidator chỉ add kb/; (2) cooldown wags_autofix TOCTOU nếu checker chuyển parallel; (3) DollarBill 2 lần treo/timeout plan transition ZaloPay 07-06 tối — vẫn chưa điều tra; (4) schema-drift harness sau restart/đổi model — soát template tool-call in sẵn.
