"""Portfolio simulation engine for Holistic Recommendation system.

Day-by-day NAV simulation with:
  - T+1 execution (signal day t → enter at close of t+1)
  - Equal-weight positions (max N concurrent)
  - 60 trading day hold (≈3M) or stop-loss
  - TC = 0.1% per trade (in + out = 0.2% round-trip)
  - Idle cash earns deposit_annual (default 0%); negative cash charged borrow_annual (default 10%/yr)

Strategies:
  - STRAT_MEGA: max 3 positions, MEGA tier only
  - STRAT_HIGH_CONV: max 5 positions, MEGA + MOMENTUM + MOMENTUM_N
  - STRAT_BALANCED: max 8 positions, top 4 tiers
  - VNINDEX baseline: B&H

Computed metrics: CAGR, Sharpe, Sortino, MaxDD, Calmar, win rate, turnover.

LOCAL_SNAPSHOT_DIR mode (env var):
  Set LOCAL_SNAPSHOT_DIR=<path> to bypass BigQuery and load data from local parquet snapshots.
  Expected files: signal_YYYYMMDD.parquet, vni_YYYYMMDD.parquet (latest by filename sort).
  The bq() function intercepts calls and routes by SQL content:
    - SQL containing 'play_type' or 'fa_ratings' → loads signal snapshot
    - SQL containing 'VNINDEX' and 'Close'        → loads vni snapshot
    - Otherwise → falls through to real BQ (with a warning)
  Date filtering is applied by parsing DATE '{start}' / DATE '{end}' from the SQL string.
  Zero downstream changes — only the data-loading layer is patched.
"""
import os
import re
import subprocess
import sys
from io import StringIO

import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
PROJECT = "lithe-record-440915-m9"
BQ_BIN = r"bq"

# ─── LOCAL SNAPSHOT MODE ──────────────────────────────────────────────────────
# Set LOCAL_SNAPSHOT_DIR env var to bypass BigQuery entirely.
# Winston's pipeline writes: signal_YYYYMMDD.parquet, vni_YYYYMMDD.parquet
# into that directory.  bq() intercepts by SQL content and loads the latest file.
_LOCAL_SNAPSHOT_DIR = os.environ.get("LOCAL_SNAPSHOT_DIR", "").strip()

_SNAPSHOT_CACHE: dict = {}  # avoid re-loading within same process


def _load_local_snapshot(name: str) -> pd.DataFrame:
    """Load latest parquet snapshot for `name` (signal|vni|...).

    Searches _LOCAL_SNAPSHOT_DIR for files matching <name>_*.parquet and
    returns the last one by sorted filename (YYYYMMDD suffix → lexical sort
    matches chronological sort).  Raises FileNotFoundError if none found.
    """
    import glob
    pattern = os.path.join(_LOCAL_SNAPSHOT_DIR, f"{name}_*.parquet")
    files = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError(
            f"No local snapshot found for '{name}' (pattern: {pattern}). "
            f"Make sure Winston's snapshot pipeline has run and "
            f"LOCAL_SNAPSHOT_DIR={_LOCAL_SNAPSHOT_DIR!r} is correct."
        )
    chosen = files[-1]  # latest by filename sort
    print(f"[LOCAL_SNAPSHOT] loading {os.path.basename(chosen)} for '{name}'", flush=True)
    return pd.read_parquet(chosen)


def _extract_date(sql: str, key: str):
    """Extract date string from SQL pattern like DATE '{key}' where key is 'start' or 'end'.

    Returns date string (e.g. '2014-01-01') or None if not found.
    """
    pattern = rf"DATE\s+'\{{{{?{re.escape(key)}}}}}?'"
    m = re.search(pattern, sql)
    if m:
        # Already-substituted form: DATE '2014-01-01'
        pass
    # Try already-substituted literal dates around the template position:
    # Support both DATE '{start}' (template, not yet substituted) and DATE '2014-01-01'
    # We look for the first DATE '...' for start and the second for end.
    date_hits = re.findall(r"DATE\s+'(\d{4}-\d{2}-\d{2})'", sql)
    if key == "start" and len(date_hits) >= 1:
        return date_hits[0]
    if key == "end" and len(date_hits) >= 2:
        return date_hits[1]
    return None

# Simulation parameters
START_DATE = "2014-01-01"
END_DATE   = "2026-01-16"
INIT_NAV   = 1_000_000_000     # 1B VND
TC_BUY     = 0.0015             # 0.15% phí mua (Vietnam broker standard 2026)
TC_SELL    = 0.0015             # 0.15% phí bán broker
CG_TAX     = 0.001              # 0.1% thuế bán (capital gain tax VN, PIT on transaction value)
MIN_HOLD   = 2                  # T+3: tối thiểu 2 phiên sau mua mới được bán (T+2 close)
HOLD_DAYS  = 60                 # ~3 trading months target
DEPOSIT_R  = 0.03 / 252         # 3%/yr — realistic non-term cash rate
STOP_LOSS  = -0.15              # -15% stop loss
SLIPPAGE   = 0.0                # default no slippage (set 0.001-0.003 for realistic)


SIGNAL_QUERY = """
WITH fa_dated AS (
  SELECT f.ticker, f.time AS f_time, f.tier AS fa_tier,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.fa_ratings AS f
),
fin_dated AS (
  SELECT f.ticker, f.time AS fin_time, f.Revenue_YoY_P0,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_fin_time
  FROM tav2_bq.ticker_financial AS f
),
classified AS (
  SELECT
    t.ticker, t.time, t.Close,
    (CASE WHEN t.D_RSI > 0.50 THEN 25 ELSE 0 END
    + CASE WHEN t.Close > t.MA50 AND t.MA50 > t.MA200 THEN 25 ELSE 0 END
    + CASE WHEN t.Volume >= t.Volume_3M_P50 * 1.3 AND t.Close > t.Close_T1 THEN 20 ELSE 0 END
    + CASE WHEN t.D_MACDdiff > 0 THEN 15 ELSE 0 END
    + CASE WHEN t.Close > t.MA20 THEN 15 ELSE 0 END
    + CASE WHEN t.D_RSI > 0.75 THEN 5 ELSE 0 END
    + CASE WHEN t.D_RSI < 0.30 THEN -10 ELSE 0 END
    + CASE WHEN t.PE > 0 AND t.PE_MA5Y > 0 AND t.PE < t.PE_MA5Y - 0.5*t.PE_SD5Y THEN 15 ELSE 0 END
    + CASE WHEN t.PE > 0 AND t.PE_MA5Y > 0 AND t.PE > t.PE_MA5Y + 1.0*t.PE_SD5Y THEN -15 ELSE 0 END
    + CASE WHEN t.VNINDEX_RSI_Max3M > 0.65 THEN 10 ELSE 0 END
    + CASE WHEN t.ID_HI_3Y <= 5 THEN 8 ELSE 0 END
    + CASE WHEN t.D_RSI_Max1W > 0.65 THEN 5 ELSE 0 END
    + CASE WHEN t.FSCORE >= 8 THEN 10 ELSE 0 END
    + CASE WHEN t.NP_P0 > t.NP_P4 * 1.5 AND t.NP_P4 > 0 THEN 8 ELSE 0 END
    + CASE WHEN t.NP_P0 < t.NP_P4 * 0.7 AND t.NP_P4 > 0 THEN -8 ELSE 0 END
    + CASE WHEN t.ICB_Code IS NOT NULL AND CAST(FLOOR(t.ICB_Code/1000) AS INT64) IN (8,9) THEN 5 ELSE 0 END
    + CASE WHEN t.ICB_Code IS NOT NULL AND CAST(FLOOR(t.ICB_Code/1000) AS INT64) IN (4,7) THEN -5 ELSE 0 END
    + CASE WHEN t.MA50_T1 > 0 AND t.MA50 > t.MA50_T1 THEN 5 ELSE 0 END
    + CASE WHEN t.MA50_T1 > 0 AND t.MA50 > t.MA50_T1 * 1.005 THEN 5 ELSE 0 END
    + CASE WHEN t.MA50_T1 > 0 AND t.MA50 < t.MA50_T1 THEN -5 ELSE 0 END
    + CASE WHEN t.HI_3M_T1 > 0 AND t.Close / t.HI_3M_T1 < 0.85 THEN -10 ELSE 0 END
    + CASE WHEN t.NP_P0 > t.NP_P1 * 1.2 AND t.NP_P1 > 0 THEN 8 ELSE 0 END) AS ta,
    s5.state AS state5,
    fa.fa_tier,
    SAFE_DIVIDE(t.NP_P0, t.NP_P4) - 1 AS np_yoy,
    fin.Revenue_YoY_P0 AS rev_yoy,
    (t.PE - t.PE_MA5Y) / NULLIF(t.PE_SD5Y, 0) AS pe_z,
    (t.D_RSI > 0.90 OR (t.MA20 > 0 AND t.Close / t.MA20 > 1.25)) AS warn_ext,
    t.Volume_3M_P50 * COALESCE(t.Price, t.Close) AS liq   -- real (unadjusted) traded notional
  FROM tav2_bq.ticker AS t
  LEFT JOIN tav2_bq.vnindex_5state AS s5 ON s5.time = t.time
  LEFT JOIN fa_dated AS fa ON fa.ticker = t.ticker AND t.time >= fa.f_time
       AND (fa.next_f_time IS NULL OR t.time < fa.next_f_time)
  LEFT JOIN fin_dated AS fin ON fin.ticker = t.ticker AND t.time >= fin.fin_time
       AND (fin.next_fin_time IS NULL OR t.time < fin.next_fin_time)
  WHERE t.time BETWEEN DATE '{start}' AND DATE '{end}'
    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
)
SELECT
  ticker, time, Close,
  CASE
    WHEN state5 IN (1, 2) THEN 'AVOID_bear'
    WHEN fa_tier = 'E' THEN 'AVOID_faE'
    WHEN ta >= 160 AND state5 IN (4,5) AND fa_tier IN ('C','D') THEN 'MEGA'
    WHEN ta >= 160 AND state5 IN (4,5) THEN 'S_PRO'
    WHEN ta >= 145 AND state5 IN (4,5) AND fa_tier IN ('C','D') THEN 'MOMENTUM'
    WHEN ta >= 145 AND state5 IN (4,5) AND fa_tier IN ('A','B') THEN 'MOMENTUM_QUALITY'
    WHEN ta >= 145 AND state5 = 3 AND fa_tier IN ('C','D') THEN 'MOMENTUM_N'
    WHEN fa_tier IN ('A','B') AND pe_z < -0.5 AND ta >= 95 AND state5 IN (3,4,5) AND NOT warn_ext THEN 'COMPOUNDER_BUY'
    WHEN fa_tier = 'C' AND ta >= 100 AND state5 IN (4,5) AND ((np_yoy > 0.20) OR (rev_yoy > 0.20)) THEN 'DEEP_VALUE_RECOVERY'
    WHEN ta >= 130 AND state5 IN (4,5) THEN 'MOMENTUM_S'
    WHEN ta >= 115 AND state5 IN (4,5) THEN 'MOMENTUM_A'
    WHEN ta >= 130 AND state5 = 3 THEN 'MOMENTUM_S_N'
    WHEN fa_tier IN ('A','B') AND ta >= 70 AND ta < 130 THEN 'COMPOUNDER_HOLD'
    WHEN fa_tier IN ('A','B') THEN 'WAIT'
    ELSE 'PASS'
  END AS play_type,
  ta,
  liq
FROM classified
WHERE liq >= 1e9
"""

