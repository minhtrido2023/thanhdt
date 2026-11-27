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

## Mục đã tách sang `kb/coding_guidelines_topics/` (đọc theo tình huống)

| Mục | File OKF đích |
|---|---|
| 14. Every Internal Producer→Consumer Pipeline Pair Needs a Real Freshness Check, Not Just a Loose Tolerance | [`coding_guidelines_topics/pipelines-and-bash.md`](coding_guidelines_topics/pipelines-and-bash.md) |
| 15. Bash Strings Doubling as LLM Prompts: Escape `"`/`` ` ``, Then Verify by Running, Not Reading | [`coding_guidelines_topics/pipelines-and-bash.md`](coding_guidelines_topics/pipelines-and-bash.md) |
| 25. "Tiền" KHÔNG Phải Một Con Số — Mỗi Consumer Phải Khai Rõ Đang Hỏi Câu Nào | [`coding_guidelines_topics/money-and-accounting.md`](coding_guidelines_topics/money-and-accounting.md) |
| 29. `cron_health_check.py` Báo Lại Cùng 1 Lỗi Mỗi Ngày Dù Đã Sửa — Ack List + Bidirectional Date, Không Phải Trust-The-Report | [`coding_guidelines_topics/pipelines-and-bash.md`](coding_guidelines_topics/pipelines-and-bash.md) |
| Dọn 2026-10-09 (instructions-dedup) | [`coding_guidelines_topics/instructions-dedup-20261009.md`](coding_guidelines_topics/instructions-dedup-20261009.md) |

## 7. Onboarding a New Account With Legacy/Excluded Holdings

**When an account brought under management already holds positions the bot didn't buy**, use the
general mechanism; more accounts of this shape are expected:

1. **Declare in config, not code**: `"excluded_tickers": [...]` on the account's profile in
   `secrets/trading_bot_accounts.json` (`ACCOUNT_DEFAULTS` in `trading_bot/config.py`).
2. **Enforcement in ONE place**: `trading_bot.plan.filter_excluded_tickers()`, called from
   `bot_execute.py` right after `load_plan()` — applies however the plan was generated
   (DollarBill's LLM JSON or a hand-edited file; `bot_prepare_plan.py`'s template was removed 2026-09-13), so a plan
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

> Đã tách nguyên văn (OKF 2026-11-27) sang [`coding_guidelines_topics/pipelines-and-bash.md`](coding_guidelines_topics/pipelines-and-bash.md).
## 15. Bash Strings Doubling as LLM Prompts: Escape `"`/`` ` ``, Then Verify by Running, Not Reading

> Đã tách nguyên văn (OKF 2026-11-27) sang [`coding_guidelines_topics/pipelines-and-bash.md`](coding_guidelines_topics/pipelines-and-bash.md).
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

> Đã tách nguyên văn (OKF 2026-11-27) sang [`coding_guidelines_topics/money-and-accounting.md`](coding_guidelines_topics/money-and-accounting.md).
## 29. `cron_health_check.py` Báo Lại Cùng 1 Lỗi Mỗi Ngày Dù Đã Sửa — Ack List + Bidirectional Date, Không Phải Trust-The-Report

> Đã tách nguyên văn (OKF 2026-11-27) sang [`coding_guidelines_topics/pipelines-and-bash.md`](coding_guidelines_topics/pipelines-and-bash.md).
## 27. "Lệnh Đã Đặt" ≠ "Lệnh Đã Khớp" — Đối Soát Fill Thật Trước Khi Báo "Đã Đạt Target", Theo `~/.claude/skills/dnse-fill-reconciliation/`

Trước khi khẳng định 1 lệnh/plan "đã thực thi", "đã mua đủ", "đã đạt X% NAV" — đọc
`~/.claude/skills/dnse-fill-reconciliation/SKILL.md`. Đọc số lượng trong `orders[]` của plan rồi
nhân giá để suy ra tỷ trọng là **suy luận trên Ý ĐỊNH, không phải KẾT QUẢ** — với mã thanh khoản
mỏng (UPCOM, ADV vài tỷ/ngày trở xuống), khoảng cách giữa 2 số có thể là toàn bộ lệnh.

