# Path-dependency Variance — Fresh-start vs 2014-start backtests

*Generated: 2026-05-25*  •  *All 5 systems, prod-spec, 50B init*  •  *End: 2026-05-15*

Question: nếu start sim FRESH 50B tại 2018/2020/2022/2024, kết quả có khác so với 2014-start (đã chạy liên tục, mang positions tích lũy)?

## A. CAGR comparison — Fresh vs Rebased-canonical (same end date)

### Start = 2018-01  →  end 2026-05-15  (8.36 years)

| System | Fresh CAGR | Canon CAGR (rebased) | ΔCAGR | Fresh Sh | Canon Sh | ΔSh | Fresh DD | Canon DD | ΔDD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| V1 | +22.38% | +23.96% | **-1.59pp** | +1.31 | +1.47 | -0.16 | -22.01% | -18.70% | -3.31pp |
| V2 | +25.96% | +24.84% | **+1.12pp** | +1.69 | +1.75 | -0.07 | -17.78% | -11.12% | -6.66pp |
| V3 | +24.58% | +23.93% | **+0.64pp** | +1.60 | +1.68 | -0.08 | -17.78% | -14.72% | -3.06pp |
| V4 | +25.84% | +27.38% | **-1.54pp** | +1.55 | +1.77 | -0.22 | -22.01% | -15.97% | -6.04pp |
| V5 | +27.53% | +28.78% | **-1.25pp** | +1.58 | +1.76 | -0.18 | -23.82% | -15.21% | -8.61pp |

**Avg ΔCAGR across 5 systems = -0.52pp**.  
Negligible average gap — path dependency washes out at this start.

### Start = 2020-01  →  end 2026-05-15  (6.37 years)

| System | Fresh CAGR | Canon CAGR (rebased) | ΔCAGR | Fresh Sh | Canon Sh | ΔSh | Fresh DD | Canon DD | ΔDD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| V1 | +30.20% | +28.54% | **+1.66pp** | +1.63 | +1.60 | +0.03 | -17.94% | -18.70% | +0.76pp |
| V2 | +33.34% | +29.36% | **+3.98pp** | +1.96 | +1.91 | +0.05 | -13.18% | -11.12% | -2.06pp |
| V3 | +31.18% | +28.04% | **+3.14pp** | +1.86 | +1.82 | +0.04 | -16.57% | -14.72% | -1.85pp |
| V4 | +34.02% | +32.63% | **+1.39pp** | +1.90 | +1.95 | -0.06 | -16.80% | -15.97% | -0.83pp |
| V5 | +36.66% | +35.24% | **+1.42pp** | +1.95 | +1.99 | -0.03 | -16.59% | -15.21% | -1.39pp |

**Avg ΔCAGR across 5 systems = +2.32pp**.  
Fresh-start outperforms 2014-start by 2.32pp on average — favourable timing or scale benefit.

### Start = 2022-01  →  end 2026-05-15  (4.36 years)

| System | Fresh CAGR | Canon CAGR (rebased) | ΔCAGR | Fresh Sh | Canon Sh | ΔSh | Fresh DD | Canon DD | ΔDD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| V1 | +14.58% | +13.18% | **+1.40pp** | +1.04 | +0.96 | +0.08 | -17.06% | -18.70% | +1.63pp |
| V2 | +21.06% | +15.20% | **+5.86pp** | +1.40 | +1.26 | +0.14 | -13.53% | -9.31% | -4.21pp |
| V3 | +19.41% | +13.07% | **+6.34pp** | +1.28 | +1.08 | +0.20 | -15.71% | -11.89% | -3.81pp |
| V4 | +18.23% | +17.20% | **+1.03pp** | +1.27 | +1.26 | +0.01 | -13.95% | -12.46% | -1.49pp |
| V5 | +21.14% | +19.99% | **+1.15pp** | +1.37 | +1.33 | +0.04 | -12.62% | -12.69% | +0.08pp |

**Avg ΔCAGR across 5 systems = +3.16pp**.  
Fresh-start outperforms 2014-start by 3.16pp on average — favourable timing or scale benefit.

### Start = 2024-01  →  end 2026-05-15  (2.37 years)

