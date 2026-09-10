# LAG edge-health **exit-keyed** A/B — the look-ahead is real but **directionless**

**Job** `Taylor_20260910_142406` · Taylor (quant) · 2026-09-10 · user approved 21:23 ICT (topic 1547589883999158363)
**Ask (one question):** of the published **+0.60pp** for the edge-conditional allocator, how much
survives when `mean12` is keyed on the **exit** date (when a return becomes knowable) instead of the
**entry** date?

**Answer: all of it — and the defect is worth −0.02pp, which is indistinguishable from zero.**
But the audit turned up a **second, larger discrepancy that this job did not create and cannot
close**: in the current R3 pin the edge gate is worth **+0.29pp**, not +0.60pp. See §5.

Read this file alone; everything it cites is in this directory or named by absolute path.

---

## 1. Bottom line

| Question asked | Answer |
|---|---|
| **(a) How many pp survive?** | **All of them.** Removing the look-ahead *raises* CAGR by **+0.021pp** (28.86% → 28.88%). Measured against the gate-off baseline, the edge premium goes **+0.288pp → +0.309pp**, i.e. **107% survives**. |
| **(b) Distinguishable from harness noise?** | **No.** \|Δ\| = 0.021pp sits ~19× inside the ±0.40pp band a *content-free* placebo moved this same harness (job `Taylor_20260910_131906` §5). Across the N=15 gate-disagreement runs the sign split is **7+/8−, sign-test p = 0.93**. This number must be quoted as **"not distinguishable from 0"**, never as a point estimate. |
| **(c) Does +0.60pp need correcting?** | **Not for this defect** — the look-ahead removes nothing. **But the number does not reproduce in the current pin** for an unrelated reason, and I could find **no pinned source run for it anywhere in `data/results_registry.md`**. Proposed wording in §5. **I did not edit the registry.** |

**Nothing was wired.** `git status` clean on `pt_v23_audit_2014.py`, `pt_v22_dt5g.py`,
`edge_health_monitor.py`, `simulate_holistic_nav.py`. `data/lag_edge_health.csv` — a production
contract — was **never touched** (md5 `f30a5beadde2bc5e117eca47021aabef`, mtime 15:38, before this job).
**The live gate is not affected by this defect and no change to it is proposed.**

---

## 2. Harness validity — two hard gates, both passed before any delta was read

| leg | CAGR | Sharpe | MaxDD | Calmar | Final NAV | self-check | CSV md5 |
|---|---|---|---|---|---|---|---|
| `ekctrl` — pin R3, production engine | 28.86% | 1.90 | −17.79% | 1.62 | 1,178.01B | **0 VND** both books | **`7d053e6201c9d107685ff4d1dd9d2d2a`** ✅ = pinned md5 |
| `ekinert` — research copy, switch OFF | 28.86% | 1.90 | −17.79% | 1.62 | 1,178.01B | 0 VND | **`7d053e62…`** — byte-identical to ctrl ✅ |
| **`ekexit`** — gate on exit axis | **28.88%** | 1.90 | **−17.70%** | **1.63** | **1,180.40B** | 0 VND | `c24f39071a400cff5d956a2fc5288af9` |
| `eknoedge` — allocator, gate OFF | 28.58% | 1.87 | −18.56% | 1.54 | 1,145.66B | 0 VND | (denominator leg, §4) |

Metrics above are the **independent recompute** from each leg's `DAILY.combined_nav` column
(`analyze_legs.py` → `analyze_out.txt`), not the harness self-report; they agree with the harness
`METRIC` rows to the printed precision.

Environment verbatim from job `Taylor_20260910_131906`: `BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate`,
`BQ_CACHE_THREADS=1`, `NAV_TOTAL_B=50`, `ETF_LIQ=custompitg`, `BASKET_WT=namecap`,
`BASKET_SELECT=yieldcombo`, `PARK_STATES=3:0.7`, `AUDIT_END=2026-06-19`, `$DNA_PYEXE`,
`v23a none postbull 0 edge`, `EXP_TAG` on every leg (`run_leg.sh`).

**The engine copy is provably inert** — `pt_v23_exitkey.py` differs from `pt_v23_audit_2014.py` by
**one hunk, 15 lines**, all inside `if USE_EDGE_ALLOC:`, gated on `EDGE_HEALTH_EXITKEY`. With the
env var unset it produces a byte-identical CSV. Every delta below is the keying and nothing else.

---

## 3. What was actually changed, and why it is only one thing

`build_exitkey_series.py` → `lag_edge_health_exitkey.csv`.

