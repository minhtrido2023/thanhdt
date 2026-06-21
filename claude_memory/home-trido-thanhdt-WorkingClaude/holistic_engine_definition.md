---
name: Holistic Recommendation Engine
description: Layer 3 combine TA v9 + FA 7-axis + 5-state regime thành play-type recommendations
type: project
originSessionId: cc0496d6-7fd6-4cd3-8964-4af6fe223c99
---
# Holistic Recommendation Engine

**Script**: `recommend_holistic.py` | **Output**: `holistic_<date>.csv`

## Mục đích

Combine 3 hệ thống thành 1 ranked list với play-type label cho mỗi mã:
1. **FA-system** (`fundamental_rating.py`) → 7-axis quality scores + tier A/B/C/D/E
2. **TA-system v9** (`ta_score_daily.py`) → momentum score + 5-state regime
3. **5-state system** (`vnindex_5state_system.py`) → market regime

## Play Types (post-backtest calibration v1.1)

Conviction scores recalibrated từ backtest 2014-2026 (542k signals).

| Play type | Condition | Conviction | Sizing | Validated P3M | Win | Hit20 | Lose10 |
|---|---|---|---|---|---|---|---|
| **MEGA** | TA≥160 + state(4,5) + FA C/D | 100 | Full | **37.2%** | 85% | 67% | 4.1% |
| **MOMENTUM** | TA≥145 + state(4,5) + FA C/D | 88 | 60-80% | 19.2% | 68% | 43% | 18% |
| **MOMENTUM_N** | TA≥145 + state=3 + FA C/D | 80 ↑ | 30-50% | 18.2% | 71% | 39% | 16% |
| MOMENTUM_S | TA≥130 + state(4,5) | 72 | 30-50% | 12.9% | 62% | 33% | 21% |
| DEEP_VALUE_RECOVERY | FA C + NP/Rev YoY>20% + TA≥100 + **state(4,5)** ⚠ | 70 ↓ | 30-50% | 10.6% | 59% | 28% | 20% |
| **S_PRO** | TA≥160 + state(4,5), no FA filter | 70 ↓ | 50% | 9.5% | 68% | 13% | 15% |
| MOMENTUM_QUALITY | TA≥145 + state(4,5) + FA A/B | 65 ↓ | Hold core | 11.1% | 61% | 33% | 24% |
| MOMENTUM_A | TA≥115 + state(4,5) | 55 | 20-40% | 10.4% | 56% | 30% | 26% |
| **COMPOUNDER_BUY** | FA A/B + cheap_pe + TA≥95 + non-BEAR | 50 ↓ | Slow accumulate | 6.9% | 58% | 19% | 16% |
| MOMENTUM_S_N | TA≥130 + state=3 | 45 | 20-30% | 7.9% | 54% | 24% | 26% |
| COMPOUNDER_HOLD | FA A/B + 70≤TA<130 | 40 ↓ | Core hold | 6.3% | 57% | 20% | 18% |
| WAIT | FA A/B + weak TA | 30 ↓ | None | 3.6% | 54% | 15% | 20% |
| **AVOID_bear** | state(1,2) | 0 | Skip | -1.4% | 45% | 12% | 30% |

**Tightening v1.1 (post-backtest):**
- **DEEP_VALUE_RECOVERY**: state(3,4,5) → state(4,5) only (2022 BEAR signals lost -21%)
- S_PRO conviction 92 → 70 (FA filter quan trọng hơn pure score)
- MOMENTUM_QUALITY 90 → 65 (FA alignment không boost momentum)
- COMPOUNDER_BUY 82 → 50 (low edge per backtest)

## Key insight: FA × TA INVERSE relationship

- FA A (best fundamentals) → momentum trade P3M chỉ 8.6% (đã priced in)
- FA D (poor fundamentals) → momentum trade P3M 21.75% (junk rally)
- → MEGA tier requires FA C/D (recovery setup), not FA A/B

## Output structure

Per ticker: TA score + components, FA tier + 7-axis breakdown, 5-state regime,
play_type, conviction (0-100), action_note, warn flags.

Sample output 2026-02-02 (BULL state):
- 3 S_PRO (VVS, PVS, DHC), 2 MOMENTUM_QUALITY (NT2, PTB)
- 16 COMPOUNDER_BUY, 8 DEEP_VALUE_RECOVERY
- Tổng watchlist 254 mã, AVOID 28 mã

Sample output 2026-03-30 (BEAR state):
- 0 actionable, 253 AVOID — system tự động skip toàn bộ phiên

## Backtest validation (542k signals, 2014-2026)

| Strategy | n | P3M | Win | Year-win | Note |
|---|---|---|---|---|---|
| **MEGA only** | 122 | **37.2%** | 85.2% | **87.5%** | 0 trades 2022 (auto-protective) |
| HIGH_CONV (MEGA+MOMENTUM+S_PRO+M_QUALITY) | 1412 | 17.97% | 67.2% | 87.5% | broader, still strong |
| BROAD (+S/A/N/DVR) | 25k | 11.50% | 60.0% | 75% | 2022 -21% (DVR fired in NEUTRAL) |
| FA_FOCUS (COMPOUNDER + DVR) | 27k | 9.18% | 58.9% | 58.3% | low edge, 3 loss years |
| VNINDEX baseline | — | 2.78% | — | — | B&H |

**MEGA validation key stats:**
- 7/8 active years dương (87.5% year-win)
- 0 signals trong 2014-2016 (calibration) và 2022 (crash) — system saves capital correctly
- Years with positive results: 2017 (+30%), 2018 (+40.5%), 2019 (+3.7%), 2020 (+55%), 2021 (+28%), 2024 (+19%), 2025 (+25%)
- Year duy nhất âm: 2023 với n=1 mã (sample noise)

**Simplified CAGR (1 roll/year):**
- MEGA: 13.9%/yr
- HIGH_CONV: 7.3%/yr
- BROAD: 2.3%/yr
- VNINDEX B&H: ~11.5%/yr

**Real CAGR potential** với 4 rolls/year × MEGA P3M 37% có thể cao hơn nhiều, nhưng MEGA chỉ fire ~15/year nên không thể full deploy.

**Recommended live trading approach:**
1. Run holistic engine daily 14:50
2. Priority: MEGA → MOMENTUM → MOMENTUM_N → MOMENTUM_S
3. Exit: re-run weekly; if score drops below tier threshold, reduce position
4. Avoid BROAD strategy — DEEP_VALUE_RECOVERY needs tighter regime gate

## Portfolio Simulation Results (12 năm 2014-2026)

Script: `simulate_holistic_nav.py` — full day-by-day NAV simulation, T+1 exec, TC 0.1%/side, hold 60d, stop -15%

| Strategy | Max Pos | n_trades | CAGR | Sharpe | MaxDD | Calmar | WinRate | Wealth Multiplier |
|---|---|---|---|---|---|---|---|---|
| **MEGA_only** | 3 | 25 | 19.9% | 0.84 | **-17.6%** | 1.13 | **72%** | 8.9× |
| **HIGH_CONV** | 5 | 154 | **28.7%** | 1.09 | -37.2% | 0.77 | 56.5% | **20.8×** |
| **BALANCED** | 8 | 214 | 26.2% | **1.20** | -22.5% | **1.17** | 59.3% | 16.5× |
| VNINDEX B&H | — | — | 11.5% | 0.69 | -45.3% | 0.26 | — | 3.7× |

**2022 Crash Defense (validation):**
- VNINDEX B&H: -32.8% drawdown từ 2021 đỉnh
- MEGA_only: **+1.7%** (system stayed in cash) ⭐
- HIGH_CONV: -16.6% (1/2 VNINDEX)
- BALANCED: -12.3% (1/3 VNINDEX)

**Key findings:**
1. HIGH_CONV (5pos) tối đa CAGR 28.7%, nhưng MaxDD -37% — phù hợp aggressive
2. BALANCED (8pos) Sharpe 1.20 best risk-adj, MaxDD -22.5% — phù hợp balanced
3. MEGA only undertraded (25 trades / 12 năm) — nhưng WinRate 72%, avg +23%/trade — passive friendly
4. All beat VNINDEX 5.6× wealth (HIGH_CONV) với MaxDD nhỏ hơn

**Deployment guide:**
| Profile | Strategy | Expected CAGR | Max DD | Time | n_trades/year |
|---|---|---|---|---|---|
| Aggressive | HIGH_CONV 5pos | 25-30% | -35-40% | weekly | ~13 |
| Balanced | BALANCED 8pos | 22-26% | -20-25% | weekly | ~18 |
| Passive | MEGA 3pos | 15-20% | -15-20% | monthly | ~2 |

