"""
simulation_email.py -- Standalone simulation for the 'email' profile (order_point scoring).

Replicates MCP simulation v1.6 logic using:
  - profile_hit.csv:   pre-computed buy/sell signal universe
  - VNINDEX.csv:       market timing signals (BearDvg / BullDvg + PE percentile)
  - config.json:       order_point weights for 14 buy strategies

Score model (from wrap_score_1_6.py):
  - Default score = 0.5
  - Regular buy hit in last BUY_WINDOW+1=4 sessions:
      score = 1 + order_rank/100  (order_rank = strategy weight)
  - Sell pattern: score = -1  (overwrites buy)
  - Market sell (BearDvgVNI in last MARKET_WINDOW+1=12 sessions): score = -10

Usage:
    python simulation_email.py [date_from] [date_to]
    python simulation_email.py 2014-01-01 2025-01-01
    python simulation_email.py 2025-01-01 2026-04-30
"""

import sys
import warnings
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import timedelta
from collections import deque

warnings.filterwarnings("ignore")

WORKDIR = Path(r"/home/trido/thanhdt/WorkingClaude")

# -- Portfolio parameters (from simulate_config in utils_v2.py) ----------------
INITIAL_NAV       = 50_000_000_000   # 50 billion VND
N_SLOTS           = 10               # max concurrent positions (si_slot)
RATIO_DEAL        = 0.1              # each deal = 10% of NAV (ratio_deal)
CUTLOSS_PCT       = 0.15             # 15% stop-loss (cutloss) -- pre-computed in profile_hit
CUTLOSS_DURATION  = 30               # days to blacklist after cutloss / time_stop
TIME_STOP_DAYS    = 20               # sell after 20 days if never profitable -- pre-computed in profile_hit
TC_BUY            = 0.001            # 0.1% transaction cost on buy (fee_buy_rate)
TC_SELL           = 0.002            # 0.1% TC + 0.1% tax on sell (fee_sell_rate)
MIN_DEAL_VND      = 10_000_000       # 10M VND minimum (min_amount_deal)
SCORE_BUY         = 1.0              # score_buy threshold to open position
SCORE_SELL        = 0.0              # score_sell threshold to close position
GAMMA             = 1                # score_to_ratio_nav gamma: int(score) slots

# -- Scoring window sizes (from wrap_score_1_6.py) ----------------------------
BUY_WINDOW        = 3    # regular buy: sessions=3 -> rolling window=4
MARKET_WINDOW     = 11   # market sell: sessions=11 -> rolling window=12

# -- Order-point weights for 'email' profile (w_1..w_16) ----------------------
# Strategies listed in config.json filter dict order
STRATEGY_WEIGHTS = {
    'BKMA200':         14.0,
    'BullDvg':         12.0,
    'BuySupport':      13.0,
    'CashCowStock':     2.0,
    'Conservative':    12.0,
    'DividendYield':    8.0,
    'RSILow30':         4.0,
    'SuperGrowth':      0.0,
    'SurpriseEarning': 11.0,
    'TL3M':             2.0,
    'TradingValueMax':  5.0,
    'TrendingGrowth':   0.0,
    'UnderBV':          0.0,
    'VolMax1Y':         0.0,
}

ACTIVE_STRATEGIES = {k for k, v in STRATEGY_WEIGHTS.items() if v > 0}

# -- VNINDEX PE percentile thresholds for market timing -----------------------
PE_P20 = 0.20
PE_P60 = 0.60
PE_P65 = 0.65
PE_P80 = 0.80
PE_P90 = 0.90
PE_P95 = 0.95


# -----------------------------------------------------------------------------
# Data loading
# -----------------------------------------------------------------------------

def load_hits():
    """Load profile_hit.csv, keep active strategies, add weight column."""
    df = pd.read_csv(WORKDIR / 'data/profile_hit.csv',
                     usecols=['filter', 'ticker', 'time', 'Open_1D',
                               'Sell_time', 'Sell_filter', 'Sell_profit'],
                     parse_dates=['time', 'Sell_time'])
    df = df[df['filter'].isin(ACTIVE_STRATEGIES)].copy()
    df['weight'] = df['filter'].map(STRATEGY_WEIGHTS)
    # Keep only highest-weight strategy per (ticker, time) -- matches utils_v2.py drop_duplicates
    df = (df.sort_values(['time', 'ticker', 'weight'], ascending=[True, True, False])
            .drop_duplicates(subset=['ticker', 'time'], keep='first')
            .reset_index(drop=True))
    return df


