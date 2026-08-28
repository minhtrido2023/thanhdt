# Coding Guidelines — phần MỞ RỘNG (tách khỏi `coding_guidelines.md` 2026-08-14)

> **File này KHÔNG auto-load.** `kb/coding_guidelines.md` vượt ngưỡng cứng 40KB ba lần liên tiếp
> (2026-08-01, 2026-08-05, 2026-08-10) và đã hết chỗ nén văn xuôi mà không mất fact quyết định →
> user duyệt phương án OKF-hoá tách section, đúng tiền lệ `context_pack.md` 2026-07-30.
>
> **Nội dung dưới đây được MOVE nguyên khối, byte-for-byte** — không nén, không viết lại, không
> đổi số hiệu §. Mọi tham chiếu chéo dạng "coding_guidelines §10/§11/§13/§15/§24…" trong code và
> dispatch prompt vẫn đúng số; chỉ đổi chỗ ở.
>
> Cách dùng: bảng "Mục đã tách" ở đầu `coding_guidelines.md` nói mục nào dùng khi nào →
> `Read mike/kb/coding_guidelines_ext.md` khi gặp đúng tình huống. Phần WHY/narrative gốc vẫn ở
> `kb/coding_guidelines_rationale.md` (không đổi).
>
> Thêm mục mới vào ĐÂY (thay vì file chính) khi luật đó dùng theo tình huống, không phải mỗi
> phiên — và thêm 1 dòng vào bảng con trỏ ở `coding_guidelines.md`.

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

> *(Khối dưới đây là §8b — phần thân §8 "đừng ghi output experiment vào tên file canonical" vẫn
> nằm ở `coding_guidelines.md`; chỉ mục con §8b về retention snapshot được tách sang đây.)*

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

**Bảng trên liệt kê FILE CODE — nhưng "lõi dùng chung" có 2 dạng nữa mà bản đồ import KHÔNG
thấy** (mở rộng 2026-08-20, escalation `retro-pattern-recurring-patternB-round2-4days` sau 4 ngày
Pattern-A tái diễn 08-16→08-19; cả 2 dạng đều đã cắn thật):

| Dạng lõi ẩn | Ví dụ đã cắn | Vì sao `selfcheck_scope_map.sh` mù |
|---|---|---|
| **CÔNG THỨC lặp lại ở nhiều consumer** (không phải file) | Bất biến NAV §25: mandate 08-18 thêm `egg.totalValue`, `nav_cum_dividend_selfcheck.py` ĐỎ 08-19 vì công thức trong nó chưa cập nhật — lệch đúng bằng egg (~100,2tr SpaceX / ~38,8tr ZaloPay) | Bản đồ đi theo `import`, mà công thức được **chép tay** vào từng consumer, không import từ đâu cả |
| **Module có consumer GIÁN TIẾP** (gọi qua subprocess / tên chuỗi / file dữ liệu trung gian) | `bin/oshares_live.py` sửa 3 lần trong ngày 08-19 ⇒ `corp_action_daily_selfcheck.py` IndexError ×2 | Đo thật 2026-08-20: `selfcheck_scope_map.sh bin/oshares_live.py` trả **RỖNG**, dù `corp_action_daily_selfcheck.py` phụ thuộc nó — nó không `import bin.oshares_live`, nó chạy subprocess |

**Hệ quả thao tác:** trước khi kết luận "file này ít phụ thuộc, chạy hẹp là đủ", ngoài
`selfcheck_scope_map.sh` phải thêm **một lượt `grep -rl "<tên file/tên công thức>" mike/bin`**.
Bản đồ import trả rỗng ≠ không ai phụ thuộc — nó chỉ có nghĩa "không ai IMPORT". Đây đúng chữ ký
§28: đừng suy từ sự vắng mặt trong MỘT biểu diễn ra sự vắng mặt trong thực tế.

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

## 25. "Tiền" KHÔNG Phải Một Con Số — Mỗi Consumer Phải Khai Rõ Đang Hỏi Câu Nào

**Luật:** bất kỳ code nào đọc số dư tiền từ broker PHẢI khai (trong tên biến hoặc comment ngay tại
chỗ đọc) nó đang hỏi câu nào trong hai câu dưới, và lấy đúng field của câu đó. Không có "field tiền
mặc định"; `DNSEBroker.get_cash()` **không** phải mặc định an toàn.