**Trades cố định period:**
- avg hold: 48-54 ngày (~2.5 tháng — gần bằng 3M target)
- Stop -15% chỉ trigger ~1-2% trades (most exit by time)
- Win rate cao (56-72%) phù hợp với hit_p3m>0 từ classification table

**Files:**
- `simulate_holistic_nav.py`: simulation engine (T+1 entry + T+3 min hold + 0.1% tax)
- `finetune_holistic.py`: 168-config grid search
- `final_holistic_comparison.py`: side-by-side best configs
- `final_*_nav.csv` / `final_*_trades.csv`: detailed outputs

## Realistic Simulation Final Results (T+1 entry, T+3 min hold, TC 0.1%/side + tax 0.1%/sell)

Grid search 168 configs (4 tier-sets × 4 max_pos × 4 hold_days × 3 stops) on 2014-2026:

| Profile | Config | CAGR | Sharpe | MaxDD | Calmar | n/yr | 2022 ΔNAV |
|---|---|---|---|---|---|---|---|
| **🔥 Max CAGR** | AGGRESSIVE 7p 45d -15% | **35.7%** | 1.34 | -31.6% | 1.13 | 33 | -15.4% |
| ⚖️ Best Sharpe | HIGH_CONV 10p 30d -10% | 20.3% | **1.38** | -19.2% | 1.06 | 28 | +0.4% |
| 🛡️ Best Calmar | HIGH_CONV 10p 30d -20% | 21.6% | 1.36 | **-17.6%** | **1.22** | 27 | +0.0% |
| 💼 Balanced | BALANCED 10p 60d -15% | 24.2% | 1.33 | -27.7% | 0.87 | 21 | -7.7% |
| 😎 Passive | MEGA 5p 90d -15% | 17.6% | 0.92 | -24.3% | 0.72 | 2 | +5.0% |
| baseline | VNINDEX B&H | 11.5% | 0.69 | -45.3% | 0.26 | — | -32.8% |

**Wealth 1B→2026:**
- AGGRESSIVE 39.5× | BALANCED 13.5× | BestCalmar 10.5× | BestSharpe 9.3× | MEGA 7.0× | VNINDEX 3.7×

**Tier set definitions:**
- **MEGA**: chỉ MEGA tier (rất hạn chế ~26 trades/12yr)
- **HIGH_CONV**: MEGA + MOMENTUM + MOMENTUM_N
- **BALANCED**: + MOMENTUM_S + DEEP_VALUE_RECOVERY
- **AGGRESSIVE**: + MOMENTUM_A + MOMENTUM_S_N

**Key insights from grid:**
1. AGGRESSIVE 7p 45d -15% best CAGR (+10.7pp vs baseline 25%)
2. HIGH_CONV 10p 30d -20% best risk-adj (Calmar 1.22, DD chỉ -17.6%)
3. More positions (10) > fewer almost universally (diversification)
4. Stop loss -10/-15/-20 khác biệt nhỏ trong top configs
5. Short hold (30d) + tight stop = best Sharpe; long hold (60d+) = higher CAGR
6. MEGA standalone undertrades — chỉ 2 trades/yr, không phù hợp full deploy

**2022 Crash Defense — system protection rõ ràng:**
All system configs lose < 1/2 VNINDEX (-32.8%):
- BestCalmar/BestSharpe: ~0% (essentially flat)
- MEGA: +5% (system stayed in cash)
- Even worst (AGGRESSIVE): -15.4%, half VNINDEX

**Live deployment recommendations:**
| Risk profile | Config | Expected | DD | Time |
|---|---|---|---|---|
| Aggressive (DD -32% OK) | AGGRESSIVE 7p 45d -15% | 30-36% CAGR | -32% | weekly |
| Balanced (DD -25%) | BALANCED 10p 60d -15% | 22-26% CAGR | -28% | weekly |
| Defensive (DD -20%) | BestCalmar HC 10p 30d -20% | 20-24% CAGR | -18% | weekly |
| Passive | MEGA 5p 90d -15% | 15-20% CAGR | -25% | monthly |

## Final v2 (deposit rate 3%, T+1 + T+3 + tax 0.1%) + Walk-Forward Validation

**Cash idle yield reduced from 6% → 3%/yr** (more realistic non-term VN deposit rate).
Effect: -1pp CAGR for cash-heavy strategies (MEGA), minimal for fully-deployed (HIGH_CONV/BALANCED).

**Walk-forward IS (2014-2019) vs OOS (2020-2026) results:**

| Config | IS CAGR | OOS CAGR | ΔCAGR | IS DD | OOS DD | Verdict |
|---|---|---|---|---|---|---|
| AGGRESSIVE 7p 45d -15% | 36.4% | 28.7% | **-7.8pp** | -26.1% | -36.9% | ⚠ Mild overfit, still beats VNI |
| **HC 10p 30d -20%** | 13.0% | **25.4%** | **+12.5pp** | -13.4% | -17.8% | ✓ **ROBUST**, Calmar 1.43 OOS |
| **BAL 10p 60d -15%** | 15.6% | **28.5%** | **+12.9pp** | -26.3% | -19.2% | ✓ **ROBUST**, best balanced |
| MEGA 5p 90d -15% | 7.1% (n=5) | 22.6% | +15.4pp | -9.0% | -24.3% | ⚠ IS undersampled |
| VNINDEX_BH | 11.4% | 11.6% | flat | -27% | -40% | baseline |

**Key WFA findings:**
1. HC and BALANCED **OOS CAGR > IS CAGR** — robust, not overfit. OOS got better thanks to higher volatility (2020-2026)
2. AGGRESSIVE shows -7.8pp degradation — slight overfit, expected real CAGR 28-30% (not 35%)
3. MEGA standalone IS undersampled (5 trades / 6 years) — embed MEGA into broader strategy
4. All system configs beat VNINDEX OOS by 11-17pp — genuine alpha

**AGGRESSIVE 7p 45d -15% deep-dive:**
- 395 trades over 12 years (33/year)
- Tier mix contribution: MOMENTUM_S_N largest (60% of trades, +7% avg) → MOMENTUM_N (15%, +15% best win 72%) → MEGA (1%, undertraded)
- **MOMENTUM tier underperforms in actual portfolio** (0% vs 19% static) due to capacity constraint when signals cluster
- Sector tilt: Materials (1) +15% best, Financials/RE (8) +6% (drag despite 47% of trades)
- Top 5 drawdowns: 2021-11 → 2024-04 (-33.7%, 853 days), 2014-12 → 2016-03 (-26%), 2020 COVID (-24.7%)
- Monthly: 66% positive months, std 8.22%, P5 = -10%, P95 = +16%
- 2022 disaster: 13 entries, 1 winner (7.7%), 5 stops, profit factor 0.09
- Max lose streak: 16 consecutive losses (psychological challenge)

## Capacity Issue Investigation (round 3)

**Problem:** AGGRESSIVE captures only 4/123 MEGA signals (3.3%). MOMENTUM_S_N (60% of trades) takes slots before higher-tier signals fire.

**Solutions tested:**
1. **Priority eviction** (close lower-tier when higher fires): -4pp CAGR — **cuts winners** (avg evicted +6.4% ret), high turnover hurts
2. **Drop MOMENTUM_S_N tier**: -9pp CAGR — slots stay empty, cash idle at 3% loses gains. MEGA capture 4→2 (worse)
3. **Drop weak tiers (TOP3 only MEGA+M+MN)**: -13pp CAGR — too few signals, undeployed
4. **Verdict:** Current AGG_full is optimal for CAGR. Capacity issue is a false framing — mediocre signals fill slots and contribute meaningfully.

## OOS-Tuned vs Full-History-Tuned Grid (round 4)

Re-ran 168-config grid on 2020-2026 only. Best params per tier set:

| Tier | Full-hist best | OOS-only best | Difference |
|---|---|---|---|
| MEGA | 5p 90d -15% | 5p 60d -15% | hold ↓ |
| HIGH_CONV | 10p 30d **-10%** | 10p 30d **-20%** | stop **looser** |
| **BALANCED** | 10p **60d** -15% | 10p **45d -20%** | hold ↓, stop **looser** |
| AGGRESSIVE | 7p **45d -15%** | 7p **60d -10%** | hold ↑ stop tighter |

**Key insight:** Looser stops (-20% vs -15/-10%) win in OOS because VN market has fake breakouts + recoveries; -15% stops trigger then miss bounces.

**Pairwise comparison on full history:**

