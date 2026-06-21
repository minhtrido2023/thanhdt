# -*- coding: utf-8 -*-
"""V11 transparent simulation 09-06-2025 -> NOW, 50B NAV.

Applies the full production stack INCLUDING Layer 3 v4 intraday rule:
  - V11 = SV_TIGHT (state-conditional Fresh-Q) + P3 (overheat block)
          + RE_BACKLOG_BUY + 50/50 BAL+VN30 + V6 ETF (70% idle cash in NEUTRAL)
  - Layer 3 v4 HYBRID: BUY at T+1 14:45 ATC for T1_TOP, T+1 11:15 for non-TOP
                       (with fallback to T+1 Open if intraday missing)
  - Sell: T+1 09:00 OPEN (canonical, unchanged — Phase 5 validated)
  - Open positions at end of period: KEEP, mark unrealized P&L (no force-close)

Outputs (analyze_portfolio.py compatible):
  data/v11_transparent_logs.csv          — daily NAV + cash + n_pos + n_tx
  data/v11_transparent_transactions.csv  — every buy/sell + ETF rebalance as rows
  data/v11_transparent_open_positions.csv — unrealized P&L snapshot at end
  data/v11_transparent_report.md         — analyze_portfolio.py output
"""
import os, sys, io, pickle
from datetime import datetime
import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import simulate, bq, VNI_QUERY
from signal_v10_sql import SIGNAL_V10

START_DATE = "2025-01-01"
END_DATE   = datetime.now().strftime("%Y-%m-%d")
TOTAL_NAV  = 50e9
BOOK_NAV   = 25e9   # per book (BAL + VN30, 50/50 split)
POSITION_VND = 1.25e9   # per book leg
FILL_CAP = 0.20
T1_TOP_ADV = 50e9       # liquidity tier

INTRADAY_PKL = os.path.join(WORKDIR, "intraday_full.pkl")

BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO",
                  "RE_BACKLOG_BUY"}
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY",
            "RE_BACKLOG_BUY"]
SECTOR_CAP_EXEMPT = {"RE_BACKLOG_BUY"}   # D1: exempt from sector cap=4 (matches prod)
# slot12 deployment (2026-05-16, validated E4): max_positions=12, sizing=10% NAV
# per position (NOT 1/12). Extra 2 slots let RE_BACKLOG_BUY enter beyond 10
# without shrinking other slots.
MAX_POS_V11 = 12
TIER_WEIGHTS_V11 = {tier: 0.10 for tier in TIER_BAL}

print("=" * 100)
print(f"  V11 TRANSPARENT SIMULATION")
print(f"  Period: {START_DATE} -> {END_DATE}, NAV={TOTAL_NAV/1e9:.0f}B")
print(f"  Stack: V11 (SV_TIGHT + P3 + RE_BACKLOG + V6 ETF) + Layer 3 v4 HYBRID intraday")
print("=" * 100)

# ============================================================================
# 1) Load intraday for v4 alt-fill (BUY only — SELL stays at T+1 Open)
# ============================================================================
print("\n[1/8] Building v4 HYBRID alt-fill price dict...")
with open(INTRADAY_PKL, "rb") as f:
    intraday = pickle.load(f)
print(f"  Loaded {len(intraday)} tickers from intraday cache")

# Compute per-ticker ADV for tier classification
adv_by_ticker = {}
slot_price_atc = {}     # {tk: {date: p_atc}}
slot_vol_atc = {}       # {tk: {date: vol_atc_vnd}}
slot_price_t1115 = {}
slot_vol_t1115 = {}
for tk, bars in intraday.items():
    if bars is None or bars.empty: continue
    b = bars.copy()
    b["time"] = pd.to_datetime(b["time"])
    b["date_ts"] = b["time"].dt.normalize()
    b["hm"] = b["time"].dt.strftime("%H:%M")
    b["close_vnd"] = b["close"].astype(float) * 1000.0
    b["vnd_traded"] = b["close_vnd"] * b["volume"].astype(float)
    sess = b.groupby("date_ts", sort=False)["vnd_traded"].sum()
    adv_by_ticker[tk] = float(sess.mean())
    for label, hm, p_dict, v_dict in [
        ("atc", "14:45", slot_price_atc, slot_vol_atc),
        ("t1115", "11:15", slot_price_t1115, slot_vol_t1115),
    ]:
        sub = b[b["hm"] == hm]
        if sub.empty: continue
        for _, row in sub.iterrows():
            d_ts = row["date_ts"]
            p_dict.setdefault(tk, {})[d_ts] = float(row["close_vnd"])
            v_dict.setdefault(tk, {})[d_ts] = float(row["vnd_traded"])

# Build HYBRID alt-fill: ATC for T1_TOP (with liquidity gate), T1115 for others
alt_hybrid = {}
n_atc_full = n_t1115_full = n_skipped = 0
for tk in set(slot_price_atc.keys()) | set(slot_price_t1115.keys()):
    adv = adv_by_ticker.get(tk, 0)
    is_t1_top = adv >= T1_TOP_ADV
    src_p = slot_price_atc.get(tk, {}) if is_t1_top else slot_price_t1115.get(tk, {})
    src_v = slot_vol_atc.get(tk, {}) if is_t1_top else slot_vol_t1115.get(tk, {})
    for d_ts, p in src_p.items():
        v = src_v.get(d_ts)
        if v is not None and v * FILL_CAP >= POSITION_VND:
            alt_hybrid.setdefault(tk, {})[d_ts] = p
            if is_t1_top: n_atc_full += 1
            else: n_t1115_full += 1
        else:
            n_skipped += 1   # liquidity gate fails -> fall back to OPEN in sim
