---
kind: coding-guideline-topic
title: "Pipelines, Bash Prompts, and Cron Health Check (§14, §15, §29)"
owner: Mike
status: canonical
updated: 2026-11-27
---

# Pipelines, Bash Prompts, and Cron Health Check (§14, §15, §29)

> Tách nguyên văn từ [`../coding_guidelines_ext.md`](../coding_guidelines_ext.md) (2026-11-27, giữ trần <40 KB).

## 14. Every Internal Producer→Consumer Pipeline Pair Needs a Real Freshness Check, Not Just a Loose Tolerance

**Rule:** when a script's output feeds another script on its own cron schedule (not triggered by the
producer finishing), don't trust "producer already ran by the time I run" on schedule alone:
- Add a **real freshness precheck** in the consumer: read the producer's own timestamp/marker (a
  `_asof`/`_generated_at` field, file mtime, a `*_ok` flag) and confirm it's from *today's* run —
  not just "a file exists" or "cron order says it should be done by now." Schedule assumptions
  drift; a precheck is the only thing that catches it.
- Set the tolerance **as tight as the real risk allows** — wide enough for normal jitter (a job
  finishing 5 minutes late), tight enough that a full day's staleness (or a full skipped run) trips
  it. `MAX_STATE_LAG=2` days is the concrete anti-pattern.
- Cron schedule change on either side of a pair: folded into §11's mandatory 4 questions
  (`kb/cron_registry.md`) — treat "does the consumer verify freshness or just trust timing" as part
  of answering, not a separate step.
- Applies to ANY internal producer→consumer relationship on independent cron schedules — not just
  BQ/DNSE, not just DT5G. Same reasoning as §6/§9: verify the artifact, don't infer it from schedule
  math.

**Not a mandate to retrofit every existing pair at once** — apply going forward on every new/changed
cron pair (§11); a periodic sweep of *existing* pairs is Friday KB editorial review material.

*→ rationale §14.*

### 14b. Consumer cron KHÔNG được đồng bộ với producer bằng ĐỒNG HỒ — phải CHỜ ARTIFACT, có trần, fail loud

**Luật:** một consumer chạy theo cron riêng **không được** dựa vào thứ tự giờ với producer
("producer 19:00, mình 19:05 là xong"). Nó phải **chờ artifact**: file tồn tại + `mtime` = hôm nay
(giờ VN), poll định kỳ, có **trần thời gian**, hết trần thì **fail LOUD** (nêu rõ đã chờ bao lâu,
trần bao nhiêu, file nào, producer nào — §29), **không** âm thầm chạy trên dữ liệu phiên trước.
Cơ chế dùng sẵn: `bin/wait_for_artifact.sh <file> "<producer hint>"` (mặc định poll 30s, trần 10
phút; uỷ quyền phép so ngày cho `bin/csv_fresh_today.sh` đã neo TZ). Giờ cron vẫn đặt sau producer
— nhưng chỉ là **thắt lưng an toàn**, không phải cơ chế đồng bộ.

**Khi đăng ký cron (§11) phải ghi vào `kb/cron_registry.md`: INPUT file cụ thể + PRODUCER job nào
ghi ra nó.** Không viết được 2 thứ đó ⇒ chưa đủ hiểu để chọn giờ.

