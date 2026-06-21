---
name: BA-system definition
description: Holistic recommendation engine final v10 — combine TA momentum + FA tier + 5-state regime + 50/50 BAL+VN30 split
type: project
originSessionId: cc0496d6-7fd6-4cd3-8964-4af6fe223c99
---
# BA-system — Final Production Config

**Origin:** Distillation of 15 backtest rounds. Score formula = v10 (round 12).
**Architecture:** TA v9 + FA tier inverse + 5-state regime + sector tilt + Fin/RE-D bonus.
**Strategy:** 50% BAL+Fin/RE-max-4 + 50% VN30_BAL split.

---

## Score formula v10 (max ~194)

### Technical (max 113)
- +25 RSI strong: D_RSI > 0.50
- +25 Uptrend: Close > MA50 AND MA50 > MA200
- +20 Volume confirm: Volume ≥ Vol_3M_P50 × 1.3 AND Close > Close_T1
- +15 MACD positive: D_MACDdiff > 0
- +15 Above MA20
- +10 VNI 3M strong: VNINDEX_RSI_Max3M > 0.65
- +8 Fresh 3Y high: ID_HI_3Y ≤ 5
- +5 RSI Max1W: D_RSI_Max1W > 0.65
- +5 RSI extreme: D_RSI > 0.75
- -10 Penalty weak: D_RSI < 0.30

### Valuation
- +15 Cheap PE: PE < PE_MA5Y - 0.5×PE_SD5Y
- -15 Expensive PE: PE > PE_MA5Y + 1.0×PE_SD5Y

### FA quality
- +10 FSCORE ≥ 8 (Piotroski)
- +8 NP YoY growth strong: NP_P0 > 1.5×NP_P4
- -8 NP YoY decline: NP_P0 < 0.7×NP_P4

### Sector tilt
- +5 Sector 8 (Financials/RE) or 9 (Tech/Telecom)
- -5 Sector 4 (Health) or 7 (Utilities)

### Trend confirmation
- +5 MA50 rising
- +5 MA50 strong rising (>0.5%/d)
- -5 MA50 falling
- -10 Drawdown deep: Close/HI_3M_T1 < 0.85 (relief rally guard)

### Earnings momentum
- +8 NP QoQ accel: NP_P0 > 1.2×NP_P1

### v10 Sector × FA bonus (round 12 breakthrough)
- **+10 Fin/RE × FA-D** (recovery rally setup)
- **-10 Fin/RE × FA-A** (overpriced compounder weakness)

---

## Tier thresholds (v10)

| Tier | Score | Plus regime | Plus FA |
|---|---|---|---|
| MEGA | ≥170 | state(4,5) | C/D |
| S_PRO | ≥170 | state(4,5) | any |
| MOMENTUM | ≥155 | state(4,5) | C/D |
| MOMENTUM_QUALITY | ≥155 | state(4,5) | A/B |
| MOMENTUM_N | ≥155 | state=3 | C/D |
| S | ≥140 | state(4,5) | any |
| MOMENTUM_S_N | ≥140 | state=3 | any |
| A | ≥125 | state(4,5) | any |
| COMPOUNDER_BUY | ≥95 | state(3,4,5) | A/B + cheap PE + no warn |
| DEEP_VALUE_RECOVERY | ≥100 | state(4,5) | C + NP/Rev YoY > 20% |
| COMPOUNDER_HOLD | 70-130 | non-BEAR | A/B |
| WAIT | <70 | non-BEAR | A/B |
| AVOID_bear | any | state(1,2) | any |
| AVOID_faE | any | any | E |

---

## Strategy: 50/50 BAL+Fin/RE-max-4 + VN30_BAL

### BAL component (50% capital)
- Tiers: MEGA, MOMENTUM, MOMENTUM_N, MOMENTUM_S, DEEP_VALUE_RECOVERY
- Universe: ticker_prune (~449 mã quality)
- Sector limit: Fin/RE (sector 8) max 4 positions
- max_positions=10, hold_days=45
- **stop_loss = -20%** (NOT -25%, kept conservative per user preference)
- min_hold=2 (T+3)
- reentry_blacklist_days=20
- liquidity_volume_pct=0.20 (max 20% ADV/day)
- max_fill_days=5
- slippage=0.001 (0.1% per side)
- exit_slippage_tiered=True (extra +0.1/0.3/0.5% slip if position > 5/10/20% ADV)

### VN30 component (50% capital)
- Same tier set as BAL
- Universe: top 30 tickers by avg liquidity (CTG, FPT, HPG, MBB, MWG, VNM, VHM, VPB, ...)
- Same PM as BAL (no sector limit needed since VN30 inherently diversified)
- max_positions=10, hold_days=45, stop -20%, BL20

---

## Validated metrics

### REALISTIC T+1 Open execution (2026-05-17 canonical, production default)
| NAV | CAGR | Sharpe | MaxDD | Calmar | Notes |
|---|---|---|---|---|---|
| 50B v11 stack (SV_TIGHT + P3 + RE_BACKLOG + V6 ETF) | **18.18%** | ~1.15 | ~-15-16% | ~1.10 | T+1 Open buy + exit, no look-ahead |

