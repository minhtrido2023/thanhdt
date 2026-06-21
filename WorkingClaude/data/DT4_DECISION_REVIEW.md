# ⭐ DECISION DUE — DT 4-gate vs TQ34b (V12 paper-trade A/B)

*Reminder fired: 2026-05-28 14:55*

You set this checkpoint to decide whether to switch the V12 paper-trade system
from TQ34b to the DT 4-gate state. Below is the latest A/B from ~3 months of
live paper-trade (Apr 1 → end June 2026).

**How to decide:**
- 🟢 SWITCH  → DT 4-gate held its backtested edge (+1.06pp). To promote: point
  pt_v12_tq34b.py's state source to DT (or retire it for pt_v12_dt4.py), and
  consider promoting `tav2_bq.vnindex_5state_dt_4gate` to LIVE `vnindex_5state`.
- 🟡 HOLD    → keep both arms running, revisit later.
- 🔴 KEEP TQ → DT underperformed live; stay on TQ34b.

Full report: `data/papertrade_compare5.md`

---

## V12_DT4 vs V12_TQ34b — DT 4-gate A/B (DECISION: end June 2026) ⭐

- Backtest expectation (12y): DT 4-gate +1.06pp Full CAGR on V12, DD ≈ neutral.
- ΔRet (window)  = **+1.33pp**
- ΔDD  (window)  = **-0.01pp**  (positive = DT shallower DD)
- ΔSharpe        = **-0.03**
- Verdict: **🟢 SWITCH to DT**
- ⚠️ Short window — treat as directional only; confirm with full June data before switching.


---

## Headline metrics

| System | Final NAV | Total Ret | CAGR | Vol (ann) | Sharpe | Max DD | Calmar |
|---|---|---|---|---|---|---|---|
| **V11 Song Sinh + KELLY + DT_10_25_25 ⭐** | 55.139B | +10.44% | +112.96% | 23.80% | +3.51 | -2.61% | +43.33 |
| **V12 Âm Dương (BAL+LAGGED) + TQ34b** | 50.848B | +1.70% | +11.82% | 4.73% | +2.51 | -1.32% | +8.97 |
| **V12 Âm Dương + DT 4-gate (SHADOW A/B) ⭐** | 51.487B | +3.03% | +21.90% | 8.54% | +2.49 | -1.32% | +16.56 |
| **V12.1 Ensemble (M1+M3r AND-HOLD) + BASE** | 52.442B | +4.88% | +43.75% | 8.21% | +4.76 | -1.30% | +33.52 |
| **V12.1 Ensemble + Kelly NEUTRAL{3:1.0}** | 53.303B | +6.61% | +62.71% | 10.37% | +5.07 | -1.81% | +34.60 |
| **VNINDEX Buy & Hold (rebased 50B)** | 55.322B | +10.64% | +95.75% | 17.48% | +4.14 | -2.64% | +36.33 |

