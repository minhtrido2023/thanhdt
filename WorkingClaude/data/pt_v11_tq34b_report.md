

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
| Stock buys — share cost | +12.5094B |
| Stock buys — fee | +0.0188B |
| Stock sells — gross | +2.5979B |
| Stock sells — fee+tax | +0.0065B |
| **Net stock realized P&L** | **-9.9368B** |
| ETF buys — share cost | +67.2049B |
| ETF buys — friction | +0.1008B |
| ETF sells — gross | +27.2803B |
| ETF sells — friction | +0.0409B |
| **Net ETF cash flow** | **-40.0663B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| VHM (BAL) | +2.544B | +2.704B | +0.160B | +6.44% |
| VIC (BAL) | +2.969B | +3.045B | +0.076B | +2.71% |
| TVN (BAL) | +1.310B | +1.308B | -0.002B | +0.00% |
| VHM (VN30) | +2.544B | +2.704B | +0.160B | +6.44% |
| E1VFVN30 (BAL) | +2.386B | +2.571B | +0.185B | +7.75% |
| E1VFVN30 (BAL) | +2.121B | +2.098B | -0.024B | -1.12% |
| E1VFVN30 (BAL) | +0.514B | +0.497B | -0.017B | -3.30% |
| E1VFVN30 (BAL) | +2.174B | +2.122B | -0.053B | -2.42% |
| E1VFVN30 (BAL) | +0.537B | +0.526B | -0.010B | -1.94% |
| E1VFVN30 (BAL) | +2.482B | +2.453B | -0.029B | -1.17% |
| E1VFVN30 (BAL) | +1.157B | +1.138B | -0.018B | -1.58% |
| E1VFVN30 (BAL) | +0.507B | +0.503B | -0.004B | -0.78% |
| E1VFVN30 (BAL) | +2.086B | +2.079B | -0.008B | -0.37% |
| E1VFVN30 (BAL) | +0.630B | +0.630B | -0.000B | -0.06% |
| E1VFVN30 (BAL) | +2.208B | +2.242B | +0.033B | +1.52% |
| E1VFVN30 (BAL) | +0.389B | +0.395B | +0.006B | +1.52% |
| E1VFVN30 (BAL) | +2.265B | +2.274B | +0.009B | +0.40% |
| E1VFVN30 (VN30) | +22.503B | +24.247B | +1.743B | +7.75% |
| E1VFVN30 (VN30) | +0.134B | +0.132B | -0.001B | -1.12% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -9.937B |
| + ETF net cash flow + MTM | +3.840B |
| + Stock unrealized MTM | +9.761B (cost 9.368B → realized would be +0.393B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +12.5281B |
| + Stock sells (sell_amount - fee in) | +2.5914B |
| - ETF buys (buy_amount + fee out) | +67.3057B |
| + ETF sells (sell_amount - fee in) | +27.2394B |
| = Expected end cash (from transactions only) | -0.0030B |
| Actual end cash (from logs) | -0.0036B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0006B** |
| Actual end ETF balance (still in cash_etf) | +43.9062B |
| Open stock positions mark value | +9.7613B |
| = **Final NAV (cash + ETF + open stocks)** | **+54.0309B** |

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
| Stock buys — share cost | +11.7362B |
| Stock buys — fee | +0.0176B |
| Stock sells — gross | +2.2043B |
| Stock sells — fee+tax | +0.0055B |
| **Net stock realized P&L** | **-9.5550B** |
| ETF buys — share cost | +62.3423B |
| ETF buys — friction | +0.0935B |
| ETF sells — gross | +22.0233B |
| ETF sells — friction | +0.0330B |
| **Net ETF cash flow** | **-40.4455B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| VHM (BAL) | +2.544B | +2.715B | +0.170B | +6.85% |
| VIC (BAL) | +2.969B | +3.173B | +0.203B | +7.01% |
| TVN (BAL) | +1.310B | +1.251B | -0.058B | -4.31% |
| VHM (VN30) | +2.544B | +2.715B | +0.170B | +6.85% |
| E1VFVN30 (BAL) | +7.311B | +7.885B | +0.573B | +7.84% |
| E1VFVN30 (BAL) | +2.121B | +2.099B | -0.022B | -1.03% |
| E1VFVN30 (BAL) | +0.514B | +0.498B | -0.017B | -3.22% |
| E1VFVN30 (BAL) | +2.174B | +2.123B | -0.051B | -2.34% |
| E1VFVN30 (BAL) | +0.537B | +0.527B | -0.010B | -1.85% |
| E1VFVN30 (BAL) | +2.482B | +2.455B | -0.027B | -1.09% |
| E1VFVN30 (BAL) | +1.157B | +1.139B | -0.017B | -1.50% |
| E1VFVN30 (BAL) | +0.507B | +0.503B | -0.004B | -0.70% |
| E1VFVN30 (BAL) | +2.086B | +2.081B | -0.006B | -0.28% |
| E1VFVN30 (BAL) | +0.630B | +0.630B | +0.000B | +0.03% |
| E1VFVN30 (VN30) | +22.503B | +24.267B | +1.764B | +7.84% |
| E1VFVN30 (VN30) | +0.134B | +0.133B | -0.001B | -1.03% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -9.555B |
| + ETF net cash flow + MTM | +3.894B |
| + Stock unrealized MTM | +9.853B (cost 9.368B → realized would be +0.485B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +11.7538B |
| + Stock sells (sell_amount - fee in) | +2.1988B |
| - ETF buys (buy_amount + fee out) | +62.4358B |
| + ETF sells (sell_amount - fee in) | +21.9903B |
| = Expected end cash (from transactions only) | -0.0006B |
| Actual end cash (from logs) | -0.0012B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0006B** |
| Actual end ETF balance (still in cash_etf) | +44.3398B |
| Open stock positions mark value | +9.8532B |
| = **Final NAV (cash + ETF + open stocks)** | **+54.1919B** |

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
| Stock buys — share cost | +12.5094B |
| Stock buys — fee | +0.0188B |
| Stock sells — gross | +2.9609B |
| Stock sells — fee+tax | +0.0074B |
| **Net stock realized P&L** | **-9.5746B** |
| ETF buys — share cost | +67.5636B |
| ETF buys — friction | +0.1013B |
| ETF sells — gross | +27.2803B |
| ETF sells — friction | +0.0409B |
| **Net ETF cash flow** | **-40.4255B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| VHM (BAL) | +2.544B | +2.777B | +0.233B | +9.32% |
| VIC (BAL) | +2.969B | +3.193B | +0.224B | +7.71% |
| TVN (BAL) | +1.310B | +1.240B | -0.070B | -5.17% |
| VHM (VN30) | +2.544B | +2.777B | +0.233B | +9.32% |
| E1VFVN30 (BAL) | +2.386B | +2.598B | +0.212B | +8.90% |
| E1VFVN30 (BAL) | +2.121B | +2.120B | -0.001B | -0.06% |
| E1VFVN30 (BAL) | +0.514B | +0.503B | -0.012B | -2.26% |
| E1VFVN30 (BAL) | +2.174B | +2.144B | -0.030B | -1.38% |
| E1VFVN30 (BAL) | +0.537B | +0.532B | -0.005B | -0.88% |
| E1VFVN30 (BAL) | +2.482B | +2.480B | -0.003B | -0.11% |
| E1VFVN30 (BAL) | +1.157B | +1.151B | -0.006B | -0.53% |
| E1VFVN30 (BAL) | +0.507B | +0.508B | +0.001B | +0.28% |
| E1VFVN30 (BAL) | +2.086B | +2.101B | +0.015B | +0.70% |
| E1VFVN30 (BAL) | +0.630B | +0.636B | +0.006B | +1.01% |
| E1VFVN30 (BAL) | +2.208B | +2.266B | +0.058B | +2.60% |
| E1VFVN30 (BAL) | +0.389B | +0.399B | +0.010B | +2.60% |
| E1VFVN30 (BAL) | +2.265B | +2.298B | +0.033B | +1.47% |
| E1VFVN30 (BAL) | +0.359B | +0.359B | +0.000B | +0.00% |
| E1VFVN30 (VN30) | +22.503B | +24.506B | +2.003B | +8.90% |
| E1VFVN30 (VN30) | +0.134B | +0.134B | -0.000B | -0.06% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -9.575B |
| + ETF net cash flow + MTM | +4.310B |
| + Stock unrealized MTM | +9.988B (cost 9.368B → realized would be +0.620B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +12.5281B |
| + Stock sells (sell_amount - fee in) | +2.9535B |
| - ETF buys (buy_amount + fee out) | +67.6649B |
| + ETF sells (sell_amount - fee in) | +27.2394B |
| = Expected end cash (from transactions only) | -0.0001B |
| Actual end cash (from logs) | -0.0007B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0006B** |
| Actual end ETF balance (still in cash_etf) | +44.7353B |
| Open stock positions mark value | +9.9880B |
| = **Final NAV (cash + ETF + open stocks)** | **+54.7226B** |

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
| Stock buys — share cost | +12.5094B |
| Stock buys — fee | +0.0188B |
| Stock sells — gross | +2.9609B |
| Stock sells — fee+tax | +0.0074B |
| **Net stock realized P&L** | **-9.5746B** |
| ETF buys — share cost | +67.5636B |
| ETF buys — friction | +0.1013B |
| ETF sells — gross | +27.2803B |
| ETF sells — friction | +0.0409B |
| **Net ETF cash flow** | **-40.4255B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| VHM (BAL) | +2.544B | +2.723B | +0.179B | +7.19% |
| VIC (BAL) | +2.969B | +3.117B | +0.148B | +5.14% |
| TVN (BAL) | +1.310B | +1.319B | +0.009B | +0.86% |
| VHM (VN30) | +2.544B | +2.723B | +0.179B | +7.19% |
| E1VFVN30 (BAL) | +2.386B | +2.594B | +0.208B | +8.72% |
| E1VFVN30 (BAL) | +2.121B | +2.117B | -0.005B | -0.22% |
| E1VFVN30 (BAL) | +0.514B | +0.502B | -0.012B | -2.43% |
| E1VFVN30 (BAL) | +2.174B | +2.141B | -0.033B | -1.54% |
| E1VFVN30 (BAL) | +0.537B | +0.531B | -0.006B | -1.05% |
| E1VFVN30 (BAL) | +2.482B | +2.475B | -0.007B | -0.28% |
| E1VFVN30 (BAL) | +1.157B | +1.149B | -0.008B | -0.69% |
| E1VFVN30 (BAL) | +0.507B | +0.507B | +0.001B | +0.11% |
| E1VFVN30 (BAL) | +2.086B | +2.098B | +0.011B | +0.53% |
| E1VFVN30 (BAL) | +0.630B | +0.635B | +0.005B | +0.85% |
| E1VFVN30 (BAL) | +2.208B | +2.262B | +0.054B | +2.43% |
| E1VFVN30 (BAL) | +0.389B | +0.399B | +0.009B | +2.43% |
| E1VFVN30 (BAL) | +2.265B | +2.294B | +0.029B | +1.30% |
| E1VFVN30 (BAL) | +0.359B | +0.358B | -0.001B | -0.17% |
| E1VFVN30 (VN30) | +22.503B | +24.465B | +1.962B | +8.72% |
| E1VFVN30 (VN30) | +0.134B | +0.134B | -0.000B | -0.22% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -9.575B |
| + ETF net cash flow + MTM | +4.235B |
| + Stock unrealized MTM | +9.883B (cost 9.368B → realized would be +0.515B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +12.5281B |
| + Stock sells (sell_amount - fee in) | +2.9535B |
| - ETF buys (buy_amount + fee out) | +67.6649B |
| + ETF sells (sell_amount - fee in) | +27.2394B |
| = Expected end cash (from transactions only) | -0.0001B |
| Actual end cash (from logs) | -0.0007B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0006B** |
| Actual end ETF balance (still in cash_etf) | +44.6604B |
| Open stock positions mark value | +9.8829B |
| = **Final NAV (cash + ETF + open stocks)** | **+54.5425B** |

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
| Stock buys — share cost | +12.5094B |
| Stock buys — fee | +0.0188B |
| Stock sells — gross | +2.9609B |
| Stock sells — fee+tax | +0.0074B |
| **Net stock realized P&L** | **-9.5746B** |
| ETF buys — share cost | +67.5636B |
| ETF buys — friction | +0.1013B |
| ETF sells — gross | +27.2803B |
| ETF sells — friction | +0.0409B |
| **Net ETF cash flow** | **-40.4255B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| VHM (BAL) | +2.544B | +2.723B | +0.179B | +7.19% |
| VIC (BAL) | +2.969B | +3.117B | +0.148B | +5.14% |
| TVN (BAL) | +1.310B | +1.319B | +0.009B | +0.86% |
| VHM (VN30) | +2.544B | +2.723B | +0.179B | +7.19% |
| E1VFVN30 (BAL) | +2.386B | +2.594B | +0.208B | +8.72% |
| E1VFVN30 (BAL) | +2.121B | +2.117B | -0.005B | -0.22% |
| E1VFVN30 (BAL) | +0.514B | +0.502B | -0.012B | -2.43% |
| E1VFVN30 (BAL) | +2.174B | +2.141B | -0.033B | -1.54% |
| E1VFVN30 (BAL) | +0.537B | +0.531B | -0.006B | -1.05% |
| E1VFVN30 (BAL) | +2.482B | +2.475B | -0.007B | -0.28% |
| E1VFVN30 (BAL) | +1.157B | +1.149B | -0.008B | -0.69% |
| E1VFVN30 (BAL) | +0.507B | +0.507B | +0.001B | +0.11% |
| E1VFVN30 (BAL) | +2.086B | +2.098B | +0.011B | +0.53% |
| E1VFVN30 (BAL) | +0.630B | +0.635B | +0.005B | +0.85% |
| E1VFVN30 (BAL) | +2.208B | +2.262B | +0.054B | +2.43% |
| E1VFVN30 (BAL) | +0.389B | +0.399B | +0.009B | +2.43% |
| E1VFVN30 (BAL) | +2.265B | +2.294B | +0.029B | +1.30% |
| E1VFVN30 (BAL) | +0.359B | +0.358B | -0.001B | -0.17% |
| E1VFVN30 (VN30) | +22.503B | +24.465B | +1.962B | +8.72% |
| E1VFVN30 (VN30) | +0.134B | +0.134B | -0.000B | -0.22% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -9.575B |
| + ETF net cash flow + MTM | +4.235B |
| + Stock unrealized MTM | +9.883B (cost 9.368B → realized would be +0.515B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +12.5281B |
| + Stock sells (sell_amount - fee in) | +2.9535B |
| - ETF buys (buy_amount + fee out) | +67.6649B |
| + ETF sells (sell_amount - fee in) | +27.2394B |
| = Expected end cash (from transactions only) | -0.0001B |
| Actual end cash (from logs) | -0.0007B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0006B** |
| Actual end ETF balance (still in cash_etf) | +44.6604B |
| Open stock positions mark value | +9.8829B |
| = **Final NAV (cash + ETF + open stocks)** | **+54.5425B** |

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
| Stock buys — share cost | +12.5094B |
| Stock buys — fee | +0.0188B |
| Stock sells — gross | +2.9609B |
| Stock sells — fee+tax | +0.0074B |
| **Net stock realized P&L** | **-9.5746B** |
| ETF buys — share cost | +67.4963B |
| ETF buys — friction | +0.1012B |
| ETF sells — gross | +27.2128B |
| ETF sells — friction | +0.0408B |
| **Net ETF cash flow** | **-40.4255B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| VHM (BAL) | +2.544B | +2.622B | +0.078B | +3.22% |
| VIC (BAL) | +2.969B | +3.117B | +0.148B | +5.14% |
| TVN (BAL) | +1.310B | +1.319B | +0.009B | +0.86% |
| VHM (VN30) | +2.544B | +2.622B | +0.078B | +3.22% |
| E1VFVN30 (BAL) | +2.448B | +2.662B | +0.213B | +8.72% |
| E1VFVN30 (BAL) | +2.112B | +2.108B | -0.005B | -0.22% |
| E1VFVN30 (BAL) | +0.514B | +0.502B | -0.012B | -2.43% |
| E1VFVN30 (BAL) | +2.164B | +2.131B | -0.033B | -1.54% |
| E1VFVN30 (BAL) | +0.537B | +0.531B | -0.006B | -1.05% |
| E1VFVN30 (BAL) | +2.472B | +2.465B | -0.007B | -0.28% |
| E1VFVN30 (BAL) | +1.147B | +1.139B | -0.008B | -0.69% |
| E1VFVN30 (BAL) | +0.507B | +0.507B | +0.001B | +0.11% |
| E1VFVN30 (BAL) | +2.077B | +2.088B | +0.011B | +0.53% |
| E1VFVN30 (BAL) | +0.630B | +0.635B | +0.005B | +0.85% |
| E1VFVN30 (BAL) | +2.199B | +2.252B | +0.053B | +2.43% |
| E1VFVN30 (BAL) | +0.389B | +0.399B | +0.009B | +2.43% |
| E1VFVN30 (BAL) | +2.256B | +2.285B | +0.029B | +1.30% |
| E1VFVN30 (BAL) | +0.359B | +0.358B | -0.001B | -0.17% |
| E1VFVN30 (VN30) | +22.503B | +24.465B | +1.962B | +8.72% |
| E1VFVN30 (VN30) | +0.134B | +0.134B | -0.000B | -0.22% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -9.575B |
| + ETF net cash flow + MTM | +4.235B |
| + Stock unrealized MTM | +9.681B (cost 9.368B → realized would be +0.313B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +12.5281B |
| + Stock sells (sell_amount - fee in) | +2.9535B |
| - ETF buys (buy_amount + fee out) | +67.5975B |
| + ETF sells (sell_amount - fee in) | +27.1720B |
| = Expected end cash (from transactions only) | -0.0001B |
| Actual end cash (from logs) | -0.0007B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0006B** |
| Actual end ETF balance (still in cash_etf) | +44.6606B |
| Open stock positions mark value | +9.6810B |
| = **Final NAV (cash + ETF + open stocks)** | **+54.3409B** |

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
| Stock buys — share cost | +21.2500B |
| Stock buys — fee | +0.0319B |
| Stock sells — gross | +2.9609B |
| Stock sells — fee+tax | +0.0074B |
| **Net stock realized P&L** | **-18.3284B** |
| ETF buys — share cost | +67.4963B |
| ETF buys — friction | +0.1012B |
| ETF sells — gross | +35.9805B |
| ETF sells — friction | +0.0540B |
| **Net ETF cash flow** | **-31.6710B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| VHM (BAL) | +2.544B | +2.642B | +0.097B | +3.97% |
| VIC (BAL) | +2.969B | +3.159B | +0.190B | +6.54% |
| TVN (BAL) | +1.310B | +1.308B | -0.002B | +0.00% |
| PVD (BAL) | +2.720B | +2.716B | -0.004B | +0.00% |
| VCG (BAL) | +2.988B | +2.983B | -0.004B | +0.00% |
| VHM (VN30) | +2.544B | +2.642B | +0.097B | +3.97% |
| PVD (VN30) | +2.725B | +2.721B | -0.004B | +0.00% |
| E1VFVN30 (BAL) | +1.399B | +1.380B | -0.018B | -1.32% |
| E1VFVN30 (BAL) | +0.537B | +0.532B | -0.004B | -0.83% |
| E1VFVN30 (BAL) | +2.472B | +2.471B | -0.001B | -0.06% |
| E1VFVN30 (BAL) | +1.147B | +1.141B | -0.005B | -0.47% |
| E1VFVN30 (BAL) | +0.507B | +0.508B | +0.002B | +0.34% |
| E1VFVN30 (BAL) | +2.077B | +2.092B | +0.016B | +0.76% |
| E1VFVN30 (BAL) | +0.630B | +0.637B | +0.007B | +1.07% |
| E1VFVN30 (BAL) | +2.199B | +2.258B | +0.059B | +2.66% |
| E1VFVN30 (BAL) | +0.389B | +0.400B | +0.010B | +2.66% |
| E1VFVN30 (BAL) | +2.256B | +2.290B | +0.034B | +1.53% |
| E1VFVN30 (BAL) | +0.359B | +0.359B | +0.000B | +0.06% |
| E1VFVN30 (VN30) | +19.998B | +21.790B | +1.792B | +8.96% |
| E1VFVN30 (VN30) | +0.134B | +0.134B | +0.000B | +0.00% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -18.328B |
| + ETF net cash flow + MTM | +4.322B |
| + Stock unrealized MTM | +18.170B (cost 17.801B → realized would be +0.369B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +21.2819B |
| + Stock sells (sell_amount - fee in) | +2.9535B |
| - ETF buys (buy_amount + fee out) | +67.5975B |
| + ETF sells (sell_amount - fee in) | +35.9265B |
| = Expected end cash (from transactions only) | +0.0006B |
| Actual end cash (from logs) | +0.0000B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0006B** |
| Actual end ETF balance (still in cash_etf) | +35.9928B |
| Open stock positions mark value | +18.1703B |
| = **Final NAV (cash + ETF + open stocks)** | **+54.4830B** |

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
| Stock buys — share cost | +24.3207B |
| Stock buys — fee | +0.0365B |
| Stock sells — gross | +2.9609B |
| Stock sells — fee+tax | +0.0074B |
| **Net stock realized P&L** | **-21.4036B** |
| ETF buys — share cost | +70.1473B |
| ETF buys — friction | +0.1052B |
| ETF sells — gross | +41.7154B |
| ETF sells — friction | +0.0626B |
| **Net ETF cash flow** | **-28.5998B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| VHM (BAL) | +2.544B | +2.588B | +0.043B | +1.85% |
| VIC (BAL) | +2.969B | +3.159B | +0.190B | +6.54% |
| TVN (BAL) | +1.310B | +1.341B | +0.032B | +2.59% |
| PVD (BAL) | +2.720B | +2.779B | +0.058B | +2.29% |
| VCG (BAL) | +2.988B | +2.983B | -0.004B | +0.00% |
| TPB (BAL) | +2.728B | +2.724B | -0.004B | +0.00% |
| VHM (VN30) | +2.544B | +2.588B | +0.043B | +1.85% |
| PVD (VN30) | +2.725B | +2.784B | +0.058B | +2.29% |
| E1VFVN30 (BAL) | +0.330B | +0.333B | +0.003B | +0.92% |
| E1VFVN30 (BAL) | +2.077B | +2.105B | +0.028B | +1.35% |
| E1VFVN30 (BAL) | +0.630B | +0.640B | +0.010B | +1.66% |
| E1VFVN30 (BAL) | +2.199B | +2.271B | +0.072B | +3.26% |
| E1VFVN30 (BAL) | +0.389B | +0.402B | +0.013B | +3.26% |
| E1VFVN30 (BAL) | +2.256B | +2.303B | +0.048B | +2.12% |
| E1VFVN30 (BAL) | +0.359B | +0.361B | +0.002B | +0.64% |
| E1VFVN30 (BAL) | +2.651B | +2.651B | +0.000B | +0.00% |
| E1VFVN30 (VN30) | +19.998B | +21.918B | +1.920B | +9.60% |
| E1VFVN30 (VN30) | +0.134B | +0.135B | +0.001B | +0.59% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -21.404B |
| + ETF net cash flow + MTM | +4.520B |
| + Stock unrealized MTM | +20.945B (cost 20.529B → realized would be +0.416B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +24.3571B |
| + Stock sells (sell_amount - fee in) | +2.9535B |
| - ETF buys (buy_amount + fee out) | +70.2526B |
| + ETF sells (sell_amount - fee in) | +41.6528B |
| = Expected end cash (from transactions only) | -0.0034B |
| Actual end cash (from logs) | -0.0040B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0006B** |
| Actual end ETF balance (still in cash_etf) | +33.1197B |
| Open stock positions mark value | +20.9448B |
| = **Final NAV (cash + ETF + open stocks)** | **+54.7196B** |

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
| Stock buys — share cost | +24.3207B |
| Stock buys — fee | +0.0365B |
| Stock sells — gross | +2.9609B |
| Stock sells — fee+tax | +0.0074B |
| **Net stock realized P&L** | **-21.4036B** |
| ETF buys — share cost | +70.1473B |
| ETF buys — friction | +0.1052B |
| ETF sells — gross | +41.7154B |
| ETF sells — friction | +0.0626B |
| **Net ETF cash flow** | **-28.5998B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| VHM (BAL) | +2.544B | +2.617B | +0.073B | +3.01% |
| VIC (BAL) | +2.969B | +3.159B | +0.190B | +6.54% |
| TVN (BAL) | +1.310B | +1.319B | +0.009B | +0.86% |
| PVD (BAL) | +2.720B | +2.721B | +0.000B | +0.15% |
| VCG (BAL) | +2.988B | +3.012B | +0.024B | +0.95% |
| TPB (BAL) | +2.728B | +2.707B | -0.020B | -0.60% |
| VHM (VN30) | +2.544B | +2.617B | +0.073B | +3.01% |
| PVD (VN30) | +2.725B | +2.725B | +0.000B | +0.15% |
| E1VFVN30 (BAL) | +0.330B | +0.333B | +0.002B | +0.70% |
| E1VFVN30 (BAL) | +2.077B | +2.100B | +0.023B | +1.12% |
| E1VFVN30 (BAL) | +0.630B | +0.639B | +0.009B | +1.44% |
| E1VFVN30 (BAL) | +2.199B | +2.266B | +0.067B | +3.03% |
| E1VFVN30 (BAL) | +0.389B | +0.401B | +0.012B | +3.03% |
| E1VFVN30 (BAL) | +2.256B | +2.298B | +0.043B | +1.90% |
| E1VFVN30 (BAL) | +0.359B | +0.360B | +0.002B | +0.42% |
| E1VFVN30 (BAL) | +2.651B | +2.645B | -0.006B | -0.22% |
| E1VFVN30 (VN30) | +19.998B | +21.869B | +1.871B | +9.36% |
| E1VFVN30 (VN30) | +0.134B | +0.134B | +0.000B | +0.36% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -21.404B |
| + ETF net cash flow + MTM | +4.446B |
| + Stock unrealized MTM | +20.877B (cost 20.529B → realized would be +0.348B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +24.3571B |
| + Stock sells (sell_amount - fee in) | +2.9535B |
| - ETF buys (buy_amount + fee out) | +70.2526B |
| + ETF sells (sell_amount - fee in) | +41.6528B |
| = Expected end cash (from transactions only) | -0.0034B |
| Actual end cash (from logs) | -0.0040B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0006B** |
| Actual end ETF balance (still in cash_etf) | +33.0462B |
| Open stock positions mark value | +20.8770B |
| = **Final NAV (cash + ETF + open stocks)** | **+54.5963B** |

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
| Stock buys — share cost | +12.5094B |
| Stock buys — fee | +0.0188B |
| Stock sells — gross | +2.9609B |
| Stock sells — fee+tax | +0.0074B |
| **Net stock realized P&L** | **-9.5746B** |
| ETF buys — share cost | +67.5636B |
| ETF buys — friction | +0.1013B |
| ETF sells — gross | +27.2803B |
| ETF sells — friction | +0.0409B |
| **Net ETF cash flow** | **-40.4255B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| VHM (BAL) | +2.544B | +2.723B | +0.179B | +7.19% |
| VIC (BAL) | +2.969B | +3.117B | +0.148B | +5.14% |
| TVN (BAL) | +1.310B | +1.319B | +0.009B | +0.86% |
| VHM (VN30) | +2.544B | +2.723B | +0.179B | +7.19% |
| E1VFVN30 (BAL) | +2.386B | +2.594B | +0.208B | +8.72% |
| E1VFVN30 (BAL) | +2.121B | +2.117B | -0.005B | -0.22% |
| E1VFVN30 (BAL) | +0.514B | +0.502B | -0.012B | -2.43% |
| E1VFVN30 (BAL) | +2.174B | +2.141B | -0.033B | -1.54% |
| E1VFVN30 (BAL) | +0.537B | +0.531B | -0.006B | -1.05% |
| E1VFVN30 (BAL) | +2.482B | +2.475B | -0.007B | -0.28% |
| E1VFVN30 (BAL) | +1.157B | +1.149B | -0.008B | -0.69% |
| E1VFVN30 (BAL) | +0.507B | +0.507B | +0.001B | +0.11% |
| E1VFVN30 (BAL) | +2.086B | +2.098B | +0.011B | +0.53% |
| E1VFVN30 (BAL) | +0.630B | +0.635B | +0.005B | +0.85% |
| E1VFVN30 (BAL) | +2.208B | +2.262B | +0.054B | +2.43% |
| E1VFVN30 (BAL) | +0.389B | +0.399B | +0.009B | +2.43% |
| E1VFVN30 (BAL) | +2.265B | +2.294B | +0.029B | +1.30% |
| E1VFVN30 (BAL) | +0.359B | +0.358B | -0.001B | -0.17% |
| E1VFVN30 (VN30) | +22.503B | +24.465B | +1.962B | +8.72% |
| E1VFVN30 (VN30) | +0.134B | +0.134B | -0.000B | -0.22% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -9.575B |
| + ETF net cash flow + MTM | +4.235B |
| + Stock unrealized MTM | +9.883B (cost 9.368B → realized would be +0.515B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +12.5281B |
| + Stock sells (sell_amount - fee in) | +2.9535B |
| - ETF buys (buy_amount + fee out) | +67.6649B |
| + ETF sells (sell_amount - fee in) | +27.2394B |
| = Expected end cash (from transactions only) | -0.0001B |
| Actual end cash (from logs) | -0.0007B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0006B** |
| Actual end ETF balance (still in cash_etf) | +44.6604B |
| Open stock positions mark value | +9.8829B |
| = **Final NAV (cash + ETF + open stocks)** | **+54.5425B** |

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
| Stock buys — share cost | +24.9730B |
| Stock buys — fee | +0.0375B |
| Stock sells — gross | +12.1922B |
| Stock sells — fee+tax | +0.0305B |
| **Net stock realized P&L** | **-12.8487B** |
| ETF buys — share cost | +78.6983B |
| ETF buys — friction | +0.1180B |
| ETF sells — gross | +41.7154B |
| ETF sells — friction | +0.0626B |
| **Net ETF cash flow** | **-37.1635B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| TVN (BAL) | +1.310B | +1.251B | -0.058B | -4.31% |
| PVD (BAL) | +2.720B | +2.621B | -0.100B | -3.52% |
| VCG (BAL) | +2.988B | +2.869B | -0.118B | -3.82% |
| TPB (BAL) | +2.728B | +2.658B | -0.070B | -2.41% |
| PVD (VN30) | +2.725B | +2.625B | -0.100B | -3.52% |
| E1VFVN30 (BAL) | +0.330B | +0.330B | +0.000B | +0.00% |
| E1VFVN30 (BAL) | +2.077B | +2.085B | +0.009B | +0.42% |
| E1VFVN30 (BAL) | +0.630B | +0.635B | +0.005B | +0.73% |
| E1VFVN30 (BAL) | +2.199B | +2.250B | +0.051B | +2.32% |
| E1VFVN30 (BAL) | +0.389B | +0.398B | +0.009B | +2.32% |
| E1VFVN30 (BAL) | +2.256B | +2.282B | +0.027B | +1.19% |
| E1VFVN30 (BAL) | +0.359B | +0.358B | -0.001B | -0.28% |
| E1VFVN30 (BAL) | +2.651B | +2.627B | -0.024B | -0.91% |
| E1VFVN30 (BAL) | +5.796B | +5.796B | +0.000B | +0.00% |
| E1VFVN30 (VN30) | +19.998B | +21.718B | +1.719B | +8.60% |
| E1VFVN30 (VN30) | +0.134B | +0.133B | -0.000B | -0.33% |
| E1VFVN30 (VN30) | +2.755B | +2.755B | +0.000B | +0.00% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -12.849B |
| + ETF net cash flow + MTM | +4.204B |
| + Stock unrealized MTM | +12.025B (cost 12.471B → realized would be -0.446B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +25.0105B |
| + Stock sells (sell_amount - fee in) | +12.1617B |
| - ETF buys (buy_amount + fee out) | +78.8163B |
| + ETF sells (sell_amount - fee in) | +41.6528B |
| = Expected end cash (from transactions only) | -0.0122B |
| Actual end cash (from logs) | -0.0128B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0006B** |
| Actual end ETF balance (still in cash_etf) | +41.3677B |
| Open stock positions mark value | +12.0250B |
| = **Final NAV (cash + ETF + open stocks)** | **+54.0685B** |

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
| Stock buys — share cost | +24.9730B |
| Stock buys — fee | +0.0375B |
| Stock sells — gross | +12.1922B |
| Stock sells — fee+tax | +0.0305B |
| **Net stock realized P&L** | **-12.8487B** |
| ETF buys — share cost | +78.6983B |
| ETF buys — friction | +0.1180B |
| ETF sells — gross | +41.7154B |
| ETF sells — friction | +0.0626B |
| **Net ETF cash flow** | **-37.1635B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| TVN (BAL) | +1.310B | +1.251B | -0.058B | -4.31% |
| PVD (BAL) | +2.720B | +2.621B | -0.100B | -3.52% |
| VCG (BAL) | +2.988B | +2.869B | -0.118B | -3.82% |
| TPB (BAL) | +2.728B | +2.658B | -0.070B | -2.41% |
| PVD (VN30) | +2.725B | +2.625B | -0.100B | -3.52% |
| E1VFVN30 (BAL) | +0.330B | +0.330B | +0.000B | +0.00% |
| E1VFVN30 (BAL) | +2.077B | +2.085B | +0.009B | +0.42% |
| E1VFVN30 (BAL) | +0.630B | +0.635B | +0.005B | +0.73% |
| E1VFVN30 (BAL) | +2.199B | +2.250B | +0.051B | +2.32% |
| E1VFVN30 (BAL) | +0.389B | +0.398B | +0.009B | +2.32% |
| E1VFVN30 (BAL) | +2.256B | +2.282B | +0.027B | +1.19% |
| E1VFVN30 (BAL) | +0.359B | +0.358B | -0.001B | -0.28% |
| E1VFVN30 (BAL) | +2.651B | +2.627B | -0.024B | -0.91% |
| E1VFVN30 (BAL) | +5.796B | +5.796B | +0.000B | +0.00% |
| E1VFVN30 (VN30) | +19.998B | +21.718B | +1.719B | +8.60% |
| E1VFVN30 (VN30) | +0.134B | +0.133B | -0.000B | -0.33% |
| E1VFVN30 (VN30) | +2.755B | +2.755B | +0.000B | +0.00% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -12.849B |
| + ETF net cash flow + MTM | +4.204B |
| + Stock unrealized MTM | +12.025B (cost 12.471B → realized would be -0.446B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +25.0105B |
| + Stock sells (sell_amount - fee in) | +12.1617B |
| - ETF buys (buy_amount + fee out) | +78.8163B |
| + ETF sells (sell_amount - fee in) | +41.6528B |
| = Expected end cash (from transactions only) | -0.0122B |
| Actual end cash (from logs) | -0.0128B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0006B** |
| Actual end ETF balance (still in cash_etf) | +41.3677B |
| Open stock positions mark value | +12.0250B |
| = **Final NAV (cash + ETF + open stocks)** | **+54.0685B** |

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
| Stock buys — share cost | +24.9730B |
| Stock buys — fee | +0.0375B |
| Stock sells — gross | +12.8809B |
| Stock sells — fee+tax | +0.0322B |
| **Net stock realized P&L** | **-12.1618B** |
| ETF buys — share cost | +79.3765B |
| ETF buys — friction | +0.1191B |
| ETF sells — gross | +41.7154B |
| ETF sells — friction | +0.0626B |
| **Net ETF cash flow** | **-37.8427B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| TVN (BAL) | +1.310B | +1.251B | -0.058B | -4.31% |
| PVD (BAL) | +2.720B | +2.621B | -0.100B | -3.52% |
| VCG (BAL) | +2.988B | +2.912B | -0.076B | -2.39% |
| TPB (BAL) | +2.728B | +2.658B | -0.070B | -2.41% |
| PVD (VN30) | +2.725B | +2.625B | -0.100B | -3.52% |
| E1VFVN30 (BAL) | +0.330B | +0.331B | +0.000B | +0.06% |
| E1VFVN30 (BAL) | +2.077B | +2.087B | +0.010B | +0.48% |
| E1VFVN30 (BAL) | +0.630B | +0.635B | +0.005B | +0.79% |
| E1VFVN30 (BAL) | +2.199B | +2.251B | +0.052B | +2.38% |
| E1VFVN30 (BAL) | +0.389B | +0.399B | +0.009B | +2.38% |
| E1VFVN30 (BAL) | +2.256B | +2.284B | +0.028B | +1.25% |
| E1VFVN30 (BAL) | +0.359B | +0.358B | -0.001B | -0.22% |
| E1VFVN30 (BAL) | +2.651B | +2.628B | -0.023B | -0.86% |
| E1VFVN30 (BAL) | +5.796B | +5.799B | +0.003B | +0.06% |
| E1VFVN30 (BAL) | +0.678B | +0.678B | +0.000B | +0.00% |
| E1VFVN30 (VN30) | +19.998B | +21.730B | +1.731B | +8.66% |
| E1VFVN30 (VN30) | +0.134B | +0.134B | -0.000B | -0.28% |
| E1VFVN30 (VN30) | +2.755B | +2.756B | +0.002B | +0.06% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -12.162B |
| + ETF net cash flow + MTM | +4.226B |
| + Stock unrealized MTM | +12.068B (cost 12.471B → realized would be -0.403B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +25.0105B |
| + Stock sells (sell_amount - fee in) | +12.8487B |
| - ETF buys (buy_amount + fee out) | +79.4955B |
| + ETF sells (sell_amount - fee in) | +41.6528B |
| = Expected end cash (from transactions only) | -0.0045B |
| Actual end cash (from logs) | -0.0052B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0006B** |
| Actual end ETF balance (still in cash_etf) | +42.0690B |
| Open stock positions mark value | +12.0677B |
| = **Final NAV (cash + ETF + open stocks)** | **+54.1316B** |

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
| Stock buys — share cost | +24.9730B |
| Stock buys — fee | +0.0375B |
| Stock sells — gross | +12.8809B |
| Stock sells — fee+tax | +0.0322B |
| **Net stock realized P&L** | **-12.1618B** |
| ETF buys — share cost | +79.3765B |
| ETF buys — friction | +0.1191B |
| ETF sells — gross | +41.7154B |
| ETF sells — friction | +0.0626B |
| **Net ETF cash flow** | **-37.8427B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| TVN (BAL) | +1.310B | +1.251B | -0.058B | -4.31% |
| PVD (BAL) | +2.720B | +2.621B | -0.100B | -3.52% |
| VCG (BAL) | +2.988B | +2.940B | -0.047B | -1.43% |
| TPB (BAL) | +2.728B | +2.675B | -0.053B | -1.81% |
| PVD (VN30) | +2.725B | +2.625B | -0.100B | -3.52% |
| E1VFVN30 (BAL) | +0.330B | +0.331B | +0.000B | +0.14% |
| E1VFVN30 (BAL) | +2.077B | +2.088B | +0.012B | +0.56% |
| E1VFVN30 (BAL) | +0.630B | +0.636B | +0.006B | +0.87% |
| E1VFVN30 (BAL) | +2.199B | +2.253B | +0.054B | +2.46% |
| E1VFVN30 (BAL) | +0.389B | +0.399B | +0.010B | +2.46% |
| E1VFVN30 (BAL) | +2.256B | +2.286B | +0.030B | +1.33% |
| E1VFVN30 (BAL) | +0.359B | +0.358B | -0.001B | -0.14% |
| E1VFVN30 (BAL) | +2.651B | +2.630B | -0.021B | -0.78% |
| E1VFVN30 (BAL) | +5.796B | +5.804B | +0.008B | +0.14% |
| E1VFVN30 (BAL) | +0.678B | +0.679B | +0.001B | +0.08% |
| E1VFVN30 (VN30) | +19.998B | +21.748B | +1.750B | +8.75% |
| E1VFVN30 (VN30) | +0.134B | +0.134B | -0.000B | -0.20% |
| E1VFVN30 (VN30) | +2.755B | +2.759B | +0.004B | +0.14% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -12.162B |
| + ETF net cash flow + MTM | +4.262B |
| + Stock unrealized MTM | +12.113B (cost 12.471B → realized would be -0.358B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +25.0105B |
| + Stock sells (sell_amount - fee in) | +12.8487B |
| - ETF buys (buy_amount + fee out) | +79.4955B |
| + ETF sells (sell_amount - fee in) | +41.6528B |
| = Expected end cash (from transactions only) | -0.0045B |
| Actual end cash (from logs) | -0.0052B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0006B** |
| Actual end ETF balance (still in cash_etf) | +42.1043B |
| Open stock positions mark value | +12.1126B |
| = **Final NAV (cash + ETF + open stocks)** | **+54.2118B** |

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
| Stock buys — share cost | +24.9730B |
| Stock buys — fee | +0.0375B |
| Stock sells — gross | +12.8809B |
| Stock sells — fee+tax | +0.0322B |
| **Net stock realized P&L** | **-12.1618B** |
| ETF buys — share cost | +79.3765B |
| ETF buys — friction | +0.1191B |
| ETF sells — gross | +41.7154B |
| ETF sells — friction | +0.0626B |
| **Net ETF cash flow** | **-37.8427B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| TVN (BAL) | +1.310B | +1.251B | -0.058B | -4.31% |
| PVD (BAL) | +2.720B | +2.621B | -0.100B | -3.52% |
| VCG (BAL) | +2.988B | +2.955B | -0.033B | -0.95% |
| TPB (BAL) | +2.728B | +2.658B | -0.070B | -2.41% |
| PVD (VN30) | +2.725B | +2.625B | -0.100B | -3.52% |
| E1VFVN30 (BAL) | +0.330B | +0.330B | -0.000B | -0.03% |
| E1VFVN30 (BAL) | +2.077B | +2.085B | +0.008B | +0.39% |
| E1VFVN30 (BAL) | +0.630B | +0.634B | +0.004B | +0.70% |
| E1VFVN30 (BAL) | +2.199B | +2.249B | +0.050B | +2.29% |
| E1VFVN30 (BAL) | +0.389B | +0.398B | +0.009B | +2.29% |
| E1VFVN30 (BAL) | +2.256B | +2.282B | +0.026B | +1.16% |
| E1VFVN30 (BAL) | +0.359B | +0.358B | -0.001B | -0.31% |
| E1VFVN30 (BAL) | +2.651B | +2.626B | -0.025B | -0.94% |
| E1VFVN30 (BAL) | +5.796B | +5.795B | -0.002B | -0.03% |
| E1VFVN30 (BAL) | +0.678B | +0.678B | -0.001B | -0.08% |
| E1VFVN30 (VN30) | +19.998B | +21.712B | +1.713B | +8.57% |
| E1VFVN30 (VN30) | +0.134B | +0.133B | -0.000B | -0.36% |
| E1VFVN30 (VN30) | +2.755B | +2.754B | -0.001B | -0.03% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -12.162B |
| + ETF net cash flow + MTM | +4.191B |
| + Stock unrealized MTM | +12.110B (cost 12.471B → realized would be -0.360B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +25.0105B |
| + Stock sells (sell_amount - fee in) | +12.8487B |
| - ETF buys (buy_amount + fee out) | +79.4955B |
| + ETF sells (sell_amount - fee in) | +41.6528B |
| = Expected end cash (from transactions only) | -0.0045B |
| Actual end cash (from logs) | -0.0052B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0006B** |
| Actual end ETF balance (still in cash_etf) | +42.0337B |
| Open stock positions mark value | +12.1105B |
| = **Final NAV (cash + ETF + open stocks)** | **+54.1390B** |

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
| Stock buys — share cost | +27.6393B |
| Stock buys — fee | +0.0415B |
| Stock sells — gross | +12.8809B |
| Stock sells — fee+tax | +0.0322B |
| **Net stock realized P&L** | **-14.8321B** |
| ETF buys — share cost | +79.3765B |
| ETF buys — friction | +0.1191B |
| ETF sells — gross | +44.3907B |
| ETF sells — friction | +0.0666B |
| **Net ETF cash flow** | **-35.1714B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| TVN (BAL) | +1.310B | +1.274B | -0.036B | -2.59% |
| PVD (BAL) | +2.720B | +2.621B | -0.100B | -3.52% |
| VCG (BAL) | +2.988B | +2.891B | -0.097B | -3.10% |
| TPB (BAL) | +2.728B | +2.617B | -0.111B | -3.92% |
| MBS (BAL) | +2.670B | +2.666B | -0.004B | +0.00% |
| PVD (VN30) | +2.725B | +2.625B | -0.100B | -3.52% |
| E1VFVN30 (BAL) | +0.359B | +0.360B | +0.001B | +0.23% |
| E1VFVN30 (BAL) | +2.199B | +2.239B | +0.040B | +1.80% |
| E1VFVN30 (BAL) | +0.389B | +0.396B | +0.007B | +1.80% |
| E1VFVN30 (BAL) | +2.256B | +2.271B | +0.015B | +0.68% |
| E1VFVN30 (BAL) | +0.359B | +0.356B | -0.003B | -0.78% |
| E1VFVN30 (BAL) | +2.651B | +2.614B | -0.037B | -1.41% |
| E1VFVN30 (BAL) | +5.796B | +5.767B | -0.029B | -0.50% |
| E1VFVN30 (BAL) | +0.678B | +0.674B | -0.004B | -0.56% |
| E1VFVN30 (VN30) | +19.998B | +21.608B | +1.610B | +8.05% |
| E1VFVN30 (VN30) | +0.134B | +0.133B | -0.001B | -0.84% |
| E1VFVN30 (VN30) | +2.755B | +2.741B | -0.014B | -0.50% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -14.832B |
| + ETF net cash flow + MTM | +3.987B |
| + Stock unrealized MTM | +14.694B (cost 15.141B → realized would be -0.447B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +27.6808B |
| + Stock sells (sell_amount - fee in) | +12.8487B |
| - ETF buys (buy_amount + fee out) | +79.4955B |
| + ETF sells (sell_amount - fee in) | +44.3241B |
| = Expected end cash (from transactions only) | -0.0035B |
| Actual end cash (from logs) | -0.0041B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0006B** |
| Actual end ETF balance (still in cash_etf) | +39.1585B |
| Open stock positions mark value | +14.6942B |
| = **Final NAV (cash + ETF + open stocks)** | **+53.8485B** |

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
| Stock buys — share cost | +25.1732B |
| Stock buys — fee | +0.0378B |
| Stock sells — gross | +6.9165B |
| Stock sells — fee+tax | +0.0173B |
| **Net stock realized P&L** | **-18.3117B** |
| ETF buys — share cost | +73.5778B |
| ETF buys — friction | +0.1104B |
| ETF sells — gross | +42.0640B |
| ETF sells — friction | +0.0631B |
| **Net ETF cash flow** | **-31.6872B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| TVN (BAL) | +1.310B | +1.195B | -0.115B | -8.62% |
| NAB (BAL) | +2.705B | +2.660B | -0.045B | -1.52% |
| PVD (BAL) | +2.978B | +2.823B | -0.154B | -5.05% |
| VCG (BAL) | +3.270B | +3.086B | -0.184B | -5.49% |
| TPB (BAL) | +2.720B | +2.544B | -0.176B | -6.33% |
| MBS (BAL) | +2.659B | +2.488B | -0.171B | -6.31% |
| PVD (VN30) | +2.544B | +2.412B | -0.132B | -5.05% |
| E1VFVN30 (BAL) | +0.098B | +0.097B | -0.001B | -1.41% |
| E1VFVN30 (BAL) | +2.204B | +2.207B | +0.003B | +0.14% |
| E1VFVN30 (BAL) | +0.389B | +0.390B | +0.001B | +0.14% |
| E1VFVN30 (BAL) | +2.266B | +2.244B | -0.022B | -0.96% |
| E1VFVN30 (BAL) | +0.359B | +0.350B | -0.009B | -2.40% |
| E1VFVN30 (BAL) | +2.642B | +2.562B | -0.080B | -3.02% |
| E1VFVN30 (BAL) | +2.602B | +2.546B | -0.055B | -2.13% |
| E1VFVN30 (BAL) | +0.683B | +0.668B | -0.015B | -2.18% |
| E1VFVN30 (VN30) | +22.504B | +23.919B | +1.415B | +6.29% |
| E1VFVN30 (VN30) | +0.134B | +0.131B | -0.003B | -2.45% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -18.312B |
| + ETF net cash flow + MTM | +3.426B |
| + Stock unrealized MTM | +17.207B (cost 18.185B → realized would be -0.978B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +25.2110B |
| + Stock sells (sell_amount - fee in) | +6.8992B |
| - ETF buys (buy_amount + fee out) | +73.6881B |
| + ETF sells (sell_amount - fee in) | +42.0009B |
| = Expected end cash (from transactions only) | +0.0010B |
| Actual end cash (from logs) | -0.0002B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0012B** |
| Actual end ETF balance (still in cash_etf) | +35.1137B |
| Open stock positions mark value | +17.2074B |
| = **Final NAV (cash + ETF + open stocks)** | **+52.3209B** |

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
| Stock buys — share cost | +7.0039B |
| Stock buys — fee | +0.0105B |
| Stock sells — gross | +5.6025B |
| Stock sells — fee+tax | +0.0140B |
| **Net stock realized P&L** | **-1.4259B** |
| ETF buys — share cost | +70.1517B |
| ETF buys — friction | +0.1052B |
| ETF sells — gross | +21.6742B |
| ETF sells — friction | +0.0325B |
| **Net ETF cash flow** | **-48.6152B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| TVN (BAL) | +1.310B | +1.161B | -0.149B | -11.21% |
| E1VFVN30 (BAL) | +5.034B | +5.342B | +0.307B | +6.11% |
| E1VFVN30 (BAL) | +0.134B | +0.130B | -0.004B | -2.62% |
| E1VFVN30 (BAL) | +2.129B | +2.074B | -0.056B | -2.62% |
| E1VFVN30 (BAL) | +0.514B | +0.490B | -0.025B | -4.77% |
| E1VFVN30 (BAL) | +2.166B | +2.082B | -0.085B | -3.91% |
| E1VFVN30 (BAL) | +0.537B | +0.518B | -0.018B | -3.43% |
| E1VFVN30 (BAL) | +2.460B | +2.394B | -0.066B | -2.67% |
| E1VFVN30 (BAL) | +1.146B | +1.110B | -0.035B | -3.08% |
| E1VFVN30 (BAL) | +0.507B | +0.495B | -0.012B | -2.29% |
| E1VFVN30 (BAL) | +2.076B | +2.037B | -0.039B | -1.88% |
| E1VFVN30 (BAL) | +0.630B | +0.620B | -0.010B | -1.58% |
| E1VFVN30 (BAL) | +2.204B | +2.203B | -0.001B | -0.03% |
| E1VFVN30 (BAL) | +0.389B | +0.389B | -0.000B | -0.03% |
| E1VFVN30 (BAL) | +2.266B | +2.240B | -0.026B | -1.13% |
| E1VFVN30 (BAL) | +0.359B | +0.350B | -0.009B | -2.57% |
| E1VFVN30 (BAL) | +2.634B | +2.574B | -0.060B | -2.29% |
| E1VFVN30 (VN30) | +25.000B | +26.526B | +1.526B | +6.11% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -1.426B |
| + ETF net cash flow + MTM | +2.960B |
| + Stock unrealized MTM | +1.161B (cost 1.310B → realized would be -0.149B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +7.0144B |
| + Stock sells (sell_amount - fee in) | +5.5885B |
| - ETF buys (buy_amount + fee out) | +70.2569B |
| + ETF sells (sell_amount - fee in) | +21.6417B |
| = Expected end cash (from transactions only) | -0.0411B |
| Actual end cash (from logs) | -0.0425B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0014B** |
| Actual end ETF balance (still in cash_etf) | +51.5754B |
| Open stock positions mark value | +1.1611B |
| = **Final NAV (cash + ETF + open stocks)** | **+52.6939B** |

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
| Stock buys — share cost | +7.0039B |
| Stock buys — fee | +0.0105B |
| Stock sells — gross | +5.6025B |
| Stock sells — fee+tax | +0.0140B |
| **Net stock realized P&L** | **-1.4259B** |
| ETF buys — share cost | +70.1517B |
| ETF buys — friction | +0.1052B |
| ETF sells — gross | +21.6742B |
| ETF sells — friction | +0.0325B |
| **Net ETF cash flow** | **-48.6152B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| TVN (BAL) | +1.310B | +1.172B | -0.137B | -10.34% |
| E1VFVN30 (BAL) | +5.034B | +5.304B | +0.269B | +5.35% |
| E1VFVN30 (BAL) | +0.134B | +0.129B | -0.004B | -3.32% |
| E1VFVN30 (BAL) | +2.129B | +2.059B | -0.071B | -3.32% |
| E1VFVN30 (BAL) | +0.514B | +0.486B | -0.028B | -5.45% |
| E1VFVN30 (BAL) | +2.166B | +2.067B | -0.100B | -4.59% |
| E1VFVN30 (BAL) | +0.537B | +0.515B | -0.022B | -4.12% |
| E1VFVN30 (BAL) | +2.460B | +2.377B | -0.083B | -3.37% |
| E1VFVN30 (BAL) | +1.146B | +1.102B | -0.043B | -3.77% |
| E1VFVN30 (BAL) | +0.507B | +0.491B | -0.015B | -2.99% |
| E1VFVN30 (BAL) | +2.076B | +2.023B | -0.054B | -2.58% |
| E1VFVN30 (BAL) | +0.630B | +0.616B | -0.014B | -2.28% |
| E1VFVN30 (BAL) | +2.204B | +2.188B | -0.016B | -0.74% |
| E1VFVN30 (BAL) | +0.389B | +0.386B | -0.003B | -0.74% |
| E1VFVN30 (BAL) | +2.266B | +2.224B | -0.042B | -1.84% |
| E1VFVN30 (BAL) | +0.359B | +0.347B | -0.012B | -3.26% |
| E1VFVN30 (BAL) | +2.634B | +2.556B | -0.079B | -2.99% |
| E1VFVN30 (VN30) | +25.000B | +26.337B | +1.337B | +5.35% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -1.426B |
| + ETF net cash flow + MTM | +2.591B |
| + Stock unrealized MTM | +1.172B (cost 1.310B → realized would be -0.137B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +7.0144B |
| + Stock sells (sell_amount - fee in) | +5.5885B |
| - ETF buys (buy_amount + fee out) | +70.2569B |
| + ETF sells (sell_amount - fee in) | +21.6417B |
| = Expected end cash (from transactions only) | -0.0411B |
| Actual end cash (from logs) | -0.0425B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0014B** |
| Actual end ETF balance (still in cash_etf) | +51.2062B |
| Open stock positions mark value | +1.1723B |
| = **Final NAV (cash + ETF + open stocks)** | **+52.3360B** |

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
| Stock buys — share cost | +7.0039B |
| Stock buys — fee | +0.0105B |
| Stock sells — gross | +5.6025B |
| Stock sells — fee+tax | +0.0140B |
| **Net stock realized P&L** | **-1.4259B** |
| ETF buys — share cost | +70.1517B |
| ETF buys — friction | +0.1052B |
| ETF sells — gross | +21.6742B |
| ETF sells — friction | +0.0325B |
| **Net ETF cash flow** | **-48.6152B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| TVN (BAL) | +1.310B | +1.184B | -0.126B | -9.48% |
| E1VFVN30 (BAL) | +5.034B | +5.330B | +0.295B | +5.86% |
| E1VFVN30 (BAL) | +0.134B | +0.130B | -0.004B | -2.84% |
| E1VFVN30 (BAL) | +2.129B | +2.069B | -0.061B | -2.84% |
| E1VFVN30 (BAL) | +0.514B | +0.489B | -0.026B | -4.99% |
| E1VFVN30 (BAL) | +2.166B | +2.077B | -0.089B | -4.13% |
| E1VFVN30 (BAL) | +0.537B | +0.517B | -0.020B | -3.65% |
| E1VFVN30 (BAL) | +2.460B | +2.389B | -0.071B | -2.90% |
| E1VFVN30 (BAL) | +1.146B | +1.108B | -0.038B | -3.30% |
| E1VFVN30 (BAL) | +0.507B | +0.494B | -0.013B | -2.52% |
| E1VFVN30 (BAL) | +2.076B | +2.033B | -0.044B | -2.11% |
| E1VFVN30 (BAL) | +0.630B | +0.619B | -0.011B | -1.80% |
| E1VFVN30 (BAL) | +2.204B | +2.198B | -0.006B | -0.26% |
| E1VFVN30 (BAL) | +0.389B | +0.388B | -0.001B | -0.26% |
| E1VFVN30 (BAL) | +2.266B | +2.235B | -0.031B | -1.36% |
| E1VFVN30 (BAL) | +0.359B | +0.349B | -0.010B | -2.79% |
| E1VFVN30 (BAL) | +2.634B | +2.568B | -0.066B | -2.52% |
| E1VFVN30 (VN30) | +25.000B | +26.466B | +1.466B | +5.86% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -1.426B |
| + ETF net cash flow + MTM | +2.842B |
| + Stock unrealized MTM | +1.184B (cost 1.310B → realized would be -0.126B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +7.0144B |
| + Stock sells (sell_amount - fee in) | +5.5885B |
| - ETF buys (buy_amount + fee out) | +70.2569B |
| + ETF sells (sell_amount - fee in) | +21.6417B |
| = Expected end cash (from transactions only) | -0.0411B |
| Actual end cash (from logs) | -0.0426B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0014B** |
| Actual end ETF balance (still in cash_etf) | +51.4573B |
| Open stock positions mark value | +1.1836B |
| = **Final NAV (cash + ETF + open stocks)** | **+52.5983B** |

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
| Stock buys — share cost | +7.0039B |
| Stock buys — fee | +0.0105B |
| Stock sells — gross | +5.6025B |
| Stock sells — fee+tax | +0.0140B |
| **Net stock realized P&L** | **-1.4259B** |
| ETF buys — share cost | +70.1517B |
| ETF buys — friction | +0.1052B |
| ETF sells — gross | +21.6742B |
| ETF sells — friction | +0.0325B |
| **Net ETF cash flow** | **-48.6152B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| TVN (BAL) | +1.310B | +1.139B | -0.171B | -12.93% |
| E1VFVN30 (BAL) | +5.034B | +5.302B | +0.268B | +5.32% |
| E1VFVN30 (BAL) | +0.134B | +0.129B | -0.004B | -3.35% |
| E1VFVN30 (BAL) | +2.129B | +2.058B | -0.071B | -3.35% |
| E1VFVN30 (BAL) | +0.514B | +0.486B | -0.028B | -5.48% |
| E1VFVN30 (BAL) | +2.166B | +2.066B | -0.100B | -4.62% |
| E1VFVN30 (BAL) | +0.537B | +0.514B | -0.022B | -4.15% |
| E1VFVN30 (BAL) | +2.460B | +2.377B | -0.084B | -3.40% |
| E1VFVN30 (BAL) | +1.146B | +1.102B | -0.044B | -3.80% |
| E1VFVN30 (BAL) | +0.507B | +0.491B | -0.015B | -3.02% |
| E1VFVN30 (BAL) | +2.076B | +2.022B | -0.054B | -2.61% |
| E1VFVN30 (BAL) | +0.630B | +0.615B | -0.015B | -2.31% |
| E1VFVN30 (BAL) | +2.204B | +2.187B | -0.017B | -0.77% |
| E1VFVN30 (BAL) | +0.389B | +0.386B | -0.003B | -0.77% |
| E1VFVN30 (BAL) | +2.266B | +2.223B | -0.042B | -1.87% |
| E1VFVN30 (BAL) | +0.359B | +0.347B | -0.012B | -3.29% |
| E1VFVN30 (BAL) | +2.634B | +2.555B | -0.080B | -3.02% |
| E1VFVN30 (VN30) | +25.000B | +26.329B | +1.329B | +5.32% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -1.426B |
| + ETF net cash flow + MTM | +2.576B |
| + Stock unrealized MTM | +1.139B (cost 1.310B → realized would be -0.171B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +7.0144B |
| + Stock sells (sell_amount - fee in) | +5.5885B |
| - ETF buys (buy_amount + fee out) | +70.2569B |
| + ETF sells (sell_amount - fee in) | +21.6417B |
| = Expected end cash (from transactions only) | -0.0411B |
| Actual end cash (from logs) | -0.0426B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0014B** |
| Actual end ETF balance (still in cash_etf) | +51.1915B |
| Open stock positions mark value | +1.1385B |
| = **Final NAV (cash + ETF + open stocks)** | **+52.2874B** |

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
| Stock buys — share cost | +7.0039B |
| Stock buys — fee | +0.0105B |
| Stock sells — gross | +5.6025B |
| Stock sells — fee+tax | +0.0140B |
| **Net stock realized P&L** | **-1.4259B** |
| ETF buys — share cost | +70.1517B |
| ETF buys — friction | +0.1052B |
| ETF sells — gross | +21.6742B |
| ETF sells — friction | +0.0325B |
| **Net ETF cash flow** | **-48.6152B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| TVN (BAL) | +1.310B | +1.048B | -0.261B | -19.83% |
| E1VFVN30 (BAL) | +5.034B | +5.215B | +0.180B | +3.58% |
| E1VFVN30 (BAL) | +0.134B | +0.127B | -0.007B | -4.93% |
| E1VFVN30 (BAL) | +2.129B | +2.024B | -0.105B | -4.93% |
| E1VFVN30 (BAL) | +0.514B | +0.478B | -0.036B | -7.03% |
| E1VFVN30 (BAL) | +2.166B | +2.032B | -0.134B | -6.19% |
| E1VFVN30 (BAL) | +0.537B | +0.506B | -0.031B | -5.72% |
| E1VFVN30 (BAL) | +2.460B | +2.338B | -0.123B | -4.99% |
| E1VFVN30 (BAL) | +1.146B | +1.084B | -0.062B | -5.38% |
| E1VFVN30 (BAL) | +0.507B | +0.483B | -0.023B | -4.62% |
| E1VFVN30 (BAL) | +2.076B | +1.989B | -0.087B | -4.21% |
| E1VFVN30 (BAL) | +0.630B | +0.605B | -0.025B | -3.92% |
| E1VFVN30 (BAL) | +2.204B | +2.151B | -0.053B | -2.40% |
| E1VFVN30 (BAL) | +0.389B | +0.380B | -0.009B | -2.40% |
| E1VFVN30 (BAL) | +2.266B | +2.187B | -0.079B | -3.48% |
| E1VFVN30 (BAL) | +0.359B | +0.341B | -0.018B | -4.88% |
| E1VFVN30 (BAL) | +2.634B | +2.513B | -0.122B | -4.62% |
| E1VFVN30 (VN30) | +25.000B | +25.896B | +0.896B | +3.58% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -1.426B |
| + ETF net cash flow + MTM | +1.735B |
| + Stock unrealized MTM | +1.048B (cost 1.310B → realized would be -0.261B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +7.0144B |
| + Stock sells (sell_amount - fee in) | +5.5885B |
| - ETF buys (buy_amount + fee out) | +70.2569B |
| + ETF sells (sell_amount - fee in) | +21.6417B |
| = Expected end cash (from transactions only) | -0.0411B |
| Actual end cash (from logs) | -0.0426B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0015B** |
| Actual end ETF balance (still in cash_etf) | +50.3499B |
| Open stock positions mark value | +1.0484B |
| = **Final NAV (cash + ETF + open stocks)** | **+51.3556B** |

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
| Stock buys — share cost | +7.0039B |
| Stock buys — fee | +0.0105B |
| Stock sells — gross | +5.6025B |
| Stock sells — fee+tax | +0.0140B |
| **Net stock realized P&L** | **-1.4259B** |
| ETF buys — share cost | +70.1517B |
| ETF buys — friction | +0.1052B |
| ETF sells — gross | +21.6742B |
| ETF sells — friction | +0.0325B |
| **Net ETF cash flow** | **-48.6152B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| TVN (BAL) | +1.310B | +1.071B | -0.239B | -18.10% |
| E1VFVN30 (BAL) | +5.034B | +5.200B | +0.165B | +3.28% |
| E1VFVN30 (BAL) | +0.134B | +0.127B | -0.007B | -5.21% |
| E1VFVN30 (BAL) | +2.129B | +2.018B | -0.111B | -5.21% |
| E1VFVN30 (BAL) | +0.514B | +0.477B | -0.038B | -7.31% |
| E1VFVN30 (BAL) | +2.166B | +2.026B | -0.140B | -6.46% |
| E1VFVN30 (BAL) | +0.537B | +0.504B | -0.032B | -6.00% |
| E1VFVN30 (BAL) | +2.460B | +2.331B | -0.130B | -5.27% |
| E1VFVN30 (BAL) | +1.146B | +1.081B | -0.065B | -5.66% |
| E1VFVN30 (BAL) | +0.507B | +0.482B | -0.025B | -4.90% |
| E1VFVN30 (BAL) | +2.076B | +1.983B | -0.093B | -4.49% |
| E1VFVN30 (BAL) | +0.630B | +0.604B | -0.026B | -4.20% |
| E1VFVN30 (BAL) | +2.204B | +2.145B | -0.059B | -2.69% |
| E1VFVN30 (BAL) | +0.389B | +0.379B | -0.010B | -2.69% |
| E1VFVN30 (BAL) | +2.266B | +2.180B | -0.085B | -3.76% |
| E1VFVN30 (BAL) | +0.359B | +0.340B | -0.019B | -5.16% |
| E1VFVN30 (BAL) | +2.634B | +2.505B | -0.129B | -4.90% |
| E1VFVN30 (VN30) | +25.000B | +25.820B | +0.820B | +3.28% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -1.426B |
| + ETF net cash flow + MTM | +1.587B |
| + Stock unrealized MTM | +1.071B (cost 1.310B → realized would be -0.239B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +7.0144B |
| + Stock sells (sell_amount - fee in) | +5.5885B |
| - ETF buys (buy_amount + fee out) | +70.2569B |
| + ETF sells (sell_amount - fee in) | +21.6417B |
| = Expected end cash (from transactions only) | -0.0411B |
| Actual end cash (from logs) | -0.0426B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0015B** |
| Actual end ETF balance (still in cash_etf) | +50.2022B |
| Open stock positions mark value | +1.0709B |
| = **Final NAV (cash + ETF + open stocks)** | **+51.2305B** |

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
| Stock buys — share cost | +24.6060B |
| Stock buys — fee | +0.0369B |
| Stock sells — gross | +6.9165B |
| Stock sells — fee+tax | +0.0173B |
| **Net stock realized P&L** | **-17.7436B** |
| ETF buys — share cost | +73.5859B |
| ETF buys — friction | +0.1104B |
| ETF sells — gross | +41.5032B |
| ETF sells — friction | +0.0623B |
| **Net ETF cash flow** | **-32.2553B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| TVN (BAL) | +1.310B | +0.969B | -0.340B | -25.86% |
| PVD (BAL) | +2.708B | +2.416B | -0.293B | -10.67% |
| VCG (BAL) | +2.974B | +2.472B | -0.502B | -16.76% |
| TPB (BAL) | +2.723B | +2.310B | -0.414B | -15.06% |
| PVS (BAL) | +2.708B | +2.307B | -0.401B | -14.69% |
| MBS (BAL) | +2.640B | +2.220B | -0.420B | -15.77% |
| PVS (VN30) | +2.553B | +2.175B | -0.378B | -14.69% |
| E1VFVN30 (BAL) | +0.043B | +0.040B | -0.003B | -6.74% |
| E1VFVN30 (BAL) | +0.630B | +0.589B | -0.041B | -6.45% |
| E1VFVN30 (BAL) | +2.204B | +2.094B | -0.110B | -4.98% |
| E1VFVN30 (BAL) | +0.389B | +0.370B | -0.019B | -4.98% |
| E1VFVN30 (BAL) | +2.266B | +2.129B | -0.137B | -6.03% |
| E1VFVN30 (BAL) | +0.359B | +0.332B | -0.027B | -7.39% |
| E1VFVN30 (BAL) | +2.646B | +2.435B | -0.211B | -7.98% |
| E1VFVN30 (BAL) | +2.605B | +2.420B | -0.186B | -7.13% |
| E1VFVN30 (BAL) | +0.683B | +0.634B | -0.049B | -7.18% |
| E1VFVN30 (VN30) | +22.504B | +22.695B | +0.191B | +0.85% |
| E1VFVN30 (VN30) | +0.134B | +0.124B | -0.010B | -7.78% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -17.744B |
| + ETF net cash flow + MTM | +1.607B |
| + Stock unrealized MTM | +14.869B (cost 17.617B → realized would be -2.748B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +24.6429B |
| + Stock sells (sell_amount - fee in) | +6.8992B |
| - ETF buys (buy_amount + fee out) | +73.6962B |
| + ETF sells (sell_amount - fee in) | +41.4409B |
| = Expected end cash (from transactions only) | +0.0011B |
| Actual end cash (from logs) | -0.0002B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0013B** |
| Actual end ETF balance (still in cash_etf) | +33.8619B |
| Open stock positions mark value | +14.8694B |
| = **Final NAV (cash + ETF + open stocks)** | **+48.7310B** |

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
| Stock buys — share cost | +24.6060B |
| Stock buys — fee | +0.0369B |
| Stock sells — gross | +7.8860B |
| Stock sells — fee+tax | +0.0226B |
| **Net stock realized P&L** | **-16.7795B** |
| ETF buys — share cost | +74.5500B |
| ETF buys — friction | +0.1118B |
| ETF sells — gross | +41.5032B |
| ETF sells — friction | +0.0623B |
| **Net ETF cash flow** | **-33.2209B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| PVD (BAL) | +2.708B | +2.554B | -0.155B | -5.56% |
| VCG (BAL) | +2.974B | +2.520B | -0.454B | -15.15% |
| TPB (BAL) | +2.723B | +2.293B | -0.430B | -15.66% |
| PVS (BAL) | +2.708B | +2.391B | -0.318B | -11.60% |
| MBS (BAL) | +2.640B | +2.304B | -0.336B | -12.61% |
| PVS (VN30) | +2.553B | +2.254B | -0.299B | -11.60% |
| E1VFVN30 (BAL) | +0.043B | +0.040B | -0.003B | -6.60% |
| E1VFVN30 (BAL) | +0.630B | +0.590B | -0.040B | -6.31% |
| E1VFVN30 (BAL) | +2.204B | +2.098B | -0.107B | -4.84% |
| E1VFVN30 (BAL) | +0.389B | +0.370B | -0.019B | -4.84% |
| E1VFVN30 (BAL) | +2.266B | +2.132B | -0.133B | -5.89% |
| E1VFVN30 (BAL) | +0.359B | +0.333B | -0.026B | -7.25% |
| E1VFVN30 (BAL) | +2.646B | +2.438B | -0.208B | -7.84% |
| E1VFVN30 (BAL) | +2.605B | +2.423B | -0.182B | -6.99% |
| E1VFVN30 (BAL) | +0.683B | +0.635B | -0.048B | -7.05% |
| E1VFVN30 (BAL) | +0.964B | +0.964B | +0.000B | +0.00% |
| E1VFVN30 (VN30) | +22.504B | +22.729B | +0.226B | +1.00% |
| E1VFVN30 (VN30) | +0.134B | +0.124B | -0.010B | -7.64% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -16.780B |
| + ETF net cash flow + MTM | +1.656B |
| + Stock unrealized MTM | +14.315B (cost 16.307B → realized would be -1.992B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +24.6429B |
| + Stock sells (sell_amount - fee in) | +7.8634B |
| - ETF buys (buy_amount + fee out) | +74.6618B |
| + ETF sells (sell_amount - fee in) | +41.4409B |
| = Expected end cash (from transactions only) | -0.0004B |
| Actual end cash (from logs) | -0.0016B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0013B** |
| Actual end ETF balance (still in cash_etf) | +34.8770B |
| Open stock positions mark value | +14.3150B |
| = **Final NAV (cash + ETF + open stocks)** | **+49.1904B** |

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
| Stock buys — share cost | +7.0039B |
| Stock buys — fee | +0.0105B |
| Stock sells — gross | +6.5719B |
| Stock sells — fee+tax | +0.0193B |
| **Net stock realized P&L** | **-0.4618B** |
| ETF buys — share cost | +71.1119B |
| ETF buys — friction | +0.1067B |
| ETF sells — gross | +21.6742B |
| ETF sells — friction | +0.0325B |
| **Net ETF cash flow** | **-49.5768B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| E1VFVN30 (BAL) | +5.034B | +5.047B | +0.012B | +0.24% |
| E1VFVN30 (BAL) | +0.134B | +0.123B | -0.011B | -8.00% |
| E1VFVN30 (BAL) | +2.129B | +1.959B | -0.170B | -8.00% |
| E1VFVN30 (BAL) | +0.514B | +0.463B | -0.052B | -10.03% |
| E1VFVN30 (BAL) | +2.166B | +1.967B | -0.200B | -9.22% |
| E1VFVN30 (BAL) | +0.537B | +0.490B | -0.047B | -8.76% |
| E1VFVN30 (BAL) | +2.460B | +2.262B | -0.198B | -8.05% |
| E1VFVN30 (BAL) | +1.146B | +1.049B | -0.097B | -8.44% |
| E1VFVN30 (BAL) | +0.507B | +0.468B | -0.039B | -7.69% |
| E1VFVN30 (BAL) | +2.076B | +1.925B | -0.152B | -7.30% |
| E1VFVN30 (BAL) | +0.630B | +0.586B | -0.044B | -7.02% |
| E1VFVN30 (BAL) | +2.204B | +2.082B | -0.122B | -5.55% |
| E1VFVN30 (BAL) | +0.389B | +0.368B | -0.022B | -5.55% |
| E1VFVN30 (BAL) | +2.266B | +2.116B | -0.149B | -6.59% |
| E1VFVN30 (BAL) | +0.359B | +0.330B | -0.029B | -7.95% |
| E1VFVN30 (BAL) | +2.634B | +2.432B | -0.203B | -7.69% |
| E1VFVN30 (BAL) | +0.960B | +0.953B | -0.007B | -0.75% |
| E1VFVN30 (VN30) | +25.000B | +25.061B | +0.061B | +0.24% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -0.462B |
| + ETF net cash flow + MTM | +0.102B |
| + Stock unrealized MTM | +0.000B (cost 0.000B → realized would be +0.000B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +7.0144B |
| + Stock sells (sell_amount - fee in) | +6.5526B |
| - ETF buys (buy_amount + fee out) | +71.2185B |
| + ETF sells (sell_amount - fee in) | +21.6417B |
| = Expected end cash (from transactions only) | -0.0386B |
| Actual end cash (from logs) | -0.0401B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0015B** |
| Actual end ETF balance (still in cash_etf) | +49.6786B |
| Open stock positions mark value | +0.0000B |
| = **Final NAV (cash + ETF + open stocks)** | **+49.6385B** |

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
| Stock buys — share cost | +7.0039B |
| Stock buys — fee | +0.0105B |
| Stock sells — gross | +6.5719B |
| Stock sells — fee+tax | +0.0193B |
| **Net stock realized P&L** | **-0.4618B** |
| ETF buys — share cost | +71.1119B |
| ETF buys — friction | +0.1067B |
| ETF sells — gross | +21.6742B |
| ETF sells — friction | +0.0325B |
| **Net ETF cash flow** | **-49.5768B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| E1VFVN30 (BAL) | +5.034B | +4.999B | -0.035B | -0.70% |
| E1VFVN30 (BAL) | +0.134B | +0.122B | -0.012B | -8.87% |
| E1VFVN30 (BAL) | +2.129B | +1.941B | -0.189B | -8.87% |
| E1VFVN30 (BAL) | +0.514B | +0.458B | -0.056B | -10.88% |
| E1VFVN30 (BAL) | +2.166B | +1.948B | -0.218B | -10.07% |
| E1VFVN30 (BAL) | +0.537B | +0.485B | -0.052B | -9.62% |
| E1VFVN30 (BAL) | +2.460B | +2.241B | -0.219B | -8.92% |
| E1VFVN30 (BAL) | +1.146B | +1.039B | -0.106B | -9.30% |
| E1VFVN30 (BAL) | +0.507B | +0.463B | -0.043B | -8.56% |
| E1VFVN30 (BAL) | +2.076B | +1.907B | -0.170B | -8.17% |
| E1VFVN30 (BAL) | +0.630B | +0.580B | -0.050B | -7.89% |
| E1VFVN30 (BAL) | +2.204B | +2.062B | -0.142B | -6.44% |
| E1VFVN30 (BAL) | +0.389B | +0.364B | -0.025B | -6.44% |
| E1VFVN30 (BAL) | +2.266B | +2.096B | -0.169B | -7.47% |
| E1VFVN30 (BAL) | +0.359B | +0.327B | -0.032B | -8.81% |
| E1VFVN30 (BAL) | +2.634B | +2.409B | -0.225B | -8.56% |
| E1VFVN30 (BAL) | +0.960B | +0.944B | -0.016B | -1.68% |
| E1VFVN30 (VN30) | +25.000B | +24.825B | -0.175B | -0.70% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -0.462B |
| + ETF net cash flow + MTM | -0.365B |
| + Stock unrealized MTM | +0.000B (cost 0.000B → realized would be +0.000B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +7.0144B |
| + Stock sells (sell_amount - fee in) | +6.5526B |
| - ETF buys (buy_amount + fee out) | +71.2185B |
| + ETF sells (sell_amount - fee in) | +21.6417B |
| = Expected end cash (from transactions only) | -0.0386B |
| Actual end cash (from logs) | -0.0402B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0015B** |
| Actual end ETF balance (still in cash_etf) | +49.2119B |
| Open stock positions mark value | +0.0000B |
| = **Final NAV (cash + ETF + open stocks)** | **+49.1718B** |

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
| Stock buys — share cost | +6.2307B |
| Stock buys — fee | +0.0093B |
| Stock sells — gross | +5.8153B |
| Stock sells — fee+tax | +0.0174B |
| **Net stock realized P&L** | **-0.4422B** |
| ETF buys — share cost | +65.8936B |
| ETF buys — friction | +0.0988B |
| ETF sells — gross | +16.4207B |
| ETF sells — friction | +0.0246B |
| **Net ETF cash flow** | **-49.5964B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| E1VFVN30 (BAL) | +9.957B | +9.945B | -0.012B | -0.12% |
| E1VFVN30 (BAL) | +0.134B | +0.123B | -0.011B | -8.34% |
| E1VFVN30 (BAL) | +2.129B | +1.952B | -0.177B | -8.34% |
| E1VFVN30 (BAL) | +0.514B | +0.461B | -0.053B | -10.36% |
| E1VFVN30 (BAL) | +2.166B | +1.960B | -0.207B | -9.55% |
| E1VFVN30 (BAL) | +0.537B | +0.488B | -0.049B | -9.10% |
| E1VFVN30 (BAL) | +2.460B | +2.254B | -0.206B | -8.39% |
| E1VFVN30 (BAL) | +1.146B | +1.045B | -0.100B | -8.77% |
| E1VFVN30 (BAL) | +0.507B | +0.466B | -0.041B | -8.03% |
| E1VFVN30 (BAL) | +2.076B | +1.918B | -0.159B | -7.64% |
| E1VFVN30 (BAL) | +0.630B | +0.584B | -0.046B | -7.35% |
| E1VFVN30 (BAL) | +2.634B | +2.423B | -0.211B | -8.03% |
| E1VFVN30 (BAL) | +0.960B | +0.949B | -0.011B | -1.11% |
| E1VFVN30 (VN30) | +25.000B | +24.970B | -0.030B | -0.12% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -0.442B |
| + ETF net cash flow + MTM | -0.061B |
| + Stock unrealized MTM | +0.000B (cost 0.000B → realized would be +0.000B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +6.2400B |
| + Stock sells (sell_amount - fee in) | +5.7978B |
| - ETF buys (buy_amount + fee out) | +65.9924B |
| + ETF sells (sell_amount - fee in) | +16.3960B |
| = Expected end cash (from transactions only) | -0.0386B |
| Actual end cash (from logs) | -0.0402B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0016B** |
| Actual end ETF balance (still in cash_etf) | +49.5358B |
| Open stock positions mark value | +0.0000B |
| = **Final NAV (cash + ETF + open stocks)** | **+49.4956B** |

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
| Stock buys — share cost | +6.2307B |
| Stock buys — fee | +0.0093B |
| Stock sells — gross | +5.8153B |
| Stock sells — fee+tax | +0.0174B |
| **Net stock realized P&L** | **-0.4422B** |
| ETF buys — share cost | +65.8936B |
| ETF buys — friction | +0.0988B |
| ETF sells — gross | +16.4207B |
| ETF sells — friction | +0.0246B |
| **Net ETF cash flow** | **-49.5964B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| E1VFVN30 (BAL) | +9.957B | +10.075B | +0.118B | +1.18% |
| E1VFVN30 (BAL) | +0.134B | +0.124B | -0.010B | -7.14% |
| E1VFVN30 (BAL) | +2.129B | +1.977B | -0.152B | -7.14% |
| E1VFVN30 (BAL) | +0.514B | +0.467B | -0.047B | -9.19% |
| E1VFVN30 (BAL) | +2.166B | +1.985B | -0.181B | -8.36% |
| E1VFVN30 (BAL) | +0.537B | +0.494B | -0.042B | -7.91% |
| E1VFVN30 (BAL) | +2.460B | +2.283B | -0.177B | -7.19% |
| E1VFVN30 (BAL) | +1.146B | +1.059B | -0.087B | -7.57% |
| E1VFVN30 (BAL) | +0.507B | +0.472B | -0.035B | -6.83% |
| E1VFVN30 (BAL) | +2.076B | +1.943B | -0.134B | -6.43% |
| E1VFVN30 (BAL) | +0.630B | +0.591B | -0.039B | -6.14% |
| E1VFVN30 (BAL) | +2.634B | +2.454B | -0.180B | -6.83% |
| E1VFVN30 (BAL) | +0.960B | +0.962B | +0.002B | +0.18% |
| E1VFVN30 (VN30) | +25.000B | +25.296B | +0.296B | +1.18% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -0.442B |
| + ETF net cash flow + MTM | +0.587B |
| + Stock unrealized MTM | +0.000B (cost 0.000B → realized would be +0.000B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +6.2400B |
| + Stock sells (sell_amount - fee in) | +5.7978B |
| - ETF buys (buy_amount + fee out) | +65.9924B |
| + ETF sells (sell_amount - fee in) | +16.3960B |
| = Expected end cash (from transactions only) | -0.0386B |
| Actual end cash (from logs) | -0.0402B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0016B** |
| Actual end ETF balance (still in cash_etf) | +50.1836B |
| Open stock positions mark value | +0.0000B |
| = **Final NAV (cash + ETF + open stocks)** | **+50.1434B** |

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
| Stock buys — share cost | +6.2307B |
| Stock buys — fee | +0.0093B |
| Stock sells — gross | +5.8153B |
| Stock sells — fee+tax | +0.0174B |
| **Net stock realized P&L** | **-0.4422B** |
| ETF buys — share cost | +65.8936B |
| ETF buys — friction | +0.0988B |
| ETF sells — gross | +16.4207B |
| ETF sells — friction | +0.0246B |
| **Net ETF cash flow** | **-49.5964B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| E1VFVN30 (BAL) | +9.957B | +10.283B | +0.327B | +3.28% |
| E1VFVN30 (BAL) | +0.134B | +0.127B | -0.007B | -5.21% |
| E1VFVN30 (BAL) | +2.129B | +2.018B | -0.111B | -5.21% |
| E1VFVN30 (BAL) | +0.514B | +0.477B | -0.038B | -7.31% |
| E1VFVN30 (BAL) | +2.166B | +2.026B | -0.140B | -6.46% |
| E1VFVN30 (BAL) | +0.537B | +0.504B | -0.032B | -6.00% |
| E1VFVN30 (BAL) | +2.460B | +2.331B | -0.130B | -5.27% |
| E1VFVN30 (BAL) | +1.146B | +1.081B | -0.065B | -5.66% |
| E1VFVN30 (BAL) | +0.507B | +0.482B | -0.025B | -4.90% |
| E1VFVN30 (BAL) | +2.076B | +1.983B | -0.093B | -4.49% |
| E1VFVN30 (BAL) | +0.630B | +0.604B | -0.026B | -4.20% |
| E1VFVN30 (BAL) | +2.634B | +2.505B | -0.129B | -4.90% |
| E1VFVN30 (BAL) | +0.960B | +0.982B | +0.022B | +2.26% |
| E1VFVN30 (VN30) | +25.000B | +25.820B | +0.820B | +3.28% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -0.442B |
| + ETF net cash flow + MTM | +1.627B |
| + Stock unrealized MTM | +0.000B (cost 0.000B → realized would be +0.000B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +6.2400B |
| + Stock sells (sell_amount - fee in) | +5.7978B |
| - ETF buys (buy_amount + fee out) | +65.9924B |
| + ETF sells (sell_amount - fee in) | +16.3960B |
| = Expected end cash (from transactions only) | -0.0386B |
| Actual end cash (from logs) | -0.0402B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0016B** |
| Actual end ETF balance (still in cash_etf) | +51.2231B |
| Open stock positions mark value | +0.0000B |
| = **Final NAV (cash + ETF + open stocks)** | **+51.1829B** |

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
| Stock buys — share cost | +6.2307B |
| Stock buys — fee | +0.0093B |
| Stock sells — gross | +5.8153B |
| Stock sells — fee+tax | +0.0174B |
| **Net stock realized P&L** | **-0.4422B** |
| ETF buys — share cost | +65.8936B |
| ETF buys — friction | +0.0988B |
| ETF sells — gross | +16.4207B |
| ETF sells — friction | +0.0246B |
| **Net ETF cash flow** | **-49.5964B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| E1VFVN30 (BAL) | +9.957B | +10.193B | +0.236B | +2.37% |
| E1VFVN30 (BAL) | +0.134B | +0.126B | -0.008B | -6.05% |
| E1VFVN30 (BAL) | +2.129B | +2.001B | -0.129B | -6.05% |
| E1VFVN30 (BAL) | +0.514B | +0.472B | -0.042B | -8.12% |
| E1VFVN30 (BAL) | +2.166B | +2.008B | -0.158B | -7.29% |
| E1VFVN30 (BAL) | +0.537B | +0.500B | -0.037B | -6.83% |
| E1VFVN30 (BAL) | +2.460B | +2.310B | -0.150B | -6.10% |
| E1VFVN30 (BAL) | +1.146B | +1.071B | -0.074B | -6.49% |
| E1VFVN30 (BAL) | +0.507B | +0.478B | -0.029B | -5.73% |
| E1VFVN30 (BAL) | +2.076B | +1.966B | -0.111B | -5.34% |
| E1VFVN30 (BAL) | +0.630B | +0.598B | -0.032B | -5.04% |
| E1VFVN30 (BAL) | +2.634B | +2.483B | -0.151B | -5.73% |
| E1VFVN30 (BAL) | +0.960B | +0.973B | +0.013B | +1.35% |
| E1VFVN30 (VN30) | +25.000B | +25.592B | +0.592B | +2.37% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -0.442B |
| + ETF net cash flow + MTM | +1.175B |
| + Stock unrealized MTM | +0.000B (cost 0.000B → realized would be +0.000B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +6.2400B |
| + Stock sells (sell_amount - fee in) | +5.7978B |
| - ETF buys (buy_amount + fee out) | +65.9924B |
| + ETF sells (sell_amount - fee in) | +16.3960B |
| = Expected end cash (from transactions only) | -0.0386B |
| Actual end cash (from logs) | -0.0402B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0016B** |
| Actual end ETF balance (still in cash_etf) | +50.7712B |
| Open stock positions mark value | +0.0000B |
| = **Final NAV (cash + ETF + open stocks)** | **+50.7309B** |

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
| Stock buys — share cost | +6.2307B |
| Stock buys — fee | +0.0093B |
| Stock sells — gross | +5.8153B |
| Stock sells — fee+tax | +0.0174B |
| **Net stock realized P&L** | **-0.4422B** |
| ETF buys — share cost | +65.8936B |
| ETF buys — friction | +0.0988B |
| ETF sells — gross | +16.4207B |
| ETF sells — friction | +0.0246B |
| **Net ETF cash flow** | **-49.5964B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| E1VFVN30 (BAL) | +9.957B | +10.404B | +0.448B | +4.50% |
| E1VFVN30 (BAL) | +0.134B | +0.128B | -0.005B | -4.10% |
| E1VFVN30 (BAL) | +2.129B | +2.042B | -0.087B | -4.10% |
| E1VFVN30 (BAL) | +0.514B | +0.482B | -0.032B | -6.22% |
| E1VFVN30 (BAL) | +2.166B | +2.050B | -0.116B | -5.36% |
| E1VFVN30 (BAL) | +0.537B | +0.510B | -0.026B | -4.89% |
| E1VFVN30 (BAL) | +2.460B | +2.358B | -0.102B | -4.15% |
| E1VFVN30 (BAL) | +1.146B | +1.093B | -0.052B | -4.55% |
| E1VFVN30 (BAL) | +0.507B | +0.487B | -0.019B | -3.78% |
| E1VFVN30 (BAL) | +2.076B | +2.006B | -0.070B | -3.37% |
| E1VFVN30 (BAL) | +0.630B | +0.611B | -0.019B | -3.07% |
| E1VFVN30 (BAL) | +2.634B | +2.535B | -0.099B | -3.78% |
| E1VFVN30 (BAL) | +0.960B | +0.993B | +0.033B | +3.46% |
| E1VFVN30 (VN30) | +25.000B | +26.124B | +1.124B | +4.50% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -0.442B |
| + ETF net cash flow + MTM | +2.229B |
| + Stock unrealized MTM | +0.000B (cost 0.000B → realized would be +0.000B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +6.2400B |
| + Stock sells (sell_amount - fee in) | +5.7978B |
| - ETF buys (buy_amount + fee out) | +65.9924B |
| + ETF sells (sell_amount - fee in) | +16.3960B |
| = Expected end cash (from transactions only) | -0.0386B |
| Actual end cash (from logs) | -0.0402B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0016B** |
| Actual end ETF balance (still in cash_etf) | +51.8258B |
| Open stock positions mark value | +0.0000B |
| = **Final NAV (cash + ETF + open stocks)** | **+51.7855B** |

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
| Stock buys — share cost | +6.2307B |
| Stock buys — fee | +0.0093B |
| Stock sells — gross | +5.8153B |
| Stock sells — fee+tax | +0.0174B |
| **Net stock realized P&L** | **-0.4422B** |
| ETF buys — share cost | +65.8936B |
| ETF buys — friction | +0.0988B |
| ETF sells — gross | +16.4207B |
| ETF sells — friction | +0.0246B |
| **Net ETF cash flow** | **-49.5964B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| E1VFVN30 (BAL) | +9.957B | +10.444B | +0.487B | +4.89% |
| E1VFVN30 (BAL) | +0.134B | +0.129B | -0.005B | -3.74% |
| E1VFVN30 (BAL) | +2.129B | +2.050B | -0.080B | -3.74% |
| E1VFVN30 (BAL) | +0.514B | +0.484B | -0.030B | -5.86% |
| E1VFVN30 (BAL) | +2.166B | +2.058B | -0.108B | -5.01% |
| E1VFVN30 (BAL) | +0.537B | +0.512B | -0.024B | -4.53% |
| E1VFVN30 (BAL) | +2.460B | +2.367B | -0.093B | -3.79% |
| E1VFVN30 (BAL) | +1.146B | +1.098B | -0.048B | -4.19% |
| E1VFVN30 (BAL) | +0.507B | +0.489B | -0.017B | -3.41% |
| E1VFVN30 (BAL) | +2.076B | +2.014B | -0.062B | -3.01% |
| E1VFVN30 (BAL) | +0.630B | +0.613B | -0.017B | -2.70% |
| E1VFVN30 (BAL) | +2.634B | +2.544B | -0.090B | -3.41% |
| E1VFVN30 (BAL) | +0.960B | +0.997B | +0.037B | +3.85% |
| E1VFVN30 (VN30) | +25.000B | +26.223B | +1.223B | +4.89% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -0.442B |
| + ETF net cash flow + MTM | +2.425B |
| + Stock unrealized MTM | +0.000B (cost 0.000B → realized would be +0.000B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +6.2400B |
| + Stock sells (sell_amount - fee in) | +5.7978B |
| - ETF buys (buy_amount + fee out) | +65.9924B |
| + ETF sells (sell_amount - fee in) | +16.3960B |
| = Expected end cash (from transactions only) | -0.0386B |
| Actual end cash (from logs) | -0.0402B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0016B** |
| Actual end ETF balance (still in cash_etf) | +52.0216B |
| Open stock positions mark value | +0.0000B |
| = **Final NAV (cash + ETF + open stocks)** | **+51.9814B** |

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
| Stock buys — share cost | +6.2307B |
| Stock buys — fee | +0.0093B |
| Stock sells — gross | +5.8153B |
| Stock sells — fee+tax | +0.0174B |
| **Net stock realized P&L** | **-0.4422B** |
| ETF buys — share cost | +65.8936B |
| ETF buys — friction | +0.0988B |
| ETF sells — gross | +16.4207B |
| ETF sells — friction | +0.0246B |
| **Net ETF cash flow** | **-49.5964B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| E1VFVN30 (BAL) | +9.957B | +10.404B | +0.448B | +4.50% |
| E1VFVN30 (BAL) | +0.134B | +0.128B | -0.005B | -4.10% |
| E1VFVN30 (BAL) | +2.129B | +2.042B | -0.087B | -4.10% |
| E1VFVN30 (BAL) | +0.514B | +0.482B | -0.032B | -6.22% |
| E1VFVN30 (BAL) | +2.166B | +2.050B | -0.116B | -5.36% |
| E1VFVN30 (BAL) | +0.537B | +0.510B | -0.026B | -4.89% |
| E1VFVN30 (BAL) | +2.460B | +2.358B | -0.102B | -4.15% |
| E1VFVN30 (BAL) | +1.146B | +1.093B | -0.052B | -4.55% |
| E1VFVN30 (BAL) | +0.507B | +0.487B | -0.019B | -3.78% |
| E1VFVN30 (BAL) | +2.076B | +2.006B | -0.070B | -3.37% |
| E1VFVN30 (BAL) | +0.630B | +0.611B | -0.019B | -3.07% |
| E1VFVN30 (BAL) | +2.634B | +2.535B | -0.099B | -3.78% |
| E1VFVN30 (BAL) | +0.960B | +0.993B | +0.033B | +3.46% |
| E1VFVN30 (VN30) | +25.000B | +26.124B | +1.124B | +4.50% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -0.442B |
| + ETF net cash flow + MTM | +2.229B |
| + Stock unrealized MTM | +0.000B (cost 0.000B → realized would be +0.000B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +6.2400B |
| + Stock sells (sell_amount - fee in) | +5.7978B |
| - ETF buys (buy_amount + fee out) | +65.9924B |
| + ETF sells (sell_amount - fee in) | +16.3960B |
| = Expected end cash (from transactions only) | -0.0386B |
| Actual end cash (from logs) | -0.0403B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0017B** |
| Actual end ETF balance (still in cash_etf) | +51.8258B |
| Open stock positions mark value | +0.0000B |
| = **Final NAV (cash + ETF + open stocks)** | **+51.7855B** |

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
| Stock buys — share cost | +6.2307B |
| Stock buys — fee | +0.0093B |
| Stock sells — gross | +5.8153B |
| Stock sells — fee+tax | +0.0174B |
| **Net stock realized P&L** | **-0.4422B** |
| ETF buys — share cost | +65.8936B |
| ETF buys — friction | +0.0988B |
| ETF sells — gross | +16.4207B |
| ETF sells — friction | +0.0246B |
| **Net ETF cash flow** | **-49.5964B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| E1VFVN30 (BAL) | +9.957B | +10.371B | +0.414B | +4.16% |
| E1VFVN30 (BAL) | +0.134B | +0.128B | -0.006B | -4.40% |
| E1VFVN30 (BAL) | +2.129B | +2.036B | -0.094B | -4.40% |
| E1VFVN30 (BAL) | +0.514B | +0.481B | -0.034B | -6.52% |
| E1VFVN30 (BAL) | +2.166B | +2.044B | -0.123B | -5.67% |
| E1VFVN30 (BAL) | +0.537B | +0.509B | -0.028B | -5.20% |
| E1VFVN30 (BAL) | +2.460B | +2.351B | -0.110B | -4.46% |
| E1VFVN30 (BAL) | +1.146B | +1.090B | -0.056B | -4.86% |
| E1VFVN30 (BAL) | +0.507B | +0.486B | -0.021B | -4.08% |
| E1VFVN30 (BAL) | +2.076B | +2.000B | -0.076B | -3.68% |
| E1VFVN30 (BAL) | +0.630B | +0.609B | -0.021B | -3.38% |
| E1VFVN30 (BAL) | +2.634B | +2.526B | -0.108B | -4.08% |
| E1VFVN30 (BAL) | +0.960B | +0.990B | +0.030B | +3.13% |
| E1VFVN30 (VN30) | +25.000B | +26.040B | +1.040B | +4.16% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -0.442B |
| + ETF net cash flow + MTM | +2.064B |
| + Stock unrealized MTM | +0.000B (cost 0.000B → realized would be +0.000B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +6.2400B |
| + Stock sells (sell_amount - fee in) | +5.7978B |
| - ETF buys (buy_amount + fee out) | +65.9924B |
| + ETF sells (sell_amount - fee in) | +16.3960B |
| = Expected end cash (from transactions only) | -0.0386B |
| Actual end cash (from logs) | -0.0403B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0017B** |
| Actual end ETF balance (still in cash_etf) | +51.6600B |
| Open stock positions mark value | +0.0000B |
| = **Final NAV (cash + ETF + open stocks)** | **+51.6198B** |

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
| Stock buys — share cost | +6.2307B |
| Stock buys — fee | +0.0093B |
| Stock sells — gross | +5.8153B |
| Stock sells — fee+tax | +0.0174B |
| **Net stock realized P&L** | **-0.4422B** |
| ETF buys — share cost | +65.8936B |
| ETF buys — friction | +0.0988B |
| ETF sells — gross | +16.4207B |
| ETF sells — friction | +0.0246B |
| **Net ETF cash flow** | **-49.5964B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| E1VFVN30 (BAL) | +9.957B | +10.359B | +0.402B | +4.04% |
| E1VFVN30 (BAL) | +0.134B | +0.128B | -0.006B | -4.52% |
| E1VFVN30 (BAL) | +2.129B | +2.033B | -0.096B | -4.52% |
| E1VFVN30 (BAL) | +0.514B | +0.480B | -0.034B | -6.62% |
| E1VFVN30 (BAL) | +2.166B | +2.041B | -0.125B | -5.78% |
| E1VFVN30 (BAL) | +0.537B | +0.508B | -0.028B | -5.31% |
| E1VFVN30 (BAL) | +2.460B | +2.348B | -0.112B | -4.57% |
| E1VFVN30 (BAL) | +1.146B | +1.089B | -0.057B | -4.97% |
| E1VFVN30 (BAL) | +0.507B | +0.485B | -0.021B | -4.20% |
| E1VFVN30 (BAL) | +2.076B | +1.998B | -0.079B | -3.79% |
| E1VFVN30 (BAL) | +0.630B | +0.608B | -0.022B | -3.49% |
| E1VFVN30 (BAL) | +2.634B | +2.523B | -0.111B | -4.20% |
| E1VFVN30 (BAL) | +0.960B | +0.989B | +0.029B | +3.01% |
| E1VFVN30 (VN30) | +25.000B | +26.010B | +1.010B | +4.04% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -0.442B |
| + ETF net cash flow + MTM | +2.003B |
| + Stock unrealized MTM | +0.000B (cost 0.000B → realized would be +0.000B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +6.2400B |
| + Stock sells (sell_amount - fee in) | +5.7978B |
| - ETF buys (buy_amount + fee out) | +65.9924B |
| + ETF sells (sell_amount - fee in) | +16.3960B |
| = Expected end cash (from transactions only) | -0.0386B |
| Actual end cash (from logs) | -0.0403B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0017B** |
| Actual end ETF balance (still in cash_etf) | +51.5998B |
| Open stock positions mark value | +0.0000B |
| = **Final NAV (cash + ETF + open stocks)** | **+51.5595B** |

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
| Stock buys — share cost | +6.2307B |
| Stock buys — fee | +0.0093B |
| Stock sells — gross | +5.8153B |
| Stock sells — fee+tax | +0.0174B |
| **Net stock realized P&L** | **-0.4422B** |
| ETF buys — share cost | +65.8936B |
| ETF buys — friction | +0.0988B |
| ETF sells — gross | +16.4207B |
| ETF sells — friction | +0.0246B |
| **Net ETF cash flow** | **-49.5964B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| E1VFVN30 (BAL) | +9.957B | +10.432B | +0.475B | +4.77% |
| E1VFVN30 (BAL) | +0.134B | +0.129B | -0.005B | -3.85% |
| E1VFVN30 (BAL) | +2.129B | +2.047B | -0.082B | -3.85% |
| E1VFVN30 (BAL) | +0.514B | +0.483B | -0.031B | -5.97% |
| E1VFVN30 (BAL) | +2.166B | +2.056B | -0.111B | -5.12% |
| E1VFVN30 (BAL) | +0.537B | +0.512B | -0.025B | -4.64% |
| E1VFVN30 (BAL) | +2.460B | +2.364B | -0.096B | -3.90% |
| E1VFVN30 (BAL) | +1.146B | +1.096B | -0.049B | -4.30% |
| E1VFVN30 (BAL) | +0.507B | +0.489B | -0.018B | -3.52% |
| E1VFVN30 (BAL) | +2.076B | +2.012B | -0.065B | -3.12% |
| E1VFVN30 (BAL) | +0.630B | +0.612B | -0.018B | -2.82% |
| E1VFVN30 (BAL) | +2.634B | +2.541B | -0.093B | -3.52% |
| E1VFVN30 (BAL) | +0.960B | +0.996B | +0.036B | +3.73% |
| E1VFVN30 (VN30) | +25.000B | +26.192B | +1.192B | +4.77% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -0.442B |
| + ETF net cash flow + MTM | +2.365B |
| + Stock unrealized MTM | +0.000B (cost 0.000B → realized would be +0.000B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +6.2400B |
| + Stock sells (sell_amount - fee in) | +5.7978B |
| - ETF buys (buy_amount + fee out) | +65.9924B |
| + ETF sells (sell_amount - fee in) | +16.3960B |
| = Expected end cash (from transactions only) | -0.0386B |
| Actual end cash (from logs) | -0.0403B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0017B** |
| Actual end ETF balance (still in cash_etf) | +51.9613B |
| Open stock positions mark value | +0.0000B |
| = **Final NAV (cash + ETF + open stocks)** | **+51.9210B** |

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
| Stock buys — share cost | +6.2307B |
| Stock buys — fee | +0.0093B |
| Stock sells — gross | +5.8153B |
| Stock sells — fee+tax | +0.0174B |
| **Net stock realized P&L** | **-0.4422B** |
| ETF buys — share cost | +65.8936B |
| ETF buys — friction | +0.0988B |
| ETF sells — gross | +16.4207B |
| ETF sells — friction | +0.0246B |
| **Net ETF cash flow** | **-49.5964B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| E1VFVN30 (BAL) | +9.957B | +10.435B | +0.478B | +4.80% |
| E1VFVN30 (BAL) | +0.134B | +0.129B | -0.005B | -3.82% |
| E1VFVN30 (BAL) | +2.129B | +2.048B | -0.081B | -3.82% |
| E1VFVN30 (BAL) | +0.514B | +0.484B | -0.031B | -5.94% |
| E1VFVN30 (BAL) | +2.166B | +2.056B | -0.110B | -5.09% |
| E1VFVN30 (BAL) | +0.537B | +0.512B | -0.025B | -4.62% |
| E1VFVN30 (BAL) | +2.460B | +2.365B | -0.095B | -3.87% |
| E1VFVN30 (BAL) | +1.146B | +1.097B | -0.049B | -4.27% |
| E1VFVN30 (BAL) | +0.507B | +0.489B | -0.018B | -3.50% |
| E1VFVN30 (BAL) | +2.076B | +2.012B | -0.064B | -3.09% |
| E1VFVN30 (BAL) | +0.630B | +0.612B | -0.018B | -2.79% |
| E1VFVN30 (BAL) | +2.634B | +2.542B | -0.092B | -3.50% |
| E1VFVN30 (BAL) | +0.960B | +0.996B | +0.036B | +3.76% |
| E1VFVN30 (VN30) | +25.000B | +26.200B | +1.200B | +4.80% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -0.442B |
| + ETF net cash flow + MTM | +2.380B |
| + Stock unrealized MTM | +0.000B (cost 0.000B → realized would be +0.000B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +6.2400B |
| + Stock sells (sell_amount - fee in) | +5.7978B |
| - ETF buys (buy_amount + fee out) | +65.9924B |
| + ETF sells (sell_amount - fee in) | +16.3960B |
| = Expected end cash (from transactions only) | -0.0386B |
| Actual end cash (from logs) | -0.0403B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0017B** |
| Actual end ETF balance (still in cash_etf) | +51.9764B |
| Open stock positions mark value | +0.0000B |
| = **Final NAV (cash + ETF + open stocks)** | **+51.9361B** |

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
| Stock buys — share cost | +6.2307B |
| Stock buys — fee | +0.0093B |
| Stock sells — gross | +5.8153B |
| Stock sells — fee+tax | +0.0174B |
| **Net stock realized P&L** | **-0.4422B** |
| ETF buys — share cost | +65.8936B |
| ETF buys — friction | +0.0988B |
| ETF sells — gross | +16.4207B |
| ETF sells — friction | +0.0246B |
| **Net ETF cash flow** | **-49.5964B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| E1VFVN30 (BAL) | +9.957B | +10.498B | +0.541B | +5.44% |
| E1VFVN30 (BAL) | +0.134B | +0.130B | -0.004B | -3.23% |
| E1VFVN30 (BAL) | +2.129B | +2.060B | -0.069B | -3.23% |
| E1VFVN30 (BAL) | +0.514B | +0.487B | -0.028B | -5.37% |
| E1VFVN30 (BAL) | +2.166B | +2.069B | -0.098B | -4.51% |
| E1VFVN30 (BAL) | +0.537B | +0.515B | -0.022B | -4.04% |
| E1VFVN30 (BAL) | +2.460B | +2.379B | -0.081B | -3.29% |
| E1VFVN30 (BAL) | +1.146B | +1.103B | -0.042B | -3.69% |
| E1VFVN30 (BAL) | +0.507B | +0.492B | -0.015B | -2.91% |
| E1VFVN30 (BAL) | +2.076B | +2.025B | -0.052B | -2.50% |
| E1VFVN30 (BAL) | +0.630B | +0.616B | -0.014B | -2.20% |
| E1VFVN30 (BAL) | +2.634B | +2.557B | -0.077B | -2.91% |
| E1VFVN30 (BAL) | +0.960B | +1.002B | +0.042B | +4.39% |
| E1VFVN30 (VN30) | +25.000B | +26.359B | +1.359B | +5.44% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -0.442B |
| + ETF net cash flow + MTM | +2.696B |
| + Stock unrealized MTM | +0.000B (cost 0.000B → realized would be +0.000B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +6.2400B |
| + Stock sells (sell_amount - fee in) | +5.7978B |
| - ETF buys (buy_amount + fee out) | +65.9924B |
| + ETF sells (sell_amount - fee in) | +16.3960B |
| = Expected end cash (from transactions only) | -0.0386B |
| Actual end cash (from logs) | -0.0403B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0017B** |
| Actual end ETF balance (still in cash_etf) | +52.2928B |
| Open stock positions mark value | +0.0000B |
| = **Final NAV (cash + ETF + open stocks)** | **+52.2524B** |

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
| Stock buys — share cost | +6.2307B |
| Stock buys — fee | +0.0093B |
| Stock sells — gross | +5.8153B |
| Stock sells — fee+tax | +0.0174B |
| **Net stock realized P&L** | **-0.4422B** |
| ETF buys — share cost | +65.8936B |
| ETF buys — friction | +0.0988B |
| ETF sells — gross | +16.4207B |
| ETF sells — friction | +0.0246B |
| **Net ETF cash flow** | **-49.5964B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| E1VFVN30 (BAL) | +9.957B | +10.447B | +0.490B | +4.92% |
| E1VFVN30 (BAL) | +0.134B | +0.129B | -0.005B | -3.71% |
| E1VFVN30 (BAL) | +2.129B | +2.050B | -0.079B | -3.71% |
| E1VFVN30 (BAL) | +0.514B | +0.484B | -0.030B | -5.83% |
| E1VFVN30 (BAL) | +2.166B | +2.059B | -0.108B | -4.98% |
| E1VFVN30 (BAL) | +0.537B | +0.512B | -0.024B | -4.51% |
| E1VFVN30 (BAL) | +2.460B | +2.368B | -0.093B | -3.76% |
| E1VFVN30 (BAL) | +1.146B | +1.098B | -0.048B | -4.16% |
| E1VFVN30 (BAL) | +0.507B | +0.489B | -0.017B | -3.38% |
| E1VFVN30 (BAL) | +2.076B | +2.015B | -0.062B | -2.98% |
| E1VFVN30 (BAL) | +0.630B | +0.613B | -0.017B | -2.68% |
| E1VFVN30 (BAL) | +2.634B | +2.545B | -0.089B | -3.38% |
| E1VFVN30 (BAL) | +0.960B | +0.997B | +0.037B | +3.88% |
| E1VFVN30 (VN30) | +25.000B | +26.230B | +1.230B | +4.92% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -0.442B |
| + ETF net cash flow + MTM | +2.440B |
| + Stock unrealized MTM | +0.000B (cost 0.000B → realized would be +0.000B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +6.2400B |
| + Stock sells (sell_amount - fee in) | +5.7978B |
| - ETF buys (buy_amount + fee out) | +65.9924B |
| + ETF sells (sell_amount - fee in) | +16.3960B |
| = Expected end cash (from transactions only) | -0.0386B |
| Actual end cash (from logs) | -0.0404B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0017B** |
| Actual end ETF balance (still in cash_etf) | +52.0367B |
| Open stock positions mark value | +0.0000B |
| = **Final NAV (cash + ETF + open stocks)** | **+51.9963B** |

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
| Stock buys — share cost | +6.2307B |
| Stock buys — fee | +0.0093B |
| Stock sells — gross | +5.8153B |
| Stock sells — fee+tax | +0.0174B |
| **Net stock realized P&L** | **-0.4422B** |
| ETF buys — share cost | +65.8936B |
| ETF buys — friction | +0.0988B |
| ETF sells — gross | +16.4207B |
| ETF sells — friction | +0.0246B |
| **Net ETF cash flow** | **-49.5964B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| E1VFVN30 (BAL) | +9.957B | +10.253B | +0.296B | +2.98% |
| E1VFVN30 (BAL) | +0.134B | +0.127B | -0.007B | -5.49% |
| E1VFVN30 (BAL) | +2.129B | +2.012B | -0.117B | -5.49% |
| E1VFVN30 (BAL) | +0.514B | +0.475B | -0.039B | -7.58% |
| E1VFVN30 (BAL) | +2.166B | +2.020B | -0.146B | -6.74% |
| E1VFVN30 (BAL) | +0.537B | +0.503B | -0.034B | -6.28% |
| E1VFVN30 (BAL) | +2.460B | +2.324B | -0.136B | -5.54% |
| E1VFVN30 (BAL) | +1.146B | +1.078B | -0.068B | -5.94% |
| E1VFVN30 (BAL) | +0.507B | +0.480B | -0.026B | -5.17% |
| E1VFVN30 (BAL) | +2.076B | +1.977B | -0.099B | -4.78% |
| E1VFVN30 (BAL) | +0.630B | +0.602B | -0.028B | -4.48% |
| E1VFVN30 (BAL) | +2.634B | +2.498B | -0.136B | -5.17% |
| E1VFVN30 (BAL) | +0.960B | +0.979B | +0.019B | +1.95% |
| E1VFVN30 (VN30) | +25.000B | +25.744B | +0.744B | +2.98% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -0.442B |
| + ETF net cash flow + MTM | +1.476B |
| + Stock unrealized MTM | +0.000B (cost 0.000B → realized would be +0.000B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +6.2400B |
| + Stock sells (sell_amount - fee in) | +5.7978B |
| - ETF buys (buy_amount + fee out) | +65.9924B |
| + ETF sells (sell_amount - fee in) | +16.3960B |
| = Expected end cash (from transactions only) | -0.0386B |
| Actual end cash (from logs) | -0.0404B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0018B** |
| Actual end ETF balance (still in cash_etf) | +51.0725B |
| Open stock positions mark value | +0.0000B |
| = **Final NAV (cash + ETF + open stocks)** | **+51.0321B** |

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
| Stock buys — share cost | +6.2307B |
| Stock buys — fee | +0.0093B |
| Stock sells — gross | +5.8153B |
| Stock sells — fee+tax | +0.0174B |
| **Net stock realized P&L** | **-0.4422B** |
| ETF buys — share cost | +65.8936B |
| ETF buys — friction | +0.0988B |
| ETF sells — gross | +16.4207B |
| ETF sells — friction | +0.0246B |
| **Net ETF cash flow** | **-49.5964B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| E1VFVN30 (BAL) | +9.957B | +10.223B | +0.266B | +2.67% |
| E1VFVN30 (BAL) | +0.134B | +0.126B | -0.008B | -5.77% |
| E1VFVN30 (BAL) | +2.129B | +2.006B | -0.123B | -5.77% |
| E1VFVN30 (BAL) | +0.514B | +0.474B | -0.040B | -7.85% |
| E1VFVN30 (BAL) | +2.166B | +2.014B | -0.152B | -7.02% |
| E1VFVN30 (BAL) | +0.537B | +0.501B | -0.035B | -6.55% |
| E1VFVN30 (BAL) | +2.460B | +2.317B | -0.143B | -5.82% |
| E1VFVN30 (BAL) | +1.146B | +1.074B | -0.071B | -6.22% |
| E1VFVN30 (BAL) | +0.507B | +0.479B | -0.028B | -5.45% |
| E1VFVN30 (BAL) | +2.076B | +1.971B | -0.105B | -5.06% |
| E1VFVN30 (BAL) | +0.630B | +0.600B | -0.030B | -4.76% |
| E1VFVN30 (BAL) | +2.634B | +2.490B | -0.144B | -5.45% |
| E1VFVN30 (BAL) | +0.960B | +0.976B | +0.016B | +1.65% |
| E1VFVN30 (VN30) | +25.000B | +25.668B | +0.668B | +2.67% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -0.442B |
| + ETF net cash flow + MTM | +1.325B |
| + Stock unrealized MTM | +0.000B (cost 0.000B → realized would be +0.000B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +6.2400B |
| + Stock sells (sell_amount - fee in) | +5.7978B |
| - ETF buys (buy_amount + fee out) | +65.9924B |
| + ETF sells (sell_amount - fee in) | +16.3960B |
| = Expected end cash (from transactions only) | -0.0386B |
| Actual end cash (from logs) | -0.0404B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0018B** |
| Actual end ETF balance (still in cash_etf) | +50.9218B |
| Open stock positions mark value | +0.0000B |
| = **Final NAV (cash + ETF + open stocks)** | **+50.8814B** |

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
| Stock buys — share cost | +6.2307B |
| Stock buys — fee | +0.0093B |
| Stock sells — gross | +5.8153B |
| Stock sells — fee+tax | +0.0174B |
| **Net stock realized P&L** | **-0.4422B** |
| ETF buys — share cost | +65.8936B |
| ETF buys — friction | +0.0988B |
| ETF sells — gross | +16.4207B |
| ETF sells — friction | +0.0246B |
| **Net ETF cash flow** | **-49.5964B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| E1VFVN30 (BAL) | +9.957B | +10.223B | +0.266B | +2.67% |
| E1VFVN30 (BAL) | +0.134B | +0.126B | -0.008B | -5.77% |
| E1VFVN30 (BAL) | +2.129B | +2.006B | -0.123B | -5.77% |
| E1VFVN30 (BAL) | +0.514B | +0.474B | -0.040B | -7.85% |
| E1VFVN30 (BAL) | +2.166B | +2.014B | -0.152B | -7.02% |
| E1VFVN30 (BAL) | +0.537B | +0.501B | -0.035B | -6.55% |
| E1VFVN30 (BAL) | +2.460B | +2.317B | -0.143B | -5.82% |
| E1VFVN30 (BAL) | +1.146B | +1.074B | -0.071B | -6.22% |
| E1VFVN30 (BAL) | +0.507B | +0.479B | -0.028B | -5.45% |
| E1VFVN30 (BAL) | +2.076B | +1.971B | -0.105B | -5.06% |
| E1VFVN30 (BAL) | +0.630B | +0.600B | -0.030B | -4.76% |
| E1VFVN30 (BAL) | +2.634B | +2.490B | -0.144B | -5.45% |
| E1VFVN30 (BAL) | +0.960B | +0.976B | +0.016B | +1.65% |
| E1VFVN30 (VN30) | +25.000B | +25.668B | +0.668B | +2.67% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -0.442B |
| + ETF net cash flow + MTM | +1.325B |
| + Stock unrealized MTM | +0.000B (cost 0.000B → realized would be +0.000B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +6.2400B |
| + Stock sells (sell_amount - fee in) | +5.7978B |
| - ETF buys (buy_amount + fee out) | +65.9924B |
| + ETF sells (sell_amount - fee in) | +16.3960B |
| = Expected end cash (from transactions only) | -0.0386B |
| Actual end cash (from logs) | -0.0404B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0018B** |
| Actual end ETF balance (still in cash_etf) | +50.9218B |
| Open stock positions mark value | +0.0000B |
| = **Final NAV (cash + ETF + open stocks)** | **+50.8814B** |

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
| Stock buys — share cost | +6.2307B |
| Stock buys — fee | +0.0093B |
| Stock sells — gross | +5.8153B |
| Stock sells — fee+tax | +0.0174B |
| **Net stock realized P&L** | **-0.4422B** |
| ETF buys — share cost | +65.8936B |
| ETF buys — friction | +0.0988B |
| ETF sells — gross | +16.4207B |
| ETF sells — friction | +0.0246B |
| **Net ETF cash flow** | **-49.5964B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| E1VFVN30 (BAL) | +9.957B | +10.217B | +0.260B | +2.61% |
| E1VFVN30 (BAL) | +0.134B | +0.126B | -0.008B | -5.83% |
| E1VFVN30 (BAL) | +2.129B | +2.005B | -0.124B | -5.83% |
| E1VFVN30 (BAL) | +0.514B | +0.474B | -0.041B | -7.91% |
| E1VFVN30 (BAL) | +2.166B | +2.013B | -0.153B | -7.07% |
| E1VFVN30 (BAL) | +0.537B | +0.501B | -0.035B | -6.61% |
| E1VFVN30 (BAL) | +2.460B | +2.316B | -0.145B | -5.88% |
| E1VFVN30 (BAL) | +1.146B | +1.074B | -0.072B | -6.27% |
| E1VFVN30 (BAL) | +0.507B | +0.479B | -0.028B | -5.51% |
| E1VFVN30 (BAL) | +2.076B | +1.970B | -0.106B | -5.11% |
| E1VFVN30 (BAL) | +0.630B | +0.600B | -0.030B | -4.82% |
| E1VFVN30 (BAL) | +2.634B | +2.489B | -0.145B | -5.51% |
| E1VFVN30 (BAL) | +0.960B | +0.975B | +0.015B | +1.59% |
| E1VFVN30 (VN30) | +25.000B | +25.653B | +0.653B | +2.61% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -0.442B |
| + ETF net cash flow + MTM | +1.295B |
| + Stock unrealized MTM | +0.000B (cost 0.000B → realized would be +0.000B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +6.2400B |
| + Stock sells (sell_amount - fee in) | +5.7978B |
| - ETF buys (buy_amount + fee out) | +65.9924B |
| + ETF sells (sell_amount - fee in) | +16.3960B |
| = Expected end cash (from transactions only) | -0.0386B |
| Actual end cash (from logs) | -0.0404B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0018B** |
| Actual end ETF balance (still in cash_etf) | +50.8917B |
| Open stock positions mark value | +0.0000B |
| = **Final NAV (cash + ETF + open stocks)** | **+50.8513B** |

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
| Stock buys — share cost | +8.7469B |
| Stock buys — fee | +0.0131B |
| Stock sells — gross | +5.8153B |
| Stock sells — fee+tax | +0.0174B |
| **Net stock realized P&L** | **-2.9622B** |
| ETF buys — share cost | +65.8936B |
| ETF buys — friction | +0.0988B |
| ETF sells — gross | +18.9459B |
| ETF sells — friction | +0.0284B |
| **Net ETF cash flow** | **-47.0750B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| VPI (BAL) | +2.520B | +2.516B | -0.004B | +0.00% |
| E1VFVN30 (BAL) | +7.497B | +7.698B | +0.200B | +2.67% |
| E1VFVN30 (BAL) | +0.134B | +0.126B | -0.008B | -5.77% |
| E1VFVN30 (BAL) | +2.129B | +2.006B | -0.123B | -5.77% |
| E1VFVN30 (BAL) | +0.514B | +0.474B | -0.040B | -7.85% |
| E1VFVN30 (BAL) | +2.166B | +2.014B | -0.152B | -7.02% |
| E1VFVN30 (BAL) | +0.537B | +0.501B | -0.035B | -6.55% |
| E1VFVN30 (BAL) | +2.460B | +2.317B | -0.143B | -5.82% |
| E1VFVN30 (BAL) | +1.146B | +1.074B | -0.071B | -6.22% |
| E1VFVN30 (BAL) | +0.507B | +0.479B | -0.028B | -5.45% |
| E1VFVN30 (BAL) | +2.076B | +1.971B | -0.105B | -5.06% |
| E1VFVN30 (BAL) | +0.630B | +0.600B | -0.030B | -4.76% |
| E1VFVN30 (BAL) | +2.634B | +2.490B | -0.144B | -5.45% |
| E1VFVN30 (BAL) | +0.960B | +0.976B | +0.016B | +1.65% |
| E1VFVN30 (VN30) | +25.000B | +25.668B | +0.668B | +2.67% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -2.962B |
| + ETF net cash flow + MTM | +1.322B |
| + Stock unrealized MTM | +2.516B (cost 2.520B → realized would be -0.004B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +8.7600B |
| + Stock sells (sell_amount - fee in) | +5.7978B |
| - ETF buys (buy_amount + fee out) | +65.9924B |
| + ETF sells (sell_amount - fee in) | +18.9175B |
| = Expected end cash (from transactions only) | -0.0372B |
| Actual end cash (from logs) | -0.0390B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0018B** |
| Actual end ETF balance (still in cash_etf) | +48.3966B |
| Open stock positions mark value | +2.5162B |
| = **Final NAV (cash + ETF + open stocks)** | **+50.8738B** |

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
| Stock buys — share cost | +8.7469B |
| Stock buys — fee | +0.0131B |
| Stock sells — gross | +5.8153B |
| Stock sells — fee+tax | +0.0174B |
| **Net stock realized P&L** | **-2.9622B** |
| ETF buys — share cost | +65.8936B |
| ETF buys — friction | +0.0988B |
| ETF sells — gross | +18.9459B |
| ETF sells — friction | +0.0284B |
| **Net ETF cash flow** | **-47.0750B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| VPI (BAL) | +2.520B | +2.613B | +0.093B | +3.83% |
| E1VFVN30 (BAL) | +7.497B | +7.914B | +0.417B | +5.56% |
| E1VFVN30 (BAL) | +0.134B | +0.130B | -0.004B | -3.12% |
| E1VFVN30 (BAL) | +2.129B | +2.063B | -0.066B | -3.12% |
| E1VFVN30 (BAL) | +0.514B | +0.487B | -0.027B | -5.26% |
| E1VFVN30 (BAL) | +2.166B | +2.071B | -0.095B | -4.40% |
| E1VFVN30 (BAL) | +0.537B | +0.516B | -0.021B | -3.93% |
| E1VFVN30 (BAL) | +2.460B | +2.382B | -0.078B | -3.18% |
| E1VFVN30 (BAL) | +1.146B | +1.105B | -0.041B | -3.58% |
| E1VFVN30 (BAL) | +0.507B | +0.492B | -0.014B | -2.80% |
| E1VFVN30 (BAL) | +2.076B | +2.027B | -0.050B | -2.39% |
| E1VFVN30 (BAL) | +0.630B | +0.617B | -0.013B | -2.09% |
| E1VFVN30 (BAL) | +2.634B | +2.560B | -0.074B | -2.80% |
| E1VFVN30 (BAL) | +0.960B | +1.003B | +0.043B | +4.51% |
| E1VFVN30 (VN30) | +25.000B | +26.390B | +1.390B | +5.56% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -2.962B |
| + ETF net cash flow + MTM | +2.682B |
| + Stock unrealized MTM | +2.613B (cost 2.520B → realized would be +0.093B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +8.7600B |
| + Stock sells (sell_amount - fee in) | +5.7978B |
| - ETF buys (buy_amount + fee out) | +65.9924B |
| + ETF sells (sell_amount - fee in) | +18.9175B |
| = Expected end cash (from transactions only) | -0.0372B |
| Actual end cash (from logs) | -0.0390B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0018B** |
| Actual end ETF balance (still in cash_etf) | +49.7569B |
| Open stock positions mark value | +2.6127B |
| = **Final NAV (cash + ETF + open stocks)** | **+52.3305B** |

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
| Stock buys — share cost | +8.7469B |
| Stock buys — fee | +0.0131B |
| Stock sells — gross | +5.8153B |
| Stock sells — fee+tax | +0.0174B |
| **Net stock realized P&L** | **-2.9622B** |
| ETF buys — share cost | +65.8936B |
| ETF buys — friction | +0.0988B |
| ETF sells — gross | +18.9459B |
| ETF sells — friction | +0.0284B |
| **Net ETF cash flow** | **-47.0750B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| VPI (BAL) | +2.520B | +2.593B | +0.073B | +3.04% |
| E1VFVN30 (BAL) | +7.497B | +7.937B | +0.440B | +5.86% |
| E1VFVN30 (BAL) | +0.134B | +0.130B | -0.004B | -2.84% |
| E1VFVN30 (BAL) | +2.129B | +2.069B | -0.061B | -2.84% |
| E1VFVN30 (BAL) | +0.514B | +0.489B | -0.026B | -4.99% |
| E1VFVN30 (BAL) | +2.166B | +2.077B | -0.089B | -4.13% |
| E1VFVN30 (BAL) | +0.537B | +0.517B | -0.020B | -3.65% |
| E1VFVN30 (BAL) | +2.460B | +2.389B | -0.071B | -2.90% |
| E1VFVN30 (BAL) | +1.146B | +1.108B | -0.038B | -3.30% |
| E1VFVN30 (BAL) | +0.507B | +0.494B | -0.013B | -2.52% |
| E1VFVN30 (BAL) | +2.076B | +2.033B | -0.044B | -2.11% |
| E1VFVN30 (BAL) | +0.630B | +0.619B | -0.011B | -1.80% |
| E1VFVN30 (BAL) | +2.634B | +2.568B | -0.066B | -2.52% |
| E1VFVN30 (BAL) | +0.960B | +1.006B | +0.046B | +4.81% |
| E1VFVN30 (VN30) | +25.000B | +26.466B | +1.466B | +5.86% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -2.962B |
| + ETF net cash flow + MTM | +2.825B |
| + Stock unrealized MTM | +2.593B (cost 2.520B → realized would be +0.073B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +8.7600B |
| + Stock sells (sell_amount - fee in) | +5.7978B |
| - ETF buys (buy_amount + fee out) | +65.9924B |
| + ETF sells (sell_amount - fee in) | +18.9175B |
| = Expected end cash (from transactions only) | -0.0372B |
| Actual end cash (from logs) | -0.0390B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0019B** |
| Actual end ETF balance (still in cash_etf) | +49.9001B |
| Open stock positions mark value | +2.5926B |
| = **Final NAV (cash + ETF + open stocks)** | **+52.4536B** |

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
| Stock buys — share cost | +8.7469B |
| Stock buys — fee | +0.0131B |
| Stock sells — gross | +5.8153B |
| Stock sells — fee+tax | +0.0174B |
| **Net stock realized P&L** | **-2.9622B** |
| ETF buys — share cost | +65.8936B |
| ETF buys — friction | +0.0988B |
| ETF sells — gross | +18.9459B |
| ETF sells — friction | +0.0284B |
| **Net ETF cash flow** | **-47.0750B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| VPI (BAL) | +2.520B | +2.617B | +0.097B | +3.99% |
| E1VFVN30 (BAL) | +7.497B | +7.957B | +0.460B | +6.14% |
| E1VFVN30 (BAL) | +0.134B | +0.130B | -0.003B | -2.59% |
| E1VFVN30 (BAL) | +2.129B | +2.074B | -0.055B | -2.59% |
| E1VFVN30 (BAL) | +0.514B | +0.490B | -0.024B | -4.74% |
| E1VFVN30 (BAL) | +2.166B | +2.082B | -0.084B | -3.88% |
| E1VFVN30 (BAL) | +0.537B | +0.518B | -0.018B | -3.40% |
| E1VFVN30 (BAL) | +2.460B | +2.395B | -0.065B | -2.65% |
| E1VFVN30 (BAL) | +1.146B | +1.111B | -0.035B | -3.05% |
| E1VFVN30 (BAL) | +0.507B | +0.495B | -0.011B | -2.27% |
| E1VFVN30 (BAL) | +2.076B | +2.038B | -0.038B | -1.85% |
| E1VFVN30 (BAL) | +0.630B | +0.620B | -0.010B | -1.55% |
| E1VFVN30 (BAL) | +2.634B | +2.574B | -0.060B | -2.27% |
| E1VFVN30 (BAL) | +0.960B | +1.009B | +0.049B | +5.08% |
| E1VFVN30 (VN30) | +25.000B | +26.534B | +1.534B | +6.14% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -2.962B |
| + ETF net cash flow + MTM | +2.954B |
| + Stock unrealized MTM | +2.617B (cost 2.520B → realized would be +0.097B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +8.7600B |
| + Stock sells (sell_amount - fee in) | +5.7978B |
| - ETF buys (buy_amount + fee out) | +65.9924B |
| + ETF sells (sell_amount - fee in) | +18.9175B |
| = Expected end cash (from transactions only) | -0.0372B |
| Actual end cash (from logs) | -0.0390B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0019B** |
| Actual end ETF balance (still in cash_etf) | +50.0289B |
| Open stock positions mark value | +2.6167B |
| = **Final NAV (cash + ETF + open stocks)** | **+52.6066B** |

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
| Stock buys — share cost | +8.7469B |
| Stock buys — fee | +0.0131B |
| Stock sells — gross | +5.8153B |
| Stock sells — fee+tax | +0.0174B |
| **Net stock realized P&L** | **-2.9622B** |
| ETF buys — share cost | +65.8936B |
| ETF buys — friction | +0.0988B |
| ETF sells — gross | +18.9459B |
| ETF sells — friction | +0.0284B |
| **Net ETF cash flow** | **-47.0750B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| VPI (BAL) | +2.520B | +2.725B | +0.205B | +8.31% |
| E1VFVN30 (BAL) | +7.497B | +8.037B | +0.540B | +7.20% |
| E1VFVN30 (BAL) | +0.134B | +0.132B | -0.002B | -1.62% |
| E1VFVN30 (BAL) | +2.129B | +2.095B | -0.034B | -1.62% |
| E1VFVN30 (BAL) | +0.514B | +0.495B | -0.019B | -3.79% |
| E1VFVN30 (BAL) | +2.166B | +2.103B | -0.063B | -2.92% |
| E1VFVN30 (BAL) | +0.537B | +0.524B | -0.013B | -2.43% |
| E1VFVN30 (BAL) | +2.460B | +2.419B | -0.041B | -1.67% |
| E1VFVN30 (BAL) | +1.146B | +1.122B | -0.024B | -2.08% |
| E1VFVN30 (BAL) | +0.507B | +0.500B | -0.007B | -1.29% |
| E1VFVN30 (BAL) | +2.076B | +2.058B | -0.018B | -0.87% |
| E1VFVN30 (BAL) | +0.630B | +0.626B | -0.004B | -0.56% |
| E1VFVN30 (BAL) | +2.634B | +2.600B | -0.034B | -1.29% |
| E1VFVN30 (BAL) | +0.960B | +1.019B | +0.059B | +6.14% |
| E1VFVN30 (VN30) | +25.000B | +26.800B | +1.800B | +7.20% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -2.962B |
| + ETF net cash flow + MTM | +3.455B |
| + Stock unrealized MTM | +2.725B (cost 2.520B → realized would be +0.205B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +8.7600B |
| + Stock sells (sell_amount - fee in) | +5.7978B |
| - ETF buys (buy_amount + fee out) | +65.9924B |
| + ETF sells (sell_amount - fee in) | +18.9175B |
| = Expected end cash (from transactions only) | -0.0372B |
| Actual end cash (from logs) | -0.0390B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0019B** |
| Actual end ETF balance (still in cash_etf) | +50.5301B |
| Open stock positions mark value | +2.7252B |
| = **Final NAV (cash + ETF + open stocks)** | **+53.2162B** |

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
| Stock buys — share cost | +11.3974B |
| Stock buys — fee | +0.0171B |
| Stock sells — gross | +5.8153B |
| Stock sells — fee+tax | +0.0174B |
| **Net stock realized P&L** | **-5.6167B** |
| ETF buys — share cost | +65.8936B |
| ETF buys — friction | +0.0988B |
| ETF sells — gross | +21.6043B |
| ETF sells — friction | +0.0324B |
| **Net ETF cash flow** | **-44.4205B** |

### Open positions at end of period (unrealized)

| Position | Cost basis | Current value | Unrealized P&L | Return |
|---|---|---|---|---|
| VPI (BAL) | +2.520B | +2.713B | +0.193B | +7.83% |
| VIC (BAL) | +2.654B | +2.650B | -0.004B | +0.00% |
| E1VFVN30 (BAL) | +5.032B | +5.426B | +0.394B | +7.84% |
| E1VFVN30 (BAL) | +0.134B | +0.133B | -0.001B | -1.03% |
| E1VFVN30 (BAL) | +2.129B | +2.107B | -0.022B | -1.03% |
| E1VFVN30 (BAL) | +0.514B | +0.498B | -0.017B | -3.22% |
| E1VFVN30 (BAL) | +2.166B | +2.116B | -0.051B | -2.34% |
| E1VFVN30 (BAL) | +0.537B | +0.527B | -0.010B | -1.85% |
| E1VFVN30 (BAL) | +2.460B | +2.434B | -0.027B | -1.09% |
| E1VFVN30 (BAL) | +1.146B | +1.128B | -0.017B | -1.50% |
| E1VFVN30 (BAL) | +0.507B | +0.503B | -0.004B | -0.70% |
| E1VFVN30 (BAL) | +2.076B | +2.071B | -0.006B | -0.28% |
| E1VFVN30 (BAL) | +0.630B | +0.630B | +0.000B | +0.03% |
| E1VFVN30 (BAL) | +2.634B | +2.616B | -0.018B | -0.70% |
| E1VFVN30 (BAL) | +0.960B | +1.025B | +0.065B | +6.77% |
| E1VFVN30 (VN30) | +25.000B | +26.959B | +1.959B | +7.84% |

### Final reconciliation

| Component | Value |
|---|---|
| Initial NAV | +50.000B |
| + Realized P&L from stocks | -5.617B |
| + ETF net cash flow + MTM | +3.752B |
| + Stock unrealized MTM | +5.364B (cost 5.174B → realized would be +0.189B if sold today) |
| Initial NAV | +50.0000B |
| - Stock buys (buy_amount + fee out) | +11.4145B |
| + Stock sells (sell_amount - fee in) | +5.7978B |
| - ETF buys (buy_amount + fee out) | +65.9924B |
| + ETF sells (sell_amount - fee in) | +21.5719B |
| = Expected end cash (from transactions only) | -0.0372B |
| Actual end cash (from logs) | -0.0391B |
| **Diff (ETF appreciation rebalanced into cash)** | **-0.0019B** |
| Actual end ETF balance (still in cash_etf) | +48.1723B |
| Open stock positions mark value | +5.3636B |
| = **Final NAV (cash + ETF + open stocks)** | **+53.4969B** |

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