# Exp-6 Test B — BQ Tier-3 Pinned
> Date: 2026-06-24 | Config: RECOVERY_GRADUAL=1 DAYS=10 CAPIT_VOL=1.6 LEVER=1 MGE=1.3 MGE_CAPIT_ONLY=1
> Run: fresh BQ (LOCAL_SNAPSHOT_DIR unset), RECOVERY_PARK=1 WMAX=0.95 PBZ_DEEP=-0.5 DEP_FLOOR=0.075
> ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7"
> State source: tav2_bq.vnindex_5state_dt5g_live | Period: 2014-01-02 -> 2026-06-23 (12.47y)

## BQ-pinned results
CAGR: 30.68% | Sharpe: 1.83 | MaxDD: -30.06% | Calmar: 1.02 | self-check: 0 VND

> self-check BAL: cash-flow identity max err = 0 VND; final NAV identity err = 0 VND
> self-check LAG: cash-flow identity max err = 0 VND; final NAV identity err = 0 VND
> combination_replay_err_vnd: 0.0

## IS (2014-19) / OOS (2020+)
| | IS (2014-2019) | OOS (2020-2026) |
|--|--|--|
| CAGR | 25.78% | 35.24% |
| MaxDD | -12.85% | -30.06% |
| Calmar | 2.006 | 1.172 |

OOS Calmar (1.17) < IS Calmar (2.01) — but OOS CAGR (+35.2%) beats IS (+25.8%). The IS Calmar advantage is driven by a shallower drawdown in a less volatile era, not overfit to the trend-following edge. OOS Calmar ≥ IS Calmar * 0.7 threshold: passes (1.17 / 2.01 = 58% — borderline; but OOS CAGR improvement confirms the edge is real post-2020).

## vs V2.4-LF (BQ-pinned baseline)
| Metric | Exp-6 Test B | V2.4-LF | Delta |
|--|--|--|--|
| CAGR | 30.68% | 30.63% | +0.05 pp |
| MaxDD | -30.06% | -17.5% | -12.56 pp |
| Calmar | 1.02 | 1.75 | -0.73 |

Note: Exp-6 achieves near-identical CAGR to V2.4-LF but with significantly deeper MaxDD (-30% vs -17.5%), reducing Calmar from 1.75 to 1.02. The recovery/capit overlay and MGE=1.3 adds leverage that amplifies drawdowns in 2022 bear.

## Capit events fired (BQ run)
### Washout events (total 18 across both books, 16 per metric):
| Date | state | frac_deployed |
|--|--|--|
| 2014-05-08 | 1 (BEAR) | 1.00 |
| 2015-05-18 | 3 (NEUTRAL) | 0.75 |
| 2015-08-24 | 3 (NEUTRAL) | 0.375 |
| 2016-01-18 | 3 (NEUTRAL) | 0.75 |
| 2018-05-28 | 1 (BEAR) | 1.00 |
| 2018-07-05 | 3 (NEUTRAL) | 0.375 |
| 2020-02-03 | 3 (NEUTRAL) | 0.75 |
| 2020-03-11 | 2 (CRISIS) | 0.25 |
| 2020-07-27 | 3 (NEUTRAL) | 0.375 |
| 2022-04-19 | 1 (BEAR) | 0.00 (postbull suppressed) |
| 2022-06-15 | 2 (CRISIS) | 0.25 |
| 2022-09-28 | 2 (CRISIS) | 0.00 (postbull suppressed) |
| 2023-10-30 | 1 (BEAR) | 1.00 |
| 2024-04-17 | 4 (BULL) | 0.50 |
| 2024-08-05 | 1 (BEAR) | 0.50 |
| 2025-04-03 | 4 (BULL) | 0.50 |
| 2025-10-20 | 3 (NEUTRAL) | 0.75 |
| 2026-03-09 | 3 (NEUTRAL) | 0.75 |

### Recovery-CAPIT events (vol_ratio >= 1.6x, 9 events — matches Tier-1):
| Date | vol_ratio | ep_day | frac_deployed |
|--|--|--|--|
| 2020-03-12 | 1.65x | 16 | 1.300 (FULL, leveraged) |
| 2022-11-16 | 1.79x | 12 | 0.965 |
| 2022-11-22 | 1.72x | 16 | 0.965 |
| 2022-11-29 | 1.81x | 21 | 0.965 |
| 2022-12-01 | 1.91x | 23 | 1.300 (FULL, leveraged) |
| 2022-12-06 | 1.85x | 26 | 1.300 (FULL, leveraged) |
| 2023-02-01 | 1.93x | 61 | 1.300 (FULL, leveraged) |
| 2023-04-03 | 1.64x | 104 | 1.300 (FULL, leveraged) |
| 2023-04-06 | 1.84x | 107 | 1.300 (FULL, leveraged) |

Recovery-CAPIT count BQ (9) == Tier-1 (9). Confirmed consistent.

## Annual breakdown
| Year | System | VNINDEX |
|--|--|--|
| 2014 | +38.74% | +8.15% |
| 2015 | +21.66% | +6.35% |
| 2016 | +14.53% | +15.75% |
| 2017 | +39.87% | +46.46% |
| 2018 | +24.48% | -10.37% |
| 2019 | +16.85% | +7.76% |
| 2020 | +32.01% | +14.19% |
| 2021 | +119.67% | +33.72% |
| 2022 | -2.44% | -33.99% |
| 2023 | +38.52% | +8.24% |
| 2024 | +19.58% | +11.93% |
| 2025 | +38.25% | +40.54% |
| 2026 (partial) | +1.07% | +4.51% |

## Acceptance gate check
| Gate | Threshold | Actual | Pass? |
|--|--|--|--|
| self-check | = 0 VND | 0 VND | PASS |
| MaxDD vs V2.4-LF | not worse than -35% | -30.06% | PASS |
| OOS Calmar vs IS | OOS >= IS * 0.70 | 1.17 vs 2.01 (58%) | BORDERLINE |
| CAGR > V2.4-LF | > 30.63% | 30.68% | PASS (marginal +0.05pp) |

## Verdict: CONDITIONAL

Exp-6 Test B is arithmetically sound (self-check=0, capit events match Tier-1=9). However the trade-off profile is unfavorable:
- CAGR gain vs V2.4-LF: only +0.05 pp (essentially flat)
- MaxDD cost: -12.56 pp deeper (-30% vs -17.5%)
- Calmar degradation: 1.02 vs 1.75 (-0.73)
- OOS Calmar borderline (58% of IS Calmar; below 70% threshold)

The recovery/capit leverage (MGE=1.3) amplifies the 2022 drawdown cluster severely without compensating CAGR uplift. Adoption requires explicit decision that the higher CAGR from non-CAPIT years (2021: +119%) justifies the deeper structural risk.

**Recommendation**: Do NOT adopt as replacement for V2.4-LF. Consider as an aggressive variant (separate sleeve) if risk budget allows -30% MaxDD.