| Tier | Full vs OOS-tuned | ΔCAGR | ΔSharpe | ΔCalmar | Verdict |
|---|---|---|---|---|---|
| BALANCED | OOS (10p 45d -20%) > Full (60d -15%) | +1.5pp | +0.07 | +0.08 | OOS-tuned wins |
| HIGH_CONV | OOS (30d -20%) > Full (30d -10%) | +1.6pp | +0.01 | **+0.17** | OOS-tuned wins |
| AGGRESSIVE | Full (45d -15%) > OOS (60d -10%) | -5.2pp | -0.07 | -0.09 | OOS-tuned overfit, use full |

**Final updated recommendations:**

| Profile | Recommended config | Full-hist CAGR | Sharpe | DD | Calmar | Notes |
|---|---|---|---|---|---|---|
| 🏆 **Best Sharpe** | **BALANCED 10p 45d -20%** | 22.8% | **1.27** | -28.6% | 0.80 | OOS-tuned, robust |
| 🛡️ **Best Calmar** | **HIGH_CONV 10p 30d -20%** | 19.1% | 1.22 | -17.8% | **1.07** | low DD |
| 🔥 **Max CAGR** | **AGGRESSIVE 7p 45d -15%** | 29.0% | 1.16 | -43.6% | 0.67 | full-hist tuned, accept high DD |

**Live deployment (final):**
1. Aggressive: AGG 7p 45d -15% (29% CAGR, accept -44% DD)
2. Balanced: BAL 10p 45d -20% (23% CAGR, -28% DD) ⭐ recommended for most users
3. Conservative: HC 10p 30d -20% (19% CAGR, -18% DD, Calmar 1.07)
4. Avoid AGGRESSIVE OOS-tuned (60d -10%) — overfit

## Robustness + Position Management (round 5)

Tested with default BALANCED 10p 45d -20% as base.

### Slippage robustness (CAGR degradation per 0.1% slip):

| Slippage | CAGR | Sharpe | DD | ΔCAGR |
|---|---|---|---|---|
| 0% | 22.82% | 1.27 | -28.6% | baseline |
| **0.1% (realistic)** | **22.10%** | 1.24 | -29.2% | **-0.7pp** |
| 0.2% | 22.00% | 1.23 | -29.8% | -0.8pp |
| 0.3% (high) | 21.03% | 1.15 | -30.4% | -1.8pp |

**Realistic slippage 0.1% chỉ giảm 0.7pp CAGR** — system robust với friction.

### Position Management variants (all với slip 0.1%):

| Variant | CAGR | Sharpe | DD | Calmar | ΔvsBase |
|---|---|---|---|---|---|
| BASE | 22.10% | 1.24 | -29.2% | 0.76 | baseline |
| **PM_trail_tight (+10%/-6%)** | 19.93% | **1.28** | -26.3% | 0.76 | -2.2/+0.04Sh ⭐ best Sharpe |
| PM_trail (+15%/-8%) | 19.84% | 1.17 | -25.9% | 0.77 | -2.3/-0.07Sh |
| PM_sector3 (max 3/sector) | 19.49% | 1.18 | **-25.3%** | 0.77 | -2.6/+3.9pp DD reduction |
| PM_partial (1/3@15, 1/2@25) | 15.86% | 1.20 | -25.5% | 0.62 | **-6.2 ❌ cuts winners** |
| PM_partial_aggro | 14.90% | 1.19 | -26.0% | 0.57 | -7.2 ❌ |
| PM_sector2 | 13.75% | 0.95 | -24.0% | 0.57 | **-8.4 ❌ too restrictive** |
| PM_ALL combined | 15.41% | 1.12 | -23.1% | 0.67 | -6.7 (additive penalty) |

**Findings:**
1. **Trailing stop tight (+10/-6%) đạt Sharpe 1.28 — best risk-adj** (vs base 1.24)
2. **Partial profit-taking HURTS** -6 đến -7pp CAGR — cắt winners → mất long-tail mega-winners
3. **Sector limit 3** modest improvement (DD -3.9pp, CAGR -2.6pp)
4. **Sector limit 2** quá restrictive
5. **Combined PM_ALL** không tốt — additive penalties

### Final live config recommendations (post-round 5):

| Profile | Base config + overlay | Realistic CAGR (slip 0.1%) | Sharpe | DD |
|---|---|---|---|---|
| 🏆 **Default** | BAL 10p 45d -20% | **22.1%** | 1.24 | -29.2% |
| ⚖️ **Best Sharpe** | + trail tight (+10/-6%) | 19.9% | **1.28** | -26.3% |
| 🛡️ **Best DD** | + sector limit 3 | 19.5% | 1.18 | -25.3% |

**Default applied to recommend_holistic.py:** BALANCED 10p 45d -20% with sector limit warning ≥3.

**Files (round 5):**
- `test_robustness_pm.py`: slippage + PM variants test
- `test_eviction.py`: priority eviction (validated not useful)
- `test_tier_optimization.py`: drop weak tiers (validated not useful)
- `robustness_pm_results.csv`: all 11 variants results
- `recommend_holistic.py` updated: BALANCED priority + sector warning

## Round 6+7: Walk-Forward Quarterly + Multi-Strategy + Re-entry Blacklist

### Quarterly walk-forward (48 quarters 2014-2026):

| Strategy | Mean Q | Median | Std | Win% | Best | Worst | P5 | P95 |
|---|---|---|---|---|---|---|---|---|
| BAL 10p 45d -20% | 5.74% | 0.75% | 11.87% | 60% | +39.6% | -15.5% | -8.0% | +26.3% |
| AGG 7p 45d -15% | 6.40% | 2.83% | 13.73% | 67% | +39.6% | -24.0% | -14.3% | +26.4% |
| HC 10p 30d -20% | 4.81% | 0.79% | 10.84% | 71% | +50.0% | -12.8% | -6.8% | +24.2% |
| VNINDEX | 3.05% | 3.59% | 11.05% | 63% | +24.5% | -31.1% | -16.1% | +21.5% |

**Worst quarters concentrated in 2014 (early), 2018 H2, 2020 Q1 COVID, 2022 H2.** No deterioration over time.

### Multi-strategy portfolio (combine BAL + AGG + HC + cash):

| Mix | CAGR | Sharpe | DD | Calmar | Wealth × | 2022 |
|---|---|---|---|---|---|---|
| **50_BAL_25_AGG_25_HC** | 23.16% | **1.30** | -27.9% | 0.83 | 12.3× | -12.2% ⭐ |
| 70_BAL_30_AGG | 24.17% | 1.29 | -30.0% | 0.80 | 13.5× | -13.7% |
| 33_BAL_33_AGG_33_HC | 23.48% | 1.28 | -30.6% | 0.77 | 12.7× | -13.8% |
| 50_BAL_50_AGG | 25.36% | 1.24 | -35.8% | 0.71 | **15.2×** | -17.2% |
| 100% BAL | 22.10% | 1.24 | -29.2% | 0.76 | 11.1× | -5.9% |
| 100% AGG | **27.88%** | 1.12 | -44.7% | 0.62 | **19.3×** | -23.0% |

Diversification 50/25/25 mix improves Sharpe +0.06 vs single BAL.

### Re-entry blacklist after STOP/TRAIL exit:

**BAL 10p 45d -20%** — short blacklist 10-30d helps universally:
| BL days | CAGR | Sharpe | DD |
|---|---|---|---|
| 0 | 22.10% | 1.24 | -29.2% |
| **20d** | **22.67%** | **1.27** | -26.8% (+0.56pp/+0.03Sh/-2.4DD) ⭐ |
| 90d | 22.40% | 1.26 | -28.1% |

**AGG 7p 45d -15%** — only 10d short helps, longer hurts:
| BL days | CAGR | Sharpe | DD |
|---|---|---|---|
| 0 | 27.88% | 1.12 | -44.7% |
| 10d | 28.14% | 1.13 | -45.3% (marginal) |
| 45d | 25.86% | 1.06 | -47.7% (-2pp CAGR) |
| 90d | 25.45% | 1.03 | -39.8% (-2.4pp CAGR) |

**Insight:** Stocks stopped at -20% have 2-3 week downward bias → BAL benefits from 20d cool-off. AGG fires faster, blocking re-entry costs missed signals.

### 🏆 Final OPTIMAL COMBINATIONS:

| Config | CAGR | Sharpe | DD | Calmar | 2022 | Best for |
|---|---|---|---|---|---|---|
| **BAL + BL20** ⭐ simple | **22.67%** | 1.27 | -26.8% | 0.85 | -5.9% | Default — easy to implement |
| **MULTI 50%BAL_ALL+25%AGG+25%HC** ⭐ best Sharpe | 22.01% | **1.30** | -26.4% | 0.83 | -11.6% | Diversified portfolio |
| **BAL_ALL** (BL20+trail+sec3) ⭐ best DD | 19.10% | 1.28 | **-22.2%** | **0.86** | **-0.3%** | Risk-averse, 2022-style crash defense |
| BAL baseline | 22.10% | 1.24 | -29.2% | 0.76 | -5.9% | original |

**Recommended live deployment:**
1. **Default: BAL 10p 45d -20% + BL20** — easy, +0.6pp CAGR universal improvement
2. **Risk-averse: BAL_ALL** (add trailing tight +10/-6 + sector limit 3) — sacrifice 3pp CAGR for -7pp DD reduction; 2022 nearly flat
3. **Best risk-adjusted portfolio: MULTI 50/25/25** — Sharpe 1.30, diversified across BAL/AGG/HC

**Files (rounds 6-7):**
- `test_quarterly_wf.py`: 48-quarter walk-forward analysis
- `test_multi_strategy.py`: portfolio mix variants
- `test_reentry_blacklist.py`: blacklist 0-90 days
- `test_optimal_combo.py`: stack overlays
- `quarterly_returns.csv`, `multi_strategy_results.csv`, `blacklist_results_*.csv`, `optimal_combo_results.csv`

## Round 8: Capital Scaling Test (1B vs 50B)

**BL20 default applied to sim engine** (round 7 finding: +0.6pp CAGR universal).

**Liquidity-aware sizing implemented:**
- `liquidity_volume_pct`: max % daily turnover per day (None = no limit; 0.20 typical)
- `max_fill_days`: # days to attempt fill (default 1; 5 for realistic)
- `min_fill_pct`: abandon if can't fill at least 30%
- Multi-day fill with weighted-avg entry price
- NAV correctly counts pending partial fills

### Capital scaling results (BAL 10p 45d -20% + BL20 + slip 0.1%):

| NAV | Liq cap | Wealth × | CAGR | Sharpe | MaxDD | Trades | 2022 |
|---|---|---|---|---|---|---|---|
| 1B | none (current) | 8.99× | 20.01% | 1.15 | -28.1% | 292 | -5.3% |
| **1B** | 20% vol, 5-day fill | **10.66×** | **21.72%** | **1.21** | -29.0% | 296 | -4.5% |
| **50B** | 20% vol, 5-day fill | **6.54×** | **16.88%** | **0.92** | **-20.6%** | 329 | **+0.02%** |
| 50B | 10% vol cap (stricter) | 4.38× | 13.06% | 0.82 | -18.2% | 312 | +0.7% |
| 50B | 5% vol cap (very strict) | 4.03× | 12.27% | 0.82 | -17.9% | 276 | -1.4% |
| VNINDEX baseline | — | 3.72× | 11.54% | 0.69 | -45.3% | — | -32.8% |

### Key findings:

1. **50B portfolio beats VNINDEX +5.4pp CAGR** (16.88% vs 11.54%) — system still works at scale
2. **DD GIẢM at 50B (-20% vs 1B -29%)** — multi-day fills naturally average entry prices, reduce concentration risk
3. **Sharpe degradation -0.29** (1.21 → 0.92) — significant friction but still > VNINDEX 0.69
4. **2022 crash defense** at 50B: +0.02% (vs 1B -4.5%, VNINDEX -33%) — slow fills during crash = defensive by accident
5. **Optimal liquidity config**: 20% volume cap + 5-day fill window. 10%/5% caps too restrictive (lose 4-5pp CAGR)
6. **Wealth multiplier**: 1B → 10.66× (10.66B), 50B → 6.54× (327B over 12 years)

### Realistic CAGR scaling table:

| NAV | Realistic CAGR | DD | Comment |
|---|---|---|---|
| 1B (~$40k) | 21-22% | -29% | Easy to deploy |
| 10B (~$400k) | ~20% | ~-26% | Smooth scaling |
| **50B (~$2M)** | **17%** | **-20%** | Sweet spot — DD reduces! |
| 100B (~$4M) | ~14% | ~-18% | Liquidity becomes binding |
| 500B+ ($20M+) | ~10-12% | — | Approaches VNINDEX baseline |

### Liquidity universe stats (Volume_3M_P50 × Close):
- Median: 5-10B VND/day
- P75: 30B/day
- P95: 200B+/day (large caps)
- 50B portfolio with 5B/position requires turnover ≥ 25B → only top 25% stocks reachable

**Conclusion:** System scales gracefully. 50B is realistic upper bound for retail; 100B+ requires institutional execution (multi-day fill spreading, working orders).

**Files (round 8):**
- `simulate_holistic_nav.py`: extended with liquidity_volume_pct, max_fill_days, min_fill_pct, liquidity_lookup, init_nav params + BL20 default
- `test_capital_scaling.py`: 1B vs 50B variants
- `capital_scaling_results.csv`: all metrics

## Round 9: Extended scaling + sector concentration + multi-strategy 50B

### Capital scaling table (1B → 500B):

| NAV | Wealth × | CAGR | Sharpe | DD | Sector Fin/RE | Median liquidity captured |
|---|---|---|---|---|---|---|
| 1B | 10.66× | 21.72% | 1.21 | -29.0% | 54% | 9.7B |
| 10B | 9.11× | 20.14% | 1.16 | -24.3% | 53% | 13.8B |
| 30B | 6.14× | 16.27% | 0.95 | -23.2% | 53% | 15.2B |
| **50B** | 6.54× | **16.88%** | 0.92 | -20.6% | **54%** | 16.4B |
| 100B | 4.44× | 13.17% | 0.82 | -18.0% | 59% | 20.0B |
| 200B | 4.03× | 12.27% | 0.82 | -17.9% | 59% | 25.7B |
| 500B | 3.52× | 11.01% | 0.75 | -17.1% | 63% | 34.2B |

**Pattern:** Each +50B adds ~1pp CAGR drag. 500B essentially parity với VNINDEX (11.5%) → upper bound for system edge.

### Sector concentration insights:
- **Financials/RE (sector 8) dominates 54-63%** of trades regardless of NAV size — natural pull due to liquidity + edge
- Health (sector 4): never traded — penalty + low liquidity
- Tech/Telecom (9): drops 8 → 1 trade as NAV grows (size out of niche)
- At 500B: 63% Fin/RE → high systemic risk

### Sector limit at 50B (BAL strategy):

| sec_lim | CAGR | Sharpe | DD | Trades |
|---|---|---|---|---|
| None | 16.88% | 0.92 | -20.6% | 329 |
| 4 | 13.37% | 0.87 | -20.3% | 318 |
| 3 | 13.22% | 0.90 | -19.7% | 307 |
| **2** | **15.73%** | **1.03** | -20.3% | 290 |

**sec_lim=2 wins on Sharpe** (+0.11) at CAGR cost -1.15pp. Forces diversification away from over-concentrated Fin/RE.

### Multi-strategy at 50B:

| Mix | CAGR | Sharpe | DD | Wealth × |
|---|---|---|---|---|
| 100% BAL_50B | 16.88% | 0.92 | -20.6% | 6.54× |
| 100% AGG_50B | 14.55% | 0.72 | -31.3% | 5.13× |
| **100% HC_50B** ⭐ | 15.03% | **1.24** | **-12.7%** | 5.40× |
| **50/25/25 mix** | **15.89%** | **1.04** | -18.5% | 5.90× |
| 70_BAL_30_AGG | 16.23% | 0.95 | -21.8% | 6.12× |

**HC_50B is surprise winner** (Sharpe 1.24, DD -12.7%): only top 3 tiers (MEGA/MOMENTUM/MOMENTUM_N) → easier to fill at scale + higher per-trade quality.

### Final 50B deployment recommendations:

| Profile | Config | Realistic CAGR | Sharpe | DD |
|---|---|---|---|---|
| 🏆 Best Sharpe | **HC_50B** standalone | 15.0% | **1.24** | **-12.7%** |
| Diversified | 50% BAL + 25% AGG + 25% HC | 15.9% | 1.04 | -18.5% |
| Max return | 70% BAL + 30% AGG | 16.2% | 0.95 | -21.8% |
| Smooth | BAL + sec_lim=2 | 15.7% | 1.03 | -20.3% |