| System | Fresh CAGR | Canon CAGR (rebased) | ΔCAGR | Fresh Sh | Canon Sh | ΔSh | Fresh DD | Canon DD | ΔDD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| V1 | +29.46% | +27.50% | **+1.96pp** | +1.60 | +1.50 | +0.10 | -17.30% | -18.70% | +1.39pp |
| V2 | +30.55% | +23.51% | **+7.04pp** | +1.86 | +1.70 | +0.16 | -9.50% | -9.10% | -0.39pp |
| V3 | +29.80% | +21.70% | **+8.11pp** | +1.81 | +1.59 | +0.22 | -10.39% | -9.46% | -0.93pp |
| V4 | +33.03% | +30.61% | **+2.42pp** | +1.81 | +1.72 | +0.09 | -11.01% | -12.46% | +1.45pp |
| V5 | +36.37% | +36.04% | **+0.33pp** | +1.88 | +1.86 | +0.02 | -10.97% | -12.69% | +1.72pp |

**Avg ΔCAGR across 5 systems = +3.97pp**.  
Fresh-start outperforms 2014-start by 3.97pp on average — favourable timing or scale benefit.

## B. Gap matrix (ΔCAGR fresh − canonical, pp)

| Start | V1 | V2 | V3 | V4 | V5 | Mean |
|---|---:|---:|---:|---:|---:|---:|
| 2018-01 | -1.59 | +1.12 | +0.64 | -1.54 | -1.25 | **-0.52** |
| 2020-01 | +1.66 | +3.98 | +3.14 | +1.39 | +1.42 | **+2.32** |
| 2022-01 | +1.40 | +5.86 | +6.34 | +1.03 | +1.15 | **+3.16** |
| 2024-01 | +1.96 | +7.04 | +8.11 | +2.42 | +0.33 | **+3.97** |

**Column means** (avg gap per system across 4 start dates):  V1=+0.86pp · V2=+4.50pp · V3=+4.56pp · V4=+0.83pp · V5=+0.41pp

## C. Wealth comparison

| Start | System | Fresh Wealth | Canon Wealth (rebased) | Ratio Fresh/Canon |
|---|---|---:|---:|---:|
| 2018-01 | V1 | 5.415x | 6.030x | 0.898 |
| 2018-01 | V2 | 6.891x | 6.394x | 1.078 |
| 2018-01 | V3 | 6.284x | 6.018x | 1.044 |
| 2018-01 | V4 | 6.838x | 7.572x | 0.903 |
| 2018-01 | V5 | 7.645x | 8.297x | 0.922 |
| 2020-01 | V1 | 5.365x | 4.944x | 1.085 |
| 2020-01 | V2 | 6.244x | 5.149x | 1.213 |
| 2020-01 | V3 | 5.628x | 4.824x | 1.167 |
| 2020-01 | V4 | 6.449x | 6.034x | 1.069 |
| 2020-01 | V5 | 7.303x | 6.833x | 1.069 |
| 2022-01 | V1 | 1.810x | 1.715x | 1.055 |
| 2022-01 | V2 | 2.301x | 1.853x | 1.241 |
| 2022-01 | V3 | 2.167x | 1.708x | 1.268 |
| 2022-01 | V4 | 2.075x | 1.997x | 1.039 |
| 2022-01 | V5 | 2.307x | 2.213x | 1.042 |
| 2024-01 | V1 | 1.842x | 1.776x | 1.037 |
| 2024-01 | V2 | 1.879x | 1.648x | 1.140 |
| 2024-01 | V3 | 1.853x | 1.591x | 1.165 |
| 2024-01 | V4 | 1.964x | 1.881x | 1.044 |
| 2024-01 | V5 | 2.083x | 2.071x | 1.006 |

## D. Equity curves (V1 + V5)

![curves](data/path_dependency_curves.png)

## E. Synthesis

- **20 datapoints** (5 systems × 4 start dates)
- Mean ΔCAGR (fresh - canonical, rebased): **+2.23pp**
- Std ΔCAGR: **2.76pp**
- Min: -1.59pp  (start=2018-01, sys=V1)
- Max: +8.11pp  (start=2024-01, sys=V3)
- Fresh > Canon: 17/20  (85%)

**Reading**: if average is near 0 with high std, path dependency is large but symmetric → start timing is a coin flip. If average is positive/negative, there's systematic carryover bias.

## F. Source

- `data/5sys_prodspec_*.csv` — 5 daily NAV CSVs (one per start date)
- `data/path_dependency_gaps.csv` — gap table
- `data/path_dependency_curves.png` — V1/V5 fresh vs canon overlay
- `run_5systems_prodspec.py` — engine (env START_DATE controls start)