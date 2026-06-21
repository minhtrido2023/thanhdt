---
name: FA sector-IC patterns (descriptive, not actionable in scoring)
description: Sector IC differences are real but sector-conditional weighting/filtering FAILS at portfolio level; use as manual selection knowledge
type: project
originSessionId: 762b6179-ddcb-41b7-ac2b-ee8d2f143ccc
---
# Sector-IC patterns — descriptive, not for automated scoring

**Date:** 2026-05-13 | Scripts: `test_fa_growth_sector_horizon.py`, `test_fa_v7_sector.py`, `test_fa_v7_sector_elite.py`

## Key sector-specific IC findings (vs profit_3M, Q4 universe)

### Strong patterns (use as manual selection knowledge)

**Banks (sector 8, N=1097):**
- NP_TTM_growth = **-0.125** — high-growth banks UNDERPERFORM
- ROE_Min5Y = +0.106 (the only meaningful indicator)
- ROIC5Y = +0.009 (zero — typical for banks; use ROE)
- → Manual rule: prefer banks with high stable ROE + AVOID high earnings growth

**Tech (sector 9, N=56 small):**
- FCF_yield = **+0.280** extreme (highest in any sector for any indicator)
- NP_CV (inv) = +0.247 (stability strong)
- smoothed_EY = -0.024 (value DOESN'T work for tech)
- → Manual rule: prefer tech with high FCF yield + stable earnings; ignore PE

**Energy/Cyclical (sector 0, N=78):**
- NP_peak_ratio = **+0.308** extreme (peak earnings detection works for commodities)
- → Manual rule: cyclical at-peak signals top → sell signal

**Materials (sector 1, N=417):**
- smoothed_EY = +0.017 (zero — value doesn't work)
- ROIC5Y = +0.134 (strong)
- → Manual rule: focus on ROIC, ignore valuation z-scores

**ConsServices (sector 5, N=153):**
- smoothed_EY = +0.267, NP_TTM_growth = +0.209 (both work)
- → Both value and growth matter

**Industrials (sector 2, N=756):** balanced classic FA, all axes work
**ConsGoods (sector 3, N=493):** standard v4-like, no special handling
**Utility (sector 7, N=150):** ROIC matters, FCF_yield NEGATIVE (-0.092)

## Why sector-conditional scoring FAILS at portfolio level

Tested 3 approaches, all failed:

1. **Sector-tuned axis weights (v7_full)**: -0.73pp spread vs v6b. Reason: aggregation issue — different weights per sector create apples-vs-oranges in global ranking.

2. **Sector-relative ranking (T6e/T6g, earlier session)**: neutral. Same issue.

3. **Sector-elite filter (within A tier)**: -2.2 to -3.6pp WR. Materials and Banks improve, but Industrials lose -7.54pp (overfilters good picks).

Root cause: v6b's universal scoring already picks well across sectors (Materials A tier +15.70%, Tech +15.87%). Adding explicit sector logic creates overfit + breaks ranking aggregation.

## Where these insights ARE useful

✅ **Manual rules in `recommend_holistic.py`** (live picks):
- When choosing from A tier, prefer Banks with low NP_TTM
- When choosing from A tier, prefer Tech with high FCF_yield
- When choosing from A tier, prefer Energy/Cyclical at NP_peak_ratio=1

✅ **Risk filtering in portfolio construction**: cap Industrials exposure (highest variance in A tier)

✅ **Hold period strategy**: FA alpha is 2x at 2Y vs 3M (smoothed_EY IC 0.081→0.182). Long-hold strategies absorb more FA alpha.

❌ **Don't automate into FA scoring** — validated failure across 3 separate approaches.

## Status

- [x] Sector-conditional v7 weights tested → reject
- [x] Sector-elite filters tested → reject  
- [x] Sector findings documented as manual knowledge
- **FA-system production stays at v6b** (uniform scoring)