The `(entry, ret)` pairs are copied **verbatim** from `data/lag_edge_health.csv` — 5,431 rows, no
cohort rebuild. Only the **date axis of the trailing-12M window** changes: for each entry date the
exit date is `entry + 25 sessions` on the *same* price calendar the producer uses
(`earnings_px.pkl` pivot index; `edge_health_monitor.py:160-165`). Measured exit lag: **32–45
calendar days, median 35** — the ~5 weeks predicted.

Rebuilding the cohort would have re-run a daily-refreshed cache and put cohort drift on top of the
effect being sized. This way treatment and control share identical events and identical returns.

**Self-check (in `build_exitkey_series.py`):** recomputing the *entry*-keyed window on this frame
reproduces the production `mean12` column to `1.0e-13`. So the window arithmetic is faithful and
any delta is the keying, not the arithmetic.

**How much does the gate actually change?** On the allocator's axis (3,109 sessions, 2014-01-01 →
2026-06-19): entry-keyed reads `≥4%` on **47.3%** of sessions, exit-keyed on **51.3%**. They
**disagree on 367 sessions (11.8%)**; after the allocator's own state filter (the gate only bites in
states 3/4/5) `w_lag_tgt` actually differs on **300 of 3,107 sessions (9.7%)**, in **15 contiguous
runs**. Mean \|Δmean12\| = 0.78pp, max 5.91pp.

**N = 15 runs**, per PREREG — not 300 sessions, not 3,107 rows.

---

## 4. Result — real per-episode, zero in aggregate

```
TREATMENT DELTA (exitkey − ctrl):  CAGR +0.021pp   Sharpe +0.001
                                   MaxDD +0.086pp (−17.79% → −17.70%, i.e. slightly BETTER)
                                   Calmar +0.009   Final NAV +2.39B on 1,178B
```

The interesting part is the decomposition (`decomp_runs.py` → `decomp_out.txt`). A net of zero can
mean "small everywhere" or "large but cancelling". **It is the second:**

| | log-% of NAV |
|---|---|
| **gross** movement across the 15 runs (Σ\|run\|) | **7.234** |
| largest single run (2015-08-10 → 11-23) | 1.171 |
| second/third largest (2017-05-26, 2025-05-12) | −0.956 / −0.955 |
| **net** across the 15 runs | +0.808 |
| residual outside every run (pure path divergence) | −0.605 |
| **TOTAL 2014-2026** | **+0.203** → **+0.016pp CAGR** over 12.46y |

Sign split **7 positive / 8 negative**, informal two-sided sign test **p = 0.93**.

**So the look-ahead is not harmless per episode — it moves NAV by up to ±1.2% in a given window.
It is harmless in aggregate because it is directionless.** Reading `mean12` five weeks early is a
coin flip about whether the gate is on or off, not a systematic peek at good news. That is the
mechanism: `mean12` is a *trailing 12-month mean over ~600 events*; shifting its index by 25
sessions changes which side of a fixed 4% threshold it lands on near crossings, but carries no
information about the *forward* return of the LAG book.

Per-year (`analyze_out.txt`): the whole thing lives in 2015 (+0.0099 log) against 2025 (−0.0069)
and 2019 (−0.0043); 2014, 2016 and 2022 are exactly 0.000.

---

## 5. The number that does **not** reproduce — and it is not this defect

Measured against the same allocator with the gate switched off (`eknoedge`, argv5 ≠ `edge`), in the
**current R3 pin**:

| gate series | CAGR | edge premium vs gate-off (28.58%) |
|---|---|---|
| entry-keyed (as published, has the look-ahead) | 28.86% | **+0.288pp** |
| exit-keyed (causal) | 28.88% | **+0.309pp** |

**The gate is worth ~+0.29pp here, not +0.60pp — and the look-ahead accounts for none of the gap
(it moves the premium the *wrong* way, +0.02pp).** The gap must come from something else: the
+0.60pp is dated **2026-06-13** (`pt_v23_audit_2014.py:172`), i.e. **before** the `universe_pit`
repin of 2026-08-03 and this `bq_cache_asof20260729_postrestate` snapshot, and probably at a
different `NAV_TOTAL_B` / `ETF_LIQ` / `BASKET_*` configuration.

**I could not locate a pinned source run for +0.60pp.** `grep` over `data/results_registry.md`,
`kb/KNOWLEDGE.md` and `kb/events_buffer.md` returns the string `+0,60pp` **only** in today's own
entries referring to this same claim — there is no `## 2026-06-13` section, and no CSV/md5 behind
it. Tracing it is outside this job's scope and I did not attempt it.

