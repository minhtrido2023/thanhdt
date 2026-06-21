# Backtest canonical = prod spec (2026-05-25)

## Decision

`run_5systems_prodspec.py` REPLACES `run_full_5systems_2014_2026.py` as canonical
5-system backtest engine. Old script kept as deprecated reference only.

## Spec difference vs old (6 changes)

1. `max_positions=12` (was 10) — slot12 deployed 2026-05-16
2. `tier_weights={tier: 0.10}` for all TIER_BAL — 10% fixed sizing
3. `t1_open_exec=True` + `open_prices` loaded — T+1 OPEN exec (was legacy T-close)
4. `RE_BACKLOG_BUY` tier added via D1 reclassification (ICB 8633, AdvCust YoY > 50%, FA C/D, state 3-5)
5. `sector_cap_exempt_tiers={"RE_BACKLOG_BUY"}` — exempts new tier from sector cap
6. `SV_TIGHT` state-conditional days_since_release filter (state 1: ≤30d, state 2-3: ≤60d, state 4-5: no limit)

NOT applied (data unavailable pre-2024): `entry_alt_prices=alt_hybrid` HYBRID buy
rule (ATC for T1_TOP, T1115 for others). Production gets ~+0.5pp Sharpe edge from
this; backtest is conservative.

## Spec-update impact (V5 prod vs old, FULL 12y)

| Period | V5_old | V5_prod | Δ |
|---|---:|---:|---:|
| FULL 12y CAGR | 25.71% | 26.09% | +0.38pp |
| FULL Wealth | 16.93x | 17.58x | +3.8% |
| Mid 2018-23 | 24.73% | 26.05% | +1.32pp |
| Y2020 | 48.5% | 54.1% | +5.6pp |
| Y2021 | 86.5% | 93.9% | +7.4pp |
| **2026 YTD** | 7.06% | **13.26%** | **+6.20pp** |
| OOS 24-26 MaxDD | -14.94% | -12.69% | -2.24pp (better) |

Spec changes consistently positive in 2020+ era (tuned for 2025-2026). IS 2014-19
slightly worse (-0.4pp) — acceptable trade-off.

## Path-dependency variance (4 fresh starts vs canonical)

Ran fresh-start 50B sims from 2018/2020/2022/2024 + canonical 2014. Compared each
fresh CAGR to rebased canonical CAGR over same end-date window.

**Gap matrix (ΔCAGR fresh − canonical, pp):**

| Start | V1 | V2 | V3 | V4 | V5 | Mean |
|---|---:|---:|---:|---:|---:|---:|
| 2018-01 | -1.59 | +1.12 | +0.64 | -1.54 | -1.25 | -0.52 |
| 2020-01 | +1.66 | +3.98 | +3.14 | +1.39 | +1.42 | +2.32 |
| 2022-01 | +1.40 | +5.86 | +6.34 | +1.03 | +1.15 | +3.16 |
| 2024-01 | +1.96 | +7.04 | +8.11 | +2.42 | +0.33 | +3.97 |
| Col mean | +0.86 | +4.50 | +4.56 | +0.83 | +0.41 | |

**Key findings:**
- **20 datapoints; mean ΔCAGR = +2.23pp, std = 2.76pp**
- Fresh > canonical in **17/20 (85%)** of cases
- V2/V3 (LAGGED book) MOST path-dependent (col mean +4.5pp) — LAGGED filling fresh book aligned to current earnings events
- V1/V4/V5 (BAL + ensemble) LESS path-dependent (+0.4 to +0.9pp) — BAL has 45d turnover continuously
- Path-dep increases as start moves closer to today

## Quoting convention (per user 2026-05-25)

Never quote a single CAGR without start-date qualifier. Use either:
- `"CAGR 12y continuous = X% (canonical, with carryover positions)"`
- `"CAGR 2.4y fresh-start 2024-01 = Y% (cold-start, new deployer proxy)"`

## Expected returns for new deployer (fresh 2024-01)

| System | Fresh CAGR | Sharpe | MaxDD | Wealth 2.4y |
|---|---:|---:|---:|---:|
| V1 V11+TQ34b | +29.46% | +1.60 | -17.30% | 1.84x |
| V2 V12+TQ34b | +30.55% | +1.86 | -9.50% | 1.88x |
| V3 V12+LIVE | +29.80% | +1.81 | -10.39% | 1.85x |
| V4 V121_ENS | +33.03% | +1.81 | -11.01% | 1.96x |
| **V5 V4+KellyQ2** | **+36.37%** | **+1.88** | **-10.97%** | **2.08x** |
| VNI B&H | +25.08% | +1.30 | -18.11% | 1.70x |

Real-world haircut: subtract ~1.5pp/yr for slippage/tax/execution drag.

## Evidence hierarchy for forward-looking decisions

1. **Paper-trade live 2026-04 onward** = primary (zero look-ahead, real conditions)
2. **Fresh-start 2024-01 backtest** = best proxy (recent cold start, prod spec)
3. **Period slices (OOS 2024-26)** = good for regime questions
4. **12y canonical CAGR** = theoretical max with carryover; use for compounding stories only

## Artifacts

- Engine: [run_5systems_prodspec.py](../../../../OneDrive/Pictures/Documents/WorkingClaude/run_5systems_prodspec.py)
- Primary report: [data/papertrade_canonical_2026-05.md](../../../../OneDrive/Pictures/Documents/WorkingClaude/data/papertrade_canonical_2026-05.md)
- Path-dep report: [data/path_dependency_report.md](../../../../OneDrive/Pictures/Documents/WorkingClaude/data/path_dependency_report.md)
- Daily NAV CSVs: `data/5sys_prodspec_<start>_<end>.csv` (5 files)
- Old artifacts archived: `data/archive/`
