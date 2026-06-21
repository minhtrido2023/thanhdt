

## Cash-Flow Reconciliation (verifiable from transactions.csv)

All numbers below derive ONLY from the transactions CSV. The MTM_UNREALIZED
rows (flagged in `reason` column) are phantom mark-to-market entries used by
analyze_portfolio.py to compute unrealized P&L on open positions — they are NOT
real trades. Filter `reason != 'MTM_UNREALIZED'` to see only real broker activity.

### Schema (per user 2026-05-18)

- `buy_amount` = cost of shares (clean, no fee)
- `sell_amount` = gross from sale (clean, no fee deducted)
- `fee` = transaction cost (buy: 0.15% broker; sell: 0.15% broker + 0.1% PIT tax)
- **Cash deducted on buy = buy_amount + fee**
- **Cash received on sell = sell_amount - fee**
- `deposit_annual=0` (no overnight interest)

### Real activity (excludes MTM_UNREALIZED phantoms)

| Category | Amount |
|---|---|
| Stock buys — share cost | +258.5360B |
| Stock buys — fee | +0.3878B |
| Stock sells — gross | +235.0047B |
| Stock sells — fee+tax | +0.8186B |
| **Net stock realized P&L** | **-24.7377B** |
| ETF buys — share cost | +347.4621B |
| ETF buys — friction | +0.5212B |
| ETF sells — gross | +332.8139B |
| ETF sells — friction | +0.4992B |
| **Net ETF cash flow** | **-15.6686B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| PAN (BAL) | +1.680B | +1.695B | +0.016B | +1.08% |
| VHM (BAL) | +1.797B | +1.930B | +0.133B | +7.53% |
| VIC (BAL) | +1.976B | +2.076B | +0.099B | +5.19% |
| VJC (BAL) | +1.563B | +1.475B | -0.088B | -5.49% |
| POW (BAL) | +1.719B | +1.675B | -0.044B | -2.44% |
| KSF (BAL) | +2.070B | +1.958B | -0.112B | -5.27% |
| GVR (BAL) | +0.321B | +0.326B | +0.006B | +1.95% |
| DPR (BAL) | +0.016B | +0.015B | -0.001B | -3.68% |
| ABB (BAL) | +1.763B | +1.749B | -0.014B | -0.65% |
| PHR (BAL) | +1.938B | +1.953B | +0.015B | +0.93% |
| MSN (BAL) | +0.493B | +0.470B | -0.023B | -4.61% |
| AAA (BAL) | +1.694B | +1.617B | -0.077B | -4.41% |
| TVN (BAL) | +2.069B | +2.123B | +0.054B | +2.76% |
| PSD (BAL) | +0.803B | +0.748B | -0.055B | -6.66% |
| AMS (BAL) | +1.053B | +1.013B | -0.040B | -3.64% |
| TLD (BAL) | +1.605B | +1.606B | +0.001B | +0.21% |
| VHM (VN30) | +1.008B | +1.082B | +0.074B | +7.53% |
| VRE (VN30) | +1.039B | +0.952B | -0.087B | -8.22% |
| MWG (VN30) | +1.143B | +1.038B | -0.105B | -9.07% |
| MSN (VN30) | +1.189B | +1.133B | -0.057B | -4.61% |
| GEX (VN30) | +1.308B | +1.411B | +0.103B | +8.06% |
| E1VFVN30 (BAL) | +4.240B | +4.184B | -0.057B | -1.34% |
| E1VFVN30 (VN30) | +15.299B | +16.241B | +0.942B | +6.16% |
| E1VFVN30 (VN30) | +1.429B | +1.443B | +0.013B | +0.92% |
| E1VFVN30 (VN30) | +0.501B | +0.495B | -0.007B | -1.34% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -24.738B |
| + ETF net cash flow + MTM | +6.693B |
| + Stock unrealized MTM | +28.047B (cost 28.249B → realized would be -0.202B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +258.9238B |
| + Stock sells (sell_amount - fee in) | +234.1861B |
| - ETF buys (buy_amount + fee out) | +347.9833B |
| + ETF sells (sell_amount - fee in) | +332.3147B |
| = Expected end cash (from transactions only) | +9.5937B |
| Actual end cash (from logs) | +9.5937B |
| **Diff (ETF appreciation rebalanced into cash)** | **+0.0000B** |
| Actual end ETF balance (still in cash_etf) | +22.3617B |
| Open stock positions mark value | +28.0471B |
| = **Final NAV (cash + ETF + open stocks)** | **+60.0025B** |

**Note on `Diff` line**: when ETF appreciates daily by VN30 return, cash_etf grows.
The rebalance logic (target 70% of total cash+ETF in state=NEUTRAL) periodically moves
a portion OUT of cash_etf and INTO cash. Those are logged as ETF 'sell' transactions,
but the moved amount EXCEEDS the original cost basis (because ETF appreciated meanwhile).
The diff line = appreciation that flowed to cash via rebalances. To FULLY reconcile,
compute ETF return = (etf_sells + etf_etf_residual_mark) − etf_buys − etf_fees.

### Per-book daily breakdown (in logs CSV)

The `data/v11_tq34b_logs.csv` now has 6 per-book columns:
`BAL_cash`, `BAL_stocks`, `BAL_etf`, `VN30_cash`, `VN30_stocks`, `VN30_etf`.
Each row: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf = NAV`.
Cross-check at any date: when ETF is bought in BAL, BAL_cash decreases and BAL_etf increases (minus friction).