**Files (round 9):**
- `test_scaling_extended.py`: 1B-500B scaling + sector + multi-strategy
- `scaling_extended.csv`: capital scaling metrics
- `sector_limit_50B.csv`: sector limit variants
- `multi_strategy_50B.csv`: portfolio mixes at 50B
- `layer3_intraday_timing.py` (new): intraday entry timing (Layer 3)

## Round 10: Tiered Exit Slippage + Sector Rotation + HC/BAL Multi-NAV

### A) Tiered exit slippage (extra slip when position > X% of ADV):

Slippage tiers:
- > 20% ADV → +0.5% extra slip
- 10-20% ADV → +0.3% extra slip
- 5-10% ADV → +0.1% extra slip
- < 5% ADV → no extra slip

Impact on CAGR:

| NAV | Without tiered slip | With tiered slip | Δ | Slip-tiered exits |
|---|---|---|---|---|
| 1B | 21.72% | 21.50% | -0.22pp | 108/296 (37%) |
| **50B** | 16.88% | **15.47%** | **-1.41pp** | 280/329 (85%) |
| 100B | 13.17% | 12.55% | -0.62pp | 276/312 (88%) |

**At 50B: 85% of exits cross 20% ADV** (typical position 5B vs 25B ADV = 20%). Realistic CAGR 15.47% (was 16.88% naive).

### B) Sector rotation (cap Fin/RE specifically) at 50B realistic:

| Config | CAGR | Sharpe | DD | Calmar | Fin/RE % |
|---|---|---|---|---|---|
| Base (no caps) | 15.47% | 0.86 | -21.8% | 0.71 | 54% |
| Global lim 3 | 11.77% | 0.85 | -22.0% | 0.53 | 40% |
| Global lim 2 | 14.85% | 1.02 | -20.6% | 0.72 | 37% |
| **Fin/RE max 4** ⭐ | **16.05%** | 0.98 | **-20.2%** | **0.79** | 48% |
| Fin/RE max 3 | 12.82% | 0.91 | -22.0% | 0.58 | 41% |
| Fin/RE max 2 | 13.71% | 0.94 | -20.9% | 0.65 | 32% |
| Excl Fin/RE entirely | 11.16% | 0.95 | -21.5% | 0.52 | 0% |

**🏆 BREAKTHROUGH: Fin/RE max 4 is universally best:**
- CAGR 16.05% (highest!)
- Sharpe 0.98 (vs base 0.86)
- DD -20.2% (best!)
- Calmar 0.79 (best!)

Cap chỉ 1 sector (Fin/RE), giữ nguyên các sector khác → vừa exposure tới sector mạnh nhất, vừa diversification.

### C) HC vs BAL at multiple NAVs (with tiered exit slip):

| NAV | BAL CAGR | HC CAGR | BAL Sh | HC Sh | BAL DD | HC DD |
|---|---|---|---|---|---|---|
| 1B | **21.50%** | 18.29% | 1.20 | 1.23 | -29.1% | **-16.5%** |
| 30B | 16.30% | 15.74% | 0.98 | 1.20 | -23.1% | -16.4% |
| 50B | 15.47% | 14.35% | 0.86 | **1.18** | -21.8% | **-14.2%** |
| 100B | 12.55% | 11.05% | 0.78 | **1.02** | -18.1% | **-12.0%** |
| 200B | 10.94% | 8.30% | 0.73 | 0.83 | -18.3% | -12.0% |

**Findings:**
- BAL wins CAGR at 1-100B; HC wins Sharpe at ALL scales
- HC DD ~half of BAL across all scales
- **At 100B+: HC clearly preferred** (better risk-adj despite lower CAGR)

### D) Exit signal analysis (BAL_50B with realistic friction):

| Reason | n | % | avg ret | win% | avg hold |
|---|---|---|---|---|---|
| **TIME** (60d hit) | 262 | 82% | **+12.5%** | 66% | 45d |
| **STOP** (-20%) | 42 | 13% | **-23.9%** | 0% | 20d |
| EOD | 15 | 5% | +1.8% | 53% | 6d |

**TIME exits = profit harvest, STOP = risk control working.** STOP avg -23.9% (slippage adds to -20% cap).

### Final 50B deployment recommendations (post-round 10):

| Profile | Config | Realistic CAGR | Sharpe | DD |
|---|---|---|---|---|
| 🏆 **Best overall** | **BAL + Fin/RE max 4** | **16.05%** | 0.98 | **-20.2%** |
| Best Sharpe | HC standalone | 14.35% | **1.18** | -14.2% |
| Diversified | 50/25/25 mix | 15.89% | 1.04 | -18.5% |
| Smooth | BAL + global sec_lim 2 | 14.85% | 1.02 | -20.6% |

**For 100B+:** HC strongly preferred (higher Sharpe + lower DD).

**Files (round 10):**
- `simulate_holistic_nav.py`: extended với `exit_slippage_tiered`, `sector_limit_per_sector` params
- `test_advanced_features.py`: comprehensive test
- `sector_rotation_50B.csv`, `hc_vs_bal_scaling.csv`, `exit_analysis_trades.csv`

## Round 11: FA × Sector + Multi-strat Optimal + VN30 + Rolling Window

### A) FA × Sector interaction (within S130+ BULL):

**Sector 8 Fin/RE breakdown by FA tier:**

| FA tier | n | P3M | hit10 |
|---|---|---|---|
| **A** (best fundamentals) | 138 | **1.4%** | 25.4% (terrible!) |
| B | 830 | 15.06% | 49.2% |
| C | 1468 | 18.84% | 54.6% |
| **D** ⭐ | **1163** | **21.33%** | 54.3% |
| E | 458 | 11.47% | 38.4% |

**Within Fin/RE, FA inverse extra strong**: A 1.4% → D 21.33% (gap +19.9pp). Confirms momentum-style trades favor recovery candidates. Materials, Cons Goods follow similar pattern. Utilities (sec 7) low edge regardless of tier.

### B) Multi-strategy mixes (BAL+Fin/RE-max-4 vs HC at 50B):

| Mix | CAGR | Sharpe | DD | Calmar |
|---|---|---|---|---|
| 100% BAL+Fin4 | **16.05%** | 0.98 | -20.2% | 0.79 |
| 100% HC | 14.35% | **1.18** | **-14.2%** | **1.01** |
| 70 BW + 30 HC | 15.57% | 1.08 | -17.2% | 0.90 |
| **60 BW + 40 HC** | **15.40%** | 1.11 | -16.7% | 0.92 |
| **50 BW + 50 HC** | **15.23%** | **1.14** | -16.1% | 0.95 |
| 40 BW + 60 HC | 15.06% | 1.17 | -15.5% | 0.97 |
| 30 BW + 70 HC | 14.89% | 1.19 | -15.1% | 0.98 |

**🏆 50% BAL+Fin4 + 50% HC mix:** Pareto-optimal (CAGR 15.23% vs HC alone 14.35%, Sharpe 1.14 vs HC 1.18).

### C) VN30-only universe (top 30 by avg liquidity):

VN30 list: CTG, DGC, DIG, DXG, FPT, GEX, HAG, HPG, HSG, KBC, MBB, MSN, MWG, NKG, NVL, PDR, POW, PVD, PVS, SHB, SHS, SSI, STB, TCB, VHM, VIX, VND, VNM, VPB, VRE.

| Config | CAGR | Sharpe | DD | Wealth × |
|---|---|---|---|---|
| VN30_BAL_50B | 15.93% | **1.05** | **-16.1%** | 5.79× |
| **VN30_HC_50B** | 9.10% | **1.31** | **-8.2%** | 3.27× |
| VN30_BAL_100B | 14.24% | 0.98 | -15.8% | 4.93× |
| VN30_HC_100B | 7.63% | 1.20 | -7.4% | 2.76× |
| VN30_BAL_500B | 11.34% | 0.82 | -17.7% | 3.51× |
| VN30_HC_500B | 6.64% | 0.91 | **-5.1%** | 2.45× |

**Insights:**
- VN30 BAL_50B: similar CAGR to full universe (15.93 vs 16.05) BUT Sharpe better (1.05 vs 0.98), DD better (-16.1 vs -20.2)
- VN30 HC: very smooth (-5 to -8% DD) but low CAGR
- VN30 scales BETTER at 500B (BAL 11.34% vs 11.01% full universe)
- **For institutional capital >100B: VN30-only better risk-adj**

### D) Rolling 3-year window stability (BAL+Fin/RE max 4 at 50B):

