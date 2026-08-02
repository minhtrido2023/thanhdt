# Coding Guidelines — áp dụng cho toàn fleet

Behavioral guidelines to reduce common LLM coding mistakes.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

**Enforcement policy (thêm 2026-08-01, user mandate — "đẩy bài học cũ ra công cụ/linter thay vì
văn xuôi"):** lesson nào diễn đạt được thành 1 PATTERN CƠ HỌC trong code (không cần phán đoán ngữ
nghĩa) → mục tiêu là 1 check tự động chặn commit, KHÔNG chỉ thêm văn xuôi. Theo SRE postmortem
culture (Google SRE workbook — action item tốt nhất là 1 CI rule, không phải 1 dòng ghi chú) và
kỷ luật viết rule của Semgrep ("1 rule bắt đúng 2 lần còn hơn 1 rule bắt nhầm 200 lần" — luôn
test rule mới trên file thật trước khi bật, không đoán). Cơ chế đang có, đã verify bằng
`git commit` thật: **`bin/shellcheck_gate.sh`** (pre-commit hook, ShellCheck — bắt được cả 4 sự
cố quoting thật trong bash strings/heredoc-as-dispatch-prompt 2026-07-17→08-01, xem §15 +
`kb/incidents/2026-08/2026-08-01-shellcheck-precommit-gate.md`). Setup 1 lần/repo (hook dùng chung
mọi worktree): `pip install --user pre-commit shellcheck-py && pre-commit install`. Không phải mọi
lesson đều mechanize được — §7, §10, §11, §13 là quy trình/judgment call, KHÔNG có pattern cú pháp
rõ ràng để lint; giữ dạng văn xuôi là đúng, không phải thiếu sót.

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

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## 5. Idempotent Side Effects

**Any script that can be killed mid-run and re-run must not repeat an external action.**

Root cause (2026-07-02 double-buy, `kb/incidents/2026-07/2026-07-02-double-buy-concurrent-bot-execute.md`): a lock only stops two runs from
overlapping — nothing for one run dying mid-write between the external action and persisting
that fact locally. Fixed in `trading_bot/executor.py` (`_ghost_tickers` + atomic `_save_state`);
apply the same reasoning to every new script.

Before writing any script that calls an external system with a side effect (place an order,
send a message, write a shared file, call an API that isn't naturally idempotent):
- Ask: "if this process is killed right after the external call succeeds but before local
  state is saved, what does the next run do?" If the answer is "repeats the action," that's
  a bug, not an edge case.
- Prefer the external system's own source of truth (broker's live order book, the sent-messages
  log) over local state — local state can lag reality.
- When you can't tell whether an action already happened, **fail-safe pause and flag for a
  human** — do not guess-and-merge into local state, do not silently proceed.
- Persist "the action happened" as close to the actual external call as possible (write
  immediately after, not batched at the end of a longer loop).
- Writes to shared state files must be atomic (`tmp` + `os.replace`/`os.rename`), never a
  direct overwrite — a kill mid-write must never leave a half-written file for the next run
  to trust.

## 6. Verify Report Data Provenance (client-facing numbers)

**A field's name and a plausible-looking value are not verification.** Root cause (2026-07-03,
`kb/incidents/2026-07/2026-07-03-weekly-report-estimated-cost-basis.md`): a P&L calc read a
snapshot field labeled `"source": "ref_px_approx"` (an approximate price for an unrelated
purpose) and reported it as real cost basis, unchecked, in a client-facing doc.