**Case thật (2026-08-11)**: Mike báo "TV1 đã đạt ~5% NAV cả 2 account" theo số lượng ĐẶT trong plan
đã duyệt. Đối soát bằng email "Báo cáo giao dịch khớp lệnh" DNSE tự gửi (~16:30 ICT, broker-issued,
độc lập hoàn toàn với `dnse_raw_*.jsonl`) lộ ra: DRI khớp đủ đúng kế hoạch cả 2 account, nhưng TV1
chỉ khớp **100/2.000cp (SpaceX)** và **0/1.300cp (ZaloPay)** — do ADV quá mỏng (~0,6 tỷ/ngày) không
hấp thụ hết lô trong 1 phiên. Không phải bug (giá/trần đều đúng) — thị trường không đủ đối ứng.

**Công cụ**: `fetch_dnse_khoplenh_email.py` (root WorkingClaude, dùng chung Gmail OAuth readonly có
sẵn cho auto-OTP) tải + parse email này thành CSV khớp lệnh sạch theo từng account/mã. Nguồn ghi ở
`kb/data_registry/trading-bot/dnse_khoplenh_broker_email.md`. Email chỉ có sau ~16:30 ICT — báo cáo
trong-phiên/cùng ngày trước giờ đó vẫn phải đọc `positions` mới nhất trong `dnse_raw_<date>.jsonl`
(không đợi được email).

**KHÔNG thay thế pipeline §6 đã chốt** (`verify_account_snapshot.py`/`daily_nav_snapshot.py`/
`reconcile_equity.py` vẫn CANONICAL cho cost-basis) — đây là lớp đối soát ĐỘC LẬP thêm vào, giá trị
chính là nó đi qua đường dữ liệu khác (backend DNSE tự phát hành, không phải API client của mình)
nên bắt được lỗi ở CẢ HAI phía. Fold vào pipeline sinh report tự động là thay đổi lớn hơn — qua
Taylor + quant-skeptic review trước khi coi là đã wire.

## 31. Bảng "Hiệu suất lũy kế" Báo Cáo SpaceX: BẮT BUỘC Qua `nav_period_returns.py`, KHÔNG Tự Tính Từ `nav_history` Raw

**Quy tắc:** khi soạn dòng WTD/MTD/"Từ khi bắt đầu hoạt động" trong bảng "Hiệu suất lũy kế" (mục
3.2) của báo cáo SpaceX weekly/monthly, PHẢI chạy:

```bash
python3 mike/bin/nav_period_returns.py --account SpaceX --report-date <YYYY-MM-DD>
```

và lấy `return_pct` của từng key (`inception`/`wtd`/`mtd`) trong JSON output làm số đưa vào bảng —
**KHÔNG** tự viết `(nav_cuối/nav_đầu − 1) × 100` trực tiếp từ `nav_history_SpaceX.csv`.

**Vì sao (đã cắn thật, 2026-09-19):** dòng đầu tiên của `nav_history_SpaceX.csv` (07-02) là snapshot
SAU phiên giao dịch đầu tiên, không phải vốn khởi điểm thật (1.000.000.000đ nạp ngày 01/07 —
account clean-slate). Báo cáo tuần 09-14→09-18 dùng thẳng dòng đầu làm baseline, ra "Từ khi bắt đầu
hoạt động = −1,66%" trong khi số đúng là **−2,177%** (lệch 0,517pp). `nav_period_returns.py` đọc
`data/account_inception.json` để lấy đúng mốc: SpaceX `starting_capital=1.000.000.000` (dùng THAY
`nav_history` dòng đầu); ZaloPay `starting_capital=null` (dùng ĐÚNG dòng đầu `nav_history`, vì
account có vị thế legacy trước go-live, không có mốc "vốn nạp ngày 1" sạch — KHÔNG áp cùng công
thức 2 account như nhau).

**Cưỡng chế cơ học một phần:** `mike/bin/report_delivery_gate.py::_check_period_returns()` BLOCK
việc giao báo cáo SpaceX investor-facing (không áp ZaloPay — kênh nội bộ) nếu dòng "Từ khi bắt đầu
hoạt động" lệch canonical ≥ 0,05pp — nhưng đây là lưới AN TOÀN ở cuối pipeline (chỉ chạy khi *gửi*,
và fail-open nếu không parse được bảng/thiếu data), không thay được việc dùng đúng nguồn NGAY LÚC
SOẠN. Cùng tinh thần §6 (verify artifact, không tự ước lượng) và §9 (tra nguồn chuẩn trước khi wire).

