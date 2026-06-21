

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
| Stock buys — share cost | +20.5625B |
| Stock buys — fee | +0.0308B |
| Stock sells — gross | +0.0000B |
| Stock sells — fee+tax | +0.0000B |
| **Net stock realized P&L** | **-20.5934B** |
| ETF buys — share cost | +35.0000B |
| ETF buys — friction | +0.0525B |
| ETF sells — gross | +14.3823B |
| ETF sells — friction | +0.0216B |
| **Net ETF cash flow** | **-20.6917B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| PAN (BAL) | +0.747B | +0.754B | +0.007B | +1.08% |
| VHM (BAL) | +0.827B | +0.888B | +0.061B | +7.53% |
| VIC (BAL) | +0.910B | +0.955B | +0.046B | +5.19% |
| KSF (BAL) | +0.945B | +0.856B | -0.088B | -9.23% |
| VJC (BAL) | +1.026B | +0.968B | -0.058B | -5.49% |
| POW (BAL) | +1.128B | +1.099B | -0.029B | -2.44% |
| VRE (BAL) | +1.241B | +1.137B | -0.104B | -8.22% |
| AAA (BAL) | +1.364B | +1.298B | -0.066B | -4.70% |
| GVR (BAL) | +1.385B | +1.410B | +0.025B | +1.95% |
| DPR (BAL) | +0.069B | +0.067B | -0.003B | -3.68% |
| PHR (BAL) | +0.003B | +0.004B | +0.000B | +1.87% |
| MSN (BAL) | +1.488B | +1.417B | -0.071B | -4.61% |
| PSI (BAL) | +1.241B | +1.252B | +0.011B | +1.07% |
| AMS (BAL) | +1.053B | +1.013B | -0.040B | -3.64% |
| PSD (BAL) | +1.488B | +1.402B | -0.087B | -5.69% |
| VHM (VN30) | +0.778B | +0.835B | +0.057B | +7.53% |
| VRE (VN30) | +0.839B | +0.769B | -0.070B | -8.22% |
| MWG (VN30) | +0.922B | +0.838B | -0.085B | -9.07% |
| MSN (VN30) | +0.972B | +0.926B | -0.046B | -4.61% |
| GEX (VN30) | +1.069B | +1.153B | +0.084B | +8.06% |
| PVD (VN30) | +1.097B | +1.095B | -0.002B | +0.00% |
| E1VFVN30 (BAL) | +7.328B | +7.780B | +0.451B | +6.16% |
| E1VFVN30 (VN30) | +14.155B | +15.026B | +0.872B | +6.16% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -20.593B |
| + ETF net cash flow + MTM | +2.114B |
| + Stock unrealized MTM | +20.137B (cost 20.593B → realized would be -0.456B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +20.5934B |
| + Stock sells (sell_amount - fee in) | +0.0000B |
| - ETF buys (buy_amount + fee out) | +35.0525B |
| + ETF sells (sell_amount - fee in) | +14.3608B |
| = Expected end cash (from transactions only) | +8.7149B |
| Actual end cash (from logs) | +8.7149B |
| **Diff (ETF appreciation rebalanced into cash)** | **+0.0000B** |
| Actual end ETF balance (still in cash_etf) | +22.8059B |
| Open stock positions mark value | +20.1371B |
| = **Final NAV (cash + ETF + open stocks)** | **+51.6580B** |

**Note on `Diff` line**: when ETF appreciates daily by VN30 return, cash_etf grows.
The rebalance logic (target 70% of total cash+ETF in state=NEUTRAL) periodically moves
a portion OUT of cash_etf and INTO cash. Those are logged as ETF 'sell' transactions,
but the moved amount EXCEEDS the original cost basis (because ETF appreciated meanwhile).
The diff line = appreciation that flowed to cash via rebalances. To FULLY reconcile,
compute ETF return = (etf_sells + etf_etf_residual_mark) − etf_buys − etf_fees.

### Per-book daily breakdown (in logs CSV)

The `data/pt_v11_tq34b_logs.csv` now has 6 per-book columns:
`BAL_cash`, `BAL_stocks`, `BAL_etf`, `VN30_cash`, `VN30_stocks`, `VN30_etf`.
Each row: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf = NAV`.
Cross-check at any date: when ETF is bought in BAL, BAL_cash decreases and BAL_etf increases (minus friction).

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
| Stock buys — share cost | +20.5625B |
| Stock buys — fee | +0.0308B |
| Stock sells — gross | +0.0000B |
| Stock sells — fee+tax | +0.0000B |
| **Net stock realized P&L** | **-20.5934B** |
| ETF buys — share cost | +35.0000B |
| ETF buys — friction | +0.0525B |
| ETF sells — gross | +14.3823B |
| ETF sells — friction | +0.0216B |
| **Net ETF cash flow** | **-20.6917B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| PAN (BAL) | +0.747B | +0.754B | +0.007B | +1.08% |
| VHM (BAL) | +0.827B | +0.888B | +0.061B | +7.53% |
| VIC (BAL) | +0.910B | +0.955B | +0.046B | +5.19% |
| KSF (BAL) | +0.945B | +0.856B | -0.088B | -9.23% |
| VJC (BAL) | +1.026B | +0.968B | -0.058B | -5.49% |
| POW (BAL) | +1.128B | +1.099B | -0.029B | -2.44% |
| VRE (BAL) | +1.241B | +1.137B | -0.104B | -8.22% |
| AAA (BAL) | +1.364B | +1.298B | -0.066B | -4.70% |
| GVR (BAL) | +1.385B | +1.410B | +0.025B | +1.95% |
| DPR (BAL) | +0.069B | +0.067B | -0.003B | -3.68% |
| PHR (BAL) | +0.003B | +0.004B | +0.000B | +1.87% |
| MSN (BAL) | +1.488B | +1.417B | -0.071B | -4.61% |
| PSI (BAL) | +1.241B | +1.252B | +0.011B | +1.07% |
| AMS (BAL) | +1.053B | +1.013B | -0.040B | -3.64% |
| PSD (BAL) | +1.488B | +1.402B | -0.087B | -5.69% |
| VHM (VN30) | +0.778B | +0.835B | +0.057B | +7.53% |
| VRE (VN30) | +0.839B | +0.769B | -0.070B | -8.22% |
| MWG (VN30) | +0.922B | +0.838B | -0.085B | -9.07% |
| MSN (VN30) | +0.972B | +0.926B | -0.046B | -4.61% |
| GEX (VN30) | +1.069B | +1.153B | +0.084B | +8.06% |
| PVD (VN30) | +1.097B | +1.095B | -0.002B | +0.00% |
| E1VFVN30 (BAL) | +7.328B | +7.780B | +0.451B | +6.16% |
| E1VFVN30 (VN30) | +14.155B | +15.026B | +0.872B | +6.16% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -20.593B |
| + ETF net cash flow + MTM | +2.114B |
| + Stock unrealized MTM | +20.137B (cost 20.593B → realized would be -0.456B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +20.5934B |
| + Stock sells (sell_amount - fee in) | +0.0000B |
| - ETF buys (buy_amount + fee out) | +35.0525B |
| + ETF sells (sell_amount - fee in) | +14.3608B |
| = Expected end cash (from transactions only) | +8.7149B |
| Actual end cash (from logs) | +8.7149B |
| **Diff (ETF appreciation rebalanced into cash)** | **+0.0000B** |
| Actual end ETF balance (still in cash_etf) | +22.8059B |
| Open stock positions mark value | +20.1371B |
| = **Final NAV (cash + ETF + open stocks)** | **+51.6580B** |

**Note on `Diff` line**: when ETF appreciates daily by VN30 return, cash_etf grows.
The rebalance logic (target 70% of total cash+ETF in state=NEUTRAL) periodically moves
a portion OUT of cash_etf and INTO cash. Those are logged as ETF 'sell' transactions,
but the moved amount EXCEEDS the original cost basis (because ETF appreciated meanwhile).
The diff line = appreciation that flowed to cash via rebalances. To FULLY reconcile,
compute ETF return = (etf_sells + etf_etf_residual_mark) − etf_buys − etf_fees.

### Per-book daily breakdown (in logs CSV)

The `data/pt_v11_tq34b_logs.csv` now has 6 per-book columns:
`BAL_cash`, `BAL_stocks`, `BAL_etf`, `VN30_cash`, `VN30_stocks`, `VN30_etf`.
Each row: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf = NAV`.
Cross-check at any date: when ETF is bought in BAL, BAL_cash decreases and BAL_etf increases (minus friction).

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
| Stock buys — share cost | +20.5625B |
| Stock buys — fee | +0.0308B |
| Stock sells — gross | +0.0000B |
| Stock sells — fee+tax | +0.0000B |
| **Net stock realized P&L** | **-20.5934B** |
| ETF buys — share cost | +35.0000B |
| ETF buys — friction | +0.0525B |
| ETF sells — gross | +14.3823B |
| ETF sells — friction | +0.0216B |
| **Net ETF cash flow** | **-20.6917B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| PAN (BAL) | +0.747B | +0.754B | +0.007B | +1.08% |
| VHM (BAL) | +0.827B | +0.888B | +0.061B | +7.53% |
| VIC (BAL) | +0.910B | +0.955B | +0.046B | +5.19% |
| KSF (BAL) | +0.945B | +0.856B | -0.088B | -9.23% |
| VJC (BAL) | +1.026B | +0.968B | -0.058B | -5.49% |
| POW (BAL) | +1.128B | +1.099B | -0.029B | -2.44% |
| VRE (BAL) | +1.241B | +1.137B | -0.104B | -8.22% |
| AAA (BAL) | +1.364B | +1.298B | -0.066B | -4.70% |
| GVR (BAL) | +1.385B | +1.410B | +0.025B | +1.95% |
| DPR (BAL) | +0.069B | +0.067B | -0.003B | -3.68% |
| PHR (BAL) | +0.003B | +0.004B | +0.000B | +1.87% |
| MSN (BAL) | +1.488B | +1.417B | -0.071B | -4.61% |
| PSI (BAL) | +1.241B | +1.252B | +0.011B | +1.07% |
| AMS (BAL) | +1.053B | +1.013B | -0.040B | -3.64% |
| PSD (BAL) | +1.488B | +1.402B | -0.087B | -5.69% |
| VHM (VN30) | +0.778B | +0.835B | +0.057B | +7.53% |
| VRE (VN30) | +0.839B | +0.769B | -0.070B | -8.22% |
| MWG (VN30) | +0.922B | +0.838B | -0.085B | -9.07% |
| MSN (VN30) | +0.972B | +0.926B | -0.046B | -4.61% |
| GEX (VN30) | +1.069B | +1.153B | +0.084B | +8.06% |
| PVD (VN30) | +1.097B | +1.095B | -0.002B | +0.00% |
| E1VFVN30 (BAL) | +7.328B | +7.780B | +0.451B | +6.16% |
| E1VFVN30 (VN30) | +14.155B | +15.026B | +0.872B | +6.16% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -20.593B |
| + ETF net cash flow + MTM | +2.114B |
| + Stock unrealized MTM | +20.137B (cost 20.593B → realized would be -0.456B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +20.5934B |
| + Stock sells (sell_amount - fee in) | +0.0000B |
| - ETF buys (buy_amount + fee out) | +35.0525B |
| + ETF sells (sell_amount - fee in) | +14.3608B |
| = Expected end cash (from transactions only) | +8.7149B |
| Actual end cash (from logs) | +8.7149B |
| **Diff (ETF appreciation rebalanced into cash)** | **+0.0000B** |
| Actual end ETF balance (still in cash_etf) | +22.8059B |
| Open stock positions mark value | +20.1371B |
| = **Final NAV (cash + ETF + open stocks)** | **+51.6580B** |

**Note on `Diff` line**: when ETF appreciates daily by VN30 return, cash_etf grows.
The rebalance logic (target 70% of total cash+ETF in state=NEUTRAL) periodically moves
a portion OUT of cash_etf and INTO cash. Those are logged as ETF 'sell' transactions,
but the moved amount EXCEEDS the original cost basis (because ETF appreciated meanwhile).
The diff line = appreciation that flowed to cash via rebalances. To FULLY reconcile,
compute ETF return = (etf_sells + etf_etf_residual_mark) − etf_buys − etf_fees.

### Per-book daily breakdown (in logs CSV)

The `data/pt_v11_tq34b_logs.csv` now has 6 per-book columns:
`BAL_cash`, `BAL_stocks`, `BAL_etf`, `VN30_cash`, `VN30_stocks`, `VN30_etf`.
Each row: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf = NAV`.
Cross-check at any date: when ETF is bought in BAL, BAL_cash decreases and BAL_etf increases (minus friction).

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
| Stock buys — share cost | +43.0263B |
| Stock buys — fee | +0.0645B |
| Stock sells — gross | +0.7645B |
| Stock sells — fee+tax | +0.0019B |
| **Net stock realized P&L** | **-42.3282B** |
| ETF buys — share cost | +35.0002B |
| ETF buys — friction | +0.0525B |
| ETF sells — gross | +28.5454B |
| ETF sells — friction | +0.0428B |
| **Net ETF cash flow** | **-6.5501B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| PAN (BAL) | +2.503B | +2.526B | +0.023B | +1.08% |
| VHM (BAL) | +2.571B | +2.761B | +0.190B | +7.53% |
| VIC (BAL) | +2.828B | +2.970B | +0.142B | +5.19% |
| VJC (BAL) | +2.640B | +2.491B | -0.149B | -5.49% |
| POW (BAL) | +2.902B | +2.827B | -0.075B | -2.44% |
| VRE (BAL) | +3.188B | +2.922B | -0.266B | -8.22% |
| GVR (BAL) | +3.503B | +3.567B | +0.063B | +1.95% |
| DPR (BAL) | +2.093B | +2.013B | -0.080B | -3.68% |
| PHR (BAL) | +0.105B | +0.106B | +0.002B | +1.87% |
| PCH (BAL) | +0.005B | +0.005B | -0.000B | -0.90% |
| KSF (BAL) | +1.685B | +1.574B | -0.111B | -6.47% |
| AAA (BAL) | +2.002B | +1.928B | -0.075B | -3.59% |
| VHM (VN30) | +2.588B | +2.779B | +0.191B | +7.53% |
| VRE (VN30) | +2.652B | +2.430B | -0.222B | -8.22% |
| MWG (VN30) | +2.916B | +2.648B | -0.268B | -9.07% |
| MSN (VN30) | +2.645B | +2.519B | -0.126B | -4.61% |
| GEX (VN30) | +2.909B | +3.139B | +0.230B | +8.06% |
| PVD (VN30) | +2.588B | +2.584B | -0.004B | +0.00% |
| E1VFVN30 (VN30) | +8.152B | +8.654B | +0.502B | +6.16% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -42.328B |
| + ETF net cash flow + MTM | +2.104B |
| + Stock unrealized MTM | +41.787B (cost 42.323B → realized would be -0.536B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +43.0908B |
| + Stock sells (sell_amount - fee in) | +0.7626B |
| - ETF buys (buy_amount + fee out) | +35.0527B |
| + ETF sells (sell_amount - fee in) | +28.5026B |
| = Expected end cash (from transactions only) | +1.1217B |
| Actual end cash (from logs) | +1.1217B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0000B** |
| Actual end ETF balance (still in cash_etf) | +8.6544B |
| Open stock positions mark value | +41.7874B |
| = **Final NAV (cash + ETF + open stocks)** | **+51.5635B** |

**Note on `Diff` line**: when ETF appreciates daily by VN30 return, cash_etf grows.
The rebalance logic (target 70% of total cash+ETF in state=NEUTRAL) periodically moves
a portion OUT of cash_etf and INTO cash. Those are logged as ETF 'sell' transactions,
but the moved amount EXCEEDS the original cost basis (because ETF appreciated meanwhile).
The diff line = appreciation that flowed to cash via rebalances. To FULLY reconcile,
compute ETF return = (etf_sells + etf_etf_residual_mark) − etf_buys − etf_fees.

### Per-book daily breakdown (in logs CSV)

The `data/pt_v11_tq34b_logs.csv` now has 6 per-book columns:
`BAL_cash`, `BAL_stocks`, `BAL_etf`, `VN30_cash`, `VN30_stocks`, `VN30_etf`.
Each row: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf = NAV`.
Cross-check at any date: when ETF is bought in BAL, BAL_cash decreases and BAL_etf increases (minus friction).

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
| Stock buys — share cost | +43.0263B |
| Stock buys — fee | +0.0645B |
| Stock sells — gross | +0.7645B |
| Stock sells — fee+tax | +0.0019B |
| **Net stock realized P&L** | **-42.3282B** |
| ETF buys — share cost | +35.0002B |
| ETF buys — friction | +0.0525B |
| ETF sells — gross | +28.5454B |
| ETF sells — friction | +0.0428B |
| **Net ETF cash flow** | **-6.5501B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| PAN (BAL) | +2.503B | +2.526B | +0.023B | +1.08% |
| VHM (BAL) | +2.571B | +2.761B | +0.190B | +7.53% |
| VIC (BAL) | +2.828B | +2.970B | +0.142B | +5.19% |
| VJC (BAL) | +2.640B | +2.491B | -0.149B | -5.49% |
| POW (BAL) | +2.902B | +2.827B | -0.075B | -2.44% |
| VRE (BAL) | +3.188B | +2.922B | -0.266B | -8.22% |
| GVR (BAL) | +3.503B | +3.567B | +0.063B | +1.95% |
| DPR (BAL) | +2.093B | +2.013B | -0.080B | -3.68% |
| PHR (BAL) | +0.105B | +0.106B | +0.002B | +1.87% |
| PCH (BAL) | +0.005B | +0.005B | -0.000B | -0.90% |
| KSF (BAL) | +1.685B | +1.574B | -0.111B | -6.47% |
| AAA (BAL) | +2.002B | +1.928B | -0.075B | -3.59% |
| VHM (VN30) | +2.588B | +2.779B | +0.191B | +7.53% |
| VRE (VN30) | +2.652B | +2.430B | -0.222B | -8.22% |
| MWG (VN30) | +2.916B | +2.648B | -0.268B | -9.07% |
| MSN (VN30) | +2.645B | +2.519B | -0.126B | -4.61% |
| GEX (VN30) | +2.909B | +3.139B | +0.230B | +8.06% |
| PVD (VN30) | +2.588B | +2.584B | -0.004B | +0.00% |
| E1VFVN30 (VN30) | +8.152B | +8.654B | +0.502B | +6.16% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -42.328B |
| + ETF net cash flow + MTM | +2.104B |
| + Stock unrealized MTM | +41.787B (cost 42.323B → realized would be -0.536B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +43.0908B |
| + Stock sells (sell_amount - fee in) | +0.7626B |
| - ETF buys (buy_amount + fee out) | +35.0527B |
| + ETF sells (sell_amount - fee in) | +28.5026B |
| = Expected end cash (from transactions only) | +1.1217B |
| Actual end cash (from logs) | +1.1217B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0000B** |
| Actual end ETF balance (still in cash_etf) | +8.6544B |
| Open stock positions mark value | +41.7874B |
| = **Final NAV (cash + ETF + open stocks)** | **+51.5635B** |

**Note on `Diff` line**: when ETF appreciates daily by VN30 return, cash_etf grows.
The rebalance logic (target 70% of total cash+ETF in state=NEUTRAL) periodically moves
a portion OUT of cash_etf and INTO cash. Those are logged as ETF 'sell' transactions,
but the moved amount EXCEEDS the original cost basis (because ETF appreciated meanwhile).
The diff line = appreciation that flowed to cash via rebalances. To FULLY reconcile,
compute ETF return = (etf_sells + etf_etf_residual_mark) − etf_buys − etf_fees.

### Per-book daily breakdown (in logs CSV)

The `data/pt_v11_tq34b_logs.csv` now has 6 per-book columns:
`BAL_cash`, `BAL_stocks`, `BAL_etf`, `VN30_cash`, `VN30_stocks`, `VN30_etf`.
Each row: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf = NAV`.
Cross-check at any date: when ETF is bought in BAL, BAL_cash decreases and BAL_etf increases (minus friction).

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
| Stock buys — share cost | +43.0263B |
| Stock buys — fee | +0.0645B |
| Stock sells — gross | +0.7645B |
| Stock sells — fee+tax | +0.0019B |
| **Net stock realized P&L** | **-42.3282B** |
| ETF buys — share cost | +35.0002B |
| ETF buys — friction | +0.0525B |
| ETF sells — gross | +28.5454B |
| ETF sells — friction | +0.0428B |
| **Net ETF cash flow** | **-6.5501B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| PAN (BAL) | +2.503B | +2.526B | +0.023B | +1.08% |
| VHM (BAL) | +2.571B | +2.761B | +0.190B | +7.53% |
| VIC (BAL) | +2.828B | +2.970B | +0.142B | +5.19% |
| VJC (BAL) | +2.640B | +2.491B | -0.149B | -5.49% |
| POW (BAL) | +2.902B | +2.827B | -0.075B | -2.44% |
| VRE (BAL) | +3.188B | +2.922B | -0.266B | -8.22% |
| GVR (BAL) | +3.501B | +3.564B | +0.063B | +1.95% |
| DPR (BAL) | +2.095B | +2.015B | -0.080B | -3.68% |
| PHR (BAL) | +0.105B | +0.107B | +0.002B | +1.87% |
| PCH (BAL) | +0.005B | +0.005B | -0.000B | -0.90% |
| KSF (BAL) | +1.685B | +1.574B | -0.111B | -6.47% |
| AAA (BAL) | +2.002B | +1.928B | -0.075B | -3.59% |
| VHM (VN30) | +2.588B | +2.779B | +0.191B | +7.53% |
| VRE (VN30) | +2.652B | +2.430B | -0.222B | -8.22% |
| MWG (VN30) | +2.916B | +2.648B | -0.268B | -9.07% |
| MSN (VN30) | +2.645B | +2.519B | -0.126B | -4.61% |
| GEX (VN30) | +2.909B | +3.139B | +0.230B | +8.06% |
| PVD (VN30) | +2.588B | +2.584B | -0.004B | +0.00% |
| E1VFVN30 (VN30) | +8.152B | +8.654B | +0.502B | +6.16% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -42.328B |
| + ETF net cash flow + MTM | +2.104B |
| + Stock unrealized MTM | +41.787B (cost 42.323B → realized would be -0.536B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +43.0908B |
| + Stock sells (sell_amount - fee in) | +0.7626B |
| - ETF buys (buy_amount + fee out) | +35.0527B |
| + ETF sells (sell_amount - fee in) | +28.5026B |
| = Expected end cash (from transactions only) | +1.1217B |
| Actual end cash (from logs) | +1.1217B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0000B** |
| Actual end ETF balance (still in cash_etf) | +8.6544B |
| Open stock positions mark value | +41.7873B |
| = **Final NAV (cash + ETF + open stocks)** | **+51.5634B** |

**Note on `Diff` line**: when ETF appreciates daily by VN30 return, cash_etf grows.
The rebalance logic (target 70% of total cash+ETF in state=NEUTRAL) periodically moves
a portion OUT of cash_etf and INTO cash. Those are logged as ETF 'sell' transactions,
but the moved amount EXCEEDS the original cost basis (because ETF appreciated meanwhile).
The diff line = appreciation that flowed to cash via rebalances. To FULLY reconcile,
compute ETF return = (etf_sells + etf_etf_residual_mark) − etf_buys − etf_fees.

### Per-book daily breakdown (in logs CSV)

The `data/pt_v11_tq34b_logs.csv` now has 6 per-book columns:
`BAL_cash`, `BAL_stocks`, `BAL_etf`, `VN30_cash`, `VN30_stocks`, `VN30_etf`.
Each row: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf = NAV`.
Cross-check at any date: when ETF is bought in BAL, BAL_cash decreases and BAL_etf increases (minus friction).

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
| Stock buys — share cost | +13.1132B |
| Stock buys — fee | +0.0197B |
| Stock sells — gross | +0.0000B |
| Stock sells — fee+tax | +0.0000B |
| **Net stock realized P&L** | **-13.1329B** |
| ETF buys — share cost | +35.0000B |
| ETF buys — friction | +0.0525B |
| ETF sells — gross | +9.8327B |
| ETF sells — friction | +0.0147B |
| **Net ETF cash flow** | **-25.2345B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| PAN (BAL) | +2.563B | +2.547B | -0.016B | -0.46% |
| VHM (BAL) | +2.577B | +2.767B | +0.190B | +7.53% |
| VIC (BAL) | +2.834B | +2.976B | +0.143B | +5.19% |
| KSF (BAL) | +2.569B | +2.456B | -0.113B | -4.26% |
| VHM (VN30) | +2.590B | +2.781B | +0.191B | +7.53% |
| E1VFVN30 (BAL) | +10.169B | +10.812B | +0.642B | +6.31% |
| E1VFVN30 (VN30) | +15.492B | +16.470B | +0.978B | +6.31% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -13.133B |
| + ETF net cash flow + MTM | +2.047B |
| + Stock unrealized MTM | +13.528B (cost 13.133B → realized would be +0.395B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +13.1329B |
| + Stock sells (sell_amount - fee in) | +0.0000B |
| - ETF buys (buy_amount + fee out) | +35.0525B |
| + ETF sells (sell_amount - fee in) | +9.8180B |
| = Expected end cash (from transactions only) | +11.6325B |
| Actual end cash (from logs) | +11.6325B |
| **Diff (ETF appreciation rebalanced into cash)** | **+0.0000B** |
| Actual end ETF balance (still in cash_etf) | +27.2818B |
| Open stock positions mark value | +13.5278B |
| = **Final NAV (cash + ETF + open stocks)** | **+52.4422B** |

**Note on `Diff` line**: when ETF appreciates daily by VN30 return, cash_etf grows.
The rebalance logic (target 70% of total cash+ETF in state=NEUTRAL) periodically moves
a portion OUT of cash_etf and INTO cash. Those are logged as ETF 'sell' transactions,
but the moved amount EXCEEDS the original cost basis (because ETF appreciated meanwhile).
The diff line = appreciation that flowed to cash via rebalances. To FULLY reconcile,
compute ETF return = (etf_sells + etf_etf_residual_mark) − etf_buys − etf_fees.

### Per-book daily breakdown (in logs CSV)

The `data/pt_v11_tq34b_logs.csv` now has 6 per-book columns:
`BAL_cash`, `BAL_stocks`, `BAL_etf`, `VN30_cash`, `VN30_stocks`, `VN30_etf`.
Each row: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf = NAV`.
Cross-check at any date: when ETF is bought in BAL, BAL_cash decreases and BAL_etf increases (minus friction).

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
| Stock buys — share cost | +13.1132B |
| Stock buys — fee | +0.0197B |
| Stock sells — gross | +0.0000B |
| Stock sells — fee+tax | +0.0000B |
| **Net stock realized P&L** | **-13.1329B** |
| ETF buys — share cost | +35.0000B |
| ETF buys — friction | +0.0525B |
| ETF sells — gross | +9.8327B |
| ETF sells — friction | +0.0147B |
| **Net ETF cash flow** | **-25.2345B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| PAN (BAL) | +2.563B | +2.547B | -0.016B | -0.46% |
| VHM (BAL) | +2.577B | +2.767B | +0.190B | +7.53% |
| VIC (BAL) | +2.834B | +2.976B | +0.143B | +5.19% |
| KSF (BAL) | +2.569B | +2.456B | -0.113B | -4.26% |
| VHM (VN30) | +2.590B | +2.781B | +0.191B | +7.53% |
| E1VFVN30 (BAL) | +10.169B | +10.812B | +0.642B | +6.31% |
| E1VFVN30 (VN30) | +15.492B | +16.470B | +0.978B | +6.31% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -13.133B |
| + ETF net cash flow + MTM | +2.047B |
| + Stock unrealized MTM | +13.528B (cost 13.133B → realized would be +0.395B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +13.1329B |
| + Stock sells (sell_amount - fee in) | +0.0000B |
| - ETF buys (buy_amount + fee out) | +35.0525B |
| + ETF sells (sell_amount - fee in) | +9.8180B |
| = Expected end cash (from transactions only) | +11.6325B |
| Actual end cash (from logs) | +11.6325B |
| **Diff (ETF appreciation rebalanced into cash)** | **+0.0000B** |
| Actual end ETF balance (still in cash_etf) | +27.2818B |
| Open stock positions mark value | +13.5278B |
| = **Final NAV (cash + ETF + open stocks)** | **+52.4422B** |

**Note on `Diff` line**: when ETF appreciates daily by VN30 return, cash_etf grows.
The rebalance logic (target 70% of total cash+ETF in state=NEUTRAL) periodically moves
a portion OUT of cash_etf and INTO cash. Those are logged as ETF 'sell' transactions,
but the moved amount EXCEEDS the original cost basis (because ETF appreciated meanwhile).
The diff line = appreciation that flowed to cash via rebalances. To FULLY reconcile,
compute ETF return = (etf_sells + etf_etf_residual_mark) − etf_buys − etf_fees.

### Per-book daily breakdown (in logs CSV)

The `data/pt_v11_tq34b_logs.csv` now has 6 per-book columns:
`BAL_cash`, `BAL_stocks`, `BAL_etf`, `VN30_cash`, `VN30_stocks`, `VN30_etf`.
Each row: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf = NAV`.
Cross-check at any date: when ETF is bought in BAL, BAL_cash decreases and BAL_etf increases (minus friction).

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
| Stock buys — share cost | +11.8673B |
| Stock buys — fee | +0.0178B |
| Stock sells — gross | +1.0599B |
| Stock sells — fee+tax | +0.0026B |
| **Net stock realized P&L** | **-10.8278B** |
| ETF buys — share cost | +55.0457B |
| ETF buys — friction | +0.0826B |
| ETF sells — gross | +16.5178B |
| ETF sells — friction | +0.0248B |
| **Net ETF cash flow** | **-38.6352B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| PAN (BAL) | +2.506B | +2.490B | -0.015B | -0.46% |
| VHM (BAL) | +2.701B | +2.900B | +0.199B | +7.53% |
| VIC (BAL) | +2.970B | +3.119B | +0.149B | +5.19% |
| VHM (VN30) | +2.544B | +2.732B | +0.188B | +7.53% |
| E1VFVN30 (BAL) | +12.333B | +13.562B | +1.229B | +9.96% |
| E1VFVN30 (BAL) | +0.132B | +0.135B | +0.003B | +2.46% |
| E1VFVN30 (BAL) | +2.109B | +2.128B | +0.019B | +0.92% |
| E1VFVN30 (BAL) | +0.514B | +0.507B | -0.007B | -1.31% |
| E1VFVN30 (BAL) | +2.157B | +2.148B | -0.009B | -0.41% |
| E1VFVN30 (VN30) | +22.503B | +24.746B | +2.242B | +9.96% |
| E1VFVN30 (VN30) | +0.134B | +0.135B | +0.001B | +0.92% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -10.828B |
| + ETF net cash flow + MTM | +4.726B |
| + Stock unrealized MTM | +11.242B (cost 10.721B → realized would be +0.521B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +11.8851B |
| + Stock sells (sell_amount - fee in) | +1.0573B |
| - ETF buys (buy_amount + fee out) | +55.1283B |
| + ETF sells (sell_amount - fee in) | +16.4931B |
| = Expected end cash (from transactions only) | +0.5370B |
| Actual end cash (from logs) | +0.5365B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0005B** |
| Actual end ETF balance (still in cash_etf) | +43.3612B |
| Open stock positions mark value | +11.2418B |
| = **Final NAV (cash + ETF + open stocks)** | **+55.1394B** |

**Note on `Diff` line**: when ETF appreciates daily by VN30 return, cash_etf grows.
The rebalance logic (target 70% of total cash+ETF in state=NEUTRAL) periodically moves
a portion OUT of cash_etf and INTO cash. Those are logged as ETF 'sell' transactions,
but the moved amount EXCEEDS the original cost basis (because ETF appreciated meanwhile).
The diff line = appreciation that flowed to cash via rebalances. To FULLY reconcile,
compute ETF return = (etf_sells + etf_etf_residual_mark) − etf_buys − etf_fees.

### Per-book daily breakdown (in logs CSV)

The `data/pt_v11_tq34b_logs.csv` now has 6 per-book columns:
`BAL_cash`, `BAL_stocks`, `BAL_etf`, `VN30_cash`, `VN30_stocks`, `VN30_etf`.
Each row: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf = NAV`.
Cross-check at any date: when ETF is bought in BAL, BAL_cash decreases and BAL_etf increases (minus friction).

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
| Stock buys — share cost | +12.4032B |
| Stock buys — fee | +0.0186B |
| Stock sells — gross | +1.0599B |
| Stock sells — fee+tax | +0.0026B |
| **Net stock realized P&L** | **-11.3645B** |
| ETF buys — share cost | +55.0457B |
| ETF buys — friction | +0.0826B |
| ETF sells — gross | +16.5178B |
| ETF sells — friction | +0.0248B |
| **Net ETF cash flow** | **-38.6352B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| PAN (BAL) | +2.506B | +2.551B | +0.046B | +1.98% |
| VHM (BAL) | +2.701B | +2.841B | +0.140B | +5.34% |
| VIC (BAL) | +2.970B | +2.951B | -0.018B | -0.47% |
| TVN (BAL) | +0.274B | +0.274B | -0.000B | +0.00% |
| VHM (VN30) | +2.544B | +2.676B | +0.132B | +5.34% |
| E1VFVN30 (BAL) | +12.333B | +13.562B | +1.229B | +9.96% |
| E1VFVN30 (BAL) | +0.132B | +0.135B | +0.003B | +2.46% |
| E1VFVN30 (BAL) | +2.109B | +2.128B | +0.019B | +0.92% |
| E1VFVN30 (BAL) | +0.514B | +0.507B | -0.007B | -1.31% |
| E1VFVN30 (BAL) | +2.157B | +2.148B | -0.009B | -0.41% |
| E1VFVN30 (VN30) | +22.503B | +24.746B | +2.242B | +9.96% |
| E1VFVN30 (VN30) | +0.134B | +0.135B | +0.001B | +0.92% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -11.364B |
| + ETF net cash flow + MTM | +4.726B |
| + Stock unrealized MTM | +11.294B (cost 10.995B → realized would be +0.299B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +12.4218B |
| + Stock sells (sell_amount - fee in) | +1.0573B |
| - ETF buys (buy_amount + fee out) | +55.1283B |
| + ETF sells (sell_amount - fee in) | +16.4931B |
| = Expected end cash (from transactions only) | +0.0003B |
| Actual end cash (from logs) | -0.0002B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0005B** |
| Actual end ETF balance (still in cash_etf) | +43.3612B |
| Open stock positions mark value | +11.2939B |
| = **Final NAV (cash + ETF + open stocks)** | **+54.9238B** |

**Note on `Diff` line**: when ETF appreciates daily by VN30 return, cash_etf grows.
The rebalance logic (target 70% of total cash+ETF in state=NEUTRAL) periodically moves
a portion OUT of cash_etf and INTO cash. Those are logged as ETF 'sell' transactions,
but the moved amount EXCEEDS the original cost basis (because ETF appreciated meanwhile).
The diff line = appreciation that flowed to cash via rebalances. To FULLY reconcile,
compute ETF return = (etf_sells + etf_etf_residual_mark) − etf_buys − etf_fees.

### Per-book daily breakdown (in logs CSV)

The `data/pt_v11_tq34b_logs.csv` now has 6 per-book columns:
`BAL_cash`, `BAL_stocks`, `BAL_etf`, `VN30_cash`, `VN30_stocks`, `VN30_etf`.
Each row: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf = NAV`.
Cross-check at any date: when ETF is bought in BAL, BAL_cash decreases and BAL_etf increases (minus friction).

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
| Stock buys — share cost | +13.6753B |
| Stock buys — fee | +0.0205B |
| Stock sells — gross | +1.0599B |
| Stock sells — fee+tax | +0.0026B |
| **Net stock realized P&L** | **-12.6385B** |
| ETF buys — share cost | +59.2230B |
| ETF buys — friction | +0.0888B |
| ETF sells — gross | +21.9818B |
| ETF sells — friction | +0.0330B |
| **Net ETF cash flow** | **-37.3630B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| PAN (BAL) | +2.506B | +2.506B | +0.000B | +0.15% |
| VHM (BAL) | +2.701B | +2.913B | +0.212B | +8.01% |
| VIC (BAL) | +2.970B | +2.921B | -0.049B | -1.50% |
| VHM (VN30) | +2.544B | +2.744B | +0.200B | +8.01% |
| E1VFVN30 (BAL) | +7.331B | +7.971B | +0.639B | +8.72% |
| E1VFVN30 (BAL) | +0.132B | +0.134B | +0.002B | +1.30% |
| E1VFVN30 (BAL) | +2.109B | +2.104B | -0.005B | -0.22% |
| E1VFVN30 (BAL) | +0.514B | +0.502B | -0.012B | -2.43% |
| E1VFVN30 (BAL) | +2.157B | +2.124B | -0.033B | -1.54% |
| E1VFVN30 (BAL) | +0.537B | +0.531B | -0.006B | -1.05% |
| E1VFVN30 (BAL) | +2.484B | +2.477B | -0.007B | -0.28% |
| E1VFVN30 (BAL) | +1.156B | +1.148B | -0.008B | -0.69% |
| E1VFVN30 (VN30) | +22.503B | +24.465B | +1.962B | +8.72% |
| E1VFVN30 (VN30) | +0.134B | +0.134B | -0.000B | -0.22% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -12.638B |
| + ETF net cash flow + MTM | +4.226B |
| + Stock unrealized MTM | +11.084B (cost 10.721B → realized would be +0.363B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +13.6958B |
| + Stock sells (sell_amount - fee in) | +1.0573B |
| - ETF buys (buy_amount + fee out) | +59.3118B |
| + ETF sells (sell_amount - fee in) | +21.9488B |
| = Expected end cash (from transactions only) | -0.0014B |
| Actual end cash (from logs) | -0.0019B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0005B** |
| Actual end ETF balance (still in cash_etf) | +41.5893B |
| Open stock positions mark value | +11.0840B |
| = **Final NAV (cash + ETF + open stocks)** | **+54.5230B** |

**Note on `Diff` line**: when ETF appreciates daily by VN30 return, cash_etf grows.
The rebalance logic (target 70% of total cash+ETF in state=NEUTRAL) periodically moves
a portion OUT of cash_etf and INTO cash. Those are logged as ETF 'sell' transactions,
but the moved amount EXCEEDS the original cost basis (because ETF appreciated meanwhile).
The diff line = appreciation that flowed to cash via rebalances. To FULLY reconcile,
compute ETF return = (etf_sells + etf_etf_residual_mark) − etf_buys − etf_fees.

### Per-book daily breakdown (in logs CSV)

The `data/pt_v11_tq34b_logs.csv` now has 6 per-book columns:
`BAL_cash`, `BAL_stocks`, `BAL_etf`, `VN30_cash`, `VN30_stocks`, `VN30_etf`.
Each row: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf = NAV`.
Cross-check at any date: when ETF is bought in BAL, BAL_cash decreases and BAL_etf increases (minus friction).

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
| Stock buys — share cost | +13.6753B |
| Stock buys — fee | +0.0205B |
| Stock sells — gross | +1.0599B |
| Stock sells — fee+tax | +0.0026B |
| **Net stock realized P&L** | **-12.6385B** |
| ETF buys — share cost | +59.2230B |
| ETF buys — friction | +0.0888B |
| ETF sells — gross | +21.9818B |
| ETF sells — friction | +0.0330B |
| **Net ETF cash flow** | **-37.3630B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| PAN (BAL) | +2.506B | +2.506B | +0.000B | +0.15% |
| VHM (BAL) | +2.701B | +2.913B | +0.212B | +8.01% |
| VIC (BAL) | +2.970B | +2.921B | -0.049B | -1.50% |
| VHM (VN30) | +2.544B | +2.744B | +0.200B | +8.01% |
| E1VFVN30 (BAL) | +7.331B | +7.971B | +0.639B | +8.72% |
| E1VFVN30 (BAL) | +0.132B | +0.134B | +0.002B | +1.30% |
| E1VFVN30 (BAL) | +2.109B | +2.104B | -0.005B | -0.22% |
| E1VFVN30 (BAL) | +0.514B | +0.502B | -0.012B | -2.43% |
| E1VFVN30 (BAL) | +2.157B | +2.124B | -0.033B | -1.54% |
| E1VFVN30 (BAL) | +0.537B | +0.531B | -0.006B | -1.05% |
| E1VFVN30 (BAL) | +2.484B | +2.477B | -0.007B | -0.28% |
| E1VFVN30 (BAL) | +1.156B | +1.148B | -0.008B | -0.69% |
| E1VFVN30 (VN30) | +22.503B | +24.465B | +1.962B | +8.72% |
| E1VFVN30 (VN30) | +0.134B | +0.134B | -0.000B | -0.22% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -12.638B |
| + ETF net cash flow + MTM | +4.226B |
| + Stock unrealized MTM | +11.084B (cost 10.721B → realized would be +0.363B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +13.6958B |
| + Stock sells (sell_amount - fee in) | +1.0573B |
| - ETF buys (buy_amount + fee out) | +59.3118B |
| + ETF sells (sell_amount - fee in) | +21.9488B |
| = Expected end cash (from transactions only) | -0.0014B |
| Actual end cash (from logs) | -0.0019B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0005B** |
| Actual end ETF balance (still in cash_etf) | +41.5893B |
| Open stock positions mark value | +11.0840B |
| = **Final NAV (cash + ETF + open stocks)** | **+54.5230B** |

**Note on `Diff` line**: when ETF appreciates daily by VN30 return, cash_etf grows.
The rebalance logic (target 70% of total cash+ETF in state=NEUTRAL) periodically moves
a portion OUT of cash_etf and INTO cash. Those are logged as ETF 'sell' transactions,
but the moved amount EXCEEDS the original cost basis (because ETF appreciated meanwhile).
The diff line = appreciation that flowed to cash via rebalances. To FULLY reconcile,
compute ETF return = (etf_sells + etf_etf_residual_mark) − etf_buys − etf_fees.

### Per-book daily breakdown (in logs CSV)

The `data/pt_v11_tq34b_logs.csv` now has 6 per-book columns:
`BAL_cash`, `BAL_stocks`, `BAL_etf`, `VN30_cash`, `VN30_stocks`, `VN30_etf`.
Each row: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf = NAV`.
Cross-check at any date: when ETF is bought in BAL, BAL_cash decreases and BAL_etf increases (minus friction).

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
| Stock buys — share cost | +13.6753B |
| Stock buys — fee | +0.0205B |
| Stock sells — gross | +1.5696B |
| Stock sells — fee+tax | +0.0039B |
| **Net stock realized P&L** | **-12.1301B** |
| ETF buys — share cost | +59.7296B |
| ETF buys — friction | +0.0896B |
| ETF sells — gross | +21.9818B |
| ETF sells — friction | +0.0330B |
| **Net ETF cash flow** | **-37.8703B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| PAN (BAL) | +2.506B | +1.862B | -0.644B | -25.57% |
| VHM (BAL) | +2.701B | +2.882B | +0.181B | +6.85% |
| VIC (BAL) | +2.970B | +2.928B | -0.042B | -1.26% |
| VHM (VN30) | +2.544B | +2.715B | +0.170B | +6.85% |
| E1VFVN30 (BAL) | +7.331B | +7.962B | +0.630B | +8.60% |
| E1VFVN30 (BAL) | +0.132B | +0.133B | +0.002B | +1.19% |
| E1VFVN30 (BAL) | +2.109B | +2.102B | -0.007B | -0.33% |
| E1VFVN30 (BAL) | +0.514B | +0.501B | -0.013B | -2.54% |
| E1VFVN30 (BAL) | +2.157B | +2.121B | -0.036B | -1.65% |
| E1VFVN30 (BAL) | +0.537B | +0.530B | -0.006B | -1.16% |
| E1VFVN30 (BAL) | +2.484B | +2.474B | -0.010B | -0.39% |
| E1VFVN30 (BAL) | +1.156B | +1.147B | -0.009B | -0.80% |
| E1VFVN30 (BAL) | +0.507B | +0.507B | +0.000B | +0.00% |
| E1VFVN30 (VN30) | +22.503B | +24.438B | +1.935B | +8.60% |
| E1VFVN30 (VN30) | +0.134B | +0.133B | -0.000B | -0.33% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -12.130B |
| + ETF net cash flow + MTM | +4.179B |
| + Stock unrealized MTM | +10.386B (cost 10.721B → realized would be -0.334B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +13.6958B |
| + Stock sells (sell_amount - fee in) | +1.5656B |
| - ETF buys (buy_amount + fee out) | +59.8192B |
| + ETF sells (sell_amount - fee in) | +21.9488B |
| = Expected end cash (from transactions only) | -0.0005B |
| Actual end cash (from logs) | -0.0010B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0005B** |
| Actual end ETF balance (still in cash_etf) | +42.0494B |
| Open stock positions mark value | +10.3864B |
| = **Final NAV (cash + ETF + open stocks)** | **+53.7875B** |

**Note on `Diff` line**: when ETF appreciates daily by VN30 return, cash_etf grows.
The rebalance logic (target 70% of total cash+ETF in state=NEUTRAL) periodically moves
a portion OUT of cash_etf and INTO cash. Those are logged as ETF 'sell' transactions,
but the moved amount EXCEEDS the original cost basis (because ETF appreciated meanwhile).
The diff line = appreciation that flowed to cash via rebalances. To FULLY reconcile,
compute ETF return = (etf_sells + etf_etf_residual_mark) − etf_buys − etf_fees.

### Per-book daily breakdown (in logs CSV)

The `data/pt_v11_tq34b_logs.csv` now has 6 per-book columns:
`BAL_cash`, `BAL_stocks`, `BAL_etf`, `VN30_cash`, `VN30_stocks`, `VN30_etf`.
Each row: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf = NAV`.
Cross-check at any date: when ETF is bought in BAL, BAL_cash decreases and BAL_etf increases (minus friction).

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
| Stock buys — share cost | +14.3949B |
| Stock buys — fee | +0.0216B |
| Stock sells — gross | +1.5696B |
| Stock sells — fee+tax | +0.0039B |
| **Net stock realized P&L** | **-12.8509B** |
| ETF buys — share cost | +61.8085B |
| ETF buys — friction | +0.0927B |
| ETF sells — gross | +24.7865B |
| ETF sells — friction | +0.0372B |
| **Net ETF cash flow** | **-37.1520B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| PAN (BAL) | +2.506B | +2.370B | -0.136B | -5.27% |
| VHM (BAL) | +2.701B | +2.786B | +0.085B | +3.29% |
| VIC (BAL) | +2.970B | +2.839B | -0.131B | -4.25% |
| TVN (BAL) | +1.310B | +1.206B | -0.103B | -7.76% |
| VHM (VN30) | +2.544B | +2.624B | +0.080B | +3.29% |
| E1VFVN30 (BAL) | +4.738B | +5.093B | +0.355B | +7.50% |
| E1VFVN30 (BAL) | +0.132B | +0.132B | +0.000B | +0.17% |
| E1VFVN30 (BAL) | +2.109B | +2.080B | -0.028B | -1.34% |
| E1VFVN30 (BAL) | +0.514B | +0.496B | -0.018B | -3.52% |
| E1VFVN30 (BAL) | +2.157B | +2.100B | -0.057B | -2.64% |
| E1VFVN30 (BAL) | +0.537B | +0.525B | -0.012B | -2.16% |
| E1VFVN30 (BAL) | +2.484B | +2.450B | -0.035B | -1.39% |
| E1VFVN30 (BAL) | +1.157B | +1.136B | -0.021B | -1.80% |
| E1VFVN30 (BAL) | +0.507B | +0.502B | -0.005B | -1.01% |
| E1VFVN30 (BAL) | +2.079B | +2.067B | -0.012B | -0.59% |
| E1VFVN30 (VN30) | +22.503B | +24.192B | +1.688B | +7.50% |
| E1VFVN30 (VN30) | +0.134B | +0.132B | -0.002B | -1.34% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -12.851B |
| + ETF net cash flow + MTM | +3.753B |
| + Stock unrealized MTM | +11.825B (cost 12.030B → realized would be -0.205B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +14.4165B |
| + Stock sells (sell_amount - fee in) | +1.5656B |
| - ETF buys (buy_amount + fee out) | +61.9012B |
| + ETF sells (sell_amount - fee in) | +24.7493B |
| = Expected end cash (from transactions only) | -0.0028B |
| Actual end cash (from logs) | -0.0033B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0005B** |
| Actual end ETF balance (still in cash_etf) | +40.9046B |
| Open stock positions mark value | +11.8253B |
| = **Final NAV (cash + ETF + open stocks)** | **+53.5149B** |

**Note on `Diff` line**: when ETF appreciates daily by VN30 return, cash_etf grows.
The rebalance logic (target 70% of total cash+ETF in state=NEUTRAL) periodically moves
a portion OUT of cash_etf and INTO cash. Those are logged as ETF 'sell' transactions,
but the moved amount EXCEEDS the original cost basis (because ETF appreciated meanwhile).
The diff line = appreciation that flowed to cash via rebalances. To FULLY reconcile,
compute ETF return = (etf_sells + etf_etf_residual_mark) − etf_buys − etf_fees.

### Per-book daily breakdown (in logs CSV)

The `data/pt_v11_tq34b_logs.csv` now has 6 per-book columns:
`BAL_cash`, `BAL_stocks`, `BAL_etf`, `VN30_cash`, `VN30_stocks`, `VN30_etf`.
Each row: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf = NAV`.
Cross-check at any date: when ETF is bought in BAL, BAL_cash decreases and BAL_etf increases (minus friction).

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
| Stock buys — share cost | +14.3949B |
| Stock buys — fee | +0.0216B |
| Stock sells — gross | +1.5696B |
| Stock sells — fee+tax | +0.0039B |
| **Net stock realized P&L** | **-12.8509B** |
| ETF buys — share cost | +61.8085B |
| ETF buys — friction | +0.0927B |
| ETF sells — gross | +24.7865B |
| ETF sells — friction | +0.0372B |
| **Net ETF cash flow** | **-37.1520B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| PAN (BAL) | +2.506B | +2.315B | -0.191B | -7.48% |
| VHM (BAL) | +2.701B | +2.771B | +0.070B | +2.74% |
| VIC (BAL) | +2.970B | +2.774B | -0.196B | -6.45% |
| TVN (BAL) | +1.310B | +1.263B | -0.047B | -3.45% |
| VHM (VN30) | +2.544B | +2.610B | +0.066B | +2.74% |
| E1VFVN30 (BAL) | +4.738B | +5.108B | +0.370B | +7.81% |
| E1VFVN30 (BAL) | +0.132B | +0.132B | +0.001B | +0.45% |
| E1VFVN30 (BAL) | +2.109B | +2.086B | -0.022B | -1.06% |
| E1VFVN30 (BAL) | +0.514B | +0.498B | -0.017B | -3.24% |
| E1VFVN30 (BAL) | +2.157B | +2.106B | -0.051B | -2.37% |
| E1VFVN30 (BAL) | +0.537B | +0.527B | -0.010B | -1.88% |
| E1VFVN30 (BAL) | +2.484B | +2.456B | -0.028B | -1.11% |
| E1VFVN30 (BAL) | +1.157B | +1.139B | -0.018B | -1.53% |
| E1VFVN30 (BAL) | +0.507B | +0.503B | -0.004B | -0.73% |
| E1VFVN30 (BAL) | +2.079B | +2.072B | -0.006B | -0.31% |
| E1VFVN30 (VN30) | +22.503B | +24.260B | +1.757B | +7.81% |
| E1VFVN30 (VN30) | +0.134B | +0.133B | -0.001B | -1.06% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -12.851B |
| + ETF net cash flow + MTM | +3.868B |
| + Stock unrealized MTM | +11.732B (cost 12.030B → realized would be -0.298B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +14.4165B |
| + Stock sells (sell_amount - fee in) | +1.5656B |
| - ETF buys (buy_amount + fee out) | +61.9012B |
| + ETF sells (sell_amount - fee in) | +24.7493B |
| = Expected end cash (from transactions only) | -0.0028B |
| Actual end cash (from logs) | -0.0033B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0005B** |
| Actual end ETF balance (still in cash_etf) | +41.0202B |
| Open stock positions mark value | +11.7325B |
| = **Final NAV (cash + ETF + open stocks)** | **+53.4918B** |

**Note on `Diff` line**: when ETF appreciates daily by VN30 return, cash_etf grows.
The rebalance logic (target 70% of total cash+ETF in state=NEUTRAL) periodically moves
a portion OUT of cash_etf and INTO cash. Those are logged as ETF 'sell' transactions,
but the moved amount EXCEEDS the original cost basis (because ETF appreciated meanwhile).
The diff line = appreciation that flowed to cash via rebalances. To FULLY reconcile,
compute ETF return = (etf_sells + etf_etf_residual_mark) − etf_buys − etf_fees.

### Per-book daily breakdown (in logs CSV)

The `data/pt_v11_tq34b_logs.csv` now has 6 per-book columns:
`BAL_cash`, `BAL_stocks`, `BAL_etf`, `VN30_cash`, `VN30_stocks`, `VN30_etf`.
Each row: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf = NAV`.
Cross-check at any date: when ETF is bought in BAL, BAL_cash decreases and BAL_etf increases (minus friction).

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
| Stock buys — share cost | +14.3949B |
| Stock buys — fee | +0.0216B |
| Stock sells — gross | +1.5696B |
| Stock sells — fee+tax | +0.0039B |
| **Net stock realized P&L** | **-12.8509B** |
| ETF buys — share cost | +61.8085B |
| ETF buys — friction | +0.0927B |
| ETF sells — gross | +24.7865B |
| ETF sells — friction | +0.0372B |
| **Net ETF cash flow** | **-37.1520B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| PAN (BAL) | +2.506B | +2.315B | -0.191B | -7.48% |
| VHM (BAL) | +2.701B | +2.771B | +0.070B | +2.74% |
| VIC (BAL) | +2.970B | +2.774B | -0.196B | -6.45% |
| TVN (BAL) | +1.310B | +1.263B | -0.047B | -3.45% |
| VHM (VN30) | +2.544B | +2.610B | +0.066B | +2.74% |
| E1VFVN30 (BAL) | +4.738B | +5.108B | +0.370B | +7.81% |
| E1VFVN30 (BAL) | +0.132B | +0.132B | +0.001B | +0.45% |
| E1VFVN30 (BAL) | +2.109B | +2.086B | -0.022B | -1.06% |
| E1VFVN30 (BAL) | +0.514B | +0.498B | -0.017B | -3.24% |
| E1VFVN30 (BAL) | +2.157B | +2.106B | -0.051B | -2.37% |
| E1VFVN30 (BAL) | +0.537B | +0.527B | -0.010B | -1.88% |
| E1VFVN30 (BAL) | +2.484B | +2.456B | -0.028B | -1.11% |
| E1VFVN30 (BAL) | +1.157B | +1.139B | -0.018B | -1.53% |
| E1VFVN30 (BAL) | +0.507B | +0.503B | -0.004B | -0.73% |
| E1VFVN30 (BAL) | +2.079B | +2.072B | -0.006B | -0.31% |
| E1VFVN30 (VN30) | +22.503B | +24.260B | +1.757B | +7.81% |
| E1VFVN30 (VN30) | +0.134B | +0.133B | -0.001B | -1.06% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -12.851B |
| + ETF net cash flow + MTM | +3.868B |
| + Stock unrealized MTM | +11.732B (cost 12.030B → realized would be -0.298B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +14.4165B |
| + Stock sells (sell_amount - fee in) | +1.5656B |
| - ETF buys (buy_amount + fee out) | +61.9012B |
| + ETF sells (sell_amount - fee in) | +24.7493B |
| = Expected end cash (from transactions only) | -0.0028B |
| Actual end cash (from logs) | -0.0033B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0005B** |
| Actual end ETF balance (still in cash_etf) | +41.0202B |
| Open stock positions mark value | +11.7325B |
| = **Final NAV (cash + ETF + open stocks)** | **+53.4918B** |

**Note on `Diff` line**: when ETF appreciates daily by VN30 return, cash_etf grows.
The rebalance logic (target 70% of total cash+ETF in state=NEUTRAL) periodically moves
a portion OUT of cash_etf and INTO cash. Those are logged as ETF 'sell' transactions,
but the moved amount EXCEEDS the original cost basis (because ETF appreciated meanwhile).
The diff line = appreciation that flowed to cash via rebalances. To FULLY reconcile,
compute ETF return = (etf_sells + etf_etf_residual_mark) − etf_buys − etf_fees.

### Per-book daily breakdown (in logs CSV)

The `data/pt_v11_tq34b_logs.csv` now has 6 per-book columns:
`BAL_cash`, `BAL_stocks`, `BAL_etf`, `VN30_cash`, `VN30_stocks`, `VN30_etf`.
Each row: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf = NAV`.
Cross-check at any date: when ETF is bought in BAL, BAL_cash decreases and BAL_etf increases (minus friction).

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
| Stock buys — share cost | +14.3949B |
| Stock buys — fee | +0.0216B |
| Stock sells — gross | +2.2043B |
| Stock sells — fee+tax | +0.0055B |
| **Net stock realized P&L** | **-12.2177B** |
| ETF buys — share cost | +62.4385B |
| ETF buys — friction | +0.0937B |
| ETF sells — gross | +24.7865B |
| ETF sells — friction | +0.0372B |
| **Net ETF cash flow** | **-37.7829B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| PAN (BAL) | +2.506B | +2.315B | -0.191B | -7.48% |
| VHM (BAL) | +2.701B | +2.808B | +0.107B | +4.11% |
| VIC (BAL) | +2.970B | +2.868B | -0.101B | -3.27% |
| TVN (BAL) | +1.310B | +1.263B | -0.047B | -3.45% |
| VHM (VN30) | +2.544B | +2.645B | +0.101B | +4.11% |
| E1VFVN30 (BAL) | +4.738B | +5.108B | +0.370B | +7.81% |
| E1VFVN30 (BAL) | +0.132B | +0.132B | +0.001B | +0.45% |
| E1VFVN30 (BAL) | +2.109B | +2.086B | -0.022B | -1.06% |
| E1VFVN30 (BAL) | +0.514B | +0.498B | -0.017B | -3.24% |
| E1VFVN30 (BAL) | +2.157B | +2.106B | -0.051B | -2.37% |
| E1VFVN30 (BAL) | +0.537B | +0.527B | -0.010B | -1.88% |
| E1VFVN30 (BAL) | +2.484B | +2.456B | -0.028B | -1.11% |
| E1VFVN30 (BAL) | +1.157B | +1.139B | -0.018B | -1.53% |
| E1VFVN30 (BAL) | +0.507B | +0.503B | -0.004B | -0.73% |
| E1VFVN30 (BAL) | +2.079B | +2.072B | -0.006B | -0.31% |
| E1VFVN30 (BAL) | +0.630B | +0.630B | +0.000B | +0.00% |
| E1VFVN30 (VN30) | +22.503B | +24.260B | +1.757B | +7.81% |
| E1VFVN30 (VN30) | +0.134B | +0.133B | -0.001B | -1.06% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -12.218B |
| + ETF net cash flow + MTM | +3.867B |
| + Stock unrealized MTM | +11.898B (cost 12.030B → realized would be -0.132B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +14.4165B |
| + Stock sells (sell_amount - fee in) | +2.1988B |
| - ETF buys (buy_amount + fee out) | +62.5322B |
| + ETF sells (sell_amount - fee in) | +24.7493B |
| = Expected end cash (from transactions only) | -0.0006B |
| Actual end cash (from logs) | -0.0011B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0005B** |
| Actual end ETF balance (still in cash_etf) | +41.6502B |
| Open stock positions mark value | +11.8984B |
| = **Final NAV (cash + ETF + open stocks)** | **+53.5474B** |

**Note on `Diff` line**: when ETF appreciates daily by VN30 return, cash_etf grows.
The rebalance logic (target 70% of total cash+ETF in state=NEUTRAL) periodically moves
a portion OUT of cash_etf and INTO cash. Those are logged as ETF 'sell' transactions,
but the moved amount EXCEEDS the original cost basis (because ETF appreciated meanwhile).
The diff line = appreciation that flowed to cash via rebalances. To FULLY reconcile,
compute ETF return = (etf_sells + etf_etf_residual_mark) − etf_buys − etf_fees.

### Per-book daily breakdown (in logs CSV)

The `data/pt_v11_tq34b_logs.csv` now has 6 per-book columns:
`BAL_cash`, `BAL_stocks`, `BAL_etf`, `VN30_cash`, `VN30_stocks`, `VN30_etf`.
Each row: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf = NAV`.
Cross-check at any date: when ETF is bought in BAL, BAL_cash decreases and BAL_etf increases (minus friction).

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
| Stock buys — share cost | +14.3949B |
| Stock buys — fee | +0.0216B |
| Stock sells — gross | +2.2043B |
| Stock sells — fee+tax | +0.0055B |
| **Net stock realized P&L** | **-12.2177B** |
| ETF buys — share cost | +62.4385B |
| ETF buys — friction | +0.0937B |
| ETF sells — gross | +24.7865B |
| ETF sells — friction | +0.0372B |
| **Net ETF cash flow** | **-37.7829B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| PAN (BAL) | +2.506B | +2.315B | -0.191B | -7.48% |
| VHM (BAL) | +2.701B | +2.808B | +0.107B | +4.11% |
| VIC (BAL) | +2.970B | +2.868B | -0.101B | -3.27% |
| TVN (BAL) | +1.310B | +1.263B | -0.047B | -3.45% |
| VHM (VN30) | +2.544B | +2.645B | +0.101B | +4.11% |
| E1VFVN30 (BAL) | +4.738B | +5.108B | +0.370B | +7.81% |
| E1VFVN30 (BAL) | +0.132B | +0.132B | +0.001B | +0.45% |
| E1VFVN30 (BAL) | +2.109B | +2.086B | -0.022B | -1.06% |
| E1VFVN30 (BAL) | +0.514B | +0.498B | -0.017B | -3.24% |
| E1VFVN30 (BAL) | +2.157B | +2.106B | -0.051B | -2.37% |
| E1VFVN30 (BAL) | +0.537B | +0.527B | -0.010B | -1.88% |
| E1VFVN30 (BAL) | +2.484B | +2.456B | -0.028B | -1.11% |
| E1VFVN30 (BAL) | +1.157B | +1.139B | -0.018B | -1.53% |
| E1VFVN30 (BAL) | +0.507B | +0.503B | -0.004B | -0.73% |
| E1VFVN30 (BAL) | +2.079B | +2.072B | -0.006B | -0.31% |
| E1VFVN30 (BAL) | +0.630B | +0.630B | +0.000B | +0.00% |
| E1VFVN30 (VN30) | +22.503B | +24.260B | +1.757B | +7.81% |
| E1VFVN30 (VN30) | +0.134B | +0.133B | -0.001B | -1.06% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -12.218B |
| + ETF net cash flow + MTM | +3.867B |
| + Stock unrealized MTM | +11.898B (cost 12.030B → realized would be -0.132B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +14.4165B |
| + Stock sells (sell_amount - fee in) | +2.1988B |
| - ETF buys (buy_amount + fee out) | +62.5322B |
| + ETF sells (sell_amount - fee in) | +24.7493B |
| = Expected end cash (from transactions only) | -0.0006B |
| Actual end cash (from logs) | -0.0011B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0005B** |
| Actual end ETF balance (still in cash_etf) | +41.6502B |
| Open stock positions mark value | +11.8984B |
| = **Final NAV (cash + ETF + open stocks)** | **+53.5474B** |

**Note on `Diff` line**: when ETF appreciates daily by VN30 return, cash_etf grows.
The rebalance logic (target 70% of total cash+ETF in state=NEUTRAL) periodically moves
a portion OUT of cash_etf and INTO cash. Those are logged as ETF 'sell' transactions,
but the moved amount EXCEEDS the original cost basis (because ETF appreciated meanwhile).
The diff line = appreciation that flowed to cash via rebalances. To FULLY reconcile,
compute ETF return = (etf_sells + etf_etf_residual_mark) − etf_buys − etf_fees.

### Per-book daily breakdown (in logs CSV)

The `data/pt_v11_tq34b_logs.csv` now has 6 per-book columns:
`BAL_cash`, `BAL_stocks`, `BAL_etf`, `VN30_cash`, `VN30_stocks`, `VN30_etf`.
Each row: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf = NAV`.
Cross-check at any date: when ETF is bought in BAL, BAL_cash decreases and BAL_etf increases (minus friction).

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
| Stock buys — share cost | +14.7929B |
| Stock buys — fee | +0.0222B |
| Stock sells — gross | +2.2043B |
| Stock sells — fee+tax | +0.0055B |
| **Net stock realized P&L** | **-12.6164B** |
| ETF buys — share cost | +64.6256B |
| ETF buys — friction | +0.0969B |
| ETF sells — gross | +27.3770B |
| ETF sells — friction | +0.0411B |
| **Net ETF cash flow** | **-37.3866B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| PAN (BAL) | +2.506B | +2.264B | -0.241B | -9.49% |
| VHM (BAL) | +2.701B | +2.710B | +0.009B | +0.48% |
| VIC (BAL) | +2.970B | +2.702B | -0.268B | -8.88% |
| TVN (BAL) | +1.310B | +1.240B | -0.070B | -5.17% |
| VHM (VN30) | +2.544B | +2.553B | +0.008B | +0.48% |
| E1VFVN30 (BAL) | +2.297B | +2.438B | +0.141B | +6.14% |
| E1VFVN30 (BAL) | +0.132B | +0.130B | -0.001B | -1.10% |
| E1VFVN30 (BAL) | +2.109B | +2.054B | -0.055B | -2.59% |
| E1VFVN30 (BAL) | +0.514B | +0.490B | -0.024B | -4.74% |
| E1VFVN30 (BAL) | +2.157B | +2.073B | -0.084B | -3.88% |
| E1VFVN30 (BAL) | +0.537B | +0.518B | -0.018B | -3.40% |
| E1VFVN30 (BAL) | +2.484B | +2.418B | -0.066B | -2.65% |
| E1VFVN30 (BAL) | +1.157B | +1.121B | -0.035B | -3.05% |
| E1VFVN30 (BAL) | +0.507B | +0.495B | -0.011B | -2.27% |
| E1VFVN30 (BAL) | +2.079B | +2.040B | -0.039B | -1.85% |
| E1VFVN30 (BAL) | +0.630B | +0.620B | -0.010B | -1.55% |
| E1VFVN30 (BAL) | +2.187B | +2.187B | +0.000B | +0.00% |
| E1VFVN30 (VN30) | +22.503B | +23.884B | +1.381B | +6.14% |
| E1VFVN30 (VN30) | +0.134B | +0.130B | -0.003B | -2.59% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -12.616B |
| + ETF net cash flow + MTM | +3.215B |
| + Stock unrealized MTM | +11.469B (cost 12.030B → realized would be -0.561B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +14.8151B |
| + Stock sells (sell_amount - fee in) | +2.1988B |
| - ETF buys (buy_amount + fee out) | +64.7225B |
| + ETF sells (sell_amount - fee in) | +27.3359B |
| = Expected end cash (from transactions only) | -0.0030B |
| Actual end cash (from logs) | -0.0035B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0005B** |
| Actual end ETF balance (still in cash_etf) | +40.6012B |
| Open stock positions mark value | +11.4692B |
| = **Final NAV (cash + ETF + open stocks)** | **+52.4649B** |

**Note on `Diff` line**: when ETF appreciates daily by VN30 return, cash_etf grows.
The rebalance logic (target 70% of total cash+ETF in state=NEUTRAL) periodically moves
a portion OUT of cash_etf and INTO cash. Those are logged as ETF 'sell' transactions,
but the moved amount EXCEEDS the original cost basis (because ETF appreciated meanwhile).
The diff line = appreciation that flowed to cash via rebalances. To FULLY reconcile,
compute ETF return = (etf_sells + etf_etf_residual_mark) − etf_buys − etf_fees.

### Per-book daily breakdown (in logs CSV)

The `data/pt_v11_tq34b_logs.csv` now has 6 per-book columns:
`BAL_cash`, `BAL_stocks`, `BAL_etf`, `VN30_cash`, `VN30_stocks`, `VN30_etf`.
Each row: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf = NAV`.
Cross-check at any date: when ETF is bought in BAL, BAL_cash decreases and BAL_etf increases (minus friction).

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
| Stock buys — share cost | +14.7929B |
| Stock buys — fee | +0.0222B |
| Stock sells — gross | +2.2043B |
| Stock sells — fee+tax | +0.0055B |
| **Net stock realized P&L** | **-12.6164B** |
| ETF buys — share cost | +64.6256B |
| ETF buys — friction | +0.0969B |
| ETF sells — gross | +27.3770B |
| ETF sells — friction | +0.0411B |
| **Net ETF cash flow** | **-37.3866B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| PAN (BAL) | +2.506B | +2.300B | -0.206B | -8.09% |
| VHM (BAL) | +2.701B | +2.712B | +0.011B | +0.55% |
| VIC (BAL) | +2.970B | +2.716B | -0.254B | -8.41% |
| TVN (BAL) | +1.310B | +1.263B | -0.047B | -3.45% |
| VHM (VN30) | +2.544B | +2.555B | +0.010B | +0.55% |
| E1VFVN30 (BAL) | +2.297B | +2.442B | +0.145B | +6.32% |
| E1VFVN30 (BAL) | +0.132B | +0.131B | -0.001B | -0.93% |
| E1VFVN30 (BAL) | +2.109B | +2.057B | -0.051B | -2.43% |
| E1VFVN30 (BAL) | +0.514B | +0.491B | -0.024B | -4.58% |
| E1VFVN30 (BAL) | +2.157B | +2.077B | -0.080B | -3.71% |
| E1VFVN30 (BAL) | +0.537B | +0.519B | -0.017B | -3.23% |
| E1VFVN30 (BAL) | +2.484B | +2.423B | -0.062B | -2.48% |
| E1VFVN30 (BAL) | +1.157B | +1.123B | -0.033B | -2.89% |
| E1VFVN30 (BAL) | +0.507B | +0.496B | -0.011B | -2.10% |
| E1VFVN30 (BAL) | +2.079B | +2.044B | -0.035B | -1.69% |
| E1VFVN30 (BAL) | +0.630B | +0.621B | -0.009B | -1.38% |
| E1VFVN30 (BAL) | +2.187B | +2.191B | +0.004B | +0.17% |
| E1VFVN30 (VN30) | +22.503B | +23.925B | +1.422B | +6.32% |
| E1VFVN30 (VN30) | +0.134B | +0.131B | -0.003B | -2.43% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -12.616B |
| + ETF net cash flow + MTM | +3.284B |
| + Stock unrealized MTM | +11.544B (cost 12.030B → realized would be -0.486B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +14.8151B |
| + Stock sells (sell_amount - fee in) | +2.1988B |
| - ETF buys (buy_amount + fee out) | +64.7225B |
| + ETF sells (sell_amount - fee in) | +27.3359B |
| = Expected end cash (from transactions only) | -0.0030B |
| Actual end cash (from logs) | -0.0035B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0005B** |
| Actual end ETF balance (still in cash_etf) | +40.6710B |
| Open stock positions mark value | +11.5444B |
| = **Final NAV (cash + ETF + open stocks)** | **+52.6055B** |

**Note on `Diff` line**: when ETF appreciates daily by VN30 return, cash_etf grows.
The rebalance logic (target 70% of total cash+ETF in state=NEUTRAL) periodically moves
a portion OUT of cash_etf and INTO cash. Those are logged as ETF 'sell' transactions,
but the moved amount EXCEEDS the original cost basis (because ETF appreciated meanwhile).
The diff line = appreciation that flowed to cash via rebalances. To FULLY reconcile,
compute ETF return = (etf_sells + etf_etf_residual_mark) − etf_buys − etf_fees.

### Per-book daily breakdown (in logs CSV)

The `data/pt_v11_tq34b_logs.csv` now has 6 per-book columns:
`BAL_cash`, `BAL_stocks`, `BAL_etf`, `VN30_cash`, `VN30_stocks`, `VN30_etf`.
Each row: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf = NAV`.
Cross-check at any date: when ETF is bought in BAL, BAL_cash decreases and BAL_etf increases (minus friction).

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
| Stock buys — share cost | +14.7929B |
| Stock buys — fee | +0.0222B |
| Stock sells — gross | +2.2043B |
| Stock sells — fee+tax | +0.0055B |
| **Net stock realized P&L** | **-12.6164B** |
| ETF buys — share cost | +64.6256B |
| ETF buys — friction | +0.0969B |
| ETF sells — gross | +27.3770B |
| ETF sells — friction | +0.0411B |
| **Net ETF cash flow** | **-37.3866B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| PAN (BAL) | +2.506B | +2.295B | -0.211B | -8.29% |
| VHM (BAL) | +2.701B | +2.669B | -0.032B | -1.03% |
| VIC (BAL) | +2.970B | +2.716B | -0.254B | -8.41% |
| TVN (BAL) | +1.310B | +1.308B | -0.002B | +0.00% |
| VHM (VN30) | +2.544B | +2.515B | -0.030B | -1.03% |
| E1VFVN30 (BAL) | +2.297B | +2.439B | +0.142B | +6.17% |
| E1VFVN30 (BAL) | +0.132B | +0.130B | -0.001B | -1.08% |
| E1VFVN30 (BAL) | +2.109B | +2.054B | -0.054B | -2.56% |
| E1VFVN30 (BAL) | +0.514B | +0.490B | -0.024B | -4.72% |
| E1VFVN30 (BAL) | +2.157B | +2.074B | -0.083B | -3.85% |
| E1VFVN30 (BAL) | +0.537B | +0.519B | -0.018B | -3.37% |
| E1VFVN30 (BAL) | +2.484B | +2.419B | -0.065B | -2.62% |
| E1VFVN30 (BAL) | +1.157B | +1.122B | -0.035B | -3.02% |
| E1VFVN30 (BAL) | +0.507B | +0.495B | -0.011B | -2.24% |
| E1VFVN30 (BAL) | +2.079B | +2.041B | -0.038B | -1.83% |
| E1VFVN30 (BAL) | +0.630B | +0.620B | -0.010B | -1.52% |
| E1VFVN30 (BAL) | +2.187B | +2.188B | +0.001B | +0.03% |
| E1VFVN30 (VN30) | +22.503B | +23.891B | +1.388B | +6.17% |
| E1VFVN30 (VN30) | +0.134B | +0.130B | -0.003B | -2.56% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -12.616B |
| + ETF net cash flow + MTM | +3.226B |
| + Stock unrealized MTM | +11.502B (cost 12.030B → realized would be -0.529B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +14.8151B |
| + Stock sells (sell_amount - fee in) | +2.1988B |
| - ETF buys (buy_amount + fee out) | +64.7225B |
| + ETF sells (sell_amount - fee in) | +27.3359B |
| = Expected end cash (from transactions only) | -0.0030B |
| Actual end cash (from logs) | -0.0035B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0005B** |
| Actual end ETF balance (still in cash_etf) | +40.6129B |
| Open stock positions mark value | +11.5019B |
| = **Final NAV (cash + ETF + open stocks)** | **+52.5093B** |

**Note on `Diff` line**: when ETF appreciates daily by VN30 return, cash_etf grows.
The rebalance logic (target 70% of total cash+ETF in state=NEUTRAL) periodically moves
a portion OUT of cash_etf and INTO cash. Those are logged as ETF 'sell' transactions,
but the moved amount EXCEEDS the original cost basis (because ETF appreciated meanwhile).
The diff line = appreciation that flowed to cash via rebalances. To FULLY reconcile,
compute ETF return = (etf_sells + etf_etf_residual_mark) − etf_buys − etf_fees.

### Per-book daily breakdown (in logs CSV)

The `data/pt_v11_tq34b_logs.csv` now has 6 per-book columns:
`BAL_cash`, `BAL_stocks`, `BAL_etf`, `VN30_cash`, `VN30_stocks`, `VN30_etf`.
Each row: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf = NAV`.
Cross-check at any date: when ETF is bought in BAL, BAL_cash decreases and BAL_etf increases (minus friction).

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
| Stock buys — share cost | +14.7929B |
| Stock buys — fee | +0.0222B |
| Stock sells — gross | +2.5979B |
| Stock sells — fee+tax | +0.0065B |
| **Net stock realized P&L** | **-12.2237B** |
| ETF buys — share cost | +65.0149B |
| ETF buys — friction | +0.0975B |
| ETF sells — gross | +27.3770B |
| ETF sells — friction | +0.0411B |
| **Net ETF cash flow** | **-37.7765B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| PAN (BAL) | +2.506B | +2.285B | -0.221B | -8.69% |
| VHM (BAL) | +2.701B | +2.562B | -0.139B | -5.00% |
| VIC (BAL) | +2.970B | +2.709B | -0.261B | -8.64% |
| TVN (BAL) | +1.310B | +1.229B | -0.081B | -6.03% |
| VHM (VN30) | +2.544B | +2.414B | -0.131B | -5.00% |
| E1VFVN30 (BAL) | +2.297B | +2.438B | +0.141B | +6.14% |
| E1VFVN30 (BAL) | +0.132B | +0.130B | -0.001B | -1.10% |
| E1VFVN30 (BAL) | +2.109B | +2.054B | -0.055B | -2.59% |
| E1VFVN30 (BAL) | +0.514B | +0.490B | -0.024B | -4.74% |
| E1VFVN30 (BAL) | +2.157B | +2.073B | -0.084B | -3.88% |
| E1VFVN30 (BAL) | +0.537B | +0.518B | -0.018B | -3.40% |
| E1VFVN30 (BAL) | +2.484B | +2.418B | -0.066B | -2.65% |
| E1VFVN30 (BAL) | +1.157B | +1.121B | -0.035B | -3.05% |
| E1VFVN30 (BAL) | +0.507B | +0.495B | -0.011B | -2.27% |
| E1VFVN30 (BAL) | +2.079B | +2.040B | -0.039B | -1.85% |
| E1VFVN30 (BAL) | +0.630B | +0.620B | -0.010B | -1.55% |
| E1VFVN30 (BAL) | +2.187B | +2.187B | +0.000B | +0.00% |
| E1VFVN30 (BAL) | +0.389B | +0.389B | +0.000B | +0.00% |
| E1VFVN30 (VN30) | +22.503B | +23.884B | +1.381B | +6.14% |
| E1VFVN30 (VN30) | +0.134B | +0.130B | -0.003B | -2.59% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -12.224B |
| + ETF net cash flow + MTM | +3.214B |
| + Stock unrealized MTM | +11.198B (cost 12.030B → realized would be -0.833B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +14.8151B |
| + Stock sells (sell_amount - fee in) | +2.5914B |
| - ETF buys (buy_amount + fee out) | +65.1125B |
| + ETF sells (sell_amount - fee in) | +27.3359B |
| = Expected end cash (from transactions only) | -0.0003B |
| Actual end cash (from logs) | -0.0008B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0005B** |
| Actual end ETF balance (still in cash_etf) | +40.9906B |
| Open stock positions mark value | +11.1979B |
| = **Final NAV (cash + ETF + open stocks)** | **+52.1877B** |

**Note on `Diff` line**: when ETF appreciates daily by VN30 return, cash_etf grows.
The rebalance logic (target 70% of total cash+ETF in state=NEUTRAL) periodically moves
a portion OUT of cash_etf and INTO cash. Those are logged as ETF 'sell' transactions,
but the moved amount EXCEEDS the original cost basis (because ETF appreciated meanwhile).
The diff line = appreciation that flowed to cash via rebalances. To FULLY reconcile,
compute ETF return = (etf_sells + etf_etf_residual_mark) − etf_buys − etf_fees.

### Per-book daily breakdown (in logs CSV)

The `data/pt_v11_tq34b_logs.csv` now has 6 per-book columns:
`BAL_cash`, `BAL_stocks`, `BAL_etf`, `VN30_cash`, `VN30_stocks`, `VN30_etf`.
Each row: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf = NAV`.
Cross-check at any date: when ETF is bought in BAL, BAL_cash decreases and BAL_etf increases (minus friction).

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
| Stock buys — share cost | +14.7929B |
| Stock buys — fee | +0.0222B |
| Stock sells — gross | +2.5979B |
| Stock sells — fee+tax | +0.0065B |
| **Net stock realized P&L** | **-12.2237B** |
| ETF buys — share cost | +65.0149B |
| ETF buys — friction | +0.0975B |
| ETF sells — gross | +27.3770B |
| ETF sells — friction | +0.0411B |
| **Net ETF cash flow** | **-37.7765B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| PAN (BAL) | +2.506B | +2.285B | -0.221B | -8.69% |
| VHM (BAL) | +2.701B | +2.562B | -0.139B | -5.00% |
| VIC (BAL) | +2.970B | +2.709B | -0.261B | -8.64% |
| TVN (BAL) | +1.310B | +1.229B | -0.081B | -6.03% |
| VHM (VN30) | +2.544B | +2.414B | -0.131B | -5.00% |
| E1VFVN30 (BAL) | +2.297B | +2.438B | +0.141B | +6.14% |
| E1VFVN30 (BAL) | +0.132B | +0.130B | -0.001B | -1.10% |
| E1VFVN30 (BAL) | +2.109B | +2.054B | -0.055B | -2.59% |
| E1VFVN30 (BAL) | +0.514B | +0.490B | -0.024B | -4.74% |
| E1VFVN30 (BAL) | +2.157B | +2.073B | -0.084B | -3.88% |
| E1VFVN30 (BAL) | +0.537B | +0.518B | -0.018B | -3.40% |
| E1VFVN30 (BAL) | +2.484B | +2.418B | -0.066B | -2.65% |
| E1VFVN30 (BAL) | +1.157B | +1.121B | -0.035B | -3.05% |
| E1VFVN30 (BAL) | +0.507B | +0.495B | -0.011B | -2.27% |
| E1VFVN30 (BAL) | +2.079B | +2.040B | -0.039B | -1.85% |
| E1VFVN30 (BAL) | +0.630B | +0.620B | -0.010B | -1.55% |
| E1VFVN30 (BAL) | +2.187B | +2.187B | +0.000B | +0.00% |
| E1VFVN30 (BAL) | +0.389B | +0.389B | +0.000B | +0.00% |
| E1VFVN30 (VN30) | +22.503B | +23.884B | +1.381B | +6.14% |
| E1VFVN30 (VN30) | +0.134B | +0.130B | -0.003B | -2.59% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -12.224B |
| + ETF net cash flow + MTM | +3.214B |
| + Stock unrealized MTM | +11.198B (cost 12.030B → realized would be -0.833B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +14.8151B |
| + Stock sells (sell_amount - fee in) | +2.5914B |
| - ETF buys (buy_amount + fee out) | +65.1125B |
| + ETF sells (sell_amount - fee in) | +27.3359B |
| = Expected end cash (from transactions only) | -0.0003B |
| Actual end cash (from logs) | -0.0008B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0005B** |
| Actual end ETF balance (still in cash_etf) | +40.9906B |
| Open stock positions mark value | +11.1979B |
| = **Final NAV (cash + ETF + open stocks)** | **+52.1877B** |

**Note on `Diff` line**: when ETF appreciates daily by VN30 return, cash_etf grows.
The rebalance logic (target 70% of total cash+ETF in state=NEUTRAL) periodically moves
a portion OUT of cash_etf and INTO cash. Those are logged as ETF 'sell' transactions,
but the moved amount EXCEEDS the original cost basis (because ETF appreciated meanwhile).
The diff line = appreciation that flowed to cash via rebalances. To FULLY reconcile,
compute ETF return = (etf_sells + etf_etf_residual_mark) − etf_buys − etf_fees.

### Per-book daily breakdown (in logs CSV)

The `data/pt_v11_tq34b_logs.csv` now has 6 per-book columns:
`BAL_cash`, `BAL_stocks`, `BAL_etf`, `VN30_cash`, `VN30_stocks`, `VN30_etf`.
Each row: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf = NAV`.
Cross-check at any date: when ETF is bought in BAL, BAL_cash decreases and BAL_etf increases (minus friction).

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
| Stock buys — share cost | +14.7929B |
| Stock buys — fee | +0.0222B |
| Stock sells — gross | +2.5979B |
| Stock sells — fee+tax | +0.0065B |
| **Net stock realized P&L** | **-12.2237B** |
| ETF buys — share cost | +65.0149B |
| ETF buys — friction | +0.0975B |
| ETF sells — gross | +27.3770B |
| ETF sells — friction | +0.0411B |
| **Net ETF cash flow** | **-37.7765B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| PAN (BAL) | +2.506B | +2.285B | -0.221B | -8.69% |
| VHM (BAL) | +2.701B | +2.562B | -0.139B | -5.00% |
| VIC (BAL) | +2.970B | +2.709B | -0.261B | -8.64% |
| TVN (BAL) | +1.310B | +1.229B | -0.081B | -6.03% |
| VHM (VN30) | +2.544B | +2.414B | -0.131B | -5.00% |
| E1VFVN30 (BAL) | +2.297B | +2.438B | +0.141B | +6.14% |
| E1VFVN30 (BAL) | +0.132B | +0.130B | -0.001B | -1.10% |
| E1VFVN30 (BAL) | +2.109B | +2.054B | -0.055B | -2.59% |
| E1VFVN30 (BAL) | +0.514B | +0.490B | -0.024B | -4.74% |
| E1VFVN30 (BAL) | +2.157B | +2.073B | -0.084B | -3.88% |
| E1VFVN30 (BAL) | +0.537B | +0.518B | -0.018B | -3.40% |
| E1VFVN30 (BAL) | +2.484B | +2.418B | -0.066B | -2.65% |
| E1VFVN30 (BAL) | +1.157B | +1.121B | -0.035B | -3.05% |
| E1VFVN30 (BAL) | +0.507B | +0.495B | -0.011B | -2.27% |
| E1VFVN30 (BAL) | +2.079B | +2.040B | -0.039B | -1.85% |
| E1VFVN30 (BAL) | +0.630B | +0.620B | -0.010B | -1.55% |
| E1VFVN30 (BAL) | +2.187B | +2.187B | +0.000B | +0.00% |
| E1VFVN30 (BAL) | +0.389B | +0.389B | +0.000B | +0.00% |
| E1VFVN30 (VN30) | +22.503B | +23.884B | +1.381B | +6.14% |
| E1VFVN30 (VN30) | +0.134B | +0.130B | -0.003B | -2.59% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -12.224B |
| + ETF net cash flow + MTM | +3.214B |
| + Stock unrealized MTM | +11.198B (cost 12.030B → realized would be -0.833B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +14.8151B |
| + Stock sells (sell_amount - fee in) | +2.5914B |
| - ETF buys (buy_amount + fee out) | +65.1125B |
| + ETF sells (sell_amount - fee in) | +27.3359B |
| = Expected end cash (from transactions only) | -0.0003B |
| Actual end cash (from logs) | -0.0008B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0005B** |
| Actual end ETF balance (still in cash_etf) | +40.9906B |
| Open stock positions mark value | +11.1979B |
| = **Final NAV (cash + ETF + open stocks)** | **+52.1877B** |

**Note on `Diff` line**: when ETF appreciates daily by VN30 return, cash_etf grows.
The rebalance logic (target 70% of total cash+ETF in state=NEUTRAL) periodically moves
a portion OUT of cash_etf and INTO cash. Those are logged as ETF 'sell' transactions,
but the moved amount EXCEEDS the original cost basis (because ETF appreciated meanwhile).
The diff line = appreciation that flowed to cash via rebalances. To FULLY reconcile,
compute ETF return = (etf_sells + etf_etf_residual_mark) − etf_buys − etf_fees.

### Per-book daily breakdown (in logs CSV)

The `data/pt_v11_tq34b_logs.csv` now has 6 per-book columns:
`BAL_cash`, `BAL_stocks`, `BAL_etf`, `VN30_cash`, `VN30_stocks`, `VN30_etf`.
Each row: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf = NAV`.
Cross-check at any date: when ETF is bought in BAL, BAL_cash decreases and BAL_etf increases (minus friction).

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
| Stock buys — share cost | +14.7929B |
| Stock buys — fee | +0.0222B |
| Stock sells — gross | +2.5979B |
| Stock sells — fee+tax | +0.0065B |
| **Net stock realized P&L** | **-12.2237B** |
| ETF buys — share cost | +65.0149B |
| ETF buys — friction | +0.0975B |
| ETF sells — gross | +27.3770B |
| ETF sells — friction | +0.0411B |
| **Net ETF cash flow** | **-37.7765B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| PAN (BAL) | +2.506B | +2.320B | -0.186B | -7.28% |
| VHM (BAL) | +2.701B | +2.514B | -0.187B | -6.78% |
| VIC (BAL) | +2.970B | +2.669B | -0.301B | -10.00% |
| TVN (BAL) | +1.310B | +1.217B | -0.092B | -6.90% |
| VHM (VN30) | +2.544B | +2.368B | -0.176B | -6.78% |
| E1VFVN30 (BAL) | +2.297B | +2.449B | +0.152B | +6.62% |
| E1VFVN30 (BAL) | +0.132B | +0.131B | -0.001B | -0.65% |
| E1VFVN30 (BAL) | +2.109B | +2.063B | -0.045B | -2.15% |
| E1VFVN30 (BAL) | +0.514B | +0.492B | -0.022B | -4.31% |
| E1VFVN30 (BAL) | +2.157B | +2.083B | -0.074B | -3.44% |
| E1VFVN30 (BAL) | +0.537B | +0.521B | -0.016B | -2.96% |
| E1VFVN30 (BAL) | +2.484B | +2.429B | -0.055B | -2.20% |
| E1VFVN30 (BAL) | +1.157B | +1.126B | -0.030B | -2.61% |
| E1VFVN30 (BAL) | +0.507B | +0.497B | -0.009B | -1.82% |
| E1VFVN30 (BAL) | +2.079B | +2.050B | -0.029B | -1.40% |
| E1VFVN30 (BAL) | +0.630B | +0.623B | -0.007B | -1.10% |
| E1VFVN30 (BAL) | +2.187B | +2.197B | +0.010B | +0.46% |
| E1VFVN30 (BAL) | +0.389B | +0.391B | +0.002B | +0.46% |
| E1VFVN30 (VN30) | +22.503B | +23.994B | +1.490B | +6.62% |
| E1VFVN30 (VN30) | +0.134B | +0.131B | -0.003B | -2.15% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -12.224B |
| + ETF net cash flow + MTM | +3.402B |
| + Stock unrealized MTM | +11.088B (cost 12.030B → realized would be -0.942B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +14.8151B |
| + Stock sells (sell_amount - fee in) | +2.5914B |
| - ETF buys (buy_amount + fee out) | +65.1125B |
| + ETF sells (sell_amount - fee in) | +27.3359B |
| = Expected end cash (from transactions only) | -0.0003B |
| Actual end cash (from logs) | -0.0008B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0005B** |
| Actual end ETF balance (still in cash_etf) | +41.1783B |
| Open stock positions mark value | +11.0884B |
| = **Final NAV (cash + ETF + open stocks)** | **+52.2659B** |

**Note on `Diff` line**: when ETF appreciates daily by VN30 return, cash_etf grows.
The rebalance logic (target 70% of total cash+ETF in state=NEUTRAL) periodically moves
a portion OUT of cash_etf and INTO cash. Those are logged as ETF 'sell' transactions,
but the moved amount EXCEEDS the original cost basis (because ETF appreciated meanwhile).
The diff line = appreciation that flowed to cash via rebalances. To FULLY reconcile,
compute ETF return = (etf_sells + etf_etf_residual_mark) − etf_buys − etf_fees.

### Per-book daily breakdown (in logs CSV)

The `data/pt_v11_tq34b_logs.csv` now has 6 per-book columns:
`BAL_cash`, `BAL_stocks`, `BAL_etf`, `VN30_cash`, `VN30_stocks`, `VN30_etf`.
Each row: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf = NAV`.
Cross-check at any date: when ETF is bought in BAL, BAL_cash decreases and BAL_etf increases (minus friction).

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
| Stock buys — share cost | +14.7929B |
| Stock buys — fee | +0.0222B |
| Stock sells — gross | +2.5979B |
| Stock sells — fee+tax | +0.0065B |
| **Net stock realized P&L** | **-12.2237B** |
| ETF buys — share cost | +65.0149B |
| ETF buys — friction | +0.0975B |
| ETF sells — gross | +27.3770B |
| ETF sells — friction | +0.0411B |
| **Net ETF cash flow** | **-37.7765B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| PAN (BAL) | +2.506B | +2.320B | -0.186B | -7.28% |
| VHM (BAL) | +2.701B | +2.514B | -0.187B | -6.78% |
| VIC (BAL) | +2.970B | +2.669B | -0.301B | -10.00% |
| TVN (BAL) | +1.310B | +1.217B | -0.092B | -6.90% |
| VHM (VN30) | +2.544B | +2.368B | -0.176B | -6.78% |
| E1VFVN30 (BAL) | +2.297B | +2.449B | +0.152B | +6.62% |
| E1VFVN30 (BAL) | +0.132B | +0.131B | -0.001B | -0.65% |
| E1VFVN30 (BAL) | +2.109B | +2.063B | -0.045B | -2.15% |
| E1VFVN30 (BAL) | +0.514B | +0.492B | -0.022B | -4.31% |
| E1VFVN30 (BAL) | +2.157B | +2.083B | -0.074B | -3.44% |
| E1VFVN30 (BAL) | +0.537B | +0.521B | -0.016B | -2.96% |
| E1VFVN30 (BAL) | +2.484B | +2.429B | -0.055B | -2.20% |
| E1VFVN30 (BAL) | +1.157B | +1.126B | -0.030B | -2.61% |
| E1VFVN30 (BAL) | +0.507B | +0.497B | -0.009B | -1.82% |
| E1VFVN30 (BAL) | +2.079B | +2.050B | -0.029B | -1.40% |
| E1VFVN30 (BAL) | +0.630B | +0.623B | -0.007B | -1.10% |
| E1VFVN30 (BAL) | +2.187B | +2.197B | +0.010B | +0.46% |
| E1VFVN30 (BAL) | +0.389B | +0.391B | +0.002B | +0.46% |
| E1VFVN30 (VN30) | +22.503B | +23.994B | +1.490B | +6.62% |
| E1VFVN30 (VN30) | +0.134B | +0.131B | -0.003B | -2.15% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -12.224B |
| + ETF net cash flow + MTM | +3.402B |
| + Stock unrealized MTM | +11.088B (cost 12.030B → realized would be -0.942B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +14.8151B |
| + Stock sells (sell_amount - fee in) | +2.5914B |
| - ETF buys (buy_amount + fee out) | +65.1125B |
| + ETF sells (sell_amount - fee in) | +27.3359B |
| = Expected end cash (from transactions only) | -0.0003B |
| Actual end cash (from logs) | -0.0008B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0005B** |
| Actual end ETF balance (still in cash_etf) | +41.1783B |
| Open stock positions mark value | +11.0884B |
| = **Final NAV (cash + ETF + open stocks)** | **+52.2659B** |

**Note on `Diff` line**: when ETF appreciates daily by VN30 return, cash_etf grows.
The rebalance logic (target 70% of total cash+ETF in state=NEUTRAL) periodically moves
a portion OUT of cash_etf and INTO cash. Those are logged as ETF 'sell' transactions,
but the moved amount EXCEEDS the original cost basis (because ETF appreciated meanwhile).
The diff line = appreciation that flowed to cash via rebalances. To FULLY reconcile,
compute ETF return = (etf_sells + etf_etf_residual_mark) − etf_buys − etf_fees.

### Per-book daily breakdown (in logs CSV)

The `data/pt_v11_tq34b_logs.csv` now has 6 per-book columns:
`BAL_cash`, `BAL_stocks`, `BAL_etf`, `VN30_cash`, `VN30_stocks`, `VN30_etf`.
Each row: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf = NAV`.
Cross-check at any date: when ETF is bought in BAL, BAL_cash decreases and BAL_etf increases (minus friction).

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
| Stock buys — share cost | +14.7929B |
| Stock buys — fee | +0.0222B |
| Stock sells — gross | +2.5979B |
| Stock sells — fee+tax | +0.0065B |
| **Net stock realized P&L** | **-12.2237B** |
| ETF buys — share cost | +65.0149B |
| ETF buys — friction | +0.0975B |
| ETF sells — gross | +27.3770B |
| ETF sells — friction | +0.0411B |
| **Net ETF cash flow** | **-37.7765B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| PAN (BAL) | +2.506B | +2.335B | -0.171B | -6.68% |
| VHM (BAL) | +2.701B | +2.522B | -0.180B | -6.51% |
| VIC (BAL) | +2.970B | +2.688B | -0.282B | -9.35% |
| TVN (BAL) | +1.310B | +1.263B | -0.047B | -3.45% |
| VHM (VN30) | +2.544B | +2.375B | -0.169B | -6.51% |
| E1VFVN30 (BAL) | +2.297B | +2.453B | +0.156B | +6.77% |
| E1VFVN30 (BAL) | +0.132B | +0.131B | -0.001B | -0.51% |
| E1VFVN30 (BAL) | +2.109B | +2.066B | -0.042B | -2.01% |
| E1VFVN30 (BAL) | +0.514B | +0.493B | -0.021B | -4.17% |
| E1VFVN30 (BAL) | +2.157B | +2.086B | -0.071B | -3.30% |
| E1VFVN30 (BAL) | +0.537B | +0.522B | -0.015B | -2.82% |
| E1VFVN30 (BAL) | +2.484B | +2.433B | -0.051B | -2.06% |
| E1VFVN30 (BAL) | +1.157B | +1.128B | -0.029B | -2.47% |
| E1VFVN30 (BAL) | +0.507B | +0.498B | -0.009B | -1.68% |
| E1VFVN30 (BAL) | +2.079B | +2.052B | -0.026B | -1.26% |
| E1VFVN30 (BAL) | +0.630B | +0.624B | -0.006B | -0.96% |
| E1VFVN30 (BAL) | +2.187B | +2.200B | +0.013B | +0.60% |
| E1VFVN30 (BAL) | +0.389B | +0.392B | +0.002B | +0.60% |
| E1VFVN30 (VN30) | +22.503B | +24.028B | +1.524B | +6.77% |
| E1VFVN30 (VN30) | +0.134B | +0.131B | -0.003B | -2.01% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -12.224B |
| + ETF net cash flow + MTM | +3.460B |
| + Stock unrealized MTM | +11.182B (cost 12.030B → realized would be -0.848B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +14.8151B |
| + Stock sells (sell_amount - fee in) | +2.5914B |
| - ETF buys (buy_amount + fee out) | +65.1125B |
| + ETF sells (sell_amount - fee in) | +27.3359B |
| = Expected end cash (from transactions only) | -0.0003B |
| Actual end cash (from logs) | -0.0008B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0005B** |
| Actual end ETF balance (still in cash_etf) | +41.2369B |
| Open stock positions mark value | +11.1824B |
| = **Final NAV (cash + ETF + open stocks)** | **+52.4185B** |

**Note on `Diff` line**: when ETF appreciates daily by VN30 return, cash_etf grows.
The rebalance logic (target 70% of total cash+ETF in state=NEUTRAL) periodically moves
a portion OUT of cash_etf and INTO cash. Those are logged as ETF 'sell' transactions,
but the moved amount EXCEEDS the original cost basis (because ETF appreciated meanwhile).
The diff line = appreciation that flowed to cash via rebalances. To FULLY reconcile,
compute ETF return = (etf_sells + etf_etf_residual_mark) − etf_buys − etf_fees.

### Per-book daily breakdown (in logs CSV)

The `data/pt_v11_tq34b_logs.csv` now has 6 per-book columns:
`BAL_cash`, `BAL_stocks`, `BAL_etf`, `VN30_cash`, `VN30_stocks`, `VN30_etf`.
Each row: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf = NAV`.
Cross-check at any date: when ETF is bought in BAL, BAL_cash decreases and BAL_etf increases (minus friction).

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
| Stock buys — share cost | +14.7929B |
| Stock buys — fee | +0.0222B |
| Stock sells — gross | +2.5979B |
| Stock sells — fee+tax | +0.0065B |
| **Net stock realized P&L** | **-12.2237B** |
| ETF buys — share cost | +65.0149B |
| ETF buys — friction | +0.0975B |
| ETF sells — gross | +27.3770B |
| ETF sells — friction | +0.0411B |
| **Net ETF cash flow** | **-37.7765B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| PAN (BAL) | +2.506B | +2.335B | -0.171B | -6.68% |
| VHM (BAL) | +2.701B | +2.494B | -0.207B | -7.53% |
| VIC (BAL) | +2.970B | +2.660B | -0.309B | -10.28% |
| TVN (BAL) | +1.310B | +1.251B | -0.058B | -4.31% |
| VHM (VN30) | +2.544B | +2.349B | -0.195B | -7.53% |
| E1VFVN30 (BAL) | +2.297B | +2.441B | +0.144B | +6.26% |
| E1VFVN30 (BAL) | +0.132B | +0.131B | -0.001B | -0.99% |
| E1VFVN30 (BAL) | +2.109B | +2.056B | -0.052B | -2.48% |
| E1VFVN30 (BAL) | +0.514B | +0.490B | -0.024B | -4.63% |
| E1VFVN30 (BAL) | +2.157B | +2.076B | -0.081B | -3.77% |
| E1VFVN30 (BAL) | +0.537B | +0.519B | -0.018B | -3.29% |
| E1VFVN30 (BAL) | +2.484B | +2.421B | -0.063B | -2.54% |
| E1VFVN30 (BAL) | +1.157B | +1.123B | -0.034B | -2.94% |
| E1VFVN30 (BAL) | +0.507B | +0.496B | -0.011B | -2.15% |
| E1VFVN30 (BAL) | +2.079B | +2.043B | -0.036B | -1.74% |
| E1VFVN30 (BAL) | +0.630B | +0.621B | -0.009B | -1.44% |
| E1VFVN30 (BAL) | +2.187B | +2.190B | +0.003B | +0.11% |
| E1VFVN30 (BAL) | +0.389B | +0.390B | +0.000B | +0.11% |
| E1VFVN30 (VN30) | +22.503B | +23.912B | +1.408B | +6.26% |
| E1VFVN30 (VN30) | +0.134B | +0.131B | -0.003B | -2.48% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -12.224B |
| + ETF net cash flow + MTM | +3.261B |
| + Stock unrealized MTM | +11.090B (cost 12.030B → realized would be -0.941B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +14.8151B |
| + Stock sells (sell_amount - fee in) | +2.5914B |
| - ETF buys (buy_amount + fee out) | +65.1125B |
| + ETF sells (sell_amount - fee in) | +27.3359B |
| = Expected end cash (from transactions only) | -0.0003B |
| Actual end cash (from logs) | -0.0008B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0005B** |
| Actual end ETF balance (still in cash_etf) | +41.0375B |
| Open stock positions mark value | +11.0896B |
| = **Final NAV (cash + ETF + open stocks)** | **+52.1263B** |

**Note on `Diff` line**: when ETF appreciates daily by VN30 return, cash_etf grows.
The rebalance logic (target 70% of total cash+ETF in state=NEUTRAL) periodically moves
a portion OUT of cash_etf and INTO cash. Those are logged as ETF 'sell' transactions,
but the moved amount EXCEEDS the original cost basis (because ETF appreciated meanwhile).
The diff line = appreciation that flowed to cash via rebalances. To FULLY reconcile,
compute ETF return = (etf_sells + etf_etf_residual_mark) − etf_buys − etf_fees.

### Per-book daily breakdown (in logs CSV)

The `data/pt_v11_tq34b_logs.csv` now has 6 per-book columns:
`BAL_cash`, `BAL_stocks`, `BAL_etf`, `VN30_cash`, `VN30_stocks`, `VN30_etf`.
Each row: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf = NAV`.
Cross-check at any date: when ETF is bought in BAL, BAL_cash decreases and BAL_etf increases (minus friction).

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
| Stock buys — share cost | +15.1681B |
| Stock buys — fee | +0.0228B |
| Stock sells — gross | +2.5979B |
| Stock sells — fee+tax | +0.0065B |
| **Net stock realized P&L** | **-12.5995B** |
| ETF buys — share cost | +67.2608B |
| ETF buys — friction | +0.1009B |
| ETF sells — gross | +30.0030B |
| ETF sells — friction | +0.0450B |
| **Net ETF cash flow** | **-37.4036B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| PAN (BAL) | +2.506B | +2.320B | -0.186B | -7.28% |
| VHM (BAL) | +2.701B | +2.667B | -0.034B | -1.10% |
| VIC (BAL) | +2.970B | +2.846B | -0.124B | -4.02% |
| TVN (BAL) | +1.310B | +1.263B | -0.047B | -3.45% |
| VHM (VN30) | +2.544B | +2.513B | -0.032B | -1.10% |
| E1VFVN30 (BAL) | +2.079B | +2.048B | -0.031B | -1.51% |
| E1VFVN30 (BAL) | +0.514B | +0.495B | -0.019B | -3.68% |
| E1VFVN30 (BAL) | +2.157B | +2.097B | -0.061B | -2.81% |
| E1VFVN30 (BAL) | +0.537B | +0.524B | -0.012B | -2.32% |
| E1VFVN30 (BAL) | +2.484B | +2.445B | -0.039B | -1.56% |
| E1VFVN30 (BAL) | +1.157B | +1.134B | -0.023B | -1.97% |
| E1VFVN30 (BAL) | +0.507B | +0.501B | -0.006B | -1.17% |
| E1VFVN30 (BAL) | +2.079B | +2.063B | -0.016B | -0.76% |
| E1VFVN30 (BAL) | +0.630B | +0.627B | -0.003B | -0.45% |
| E1VFVN30 (BAL) | +2.187B | +2.211B | +0.024B | +1.12% |
| E1VFVN30 (BAL) | +0.389B | +0.394B | +0.004B | +1.12% |
| E1VFVN30 (BAL) | +2.246B | +2.246B | +0.000B | +0.00% |
| E1VFVN30 (VN30) | +22.503B | +24.151B | +1.647B | +7.32% |
| E1VFVN30 (VN30) | +0.134B | +0.132B | -0.002B | -1.51% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -12.599B |
| + ETF net cash flow + MTM | +3.664B |
| + Stock unrealized MTM | +11.609B (cost 12.030B → realized would be -0.422B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +15.1908B |
| + Stock sells (sell_amount - fee in) | +2.5914B |
| - ETF buys (buy_amount + fee out) | +67.3616B |
| + ETF sells (sell_amount - fee in) | +29.9580B |
| = Expected end cash (from transactions only) | -0.0031B |
| Actual end cash (from logs) | -0.0036B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0005B** |
| Actual end ETF balance (still in cash_etf) | +41.0679B |
| Open stock positions mark value | +11.6087B |
| = **Final NAV (cash + ETF + open stocks)** | **+53.0481B** |

**Note on `Diff` line**: when ETF appreciates daily by VN30 return, cash_etf grows.
The rebalance logic (target 70% of total cash+ETF in state=NEUTRAL) periodically moves
a portion OUT of cash_etf and INTO cash. Those are logged as ETF 'sell' transactions,
but the moved amount EXCEEDS the original cost basis (because ETF appreciated meanwhile).
The diff line = appreciation that flowed to cash via rebalances. To FULLY reconcile,
compute ETF return = (etf_sells + etf_etf_residual_mark) − etf_buys − etf_fees.

### Per-book daily breakdown (in logs CSV)

The `data/pt_v11_tq34b_logs.csv` now has 6 per-book columns:
`BAL_cash`, `BAL_stocks`, `BAL_etf`, `VN30_cash`, `VN30_stocks`, `VN30_etf`.
Each row: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf = NAV`.
Cross-check at any date: when ETF is bought in BAL, BAL_cash decreases and BAL_etf increases (minus friction).