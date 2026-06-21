

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
| Stock buys — share cost | +245.3743B |
| Stock buys — fee | +0.3681B |
| Stock sells — gross | +206.9288B |
| Stock sells — fee+tax | +0.6989B |
| **Net stock realized P&L** | **-39.5124B** |
| ETF buys — share cost | +216.6124B |
| ETF buys — friction | +0.3249B |
| ETF sells — gross | +224.2753B |
| ETF sells — friction | +0.3364B |
| **Net ETF cash flow** | **+7.0016B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| PAN (BAL) | +1.764B | +1.781B | +0.016B | +1.08% |
| VHM (BAL) | +2.179B | +2.339B | +0.161B | +7.53% |
| VIC (BAL) | +0.566B | +0.594B | +0.028B | +5.19% |
| POW (BAL) | +2.887B | +2.813B | -0.075B | -2.44% |
| KSF (BAL) | +1.853B | +1.741B | -0.112B | -5.88% |
| VRE (BAL) | +3.346B | +3.067B | -0.280B | -8.22% |
| GVR (BAL) | +3.680B | +3.746B | +0.066B | +1.95% |
| DPR (BAL) | +4.047B | +3.892B | -0.155B | -3.68% |
| BFC (BAL) | +2.651B | +2.378B | -0.273B | -10.18% |
| CTD (BAL) | +0.133B | +0.120B | -0.013B | -9.31% |
| VCG (BAL) | +0.007B | +0.006B | -0.000B | -5.59% |
| AAA (BAL) | +1.656B | +1.584B | -0.072B | -4.19% |
| PHR (BAL) | +3.907B | +3.974B | +0.067B | +1.87% |
| VHM (VN30) | +1.206B | +1.295B | +0.089B | +7.53% |
| VRE (VN30) | +3.241B | +2.970B | -0.271B | -8.22% |
| MWG (VN30) | +3.564B | +3.236B | -0.328B | -9.07% |
| MSN (VN30) | +3.231B | +3.077B | -0.154B | -4.61% |
| GEX (VN30) | +3.553B | +3.834B | +0.281B | +8.06% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -39.512B |
| + ETF net cash flow + MTM | +7.002B |
| + Stock unrealized MTM | +42.446B (cost 43.469B → realized would be -1.023B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +245.7424B |
| + Stock sells (sell_amount - fee in) | +206.2300B |
| - ETF buys (buy_amount + fee out) | +216.9373B |
| + ETF sells (sell_amount - fee in) | +223.9389B |
| = Expected end cash (from transactions only) | +17.4892B |
| Actual end cash (from logs) | +17.4892B |
| **Diff (ETF appreciation rebalanced into cash)** | **+0.0000B** |
| Actual end ETF balance (still in cash_etf) | +0.0000B |
| Open stock positions mark value | +42.4464B |
| = **Final NAV (cash + ETF + open stocks)** | **+59.9356B** |

**Note on `Diff` line**: when ETF appreciates daily by VN30 return, cash_etf grows.
The rebalance logic (target 70% of total cash+ETF in state=NEUTRAL) periodically moves
a portion OUT of cash_etf and INTO cash. Those are logged as ETF 'sell' transactions,
but the moved amount EXCEEDS the original cost basis (because ETF appreciated meanwhile).
The diff line = appreciation that flowed to cash via rebalances. To FULLY reconcile,
compute ETF return = (etf_sells + etf_etf_residual_mark) − etf_buys − etf_fees.

### Per-book daily breakdown (in logs CSV)

The `data/v11_live_logs.csv` now has 6 per-book columns:
`BAL_cash`, `BAL_stocks`, `BAL_etf`, `VN30_cash`, `VN30_stocks`, `VN30_etf`.
Each row: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf = NAV`.
Cross-check at any date: when ETF is bought in BAL, BAL_cash decreases and BAL_etf increases (minus friction).