**Vì sao §14 (văn xuôi, có từ 2026-08) KHÔNG ngăn được sự cố 2026-09-12** — đây mới là phần đáng nhớ:
`hit_details_daily.sh` được đăng ký 19:05 "sau `bq_freshness_check` 19:00", trong khi producer thật
sự ghi `golive_v23_recommendations_<date>.csv` lúc **19:06-19:07**. Hậu quả ĐO ĐƯỢC (không suy đoán):
lần chạy cron đầu tiên 2026-09-11 chết với `Không thấy .../golive_v23_recommendations_2026-09-11.csv`,
exit 1 — **không post Discord, không sinh artifact**, thất bại chỉ nằm trong `logs/hit_details_daily.log`
mà không checker nào đọc ⇒ với người dùng, job đơn giản là *không tồn tại*. (Consumer này hỏi file
theo NGÀY TƯỜNG MINH nên chết to; một consumer lấy "file mới nhất" bằng glob — như chính nhánh default
của `hit_details.py` — sẽ âm thầm chạy trên PHIÊN TRƯỚC và ra số sai mà không ai biết. Cả hai đều là
cùng một lỗi gốc.) Người đăng ký đã đọc §11 và §14. Ba lỗ hổng cơ chế, đã vá:
1. Registry + policy chỉ ghi giờ **BẮT ĐẦU** của producer ("recommendations tươi sau pipeline
   19:00"). Giờ bắt đầu không phải mốc tươi. Đã sửa mốc trong
   `kb/cron_registry/_adding-cron-policy.md` thành giờ **artifact sẵn sàng** (đo bằng `mtime` thật).
2. "Thêm freshness precheck" là việc phải TỰ NGHĨ RA mỗi lần ⇒ bỏ qua vì tưởng giờ cron đã đủ. Giờ
   là một dòng gọi script có sẵn + selfcheck (`bin/wait_for_artifact_selfcheck.py`).
3. Ước lượng runtime của producer bằng cảm tính, không ai đo. Vòng chờ artifact làm phép ước lượng
   đó **không còn load-bearing**: producer chậm 60s hay 6 phút, consumer vẫn đúng.

*Sự cố: job `Wags_20260912_052122`, bus `Mike/hit-details-daily-chay-truoc-producer-2-phut`.*

## 15. Bash Strings Doubling as LLM Prompts: Escape `"`/`` ` ``, Then Verify by Running, Not Reading

Both `"` and `` ` `` are live bash metacharacters even inside double quotes (unlike single quotes) —
an unescaped one silently terminates the string or triggers real command substitution.

**Rule:**
1. Any `"` or `` ` `` inside a bash double-quoted string must be escaped (`\"`, `` \` ``) — no
   exceptions, even for text that "looks like it's just prose."
2. **Prefer a single-quoted heredoc** (`<<'EOF'`) for large prompt-text bodies when you don't need
   variable interpolation — zero escaping of either character (pattern: `bin/weekly_ops_audit.sh`).
   If you DO need `$VAR` interpolation, either accept the escaping burden or hardcode the
   (usually-fixed) absolute paths as literal text.
3. **Verify by running, not by reading.** Re-reading "looks fine" is how all 4 instances shipped — a
   quote 40 lines into an 80-line string is not something a re-read catches. Extract the
   assignment/heredoc in isolation and execute it before trusting a fix.

**Enforced by:** `bin/shellcheck_gate.sh` (pre-commit hook) — ShellCheck detects this exact pattern
for free (`SC1078`/`SC1079` unterminated/suspicious string quote, `SC2006` legacy backtick where
`$(...)` was intended, `SC2261` competing redirections — the downstream symptom when a quote break
leaves stray text mid-command). No custom rule needed; the fix was turning ShellCheck ON as a hard
gate with a curated code list (its own header explains why curated, not "any finding," and why
`SC2154` was tried and dropped — false positives on `hooks/*.sh`'s cross-file `source` chains).

*Why: 4 real incidents 2026-07-17 → 2026-08-01 in `daily_retro.sh`, `kb_nightly.sh`,
`fleet_housekeeping.sh` — crash before `notify.sh` ran, corrupted-but-launched dispatch
(`dispatch.sh` got extra args), bash running the quoted text as a command. Evaluated and NOT shipped:
a Semgrep rule for §12 (tested on `bin/verify_account_snapshot.py`; needs dataflow-aware engineering
to hit "fires twice at 100% accuracy"). → rationale §15.*

⚠️ **Gap `bin/shellcheck_gate.sh` KHÔNG phủ tới: dispatch gõ trực tiếp trong phiên tương tác
(Bash tool call của Mike, không phải file `.sh` được commit).** Hook chỉ chạy ở `pre-commit` —
một lệnh `bin/dispatch.sh Taylor "... \`code_snippet\` ..."` gõ thẳng vào Bash tool KHÔNG BAO GIỜ
đi qua git commit, nên ShellCheck không bao giờ thấy nó. Ca thật: 2026-08-15 00:41Z, job
`Taylor_20260815_004105` — 2 đoạn code (`` `_limit_price` ``, `ref_price = anchor/1.04`) biến mất
khỏi prompt vì backtick bị bash coi là command substitution NGAY TRONG lệnh Bash tool, trước khi
`dispatch.sh` kịp nhận `$2`. Không có cách nào vá phía `dispatch.sh` — hư hại xảy ra ở shell của
NGƯỜI GỌI. Rule + template cụ thể cho tình huống này (không lặp lại nội dung):
**`~/.claude/skills/dispatch-prompt-heredoc/SKILL.md`** — đọc trước bất kỳ dispatch tương tác nào
mang theo backtick/`"`/code snippet, và ngay khi thấy "command not found" xuất hiện sát một lệnh
dispatch (đó là dấu hiệu, không phải lỗi không liên quan).

## 29. `cron_health_check.py` Báo Lại Cùng 1 Lỗi Mỗi Ngày Dù Đã Sửa — Ack List + Bidirectional Date, Không Phải Trust-The-Report

Triage 2026-08-16 (user: "mỗi ngày đều có warning... là warning thật hay báo động giả?") tìm ra
**cả 6 mục trong `ERRORS_FOUND` hôm đó đều là báo động giả — bug thật đã được sửa từ trước**
(`discover_sessions.py` ENAMETOOLONG, commit `03419973` 2026-08-15; `trading_bot/config.py`
git-stash-conflict-marker ×3 log, đã đóng cùng ngày trong `kb/incidents/2026-08/
2026-08-14-git-stash-conflict-markers-giet-bot-ca-2-account.md`). Root cause KHÔNG phải bug
logic trading — là 2 lỗ hổng trong chính checker + hạ tầng log:

1. **`mike/logs/*.log` không có cơ chế rotate cho log ghi tĩnh-tên-mãi-mãi** (`discover.log` mỗi
   10 phút, `ops_health.log`/`preflight.log`/`paper_main_probe_plan.log` mỗi phiên
   `for_each_live_account.sh`) — dòng lỗi CŨ nằm mãi trong 200KB tail mà `scan_errors()` quét,
   dù bug gốc đã sửa từ lâu. `fleet_housekeeping.sh` CÓ category `rotate` nhưng ngưỡng `>10MB`
   quá cao cho nhóm file này (discover.log mới 1,7MB, `paper_main_probe_plan.log` chỉ vài chục KB
   — sẽ không bao giờ chạm ngưỡng dù mang lỗi hàng chục ngày tuổi).
2. **`scan_errors()`'s recency filter chỉ nhìn NGƯỢC (look-behind)** — nếu dòng lỗi là dòng ĐẦU
   file, hoặc mốc ngày gần nhất nằm SAU (không phải trước) dòng lỗi, filter không bao giờ lọc
   được nó dù đã quá `RECENT_DAYS=10`. Ca thật: `newdeals_daily_report.log` giữ 1 lỗi
   `2026-07-06` (41 ngày tuổi) sống sót qua ngưỡng 10 ngày chỉ vì mốc ngày nằm 3 dòng SAU dòng
   traceback. Đã vá: tìm mốc ngày gần nhất CẢ HAI CHIỀU (`nearest_date()`).
3. **`cron_health_check_daily.sh` post lại TOÀN BỘ report thô ra Discord mỗi ngày, không có bộ
   nhớ triage** — đây là nguyên nhân trực tiếp của "ngày nào cũng có": dù Mike/user đã xác nhận
   1 mục là báo động giả hôm qua, hôm nay checker chạy lại từ đầu, không biết gì về xác nhận đó,
   và post lại y hệt.

**Cơ chế đã thêm (không phải chỉ sửa 1 lần cho xong):**
- `state/cron_health_ack.json` — mỗi entry khai `script` + `match_substr` (text PHẢI xuất hiện
  trong 1 trong các dòng lỗi bắt được của job đó) + `acked_at`/`acked_by`/`expires_days`/`note`
  (bắt buộc trích commit/incident file làm bằng chứng, không ghi "đã kiểm tra" suông). `find_job_ack()`
  khớp ở granularity CẢ JOB (không phải từng dòng riêng) — 1 traceback thường sinh nhiều dòng hit
  khác nhau (dòng header chung "Traceback (most recent call last):" + dòng exception cụ thể); ack
  đúng dòng exception nhưng bỏ sót dòng header chung sẽ để lại 1 dòng vẫn báo động (bug thật gặp
  khi build cơ chế này — xem comment `find_job_ack()`).
- Ack có **HẠN** (`expires_days`, mặc định 14) — hết hạn tự động coi như CHƯA ack, để lỗi thật
  còn sống lại tự trồi lên thay vì bị im lặng vĩnh viễn. Ack là SNOOZE, không phải tắt cảnh báo.
- Thêm pattern regex bắt dòng exception Python thật (`^\s*\w+(Error|Exception):` — vd
  `SyntaxError:`, `ValueError:`) — pattern cũ `^\s*Error:` chỉ khớp "Error:" trần, bỏ sót MỌI
  tên class exception thật, khiến dòng hit duy nhất bắt được luôn là header chung vô nghĩa.

**Thêm 1 ack mới khi triage xong 1 lỗi đã xác nhận sửa**: sửa `state/cron_health_ack.json`, chọn
`match_substr` = đoạn text ĐẶC TRƯNG nhất THẬT SỰ xuất hiện trong output của `python3
bin/cron_health_check.py` (không đoán — chạy thử trước, xem đúng dòng nào bị bắt), ghi rõ commit/
incident file làm bằng chứng trong `note`. KHÔNG ack dựa trên "nhìn log thấy quen" — phải verify
artifact thật (đúng tinh thần §6/§9/§14/§28).

*→ job `Taylor_20260809_123917`.*