def load_vnindex():
    needed_cols = [
        'time', 'VNINDEX_PE_PERCENTILE',
        'D_RSI', 'D_RSI_T1W',
        'D_RSI_Max1W', 'D_RSI_Max1W_Close', 'D_RSI_Max1W_MACD',
        'D_RSI_Max3M', 'D_RSI_Max3M_Close', 'D_RSI_Max3M_MACD',
        'D_RSI_Min1W', 'D_RSI_Min1W_Close',
        'D_RSI_Min3M', 'D_RSI_Min3M_Close',
        'D_RSI_MinT3', 'D_MACDdiff', 'D_CMF', 'C_L1M', 'C_L1W', 'Close',
    ]
    df = pd.read_csv(WORKDIR / 'data/VNINDEX.csv', usecols=needed_cols, parse_dates=['time'])
    return df.sort_values('time').reset_index(drop=True)


# -----------------------------------------------------------------------------
# Market timing
# -----------------------------------------------------------------------------

def evaluate_market_signals(vn):
    """Evaluate BearDvgVNI1/2 and BullDvgVNI1/12 on VNINDEX data."""
    df = vn.copy()

    bear1 = (
        (df['time'] >= '2011-01-01') &
        (df['D_RSI_Max1W'] / df['D_RSI'].replace(0, np.nan) > 1.044) &
        (df['D_RSI_Max3M'] > 0.74) &
        (df['D_RSI_Max1W'] < 0.72) & (df['D_RSI_Max1W'] > 0.61) &
        (df['D_RSI_Max1W_Close'] / df['D_RSI_Max3M_Close'].replace(0, np.nan) > 1.028) &
        (df['D_RSI_Max3M_MACD'] / df['D_RSI_Max1W_MACD'].replace(0, np.nan) > 1.11) &
        (df['D_MACDdiff'] < 0) &
        (df['Close'] / df['D_RSI_Max3M_Close'].replace(0, np.nan) > 0.96) &
        (df['D_RSI_MinT3'] > 0.43) & (df['D_CMF'] < 0.13)
    )
    bear2 = (
        (df['time'] >= '2011-01-01') &
        (df['D_RSI_Max1W'] / df['D_RSI'].replace(0, np.nan) > 1.016) &
        (df['D_RSI_Max3M'] > 0.77) &
        (df['D_RSI_Max1W'] < 0.79) & (df['D_RSI_Max1W'] > 0.60) &
        (df['D_RSI_Max1W_Close'] / df['D_RSI_Max3M_Close'].replace(0, np.nan) > 1.008) &
        (df['D_RSI_Max3M_MACD'] / df['D_RSI_Max1W_MACD'].replace(0, np.nan) > 1.10) &
        (df['D_MACDdiff'] < 0) &
        (df['Close'] / df['D_RSI_Max3M_Close'].replace(0, np.nan) > 0.97) &
        (df['D_RSI_MinT3'] > 0.50) & (df['D_CMF'] < 0.15)
    )
    bull1 = (
        (df['time'] >= '2011-01-01') &
        (df['D_RSI_Min1W'] / df['D_RSI_Min3M'].replace(0, np.nan) > 0.90) &
        (df['D_RSI_Min1W'] < 0.60) & (df['D_RSI_Min3M'] < 0.40) &
        (df['D_RSI_Min1W_Close'] / df['D_RSI_Min3M_Close'].replace(0, np.nan) < 1.15) &
        (df['D_MACDdiff'] > 0) & (df['D_RSI_MinT3'] < 0.50) & (df['D_RSI_Max1W'] < 0.48) &
        (df['D_RSI'] / df['D_RSI_T1W'].replace(0, np.nan) > 1.12) &
        (df['D_CMF'] > 0) & (df['C_L1M'] < 1.21) & (df['C_L1W'] < 1.05)
    )
    bull12 = (
        (df['time'] >= '2011-01-01') &
        (df['D_RSI_Min1W'] / df['D_RSI_Min3M'].replace(0, np.nan) > 0.92) &
        (df['D_RSI_Min1W'] < 0.52) & (df['D_RSI_Min3M'] < 0.38) &
        (df['D_RSI_Min1W_Close'] / df['D_RSI_Min3M_Close'].replace(0, np.nan) < 1.10) &
        (df['D_MACDdiff'] > 0) & (df['D_RSI_MinT3'] < 0.56) & (df['D_RSI_Max1W'] < 0.64) &
        (df['D_RSI'] / df['D_RSI_T1W'].replace(0, np.nan) > 1.10) &
        (df['D_CMF'] > 0) & (df['C_L1M'] < 1.20) & (df['C_L1W'] < 1.025)
    )

    # Bear signals: require PE >= P60; de-dup to one per month
    bear_df = df[bear1 | bear2][['time', 'VNINDEX_PE_PERCENTILE']].copy()
    bear_df = bear_df[bear_df['VNINDEX_PE_PERCENTILE'] >= PE_P60]
    bear_df['month'] = bear_df['time'].dt.to_period('M')
    bear_df = (bear_df.sort_values('time')
               .drop_duplicates(subset='month', keep='first')
               .reset_index(drop=True))

    # Bull signals: require PE <= P60; de-dup to one per month
    bull_df = df[bull1 | bull12][['time', 'VNINDEX_PE_PERCENTILE']].copy()
    bull_df = bull_df[bull_df['VNINDEX_PE_PERCENTILE'] <= PE_P60]
    bull_df['month'] = bull_df['time'].dt.to_period('M')
    bull_df = (bull_df.sort_values('time')
               .drop_duplicates(subset='month', keep='first')
               .reset_index(drop=True))

    return bear_df, bull_df


