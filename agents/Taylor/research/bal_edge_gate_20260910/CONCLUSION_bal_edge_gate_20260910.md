# BAL edge-gate (AMH #1) — **NO-GO**

**Job** `Taylor_20260910_131906` · Taylor (quant) · 2026-09-10 · deadline 2026-09-16 (VPI/BAL review)
**Ask:** build an edge-gate for book BAL, symmetric to the `w_LAG` edge-gate already live.
**Answer:** the symmetric gate is **structurally impossible**, and the closest workable substitute
is **refuted by its own placebo**. Recommend **no production change**. Nothing was wired.

Read this file alone; everything it cites is in this directory or named by absolute path.

---

## 1. Bottom line

| Question | Answer |
|---|---|
| Can BAL have a LAG-style realized-edge gate? | **No.** BAL is a BULL-only book with N=10 signal episodes and gaps up to 25 months. Read causally, the gate is blind (`n12=0`) at the open of 3 of 6 clusters and ranks the rest backwards. |
| Does a fwd-1M IC give an earlier warning? | **No.** Median wall-clock lead 1 month against a 2-month free floor from publication lag — i.e. **−1 month** in signal terms — at 30% unconfirmed alarms and 3 missed real ones. |
| Does gating BAL on the production momentum FLIPPED verdict help? | **No.** MaxDD is bit-identical across all 8 legs; a content-free calendar placebo beats the real gate; 3 of the 4 real episodes lost money. |
| Is BAL actually missing an adaptive feedback loop (gap G1)? | **No — the premise is wrong.** BAL already has a state-conditional loop. See §6. |

**Nothing was wired. `git status` clean on `pt_v23_audit_2014.py`, `simulate_holistic_nav.py`,
`edge_health_monitor.py`, `pt_v22_dt5g.py`, `signal_v11_sql.py`. `data/lag_edge_health.csv` — a
production contract — was never touched.**

---

## 2. Step 1 — the ledger, and two corrections to the brief

Artifact: `bal_edge_health.csv` (7,622 shadow trades, 2017-12 → 2026-02), built by
`build_bal_edge_health.py`, causal columns added by `make_causal_ledger.py`.

**Correction A — `lag_edge_health()` does not read realized fills.** It rebuilds the LAG *entry
cohort* from the earnings caches (`NP_R>=15 & prior_n_good>=4 & pa_HL3>=5`), enters T+5, holds the
book's own 25 sessions, and takes a plain price return — no sizing, no slots, no parking. That is
why it never stalls when the book is parked, and why it is causal enough to feed an allocator. The
brief's premise ("the ledger will stall because BAL is parking") does not apply; the real obstacle
is different and worse.

**Correction B — BAL is a BULL-only book by construction.** Every `TIER_BAL` buy tier in
`signal_v11_sql.py` requires `state5 IN (4,5)`:

```
WHEN ta >= 170 AND state5 IN (4,5) AND fa_tier IN ('C','D') THEN 'MEGA'
WHEN ta >= 155 AND state5 IN (4,5) AND fa_tier IN ('C','D') THEN 'MOMENTUM'
WHEN fa_tier = 'C' AND ta >= 100 AND state5 IN (4,5) AND (...) THEN 'DEEP_VALUE_RECOVERY'
```

DT5G has **zero** BULL/EXBULL sessions in 2014, 2015, 2016, 2019, 2022 and 2023 — BAL is silent for
6 of 13 years. Its cohort arrives in **10 episodes**, total 482 sessions.

**Why the symmetric gate cannot work.** Reading the ledger *causally* (stats keyed on exit date =
the date a return becomes knowable) at the open of each signal cluster:

| cluster opens | gate reading | n available | staleness | what the cluster then did |
|---|---|---|---|---|
| 2017-12-27 | — | **0** | — | −0.30% |
| 2020-10-07 | — | **0** | 819 days | +14.53% |
| 2024-01-25 | — | **0** | 688 days | +2.69% |
| 2025-03-10 | +2.69% | 956 | 237 days | **+12.49%** ← gate would have blocked the best |
| 2025-08-13 | +12.49% | 465 | 23 days | **−6.22%** ← gate would have waved through the worst |
| 2026-01-29 | +2.62% | 984 | 52 days | −1.14% (correct) |

