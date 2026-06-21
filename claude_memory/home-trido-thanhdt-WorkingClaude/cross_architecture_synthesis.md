# Cross-Architecture Optimization Synthesis (2026-05-27)

**Status**: 🟢 RESEARCH COMPLETE — synthesizing 26 tests across state/filter/architecture/ensemble dimensions

## TL;DR — Optimal stack per system

| System | Architecture | State | ETF | Filter | Expected Full CAGR |
|--------|--------------|-------|-----|--------|---------------------|
| V1-V3 | BAL+VN30 | TQ34b | BASE {3:0.7} | **C3_clean** | ~20.5-21% |
| V4 | BAL+VN30 | TQ34b | BASE | V_PROD | ~20% (defensive) |
| **V5** | BAL+VN30 | **DT_10_25_25** | KELLY {3:1.0} | V_PROD | 22.15% (validated) |
| V12 | BAL+LAGGED | TQ34b | BASE | C3_clean | ~21.3% |
| V12.1 | BAL+LAGGED V12.1 | TQ34b | BASE | C3_clean | ~22.2% |
| **V121_ENS** ⭐ | V12.1+ensemble | TQ34b | BASE | C3_clean | ~24.3-24.7% |

## Lever value summary (12y backtest Full CAGR)

| Lever | Mechanism | Magnitude |
|-------|-----------|-----------|
| Architecture: VN30 → LAGGED HL_3y | post-earnings drift alpha | +1.4pp |
| Architecture: S2 sizing on LAGGED | surprise-conditioned sizing | +0.85pp |
| Ensemble: M1+M3 AND-HOLD | regime timing | +2.1pp |
| State: DT_10_25_25 | smoother transitions | +0.46 to +1.30pp (context-dependent) |
| Filter: C3_clean (no SVT) | remove obsolete legacy filter | +0.3pp Full / +3.6pp OOS |
| ETF: KELLY (100%) | aggressive NEUTRAL parking | +0.65pp (V11 only) |

## Key empirical findings (validated)

### Finding 1: Architecture is the biggest lever
- V11 static → V12.1 ensemble: +4.3pp Full CAGR
- Other levers max +1.5pp each
- **Priority: upgrade architecture first**

### Finding 2: DT_10_25_25 benefit is context-dependent
| Context | DT Benefit |
|---------|-----------|
| V5 KELLY (100% ETF) | **+1.90pp** ⭐ (ETF amplifies state noise) |
| V11 static (BAL+VN30) | +1.30pp |
| V12.1 static (BAL+LAGGED) | +0.99pp |
| ENS V12 | +0.53pp |
| **ENS V12.1** | **+0.46pp** (ensemble pre-empts state benefit) |

Mechanism: M1+M3 ensemble already does market timing → DT smoothing marginal.
KELLY ETF amplifies state transitions → DT smoothing critical.

### Finding 3: DT has OOS 24-26 weakness in ensemble systems
- ENS_V121 + DT: -0.61pp OOS 24-26 vs TQ34b
- Possible over-smoothing in recent volatile regime
- IS 14-19: DT +1.12pp (positive)
- Net Full: +0.46pp positive but caveat for forward use

### Finding 4: State × Filter optimizations CONFLICT
Validated for V11 (BA v11) and V5:
- Filter alone (C3_clean) → +0.34pp Full
- State alone (DT) → +1.90pp Full (V5)
- Combined → +1.19pp Full (V5)
- Interaction term -1.03pp (over-loosens)

→ Each system uses ONE primary lever, not both.

### Finding 5: User insights all validated empirically
1. ✅ "state = crowd psychology, can't strip" — V_BLIND failed
2. ✅ "SVT not needed in modern market" — C3_clean +3.6pp OOS
3. ✅ "V5 integrated khác V11" — V5+DT +1.90 vs V11+DT +0.28pp
4. ✅ "architecture upgrade first" — V12.1 ensemble +4.3pp dominates

## Pre-2014 stress test caveats

| Variant | Pre-2014 7y CAGR | DD | Note |
|---------|-------------------|-----|------|
| V_PROD (V11 BAL only) | -0.08% | -12.2% | Capacity-limited, defensive |
| V5_TQ_KELLY | +7.26% | -37.8% | Architecture risky pre-2014 |
| V5_DT_KELLY | +4.01% | **-44.2%** | DT misses 2009 V-recovery |
| C3_safer (V_PROD + SVT s3=90) | -0.08% | -12.2% | IDENTICAL to baseline ✅ |
| C3_clean (V_PROD no SVT) | -0.08% | -12.2% | IDENTICAL to baseline ✅ |

**Conclusion**: V5 architecture inherently risky pre-2014. V11/V12.1 with C3_clean safe.

## Deployment recommendation

### Phase 1 (immediate, low risk):
- Deploy C3_clean filter (remove SVT) for ALL systems V1-V4 + V12 + V12.1
- Single SQL/runner change, +0.3pp Full / +3.6pp OOS gain
- Pre-2014 IDENTICAL to baseline

### Phase 2 (V5 specific):
- Deploy DT_10_25_25 state for V5 KELLY system only
- Modern era (2014+) deployment, +1.90pp Full
- Caveat: pre-2014 V-shape recovery risk

### Phase 3 (advanced, optional):
- Test V121_ENS + DT + C3_clean combined (additivity uncertain)
- Test regime-adaptive DT (faster in high VIX)
- Live shadow track 4-8 weeks before full switch