Before any number reaches a report (daily/weekly/monthly, or any client-facing artifact):
- Trace it to the *authoritative* system — for fills, the broker's own confirmation
  (`dnse_raw_*.jsonl`'s `averagePrice`/`fillQuantity`), never a downstream summary file.
- Cross-check a second independent source (internal journal `FILL` events, an audited snapshot)
  — see `bin/verify_account_snapshot.py`, the only script permitted to compute cost-basis/P&L
  for a SpaceX report. Disagreement beyond a tight tolerance → fail loudly, don't silently pick one.
- Aggregate totals can be right while per-item attribution is wrong (NAV depends on quantity ×
  market price, not cost basis, so it survived unscathed here).
- Same principle as [[verify-real-facts-dont-self-invent]] / MIKE.md §Quy chuẩn bắt buộc mục 2:
  verify the artifact, don't trust a field because its value looks plausible.

**Standing pipeline for ALL cadences, locked 2026-07-03:**
1. `bin/verify_account_snapshot.py` — true cost basis/ticker, cross-checked (broker raw vs
   internal journal vs audited snapshot).
2. `bin/daily_nav_snapshot.py` — true NAV/date (MTM stock + real cash − margin debt from a
   fresh `dnse_raw_*.jsonl` `balances` record), appended to `nav_history_{account}.csv` so every
   cadence reads the same series.
3. `bin/reconcile_equity.py` — identity check (`starting_capital + unrealized_P&L − fees −
   margin_interest == market_value + cash − margin_debt`); fee rate **0.075%** of true cost
   basis (not 0.1%, corrected 2026-07-03); residual checked against *estimated* margin accrual
   (`--margin-rate-annual`, 12.5%/yr per user, unverified against DNSE's contract) before
   calling it "unexplained."
4. Can't trace a number through this pipeline → don't put it in the report, say what's missing.

**Bright-line rule — same-day data: DNSE API, never BigQuery (user directive, 2026-07-09).** BQ
(`tav2_bq.ticker`/`ticker_1m`) syncs overnight only (`sync_bq_cache_daily.sh`, 23:45 ICT) — any
"today" query before that sync structurally reads **yesterday's** close. Incident 2026-07-09
(`kb/INCIDENTS.md`): a plan generator priced 2/4 orders off stale BQ close (+5.7% off) while 2
others used live DNSE — the inconsistency is what surfaced it.
- Any same-day/live calc (order sizing, T+1 ref prices, live NAV/exposure) MUST read DNSE
  (`dnse_api.py` secdef/latest_trade/positions/balances) — never BQ, regardless of hour.
- BQ OK only for: (a) historical/backtest queries, (b) same-day queries AFTER BQ's sync has
  demonstrably completed (verify via `bq_freshness_check.sh`'s gate, don't assume by clock time).
- In dispatch prompts (DollarBill etc.): state as unconditional MUST with a concrete wrong-vs-
  right example (see `bq_freshness_check.sh`'s DollarBill prompt).

**Cadence-specific scope** (depth differs; pipeline above does not):
- **Daily**: short — trades today, NAV + day-over-day change, margin/risk flag if any.
- **Weekly**: full narrative (`mike/reports/SpaceX_weekly_report_*.md` = template) — activity
  log, incident disclosures, sector/position tables, next-week plan, methodology appendix.
- **Monthly**: institutional conventions on top — MTD/QTD/YTD, benchmark comparison,
  attribution, risk metrics, fee/expense summary, compliance disclosures, outlook.

## 7. Onboarding a New Account With Legacy/Excluded Holdings

**When an account brought under management already holds positions the bot didn't buy** (e.g.
ZaloPay's pre-existing DGC position, kept under a trading restriction — see `kb/INCIDENTS.md`),
use the general mechanism, since more accounts of this shape are expected:

1. **Declare in config, not code**: `"excluded_tickers": [...]` on the account's profile in
   `secrets/trading_bot_accounts.json` (`ACCOUNT_DEFAULTS` in `trading_bot/config.py`). Empty by
   default elsewhere.
2. **Enforcement in ONE place**: `trading_bot.plan.filter_excluded_tickers()`, called from
   `bot_execute.py` right after `load_plan()` — applies no matter how the plan was generated
   (DollarBill's LLM JSON, `bot_prepare_plan.py`'s template, a hand-edited file), so a plan
   generator forgetting the exclusion can never place a forbidden order.
3. **Size against `active_nav`, not total NAV**: `bin/compute_active_nav.py --account <label>`
   computes `total_nav − market_value(excluded_tickers)` from LIVE broker positions/prices (no
   dependency on our execution journal, unlike `verify_account_snapshot.py`/
   `daily_nav_snapshot.py`, which need fill history that doesn't exist for a pre-existing
   position). Whoever builds the plan must use this as the allocation basis — sizing against
   total NAV when a third is locked in an excluded position deploys unavailable capital.
4. **Known gap**: `daily_nav_snapshot.py`'s P&L still assumes journal-tracked fills for cost
   basis, so it can't produce unrealized-P&L for legacy positions (NAV/active_nav are correct via
   `compute_active_nav.py`; a P&L-capable version is separate future work — needed before
   comparing this account's *return* against a clean-slate account like SpaceX).
5. **Test it**: `excluded_tickers_selfcheck.py` is the reference — empty/None no-op, single/
   multi-ticker, all-excluded edge case, exact-case-only matching. Extend this file, don't
   parallel it.

**Test-infrastructure lesson (same root cause, different files):** `Executor.__init__` eagerly
loads `state.json` from the DEFAULT `(account, plan_date)` path *before* test code can redirect
it to a tmpdir — a stale file from an earlier run silently corrupts the next run's start state.
Every selfcheck driving `Executor` needs a unique account tag AND module-load-time cleanup of any
stale default-path fixture — see `ghost_order_selfcheck.py`'s `TAG` comment.

## 8. Never Write Experiment Output to a Canonical / Registry-Pinned Filename

**Root cause (2026-07-06 R3-CSV overwrite, `data/results_registry.md` mục `## KẾT QUẢ THAM CHIẾU
phiên 2026-06-19` — cite by section title, not line: refs drift as entries get inserted):** an
output filename built from only a SUBSET of env knobs (`BASKET_SELECT`/combination-mode had no
suffix) let an experiment silently clobber the pinned production baseline. A lock wouldn't have
helped — both runs were legitimate, just colliding on an output name.

Rules when a script's output feeds `data/results_registry.md` or any pinned baseline:

- **Any config axis that changes the numbers MUST change the filename.** Every result-affecting
  env knob needs a suffix tag, or the run must pass an explicit `OUT_CSV=` override. Before
  running an experiment variant, check whether the changed knob is reflected in the filename.
- **Experiment/ad-hoc runs write to a clearly non-canonical name** (`_exp_<what>`, `_probeNNN`,
  dispatcher job-id) so a canonical pinned CSV is never a possible target.
- **Regenerating a pinned baseline: use the EXACT pinned command AND interpreter.** Registry pins
  `$DNA_PYEXE` (= `/home/trido/thanhdt/wc_venv/bin/python`, pandas 3), NOT system `python3`
  (pandas 2.3 cannot unpickle `data/earnings_surprise_data.pkl` — `NotImplementedError` in
  `NDArrayBacked.__setstate__`). Copy the command verbatim; don't substitute `python3`.
- **After regenerating, verify before trusting**: metric in expected range, `self-check 0 VND`,
  independent recompute (`extract_peryear.py <CSV>`) matching the print — then note the
  regeneration in the registry for auditability.

**§8b. `data/bq_cache_asof*` snapshot retention (chốt 2026-07-30, sau audit `fleet_housekeeping`
job Wags_20260730_112912).** Mỗi snapshot ~2,0GB, không tái tạo được (BQ time-travel tắt,
`ticker`/`ticker_prune` TRUNCATE+rebuild mỗi ngày) — xoá sai = mất vĩnh viễn bằng chứng pin.
- **Giữ tối đa 1 bản/tháng** — nhiều re-pin cùng tháng → chỉ bản MỚI NHẤT là "hiện hành".
- **>3 tháng tuổi → xoá được NẾU**: (a) KHÔNG phải bản pin CHÍNH THỨC hiện hành cho kết quả sống
  trong `current_ops.md`/`results_registry.md` (grep xác nhận, kỷ luật §10, không đoán theo
  tuổi/tên); (b) KHÔNG đánh dấu **"mốc lịch sử đặc biệt"** (vd `bq_cache_asof20260728` = mốc
  TRƯỚC restate DT5G 07-29, bằng chứng duy nhất cho attribution +0,47pp CAGR do trôi dữ liệu —
  KHÔNG BAO GIỜ xoá theo tuổi, chỉ xoá nếu người quyết định tường minh mất giá trị bằng chứng).
- **Xoá cũ CHỈ SAU KHI pin mới đã qua quant-skeptic** — không xoá bản đang chờ verify thay thế.
- **Không tạo cadence riêng** — gắn nhịp snapshot BQ hàng tháng có sẵn (`bin/bq_monthly_pin.py`,
  cron ngày 1 hàng tháng).
- Nguồn: Taylor job `Taylor_20260729_155142`, `agents/Taylor/research/asof_vintage_label_20260729.md`.

## 9. Check `mike/kb/data_registry/` Before Wiring a New Data Source

**Root cause (2026-07-11 SIGNAL_V11 base-leak, `kb/INCIDENTS.md`):** four production consumers
silently read a trap table (documented as a trap in `CLAUDE.md`, but nothing forced a check
before a new script picked a table name that *sounded* right) instead of the real production
regime table — a live paper-trading book entered 6 tickers on a fake signal.

**Mandatory rule, user directive 2026-07-11:** before reading ANY data source (BQ table, local
CSV/pickle/JSON, published state file) in new code — check `mike/kb/data_registry/` first (start
`index.md`; OKF tree, 1 source = 1 file — `kb/data_registry.md` is a stub redirect). Grep:
`grep -rn "<source>" mike/kb/data_registry/`.
- `CANONICAL` — use directly. `TRAP` — read "Bẫy" section first; usually a correctly-named
  sibling exists instead. `DEPRECATED/DEAD` — don't wire into anything new.
- **Not in the registry at all** — don't assume safe by default. Add an entry (status verified
  against real evidence — crontab, mtime, code that writes it — not guessed from the name) before
  wiring in, or ask Winston/Mike to verify first.

**Ownership**: Winston (data-ops) keeps the registry current ad-hoc. Full periodic audit folded
into the Friday KB editorial review (`kb_nightly.sh`), not a separate cron job.

**When dispatching Taylor (or anyone) for new R&D**: state explicitly "tra `mike/kb/data_registry/`
(index.md) trước khi chọn nguồn dữ liệu, đặc biệt bảng market-state/regime" — same pattern as
DollarBill's DNSE-vs-BQ rule (§6). A generic "verify your data" reminder doesn't reliably stop an
LLM reaching for whichever table name sounds closest; naming the registry file does.

## 10. When a File Becomes Canonical, Archive Its Superseded Variants in the Same Pass

**Why this matters (2026-07-11 fa_ratings incident, `kb/incidents/2026-07/2026-07-11-fa-ratings-8l-silent-write-failure.md`):** confirming which file is
canonical is only half the fix — near-identical variant files left in the repo root under
slightly different names are the landmine that makes the next agent (or human) grep and pick the
wrong one.

**Rule: when a script/file is confirmed canonical for a purpose** (a builder is identified as *the*
one that produces a pinned table, a cron is installed pointing at a specific script, a migration
decision names a specific file as the production source) — in the **same commit/session**:
1. **Identify superseded variants** — files with a similar name/purpose that are NOT the confirmed
   canonical one, and grep the whole repo (scripts + crontab) to confirm zero active callers
   reference them. Never archive on a name-similarity guess alone; verify with a real grep.
2. **`git mv` them into an `archive/` subdirectory** (preserving git history, not `rm`) — reversible
   and auditable, and it removes the file from the root namespace where a casual `ls`/glob would
   surface it as a live candidate.
3. **Update the source's file in `mike/kb/data_registry/`** to reflect the new archive path and mark the entry
   `DEPRECATED` with a pointer to the confirmed canonical replacement (per §5's obsolete-marking
   rule if this is a data-source migration, or a plain note if it's just script hygiene).
4. **Do NOT apply this to genuine audit-trail artifacts** — rejected-hypothesis backtest CSVs, dry-run
   logs proving a mechanism works, anything already namespaced into an experiment directory per §8
   (`data/*_exp/`, `agents/<id>/probe_*/`). Those are inert data files kept as evidence, not scripts
   that could be run by mistake — archiving them is churn, not safety.

**Periodic check**: `bin/data_registry_audit.sh`'s stale-duplicate scan (added 2026-07-11) flags
repo-root files with a name similar to an already-CANONICAL registry entry that are NOT yet under
`archive/` — surfaced in the Friday KB editorial review for a human/Winston decision, not auto-moved.

## 11. Check `mike/kb/cron_registry.md` Before Adding or Changing a Cron Schedule

**Root cause (2026-07-12 C1 CRITICAL, `kb/incidents/2026-07/2026-07-12-audit-cron-order-publish-cache-t1.md`):** a publish script silently read a
process-inherited T-1 cache env var for ~2.5 weeks despite its own comment stating live BQ as the
source of truth — the code didn't enforce the intent the comment stated. Nobody had asked "what
vintage does this publish step actually read?" before a downstream gate tightened and turned the
mismatch into a structural, always-fails contradiction.

**Mandatory rule**: before adding a new cron entry or changing an existing one's schedule, read
`mike/kb/cron_registry.md` first (the bảng chính) — it answers, per job, what it reads (source +
vintage T/T-1), what it writes, who consumes the output, and what buffer/verify-artifact exists
downstream. Answer its "4 câu hỏi bắt buộc" (đọc gì+vintage / nguồn tươi lúc nào — đo thật, không
tin comment / cần T hay T-1 / ai tiêu thụ + deadline), now documented in
`mike/kb/cron_registry/_adding-cron-policy.md`, before picking a time slot.

**Update the registry in the SAME commit** as any crontab change (add/remove/reschedule a line) —
same discipline as §9's data registry and §10's archive-on-canonicalize rule. A crontab change
without a matching registry update is exactly how the next agent re-introduces a cache/vintage
mismatch that "looks fine" until a downstream gate tightens.

**A production "publish" script (writes a table/file other production consumers read as the
current-day source of truth) must read its inputs live, never through a process-inherited cache
env** — if the import chain can reach `BQ_LOCAL_CACHE`/`bq_local_cache`, unset it explicitly
(`os.environ.pop(...)`) before the first query, process-locally (never edit `wc_env.sh` itself,
which would break every OTHER script that legitimately wants the cache).

## 12. Shared Multi-Account Data Files: Filter by `account_no` at Every Read

**Pattern "cross-account contamination" — 3 lần trong 15 ngày** (chi tiết `kb/incidents/index.md`). Cùng
1 root cause mỗi lần: `data/execution_logs/dnse_raw_{date}.jsonl` là file DÙNG CHUNG cho MỌI
account (phân biệt bằng field `accountNo`/`account_no` bên trong record). Code đọc file theo NGÀY
rồi tính NAV/fill/P&L mà quên lọc account → số của account này lẫn số của account kia.

**Quy tắc bắt buộc:** mọi lần đọc 1 file dữ liệu dùng chung giữa các account (hiện tại:
`dnse_raw_{date}.jsonl`, và bất kỳ file nào sau này gộp nhiều account vào 1 path), dòng ĐẦU TIÊN
xử lý record phải là bộ lọc account, không phải phép tính:

```python
if str(rec.get("accountNo")) != str(account_no):
    continue
```

Không có account_no trong scope → đó là dấu hiệu hàm đang thiếu tham số, KHÔNG phải lý do bỏ lọc.
Nếu chủ đích là gộp toàn bộ account (báo cáo fleet-wide), phải viết rõ trong docstring rằng đây là
tổng-mọi-account có chủ đích.

**Self-check trước khi commit** bất kỳ script nào đọc file dùng chung: chạy nó cho CẢ 2 account
(`SpaceX` và `ZaloPay`) trong cùng 1 ngày có giao dịch, và xác nhận 2 kết quả KHÁC nhau. Hai output
giống hệt nhau = gần như chắc chắn đang đọc chung không lọc — dấu hiệu rẻ nhất, bắt được cả 3 sự
cố trên nếu có ai chạy.

**Grep sweep không đủ nếu chỉ tìm tên file.** Lần sweep 2026-07-19 grep `dnse_raw` vẫn bỏ sót
`eod_trading_report.sh` vì file CÓ nhắc tên nhưng lọc thiếu ở 1 nhánh. Sweep đúng = với MỖI hit,
đọc xem record có bị lọc account trước khi vào phép tính hay không (audit 2026-07-22: 4/4 script
kế toán đã lọc đúng; `execution_quality_review.py` chỉ lọc KHI truyền `--account`, mặc định gộp cả
2 account — chấp nhận được cho công cụ review ad-hoc, KHÔNG được dùng làm nguồn số báo cáo).

## 13. Sửa 1 file `kb/` cần Mike duyệt trước khi live → ghi ra `<file>.proposed`, KHÔNG sửa tại chỗ

**Root cause (2026-07-30, 2 lần cùng ngày):** dặn agent "sửa `kb/canonical.md` nhưng để CHƯA
commit, chờ Mike đọc diff" — cả 2 lần, `bin/consolidate.sh` (cron mỗi giờ + tự trigger sau MỌI
dispatch) quét `git add kb/` + `commit -- kb/` **BLANKET**, cuốn bản sửa dở vào 1 commit thường lệ
trước khi Mike kịp đọc. Vá bằng "hold-list" (`state/kb_pending_review.txt` + TTL + pathspec
exclude) — arch-reviewer bác bỏ: `fleet_backup.sh` (00:00, `git add -A`) và `kb_nightly.sh`
(02:00, `git add kb/`) vẫn quét blanket ĐỘC LẬP, không biết hold-list; đo được **32,8% job
dispatch rơi đúng khung giờ TTL không kịp cảnh báo trước khi 1 sweeper quét qua**; khi bị cuốn,
`publish_context.sh` xuất bản bản CHƯA duyệt kèm banner "đã duyệt" — cổng mở nhưng tự nhận đóng.

**Quy ước đúng (đã dùng cho code `bin/*.sh.draft`, §10) — áp dụng y hệt cho `kb/`:** khi cần Mike
duyệt trước khi live, **ghi bản mới ra `kb/<file>.proposed`** (file anh em, cùng thư mục) —
**KHÔNG đụng `kb/<file>` gốc**. Vì:
- `consolidate.sh`/`fleet_backup.sh`/`kb_nightly.sh` chỉ add/commit đường dẫn **thật** — `.proposed`
  là file mới vô hại, không ảnh hưởng file gốc.
- `publish_context.sh` chỉ `cat` đúng tên file thật (`current_ops.md`, `canonical.md`,
  `projects/INDEX.md`), không bao giờ đọc `.proposed` — bản chờ duyệt **không thể** lọt vào
  `context_pack.md` dù consolidate chạy bao nhiêu lần.
- File role-scoped `@`-import thẳng từ working tree (`context_safety_core.md`,
  `context_planning_mini.md`, `context_execution_mini.md`, `context_dataops_mini.md`,
  `context_ops_mini.md`) — hold-list không che được, `.proposed` che được (agent không viết vào
  file thật).
- **Không cần state file/TTL/lock** — `.proposed` mồ côi vô hại (`kb_nightly.sh` grep `find kb/
  -name '*.proposed' -mtime +1` định kỳ nhắc dọn, không phải gate).

**Mike duyệt xong:** `diff kb/<file> kb/<file>.proposed`, OK → `mv .proposed <file>` rồi tự
`git add`+`commit` (không dựa consolidate.sh sweep hộ). Cần sửa thêm → sửa tiếp `.proposed`.

**Dặn rõ trong MỌI dispatch prompt "sửa X nhưng để Mike duyệt trước":** nói thẳng tên file
`.proposed`, đừng chỉ nói "để uncommitted" — đó là chỗ 2 sự cố hôm đó bị hiểu nhầm thành "sửa tại
chỗ, đừng git commit" trong khi mối nguy thật không nằm ở git.

## 14. Every Internal Producer→Consumer Pipeline Pair Needs a Real Freshness Check, Not Just a Loose Tolerance

**Root cause (2026-07-10 DT5G cron-order incident, bus question `retro-pattern-recurring-
dataprovenance-2`):** `daily_refresh_v34b` computed DT5G at 23:15, but `bq_freshness_check` read
it at 17:30 — 6 hours *before* that day's compute ran, so it silently read *yesterday's* value
every single day. Not a BQ-vs-DNSE source mistake (§6's rule doesn't cover it — DT5G has no
DNSE-equivalent live source); two **internal cron jobs racing**, hidden for weeks by a tolerance
(`MAX_STATE_LAG=2`) loose enough to never trip on a 1-day-late read. §6 closed the narrow cut
(same-day price/volume from DNSE, not BQ); the failure mode this rule generalizes to: "code
silently consumes data that isn't ready yet, hidden by a tolerance or schedule assumption wider
than the real risk."

**Rule:** when a script's output feeds another script on its own cron schedule (not triggered
by the producer finishing) — before trusting "producer already ran by the time I run" on
schedule alone:
- Add a **real freshness precheck** in the consumer: read the producer's own timestamp/marker
  (a `_asof`/`_generated_at` field, file mtime, a `*_ok` flag) and confirm it's from *today's*
  run — not just "a file exists" or "cron order says it should be done by now." Schedule
  assumptions drift (a producer running late, a job that silently fails but leaves yesterday's
  output in place); a precheck is the only thing that catches it.
- Set the tolerance **as tight as the real risk allows** — wide enough to survive normal jitter
  (a job finishing 5 minutes late), tight enough that a full day's staleness (or a full skipped
  run) trips it. `MAX_STATE_LAG=2` days is the concrete anti-pattern: it papered over a
  structural 6-hour-early read for weeks because "2 days behind" never looked urgent.
