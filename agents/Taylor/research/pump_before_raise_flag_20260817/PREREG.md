# PREREG — "pre-raise high-momentum issuer" flag: threshold, sector, beta

Job `Taylor_20260817_101337`. Follow-up to `serial_capital_raiser_20260817` (commit `ec3fd8d2`).
**This file is committed before any outcome number in Mục 1/2/3 is produced.** Anything computed
after this commit that is not specified here is a DEVIATION and goes in `DEVIATIONS.md` with a
reason.

Descriptive facts already established BEFORE this prereg (and used to write it — declared so that
nobody later mistakes them for results): the prior program's event panel has 2,953 ISS events / 578
tickers; 735 of them are RIGHTS ∪ PRIVATE_PLACEMENT; `ICB_Code` is the 4-digit ICB and code 8777
covers 32 tickers that are all brokerages (SSI, HCM, SHS, VND, MBS, BSI, FTS, CTS, …);
`tav2_bq.risk_rating.Beta` takes only the values 1–5 and is NULL on 99,047 of 117,390 rows.

---

## 0. Language rule (binding on every output file)

Never "manipulation", "pump", "thao túng", "tội phạm" as a claim about any named company. The
construct is **"pre-raise high-momentum issuer"** — a *statistical* condition on realised excess
return before an ex-date. The internal shorthand `PRHM` may be used; `pump` may appear only inside a
quoted restatement of the dispatch. No individual ticker is characterised as having done anything
improper anywhere in `FINDINGS.md` or `FLAG_SPEC.md`.

## 1. Data — reuse, do not rebuild

Primary input is the already-built `../serial_capital_raiser_20260817/out/q1_bhar.csv` (2,953 rows).
`pretrend_250`, `bhar_250/500/750`, `icb`, `adv60`, `rvol60`, `subtype`, `month`, `year` are read as
stored. The event keys, the dedup/survivor rule, the `universe_pit` PIT gate and the session-indexed
horizons are inherited unchanged; re-deriving them would risk silent drift.

One new read-only BQ pull (`build_extras.py`), keyed on the identical `(ticker, t0)` set, importing
`EVENTS_CTE`/`PX_CTE`/`Q1_MIN`/`Q1_MAX` **directly from the prior program's `build.py`** so the event
definition cannot diverge:

| new field | definition | why |
|---|---|---|
| `roic_trailing`, `fscore`, `npm_p0`, `debt_eq`, `pe`, `pb` | `tav2_bq.ticker` **as stored** on the session at `k = −1` (last session strictly before the ex-date) | false-positive gate (Mục 1); read as stored per registry `valuation_pe_pb_pcf_ps.md` bẫy (4) — never rescaled |
| `beta_raw`, `beta_n` | OLS beta of the ticker's daily return on VNINDEX's over `k ∈ [−250, −1]`, `COVAR_POP/VAR_POP`; NULL unless `beta_n ≥ 150` | Mục 3 primary; the only measure that can carry the dispatched 1.2/1.8 cut points |
| `rr_beta_bin`, `rr_quarter`, `rr_lag_q` | `tav2_bq.risk_rating` `Beta`, taking the latest `quarter` **strictly before** the calendar quarter containing `t0` | Mục 3 cross-check against the canonical table |