| Câu hỏi | Field ĐÚNG | Dùng ở | Sai thì hỏng kiểu gì |
|---|---|---|---|
| "Tôi **SỞ HỮU** bao nhiêu vốn?" (cơ sở NAV / mẫu số tính tỷ trọng mục tiêu) | **`totalCash − totalDebt` (+ `egg.totalValue` nếu consumer là NAV/pool, xem dưới)** | `daily_nav_snapshot.py:449`, `reconcile_equity.py`, `compute_park_trim.py` (mẫu số pool), `compute_active_nav.py` (§cash) | Khai THIẾU NAV đúng bằng tiền bán chưa settle ⇒ under-deploy, hoặc pool co lại đúng bằng lượng vừa bán ⇒ **vòng lặp tự kích bán tiếp** |
| "Tôi **TIÊU ĐƯỢC NGAY** bao nhiêu?" (sức mua đặt lệnh phiên này) | **`ppse.pp0Buy`/`qmaxBuy`**, hoặc `availableCash` khi không gọi được ppse | `DNSEBroker.get_cash()`, `check_plan_funding()`, `executor.py` · ⚠️ `compute_jit_unpark.py` (L2) là NGOẠI LỆ user duyệt — xem ghi chú ngay dưới bảng | Nới lỏng gate tiền ⇒ đặt lệnh không có tiền; hoặc chặn oan plan tự cấp vốn đủ |

**Chiều thứ BA (thêm 2026-08-19, sau sự cố TRIM giả cùng ngày): Trứng vàng (`egg.totalValue`,
sibling của `stock` trong payload `balances` — xem `kb/data_registry/trading-bot/
dnse_openapi_v2_calling_guideline.md`) KHÔNG nằm trong `totalCash` VÀ KHÔNG nằm trong
`availableCash`.** Nó là vốn CHỦ SỞ HỮU thật (thuộc dòng "SỞ HỮU" ở trên) nhưng cần lệnh rút +
về tài khoản T+1 mới tiêu được (KHÔNG thuộc dòng "TIÊU ĐƯỢC NGAY"). Consumer thuộc dòng "SỞ HỮU"
PHẢI cộng thêm field này (đã làm ở `compute_active_nav.py`/`daily_nav_snapshot.py` từ 08-18,
`compute_park_trim.py` từ 08-19 — sự cố xảy ra vì L1 bị bỏ sót khi 2 file kia đã sửa: tiền
chuyển từ cash sang egg làm pool L1 co lại giả, sinh TRIM oan ~58,7tr cho SpaceX+ZaloPay).
Consumer thuộc dòng "TIÊU ĐƯỢC NGAY" (`check_plan_funding()`, `executor.py`)
**KHÔNG được cộng egg** — đó là nới lỏng gate tiền y hệt lỗi ở dòng trên.

⚠️ **NGOẠI LỆ DUY NHẤT, user duyệt 2026-08-19: `compute_jit_unpark.py` (L2) CÓ cộng egg.**
Bảng trên xếp L2 vào dòng "TIÊU ĐƯỢC NGAY" và cấm cộng egg; commit `956d8ec5` (2026-08-20)
làm NGƯỢC LẠI, và đó là quyết định có chủ đích chứ không phải vi phạm — 2 vòng làm rõ cùng
ngày + quant-skeptic vòng 2, user chốt. Lý do hợp lệ: **L2 là tầng ĐỀ XUẤT, không phải tầng
GATE.** Gate cứng vẫn là `check_plan_funding()` (P0) và nó vẫn KHÔNG cộng egg — nghĩa là
egg không hề nới lỏng cổng tiền, nó chỉ cho phép L2 đề xuất "mua đủ, có rút egg" thay vì
âm thầm SHRINK lệnh xuống phần cash thật. Bù lại, mỗi `buy_amendments[i]` phải mang
`funded_via` ("cash" | "cash+egg") + `egg_relied_vnd` (CẬN TRÊN, không phải số chính xác)
và in cảnh báo rút egg tường minh; egg không rút kịp ⇒ P0 giữ HOLD, đúng thiết kế.
Ranh giới cứng + vì sao KHÔNG chiết khấu phí: docstring `§pool-egg-L2` trong
`mike/bin/compute_jit_unpark.py` — ĐỌC TRƯỚC khi đổi lại chỗ đó.
Bằng chứng chạy thật (2026-08-19, ZaloPay): `cash đầu 39.17tr (availableCash 0.39tr +
Trứng vàng 38.78tr)` kèm đúng dòng cảnh báo "CẦN RÚT Trứng vàng ... TRƯỚC khi đặt lệnh".
(Ghi lại 2026-08-22 tại weekly ops audit: bảng §25 viết 08-19 còn quyết định L2 chốt 08-19→20,
nên hai nguồn mâu thuẫn nhau đúng 3 ngày. Ai đọc bảng mà không đọc dòng này sẽ "sửa" L2 bỏ
egg đi và lặng lẽ revert một quyết định user đã duyệt.)

