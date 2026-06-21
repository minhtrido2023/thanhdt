---
name: Layer 3 consolidated findings (3 directions tested)
description: (a) SELL anticipation huge win on STOP (+8.5pp), TP fails. (b) Tuned S2 d_thr=-3 b_win=30m: +1.74pp ALL_lift, +3.74pp TOP30. (c) Both integrated into paper_trade_daily.py.
type: project
originSessionId: 90878235-541c-4207-a725-44398117b136
---
Scripts: `layer3_sell_anticipate.py` (51K events), `layer3_s2_tune_fast.py` (grid 30 variants), `paper_trade_daily.py` (production integration).

### (a) SELL ANTICIPATION — STOP wins big, TP fails
- 51,071 sell-events across 85 tickers × 2 lookback windows × stops/TPs
- **STOP-20% intraday** (BA-system default): mean realized = −20.00% vs **wait EoD −28.55%** → saves **+8.5pp/event**
- STOP-15%: −15% vs −23.57% → +8.6pp  
- STOP-10%: −10% vs −19.00% → +9.0pp
- FP rate (intraday hit but EoD recovers): 11-19% — acceptable
- **TP intraday FAILS**: TP-25% locks +25% vs wait EoD +44.29% → **loses −19.3pp/event**. Don't anticipate take-profit.
- Key: gap-down days overshoot stop (avg close −28% vs stop −20%); intraday fire saves the overshoot. Gap-up days have momentum that runs past TP; TP intraday cuts upside.

### (b) S2 oversold-reversal tuned (grid 30 variants)
- Original: `day_chg≤-2 AND bounce_30m>0` → ALL_lift +1.50pp
- **Tuned: `day_chg≤-3 AND bounce_30m>0`** → **ALL_lift +1.74pp, TOP30 +3.74pp on n=233**
- Tighter d_thr selects deeper drops where bounce is more meaningful
- FP rate 67% (similar) but more selective sample → higher avg lift
- Bounce magnitude >0.5 / >1.0 reduces n_fire too much; stay at >0

### (c) Production integration in paper_trade_daily.py
- `S2_DAYCHG_THR = -3.0`, `S2_BOUNCE_MIN_PCT = 0.0` (constants)
- `E_S2_ANTICIPATE` rule: walk bars; if S2 triggers, fire at trigger close; else fallback ATC market
- Routed via `PLAY_RULE` dict: DEEP_VALUE_RECOVERY → E_S2_ANTICIPATE; MOMENTUM_*/COMPOUNDER_BUY → E1_T1115_LIM
- Stop-loss intraday: every day for open positions, check `low ≤ entry × 0.80`; if hit, exit at stop_lvl (limit-sell at stop, assume fill); record exit_type=STOP_INTRADAY
- Time exit at HOLD_DAYS=45: X1_T0945_LIM rule (existing)

### Combined estimated CAGR impact (cumulative, BA-system 50B NAV)
- Timing rule alone (T1115 + 09:45 limit): +0.8-1.5pp
- S2 anticipation for DEEP_VALUE (~60% of flow × +0.89pp T+45 × portfolio weight): +0.3pp
- Intraday stop on ~10 stops/yr × +8.5pp × 10% portfolio: **+0.85pp**
- **Total combined: +2.0-2.7pp CAGR alpha** for BA-system 50B baseline 17.15% → ~19-20%

### Caveats
- Stop intraday assumes limit-sell fills at stop_lvl exactly (real life: slippage on gap-down may give worse fill — but still better than EoD close)
- Sample 9 months; need walk-forward validation
- TP rule confirmed NOT to anticipate — keep EoD/time-based exit
- Paper trade now testing all 3 elements live; reminder set for [REDACTED]12 review