VNI_QUERY = """
SELECT t.time, t.Close
FROM tav2_bq.ticker AS t
WHERE t.ticker = 'VNINDEX'
  AND t.time BETWEEN DATE '{start}' AND DATE '{end}'
ORDER BY t.time
"""


def bq(sql: str) -> pd.DataFrame:
    # ── LOCAL SNAPSHOT INTERCEPT ──────────────────────────────────────────────
    if _LOCAL_SNAPSHOT_DIR:
        # Route by SQL content to determine which snapshot to load
        _sql_upper = sql.upper()
        if "PLAY_TYPE" in _sql_upper or "FA_RATINGS" in _sql_upper or "FA_TIER" in _sql_upper:
            name = "signal"
        elif "VNINDEX" in _sql_upper and "CLOSE" in _sql_upper:
            name = "vni"
        else:
            name = None  # unknown query type — fall through to real BQ with a warning

        if name is not None:
            if name not in _SNAPSHOT_CACHE:
                _SNAPSHOT_CACHE[name] = _load_local_snapshot(name)
            df = _SNAPSHOT_CACHE[name].copy()

            # Parse date range from the SQL to filter the snapshot
            start_str = _extract_date(sql, "start")
            if df.empty:
                return df

            # Normalize time column to date objects for comparison
            time_col = "time" if "time" in df.columns else df.columns[0]
            df[time_col] = pd.to_datetime(df[time_col]).dt.date

            if start_str:
                start_d = pd.to_datetime(start_str).date()
                df = df[df[time_col] >= start_d]
            end_str = _extract_date(sql, "end")
            if end_str:
                end_d = pd.to_datetime(end_str).date()
                df = df[df[time_col] <= end_d]

            # Restore datetime dtype (callers expect pd.Timestamp)
            df[time_col] = pd.to_datetime(df[time_col])
            return df.reset_index(drop=True)
        else:
            print(
                f"[LOCAL_SNAPSHOT] WARNING: cannot route SQL to a local snapshot "
                f"(no 'play_type'/'fa_ratings'/'VNINDEX' keyword found). "
                f"Falling through to real BigQuery. SQL preview: {sql[:120]!r}",
                flush=True,
            )
    # ── ORIGINAL BIGQUERY PATH ────────────────────────────────────────────────
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql)
        sql_path = f.name
    try:
        cmd = (f'"{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} '
               f'--format=csv --max_rows=2000000 < "{sql_path}"')
        out = subprocess.run(cmd, capture_output=True, text=True, check=True, shell=True)
    finally:
        os.unlink(sql_path)
    if not out.stdout or not out.stdout.strip():
        return pd.DataFrame()   # zero-row result: bq --format=csv emits nothing, not even a header
    return pd.read_csv(StringIO(out.stdout))


# Tier priority for execution + eviction (higher = better conviction)
TIER_PRIORITY = {
    "MEGA":               100,
    "MOMENTUM":            85,
    "MOMENTUM_N":          80,
    "MOMENTUM_QUALITY":    70,
    "S_PRO":               65,
    "MOMENTUM_S":          60,
    "DEEP_VALUE_RECOVERY": 55,
    "RE_BACKLOG_BUY":      55,  # D1 deployed 2026-05-16: RE/KCN advance-customer surge
    "MOMENTUM_A":          50,
    "MOMENTUM_S_N":        45,
    "COMPOUNDER_BUY":      40,
    "COMPOUNDER_HOLD":     30,
    "WAIT":                10,
    "PASS":                 5,
    "AVOID_bear":           0,
    "AVOID_faE":            0,
}


def _finalize_partial(entry, positions, tk, play_type, ticker_sector_map, vni_dates, today):
    """Move partially-filled order to positions with weighted avg entry."""
    avg_px = entry["filled_cost"] / entry["filled_shares"] if entry["filled_shares"] > 0 else 0
    if avg_px <= 0:
        return
    positions[tk] = {
        "entry_price": avg_px,
        "entry_date": entry["first_fill_date"] or today,
        "shares": entry["filled_shares"],
        "days_held": (vni_dates.index(today) -
                       vni_dates.index(entry["first_fill_date"] or today)),
        "last_price": entry.get("last_seen_price", avg_px),
        "peak_price": max(entry.get("last_seen_price", avg_px), avg_px),
        "cost_basis": entry["filled_cost"],
        "play_type": play_type,
        "sector": ticker_sector_map.get(tk) if ticker_sector_map else None,
        "partial_taken": set(),
    }


