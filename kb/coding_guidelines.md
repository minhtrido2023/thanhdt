# Coding Guidelines — áp dụng cho toàn fleet

Behavioral guidelines to reduce common LLM coding mistakes.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

**Two-tier structure (split 2026-08-08).** THIS file = the rule, its enforcement mechanism, and
every number/threshold/path a rule depends on. The originating incident story and the
considered-then-rejected alternatives live in **`kb/coding_guidelines_rationale.md`** (not
auto-injected; read it when you need WHY, or before changing/removing a rule) or in the
`kb/incidents/` entry each section points to. Adding a new lesson: narrative goes straight to the
rationale file — **cut narrative, never cut a fact**.

**Enforcement policy (2026-08-01, user mandate — "đẩy bài học cũ ra công cụ/linter thay vì văn
xuôi"):** any lesson expressible as a MECHANICAL pattern in code → make it an automated check that
blocks the commit, not another paragraph; always test a new rule against real files before turning
it on. Live mechanism, verified by
a real `git commit`: **`bin/shellcheck_gate.sh`** (pre-commit hook, ShellCheck — caught all 4 real
quoting incidents 2026-07-17→08-01, see §15 +
`kb/incidents/2026-08/2026-08-01-shellcheck-precommit-gate.md`). One-time setup per repo (hook shared
by all worktrees): `pip install --user pre-commit shellcheck-py && pre-commit install`.
§7, §10, §11, §13 are process/judgment calls with no clean syntactic pattern to lint — prose is the
right form for them, not an oversight.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently; weak criteria ("make it work") don't.

## 5. Idempotent Side Effects

**Any script that can be killed mid-run and re-run must not repeat an external action.** Fixed in
`trading_bot/executor.py` (`_ghost_tickers` + atomic `_save_state`); apply the same reasoning to
every new script that calls an external system with a side effect (place an order, send a message,
write a shared file, call a non-idempotent API):
- Ask: "killed right after the external call succeeds but before local state is saved — what does
  the next run do?" Answer "repeats the action" = a bug, not an edge case.
- Prefer the external system's own source of truth (broker's live order book, the sent-messages
  log) over local state — local state can lag reality.
- Can't tell whether an action already happened → **fail-safe pause and flag for a human**; don't
  guess-and-merge, don't silently proceed.
- Persist "the action happened" immediately after the external call, not batched at loop end.
- Writes to shared state files must be atomic (`tmp` + `os.replace`/`os.rename`), never a direct
  overwrite — a kill mid-write must never leave a half-written file for the next run to trust.

*→ `kb/incidents/2026-07/2026-07-02-double-buy-concurrent-bot-execute.md`.*

**§5b. Selfcheck chạm `Executor` PHẢI đặt `MIKE_BOT_TEST_MODE=1`** — same class of "side effect to
an external system", but the external channel here is the BUS:
`trading_bot/executor.py::_publish_bot_event()` calls `mike/bin/append_event.sh Mafee ...` directly
from 6 sites (`GHOST_ORDER_DETECTED`, `LEVER_PACKAGE_UNAUTHORIZED`, `dcf-rich-fill`,
`dd-redflag-fill`, `STEP_FAIL`, `fill_lagging`).
- Guard lives in `_publish_bot_event()` (fixed 2026-08-08): return early when
  `MIKE_BOT_TEST_MODE == "1"` **or** `PYTEST_CURRENT_TEST` is set. `MIKE_BOT_TEST_EVENT_SINK=<path>`
  (optional) writes blocked events to a file so tests can still assert "this should have fired".
- **Any NEW selfcheck importing `Executor`** → one line at the top of the file, BEFORE any
  `Executor` is constructed: `os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")`. This is the ONLY
  prevention against a 5th recurrence — a new selfcheck's author has no way to know otherwise.
- **Never infer "this is a test" from an existing field** (`account` label, `plan_date` sentinel
  2099-*, `strategy="selfcheck"`): all 3 were inventoried and all 3 are inconsistent across
  selfcheck files (`capit_lever_selfcheck.py` deliberately uses the REAL labels;
  `paper_main_window_selfcheck.py` uses a real `plan_date=TODAY`). The gate must be an EXPLICIT
  env var.
- **`PYTEST_CURRENT_TEST` does NOT cover `test_trading_bot.py`** (runs as a script, no `def test_*`).

*→ rationale §5b.*

## 6. Verify Report Data Provenance (client-facing numbers)