**Vì sao là luật chứ không phải trùng hợp — HAI bug cùng loại trong HAI ngày liên tiếp:**
`compute_park_trim.py` (mẫu số pool, 2026-08-09, job `Taylor_20260809_150316`, commit `df7d92b4`)
và `compute_active_nav.py` (cơ sở NAV, 2026-08-10, job `Taylor_20260810_004252`). Cả hai đều lấy
`availableCash` vì nó là field đầu tiên `get_cash()` trả về.

**Số neo (đo thật, SpaceX 2026-08-07 — phiên bán 13 mã PARK ≈189,4tr):**
`availableCash` 11:25 = **4.821.143**; 19:10 sau khi bán = **4.821.143** (Y HỆT); `totalCash`
19:10 = **203.656.265**. ⇒ tiền bán **KHÔNG BAO GIỜ** vào `availableCash` trong ngày bán. Trên
active_nav điều đó = **−198.835.122đ, −20,7% NAV**.
Hằng đẳng thức đối soát: `totalCash == availableCash + cashDividendReceiving + depositInterest`
(ZaloPay 08-07: `5.818.854 + 6.453.500 + 318 = 12.272.672`, khớp tuyệt đối).

**Bốn hệ quả bắt buộc khi viết code loại này:**
1. **Fail-closed, KHÔNG rơi về `availableCash`.** Không đọc được `totalCash`/`totalDebt` ⇒ thoát,
   không ghi file. Rơi về = tái lập đúng bug vừa sửa, lặng lẽ.
2. **Tái dùng 3 guard, đừng viết lại**: `park_holdings._stock_block_all_zero` /
   `_cash_fields_all_zero` / `_cash_fields_inconsistent` (bất biến `totalCash ≥ availableCash`).
   Cả ba đều bắt một cách hỏng mà hai cái kia mù — bỏ bất kỳ cái nào là để hở đúng một lối.
3. **Đối soát chéo bằng nguồn có đường đi KHÁC** trước khi tin: `nav_history_<label>.csv`
   (`daily_nav_snapshot.py`) tính NAV theo path hoàn toàn khác — lệch = một trong hai sai.
4. **Cơ sở tỷ trọng ĐƯỢC PHÉP lớn hơn sức mua trong ngày** (tiền chưa settle T+2, cổ tức phải thu,
   `manual_offbook_assets_vnd`). Đó KHÔNG phải lỗi sizing; chặn overshoot là việc của tầng thực thi
   (gate P0 `check_plan_funding` + L2 JIT-unpark), không phải của tầng NAV. Nhưng phải **công bố**
   khoảng cách đó ra output, đừng để người đọc plan tưởng là lỗi.

**Vì sao prose ở data_registry KHÔNG đủ (bài học riêng):**
`kb/data_registry/trading-bot/dnse_openapi_v2_calling_guideline.md` ĐÃ ghi rõ "3 field cash khác
nhau" từ 2026-08-03 — bug vẫn xảy ra hai lần sau đó. Khác biệt: tài liệu kia nói *các field khác
nhau*, bảng trên nói **script NÀO của mình phải dùng field NÀO**. Thêm consumer tiền mới ⇒ thêm
một dòng vào bảng, đó là cách rule này không mốc.

*→ `agents/Taylor/research/active_nav_cash_basis_fix_20260810.md` (bản vá + 26 selfcheck + đối
soát độc lập khớp từng đồng, quant-skeptic CONFIRMED cao vòng 1).*

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