def build_market_blocks(bear_df, bull_df):
    """
    Build market block windows (no new buys) from BearDvg sell to BullDvg buy.
    Implements enable_market_eval=True logic from utils_v2.py / market_rule.md.
    Returns sorted list of (block_start, block_end) Timestamps.
    """
    bull_times = bull_df['time'].values
    bull_pes   = bull_df['VNINDEX_PE_PERCENTILE'].values

    blocks = []
    for _, row in bear_df.iterrows():
        sell_t  = row['time']
        sell_pe = row['VNINDEX_PE_PERCENTILE']

        if   sell_pe >= PE_P95: days = int(1.5 * 365)
        elif sell_pe >= PE_P90: days = 365
        elif sell_pe >= PE_P80: days = 90
        elif sell_pe >= PE_P65: days = 60
        else:                   days = 30

        max_end   = sell_t + timedelta(days=days)
        block_end = max_end

        # Find first valid bull signal within the window
        mask = (bull_times > sell_t) & (bull_times <= max_end)
        for bt, bp in zip(bull_times[mask], bull_pes[mask]):
            bt = pd.Timestamp(bt)
            if sell_pe >= PE_P90:
                if bp <= PE_P20:
                    block_end = bt
                    break
            else:
                block_end = bt
                break

        blocks.append((sell_t, block_end))

    if not blocks:
        return []

    blocks.sort()
    merged = [list(blocks[0])]
    for s, e in blocks[1:]:
        if s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    return [(pd.Timestamp(s), pd.Timestamp(e)) for s, e in merged]


def in_block(ts, blocks):
    """True if ts falls inside any market block window."""
    ts = pd.Timestamp(ts)
    for s, e in blocks:
        if s <= ts <= e:
            return True
    return False


# -----------------------------------------------------------------------------
# Portfolio
# -----------------------------------------------------------------------------

class Portfolio:
    def __init__(self):
        self.cash         = float(INITIAL_NAV)
        self.open         = []    # list of position dicts
        self.closed       = []
        self.nav_history  = {}
        self.cutloss_dict = {}    # ticker -> blacklist_until date

    def nav(self):
        return self.cash + sum(p['invested'] for p in self.open)

    def n_open(self):
        return len(self.open)

    def held_tickers(self):
        return {p['ticker'] for p in self.open}

    def is_blacklisted(self, ticker, today):
        """True if ticker is in cutloss/time_stop blacklist."""
        until = self.cutloss_dict.get(ticker)
        if until is None:
            return False
        return today < until

    def open_position(self, ticker, signal_date, entry_exec_date,
                      entry_price, sell_date, sell_profit, sell_filter, score,
                      n_slots=1):
        """
        Open a new position.  n_slots = int(score) from score_to_ratio_nav.
        Returns True if opened, False if insufficient cash/slots.
        """
        deal = self.nav() * RATIO_DEAL * n_slots
        deal = max(deal, INITIAL_NAV * RATIO_DEAL * n_slots)
        if deal < MIN_DEAL_VND or self.cash < deal * (1 + TC_BUY):
            return False
        cost = deal * (1 + TC_BUY)
        self.cash -= cost
        self.open.append({
            'ticker':          ticker,
            'signal_date':     signal_date,
            'entry_exec_date': entry_exec_date,
            'entry_price':     entry_price,
            'invested':        deal,
            'cost':            cost,
            'sell_date':       sell_date,
            'sell_profit':     sell_profit,
            'sell_filter':     sell_filter,
            'score':           score,
            'n_slots':         n_slots,
        })
        return True

    def close_position(self, pos, today, blacklist=False):
        """Close a position.  Optionally blacklist the ticker."""
        ratio = pos['sell_profit'] / 100.0
        gross = pos['invested'] * (1.0 + ratio)
        net   = gross * (1.0 - TC_SELL)
        self.cash += net
        pos['close_date']   = today
        pos['gross_return'] = ratio
        pos['net_pnl']      = net - pos['cost']
        self.closed.append(pos)
        if blacklist:
            until = today + timedelta(days=CUTLOSS_DURATION)
            # Keep the later date if already blacklisted
            existing = self.cutloss_dict.get(pos['ticker'])
            if existing is None or until > existing:
                self.cutloss_dict[pos['ticker']] = until

    def record_nav(self, date):
        self.nav_history[date] = self.nav()


