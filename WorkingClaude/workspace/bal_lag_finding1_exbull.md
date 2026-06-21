# Finding #1 — BAL momentum inverts in EX-BULL (state5==5) → suppress = validated win
**2026-06-12. Session: BAL/LAG selection deep-dive (kickoff angle #1 = per-term IC attribution).**

## The diagnosis (per-term IC attribution on `ta`, by DT5G state)
Panel = `ticker_prune`, liq≥1e9, 2014→2026, clean LEAD fwd20/fwd40 (NOT profit_*). Spearman IC.
Scripts: `workspace/bal_ic_attr.sql`, `workspace/bal_ta_panel.sql` → `workspace/bal_ta_panel.csv`.

**Composite `ta` IC by state (fwd20):**
| state | n | IC_ta | IC_mom | IC_val |
|---|---|---|---|---|
| CRISIS(1) | 121k | −0.046 | −0.064 | +0.049 |
| BEAR(2) | 53k | +0.029 | +0.032 | −0.008 |
| NEUTRAL(3) | 348k | +0.062 | +0.059 | +0.017 |
| BULL(4) | 111k | +0.044 | +0.030 | +0.043 |
| **EX-BULL(5)** | 17k | **−0.267** | **−0.307** | **+0.076** |

**EX-BULL momentum inversion is STRUCTURAL — 3/3 episodes** (the only state-5 windows in DT5G history):
2020 IC_mom −0.11 · 2021 −0.48 · 2025 −0.14. Value block stays POSITIVE (+0.076) in EX-BULL.

**Tier-bucket forward returns confirm monotone inversion in EX-BULL** (book buys the wrong end):
- ta 140–155 → fwd20 −6.0% / win 24% (worst)
- ta<70 (low momentum) → fwd20 +5.1% / win 54% (best)
vs BULL where it's correctly monotone (ta≥155 → +9.3%/66%).

## Why this caused the 2025-08 grind
- The grind started **2025-08**. Aug-Sep 2025 = **27 days in EX-BULL (state 5)**.
- Book's momentum tiers (MEGA/MOMENTUM/MOMENTUM_S/S_PRO) fire in `state5 IN (4,5)` — i.e. they buy peak momentum in EX-BULL too.
- The existing `overheat` guard requires VNINDEX > **1.30×MA200** AND (state5==5 OR RSI>0.75). In Aug-Sep 2025 the index was only **1.15–1.28×MA200 → guard NEVER fired**. The book bought momentum freely into the euphoria top, then it reversed → start of the −11.8%/294d grind.
- (NOTE: a *second, separate* problem remains — the 2025-26 NEUTRAL momentum flip: IC_mom 2025 +0.00 / 2026 −0.09 while IC_val +0.05/+0.03. EX-BULL fix only addresses the START of the grind. NEUTRAL style-rotation detector = open angle #2.)

## The fix (validated on faithful 2-ledger engine, real TC, 50B)
In `state5==5`, suppress momentum BUY tiers {MEGA, MOMENTUM, MOMENTUM_S, MOMENTUM_QUALITY, MOMENTUM_A, S_PRO} → `AVOID_exbull`. Keep value tiers (DEEP_VALUE_RECOVERY, COMPOUNDER_BUY, RE_BACKLOG_BUY) which have +IC in EX-BULL. Only REMOVES trades → capacity-safe, causal (live DT5G state). Test: `workspace/pt_v22_exbull_test.py`.

**Combined V2.2 + CAPIT v2.1 (50B):**
| window | baseline | EXBULL fix | Δ |
|---|---|---|---|
| FULL 2014-now | 25.77% / −20.1 / Sh1.65 / Cal1.28 | **26.09% / −20.3 / Sh1.68 / Cal1.29** | +0.32pp |
| 2022+ | 16.44% / −18.7 / 1.06 / 0.88 | 16.78% / −17.4 / 1.08 / 0.97 | +0.34pp, DD better |
| **2025+** | 18.30% / −18.7 / 1.04 / 0.98 | **19.85% / −17.4 / 1.13 / 1.14** | **+1.55pp, DD −1.3pp, Sh+0.09, Cal+0.16** |

**BAL leg only (where the fix bites; LAG unaffected), V2.2+capit:**
- FULL: 19.01% / −25.4 / 1.20 → **20.16% / −20.6 / 1.28** (+1.15pp CAGR, **MaxDD −4.8pp**)
- 2025+: 2.59% / −25.4 / 0.23 → **8.36% / −19.9 / 0.48** (+5.8pp CAGR, MaxDD −5.5pp)

Headline = the BAL book's worst-ever drawdown (the 2025 grind, −25.4%) is cut ~5pp because the grind began with EX-BULL top-buying.

## Caveat / robustness
- No-capit base FULL dips slightly (17.70→16.50 BAL-leg) because suppressing 2021 EX-BULL momentum forgoes some price gains (2021 names rose despite −IC; high-mom rose *less*). But **production = V2.2+capit**, where it's net +1.15pp FULL on the BAL leg *and* a large MaxDD cut — the freed cash is redeployed by capit into the following correction.
- Signal is structural (3/3 episodes), causal, removes-only → low overfit risk.

## Deploy recommendation (NOT yet wired to live)
Mirror the overheat guard in `pt_v22_dt5g.py` (after line ~220):
```python
EXB_MOM={"MEGA","MOMENTUM","MOMENTUM_S","MOMENTUM_QUALITY","MOMENTUM_A","S_PRO"}
sig_f.loc[(sig_f["state"]==5)&sig_f["play_type"].isin(EXB_MOM),"play_type"]="AVOID_exbull"
```
(and optionally tighten the `overheat` def, but the standalone state5==5 guard is the clean version). Currently DT5G live = NEUTRAL(3), so this would be DORMANT today — safe to deploy, fires only at the next euphoria top.