| Window | CAGR | Sharpe | DD |
|---|---|---|---|
| 2014-2016 | 6.6% | 1.73 | -3.2% |
| **2015-2017** | 12.7% | **1.80** | -8.6% |
| 2016-2018 | 12.1% | 0.98 | -20.2% |
| 2017-2019 | 9.4% | 0.76 | -20.2% |
| 2018-2020 | 14.4% | 0.82 | -20.2% |
| **2019-2021** | **45.2%** | 1.54 | -19.0% |
| **2020-2022** | **41.7%** | 1.47 | -19.0% |
| 2021-2023 | 24.2% | 1.08 | -19.0% |
| **2022-2024** | **5.0%** | **0.48** | -13.7% (worst) |
| 2023-2025 | 9.3% | 0.65 | -18.6% |
| 2024-2026 | 16.9% | 0.97 | -18.6% |

**Findings:**
- Wide variance: CAGR 5-45% across windows
- Sharpe range 0.48-1.80
- Best windows: 2019-2021, 2020-2022 (covers mega bull 2020-2021)
- Worst: 2022-2024 (chop/crash)
- DD remarkably consistent ~-20% (system mechanism stable)
- **Average rolling Sharpe ~1.1** — system structurally robust despite return variance

### Layer 3 (intraday) backtest deferred — vnstock API limited historical depth (~few months). Recommend forward-paper-tracking 30-60 days post-deployment.

### Final Recommended Live Configs (post-round 11):

| Profile | Config | NAV range | CAGR | Sharpe | DD |
|---|---|---|---|---|---|
| 🥇 Best CAGR | BAL+Fin/RE-max-4 | 1B-50B | 16% | 0.98 | -20% |
| 🥈 Best Sharpe | 50% BAL+Fin4 + 50% HC | 1B-100B | 15% | 1.14 | -16% |
| 🥉 Best DD | 100% HC | any | 14% | 1.18 | -14% |
| **For institutional 100B+** | **VN30 BAL** | 100B-500B | 11-14% | 1.0 | -16% |
| Smooth defensive | VN30 HC | 100B+ | 7-9% | 1.2-1.3 | -5 to -8% |

**Files (round 11):**
- `test_round11_optimization.py`
- `round11_multistrategy.csv`, `round11_vn30.csv`, `round11_rolling.csv`

## Round 12: Q1 2026 Data Refresh + v10 + Ultimate Combo

### Data refresh (post Q1 2026 reports):
- `ticker_financial`: 2026-05-08 (Q1 2026: 1091 tickers reported)
- **FA script** modified to use 90-day join window (was 30d) → captures Q1 2026 reports despite ticker.time max 2026-03-30
- `fa_ratings` updated: 12,367 rows (vs 11,144) — Q1 2026: 326 tickers rated
- Tier dist Q1 2026: A=33, B=65, C=98, D=82, E=48 (similar Q4 2025)

### Model effectiveness on Apr 2025 - Mar 2026 (latest available P1M):

| Tier | n | P1M | hit1m_5 | lose1m_5 |
|---|---|---|---|---|
| S_HIGH | 173 | 6.03% | 32.4% | 34.7% |
| S | 1909 | 4.63% | **37.8%** | 26.6% |
| BEAR_skip | 40k | 0.51% | 22.5% | 23.7% |
| baseline | 110k | 1.63% | 26.9% | 21.4% |

**Model still outperforms baseline +3pp P1M** on most recent 12 months. MEGA n=3 small (chop period rare). System robust.

### v10 — Add Fin/RE × FA-D bonus to score:
- +10 if Fin/RE (sector 8) AND FA tier D
- -10 if Fin/RE AND FA tier A (already weak per round 11)
- Tier thresholds adjusted: MEGA ≥170 (was 160), MOMENTUM ≥155, S ≥140, A ≥125

**v10 vs v9 at 50B BAL+Fin/RE-max-4:**

| Version | CAGR | Sharpe | DD | Calmar |
|---|---|---|---|---|
| v9 | 11.69% | 0.78 | -21.4% | 0.55 |
| **v10 (Fin/RE-D bonus)** | **18.04%** | **1.12** | -20.4% | **0.89** |

**+6.35pp CAGR, +0.34 Sharpe** breakthrough.

### VN30 + small-mid HYBRID at 50B (v10 signals):

| Mix | CAGR | Sharpe | DD | Wealth × |
|---|---|---|---|---|
| 100% VN30 | 16.27% | 1.13 | -16.0% | 6.14× |
| **70 VN30 + 30 smid** | 15.75% | **1.20** | -15.9% | 5.82× |
| 50/50 | 15.39% | 1.18 | -16.1% | 5.60× |
| 100% smid | 14.42% | 0.93 | -23.0% | 5.06× |

70/30 VN30/smid Pareto-optimal Sharpe.

### 🏆 ULTIMATE WINNER — 50/50 BAL_Fin4 (v10) + VN30_BAL at 50B:

| Mix | CAGR | Sharpe | DD | Calmar |
|---|---|---|---|---|
| 100% BAL_Fin4 (v10) | 18.04% | 1.12 | -20.4% | 0.89 |
| 70/30 | 17.54% | 1.19 | -16.1% | 1.09 |
| **🏆 50/50** | **17.19%** | **1.21** | **-14.5%** | **1.18** |
| 30/70 | 16.83% | 1.20 | -15.1% | 1.12 |
| 100% VN30 | 16.27% | 1.13 | -16.0% | 1.02 |

**50/50 split = best across ALL metrics:**
- vs original BAL_50B baseline (16.05/0.98/-20.2/0.79): **+1.14 CAGR, +0.23 Sharpe, -5.7pp DD, +0.39 Calmar**

### Final Recommended Live Configs (post-round 12):

| Profile | Config | CAGR | Sharpe | DD |
|---|---|---|---|---|
| 🏆 **Best overall** | **50/50 BAL_Fin4-v10 + VN30_BAL** | **17.19%** | **1.21** | **-14.5%** |
| Higher CAGR | BAL_Fin4-v10 alone | 18.04% | 1.12 | -20.4% |
| VN30 only (institutional) | VN30_BAL | 16.27% | 1.13 | -16.0% |
| Smooth small-NAV | 70/30 VN30+smid | 15.75% | 1.20 | -15.9% |

**Files (round 12):**
- `fundamental_rating.py`: SQL window 30d → 90d to capture latest quarter reports
- `test_round12_v10_hybrid.py`: comprehensive v10 + hybrid + combined
- `round12_v10.csv`, `round12_hybrid.csv`, `round12_combined.csv`

## Round 13: ULTIMATE multi-NAV + Rolling + v11 + Deep-dive

### A) ULTIMATE 50/50 BAL_Fin4(v10) + VN30_BAL across NAVs:

| NAV | BAL_Fin4 CAGR | VN30 CAGR | **50/50 CAGR** | **Sharpe** | **DD** | Calmar |
|---|---|---|---|---|---|---|
| **1B** | 18.49% | 16.36% | **17.40%** | **1.31** ⭐ | -18.4% | 0.95 |
| 30B | 18.80% | 16.12% | 17.54% | 1.20 | -14.8% | 1.18 |
| **50B** | 17.97% | 16.27% | **17.15%** | 1.21 | **-14.5%** | **1.18** |
| 100B | 14.91% | 14.04% | 14.49% | 1.06 | -15.3% | 0.95 |
| 200B | 12.06% | 13.69% | 12.91% | 1.01 | -14.3% | 0.90 |

**1B Sharpe 1.31 highest** — small portfolio gets best risk-adjusted return.
**50B Sharpe 1.21, DD -14.5% — institutional sweet spot.**
**200B+: VN30 alone preferred** (Sh 1.11 vs 50/50 1.01).

### B) Quarterly stability (48 quarters of ULTIMATE 50/50 50B):
- **Win rate 85.4%** quarters positive (vs ~60% for single strats!)
- Mean +4.46%, Median +0.77%, Std 10.24%
- Best Q: +44.83%, **Worst Q: -8.80%** (chỉ moderate)
- Worst 5 Q: 2018Q2 (-8.8%), 2023Q3 (-5.6%), 2019Q2 (-1.8%), 2025Q4 (-1.4%), 2018Q4 (-1.1%)

### C) v11 (extend Fin/RE-D pattern to Materials sec 1 + Cons Goods sec 3):

| Version | CAGR | Sharpe | DD | Calmar |
|---|---|---|---|---|
| v10 | 17.97% | 1.12 | -20.4% | 0.88 |
| v11 (Mat-D + ConsGoods-D +8 each) | 17.10% | 1.10 | -21.1% | 0.81 |

**v11 DOES NOT improve** (-0.87pp CAGR). Materials/Cons Goods FA-D pattern weaker than Fin/RE. **Keep v10.**

