# EW liquidity-threshold sweep (real Price tv gate) — balanced objective

*ew_v1-level 5-state, 2014+. Pure-index NAV = STATE_ALLOC alloc, 1B, dep 0%, borrow 10%, T+1. mono = corr(state-rank, mean forward VNINDEX return); higher = sharper regime ordering. n_uni_cv = universe-size coeff-of-variation (lower = more stable basket).*

| Config | Uni med | Uni min | Uni CV | Trans | Mono T+20 | Mono T+60 | NAV CAGR | Sharpe | MaxDD | Calmar |
|---|---|---|---|---|---|---|---|---|---|---|
| Close 500M (PROD) | 232 | 130 | 0.425 | 57 | -0.075 | -0.126 | +6.96% | 0.65 | -24.4% | 0.28 |
| Price 100M | 414 | 283 | 0.296 | 61 | 0.232 | 0.530 | +7.66% | 0.63 | -27.8% | 0.28 |
| Price 250M | 324 | 213 | 0.328 | 60 | -0.111 | 0.184 | +7.05% | 0.61 | -24.9% | 0.28 |
| Price 500M | 271 | 171 | 0.354 | 60 | 0.041 | 0.342 | +6.29% | 0.55 | -29.4% | 0.21 |
| Price 1B | 222 | 136 | 0.376 | 70 | -0.035 | 0.130 | +5.83% | 0.52 | -24.5% | 0.24 |
| Price 2B | 175 | 99 | 0.407 | 61 | -0.407 | -0.021 | +6.34% | 0.58 | -24.2% | 0.26 |
| Price 5B | 118 | 60 | 0.480 | 52 | 0.166 | -0.111 | +8.07% | 0.75 | -22.4% | 0.36 |
| TopN 50 | 50 | 50 | 0.000 | 57 | -0.751 | -0.212 | +5.24% | 0.50 | -33.5% | 0.16 |
| TopN 100 | 100 | 100 | 0.000 | 52 | 0.105 | 0.313 | +6.87% | 0.63 | -23.5% | 0.29 |
| TopN 150 | 150 | 150 | 0.000 | 58 | -0.246 | -0.067 | +7.82% | 0.71 | -20.1% | 0.39 |
| TopN 200 | 200 | 200 | 0.000 | 64 | -0.269 | 0.259 | +7.00% | 0.63 | -24.9% | 0.28 |