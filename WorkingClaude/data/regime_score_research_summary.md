# Phase A — Regime Score Research Summary

**Period**: 2014-01-02 → 2026-05-19 (2818 days with defined score)

## Score distribution

| Score | Days | Pct | hold_d |
|---|---|---|---|
| 0 | 1129 | 40.1% | 90 |
| 1 | 929 | 33.0% | 70 |
| 2 | 503 | 17.8% | 50 |
| 3 | 195 | 6.9% | 30 |
| 4 | 62 | 2.2% | 15 |

## Forward return per score (Multi-factor)

| Score | n | T+20 mean% | T+45 mean% | T+60 mean% | T+45 hit% |
|---|---|---|---|---|---|
| 0.0 | 1129.0 | 0.86 | 2.16 | 3.27 | 62.2 |
| 1.0 | 929.0 | 1.08 | 2.05 | 2.73 | 63.0 |
| 2.0 | 503.0 | 1.32 | 2.22 | 1.90 | 67.9 |
| 3.0 | 195.0 | 0.79 | 1.76 | 3.55 | 59.9 |
| 4.0 | 62.0 | 0.52 | 7.68 | 9.02 | 71.0 |

## Forward return per TQ v3.4b state (Option 1 baseline)

| State | n | T+20 mean% | T+45 mean% | T+60 mean% | T+45 hit% |
|---|---|---|---|---|---|
| 1.0 | 738.0 | 0.23 | 0.22 | -0.05 | 52.0 |
| 2.0 | 288.0 | 0.24 | 0.44 | 1.02 | 58.5 |
| 3.0 | 1555.0 | 1.13 | 2.44 | 3.32 | 66.3 |
| 4.0 | 325.0 | 1.83 | 4.75 | 6.33 | 63.7 |
| 5.0 | 178.0 | 2.55 | 4.58 | 5.88 | 70.8 |

## Spearman ρ comparison (T+45d)

- **Multi-factor score**: ρ = +0.0433  (expect NEGATIVE; magnitude → stronger predictor)
- **TQ v3.4b state**:    ρ = +0.1760  (expect POSITIVE; |ρ| → stronger)
- **|Multi-ρ| vs |State-ρ|**: 0.0433 vs 0.1760  → State WINS

## Threshold sweep top 5 (lowest ρ_T+45 = best predictor)

| vol_p | rsi_lo | rsi_hi | ρ_T+45 | n_score4 | n_score0 |
|---|---|---|---|---|---|
| 0.7 | 35.0 | 78.0 | +0.0378 | 68.0 | 1069.0 |
| 0.75 | 35.0 | 78.0 | +0.0433 | 62.0 | 1129.0 |
| 0.7 | 30.0 | 80.0 | +0.0437 | 48.0 | 1096.0 |
| 0.7 | 40.0 | 75.0 | +0.0440 | 98.0 | 989.0 |
| 0.75 | 30.0 | 80.0 | +0.0495 | 43.0 | 1156.0 |

## GATE

- Required: ρ_T+45 < -0.10 AND |multi-ρ| ≥ 0.8 × |state-ρ|
- Got: ρ_T+45 = +0.0433, |multi|/|state| = 0.25
- **FAIL — redesign or use simpler state mapping**