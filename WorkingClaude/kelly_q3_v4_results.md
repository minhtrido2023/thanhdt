# Kelly Q3 v4 -- HYBRID state-conditional vs static arms

**Date**: 2026-05-23
**Stack**: BA v11 full | 50/50 BAL+VN30 | V6 ETF (NEUTRAL 70%)
**Period**: 2014-01-02 -> 2026-04-03 | Init NAV: 50B
**Cost**: deposit_annual=0%, borrow_annual=10% (new defaults)

## HYBRID design

- State **4 (BULL)** + **5 (EX-BULL)**: use BOOST_ONLY weights (MOMENTUM_S/N = 14%, rest = 10%)
- State **1 (CRISIS)** + **2 (BEAR)** + **3 (NEUTRAL)**: use SHARPE_PROP weights (MOMENTUM_S/N = 13%, DVR/RE = 7%, rest = 10%)

Rationale: capture upside in bull states via BOOST, reduce volatility in non-bull via SHARPE_PROP cuts.

## Verdicts

- BOOST_ONLY:  **GREEN** -- dCAGR=+2.73pp / dSharpe=+0.10 / dMaxDD=+1.24pp
- SHARPE_PROP: **GREEN** -- dCAGR=+1.12pp / dSharpe=+0.07 / dMaxDD=+3.74pp
- HYBRID:      **GREEN** -- dCAGR=+2.11pp / dSharpe=+0.07 / dMaxDD=+1.02pp

Gate: OOS 2024-2026 dCAGR >= +0.5pp AND dSharpe >= +0.05 AND dMaxDD >= -1.5pp.

## Results -- all windows

| Period | Arm | CAGR | Sharpe | MaxDD | Calmar | Wealth | Trades |
|---|---|---:|---:|---:|---:|---:|---:|
| **FULL 2014-2026** | FLAT | +15.84% | +1.12 | -22.62% | +0.70 | 6.06x | 2013 |
| **** | BOOST_ONLY | +16.96% | +1.18 | -21.09% | +0.80 | 6.81x | 1995 |
| **** | SHARPE_PROP | +16.67% | +1.21 | -19.16% | +0.87 | 6.61x | 2005 |
| **** | HYBRID | +16.78% | +1.16 | -22.30% | +0.75 | 6.69x | 2025 |
|        | **D BOOST_ONLY-F** | **+1.11pp** | **+0.06** | **+1.53pp** | **+0.10** | -- | -- |
|        | **D SHARPE_PROP-F** | **+0.83pp** | **+0.08** | **+3.46pp** | **+0.17** | -- | -- |
|        | **D HYBRID-F** | **+0.94pp** | **+0.03** | **+0.32pp** | **+0.05** | -- | -- |
| **Pre-OOS 2014-19** | FLAT | +7.34% | +0.78 | -21.44% | +0.34 | 1.53x | 590 |
| **** | BOOST_ONLY | +7.88% | +0.83 | -20.30% | +0.39 | 1.58x | 589 |
| **** | SHARPE_PROP | +7.96% | +0.89 | -19.16% | +0.42 | 1.58x | 565 |
| **** | HYBRID | +8.13% | +0.86 | -21.11% | +0.39 | 1.60x | 566 |
|        | **D BOOST_ONLY-F** | **+0.54pp** | **+0.05** | **+1.14pp** | **+0.05** | -- | -- |
|        | **D SHARPE_PROP-F** | **+0.62pp** | **+0.11** | **+2.28pp** | **+0.07** | -- | -- |
|        | **D HYBRID-F** | **+0.80pp** | **+0.08** | **+0.33pp** | **+0.04** | -- | -- |
| **OOS 2024-2026** | FLAT | +18.29% | +1.10 | -18.70% | +0.98 | 1.46x | 569 |
| **** | BOOST_ONLY | +21.01% | +1.20 | -17.46% | +1.20 | 1.54x | 541 |
| **** | SHARPE_PROP | +19.41% | +1.17 | -14.97% | +1.30 | 1.49x | 549 |
| **** | HYBRID | +20.39% | +1.17 | -17.68% | +1.15 | 1.52x | 534 |
|        | **D BOOST_ONLY-F** | **+2.73pp** | **+0.10** | **+1.24pp** | **+0.23** | -- | -- |
|        | **D SHARPE_PROP-F** | **+1.12pp** | **+0.07** | **+3.74pp** | **+0.32** | -- | -- |
|        | **D HYBRID-F** | **+2.11pp** | **+0.07** | **+1.02pp** | **+0.18** | -- | -- |
| **Y2022** | FLAT | -16.10% | -1.96 | -15.96% | -1.01 | 0.84x | 97 |
| **** | BOOST_ONLY | -15.81% | -1.92 | -15.68% | -1.01 | 0.84x | 97 |
| **** | SHARPE_PROP | -13.96% | -1.74 | -13.84% | -1.01 | 0.86x | 88 |
| **** | HYBRID | -15.52% | -1.89 | -15.38% | -1.01 | 0.85x | 95 |
|        | **D BOOST_ONLY-F** | **+0.30pp** | **+0.04** | **+0.28pp** | **+0.00** | -- | -- |
|        | **D SHARPE_PROP-F** | **+2.14pp** | **+0.21** | **+2.13pp** | **-0.00** | -- | -- |
|        | **D HYBRID-F** | **+0.59pp** | **+0.07** | **+0.59pp** | **-0.00** | -- | -- |
| **Y2024** | FLAT | +13.35% | +1.71 | -3.46% | +3.86 | 1.13x | 79 |
| **** | BOOST_ONLY | +13.52% | +1.68 | -3.41% | +3.96 | 1.13x | 69 |
| **** | SHARPE_PROP | +11.67% | +1.69 | -3.42% | +3.41 | 1.12x | 79 |
| **** | HYBRID | +13.37% | +1.68 | -3.43% | +3.90 | 1.13x | 69 |
|        | **D BOOST_ONLY-F** | **+0.17pp** | **-0.03** | **+0.05pp** | **+0.10** | -- | -- |
|        | **D SHARPE_PROP-F** | **-1.68pp** | **-0.02** | **+0.04pp** | **-0.44** | -- | -- |
|        | **D HYBRID-F** | **+0.02pp** | **-0.03** | **+0.03pp** | **+0.05** | -- | -- |
| **Y2025** | FLAT | +43.94% | +1.79 | -13.96% | +3.15 | 1.44x | 409 |
| **** | BOOST_ONLY | +46.88% | +1.82 | -14.96% | +3.13 | 1.47x | 395 |
| **** | SHARPE_PROP | +43.54% | +1.78 | -14.12% | +3.08 | 1.43x | 387 |
| **** | HYBRID | +45.46% | +1.79 | -14.49% | +3.14 | 1.45x | 388 |
|        | **D BOOST_ONLY-F** | **+2.94pp** | **+0.03** | **-1.00pp** | **-0.01** | -- | -- |
|        | **D SHARPE_PROP-F** | **-0.40pp** | **-0.02** | **-0.16pp** | **-0.06** | -- | -- |
|        | **D HYBRID-F** | **+1.52pp** | **-0.01** | **-0.53pp** | **-0.01** | -- | -- |

## Files

- `kelly_q3_v4_out/{flat,boost_only,sharpe_prop,hybrid}_*.csv` -- per-arm logs/transactions