Blind in half the cases; inverted in the rest. This is a shape problem, not a tuning problem.

**Defect found in passing (worth a separate look, not fixed here).** `data/lag_edge_health.csv`
keys its trailing-12M stats on **entry** date, but a LAG event's return is only knowable 25
sessions later. *Live this is harmless* — the file only ever contains completed events, so the last
row is ~5 weeks old and the allocator ffills a stale-but-real value. *In backtest it is not*:
`pt_v23_audit_2014.py:770-790` reindexes that entry-keyed series across all of 2014-2026, so on
historical day `d` the gate reads a value that required data from `d+25` sessions. Magnitude ~5
weeks; it sits inside the validation of the edge-conditional allocator's published +0.60pp. **This
does not affect the live gate and is not an argument to change it** — flagging it so someone can
size it deliberately. This ledger avoids the issue via `mean12_av`/`n12_av`, keyed on exit date.

---

## 3. Step 2 — a fwd-1M IC does not buy back the 3-month lag

`fast_ic_indicator.py` → `fast_ic_out.txt`, `realtime_verdicts.csv`, `flip_lead_times.csv`.
Source: `data/edge_panel.csv`, which **already carries `fwd_1m` next to `fwd_3m`** — no new source,
no new BQ cost. Two clocks kept apart: a signal month `m` is only *available* at `m+1` (fwd-1M) or
`m+3` (fwd-3M). Verdict rule = production `classify()`, with the `full` reference mean changed to
**expanding** — production compares recent-12M against the full sample, which is fine for reading a
dashboard today but peeks at the future when dating a historical alarm.

Across `mom_200` and `D_RSI` × `ALL` and `CYCLICAL`, 2014-2026:

- **19 matched alarms, median wall-clock lead = 1.0 month** (mean 3.6 is dragged by two 11m/21m
  outliers; range −1 to +21). The publication-lag difference alone is **2 months, free**. So in
  signal-month terms the fast indicator flips a month **later** — it does not even cover its own
  mechanical head start.
- **Cost: 8 of 27 fwd-1M alarms (30%) were never confirmed by a fwd-3M alarm within 12 months**,
  plus **3 real fwd-3M alarms it missed entirely**.
- **Today it would contradict production**: `mom_200 / CYCLICAL` reads FLIPPED on fwd-3M (t=3.21)
  but only WEAK on fwd-1M (t=1.82).

If someone wants earlier warning, the lever is **publication lag** (evaluate fwd-3M on the freshest
signal month that has data), not a shorter horizon.

---

## 4. Step 3 — prereg

`PREREG.md`, written before any backtest leg ran. Summary of what was committed in advance:

- **Gate:** production `mom_200`/ALL fwd-3M IC → `edge_health_monitor.classify()` = `FLIPPED`.
  Thresholds `T_SIG=2.0` and `MAG_MIN=0.015` are **pre-existing production constants** — zero free
  parameters. I deliberately did **not** invent a numeric threshold: LAG's `mean12 >= 4%` came from
  its own 2026-06-10 edge-cycle study, and BAL has no equivalent, so a number here would be a grid
  search wearing a prereg's clothes.
- **Action:** one axis — `MAX_POS_V11` 12 → 6 on gate-active sessions. Not "widen custom30V
  parking", because bull-parking is separately measured as non-robust (+0.49pp / −0.03 Sharpe,
  default OFF) and would confound the gate with an open question.
- **N = 4 independent episodes** (2020-10, 2021-03, 2024-01, 2026-01; 213 of 482 BULL sessions).
  **Declared in advance: IS 2014-2019 contains zero gate-active episodes, so walk-forward cannot
  adjudicate this rule.** Substituted leave-one-episode-out + per-year LOO, per `quant-research` §5.
  With N=4 the best possible sign test is p=0.125 — **no p-value here can clear a conventional bar**,
  so a GO would have had to rest on mechanism and dose-response shape.
