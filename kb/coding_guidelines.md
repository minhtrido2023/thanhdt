# Coding Guidelines — áp dụng cho toàn fleet

Behavioral guidelines to reduce common LLM coding mistakes.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

**Enforcement policy (thêm 2026-08-01, user mandate — "đẩy bài học cũ ra công cụ/linter thay vì
văn xuôi"):** khi 1 lesson dưới đây có thể diễn đạt thành 1 PATTERN CƠ HỌC trong code (không cần
phán đoán ngữ nghĩa) — mục tiêu là 1 check tự động chặn commit, KHÔNG chỉ thêm đoạn văn xuôi này
để hy vọng agent tương lai nhớ đọc. Nguyên tắc theo đúng SRE postmortem culture (Google SRE
workbook — action item tốt nhất là 1 CI rule, không phải 1 dòng ghi chú) và kỷ luật viết rule của
Semgrep ("1 rule bắt đúng 2 lần còn hơn 1 rule bắt nhầm 200 lần" — luôn test rule mới trên file
thật trước khi bật, không đoán). Cơ chế đang có, đã verify bằng `git commit` thật (không chỉ đọc
lại): **`bin/shellcheck_gate.sh`** (pre-commit hook, ShellCheck — bắt được cả 4 sự cố quoting
thật trong bash strings/heredoc-as-dispatch-prompt 2026-07-17→08-01, xem §15 + `kb/incidents/
2026-08/2026-08-01-shellcheck-precommit-gate.md`). Setup 1 lần/repo (hook dùng chung mọi
worktree): `pip install --user pre-commit shellcheck-py && pre-commit install`. Không phải mọi
lesson đều mechanize được — nhiều mục dưới đây (§7, §10, §11, §13) là quy trình/judgment call,
KHÔNG có pattern cú pháp rõ ràng để lint; giữ nguyên dạng văn xuôi là đúng, không phải thiếu sót.

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
overlapping — it does nothing for one run dying mid-write between the external action and
persisting that fact locally. Fixed in `trading_bot/executor.py` (`_ghost_tickers` + atomic
`_save_state`); apply the same reasoning to every new script.

Before writing any script that calls an external system with a side effect (place an order,
send a message, write a shared file, call an API that isn't naturally idempotent):
- Ask: "if this process is killed right after the external call succeeds but before local
  state is saved, what does the next run do?" If the answer is "repeats the action," that's
  a bug, not an edge case.
- Prefer checking the external system's own source of truth (broker's live order book,
  the sent-messages log, etc.) over trusting only local state — local state can lag reality.
- When you can't tell whether an action already happened, **fail-safe pause and flag for a
  human** — do not guess-and-merge into local state, and do not silently proceed as if
  nothing happened. Guessing wrong is worse than stopping.
- Persist "the action happened" as close to the actual external call as possible (write
  immediately after, not batched at the end of a longer loop) — this shrinks the crash
  window rather than closing it, but every bit of shrinkage matters.
- Writes to shared state files must be atomic (`tmp` + `os.replace`/`os.rename`), never a
  direct overwrite — a kill mid-write must never leave a half-written file for the next run
  to trust.

## 6. Verify Report Data Provenance (client-facing numbers)

**A field's name and a plausible-looking value are not verification.** Root cause (2026-07-03
weekly-report incident, `kb/incidents/2026-07/2026-07-03-weekly-report-estimated-cost-basis.md`): a P&L calc read a snapshot field labeled
`"source": "ref_px_approx"` (an approximate price for an unrelated purpose) and reported it as
real cost basis, unchecked, into a client-facing document.

Before any number reaches a report (daily/weekly/monthly, or any client-facing artifact):
- Trace it back to the system that is *authoritative* for that fact — for trade prices/fills,
  that is the broker's own fill confirmation (`dnse_raw_*.jsonl`'s `averagePrice`/
  `fillQuantity`), never a downstream summary file written for a different purpose.
- Cross-check against a second independent source (internal execution journal `FILL` events,
  an already-audited snapshot) before trusting either — see `bin/verify_account_snapshot.py`,
  the only script now permitted to compute cost-basis/P&L for a SpaceX trading report. If two
  independent sources disagree beyond a tight tolerance, fail loudly (non-zero exit) — do not
  silently pick one and proceed.
- Aggregate totals can be accidentally right while per-item attribution is wrong (NAV here only
  depends on quantity × market price, not cost basis, so it happened to survive unscathed) —
  don't let a correct-looking total substitute for verifying the breakdown a client will read.
- This is the same principle as [[verify-real-facts-dont-self-invent]] and the artifact-vs-
  self-report rule (MIKE.md §Quy chuẩn bắt buộc mục 2) applied to report generation: verify the
  artifact, don't trust a field because its value looks plausible.

