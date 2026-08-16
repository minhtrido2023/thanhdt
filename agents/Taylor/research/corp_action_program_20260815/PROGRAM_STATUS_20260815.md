# Program status — corp-action research Sprints 1-4

> Author: Taylor (quant) · Date: 2026-08-15/16 · Branch: `session/1538146805207011358`
> Scope: read-only BigQuery research under this folder. No production tables, views, cron,
> trading rules, reports or wiring were changed.

## Current state

Sprints 1-4 are complete and committed in this worktree. There is no Sprint 5 preregistration yet,
so this note is a program-level status and handoff, not a new hypothesis lock.

| Sprint | Topic | Verdict | Key numbers / gate | Selfcheck |
|---|---|---|---|---|
| 1 | Ledger + data-quality audit | `CONDITIONAL PASS` | Ex-date/post-event allowed; announcement study banned because `public_date` is not proven PIT and table is upserted in place | 21/21 PASS |
| 2 | Cash dividend ex-date + drift | Module A `DESCRIPTIVE ONLY`; Module B `RISK / DUE-DILIGENCE` | P-CORE `BHAR_20 = -1.065%`, CI `[-1.599%, -0.533%]`; yield regression `-0.4971pp` per gross-yield pp, `t=-5.60`; no alpha candidate | 50/50 PASS |
| 3 | Stock dividend and bonus shares | Ex-date `DESCRIPTIVE ONLY`; AIS `RISK / DUE-DILIGENCE` | Ex `BHAR_20 = -0.575%` null; AIS T+20 `-0.988%`, Holm significant but OOS CI contains zero; no alpha candidate | 30/30 PASS |
| 4 | Rights, ESOP, private placement | `DESCRIPTIVE ONLY` | Rights T+20 `+1.647%` CI `[-0.151%, +3.734%]` Holm `0.1588`; pooled AIS T+20 `-0.584%` CI `[-2.061%, +1.089%]`; dilution/discount null | 32/32 PASS |

## Program-level verdict

**No alpha candidate has been established in any Sprint.**

- Cash-dividend results support a negative post-ex cost association, not a tradeable edge and
  not a causal claim. Short-selling is unavailable in VN, so the negative drift is a planning
  data point, not a harvestable signal.
- Stock-distribution ex-date results are null after multiplicity correction. The short AIS
  negative window is a due-diligence risk, not a strategy.
- Issuance-family results are descriptive only; rights T+5 positive association does not survive
  the locked T+20 primary, matched controls, or wider population checks.
- No production gate, no `coding_guidelines` §21 change, no live signal, no cron/trading rule.

## Maintained constraints

- Announcement studies remain forbidden until a second ledger vintage proves amendment rate.
- `ticker.Price` on the exact ex-date row remains banned; all Sprints used the reconstructed/raw
  price route consistent with the Sprint 1 gate.
- Every numeric claim in the sprint reports is backed by `out*/results.json` and the corresponding
  selfcheck.
- This research folder is the only committed scope; `kb/fleet_status.md` remains an unrelated
  pre-existing local change and was not touched.

## Open items and recommended next actions

| # | Item | Source | Suggested owner / timing |
|---|---|---|---|
| O1 | Measure amendment rate by rebuilding `build_event_ledger.py` and diffing the second vintage against `out/vintage_asof_20260814.csv.gz` | `ISSUES_LEDGER.md` C1 / Sprint 2 S2-3 | Taylor/Winston around **2026-09-12**; prerequisite for announcement study |
| O2 | Trace the 182 cash-dividend cases with no price step (and the 694 X4 cases) | `ISSUES_LEDGER.md` C2 / Sprint 2 S2-2 | Winston/data-quality, before relying on the full adjusted-price population |
| O3 | Reconcile `value_per_share` against real broker cash receipts | `ISSUES_LEDGER.md` C5 | Winston/ops; `coding_guidelines` §21 stays unchanged |
| O4 | Report `ticker.Price` anomalies for DNN/BCB/PTX to Winston/bq_admin | `ISSUES_LEDGER.md` C3 | Data-quality follow-up, already filtered in research samples |
| O5 | Decide whether `Close` dividend reconstruction uses gross or net dividend | Sprint 2 S2-1 | Winston -> bq_admin |
| O6 | Consider adding “ex-date + yield” to candidate due-diligence; product decision, not research result | Sprint 2 S2-4 | User / Mike |
| O7 | No PIT market-cap control in Sprints 3-4 | `SPRINT3_DEVIATIONS.md`, `SPRINT4_DEVIATIONS.md` | Future work if size control is required |
| O8 | Tier-B AIS fallback and rights matched-control N below floor | `SPRINT4_DEVIATIONS.md` D2/D4 | Disclosed limits; no upgrade to verdict |

## Reproducibility

- Sprint 1: `profile_corp_action.py` → `build_event_ledger.py` → `selfcheck_sprint1.py`.
- Sprint 2: `sprint2_build.py` → `sprint2_analyze.py` → `sprint2_plots.py` →
  `selfcheck_sprint2.py`.
- Sprint 3: `sprint3_build.py` → `sprint3_analyze.py` → `sprint3_plots.py` →
  `selfcheck_sprint3.py`.
- Sprint 4: `sprint4_build.py` → `sprint4_analyze.py` → `sprint4_plots.py` →
  `selfcheck_sprint4.py`.

Large per-event panels are gitignored; the committed SQL and scripts rebuild them read-only.

## Next step

Recommended next step is to close the data/ops items O1-O4 before writing any new preregistration.
If a new research sprint is wanted, it should be a separate prereg with explicit scope and gates,
and should not re-open announcement study or any conclusion already closed above.
