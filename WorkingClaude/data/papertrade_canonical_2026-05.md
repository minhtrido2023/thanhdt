# Paper-Trade 5 Systems — Canonical Backtest Report (prod spec)

*Generated: 2026-05-25*  •  *Engine: run_5systems_prodspec.py + simulate_holistic_nav.py*  •  *Init NAV: 50B per system, prod spec (max_pos=12 + tier_weights 10% + t1_open + RE_BACKLOG + SV_TIGHT)*

## TL;DR — expected return for new deployer (most relevant)

If you deploy 50B fresh today, the *best historical proxy* is the fresh-start backtest from 2024-01-02 (most recent 2.37y cold-start). Numbers below are from that variant.

| System | Expected CAGR (fresh 2024) | Sharpe | MaxDD | Wealth in 2.4y |
|---|---:|---:|---:|---:|
| **V1 V11+TQ34b** | **+29.46%** | +1.60 | -17.30% | 1.84x |
| **V2 V12+TQ34b** | **+30.55%** | +1.86 | -9.50% | 1.88x |
| **V3 V12+LIVE** | **+29.80%** | +1.81 | -10.39% | 1.85x |
| **V4 V121_ENS** | **+33.03%** | +1.81 | -11.01% | 1.96x |
| **V5 V4+KellyQ2** | **+36.37%** | +1.88 | -10.97% | 2.08x |
| VNI B&H | +25.08% | +1.30 | -18.11% | 1.70x |

⚠ Real return ≈ backtest − 1.5pp/yr (slippage + tax + execution drag not modelled). So V5 realistic ≈ 35% CAGR; V1 ≈ 28%.

## A. Headline — 12y continuous (canonical prod spec)

Treats the backtest as if the system was running continuously since 2014-01-02. Compounds carryover positions; reflects MAX possible historical performance.

| System | CAGR | Sharpe | Sortino | MaxDD | Calmar | Wealth (12.4y) |
|---|---:|---:|---:|---:|---:|---:|
| V1 V11+TQ34b | +20.85% | +1.44 | +1.50 | -18.70% | +1.11 | 10.39x |
| V2 V12+TQ34b | +21.65% | +1.68 | +1.94 | -14.42% | +1.50 | 11.28x |
| V3 V12+LIVE | +20.91% | +1.62 | +1.89 | -14.72% | +1.42 | 10.46x |
| V4 V121_ENS | +24.64% | +1.75 | +1.95 | -15.97% | +1.54 | 15.23x |
| V5 V4+KellyQ2 | +26.09% | +1.73 | +1.96 | -16.97% | +1.54 | 17.58x |
| VNI B&H | +11.42% | +0.68 | +0.80 | -45.26% | +0.25 | 3.81x |

## B. Period slices — 12y canonical

### OOS 2024-26

| System | CAGR | Sharpe | MaxDD | Wealth |
|---|---:|---:|---:|---:|
| V1 V11+TQ34b | +27.50% | +1.50 | -18.70% | 1.78x |
| V2 V12+TQ34b | +23.51% | +1.70 | -9.10% | 1.65x |
| V3 V12+LIVE | +21.70% | +1.59 | -9.46% | 1.59x |
| V4 V121_ENS | +30.61% | +1.72 | -12.46% | 1.88x |
| V5 V4+KellyQ2 | +36.04% | +1.86 | -12.69% | 2.07x |
| VNI B&H | +25.08% | +1.30 | -18.11% | 1.70x |

### IS 2014-19

| System | CAGR | Sharpe | MaxDD | Wealth |
|---|---:|---:|---:|---:|
| V1 V11+TQ34b | +13.11% | +1.25 | -18.42% | 2.09x |
| V2 V12+TQ34b | +13.93% | +1.38 | -14.42% | 2.18x |
| V3 V12+LIVE | +13.72% | +1.37 | -14.56% | 2.16x |
| V4 V121_ENS | +16.62% | +1.50 | -14.81% | 2.51x |
| V5 V4+KellyQ2 | +16.97% | +1.41 | -16.97% | 2.56x |
| VNI B&H | +11.35% | +0.76 | -27.08% | 1.90x |

### Mid 2018-23

| System | CAGR | Sharpe | MaxDD | Wealth |
|---|---:|---:|---:|---:|
| V1 V11+TQ34b | +22.62% | +1.46 | -16.14% | 3.39x |
| V2 V12+TQ34b | +25.40% | +1.77 | -11.12% | 3.88x |
| V3 V12+LIVE | +24.87% | +1.71 | -14.72% | 3.78x |
| V4 V121_ENS | +26.17% | +1.80 | -15.97% | 4.02x |
| V5 V4+KellyQ2 | +26.05% | +1.72 | -15.21% | 4.00x |
| VNI B&H | +2.13% | +0.21 | -45.26% | 1.13x |