**A field's name and a plausible-looking value are not verification.** Before any number reaches a
report (daily/weekly/monthly, or any client-facing artifact):
- Trace it to the *authoritative* system — for fills, the broker's confirmation
  (`dnse_raw_*.jsonl`'s `averagePrice`/`fillQuantity`), never a downstream summary file.
- Cross-check a second independent source (journal `FILL` events, an audited snapshot);
  `bin/verify_account_snapshot.py` is the only script permitted to compute cost-basis/P&L for a
  SpaceX report. Disagreement beyond a tight tolerance → fail loudly, don't pick one silently.
- Aggregate totals can be right while per-item attribution is wrong (NAV uses quantity × market
  price, not cost basis).
- Same principle as [[verify-real-facts-dont-self-invent]] / MIKE.md §Quy chuẩn bắt buộc mục 2:
  verify the artifact, don't trust a plausible-looking field.

**Standing pipeline for ALL cadences, locked 2026-07-03:**
1. `bin/verify_account_snapshot.py` — true cost basis/ticker (broker raw vs journal vs snapshot).
2. `bin/daily_nav_snapshot.py` — true NAV/date (MTM stock + real cash − margin debt from a fresh
   `dnse_raw_*.jsonl` `balances` record), appended to `nav_history_{account}.csv`.
3. `bin/reconcile_equity.py` — identity check (`starting_capital + unrealized_P&L − fees −
   margin_interest == market_value + cash − margin_debt`); fee rate **0.075%** of true cost basis
   (not 0.1%, corrected 2026-07-03); residual checked against *estimated* margin accrual
   (`--margin-rate-annual`, 12.5%/yr per user, unverified against DNSE's contract) before calling
   it "unexplained."
4. Can't trace a number through this pipeline → don't put it in the report, say what's missing.

**Bright-line rule — same-day data: DNSE API, never BigQuery (user directive, 2026-07-09).** BQ
(`tav2_bq.ticker`/`ticker_1m`) syncs overnight only (`sync_bq_cache_daily.sh`, 23:45 ICT) — a
"today" query before that sync structurally reads **yesterday's** close.
- Any same-day/live calc (order sizing, T+1 ref prices, live NAV/exposure) MUST read DNSE
  (`dnse_api.py` secdef/latest_trade/positions/balances) — never BQ, regardless of hour.
- BQ OK only for: (a) historical/backtest queries, (b) same-day queries AFTER BQ's sync has
  demonstrably completed (verify via `bq_freshness_check.sh`'s gate, don't assume by clock time).
- In dispatch prompts (DollarBill etc.): state as unconditional MUST with a concrete wrong-vs-right
  example (see `bq_freshness_check.sh`'s DollarBill prompt).

**Cadence-specific scope** (depth differs; the pipeline above does not): **Daily** = trades today,
NAV + day-over-day change, margin/risk flag if any. **Weekly** = full narrative, template
`mike/reports/SpaceX_weekly_report_*.md` (activity log, incident disclosures, sector/position
tables, next-week plan, methodology appendix). **Monthly** = institutional conventions on top
(MTD/QTD/YTD, benchmark comparison, attribution, risk metrics, fee/expense summary, compliance
disclosures, outlook).

*→ rationale §6.*

## 7. Onboarding a New Account With Legacy/Excluded Holdings

**When an account brought under management already holds positions the bot didn't buy**, use the
general mechanism; more accounts of this shape are expected:

1. **Declare in config, not code**: `"excluded_tickers": [...]` on the account's profile in
   `secrets/trading_bot_accounts.json` (`ACCOUNT_DEFAULTS` in `trading_bot/config.py`).
2. **Enforcement in ONE place**: `trading_bot.plan.filter_excluded_tickers()`, called from
   `bot_execute.py` right after `load_plan()` — applies however the plan was generated
   (DollarBill's LLM JSON, `bot_prepare_plan.py`'s template, a hand-edited file), so a plan
   generator forgetting the exclusion can never place a forbidden order.
3. **Size against `active_nav`, not total NAV**: `bin/compute_active_nav.py --account <label>`
   computes `total_nav − market_value(excluded_tickers)` from LIVE broker positions/prices — no
   dependency on our execution journal, unlike `verify_account_snapshot.py`/`daily_nav_snapshot.py`,
   which need fill history a pre-existing position lacks. Sizing against total NAV when a third is
   locked in an excluded position deploys unavailable capital.
4. **Known gap**: `daily_nav_snapshot.py`'s P&L assumes journal-tracked fills for cost basis, so it
   can't produce unrealized-P&L for legacy positions (NAV/active_nav stay correct via
   `compute_active_nav.py`). A P&L-capable version is needed before comparing this account's
   *return* against a clean-slate account like SpaceX.
5. **Test it**: `excluded_tickers_selfcheck.py` is the reference — empty/None no-op, single/
   multi-ticker, all-excluded edge case, exact-case-only matching. Extend this file, don't
   parallel it.

**Test-infrastructure lesson (same root cause, different files):** `Executor.__init__` eagerly loads
`state.json` from the DEFAULT `(account, plan_date)` path *before* test code can redirect it to a
tmpdir. Every selfcheck driving `Executor` needs a unique account tag AND module-load-time cleanup
of any stale default-path fixture — see `ghost_order_selfcheck.py`'s `TAG` comment.

*→ rationale §7.*

## 8. Never Write Experiment Output to a Canonical / Registry-Pinned Filename

Rules when a script's output feeds `data/results_registry.md` or any pinned baseline:
- **Any config axis that changes the numbers MUST change the filename.** Every result-affecting env
  knob needs a suffix tag, or the run must pass an explicit `OUT_CSV=` override.
- **Experiment/ad-hoc runs write to a clearly non-canonical name** (`_exp_<what>`, `_probeNNN`,
  dispatcher job-id) so a canonical pinned CSV is never a possible target.
- **Regenerating a pinned baseline: use the EXACT pinned command AND interpreter.** Registry pins
  `$DNA_PYEXE` (= `/home/trido/thanhdt/wc_venv/bin/python`, pandas 3), NOT system `python3`
  (pandas 2.3 cannot unpickle `data/earnings_surprise_data.pkl` — `NotImplementedError` in
  `NDArrayBacked.__setstate__`). Copy the command verbatim; don't substitute `python3`.
- **After regenerating, verify before trusting**: metric in expected range, `self-check 0 VND`,
  independent recompute (`extract_peryear.py <CSV>`) matching the print — then note the regeneration
  in the registry for auditability.
- Cite the registry **by section title** (e.g. `## KẾT QUẢ THAM CHIẾU phiên 2026-06-19`), never by
  line number — refs drift as entries get inserted.

*→ rationale §8 (+ §8b).*

**§8b. `data/bq_cache_asof*` snapshot retention (chốt 2026-07-30, audit job `Wags_20260730_112912`).**
Each snapshot is ~2,0GB and NOT reproducible (BQ time-travel off, `ticker`/`ticker_prune`
TRUNCATE+rebuild daily) — a wrong delete permanently destroys a pin's evidence.
- **Keep at most 1 per month** — with several re-pins in one month, only the LATEST is "current".
- **Older than 3 months → deletable IF**: (a) NOT the OFFICIAL current pin for a live result in
  `current_ops.md`/`results_registry.md` (confirm by grep, §10 discipline — never guess from
  age/name); (b) NOT flagged a **"special historical marker"** (e.g. `bq_cache_asof20260728` = the
  pre-restate marker for DT5G 2026-07-29, the only evidence for the +0,47pp CAGR data-drift
  attribution).
- **Delete an old one only AFTER the new pin has cleared quant-skeptic.**
- **Don't create a separate cadence** — hang it off the existing monthly BQ snapshot
  (`bin/bq_monthly_pin.py`, cron day 1). Source: job `Taylor_20260729_155142`,
  `agents/Taylor/research/asof_vintage_label_20260729.md`.

## 9. Check `mike/kb/data_registry/` Before Wiring a New Data Source

**Mandatory rule, user directive 2026-07-11:** before reading ANY data source (BQ table, local
CSV/pickle/JSON, published state file) in new code — check `mike/kb/data_registry/` first (start
`index.md`; OKF tree, 1 source = 1 file — `kb/data_registry.md` is a stub redirect). Grep:
`grep -rn "<source>" mike/kb/data_registry/`.
- `CANONICAL` — use directly. `TRAP` — read "Bẫy" section first; usually a correctly-named sibling
  exists instead. `DEPRECATED/DEAD` — don't wire into anything new.
- **Not in the registry at all** — don't assume safe by default. Add an entry (status verified
  against real evidence — crontab, mtime, code that writes it — not guessed from the name) before
  wiring in, or ask Winston/Mike to verify first.

**Ownership**: Winston (data-ops) keeps the registry current ad-hoc; full periodic audit folded into
the Friday KB editorial review (`kb_nightly.sh`), not a separate cron job.

**When dispatching Taylor (or anyone) for new R&D**: state explicitly "tra `mike/kb/data_registry/`
(index.md) trước khi chọn nguồn dữ liệu, đặc biệt bảng market-state/regime" — same pattern as
DollarBill's DNSE-vs-BQ rule (§6). A generic "verify your data" reminder doesn't stop an LLM
reaching for the closest-sounding name; naming the registry file does.

*→ rationale §9.*

## 10. When a File Becomes Canonical, Archive Its Superseded Variants in the Same Pass

**Rule: when a script/file is confirmed canonical for a purpose** (a builder produces a pinned
table, a cron is installed pointing at it, a migration names it the production source) — in the
**same commit/session**:
1. **Identify superseded variants** — files with a similar name/purpose that are NOT the canonical
   one, and grep the whole repo (scripts + crontab) to confirm zero active callers reference them.
   Never archive on a name-similarity guess alone; verify with a real grep.
2. **`git mv` them into an `archive/` subdirectory** (preserving git history, not `rm`) —
   reversible, and it removes the file from the root namespace where a casual `ls`/glob would
   surface it as a live candidate.
3. **Update the source's file in `mike/kb/data_registry/`** to reflect the new archive path and mark
   the entry `DEPRECATED` with a pointer to the canonical replacement (per §5's obsolete-marking
   rule if this is a data-source migration, or a plain note if it's just script hygiene).
4. **Do NOT apply this to genuine audit-trail artifacts** — rejected-hypothesis backtest CSVs,
   dry-run logs proving a mechanism works, anything already namespaced into an experiment directory
   per §8 (`data/*_exp/`, `agents/<id>/probe_*/`). Those are inert evidence, not scripts that could
   be run by mistake — archiving them is churn, not safety.

**Periodic check**: `bin/data_registry_audit.sh`'s stale-duplicate scan (added 2026-07-11) flags
repo-root files with a name similar to an already-CANONICAL registry entry that are NOT yet under
`archive/` — surfaced in the Friday KB editorial review for a human/Winston decision, not auto-moved.

*→ `kb/incidents/2026-07/2026-07-11-fa-ratings-8l-silent-write-failure.md`.*

## 11. Check `mike/kb/cron_registry.md` Before Adding or Changing a Cron Schedule

**Mandatory rule**: before adding a new cron entry or changing an existing one's schedule, read
`mike/kb/cron_registry.md` first (the bảng chính) — it answers, per job: what it reads (source +
vintage T/T-1), what it writes, who consumes it, what buffer/verify-artifact exists downstream.
Answer its "4 câu hỏi bắt buộc" (đọc gì+vintage / nguồn tươi lúc nào — đo thật, không tin comment /
cần T hay T-1 / ai tiêu thụ + deadline), documented in
`mike/kb/cron_registry/_adding-cron-policy.md`, before picking a time slot.

**Update the registry in the SAME commit** as any crontab change (add/remove/reschedule a line) —
same discipline as §9 and §10. A crontab change without a matching registry update is how the next
agent re-introduces a cache/vintage mismatch.

**A production "publish" script (writes a table/file other production consumers read as the
current-day source of truth) must read its inputs live, never through a process-inherited cache
env** — if the import chain can reach `BQ_LOCAL_CACHE`/`bq_local_cache`, unset it explicitly
(`os.environ.pop(...)`) before the first query, process-locally (never edit `wc_env.sh` itself,
which would break every OTHER script that legitimately wants the cache).

*→ `kb/incidents/2026-07/2026-07-12-audit-cron-order-publish-cache-t1.md`.*

## 12. Shared Multi-Account Data Files: Filter by `account_no` at Every Read

`data/execution_logs/dnse_raw_{date}.jsonl` là file DÙNG CHUNG cho MỌI account (phân biệt bằng field
`accountNo`/`account_no` trong record). **Quy tắc bắt buộc:** mọi lần đọc 1 file dữ liệu dùng chung
giữa các account (hiện tại `dnse_raw_{date}.jsonl`, và bất kỳ file nào sau này gộp nhiều account vào
1 path), dòng ĐẦU TIÊN xử lý record phải là bộ lọc account, không phải phép tính:

```python
if str(rec.get("accountNo")) != str(account_no):
    continue
```

Không có account_no trong scope → đó là dấu hiệu hàm đang thiếu tham số, KHÔNG phải lý do bỏ lọc.
Nếu chủ đích là gộp toàn bộ account (báo cáo fleet-wide), phải viết rõ trong docstring.

**Self-check trước khi commit** bất kỳ script nào đọc file dùng chung: chạy cho CẢ 2 account
(`SpaceX` và `ZaloPay`) cùng 1 ngày có giao dịch, xác nhận 2 kết quả KHÁC nhau. Giống hệt nhau = gần
như chắc chắn đọc chung không lọc — dấu hiệu rẻ nhất, bắt được cả 3 sự cố nếu có ai chạy.

**Grep sweep không đủ nếu chỉ tìm tên file.** Sweep 2026-07-19 grep `dnse_raw` vẫn bỏ sót
`eod_trading_report.sh` vì file CÓ nhắc tên nhưng lọc thiếu ở 1 nhánh. Sweep đúng = với MỖI hit, đọc
xem record có bị lọc account trước phép tính không (audit 2026-07-22: 4/4 script kế toán đã lọc
đúng; `execution_quality_review.py` chỉ lọc KHI truyền `--account`, mặc định gộp cả 2 account — chấp
nhận được cho công cụ review ad-hoc, KHÔNG được dùng làm nguồn số báo cáo).

*→ 3 entry trong `kb/incidents/index.md` + rationale §12.*

## 13. Sửa 1 file `kb/` cần Mike duyệt trước khi live → ghi ra `<file>.proposed`, KHÔNG sửa tại chỗ

**Quy ước (đã dùng cho code `bin/*.sh.draft`, §10) — áp y hệt cho `kb/`:** khi cần Mike duyệt trước
khi live, **ghi bản mới ra `kb/<file>.proposed`** (file anh em, cùng thư mục) — **KHÔNG đụng
`kb/<file>` gốc**. Cơ chế: `consolidate.sh`/`fleet_backup.sh`/`kb_nightly.sh` chỉ add/commit đường
dẫn **thật**; `publish_context.sh` chỉ `cat` đúng tên file thật (`current_ops.md`, `canonical.md`,
`projects/INDEX.md`) nên bản chờ duyệt không thể lọt vào `context_pack.md`; file role-scoped
`@`-import thẳng từ working tree (`context_safety_core.md`, `context_planning_mini.md`,
`context_execution_mini.md`, `context_dataops_mini.md`, `context_ops_mini.md`) cũng được che. Không
cần state file/TTL/lock — `.proposed` mồ côi vô hại (`kb_nightly.sh` grep
`find kb/ -name '*.proposed' -mtime +1` nhắc dọn định kỳ, không phải gate).

**Mike duyệt xong:** `diff kb/<file> kb/<file>.proposed`, OK → `mv .proposed <file>` rồi tự
`git add`+`commit` (không dựa consolidate.sh sweep hộ). Cần sửa thêm → sửa tiếp `.proposed`.

**Dặn rõ trong MỌI dispatch prompt "sửa X nhưng để Mike duyệt trước":** nói thẳng tên file
`.proposed`, đừng chỉ nói "để uncommitted" — mối nguy thật không nằm ở thao tác git của agent mà ở
các sweeper chạy nền.

*→ rationale §13.*

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

## 16. Never Trust the Host's System Timezone for Date/Time Comparisons — Anchor Explicitly

**Rule:** anchor timezone explicitly, never assume the calling process has the right `TZ`:
- Python: `datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))`, not bare `datetime.now()`.
- Bash: `TZ='Asia/Ho_Chi_Minh' date ...` (ref pattern: `bin/csv_fresh_today.sh`).
- Selfchecks for date/freshness logic: run under `env -u TZ` (+ a foreign TZ) — the exact test that
  caught this bug; a selfcheck inheriting the author's own correct `TZ` passes regardless.

Shipped alongside: a `TZ=Asia/Ho_Chi_Minh` crontab export (closes the ambient-env gap).

*→ rationale §16.*

## 17. A Reader Reporting "Still Open" State Must Scan Every Retention Tier a Mover Can Reach

**Rule:** before shipping/auditing a "is X still open" reader, check `kb/cron_registry.md` for every
mover that can archive X's data, and confirm the reader globs ALL tiers — use `mike_json.py`'s
`_inbox_files()`/`_agent_files()`/`_job_record_path()` helpers (added 2026-08-01) instead of
hand-rolling `glob.glob(inbox/*.jsonl)`. Ship WITH a regression test in the extract-and-test style
(`CHECK5_BEGIN`/`END` marker; `mike_json_archive_selfcheck.py`) — a prose "scans both tiers" claim
has already failed twice without a test enforcing it.

**Boundary:** hot-only readers showing "recent activity" (`context_pack.md`'s "MỚI NHẤT") are
correctly hot-only by design — don't change them.

*→ rationale §17.*

## 18. Any Quant R&D Task (Backtest, IC Test, Gate/Selector Change) — Follow `.claude/skills/quant-research/`

Before designing/running a backtest, factor-IC test, or production-rule review, read the
`quant-research` skill (`/home/trido/thanhdt/WorkingClaude/.claude/skills/quant-research/SKILL.md` —
Skill tool or direct read in headless dispatch); it holds the fixed order of operations. The 5 steps
most often skipped: declare **N as independent events, not row count** (and match the statistical
tool to N); `self-check 0 VND` with a control leg reproducing the pinned number; point-in-time joins
only; DSR/PBO plus the quant-skeptic gate before recommending a wire; verify the artifact, not the
self-report, before relaying a conclusion.

## 18b. `srcwalk` để ĐỌC file, `grep` để TÌM — chia theo VIỆC, đã đo (chốt 2026-08-03)

**Quy tắc hành động đầy đủ: `WorkingClaude/CLAUDE.md` § Code navigation — nguồn duy nhất, và nó đã
được auto-inject mỗi phiên.** Mục này chỉ giữ số đo + con trỏ, KHÔNG chép lại luật.

- **ĐỌC file → `srcwalk`** (−88,8% token CI[86,5–90,7], giữ 95,7% top-level symbol, 0/150 file đắt
  hơn `Read`); **TÌM định nghĩa/call site → `grep`** (ΔF1 +0,052 và +0,062, CI không chứa 0; rẻ
  3–25×; **0% im lặng trả rỗng** so với **8,2%** CI[4,4–12,6] của srcwalk). Ngoại lệ: tên xuất hiện
  >10 file (`main`/`run`) → `srcwalk discover` (precision 0,844 vs 0,459; 200 token vs 740).
- **4 cạm bẫy** (chi tiết ở CLAUDE.md): `.gitignore` ẩn `mike/` ⇒ **44% file `.py` vô hình** với
  discovery (`--scope .` cho F1 0,065) → luôn scope vào thư mục chứa code; im lặng trả rỗng; chỉ
  `trace --depth 1` (hop-2 nở 500 cạnh / 121 file rác); `review` bỏ sót hàm mới thêm → `git diff`.
  Bash/`.json`/`.sql`/`.csv`: không hỗ trợ.
- Cùng tinh thần §6/§9/§14: đây là bằng chứng **điều hướng cấu trúc**, không phải bằng chứng runtime
  — giữ nguyên dòng `confidence:`/`caveat:` công cụ tự in khi trích dẫn kết luận.

*→ rationale §18b.*

## 19. Any Task With a Selfcheck/Test — Follow `~/.claude/skills/verify-before-done/`

Before reporting a coding/fix task done with a selfcheck involved, read the `verify-before-done`
skill (`/home/trido/.claude/skills/verify-before-done/SKILL.md`, built 2026-08-01). Core habit: run
the selfcheck for real, name its environment dependencies (TZ tops the list — §16), re-run under a
stripped/adversarial variant, treat any cross-environment difference as the finding. Applies to the
author before claiming done AND to anyone re-verifying (baked into `arch-reviewer`'s mandate —
`~/.claude/agents/arch-reviewer.md`).

## 20. Mark `decided_by: "user"` When a Real User Confirmed a Closure — Not Just "Seemed Reasonable"

**Rule:** when an `answer`/`decision` closes a money/decision-adjacent `question`, include
`"decided_by": "user"` in the payload ONLY when the user actually confirmed it in real time. When
Mike/an agent closes on its own judgment (even well-evidenced) — omit the field, or use
`"decided_by": "agent"`. Not a quality judgment on the closure — a provenance record, so later
counting/reporting can separate "confirmed by a person" from "judged, not confirmed."

**Enforced by:** `bin/bus_question_audit.py`'s closure-provenance report — breakdown by `decided_by`
for the last N days (`--provenance-days`, default 14), always shown, feeding weekly review. A report,
not a gate — high unmarked-agent-closure counts prompt spot-review, not wrongdoing.

*→ rationale §20.*

## 21. Tỉ suất Lợi Nhuận Per-Position Trong Báo Cáo: BẮT BUỘC Cộng Lại Cổ Tức Tiền Mặt

**Quy tắc:** mọi tỉ suất per-position trong bất kỳ báo cáo nào (ngày/tuần/tháng) **PHẢI** đi qua
`mike/bin/dividend_adjusted_return.py` — không tự viết lại công thức, không suy cổ tức bằng hiệu
`Close − Price` (quan hệ là phép NHÂN; hiệu số biến thiên theo giá và cho sai cả số tiền lẫn
ex-date). Sự kiện chưa đối soát được với sổ broker bị gắn cờ `UNVERIFIED` và **CẤM** đưa vào báo cáo
gửi nhà đầu tư — vì `Close/Price` không phân biệt được cổ tức tiền mặt với chia tách cổ phiếu.

Chi tiết cơ chế, 4 cái bẫy cụ thể và cách kiểm chứng 3 nguồn độc lập:
**`mike/kb/data_registry/price-volume/ticker_close_vs_price_dividend_adj.md`**. Bổ sung cho §6, không
thay thế: §6 lo "số này lấy từ nguồn có thẩm quyền chưa", §21 lo "công thức có bỏ sót cấu phần lợi
nhuận nào không".

*→ rationale §21.*

## 22. Một Quy Tắc Sống Trong Văn Xuôi Mà LLM Cứ Áp Sai Khác Nhau Mỗi Lần — Chuyển Thành Code, Theo `.claude/skills/deterministic-decision-gate/`

Khi 2 phiên LLM (hoặc cùng 1 phiên ở 2 lần dispatch) áp cùng một luật từ `context_*.md` ra 2 kết quả
khác nhau trên cùng dữ liệu — đó là dấu hiệu luật đó thuộc loại **suy dẫn thuần tuý từ dữ liệu có
sẵn** (offset ngày, đọc field rồi lọc, tra bảng, so số với hằng số) và nên là CODE, không phải văn
xuôi để LLM tự nhớ mỗi lần. Trước khi build/áp patch loại này, theo
`.claude/skills/deterministic-decision-gate/SKILL.md` (đúc kết từ chuỗi A1-A4, 2026-08-04, audit
`Taylor_20260804_125048`). Hai điểm hay bị bỏ nhất: **`git apply` báo exit 0 KHÔNG PHẢI bằng chứng
đã ghi file** (dùng `patch` + verify độc lập sau mỗi lần áp), và **tách quyết định CHÍNH SÁCH (phải
hỏi user) khỏi quyết định KỸ THUẬT** (quant-skeptic CONFIRMED là đủ).

## 23. Chạy Selfcheck THEO PHẠM VI Cái Vừa Sửa — Không Chạy Cả Bộ Theo Phản Xạ

**Nguyên tắc:** chạy selfcheck **liên quan tới file mình vừa đụng**, không chạy cả bộ mặc định —
TRỪ KHI đụng vào **module lõi dùng chung**, lúc đó quét rộng là bắt buộc và **phải nói rõ trong báo
cáo vì sao** (biến phán đoán đó thành hành động có chủ đích, không phải phản xạ).

**Module lõi dùng chung — sửa là PHẢI quét rộng** (số đo bằng máy từ import thật):

| Sửa | Số selfcheck phụ thuộc |
|---|---:|
| `trading_bot/plan.py` | 21 |
| `trading_bot/config.py` | 15 |
| `trading_bot/executor.py` | 11 |
| `trading_bot/brokers.py` | 7 |
| `trading_bot/plan_funding_gate.py` | 2 import trực tiếp, **nhưng ca 08-07 cho thấy phụ thuộc thật rộng hơn** (gate chạy trong luồng của 6+ selfcheck khác) — coi như lõi |

Mọi module khác (`lag_*.py`, `dcf_*.py`, `custom_basket.py`, `anomaly_gate.py`,
`trading_bot/{due_diligence,netting_recon,plan_cash_commitment,discretionary_accumulation}.py`, …)
có **1–6** selfcheck phụ thuộc → chạy đúng những file đó.

**Tra bản đồ ngược bằng LỆNH, đừng chép bảng vào đây** (bảng chép tay sẽ mốc; lệnh thì không) —
`bin/selfcheck_scope_map.sh` (không tham số = toàn bộ bản đồ; `bin/selfcheck_scope_map.sh
trading_bot/plan.py` = chỉ file đó). Bảng trên chỉ là mốc tham chiếu đo ngày 2026-08-08; nguồn
chuẩn tắc là output của script.

**Hệ luận — 2 quy ước để bộ test không mốc tiếp:**
1. **Selfcheck KHÔNG được assert lên trạng thái SỐNG.** Chép cứng một rổ mã, một số đếm đo tại một
   ngày, hay đọc thẳng file production (`data/trade_plans/…`, `anomaly_flags.json`, `universe_pit`)
   làm assertion ⇒ test **tự vô hiệu theo thời gian** và trở thành nhiễu nền. Đóng băng fixture,
   hoặc assert lên *bất biến* (quan hệ, dấu, fail-safe) thay vì lên *giá trị*.
2. **`test_*.py` ở repo root KHÔNG PHẢI test** — 165 file, là script backtest/R&D (đặt tên theo lịch
   sử), 154/165 không đụng từ 2026-06-21. **Không archive** (artifact nghiên cứu, §10 mục 4) nhưng
   **KHÔNG bao giờ gộp vào "chạy bộ test"**. Script R&D MỚI đặt tên `exp_*` / `probe_*` / `stress_*`.

*→ rationale §23.*

## 24. Ràng Buộc Giá/Hạn Mức Của Plan Phải Là FIELD RIÊNG Được Cưỡng Chế Bằng CODE — Không Bẻ Cong Một Field Khác Để "Vô Tình" Ra Đúng Số

**Luật:** khi một luật giao dịch nói "không bao giờ được X quá ngưỡng N" (trần giá entry-window,
trần %ADV, hạn mức vị thế), ngưỡng N phải (a) là **field riêng trong `PlannedOrder`**, (b) được
**suy ra/cưỡng chế ở MỘT chỗ tại ranh giới nạp plan** (`load_plan()`, cùng tinh thần
`filter_excluded_tickers()` §7), (c) có **guard cuối** sau mọi phép biến đổi giá. TUYỆT ĐỐI không
neo ngược một field khác (`ref_price`) để công thức sẵn có "vô tình" cho ra đúng ngưỡng.

**Vì sao — 3 cách mẹo neo ngược hỏng, đều là ca thật 2026-08-09 (DRI, anchor 13.000đ):**
1. **Hằng số giả định sai và ĐỔI THEO NGÀY.** Mẹo `ref_price = anchor/1,04` giả định trần đuổi
   luôn 4%; thực tế `chase = clamp(2×rvol_20d, 1,5%, 4%)` — đo thật DRI rvol=0,0153 ⇒ **3,06%**
   ⇒ trần thực chỉ 12.800đ khi thị trường 13.100–13.200đ ⇒ **gần như chắc không khớp**, và con số
   đổi mỗi ngày theo rvol.
2. **Phép biến đổi PHÍA SAU có thể đẩy vượt.** `_limit_price` kết thúc bằng `px = max(px, q.floor)`
   — sàn phiên > anchor thì giá đặt bị đẩy **lên trên** anchor, trần % không biết anchor nên không
   chặn được. Cần guard cuối: `if hard and px > hard: return None`.
3. **Đường đi khác không qua chỗ tính giá.** `_atc_sweep` đặt ATC `price=None` (khớp giá đóng cửa,
   không đặt được giá) ⇒ phải bỏ qua hẳn lệnh có trần, không lách được.

**Hệ quả kèm theo — field mà `load_plan()` lọc mất là im lặng.** `load_plan()` chỉ giữ key nằm
trong `dataclasses.fields(PlannedOrder)`. `entry_anchor_price` (từ 74a5d338) và
`hard_no_chase_ceiling_vnd` (do `discretionary_accumulation.py` sinh ra) **đều đã có trong plan JSON
từ trước mà executor không bao giờ thấy** — không lỗi, không cảnh báo. Thêm field vào plan generator
mà quên thêm vào dataclass = ràng buộc không tồn tại. Kiểm bằng `load_plan()` thật, đừng đọc JSON.

**Cơ chế LIVE hiện tại** (commit `a29ab4f`/`319e1b2`/`aa0afea`, quant-skeptic CONFIRMED 2 vòng):
`PlannedOrder.hard_no_chase_ceiling_vnd` (VND tuyệt đối, chỉ `side="buy"`); `load_plan()` tự suy
`= entry_anchor_price` (giữ giá trị CHẶT HƠN nếu generator ghi sẵn; giá trị **rác chỉ được rơi về
anchor, không bao giờ vô hiệu hoá trần**); `_limit_price` clamp `min(ref×(1+chase%), q.ceiling,
hard)` + guard cuối; journal `HARD_CEILING_BLOCK`. Nhờ có trần độc lập, `ref_price` trả về đúng
nghĩa giá tham chiếu thật ⇒ lệnh **bám `q.ask` sống** (re-price mỗi `slice_interval_min`) mà vẫn
không bao giờ vượt trần. Selfcheck: `hard_no_chase_ceiling_selfcheck.py` (50 ca) — mọi ca "chặn
được" đều có **ca chứng minh ngược** (bỏ trần ⇒ thật sự vượt), không chỉ khẳng định suông.

*→ job `Taylor_20260809_123917`.*
