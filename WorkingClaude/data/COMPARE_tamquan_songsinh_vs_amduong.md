# Tam Quan v3.1 + Song Sinh (V11) vs Tam Quan v3.1 + Âm Dương (V12)
## Simulation 2025-06-09 → 2026-05-19 (50B NAV)

### Defaults applied (per user spec 2026-05-20)
- Transparent pattern: `sim_v11_transparent.py` / `sim_v12_transparent.py` clones (`sim_v11_tamquan.py`, `sim_v12_tamquan.py`).
- `event_log` + `etf_log` emitted, `force_close_eod=False`, MTM phantoms appended.
- 4 CSV outputs per sim: `*_logs.csv`, `*_transactions.csv`, `*_open_positions.csv`, `*_report.md`.
- `analyze_portfolio.py` run on both.
- 4-gate reconciliation passes on both (cash trajectory from tx CSV matches end_cash to 0.000B; NAV = cash + cash_etf + stocks_mv every day; MTM totals match buckets).

### State source swap
Only difference vs production sims: `tav2_bq.vnindex_5state` → `tav2_bq.vnindex_5state_tam_quan_v31_clean` (Tam Quan v3.1 staging).
- T+1 Open execution canonical
- Real `E1VFVN30` ETF prices (no proxy)
- Layer 3 v4 HYBRID BUY (ATC T1_TOP / T1115 non-TOP / fallback OPEN)
- Sell at T+1 09:00 Open
- 10% NAV fixed sizing × 12 slots
- Live state cached up to 2026-05-12 (intraday); BQ ticker cached up to 2026-05-19

### Headline results (4-way, same window 2025-06-09 → 2026-05-19, 0.94 years)

| Sim                         | Final NAV  | Return  | CAGR    | Sharpe | Sortino | MaxDD   | Calmar |
|-----------------------------|-----------:|--------:|--------:|-------:|--------:|--------:|-------:|
| V11 Song Sinh + LIVE Tinh Tế | 59.94 B    | +20.00% | +21.36% | 1.050  | 1.310   | -13.51% | 1.581  |
| **V11 Song Sinh + TAM QUAN v3.1** | **58.61 B** | **+17.23%** | **+18.38%** | **1.018** | **1.242** | **-16.15%** | **1.138** |
| V12 Âm Dương  + LIVE Tinh Tế | 53.02 B    | +6.09%  | +6.48%  | 0.440  | 0.508   | -11.84% | 0.547  |
| **V12 Âm Dương  + TAM QUAN v3.1** | **51.24 B** | **+2.47%** | **+2.62%** | **0.241** | **0.268** | **-14.21%** | **0.185** |

### Δ Tam Quan v3.1 vs LIVE Tinh Tế (same BA stack)
| Stack      | ΔCAGR    | ΔSharpe | ΔMaxDD  |
|------------|---------:|--------:|--------:|
| V11        | **-2.97pp** | -0.032 | -2.64pp |
| V12        | **-3.86pp** | -0.199 | -2.36pp |

Tam Quan v3.1 underperforms LIVE on this 11-mo window for both stacks — it is **more cautious**: holds NEUTRAL state 3 longer and downgrades from BULL earlier. In a bull-heavy period this costs CAGR and adds drawdown via late re-entry. Expected behavior of the US-shock override + dual-blend dampening.

### Δ Âm Dương vs Song Sinh (same state source)
| State src | ΔCAGR    | ΔSharpe | ΔMaxDD  |
|-----------|---------:|--------:|--------:|
| LIVE      | -14.87pp | -0.609  | +1.66pp |
| Tam Quan  | -15.76pp | -0.777  | +1.95pp |

V12's LAGGED leg essentially stayed flat in this window (final 24.99 B from 25 B init, 0 open positions at end), confirming the memory note "Y2025 bull -16.59pp vs v11" for Âm Dương. The LAGGED HL_3y signal is structurally defensive and underperforms in strong bulls — when the BAL leg + VN30 (V11) rides BULL via VN30 ETF parking, V12 leaves that upside on the table.

### State coverage divergence (235 trading days)
| State | LIVE Tinh Tế | Tam Quan v3.1 |
|-------|-------------:|--------------:|
| 1 (CRISIS)  | 6 d (3%)   | 6 d (3%)   |
| 2 (BEAR)    | 12 d (5%)  | 19 d (8%)  |
| 3 (NEUTRAL) | 103 d (44%) | **128 d (54%)** |
| 4 (BULL)    | 65 d (28%) | 42 d (18%) |
| 5 (EX-BULL) | 49 d (21%) | 40 d (17%) |

Days where states differ: **64 / 235 (27%)**. Major divergences:
- 2025-12-25 → 2026-01-22 (29 d): LIVE BULL vs TQ NEUTRAL — TQ downgraded earlier as US sold off late Dec
- 2026-05-06 → 2026-05-19 (14 d): LIVE BULL vs TQ NEUTRAL — TQ in NEUTRAL today (matches memory: "State today (2026-05-20): NEUTRAL")
- 2026-04-03 → 2026-04-09 (7 d): LIVE NEUTRAL vs TQ BEAR — TQ caught Q1-2026 sell-off one notch deeper

### Reconciliation (4-gate verification, both sims)
| Check                                              | V11+TQ | V12+TQ |
|----------------------------------------------------|:------:|:------:|
| Cash trajectory from tx CSV = end_cash             | PASS (0.0000B) | PASS (0.0000B) |
| Daily NAV = cash + cash_etf + stocks_mv            | PASS   | PASS   |
| MTM totals match bucket (stocks/ETF)               | PASS   | PASS   |
| Final NAV (sim) = cash + ETF + open_stock_MTM      | PASS (58.6127B) | PASS (51.2351B) |

### Files produced
```
data/v11_tq_logs.csv             data/v12_tq_logs.csv
data/v11_tq_transactions.csv     data/v12_tq_transactions.csv
data/v11_tq_open_positions.csv   data/v12_tq_open_positions.csv
data/v11_tq_report.md            data/v12_tq_report.md
data/v11_live_logs.csv           data/v12_live_logs.csv         (baseline)
data/v11_live_transactions.csv   data/v12_live_transactions.csv (baseline)
data/COMPARE_tamquan_songsinh_vs_amduong.md  (this file)
```

### Read it like this
1. **Tam Quan v3.1 is more cautious than LIVE on bull windows.** In this 11-month, mostly-BULL period it cost both stacks ~3-4pp CAGR. The memory note "FULL CAGR 19.33% vs LIVE 18.47% (+0.35pp)" is on a 12-year span where the US-shock override saves it in 2008/2022. Don't expect a single bull window to show that gain.
2. **Song Sinh dominates Âm Dương on this window — regardless of state source.** LAGGED is structurally weaker in bulls; if you expect another bull leg, stay on V11. The v12.1 "Âm Dương Tinh Tế" (S2 sizing modulation) memory note shows Y2022 +0.50% bull-defensive — that hedge value doesn't appear in a window dominated by uptrend.
3. **The 2-week shadow-track guideline on Tam Quan v3.1 still holds.** This run is consistent with "more cautious in bulls, better in shocks" — wait for at least one real stress to validate the promote.
