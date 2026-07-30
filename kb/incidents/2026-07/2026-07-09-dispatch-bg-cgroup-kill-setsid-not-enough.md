---
kind: incident
date: 2026-07-09
topic: dispatch-bg-cgroup-kill-setsid-not-enough
title: >-
  2026-07-09 — dispatch --bg jobs chết theo cgroup của caller (bridge restart giết job "background") — setsid KHÔNG đủ, phải tách cgroup bằng systemd-run --scope
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-09 — dispatch --bg jobs chết theo cgroup của caller (bridge restart giết job "background") — setsid KHÔNG đủ, phải tách cgroup bằng systemd-run --scope

**Phát hiện**: Taylor (job `Taylor_20260709_012737`): mọi `dispatch.sh --bg` spawn con
trong cgroup của caller — khi caller là `ccdb-mike.service` (bridge Discord) restart,
systemd giết TOÀN BỘ pid trong cgroup (`KillMode=control-group`, default), job đang
chạy chết ngay, record kẹt `status=running` vĩnh viễn (không finalize). Evidence:
`Taylor_20260708_170202` chết đúng timestamp "Stopping ccdb-mike" 2026-07-09 00:28:15.
Cùng dạng lỗi lần 3 trong 3 ngày (07-07 agent-wrapper-monitor-gap; 07-09 sáng
`DollarBill_20260709_125326` sync-mode bị Bash-tool 2-min timeout giết, record cũng kẹt).

**Root cause (verify bằng thí nghiệm thật, Wags job `Wags_20260709_134401`)**: `setsid`
(dòng spawn cũ) chỉ tách SESSION, không tách CGROUP — child qua setsid vẫn nằm
`.../ccdb-mike.service` (đọc `/proc/<pid>/cgroup`). Negative control: fake parent
service + setsid child → `systemctl --user stop` parent → child CHẾT. Với
`systemd-run --user --scope` child nằm cgroup riêng `run-*.scope` → cùng kịch bản stop
→ child SỐNG, wrapper finalize record `done` bình thường.

**Fix (`bin/dispatch.sh`, Wags 2026-07-09)**:
1. `_detached_spawn()`: mọi spawn nền của nhánh --bg (`_bg_wrapper` + `_job_watcher`)
   đi qua `systemd-run --user --scope --quiet --collect --description="mike-dispatch
   <job_id>"` — cgroup riêng, sống độc lập với caller (bridge/Bash tool/cron). Probe
   runtime 1 lần/dispatch; fallback setsid (hành vi cũ) khi không có systemd-run/user
   manager; escape hatch `DISPATCH_CGROUP_DETACH=0`. Env + exported functions truyền
   qua --scope như fork thường (verify thật). Middleman systemd-run chết theo caller
   nhưng KHÔNG forward TERM cho child (verify thật).
2. Nhánh sync: trap TERM/INT/HUP finalize record (`status=failed exit_code=143`,
   summary "KILLED... bởi trap") thay vì kẹt `running` khi dispatch.sh bị kill giữa
   chừng. Best-effort (SIGKILL không trap được); bash defer trap đến khi claude-child
   thoát — bounded bởi `--timeout` vì `timeout(1)` vẫn giết claude đúng hạn.
3. Watcher lifetime cap (quá deadline worst-case +15' → alert 🧟 1 lần rồi dừng) — vì
   watcher giờ sống độc lập theo thiết kế, không được bất tử + heartbeat giả khi record
   kẹt do wrapper bị SIGKILL/OOM.

**Verify**: Test A end-to-end trên đường spawn thật (`DISPATCH_CLAUDE_BIN` fake, fake
bridge service): job --bg sống qua `systemctl --user stop` fake-bridge, record finalize
`done` + result_summary đúng. Test B: kill process-group dispatch sync → record
finalize `failed/143` với summary KILLED (job test `Winston_20260709_135131` /
`Winston_20260709_135425` — TEST, ignore khi đọc job board). Regression smoke --bg
thường: PASS. Lưu ý vận hành: scope hiện ra trong `systemctl --user list-units
'run-r*'` với description `mike-dispatch <job_id>` — triage được job sống bằng systemd,
không chỉ ps/HB_AGE.

**Bài học**: (1) "background" thật sự = tách cả LIFETIME (cgroup), không chỉ
session/terminal — mọi daemonization dưới systemd service với KillMode mặc định đều
phải nghĩ đến cgroup; (2) pgrep -f khi chính argv của shell chứa pattern → tự khớp
mình (đã tự giết shell test 1 lần trong lúc verify) — dùng pidfile.
