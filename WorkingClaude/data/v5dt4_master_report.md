# V5 + DT4(4-gate) — Transparent Simulation Report

*Generated 2026-05-28 22:09*  |  Period **2025-01-02 → 2026-05-15**  |  init **50B** (25B BAL + 25B 2nd leg)

V5 = V121_ENS + KELLY parking on the DT4 (`vnindex_5state_dt_4gate`) foundation. Mirrors `run_5systems_dt4.py` V5 exactly; adds transparent per-leg trade logs.

## Headline

| System | CAGR | Sharpe | MaxDD | Calmar | TotRet | Final NAV |
|---|---|---|---|---|---|---|
| **V5+DT4 (ensemble)** | +42.27% | +1.87 | -13.85% | +3.05 | +61.71% | 80.86B |
| VNINDEX B&H | +35.52% | +1.52 | -18.11% | +1.96 | +51.34% | 75.67B |

### Underlying leg performance (standalone, each 25B book)

| Leg | CAGR | Sharpe | MaxDD | Final NAV |
|---|---|---|---|---|
| BAL_kelly | +25.95% | +1.10 | -18.56% | 34.19B |
| VN30_kelly | +48.06% | +2.01 | -14.67% | 42.63B |
| LAGGED_v121 | +25.81% | +1.38 | -14.40% | 34.19B |

## Per-leg trade reconciliation (4 gates — every delta must be ~0)

| Leg | G2 NAV-identity (max abs) | G3a ΣMTM stocks vs positions_mv | G3b ΣMTM ETF vs cash_etf | G1 cash residual* | G4 open↔buy match | pending (in-flight) | real tx |
|---|---|---|---|---|---|---|---|
| bal_kelly | 0.00 | 0.00 | 0.00 | -0.0005B | PASS | 0.572B | 318 |
| vn30_kelly | 0.00 | 0.00 | 0.00 | -0.0014B | PASS | 0.000B | 88 |
| lagged_v121 | 0.00 | 0.00 | 0.00 | +0.0000B | PASS | 0.000B | 112 |

*G1 cash residual = `end_cash − (init − buys−fees + sells−fees)`. For LAGGED (no ETF) this is ~0. For BAL/VN30 it equals ETF appreciation that the KELLY rebalance moved out of `cash_etf` into `cash` — expected & explained, NOT an error; the strict daily NAV identity (G2) is the binding gate and is ~0.

## Ensemble construction (the part that is NOT trade-reconcilable)

- V5 daily NAV identity gate (V5 == BAL_path + second_leg): **max abs = 0.0000 VND** (≈0).

- The **switch** between VN30_kelly and LAGGED_v121 is applied at the **return level** (`second_leg[t] = second_leg[t-1]·(1±switch_cost)·(1 + r_active)`), NOT by moving actual share lots. So the 2nd-leg book that is *inactive* on a given day still has real, logged trades in its own CSV, but those trades are not 'realized' by V5 that day. This is the documented idealization (`[[v5-prodspec-integrity-audit]]` 'independent-leg recombine'). Trade-level truth lives in each leg's CSV; the ensemble overlay is a return-path construct, verified only via the NAV identity above.

- Switches over period: **4** flips; days in VN30 = 294, days in LAGGED = 42.

## Files

- **bal_kelly**: `data\v5dt4_bal_kelly_logs.csv`, `data\v5dt4_bal_kelly_transactions.csv`, `data\v5dt4_bal_kelly_open_positions.csv`, `data\v5dt4_bal_kelly_report.md`
- **vn30_kelly**: `data\v5dt4_vn30_kelly_logs.csv`, `data\v5dt4_vn30_kelly_transactions.csv`, `data\v5dt4_vn30_kelly_open_positions.csv`, `data\v5dt4_vn30_kelly_report.md`
- **lagged_v121**: `data\v5dt4_lagged_v121_logs.csv`, `data\v5dt4_lagged_v121_transactions.csv`, `data\v5dt4_lagged_v121_open_positions.csv`, `data\v5dt4_lagged_v121_report.md`
- **ensemble**: `data\v5dt4_ensemble_logs.csv`