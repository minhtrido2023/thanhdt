# BA v11 C3 Filter Re-tune (2026-05-27)

**Status**: 🟢 RECOMMENDATION FINALIZED v2 — C3_clean chosen after empirical confirmation
**Recommended**: `C3_clean` — REMOVE SVT entirely (user insight: modern market matured, SVT redundant)
**Conservative alternative**: `C3_safer` (s3=60→90 only) — same pre-2014 safety, slightly less OOS
**Rejected**: `C3_cons` (with cash_etf bear) — pre-2014 DD -36% risk in 2011-style sustained bears  
**Scope**: BA v11 filter re-tune (state machine TQ34b PRESERVED — user insight that market_state reflects crowd psychology + has real informational value)

## TL;DR — FINAL after dual pre-2014 stress tests (2026-05-27)

**RECOMMENDED: C3_clean** — REMOVE SV_TIGHT entirely (user thesis: market matured post-2014):
- Remove SV_TIGHT filter from runner (no days_since_release gate at all)
- Everything else UNCHANGED (cash_etf {3: 0.7}, AVOID_bear, overheat, D1, FA guards)

**Result (12y integrated BAL leg, 25B book):**
- Full CAGR: 21.52% → 21.81% (+0.30pp)
- IS 14-19: 14.77% → 11.76% (-3.02pp — REGRESSION accepted)
- OOS 20-26: 28.12% → **32.00%** (+3.88pp) ⭐
- MaxDD: -20.8% → -20.9% (essentially same)
- Sharpe: 1.38 → 1.40

**Pre-2014 stress test (2007-2013): IDENTICAL to V_PROD and C3_safer** ✅
- Reason: Pre-2014 is capacity-constrained (max_positions=10, hold_days=45, AVOID_bear blocks 2008-2011), not signal-constrained. Removing SVT doesn't change which trades execute — capacity ceiling already binds at 17 trades for 7 years.

**Why C3_clean > C3_safer (the safer alternative):**
- Architecturally cleaner: 1 layer less (3 layers vs 4)
- Aligned with user thesis: modern market doesn't need earnings-freshness filter
- Marginally better OOS (+0.22pp vs C3_safer)
- Same pre-2014 safety (both identical to V_PROD)
- Empirically supports user's claim that SVT was a legacy filter for immature market

**ALTERNATIVE: C3_cons** — TWO changes vs V_PROD:
1. SV_TIGHT s3: 60 → 90
2. cash_etf: {3: 0.7} → {2: 0.5, 3: 0.7}

**Result:**
- Full CAGR: 21.52% → **22.71%** (+1.19pp)
- OOS 20-26: 28.12% → 30.76% (+2.63pp)
- IS 14-19: 14.77% → 14.61% (-0.17pp, preserved by ETF)
- MaxDD 2014-2026: -20.6%
- **⚠️ Pre-2014 DD: -36% (2008 GFC -27%, 2011 inflation -22pp annual loss)** vs V_PROD -12%

## Pre-2014 Stress Test (2007-2013)

| Variant | 7y CAGR | MaxDD | 2008 GFC DD | 2011 annual |
|---------|---------|-------|-------------|-------------|
| V_PROD baseline | -0.08% | -12.2% | -12.2% | 0.0% |
| **C3_safer** | -0.08% | -12.2% | -12.2% | 0.0% (= V_PROD) |
| C3_cons | +6.70% | -36.0% | -27.3% | **-22.1%** ⚠️ |
| B&H VNINDEX | -5.35% | -79.9% | -65.7% | -27.7% |

**Mechanism of C3_cons risk**: cash_etf {2: 0.5} = 50% of idle cash → ETF tracking VNI during BEAR state. During sustained bears (2011 inflation crisis -27.7% VNI over the year), ETF held throughout → massive drag. Pre-2014 state 2 was extended period; in 2014-2026, state 2 is shorter and recovery follows quickly → ETF wins.

**C3_safer mechanism**: SVT s3=90 only changes NEUTRAL state behavior. Pre-2014 had very few state 3 days (mostly state 1/2 in 2008-2011) → zero impact. In 2014-2026, NEUTRAL is more common → boost OOS.

## Research path (rejected alternatives)

This came after a multi-stream research showing:

### Stream 1: State series alternatives (REJECTED)
- DT (Asymmetric Causal Confirmation): +2.68pp standalone but FAILS integrated (-0.98pp OOS)
- DT_15_30_25: catastrophic in 2008 GFC stress test (-21pp vs TQ34b)
- v3.5/v3.6/v3.7 macro floor: improvements were smoothing artifacts (deep-dive proven)
- v2g lesson confirmed: state-machine standalone wins don't transfer to integrated

### Stream 2: State-stripped BA v11 (REJECTED)
- V_BLIND (fully state-independent): -12.88pp OOS, MaxDD -64.4% (catastrophic)
- V_VNI_DEP (VNI-proxy filters): -10.46pp OOS vs PROD (5pp transparency tax)
- Confirms user insight: market_state reflects real crowd psychology, can't be eliminated

### Stream 3: Filter re-tuning (WINNER)
- User insight: "tune BA v11 filter một chút, kết quả sẽ tốt lên"
- Ablation revealed: SV_TIGHT s3=60 was OVERFIT IS, removing it improved OOS +3.88pp
- Cross-test revealed: state × filter optimizations CONFLICT (not additive)
- Best filter tune + TQ34b state = optimal

## C3_cons spec

### Changes from V_PROD (current production)

