---
name: Layer 3 intraday backtest findings
description: 6,742-event factor IC study (top30 × 225 sessions, Aug 2025-May 2026) — validates which intraday 15m features actually predict forward returns; some contradict current Layer 3 weights
type: project
originSessionId: 90878235-541c-4207-a725-44398117b136
---
Backtest scripts: `layer3_backtest.py`, `layer3_analyze.py`, `layer3_deep_dive.py`. Output: `layer3_backtest_eventsB.csv` (6,742 events), `layer3_factor_ic.csv`.

**Why:** Test whether intraday 15m features add alpha to BA-system EoD decision and whether current Layer 3 score formula is well-calibrated.

**Key findings (Spearman IC, p < 1e-10 unless noted):**
- **Strongest overnight predictors:** day_chg +0.145, pct_above_vwap +0.130, macdh +0.099, rsi15m +0.082, pos_in_range +0.086
- **Surprises (contradict current Layer 3 weights):**
  - **vol_burst NEGATIVELY correlated** with overnight return (IC −0.093). Current Layer 3 rewards burst ≥1.5; should be neutral or contrarian.
  - **rsi15m mean-reverts at 20d** (IC −0.060). Current Layer 3 rewards RSI 50-75; works overnight only, hurts longer hold.
  - **late_chg NEGATIVE at 20d** (IC −0.080). Late-day strength predicts WORSE 20d return.
- **Decay:** signal concentrated at overnight + 5d, near-zero at 10-20d. Layer 3 is an entry-timing filter, not an alpha source for BA-system's 45-day horizon.
- **Composite score IC degraded by RSI/vol_burst:** original score ret_5 IC = 0.017; "alt-score" (drop RSI reward, invert vol_burst, narrow trend) = 0.028 + monotonic quintile lift.

**Production-ready signals (validated on 6,742 events):**
- **Strong combo (n=197):** pct_above_vwap≥60 & day_chg∈[-1%,+2%] & vol_burst<1.5 & macdh>0 → ret_5 +0.81% (hit 53.3%) vs baseline +0.33% (hit 46.2%). +0.49pp lift, +7.1pp hit rate.
- **Hard avoid (n=1,522):** pct_above_vwap<40 & day_chg<-1% → ret_5 +0.11% (hit 45.9%). Skip these entries.

**How to apply:** When revising Layer 3 score formula, (1) drop the RSI 50-75 reward, (2) invert vol_burst (penalize ≥2.0, reward only 1.0-1.5 with trend), (3) demote late_chg penalty, (4) keep pct_above_vwap and day_chg as main inputs. Use the "Strong combo" as a GO_STRONG override and "Hard avoid" as a HARD SKIP. Track A on 18 actual BUYs was too small to validate (n=2 GO_STRONG both bad — DEEP_VALUE_RECOVERY picks naturally show AVOID-type intraday because system buys weakness).
