---
name: BA picks manual review rules (from LH v3 research)
description: Manual filtering rules to apply when reviewing daily BA picks. Based on multi-factor + sector-conditional research. Do NOT modify BA score formula — apply as discretionary screen.
type: project
originSessionId: 70c13426-2492-456b-9547-d14c8cf8fcb7
---
# BA Picks — Manual Review Rules

**Created**: 2026-05-15 | **Source**: LH v3 multi-factor research (`research_lh_v3_factors.py`, `research_commodity_sectors.py`, `research_lh_v3_sector_conditional.py`)

## Why these rules

LH v3 multi-factor research surfaced 3 strong insights that BA-system doesn't explicitly use:
1. **Cash_MktCap** is a defensive premium factor (+0.16 IC at 1Y) — not in BA score
2. **Commodity-cyclical sectors have INVERSE cycle dynamics** (IC -0.13 to -0.24) — STEEL/OIL_GAS/RUBBER/CHEMICAL/AQUA/SHIPPING tend to crash AFTER FA looks strongest
3. **All Value factors positive IC** at 1Y — smoothed_EY/BY/EVEB_inv consistent +0.10 to +0.16

These insights are at **1Y horizon** (LH's hold period). BA-system holds 45d so direct application differs, but the **stock-quality dimension** still helps when manually reviewing BA daily picks.

**Important**: Do NOT add these as BA score bonuses without canonical sim validation (memory rule from FA v5/v8c failures).
Use as **manual discretionary filters** when reviewing recommend_holistic.py output.

---

## ✅ POSITIVE TILT — Prefer when reviewing BA picks

### Rule 1: Cash buffer bonus
- **When**: ticker has `Cash_P0 / MktCap ≥ 0.20` (20%+ cash buffer)
- **Action**: Prefer this ticker over equivalent-score peers
- **Rationale**: Cash-rich companies have dry powder, defensive premium, IC +0.16 at 1Y
- **Examples to look for**: industrials with conservative balance sheet

### Rule 2: Value confirmation
- **When**: BA tier ≥ S AND `PE < PE_MA5Y - 1 × PE_SD5Y` (deep value vs own history)
- **Action**: High conviction pick — value + momentum confluence
- **Rationale**: PE z-score most consistent value factor in VN
- **Watch**: avoid value traps (next rule)

### Rule 3: Strong NP growth in NON-cyclical sector
- **When**: ticker is BANK / REIT / INSURANCE / TEXTILE / RETAIL AND `NP_TTM growth > +15%`
- **Action**: Prefer
- **Rationale**: For non-cyclical sectors, IC of NP_yoy is POSITIVE (+0.07 to +0.23). Buying improving fundamentals works.

---

## ❌ NEGATIVE TILT — Avoid or downsize

### Rule 4: Commodity peak warning ⚠️ KEY
- **When**: ticker is in commodity-cyclical group AND meets 2+ peak indicators:
  - Group: `STEEL` (HPG/HSG/NKG/POM), `OIL_GAS` (BSR/PVD/PVS/GAS), `CHEMICAL` (DGC/DCM/DPM), `RUBBER` (GVR/PHR/DPR), `AQUACULTURE` (VHC/ANV/MPC), `SHIPPING` (HAH/VOS/GMD), `COAL` (KSB/TVD)
  - Peak indicator A: `NP_TTM_growth > +30%`
  - Peak indicator B: `12M return > +40%`
  - Peak indicator C: `GPM expansion > +5pp YoY`
  - Peak indicator D: `Close > MA200 × 1.30`
- **Action**: SKIP or reduce position 50%
- **Rationale**: IC analysis showed -0.13 to -0.24 cycle IC for commodity sectors. FA score peaks correspond to PRICE peaks.
- **Historical examples avoided**:
  - HPG @ 2021-Q3 (peak before -65% crash)
  - DGC @ 2022-Q3 (peak before -50% crash)
  - VHC @ 2022-Q2 (peak before -55% crash)

### Rule 5: Commodity downtrend trap
- **When**: ticker is in commodity-cyclical group AND:
  - `12M return < -30%` (already crashed)
  - `Close < MA200` (long-term downtrend)
  - `NP_TTM growth < 0` (earnings still declining)
- **Action**: WAIT for bottom signal (Rule 6 below). Don't catch falling knife.
- **Rationale**: Commodity cycles take 4-8 quarters. Trough buying needs catalyst.

### Rule 6: NP decline in non-cyclical sector
- **When**: ticker is in BANK / REIT / INSURANCE / TEXTILE AND `NP_TTM growth < -10%`
- **Action**: SKIP even if BA score is high
- **Rationale**: For non-cyclical sectors, NP growth direction matters. Declining earnings → forward returns negative.

---

## 🎯 CYCLICAL CONTRARIAN — Special opportunity

### Rule 7: Commodity trough buying
- **When**: ticker is in commodity-cyclical group AND meets BOTH:
  - `NP_TTM growth < -20%` (deep earnings decline)
  - `12M return < -25%` (price crashed)
  - `Close > MA200` (recovering — broke back above trend)
  - `Cash_P0 / MktCap > 0.15` (survived with cash)
- **Action**: STRONG BUY (even if BA score is moderate)
- **Rationale**: Anti-cycle works for commodity sectors. Buy bottom = buy future earnings recovery at low cost.
- **Examples that would have triggered**:
  - HPG @ Q4-2022 (after -65% crash, cash strong, MA200 cross up)
  - DGC @ ? (TBD — currently still in downcycle)
  - VHC @ Q3-2023 (after -55% crash)

---

## 📋 Quick checklist for daily BA pick review

When recommend_holistic.py outputs daily picks, run through this checklist:

| Step | Question | Action if NO/RED FLAG |
|---|---|---|
| 1 | Is ticker in commodity-cyclical group? (STEEL/OIL_GAS/RUBBER/CHEMICAL/AQUA/SHIPPING/COAL) | If YES → check Rules 4-5 strictly |
| 2 | If commodity: are 2+ peak indicators triggered? | SKIP (Rule 4) |
| 3 | If non-cyclical: is NP_TTM growth ≥ 0? | SKIP if NO (Rule 6) |
| 4 | Does ticker have Cash_P0/MktCap ≥ 20%? | If YES → bonus conviction (Rule 1) |
| 5 | Is PE deeply below 5Y average? (PE_z < -1) | If YES → bonus conviction (Rule 2) |
| 6 | If commodity in deep trough: cash strong AND MA200 cross up? | If YES → strong buy candidate (Rule 7) |

---

## Active warnings on current commodity universe (snapshot 2026-Q1)

Based on `lh_v3_sector_cycle.csv`:

| Group | Status | Active warning |
|---|---|---|
| STEEL (HPG/HSG) | Early upcycle (+0.31) | NP yoy +38% rebound — watch for Rule 4 if continues to push high |
| **OIL_GAS** (BSR/PVD) | ⚠ **PEAK WARNING** | NP yoy +208% spike — Rule 4 likely fires; take profits |
| **CHEMICAL** (DGC) | Deep downcycle (-0.50) | NP yoy -13%; wait for cash + MA200 reclaim signal (Rule 7) |
| RUBBER (GVR/PHR) | Downcycle (-0.37) | Watch for trough signal |
| AQUACULTURE (VHC/ANV) | Recovery (+0.23) | NP yoy +64% — early bullish but commodity = treat with caution |
| SHIPPING (HAH/VOS) | Mid-cycle (-0.07) | Neutral |

## Sector universe groupings (for reference)

```
COMMODITY_CYCLICAL = {STEEL, OIL_GAS, RUBBER, AQUACULTURE, SHIPPING, CHEMICAL, COAL, SUGAR, CEMENT, PAPER_PULP, AVIATION}
NON_COMMODITY_NORMAL = {BANK, REIT_RES, REIT_KCN, INSURANCE, TEXTILE, RETAIL, SECURITIES, DAIRY, BEVERAGE}
```

Detailed ticker mapping in `research_commodity_sectors.py` COMMODITY_GROUPS dict.

---

## Why not auto-encode into BA score?

Memory rule (from FA v5/v8c failures):
> "Tier-level forward-returns test KHÔNG đủ validate FA refactor. Phải chạy `compare_ba_canonical_v4_vs_v5.py` template trên FULL_PERIOD + OOS_2024_2026 trước khi adopt."

Adding Cash_MktCap bonus or anti-commodity-peak penalty to BA score v10 would require:
1. Canonical 12y backtest (5+ hour rerun)
2. OOS 2024+ validation
3. Q1 2026 specific test
4. Tuning interaction with existing Fin/RE +10/-10 bonus
5. QWF re-snapshot

→ Better to apply as MANUAL discretion until canonical-validated. Safer for production.

Future work (if needed): convert these rules into BA score v12 patches with proper canonical validation.

## Files referenced
- `research_lh_v3_factors.py` — 43-factor IC analysis
- `research_commodity_sectors.py` — sector-cycle research
- `research_lh_v3_sector_conditional.py` — sector-conditional composite
- `research_lh_v3_c14_hybrid.py` — final hybrid attempts
- `lh_v3_factor_ic.csv` — factor IC reference
- `lh_v3_sector_cycle.csv` — sector cycle history