def simulate(signals_df, prices, vni_dates, *,
             allowed_tiers, max_positions,
             hold_days=HOLD_DAYS, stop_loss=STOP_LOSS, min_hold=MIN_HOLD,
             hold_days_by_state=None,        # optional dict {state_int: hold_days_cap}; falls back to hold_days if state not in map / None state
             hold_days_by_tier=None,         # optional dict {play_type: hold_days_cap}; PRECEDES hold_days_by_state (committed sleeves e.g. CAPIT 60d)
             stop_exempt_tiers=None,         # optional set of play_types exempt from STOP/soft-stop (committed sleeves hold through the flush)
             stop_by_tier=None,              # optional {play_type: stop_loss} — per-tier hard stop; overrides exempt for that tier (e.g. liquid custom30 capit can cutloss)
             slot_exempt_tiers=None,         # optional set of play_types that don't count toward (or get blocked by) max_positions; cap them via tier_position_limit
             force_close_tiers_dates=None,   # optional dict {pd.Timestamp: set(play_types)} — on that date queue close (T+1 Open) of ALL positions in those tiers + cancel their pending entries; real mode-flips in switched books
             cash_etf_states_by_date=None,   # optional dict {pd.Timestamp: {state: etf_frac}} — per-date override of cash_etf_states (e.g. concentration-tilted parking); falls back to cash_etf_states when date absent
             max_gross_exposure=None,        # optional float (e.g. 1.5 = V6-v3 margin<=150%): stock buys may draw cash negative down to -(mge-1)*NAV; negative cash pays borrow_annual; ETF parking never uses margin
             margin_tiers=None,              # optional set of play_types ALLOWED to use the margin room (e.g. crisis-capit only); None = all tiers when max_gross_exposure is set

             lows=None,                    # dict {ticker: {date: daily_low}} for INTRADAY_LOW stop mode
             stop_mode="CLOSE",            # "CLOSE" (default, today's close) or "INTRADAY_LOW" (today's low touches stop)
             eviction=False, eviction_priority_gap=15,
             slippage=SLIPPAGE,
             trailing_stop_activate=None,   # e.g., 0.15 → activate trailing when ret >= +15%
             trailing_stop_pct=None,         # e.g., 0.08 → exit if drops 8% from peak
             partial_take_at=None,           # list of (ret_threshold, fraction_to_sell)
             soft_stop_partial=None,         # tuple (trim_threshold, trim_frac) — trim on loss; e.g. (-0.15, 0.5)

             sector_limit=None,              # max positions per sector (None = unlimited)
             ticker_sector_map=None,         # dict: ticker -> sector_top
             reentry_blacklist_days=20,      # default 20d (validated +0.6pp CAGR for BAL)
             init_nav=None,                  # capital size; default INIT_NAV (1B)
             liquidity_volume_pct=None,      # max % of daily turnover per day (None = no limit)
             max_fill_days=1,                # how many days to attempt completion of order
             min_fill_pct=0.30,              # if <30% filled after max_fill_days → abandon
             liquidity_lookup=None,          # dict: (ticker, time) -> volume_3m_p50 * price (real unadjusted notional, VND)
             exit_slippage_tiered=False,     # True: add extra slip on exit if position large vs ADV
             sector_limit_per_sector=None,   # dict {sector_id: max_pos} for per-sector caps
             sector_cap_exempt_tiers=None,   # set/list of play_types exempt from sector caps (D1)
             tier_position_limit=None,       # dict {play_type: max_concurrent} for per-tier cap (E3)
             tier_weights=None,              # dict {play_type: fraction_of_NAV} for tier-sized positions; None → equal-weight 1/max_positions
             tier_weights_by_state=None,     # OPTIONAL dict {state_int: {play_type: fraction}} — state-conditional tier weights; falls back to tier_weights if state not in map
             regime_suppress_dates=None,     # OPTIONAL set of pd.Timestamp: on these dates skip the tier_weights_by_state override (use base tier_weights). Used to SUPPRESS regime_size weak-halving during capitulation windows (validated: RS-off-in-capitulation). Default None = no suppression.
             state_by_date=None,             # optional dict {pd.Timestamp: state_int 1-5}; enables state-transition exits
             state_exit_map=None,            # dict {state_int: fraction_to_close} e.g. {1: 1.0, 2: 1.0} = close all in CRISIS/BEAR
             profit_target=None,             # close position if ret >= profit_target (e.g., 0.30 = +30%)
             pt_blacklist_days=0,            # re-entry blacklist after PROFIT_TARGET exit (default 0 = re-enter freely)
             deposit_annual=0.0,             # idle cash yield (default 0%/yr; set 0.01 or 0.005 for realistic VN non-term)
             borrow_annual=0.10,             # margin borrow rate (default 10%/yr per CLAUDE.md); charged when cash<0
             nav_log_extra=None,             # optional list to capture (date, cash, n_pos, deployed_pct, state)
             etf_log=None,                   # optional list to capture ETF rebalance events {ymd, action, amount_vnd, price_vn30, friction_cost, cash_after, cash_etf_after}
             event_log=None,                 # optional list to capture every BUY/SELL event individually (analyze_portfolio.py format)
             force_close_eod=True,           # if False, leave positions open at end (for unrealized P&L tracking)
             cash_etf_states=None,           # dict {state: etf_fraction} — fraction of cash parked in VN30 ETF per state
             vn30_underlying=None,           # pd.Series indexed by date with VN30 close prices (for ETF returns)
             etf_mgmt_fee_annual=0.0,        # ETF management fee (e.g., 0.0065 for E1VFVN30 0.65%/yr)
             etf_tracking_drag_annual=0.0,   # tracking error drag (e.g., 0.003 for -0.3%/yr)
             etf_rebalance_friction=0.0005,  # per side on rebalance (default 0.05%; realistic ~0.0015 = 0.15%)
             etf_adv_lookup=None,            # OPTIONAL dict {date: ETF daily ADV in VND} — liquidity ceiling for parking
             etf_liquidity_pct=None,         # OPTIONAL fraction of etf_adv usable/day (e.g. 0.20). None = no ETF liq cap (legacy)
             open_prices=None,               # dict {ticker: {time: Open}} — REQUIRED for realistic timing
             t1_open_exec=True,              # DEFAULT True (2026-05-12 production): buy at T+1 Open, exits at next-day Open
                                             # Set False only for back-compat with legacy backtests (introduces look-ahead bias)
             entry_alt_prices=None,          # OPTIONAL dict {ticker: {time: alt_fill_price}} — Layer 3 buy-point research
                                             # When set, overrides T+1 Open fill price with intraday-derived alternative
                                             # (e.g. 11:15 LIM fill, VWAP, ATC). Falls back to Open if (tk, today) missing.
             entry_fill_mode="open",         # label only, for trade-record annotation (e.g. "t1115_lim")
             exit_alt_prices=None,           # OPTIONAL dict {ticker: {time: alt_sell_price}} — Layer 3 sell-point research
                                             # When set, overrides T+1 Open sell price with intraday-derived alternative.
                                             # Note: STOP exits also re-priced. Falls back to Open if (tk, today) missing.
             exit_fill_mode="open",          # label only
             name="sim"):
    """
    Realistic simulation (production default, 2026-05-12+):
      - T+1 Open entry: signal at close of T → buy at OPEN of T+1 (matches live workflow)
      - T+1 Open exit:  STOP/TIME detected at T close → SELL at OPEN of T+1 (no look-ahead bias)
      - T+3 min hold: bán sớm nhất sau 2 phiên kể từ entry (= T+3 từ signal)
      - TC: 0.1% buy + 0.1% sell + 0.1% capital gain tax (0.3% round-trip total)
      - Stop loss + time exit (whichever first, sau khi qua min_hold)

    Note: t1_open_exec=True is the DEFAULT (realistic). Setting False reverts to legacy
    T-close execution which OVERSTATES returns by ~1.92pp CAGR over 12y (look-ahead bias).

    signals_df: [time, ticker, play_type, ta, Close]
    prices: dict {ticker: {time: Close}}
    open_prices: dict {ticker: {time: Open}} — REQUIRED for realistic timing
    vni_dates: sorted list of trading dates
    """
    nav_init = init_nav if init_nav is not None else INIT_NAV
    cash = nav_init
    # ETF FIFO accounting (per user 2026-05-18): each rebalance-buy creates a "lot"
    # with real entry_date + shares + cost_basis. Each rebalance-sell consumes
    # oldest lots first. cash_etf is computed as the mark-to-market sum of all
    # lots × today's ETF price — never tracked as a free-floating scalar.
    etf_lots = []   # list of {entry_date, shares, cost_basis, last_px, holding_id}
    _etf_lot_seq = [0]   # list-wrapped int so nested fn can mutate

    def _etf_mark(today):
        """Mark-to-market all ETF lots at today's price (or last-known if missing)."""
        if not etf_lots:
            return 0.0
        px = vn30_underlying.get(today) if vn30_underlying is not None else None
        if px is None or pd.isna(px) or px <= 0:
            return sum(lot["shares"] * lot.get("last_px", 0.0) for lot in etf_lots)
        px_f = float(px)
        for lot in etf_lots:
            lot["last_px"] = px_f
        return sum(lot["shares"] * px_f for lot in etf_lots)

    _ETF_LIQ_ON = (etf_liquidity_pct is not None and etf_adv_lookup is not None)
    def _etf_day_cap(today):
        """Max VND of E1VFVN30 tradeable today (liquidity ceiling for parking buys AND sells).
        None/inf when no cap configured (legacy behavior)."""
        if not _ETF_LIQ_ON:
            return float("inf")
        adv = etf_adv_lookup.get(today)
        return etf_liquidity_pct * float(adv) if (adv is not None and adv > 0) else 0.0

    positions = {}      # ticker -> {entry_price, entry_date, shares, days_held, last_price}
    pending_entries = []  # list of dicts (multi-day fill capable)
    pending_exits = []    # T+1 open exec mode: list of (ticker, reason) to execute next day at Open
    blacklist = {}        # ticker -> days_remaining_until_eligible
    nav_history = []
    trades = []
    skipped_for_liquidity = 0
    abandoned_partial = 0
    _entry_seq = 0       # monotonic counter for unique holding_id

    sig_filtered = signals_df[signals_df["play_type"].isin(allowed_tiers)].copy()
    sig_by_date = {d: g for d, g in sig_filtered.groupby("time")}
    date_idx = {d: i for i, d in enumerate(vni_dates)}

    # Slippage: pay more on buy, get less on sell
    sell_cost_factor = (1 - TC_SELL - CG_TAX) * (1 - slippage)   # 0.998 * (1 - slip)
    buy_cost_factor  = (1 + TC_BUY) * (1 + slippage)             # 1.001 * (1 + slip)
    if ticker_sector_map is None:
        ticker_sector_map = {}

    for i, today in enumerate(vni_dates):
        # 0) T+1 OPEN EXEC: execute pending exits from prior session at today's Open price
        if t1_open_exec and pending_exits:
            still_pending = []
            for entry in pending_exits:
                tk = entry["ticker"]
                reason = entry["reason"]
                if tk not in positions:
                    continue  # position already gone (shouldn't happen normally)
                pos = positions[tk]
                # Use today's OPEN price (with fallback to Close if Open unavailable)
                # Layer 3 sell-point research: if exit_alt_prices supplies an
                # intraday-derived alt sell (e.g. 14:45 ATC), use that.
                open_px = None
                if exit_alt_prices is not None:
                    open_px = exit_alt_prices.get(tk, {}).get(today)
                    if open_px is None or pd.isna(open_px) or open_px <= 0:
                        open_px = None
                if open_px is None and open_prices is not None:
                    open_px = open_prices.get(tk, {}).get(today)
                if open_px is None or pd.isna(open_px):
                    open_px = prices.get(tk, {}).get(today)
                if open_px is None or pd.isna(open_px):
                    still_pending.append(entry)  # keep trying tomorrow
                    continue
                # Execute the sell at Open
                gross = pos["shares"] * open_px
                extra_slip = 0.0
                if exit_slippage_tiered and liquidity_lookup:
                    liq = liquidity_lookup.get((tk, today)) or 0
                    if liq > 0:
                        pct_of_adv = gross / liq
                        if pct_of_adv > 0.20:    extra_slip = 0.005
                        elif pct_of_adv > 0.10:  extra_slip = 0.003
                        elif pct_of_adv > 0.05:  extra_slip = 0.001
                effective_sell_factor = sell_cost_factor * (1 - extra_slip)
                proceeds = gross * effective_sell_factor
                cash += proceeds
                ret_gross = (open_px / pos["entry_price"]) - 1
                ret_net = (proceeds / pos["cost_basis"]) - 1
                trades.append({
                    "ticker": tk, "entry_date": pos["entry_date"], "exit_date": today,
                    "entry_price": pos["entry_price"], "exit_price": open_px,
                    "ret_gross": ret_gross, "ret_net": ret_net,
                    "reason": reason, "days_held": pos["days_held"],
                    "play_type": pos.get("play_type", "?"),
                    "exit_extra_slip": extra_slip,
                })
                # Event log: capture SELL fill
                # Semantics (per user 2026-05-18):
                #   sell_amount = shares × market price (CLEAN gross, before fees+tax)
                #   fee         = TC_sell + CG_TAX + tiered_slip (deducted from gross)
                #   cash_after  = cash AFTER fees deducted = cash + (sell_amount - fee)
                # → sell_amount - fee = proceeds = cash added to balance
                if event_log is not None:
                    fee = gross - proceeds  # TC_sell + CG_tax + slip
                    event_log.append({
                        "ymd": today, "ticker": tk, "action": "sell",
                        "buy_amount": 0.0,
                        "sell_amount": float(gross),
                        "fee": float(max(fee, 0.0)),
                        "adj_price": float(open_px),
                        "shares": float(pos["shares"]),
                        "holding_id": pos.get("holding_id", f"{tk}_{pos['entry_date'].strftime('%Y%m%d')}_?"),
                        "play_type": pos.get("play_type", "?"),
                        "cash_after": float(cash),
                        "reason": reason,
                    })
                if reentry_blacklist_days > 0 and reason in ("STOP", "TRAIL"):
                    blacklist[tk] = reentry_blacklist_days
                elif pt_blacklist_days > 0 and reason == "PROFIT_TARGET":
                    blacklist[tk] = pt_blacklist_days
                del positions[tk]
            pending_exits = still_pending

        # 1) Mark-to-market positions, increment days_held, track peak
        for tk, pos in positions.items():
            cur_price = prices.get(tk, {}).get(today)
            if cur_price is not None and not pd.isna(cur_price):
                pos["last_price"] = cur_price
                if cur_price > pos.get("peak_price", pos["entry_price"]):
                    pos["peak_price"] = cur_price
            pos["days_held"] += 1
            pos.setdefault("peak_price", pos["entry_price"])
            pos.setdefault("partial_taken", set())

        # State-transition exit: if today's state triggers exit, mark positions
        today_state = None
        state_exit_frac = 0.0
        if state_by_date is not None and state_exit_map is not None:
            today_state = state_by_date.get(today)
            if today_state is not None and int(today_state) in state_exit_map:
                state_exit_frac = state_exit_map[int(today_state)]

        # 2) Check exits (only after MIN_HOLD)
        to_close = []
        partial_sells = []  # (tk, fraction, threshold)
        # If full state exit triggered, close all eligible positions
        if state_exit_frac >= 1.0:
            for tk, pos in positions.items():
                if pos["days_held"] >= min_hold:
                    to_close.append((tk, f"STATE_EXIT_S{today_state}"))
        elif state_exit_frac > 0:
            # Partial state exit: close fraction of each position
            for tk, pos in positions.items():
                if pos["days_held"] >= min_hold:
                    if state_exit_frac not in pos.get("partial_taken", set()):
                        partial_sells.append((tk, state_exit_frac,
                                              -100 - int(today_state)))  # unique marker

        # Mode-flip force close (switched books): liquidate outgoing-mode tiers for real
        if force_close_tiers_dates is not None:
            _fc = force_close_tiers_dates.get(today)
            if _fc:
                for tk, pos in positions.items():
                    if (pos.get("play_type") in _fc and pos["days_held"] >= min_hold
                            and not any(t == tk for t, _ in to_close)):
                        to_close.append((tk, "MODE_FLIP"))
                pending_entries = [p for p in pending_entries if p["play_type"] not in _fc]

        for tk, pos in positions.items():
            if pos["days_held"] < min_hold:
                continue  # T+3 rule: cannot sell yet
            if any(t == tk for t, _ in to_close):
                continue  # already in state-exit list
            ret = (pos["last_price"] / pos["entry_price"]) - 1
            ret_from_peak = (pos["last_price"] / pos["peak_price"]) - 1

            # Time exit (uses per-position cap if state-conditional, else global hold_days)
            pos_hold_cap = pos.get("hold_days_cap", hold_days)
            if pos["days_held"] >= pos_hold_cap:
                to_close.append((tk, "TIME"))
                continue
            # Committed-sleeve tiers (e.g. CAPIT) hold through the flush: no stop, no trim
            _stop_exempt = (stop_exempt_tiers is not None
                            and pos.get("play_type") in stop_exempt_tiers)
            # per-tier hard stop (e.g. liquid custom30 capit): overrides exempt, uses its own level
            _tier_stop = stop_by_tier.get(pos.get("play_type")) if stop_by_tier else None
            _eff_stop = _tier_stop if _tier_stop is not None else stop_loss
            _stop_active = (_tier_stop is not None) or (not _stop_exempt)
            # Intraday-low stop (Rule 3) — fires when today's daily Low touches stop_lvl
            # Fill at stop_lvl (assumes limit-sell fills exactly at stop)
            if stop_mode == "INTRADAY_LOW" and lows is not None and _stop_active:
                today_low = lows.get(tk, {}).get(today)
                if today_low is not None and not pd.isna(today_low):
                    stop_lvl = pos["entry_price"] * (1 + _eff_stop)
                    if today_low <= stop_lvl:
                        pos["last_price"] = stop_lvl   # exit fill at stop level
                        to_close.append((tk, "STOP_INTRADAY"))
                        continue
            # Hard stop (close-based, default)
            if ret <= _eff_stop and _stop_active:
                to_close.append((tk, "STOP"))
                continue
            # Soft-stop partial trim — fire when ret crosses trim threshold AND not yet triggered
            if soft_stop_partial is not None and not _stop_exempt:
                _trim_thr, _trim_frac = soft_stop_partial
                _trim_key = f"_softstop_{_trim_thr}"
                if ret <= _trim_thr and _trim_key not in pos.get("partial_taken", set()):
                    partial_sells.append((tk, _trim_frac, _trim_thr))

            # Profit target exit (full close, recycle capital)
            if profit_target is not None and ret >= profit_target:
                to_close.append((tk, "PROFIT_TARGET"))
                continue
            # Trailing stop (activated only after target gain)
            if (trailing_stop_activate is not None and trailing_stop_pct is not None
                and ret >= trailing_stop_activate
                and ret_from_peak <= -trailing_stop_pct):
                to_close.append((tk, "TRAIL"))
                continue
            # Partial profit-taking
            if partial_take_at is not None:
                for thr, frac in partial_take_at:
                    if ret >= thr and thr not in pos["partial_taken"]:
                        partial_sells.append((tk, frac, thr))

        # 3a) Execute partial sells first (reduce position size, keep position open)
        for tk, frac, thr in partial_sells:
            if tk not in positions:
                continue
            pos = positions[tk]
            cur_price = pos["last_price"]
            shares_to_sell = pos["shares"] * frac
            gross = shares_to_sell * cur_price
            proceeds = gross * sell_cost_factor
            cost_sold = pos["cost_basis"] * frac
            cash += proceeds
            ret_gross = (cur_price / pos["entry_price"]) - 1
            ret_net = (proceeds / cost_sold) - 1
            # Reason label: state-exit uses large negative marker (< -1); soft-stop is small negative (-1..0); profit is positive
            if thr < -1:
                reason_label = f"STATE_PARTIAL_S{int(-thr - 100)}"
            elif thr < 0:
                reason_label = f"SOFT_STOP_{int(thr*100)}"
            else:
                reason_label = f"PARTIAL_{int(thr*100)}"
            trades.append({
                "ticker": tk, "entry_date": pos["entry_date"], "exit_date": today,
                "entry_price": pos["entry_price"], "exit_price": cur_price,
                "ret_gross": ret_gross, "ret_net": ret_net,
                "reason": reason_label, "days_held": pos["days_held"],
                "play_type": pos.get("play_type", "?"),
            })
            # Event log: capture this PARTIAL SELL fill
            if event_log is not None:
                fee = gross - proceeds
                event_log.append({
                    "ymd": today, "ticker": tk, "action": "sell",
                    "buy_amount": 0.0,
                    "sell_amount": float(gross),
                    "fee": float(max(fee, 0.0)),
                    "adj_price": float(cur_price),
                    "shares": float(shares_to_sell),
                    "holding_id": pos.get("holding_id", f"{tk}_{pos['entry_date'].strftime('%Y%m%d')}_?"),
                    "play_type": pos.get("play_type", "?"),
                    "cash_after": float(cash),
                    "reason": reason_label,
                })
            pos["shares"] *= (1 - frac)
            pos["cost_basis"] *= (1 - frac)
            # Soft-stop uses a string key to allow multiple thresholds; profit uses raw thr
            if thr < 0 and thr > -1:
                pos["partial_taken"].add(f"_softstop_{thr}")
            else:
                pos["partial_taken"].add(thr)

        # 3b) Execute full close
        # T+1 OPEN EXEC MODE: defer exits to next session's Open (realistic timing)
        if t1_open_exec:
            for tk, reason in to_close:
                pending_exits.append({"ticker": tk, "reason": reason,
                                      "trigger_date": today})
            to_close = []  # do not execute today

        for tk, reason in to_close:
            pos = positions[tk]
            cur_price = pos["last_price"]
            gross = pos["shares"] * cur_price
            # Tiered exit slippage based on position size vs ADV
            extra_slip = 0.0
            if exit_slippage_tiered and liquidity_lookup:
                liq = liquidity_lookup.get((tk, today)) or 0
                if liq > 0:
                    pct_of_adv = gross / liq
                    if pct_of_adv > 0.20:
                        extra_slip = 0.005    # +0.5% (>20% ADV)
                    elif pct_of_adv > 0.10:
                        extra_slip = 0.003    # +0.3% (>10% ADV)
                    elif pct_of_adv > 0.05:
                        extra_slip = 0.001    # +0.1% (>5% ADV)
            effective_sell_factor = sell_cost_factor * (1 - extra_slip)
            proceeds = gross * effective_sell_factor
            cash += proceeds
            ret_gross = (cur_price / pos["entry_price"]) - 1
            ret_net = (proceeds / pos["cost_basis"]) - 1
            trades.append({
                "ticker": tk, "entry_date": pos["entry_date"], "exit_date": today,
                "entry_price": pos["entry_price"], "exit_price": cur_price,
                "ret_gross": ret_gross, "ret_net": ret_net,
                "reason": reason, "days_held": pos["days_held"],
                "play_type": pos.get("play_type", "?"),
                "exit_extra_slip": extra_slip,
            })
            # Event log: legacy T-close SELL (only runs when t1_open_exec=False)
            if event_log is not None:
                fee = gross - proceeds
                event_log.append({
                    "ymd": today, "ticker": tk, "action": "sell",
                    "buy_amount": 0.0,
                    "sell_amount": float(gross),
                    "fee": float(max(fee, 0.0)),
                    "adj_price": float(cur_price),
                    "shares": float(pos["shares"]),
                    "holding_id": pos.get("holding_id", f"{tk}_{pos['entry_date'].strftime('%Y%m%d')}_?"),
                    "play_type": pos.get("play_type", "?"),
                    "cash_after": float(cash),
                    "reason": reason,
                })
            # Add to blacklist if STOP/TRAIL exit
            if reentry_blacklist_days > 0 and reason in ("STOP", "TRAIL"):
                blacklist[tk] = reentry_blacklist_days
            # Profit-target re-entry blacklist (independent, default 0 = re-enter freely)
            elif pt_blacklist_days > 0 and reason == "PROFIT_TARGET":
                blacklist[tk] = pt_blacklist_days
            del positions[tk]

        # Decrement blacklist counters
        if blacklist:
            blacklist = {tk: d - 1 for tk, d in blacklist.items() if d > 1}

        # 4) Cash earns deposit rate (parameterized; default 0%/yr; set positive to enable)
        #    Negative cash (margin) charged borrow_annual (default 10%/yr per CLAUDE.md cost model).
        #    _interest_today = the cash change from interest (no tx row); recorded so the per-session
        #    cash-flow self-check can reconcile it (>0 = deposit earned, <0 = borrow interest paid).
        _cash_pre_int = cash
        if cash > 0 and deposit_annual > 0:
            cash *= (1 + deposit_annual / 252)
        if cash < 0 and borrow_annual > 0:
            cash *= (1 + borrow_annual / 252)  # cash<0 grows MORE negative (interest expense)
        _interest_today = cash - _cash_pre_int

        # 4b) ETF management fee / tracking drag — applied as shares shrink on each lot
        # (Daily MTM happens via _etf_mark on demand; no separate compounding step.)
        if etf_lots and (etf_mgmt_fee_annual > 0 or etf_tracking_drag_annual > 0):
            decay = (1 - etf_mgmt_fee_annual / 252) * (1 - etf_tracking_drag_annual / 252)
            for lot in etf_lots:
                lot["shares"] *= decay

        # 4c) ETF PRE-FILL SELL — only releases ETF when state target drops below current
        #     allocation (e.g., state transitions BULL->CRISIS, etf_frac 1.0->0.0).
        #     BA-deal-first semantics (user 2026-05-23): ETF is a parking lot for IDLE
        #     cash. The matching post-fill BUY block (step 6b below) sweeps leftover
        #     cash to ETF AFTER BA fills. During BA fills (step 5), JIT sell unwinds
        #     ETF on demand if cash short. Net effect: deals get priority, ETF holds
        #     only the remainder. This block is SELL-only.
        if cash_etf_states is not None and state_by_date is not None:
            today_state_int = int(state_by_date.get(today, 3)) if state_by_date.get(today) is not None else None
            if today_state_int is not None:
                _etf_map = (cash_etf_states_by_date.get(today, cash_etf_states)
                            if cash_etf_states_by_date is not None else cash_etf_states)
                etf_frac = _etf_map.get(today_state_int, 0.0)
                current_etf_value = _etf_mark(today)
                total_cash_pool = cash + current_etf_value
                target_etf = total_cash_pool * etf_frac
                delta = target_etf - current_etf_value
                px = vn30_underlying.get(today) if vn30_underlying is not None else None
                px_ok = px is not None and not pd.isna(px) and px > 0
                # SELL only (delta < 0 means current ETF > target → reduce)
                if delta < -total_cash_pool * 0.005 and px_ok:
                    px_f = float(px)
                    sell_vnd_target = min(-delta, _etf_day_cap(today))   # cap by ETF daily liquidity
                    friction = sell_vnd_target * etf_rebalance_friction
                    shares_to_sell = sell_vnd_target / px_f
                    remaining = shares_to_sell
                    new_lots = []
                    sold = []   # list of (lot_ref, sold_shares, sold_vnd, sold_cost)
                    for lot in etf_lots:
                        if remaining <= 1e-9:
                            new_lots.append(lot)
                            continue
                        if lot["shares"] <= remaining + 1e-9:
                            s = lot["shares"]
                            sold.append((lot, s, s * px_f, lot["cost_basis"]))
                            remaining -= s
                        else:
                            frac = remaining / lot["shares"]
                            s = remaining
                            sold_cost = lot["cost_basis"] * frac
                            sold.append((lot, s, s * px_f, sold_cost))
                            new_lots.append({
                                **lot,
                                "shares": lot["shares"] - s,
                                "cost_basis": lot["cost_basis"] - sold_cost,
                            })
                            remaining = 0
                    etf_lots = new_lots
                    total_sold_vnd = sum(x[2] for x in sold)
                    cash = cash + total_sold_vnd - friction
                    if etf_log is not None and total_sold_vnd > 0:
                        for idx, (lot_ref, sold_shares, sold_vnd, sold_cost) in enumerate(sold):
                            lot_friction = friction * (sold_vnd / total_sold_vnd)
                            is_last = (idx == len(sold) - 1)
                            etf_log.append({
                                "ymd": today, "action": "sell_etf",
                                "amount_vnd": float(sold_vnd),
                                "shares": float(sold_shares),
                                "price_vn30": px_f,
                                "friction_cost": float(lot_friction),
                                "cash_after": float(cash) if is_last else None,
                                "cash_etf_after": float(_etf_mark(today)) if is_last else None,
                                "state": today_state_int,
                                "target_etf_frac": float(etf_frac),
                                "holding_id": lot_ref["holding_id"],
                                "lot_entry_date": lot_ref["entry_date"],
                                "lot_cost_basis": float(sold_cost),
                                "reason_tag": "PREFILL_STATE_REBAL",
                            })

        # 5) Execute pending entries (T+1+) — multi-day fill capable
        executed_today = []
        new_pending = []
        active = [p for p in pending_entries if p["exec_start_date"] <= today]
        future = [p for p in pending_entries if p["exec_start_date"] > today]

        def pri(item):
            return (-TIER_PRIORITY.get(item["play_type"], 0), -item["ta"])
        active.sort(key=pri)

        for entry in active:
            tk = entry["ticker"]
            play_type = entry["play_type"]
            if tk in positions:
                continue   # already entered
            if tk in blacklist:
                continue   # blacklisted

            # T+1 OPEN EXEC: prefer Open price for entry fill (more realistic)
            # Fallback to Close if Open unavailable for this date
            # Layer 3 buy-point research: if entry_alt_prices supplies an intraday-
            # derived fill (e.g. 11:15 LIM), use that in place of Open.
            px = None
            if entry_alt_prices is not None:
                px = entry_alt_prices.get(tk, {}).get(today)
                if px is None or pd.isna(px) or px <= 0:
                    px = None
            if px is None:
                if t1_open_exec and open_prices is not None:
                    px = open_prices.get(tk, {}).get(today)
                    if px is None or pd.isna(px) or px <= 0:
                        px = prices.get(tk, {}).get(today)  # fallback
                else:
                    px = prices.get(tk, {}).get(today)
            entry["days_filling"] += 1
            is_first_fill = entry["filled_shares"] == 0

            # No price today: carry over if window remaining
            if px is None or pd.isna(px) or px <= 0:
                if entry["days_filling"] < max_fill_days:
                    new_pending.append(entry)
                else:
                    if entry["filled_shares"] > 0:
                        _finalize_partial(entry, positions, tk, play_type,
                                          ticker_sector_map, vni_dates, today)
                        abandoned_partial += 1
                continue

            entry["last_seen_price"] = px

            # Sector limit (only at first fill).
            # D1: certain play_types (e.g. RE_BACKLOG_BUY) may be exempt — they can
            # slot beyond the per-sector cap to avoid displacing other sector-8 plays.
            _exempt = (sector_cap_exempt_tiers is not None
                       and play_type in sector_cap_exempt_tiers)
            # E3: per-tier concurrent cap (applies even when sector-exempt)
            if is_first_fill and tier_position_limit and play_type in tier_position_limit:
                same_tier = sum(1 for p in positions.values()
                                if p.get("play_type") == play_type)
                if same_tier >= tier_position_limit[play_type]:
                    continue
            if is_first_fill and ticker_sector_map and not _exempt:
                tk_sec = ticker_sector_map.get(tk)
                if tk_sec is not None:
                    same = sum(1 for p in positions.values() if p.get("sector") == tk_sec)
                    # Global limit
                    if sector_limit is not None and same >= sector_limit:
                        continue
                    # Per-sector specific limit
                    if sector_limit_per_sector and tk_sec in sector_limit_per_sector:
                        if same >= sector_limit_per_sector[tk_sec]:
                            continue

            # Slot check (only at first fill). Slot-exempt tiers (committed sleeves)
            # neither consume nor are blocked by max_positions; their own concurrency
            # is enforced via tier_position_limit above.
            _slot_exempt = (slot_exempt_tiers is not None and play_type in slot_exempt_tiers)
            if slot_exempt_tiers is not None:
                _n_slots = sum(1 for p in positions.values()
                               if p.get("play_type") not in slot_exempt_tiers)
            else:
                _n_slots = len(positions)
            if is_first_fill and not _slot_exempt and _n_slots >= max_positions:
                if not eviction:
                    continue
                cur_pri = TIER_PRIORITY.get(play_type, 0)
                evictable = [(tk2, p) for tk2, p in positions.items()
                             if p["days_held"] >= min_hold
                             and TIER_PRIORITY.get(p.get("play_type", "PASS"), 0) < cur_pri - eviction_priority_gap]
                if not evictable:
                    continue
                evictable.sort(key=lambda x: (TIER_PRIORITY.get(x[1].get("play_type", "PASS"), 0),
                                              -x[1]["days_held"]))
                evict_tk, evict_pos = evictable[0]
                evict_price = evict_pos["last_price"]
                evict_gross = evict_pos["shares"] * evict_price
                proceeds = evict_gross * sell_cost_factor
                cash += proceeds
                trades.append({
                    "ticker": evict_tk, "entry_date": evict_pos["entry_date"], "exit_date": today,
                    "entry_price": evict_pos["entry_price"], "exit_price": evict_price,
                    "ret_gross": (evict_price/evict_pos["entry_price"])-1,
                    "ret_net": (proceeds/evict_pos["cost_basis"])-1,
                    "reason": "EVICT", "days_held": evict_pos["days_held"],
                    "play_type": evict_pos.get("play_type", "?"),
                })
                # Event log: capture EVICT SELL
                if event_log is not None:
                    fee = evict_gross - proceeds
                    event_log.append({
                        "ymd": today, "ticker": evict_tk, "action": "sell",
                        "buy_amount": 0.0,
                        "sell_amount": float(evict_gross),
                        "fee": float(max(fee, 0.0)),
                        "adj_price": float(evict_price),
                        "shares": float(evict_pos["shares"]),
                        "holding_id": evict_pos.get("holding_id", f"{evict_tk}_{evict_pos['entry_date'].strftime('%Y%m%d')}_?"),
                        "play_type": evict_pos.get("play_type", "?"),
                        "cash_after": float(cash),
                        "reason": "EVICT",
                    })
                del positions[evict_tk]

            # Compute target_value at first fill (include pending fills + ETF parking in NAV)
            # NOTE (2026-05-23 fix): cur_nav now includes cash_etf (was excluded → bug
            # under high ETF allocation: target_value collapsed to 0 because NAV looked
            # tiny, BA buys silently skipped. With JIT sell on demand, ETF value IS
            # liquid and should count toward NAV for tier-sizing purposes.)
            if is_first_fill:
                cur_pos_mv = sum(p["shares"] * p["last_price"] for p in positions.values())
                pending_mv = sum(p["filled_shares"] * p.get("last_seen_price", 0)
                                 for p in pending_entries if p["filled_shares"] > 0)
                cash_etf_now = _etf_mark(today)
                cur_nav = cash + cash_etf_now + cur_pos_mv + pending_mv
                # Tier-based weight if tier_weights provided, else equal-weight
                # State-conditional override: tier_weights_by_state[state] takes precedence
                effective_tw = tier_weights
                _suppress = (regime_suppress_dates is not None and today in regime_suppress_dates)
                if tier_weights_by_state is not None and state_by_date is not None and not _suppress:
                    _st = state_by_date.get(today)
                    if _st is not None and int(_st) in tier_weights_by_state:
                        effective_tw = tier_weights_by_state[int(_st)]
                if effective_tw is not None and play_type in effective_tw:
                    target_value = cur_nav * effective_tw[play_type]
                else:
                    target_value = cur_nav / max_positions
                # JIT sell ETF if cash insufficient for this BA buy (user 2026-05-23:
                # "cần cash thì bán etf đúng bằng lượng cần"). FIFO sell exactly the
                # shortfall amount. Friction at etf_rebalance_friction.
                if cash < target_value * 0.99 and etf_lots and cash_etf_states is not None:
                    needed = min(target_value - max(cash, 0), _etf_day_cap(today))  # cap by ETF daily liquidity
                    px_jit = vn30_underlying.get(today) if vn30_underlying is not None else None
                    if px_jit is not None and not pd.isna(px_jit) and px_jit > 0 and needed > 0:
                        px_f_jit = float(px_jit)
                        shares_to_sell_jit = needed / px_f_jit
                        remaining_jit = shares_to_sell_jit
                        new_lots_jit = []
                        sold_jit = []
                        for lot in etf_lots:
                            if remaining_jit <= 1e-9:
                                new_lots_jit.append(lot); continue
                            if lot["shares"] <= remaining_jit + 1e-9:
                                s = lot["shares"]
                                sold_jit.append((lot, s, s * px_f_jit, lot["cost_basis"]))
                                remaining_jit -= s
                            else:
                                frac_jit = remaining_jit / lot["shares"]
                                s = remaining_jit
                                sold_cost_jit = lot["cost_basis"] * frac_jit
                                sold_jit.append((lot, s, s * px_f_jit, sold_cost_jit))
                                new_lots_jit.append({**lot,
                                    "shares": lot["shares"] - s,
                                    "cost_basis": lot["cost_basis"] - sold_cost_jit})
                                remaining_jit = 0
                        etf_lots = new_lots_jit
                        total_sold_vnd_jit = sum(x[2] for x in sold_jit)
                        if total_sold_vnd_jit > 0:
                            friction_jit = total_sold_vnd_jit * etf_rebalance_friction
                            cash = cash + total_sold_vnd_jit - friction_jit
                            if etf_log is not None:
                                _st_jit = int(state_by_date.get(today, 3)) if (state_by_date and state_by_date.get(today) is not None) else None
                                for idx_jit, (lot_ref, sold_shares, sold_vnd, sold_cost) in enumerate(sold_jit):
                                    lot_friction_j = friction_jit * (sold_vnd / total_sold_vnd_jit)
                                    is_last_j = (idx_jit == len(sold_jit) - 1)
                                    etf_log.append({
                                        "ymd": today, "action": "sell_etf",
                                        "amount_vnd": float(sold_vnd),
                                        "shares": float(sold_shares),
                                        "price_vn30": px_f_jit,
                                        "friction_cost": float(lot_friction_j),
                                        "cash_after": float(cash) if is_last_j else None,
                                        "cash_etf_after": float(_etf_mark(today)) if is_last_j else None,
                                        "state": _st_jit,
                                        "target_etf_frac": None,
                                        "holding_id": lot_ref["holding_id"],
                                        "lot_entry_date": lot_ref["entry_date"],
                                        "lot_cost_basis": float(sold_cost),
                                        "reason_tag": "JIT_FOR_BA_BUY",
                                    })
                # Buying power: plain cash, or cash + margin room (V6-v3 style gross cap).
                # margin_tiers restricts the room to specific play_types (e.g. crisis-capit).
                _mg_ok = (max_gross_exposure is not None
                          and (margin_tiers is None or play_type in margin_tiers))
                _margin_room = ((max_gross_exposure - 1.0) *
                                (nav_history[-1]["nav"] if nav_history else nav_init)
                                if _mg_ok else 0.0)
                if cash + _margin_room < target_value * 0.99:
                    target_value = (cash + _margin_room) * 0.95
                if target_value < 1_000_000:
                    continue
                entry["target_value"] = target_value

            # Compute today's affordable buy
            remaining_value = entry["target_value"] - entry["filled_cost"]
            daily_max = remaining_value
            if liquidity_volume_pct is not None and liquidity_lookup is not None:
                liq = liquidity_lookup.get((tk, today))
                if liq and liq > 0:
                    daily_max = liq * liquidity_volume_pct
            _mg_ok2 = (max_gross_exposure is not None
                       and (margin_tiers is None or play_type in margin_tiers))
            _bp = cash + ((max_gross_exposure - 1.0) *
                          (nav_history[-1]["nav"] if nav_history else nav_init)
                          if _mg_ok2 else 0.0)
            buy_value = min(remaining_value, daily_max, _bp)

            if buy_value >= 100_000:
                buy_shares = buy_value / (px * buy_cost_factor)
                cost = buy_shares * px * buy_cost_factor
                cash -= cost
                entry["filled_shares"] += buy_shares
                entry["filled_cost"] += cost
                if entry["first_fill_date"] is None:
                    entry["first_fill_date"] = today
                # Event log: capture this BUY fill (one row per fill day for multi-day fills)
                # Semantics (per user 2026-05-18):
                #   buy_amount = shares × market price (CLEAN cost of shares, excludes fees)
                #   fee        = transaction cost + tax + slippage (added on top)
                #   cash_after = cash AFTER this fill (after buy_amount + fee deducted)
                # → buy_amount + fee = total cash deducted = `cost`
                if event_log is not None:
                    share_cost = buy_shares * px      # clean cost of shares
                    fee = cost - share_cost            # = share_cost × (buy_cost_factor - 1)
                    event_log.append({
                        "ymd": today, "ticker": tk, "action": "buy",
                        "buy_amount": float(share_cost),
                        "sell_amount": 0.0,
                        "fee": float(max(fee, 0.0)),
                        "adj_price": float(px),
                        "shares": float(buy_shares),
                        "holding_id": f"{tk}_{(entry['first_fill_date'] or today).strftime('%Y%m%d')}_{entry.get('seq_id', '?')}",
                        "play_type": play_type,
                        "cash_after": float(cash),
                        "reason": "ENTRY_FILL",
                    })

            # Check completion
            fill_pct = entry["filled_cost"] / entry["target_value"] if entry["target_value"] > 0 else 0
            done = (fill_pct >= 0.95) or (entry["days_filling"] >= max_fill_days)

            if not done:
                new_pending.append(entry)
            elif entry["filled_shares"] > 0 and fill_pct >= min_fill_pct:
                # Move to position
                avg_px = entry["filled_cost"] / entry["filled_shares"] / buy_cost_factor  # actual avg paid
                # State-conditional hold cap (fixed at entry; trend-following — entry regime decides hold)
                _entry_state = state_by_date.get(entry["first_fill_date"]) if state_by_date else None
                _hold_cap = (hold_days_by_state.get(int(_entry_state), hold_days)
                             if (hold_days_by_state and _entry_state is not None and not pd.isna(_entry_state))
                             else hold_days)
                # Per-tier override (committed sleeves, e.g. CAPIT 60d) takes precedence
                if hold_days_by_tier and play_type in hold_days_by_tier:
                    _hold_cap = hold_days_by_tier[play_type]
                positions[tk] = {
                    "entry_price": avg_px,
                    "entry_date": entry["first_fill_date"],
                    "shares": entry["filled_shares"],
                    "days_held": (vni_dates.index(today) - vni_dates.index(entry["first_fill_date"])),
                    "last_price": px,
                    "peak_price": max(px, avg_px),
                    "cost_basis": entry["filled_cost"],
                    "play_type": play_type,
                    "sector": ticker_sector_map.get(tk) if ticker_sector_map else None,
                    "partial_taken": set(),
                    "holding_id": f"{tk}_{entry['first_fill_date'].strftime('%Y%m%d')}_{entry['seq_id']}",
                    "hold_days_cap": _hold_cap,
                }
                executed_today.append(tk)
            else:
                # Abandoned: refund any tiny partial (sell back filled_shares at today's px)
                # NNC bug fix (2026-05-18): previously this refund was silent — no
                # event_log entry — so analyze_portfolio.py saw orphan buys with
                # no matching sell. Now logged as a SELL with reason=ABANDONED_REFUND
                # and the same holding_id as the buys, so analyze_portfolio groups them.
                if entry["filled_shares"] > 0:
                    refund_shares = entry["filled_shares"]
                    refund_gross = refund_shares * px
                    refund_proceeds = refund_gross * sell_cost_factor
                    cash += refund_proceeds
                    if event_log is not None:
                        fee = refund_gross - refund_proceeds
                        first_fd = entry["first_fill_date"] or today
                        event_log.append({
                            "ymd": today, "ticker": tk, "action": "sell",
                            "buy_amount": 0.0,
                            "sell_amount": float(refund_gross),
                            "fee": float(max(fee, 0.0)),
                            "adj_price": float(px),
                            "shares": float(refund_shares),
                            "holding_id": f"{tk}_{first_fd.strftime('%Y%m%d')}_{entry.get('seq_id', '?')}",
                            "play_type": play_type,
                            "cash_after": float(cash),
                            "reason": "ABANDONED_REFUND",
                        })
                skipped_for_liquidity += 1

        pending_entries = future + new_pending

        # 6) Look at TODAY's signals → queue for T+1 execution (new dict format)
        if today in sig_by_date and len(positions) + len(pending_entries) < max_positions * 3:
            next_idx = i + 1
            if next_idx < len(vni_dates):
                exec_date = vni_dates[next_idx]
                todays_sig = sig_by_date[today].copy()
                todays_sig["_pri"] = todays_sig["play_type"].map(TIER_PRIORITY).fillna(0)
                todays_sig = todays_sig.sort_values(["_pri", "ta"], ascending=[False, False])
                held_or_pending = set(positions.keys()) | {p["ticker"] for p in pending_entries}
                for _, sig in todays_sig.iterrows():
                    if sig["ticker"] in held_or_pending:
                        continue
                    _entry_seq += 1
                    pending_entries.append({
                        "ticker": sig["ticker"],
                        "exec_start_date": exec_date,
                        "play_type": sig["play_type"],
                        "ta": sig["ta"],
                        "signal_close": sig["Close"],
                        "target_value": 0,    # set on first fill
                        "target_shares": 0,
                        "filled_shares": 0,
                        "filled_cost": 0,
                        "days_filling": 0,
                        "first_fill_date": None,
                        "last_seen_price": sig["Close"],
                        "seq_id": _entry_seq,
                    })
                    held_or_pending.add(sig["ticker"])
                    if len(pending_entries) + len(positions) >= max_positions * 3:
                        break

        # 6b) ETF POST-FILL SWEEP — park leftover idle cash up to state target.
        #      Pairs with the SELL-only prefill block 4c. This sweep is the only
        #      ETF BUY path. Honors state target (etf_frac × pool) as ceiling for
        #      total ETF allocation, but never spends more cash than available.
        if cash_etf_states is not None and state_by_date is not None and cash > 0:
            today_state_int_pb = int(state_by_date.get(today, 3)) if state_by_date.get(today) is not None else None
            if today_state_int_pb is not None:
                _etf_map_pb = (cash_etf_states_by_date.get(today, cash_etf_states)
                               if cash_etf_states_by_date is not None else cash_etf_states)
                etf_frac_pb = _etf_map_pb.get(today_state_int_pb, 0.0)
                if etf_frac_pb > 0:
                    current_etf_value_pb = _etf_mark(today)
                    total_cash_pool_pb = cash + current_etf_value_pb
                    target_etf_pb = total_cash_pool_pb * etf_frac_pb
                    delta_pb = target_etf_pb - current_etf_value_pb
                    px_pb = vn30_underlying.get(today) if vn30_underlying is not None else None
                    px_ok_pb = px_pb is not None and not pd.isna(px_pb) and px_pb > 0
                    if delta_pb > total_cash_pool_pb * 0.005 and px_ok_pb:
                        buy_amt = min(delta_pb, cash, _etf_day_cap(today))  # cap by ETF daily liquidity
                        if buy_amt > total_cash_pool_pb * 0.005:
                            px_f_pb = float(px_pb)
                            friction_pb = buy_amt * etf_rebalance_friction
                            _etf_lot_seq[0] += 1
                            shares_pb = buy_amt / px_f_pb
                            lot_hid_pb = f"E1VFVN30_{name}_{today.strftime('%Y%m%d')}_{_etf_lot_seq[0]}"
                            etf_lots.append({
                                "entry_date": today,
                                "shares": float(shares_pb),
                                "cost_basis": float(buy_amt),
                                "last_px": px_f_pb,
                                "holding_id": lot_hid_pb,
                            })
                            cash = cash - buy_amt - friction_pb
                            if etf_log is not None:
                                etf_log.append({
                                    "ymd": today, "action": "buy_etf",
                                    "amount_vnd": float(buy_amt),
                                    "shares": float(shares_pb),
                                    "price_vn30": px_f_pb,
                                    "friction_cost": float(friction_pb),
                                    "cash_after": float(cash),
                                    "cash_etf_after": float(_etf_mark(today)),
                                    "state": today_state_int_pb,
                                    "target_etf_frac": float(etf_frac_pb),
                                    "holding_id": lot_hid_pb,
                                    "lot_entry_date": today,
                                    "lot_cost_basis": float(buy_amt),
                                    "reason_tag": "POST_FILL_SWEEP",
                                })

        # 7) Record NAV (include pending partial fills + ETF mark-to-market)
        positions_mv = sum(p["shares"] * p["last_price"] for p in positions.values())
        pending_mv = sum(p["filled_shares"] * p.get("last_seen_price", 0)
                         for p in pending_entries if p["filled_shares"] > 0)
        cash_etf_val = _etf_mark(today)
        nav = cash + cash_etf_val + positions_mv + pending_mv
        nav_history.append({
            "time": today, "nav": nav,
            "cash": float(cash),
            "cash_etf": float(cash_etf_val),
            "positions_mv": float(positions_mv),
            "pending_mv": float(pending_mv),
            "n_pos": len(positions), "n_pending": len(pending_entries),
            "n_etf_lots": len(etf_lots),
            "cash_pct": cash / nav * 100 if nav > 0 else 0,
            "cash_etf_pct": cash_etf_val / nav * 100 if nav > 0 else 0,
            "deployed_pct": (positions_mv + pending_mv) / nav * 100 if nav > 0 else 0,
            "interest": float(_interest_today),   # deposit/borrow interest (no tx row) — for self-check reconcile
            "state": state_by_date.get(today) if state_by_date else None,
        })

    # Force close any remaining at end (only if force_close_eod=True)
    last_day = vni_dates[-1]
    open_positions_final = []
    etf_lots_final = []
    if force_close_eod:
        for tk, pos in list(positions.items()):
            cur = pos["last_price"]
            gross = pos["shares"] * cur
            proceeds = gross * sell_cost_factor
            cash += proceeds
            ret_gross = (cur / pos["entry_price"]) - 1
            ret_net = (proceeds / pos["cost_basis"]) - 1
            trades.append({
                "ticker": tk, "entry_date": pos["entry_date"], "exit_date": last_day,
                "entry_price": pos["entry_price"], "exit_price": cur,
                "ret_gross": ret_gross, "ret_net": ret_net,
                "reason": "EOD", "days_held": pos["days_held"],
                "play_type": pos.get("play_type", "?"),
            })
            if event_log is not None:
                fee = gross - proceeds
                event_log.append({
                    "ymd": last_day, "ticker": tk, "action": "sell",
                    "buy_amount": 0.0, "sell_amount": float(gross),   # clean gross (excl fees)
                    "fee": float(max(fee, 0.0)),
                    "adj_price": float(cur), "shares": float(pos["shares"]),
                    "holding_id": pos.get("holding_id", f"{tk}_{pos['entry_date'].strftime('%Y%m%d')}_?"),
                    "play_type": pos.get("play_type", "?"),
                    "cash_after": float(cash), "reason": "EOD",
                })
        # Liquidate ETF lots at EOD too
        last_px = vn30_underlying.get(last_day) if vn30_underlying is not None else None
        if etf_lots and last_px is not None and not pd.isna(last_px) and last_px > 0:
            last_px_f = float(last_px)
            for lot in etf_lots:
                gross = lot["shares"] * last_px_f
                cash += gross
                if etf_log is not None:
                    etf_log.append({
                        "ymd": last_day, "action": "sell_etf",
                        "amount_vnd": float(gross),
                        "shares": float(lot["shares"]),
                        "price_vn30": last_px_f,
                        "friction_cost": 0.0,
                        "cash_after": float(cash),
                        "cash_etf_after": 0.0,
                        "state": None,
                        "target_etf_frac": 0.0,
                        "holding_id": lot["holding_id"],
                        "lot_entry_date": lot["entry_date"],
                        "lot_cost_basis": float(lot["cost_basis"]),
                    })
            etf_lots = []
    else:
        # Keep positions open — record their final state for unrealized P&L
        for tk, pos in positions.items():
            cur = pos["last_price"]
            mark_value = pos["shares"] * cur
            unrealised_gross = mark_value - pos["cost_basis"]
            ret_unrealised = (cur / pos["entry_price"]) - 1
            open_positions_final.append({
                "ticker": tk, "entry_date": pos["entry_date"], "last_date": last_day,
                "entry_price": pos["entry_price"], "last_price": cur,
                "shares": pos["shares"], "cost_basis": pos["cost_basis"],
                "mark_value": mark_value, "unrealised_pnl": unrealised_gross,
                "unrealised_ret_pct": ret_unrealised * 100,
                "days_held": pos["days_held"], "play_type": pos.get("play_type", "?"),
                "holding_id": pos.get("holding_id", "?"),
            })
        # Snapshot ETF lots — REAL entry_dates (no hallucination)
        last_px = vn30_underlying.get(last_day) if vn30_underlying is not None else None
        last_px_f = (float(last_px) if last_px is not None and not pd.isna(last_px) and last_px > 0
                     else None)
        for lot in etf_lots:
            px_for_mark = last_px_f if last_px_f is not None else lot.get("last_px", 0.0)
            mark_value = lot["shares"] * px_for_mark
            unrealised = mark_value - lot["cost_basis"]
            etf_lots_final.append({
                "ticker": "E1VFVN30",
                "holding_id": lot["holding_id"],
                "entry_date": lot["entry_date"],
                "last_date": last_day,
                "entry_price": None,        # ETF buys denominated in VND, not shares
                "last_price": px_for_mark,
                "shares": float(lot["shares"]),
                "cost_basis": float(lot["cost_basis"]),
                "mark_value": float(mark_value),
                "unrealised_pnl": float(unrealised),
                "unrealised_ret_pct": (unrealised / lot["cost_basis"] * 100) if lot["cost_basis"] > 0 else 0.0,
                "days_held": (last_day - lot["entry_date"]).days,
                "play_type": "ETF_PARK",
            })

    nav_df = pd.DataFrame(nav_history)
    trades_df = pd.DataFrame(trades)
    if not force_close_eod:
        # Attach open positions snapshot as attribute for caller
        nav_df.attrs["open_positions_final"] = pd.DataFrame(open_positions_final)
        nav_df.attrs["etf_lots_final"] = pd.DataFrame(etf_lots_final)
    return nav_df, trades_df