- Cron schedule change on either side of a pair: this check is folded into §11's mandatory 4
  questions (`kb/cron_registry.md`) — "đọc gì+vintage" already asks it; treat "does the consumer
  verify freshness or just trust timing" as part of answering, not a separate step.
- Applies to ANY internal producer→consumer relationship on independent cron schedules — not
  just BQ/DNSE, not just DT5G. Same reasoning as §6 and §9: verify the artifact you're about to
  consume is actually the one you think it is, don't infer it from schedule math.

**Not a mandate to retrofit every existing pair at once** — apply going forward on every new/
changed cron pair (§11); a periodic sweep of *existing* pairs (checking `cron_registry.md` for
any pair whose consumer trusts schedule-order alone) is Friday KB editorial review material,
same as the data-registry and stale-duplicate audits already folded in there.

## 15. Bash Strings Doubling as LLM Prompts: Escape `"`/`` ` ``, Then Verify by Running, Not Reading

**Root cause (4 real incidents, 2026-07-17 → 2026-08-01, all the same shape):** this fleet's
dispatch scripts (`daily_retro.sh`, `kb_nightly.sh`, `fleet_housekeeping.sh`) build large
multi-line bash double-quoted strings that double as LLM prompt text — Vietnamese prose full of
markdown emphasis (`"quoted phrase"`) and inline-code backticks (`` `filename` ``). Both `"` and
`` ` `` are live bash metacharacters even inside a double-quoted string (unlike single quotes) —
an unescaped one silently terminates the string or triggers real command substitution. Symptoms:
a **fatal crash before any notify.sh call runs** (daily_retro.sh: 2 nights silent); a
**corrupted-but-still-launched** dispatch (kb_nightly.sh: `dispatch.sh` received extra positional
args, exited 1 immediately — 2 weeks of Friday/Saturday editorial review silently never ran);
**bash executing the quoted text as a command** (`fleet_housekeeping.sh --help`: `` `datacold` ``
got run as a command, silently swallowed, word vanished from the output). "The script ran" / "the
dispatch launched" was mistaken for "the content parsed as intended" every time.

**Rule:**
1. Any `"` or `` ` `` inside a bash double-quoted string must be escaped (`\"`, `` \` ``) — no
   exceptions, even for text that "looks like it's just prose."
