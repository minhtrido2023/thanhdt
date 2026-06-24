# Exp-8 — MGE leverage sensitivity (CAPIT config, Test A held fixed)

**Taylor, 2026-06-24** · Tier-3 BQ · same-snapshot `AUDIT_END=2026-06-19` · NAV 50B · self-check **0 VND** all 4 runs both books.

## Question (Mike dispatch)
Hold Test A best config fixed (`RECOVERY_CAPIT_ONLY=1`, vol_ratio 3M/63d threshold **1.7x**). Sweep ONLY the
gross-exposure cap **MGE ∈ {1.2, 1.3, 1.4, 1.5}**. Is there diminishing return (Calmar falling) pushing
MGE 1.3→1.5? Where is the cliff?

## Fixed config (every run identical except MGE)
```
RECOVERY_PARK=1 RECOVERY_WMAX=0.95 RECOVERY_PBZ_DEEP=-0.5 RECOVERY_DEP_FLOOR=0.075 \
MGE=<X> MGE_CAPIT_ONLY=1 \
RECOVERY_CAPIT_ONLY=1 RECOVERY_CAPIT_BASE=63 RECOVERY_CAPIT_VOL=1.7 \
ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7" \
NAV_TOTAL_B=50 AUDIT_END=2026-06-19  pt_v23_audit_2014.py v23a none postbull 0 edge
```
MGE=1.3 reproduces the published Test A exactly (FULL 31.09 vs registry 31.07 — rounding). IS = 2014-01..2019-12,
OOS = 2020-01..now, recomputed from each audit CSV with the harness's own `calc_metrics` (`data/_exp8_mge_recompute.py`).

## Results

| MGE | window | CAGR | Sharpe | MaxDD | Calmar | selfcheck |
|---|---|---|---|---|---|---|
| **1.2** | FULL | 31.08% | 1.88 | −21.5% | 1.44 | 0 VND |
|     | IS 14-19 | 25.89% | 1.77 | −13.3% | 1.94 | |
|     | OOS 20+ | 36.05% | 1.98 | −21.5% | 1.67 | |
| **1.3** | **FULL** | **31.09%** | **1.87** | **−20.5%** | **1.52** | **0 VND** |
|     | IS 14-19 | 26.13% | 1.78 | −13.4% | 1.96 | |
|     | OOS 20+ | 35.85% | 1.94 | −20.5% | 1.75 | |
| **1.4** | FULL | 30.98% | 1.86 | −20.5% | 1.51 | 0 VND |
|     | IS 14-19 | 26.40% | 1.79 | −13.4% | 1.97 | |
|     | OOS 20+ | 35.36% | 1.93 | −20.5% | 1.73 | |
| **1.5** | FULL | 30.93% | 1.86 | −20.5% | 1.51 | 0 VND |
|     | IS 14-19 | 26.83% | 1.81 | −13.5% | 1.99 | |
|     | OOS 20+ | 34.82% | 1.90 | −20.5% | 1.70 | |

## Marginal step (per +0.1 MGE)

| step | ΔFULL CAGR | ΔFULL Calmar | ΔOOS CAGR | ΔOOS Calmar | ΔMaxDD |
|---|---|---|---|---|---|
| 1.2→1.3 | +0.01pp | +0.08 | −0.20pp | +0.08 | −1.0pp (better) |
| 1.3→1.4 | −0.11pp | −0.01 | −0.49pp | −0.02 | 0.0 |
| 1.4→1.5 | −0.05pp | 0.00 | −0.54pp | −0.03 | 0.0 |

## Findings

**1. Diminishing return is REAL — and marginal return goes NEGATIVE past 1.3.**
- FULL CAGR peaks at **MGE 1.3 (31.09%)** then erodes: 31.09 → 30.98 → 30.93. Each +0.1 leverage past 1.3 *costs* CAGR.
- OOS CAGR is *monotonically decreasing* across the whole range (36.05 → 35.85 → 35.36 → 34.82) — the most-levered run is the worst OOS earner, and the decline *accelerates* (−0.20 → −0.49 → −0.54 per step).
- OOS Calmar falls monotonically from 1.3 (1.75 → 1.73 → 1.70).

**2. There is NO cliff — it's a smooth, gentle erosion, not a break.** MaxDD pins at **−20.5%** for MGE 1.3/1.4/1.5
(identical to 3 sig-figs). Because the leverage is `MGE_CAPIT_ONLY` it lands only on the capped deep-washout arm, so
the *binding* drawdown event does not deepen with more borrow. The cost of over-levering here is therefore **pure
return drag** (10%/yr borrow on the incremental headroom), **not tail risk** — risk does not blow up, return just bleeds.

**3. FULL Calmar peaks at 1.3 (1.52); 1.4/1.5 plateau one tick lower (1.51).** So 1.3–1.4 is a flat Calmar plateau, with
1.3 the apex. The drop to 1.5 is trivial (−0.01) but in the *wrong* direction with falling CAGR alongside.

**4. Why MGE 1.2 is NOT better despite the highest OOS CAGR (36.05%):** its FULL Calmar is the *worst* (1.44) because
its MaxDD is −21.5% (1pp deeper than the −20.5% plateau). This is a path artifact — at the lower cap the depth-scaled
fill into the 2022 bear interacts differently; it is not a monotonic risk signal (1.3 with *more* leverage has a
*shallower* DD). On the risk-adjusted metric 1.2 loses to 1.3.

**5. IS (2014-19) runs the OTHER way — Calmar rises with MGE (1.94→1.99), CAGR 25.89→26.83.** No recovery-park capit
deploy fires in-sample (all are 2020+ by construction), but the *standard CAPIT washout sleeve* (2018 bear) is also
`MGE_CAPIT_ONLY`-leverageable, and there the extra borrow pays in-sample. This is the same dormant-in-sample asymmetry
as DT5G — IS/OOS is a weak overfit test here; the net FULL verdict is driven by the OOS regime where over-levering bleeds.

## Verdict

🟢 **MGE = 1.3 is the optimum and the right stop.** It is the joint peak of FULL CAGR (31.09%) and FULL Calmar (1.52),
and the start of the OOS-Calmar decline. **Diminishing return pushing 1.3→1.5 is confirmed**: FULL CAGR −0.16pp,
OOS CAGR −1.03pp, OOS Calmar −0.05, with **MaxDD flat at −20.5%** the whole way. **No cliff** — a smooth bleed, because
CAPIT-only leverage caps the tail; the penalty for going past 1.3 is lost return (borrow cost), not added drawdown.
Going *below* to 1.2 trades a touch of OOS CAGR for a worse FULL Calmar (deeper DD). **Stay at 1.3.**

**Unchanged caveats:** REAL leverage (cash<0, borrow 10%/yr) → needs Spyros sign-off + user approval before any LIVE
use; go-live default stays leverage-free unless promoted. Cite DELTA vs same-snapshot baseline (V2.4-LF FULL 28.04%),
not absolute (brief's 30.63% predates VVS/VCS/DTD corp-action drift). Recompute helper: `data/_exp8_mge_recompute.py`.
