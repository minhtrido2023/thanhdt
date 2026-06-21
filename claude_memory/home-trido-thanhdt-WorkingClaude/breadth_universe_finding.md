# Breadth Universe Convention (2026-05-20)

**TL;DR**: 5-state production breadth dùng `tav2_bq.ticker_prune` (500 mã,
mixed HSX/HNX/UPCOM). KHÔNG dùng HSX-only, KHÔNG dùng full ticker table.
Đây là **intentional design choice** đã empirically validate.

## Decision rationale

Tested 4 universes for breadth (% above MA50) trên VNI fwd returns + state
machine standalone backtest 2014-2026:

| Universe | n_tickers | FULL CAGR | OOS CAGR | Transitions |
|---|---|---|---|---|
| **prune (production)** | 500 | **12.01** | 12.51 | 111 |
| HSX-only proxy | 458 | 11.72 (-0.29pp) | 11.91 | 116 |
| ensemble split 6+6 | 500+458 | 12.23 (+0.22pp) | 12.72 | 113 |
| all tickers (mistake) | 1272 | weakest IC | — | — |

State agreement: ensemble 99.2%, HSX 97.1% vs prune baseline.

## Why prune > HSX-only

State-conditional IC vs fwd20:
- **Prune leads BULL entry** (T-0: 0.71 vs HSX 0.64) — HNX/UPCOM rally trước
- **Prune unique EX-BULL detection** (+0.15 vs HSX +0.09)
- HSX-only slightly better in BEAR/BULL state forward returns
- All 1272 universally weakest (noise from thin/illiquid)

## Convention cho future research

**Always use `tav2_bq.ticker_prune` for breadth** computations to match
production. SQL template:

```sql
SELECT t.time,
       SUM(CASE WHEN t.Close > t.MA50 THEN 1 ELSE 0 END) / COUNT(*) AS breadth
FROM tav2_bq.ticker AS t
WHERE t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
  AND t.Close IS NOT NULL AND t.MA50 IS NOT NULL
GROUP BY t.time
```

**DO NOT** use `WHERE t.ticker != 'VNINDEX'` (this includes all 1272 tickers
including thin HNX/UPCOM — weakest signal). My tier1a/tier2 research scripts
made this mistake — `breadth_slope5 IC +0.42` finding may be inflated.

## Ensemble option tested + REJECTED

Split breadth 12% → prune 6% + HSX 6% gives only +0.22pp standalone CAGR
(within noise). Plus v2g lesson: standalone-win doesn't transfer to BA stack
(v2g was +1.28pp standalone but -2.40pp integrated). Risk > reward.

**Don't rebuild state machine for ensemble.** Production design is correct.

## Files

- `breadth_universe_analysis.py` — correlation + diff analysis
- `breadth_predictive_test.py` — state-conditional IC test
- `breadth_ensemble_backtest.py` — 4-config state machine backtest
- `breadth_universe_comparison.csv` — daily breadth (3 universes)
- `breadth_ensemble_states.csv` — state series per config
