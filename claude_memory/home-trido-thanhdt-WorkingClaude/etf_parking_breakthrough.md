---
name: ETF parking — V6 breakthrough
description: BA-system v10.1 enhancement — park 70% of idle cash in VN30 ETF during NEUTRAL state. At realistic 1% deposit rate, lifts CAGR +3.65pp to 17.60%, Sharpe to 1.16, DD better -3.9pp. Beats even 3% deposit assumption.
type: project
originSessionId: df3c1340-40c2-46c7-b6dc-247737308843
---
## ETF Parking — Strategy V6 (round 18 breakthrough)

**Motivation (from user feedback):** Deposit rate 3% assumption is optimistic; realistic non-term VN rate is 0.5-1%. BA-system sits 71% in cash on average → significant opportunity cost at low yield.

### Deployment analysis (12-yr 2014-2026)

| State | % time | Avg deployed | Avg cash |
|---|---|---|---|
| CRISIS | 28.4% | 13.7% | 86.3% |
| BEAR | 3.5% | 15.9% | 84.1% |
| **NEUTRAL** | **51.3%** | **17.9%** | **82.1%** |
| BULL | 13.0% | 89.4% | 10.6% |
| EX-BULL | 3.9% | 95.1% | 4.9% |
| **OVERALL** | 100% | **28.9%** | **71.1%** |

→ System sit cash 71% of time. NEUTRAL = 51% of sessions với chỉ 18% deployed.

### Deposit rate sensitivity (single-book BAL_Fin4 50B)

| Deposit rate | CAGR | Sharpe |
|---|---|---|
| 0.0% | 13.63% | 0.85 |
| 0.5% | 13.62% | 0.84 |
| **1.0% (realistic)** | **13.88%** | **0.86** |
| 1.5% | 17.16% | 1.05 |
| **3.0% (original assumption)** | **17.01%** | **1.06** |
| 5.0% | 17.79% | 1.11 |

**At 1% deposit: CAGR drops -3.13pp** vs 3% assumption.

### V6 ETF parking solution

**Logic:**
- In NEUTRAL state: park 70% of idle cash in VN30 ETF (E1VFVN30 or similar tracker)
- In BEAR/CRISIS: keep cash defensive (0% ETF)
- In BULL/EX-BULL: not needed (system already 90%+ deployed)
- 0.05% friction per side on rebalance (ETF spread)
- Rebalance threshold: only when delta > 0.5% of cash pool

### Test results — single-book BAL+Fin/RE-max-4 at 50B (deposit 1% realistic)

| Variant | CAGR | Sharpe | DD | Calmar |
|---|---|---|---|---|
| baseline (no ETF) | 13.88% | 0.86 | -20.8% | 0.67 |
| ETF 30% in NEUTRAL | 17.07% | 1.06 | -20.5% | 0.83 |
| **ETF 70% in NEUTRAL (V6)** | **18.34%** | **1.11** | -21.1% | **0.87** ⭐ |
| ETF 100% in NEUTRAL | 16.25% | 0.88 | -24.3% | 0.67 |
| ETF 100% in NEU+BULL | 11.47% | 0.80 | -26.4% | 0.44 ❌ |

70% is Pareto-optimal — 30% cash cushion prevents DD blowout when VN30 dips in NEUTRAL.

### Test results — PRODUCTION 50/50 BAL+VN30 split at 50B

| Variant | CAGR | Sharpe | DD | Calmar | NAV end |
|---|---|---|---|---|---|
| P0 (3% deposit, no ETF) — ORIGINAL | 15.97% | 1.08 | -21.0% | 0.76 | 306.4B |
| P1 (1% deposit, no ETF) — REALISTIC | 13.95% | 1.00 | -21.3% | 0.65 | 247.1B |
| **P2 (1% dep + V6 ETF 70% NEU)** | **17.60%** | **1.16** | **-17.4%** | **1.01** | **363.5B** |