2. **Prefer a single-quoted heredoc** (`<<'EOF'`) for large prompt-text bodies when you don't
   need variable interpolation — it needs zero escaping of either character (see
   `bin/weekly_ops_audit.sh` for the pattern). If you DO need `$VAR` interpolation, either accept
   the escaping burden or hardcode the (usually-fixed) absolute paths as literal text instead.
3. **Verify by running, not by reading.** Re-reading "looks fine" is how all 4 instances shipped
   — a quote 40 lines into an 80-line string is not something a re-read catches reliably. Extract
   the assignment/heredoc in isolation and actually execute it (see the 4 incident writeups for
   the exact technique used each time) before trusting a fix.

**Enforced by:** `bin/shellcheck_gate.sh` (pre-commit hook) — ShellCheck already detects this
exact pattern for free (`SC1078`/`SC1079` unterminated/suspicious string quote, `SC2006` legacy
backtick used where `$(...)`-style command substitution wasn't intended, `SC2261` competing
redirections — the downstream symptom when a quote break leaves stray text mid-command). No
custom rule needed; the fix was turning ShellCheck ON as a hard gate with a curated code list
(see `bin/shellcheck_gate.sh`'s own header for why curated, not "any finding," and why `SC2154`
was tried and dropped — false positives on `hooks/*.sh`'s cross-file `source` chains).

**Evaluated and NOT shipped:** a Semgrep rule for §12 (missing `accountNo` filter when reading
`dnse_raw_*.jsonl`) — tested against `bin/verify_account_snapshot.py` (which has the correct
filter); a naive `pattern-not: for $REC in $ITER: ... $REC.get("accountNo") ...` fires on every
unrelated loop in the file (not scoped to loops that actually read the shared file) — needs
dataflow-aware rule engineering (semgrep taint mode or similar), not a quick pattern match, to
reach the "fires twice at 100% accuracy" bar. Left as a prose lesson (§12) until someone has time
to build and test that properly — a noisy rule erodes trust in the whole gate faster than no rule.

## 16. Never Trust the Host's System Timezone for Date/Time Comparisons — Anchor Explicitly

**Root cause (2026-07-31, `bin/dt5g_writer_watch.py`):** host runs `Etc/UTC` (`timedatectl`
confirmed), but code read a BQ `lastModifiedTime` with `datetime.fromtimestamp(ms/1000.0)` +
a false comment claiming "process TZ = ICT". A 19:01 ICT write got labeled "12:01", missing
ICT time windows by 7h. **Real but latent**: production callers `source wc_env.sh` (exports
`TZ=Asia/Ho_Chi_Minh`) before running the script, so it never fired live — caught only because
Mike ran the code by hand (no inherited `TZ`) and via the script's own selfcheck under `env -u TZ`.

**Rule:** anchor timezone explicitly, never assume the calling process has the right `TZ`:
- Python: `datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))`, not bare `datetime.now()`.
- Bash: `TZ='Asia/Ho_Chi_Minh' date ...` (ref pattern: `bin/csv_fresh_today.sh`).
- Selfchecks for date/freshness logic: run under `env -u TZ` (+ a foreign TZ) — the exact test
  that caught this bug; a selfcheck inheriting the author's own correct `TZ` passes regardless.

**Evaluated and NOT shipped:** a static lint gate (`datetime.now()`/`date.today()` without
`tz=`) — measured **243 matches** in the real repo, 0 live bugs among them, several false
positives (including matching its own explanatory comment); same verdict as §12. Shipped
instead: this doc + a `TZ=Asia/Ho_Chi_Minh` crontab export (closes the ambient-env gap) +
relying on §14's "run the real code path" habit.

## 17. A Reader Reporting "Still Open" State Must Scan Every Retention Tier a Mover Can Reach

**Root cause (2026-08-01, fleet architecture audit vs Paseo):** `mike_json.py`'s `trace`/
`verify-coverage` globbed only hot `bus/inbox/*.jsonl` — anything past the archive threshold
(`kb_nightly.sh` Phase 1b2 = 30d for bus events, `fleet_housekeeping.sh` Phase 1b3 for
`bus/jobs/`) silently read as "not found" instead of "archived." Same shape as the 2026-07-31
`ops_health_check.sh` check-#5 bug (2 questions invisible for a month, fixed via
`ops_health_check_selfcheck.py`) but NOT the same fix: a proposed generic `conservation_check.py`
(count_before==count_after+archived) was rejected — every mover already conserves counts
correctly, so it wouldn't have caught either bug. The defect is per-READER: does THIS reader
(reporting unresolved state for a human decision) scan every tier a mover can place data into?
Hot-only readers showing "recent activity" (`context_pack.md`'s "MỚI NHẤT") are correctly
hot-only by design.

**Rule:** before shipping/auditing a "is X still open" reader, check `kb/cron_registry.md` for
every mover that can archive X's data, and confirm the reader globs ALL tiers — use
`mike_json.py`'s `_inbox_files()`/`_agent_files()`/`_job_record_path()` helpers (added
2026-08-01) instead of hand-rolling `glob.glob(inbox/*.jsonl)` again. Ship WITH a regression
test in the extract-and-test style (`CHECK5_BEGIN`/`END` marker; `mike_json_archive_selfcheck.py`)
— a prose "scans both tiers" claim has already failed twice without a test enforcing it.

