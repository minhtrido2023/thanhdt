# Kelly Q3 v3 -- FLAT vs BOOST_ONLY vs SHARPE_PROP

**Date**: 2026-05-23
**Stack**: BA v11 full | 50/50 BAL+VN30 | V6 ETF (NEUTRAL 70%)
**Period**: 2014-01-02 -> 2026-04-03 | Init NAV: 50B
**Cost (NEW)**: deposit_annual=0% (default), borrow_annual=10% (default)

## Weights compared

| tier | n | Sharpe/tr | Kelly_c | FLAT | BOOST_ONLY | SHARPE_PROP | note |
|---|---:|---:|---:|---:|---:|---:|---|
| MOMENTUM_S | 74 | 0.587 | 1.791 | 10.0% | 14.0% | 13.0% |  |
| MOMENTUM_N | 45 | 0.572 | 2.151 | 10.0% | 14.0% | 13.0% |  |
| MOMENTUM | 14 | 0.538 | 1.551 | 10.0% | 10.0% | 10.0% | small_n_keep_flat (n<30) |
| DEEP_VALUE_RECOVERY | 293 | 0.230 | 0.916 | 10.0% | 10.0% | 7.0% |  |
| RE_BACKLOG_BUY | 109 | 0.196 | 0.788 | 10.0% | 10.0% | 7.0% |  |
| MEGA | 2 | -0.030 | -0.139 | 10.0% | 10.0% | 10.0% | small_n_keep_flat (n<30) |

## Results -- all windows

| Period | Arm | CAGR | Sharpe | MaxDD | Calmar | Wealth | Trades |
|---|---|---:|---:|---:|---:|---:|---:|
| **FULL 2014-2026** | FLAT | +16.06% | +1.13 | -25.19% | +0.64 | 6.20x | 2083 |
| **FULL 2014-2026** | BOOST_ONLY | +17.65% | +1.20 | -25.49% | +0.69 | 7.32x | 2179 |
| **FULL 2014-2026** | SHARPE_PROP | +16.61% | +1.18 | -23.04% | +0.72 | 6.57x | 2172 |
|        | **B-F** | **+1.59pp** | **+0.07** | **-0.31pp** | **+0.05** | -- | -- |
|        | **S-F** | **+0.55pp** | **+0.04** | **+2.15pp** | **+0.08** | -- | -- |
| **Pre-OOS 2014-19** | FLAT | +8.06% | +0.84 | -22.38% | +0.36 | 1.59x | 660 |
| **Pre-OOS 2014-19** | BOOST_ONLY | +8.35% | +0.86 | -23.52% | +0.36 | 1.62x | 686 |
| **Pre-OOS 2014-19** | SHARPE_PROP | +8.76% | +0.94 | -20.15% | +0.43 | 1.65x | 673 |
|        | **B-F** | **+0.30pp** | **+0.02** | **-1.14pp** | **-0.00** | -- | -- |
|        | **S-F** | **+0.71pp** | **+0.10** | **+2.24pp** | **+0.07** | -- | -- |
| **OOS 2024-2026** | FLAT | +22.10% | +1.29 | -17.58% | +1.26 | 1.57x | 517 |
| **OOS 2024-2026** | BOOST_ONLY | +25.14% | +1.37 | -18.00% | +1.40 | 1.66x | 529 |
| **OOS 2024-2026** | SHARPE_PROP | +21.30% | +1.25 | -14.21% | +1.50 | 1.54x | 516 |
|        | **B-F** | **+3.04pp** | **+0.08** | **-0.42pp** | **+0.14** | -- | -- |
|        | **S-F** | **-0.80pp** | **-0.03** | **+3.36pp** | **+0.24** | -- | -- |
| **Y2022** | FLAT | -19.36% | -2.18 | -20.02% | -0.97 | 0.81x | 98 |
| **Y2022** | BOOST_ONLY | -19.61% | -2.11 | -21.03% | -0.93 | 0.81x | 130 |
| **Y2022** | SHARPE_PROP | -16.73% | -1.90 | -18.14% | -0.92 | 0.83x | 98 |
|        | **B-F** | **-0.26pp** | **+0.07** | **-1.01pp** | **+0.03** | -- | -- |
|        | **S-F** | **+2.63pp** | **+0.28** | **+1.89pp** | **+0.04** | -- | -- |
| **Y2024** | FLAT | +13.33% | +1.63 | -3.36% | +3.97 | 1.13x | 68 |
| **Y2024** | BOOST_ONLY | +13.90% | +1.64 | -3.66% | +3.80 | 1.14x | 69 |
| **Y2024** | SHARPE_PROP | +11.79% | +1.64 | -3.56% | +3.31 | 1.12x | 76 |
|        | **B-F** | **+0.57pp** | **+0.01** | **-0.31pp** | **-0.18** | -- | -- |
|        | **S-F** | **-1.54pp** | **+0.01** | **-0.21pp** | **-0.66** | -- | -- |
| **Y2025** | FLAT | +51.15% | +2.06 | -13.62% | +3.76 | 1.51x | 375 |
| **Y2025** | BOOST_ONLY | +58.92% | +2.15 | -14.44% | +4.08 | 1.58x | 376 |
| **Y2025** | SHARPE_PROP | +48.18% | +1.91 | -13.55% | +3.55 | 1.48x | 362 |
|        | **B-F** | **+7.76pp** | **+0.09** | **-0.82pp** | **+0.32** | -- | -- |
|        | **S-F** | **-2.97pp** | **-0.16** | **+0.07pp** | **-0.20** | -- | -- |

## Verdict

### BOOST_ONLY: **GREEN** -- dCAGR=+3.04pp / dSharpe=+0.08 / dMaxDD=-0.42pp
### SHARPE_PROP: **RED** -- dCAGR=-0.80pp / dSharpe=-0.03 / dMaxDD=+3.36pp

Gate: OOS 2024-2026 dCAGR >= +0.5pp AND dSharpe >= +0.05 AND dMaxDD >= -1.5pp.

## Files

- `kelly_q3_v3_tier_weights.csv` -- weights table
- `kelly_q3_v3_out/{flat,boost_only,sharpe_prop}_*.csv` -- per-arm logs/transactions

## Design vs v2

- v2 PROPOSED cut all tiers to floor 6% -> cash drag -> RED
- v3 BOOST_ONLY: only raise high-Sharpe tiers, no cuts -> tests if extra capital to high-edge tiers wins
- v3 SHARPE_PROP: w_i = 0.10 x Sharpe_i/mean(Sharpe), clip [7%, 13%] -> tighter band, anchored to Sharpe (not Kelly_c)