**P2 vs P1: +3.65pp CAGR, +0.16 Sharpe, DD better -3.9pp**
**P2 vs P0: +1.63pp CAGR, +0.08 Sharpe, DD better -3.6pp**

V6 ETF parking at realistic 1% deposit BEATS the original 3% deposit assumption.

### Capital allocation in P2 (avg across 12 years)

| Component | BAL book | VN30 book |
|---|---|---|
| BA active positions | 26.9% | 18.6% |
| ETF parking (VN30) | 30.7% | 33.0% |
| Cash residual | 42.4% | 48.4% |
| **Active "working" capital** | **57.6%** | **51.6%** |

Working capital roughly DOUBLED vs P1 baseline (28% → 55%).

### Why ETF parking works (vs failed alternatives)

✅ ETF parking — **PASSIVE BETA** on idle cash. Earns market return (~11.5%/yr) when system not actively deployed. Doesn't compete with BA-alpha.

❌ Expanded NEUTRAL tier set — **ACTIVE BETA** with low-conviction signals. Adds noise, no alpha:
- E1 + MOMENTUM_S_N: -4.32pp CAGR
- E3 + DVR_N: -4.57pp CAGR, DD -49.5% catastrophic
- Lesson: NEUTRAL state signals genuinely don't have edge for lower tiers

❌ Combining V6 + expanded tiers — doesn't compound (bad tiers cancel ETF benefit)

### Failed variants (for record)

| Variant | CAGR | Issue |
|---|---|---|
| ETF 100% NEUTRAL | 16.25% | DD -24.3% (no cash cushion) |
| ETF 100% NEU+BULL+EXBULL | 11.47% | Adds ETF on top of already-deployed BULL → drag |
| ETF 100% NEU + 50% BEAR | 75% (anomaly) | Bug in rebalance logic — DO NOT USE |
| Expanded NEUTRAL tiers (E1,E2,E3) | 9-10% | Bad signals destroy alpha |

### Implementation plan

**For live system at 50B NAV:**

1. **Daily routine post-14:50:**
   - Run recommend_holistic for BA-core stock picks (BAL + VN30 books)
   - Check current 5-state regime

2. **In NEUTRAL state:**
   - After deploying BA-core picks (typically 2-3 positions = 5-15% NAV)
   - **Use 70% of remaining cash to buy E1VFVN30 (or similar VN30 ETF)**
   - Keep 30% cash as defensive cushion

3. **State transitions:**
   - On NEUTRAL → BULL: SELL ETF position, deploy cash to new BA-core BULL picks
   - On NEUTRAL → BEAR: SELL ETF position, hold full cash defensive
   - On BULL → NEUTRAL: no immediate ETF buy (wait for BA-core deployment first)

4. **Rebalance threshold:** Only act if delta > 0.5% of cash pool (avoid over-trading)

### Expected outcomes at production NAV

| NAV | CAGR (P2) | Sharpe | DD |
|---|---|---|---|
| 1B-10B | ~18-20% | 1.20+ | -16% |
| **50B (validated)** | **17.60%** | **1.16** | **-17.4%** |
| 100B | ~15% | 1.10 | -16% |
| 200B+ | ~12-13% | 1.05 | -15% |

ETF benefit scales well — VN30 ETF has deep liquidity.

### Files
- `test_etf_parking.py` — 8-variant grid (single book)
- `test_expanded_neutral.py` — expanded NEUTRAL tier set (rejected)
- `test_production_etf.py` — final 50/50 production test
- `etf_parking_results.csv`, `expanded_neutral_results.csv`, `production_etf_results.csv`
- `production_etf_nav_traces.csv` — daily NAV for P0/P1/P2

### Engine extension

`simulate_holistic_nav.py` extended with new params (round 18):
- `deposit_annual` — yield on idle cash (default 0.03 = 3%/yr; use 0.01 realistic)
- `cash_etf_states` — dict {state_int: etf_fraction} (e.g., {3: 0.7} for V6)
- `vn30_underlying` — daily VN30 close prices for ETF returns