**Evaluated and NOT shipped:** the generic conservation-check (wrong layer, above); a blanket
archive-aware rewrite of every bus reader — `cmd_recent`/`cursor-advance` are correctly hot-only
("what's new," not "what's owed"); making them archive-aware would be an unrequested behavior
change.

## 18. Any Quant R&D Task (Backtest, IC Test, Gate/Selector Change) — Follow `.claude/skills/quant-research/`

Before designing/running a backtest, factor-IC test, or production-rule review, check the
`quant-research` skill (`/home/trido/thanhdt/WorkingClaude/.claude/skills/quant-research/SKILL.md`
— Skill tool or direct read in headless dispatch). Fixed order of operations this fleet converged
on: scope by reading real code first, check `mike/kb/data_registry/`, pin the
environment, declare N as independent events not row count, match statistical tool to N
(IS/OOS large, LOO+bootstrap small, always disclosed), verify position-tier AND full-engine-tier,
self-check 0 VND with control leg reproducing the pinned number, point-in-time joins only, look
for dose-response, decompose kept-vs-added on basket-size changes, reconcile adjacent findings,
DSR/PBO before recommending a wire, confirm production untouched via `git diff`, quant-skeptic
gate before any production-change recommendation, verify the artifact not the self-report before
relaying a conclusion. Point Taylor at this skill explicitly rather than re-deriving by hand.