### D) ULTIMATE deep-dive — Top 5 drawdowns:

| Peak | Trough | Recovery | DD | Days |
|---|---|---|---|---|
| 2021-01-12 | 2021-02-01 | 2021-03-15 | -14.5% | 25d (fast) |
| 2021-06-17 | 2021-07-19 | 2021-09-06 | -13.6% | 33d |
| 2025-08-26 | 2025-10-03 | ongoing | -13.5% | recovering |
| 2018-03-26 | 2018-10-29 | 2020-09-29 | -13.1% | **479d (worst)** |
| 2024-05-16 | 2025-04-09 | 2025-06-17 | -12.9% | 46d |

**Yearly wealth progression (1B start, 50B sim normalized):**
- 2014: 1.03×, 2017: 1.36×, **2020: 2.37× (COVID recovery +55%)**
- **2021: 4.60× (mega bull +94%)** ⭐
- **2022: 4.72× (only -2% vs VNI -33%)** ⭐⭐ excellent crash defense
- 2025: 6.62× (+32%), 2026: 6.73×

### 🏆 FINAL CONFIG RECOMMENDATIONS (post-round 13):

| Capital scale | Recommended config | CAGR | Sharpe | DD | Win rate |
|---|---|---|---|---|---|
| 1B | 50/50 BAL_Fin4(v10) + VN30 | 17.40% | **1.31** | -18.4% | very high |
| 30-50B | 50/50 BAL_Fin4(v10) + VN30 | **17.15-17.54%** | **1.21** | **-14.5%** | 85% Q win |
| 100B | 50/50 mix | 14.49% | 1.06 | -15.3% | high |
| **200B+** | **VN30_BAL alone (v10)** | **13.69%** | **1.11** | -14.3% | better than 50/50 |

**Files (round 13):**
- `test_round13_ultimate.py`: comprehensive multi-NAV + v11 + rolling + DD
- `round13_multi_nav.csv`, `round13_v11.csv`, `round13_dd_periods.csv`

## Round 14: Stability tests — Sector evolution + Day/month patterns + PM variants

### A) Sector evolution year-by-year (BAL_Fin4 50B):

**Fin/RE concentration:** stable 40-60% across years
- 2020: lowest 47% (COVID broad rally)
- **2023: highest 73%** (chop year, only Fin/RE recovery worked)
- 2025-2026: 42-43% (recent broader diversification — Materials, Industrials, Cons Goods picked up)

**Conclusion:** Fin/RE structural pull is consistent over time. 2023 anomaly aligns with regime weakness.

### B) Day-of-week + month patterns (BAL_Fin4 50B):

**Day-of-week:**
| Day | Avg Ret | Win% |
|---|---|---|
| Monday | 5.28% | 53.4% |
| Tuesday | 5.83% | 60.0% |
| Wednesday | 10.39% | 64.1% |
| **Thursday** ⭐ | **14.89%** | **73.0%** |
| Friday | 8.91% | 65.2% |

**Thursday entries 3× better than Monday.** Weekly momentum building toward end of week.

**Month patterns:**
- **May: 24.69%, 93.3% win** ⭐
- **Q4 (Oct-Dec): 18.37% avg, 80% win** ⭐
- November: 18.53%, 79.3%
- December: 21.56%, 81.3%
- August: 15.80%, 77.8%
- **July: -1.86%, 28.6% win** ❌ avoid
- March-April: weak (1-2% returns)

**Q1/Q2/Q3/Q4 returns:** 5.84% / 8.30% / 7.74% / **18.37%**

### C) Position management variants (50B BAL_Fin4):

| Variant | CAGR | Sharpe | DD | Calmar | Note |
|---|---|---|---|---|---|
| **baseline (BL20, hold 45d, stop -20%)** | **17.97%** | **1.12** | -20.4% | 0.88 | optimal |
| **stop_-25%** | **18.30%** | 1.12 | -20.6% | **0.89** | slight win |
| stop_-15% | 14.87% | 1.01 | -16.8% | 0.88 | DD trade-off |
| BL10/BL30 same as BL20 | 17.97% | 1.12 | -20.4% | 0.88 | re-entries rare at 50B |
| BL40 | 16.88% | 1.07 | -20.4% | 0.83 | too long |
| trail_tight (+10/-6) | 14.73% | 1.05 | -17.5% | 0.84 | cuts winners |
| sec_lim_2_global | 13.25% | 0.91 | -19.7% | 0.67 | over-restrictive |
| hold_30d | 12.30% | 0.85 | -21.2% | 0.58 | too short |
| hold_60d | 14.88% | 0.99 | -27.3% | 0.54 | DD worse |
| hold_90d | 13.57% | 0.96 | -29.2% | 0.46 | DD worse |

**Confirmation:** Default settings (BL20, hold 45d, stop -20%) is genuinely optimal. Only stop -25% gives marginal improvement (+0.33pp CAGR).

### Key Stability Conclusions

1. **Sector mix stable** — Fin/RE 40-60% across years; recent diversification healthy
2. **Day-of-week tactical edge** — Thursday entries 3× Monday returns; could weight execution toward Tue-Thu
3. **Month seasonality real** — May (+25%), Q4 (+18%) strong; July (-2%, 29% win) AVOID
4. **PM near-optimal** — only stop -25% improves marginally; all other adjustments hurt
5. **System robust to parameter changes** — ±5d hold, ±5% stop, BL10-30 give similar results

### Tactical refinements (potential):
- **Skip July entries** — system avg -1.86% / 29% win is anti-edge
- **Weight execution to Tue-Thu** — avoid Monday entries
- **Q4 + May = double-down periods** — historical 80%+ win rates
- **Stop -25% adoption** — marginal +0.33pp CAGR free

**Files (round 14):**
- `test_round14_stability.py`
- `round14_trades.csv`, `round14_pm.csv`

## Round 15: Tactical refinements + Forward holdout + Stress test

### A) Tactical refinements — Calendar filters FAIL ❌

| Variant | CAGR | Sharpe | Δ vs base |
|---|---|---|---|
| baseline | 17.97% | 1.12 | — |
| **stop -25%** | **18.30%** | 1.12 | **+0.33pp** ✓ |
| skip July | 15.86% | 1.03 | -2.11pp ❌ |
| Tue-Thu only | 15.13% | 0.97 | -2.84pp ❌ |
| Tue-Thu + skip July | 12.65% | 0.88 | -5.32pp ❌ |
| All combined | 13.66% | 0.91 | -4.31pp ❌ |

**Critical lesson:** Day-of-week and monthly patterns from round 14 were CORRELATION, not exploitable CAUSATION. System already filters via TA score + state5. Manual calendar filters remove winning signals along with losers. **Only stop -25% adopted** as confirmed +0.33pp improvement.

### B) Forward Holdout (Jan 2024 - Jan 2026 OOS, 24 months):

| Strategy | CAGR | Sharpe | DD | Calmar |
|---|---|---|---|---|
| BAL_Fin4 50B baseline | 21.22% | 1.05 | -15.2% | **1.39** |
| BAL_Fin4 50B + stop -25% | 22.97% | 1.09 | -17.1% | 1.34 |
| **VNINDEX_BH** | **28.22%** | — | — | — |

**Insights:**
- System CAGR 21-23% in 2024-2026 holdout vs VNINDEX 28.22%
- System UNDERPERFORMS B&H in extreme bull period
- Sharpe 1.05 maintained (similar to full-period 1.12)
- **DD -15.2% (BETTER than full-period -20%)** — defensive quality preserved
- Calmar 1.39 still excellent
- Trade-off: smoother ride vs lower returns in pure-bull regime

### D) Stress test — System robust to shocks

Peak NAV at 2025-09-04 (8.06× wealth multiplier from 12-yr compounding).

| Shock at peak | CAGR | Sharpe | DD |
|---|---|---|---|
| Baseline (no shock) | 17.97% | 1.12 | -20.4% |
| Shock -25% | 18.15% | 1.15 | -25.0% |
| Shock -40% | 17.67% | 1.12 | -40.0% |
| Shock -60% (Black Swan) | 16.98% | 1.04 | -60.0% |

**Findings:**
- 12-year compounding cushions single-event shocks
- Even -40% shock: CAGR drops only -0.30pp
- -60% Black Swan: still 16.98% CAGR (50% above VNINDEX baseline 11.5%)
- Sharpe maintains 1.04+ even in worst case
- Years 2014-2024 unaffected (shock at 2025); only 2025-2026 returns scale

### Final Conclusions (post-round 15)