`SELECT DISTINCT` on `risk_rating` regardless of whether the current vintage shows duplicates
(CLAUDE.md standing trap #3).

**Deviation declared in advance — D-B1.** The dispatch asks for beta cuts at 1.2 / 1.8 from
`tav2_bq.risk_rating`. That column cannot deliver them: it is an integer 1–5 **bin**, not a beta
coefficient (`SSI` = 5.0 in every quarter since 2025Q2), and it is NULL on 84.4% of table rows.
Applying "≤1.2" to it would silently mean "bin 1 only". So the **primary** beta is the
self-computed 250-session coefficient above, on the dispatched cut points; `risk_rating.Beta` is
reported as a **secondary** cross-check on its own scale (low = bin 1–2, mid = 3, high = 4–5), with
coverage stated. Both are point-in-time.

## 2. Mục 1 — threshold grid and the rule for picking T

**Population P (primary):** events with `subtype ∈ {RIGHTS, PRIVATE_PLACEMENT}` and both
`pretrend_250` and `bhar_250` non-null. (The dispatch names these two subtypes; the prior program's
`RAISE_SET` additionally contains AUCTION at n=23, which is below that program's own N=200 reporting
floor. AUCTION is therefore reported as a **sensitivity**, `P_RAISE`, not folded into the primary.)

**Grid:** `T ∈ {15%, 20%, 25%, 30%, 40%, 50%, 60%}` — exactly as dispatched, no other value tried.

**Per T report:** `n_susp`, `n_non`, distinct tickers each side, mean `bhar_250` each side, `gap =
mean_susp − mean_non`, block-bootstrap 95% CI and p for the gap (blocks = anchor year-month, the
prior program's `scr_lib.boot`), plus `bhar_500`/`bhar_750` gaps for context.

**False positive rate** — the dispatch's definition, taken literally:
`FPR(T) = share of suspected events with (ROIC_Trailing > m) AND (FSCORE > 4)`, where `m` = **median
`ROIC_Trailing` over the whole of P** (events with either field missing are excluded from the FPR
denominator, and that denominator is reported next to the rate). Sensitivity: `m` recomputed as the
within-calendar-year median. Rationale for calling this a false positive is the dispatch's: the flag
fires, yet profitability and Piotroski both look healthy, so the run-up is plausibly earned.

**Selection rule — applied in this order, decided now:**

1. **Power floor.** Both groups ≥ 100 events **and** ≥ 60 distinct tickers. A T failing this is
   ineligible regardless of its gap.
2. **Gap requirement.** Bootstrap 95% CI of the gap excludes zero, **and** the gap is ≤ −5.0pp
   (suspected group worse), **and** the gap's p survives Holm across all 7 grid points.
3. **False-positive requirement.** `FPR(T) < 0.40`.
4. Among the T that pass 1–3, take the **largest |gap|**. If two are within 1.0pp of each other,
   prefer the **smaller T** (wider coverage); still tied, prefer the smaller FPR.
5. **If no T passes 1–3 → verdict `NO-FLAG`.** No `T_optimal` is named, `FLAG_SPEC.md` documents the
   flag as NOT RECOMMENDED FOR WIRING and says why, and Mục 3's combined cut uses the least-bad T
   purely as a labelled exploratory slice.

**Stability, decided now and binding on the verdict.** At the chosen T, split IS (`t0 < 2020`) /
OOS (`t0 ≥ 2020`) and run leave-one-year-out on the gap. If the gap **flips sign OOS**, or one year
carries > 60% of the effect, the flag is labelled **IS-ONLY / NOT DEPLOYABLE AS A RETURN
PREDICTOR** in `FLAG_SPEC.md` even if steps 1–4 selected a T. The prior program already found
`bhar_250` insignificant OOS for the pooled RAISE_SET, so this is an expected, not a hypothetical,
branch.

**N trials declared:** 7 (Mục 1 grid) + 3 (Mục 3 beta bins) + 1 (combined cut) = **11** on one
sample. Holm within each family; families named in `FINDINGS.md`. DSR/PBO are **not** computed
because nothing here is being selected for deployment — same reasoning as the prior program's
PREREG §5. If anyone later proposes wiring this flag as a return screen, DSR/PBO plus a
quant-skeptic gate become mandatory first.

## 3. Mục 2 — sector

Sector = `ICB_Code` at `k = −1`, 4 digits. **Securities / non-bank financial = ICB 8777
(Investment Services)**; the neighbouring financial codes 8355 (Banks), 8536/8575 (Insurance),
8773/8775 (Consumer & Specialty Finance) are reported separately and never merged into 8777.

Measures, on P and on all-ISS:
- raises per distinct ticker, and share of the sector's tickers with ≥2 raises, vs all other sectors;
- `bhar_250` for 8777 vs the rest, block-bootstrap CI;
- the top-20 tickers by ISS count over the window, each with its ICB code and a sector label.

**Reporting floors:** a CI is shown from N ≥ 30 events; **no verdict** is offered below N = 100
events / 60 tickers — the number is printed with an explicit "below verdict floor" tag instead.
Sector labels come from the ICB code itself, cross-checked against the actual ticker membership;
where a code's membership does not obviously match its ICB name, the label is written as
`ICB <code> (unverified label)` rather than guessed.

## 4. Mục 3 — beta

Bins on `beta_raw`: **low ≤ 1.2**, **mid (1.2, 1.8]**, **high > 1.8**. Report `bhar_250` per bin with
block-bootstrap CI, plus the monotonicity check (does BHAR fall as beta rises?). Cross-check the same
three-way ordering with `rr_beta_bin` (1–2 / 3 / 4–5).

Combined cut: `suspected(T_chosen) AND beta_high`. **Power declaration decided now:** if that cell
has < 60 events or < 40 distinct tickers, it is reported with its CI and explicitly labelled
**UNDERPOWERED — no verdict**, and it may not appear as a recommendation in `FLAG_SPEC.md`.

A beta result is only called "beta predicts underperformance" if the trend across the three bins is
monotone **and** the low-vs-high difference's bootstrap CI excludes zero. Otherwise: "no ordering
detected".

## 5. Cross-check in place of a `self-check 0 VND`

No NAV is simulated, so the money identity does not apply. Substituted, and required to pass before
`FINDINGS.md` is written:

- **CC1** — pooled `bhar_250` over `RAISE_SET` recomputed here must reproduce the prior program's
  published **−7.74% at n=712** (tolerance 1e-6 on the mean, exact on n).
- **CC2** — pooled `pretrend_250` over `RAISE_SET` must reproduce **+45.54%**, and the far placebo
  **+30.21%** (same tolerance).
- **CC3** — both threshold groups at every T must partition P exactly: `n_susp + n_non == |P|`.
- **CC4** — the chosen T's suspected-group mean `bhar_250` must lie inside the prior program's
  pre-trend-quartile table's range for the top two quartiles (−7.90% … −10.38%) **or** the deviation
  must be explained in `FINDINGS.md`. This is the consistency requirement the dispatch asked for.
- **CC5** — `build_extras.py`'s event key set must equal `q1_bhar.csv`'s exactly (same 2,953 pairs).

`selfcheck_pump_flag.py` runs these plus the threshold/sector/beta logic tests on fixtures. It must
pass identically under `env -u TZ` and under a foreign `TZ` (§16 of `coding_guidelines.md`).

## 6. Out of scope — stated so it is not quietly added later

No announcement-window study (`public_date` is `WEAK_UNVERIFIED_VINTAGE` until the second
`corporate_action` vintage, ≈2026-09-12). No wiring into `due_diligence.py`, no change to
`trading_rules.json`, no cron. No new research questions beyond the three above. `FLAG_SPEC.md` is a
**specification document only** — it describes what would be wired, and under the verdict above may
well say "do not wire this as a return predictor".
