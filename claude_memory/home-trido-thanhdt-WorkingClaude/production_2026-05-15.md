---
name: Production spec 2026-05-15 — BA v11 only
description: Final production decision after LH backtest research. Drop LH from v11 deployment; continue R&D separately.
type: project
originSessionId: 70c13426-2492-456b-9547-d14c8cf8fcb7
---
# Production Spec 2026-05-15 — BA v11 ONLY

**Decision**: Drop LH-system from production v11 deployment. Run 100% NAV in BA v11.
**LH status**: R&D paused, all artifacts retained, redesign required before retry.

## Why drop LH

### Original LH numbers were inflated (bug)
- v1 reported CAGR **19.85%** based on `simulate_lh_nav.py` with concentration bug
- Bug: `target_per_pos = cash / len(new_buys)` → first cohort positions got 50% NAV each
- After fix: target per position = NAV / n_positions (fixed 10% NAV)

### Corrected LH performance (with bugs fixed)
| Metric | Original (bug) | Corrected |
|---|---|---|
| 12y CAGR | 19.85% | **11.53%** |
| Sharpe | 1.16 | 1.01 |
| MaxDD | -26.66% | -18.73% |
| OOS_2024+ | 41.81% | 13.18% |

### LH only ~2.5pp alpha vs VNI — marginal value
- VNI B&H 12y CAGR ~9.0% → LH +2.5pp
- BA v11 CAGR ~17% (per memory `ba_v11_production_proposal.md`) → BA +8pp vs VNI
- LH delivers 1/3 the alpha of BA at same NAV
- Capacity advantage doesn't compensate (both scale similarly at <200B)

### v2 "Dynamic trend-following + FA" research FAILED

Tested 6 v2c variants (OR-logic exits): trend_break, trailing stop, CRISIS_LOCK, FA degradation.
**All variants underperformed v1**.

| Variant | 12y CAGR | Sharpe | MaxDD |
|---|---|---|---|
| LH v1 (corrected baseline) | **11.53%** | **1.01** | -18.7% |
| v2c_orig (TB=5d + trail + CRISIS) | 9.29% | 0.76 | -21.9% |
| v2c_no_crisis | 8.05% | 0.64 | -26.3% |
| v2c_slow_tb20 | 6.69% | 0.53 | -37.8% |
| v2c_loose_trail (35%/+50%) | 10.19% | 0.69 | -28.5% |
| v2c_pure_FA (only FA exit) | 10.46% | 0.62 | -44.9% |
| v2c_combined | 7.71% | 0.55 | -38.1% |

**Root cause**: Vietnamese stocks have high volatility — MA200 breaks frequently then recover, causing whipsaws. CRISIS_LOCK cuts winners (FPT 2018 at +33% missed subsequent 5-year 8x). Trend-following + FA-quality doesn't generate alpha here.

## BA v11 production (PROCEED)

Per memory `ba_v11_production_proposal.md` and `hybrid_v11_deployment.md`:

### Configuration
- 100% NAV in BA v11
- Script: `recommend_holistic.py` (already deployed 2026-05-15)
- v10 score (Fin/RE +10/-10) + **SV_TIGHT Fresh-Q** + **P3 overheated guard**
- 50/50 BAL+Fin/RE-max-4 + VN30_BAL split (within BA)

### Validated metrics (per memory)
- FULL 12y: CAGR **19.37%** / Sharpe **1.41** / MaxDD **-16.1%** / Calmar **1.20**
- OOS 2024-2026: CAGR **25.91%** / Sharpe **1.43** / DD **-13.1%**
- vs hybrid v11 (50/50 BA+LH): **HIGHER CAGR**, similar Sharpe

### Capacity
- 50B: optimal
- 100B: CAGR ~14% (degradation -3pp), still alpha +5pp vs VNI
- 200B: CAGR ~12%, marginal alpha +3pp
- 250B+: switch to VN30-only

## LH R&D — what to try next

Current LH design failed because:
1. **Static FA score** — doesn't capture price/regime dynamics
2. **Quarterly rebal** — too slow to react
3. **Equal-weight** — doesn't size by conviction
4. **Single-factor (FA)** — needs Quality + Value + Momentum + Low-Vol multi-factor

### Hypothesis for LH v3 (future work, not implemented)
- **Multi-factor portfolio**: Quality (ROIC, ROE) + Value (smoothed_EY) + Momentum (12M ret pos) + Low-Vol (lower NP_CV)
- **Monthly rebalance** instead of quarterly (faster signal incorporation)
- **Score-weighted sizing** (higher score → more capital)
- **Sector tilt**: rotate based on regime — overweight defensive sectors in BEAR, growth in BULL
- **Pre-screened universe**: only top 100 by liquidity + drop ICB 3353 + auto-exclude

### Required validation gates before LH v3 deployment
1. Tier-level forward IC test (3M/6M/1Y/2Y)
2. Canonical 12y backtest with realistic costs
3. Fresh-start 1Y window test (no cohort inheritance)
4. Q1 2026 BEAR survival
5. OOS_2024+ test
6. Capacity test at 50B/100B
7. Verdict gate: must show ≥ +1pp CAGR vs LH v1 AND ≥ 1.10 Sharpe at same Calmar

## Artifacts retained (LH R&D)

LH v1 scripts (do NOT use for production):
- `score_fa_lh.py` — FA scoring with v8c_final + pre-sales
- `simulate_lh_nav.py` — simulator (bugs fixed)
- `simulate_lh_v2.py` — dynamic trend-following variant
- `recommend_lh.py` — live picks (kept for future testing)
- `run_lh_matrix.py`, `tests_option_c.py`, `tests_growth_ta_filters.py`, etc. — research scripts

Memory files (mark as R&D, not deployed):
- `fa_long_hold_spec.md` — LH design history (annotate "NOT FOR PRODUCTION")
- `hybrid_v11_deployment.md` — annotate "REPLACED by BA-only"

## Lessons learned

1. **Tier-level performance ≠ portfolio performance** — A-tier picks median return doesn't translate directly to NAV (sizing, liquidity, slippage matter)
2. **FA signals LAG market** — quarterly reports cannot anticipate market peaks (4+ investigations confirmed)
3. **Vietnamese market has weak trend persistence** — MA200/MA50 breaks frequent, whipsaws kill trend-following
4. **Simulator bugs inflate results** — [REDACTED] validate sizing logic on fresh-start before reporting
5. **BA-system v10/v11 is the production winner** — TA momentum + FA tier + regime overlay outperforms pure FA
6. **Diversification has diminishing returns when one leg is much stronger** — 50/50 hybrid was actually pulled down by weaker LH leg

## Deployment action

✅ **Today (2026-05-15)**: BA v11 already deployed via `recommend_holistic.py`. Run normal daily operations:
```
python recommend_holistic.py
# Output: holistic_2026-05-15.csv + ba_book_bal_*.csv + ba_book_vn30_*.csv
# Manual: review picks, execute trades for BAL + VN30 books
```

✅ **Monitoring**: Quarterly `quarterly_walkforward.py` snapshot (existing BA-only QWF, not hybrid)

⏸️ **LH paused**: revisit when ready to design v3 (multi-factor, monthly rebal)
