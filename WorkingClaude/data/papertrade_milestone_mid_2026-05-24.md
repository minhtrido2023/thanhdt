# Paper-Trade MILESTONE Report — MID

*Generated: 2026-05-24*
*Window: 2026-04-01 → 2026-05-24* (53 days)

## A. Realized vs Backtest expectation

| Sys | Name | Realized CAGR | Backtest FULL/OOS | Realized DD | Backtest DD | Realized Sharpe | Backtest Sharpe | Verdict |
|---|---|---:|---:|---:|---:|---:|---:|---|
| **V1** | V11 Song Sinh + TQ34b | +26.40% | 21.14% / 28.88% | -2.41% | -17.82% | +2.39 | 1.45 | 🟢 |
| **V2** | V12 Âm Dương + TQ34b | +7.52% | 21.96% / 23.22% | -1.43% | -14.39% | +1.82 | 1.65 | 🟡 |
| **V3** | V12 Âm Dương + LIVE Tinh Tế | +15.87% | 22.00% / 23.00% | -1.82% | -14.50% | +1.51 | 1.65 | 🟢 |
| **V4** | V12.1 Ensemble (M1+M3r AND-HOLD) | +26.40% | 24.70% / 31.92% | -2.41% | -15.43% | +2.39 | 1.76 | 🟢 |
| **V5** | V4 + Kelly Q2 NEUTRAL{1.0} | +46.15% | 25.71% / 36.16% | -2.46% | -16.93% | +3.51 | 1.70 | 🟢 |

## B. Monthly returns per system

| Month | V1 | V2 | V3 | V4 | V5 |
|---|---|---|---|---|---|
| 2026-04 | +3.16% | +1.58% | +3.15% | +3.16% | +4.62% |
| 2026-05 | -0.03% | -0.61% | -1.16% | -0.03% | +0.47% |

## C. V5 (Kelly Q2 overlay) vs V4 (baseline ensemble) — FINAL VERDICT

- Realized ΔRet:    **+1.99pp**  (backtest expected: +1pp FULL / +4pp OOS)
- Realized ΔDD:     **-0.06pp**   (backtest expected: -4pp wider; gate: ≥ -6pp)
- Realized ΔSharpe: **+1.13**     (backtest expected: ≈ flat)
- Realized ΔCalmar: **+7.77** (backtest expected: -0.5)

**Final verdict: 🟢 **GREEN — Q2 alpha confirmed, deploy to production****

## D. Trade activity (transactions count)

| Sys | Total tx | Stock tx | ETF tx | ETF turnover (B) |
|---|---:|---:|---:|---:|
| **V1** | 57 | 27 | 30 | 63.55B |
| **V2** | 46 | 33 | 13 | 28.32B |
| **V3** | 38 | 28 | 10 | 37.12B |
| **V4** | 57 | 27 | 30 | 63.55B |
| **V5** | 54 | 28 | 26 | 94.96B |

## E. Recommendation

**Ranking by realized Sharpe (live data):**
  1. **V5** — CAGR +46.15% / Sharpe +3.51 / DD -2.46%
  2. **V1** — CAGR +26.40% / Sharpe +2.39 / DD -2.41%
  3. **V4** — CAGR +26.40% / Sharpe +2.39 / DD -2.41%
  4. **V2** — CAGR +7.52% / Sharpe +1.82 / DD -1.43%
  5. **V3** — CAGR +15.87% / Sharpe +1.51 / DD -1.82%

**Lead candidate after mid milestone: V5**

→ Continue paper trade through Aug 31, monitor V5 vs V4 gap.