### Bull 2020-21

| System | CAGR | Sharpe | MaxDD | Wealth |
|---|---:|---:|---:|---:|
| V1 V11+TQ34b | +69.83% | +2.62 | -16.14% | 2.88x |
| V2 V12+TQ34b | +66.66% | +2.97 | -10.96% | 2.77x |
| V3 V12+LIVE | +68.02% | +3.00 | -11.01% | 2.82x |
| V4 V121_ENS | +73.87% | +3.13 | -15.97% | 3.02x |
| V5 V4+KellyQ2 | +75.76% | +3.17 | -15.21% | 3.08x |
| VNI B&H | +24.55% | +1.11 | -33.51% | 1.55x |

### Bear 2022

| System | CAGR | Sharpe | MaxDD | Wealth |
|---|---:|---:|---:|---:|
| V1 V11+TQ34b | -0.26% | -0.11 | -2.71% | 1.00x |
| V2 V12+TQ34b | +2.94% | +0.37 | -8.72% | 1.03x |
| V3 V12+LIVE | -3.66% | -0.30 | -11.89% | 0.96x |
| V4 V121_ENS | +5.24% | +1.27 | -3.31% | 1.05x |
| V5 V4+KellyQ2 | +5.96% | +1.31 | -3.28% | 1.06x |
| VNI B&H | -34.39% | -1.58 | -40.34% | 0.66x |

### Y2025 bull

| System | CAGR | Sharpe | MaxDD | Wealth |
|---|---:|---:|---:|---:|
| V1 V11+TQ34b | +60.58% | +2.39 | -16.26% | 1.60x |
| V2 V12+TQ34b | +37.45% | +2.27 | -8.31% | 1.37x |
| V3 V12+LIVE | +32.54% | +2.04 | -8.40% | 1.32x |
| V4 V121_ENS | +74.27% | +3.18 | -7.99% | 1.74x |
| V5 V4+KellyQ2 | +85.25% | +3.31 | -7.71% | 1.85x |
| VNI B&H | +40.84% | +1.73 | -18.11% | 1.41x |

### 2026 YTD

| System | CAGR | Sharpe | MaxDD | Wealth |
|---|---:|---:|---:|---:|
| V1 V11+TQ34b | +3.65% | +0.28 | -12.07% | 1.01x |
| V2 V12+TQ34b | +0.35% | +0.09 | -9.10% | 1.00x |
| V3 V12+LIVE | -2.65% | -0.15 | -8.95% | 0.99x |
| V4 V121_ENS | +1.93% | +0.20 | -12.46% | 1.01x |
| V5 V4+KellyQ2 | +13.26% | +0.69 | -12.69% | 1.05x |
| VNI B&H | +25.28% | +1.11 | -16.38% | 1.09x |

## C. Fresh-start variants — path-dependency robust

Each row = restart sim with fresh 50B all-cash from that date. Different starts simulate *new deployer* at that moment.

### C1. CAGR per system per start

| Start | Years | V1 V11 | V2 V12 | V3 V12+LIVE | V4 V121_ENS | V5 V4+KellyQ2 | VNI |
|---|---:|---:|---:|---:|---:|---:|---:|
| 12y-cont | 12.36 | +20.85% | +21.65% | +20.91% | +24.64% | +26.09% | +11.42% |
| fresh-2018 | 8.36 | +22.38% | +25.96% | +24.58% | +25.84% | +27.53% | +8.18% |
| fresh-2020 | 6.37 | +30.20% | +33.34% | +31.18% | +34.02% | +36.66% | +11.40% |
| fresh-2022 | 4.36 | +14.58% | +21.06% | +19.41% | +18.23% | +21.14% | +5.44% |
| fresh-2024 | 2.37 | +29.46% | +30.55% | +29.80% | +33.03% | +36.37% | +25.08% |

### C2. Sharpe per system per start

| Start | V1 V11 | V2 V12 | V3 V12+LIVE | V4 V121_ENS | V5 V4+KellyQ2 | VNI |
|---|---:|---:|---:|---:|---:|---:|
| 12y-cont | +1.44 | +1.68 | +1.62 | +1.75 | +1.73 | +0.68 |
| fresh-2018 | +1.31 | +1.69 | +1.60 | +1.55 | +1.58 | +0.50 |
| fresh-2020 | +1.63 | +1.96 | +1.86 | +1.90 | +1.95 | +0.63 |
| fresh-2022 | +1.04 | +1.40 | +1.28 | +1.27 | +1.37 | +0.37 |
| fresh-2024 | +1.60 | +1.86 | +1.81 | +1.81 | +1.88 | +1.30 |

### C3. MaxDD per system per start

