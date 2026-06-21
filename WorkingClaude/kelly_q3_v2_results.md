# Kelly Q3 v2 — FLAT 10% vs PROPOSED tier weights (no rescale collapse)

**Date**: 2026-05-23
**Stack**: BA v11 full | 50/50 BAL+VN30 | V6 ETF (NEUTRAL 70%)
**Period**: 2014-01-02 → 2026-04-03
**Init NAV**: 50B
**Cost (NEW)**: deposit_annual=0% (default), borrow_annual=10% (default), TC=0.1%/side, ETF friction=0.15%/side

## Normalization (fixed from v1)

- `w = 0.10 × (Kelly_c / mean(Kelly_c)) × 0.25`  (quarter-Kelly, relative to mean)
- Clip to **[0.06, 0.14]**  (±40% band around 10%)
- Tiers with `n < 30` forced to flat 10%
- **No final rescale** — let proposed weights diverge genuinely from flat 10%

## Proposed weights

| tier | n | mean_ret % | Kelly_c | current | proposed | Δpp | note |
|---|---:|---:|---:|---:|---:|---:|---|
| MOMENTUM_N | 45 | +15.23 | +2.151 | 10.00% | **6.00%** | -4.00 |  |
| MOMENTUM_S | 74 | +19.22 | +1.791 | 10.00% | **6.00%** | -4.00 |  |
| MOMENTUM | 14 | +18.70 | +1.551 | 10.00% | **10.00%** | +0.00 | small_n_keep_flat (n<30) |
| DEEP_VALUE_RECOVERY | 293 | +5.76 | +0.916 | 10.00% | **6.00%** | -4.00 |  |
| RE_BACKLOG_BUY | 109 | +4.87 | +0.788 | 10.00% | **6.00%** | -4.00 |  |
| MEGA | 2 | -0.65 | -0.139 | 10.00% | **10.00%** | +0.00 | small_n_keep_flat (n<30) |

Tiers diverging from flat 10%: **4/6**

## Verdict

### **RED** — ΔCAGR=-6.15pp / ΔSharpe=-0.20 / ΔMaxDD=+3.38pp — fails gate

Gate: OOS 2024-2026 ΔCAGR ≥ +0.5pp AND ΔSharpe ≥ +0.05 AND ΔMaxDD ≥ -1.5pp.

## Results — all windows

| Period | Arm | CAGR | Sharpe | MaxDD | Calmar | Trades |
|---|---|---:|---:|---:|---:|---:|
| **FULL 2014-2026** | FLAT | +15.84% | +1.12 | -22.62% | +0.70 | 2963 |
|        | PROPOSED | +13.65% | +1.11 | -17.89% | +0.76 | 2774 |
|        | **Δ P-F** | **-2.20pp** | **-0.02** | **+4.73pp** | **+0.06** | — |
| **Pre-OOS 2014-19** | FLAT | +7.34% | +0.78 | -21.44% | +0.34 | 978 |
|        | PROPOSED | +7.14% | +0.85 | -17.22% | +0.41 | 894 |
|        | **Δ P-F** | **-0.19pp** | **+0.07** | **+4.21pp** | **+0.07** | — |
| **OOS 2024-2026** | FLAT | +18.29% | +1.10 | -18.70% | +0.98 | 750 |
|        | PROPOSED | +12.13% | +0.90 | -15.32% | +0.79 | 688 |
|        | **Δ P-F** | **-6.15pp** | **-0.20** | **+3.38pp** | **-0.19** | — |
| **Y2022** | FLAT | -16.10% | -1.96 | -15.96% | -1.01 | 158 |
|        | PROPOSED | -13.43% | -1.71 | -13.30% | -1.01 | 134 |
|        | **Δ P-F** | **+2.68pp** | **+0.24** | **+2.67pp** | **-0.00** | — |
| **Y2024** | FLAT | +13.35% | +1.71 | -3.46% | +3.86 | 109 |
|        | PROPOSED | +11.08% | +1.82 | -3.49% | +3.17 | 102 |
|        | **Δ P-F** | **-2.27pp** | **+0.11** | **-0.03pp** | **-0.69** | — |
| **Y2025** | FLAT | +43.94% | +1.79 | -13.96% | +3.15 | 520 |
|        | PROPOSED | +26.09% | +1.37 | -14.35% | +1.82 | 464 |
|        | **Δ P-F** | **-17.85pp** | **-0.42** | **-0.39pp** | **-1.33** | — |

## Files

- `kelly_q3_v2_tier_weights.csv` — proposed weights table
- `kelly_q3_v2_out/flat_*.csv` — FLAT 10% arm logs/transactions/open positions
- `kelly_q3_v2_out/proposed_*.csv` — PROPOSED arm logs/transactions/open positions

## Notes vs v1

- v1 (`test_kelly_q3_tier_weights.py`) had a rescale loop that collapsed proposed weights
  back to flat 10% — Δ was identically zero. v2 drops the rescale and uses a tighter [6%, 14%] clip.
- Uses same cached signal pkl as Part B + Q2 v2 for identical signal stream.
- Built directly on sim_v11_transparent.py canonical pattern — only `tier_weights` differs.