**Standing pipeline for ALL cadences (daily/weekly/monthly), locked in 2026-07-03:**
1. `bin/verify_account_snapshot.py` — true cost basis per ticker, cross-checked (broker raw log
   vs internal journal vs any audited snapshot).
2. `bin/daily_nav_snapshot.py` — true NAV for one date (MTM stock + real cash − real margin debt
   from a fresh `dnse_raw_*.jsonl` `balances` record), appended to `nav_history_{account}.csv` so
   every cadence reads the same day-by-day series instead of recomputing NAV differently each time.
3. `bin/reconcile_equity.py` — the two-sided identity check (`starting_capital + unrealized_P&L −
   fees − margin_interest == market_value + cash − margin_debt`); confirmed fee rate is
   **0.075%** of true cost basis (not 0.1%, corrected 2026-07-03), and any residual after that
   should be checked against an *estimated* margin-interest accrual (`--margin-rate-annual`,
   12.5%/year per user, unverified against DNSE's actual contract) before being called
   "unexplained" — see the 2026-07-03 report for a worked example (residual matched ~4 days of
   accrued-but-not-yet-posted interest almost exactly).
4. If a number can't be traced through this pipeline, don't put it in the report — say what's
   missing instead of estimating silently.

**Bright-line rule — same-day data: DNSE API, never BigQuery (user directive, 2026-07-09).**
BQ (`tav2_bq.ticker`/`ticker_1m`) only syncs overnight (`sync_bq_cache_daily.sh`, 23:45 ICT) —
any script reading BQ for "today's" price/volume before that sync is reading **yesterday's**
close, structurally, every time (BQ physically cannot have today's data yet). Incident
2026-07-09 (`kb/INCIDENTS.md`): a plan generator priced 2/4 orders off stale BQ close (+5.7%
off) while 2 others happened to use live DNSE — the inconsistency is what let it go unnoticed.
- Any same-day/live calculation (order sizing, ref prices for a T+1 plan, live NAV/exposure
  checks, anything a report will call "today's" number) MUST read DNSE (`dnse_api.py`
  secdef/latest_trade/positions/balances) — never BQ — regardless of what hour the script runs.
- BQ is fine ONLY for: (a) historical/backtest queries on past trading days, (b) same-day
  queries run AFTER BigQuery's own daily sync has demonstrably completed (verify via
  `bq_freshness_check.sh`'s own freshness gate, not by assuming "it's after 18:00 so it must be
  synced" — confirm the gate passed).
- When adding this constraint to a dispatch prompt (LLM-authored script/plan, e.g. DollarBill),
  state it as an unconditional MUST with a concrete example of the wrong vs right source (see
  `mike/bin/bq_freshness_check.sh`'s DollarBill prompt for the wording already in place) — a
  general "verify your data" reminder does not reliably stop an LLM from reaching for whichever
  source is easiest to query in the moment.

**Cadence-specific scope** (content depth differs; the verification pipeline above does not):
- **Daily**: keep it short — trades executed today, NAV + day-over-day change, and a margin/risk
  flag if one exists. No attribution, no methodology appendix.
- **Weekly**: full narrative (see `mike/reports/SpaceX_weekly_report_*.md` as the reference
  template) — activity log, incident disclosures, sector/position tables, next-week plan, full
  methodology appendix.
- **Monthly**: apply institutional asset-management conventions on top of the weekly template —
  MTD/QTD/YTD returns, benchmark comparison, sector/name attribution, risk metrics (drawdown,
  volatility — once enough daily NAV history exists), fee/expense summary, compliance
  disclosures, outlook. Same verified-data pipeline underneath; more sections on top.

## 7. Onboarding a New Account With Legacy/Excluded Holdings

**When an account brought under management already holds positions the bot didn't buy** (e.g.
ZaloPay's pre-existing DGC position, kept for its own thesis under a trading restriction — see
`kb/INCIDENTS.md`), don't hand-roll a one-off workaround — use the general mechanism, since more
accounts of this shape are expected:

1. **Declare it in config, not code**: set `"excluded_tickers": [...]` on the account's profile
   in `secrets/trading_bot_accounts.json` (field added to `ACCOUNT_DEFAULTS` in
   `trading_bot/config.py`). Empty by default for every other account.
2. **Enforcement lives in ONE place**: `trading_bot.plan.filter_excluded_tickers()`, called from
   `bot_execute.py` immediately after `load_plan()` — this makes it apply no matter how the plan
   was generated (DollarBill's LLM-authored JSON, `bot_prepare_plan.py`'s templated strategy, or
   a hand-edited file), so a plan generator forgetting the exclusion can never actually place a
   forbidden order. Never rely on the plan generator remembering to leave the ticker out.
3. **Size the strategy against `active_nav`, not total NAV**: `bin/compute_active_nav.py --account
   <label>` computes `total_nav − market_value(excluded_tickers)` from LIVE broker
   positions/prices (no dependency on our own execution journal, unlike
   `verify_account_snapshot.py`/`daily_nav_snapshot.py` — those need fill history WE recorded,
   which doesn't exist for a position the account already held before bot management). Whoever
   builds the plan (DollarBill, or Mike dispatching it) must use this number as the allocation
   basis — sizing V2.4 targets against total NAV when a third of it is locked in an excluded
   position tries to deploy capital that isn't actually available.
4. **Known gap, not yet closed**: `daily_nav_snapshot.py`'s P&L computation still assumes
   journal-tracked fills for cost basis, so it can't yet produce a correct unrealized-P&L
   breakdown for legacy positions (NAV/active_nav are correct today via
   `compute_active_nav.py`; a P&L-capable version for legacy-position accounts is separate future
   work — needed before any report that compares this account's *return*, not just its NAV,
   against a clean-slate account like SpaceX).
5. **Test it**: `excluded_tickers_selfcheck.py` is the reference — covers empty/None config
   no-op, single/multi-ticker exclusion, the all-excluded edge case, and exact-case-only
   matching (a lowercase config typo must not silently fail to exclude). Extend this file rather
   than writing a parallel one when the mechanism itself changes.

**Test-infrastructure lesson (same root cause, different files):** `Executor.__init__` eagerly
loads `state.json` from the DEFAULT `(account, plan_date)` path *before* test code can redirect
it to a tmpdir — a stale file from an earlier run (or another selfcheck reusing the same account
tag) silently corrupts the next run's starting state. Every selfcheck driving `Executor` needs
BOTH a unique account tag AND a module-load-time cleanup of any stale fixture at the default path
— see `ghost_order_selfcheck.py`'s `TAG` comment for the pattern.

## 8. Never Write Experiment Output to a Canonical / Registry-Pinned Filename

**Root cause (2026-07-06 R3-CSV overwrite, `data/results_registry.md` mục `## KẾT QUẢ THAM CHIẾU
phiên 2026-06-19` — cite by section title, not line number: line refs in this ledger drift as new
entries get inserted, see the file's own top-of-file navigation note):** an output
filename built from only a SUBSET of env knobs (e.g. `BASKET_SELECT` / combination-mode had no
suffix) — a config axis that materially changes the result but has no filename suffix lets an
experiment run silently clobber the registry-pinned production baseline. A lock wouldn't help —
both runs were legitimate, just colliding on an output name.

Rules when a script's output feeds `data/results_registry.md` or any pinned baseline:

- **Any config axis that changes the numbers MUST change the filename.** If a script derives its
  output path from env vars, every result-affecting knob needs a suffix tag — or the run must
  pass an explicit `OUT_CSV=` override. Before running an experiment variant, check whether your
  changed knob is actually reflected in the output filename; if not, set an explicit distinct
  output path.
- **Experiment/ad-hoc runs write to a clearly non-canonical name** — add an experiment suffix
  (`_exp_<what>`, `_probeNNN`, dispatcher job-id) so a canonical pinned CSV is never a possible
  target. Treat the registry-pinned filenames as read-only artifacts owned by the pinned command.
- **Regenerating a pinned baseline: use the EXACT pinned command AND the pinned interpreter.**
  The registry pins `$DNA_PYEXE` (= `/home/trido/thanhdt/wc_venv/bin/python`, pandas 3), NOT
  system `python3` (pandas 2.3, which cannot unpickle `data/earnings_surprise_data.pkl` — raises
  `NotImplementedError` in `NDArrayBacked.__setstate__`). Copy the command verbatim including
  `$DNA_PYEXE`; don't substitute `python3` even if a prompt writes it that way.
- **After regenerating, verify before trusting**: metric in expected range, `self-check 0 VND`,
  and an independent recompute from the CSV (`extract_peryear.py <CSV>`) matching the print — then
  note the regeneration in the registry so the overwrite episode is auditable.

**§8b. `data/bq_cache_asof*` snapshot retention (policy chốt 2026-07-30, user directive, sau audit
`fleet_housekeeping` job Wags_20260730_112912).** Mỗi snapshot ~2,0GB, không tái tạo được (BQ
time-travel tắt, `ticker`/`ticker_prune` TRUNCATE+rebuild mỗi ngày) — xoá sai = mất vĩnh viễn bằng
chứng cho 1 kết quả pinned.

- **Giữ tối đa 1 bản/tháng.** Nhiều snapshot cùng tháng dương lịch (vd nhiều lần re-pin do restate
  trong cùng tháng) → chỉ giữ bản MỚI NHẤT của tháng đó là bản "hiện hành" cho AS-OF vintage.
- **>3 tháng tuổi → xoá được, NẾU không có vấn đề** — "không có vấn đề" nghĩa là: (a) KHÔNG phải
  bản snapshot pin CHÍNH THỨC hiện hành cho 1 kết quả sống trong `current_ops.md`/
  `results_registry.md` (grep xác nhận trước khi xoá, đúng kỷ luật §10 — không đoán theo tuổi/tên);
  (b) KHÔNG được đánh dấu **"mốc lịch sử đặc biệt — giữ riêng"** (vd `bq_cache_asof20260728` =
  mốc TRƯỚC restate DT5G 07-29, bằng chứng duy nhất cho attribution +0,47pp CAGR do trôi dữ liệu —
  **KHÔNG BAO GIỜ xoá theo tuổi**, chỉ xoá nếu người quyết định tường minh việc này không còn giá
  trị bằng chứng).
- **Xoá snapshot cũ CHỈ SAU KHI số pin mới đã qua quant-skeptic** — không xoá bản đang dùng để
  chờ verify xong bản thay thế (tránh mất cả 2 nếu bản mới bị REFUTED).
- **Không tạo cadence re-pin riêng** — gắn vào nhịp snapshot BQ hàng tháng Winston đã dựng
  (`bin/bq_monthly_pin.py`, cron ngày 1 hàng tháng) thay vì đặt lịch mới.
- Nguồn đề xuất gốc: Taylor job `Taylor_20260729_155142`, `agents/Taylor/research/asof_vintage_label_20260729.md`.

## 9. Check `mike/kb/data_registry/` Before Wiring a New Data Source

**Root cause (2026-07-11 SIGNAL_V11 base-leak, `kb/INCIDENTS.md`):** four production consumers
silently read a trap table (documented as a trap in `CLAUDE.md`, but nothing forced a check
against it before each new script picked a table name that *sounded* right) instead of the real
production regime table — causing a live paper-trading book to enter 6 tickers on a fake signal.

**Mandatory rule, user directive 2026-07-11:** before reading ANY data source (BQ table, local
CSV/pickle/JSON, published state file) in new research or production code — check
`mike/kb/data_registry/` first (start at `index.md`; it is now an OKF tree, 1 source = 1 file —
`kb/data_registry.md` is a stub redirect). Grep still works: `grep -rn "<source>" mike/kb/data_registry/`.
- If the source is listed as `CANONICAL` — use it directly.
- If listed as `TRAP` — read the "Bẫy" section before touching it; there is almost always a
  correctly-named sibling table/file to use instead.
- If listed as `DEPRECATED/DEAD` — don't wire it into anything new; it may still exist for
  historical reference only.
- **If the source isn't in the registry at all** — don't assume it's safe by default. Add an
  entry (status verified against real evidence — crontab, file mtime, code that writes it — not
  guessed from the name) before wiring it in, or ask Winston/Mike to verify first.

**Ownership**: Winston (data-ops) keeps the registry current ad-hoc whenever a new source
surfaces in other work. A full periodic audit (re-verify every entry's freshness, sweep the
codebase for sources still missing) is folded into the existing Friday KB editorial review
(`kb_nightly.sh`'s headless Mike dispatch) rather than a separate new cron job.

**When dispatching Taylor (or anyone) for new R&D**: the dispatch prompt should explicitly say
"tra `mike/kb/data_registry/` (index.md) trước khi chọn nguồn dữ liệu, đặc biệt bảng market-state/regime"
— matching the same pattern already used for DollarBill's DNSE-vs-BQ rule (§6). A general
"verify your data" reminder does not reliably stop an LLM from reaching for whichever table name
sounds closest to what it needs in the moment; naming the specific registry file does.

## 10. When a File Becomes Canonical, Archive Its Superseded Variants in the Same Pass

**Why this matters (2026-07-11 fa_ratings incident, `kb/incidents/2026-07/2026-07-11-fa-ratings-8l-silent-write-failure.md`):** confirming which file is
canonical is only half the fix — near-identical variant files left in the repo root under
slightly different names are exactly the landmine that causes the next agent (or human) doing a
quick grep to pick the wrong one.

**Rule: when a script/file is confirmed canonical for a purpose** (a builder is identified as *the*
one that produces a pinned table, a cron is installed pointing at a specific script, a migration
decision names a specific file as the production source) — in the **same commit/session**:
1. **Identify superseded variants** — files with a similar name/purpose that are NOT the confirmed
   canonical one, and grep the whole repo (scripts + crontab) to confirm zero active callers
   reference them. Never archive on a name-similarity guess alone; verify with a real grep.
2. **`git mv` them into an `archive/` subdirectory** (preserving git history, not `rm`) — this is
   reversible and auditable, unlike deletion, but it removes the file from the root namespace where
   a casual `ls`/glob would surface it as a live candidate.
3. **Update the source's file in `mike/kb/data_registry/`** to reflect the new archive path and mark the entry
   `DEPRECATED` with a pointer to the confirmed canonical replacement (per §5's obsolete-marking
   rule if this is a data-source migration, or a plain note if it's just script hygiene).
4. **Do NOT apply this to genuine audit-trail artifacts** — rejected-hypothesis backtest CSVs, dry-run
   logs proving a mechanism works, anything already namespaced into an experiment directory per §8
   (`data/*_exp/`, `agents/<id>/probe_*/`). Those are inert data files kept as evidence, not scripts
   that could be run by mistake — archiving them is unnecessary churn, not safety.

**Periodic check**: `bin/data_registry_audit.sh`'s stale-duplicate scan (added 2026-07-11) flags
repo-root files with a name similar to an already-CANONICAL registry entry that are NOT yet under
`archive/` — surfaced in the Friday KB editorial review for a human/Winston decision, not auto-moved.

## 11. Check `mike/kb/cron_registry.md` Before Adding or Changing a Cron Schedule

**Root cause (2026-07-12 C1 CRITICAL, `kb/incidents/2026-07/2026-07-12-audit-cron-order-publish-cache-t1.md`):** a publish script silently read a
process-inherited T-1 cache env var for ~2.5 weeks despite its own comment stating live BQ as the
source of truth — the code didn't actually enforce the intent the comment stated. Nobody had
asked "what vintage does this publish step actually read?" before a downstream gate tightened and
turned the mismatch into a structural, always-fails contradiction.

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
giống hệt nhau = gần như chắc chắn đang đọc chung không lọc — đây là dấu hiệu rẻ nhất, bắt được cả
3 sự cố trên nếu có ai chạy.

**Grep sweep không đủ nếu chỉ tìm tên file.** Lần sweep 2026-07-19 grep `dnse_raw` vẫn bỏ sót
`eod_trading_report.sh` vì file CÓ nhắc tên nhưng lọc thiếu ở 1 nhánh. Sweep đúng = với MỖI hit,
đọc xem record có bị lọc account trước khi vào phép tính hay không (audit 2026-07-22: 4/4 script
kế toán đã lọc đúng; `execution_quality_review.py` chỉ lọc KHI truyền `--account`, mặc định gộp cả
2 account — chấp nhận được cho công cụ review ad-hoc, KHÔNG được dùng làm nguồn số báo cáo).

## 13. Sửa 1 file `kb/` cần Mike duyệt trước khi live → ghi ra `<file>.proposed`, KHÔNG sửa tại chỗ

**Root cause (2026-07-30, 2 lần cùng ngày):** một agent được dặn "sửa `kb/canonical.md` nhưng để
CHƯA commit, chờ Mike đọc diff" — cả 2 lần, `bin/consolidate.sh` (cron mỗi giờ + tự trigger sau MỌI
dispatch) quét `git add kb/` + `git commit -- kb/` **BLANKET**, cuốn bản sửa dở vào 1 commit thường
lệ trong vài chục giây, trước khi Mike kịp đọc. Thử vá bằng cơ chế "hold-list" (`state/
kb_pending_review.txt` + TTL + pathspec exclude trong `consolidate.sh`) — arch-reviewer bác bỏ:
`bin/fleet_backup.sh` (00:00 ICT, `git add -A`) và `bin/kb_nightly.sh` (02:00 ICT, `git add kb/`)
vẫn quét blanket ĐỘC LẬP, không biết gì về hold-list; đo được **32,8% job dispatch bắt đầu đúng
trong khung giờ mà TTL không kịp cảnh báo trước khi 1 trong 2 sweeper đó quét qua** — và khi bị
cuốn, `publish_context.sh` (đọc `git show HEAD:<path>`) xuất bản đúng bản CHƯA duyệt kèm banner
khẳng định "đây là bản đã duyệt" — cổng mở nhưng tự nhận là đóng, tệ hơn không có cổng nào.

**Quy ước đúng, đã dùng sẵn cho code (`bin/*.sh.draft`, §10) — áp dụng y hệt cho nội dung `kb/`:**
khi 1 agent/Mike sửa `kb/<file>` mà cần Mike đọc/duyệt trước khi live, **ghi bản mới ra
`kb/<file>.proposed`** (file anh em, cùng thư mục) — **KHÔNG đụng vào `kb/<file>` gốc**. Vì:
- `consolidate.sh`/`fleet_backup.sh`/`kb_nightly.sh` chỉ `git add`/`commit` các đường dẫn **thật**
  — file `.proposed` được add như 1 file mới vô hại, không ảnh hưởng nội dung file gốc.
- `publish_context.sh` chỉ `cat` đúng tên file thật (`current_ops.md`, `canonical.md`,
  `projects/INDEX.md`) — không bao giờ đọc `.proposed`, nên bản đang chờ duyệt **không thể** lọt
  vào `context_pack.md` dù có bao nhiêu lần consolidate chạy.
- Các file role-scoped `@`-import thẳng từ working tree (`context_safety_core.md`,
  `context_planning_mini.md`, `context_execution_mini.md`, `context_dataops_mini.md`,
  `context_ops_mini.md`) — hold-list KHÔNG che được các file này (chỉ publish_context.sh mới hiểu
  hold-list); `.proposed` che được VÌ agent đơn giản không viết vào file thật.
- **Không cần state file, không cần TTL/debounce, không cần lock** — không có gì để mất-cập-nhật
  hay quên-release: `.proposed` mồ côi vô hại (Mike hoặc `kb_nightly.sh` grep `find kb/ -name
  '*.proposed' -mtime +1` định kỳ nhắc dọn/áp dụng, không phải gate).

**Mike áp dụng khi duyệt xong:** đọc `diff kb/<file> kb/<file>.proposed`, nếu OK →
`mv kb/<file>.proposed kb/<file>` rồi `git add`+`commit` như thường lệ (Mike tự commit, không dựa
consolidate.sh sweep hộ). Nếu cần sửa thêm → sửa tiếp `.proposed`, không đụng file gốc, không lo
mất bản đang chờ duyệt vì không tiến trình nào khác động vào đường dẫn `.proposed`.

**Dặn rõ trong MỌI dispatch prompt yêu cầu "sửa X nhưng để Mike duyệt trước":** nói thẳng tên file
`.proposed`, đừng chỉ nói "để uncommitted" — đó là chỗ 2 lần sự cố hôm nay bị hiểu nhầm thành "sửa
tại chỗ, đừng git commit" trong khi mối nguy thật không nằm ở git.

## 14. Every Internal Producer→Consumer Pipeline Pair Needs a Real Freshness Check, Not Just a Loose Tolerance

**Root cause (2026-07-10 DT5G cron-order incident, bus question `retro-pattern-recurring-
dataprovenance-2`):** `daily_refresh_v34b` computed DT5G at 23:15, but `bq_freshness_check` read
it at 17:30 — 6 hours *before* that day's compute ran, so it silently read *yesterday's* value
every single day. This wasn't a BQ-vs-DNSE source mistake (§6's rule doesn't cover it — DT5G has
no DNSE-equivalent live source); it was two **internal cron jobs racing**, hidden for weeks by a
tolerance (`MAX_STATE_LAG=2`) loose enough to never trip on a 1-day-late read. §6 closed the
narrow cut (same-day price/volume must come from DNSE, not BQ); this rule generalizes past it —
the actual failure mode is "code silently consumes data that isn't ready yet, hidden by a
tolerance or schedule assumption wider than the real risk," and that shape recurs for ANY
producer→consumer pair, not just BQ-vs-DNSE.

**Rule:** when a script's output feeds another script that runs on its own cron schedule (not
triggered directly by the producer finishing) — before trusting "producer already ran by the
time I run" on schedule alone:
- Add a **real freshness precheck** in the consumer: read the producer's own timestamp/marker
  (a `_asof`/`_generated_at` field, file mtime, a `*_ok` flag) and confirm it's from *today's*
  run — not just "a file exists" or "cron order says it should be done by now." Schedule
  assumptions drift (a producer that starts running late, a job that silently fails but leaves
  yesterday's output in place) and a precheck is the only thing that catches it.
- Set the tolerance **as tight as the real risk allows** — wide enough to survive normal jitter
  (a job finishing 5 minutes late), tight enough that a full day's staleness (or a full skipped
  run) trips it. `MAX_STATE_LAG=2` days is the concrete anti-pattern: it papered over a
  structural 6-hour-early read for weeks because "2 days behind" never looked urgent.
- When adding or changing a cron schedule for either side of a pair, this check is now folded
  into §11's mandatory 4 questions (`kb/cron_registry.md`) — "đọc gì+vintage" already asks this;
  treat "does the consumer verify freshness or just trust timing" as part of answering it, not a
  separate step to skip.
- This applies to ANY internal producer→consumer relationship on independent cron schedules —
  not just BQ/DNSE, not just DT5G. Same reasoning as §6 and §9, generalized: verify the artifact
  you're about to consume is actually the one you think it is, don't infer it from schedule math.

**Not a mandate to retrofit every existing pair at once** — apply going forward on every new/
changed cron pair (§11), and treat a periodic sweep of *existing* pairs (checking `cron_registry.md`
for any pair whose consumer trusts schedule-order alone) as Friday KB editorial review material,
same as the data-registry and stale-duplicate audits already folded in there.

## 15. Bash Strings Doubling as LLM Prompts: Escape `"`/`` ` ``, Then Verify by Running, Not Reading

**Root cause (4 real incidents, 2026-07-17 → 2026-08-01, all the same shape):** this fleet's
dispatch scripts (`daily_retro.sh`, `kb_nightly.sh`, `fleet_housekeeping.sh`) build large
multi-line bash double-quoted strings that double as LLM prompt text — Vietnamese prose full of
markdown emphasis (`"quoted phrase"`) and inline-code backticks (`` `filename` ``). Both `"` and
`` ` `` are live bash metacharacters even inside a double-quoted string (unlike single quotes) —
an unescaped one silently terminates the string or triggers real command substitution. Every
occurrence went undetected for weeks because the symptom is either a **fatal crash before any
notify.sh call runs** (daily_retro.sh: 2 nights silent) or a **corrupted-but-still-launched**
dispatch (kb_nightly.sh: `dispatch.sh` received extra positional args, exited 1 immediately —
2 weeks of Friday/Saturday editorial review silently never ran) or **bash executing the quoted
text as a command** (`fleet_housekeeping.sh --help`: `` `datacold` `` got run as a command,
silently swallowed, word vanished from the output). "The script ran" / "the dispatch launched"
was mistaken for "the content parsed as intended" every time.

**Rule:**
1. Any `"` or `` ` `` inside a bash double-quoted string must be escaped (`\"`, `` \` ``) — no
   exceptions, even for text that "looks like it's just prose."
2. **Prefer a single-quoted heredoc** (`<<'EOF'`) for large prompt-text bodies when you don't
   need variable interpolation — it needs zero escaping of either character (see
   `bin/weekly_ops_audit.sh` for the pattern). If you DO need `$VAR` interpolation, either accept
   the escaping burden or hardcode the (usually-fixed) absolute paths as literal text instead.
3. **Verify by running, not by reading.** Re-reading the text "looks fine" is exactly how all 4
   instances shipped — a quote 40 lines into an 80-line string is not something a re-read catches
   reliably. Extract the assignment/heredoc in isolation and actually execute it (see the 4
   incident writeups for the exact technique used each time) before trusting a fix.

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
unrelated loop in the file (not scoped to loops that actually read the shared file) — this needs
dataflow-aware rule engineering (semgrep taint mode or similar), not a quick pattern match, to
reach the "fires twice at 100% accuracy" bar. Left as a documented prose lesson (§12) until
someone has time to build and test that properly — shipping a noisy rule would erode trust in
the whole gate faster than having no rule at all.

## 16. Never Trust the Host's System Timezone for Date/Time Comparisons — Anchor Explicitly

**Root cause (2026-07-31, `bin/dt5g_writer_watch.py`):** the host runs `Etc/UTC`
(`timedatectl` confirmed), but the code read a BQ table's `lastModifiedTime` (epoch millis, UTC)
with `datetime.fromtimestamp(ms/1000.0)` and a comment claiming *"process TZ = ICT trên host
này"* — a false, unverified assumption. Under the host's real UTC clock, a write that happened
at 19:01 ICT got labeled "12:01" and compared against ICT-denominated time windows, missing by
exactly 7 hours. The bug was **real but latent**: production cron callers happened to
`source wc_env.sh` (which exports `TZ=Asia/Ho_Chi_Minh`) before invoking the script, so it never
fired live — it was only caught because Mike ran the same code by hand (no inherited `TZ`) while
independently verifying a dispatched fix, and separately by running the script's own selfcheck
under `env -u TZ`.

**Rule:** any code that computes "today," parses a date, or compares two timestamps for
freshness/staleness MUST anchor the timezone explicitly — never assume the calling process
happens to have the right `TZ` in its environment:
- Python: `datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))` / `datetime.fromtimestamp(epoch_ms/1000,
  ZoneInfo("Asia/Ho_Chi_Minh"))` — not bare `datetime.now()`/`.fromtimestamp()` with an implicit
  local-time interpretation.
- Bash: `TZ='Asia/Ho_Chi_Minh' date ...` — not bare `date` in any script that compares dates
  (see `bin/csv_fresh_today.sh` for the reference pattern, added same day as this rule).
- When writing a selfcheck for freshness/date logic, run it under `env -u TZ` (and ideally a
  second foreign TZ, e.g. `TZ=America/New_York`) — the exact test that caught this bug. A
  selfcheck that inherits the developer's own correctly-set `TZ` will pass even when the
  underlying code is wrong, exactly as happened here on the first pass.

**Evaluated and NOT shipped:** a static grep/lint gate for this class of bug (`datetime.now()`/
`date.today()`/`utcnow()` without `tz=`/`ZoneInfo`, or `date +...` without a `TZ=` prefix) —
measured against the real repo: **243 matches for the naive Python pattern alone**, spot-checked
finding zero live bugs among them (the one real bug already fixed) and several false positives,
including the gate matching its **own explanatory comment** in the just-fixed file. Same verdict
as §12's Semgrep evaluation: a rule this noisy erodes trust in the whole gate faster than having
none. The cheaper, already-verified-effective mitigation is the pattern this fleet already relies
on for the actual class of bug found today (§14): **run the changed code path for real**, under
an adversarial environment (`env -u TZ`), rather than trying to catch it by static reading alone.
Documentation (this section) plus a single `TZ=Asia/Ho_Chi_Minh` export at the top of the
crontab (so every cron-invoked script gets a correct ambient `TZ` by default, closing the
specific gap that made this bug latent-not-live) is the shipped fix — not a lint rule.

## 17. A Reader Reporting "Still Open" State Must Scan Every Retention Tier a Mover Can Reach

**Root cause (2026-08-01, audit kiến trúc fleet — Fable plan + Opus adversarial critique,
so sánh với Paseo):** `bin/mike_json.py`'s `trace`/`verify-coverage` commands globbed only
`bus/inbox/*.jsonl` (hot) — a job/event older than the archive threshold (`kb_nightly.sh`
Phase 1b2 = 30 days for bus events, `fleet_housekeeping.sh` Phase 1b3 for `bus/jobs/`) silently
came back "not found" instead of "archived." This is the SAME shape as the 2026-07-31 bug where
`ops_health_check.sh`'s check #5 lost visibility into 2 never-answered questions for over a
month (§ fixed, see `ops_health_check_selfcheck.py`) — but it is NOT the same fix. An adversarial
review first proposed a generic "conservation check" (`count_before == count_after +
count_archived`) — that invariant is trivially satisfied by every mover in this fleet already
(nothing is silently deleted, everything is genuinely moved); it would NOT have caught either
bug. The actual defect is per-READER, not per-mover: does THIS specific reader, which reports
unresolved/pending/backlog state to a human for a decision, scan every tier a mover can place
data into? A reader that only shows "recent activity" (e.g. `context_pack.md`'s "MỚI NHẤT"
section) is correctly hot-only by design — excluding 2-month-old chatter is the point, not a bug.

**Rule:** before shipping a new reader (or auditing an existing one) that answers "is X still
open / unresolved / pending," identify every mover that can place X's data into cold storage
(`kb/cron_registry.md` + this file's archival scripts — currently `kb_nightly.sh` Phase 1b2 for
`bus/inbox/`, `fleet_housekeeping.sh` for `bus/jobs/`, `logs/`, `bus/registry/`) and confirm the
reader globs ALL of them, not just the hot path. Use `mike_json.py`'s `_inbox_files()`/
`_agent_files()`/`_job_record_path()` helpers (added 2026-08-01) instead of hand-rolling
`glob.glob(".../inbox/*.jsonl")` again — that literal pattern is exactly what went stale twice.
Ship the new/fixed reader WITH a regression test in the extract-and-test style already
established (`ops_health_check.sh`'s `CHECK5_BEGIN`/`CHECK5_END` marker +
`ops_health_check_selfcheck.py`; `mike_json_archive_selfcheck.py` for `trace`/`verify-coverage`)
— a prose claim of "scans both tiers" is exactly the kind of self-report that has already failed
twice without a test forcing it to stay true as the archival layout evolves.

**Evaluated and NOT shipped:** a generic `conservation_check.py` invariant across every mover
(see root-cause paragraph above for why it targets the wrong layer). Also not shipped: a
blanket rewrite of every `bus/inbox` reader in the fleet to be archive-aware — `cmd_recent`
(shows only the newest N lines for `context_pack.md`) and the `cursor-advance` consolidator
cursor are correctly hot-only (their entire purpose is "what's new," not "what's still owed");
making them archive-aware would be a behavior change nobody asked for, not a fix.

## 18. Any Quant R&D Task (Backtest, IC Test, Gate/Selector Change) — Follow `.claude/skills/quant-research/`

Before designing or running any backtest, factor-IC test, or production-rule review — check the
`quant-research` skill (`/home/trido/thanhdt/WorkingClaude/.claude/skills/quant-research/SKILL.md`,
invoke via the Skill tool where available, or read directly in a headless dispatch). It's the
fixed order of operations this fleet has converged on from real jobs (2026-08-01 CAPIT
quality-exit + FSCORE-role reviews and earlier): scope by reading the real code first, check
`mike/kb/data_registry/`, pin the environment, declare N as independent events not row count,
match the statistical tool to N (IS/OOS when large, LOO+bootstrap when small — always disclosed),
verify at both position-tier and full-engine-tier, self-check 0 VND with the control leg
reproducing the pinned number, point-in-time joins only, look for dose-response across variants,
decompose kept-vs-added when basket size changes, reconcile against adjacent findings, DSR/PBO
only when a config is actually being recommended for wire, confirm production untouched via
`git diff`, quant-skeptic gate before any production-change recommendation, and independently
verify the artifact (not the self-report) before relaying a conclusion. When dispatching Taylor
for R&D, point at this skill explicitly in the prompt rather than re-deriving the checklist by
hand each time — see `bin/dispatch.sh` prompts from 2026-08-01 for the reference wording.
