---
kind: incident-index
title: Incidents — Mike fleet (sổ postmortem, cấu trúc OKF)
owner: Mike fleet (mọi agent ghi; daily_retro.sh ghi entry RETRO hằng đêm)
format: OKF (Open Knowledge Format) — markdown + YAML frontmatter, 1 sự cố = 1 file
migrated_from: kb/INCIDENTS.md (single-file 408KB, migrate → OKF 2026-07-30 job Winston_20260730_144031)
entries: 102 file (71 sự cố + 30 RETRO + 1 mục open-items chung)
---

# Incidents — Mike fleet

Blameless postmortem log (Google SRE convention): what broke, why, the fix, the lesson.
Every entry traces to a verifiable artifact (commit hash, bus event, memory file) — no
incident is recorded from memory alone. Newest first.

**When to add an entry:** anything that broke a live workflow, cost real money/time, or
required a human to intervene outside the normal happy path — not every bug, and not
things caught in review before they ever ran (that's a normal fix, not an incident).

**Format:** Date · What happened · Root cause · Fix · Lesson (with a `[[memory-link]]` or
commit hash where one exists).

> 4 đoạn trên là nguyên văn phần đầu `kb/INCIDENTS.md` trước migrate — quy tắc ghi entry
> KHÔNG đổi, chỉ đổi chỗ chứa (1 sự cố = 1 file thay vì 1 file 408KB).

## Cấu trúc thư mục

| Thư mục | Nội dung |
|---|---|
| [`2026-08/`](2026-08/) | Sự cố tháng 8/2026 — tên file `YYYY-MM-DD-<topic>.md` |
| [`2026-07/`](2026-07/) | Sự cố tháng 7/2026 — tên file `YYYY-MM-DD-<topic>.md` |
| [`2026-06/`](2026-06/) | Sự cố tháng 6/2026 |
| [`retro/`](retro/) | Entry **RETRO** hằng ngày (tổng hợp/phân loại sự cố cả ngày do `bin/daily_retro.sh` sinh) — `retro-YYYY-MM-DD.md` |
| [`_open-not-yet-hardened.md`](_open-not-yet-hardened.md) | Mục "Open / not-yet-hardened" — việc đã biết còn hở, chưa gắn với 1 sự cố cụ thể nào |

**Vì sao tách `retro/`:** RETRO là văn bản META (tổng hợp nhiều sự cố trong 1 ngày, 1 file/ngày),
không phải bản thân sự cố. Tách ra để ai tra 1 sự cố cụ thể không bị digest cuối ngày lấn át
(đúng vấn đề `incident_lookup.py` từng phải xử lý bằng chuẩn hoá density).

**Vì sao nhóm theo THÁNG (không theo loại lỗi):** cách tra thực tế của fleet luôn bắt đầu từ
NGÀY (`grep '^## 2026-07-29'`, "sự cố hôm 07-06", retro đọc `--since <ngày>`), còn "loại lỗi" đã
có trường `Phân loại` (category) trong chính các entry RETRO và tra được bằng grep nội dung.
Nhóm theo tháng giữ nguyên trục tra sẵn có, không bắt ai học cây phân loại mới.

## Cách tra (grep vẫn hoạt động y như trước)

```bash
# theo ngày
ls mike/kb/incidents/2026-07/ | grep 2026-07-06
# theo từ khoá, toàn bộ sổ
grep -rn "loanPackageId" mike/kb/incidents/
# tra tự động theo từ khoá (dùng bởi ops_autofix.sh / wags_autofix.sh)
python3 mike/bin/incident_lookup.py "<label>" "<details>"
```

## Frontmatter mỗi file

`kind` (incident/retro/open-items) · `date` · `topic` (slug) · `title` (nguyên văn tiêu đề cũ) ·
`status` · `source`.

⚠️ **`status` được gán CƠ HỌC khi migrate**, không phải phán đoán: `open-items` = thân bài có
chứa dấu hiệu văn bản "CÒN MỞ / CÒN TREO / VẪN TREO / chưa được sửa / CHƯA ĐÓNG"; `logged` =
không chứa. Nó KHÔNG có nghĩa "đã đóng hoàn toàn" — muốn biết fix còn hở hay không thì đọc thân
bài (mục "còn hở/residual/Prevention"). Đừng dùng trường này làm cổng tự động.

## Entry mới ghi vào đâu

- Sự cố mới → tạo file `incidents/<YYYY-MM>/<YYYY-MM-DD>-<topic>.md` (tạo thư mục tháng nếu
  chưa có), frontmatter như trên, rồi thêm 1 dòng vào bảng dưới.
- RETRO hằng ngày → `incidents/retro/retro-<YYYY-MM-DD>.md` (`bin/daily_retro.sh` bước 3/3 đã
  trỏ vào đây; trước 2026-07-30 nó append vào cuối `kb/INCIDENTS.md`).


## Sự cố (mới nhất trước)

### 2026-08

| Ngày | Sự cố | status |
|---|---|---|
| 2026-08-11 | [2026-08/2026-08-11-plan-dd-check-string-poll-fail.md](2026-08/2026-08-11-plan-dd-check-string-poll-fail.md) | ? |
| 2026-08-11 | [2026-08/2026-08-11-funding-gate-chan-oan-khi-restart-phien-chieu.md](2026-08/2026-08-11-funding-gate-chan-oan-khi-restart-phien-chieu.md) | ? |
| 2026-08-04 | [2026-08/2026-08-04-paper-main-netted-evidence-silent-8-days.md](2026-08/2026-08-04-paper-main-netted-evidence-silent-8-days.md) | fixed (monitoring); production-code fix in progress (Taylor job Taylor_20260804_094514) |
| 2026-08-11 | [2026-08-11: FUNDING gate chặn OAN ZaloPay khi restart phiên chiều (rc=3) — gate cộng Σ mua trên TOÀN BỘ `orders[]` (108,2tr) thay vì phần CÒN LẠI sau fills buổi sáng (27,2tr vs pp0Buy 60,5tr); bot ZaloPay không chạy cả phiên chiều, TV1 200cp còn open](2026-08/2026-08-11-funding-gate-chan-oan-khi-restart-phien-chieu.md) | escalated (chưa vá — gate tiền thật, vùng cấm Winston) |
| 2026-08-11 | [2026-08-11: plan ghi `dd_check` dạng CHUỖI (08-07/08-10 là dict) ⇒ `_sync_fills` ném `'str' object has no attribute 'get'` sau MỖI fill — 22 POLL_FAIL ZaloPay + 27 SpaceX, chặn đặt lệnh 1 chu kỳ/lần fill; fail-safe hoạt động đúng, không mất tiền](2026-08/2026-08-11-plan-dd-check-string-poll-fail.md) | escalated (chưa vá — điểm vá nằm ở `load_plan()`/executor, vùng cấm Winston) |
| 2026-08-10 | [2026-08/2026-08-10-funding-gate-multipackage-shared-pot-false-block.md](2026-08/2026-08-10-funding-gate-multipackage-shared-pot-false-block.md) | ? |
| 2026-08-04 | [2026-08/2026-08-04-paper-main-netted-evidence-silent-8-days.md](2026-08/2026-08-04-paper-main-netted-evidence-silent-8-days.md) | fixed (monitoring); production-code fix in progress (Taylor job Taylor_20260804_094514) |
| 2026-08-10 | [2026-08-10: FUNDING gate chặn oan plan ZaloPay đã duyệt — cộng tỉ lệ tiêu thụ của 2 gói vay DÙNG CHUNG một hũ tiền (cash-only) ⇒ báo 105,6% trong khi thật là 54,6%; mất cửa sổ LAG ngày 3/3 của DRI/POW/SCL](2026-08/2026-08-10-funding-gate-multipackage-shared-pot-false-block.md) | escalated (chưa vá — nới gate tiền thật, cần user/Taylor + quant-skeptic) |
| 2026-08-07 | [2026-08/2026-08-07-plan-rewrite-drops-user-approval.md](2026-08/2026-08-07-plan-rewrite-drops-user-approval.md) | ? |
| 2026-08-07 | [2026-08/2026-08-07-plan-merge-left-stale-jit-orders-double-sell.md](2026-08/2026-08-07-plan-merge-left-stale-jit-orders-double-sell.md) | ? |
| 2026-08-04 | [2026-08/2026-08-04-paper-main-netted-evidence-silent-8-days.md](2026-08/2026-08-04-paper-main-netted-evidence-silent-8-days.md) | fixed (monitoring); production-code fix in progress (Taylor job Taylor_20260804_094514) |
| 2026-08-07 | [2026-08-07: script sửa plan sau khi user đã duyệt LÀM MẤT `approved_by` → bot chặn cả 2 account giữa phiên chiều; lộ lỗ hổng chiều ngược lại (sửa `orders[]` mà giữ duyệt) hiện KHÔNG có gate nào bắt](2026-08/2026-08-07-plan-rewrite-drops-user-approval.md) | escalated (cần user duyệt lại); đề xuất `approved_orders_hash` CHƯA vá |
| 2026-08-04 | [2026-08/2026-08-04-paper-main-netted-evidence-silent-8-days.md](2026-08/2026-08-04-paper-main-netted-evidence-silent-8-days.md) | fixed (monitoring); production-code fix in progress (Taylor job Taylor_20260804_094514) |
| 2026-08-04 | [2026-08/2026-08-04-paper-main-netted-evidence-silent-8-days.md](2026-08/2026-08-04-paper-main-netted-evidence-silent-8-days.md) | fixed (monitoring); production-code fix in progress (Taylor job Taylor_20260804_094514) |
| 2026-08-04 | [2026-08/2026-08-04-paper-main-netted-evidence-silent-8-days.md](2026-08/2026-08-04-paper-main-netted-evidence-silent-8-days.md) | fixed (monitoring); production-code fix in progress (Taylor job Taylor_20260804_094514) |
| 2026-08-04 | [2026-08/2026-08-04-crontab-wipe-cross-call-pid-tmpfile.md](2026-08/2026-08-04-crontab-wipe-cross-call-pid-tmpfile.md) | fixed |
| 2026-08-03 | [2026-08-03: check #5 dispatch LẶP wags_autofix cho câu hỏi đã triage là "chỉ NGƯỜI quyết được" — ranh giới WARN-ONLY bám TUỔI 48h thay vì TRẠNG THÁI triage; thêm ACK `triaged-needs-human:`](2026-08/2026-08-03-coord-question-redispatch-triaged-ack.md) | fixed |
| 2026-08-02 | [daily_nav_snapshot.py đếm 2 lần cổ tức tiền mặt vào tối ngày chốt quyền (last-cum-date) — NAV lịch sử SpaceX/ZaloPay sai 6 dòng trên 5 phiên, tự triệt tiêu nên sống sót mọi đối soát](2026-08/2026-08-02-nav-cum-dividend-double-count.md) | fixed |
| 2026-08-02 | [2026-08/2026-08-02-lag-liquidity-fidelity-two-fixes.md](2026-08/2026-08-02-lag-liquidity-fidelity-two-fixes.md) | ? |
| 2026-08-02 | [2026-08-02: lần thứ 5 "message các topic Discord lẫn lộn" — bỏ vá từng lớp, chuyển sang registry duy nhất + pre-commit gate chặn ID trần](2026-08/2026-08-02-discord-channel-registry.md) | fixed |
| 2026-08-02 | [2026-08-02: 5 job failed "Reached max turns (50)" in one day, all attempt 2/2 with an unchanged cap — added effort-scaled defaults + auto-continuation with a bumped ceiling](2026-08/2026-08-02-max-turns-auto-continuation.md) | fixed |
| 2026-08-02 | [2026-08-02: claude-code-discord-bridge (shared infra, every Claude session on the account) found 115 commits / 3+ weeks behind origin, incl. 3 unpatched security fixes — merged + fixed](2026-08/2026-08-02-ccdb-bridge-115-commits-behind-upstream.md) | fixed |
| 2026-08-02 | [2026-08-02: saga "PE có look-ahead giá điều chỉnh" — phép nhân Price/Close sai sống 6 tuần trong rating_8l.py (từ 06-24), bị bác bỏ bằng kiểm định trong-kỳ-hằng-số rồi khôi phục; lần 2 fleet suy diễn nhầm từ 1 quan sát đúng vì test trên dữ liệu gần đây](2026-08/2026-08-02-pe-price-close-adjustment-saga.md) | fixed |
| 2026-08-02 | [2026-08-02: user noticed "Mike seems to stop / not follow topics" — root cause is /api/notify silently dropping ~10 messages/3 days on oversized embeds, one bug fixed, one flagged unfixed](2026-08/2026-08-02-notify-api-silent-message-loss.md) | partially-fixed |
| 2026-08-01 | [2026-08-01: MAX_TURNS missing from --bg export list — every background dispatch fleet-wide broken for ~1h10m, caught mid-research by Mike, root-caused via bash -x trace, fixed same-turn](2026-08/2026-08-01-dispatch-max-turns-export-missing-bg-broken.md) | fixed |
| 2026-08-01 | [2026-08-01: ShellCheck pre-commit gate — đẩy bài học quoting sang công cụ, tìm+sửa thêm 1 bug thật thứ 4](2026-08/2026-08-01-shellcheck-precommit-gate.md) | fixed |
| 2026-08-01 | [2026-08-01: audit toàn bộ crontab (64 dòng) — 1 bug thật mới (kb_nightly.sh backup.sh) + 9 log-observability gap + cron_health_check.py mới](2026-08/2026-08-01-full-crontab-audit-cron-health-check.md) | fixed |
| 2026-08-01 | [2026-08-01: kb_nightly.sh Friday/Saturday editorial dispatch silently FAILED every week since 07-17 — 2 unescaped-quote bugs](2026-08/2026-08-01-kb-nightly-friday-dispatch-silently-broken-2-weeks.md) | fixed |
| 2026-08-01 | [2026-08-01: daily_retro.sh crashed silently 2 đêm liên tiếp (07-31, 08-01) — bug quoting do chính commit migrate OKF gây ra](2026-08/2026-08-01-daily-retro-quoting-bug-silent-2day-outage.md) | fixed |
| 2026-08-01 | [2026-08-01: báo cáo tuần/tháng chết 2 tuần liền — WARN chạy đúng nhưng bị chôn trong ops_health_check 4 lần/ngày, không ai action](2026-08/2026-08-01-weekly-monthly-report-dead.md) | fixed |

### 2026-07

| Ngày | Sự cố | status |
|---|---|---|
| 2026-07-31 | [2026-07-31: `capit_fired` bị hiểu nhầm là "đang giữ vị thế" khiến mọi kênh báo cáo im lặng về CAPIT từ 07-29 dù vẫn giữ đủ 5 mã; + 1 lần artifact 07-30 bị ghi đè bởi sai interpreter](2026-07/2026-07-31-capit-status-visibility-gap-interpreter-overwrite.md) | open-items |
| 2026-07-30 | [2026-07-30: paper-trading report "báo không hoạt động" — 3 root causes tìm + sửa cùng phiên (không phải 1 bug, 3 bug độc lập chồng lên nhau)](2026-07/2026-07-30-paper-trading-report-3-root-causes.md) | logged |
| 2026-07-29 | [2026-07-29: daily_retro root-cause fix — session-directory collision (Pattern A closed)](2026-07/2026-07-29-daily-retro-session-directory-collision.md) | open-items |
| 2026-07-28 | [2026-07-28 — `spacex-loanpackageid-order-reject`: SpaceX (margin) TV1 buy orders bị DNSE từ chối `HTTP 400: loanPackageId is required` suốt ~30' phiê…](2026-07/2026-07-28-spacex-loanpackageid-order-reject.md) | logged |
| 2026-07-27 | [2026-07-27/28: KB-ingestion pipeline mất event âm thầm 9h, rồi chuỗi fix của chính nó gây thêm 2 lớp mất event mới — 5 vòng review độc lập trước khi …](2026-07/2026-07-27-kb-ingestion-pipeline-mat-event.md) | logged |
| 2026-07-21 | [2026-07-21 — ZaloPay run_bot rc=1: 5 lệnh MUA CAPIT mất + executor seed_shared crash](2026-07/2026-07-21-zalopay-run-bot-rc1-capit-seed-shared.md) | logged |
| 2026-07-21 | [2026-07-21 — `eod_trading_report.sh` cross-account contamination: báo SAI mismatch cho CẢ SpaceX lẫn ZaloPay (lần 3 của cùng 1 bug class, KHÔNG được …](2026-07/2026-07-21-eod-trading-report-cross-account-contamination.md) | logged |
| 2026-07-20 | [2026-07-20 — `missed-wakeup-after-bg-dispatch`: Mike dispatch 2 job `--bg` rồi trả lời câu hỏi khác trong CÙNG lượt, không `ScheduleWakeup` → 2 job x…](2026-07/2026-07-20-missed-wakeup-after-bg-dispatch.md) | logged |
| 2026-07-17 | [2026-07-17 — Preflight depth-check báo động giả "ticker_prune moi ruột" vì upstream ETL ghi dở partition hôm nay ngay trong phiên](2026-07/2026-07-17-preflight-depth-check-false-alarm-ticker-prune.md) | logged |
| 2026-07-17 | [2026-07-17 — Model-tier drift: fable đi từ 0%→58% dispatch trong 3 tuần, compute wall-clock +150% dù job count -76% (user hỏi "token tăng dù không re…](2026-07/2026-07-17-model-tier-drift-fable.md) | logged |
| 2026-07-15 | [2026-07-15 — ticker_prune cũng bị corruption upstream (mở rộng sự cố ticker_financial 07-14): rows 07-08→07-14 bị xóa/ghi đè, daily_refresh 07-14 ABO…](2026-07/2026-07-15-ticker-prune-corruption-upstream.md) | logged |
| 2026-07-15 | [2026-07-15 — Preflight RED giả MAFEE_NOT_AUTH trên plan đã duyệt thật (tái diễn bug 07-06) — fix vĩnh viễn ở checker](2026-07/2026-07-15-preflight-false-red-mafee-not-auth.md) | logged |
| 2026-07-14 | [2026-07-14 — ZaloPay mất plan ngày 07-14: dispatch DollarBill timeout ×2, attempt 2 chỉ được nửa thời gian](2026-07/2026-07-14-zalopay-mat-plan-dispatch-timeout.md) | logged |
| 2026-07-13 | [2026-07-13 — Unapproved ZaloPay plan (2 real-money orders) was 35 minutes from executing; approval turned out to be procedure-only, not code-enforced](2026-07/2026-07-13-unapproved-zalopay-plan-approval-not-code-enforced.md) | logged |
| 2026-07-13 | [2026-07-13 — DT5G refresh thứ Sáu 07-10 KHÔNG chạy: dời giờ cron cùng ngày rơi đúng khe hở giữa slot cũ và slot mới](2026-07/2026-07-13-dt5g-refresh-missed-cron-time-change.md) | logged |
| 2026-07-12 | [2026-07-12 — `lag_edge_health.csv`: 2 tiền đề sai liên tiếp về "bug staleness/catch-up" bị bác bỏ sau điều tra sâu — không có bug thật, tốn 2 chu kỳ …](2026-07/2026-07-12-lag-edge-health-2-tien-de-sai.md) | logged |
| 2026-07-12 | [2026-07-12 — golive_recommend_v23 (money-path) hardcode w_LAG=65% vô điều kiện, lệch edge-conditional gate của pinned R3 — gây REBALANCE flag GIẢ trê…](2026-07/2026-07-12-golive-recommend-v23-hardcode-wlag.md) | logged |
| 2026-07-12 | [2026-07-12 — Audit cron-order (Winston_20260712_142100) bắt 2 bug production-blocking cùng lúc: C1 CRITICAL publish DT5G qua cache T-1 thay vì live, …](2026-07/2026-07-12-audit-cron-order-publish-cache-t1.md) | logged |
| 2026-07-12 | [2026-07-12 — Audit sẵn sàng BCTC Q2/2026 bắt LAG live-candidate pipeline mù sự kiện mới <30 phiên (R1 CRITICAL) + freshness ticker_financial bị 1 mã …](2026-07/2026-07-12-audit-bctc-q2-lag-blind-new-events.md) | logged |
| 2026-07-11 | [2026-07-11 — fa_ratings_8l weekly-refresh wrapper bắt đúng 1 lần BQ write "thành công giả" (silent write failure) khi test tay bằng identity read-onl…](2026-07/2026-07-11-fa-ratings-8l-silent-write-failure.md) | logged |
| 2026-07-11 | [2026-07-11 — 4 lần dispatch bị hard-timeout giữa việc nặng (Fable-model, đa bước) dù fix "heartbeat-aware deadline" (2026-07-09) đã có hiệu lực — khô…](2026-07/2026-07-11-dispatch-hard-timeout-4-jobs-fable.md) | logged |
| 2026-07-10 | [2026-07-10 (sáng sớm) — `ops_health_check.sh` không bao giờ clear được câu hỏi trả lời bởi agent KHÁC người hỏi — checker match answer PER-FILE, bus …](2026-07/2026-07-10-ops-health-check-answer-per-file.md) | logged |
| 2026-07-10 | [2026-07-10 (chiều) — DollarBill tự tính sai ngày T+1: thứ Sáu → "ngày mai" = thứ Bảy (không phải ngày giao dịch), đáng lẽ phải là thứ Hai — 2 lần dis…](2026-07/2026-07-10-dollarbill-t1-date-friday-saturday.md) | logged |
| 2026-07-10 | [2026-07-10 — DollarBill lập plan luôn đọc DT5G của HÔM QUA — thứ tự cron bị đảo ngược](2026-07/2026-07-10-dollarbill-plan-doc-dt5g-hom-qua.md) | logged |
| 2026-07-10 | [2026-07-10 (đêm) — retro dời giờ theo lịch EOD mới + dọn 1 va chạm lịch phụ](2026-07/2026-07-10-cron-move-retro-eod-collision.md) | logged |
| 2026-07-09 | [2026-07-09 — TCM odd-lot remainder (10cp) silently stranded forever under a misleading "WAIT_QUOTA" reason — round_lot() bug, not a DNSE restriction](2026-07/2026-07-09-tcm-odd-lot-stranded-round-lot-bug.md) | logged |
| 2026-07-09 | [2026-07-09 — run_bot fail-branch báo ❌ giả + dispatch ops_autofix khi cron lunch-pkill 11:30 dừng bot theo lịch (rc=143)](2026-07/2026-07-09-run-bot-false-fail-lunch-pkill.md) | logged |
| 2026-07-09 | [2026-07-09 (tối) — dispatch hard-timeout giết agent ĐÃ XONG VIỆC (lần 2), trước khi nó kịp return — dẫn tới heartbeat-aware deadline](2026-07/2026-07-09-dispatch-hard-timeout-killed-finished-agent.md) | logged |
| 2026-07-09 | [2026-07-09 — dispatch --bg jobs chết theo cgroup của caller (bridge restart giết job "background") — setsid KHÔNG đủ, phải tách cgroup bằng systemd-r…](2026-07/2026-07-09-dispatch-bg-cgroup-kill-setsid-not-enough.md) | logged |
| 2026-07-08 | [2026-07-08 — ZaloPay INVALID_OTP lúc 09:05: race Gmail-OTP giữa 2 cron cùng giây, chung login DNSE — bot tự hồi phục qua heartbeat autoheal, nhưng lộ…](2026-07/2026-07-08-zalopay-invalid-otp-race-gmail.md) | logged |
| 2026-07-07 | [2026-07-07 (tối) — NAV ZaloPay sai LẦN 2 cùng ngày: balance chụp giữa 2 cú khớp](2026-07/2026-07-07-nav-zalopay-sai-lan-2-balance-giua-2-khop.md) | logged |
| 2026-07-07 | [2026-07-07 — EOD report đăng NAV ZaloPay -98,25% (17,5tr) lên Trading report](2026-07/2026-07-07-eod-nav-zalopay-minus-98.md) | logged |
| 2026-07-07 | [2026-07-07 (chiều) — agent-wrapper-monitor-gap: Agent(isolation:worktree) dùng nhầm làm "background wrapper", Mike mất tín hiệu hoàn tất job — lần 2 …](2026-07/2026-07-07-agent-wrapper-monitor-gap.md) | logged |
| 2026-07-06 | [2026-07-06 — Two wrong "end-of-day market price" sources, same day, both caught by user](2026-07/2026-07-06-two-wrong-eod-price-sources.md) | logged |
| 2026-07-06 | [2026-07-06 — Taylor's completion notification leaked into whichever topic Mike was in, not the one that asked](2026-07/2026-07-06-taylor-notification-wrong-topic.md) | logged |
| 2026-07-06 | [2026-07-06 (later same day) — Executor didn't know T+2-purchased shares aren't sellable until the afternoon session](2026-07/2026-07-06-t2-shares-not-sellable-until-afternoon.md) | logged |
| 2026-07-06 | [2026-07-06 (đêm) — macro_health false-SEV1: mảnh ghép cuối — cache sync chết âm thầm 2 bug](2026-07/2026-07-06-macro-health-false-sev1-cache-sync-dead.md) | logged |
| 2026-07-06 | [2026-07-06 (evening) — Lunch-stop `pkill` self-matched its own cron-invoking shell](2026-07/2026-07-06-lunch-stop-pkill-self-match.md) | logged |
| 2026-07-06 | [2026-07-06 — Live ops sweep for the day (user asked "is anything still wrong"), found a third, unrelated bug: false SEV1 in the DT5G macro health-che…](2026-07/2026-07-06-live-ops-sweep-false-sev1-macro-health.md) | logged |
| 2026-07-06 | [2026-07-06 — Fast-wake-on-completion rule wrongly excluded long research fan-out chains](2026-07/2026-07-06-fast-wake-rule-excluded-research-fanout.md) | logged |
| 2026-07-06 | [2026-07-06 (late afternoon) — Today's EOD report never posted + NAV computation broke on the first SELL-only day](2026-07/2026-07-06-eod-report-missing-nav-sell-only-day.md) | logged |
| 2026-07-06 | [2026-07-06 — Cross-account balance contamination: EOD report posted a WRONG NAV to Discord](2026-07/2026-07-06-cross-account-balance-contamination.md) | logged |
| 2026-07-06 | [2026-07-06 — Approved plan v2 would have been silently skipped for stale v1 (caught ~15 min before execution)](2026-07/2026-07-06-approved-plan-v2-skipped-for-stale-v1.md) | logged |
| 2026-07-03 | [2026-07-03 — Client-facing weekly report used an estimated field as real cost basis, flipped a position's sign](2026-07/2026-07-03-weekly-report-estimated-cost-basis.md) | logged |
| 2026-07-03 | [2026-07-03 — Real margin debt went unreported (stale point-in-time claim) AND a dispatched agent fabricated its "verification"](2026-07/2026-07-03-margin-debt-unreported-fabricated-verification.md) | logged |
| 2026-07-02 | [2026-07-02 — Double-buy: 2 concurrent bot_execute.py processes fill the same plan 2x](2026-07/2026-07-02-double-buy-concurrent-bot-execute.md) | logged |
| 2026-07-02 | [2026-07-02 — Background dispatch job died when the coordinator's own session restarted](2026-07/2026-07-02-bg-dispatch-died-with-coordinator-restart.md) | logged |
| 2026-07-01 | [2026-07-01 — Go-live day-1: 5 bugs, none caught by rehearsal](2026-07/2026-07-01-golive-day1-5-bugs.md) | logged |

### 2026-06

| Ngày | Sự cố | status |
|---|---|---|
| 2026-06-27 | [2026-06-27/28 — Taylor↔Winston auto-callback ping-pong (runaway dispatch loop)](2026-06/2026-06-27-taylor-winston-callback-pingpong.md) | logged |
| 2026-06-22 | [2026-06-22 — Mafee ZOMBIE: systemd reports healthy, agent isn't actually serving](2026-06/2026-06-22-mafee-zombie-systemd-healthy.md) | logged |

## RETRO hằng ngày (mới nhất trước)

| Ngày | Tóm tắt (nguyên văn tiêu đề) | status |
|---|---|---|
| 2026-08-11 | [RETRO — 2026-08-11: 5 sự cố, 2 pattern xuyên suốt (state_source escalated 2 retro liên tiếp, hôm nay fix THẬT nhưng SAU khi đã gây 30 lệnh lỡ phiên)](retro/retro-2026-08-11.md) | logged |
| 2026-08-10 | [RETRO — 2026-08-10: 7 sự cố, 3 pattern xuyên suốt (1 pattern ĐÃ ESCALATE ngày trước, VẪN chưa có quyết định sau retro thứ 3 liên tiếp — 1 pattern MỚI khẩn: SpaceX T+1 mất tích, tái diễn hình dạng sự cố ngày trước)](retro/retro-2026-08-10.md) | logged |
| 2026-08-09 | [RETRO — 2026-08-09: 7 sự cố, 4 pattern xuyên suốt (2 ĐẠT NGƯỠNG ESCALATE — 1 tiếp tục theo mục 6, 1 mới nhưng đủ nghiêm trọng để nêu bật ngay dù chưa đạt ngưỡng cứng)](retro/retro-2026-08-09.md) | logged |
| 2026-08-08 | [RETRO — 2026-08-08: 1 sự cố mới, 1 đóng thành công (Pattern 1 test-bus-pollution FIXED_VERIFIED cùng ngày), 1 pattern quy trình MỚI formal hoá (backlog ghi file kb/incidents/ — 4 retro liên tiếp chưa từng có Prevention)](retro/retro-2026-08-08.md) | logged |
| 2026-08-07 | [RETRO — 2026-08-07: 11 sự cố, 4 pattern xuyên suốt (1 ESCALATE — test-code-pollutes-bus tái diễn sau khi đã formal hoá + đề xuất Prevention ở retro 08-05 mà chưa triển khai)](retro/retro-2026-08-07.md) | logged |
| 2026-08-06 | [RETRO — 2026-08-06: 8 sự cố, 4 pattern xuyên suốt (2 pattern đóng đúng nhờ escalate hôm qua, 0 escalate mới)](retro/retro-2026-08-06.md) | logged |
| 2026-08-05 | [RETRO — 2026-08-05: 4 sự cố, 3 pattern xuyên suốt (2 pattern ĐẠT NGƯỠNG ESCALATE)](retro/retro-2026-08-05.md) | logged |
| 2026-08-02 | [RETRO — 2026-08-02: 7 sự cố, 2 pattern xuyên suốt (1 tiếp tục ESCALATED từ 07-28/08-01, 1 MỚI nêu bật, +1 sự cố bổ sung sau verify độc lập của Wags)](retro/retro-2026-08-02.md) | logged |
| 2026-08-03 | [RETRO — 2026-08-03: 5 sự cố (1 đã ghi trước, 4 bổ sung), 2 pattern xuyên suốt (1 CẢI THIỆN nhưng CHƯA về 0 — wakeup compliance dao động ngược; 1 TIẾP TỤC chờ xác nhận đa chu kỳ)](retro/retro-2026-08-03.md) | logged |
| 2026-08-04 | [RETRO — 2026-08-04: 2 sự cố ghi trước + 1 mục theo dõi liên-ngày, 1 pattern xuyên suốt (recovery-not-prevention), wakeup compliance VỀ 0% — Pattern 1 từ retro 08-03 ĐÓNG](retro/retro-2026-08-04.md) | logged |
| 2026-08-01 | [RETRO — 2026-08-01: 6 sự cố đã ghi + 2 gap chưa ghi, 3 pattern xuyên suốt (1 escalate)](retro/retro-2026-08-01.md) | open-items |
| 2026-07-29 | [RETRO — 2026-07-29: 4 sự cố, 1 pattern xuyên suốt tái diễn (data-registry-accuracy), 0 vi phạm §8 wakeup](retro/retro-2026-07-29.md) | open-items |
| 2026-07-28 | [RETRO — 2026-07-28: 3 sự cố, 1 pattern xuyên suốt CỰC KỲ QUAN TRỌNG (retro pipeline tự nó chết lặng 4 ngày 07-24→07-27, đúng lúc pattern funding_requ…](retro/retro-2026-07-28.md) | open-items |
| 2026-07-23 | [RETRO — 2026-07-23: 0 sự cố mới, 0 pattern mới (ngày sạch — 1 near-incident đã tự xác định NOT-A-BUG cùng ngày, khớp tiền lệ 07-20)](retro/retro-2026-07-23.md) | open-items |
| 2026-07-22 | [RETRO — 2026-07-22: 4 sự cố, 1 escalation ĐÓNG (cross-account-contamination), 1 pattern MỚI cần theo dõi (git-commit-blocked-by-classifier, đã 2 ngày…](retro/retro-2026-07-22.md) | open-items |
| 2026-07-21 | [RETRO — 2026-07-21: 2 sự cố, 1 pattern tái diễn (RETRO callout lần 2 — escalate), 1 lượt thiếu ScheduleWakeup (4,3%, tự phục hồi, không cần entry riê…](retro/retro-2026-07-21.md) | open-items |
| 2026-07-20 | [RETRO — 2026-07-20: 6 sự cố (2 phát hiện qua chính retro hôm nay bị Wags audit bắt lỗi ban đầu bỏ sót — xem "Đã sửa sau audit Wags" cuối entry), 3 pa…](retro/retro-2026-07-20.md) | open-items |
| 2026-07-19 | [RETRO — 2026-07-19: 1 sự cố (đã fix+verify trong ngày, chưa có entry đầy đủ trước retro — gap báo cáo tự bổ sung), 1 pattern TÁI DIỄN từ follow-up bỏ…](retro/retro-2026-07-19.md) | open-items |
| 2026-07-18 | [RETRO — 2026-07-18: 1 sự cố (phát hiện bởi chính retro hôm nay, chưa từng ghi trước — gap báo cáo), 1 pattern TÁI DIỄN dưới dạng MỚI của agent-wrappe…](retro/retro-2026-07-18.md) | open-items |
| 2026-07-17 | [RETRO — 2026-07-17: 2 sự cố (cả 2 đã có entry đầy đủ trước retro, 0 gap báo cáo), 2 pattern liên quan — 1 MỚI (cost-governance) tự bắt bởi user chứ k…](retro/retro-2026-07-17.md) | open-items |
| 2026-07-16 | [RETRO — 2026-07-16: 0 sự cố, 0 pattern mới (ngày sạch — chuỗi 5 ngày liên tiếp data-registry-accuracy 07-11→07-15 KHÔNG kéo dài sang hôm nay)](retro/retro-2026-07-16.md) | open-items |
| 2026-07-15 | [RETRO — 2026-07-15: 3 sự cố (1 GAP báo cáo — chưa ai ghi trước retro, retro tự bổ sung), 1 pattern xuyên suốt (data-registry-accuracy) ĐẠT điều kiện …](retro/retro-2026-07-15.md) | open-items |
| 2026-07-14 | [RETRO — 2026-07-14: 3 sự cố (1 đã có entry đầy đủ trước retro, 2 GAP mới do retro tự bổ sung), 1 pattern xuyên suốt TÁI DIỄN LẦN 3 với bằng chứng cụ …](retro/retro-2026-07-14.md) | open-items |
| 2026-07-12 | [RETRO — 2026-07-12: 4 sự cố (3 bug thật production-blocking đã tự bắt+tự sửa trước khi gây hại, 1 chuỗi tiền đề chẩn đoán sai không gây hại nhưng tốn…](retro/retro-2026-07-12.md) | logged |
| 2026-07-11 | [RETRO — 2026-07-11: 2 sự cố (cả 2 đều là GAP báo cáo — bus có bằng chứng nhưng chưa từng ghi vào INCIDENTS.md trước retro này), 1 pattern xuyên suốt …](retro/retro-2026-07-11.md) | open-items |
| 2026-07-10 | [RETRO — 2026-07-10: 3 sự cố, 1 pattern tái diễn dưới dạng MỚI (ESCALATE lần 2), 1 pattern mới lần đầu](retro/retro-2026-07-10.md) | open-items |
| 2026-07-10 | [RETRO — 2026-07-10 (bổ sung đóng entry — job gốc `Mike_20260710_150001` báo "failed" dù nội dung đã đúng: "Reached max turns (50)" ngay trước bước 8-…](retro/retro-2026-07-10-bo-sung.md) | open-items |
| 2026-07-09 | [RETRO — 2026-07-09: 7 sự cố, 2 pattern xuyên suốt tái diễn từ trước, prevention cũ chưa đủ](retro/retro-2026-07-09.md) | logged |
| 2026-07-09 | [RETRO — 2026-07-09 (cron 22:00, chạy lần đầu qua `bin/daily_retro.sh`): 9 sự cố tổng trong ngày, 1 sự cố mới phát hiện sau bản RETRO thủ công lúc chi…](retro/retro-2026-07-09-cron.md) | open-items |
| 2026-07-07 | [RETRO — 2026-07-07: 3 recurring failure patterns behind today's incidents](retro/retro-2026-07-07.md) | logged |

> Các ngày KHÔNG có entry RETRO trong file gốc: 2026-07-08, 07-13, 07-24, 07-25, 07-26, 07-27.
> Chuỗi 07-24→07-27 chính là "daily-retro pipeline tự nó chết lặng 4 ngày" — xem Sự cố 2 trong
> [RETRO 07-28](retro/retro-2026-07-28.md). Đây là ghi nhận trạng thái file gốc, KHÔNG phải mất
> mát khi migrate (69/69 entry gốc đã chuyển đủ, verify diff-based).