### Proposed registry wording — **for Mike to apply; I did not edit the registry**

> Cổng edge-conditional (`w_LAG` 0,65 khi `mean12 ≥ 4%`, ngược lại 0,50) đo lại trên **pin R3
> hiện hành** (`bq_cache_asof20260729_postrestate`, `universe_pit`, NAV 50B, `AUDIT_END=2026-06-19`)
> đáng **+0,29pp CAGR** so với chính allocator đó với cổng TẮT (28,86% vs 28,58%), kèm Calmar
> 1,62 vs 1,54 và MaxDD −17,79% vs −18,56%. Con số **+0,60pp** công bố 2026-06-13 thuộc một môi
> trường KHÁC (trước repin `universe_pit` 08-03) và **không có run nguồn nào được pin trong
> registry** — trích dẫn nó phải kèm môi trường, hoặc thay bằng +0,29pp của pin R3.
>
> Lỗi khoá-theo-ngày-VÀO của `data/lag_edge_health.csv` (job `Taylor_20260910_142406`) **KHÔNG**
> giải thích chênh lệch này: dựng lại khoá theo ngày RA cho **+0,02pp** (28,86% → 28,88%,
> premium +0,288 → +0,309pp), tức **~107% phần đã công bố còn sống**, và |Δ| nằm sâu trong dải
> nhiễu ±0,40pp của placebo cùng harness ⇒ **không phân biệt được với 0**. Lỗi có thật và làm
> lệch NAV tới ±1,2% trong từng cửa sổ riêng lẻ (15 run, 7+/8−, sign-test p=0,93) nhưng **vô
> hướng**, nên triệt tiêu trên 12 năm. **LIVE chưa bao giờ bị ảnh hưởng.**

---

## 6. Scope discipline

- **One treatment leg**, as briefed. `eknoedge` is a **denominator**, not a variant — without it
  "how many pp survive" has no unit. No threshold grid was run; `EDGE_THR=4.0` never moved. Zero
  free parameters.
- **Noticed, deliberately NOT pursued** (per the PREREG stopping rule, written down instead of run):
  1. Exit-keyed tilts *more* often (51.3% vs 47.3% of sessions) and gives a slightly better MaxDD
     (−17.70% vs −17.79%) and Calmar (1.63 vs 1.62). Tempting to read as "the causal series is
     mildly better." **It is not evidence** — 7+/8− at p=0.93.
  2. `edge_health_monitor.py` could be made to emit an exit-keyed column alongside `mean12` so
     future backtests are causal by construction. That is a production change with no measured
     benefit (this job is the measurement, and it found none), so it is **not** proposed.
  3. Where +0.60pp came from (§5) — a registry-archaeology task, not a quant task.
- **DSR/PBO not run** — required only when recommending a config for wire (`quant-research` §13).
  Nothing is recommended. `N_trials = 1` (one treatment leg), declared in PREREG.
- **quant-skeptic**: not required for a keep-the-status-quo measurement, but §5's +0.29pp **will**
  be quotable as a reason to value or de-value the gate. If anyone uses it to justify a change,
  send it to quant-skeptic first.

## 7. Caveats that would change how you read this

- The A/B holds the *cohort* fixed and varies only the *keying*. It therefore sizes the
  look-ahead **and nothing else** — it is not a re-validation of the gate itself.
- Both legs read `mean12` on day `d` from a value stamped at the close of day `d`'s reference
  event. That intraday convention is identical in both legs (production's own), deliberately left
  alone so the comparison is like-for-like; it is a separate, smaller question.
- `lag_edge_health.csv`'s last row is `entry=2026-07-29` (exit 2026-09-02), past `AUDIT_END=2026-06-19`,
  so the tail plays no part in either leg.

## 8. Files

`PREREG.md` (written before any leg ran) · `build_exitkey_series.py` → `lag_edge_health_exitkey.csv` ·
`pt_v23_exitkey.py` (research engine copy, 1 hunk) · `run_leg.sh` / `run_leg_noedge.sh` ·
logs `ekctrl.log` `ekinert.log` `ekexit.log` `eknoedge.log` · `analyze_legs.py` → `analyze_out.txt` ·
`decomp_runs.py` → `decomp_out.txt`.
Audit CSVs `data/v23_golive_audit_2014_now_..._exp_ek{ctrl,inert,exit,noedge}_univpit.csv`.
Canonical `..._wtnamecap.csv` untouched.
