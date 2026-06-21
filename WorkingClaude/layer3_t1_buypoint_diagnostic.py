# -*- coding: utf-8 -*-
"""Phase 1 diagnostic — within T+1 day, which buy POINT is best?

Per-trade alt-fill analysis on REAL BA-v11 trade flow (NOT synthetic universe —
prior synthetic intraday studies overstated alpha; see layer3_backfill_reality_check.md).

Method:
  1. Run v11 BAL book sim 2023-09-15 to 2026-05-12 (intraday data window) with
     realistic T+1 Open execution canonical.
  2. For each BUY trade, look up alt-mode fill prices from intraday_full.pkl:
        OPEN      = first 15m bar's close (~09:15) — proxy for baseline Open fill
        T1115_MKT = close of 11:15 bar (market order at 11:15)
        T1115_LIM = LIMIT @ p_OPEN; fills if min(low pre-11:15) <= p_OPEN, else SKIP
        VWAP      = volume-weighted avg of full session
        ATC       = close of 14:45 bar (closing auction)
        DAY_LOW   = oracle (lower-bound), theoretical best
  3. Compute hypothetical net ROI per trade with same SELL price:
        roi_mode = (exit_price / fill_mode) * (1 - TC_sell - CG_tax) /
                   (1 + TC_buy) - 1
  4. Aggregate by segment (TOP30 / OTHER) and overall.

Decision rule (per t1_intraday_research_plan.md):
  - Adopt if mode delivers >= +0.30% per-trade alpha vs OPEN baseline (TOP30 +
    OTHER both positive), miss rate < 5% for LIM modes
  - Anything weaker -> stay with OPEN
"""
import os
import sys
import io
import pickle
import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import simulate, bq, VNI_QUERY
from signal_v10_sql import SIGNAL_V10

START_DATE = "2023-09-15"   # intraday data starts 2023-09-11
END_DATE   = "2026-05-12"   # intraday data ends 2026-05-12
BOOK_NAV   = 25e9            # one book (BAL) — same as production 50/50

INTRADAY_PKL = os.path.join(WORKDIR, "intraday_full.pkl")

# Fees (mirror simulate_holistic_nav constants)
TC_BUY = 0.001
TC_SELL = 0.001
CG_TAX = 0.001  # 0.1% on sell proceeds
SLIPPAGE = 0.001
SELL_COST = (1 - TC_SELL - CG_TAX) * (1 - SLIPPAGE)
BUY_COST = (1 + TC_BUY) * (1 + SLIPPAGE)

BUY_TIERS_V11 = {"MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "MOMENTUM_QUALITY",
                  "MOMENTUM_A", "MOMENTUM_S_N", "COMPOUNDER_BUY", "DEEP_VALUE_RECOVERY", "S_PRO"}
TIER_BAL = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]

print("=" * 100)
print("  Layer 3 T+1 buy-POINT diagnostic — REAL BA v11 flow")
print(f"  Window: {START_DATE} -> {END_DATE}")
print("=" * 100)

# ============================================================================
# 1) Load intraday bars
# ============================================================================
print("\n[1/6] Loading intraday_full.pkl...")
with open(INTRADAY_PKL, "rb") as f:
    intraday = pickle.load(f)
print(f"  {len(intraday)} tickers")

# Build per-(ticker,date) session lookup with derived prices
def build_session_prices(bars_df):
    """For one ticker's bars, return dict {date -> {prices}}.

    Note: vnstock intraday prices are in THOUSANDS of VND; we scale ×1000 to
    match BQ ticker.Open/Close raw-VND units.
    """
    if bars_df is None or bars_df.empty:
        return {}
    bars = bars_df.copy()
    bars["time"] = pd.to_datetime(bars["time"])
    bars["date"] = bars["time"].dt.date
    bars["hm"] = bars["time"].dt.strftime("%H:%M")
    # Scale ×1000 to match BQ raw-VND
    for c in ("open","high","low","close"):
        bars[c] = bars[c].astype(float) * 1000.0
    out = {}
    for d, g in bars.groupby("date"):
        g = g.sort_values("time").reset_index(drop=True)
        # OPEN proxy = first bar's close (09:00 ATO if present else 09:15)
        p_open = float(g.iloc[0]["close"])
        # 11:15 bar
        morn_close = g[g["hm"] == "11:15"]
        p_1115 = float(morn_close.iloc[0]["close"]) if len(morn_close) else np.nan
        # ATC = 14:45 (last bar of session)
        p_atc = float(g.iloc[-1]["close"])
        # VWAP
        v = g["volume"].values.astype(float)
        c = g["close"].values.astype(float)
        if v.sum() > 0:
            p_vwap = float((v * c).sum() / v.sum())
        else:
            p_vwap = float(c.mean())
        # Day low and pre-11:15 low (for LIM fill check)
        p_day_low = float(g["low"].min())
        pre_1115 = g[g["hm"].isin(["09:00","09:15","09:30","09:45","10:00","10:15","10:30","10:45","11:00","11:15"])]
        p_pre_low = float(pre_1115["low"].min()) if len(pre_1115) else np.nan
        # Day high
        p_day_high = float(g["high"].max())
        out[pd.Timestamp(d)] = {
            "open": p_open, "t1115": p_1115, "atc": p_atc, "vwap": p_vwap,
            "day_low": p_day_low, "day_high": p_day_high, "pre_1115_low": p_pre_low,
            "n_bars": len(g),
        }
    return out