def metrics(nav_df, trades_df, name):
    nav = nav_df["nav"]
    times = pd.to_datetime(nav_df["time"])
    n_days = (times.iloc[-1] - times.iloc[0]).days
    n_yrs = n_days / 365.25
    total_ret = nav.iloc[-1] / nav.iloc[0] - 1
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1 / n_yrs) - 1 if n_yrs > 0 else 0

    rets = nav.pct_change().dropna()
    sessions_per_year = len(rets) / n_yrs if n_yrs > 0 else 252
    sharpe = (rets.mean() / rets.std() * np.sqrt(sessions_per_year)) if rets.std() > 0 else 0
    downside = rets[rets < 0]
    sortino = (rets.mean() / downside.std() * np.sqrt(sessions_per_year)) if len(downside) and downside.std() > 0 else 0

    peak = nav.cummax()
    dd = (nav - peak) / peak
    max_dd = dd.min()
    calmar = (cagr / abs(max_dd)) if max_dd < 0 else 0

    n_trades = len(trades_df)
    if n_trades:
        ret_col = "ret_net" if "ret_net" in trades_df.columns else "ret"
        win_rate = (trades_df[ret_col] > 0).mean() * 100
        avg_ret = trades_df[ret_col].mean() * 100
        avg_hold = trades_df["days_held"].mean()
        stop_pct = (trades_df["reason"] == "STOP").mean() * 100
        time_pct = (trades_df["reason"] == "TIME").mean() * 100
    else:
        win_rate = avg_ret = avg_hold = stop_pct = time_pct = 0

    return {
        "name": name,
        "n_yrs": n_yrs,
        "total_ret_pct": total_ret * 100,
        "cagr_pct": cagr * 100,
        "sharpe": sharpe,
        "sortino": sortino,
        "max_dd_pct": max_dd * 100,
        "calmar": calmar,
        "n_trades": n_trades,
        "trades_per_year": n_trades / n_yrs if n_yrs > 0 else 0,
        "win_rate_pct": win_rate,
        "avg_trade_ret_pct": avg_ret,
        "avg_hold_days": avg_hold,
        "stop_pct": stop_pct,
        "time_pct": time_pct,
    }