# -----------------------------------------------------------------------------
# Main simulation
# -----------------------------------------------------------------------------

def run_simulation(date_from='2014-01-01', date_to='2025-01-01', verbose=True):
    date_from = pd.Timestamp(date_from)
    date_to   = pd.Timestamp(date_to)

    hits    = load_hits()
    vnindex = load_vnindex()

    # Build market blocks (enable_market_eval=True)
    bear_df, bull_df = evaluate_market_signals(vnindex)
    blocks = build_market_blocks(bear_df, bull_df)
    if verbose:
        print(f"Market blocks: {len(blocks)}")
        for s, e in blocks[:8]:
            print(f"  {s.date()} to {e.date()}")
        if len(blocks) > 8:
            print(f"  ... ({len(blocks)} total)")

    # Trading dates in simulation range
    trading_dates = sorted(
        vnindex.loc[(vnindex['time'] >= date_from) & (vnindex['time'] <= date_to), 'time'].tolist()
    )
    trading_dates = [pd.Timestamp(d) for d in trading_dates]
    date_to_idx   = {d: i for i, d in enumerate(trading_dates)}

    # Build set of bear signal dates for market sell (score=-10) window
    # After BearDvgVNI fires, block for MARKET_WINDOW+1=12 sessions
    bear_dates_sorted = sorted(bear_df['time'].tolist())

    # Load hits in range (include BUY_WINDOW sessions of lookback)
    lookback_start = date_from - pd.Timedelta(days=BUY_WINDOW * 3)
    hits_window = hits[
        (hits['time'] >= lookback_start) & (hits['time'] <= date_to)
    ].copy().sort_values('time').reset_index(drop=True)

    # Pre-index hits by date
    hits_by_date = {}
    for d, grp in hits_window.groupby('time'):
        hits_by_date[pd.Timestamp(d)] = grp

    portfolio = Portfolio()

    # Sliding window: deque of (time, ticker, weight)
    # Keeps hits from the last BUY_WINDOW trading sessions
    win_events = deque()
    hit_iter_idx = 0
    hit_rows = list(hits_window[['time', 'ticker', 'weight']].itertuples(index=False))

    # Sliding window for market sell (BearDvgVNI): separate deque for bear dates
    bear_win = deque()  # bear signal dates within last MARKET_WINDOW sessions
    bear_iter = 0

    if verbose:
        print(f"\nSimulation: {date_from.date()} -> {date_to.date()}")
        print(f"Trading days: {len(trading_dates)}")

    for day_idx, today in enumerate(trading_dates):

        # ── Advance buy-signal sliding window ─────────────────────────────
        while hit_iter_idx < len(hit_rows) and hit_rows[hit_iter_idx].time <= today:
            e = hit_rows[hit_iter_idx]
            win_events.append((e.time, e.ticker, e.weight))
            hit_iter_idx += 1

        # Prune hits older than BUY_WINDOW trading sessions
        if day_idx >= BUY_WINDOW:
            buy_cutoff = trading_dates[day_idx - BUY_WINDOW]
        else:
            buy_cutoff = date_from - pd.Timedelta(days=1)
        while win_events and win_events[0][0] < buy_cutoff:
            win_events.popleft()

        # ── Advance market-sell (BearDvgVNI) sliding window ───────────────
        while bear_iter < len(bear_dates_sorted) and bear_dates_sorted[bear_iter] <= today:
            bear_win.append(bear_dates_sorted[bear_iter])
            bear_iter += 1

        if day_idx >= MARKET_WINDOW:
            mkt_cutoff = trading_dates[day_idx - MARKET_WINDOW]
        else:
            mkt_cutoff = date_from - pd.Timedelta(days=1)
        while bear_win and bear_win[0] < mkt_cutoff:
            bear_win.popleft()

        market_sell_active = len(bear_win) > 0

        # ── Close positions whose Sell_time <= today ───────────────────────
        still_open = []
        for pos in portfolio.open:
            sell_date = pos['sell_date']
            entry_idx = date_to_idx.get(pos['entry_exec_date'], -1)
            t2_ok     = (day_idx >= entry_idx + 2) if entry_idx >= 0 else False

            if sell_date <= today and t2_ok:
                # Blacklist on cutloss or time_stop exits
                blacklist = pos['sell_filter'] in ('cutloss', 'time_stop')
                portfolio.close_position(pos, today, blacklist=blacklist)
            else:
                still_open.append(pos)
        portfolio.open = still_open

        # ── Record NAV ────────────────────────────────────────────────────
        portfolio.record_nav(today)

        # ── Skip buying: market sell, PE-block, or fully invested ─────────
        if market_sell_active:
            continue
        if in_block(today, blocks):
            continue
        if portfolio.n_open() >= N_SLOTS:
            continue

        # ── Score: per ticker, max weight in BUY_WINDOW sessions ──────────
        # score = 1 + max_weight / 100  (from wrap_score_1_6.py)
        ticker_max_w: dict[str, float] = {}
        for _, tkr, wt in win_events:
            if wt > ticker_max_w.get(tkr, 0.0):
                ticker_max_w[tkr] = wt

        # Only consider tickers that have a hit signal TODAY
        today_hits = hits_by_date.get(today)
        if today_hits is None:
            continue

        today_tickers = set(today_hits['ticker'].unique())
        candidates = []
        for tkr in today_tickers:
            max_w = ticker_max_w.get(tkr, 0.0)
            if max_w <= 0:
                continue
            score = 1.0 + max_w / 100.0
            if score >= SCORE_BUY:
                candidates.append((tkr, score))
        candidates.sort(key=lambda x: -x[1])  # highest score first

        held      = portfolio.held_tickers()
        slots_left = N_SLOTS - portfolio.n_open()

        for tkr, score in candidates:
            if slots_left <= 0:
                break
            if tkr in held:
                continue
            if portfolio.is_blacklisted(tkr, today):
                continue

            # Pick best hit row: highest weight, then earliest Sell_time
            tkr_hits = today_hits[today_hits['ticker'] == tkr]
            tkr_hits = tkr_hits.sort_values(['weight', 'Sell_time'],
                                            ascending=[False, True])
            hit = tkr_hits.iloc[0]

            sell_date   = pd.Timestamp(hit['Sell_time'])
            sell_profit = float(hit['Sell_profit'])
            sell_filter = str(hit['Sell_filter'])
            entry_price = float(hit['Open_1D'])

            # n_slots from score_to_ratio_nav(score, 1, gamma=1) = int(score)
            n_slots_deal = int(score)  # 1 for regular (1.xx), 2 for special (2.xx)

            # Entry execution = next trading day (T+1)
            if day_idx + 1 < len(trading_dates):
                entry_exec = trading_dates[day_idx + 1]
            else:
                entry_exec = today

            opened = portfolio.open_position(
                ticker=tkr,
                signal_date=today,
                entry_exec_date=entry_exec,
                entry_price=entry_price,
                sell_date=sell_date,
                sell_profit=sell_profit,
                sell_filter=sell_filter,
                score=score,
                n_slots=n_slots_deal,
            )
            if opened:
                held.add(tkr)
                slots_left -= n_slots_deal

    # ── Flush remaining open positions (mark as "Hold") ───────────────────
    for pos in list(portfolio.open):
        pos['sell_profit'] = 0.0
        pos['sell_filter'] = 'Hold'
        portfolio.close_position(pos, trading_dates[-1])
    portfolio.open = []
    portfolio.record_nav(trading_dates[-1])

    nav_series = pd.Series(portfolio.nav_history).sort_index()
    trades_df  = pd.DataFrame(portfolio.closed) if portfolio.closed else pd.DataFrame()
    return nav_series, trades_df