*→ commit `mike` 8bbb302c (`nav_period_returns.py`), `20eafe6b` (`report_delivery_gate.py` gate),
`e4c5ec97` (`report_charts.py` — `--starting-nav` opt-in cho chart cum-return dùng cùng baseline
khi cần chart "since inception", KHÔNG auto-áp cho chart weekly/monthly theo kỳ vì sẽ làm 2 đường
NAV/VNINDEX lệch mốc index=100).*


**Từ khi có VN-Index có cổ tức (2026-10, quỹ bước 4):** bảng 3.2 weekly/monthly của CẢ SpaceX và ZaloPay KHÔNG tự
gõ nữa — dán nguyên đầu ra:

```bash
python3 mike/bin/period_table_32.py --account SpaceX  --report-date <YYYY-MM-DD>
python3 mike/bin/period_table_32.py --account ZaloPay --report-date <YYYY-MM-DD> --with-sleeve
```

6 cột `Giai đoạn | <TK> | VN-Index (giá) | VN-Index có cổ tức | Chênh so giá | Chênh so có cổ tức` + chú thích cố định
("sau thuế TNCN 5% trên cổ tức" theo cờ Q2). Mốc VN-Index = ngày dòng sổ đơn vị làm mốc kỳ (ZaloPay 06/07, không phải
03/07 — Q1). `report_delivery_gate._check_benchmark_table` chặn: ô lệch CLI > 0,005 điểm %, cột có cổ tức `chưa có số`
(Q9), bỏ cột, thiếu chú thích, dòng có số mà CLI không có kỳ đó. Dòng "Phần bot quản lý" `chưa có số` thì vẫn gửi.
Báo cáo tháng so SpaceX ↔ ZaloPay: dùng chuỗi b (`--sleeve bot`) và SpaceX CÙNG cửa sổ từ 06/07.


## Dọn 2026-10-09 (instructions-dedup)

> Đã tách nguyên văn (OKF 2026-11-27) sang [`coding_guidelines_topics/instructions-dedup-20261009.md`](coding_guidelines_topics/instructions-dedup-20261009.md).
## 32. Job Nền Song Song PHẢI Có Trần RAM — Container 40GB, KHÔNG Swap

**Sự cố 2026-10-20**: container treo ~2,5h rồi reboot 22:23 ICT; nghi cạn RAM (chưa xác nhận kernel
— không đọc được `kern.log`). Đo thật: engine `pt_v23_audit_2014.py` đỉnh **3,2GB/tiến trình**
(1,3GB lúc đầu, vọt ở ~30 giây cuối), 8 song song ≈ 26GB + nền 6-7GB trên trần 40GB, không swap.
Ghi chú sự cố: `kb/incidents/2026-10/2026-10-20-container-freeze-memory-suspected.md`.

**Luật** (mọi agent mở tiến trình nặng nền, đặc biệt Taylor):
1. Trước khi mở N tiến trình song song: `N ≤ $(bin/mem_slots.sh <GB_đỉnh_mỗi_tiến_trình>)`; chưa biết đỉnh
   thì đo 1 tiến trình (`VmHWM` trong `/proc/<pid>/status` tới hết đời) rồi mới nhân lên. Engine
   `pt_v23_audit_2014.py`: dùng **3,5GB**, KHÔNG dùng số lúc khởi động.
2. Bọc từng tiến trình nặng: `bin/memcap.sh <GB> <lệnh>` (vượt trần chỉ giết RIÊNG nó, exit 137).
3. Cơ chế nền (không cần agent nhớ): `dispatch.sh --bg` bọc mỗi job trong scope `MemoryMax=18G` (đổi:
   `DISPATCH_JOB_MEM_MAX_GB`, `0` = tắt) nằm trong `mike-jobs.slice` tổng 28G (cài bằng
   `bin/install_mike_jobs_slice.sh`). Mọi tiến trình con của job (kể cả `nohup`/`&`) nằm trong scope.
   Engine bị giết = job phải CHẠY LẠI với ít song song hơn, không phải tăng trần.
4. Đường `dispatch.sh` ĐỒNG BỘ (không `--bg`) và phiên tương tác KHÔNG được bọc — vẫn phải theo (1)-(2).