print("  building per-session price lookups...")
intraday_lkp = {}
for tk, bars in intraday.items():
    intraday_lkp[tk] = build_session_prices(bars)
n_sessions = sum(len(v) for v in intraday_lkp.values())
print(f"  {n_sessions:,} ticker-sessions indexed")

# ============================================================================
# 2) Load signals & build v11 stack (mirrors test_v11_12y_t1open.py)
# ============================================================================
print("\n[2/6] Loading v10 signals + Release_Date + 5-state + overheat...")
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
    if not arr:
        ds[i] = np.nan; continue
    idx = bisect.bisect_right(arr, pd.Timestamp(t))
    if idx == 0:
        ds[i] = np.nan; continue
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

sig["state"] = sig["time"].map(state_by_date)
def sv_tight_keep(row):
    s = row["state"]; days = row["days_since_release"]
    if pd.isna(s): return True
    s = int(s)
    if s in (4, 5): return True
    if s == 1: return pd.notna(days) and days <= 30
    if s in (2, 3): return pd.notna(days) and days <= 60
    return True
mask_bacore = sig["play_type"].isin(BUY_TIERS_V11)
mask_keep = (~mask_bacore) | sig.apply(sv_tight_keep, axis=1)
sig_f = sig[mask_keep].copy()
mask_p3 = sig_f["time"].isin(overheat_dates) & sig_f["play_type"].isin(BUY_TIERS_V11)
sig_f.loc[mask_p3, "play_type"] = "AVOID_overheated"
print(f"  {len(sig_f):,} v11-filtered signal rows ({mask_p3.sum():,} P3 blocked)")

# ============================================================================
# 3) Load Open prices & misc
# ============================================================================
print("\n[3/6] Loading Open prices, sector map, top30...")
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
vn30_underlying = dict(zip(vni["time"], vni["Close"]))

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

# ============================================================================
# 4) Run v11 BAL sim with realistic T+1 Open canonical
# ============================================================================
print("\n[4/6] Running BAL book sim (realistic T+1 Open)...")
nav_b, trades_b = simulate(sig_f, prices, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=SLIPPAGE, init_nav=BOOK_NAV,
    sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map,
    deposit_annual=0.01, state_by_date=state_ff,
    cash_etf_states={3: 0.7}, vn30_underlying=vn30_underlying,
    open_prices=open_prices, t1_open_exec=True,
    **LIQ_FULL, name="v11_BAL")

# Also run VN30 book for fuller flow
sig_vn30 = sig_f[sig_f["ticker"].isin(top30)].copy()
prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
LIQ_V30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}
nav_v, trades_v = simulate(sig_vn30, prices_vn30, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=SLIPPAGE, init_nav=BOOK_NAV,
    ticker_sector_map=sec_map,
    deposit_annual=0.01, state_by_date=state_ff,
    cash_etf_states={3: 0.7}, vn30_underlying=vn30_underlying,
    open_prices=open_prices, t1_open_exec=True,
    **LIQ_V30, name="v11_VN30")

tb = trades_b.copy(); tb["book"] = "BAL"
tv = trades_v.copy(); tv["book"] = "VN30"
trades_df = pd.concat([tb, tv], ignore_index=True)
print(f"  {len(trades_df):,} total trades captured (BAL {len(trades_b)} + VN30 {len(trades_v)})")
print(f"  trade cols: {list(trades_df.columns)}")

# ============================================================================
# 5) For each trade, lookup alt-mode fill prices and compute hypothetical ROI
# ============================================================================
print("\n[5/6] Computing alt-mode fill prices per trade...")
trades_df["entry_date"] = pd.to_datetime(trades_df["entry_date"])
trades_df["exit_date"] = pd.to_datetime(trades_df["exit_date"])

def lookup_intraday(ticker, entry_date):
    """Return dict of alt prices, or None if no intraday data."""
    by_date = intraday_lkp.get(ticker)
    if not by_date: return None
    return by_date.get(pd.Timestamp(entry_date.date()))