# -----------------------------------------------------------------------------
# Metrics
# -----------------------------------------------------------------------------

def compute_metrics(nav_series, trades_df, verbose=True):
    nav = nav_series.dropna().sort_index()
    if len(nav) < 2:
        print("Insufficient data for metrics.")
        return {}

    days         = (nav.index[-1] - nav.index[0]).days
    years        = days / 365.25
    total_return = nav.iloc[-1] / nav.iloc[0] - 1
    cagr         = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0

    daily_ret         = nav.pct_change().dropna()
    sessions_per_year = len(daily_ret) / years if years > 0 else 252
    mu_daily          = daily_ret.mean()
    std_daily         = daily_ret.std()
    sharpe            = (mu_daily / std_daily * np.sqrt(sessions_per_year)) if std_daily > 0 else 0

    downside = daily_ret[daily_ret < 0].std()
    sortino  = (mu_daily / downside * np.sqrt(sessions_per_year)) if downside > 0 else 0

    rolling_max = nav.cummax()
    dd          = (nav - rolling_max) / rolling_max
    max_dd      = dd.min()
    calmar      = cagr / abs(max_dd) if max_dd != 0 else 0

    underwater = dd < 0
    dd_dur = cur = 0
    for u in underwater:
        cur    = cur + 1 if u else 0
        dd_dur = max(dd_dur, cur)

    metrics = {
        'Period':       f"{nav.index[0].date()} to {nav.index[-1].date()}",
        'Start NAV':    f"{nav.iloc[0]/1e9:.2f}B",
        'End NAV':      f"{nav.iloc[-1]/1e9:.2f}B",
        'Total Return': f"{total_return*100:.1f}%",
        'CAGR':         f"{cagr*100:.2f}%",
        'Sharpe':       f"{sharpe:.2f}",
        'Sortino':      f"{sortino:.2f}",
        'Max DD':       f"{max_dd*100:.1f}%",
        'Calmar':       f"{calmar:.2f}",
        'DD Duration':  f"{dd_dur} trading days",
    }

    if not trades_df.empty and 'gross_return' in trades_df.columns:
        closed_real = trades_df[trades_df['sell_filter'] != 'Hold']
        n_total  = len(closed_real)
        n_hold   = (trades_df['sell_filter'] == 'Hold').sum()
        n_win    = (closed_real['gross_return'] > 0).sum()
        win_rate = n_win / n_total if n_total > 0 else 0
        avg_win  = closed_real.loc[closed_real['gross_return'] > 0, 'gross_return'].mean()
        avg_loss = closed_real.loc[closed_real['gross_return'] <= 0, 'gross_return'].mean()

        metrics.update({
            'Deals (closed)':    n_total,
            'Still Open (Hold)': n_hold,
            'Win Rate':          f"{win_rate*100:.1f}%",
            'Avg Win':           f"{avg_win*100:.1f}%" if not np.isnan(avg_win) else 'N/A',
            'Avg Loss':          f"{avg_loss*100:.1f}%" if not np.isnan(avg_loss) else 'N/A',
        })

        if 'signal_date' in trades_df.columns and 'close_date' in trades_df.columns:
            td = closed_real.copy()
            td['hold_days'] = (pd.to_datetime(td['close_date']) -
                               pd.to_datetime(td['signal_date'])).dt.days
            metrics['Avg Hold Days'] = f"{td['hold_days'].mean():.0f} days"

        sf_counts = closed_real['sell_filter'].value_counts()
        metrics['Exit breakdown'] = sf_counts.to_dict()

    if verbose:
        print("\n" + "="*55)
        print("  SIMULATION RESULTS")
        print("="*55)
        for k, v in metrics.items():
            if k == 'Exit breakdown':
                print(f"  {k}:")
                for kk, vv in v.items():
                    print(f"      {kk}: {vv}")
            else:
                print(f"  {k:<28} {v}")
        print("="*55)

    return metrics


# -----------------------------------------------------------------------------
# Entry point
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    date_from = sys.argv[1] if len(sys.argv) > 1 else '2014-01-01'
    date_to   = sys.argv[2] if len(sys.argv) > 2 else '2025-01-01'

    print("Loading data...")
    nav_series, trades_df = run_simulation(date_from=date_from, date_to=date_to)
    metrics = compute_metrics(nav_series, trades_df)

    out_path = WORKDIR / f"sim_nav_{date_from[:7]}_{date_to[:7]}.csv"
    nav_series.to_csv(out_path, header=['NAV'])
    print(f"\nNAV series saved -> {out_path.name}")