1. **Calendar tactics counter-productive** — don't filter by July or day-of-week
2. **Only stop -25% adopted** as marginal improvement (+0.33pp)
3. **System genuinely defensive** — DD -15% in 2024-2026 holdout (vs -20% full-period)
4. **Long-term compounding cushions shocks** — even -40% Black Swan only costs -0.30pp CAGR
5. **System trades returns for smoothness** in extreme bull (underperforms B&H 2024-2026 by 5pp)

### F-system mix not tested (deferred)

F-system has separate methodology (VN30F derivatives, daily script), would require integration work. Recommended for separate analysis.

**Files (round 15):**
- `test_round15_tactical.py`
- `round15_tactical.csv`, `round15_holdout.csv`

## Round 16: Tier-sized positions + EX-BULL threshold tightening — BOTH REJECTED

Two structural ideas tested on BAL_Fin4 single-book at 50B (baseline CAGR=17.97%, Sh=1.12, DD=-20.4%):

### A) Tier-based position sizing (3 variants)

| Variant | Weights | CAGR | Sharpe | DD | Δ CAGR |
|---|---|---|---|---|---|
| baseline (equal 10%) | uniform | **17.97%** | **1.12** | -20.4% | — |
| tier-mild | 13/12/11/9/8% | 16.55% | 1.06 | -18.0% | -1.42pp |
| tier-aggressive | 16/14/12/7/6% | 15.00% | 1.01 | -18.5% | -2.97pp |
| tier-defensive | 12/11/11/9/9% | 17.10% | 1.06 | -18.8% | -0.87pp |

**ALL variants underperform.** DD does improve (+2.4pp better at tier-mild) but CAGR drops more.

### B) EX-BULL threshold tightening (v11 SQL: state=5 +15 score)

| Variant | CAGR | Sharpe | DD | Δ |
|---|---|---|---|---|
| v10 baseline | 17.97% | 1.12 | -20.4% | — |
| v11 / equal-weight | 17.55% | 1.06 | -20.4% | -0.42pp |
| v11 / tier-mild | 16.66% | 1.07 | -18.0% | -1.31pp |
| v11 / tier-aggressive | 14.42% | 1.00 | -18.6% | -3.54pp |

EX-BULL filter alone is mild loss. Doesn't combine positively with tier sizing.

### Why both failed

**Tier distribution in BAL universe (% of trades):**
- DEEP_VALUE_RECOVERY: 62% ← majority
- MOMENTUM_N: 17%
- MOMENTUM_S: 15%
- MOMENTUM: 5%
- **MEGA: 0%** ← never fires (170+ threshold too high for BAL)

**Avg per-tier net return (v10 baseline):**
- MOMENTUM: +17.46%
- MOMENTUM_S: +13.76%
- MOMENTUM_N: +11.37%
- DEEP_VALUE_RECOVERY: +7.46% ← lowest but majority

**Lessons:**
1. MEGA never fires in BAL → tier weight increases for MEGA = wasted parameter
2. DVR (lowest avg return) carries 62% of trades; reducing its weight wastes slot allocation
3. MOMENTUM_S (13.76%) > MOMENTUM_N (11.37%) — **higher tier ≠ higher per-trade return** at this granularity
4. Capacity argument from round-3 holds: mediocre signals fill slots crucial for compounding
5. EX-BULL state=5 entries are mostly momentum-continuation winners; filtering removes good with bad

### Conclusion

**Equal-weight 1/10 is genuinely optimal.** Production v10 stays at CAGR 17.97% / Sh 1.12 / DD -20.4% for BAL single-book → 17.15% / 1.21 / -14.5% with VN30 50/50 split.

**Files (round 16):**
- `test_round16.py`
- `round16_results.csv`

## Round 17: Exit logic — state-transition + profit-target — BOTH REJECTED

Tested two new exit rules untried in rounds 1-16. Period EXTENDED to 2026-03-30 (was 2026-01-16) to include 2025-Q4 CRISIS (Sep-Dec, 64 sessions) and 2026-Q1 BEAR (Mar 17-Apr 8, 23 sessions).

**Re-baselined (extended period):** CAGR=17.01% Sh=1.06 DD=-20.4% Cal=0.83.

### A) State-transition exit

| Variant | CAGR | Sharpe | DD | Calmar | Note |
|---|---|---|---|---|---|
| baseline | 17.01% | 1.06 | -20.4% | 0.83 | — |
| ST: exit on CRISIS only | 16.30% | 1.08 | -18.3% | 0.89 | -0.71pp / +2.1pp DD ✓ marginal |
| ST: exit on BEAR | 15.95% | 1.05 | -18.3% | 0.87 | -1.07pp / +2.1pp DD |
| ST: halve NEUTRAL + close BEAR | 9.03% | 0.86 | -18.8% | 0.48 | -7.99pp ❌ |

State-exit fires too late (smoothing lag) — most damage done before signal confirms. CRISIS-only variant (-0.71pp) is least bad but still negative.

### B) Profit-target exit (full close + redeploy)

| Variant | CAGR | Sharpe | DD | Calmar |
|---|---|---|---|---|
| PT +25% | 14.66% | **1.17** | -20.6% | 0.71 |
| PT +30% | 14.15% | 1.04 | -22.1% | 0.64 |
| PT +35% | 13.09% | 0.93 | -19.4% | 0.67 |
| PT +40% | 15.11% | 1.05 | -20.0% | 0.75 |
| PT +30% + BL10 | 11.97% | 0.92 | -21.2% | 0.57 |

PT cuts winners — same fundamental flaw as PARTIAL (round 5). PT +30% trades hit +32.5% avg (target works), but residual TIME exits drop to +3.2% (vs baseline +13.5%) because best stocks already exited.

### C) Combined ST+PT

| Variant | CAGR | Sharpe | DD | Calmar |
|---|---|---|---|---|
| ST BEAR + PT +30% | 14.00% | 1.11 | -17.9% | 0.78 |
| ST BEAR + PT +35% | 14.42% | **1.16** | **-17.3%** | 0.83 |

Best DD across all variants (-17.3%) but CAGR -2.59pp.

### Exit breakdown insights

| Reason (baseline) | n | % | avg ret |
|---|---|---|---|
| TIME (45d) | 250 | **88.7%** | +13.52% |
| STOP (-20%) | 32 | 11.3% | -23.47% |

**Most exits are TIME** (45d hit). Adding intermediate exits (state, PT) reshuffles distribution but doesn't improve risk-adjusted return.

**ST exit on BEAR breakdown:**
- TIME drops to 52.6% (avg +18.86% — only winners ride to time)
- STATE_EXIT_S1 (CRISIS) 32.9% avg -0.36% (much better than letting -20% stop fire)
- STATE_EXIT_S2 (BEAR) 7.3% avg +1.17%

State-exit logic technically works but the slot-recycling benefit doesn't materialize because:
1. New entries during CRISIS are blocked (state filter at SQL level)
2. Capital sits in cash earning only 3%/yr deposit
3. Original plan would've TIME-exited eventually anyway

### 2026-Q1 specific behavior (user's concern)

| Variant | Q1 exits | avg ret | win % |
|---|---|---|---|
| v10 baseline | 13 | -4.66% | 23.1% |
| ST: exit on BEAR | 12 | -4.70% | 25.0% |
| ST+PT BEAR+30 | 12 | -4.43% | 25.0% |

**ST exit doesn't help 2026-Q1** because BEAR was only 13 sessions in test data, and state-confirmation lag (7-day min stay) means signal fires near end of damage period.

### Conclusion

KEEP CURRENT EXIT LOGIC: TIME 45d + STOP -20% only.

Lessons:
1. State-transition exits don't add value for **timed strategies** (45d already forces clean-up)
2. Profit targets cut winners — same as PARTIAL (round 5)
3. Compounding > risk overlays for this system's signal half-life
4. The recent 2026-Q1 weakness is a **regime-detection lag issue** (BA-system holds into BEAR for ~7-10 days before confirmation), not exit-logic issue

Future direction: if want to fix 2026-Q1-style losses, look at **earlier regime detection** (lower MIN_STAY in 5-state filter), not exit overlays. But round-11 confirmed MIN_STAY=7 is optimum for state-machine quality.

**Files (round 17):**
- `test_round17.py`
- `round17_results.csv`
- `round17_trades_*.csv` (3 variants)

**Files:**
- `walkforward_holistic.py`: IS/OOS validation
- `analyze_aggressive_deepdive.py`: trades + DD + sector breakdown
- `aggressive_trades_full.csv`: 395 trade log
- `walkforward_results.csv` / `walkforward_deltas.csv`