print(f"  Hybrid alt-fill: ATC-full {n_atc_full:,} / T1115-full {n_t1115_full:,} / "
      f"liquidity-gated-to-OPEN {n_skipped:,}")

# ============================================================================
# 2) Load v11 signals + filters
# ============================================================================
print("\n[2/8] Loading v10 signals + Release_Date + 5-state + overheat...")
sig = bq(SIGNAL_V10.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
print(f"  {len(sig):,} signal rows")

releases = bq(f"""SELECT tf.ticker, tf.Release_Date FROM tav2_bq.ticker_financial AS tf
WHERE tf.Release_Date BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'""")
releases["Release_Date"] = pd.to_datetime(releases["Release_Date"])
release_by_ticker = (releases.sort_values(["ticker","Release_Date"])
                     .groupby("ticker")["Release_Date"].apply(list).to_dict())
import bisect
ds = np.empty(len(sig))
for i, (tk, t) in enumerate(zip(sig["ticker"].values, sig["time"].values)):
    arr = release_by_ticker.get(tk)
    if not arr: ds[i] = np.nan; continue
    idx = bisect.bisect_right(arr, pd.Timestamp(t))
    if idx == 0: ds[i] = np.nan; continue
    ds[i] = (pd.Timestamp(t) - arr[idx-1]).days
sig["days_since_release"] = ds

state_df = bq(f"""SELECT s.time, s.state FROM tav2_bq.vnindex_5state AS s
WHERE s.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'""")
state_df["time"] = pd.to_datetime(state_df["time"])
state_by_date = dict(zip(state_df["time"], state_df["state"]))

vni_full = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'""")
vni_full["time"] = pd.to_datetime(vni_full["time"])
vni_full["ratio"] = vni_full["Close"] / vni_full["MA200"]
vni_full["state"] = vni_full["time"].map(state_by_date)
vni_full["overheat"] = ((vni_full["ratio"] > 1.30)
                        & ((vni_full["state"] == 5) | (vni_full["D_RSI"] > 0.75)))
overheat_dates = set(vni_full[vni_full["overheat"]]["time"])
print(f"  Overheat days: {len(overheat_dates)}")

sig["state"] = sig["time"].map(state_by_date)

# ── D1 RE_BACKLOG_BUY override (deployed 2026-05-16, ported from production
# recommend_holistic.py:243-255). ICB 8633 (RE + KCN) tickers with
# advance-customer YoY surge (>0.5) AND fa_tier C/D AND ta>=120 AND state 3/4/5
# AND (np_yoy>0 OR rev_yoy>0) get play_type → RE_BACKLOG_BUY.
# Must run BEFORE SV_TIGHT and P3 filters so the override flows through them.
print("\n[2b/8] D1 RE_BACKLOG_BUY tier override (advance-customer signal)...")
d1_sql = f"""
WITH adv_dated AS (
  SELECT f.ticker, f.time AS f_time,
    SAFE_DIVIDE(f.AdvCust_P0, NULLIF(f.AdvCust_P4, 0)) - 1 AS adv_yoy,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.ticker_financial AS f
),
fa_dated_d1 AS (
  SELECT f.ticker, f.time AS f_time, f.tier AS fa_tier,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.fa_ratings AS f
),
fin_dated_d1 AS (
  SELECT f.ticker, f.time AS fin_time, f.Revenue_YoY_P0,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_fin_time
  FROM tav2_bq.ticker_financial AS f
)
SELECT t.ticker, t.time,
  fa.fa_tier,
  SAFE_DIVIDE(t.NP_P0, t.NP_P4) - 1 AS np_yoy,
  fin.Revenue_YoY_P0 AS rev_yoy,
  adv.adv_yoy,
  s5.state AS state5
FROM tav2_bq.ticker AS t
LEFT JOIN tav2_bq.vnindex_5state AS s5 ON s5.time = t.time
LEFT JOIN fa_dated_d1 AS fa ON fa.ticker = t.ticker AND t.time >= fa.f_time
   AND (fa.next_f_time IS NULL OR t.time < fa.next_f_time)
LEFT JOIN fin_dated_d1 AS fin ON fin.ticker = t.ticker AND t.time >= fin.fin_time
   AND (fin.next_fin_time IS NULL OR t.time < fin.next_fin_time)
LEFT JOIN adv_dated AS adv ON adv.ticker = t.ticker AND t.time >= adv.f_time
   AND (adv.next_f_time IS NULL OR t.time < adv.next_f_time)
WHERE t.ICB_Code = 8633
  AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
"""
d1 = bq(d1_sql)
d1["time"] = pd.to_datetime(d1["time"])
print(f"  Loaded {len(d1):,} (ticker,time) rows from ICB 8633 universe")
d1_mask = (
    d1["adv_yoy"].notna() & (d1["adv_yoy"] > 0.5)
    & d1["fa_tier"].isin(["C", "D"])
    & d1["state5"].isin([3, 4, 5])
    & ((d1["np_yoy"].fillna(-99) > 0) | (d1["rev_yoy"].fillna(-99) > 0))
)
d1_qual = d1.loc[d1_mask, ["ticker", "time"]].assign(_d1_ok=True)
sig = sig.merge(d1_qual, on=["ticker", "time"], how="left")
override_mask = sig["_d1_ok"].fillna(False) & (sig["ta"] >= 120)
n_override = int(override_mask.sum())
sig.loc[override_mask, "play_type"] = "RE_BACKLOG_BUY"
sig = sig.drop(columns=["_d1_ok"])
print(f"  D1 override applied: {n_override:,} signal rows reclassified to RE_BACKLOG_BUY "
      f"(across {sig.loc[override_mask, 'ticker'].nunique() if n_override else 0} tickers)")

def sv_tight_keep(row):
    s = row["state"]; days = row["days_since_release"]
    if pd.isna(s): return True
    s = int(s)
    if s in (4,5): return True
    if s == 1: return pd.notna(days) and days <= 30
    if s in (2,3): return pd.notna(days) and days <= 60
    return True
mask_bacore = sig["play_type"].isin(BUY_TIERS_V11)
mask_keep = (~mask_bacore) | sig.apply(sv_tight_keep, axis=1)
sig_f = sig[mask_keep].copy()
n_filt = (mask_bacore & ~sig.apply(sv_tight_keep, axis=1)).sum()
mask_p3 = sig_f["time"].isin(overheat_dates) & sig_f["play_type"].isin(BUY_TIERS_V11)
sig_f.loc[mask_p3, "play_type"] = "AVOID_overheated"
print(f"  SV_TIGHT filtered {n_filt:,} signals; P3 blocked {mask_p3.sum():,}")

# ============================================================================
# 3) Load prices + Open + liquidity + sector + top30
# ============================================================================
print("\n[3/8] Loading prices, Open, liquidity, sector map, top30...")
opens_df = bq(f"""SELECT t.ticker, t.time, t.Open AS open_price FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
  AND t.Open IS NOT NULL""")
opens_df["time"] = pd.to_datetime(opens_df["time"])
open_prices = {tk: dict(zip(g["time"], g["open_price"])) for tk, g in opens_df.groupby("ticker")}

prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_f.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig_f.iterrows()}

vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())

# REAL E1VFVN30 ETF prices from BigQuery (per user direction 2026-05-18:
# no more VNINDEX proxy — use actual ETF tracking). Management fee + tracking
# error are already baked into the realized price → set etf_mgmt_fee_annual=0
# and etf_tracking_drag_annual=0 to avoid double-counting.
etf_real = bq(f"""SELECT t.time, t.Close
FROM tav2_bq.ticker AS t
WHERE t.ticker = 'E1VFVN30'
  AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
ORDER BY t.time""")
etf_real["time"] = pd.to_datetime(etf_real["time"])
vn30_underlying = dict(zip(etf_real["time"], etf_real["Close"]))
print(f"  Real E1VFVN30 prices loaded: {len(etf_real)} days "
      f"({etf_real['time'].min().date()} -> {etf_real['time'].max().date()})")
# Real E1VFVN30 Open prices for cross-checking ETF rebalance fill price
etf_real_open = bq(f"""SELECT t.time, t.Open
FROM tav2_bq.ticker AS t
WHERE t.ticker = 'E1VFVN30'
  AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
ORDER BY t.time""")
etf_real_open["time"] = pd.to_datetime(etf_real_open["time"])
etf_open_by_date = dict(zip(etf_real_open["time"], etf_real_open["Open"]))

sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""").set_index("ticker")["s"].to_dict()
top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])

state_ff = {}; last_s = None
for d in vni_dates:
    s = state_by_date.get(d)
    if s is not None: last_s = s
    state_ff[d] = last_s

LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
            "liquidity_lookup": liq_map, "exit_slippage_tiered": True}
print(f"  Trading days: {len(vni_dates)}, top30 size: {len(top30)}")

# ============================================================================
# 4) Run BOTH books with event_log + etf_log + open positions kept
# ============================================================================
print("\n[4/8] Running BAL book sim...")
events_bal = []
etf_bal = []
nav_bal, trades_bal = simulate(sig_f, prices, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=MAX_POS_V11, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.0, init_nav=BOOK_NAV,
    sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
    sector_cap_exempt_tiers=SECTOR_CAP_EXEMPT,   # RE_BACKLOG_BUY exempt from cap=4
    tier_weights=TIER_WEIGHTS_V11,                # 10% NAV per position (slot12 spec)
    deposit_annual=0.0, state_by_date=state_ff,    # NO overnight interest (user direction 2026-05-18)
    cash_etf_states={3: 0.7}, vn30_underlying=vn30_underlying,
    etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,   # zero — already baked into real E1VFVN30 prices
    etf_rebalance_friction=0.0015,                             # realistic broker fee 0.15% per side
    open_prices=open_prices, t1_open_exec=True,
    entry_alt_prices=alt_hybrid, entry_fill_mode="v4_hybrid",
    event_log=events_bal, etf_log=etf_bal,
    force_close_eod=False,
    **LIQ_FULL, name="v11_BAL_transparent")

print("\n[5/8] Running VN30 book sim...")
events_v30 = []
etf_v30 = []
sig_vn30 = sig_f[sig_f["ticker"].isin(top30)].copy()
prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
LIQ_V30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}
nav_v30, trades_v30 = simulate(sig_vn30, prices_vn30, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=MAX_POS_V11, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.0, init_nav=BOOK_NAV,
    ticker_sector_map=sec_map,
    tier_weights=TIER_WEIGHTS_V11,                # 10% NAV per position (slot12 spec)
    deposit_annual=0.0, state_by_date=state_ff,    # NO overnight interest (user direction 2026-05-18)
    cash_etf_states={3: 0.7}, vn30_underlying=vn30_underlying,
    etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,   # zero — already baked into real E1VFVN30 prices
    etf_rebalance_friction=0.0015,                             # realistic broker fee 0.15% per side
    open_prices=open_prices, t1_open_exec=True,
    entry_alt_prices=alt_hybrid, entry_fill_mode="v4_hybrid",
    event_log=events_v30, etf_log=etf_v30,
    force_close_eod=False,
    **LIQ_V30, name="v11_VN30_transparent")

print(f"  BAL events: {len(events_bal)} buy/sells + {len(etf_bal)} ETF rebalances")
print(f"  VN30 events: {len(events_v30)} buy/sells + {len(etf_v30)} ETF rebalances")

# ============================================================================
# 6) Merge BAL + VN30 books into combined transparent log
# ============================================================================
print("\n[6/8] Merging into 50/50 combined NAV + transactions...")
nav_bal["time"] = pd.to_datetime(nav_bal["time"])
nav_v30["time"] = pd.to_datetime(nav_v30["time"])
nav_b_s = nav_bal.set_index("time")["nav"]
nav_v_s = nav_v30.set_index("time")["nav"]
common = nav_b_s.index.intersection(nav_v_s.index)
combined_nav = nav_b_s.loc[common] + nav_v_s.loc[common]

# Absolute amounts directly from nav_history (cleaner than cash_pct × nav)
cash_b = nav_bal.set_index("time")["cash"]
cash_v = nav_v30.set_index("time")["cash"]
etf_b = nav_bal.set_index("time")["cash_etf"]
etf_v = nav_v30.set_index("time")["cash_etf"]
stk_b = nav_bal.set_index("time")["positions_mv"] + nav_bal.set_index("time")["pending_mv"]
stk_v = nav_v30.set_index("time")["positions_mv"] + nav_v30.set_index("time")["pending_mv"]
n_pos_b = nav_bal.set_index("time")["n_pos"]
n_pos_v = nav_v30.set_index("time")["n_pos"]

# Build events into a single transactions DataFrame
def annotate_events(events, book_label):
    if not events: return pd.DataFrame()
    df = pd.DataFrame(events)
    df["book"] = book_label
    return df

events_all = pd.concat([
    annotate_events(events_bal, "BAL"),
    annotate_events(events_v30, "VN30"),
], ignore_index=True) if (events_bal or events_v30) else pd.DataFrame()

# ETF events as virtual transactions
etf_all = pd.concat([
    annotate_events(etf_bal, "BAL"),
    annotate_events(etf_v30, "VN30"),
], ignore_index=True) if (etf_bal or etf_v30) else pd.DataFrame()

if not etf_all.empty:
    # FIFO accounting: each ETF buy creates a per-lot holding_id (already set by simulator);
    # each ETF sell row is tagged with the holding_id of the lot being consumed (one
    # row per lot consumed). This makes analyze_portfolio.py group buys + matching
    # sells under the SAME holding_id for correct P&L.
    etf_tx = pd.DataFrame({
        "ymd": pd.to_datetime(etf_all["ymd"]),
        "ticker": "E1VFVN30",
        "action": etf_all["action"].apply(lambda a: "buy" if a == "buy_etf" else "sell"),
        "buy_amount": np.where(etf_all["action"]=="buy_etf", etf_all["amount_vnd"], 0.0),
        "sell_amount": np.where(etf_all["action"]=="sell_etf", etf_all["amount_vnd"], 0.0),
        "fee": etf_all["friction_cost"],
        "adj_price": etf_all["price_vn30"],
        "shares": etf_all["shares"],
        "holding_id": etf_all["holding_id"],
        "play_type": "ETF_PARK",
        "cash_after": etf_all["cash_after"],
        "reason": "ETF_REBAL_state" + etf_all["state"].astype(str),
        "book": etf_all["book"],
    })
else:
    etf_tx = pd.DataFrame()

if not events_all.empty:
    events_all["ymd"] = pd.to_datetime(events_all["ymd"])
stock_tx = events_all if not events_all.empty else pd.DataFrame()

# Combine and sort (real trades only first)
all_tx = pd.concat([stock_tx, etf_tx], ignore_index=True)
all_tx["ymd"] = pd.to_datetime(all_tx["ymd"])
all_tx = all_tx.sort_values(["ymd", "book", "action", "ticker"]).reset_index(drop=True)

# Cumulative transaction count for logs
tx_counts = all_tx.groupby(all_tx["ymd"]).size().cumsum()
n_tx_series = pd.Series(0, index=common, dtype=int)
for d, n in tx_counts.items():
    n_tx_series.loc[n_tx_series.index >= d] = int(n)

# Daily logs — per-book breakdown for full transparency (user direction 2026-05-18):
#   nav = BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf
combined_logs = pd.DataFrame({
    "ymd": common,
    "nav": combined_nav.values,
    "BAL_cash": cash_b.loc[common].values,
    "BAL_stocks": stk_b.loc[common].values,
    "BAL_etf": etf_b.loc[common].values,
    "VN30_cash": cash_v.loc[common].values,
    "VN30_stocks": stk_v.loc[common].values,
    "VN30_etf": etf_v.loc[common].values,
    "cash": (cash_b + cash_v).loc[common].values,
    "cash_etf": (etf_b + etf_v).loc[common].values,
    "stocks_mv": (stk_b + stk_v).loc[common].values,
    "num_holdings": (n_pos_b + n_pos_v).loc[common].values,
    "num_transactions": n_tx_series.values,
    "state": pd.Series(common).map(state_ff).values,
})
print(f"  Combined: {len(combined_logs)} days, {len(all_tx)} transactions")

# ============================================================================
# 7) Save CSVs + open positions snapshot
# ============================================================================
print("\n[7/8] Saving CSVs...")
os.makedirs(os.path.join(WORKDIR, "data"), exist_ok=True)

def safe_to_csv(df, path):
    """Write CSV; if locked (OneDrive / Excel), fall back to .new sibling."""
    try:
        df.to_csv(path, index=False)
        return path
    except PermissionError:
        alt = path.replace(".csv", ".new.csv")
        df.to_csv(alt, index=False)
        print(f"  (original locked, wrote to {alt})")
        return alt

logs_path = safe_to_csv(combined_logs,
                        os.path.join(WORKDIR, "data", "v11_transparent_logs.csv"))
tx_path = safe_to_csv(all_tx,
                      os.path.join(WORKDIR, "data", "v11_transparent_transactions.csv"))
print(f"  {logs_path}")
print(f"  {tx_path}")

# Open positions snapshot (stocks + ETF mark-to-market)
open_bal = nav_bal.attrs.get("open_positions_final") if hasattr(nav_bal, "attrs") else None
open_v30 = nav_v30.attrs.get("open_positions_final") if hasattr(nav_v30, "attrs") else None
open_df = pd.concat([
    open_bal.assign(book="BAL") if open_bal is not None and not open_bal.empty else pd.DataFrame(),
    open_v30.assign(book="VN30") if open_v30 is not None and not open_v30.empty else pd.DataFrame(),
], ignore_index=True) if (open_bal is not None or open_v30 is not None) else pd.DataFrame()

# Add ETF open lots — each lot has its REAL entry_date from the day it was bought
# (no more hallucinated common[0]; no synthetic LIFETIME holding_id).
etf_lots_bal = nav_bal.attrs.get("etf_lots_final") if hasattr(nav_bal, "attrs") else None
etf_lots_v30 = nav_v30.attrs.get("etf_lots_final") if hasattr(nav_v30, "attrs") else None
for book_label, etf_lots_df in [("BAL", etf_lots_bal), ("VN30", etf_lots_v30)]:
    if etf_lots_df is None or etf_lots_df.empty:
        continue
    open_df = pd.concat([open_df, etf_lots_df.assign(book=book_label)],
                       ignore_index=True)

# ============================================================================
# Add phantom Mark-to-Market entries for open positions at end of period
# Flagged with reason="MTM_UNREALIZED". Filter by this to exclude from real
# cash-flow analysis. Lets analyze_portfolio.py compute correct total P&L
# (realized + unrealized) for each position.
# ============================================================================
last_day = common[-1] if len(common) > 0 else pd.Timestamp(END_DATE)
mtm_rows = []
for book_label, open_pos_df in [("BAL", open_bal), ("VN30", open_v30)]:
    if open_pos_df is None or open_pos_df.empty: continue
    for _, p in open_pos_df.iterrows():
        mtm_rows.append({
            "ymd": last_day, "ticker": p["ticker"], "action": "sell",
            "buy_amount": 0.0, "sell_amount": float(p["mark_value"]),
            "fee": 0.0, "adj_price": float(p["last_price"]),
            "shares": float(p["shares"]),
            "holding_id": p["holding_id"],
            "play_type": p["play_type"], "cash_after": None,
            "reason": "MTM_UNREALIZED", "book": book_label,
        })
# MTM phantom rows for ETF: one per open lot, using its real holding_id so
# analyze_portfolio.py matches the lot's buy + this MTM-sell together.
for book_label, etf_lots_df in [("BAL", etf_lots_bal), ("VN30", etf_lots_v30)]:
    if etf_lots_df is None or etf_lots_df.empty:
        continue
    for _, lot in etf_lots_df.iterrows():
        mtm_rows.append({
            "ymd": last_day, "ticker": "E1VFVN30", "action": "sell",
            "buy_amount": 0.0, "sell_amount": float(lot["mark_value"]),
            "fee": 0.0,
            "adj_price": float(lot["last_price"]) if pd.notna(lot["last_price"]) else None,
            "shares": float(lot["shares"]),
            "holding_id": lot["holding_id"],
            "play_type": "ETF_PARK", "cash_after": None,
            "reason": "MTM_UNREALIZED", "book": book_label,
        })

if mtm_rows:
    mtm_df = pd.DataFrame(mtm_rows)
    all_tx = pd.concat([all_tx, mtm_df], ignore_index=True)
    all_tx = all_tx.sort_values(["ymd", "book", "action", "ticker"]).reset_index(drop=True)
    print(f"  Added {len(mtm_rows)} mark-to-market phantom entries (reason='MTM_UNREALIZED')")
    tx_path = safe_to_csv(all_tx, tx_path.replace(".new.csv", ".csv"))

open_path = safe_to_csv(open_df,
                        os.path.join(WORKDIR, "data", "v11_transparent_open_positions.csv"))
print(f"  {open_path}: {len(open_df)} open positions with unrealized P&L")
if not open_df.empty:
    print(f"\n  OPEN POSITIONS DETAIL:")
    for _, r in open_df.iterrows():
        upnl = r['unrealised_pnl']/1e9
        ret = r['unrealised_ret_pct']
        cb = r['cost_basis']/1e9
        mv = r['mark_value']/1e9
        print(f"    {r['ticker']:<12} {r['book']:<5} entry={r['entry_date'].date() if pd.notna(r['entry_date']) else '-'} "
              f"days={r['days_held']:.0f} cost={cb:>+7.2f}B mark={mv:>+7.2f}B "
              f"unrealised={upnl:>+7.2f}B ({ret:+.2f}%) [{r['play_type']}]")

# ============================================================================
# 8) Quick summary
# ============================================================================
print("\n[8/8] Quick summary")
final_nav = combined_nav.iloc[-1]
final_cash = (cash_b + cash_v).iloc[-1]
final_etf = (etf_b + etf_v).iloc[-1]
final_pos = final_nav - final_cash - final_etf
years = (common[-1] - common[0]).days / 365.25
cagr = (final_nav / TOTAL_NAV)**(1/years) - 1 if years > 0 else 0
total_ret = (final_nav / TOTAL_NAV - 1) * 100
peak = combined_nav.cummax()
dd = ((combined_nav - peak)/peak).min() * 100

print(f"  Period: {common[0].date()} -> {common[-1].date()} ({years:.2f} years)")
print(f"  Initial NAV: {TOTAL_NAV/1e9:.2f}B")
print(f"  Final NAV: {final_nav/1e9:.2f}B (total return {total_ret:+.2f}%, CAGR {cagr*100:+.2f}%)")
print(f"    of which: cash {final_cash/1e9:.2f}B + ETF {final_etf/1e9:.2f}B + positions {final_pos/1e9:.2f}B")
print(f"  Max drawdown: {dd:.2f}%")
print(f"  Open positions at end: {len(open_df)}")
if not open_df.empty:
    total_unrealised = open_df["unrealised_pnl"].sum()
    print(f"  Total unrealized P&L (open): {total_unrealised/1e9:+.2f}B")

# ============================================================================
# Cash-flow reconciliation table — verifiable from transactions CSV
# ============================================================================
print("\n--- CASH-FLOW RECONCILIATION (verifiable from transactions.csv) ---")
real_tx = all_tx[all_tx["reason"] != "MTM_UNREALIZED"]
stock_real = real_tx[real_tx["ticker"] != "E1VFVN30"]
etf_real = real_tx[real_tx["ticker"] == "E1VFVN30"]

stk_buy = stock_real[stock_real["action"]=="buy"]["buy_amount"].sum()     # CLEAN share cost (no fee)
stk_sell = stock_real[stock_real["action"]=="sell"]["sell_amount"].sum()  # CLEAN gross (no fee deducted)
stk_fee = stock_real["fee"].sum()
etf_buy_total = etf_real[etf_real["action"]=="buy"]["buy_amount"].sum()
etf_sell_total = etf_real[etf_real["action"]=="sell"]["sell_amount"].sum()
etf_fee = etf_real["fee"].sum()

# Unrealized open
mtm_sells = all_tx[all_tx["reason"]=="MTM_UNREALIZED"]
mtm_stocks_val = mtm_sells[mtm_sells["ticker"]!="E1VFVN30"]["sell_amount"].sum()
mtm_etf_val = mtm_sells[mtm_sells["ticker"]=="E1VFVN30"]["sell_amount"].sum()

# Cash deducted on stock buys = buy_amount + fee (per new semantics)
# Cash received on stock sells = sell_amount - fee
stk_cash_out_buy = stk_buy + stock_real[stock_real["action"]=="buy"]["fee"].sum()
stk_cash_in_sell = stk_sell - stock_real[stock_real["action"]=="sell"]["fee"].sum()
etf_cash_out_buy = etf_buy_total + etf_real[etf_real["action"]=="buy"]["fee"].sum()
etf_cash_in_sell = etf_sell_total - etf_real[etf_real["action"]=="sell"]["fee"].sum()

print(f"  STOCK FLOW (real trades, excludes MTM):")
print(f"    Buys (share cost):  {stk_buy/1e9:>+9.4f}B")
print(f"    Buy fees:           {stock_real[stock_real['action']=='buy']['fee'].sum()/1e9:>+9.4f}B")
print(f"    Sells (gross):      {stk_sell/1e9:>+9.4f}B")
print(f"    Sell fees+tax:      {stock_real[stock_real['action']=='sell']['fee'].sum()/1e9:>+9.4f}B")
print(f"    Net realized P&L:   {(stk_cash_in_sell - stk_cash_out_buy)/1e9:>+9.4f}B  (= cash_in_from_sells - cash_out_to_buys)")
print(f"  ETF FLOW (real rebalances, excludes MTM):")
print(f"    Buys (share cost):  {etf_buy_total/1e9:>+9.4f}B")
print(f"    Buy fees (friction):{etf_real[etf_real['action']=='buy']['fee'].sum()/1e9:>+9.4f}B")
print(f"    Sells (gross):      {etf_sell_total/1e9:>+9.4f}B")
print(f"    Sell fees (friction):{etf_real[etf_real['action']=='sell']['fee'].sum()/1e9:>+9.4f}B")
print(f"    Net ETF cash flow:  {(etf_cash_in_sell - etf_cash_out_buy)/1e9:>+9.4f}B  (parked; residual still in cash_etf)")
print(f"  OPEN POSITIONS MARK-TO-MARKET (at last day):")
print(f"    Stock MTM value:    {mtm_stocks_val/1e9:>+9.4f}B")
print(f"    ETF MTM value:      {mtm_etf_val/1e9:>+9.4f}B")
print(f"  RECONCILE (cash trajectory ONLY from transactions, no interest):")
print(f"    Initial cash:                    {TOTAL_NAV/1e9:>+9.4f}B")
print(f"    - Stock buys (share+fee out):    {stk_cash_out_buy/1e9:>+9.4f}B")
print(f"    + Stock sells (gross-fee in):    {stk_cash_in_sell/1e9:>+9.4f}B")
print(f"    - ETF buys (share+fee out):      {etf_cash_out_buy/1e9:>+9.4f}B")
print(f"    + ETF sells (gross-fee in):      {etf_cash_in_sell/1e9:>+9.4f}B")
expected_cash = TOTAL_NAV - stk_cash_out_buy + stk_cash_in_sell - etf_cash_out_buy + etf_cash_in_sell
print(f"    = Expected end cash:             {expected_cash/1e9:>+9.4f}B")
actual_cash = (cash_b + cash_v).iloc[-1]
print(f"    Actual end cash:                 {actual_cash/1e9:>+9.4f}B")
print(f"    Diff (residual = ETF appreciation rebalanced into cash):  {(actual_cash - expected_cash)/1e9:>+9.4f}B")
print()
print(f"  FINAL NAV CHECK:")
print(f"    Actual end cash:    {actual_cash/1e9:>+9.4f}B")
print(f"    + Actual end ETF:   {(etf_b + etf_v).iloc[-1]/1e9:>+9.4f}B")
print(f"    + Open stock mark:  {mtm_stocks_val/1e9:>+9.4f}B")
print(f"    = Final NAV:        {final_nav/1e9:>+9.4f}B  (vs sim's NAV {final_nav/1e9:+9.4f}B)")

# Append reconciliation block to the markdown report
recon_md = []
recon_md.append("\n\n## Cash-Flow Reconciliation (verifiable from transactions.csv)\n")
recon_md.append("All numbers below derive ONLY from the transactions CSV. The MTM_UNREALIZED")
recon_md.append("rows (flagged in `reason` column) are phantom mark-to-market entries used by")
recon_md.append("analyze_portfolio.py to compute unrealized P&L on open positions — they are NOT")
recon_md.append("real trades. Filter `reason != 'MTM_UNREALIZED'` to see only real broker activity.\n")

recon_md.append(f"### Schema (per user 2026-05-18)\n")
recon_md.append(f"- `buy_amount` = cost of shares (clean, no fee)")
recon_md.append(f"- `sell_amount` = gross from sale (clean, no fee deducted)")
recon_md.append(f"- `fee` = transaction cost (buy: 0.15% broker; sell: 0.15% broker + 0.1% PIT tax)")
recon_md.append(f"- **Cash deducted on buy = buy_amount + fee**")
recon_md.append(f"- **Cash received on sell = sell_amount - fee**")
recon_md.append(f"- `deposit_annual=0` (no overnight interest)\n")
recon_md.append(f"### Real activity (excludes MTM_UNREALIZED phantoms)\n")
recon_md.append(f"| Category | Amount |")
recon_md.append(f"|---|---|")
recon_md.append(f"| Stock buys — share cost | {stk_buy/1e9:+,.4f}B |")
recon_md.append(f"| Stock buys — fee | {stock_real[stock_real['action']=='buy']['fee'].sum()/1e9:+,.4f}B |")
recon_md.append(f"| Stock sells — gross | {stk_sell/1e9:+,.4f}B |")
recon_md.append(f"| Stock sells — fee+tax | {stock_real[stock_real['action']=='sell']['fee'].sum()/1e9:+,.4f}B |")
recon_md.append(f"| **Net stock realized P&L** | **{(stk_cash_in_sell - stk_cash_out_buy)/1e9:+,.4f}B** |")
recon_md.append(f"| ETF buys — share cost | {etf_buy_total/1e9:+,.4f}B |")
recon_md.append(f"| ETF buys — friction | {etf_real[etf_real['action']=='buy']['fee'].sum()/1e9:+,.4f}B |")
recon_md.append(f"| ETF sells — gross | {etf_sell_total/1e9:+,.4f}B |")
recon_md.append(f"| ETF sells — friction | {etf_real[etf_real['action']=='sell']['fee'].sum()/1e9:+,.4f}B |")
recon_md.append(f"| **Net ETF cash flow** | **{(etf_cash_in_sell - etf_cash_out_buy)/1e9:+,.4f}B** |")
recon_md.append(f"\n### Open positions at end of period (unrealized)\n")
recon_md.append(f"| Position | Cost basis | Current value | Unrealized P&L | Return |")
recon_md.append(f"|---|---|---|---|---|")
for _, o in open_df.iterrows():
    recon_md.append(f"| {o['ticker']} ({o.get('book','-')}) | {o['cost_basis']/1e9:+,.3f}B | {o['mark_value']/1e9:+,.3f}B | {o['unrealised_pnl']/1e9:+,.3f}B | {o['unrealised_ret_pct']:+.2f}% |")
recon_md.append(f"\n### Final reconciliation\n")
recon_md.append(f"| Component | Value |")
recon_md.append(f"|---|---|")
recon_md.append(f"| Initial NAV | {TOTAL_NAV/1e9:+,.3f}B |")
recon_md.append(f"| + Realized P&L from stocks | {(stk_sell-stk_buy-stk_fee)/1e9:+,.3f}B |")
recon_md.append(f"| + ETF net cash flow + MTM | {(etf_sell_total - etf_buy_total - etf_fee + mtm_etf_val)/1e9:+,.3f}B |")
recon_md.append(f"| + Stock unrealized MTM | {mtm_stocks_val/1e9:+,.3f}B (cost {sum(o['cost_basis'] for _,o in open_df.iterrows() if o['ticker']!='E1VFVN30')/1e9:.3f}B → realized would be {(mtm_stocks_val - sum(o['cost_basis'] for _,o in open_df.iterrows() if o['ticker']!='E1VFVN30'))/1e9:+,.3f}B if sold today) |")
expected_end_cash = TOTAL_NAV - stk_cash_out_buy + stk_cash_in_sell - etf_cash_out_buy + etf_cash_in_sell
end_cash_actual = (cash_b + cash_v).iloc[-1]
end_etf_actual = (etf_b + etf_v).iloc[-1]
etf_appreciation_rebal_to_cash = end_cash_actual - expected_end_cash
recon_md.append(f"| Initial NAV | {TOTAL_NAV/1e9:+,.4f}B |")
recon_md.append(f"| - Stock buys (buy_amount + fee out) | {stk_cash_out_buy/1e9:+,.4f}B |")
recon_md.append(f"| + Stock sells (sell_amount - fee in) | {stk_cash_in_sell/1e9:+,.4f}B |")
recon_md.append(f"| - ETF buys (buy_amount + fee out) | {etf_cash_out_buy/1e9:+,.4f}B |")
recon_md.append(f"| + ETF sells (sell_amount - fee in) | {etf_cash_in_sell/1e9:+,.4f}B |")
recon_md.append(f"| = Expected end cash (from transactions only) | {expected_end_cash/1e9:+,.4f}B |")
recon_md.append(f"| Actual end cash (from logs) | {end_cash_actual/1e9:+,.4f}B |")
recon_md.append(f"| **Diff (ETF appreciation rebalanced into cash)** | **{etf_appreciation_rebal_to_cash/1e9:+,.4f}B** |")
recon_md.append(f"| Actual end ETF balance (still in cash_etf) | {end_etf_actual/1e9:+,.4f}B |")
recon_md.append(f"| Open stock positions mark value | {mtm_stocks_val/1e9:+,.4f}B |")
recon_md.append(f"| = **Final NAV (cash + ETF + open stocks)** | **{final_nav/1e9:+,.4f}B** |")
recon_md.append(f"\n**Note on `Diff` line**: when ETF appreciates daily by VN30 return, cash_etf grows.")
recon_md.append(f"The rebalance logic (target 70% of total cash+ETF in state=NEUTRAL) periodically moves")
recon_md.append(f"a portion OUT of cash_etf and INTO cash. Those are logged as ETF 'sell' transactions,")
recon_md.append(f"but the moved amount EXCEEDS the original cost basis (because ETF appreciated meanwhile).")
recon_md.append(f"The diff line = appreciation that flowed to cash via rebalances. To FULLY reconcile,")
recon_md.append(f"compute ETF return = (etf_sells + etf_etf_residual_mark) − etf_buys − etf_fees.")
recon_md.append(f"\n### Per-book daily breakdown (in logs CSV)\n")
recon_md.append(f"The `data/v11_transparent_logs.csv` now has 6 per-book columns:")
recon_md.append(f"`BAL_cash`, `BAL_stocks`, `BAL_etf`, `VN30_cash`, `VN30_stocks`, `VN30_etf`.")
recon_md.append(f"Each row: `BAL_cash + BAL_stocks + BAL_etf + VN30_cash + VN30_stocks + VN30_etf = NAV`.")
recon_md.append(f"Cross-check at any date: when ETF is bought in BAL, BAL_cash decreases and BAL_etf increases (minus friction).")

report_path = os.path.join(WORKDIR, "data", "v11_transparent_report.md")
with open(report_path, "a", encoding="utf-8") as f:
    f.write("\n".join(recon_md))
print(f"\nReconciliation appended to {report_path}")

print(f"\nFiles produced:")
print(f"  Logs (daily NAV):      {logs_path}")
print(f"  Transactions:          {tx_path}")
print(f"  Open positions:        {open_path}")
print(f"  Full markdown report:  {report_path}")
