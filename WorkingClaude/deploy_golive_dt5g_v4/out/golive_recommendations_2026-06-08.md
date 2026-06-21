# V4 + DT5G — Daily Recommendations — 2026-06-08

*Generated 2026-06-08 15:42. System: V121_ENS + BASE parking, gated DT5G state (fail-safe DT4). Sizing 10% NAV/slot, max 12, hold 45d, stop -20%.*

## Regime & parking

- **Market state (gated):** 3 = **NEUTRAL**  (source: DT5G_macro; DT4 base=3, DT5G=3)
- **ETF parking target (BASE):** park **70%** of idle cash in E1VFVN30 (NEUTRAL)
- **Ensemble mode today:** VN30 (V11-mode) → 2nd-leg book = **VN30**

## BAL book (always-on 50%) — 1 picks

| ticker | tier | ta | close | sector | weight |
|---|---|---:|---:|---:|---:|
| PSI | MOMENTUM_N | 166 | 9000.0 | 8 | 10% |

_Informational (signals today OUTSIDE V4 BAL tiers, not traded by V4):_ DRI(COMPOUNDER_BUY), NCT(COMPOUNDER_BUY), VVS(COMPOUNDER_BUY)

## 2nd leg = VN30 book (50%) — 0 picks

_(no eligible VN30 signals today)_

## Notes
- Position sizing: 10% NAV per slot, BASE parking keeps ~30% cash buffer in NEUTRAL.
- Fin/RE (sector 8) capped at 4 positions per book (RE_BACKLOG_BUY exempt).
- This is the V4 (BASE) config. State is the fail-safe gated series; if macro feeds were unhealthy the source would read 'DT4_only'.
- CSV: `out/golive_recommendations_2026-06-08.csv`