- **Expected ΔCAGR ≈ 0**; a positive ΔCAGR was declared in advance *not* to count as support.
  Success required: MaxDD improves **and** Calmar improves **and** CAGR loss ≤ ~1pp **and** the sign
  survives ≥3/4 episode-LOO and ≥10/13 year-LOO.
- **Stopping rule:** if `g6` fails, do not go shopping in the ladder. (It failed. I did not.)

---

## 5. Step 4 — backtest

Environment identical to the R3 pin (`research/lag_repin_20260803/run_repin.sh`):
`BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate`, `BQ_CACHE_THREADS=1`, `NAV_TOTAL_B=50`,
`ETF_LIQ=custompitg`, `BASKET_WT=namecap`, `BASKET_SELECT=yieldcombo`, `PARK_STATES=3:0.7`,
`AUDIT_END=2026-06-19`, `$DNA_PYEXE`, `v23a none postbull 0 edge`, `EXP_TAG` on every leg.

**Harness validity — two independent proofs:**
- `ctrl` reproduces the pin exactly: **28.86% / 1.90 / −17.79% / 1.62 / 1,178.01B**, self-check
  **0 VND** on both books, and its CSV md5 is `7d053e6201c9d107685ff4d1dd9d2d2a` — the md5 already
  pinned in `results_registry.md`.
- `inert` (the research engine copy, run with no mask) produces a **byte-identical CSV, same md5**.
  The copy is provably inert; every delta below is the gate and nothing else.

| leg | CAGR | Sharpe | MaxDD | Calmar | Final NAV | ΔCAGR | self-check |
|---|---|---|---|---|---|---|---|
| ctrl (pin R3) | 28.86% | 1.90 | −17.79% | 1.62 | 1,178.01B | — | 0 VND |
| inert copy | 28.86% | 1.90 | −17.79% | 1.62 | 1,178.01B | +0.00pp | 0 VND |
| **g6 — pre-committed** | **29.16%** | **1.92** | **−17.79%** | **1.64** | **1,212.11B** | **+0.30pp** | 0 VND |
| g10 (12→10) | 29.18% | 1.93 | −17.79% | 1.64 | 1,214.24B | +0.31pp | 0 VND |
| g8 (12→8) | 29.02% | 1.90 | −17.79% | 1.63 | 1,196.23B | +0.16pp | 0 VND |
| g4 (12→4) | 29.22% | 1.96 | −17.79% | 1.64 | 1,219.87B | +0.36pp | 0 VND |
| g0 (12→0) | 25.89% | 1.80 | −17.79% | 1.46 | 881.14B | −2.97pp | 0 VND |
| **placebo** (calendar mask) | **29.26%** | 1.93 | −17.79% | 1.65 | 1,224.16B | **+0.40pp** | 0 VND |

Metrics recomputed independently from each leg's `DAILY.combined_nav` column match the harness's
own METRIC rows to 2 decimals (`analyze_out.txt`).

### Four independent reasons this is NO-GO

**(1) MaxDD is bit-identical in all eight legs — `−0.17785101`, trough 2018-07-05.** That trough is
in 2018, inside the window where the gate has *zero* active days. The gate cannot touch the
drawdown it exists to insure against. Prereg success criterion #1 fails outright, and no ladder
variant rescues it.

**(2) The placebo wins.** A calendar mask carrying no information about edge health scores **+0.40pp**
against the real gate's **+0.30pp**, and beats every ladder variant. The +0.30pp is not the gate
knowing something; it is "hold fewer BAL slots during 2020-2024."

**(3) Leave-one-episode-out: 1 of 4.** The three episodes where the momentum edge really was flagged
FLIPPED all *lost* money by cutting slots — ep6 −0.09pp, ep8 −0.01pp, ep14 −0.10pp — and only ep20
(12 sessions, Jan 2026) helped, +0.12pp. Sign test p=0.625. The four episodes together are
**−0.08pp**; the entire +0.23pp total comes from **+0.31pp of residual outside them** — path
divergence, including +0.032 log in 2025, a year with zero gate-active days.

**(4) No dose-response.** 12→10 +0.31, 12→8 +0.16, 12→6 +0.30, 12→4 +0.36, 12→0 −2.97. Noise around
+0.3 for any mild cut, then a cliff. A real threshold effect produces a monotonic ladder (`quant-
research` §10); this is the opposite.

