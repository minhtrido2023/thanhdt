# BA v12 "Âm Dương" — Production Spec & Deployment Guide

**Status**: ✅ Backtest validated, walk-forward stable, capacity tested — **Ready for deployment**
**Date**: 2026-05-20
**Version**: v12 (Âm Dương ☯️) — replacing v11 (Song Sinh 🐦)

---

## Executive summary

| Metric | v11 Song Sinh | **v12 Âm Dương** | Improvement |
|---|---|---|---|
| 12y CAGR | 19.42% | **21.37%** | +1.95pp ✅ |
| Sharpe | 1.32 | **1.67** | +26% ✅ |
| MaxDD | −19.00% | **−14.92%** | +22% better ✅ |
| Calmar | 1.02 | **1.43** | +40% ✅ |
| Final wealth (50B init) | 8.98x | **10.96x** | +22% ✅ |
| Y2022 bear | −12.95% | **−3.07%** | +9.88pp defensive ✅ |
| Y2025 bull | +46.48% | +29.88% | **−16.59pp** ⚠️ (trade-off) |
| Annual win rate (vs v11) | — | 8/12 years | 67% |

**Core change**: Replace VN30 book (highly correlated với BAL) by LAGGED HL_3y (corr ~0.30 → diversification).

---

## Architecture

```
TOTAL NAV (50B baseline)
├─ 25B → BA v11 BAL book  (ticker_prune universe, sec_lim Fin/RE max 4)
├─ 25B → LAGGED HL_3y     (earnings post-release drift)
└─ V6 ETF parking (70% idle cash → VN30 in NEUTRAL state) on BAL leg
```

### Book A: BAL (BA v11 score)
- Universe: `tav2_bq.ticker_prune` (~500 tickers)
- Signal: SIGNAL_V11_UNIFIED (SV_TIGHT Fresh-Q built-in) + P3 overheat filter
- Tiers: MEGA, MOMENTUM, MOMENTUM_N, MOMENTUM_S, DEEP_VALUE_RECOVERY
- Position: max 10, hold 45d, stop −20%, slip 0.1%, sector limit Fin/RE max 4
- ETF parking: 70% idle cash → VN30 ETF in NEUTRAL state (state 3)
- Code: `recommend_holistic.py` select_book()

### Book B: LAGGED HL_3y ⭐ NEW
- Universe: tickers with `prior_avg_post_good_HL3y ≥ 5%` AND `prior_n_good ≥ 4`
- Profile: exp decay weight (half-life 3y) on prior good-earnings post-release returns
- Signal: New release with NP_R ≥ 15% + ticker in universe + liquidity ≥ 2B/day
- Entry: T+5 trading days after Release_Date (at Open)
- Exit: T+30 trading days (= 25d hold), at Open
- Position: max 12, sizing 8% NAV
- Friction: slip 0.1/0.15%, tax 0.1%, liq cap 20% ADV × 5d
- Deposit: 1%/yr cash idle
- Code: `lagged_pos_papertrade.py` (production-ready)

---

## Performance breakdown

### Period analysis (50B init, 12y backtest)

| Period | v12 CAGR | v12 Sharpe | v12 DD | vs v11 | vs VNI |
|---|---|---|---|---|---|
| FULL 2014-2026 | +21.37% | 1.67 | −14.92% | +1.95pp | +9.95pp |
| Pre-OOS 14-19 | +13.58% | 1.43 | −11.72% | +1.20pp | +2.23pp |
| Mid 2018-23 | **+26.17%** | **1.82** | −14.92% | +3.42pp | **+24.04pp** |
| OOS 2024-26 | +21.06% | 1.53 | −10.59% | −1.52pp | −4.02pp |
| **Y2022 bear** | **−3.07%** | −0.28 | −11.06% | **+9.88pp** | **+31.32pp** |
| Y2025 bull | +29.88% | 1.89 | −8.62% | −16.59pp | −10.96pp |
| Q1 2026 | −1.89% | −0.07 | −9.14% | +2.51pp | +20.00pp |

### Walk-forward validation (Option 1 confirmed)

| Window | v11 CAGR | v12 CAGR | Δ |
|---|---|---|---|
| FULL 14-26 | 19.42% | **21.37%** | +1.95 |
| P1_IS 14-18 | 14.16% | 15.38% | +1.22 |
| P2_OOS 19-26 | 23.18% | **25.65%** | +2.48 |
| P3_IS 14-20 | 17.60% | 17.60% | +0.00 |
| P4_OOS 21-26 | 21.29% | **26.22%** | +4.94 |
| P5_IS 14-22 | 20.50% | 22.30% | +1.80 |
| P6_OOS 23-26 | 15.80% | **18.56%** | +2.76 |

→ v12 wins Sharpe + DD on 7/7 windows. CAGR wins 6/7 (P3 tied).

### Capacity scaling

| Total NAV | CAGR | Sharpe | DD | LAGGED capped% |
|---|---|---|---|---|
| **50B (optimal)** | **21.37%** | **1.67** | −14.92% | 33% |
| 100B | 18.93% | 1.56 | −12.21% | 55% |
| 200B | 16.11% | 1.49 | −11.97% | 70% |
| 400B | 14.59% | 1.39 | −11.17% | 82% |

**Sweet spot**: 50-100B per Option 1 instance. Above 200B: returns diminish materially.

---

## Production deployment guide

### Pre-deployment checklist