## 19. Any Task With a Selfcheck/Test — Follow `~/.claude/skills/verify-before-done/`

Before reporting a coding/fix task done with a selfcheck involved, check the `verify-before-done`
skill (`/home/trido/.claude/skills/verify-before-done/SKILL.md`). Built 2026-08-01 from a
same-day pair: a selfcheck that PASSED in its author's session but FAILED under independent
re-run (§16's TZ bug — author's session inherited a correct `TZ`, the re-run didn't), and a
brand-new selfcheck that caught a real bug on its first execution (`EOFError` not an `OSError`
subclass) — the second is the skill working as intended. Core habit: run the selfcheck for real,
name its environment dependencies (TZ tops the list), re-run under a stripped/adversarial
variant, treat any cross-environment difference as the finding itself. Applies to the author
before claiming done AND to anyone re-verifying (baked into `arch-reviewer`'s mandate — see
`~/.claude/agents/arch-reviewer.md`). Point agents at this skill explicitly rather than
re-deriving the checklist each time.

## 20. Mark `decided_by: "user"` When a Real User Confirmed a Closure — Not Just "Seemed Reasonable"

**Root cause (2026-08-01, saga "coord-" round 5):** Wags's self-fix loop for check #5 reasoned
"aged-question pool has 0% natural drain rate" as the bug it was fixing, then used "pool went to
0" as evidence the fix worked — arch-reviewer caught the contradiction: a Mike session had
closed ~15 stale questions in an unrelated cleanup that overlapped in time. Nothing on a closure
event recorded WHO decided it, so the self-verification couldn't tell "coincidental cleanup"
from "the fix's mechanism working." Generalizes a risk arch-reviewer flagged narrowly (round 2:
don't let a CRON auto-expire a real pending decision) — same danger when a human OR agent session
closes a question on its own judgment, however well-reasoned, without the user confirming in the
moment.

**Rule:** when an `answer`/`decision` closes a money/decision-adjacent `question`, include
`"decided_by": "user"` in the payload ONLY when the user actually confirmed it in real time.
When Mike/an agent closes on its own judgment (even well-evidenced) — omit the field, or use
`"decided_by": "agent"`. Not a quality judgment on the closure — a provenance record, so later
counting/reporting can separate "confirmed by a person" from "judged, not confirmed."

**Enforced by:** `bin/bus_question_audit.py`'s closure-provenance report (same day) — breakdown
by `decided_by` for the last N days (`--provenance-days`, default 14), always shown, feeding
weekly review. A report, not a gate — high unmarked-agent-closure counts prompt spot-review,
not wrongdoing by itself.

**Not shipped:** enforcing this at `append_event.sh` (would touch every fleet-wide caller for a
field only meaningful on question-closures). Documented convention + report, same tier as §7/
§10/§11/§13 — judgment calls without a clean mechanical gate.

## 21. Tỉ suất Lợi Nhuận Per-Position Trong Báo Cáo: BẮT BUỘC Cộng Lại Cổ Tức Tiền Mặt

**Root cause (2026-08-02, 3 báo cáo client-facing tháng 7/2026 — tuần 20-24, tuần 27-31, tháng 7):**
báo cáo tính lãi/lỗ từng mã bằng `(giá cuối kỳ − giá vốn)/giá vốn`. Ngày chốt quyền (ex-date), giá
sàn giảm **đúng bằng** cổ tức — giá trị chuyển từ *giá cổ phiếu* sang *tiền mặt* — nên công thức đó
chỉ bắt phần giá và **báo lỗ oan** cho mã trả cổ tức cao: NCT **−11,6% → −3,1%**, SAB **−8,1% →
−1,7%**. Nghiêm trọng hơn con số: lỗi **đảo dấu một kết luận attribution** (rổ CAPIT bị mô tả "chỉ
gánh 2,6% mức lỗ" trong khi thực tế **LÃI +5,66tr**). NAV tổng vẫn đúng (tiền cổ tức đã nằm trong
`totalCash`) — đây chính là lý do lỗi sống sót: mọi phép đối soát NAV đều PASS.

**Quy tắc:** mọi tỉ suất per-position trong bất kỳ báo cáo nào (ngày/tuần/tháng) **PHẢI** đi qua
`mike/bin/dividend_adjusted_return.py` — không tự viết lại công thức, không suy cổ tức bằng hiệu
`Close − Price` (quan hệ là phép NHÂN; hiệu số biến thiên theo giá và cho sai cả số tiền lẫn ex-date).
Sự kiện chưa đối soát được với sổ broker bị gắn cờ `UNVERIFIED` và **CẤM** đưa vào báo cáo gửi nhà
đầu tư — vì `Close/Price` không phân biệt được cổ tức tiền mặt với chia tách cổ phiếu.

Chi tiết cơ chế, 4 cái bẫy cụ thể và cách kiểm chứng 3 nguồn độc lập:
**`mike/kb/data_registry/price-volume/ticker_close_vs_price_dividend_adj.md`**. Bổ sung cho §6
(provenance số liệu báo cáo), không thay thế: §6 lo "số này lấy từ nguồn có thẩm quyền chưa", §21 lo
"công thức có bỏ sót cấu phần lợi nhuận nào không".
