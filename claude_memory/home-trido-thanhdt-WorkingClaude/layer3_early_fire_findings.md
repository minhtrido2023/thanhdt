---
name: Intraday early-fire anticipation backtest
description: Test firing BUY signal khi đủ điều kiện intraday vs chờ EoD. 17,657 events qua 3 signal types × 3 segments × 3 horizons. Verdict mixed — chỉ S2 oversold-reversal work cho BA-system 45d hold.
type: project
originSessionId: 90878235-541c-4207-a725-44398117b136
---
Script: `layer3_early_fire.py` (computation), `layer3_early_fire_extend.py` (horizon breakdown). Output: `layer3_early_fire_events.csv`.

**Setup:** Cho mỗi (ticker, session) trong panel 85 ticker × ~225 phiên, walk forward 15m bar-by-bar. Tìm bar đầu tiên signal True → "EARLY_FIRE". Check EoD signal status (TP/FP).

**3 signals tested:**
- S1_STRONG_COMBO: `pct_above_vwap>=60 AND day_chg∈[-1,+2] AND MACDh>0` (momentum)
- S2_OVERSOLD_REV: `day_chg<=-2 AND close > 30min-ago close` (reversal/bounce)
- S3_VOL_BREAKOUT: `day_chg>=+1 AND vol_burst>1.5` (mostly noise — TP=0 TOP30)

**Fire-time distribution:** Hầu hết signal fires sớm: S1 mostly 09:30-09:45 (5,326/10,967). S2 spreads. Cho thấy "tickers cận triggered" thực sự appear sớm trong phiên.

**KEY result — lift theo horizon (Early vs WaitEoD mean return per trade):**

S1 STRONG_COMBO:
- TOP30 T+5: **+1.33pp** ✓ | T+20: +1.42pp ✓ | T+45: **−1.39pp ❌ INVERTS**
- MIDCAP T+5: −0.11pp | T+45: −1.63pp ❌
- PENNY T+5: +0.28pp | T+45: −1.09pp ❌

S2 OVERSOLD_REV (BA-system DEEP_VALUE-relevant):
- TOP30 T+5: **+1.43pp** | T+20: +1.47pp | **T+45: +0.89pp** ✓ stable
- MIDCAP T+5: +0.62pp | T+45: +0.13pp
- PENNY T+5: +1.13pp | T+45: +0.67pp ✓

**Verdict for BA-system (45d hold):**
- ❌ S1 momentum anticipation: TP+FP outperforms TP-only at T+5/20, but **inverts at T+45** (FP signals mean-revert by 45d)
- ✓ S2 oversold-bounce anticipation: **+0.89pp lift at T+45 on TOP30, stable across horizons**. Fit cho DEEP_VALUE_RECOVERY play_type
- ❌ HYBRID (fire early + cut on FP same-day): consistently worst — locks intraday whipsaw, misses recovery

**Why momentum (S1) fails at 45d:** FPs (signal fires intraday rồi invalidated at close) actually outperform TPs at T+5 (FP avg +1.23%, TP avg +0.85%) but underperform at T+45. Intraday momentum signal có short-horizon predictive value, decays to noise tại horizon dài.

**Production rule (proposed):**
- For BA-system DEEP_VALUE_RECOVERY pick monitoring: monitor S2 intraday → fire BUY when triggers (T1300+ best fire time per fire-time analysis)
- For MOMENTUM picks: stick with EoD decision + T1115 limit (S1 anticipation not safe for 45d hold)
- Hybrid approach: T+45 holdings should use S2 only; short-term tactical trades (5-20d) can use S1

**Caveats:** Signal definitions are proxies, not BA-system's actual condition. Real BA-system filter has FA tier + 5-state regime that we don't replicate intraday. To productionize: would need re-implement BA-system filter on intraday data (non-trivial for FA components).