# fill prices: per-trade
rows = []
missing = 0
for _, t in trades_df.iterrows():
    tk = t["ticker"]; ed = t["entry_date"]
    ip = lookup_intraday(tk, ed)
    if ip is None:
        missing += 1
        continue
    p_open = ip["open"]
    p_1115 = ip["t1115"]
    p_atc = ip["atc"]
    p_vwap = ip["vwap"]
    p_lo = ip["day_low"]
    p_pre_lo = ip["pre_1115_low"]
    exit_px = t["exit_price"]

    # LIM @ open: fills if pre-1115 low <= open price (sell-side limit fills when price dips)
    # For BUY limit at p_open: fills if intraday goes <= p_open before 11:15
    if pd.notna(p_pre_lo) and pd.notna(p_open) and p_pre_lo <= p_open:
        p_lim1115 = min(p_1115, p_open) if pd.notna(p_1115) else p_open
        lim_filled = True
    else:
        p_lim1115 = np.nan
        lim_filled = False

    def roi(fill_px):
        if pd.isna(fill_px) or fill_px <= 0: return np.nan
        return (exit_px / fill_px) * (SELL_COST / BUY_COST) - 1

    seg = "TOP30" if tk in top30 else "OTHER"
    rows.append({
        "ticker": tk, "entry_date": ed, "exit_date": t["exit_date"],
        "book": t["book"], "segment": seg, "reason": t["reason"],
        "play_type": t["play_type"], "exit_price": exit_px,
        "p_open": p_open, "p_t1115_mkt": p_1115, "p_t1115_lim": p_lim1115,
        "p_atc": p_atc, "p_vwap": p_vwap, "p_day_low": p_lo,
        "lim_filled": lim_filled,
        "roi_open": roi(p_open),
        "roi_t1115_mkt": roi(p_1115),
        "roi_t1115_lim": roi(p_lim1115),  # NaN if limit missed
        "roi_atc": roi(p_atc),
        "roi_vwap": roi(p_vwap),
        "roi_day_low": roi(p_lo),  # oracle
    })
df = pd.DataFrame(rows)
print(f"  Matched: {len(df):,} / {len(trades_df):,} trades (missing intraday: {missing})")

# ============================================================================
# 6) Aggregate & report
# ============================================================================
print("\n[6/6] Aggregate alpha per mode vs OPEN baseline...")

MODES = ["roi_open", "roi_t1115_mkt", "roi_t1115_lim", "roi_atc", "roi_vwap", "roi_day_low"]

def agg(sub, label):
    n = len(sub)
    if n == 0: return None
    out = {"label": label, "n": n}
    base = sub["roi_open"].mean()
    for m in MODES:
        v = sub[m].dropna()
        out[f"{m}_mean"] = v.mean() if len(v) else np.nan
        out[f"{m}_n"] = len(v)
        out[f"{m}_alpha"] = (v.mean() - base) if len(v) else np.nan
        out[f"{m}_win"] = (v > base).mean() if len(v) else np.nan
    return out

def print_block(label, sub):
    r = agg(sub, label)
    if r is None:
        print(f"\n--- {label}: EMPTY ---"); return
    print(f"\n--- {label} (n={r['n']}) ---")
    print(f"  {'Mode':<14} {'n':>6} {'Mean ROI':>10} {'Alpha vs OPEN':>14} {'Win-vs-OPEN':>12}")
    for m in MODES:
        mr = r[f"{m}_mean"]; ma = r[f"{m}_alpha"]; mn = r[f"{m}_n"]; mw = r[f"{m}_win"]
        miss = f"({(1-mn/r['n'])*100:.1f}% miss)" if mn < r['n'] else ""
        print(f"  {m:<14} {mn:>6} {mr*100:>+9.2f}% {ma*100:>+13.2f}pp {mw*100:>+11.1f}% {miss}")

print_block("ALL TRADES",      df)
print_block("TOP30 segment",   df[df["segment"]=="TOP30"])
print_block("OTHER segment",   df[df["segment"]!="TOP30"])
print_block("BAL book only",   df[df["book"]=="BAL"])
print_block("VN30 book only",  df[df["book"]=="VN30"])

# By exit reason (winners vs stop-outs)
print_block("Winners (TIME exits)", df[df["reason"]=="TIME"])
print_block("Losers (STOP exits)",  df[df["reason"]=="STOP"])

# Annual breakdown
df["year"] = df["entry_date"].dt.year
for y in sorted(df["year"].unique()):
    print_block(f"Year {y}", df[df["year"]==y])

# Save full csv for inspection
out_csv = os.path.join(WORKDIR, "data", "layer3_t1_buypoint_alttrades.csv")
df.to_csv(out_csv, index=False)
print(f"\nSaved: {out_csv}")

print("\n" + "=" * 100)
print("  Decision summary")
print("  - 'OPEN' is current canonical (realistic T+1 Open)")
print("  - Adopt alt-mode IF alpha >= +0.30pp/trade AND TOP30+OTHER both positive")
print("    AND (for LIM mode) miss rate < 5%")
print("=" * 100)