- [ ] BA v11 production already running (`recommend_holistic.py`) — confirmed ✅
- [ ] LAGGED HL_3y backtested + validated lookahead-free — confirmed ✅
- [ ] Paper-trade running since 2026-04-01 — confirmed ✅
- [ ] Memory + spec documented — confirmed ✅
- [ ] Capital allocation decided (recommend 25B BAL + 25B LAGGED = 50B)

### Implementation steps

**Step 1: Reduce v11 VN30 allocation to zero**
- Stop new buys in VN30_BAL book
- Wait for existing VN30 positions to exit via stop/time-trigger (~45d hold)
- OR liquidate manually if want fast switch

**Step 2: Start LAGGED book at 25B**
- Run `lagged_pos_papertrade.py` (already production-ready)
- Confirm daily run schedule:
  - 15:30 VN time daily → fetch new releases, scan signals
  - Output: pending entries for T+1, pending exits for T+1
  - Execute next trading day at Open

**Step 3: Daily operations**

```bash
# Daily run (suggested 15:30 VN time after market close)
python lagged_pos_papertrade.py --start <deployment_start_date>

# Outputs:
#   lagged_paper_nav.csv         — NAV history
#   lagged_paper_trades.csv      — all events
#   lagged_paper_positions.csv   — current open
#   lagged_paper_state.json      — summary
```

**Step 4: Monthly review**
- Check NAV vs VNI + vs v11 baseline
- Verify trade execution alignment (paper vs live)
- Review pattern: bull-year underperform OK, bear-year MUST outperform

### Risk warnings

⚠️ **Strong bull markets**: v12 will underperform v11 by ~10-15pp in years like 2025
⚠️ **Capacity ceiling**: above 200B total NAV, returns degrade significantly
⚠️ **Paper-trade current (49d)**: NAV −1% vs VNI +12%, but only 4 closes — too small sample
⚠️ **Universe relies on FA history**: new IPOs need 1-2 years before qualifying

### Execution timing rules

| Action | Trigger | Execution |
|---|---|---|
| BA buy signal | T close, recommend_holistic.py | T+1 14:45 ATC (T1_TOP) or 11:15 (non-TOP) |
| BA sell trigger | T close, stop/time | T+1 Open |
| LAGGED entry | Release_Date + 5 trading days | T+5 Open |
| LAGGED exit | Release_Date + 30 trading days | T+30 Open |

---

## Strategic positioning

### When v12 outperforms v11

✅ Bear markets (Y2022 +9.88pp)
✅ Sideways markets (Y2023 +11.78pp, Y2024 +9.14pp)
✅ Recovery from crashes (Q1 2026 +2.51pp)
✅ Mid-cycle periods (Mid 2018-23 +3.42pp)

### When v12 underperforms v11

❌ Strong momentum bull rallies (Y2017 −7.96pp, Y2020 −9.53pp, Y2025 −16.59pp)
❌ Late-cycle bull continuation
❌ Universe-wide rallies (LAGGED's mid/small-cap bias misses large-cap rotation)

### Decision framework

| Scenario | Recommended action |
|---|---|
| Bear/sideways expected | Deploy v12 full 50/50 |
| Strong bull expected | Use v12 light (BAL40_LAG10) — preserve momentum |
| Uncertain regime | Default to v12 (mathematically optimal Sharpe) |
| Large NAV (>200B) | Stick with v11 + add v12 to smaller bucket |

---

## Open items / future research

1. **Dynamic weighting**: heavy LAGGED in BEAR, heavy BAL in BULL (v13 candidate)
2. **Larger v12 universe**: relax POST_RET_MIN to 3% → wider pool (test pending)
3. **LAGGED capacity beyond liq_cap**: explore allowing partial fills over more days
4. **F-system integration**: VN30F derivatives as 3rd book (v13 idea)
5. **Sector-aware LAGGED**: weight tickers by sector cycle position
6. **Multi-time-horizon LAGGED**: combine T+5→T+30 with T+30→T+60 drift

---

## File references

| File | Purpose |
|---|---|
| `recommend_holistic.py` | Production BA v11 scanner (BAL book) |
| `lagged_pos_papertrade.py` | Production LAGGED scanner (LAGGED book) |
| `simulate_holistic_nav.py` | Backtest engine for BA book |
| `validate_lagged_hl3y.py` | LAGGED HL_3y walk-forward validation |
| `verify_hl3y_no_lookahead.py` | Lookahead verification |
| `test_ba_v11_production_12y.py` | v11 production baseline backtest |
| `test_option1_bal_lagged.py` | v12 architecture validation |
| `validate_option1_walkforward.py` | v12 walk-forward validation |
| `test_capacity_option1.py` | v12 capacity scaling |
| `earnings_events_classified.csv` | 52,950 classified events |
| `ba_v11_unified_12y_sig.pkl` | BA v11 signal cache |

---

## Quick reference card

```
v12 "Âm Dương" deploy summary
─────────────────────────────────────
Architecture:  BAL@25B + LAGGED@25B + V6 ETF
Total NAV:     50B (optimal)
Expected:      CAGR 21.4% / Sh 1.67 / DD -15%
Y2022 hedge:   +9.88pp vs v11
Y2025 cost:    -16.59pp vs v11 (trade-off)
12y wealth:    10.96x (vs v11 8.98x)
Scaling:       Sweet spot 50-100B; degrades >200B
─────────────────────────────────────
```