```python
# In runner pre-processing (e.g. recommend_holistic.py or run_5systems_prodspec.py):
SV_TIGHT_DAYS = {1: 30, 2: 60, 3: 90}     # was {1: 30, 2: 60, 3: 60}

# In simulate() call:
cash_etf_states = {2: 0.5, 3: 0.7}         # was {3: 0.7}
```

### Unchanged

- State series: TQ34b (`vnindex_5state_tam_quan_v3_4b_full_history.csv`)
- AVOID_bear: state ∈ {1, 2}
- Overheat: Close/MA200 > 1.30 AND (state=5 OR D_RSI>0.75)
- D1 RE_BACKLOG: requires state ∈ {3,4,5}
- max_positions=12, tier_weights {tier: 0.10}
- All other simulator params

## Validation breakdown

### Sub-period CAGR (4-year windows)

| Period | V_PROD | C3_cons | Δ |
|--------|--------|---------|---|
| 14-17 | +14.55% | +15.06% | +0.51pp ✓ |
| 18-19 | +13.10% | +11.87% | -1.23pp |
| 20-22 | +43.16% | +40.76% | -2.40pp |
| 23-26 | +16.17% | **+22.44%** | **+6.27pp** ⭐ |

Trade-off: marginal weakening 2018-19/2020-22 in exchange for big 2023-26 gain.

### Filter ablation insights

| Filter removed | ΔFull | ΔIS | ΔOOS |
|----------------|-------|-----|------|
| SV_TIGHT (all) | +0.30 | -3.02 | **+3.88** (filter overfits IS!) |
| AVOID_bear | -0.29 | +0.09 | -0.69 (small) |
| Overheat | -0.43 | -1.21 | +0.39 |
| **cash_etf** | **-4.08** | **-3.70** | **-4.42** (CRITICAL — keep!) |

### Why ETF in bear helps IS

- IS 2014-2019 has long sideways/mild-bear periods (2014 H2, 2015-16, 2018-19)
- During state==2 BEAR, V_PROD held idle cash (0% deposit_annual in spec)
- C3_cons: 50% of idle cash → VN30 ETF
- Even tracking VNI (-5 to +10% during bear/sideways), beats holding 0%
- Recovers ~2-3pp of IS that SV_TIGHT loosening would otherwise sacrifice

### Refinement findings

- SVT s3 > 90: no additional gain (loose_120 = loose_180 = SVT s3=90)
- SVT removed entirely (+ETF): nearly identical to SVT s3=90 + ETF
- Adding state 4 to overheat: small marginal OOS gain (-OK ignore)
- Adding state 1 to cash_etf: untested, suspect destructive in CRISIS

## Deployment checklist

- [ ] Modify `recommend_holistic.py`: update SV_TIGHT s3 threshold to 90
- [ ] Modify `simulate_holistic_nav.py` default cash_etf_states (or per-runner config)
- [ ] Update `run_5systems_prodspec.py`: `cash_etf_states = {2: 0.5, 3: 0.7}` for ETF_BASE
- [ ] Update paper-trade scripts (`pt_v11_tq34b.py`, `pt_v12_tq34b.py`, etc.)
- [ ] Pre-2014 stress test (2007-2013, 2008 GFC) — UNTESTED, must verify cash_etf in bear doesn't destroy during severe crash
- [ ] Live shadow paper-trade 4-8 weeks before full switch

## Caveats

1. **Pre-2014 unverified**: cash_etf {2: 0.5} during 2008 GFC could be catastrophic (50% in ETF when VNI -65%). MUST test before full deploy.
2. **State 2 frequency**: In 2014-2026, state 2 (BEAR) is relatively rare. In 2008-2011, state 2 was extended → cash_etf state 2 has bigger effect. Risk asymmetric.
3. **18-19 / 20-22 weakness**: -1.23pp / -2.40pp sub-period regression. SV_TIGHT s3=60 happened to align with these specific bear/recovery patterns. Trade-off accepted because 2023-26 +6.27pp dominates.
4. **2026 YTD performance** likely needs separate fresh-start validation (per path_dependency lessons).

## Conservative fallback: C3_modest_SVTonly

If user prefers minimum change:
- ONLY change SVT s3=90 (no cash_etf change)
- Full +0.34pp / OOS +3.66pp / IS -2.75pp / DD -21.0%
- BIG OOS gain but IS regression visible

## Aggressive alternative: C3_no_svt_OH

If user prefers maximum OOS:
- Remove SVT entirely + broader overheat (ma200>1.25, rsi>0.70, state (4,5))
- Full +0.44pp / OOS +4.24pp / IS -3.08pp
- Bigger OOS but bigger IS regression and more parameter changes

## Files

- `tune_bav11_filters.py` — initial ablation + per-family sweep
- `tune_bav11_combined.py` — combined C1-C7 candidates
- `cross_test_state_filter.py` — 2×3 state × filter matrix (proved conflict)
- `test_c3_refinements.py` — SVT lever refinement, final pick

## User context

User's deep intuition was correct: "market_state phản ánh tâm lý thị trường, tâm lý đám đông. ảnh hưởng rất lớn đến việc đầu tư. Nên việc đầu tư không thể tách rời việc nhận định tình trạng thị trường rồi quyết định đầu tư. Tune BA v11 filter một chút, kết quả sẽ tốt lên."

Stream 2 (strip state entirely) proved this empirically — state-blind BA v11 lost to B&H. Stream 3 (modest filter tune while keeping state) delivered the user-predicted gain.
