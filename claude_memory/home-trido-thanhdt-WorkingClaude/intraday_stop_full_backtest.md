---
name: Intraday-low stop — full 12-year backtest A/B
description: Embedded daily-Low stop in simulate_holistic_nav.py. 12 years × 255 trades for BAL_8pos strategy. CONFIRMS small-sample finding: intraday stop loses -4.31pp CAGR. 13 extra FP stops over close-confirmed. Decision: KEEP close-based stop.
type: project
originSessionId: 90878235-541c-4207-a725-44398117b136
---
Scripts: `simulate_intraday_stop_compare.py` (driver), modified `simulate_holistic_nav.py` (added `lows` + `stop_mode` params). Cache: `intraday_stop_lows.csv` (1.26M rows, 496 tickers). Outputs: `intraday_stop_compare.csv` + per-strategy `intraday_stop_{nav,trades}_*.csv`.

**Method:** Used daily Low (not synthetic intraday) as proxy for "did price touch stop intraday?". This is the standard daily-resolution approach — no fake data. `stop_mode="INTRADAY_LOW"` fires stop when `Low[D] ≤ entry × (1+stop_loss)` with fill at stop_lvl. Baseline `stop_mode="CLOSE"` fires when `Close[D] ≤ stop` with fill at close.

**BAL_8pos full 12-year results:**

| Metric | CLOSE baseline | INTRADAY_LOW | Δ |
|---|---|---|---|
| CAGR | 24.70% | 20.40% | **−4.31pp** ❌ |
| Sharpe | 1.228 | 1.077 | −0.151 |
| MaxDD | −32.72% | −30.94% | +1.78pp (slightly better) |
| WinRate | 60.0% | 56.7% | −3.3pp |
| Trades | 255 | 263 | +8 |
| Stop fires | 41 (close) | 54 (intraday) | **+13 FP stops** |
| TIME exits | 206 | 201 | −5 |

**MEGA_3pos (high conviction, smaller sample):**
| Metric | CLOSE | INTRADAY_LOW | Δ |
|---|---|---|---|
| CAGR | 12.22% | 12.93% | +0.72pp |
| Sharpe | 0.753 | 0.613 | −0.139 |
| MaxDD | −30.21% | −27.57% | +2.63pp |
| Stop fires | 3 | 3 | same |

For MEGA, 3 stops fire in both modes (price decisively breaks; close confirms). Just different fills (stop_lvl vs close). Slight CAGR gain from saving overshoot, but Sharpe worse.

**Key finding:** ~24% FP rate at strategy level (vs 17% universe, 40% small-18-event). The 13 extra stops in BAL are predominantly false alarms — price intraday-low touches stop but recovers by close. Re-entry friction + stopping out of recoveries causes −4.31pp CAGR drag.

**Scaling math:** 41 TP × ~5pp save vs 13 FP × ~10pp loss + re-entry friction → net −4.31pp CAGR confirmed. NOT worth the −1.78pp MaxDD improvement.

**Final production decision (CONFIRMED across 3 sample sizes):**
- Universe synthetic (51K events): said +8.5pp/event ⚠️ MISLEADING
- BA-system backfill (18 events): said −5.4pp/event
- Full 12-year embed (255 trades): says **−4.31pp CAGR**
- **Conclusion: KEEP close-based stop in production. KEEP `STOP_MODE = "SHADOW"` in `paper_trade_daily.py` (log but don't exit).**

**Methodology lesson:** When intraday stop fires on close-confirmed cases, fill saves overshoot (gap-down close > stop). But on FP cases (intraday wick recovers), stopping out crystallizes loss the close-based stop would have avoided. BA-system's value-buying flow has FP rate too high to make intraday stop profitable.

**Re-runnable:** `python simulate_intraday_stop_compare.py` (cached Low data, takes ~2 min).
