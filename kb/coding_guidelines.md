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

## Mục đã tách sang `kb/coding_guidelines_ext.md` — đọc khi cần, KHÔNG auto-load

Các mục dưới đây là **luật đầy đủ, còn hiệu lực y nguyên** (không nén, không sửa chữ, giữ nguyên
số hiệu §) — chỉ chuyển sang file anh em `mike/kb/coding_guidelines_ext.md` vì chúng dùng theo
TÌNH HUỐNG, không phải mỗi phiên. Gặp đúng tình huống thì `Read` file đó.

| Mục | Khi nào phải đọc |
|---|---|
| **§7** Onboarding account mới có vị thế legacy/excluded | Đưa account mới vào quản lý; sửa `excluded_tickers`/`compute_active_nav.py` |
| **§8b** Retention snapshot `data/bq_cache_asof*` | Định XOÁ một snapshot BQ cũ (~2,0GB, KHÔNG tái tạo được) |
| **§10** File thành canonical → archive biến thể bị thay thế cùng lượt | Chốt 1 script/file là canonical cho một mục đích |
| **§11** Tra `kb/cron_registry.md` trước khi thêm/đổi lịch cron | Thêm/xoá/đổi giờ bất kỳ dòng crontab nào |
| **§13** Sửa file `kb/` cần Mike duyệt → ghi ra `<file>.proposed` | Sửa file trong `kb/` mà chưa được duyệt live |
| **§14** Cặp producer→consumer phải có freshness-check thật | Viết/sửa script đọc output của script khác chạy cron riêng |
| **§15** Chuỗi bash kiêm prompt LLM: escape `"`/`` ` `` | Viết prompt dài trong `.sh` (đã có gate cơ học `bin/shellcheck_gate.sh`); dispatch **tương tác** (Bash tool, không qua commit) → gate không phủ tới, dùng skill `~/.claude/skills/dispatch-prompt-heredoc/` |
| **§17** Reader báo "còn mở" phải quét mọi tầng retention | Viết/sửa reader trạng thái bus (`mike_json.py`, checker inbox) |
| **§18b** `srcwalk` để ĐỌC, `grep` để TÌM — số đo benchmark | Cần lại số benchmark; **luật hành động đã có sẵn ở `WorkingClaude/CLAUDE.md` § Code navigation (auto-load mỗi phiên)** |
| **§22** Luật văn xuôi LLM áp sai → chuyển thành code | Thấy 2 phiên áp cùng luật ra 2 kết quả khác nhau |
| **§24** Trần giá/hạn mức của plan phải là FIELD RIÊNG cưỡng chế bằng code | Đụng giá đặt lệnh/trần đuổi giá/`PlannedOrder`, thêm field vào plan JSON |

⚠️ **Con trỏ này CỐ Ý không dùng cú pháp `@`.** `@`-import của Claude Code là **đệ quy** — viết
`@.../coding_guidelines_ext.md` ở đây sẽ nạp lại toàn bộ file ext vào mọi phiên của cả 5 agent
import file này, xoá sạch tác dụng tách. Ai "sửa" dòng này thành `@` là tái lập đúng vấn đề vượt
ngưỡng 40KB.

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
5. **Gửi email — BẮT BUỘC cho MỌI cadence (daily/weekly/monthly), không chỉ weekly/monthly**
   (mở rộng 2026-08-11, user yêu cầu sau vụ NAV ZaloPay/park-trim — email là cách user tự đối
   soát để phát hiện + báo lỗi kịp thời, không chỉ dựa vào Discord đã có sẵn): sau khi post
   Discord xong, chạy `python3 mike/bin/send_report_email.py <report.md>` cho ĐÚNG file vừa gửi.
   Script tự fail-closed nếu cổng tỉ suất §21 chưa PASS hoặc thiếu credential — đừng `--skip-
   return-gate` trừ khi đã hiểu rõ vì sao gate lệch. Backstop nếu agent quên bước này:
   `check_report_cadence.sh` quét lại MỌI report `*_daily_report_*.md` /
   `*_weekly_report_*.md` / `*_monthly_report_*.md` chưa có proof và gọi delivery gate gửi bù
   — nhưng đó là lưới AN TOÀN, không thay được việc gửi ngay lúc soạn xong report.
6. **Delivery closure — file được tạo KHÔNG có nghĩa là báo cáo đã gửi.** Mọi báo cáo tự động
   phải kết thúc bằng `python3 mike/bin/report_delivery_gate.py <report.md> --topic
   trading_report`. Chỉ `COMPLETE` (artifact qua gate + Discord + email đều có bằng chứng
   hash-bound) mới được đóng job/bus question. `maxturns_pending`, `usage_limited`, file tồn
   tại, hay chỉ một kênh thành công đều là **INCOMPLETE** và phải rescue/retry; retry không gửi
   lại kênh đã có bằng chứng. Quy trình bắt buộc: skill `report-delivery-closure`.

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

*→ rationale §8 (+ §8b).* · **§8b** (retention snapshot `data/bq_cache_asof*`) → `kb/coding_guidelines_ext.md`.

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

## 16. Never Trust the Host's System Timezone for Date/Time Comparisons — Anchor Explicitly

**Rule:** anchor timezone explicitly, never assume the calling process has the right `TZ`:
- Python: `datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))`, not bare `datetime.now()`.
- Bash: `TZ='Asia/Ho_Chi_Minh' date ...` (ref pattern: `bin/csv_fresh_today.sh`).
- Selfchecks for date/freshness logic: run under `env -u TZ` (+ a foreign TZ) — the exact test that
  caught this bug; a selfcheck inheriting the author's own correct `TZ` passes regardless.

Shipped alongside: a `TZ=Asia/Ho_Chi_Minh` crontab export (closes the ambient-env gap).

*→ rationale §16.*

## 18. Any Quant R&D Task (Backtest, IC Test, Gate/Selector Change) — Follow `.claude/skills/quant-research/`

Before designing/running a backtest, factor-IC test, or production-rule review, read the
`quant-research` skill (`/home/trido/thanhdt/WorkingClaude/.claude/skills/quant-research/SKILL.md` —
Skill tool or direct read in headless dispatch); it holds the fixed order of operations. The 5 steps
most often skipped: declare **N as independent events, not row count** (and match the statistical
tool to N); `self-check 0 VND` with a control leg reproducing the pinned number; point-in-time joins
only; DSR/PBO plus the quant-skeptic gate before recommending a wire; verify the artifact, not the
self-report, before relaying a conclusion.

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

## 25. "Tiền" KHÔNG Phải Một Con Số — Mỗi Consumer Phải Khai Rõ Đang Hỏi Câu Nào

**Luật:** bất kỳ code nào đọc số dư tiền từ broker PHẢI khai (trong tên biến hoặc comment ngay tại
chỗ đọc) nó đang hỏi câu nào trong hai câu dưới, và lấy đúng field của câu đó. Không có "field tiền
mặc định"; `DNSEBroker.get_cash()` **không** phải mặc định an toàn.

| Câu hỏi | Field ĐÚNG | Dùng ở | Sai thì hỏng kiểu gì |
|---|---|---|---|
| "Tôi **SỞ HỮU** bao nhiêu vốn?" (cơ sở NAV / mẫu số tính tỷ trọng mục tiêu) | **`totalCash − totalDebt`** | `daily_nav_snapshot.py:449`, `reconcile_equity.py`, `compute_park_trim.py` (mẫu số pool), `compute_active_nav.py` (§cash) | Khai THIẾU NAV đúng bằng tiền bán chưa settle ⇒ under-deploy, hoặc pool co lại đúng bằng lượng vừa bán ⇒ **vòng lặp tự kích bán tiếp** |
| "Tôi **TIÊU ĐƯỢC NGAY** bao nhiêu?" (sức mua đặt lệnh phiên này) | **`ppse.pp0Buy`/`qmaxBuy`**, hoặc `availableCash` khi không gọi được ppse | `DNSEBroker.get_cash()`, `check_plan_funding()`, `executor.py`, `compute_jit_unpark.py` (L2) | Nới lỏng gate tiền ⇒ đặt lệnh không có tiền; hoặc chặn oan plan tự cấp vốn đủ |

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

## 26. Đóng Câu Hỏi Trên Bus NGAY Khi Xử Lý Xong — Theo `~/.claude/skills/close-the-loop/`

Khi hành động của bạn giải quyết một `question` trên bus (fix xong, quyết định xong, điều tra ra
kết luận) — post event đóng (`answer`/`decision`/`finding` phù hợp) **NGAY**, đúng topic string,
kèm bằng chứng artifact (commit hash, giá trị config đọc lại, output selfcheck thật) — không đợi
cuối phiên. Đọc `~/.claude/skills/close-the-loop/SKILL.md` trước khi sửa/vận hành bất kỳ
checker/pipeline escalation nào (autofix, health-check, weekly audit). 2 lỗi khác nhau cho cùng
1 triệu chứng "báo động treo nhiều ngày dù việc đã xong": (A) người xử lý quên đóng — kỷ luật, có
backstop là auto-close-bằng-artifact trước khi escalate; (B) chính pipeline verify tra topic
SAI cách (match tuyệt đối trong khi producer luôn thêm hậu tố tự do vào topic) → "không tìm
thấy" bị lẫn vào cùng nhánh code với "tìm thấy và cần sửa", sinh `NEEDS_CHANGES` giả mỗi ngày.
Case thật + cách phân biệt A/B/review-thật: xem skill. Bug B cụ thể đã xác định trong
`bin/wags_autofix.sh` (`has-event ... "finding:wags-fix: $LABEL"` khớp tuyệt đối, trong khi Wags
luôn ghi topic có hậu tố tự do) — **ĐÃ VÁ 2026-08-11**: `mike_json.py has-event-prefix` (subcommand
mới, `has-event` giữ nguyên semantics tuyệt đối cho 3 caller cũ) + tách `INCONCLUSIVE` khỏi
`NEEDS_CHANGES` thành 2 question khác nhau + `bin/wags_bus_verdict.py` lấy verdict từ artifact bus
thay vì stdout. Luật cho người viết checker: `kb/ops_runbook.md` § "Checker TRA CỨU sai".

## 27. "Lệnh Đã Đặt" ≠ "Lệnh Đã Khớp" — Đối Soát Fill Thật Trước Khi Báo "Đã Đạt Target", Theo `~/.claude/skills/dnse-fill-reconciliation/`

Trước khi khẳng định 1 lệnh/plan "đã thực thi", "đã mua đủ", "đã đạt X% NAV" — đọc
`~/.claude/skills/dnse-fill-reconciliation/SKILL.md`. Đọc số lượng trong `orders[]` của plan rồi
nhân giá để suy ra tỷ trọng là **suy luận trên Ý ĐỊNH, không phải KẾT QUẢ** — với mã thanh khoản
mỏng (UPCOM, ADV vài tỷ/ngày trở xuống), khoảng cách giữa 2 số có thể là toàn bộ lệnh.

**Case thật (2026-08-11)**: Mike báo "TV1 đã đạt ~5% NAV cả 2 account" dựa trên số lượng ĐẶT trong
plan đã duyệt. Đối soát bằng email "Báo cáo giao dịch khớp lệnh" DNSE tự gửi (~16:30 ICT, broker-
issued, độc lập hoàn toàn với `dnse_raw_*.jsonl`) lộ ra: DRI khớp đủ đúng kế hoạch cả 2 account,
nhưng TV1 chỉ khớp **100/2.000cp (SpaceX)** và **0/1.300cp (ZaloPay)** — do ADV quá mỏng
(~0,6 tỷ/ngày) không hấp thụ hết lô trong 1 phiên. Không phải bug (giá/trần đều đúng) — thị trường
đơn giản không đủ đối ứng.

**Công cụ**: `fetch_dnse_khoplenh_email.py` (root WorkingClaude, dùng chung Gmail OAuth readonly
có sẵn cho auto-OTP) tải + parse email này thành CSV khớp lệnh sạch theo từng account/mã. Nguồn
ghi ở `kb/data_registry/trading-bot/dnse_khoplenh_broker_email.md`. Email chỉ có sau ~16:30 ICT —
báo cáo trong-phiên/cùng ngày trước giờ đó vẫn phải đọc `positions` mới nhất trong
`dnse_raw_<date>.jsonl` (không đợi được email).

**KHÔNG thay thế pipeline §6 đã chốt** (`verify_account_snapshot.py`/`daily_nav_snapshot.py`/
`reconcile_equity.py` vẫn CANONICAL cho cost-basis) — đây là lớp đối soát ĐỘC LẬP thêm vào, giá trị
chính là nó đi qua đường dữ liệu khác (backend DNSE tự phát hành, không phải API client của mình)
nên bắt được lỗi ở CẢ HAI phía. Fold vào pipeline sinh report tự động là thay đổi lớn hơn — qua
Taylor + quant-skeptic review trước khi coi là đã wire, như mọi thay đổi khác chạm pipeline §6.

## 28. Checker So Sánh 2 Nguồn — Chuẩn Hoá GIÁ TRỊ Trước Khi So, Không So Chuỗi Mô Tả Hay Suy Từ Sự Vắng Mặt

**Quy tắc:** khi 1 checker/script verify so sánh 2 nguồn để phát hiện lệch (dữ liệu thật vs kỳ
vọng, trạng thái A vs B, "quyết định này đã có chưa") — luôn quy CẢ HAI về **giá trị đã chuẩn hoá**
(số, enum, timestamp) trước khi so. Ba dạng SAI cụ thể, đều đã xảy ra thật:
- **So chuỗi mô tả tự do** thay vì giá trị bên dưới — 2 câu nói cùng 1 việc nhưng khác chữ ⇒ báo
  lệch giả.
- **So kênh HÀNH ĐỘNG** (tham số shell, dòng lệnh, log thô) khi chưa parse ra giá trị thật.
- **Suy diễn từ SỰ VẮNG MẶT của 1 kênh** ("không thấy `answer` trên bus" ⇒ "quyết định chưa có")
  — trong khi quyết định đã được thực thi qua đường khác (code/config đã đổi thật) mà chỉ thiếu
  bước ghi lại lên đúng kênh checker đang nhìn. Vắng mặt trên 1 kênh không phải bằng chứng của sự
  vắng mặt trong thực tế — phải xác nhận bằng ARTIFACT (giống nguyên tắc §6/§9/§14), không suy diễn.

**Vì sao thành luật:** tái diễn 4 ngày liên tiếp (2026-08-10→08-13) dưới ≥6 hình dạng khác nhau,
đều cùng gốc — vá từng call-site cụ thể (đã làm, có test, có commit) chặn đúng ca đó nhưng không
chặn được ca tiếp theo ở call-site KHÁC vì không có quy tắc chung. Ghi vào đây để mọi checker MỚI
tự tránh, không lặp lại nhóm lỗi này ở vị trí thứ 7.

*→ retro-2026-08-10 Pattern 1 · retro-2026-08-11 mục 1/4/5 · retro-2026-08-12 Pattern 2 ·
retro-2026-08-13 Pattern 1 — chi tiết từng ca cụ thể nằm trong các file retro tương ứng
(`kb/incidents/retro/`), không chép lại ở đây.
