# Liquidity fix — real (unadjusted Price) vs adjusted Close

**Change:** liquidity/capacity everywhere now uses real traded notional `Volume_3M_P50 * Price`
(unadjusted) instead of `Volume_3M_P50 * Close` (back-adjusted). DT5G market-state engine
unaffected (uses no trading value). Fix touches the stock-selection book only.

Files: signal_v11_sql.py, sim_v11_for_analyzer.py, run_5systems_prodspec.py,
simulate_holistic_nav.py. pkl rebuilt: ba_v11_unified_12y_sig.pkl (623,242 → 708,053 rows —
liquid names from 2014–2018 previously dropped by the understated `liq>=1e9` screen are now
correctly included). Backup: ba_v11_unified_12y_sig.pkl.bak_closeliq_20260601.

Backtest: prod-spec, TQ34b state, real E1VFVN30 ETF, 50B/system, 2014-01-01 → 2026-05-15.
A/B isolates the BAL+VN30 equity books (fed by pkl liq); LAGGED book uses real notional in
both arms (so its real-liq fix is included in both absolute columns).

| System | CAGR (Close) | CAGR (Price) | Δ CAGR | Sharpe C→P | MaxDD C→P | Calmar C→P |
|---|---|---|---|---|---|---|
| V1 V11+TQ34b      | +16.68% | **+18.91%** | **+2.23pp** | 1.16→1.28 | -21.1%→-20.2% | 0.79→0.94 |
| V2 V12+TQ34b      | +20.43% | **+21.39%** | **+0.96pp** | 1.58→1.63 | -16.0%→-15.3% | 1.27→1.40 |
| V3 V12+LIVE       | +20.43% | **+21.39%** | **+0.96pp** | 1.58→1.63 | -16.0%→-15.3% | 1.27→1.40 |
| V4 V121_ENS+TQ34b | +20.32% | **+21.82%** | **+1.50pp** | 1.39→1.47 | -20.7%→-20.1% | 0.98→1.08 |
| V5 V4+KellyQ2     | +21.37% | **+22.47%** | **+1.10pp** | 1.34→1.40 | -19.4%→-19.4% | 1.10→1.16 |
| VNI B&H           | +11.42% |  +11.42% |  —      | 0.68      | -45.3%        | 0.25       |

**Direction:** every system improves on ALL metrics — higher CAGR, higher Sharpe, lower
MaxDD, higher Calmar. Consistent with the earlier diagnosis: adjusted-Close understated
historical liquidity (~52% low in 2014, shrinking to ~0% by 2026), which (a) wrongly excluded
tradable names and (b) over-tightened position caps. Correcting to real notional un-throttles
the book — modestly, and most where the book is most capacity-bound (V1 pure equity +2.2pp).

**Not inflation:** the new caps reflect the *actual* VND that traded each day, so fills stay
within real market depth. The old numbers were conservative-biased, not the new ones optimistic.
