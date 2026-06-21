# Kelly Q3 — per-tier slot-weight test results

**Date**: 2026-05-21  
**Sim**: V11 canonical 12y, 2014-01-02 → 2026-04-03, init NAV 50B, T+1 Open exec, real E1VFVN30 ETF  
**Config**: max_pos=12, sector cap 8:4, RE_BACKLOG_BUY exempt, SV_TIGHT + P3 active, V6 ETF (state 3 = 70% idle cash)  
**No production code modified.**

## Stage 1 — fresh canonical trade log

Re-ran the V11 stack with **flat 10%** baseline weights to produce a trade log carrying current `TIER_BAL` labels (the existing `ba_trades_bal_refresh.csv` only had 4 legacy SCORE_V10 labels — MEGA / S_PRO / MOMENTUM_QUALITY / COMPOUNDER_BUY / RE_BACKLOG_BUY were absent).

Output: `ba_trades_v11_tier_labels.csv` — **537 trades** across **6 distinct tiers**.


## Stage 2 — per-tier stats and Kelly fit

Per-tier statistics (sorted by Kelly_continuous = mu / sigma**2):

| tier | n | WR % | avg_win % | avg_loss % | mean_ret % | sd_ret % | Sharpe/trade | Kelly_c | current | **proposed** | Δ pp | note |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| MOMENTUM_N | 45 | 68.9 | 25.98 | 8.58 | 15.23 | 26.61 | 0.572 | 2.151 | 10.0% | **10.00%** | +0.00 |  |
| MOMENTUM_S | 74 | 73.0 | 31.64 | 14.32 | 19.22 | 32.75 | 0.587 | 1.791 | 10.0% | **10.00%** | +0.00 |  |
| MOMENTUM | 14 | 71.4 | 33.00 | 17.07 | 18.70 | 34.72 | 0.538 | 1.551 | 10.0% | **10.00%** | +0.00 | small_n_keep_flat_30 |
| DEEP_VALUE_RECOVERY | 293 | 52.6 | 22.87 | 13.20 | 5.76 | 25.08 | 0.230 | 0.916 | 10.0% | **10.00%** | +0.00 |  |
| RE_BACKLOG_BUY | 109 | 50.5 | 20.69 | 11.25 | 4.87 | 24.85 | 0.196 | 0.788 | 10.0% | **10.00%** | +0.00 |  |
| MEGA | 2 | 50.0 | 14.70 | 16.01 | -0.65 | 21.71 | -0.030 | -0.139 | 10.0% | **10.00%** | +0.00 | small_n_keep_flat_30 |

**Normalization procedure** (per spec §2.3):  
`raw_w = 0.10 × (Kelly_c / mean(Kelly_c)) × 0.25` → clip `[4%, 18%]` → rescale so `Σ(n × w) = Σ(n × 0.10)` (preserves total gross exposure — pure redistribution).  
Tiers with `n < 30` kept at flat **10%**.

## Stage 3 — side-by-side sim results

| Period | Variant | CAGR | Sharpe | MaxDD | Calmar | Final NAV (B) | Wealth × | n_trades |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| FULL 2014-2026 | FLAT  | +15.84% | 1.12 | -22.6% | 0.70 | 302.87 | 6.06× | 537 |
| FULL 2014-2026 | KELLY | +15.84% | 1.12 | -22.6% | 0.70 | 302.87 | 6.06× | 537 |
| FULL 2014-2026 | **Δ K−F** | **+0.00pp** | **+0.00** | **+0.0pp** | – | – | – | +0 |
| Pre-OOS 2014-19 | FLAT  | +7.34% | 0.78 | -21.4% | 0.34 | 76.43 | 1.53× | 172 |
| Pre-OOS 2014-19 | KELLY | +7.34% | 0.78 | -21.4% | 0.34 | 76.43 | 1.53× | 172 |
| Pre-OOS 2014-19 | **Δ K−F** | **+0.00pp** | **+0.00** | **+0.0pp** | – | – | – | +0 |
| OOS 2024-2026 | FLAT  | +18.29% | 1.10 | -18.7% | 0.98 | 302.87 | 6.06× | 130 |
| OOS 2024-2026 | KELLY | +18.29% | 1.10 | -18.7% | 0.98 | 302.87 | 6.06× | 130 |
| OOS 2024-2026 | **Δ K−F** | **+0.00pp** | **+0.00** | **+0.0pp** | – | – | – | +0 |

## Per-tier deployment in PROPOSED (Kelly) sim

Rough contribution proxy = Σ(ret_net) × tier_weight × 100 (in pp-trade units; cost-basis weighting not available without re-running with per-trade size logging).

| tier | n_trades | mean_ret % | weight | pnl_proxy | share % |
|---|---:|---:|---:|---:|---:|
| DEEP_VALUE_RECOVERY | 293 | +5.76 | 10.00% | +168.72 | +36.8% |
| MOMENTUM_S | 74 | +19.22 | 10.00% | +142.20 | +31.0% |
| MOMENTUM_N | 45 | +15.23 | 10.00% | +68.51 | +14.9% |
| RE_BACKLOG_BUY | 109 | +4.87 | 10.00% | +53.03 | +11.6% |
| MOMENTUM | 14 | +18.70 | 10.00% | +26.17 | +5.7% |
| MEGA | 2 | -0.65 | 10.00% | -0.13 | -0.0% |

## Verdict — **YELLOW**

OOS 2024-2026 gate (per spec §4.2):

- ΔCAGR  = **+0.00 pp**  (gate ≥ +0.5pp)  FAIL
- ΔSharpe = **+0.00**  (gate ≥ +0.05)  FAIL
- ΔMaxDD = **+0.0 pp**  (gate ≥ −1.5pp; positive = better)  PASS

### Tiers kept at flat 10% (n < 30)

- `MOMENTUM` (n=14)
- `MEGA` (n=2)

## Files

- `ba_trades_v11_tier_labels.csv` — fresh 12y trade log with current tier labels
- `kelly_q3_tier_stats.csv` — per-tier WR/mean/sd/Kelly_c
- `kelly_q3_tier_weights.csv` — proposed weights with sample-size notes
- `test_kelly_q3_tier_weights.py` — this script (no production code touched)
- `kelly_q3_out/_sim_nav_flat.csv`, `_sim_nav_kelly.csv` — daily NAV curves
- `kelly_q3_out/_sim_trades_flat.csv`, `_sim_trades_kelly.csv` — trade-level results
- `kelly_q3_out/_sim_results.csv` — summary table