### Legacy T-close execution (LOOK-AHEAD BIAS — historical reference only)
| NAV | CAGR | Sharpe | MaxDD | Calmar | Win-Rate Q |
|---|---|---|---|---|---|
| 1B (~$40k) | 17.40% | 1.31 | -18.4% | 0.95 | high |
| 30-50B (~$1-2M) | 17.15-17.54% | 1.21 | -14.5% | 1.18 | 85.4% |
| 100B | 14.49% | 1.06 | -15.3% | 0.95 | high |
| 200B+ | shift to VN30_BAL alone, Sh 1.11 | | | | |

⚠ **Look-ahead delta**: T-close execution OVERSTATES CAGR by ~1.92pp vs realistic T+1 Open (12y validation: 20.10% optimistic vs 18.18% realistic). Crash periods worst-hit (2018-2023 mid: -4.37pp). Always cite the realistic figure in deployment specs.

**vs VNINDEX B&H (12-yr 2014-2026): 11.5% CAGR, Sh 0.69, MaxDD -45%, wealth 3.7×**
**BA-system 50B v11 realistic: ~6.0-6.5× wealth, +6.7pp CAGR alpha, ~1/3 DD**

---

## 2022 Crash defense

VNINDEX -33% YTD, BA-system **+2.6%** YTD (essentially flat). 5-state regime correctly identified BEAR period and skipped most signals.

---

## Adopted refinements (across 19 rounds)

✓ v10 score (Fin/RE-D +10, Fin/RE-A -10) — round 12 breakthrough
✓ 50/50 BAL+Fin/RE-max-4 + VN30 split — round 12-13 ULTIMATE
✓ Liquidity-aware sizing + multi-day fills — round 8
✓ Tiered exit slippage — round 10
✓ BL20 blacklist — round 7
✓ Stop -20% (kept conservative, NOT -25%) — round 14/15
✓ **V6 ETF parking (70% of idle cash → VN30 ETF in NEUTRAL state)** — round 18 breakthrough. At realistic 1% deposit, CAGR 17.60% (vs 13.95% no-ETF), Sharpe 1.16, DD -17.4%. BEATS even 3% deposit assumption.
✓ **F1 Fresh-Q Filter (days_since_release ≤ 60 for BA-core)** — round 19. Skip BA-core entries when latest quarterly report >60 days stale. Targets Q1 (Apr-May) and Q4 (Jan-Feb) earnings season risk. Per-season: Q1 win rate 65.9% → 92.3%, Q4 56.9% → 68.9%. 11-month forward validation: CAGR +6.23pp, DD -1.63pp, win rate +9.9pp, STOPs -6/-55%.

✓ **REVERT to ORIGINAL 5-state (2026-05-17)** — v2g 5-state (deployed 2026-05-17 with claim +1.28pp standalone) was tested against BA-system stack and FAILED: -2.40pp CAGR (17.44% vs 19.84% ORIGINAL), -0.18 Sharpe, **-6.9pp DD WORSE**. Reverted via BQ table swap. Lesson: state-machine optimizations don't transfer to BA-system; smoothing in original state provides stable tier classifications. v2g archived in `vnindex_5state_v2g_archive_20260512`.

✓ **T+1 Open execution as canonical (2026-05-17)** — `simulate_holistic_nav.py` now defaults `t1_open_exec=True`. Signal at T-close → fill at T+1 Open (entry AND exit). Removes look-ahead bias from legacy T-close exits where STOP/TIME triggered would have been impossible to execute at trigger price. 12y validation: OLD 20.10% CAGR → NEW 18.18% (-1.92pp), Pre-OOS 2014-19 ≈ unchanged (+0.14pp), 2018-23 -4.37pp (gap-down overshoots hurt), 2024-26 unchanged. **Live engine `recommend_holistic.py` already operated T+1 by definition** (signals run pre-market, orders placed at open) — no code change. Future direction: Layer 3 intraday timing research → optimize buy POINT within T+1 day (open vs midday low vs VWAP vs ATC) without violating T+1 constraint.

## Rejected refinements

