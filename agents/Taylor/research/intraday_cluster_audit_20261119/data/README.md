# Deal lists for the reviewer (README for the CSV files)

Read together with the report `REVIEW_REPORT.md` (the engine rules, the setup formulas and the method are there).
Created 2026-11-19 by `scripts/export_deals.py`. The script only calls the engine; the engine was not changed.

## Folders

| Folder | Decision window | Universe / engine |
|---|---|---|
| `insample/` | 2023-09-11 .. 2026-04-30 (in-sample, all research was done here) | market-cap top-50 point-in-time list (HOSE names only), realistic L5 stack, total return |
| `holdout/` | 2026-05-01 .. 2026-11-03; NAV valued until 2026-11-06 | same, with the holdout quarter lists (2026-06-30, 2026-09-30). Tested ONCE, nothing was tuned on it |

## Files in each folder

| File | Contents |
|---|---|
| `deals_<setup>.csv` | one row = one **candidate** deal of the setup (after the setup's own filters) |
| `summary.csv` | count, mean, median, win rate, mean excess of the rows with `in_stats = 1` (a simple mean, without Newey-West) |
| `book3_positions_1bn.csv` | BOOK-3 portfolio, one full-period run at 1 bn VND (fixed seed 7): one row = one position actually taken |
| `book3_skipped_1bn.csv` | the BOOK-3 candidates that were not taken, with the reason |
| `book3_nav_1bn.csv` | daily NAV of that run |

Setups: `fz-001`, `fz-002`, `c-ceil`, `c-nfloor`, `c-nfloor3`, `c-tamix`, `c-onid`. BOOK-3 = FZ-001 + FZ-002 + C-CEIL
+ C-NFLOOR, 10 slots, VNINDEX MA50 > MA200 gate on all members except C-NFLOOR.

## Important: which rows to use

- **`in_stats = 1`**: the non-overlapping, closed deals with an exit inside the window. These are the deals that the
  per-deal statistics of the report are built on (n, mean, t, win rate...).
  Rule: per symbol, a signal is taken only if its decision session is AFTER the exit session of the previously
  taken deal of the same symbol (one open deal per symbol, no re-entry in the exit session).
- `in_stats = 0`: a candidate that overlaps an earlier deal of the same symbol, OR a deal still open at the end of
  the data (`status = open`, valued at the last bar), OR a deal whose exit falls after the window end. They are
  kept because the portfolio layer may take them (it picks among ALL candidates).
- The per-deal t-statistics of the report use Newey-West standard errors over calendar weeks (lag 3). A naive t
  computed on this file will be too high, because deals bought on the same days are correlated.
- The report's statistics use **`net_ret_total`**.

## Columns of `deals_<setup>.csv`

Prices are RAW VND (the real traded price, on the HOSE tick grid). Times are Asia/Ho_Chi_Minh. Returns are fractions
(0.025 = +2.5%).

| Column | Meaning |
|---|---|
| `setup`, `period` | setup id; `insample` or `holdout` |
| `symbol` | HOSE ticker |
| `signal_day` | D: the session on whose close the setup was true (every input is final after D's closing auction) |
| `decision_ts` | 09:00 of D+1: the moment the buy order is placed |
| `status` | `closed` (exited) or `open` (still held at the end of the data; exit columns = valuation at the last bar) |
| `entry_ts`, `entry_px` | first fill of the deal engine: the 09:15 bar of D+1 = the opening-auction (ATO) price. If that bar is ceiling-locked or has no trade, the next tradable bar of D+1 at its open + 1 tick |
| `tp_px`, `sl_px` | take-profit / stop-loss levels in raw VND (`inf` / `-inf` = none). TP = entry × (1 + 6%) rounded UP to the tick; SL = entry × (1 − 2 × atr_pct) rounded DOWN. Only FZ-001 / FZ-002 have them. The levels are rescaled by the adjustment factor on ex-dates |
| `sellable_from` | 13:00 of session T+2: the earliest moment any exit is checked (VN settlement) |
| `exit_ts`, `exit_px` | exit bar and price (raw VND) |
| `exit_reason` | `tp`: a trade ABOVE the TP (or an open above it); `sl`: a trade at or below SL triggers a conditional sell order that fills at the open of the NEXT tradable bar − 1 tick (never below the floor); `time`: the ATC price of the last holding session; `open`: not exited yet |
| `hold_sessions` | sessions from the entry session to the exit session |
| `ambiguous` | the same 5m bar touched both TP and SL: counted as SL (pessimistic) |
| `gross_ret` | exit_px / entry_px − 1 (raw prices, before costs) |
| `net_ret_cash` | after costs (buy fee 0.03%; sell fee 0.03% + tax 0.1%), raw prices: cash only, **without** dividends / bonus shares |
| `net_ret_total` | the same on prices adjusted by the factor f (entry_px / f_entry, exit_px / f_exit): **includes** cash dividends and bonus shares. **Use this one** |
| `crosses_exdate` | 1 if the hold crosses an ex-rights date (f changed): there `net_ret_cash` and `net_ret_total` differ |
| `f_entry`, `f_exit` | adjustment factor at the entry / exit bar |
| `mae_pre` | lowest low between the entry and `sellable_from` / entry − 1: the loss you could not avoid because of T+2 |
| `mae`, `mfe` | lowest low / highest high during the whole hold / entry − 1 |
| `entry_bar_volume` | shares traded in the entry bar (used by the 5% participation cap in the portfolio) |
| `in_stats` | see above |
| `half` | `h1` = signal before 2025-01-01, `h2` = from 2025-01-01 (the two halves of the in-sample stability check) |
| `brd_sig` | number of universe members on which the SAME setup expression was true on D (FZ-001 / FZ-002 require >= 3) |
| `vni_ma50_gt_ma200_D` | 1 if VNINDEX MA50 > MA200 at the close of D (the market gate; C-CEIL's own filter) |
| `book_gate_pass` | 1 if the deal can enter BOOK-3 under the book gate (gate on, or the setup is exempt: C-NFLOOR / C-NFLOOR3) |
| `market_drift_same_day` | the mean `net_ret_total` of buying EVERY universe member at the ATO of D+1 with the same exit rule: what "the whole market" did |
| `excess_ret` | net_ret_total − market_drift_same_day: the stock-selection edge |
| `close_raw_D`, `ceiling_D`, `floor_D` | raw close, price-band ceiling and floor of D (±7% band) |
| `atr_pct` | Wilder ATR(14) / close on D (scales the stop-loss) |
| `pit_member` | 1 = the stock is in the point-in-time universe on the decision session (always 1 here) |
| setup inputs | the values on D of the variables in the setup formula: FZ-001 `D_RSI` (RSI14, 0..1), `fp_last_hour` (14:30 price / 13:30 price − 1), `fp_close_vwap` (closing price / session VWAP − 1); FZ-002 `D_RSI`, `ix_rv_ratio` (std of 5m returns of D / median of the 20 previous sessions), `ix_bull_div` (1 = new 5-day low with a higher 15m RSI low); C-CEIL `ceil_close`; C-NFLOOR `nflo_close`; C-NFLOOR3 `nflo3_close`; C-TAMIX `ta_mix`, `ta_mix_score`; C-ONID `ta_onid`, `ta_onid_score` (the cross-sectional score the day's top share is picked on) |
| `signal_id` | unique id: `<setup>:<symbol>\|<pattern>:<day>` |

## Columns of `book3_positions_1bn.csv` (portfolio layer)

Starting capital 1 bn VND, 10 slots, each new position budgeted at NAV / 10 (capped by settled cash). The buy order is
worked over the whole session of D+1: each slice fills at most 5% of the slice's volume (ATO auction slice: 5% of the
09:15 one-minute volume; continuous bars: typical price (H+L+C)/3 + 1 tick; the ATC bar: its price). Lots of 100.
Sell proceeds are usable from 13:00 T+2. Simultaneous candidates are ordered by a seeded random key (no setup
priority). A symbol held by one setup blocks the others.

The main columns (the file also carries the deal-engine columns described above, from the candidate that was taken):

| Column | Meaning |
|---|---|
| `setup` | the member that produced the position |
| `entry_px` | AVERAGE raw price of the worked buy order over the session of D+1 (the real fill of the portfolio) |
| `entry_px_deal` | the deal engine's first-fill price (ATO); TP / SL levels are computed from this one |
| `net_ret`, `net_ret_total`, `exit_px`, `exit_reason` | the deal engine's own path (single fill at entry_px_deal); the portfolio's realised result is `ret` / `pnl` below |
| `regime_up` | same as `vni_ma50_gt_ma200_D` |
| `score` | ordering score of simultaneous candidates (0 for every setup here -> the seeded random key decides) |
| `qty_bought` / `buy_cost` | shares bought (lots of 100) / VND paid including the buy fee |
| `cash_after_buy`, `n_open_after_buy` | settled cash and number of open positions right after this buy |
| `qty_sold`, `qty_open` | shares sold / still held at the end (valued at the last close) |
| `sell_kinds` | `exit` = the deal's own exit (TP / SL / time) |
| `last_sell_ts` | time of the last sell fill (a large position can need several bars or sessions) |
| `pnl`, `ret` | VND profit after every cost / return on `buy_cost` (total-return valuation) |

`book3_skipped_1bn.csv`: the same candidate columns (`_tie` = the seeded random ordering key, `_day` = entry day), `reason` = `symbol_held` (the symbol is already held), `slots_full`, `no_cash`,
`reentry_same_session`, `not_filled` / `liquidity` (the 5% participation cap gave less than one lot), `outside_window`.

`book3_nav_1bn.csv`: `date`, `cash`, `positions_value`, `nav`, `n_positions`, `exposure_target`.

## Check against the report (reproduced exactly)

| Period | Setup | Candidates | Deals `in_stats` | Mean `net_ret_total` | Win rate | Mean excess |
|---|---|---|---|---|---|---|
| insample | FZ-001 | 261 | 176 | +2.57% | 74% | +1.17% |
| insample | FZ-002 | 247 | 174 | +3.66% | 75% | +0.50% |
| insample | C-CEIL | 424 | 304 | +1.47% | 52% | +0.96% |
| insample | C-NFLOOR | 52 | 48 | +2.43% | 58% | +1.42% |
| insample | C-NFLOOR3 | 80 | 69 | +2.38% | 54% | +1.57% |
| insample | C-TAMIX | 587 | 164 | +2.30% | 55% | +2.18% |
| insample | C-ONID | 1511 | 256 | +0.95% | 54% | +1.06% |
| holdout | FZ-001 | 95 | 55 | +1.19% | 60% | +0.53% |
| holdout | FZ-002 | 110 | 51 | +0.24% | 57% | +0.53% |
| holdout | C-CEIL | 54 | 39 | −0.30% | 46% | −0.28% |
| holdout | C-NFLOOR | 3 | 3 | +6.82% | 100% | +5.00% |
| holdout | C-NFLOOR3 | 7 | 5 | +5.83% | 80% | +2.27% |
| holdout | C-TAMIX | 16 | 6 | −4.76% | 33% | −1.75% |
| holdout | C-ONID | 145 | 25 | −1.24% | 44% | −0.37% |

BOOK-3 at 1 bn, one full run: in-sample 368 positions, final NAV 1.744 bn (start 1.0 bn); holdout 60 positions
(FZ-001 9, −5.9% average, −52.8 M VND; FZ-002 14, +1.6%, +21.7 M; C-CEIL 37, −0.1%, −4.3 M; C-NFLOOR 0), final NAV
0.968 bn. Holdout skipped candidates: FZ-001 slots_full 29 / symbol_held 29 / no_cash 12; FZ-002 39 / 24 / 20;
C-NFLOOR no_cash 2, symbol_held 1.

## Known limits of these numbers

- This is ONE portfolio path (seed 7). The report quotes the MEDIAN of 40 Monte Carlo windows, so its CAGR differs
  from the final NAV of this file.
- TP / SL levels and exit triggers come from the deal engine's path on the ATO price, not from the average price of
  the worked order.
- `net_ret_total` treats cash dividends as received at once and untaxed, and bonus shares as sellable at once. The
  real outcome lies between `net_ret_cash` and `net_ret_total`.