def main():
    print("Loading signals + prices from BigQuery...")
    sig = bq(SIGNAL_QUERY.format(start=START_DATE, end=END_DATE))
    sig["time"] = pd.to_datetime(sig["time"])
    print(f"  {len(sig):,} signal rows")

    print("Loading VNINDEX baseline...")
    vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
    vni["time"] = pd.to_datetime(vni["time"])
    vni_dates = sorted(vni["time"].unique())
    print(f"  {len(vni_dates):,} trading days")

    # Build close-price lookup per ticker
    print("Building price lookup...")
    prices = {}
    for tk, g in sig.groupby("ticker"):
        prices[tk] = dict(zip(g["time"], g["Close"]))
    print(f"  {len(prices):,} tickers with price history")

    # Define strategies
    strategies = {
        "MEGA_only_3pos": {
            "tiers": ["MEGA"],
            "max_pos": 3,
        },
        "HIGH_CONV_5pos": {
            "tiers": ["MEGA", "MOMENTUM", "MOMENTUM_N"],
            "max_pos": 5,
        },
        "BALANCED_8pos": {
            "tiers": ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S",
                      "DEEP_VALUE_RECOVERY"],
            "max_pos": 8,
        },
    }

    results = {}
    for name, cfg in strategies.items():
        print(f"\nSimulating {name} (tiers={cfg['tiers']}, max_pos={cfg['max_pos']})...")
        nav_df, trades_df = simulate(sig, prices, vni_dates,
                                      allowed_tiers=cfg["tiers"],
                                      max_positions=cfg["max_pos"],
                                      name=name)
        m = metrics(nav_df, trades_df, name)
        results[name] = (nav_df, trades_df, m)
        print(f"  {m['n_trades']} trades, CAGR={m['cagr_pct']:.1f}%, "
              f"Sharpe={m['sharpe']:.2f}, MaxDD={m['max_dd_pct']:.1f}%, "
              f"WinRate={m['win_rate_pct']:.1f}%")

    # VNINDEX baseline
    print("\nComputing VNINDEX B&H baseline...")
    vni_nav = INIT_NAV * vni["Close"] / vni["Close"].iloc[0]
    vni_nav_df = pd.DataFrame({"time": vni["time"], "nav": vni_nav})
    vni_rets = vni_nav.pct_change().dropna()
    n_yrs = (vni["time"].iloc[-1] - vni["time"].iloc[0]).days / 365.25
    spy = len(vni_rets) / n_yrs
    vni_cagr = (vni_nav.iloc[-1] / vni_nav.iloc[0]) ** (1/n_yrs) - 1
    vni_sharpe = vni_rets.mean() / vni_rets.std() * np.sqrt(spy)
    vni_dd = (vni_nav - vni_nav.cummax()) / vni_nav.cummax()
    vni_metrics = {
        "name": "VNINDEX_BH",
        "n_yrs": n_yrs,
        "total_ret_pct": (vni_nav.iloc[-1] / vni_nav.iloc[0] - 1) * 100,
        "cagr_pct": vni_cagr * 100,
        "sharpe": vni_sharpe,
        "max_dd_pct": vni_dd.min() * 100,
        "calmar": vni_cagr / abs(vni_dd.min()) if vni_dd.min() < 0 else 0,
    }

    # ─── Print summary ───────────────────────────────────────────
    print("\n" + "═" * 100)
    print("  PORTFOLIO SIMULATION RESULTS  (T+1 exec, 0.1%/side TC, hold 60d, stop -15%)")
    print("═" * 100)
    cols = ["name", "n_yrs", "cagr_pct", "sharpe", "max_dd_pct", "calmar",
            "n_trades", "win_rate_pct", "avg_trade_ret_pct", "avg_hold_days"]
    rows = [results[k][2] for k in strategies] + [vni_metrics]
    rows_full = []
    for r in rows:
        full = {c: r.get(c, None) for c in cols}
        rows_full.append(full)
    summary = pd.DataFrame(rows_full)
    print(summary.to_string(index=False, float_format=lambda x: f"{x:.2f}"))

    # ─── Year-by-year NAV growth ─────────────────────────────────
    print("\n" + "═" * 100)
    print("  YEAR-BY-YEAR NAV (relative to start, in millions VND)")
    print("═" * 100)
    yr_table = pd.DataFrame()
    for name, (nav_df, _, _) in results.items():
        nav_df["yr"] = pd.to_datetime(nav_df["time"]).dt.year
        yr_end = nav_df.groupby("yr")["nav"].last() / 1e6
        yr_table[name] = yr_end
    yr_table["VNINDEX_BH"] = (INIT_NAV * vni["Close"] / vni["Close"].iloc[0] / 1e6).groupby(
        vni["time"].dt.year).last()
    print(yr_table.to_string(float_format=lambda x: f"{x:,.0f}"))

    # ─── Save outputs ─────────────────────────────────────────────
    for name, (nav_df, trades_df, m) in results.items():
        nav_df.to_csv(os.path.join(WORKDIR, f"sim_{name}_nav.csv"), index=False)
        trades_df.to_csv(os.path.join(WORKDIR, f"sim_{name}_trades.csv"), index=False)
    summary.to_csv(os.path.join(WORKDIR, "data/sim_holistic_summary.csv"), index=False)
    print("\nOutputs saved: sim_*_nav.csv, sim_*_trades.csv, sim_holistic_summary.csv")


if __name__ == "__main__":
    main()
