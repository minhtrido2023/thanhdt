---
name: Layer 3 timing rules — limit-fill backtest results
description: Validated 7 entry × 4 exit strategies on 9,983 events (TOP30+MIDCAP+PENNY) + 22 real BA-system BUYs. Key finding: T1115_LIM beats all market-order rules across segments because limit avoids market impact.
type: project
originSessionId: 90878235-541c-4207-a725-44398117b136
---
Scripts: `layer3_backtest_rules.py` (universe), `layer3_backtest_real_buys.py` (BA-system actual). Outputs: `backtest_entry.csv`, `backtest_exit.csv`, `backtest_combined.csv` (159,712 combo rows), `backtest_real_buys.csv`.

**Setup:** 9,983 (ticker, session) events split by liquidity segment. Limit-fill mechanics: limit @ slot_close fills if any subsequent bar's low ≤ limit (buy) or high ≥ limit (sell); otherwise fallback to ATC market with sqrt-impact slippage. Position size: TOP30 5B / MIDCAP 1B / PENNY 0.5B VND.

**Key result — per-trade lift at T+45 (after 0.2% TC, vs E0+X0 baseline):**

| Segment | Baseline | Best combo | Lift |
|---|---|---|---|
| TOP30 | +0.137% | E1_T1115_LIM + X1_T0945_LIM | **+0.902pp** |
| MIDCAP | −3.680% | E1_T1115_LIM + X1_T0945_LIM | **+1.183pp** |
| PENNY | −7.102% | E1_T1115_LIM + X1_T0945_LIM | **+1.734pp** |

**Surprise that overrode the earlier segment-aware rule:**
- Original rule (E5_SEG_AWARE) said MIDCAP/PENNY should use ATC market because slippage at 11:15 was estimated 0.22%
- Backtest shows E1_T1115_LIM beats E5_SEG_AWARE for MIDCAP (−2.214 vs −2.407) and PENNY (−5.019 vs −5.435)
- Reason: **limit orders avoid market impact entirely**; the slippage model only applies to market orders
- Miss rate at T1115 limit: TOP30 0.03%, MIDCAP 0.4%, PENNY 1.6% — limits fill almost [REDACTED]

**On 22 real BA-system BUYs (mostly DEEP_VALUE_RECOVERY plays):**
- Baseline E0+X0: +11.807%
- Best: **E3_ATC_MKT + X1_T0945_LIM: +12.741%** (lift +0.934pp)
- E1_T1115_LIM + X1_T0945_LIM: +12.098% (lift +0.291pp)
- **DEEP_VALUE plays prefer ATC entry** (buy after intraday selling) over T1115 (lunch dip)
- Sample n=22 is small; lift magnitude noisy but direction consistent with play-type logic

**Final production rule (play-type aware):**
- BUY MOMENTUM_*: limit @ 11:15 close, fallback ATC market
- BUY DEEP_VALUE_RECOVERY/COMPOUNDER: market @ ATC
- SELL all segments: limit @ 09:45 close, fallback next-day OPEN market
- Limit miss is rare (<2%), fallback rarely triggers

**Expected BA-system NAV impact (50B, hold 45d, 8 turns/yr/position):**
- Per-trade alpha: +0.3 to +1.7pp (segment-dependent)
- Conservative annual CAGR alpha: **+0.8 to +1.5pp** (current 17.15% baseline → ~18-19%)
- Sharpe improvement marginal (alpha is on entry timing, doesn't reduce volatility)

**Caveats:** 9-month sample (Aug25-May26) includes 1 BEAR quarter; limit fill rate >98% in sample but live could differ if BA-system flow becomes signal-leaked; T+45 close-to-close horizon assumed, real BA-system has 3-day ramp not modeled.
