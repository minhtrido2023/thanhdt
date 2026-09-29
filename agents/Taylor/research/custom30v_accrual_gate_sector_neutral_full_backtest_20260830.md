# custom30V accrual-quality GATE, sector-neutral variant — full backtest cycle (Bước 2, job Taylor_20260830_035832)

Continues from the panel reconciliation (`custom30v_accrual_panel_reconciliation_20260830.md`, Bước
1 of the same job) — resolved BEFORE running this. Tests whether the sector-neutral standardization
found in job `_031841` (double-sort proxy +2.69pp/2M t=3.17 vs pooled +2.20pp t=2.35, LOO robust
12/12 years) survives the full production pipeline, mirroring the exact test already done for the
pooled variant (job `_014429`, **NO-GO**, `data/results_registry.md` "2026-08-30 — CUSTOM30V
ACCRUAL-QUALITY GATE").

## 1. Pre-registration (written before running)

- **Threshold = drop worst tercile (33%)**, same as the pooled arm — chosen for direct comparability,
  not tuned to this run. 20%/50% are robustness/sensitivity points only, never candidates to
  substitute if 33% underperforms.
- **Mechanism**: sector-neutral standardization of the GATE (not the tiebreak — tiebreak arm already
  NO-GO'd generically, job `_031818`, for a structural reason unrelated to which metric feeds it).
  Within `CFO_POOL` (top-60 liquid+gated), non-financial-route names are grouped by PIT sector
  (`FLOOR(ICB_Code/1000)`, dense buckets {1,2,3,7} kept separate, rest lumped OTHER — identical
  classification to job `_031841`'s panel), then the worst-33%-by-accrual_ratio is dropped **within
  each sector group** rather than pool-wide. A sector cell with <3 eligible names that rebal is a
  no-op for that cell (fail-safe, same convention as the pool-wide <3 fallback).
- **Scope, PIT convention, fail-open, direction**: identical to the pooled arm — non-financial routes
  only, `accrual_ratio=(TTM_NP-TTM_CFO)/|TTM_NP|` ascending (low=best), as-of Release_Date fallback
  time+45d, TTM_NP≤0 or missing → neutral pass-through (never dropped).
- **Decision rule** (same as both prior arms): **WIRE requires both IS and OOS to improve** vs the
  ctrl anchor — mixed-sign or wash is NO-GO, no cherry-picking among 20/33/50.

## 2. Harness — code change

Extended `custom_basket_ag.py` (same file as the pooled arm, no new fork) with
`BASKET_AGATE_SECNEUTRAL` (default `"0"`, byte-identical to before when off):
- New PIT sector map, one BQ query at each `rebal_date` (`t.ICB_Code` from `tav2_bq.ticker`),
  identical pattern to the pre-existing dynamic sector-cap block in the same file.
- `_agate_filter()` branches: `_SECNEUTRAL=False` path is the **original, untouched code** (pooled
  rank-and-drop); `_SECNEUTRAL=True` path groups eligible names by sector at date `d`, ranks/drops
  **within each group**.
- Verified in-run: `[accrual gate] ... sec_neutral=True` printed on all 3 legs; `[accrual gate
  sec-neutral] PIT sector map loaded: 53115 (ticker,rebal_date) cells` — mechanism executing as
  designed, not silently falling back to pooled.
- **ctrl leg not re-run**: `BASKET_AGATE_SECNEUTRAL` only branches when `SELECT_MODE==
  "yieldcombo_agate"`; the ctrl leg (`BASKET_SELECT=yieldcombo`) never touches this code path, so the
  already-verified pooled-job ctrl (byte-identical to pinned R3: 28.86%/1.90/−17.8%/1.62/1.178,01B,
  IS 27.09%/OOS 30.48%) is reused directly.
- Same pinned config as R3/pooled arm: `BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate
  BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap PARK_STATES="3:0.7"
  AUDIT_END=2026-06-19 LAG_ADV_BASIS=price`, threads=1. Logs: `eng_agate{20,33,50}sec.log`. CSVs
  auto-tagged `_exp_agate{20,33,50}sec_*` — canonical R3 CSV untouched.

## 3. Results — all 3 legs `EXIT=0`, self-check clean (0 VND, BAL+LAG, both identities)

| Leg | FULL CAGR | IS (14-19) | OOS (20+) | Sharpe(252) | MaxDD | Calmar | Final NAV |
|---|---|---|---|---|---|---|---|
| ctrl (0%, shared w/ pooled) | 28.86% | 27.09% | 30.48% | 1.90 | −17.8% | 1.62 | 1.178,01B |
| agate20sec (robustness) | 29.57% | 27.96% | 31.04% | 1.93 | −17.7% | 1.67 | 1.261,49B |
| **agate33sec (PRE-REGISTERED)** | **28.85%** | **27.16%** | **30.39%** | 1.91 | −17.2% | 1.67 | 1.176,89B |
| agate50sec (robustness) | 28.97% | 26.59% | 31.15% | 1.91 | −17.6% | 1.64 | 1.189,81B |

IS/OOS independently recomputed from each leg's `combined_nav` (record_type=`DAILY`), boundary dates
IS≤2019-12-31 / OOS≥2020-01-01, identical convention to the pooled/tiebreak arms.

**Δ vs ctrl (agate33sec, PRE-REGISTERED)**: FULL **−0.01pp**, IS **+0.07pp**, OOS **−0.09pp**,
Sharpe +0.01, MaxDD better (−17.2 vs −17.8), Calmar better (1.67 vs 1.62).

**Decision (§1 rule, "WIRE requires both IS and OOS improve"):** IS improved, OOS worsened — **mixed
sign, fails the rule.** **NO-GO.**

## 4. DSR / PBO (`dsr_pbo_agate_sec.py`, fork of the pooled job's `dsr_pbo_agate.py`, same formulas)

```
agate33sec per-obs SR=0.11579 (ann 1.838) vs ctrl per-obs SR=0.11538 (ann 1.832)
DSR vs SR0=0 (any skill):        P=1.0000
DSR vs SR0=ctrl (beats baseline): P=0.5090  <-- coin-flip, RED FLAG (<0.95, per coding_guidelines)
PBO across {0%,20%,33%,50%} = 0.622  <-- >=0.5, family prone to overfitting if cherry-picked
```

Both red flags reproduce at essentially the same severity as the pooled arm (DSR P=0.52, PBO=0.607)
— sector-neutral standardization did **not** meaningfully change the statistical verdict, only
shrank the magnitude of the (already negative-ish) full-pipeline effect toward zero.

## 5. Why the double-sort proxy edge (+2.69pp/2M) doesn't survive here — same mechanism as pooled

Identical read to the pooled arm's registry entry, reproduced with a smaller but still-present gap:
the double-sort measures an in-group edge (top-EY-tercile only, 2M horizon, no transaction cost).
The real gate runs on the full `custom30V` pipeline (`CFO_POOL`→`rank(1/PE)+rank(1/PCF)`→top-30, not
"top-EY-tercile first"), is only one part of NAV (NEUTRAL-state parking sleeve; BAL/LAG books
untouched), and goes through **real 0.1%/side transaction cost** on every rebalance
(`simulate_holistic_nav.py`, per `CLAUDE.md`'s cost convention) — the same dilution path that turned
`eyrisk`'s positive IC into a NO-GO, and the pooled gate's +2.05pp double-sort into an IS/OOS-both-
worse full result. Sector-neutral standardization measurably shrank the *proxy* gap's overstatement
(smaller full-pipeline degradation than pooled: pooled IS/OOS both **−0.08/−0.13pp**, sector-neutral
IS/OOS **+0.07/−0.09pp**, essentially a wash) but did not flip the full-pipeline sign to a clean GO —
the mixed-sign IS/OOS split and the coin-flip DSR both say this is noise-level, not a real edge worth
production risk.

## 6. Conclusion

**NO-GO**, same class of conclusion as the pooled gate (job `_014429`) and the tiebreak arm (job
`_031818`) — third independent test of a `custom_basket_ag.py`-family accrual-quality mechanism, all
three land on the same structural read: **a proxy edge measured on an in-group double-sort does not
survive the full pipeline + real transaction cost**, regardless of pooled-vs-sector-neutral
standardization or gate-vs-tiebreak mechanism. Sector-neutral standardization is directionally
"less bad" than pooled (smaller magnitude of degradation, IS improved this time) but still fails the
pre-registered WIRE rule and both robustness checks (DSR, PBO). **No further variant of this axis
(different threshold, different sector granularity) is recommended** — three structurally distinct
attempts (gate/pooled, tiebreak/pooled, gate/sector-neutral) at the same underlying accrual-quality
signal have now all failed the same full-pipeline test for the same diagnosed reason.

**Not wired.** `custom_basket.py` untouched throughout (only the audit-fork `custom_basket_ag.py`
was extended). No quant-skeptic pass requested — dispatch's mandate for that gate is conditional on
"trước khi đề xuất wire"; this doc proposes no wire.

Files: `mike/agents/Taylor/research/custom30v_accrual_gate_20260830/` (`custom_basket_ag.py`
extended with `BASKET_AGATE_SECNEUTRAL`, new `dsr_pbo_agate_sec.py`, `eng_agate{20,33,50}sec.log`).
CSV pin R3 untouched (all 3 new CSVs are non-canonical `_exp_agate*sec` tagged).