**DSR/PBO not run** — per `quant-research` §13 they are required only when a specific config is being
recommended for wire. Nothing is being recommended. `N_trials = 6`, declared in advance.

---

## 6. The most useful result is the one that refutes the premise

`g0` is the informative leg: **fully suppressing BAL whenever `mom_200` reads FLIPPED costs −2.97pp
CAGR and drops Calmar 1.62 → 1.46.** The edge-health dashboard says momentum is flipped; the BAL
book made money anyway, through every one of those windows.

The mechanism is population mismatch, and it is not subtle. `edge_health_monitor` measures a
cross-sectional IC over the **whole liquid universe, every month**. BAL trades a **BULL/EXBULL-only,
tier-filtered, EXBULL-momentum-suppressed** subset. Those are different populations; a sign flip in
the first does not imply loss in the second.

So **gap G1 in `amh-adaptivity-review-20260910.md` should be re-stated.** BAL is not missing an
adaptive feedback loop. It has one, and it operates on *state* rather than on realized edge:
BULL-only entry tiers, plus EXBULL momentum suppression, plus regime-size weighting. What this job
establishes is that adding a *second* loop keyed to the IC dashboard is not incremental — measured,
placebo-controlled, NO-GO.

This is consistent with the standing AMH caveat: the one AMH-inspired directional signal this fleet
ever tested (ecology mood) was REFUTED walk-forward on 2026-07-13. Two for two.

---

## 7. Recommendations

1. **Do not wire any BAL edge-gate.** No production change requested; nothing needs user approval.
2. **Amend G1 in the AMH review** to "BAL's feedback loop is state-conditional, not edge-conditional,
   and an edge-conditional layer was tested and refuted 2026-09-10."
3. **Worth a separate, small job:** the entry-vs-exit keying of `data/lag_edge_health.csv` in
   *backtest* (§2). Live is unaffected. The question is only how much of the allocator's published
   +0.60pp survives an exit-keyed rebuild — a bounded, one-leg A/B, not a redesign.
4. **`data/bal_edge_health.csv` is NOT published to `data/`** and is not proposed as a production
   artifact. It lives here as research evidence. Neither it nor `data/edge_panel.csv` has a
   `mike/kb/data_registry/` entry — flagged for Winston; I did not add one (registry edits are
   data-ops' and need review per `coding_guidelines.md` §13).
5. **For the 2026-09-16 VPI/BAL review:** this job supplies no quantitative reason to cut BAL
   exposure on edge-health grounds. If BAL exposure is to be reduced, the argument has to come from
   somewhere other than the momentum IC dashboard — that channel was tested here and is empty.

---

## 8. Files

| File | What |
|---|---|
| `PREREG.md` | pre-registration, written before any leg ran |
| `build_bal_edge_health.py` → `bal_edge_health_dev.csv` | BAL shadow-cohort ledger, entry-keyed |
| `make_causal_ledger.py` → `bal_edge_health.csv` | + `mean12_av`/`win12_av`/`n12_av`, exit-keyed |
| `fast_ic_indicator.py` → `fast_ic_out.txt`, `realtime_verdicts.csv`, `flip_lead_times.csv` | step 2 |
| `build_gate_mask.py` → `gate_mask.csv` | pre-committed gate mask + placebo mask |
| `shn_edgegate.py` | engine copy, `max_positions_by_date` kwarg; **proven inert** (same md5 as ctrl) |
| `pt_v23_edgegate.py` | harness copy wiring the mask into BAL only |
| `run_leg.sh` | pinned run command, verbatim from the R3 pin |
| `bg_{ctrl,inert,g0,g4,g6,g8,g10,plac}.log` | 8 backtest logs, self-check lines included |
| `analyze_legs.py` → `analyze_out.txt` | metrics table, per-year, episode-LOO, placebo |

Result CSVs are in `data/` under `..._exp_bg_<leg>_univpit.csv`. **No canonical CSV was written**
(`coding_guidelines.md` §8 — every leg carried `EXP_TAG`).