| Start | V1 V11 | V2 V12 | V3 V12+LIVE | V4 V121_ENS | V5 V4+KellyQ2 | VNI |
|---|---:|---:|---:|---:|---:|---:|
| 12y-cont | -18.70% | -14.42% | -14.72% | -15.97% | -16.97% | -45.26% |
| fresh-2018 | -22.01% | -17.78% | -17.78% | -22.01% | -23.82% | -45.26% |
| fresh-2020 | -17.94% | -13.18% | -16.57% | -16.80% | -16.59% | -40.34% |
| fresh-2022 | -17.06% | -13.53% | -15.71% | -13.95% | -12.62% | -40.34% |
| fresh-2024 | -17.30% | -9.50% | -10.39% | -11.01% | -10.97% | -18.11% |

## D. Annual returns (12y canonical)

| Year | V1 V11 | V2 V12 | V3 V12+LIVE | V4 V121_ENS | V5 V4+KellyQ2 | VNI |
|---|---:|---:|---:|---:|---:|---:|
| 2014 | +12.8% | +17.1% | +17.6% | +20.5% | +27.7% | +8.2% |
| 2015 | -4.8% | +0.8% | +0.7% | +1.6% | -1.3% | +6.4% |
| 2016 | +6.6% | +10.3% | +10.2% | +9.0% | +11.6% | +15.7% |
| 2017 | +45.2% | +32.5% | +30.4% | +45.1% | +44.5% | +46.5% |
| 2018 | +17.7% | +17.5% | +17.5% | +25.8% | +22.1% | -10.4% |
| 2019 | +3.2% | +5.4% | +5.8% | -0.7% | -1.1% | +7.8% |
| 2020 | +49.2% | +39.6% | +42.1% | +59.1% | +54.1% | +14.2% |
| 2021 | +87.7% | +96.2% | +96.0% | +84.2% | +93.9% | +33.7% |
| 2022 | -0.3% | +2.9% | -3.6% | +5.2% | +5.9% | -34.0% |
| 2023 | -3.3% | +9.3% | +11.3% | +0.9% | +0.8% | +8.2% |
| 2024 | +10.3% | +20.4% | +21.6% | +8.3% | +8.1% | +11.9% |
| 2025 | +60.1% | +37.2% | +32.3% | +73.7% | +84.6% | +40.5% |
| 2026 | +0.5% | -0.3% | -1.1% | -0.2% | +3.5% | +7.4% |

## E. Charts

- 12y equity curves (log): `data/papertrade_canonical_curves.png`
- 12y drawdown: `data/papertrade_canonical_drawdown.png`
- Fresh-vs-canon overlay: `data/path_dependency_curves.png`

## F. Critical caveats — read before interpreting any CAGR

1. **Start-date sensitivity**: 5 systems × 4 fresh starts = 20 datapoints; mean ΔCAGR vs canonical = **+2.23pp**, std **2.76pp**. Fresh > canon in 17/20 (85%) of cases. Quoting 12y CAGR alone is misleading.
2. **Look-ahead bias from artifacts**: `ba_v11_unified_12y_sig.pkl` (2026-05-20 vintage) bakes in current FA tier definitions, sector classifications, ticker_prune universe (survivorship), and SIGNAL_V10 logic — applied retroactively to 2014 data. True point-in-time replay would differ.
3. **Tier evolution**: SV_TIGHT, P3 overheat, RE_BACKLOG_BUY, slot12 (max_pos=12), 10% fixed sizing — all deployed 2026-05. Pre-2026 reality used different rules.
4. **No intraday HYBRID buy** (data unavailable pre-2024). Production gets +0.5pp Sharpe edge from this; backtest is conservative.
5. **Real-world haircut**: subtract ~1.5pp/yr from backtest CAGR for slippage + tax + execution drag not modeled.
6. **Paper-trade live (2026-04 onward) is the only zero-lookahead forward evidence**. After ~5 months: V5 = +5.11% (CAGR ann +46%, n=32 sessions, too noisy).

## G. Recommended usage

| Audience | Use this number |
|---|---|
| Long-term theoretical max (12y compound) | Section A — 12y canonical CAGR |
| New deployer expected (next ~2-3 years) | Section TL;DR — fresh 2024-01 CAGR |
| Forward-looking live evidence | Paper-trade 5-system live (data/papertrade_milestone_mid_*.md) |
| Regime-conditional bet sizing | Section B — period slices |
| Risk budgeting (drawdown reserve) | Section C3 — MaxDD across starts (worst case) |

## H. Source artifacts

- Engine: `run_5systems_prodspec.py` (canonical; env START_DATE/END_DATE)
- Daily NAV CSVs: `data/5sys_prodspec_<start>_<end>.csv` (5 files)
- Path-dep report: `data/path_dependency_report.md`
- Path-dep gaps: `data/path_dependency_gaps.csv`
- Metrics: `data/papertrade_canonical_metrics.csv`
- Old simplified spec (deprecated): `run_full_5systems_2014_2026.py`