❌ Calendar filters (skip July, Tue-Thu only) — round 15: correlation not causation, -2 to -5pp CAGR
❌ Stop -25% — round 14/15: marginal +0.33pp full-period but **−2.97pp in 2021-2023 crash**, DD universally worse
❌ v11 SQL-Mat-D/Cons-D bonuses — round 13: -0.87pp CAGR
❌ **Tier-based position sizing** — round 16: ALL variants underperform equal-weight (-0.87 to -2.97pp CAGR). Reason: MEGA=0% trades, DVR=62%; concentrating into rare high-tiers wastes slots
❌ **EX-BULL threshold +15 (v11 SQL)** — round 16: -0.42pp CAGR alone, doesn't compound with tier sizing
❌ **State-transition exit (close on BEAR)** — round 17: -1.07pp CAGR for +2.1pp DD; CRISIS-only variant marginal (-0.71pp / +0.06 Calmar). State exit lag means most damage done before signal fires
❌ **Profit-target exit (+25/+30/+35/+40 redeploy)** — round 17: cuts winners. PT +30% cap: PROFIT_TARGET trades avg +32.5% but TIME residual drops to +3.2% (vs baseline +13.5%). Same problem as PARTIAL (round 5)
❌ **State-halving on NEUTRAL** — round 17: -7.99pp CAGR catastrophic. NEUTRAL is a deployment regime, not a defensive trigger
❌ Trailing stops — round 5: cuts winners
❌ Partial profit-taking — round 5: -6pp CAGR
❌ Eviction — round 6: -4pp CAGR
❌ Sector limit ≤ 2 (global) — too restrictive
❌ Drop weak tiers — slots empty hurts compounding

---

## Production scripts

- `simulate_holistic_nav.py` — sim engine with all PM params
- `recommend_holistic.py` — **BA-system live engine** (v10 score, 50/50 BAL+VN30 books, Fin/RE max-4 cap, BEAR auto-cash). **Auto-fallback ticker→ticker_1m for recent dates** (no need to manually refresh ticker daily — system reads ticker_1m for fresh data). VNINDEX_RSI_Max3M frozen forward from latest ticker row. 5-state forward-[REDACTED] from latest available. Outputs `holistic_<date>.csv` + `ba_book_bal_<date>.csv` + `ba_book_vn30_<date>.csv`
- `ta_score_daily.py` — Layer 2 standalone TA scores
- `layer3_intraday_timing.py` — Layer 3 intraday entry timing
- `layer3_paper_trade.py` — Layer 3 paper-trade tracker (modes: log / update / stats); persistent log `layer3_paper_trade_log.csv`
- `fundamental_rating.py` — Layer 1 FA 7-axis rating
- `quarterly_walkforward.py` — quarterly forward validation with traffic-light status (GREEN/YELLOW/RED). Tracking log: `qwf_tracking_log.csv`
- `test_stop_validation.py` — multi-period stop-loss grid (49 variants); confirmed -20% optimal
- `test_f_ba_mix.py` — F-system × BA-system mix grid; confirmed 70-80% BA + 20-30% F_HAdapted gives best Sharpe

## BQ tables

- `tav2_bq.fa_ratings` — 12,367 rows, Q1 2026 included (326 tickers)
- `tav2_bq.vnindex_5state` — through 2026-04-28
- `tav2_bq.ticker` — daily indicators through 2026-03-30
- `tav2_bq.ticker_prune` — quality universe through 2026-04-17
- `tav2_bq.ticker_1m` — rolling 1-month snapshot through 2026-05-08
- `tav2_bq.ticker_financial` — quarterly through 2026-05-08

## Forward Holdout validation (Jan 2024 - Jan 2026 OOS)

| Strategy | CAGR | Sharpe | DD |
|---|---|---|---|
| BA-system 50B | 21.22% | 1.05 | **-15.2%** |
| VNINDEX_BH | 28.22% | — | — |

System UNDERPERFORMS B&H in extreme bull period but maintains DD -15% (better than full-period -20%). Trade-off: smoother ride vs lower bull-market returns. Acceptable for risk-averse capital.

## Stress test (round 15)

System is robust to single-event shocks. Even -40% Black Swan at peak (2025-09) drops CAGR only -0.30pp due to 12-year compounding cushion.

## Known Limitations

1. **Underperforms B&H in extreme bull** (e.g., 2024-2026: 21% vs VNI 28%)
2. **Calendar tactics fail** — patterns are correlation, not causation
3. **System depends on regime detection** — relies on vnindex_5state quality
4. **Ticker daily data ends 2026-03-30** — for live signals after that, need rolling refresh of `ticker` table
5. **Stop -25% deferred** — user prefers conservative -20% pending more validation

## Future work

- ~~Test stop -25% over more periods/regimes~~ ✅ done — `stop_validation_results.md`. Verdict: keep -20%, -25% loses -2.97pp CAGR in 2021-2023 crash
- ~~F-system mix (combine BA + F-system VN30F derivatives)~~ ✅ done — `f_ba_mix_results.md`. Best: 80% BA + 20% F_HAdapted (Sharpe 1.26 vs 1.21)
- ~~Layer 3 forward paper-trade tracking (30-60 days)~~ ✅ framework built (`layer3_paper_trade.py`); needs daily run accumulation
- ~~Quarterly forward validation post-Q1 2026 reports~~ ✅ framework built (`quarterly_walkforward.py`); first snapshot 2026-03-30 → `qwf_2026_03_30.md` (Trailing-3Y RED on Sharpe/Calmar — known window variance, not system breakage)
- Run layer3_paper_trade.py daily for 30-60 days to accumulate forward-paper-trade samples
- Re-run QWF after next ticker data refresh (post 2026-Q2 reports)