## File index

- `tune_bav11_filters.py` — filter ablation + sweep (C3 candidates)
- `tune_bav11_combined.py` — combined C1-C7
- `cross_test_state_filter.py` — V11 state × filter conflict proof
- `test_c3_refinements.py` — SVT lever final pick
- `sim_v11_pre2014_clean.py` — C3 pre-2014 safety
- `test_v5_dt_integrated.py` — V5 KELLY benefit from DT
- `test_v5_dt_c3clean.py` — V5 state × filter conflict
- `sim_v5_pre2014.py` — V5 + DT pre-2014 risk
- `test_v12_ensemble_dt.py` — V12.1 ensemble + DT
- `simulate_state_timing.py` — DT_10_25_25 standalone validator
- `vnindex_5state_dt_10_25_25.csv` — DT state series

## Memory cross-refs

- [ba_v11_c3_cons_filter_retune.md](ba_v11_c3_cons_filter_retune.md) — C3_clean details
- [v5_kelly_dt_smoothing.md](v5_kelly_dt_smoothing.md) — V5 + DT details
- (this file) — cross-architecture synthesis

## V5 = V121_ENS + KELLY final test (2026-05-27) — HYPOTHESIS REJECTED

User hypothesis: KELLY ETF (100% NEUTRAL parking) amplifies state sensitivity → DT smoothing should help V5 V121_ENS+KELLY (like it helped V5 BAL+VN30+KELLY +1.90pp).

**Empirical result**:
| Period | V5_TQ_KELLY (canonical) | V5_DT_KELLY | Δ |
|--------|--------------------------|-------------|---|
| FULL 2014-26 | +26.07% | +24.79% | -1.29pp ❌ |
| OOS 20-26 | +34.03% | +31.84% | -2.19pp ❌ |
| OOS 24-26 | +35.59% | +33.51% | -2.08pp ❌ |

Canonical 26.07% matches memory note 26.09% — implementation validated.

**DT HURTS V5 ensemble**, not helps. Year-by-year shows DT loses -21.5pp in 2025 strong bull rally (slow regime detection misses bull re-entry).

### Lever pattern (validated comprehensively)

```
                    NO ENSEMBLE        WITH M1+M3 ENSEMBLE
              ┌──────────┬──────────┬──────────┬──────────┐
              │  BASE    │  KELLY   │  BASE    │  KELLY   │
DT impact:    │  +0.28pp │ +1.90pp  │ +0.46pp  │ -1.29pp  │
              │ marginal │  BIG ⭐   │ marginal │  HURT ❌ │
              └──────────┴──────────┴──────────┴──────────┘
```

**Insight**: DT works best in MODERATE complexity. In high complexity (ensemble + KELLY), KELLY amplifies DT's downside (delayed CRISIS exit → miss bull recovery).

V5 canonical TQ34b confirmed OPTIMAL. DT NOT recommended for V5.

## V121_ENS BASE final test result (2026-05-27) — DIMINISHING RETURNS

Tested V121_ENS × 4 combos (state × filter):

| Combo | Full | OOS 20-26 | OOS 24-26 | DD |
|-------|------|-----------|-----------|-----|
| TQ+PROD (canonical) | 24.26% | **30.63%** ⭐ | 28.52% | -17.49% |
| TQ+CLEAN | 23.94% | 30.43% | **29.24%** ⭐ | -16.03% |
| DT+PROD | 23.77% | 28.96% | 27.81% | **-14.65%** ⭐ |
| DT+CLEAN | **24.41%** ⭐ | 30.28% | 28.63% | -16.14% |

**Surprising finding**: Individual levers HURT V121_ENS!
- Filter alone (C3_clean): -0.32pp Full
- State alone (DT): -0.49pp Full
- Combined: +0.15pp Full (interaction +0.96pp positive)

**Mechanism**: M1+M3 AND-HOLD ensemble already does sophisticated market timing → DT smoothing redundant. SVT removal lets in noisy signals that ensemble would otherwise filter. Combined effect cancels individual losses.

**V121_ENS FINAL recommendation**: Keep CANONICAL TQ+PROD.
- All optimizations marginal (within noise)
- Canonical wins Sharpe (1.65) + OOS 20-26 (30.63%)
- Architecture+ensemble is the value, not parameter tuning

### Diminishing returns pattern

| System | Architecture layers | Best tune value |
|--------|---------------------|-----------------|
| V11 (BAL only) | 1 | C3_clean +3.6pp OOS |
| V5 KELLY | 2 (BAL+VN30+ETF_KELLY) | DT +1.90pp Full |
| V12.1 static | 3 (+LAGGED+S2) | DT +0.99pp Full |
| V121_ENS | 4 (+M1+M3 ensemble) | ~0 (canonical optimal) |

Each added intelligence layer reduces marginal value of parameter tuning.

## Open research (UPDATED 2026-05-27)

1. ~~Test V121_ENS + DT + C3_clean~~ → DONE, marginal +0.15pp Full only
2. Regime-adaptive DT (faster confirms during VIX>25 or large gap days)
3. Live shadow paper-trade key recommendations 4-8 weeks
4. Quarterly re-validation of OOS performance
5. Test V12.1 + KELLY ETF (does Kelly amplify V12.1 like V11?)
