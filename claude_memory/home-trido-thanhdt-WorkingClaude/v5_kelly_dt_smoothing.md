# V5 + DT_10_25_25 State Smoothing (2026-05-27)

**Status**: 🟢 VALIDATED — V5 (ETF_KELLY 100%) benefits substantially from DT state smoothing

**Key finding**: ETF parking aggressiveness controls state-machine sensitivity.

## TL;DR

DT_10_25_25 (asymmetric causal confirmation, 34 transitions vs TQ34b's 155) helps V5 significantly but barely helps V1.

| System | ETF parking | ΔFull (DT−TQ) | ΔIS | ΔOOS | ΔDD |
|--------|-------------|---------------|-----|------|-----|
| V1 BASE | {3: 0.7} (70% in NEUTRAL) | +0.28pp | +1.98pp | -1.46pp | +2.6pp better |
| **V5 KELLY** | **{3: 1.0} (100% in NEUTRAL)** | **+1.90pp** | **+2.03pp** | **+1.83pp** | **+2.9pp better** |

V5 with DT_10_25_25 = **22.15% CAGR** (vs canonical V5_TQ_KELLY 20.25%, +1.90pp).
Beats V1 baseline 20.74% by +1.41pp while having better DD (-24.5% vs -27.4%).

## Why V5 is more state-sensitive than V1

**Mechanism**:
1. ETF_KELLY puts 100% of idle cash into VN30 ETF during NEUTRAL state (vs 70% for BASE)
2. Each NEUTRAL→BULL transition = liquidate entire ETF position, deploy to stocks
3. Each BULL→NEUTRAL transition = sell all stocks, buy ETF with 100% idle cash
4. Rebalance friction = 0.15% per side
5. TQ34b 155 transitions × 0.15% × (more affected NAV with KELLY) = substantial drag
6. DT_10_25_25 with 34 transitions = -78% transition friction
7. Plus: smoother regime detection = better timing of ETF parking decisions

**V1 BASE has less impact** because only 70% of cash gets ETF-parked, so transition cost is smaller in absolute terms.

## Sub-period CAGR (V5)

| Period | V5_TQ_KELLY | V5_DT_KELLY | Δ |
|--------|-------------|-------------|---|
| 14-17 | +14.30% | +19.56% | +5.26pp |
| 18-19 | +9.04% | +5.42% | -3.62pp |
| 20-22 | +36.29% | +35.72% | -0.57pp |
| 23-26 | +19.88% | +23.62% | +3.74pp |

DT wins big in trending periods (14-17, 23-26). Slight loss in 18-19 mixed regime. Even in COVID/bear 20-22.

## 5-system stack RECOMMENDATION (updated)

Use DIFFERENT state series per system based on ETF parking intensity:

| System | State | Filter | ETF | Why |
|--------|-------|--------|-----|-----|
| V1, V2, V3, V4 | TQ34b | C3_clean (no SVT) | BASE {3: 0.7} | State noise tolerable; filter tune wins |
| **V5** | **DT_10_25_25** | **C3_clean** | KELLY {3: 1.0} | Kelly amplifies state noise; DT smoothing pays |

## Caveats

1. **Pre-2014 not retested for V5+DT integrated** — standalone DT_10_25_25 had -1.26pp 2007-2013 CAGR + -9.34pp 2008 GFC. V5 integrated pre-2014 likely worse. **CHECK before deployment.**
2. **18-19 weak period** — DT loses -3.62pp in 2018-19. If user concerned about regime variability, monitor live.
3. **Different state per system adds complexity** — operationally must maintain 2 state CSVs (TQ34b for V1-V4, DT for V5).

## Files

- `test_v5_dt_integrated.py` — V1×{TQ,DT} × ETF×{BASE,KELLY} 4-cell test
- `data/v5_dt_integrated_nav.csv` — NAV time series
- `simulate_state_timing.py` — DT_10_25_25 standalone validator
- `vnindex_5state_dt_10_25_25.csv` — DT state series

## User insight

User correctly predicted this:
> "có thể vì chúng ta dùng BA v11 làm integrated nên ảnh hưởng của transition state chưa mạnh. Vậy nếu dùng V5 để integrated có thể ảnh hưởng sẽ khác"

V11 (BAL leg only, ETF_BASE) tested earlier showed DT marginal benefit (+0.51pp Full, -0.98pp OOS). User suspected V5 would be different because ETF_KELLY parking is more aggressive. **Confirmed empirically**.

## Z1+Z2 follow-up findings (2026-05-27)

### Z1: V5+DT+C3_clean COMBINED — state+filter CONFLICT (like V11)

| Combo | Full | IS | OOS | DD |
|-------|------|-----|-----|-----|
| V5_TQ_V_PROD (baseline) | 20.25% | 13.12% | 27.30% | -27.4% |
| V5_TQ_C3_clean (filter alone) | 20.58% | 12.65% | 28.47% | -27.4% |
| **V5_DT_V_PROD (state alone) ⭐** | **22.15%** | **15.15%** | **29.12%** | **-24.5%** |
| V5_DT_C3_clean (combined) | 21.45% | 13.90% | 29.00% | -26.1% |

Additivity analysis: interaction term -1.03pp Full / -1.30pp OOS.

**State+filter CONFLICT for V5**: both optimizations want to "loosen" the system. Combining over-loosens (especially in 18-19 mixed regime, V5_DT_C3 drops to +2.86% from +9.04% baseline).

**WINNER: V5_DT_V_PROD alone** — keep SVT for V5, use DT state.

### Z2: V5+DT pre-2014 — fails 2009 V-shape recovery

| Variant | 7y CAGR | MaxDD | 2008 GFC | 2009 | 2011 |
|---------|---------|-------|----------|------|------|
| V5_TQ_KELLY | +7.26% | -37.8% | 0.0% | **+34.0%** | -28.4% |
| V5_DT_KELLY | +4.01% | -44.2% | -0.4% | +12.1% | **-16.7%** |

**DT_10_25_25 pattern (regime-dependent)**:
- ✅ Wins sustained bear (2011 inflation +11.7pp protection)
- ❌ Loses V-shape recovery (2009 -21.9pp, 25-day CRISIS confirm too slow)
- ❌ Slow ramp-up (2007 -9.3pp)
- Modern era (2014+) has NO V-shape recovery as fast as 2009 → DT safe for modern only

### Final V5 recommendation

**Deploy V5_DT_V_PROD** for modern era (2014+):
- +1.90pp Full CAGR vs canonical V5_TQ_KELLY
- +1.83pp OOS, +2.03pp IS, DD -2.9pp better
- 78% fewer state transitions = less ETF rebalance friction

**Caveats**:
1. V5_DT NOT for pre-2014 deployment (V-shape recovery risk)
2. Don't combine with C3_clean (conflict, over-loosens)
3. Monitor live for any V-shape recovery patterns
4. Pre-2014 V5_TQ DD already -37.8% — V5 KELLY architecture inherently risky in extreme bears

## User preference: V4 (BASE) as the safer/balanced default over V5 (KELLY) — 2026-05-28
On the DT4 foundation, full 2014→2026-05-15 (real E1VFVN30, current DT4 state, verified by transparent sim that matches `run_5systems_dt4.py` byte-for-byte): **V5 +23.43%/Sh1.46/Calmar1.12/DD−20.84%** vs **V4 +22.47%/Sh1.56/Calmar1.24/DD−18.13%**. V5's extra ~+1pp raw CAGR is bought with ~+3pp deeper DD + worse Sharpe/Calmar. User agreed V4 "an toàn hơn, cân bằng hơn".
**How to apply**: when recommending between V4/V5, lead with V4 as the balanced default (lower DD, better risk-adjusted); pitch V5 only when the user explicitly wants max raw return and accepts deep DD. Consistent with [[v5-prodspec-integrity-audit]] real-ETF → V4 recommended.
**Quoting rule**: 23% (V5+DT4 full 2014) is a BACKTEST upper-bound — part rides on the idealized ensemble return-level switch; realistic forward ≈ 21–22% after −1.5pp haircut. Transparent 2025+ slice + 4-gate reconciliation: `sim_v5_dt4_transparent.py` → `data/v5dt4_*`.

## Open research
- Live shadow paper-trade V5_DT_KELLY for 4-8 weeks
- Regime-adaptive DT (faster confirms during high VIX) — future enhancement
