# -*- coding: utf-8 -*-
"""Phase 2 — Full NAV simulation: OPEN vs T1115_MKT vs T1115_LIM.

Translates Phase 1 per-trade alpha into CAGR / Sharpe / MaxDD deltas via
full BA-v11 sim on 2023-09-15 -> 2026-05-12 (intraday data window).

Modes:
  OPEN       baseline (canonical realistic T+1 Open)
  T1115_MKT  market order at 11:15 (close of 11:15 bar)
  T1115_LIM  limit @ T+1 Open price; fills if pre-11:15 low <= p_open, else
             FALL BACK to T+1 Open (so no synthetic 'skip' alpha)
  VWAP       full-session VWAP

For trades on tickers without intraday coverage (~70% of trade flow), all modes
fall back to T+1 Open — so the alpha estimate is CONSERVATIVE (underweights
modes' impact, since they only apply to top30-ish covered universe).
"""
import os, sys, io, pickle
import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import simulate, bq, VNI_QUERY
from signal_v10_sql import SIGNAL_V10

START_DATE = "2023-09-15"
END_DATE   = "2026-05-12"
BOOK_NAV   = 25e9

INTRADAY_PKL = os.path.join(WORKDIR, "data/intraday_full.pkl")
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]

print("=" * 100)
print("  Phase 2: Layer 3 T+1 buy-point head-to-head NAV sim")
print(f"  Window: {START_DATE} -> {END_DATE}")
print("=" * 100)

# ============================================================================
# 1) Intraday-derived alt fill prices per mode
# ============================================================================
print("\n[1/5] Building intraday alt-fill price dicts...")
with open(INTRADAY_PKL, "rb") as f:
    intraday = pickle.load(f)

alt_t1115_mkt = {}   # {ticker: {date: p}}
alt_t1115_lim = {}
alt_vwap = {}

for tk, bars in intraday.items():
    if bars is None or bars.empty: continue
    b = bars.copy()
    b["time"] = pd.to_datetime(b["time"])
    b["date"] = b["time"].dt.date
    b["hm"]   = b["time"].dt.strftime("%H:%M")
    # vnstock prices in thousands VND -> scale x1000 to match BQ raw VND
    for c in ("open","high","low","close"):
        b[c] = b[c].astype(float) * 1000.0

    mkt = {}; lim = {}; vw = {}
    for d, g in b.groupby("date"):
        g = g.sort_values("time").reset_index(drop=True)
        d_ts = pd.Timestamp(d)
        p_open  = float(g.iloc[0]["close"])
        morn    = g[g["hm"] == "11:15"]
        p_1115  = float(morn.iloc[0]["close"]) if len(morn) else np.nan
        # VWAP
        v = g["volume"].values.astype(float); c = g["close"].values.astype(float)
        p_vwap = float((v*c).sum()/v.sum()) if v.sum() > 0 else float(c.mean())
        # pre-11:15 low (for LIM fill check)
        pre = g[g["hm"].isin(["09:00","09:15","09:30","09:45","10:00","10:15",
                              "10:30","10:45","11:00","11:15"])]
        p_pre_lo = float(pre["low"].min()) if len(pre) else np.nan
        # LIM @ p_open: fills if intraday traded <= p_open at any point pre-11:15.
        # On fill, executes at min(p_1115, p_open) — i.e. the limit price (no
        # better than placed) or 11:15 close if order auto-converted.
        # We use: if filled => use p_open (the limit price); else fall back later
        # in sim to Open. (Equivalent in NAV sim because fall-back = same Open.)
        if pd.notna(p_pre_lo) and pd.notna(p_open) and p_pre_lo <= p_open:
            # Conservative LIM semantics: limit BUY @ p_open fills at p_open
            # when intraday touches that level. Real HOSE limit orders fill at
            # the placed limit price (not at subsequent lower prices).
            p_lim = p_open
        else:
            # Limit didn't fill -> in NAV sim we fall back to OPEN.
            # Store NaN -> sim sees nothing -> uses open_prices default.
            p_lim = np.nan

        if pd.notna(p_1115): mkt[d_ts] = p_1115
        if pd.notna(p_lim):  lim[d_ts] = p_lim
        vw[d_ts] = p_vwap

    if mkt: alt_t1115_mkt[tk] = mkt
    if lim: alt_t1115_lim[tk] = lim
    if vw:  alt_vwap[tk] = vw

print(f"  T1115_MKT: {sum(len(v) for v in alt_t1115_mkt.values()):,} ticker-sessions")
print(f"  T1115_LIM: {sum(len(v) for v in alt_t1115_lim.values()):,} ticker-sessions (fills only)")
print(f"  VWAP:      {sum(len(v) for v in alt_vwap.values()):,} ticker-sessions")

# ============================================================================
# 2) v11 stack setup (mirrors diagnostic / 12y test)
# ============================================================================
print("\n[2/5] Loading v11 signals + filters...")
sig = bq(SIGNAL_V10.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])

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
sig["state"] = sig["time"].map(state_by_date)

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
mask_p3 = sig_f["time"].isin(overheat_dates) & sig_f["play_type"].isin(BUY_TIERS_V11)
sig_f.loc[mask_p3, "play_type"] = "AVOID_overheated"

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
# 3) Run 4 variants
# ============================================================================
def run_variant(label, alt):
    sig_vn30 = sig_f[sig_f["ticker"].isin(top30)].copy()
    prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
    liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
    LIQ_V30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}

    nav_b, trades_b = simulate(sig_f, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
        deposit_annual=0.01, state_by_date=state_ff,
        cash_etf_states={3: 0.7}, vn30_underlying=vn30_underlying,
        open_prices=open_prices, t1_open_exec=True,
        entry_alt_prices=alt, entry_fill_mode=label,
        **LIQ_FULL, name=f"{label}_BAL")

    nav_v, trades_v = simulate(sig_vn30, prices_vn30, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        ticker_sector_map=sec_map,
        deposit_annual=0.01, state_by_date=state_ff,
        cash_etf_states={3: 0.7}, vn30_underlying=vn30_underlying,
        open_prices=open_prices, t1_open_exec=True,
        entry_alt_prices=alt, entry_fill_mode=label,
        **LIQ_V30, name=f"{label}_VN30")

    nav_b["time"] = pd.to_datetime(nav_b["time"])
    nav_v["time"] = pd.to_datetime(nav_v["time"])
    s_b = nav_b.set_index("time")["nav"]
    s_v = nav_v.set_index("time")["nav"]
    common = s_b.index.intersection(s_v.index)
    return s_b.loc[common] + s_v.loc[common], len(trades_b)+len(trades_v)

print("\n[3/5] Running OPEN baseline...")
nav_open, n_open  = run_variant("open", None)
print(f"  {n_open} trades")
print("\n[4/5] Running T1115_MKT...")
nav_mkt,  n_mkt   = run_variant("t1115_mkt", alt_t1115_mkt)
print(f"  {n_mkt} trades")
print("        Running T1115_LIM...")
nav_lim,  n_lim   = run_variant("t1115_lim", alt_t1115_lim)
print(f"  {n_lim} trades")
print("        Running VWAP...")
nav_vwap, n_vwap  = run_variant("vwap", alt_vwap)
print(f"  {n_vwap} trades")

# ============================================================================
# 4) Metrics
# ============================================================================
print("\n[5/5] Metrics...")
def metrics(nav, label):
    rets = nav.pct_change().dropna()
    yrs  = (nav.index[-1] - nav.index[0]).days/365.25
    spy  = len(rets)/yrs if yrs > 0 else 252
    cagr = (nav.iloc[-1]/nav.iloc[0])**(1/yrs) - 1 if yrs > 0 else 0
    sh   = rets.mean()/rets.std()*np.sqrt(spy) if rets.std() > 0 else 0
    dd   = ((nav - nav.cummax())/nav.cummax()).min()
    cal  = cagr/abs(dd) if dd < 0 else 0
    return {"label": label, "cagr_pct": cagr*100, "sharpe": sh,
            "max_dd_pct": dd*100, "calmar": cal,
            "wealth_x": nav.iloc[-1]/nav.iloc[0]}

variants = [
    ("OPEN (baseline)", nav_open),
    ("T1115_MKT",       nav_mkt),
    ("T1115_LIM",       nav_lim),
    ("VWAP",            nav_vwap),
]

print("\n" + "=" * 100)
print("  RESULTS — 50B v11 stack, 2.5y (2023-09-15 -> 2026-05-12)")
print("=" * 100)
print(f"\n  {'Variant':<22} {'CAGR':>8} {'Sharpe':>7} {'MaxDD':>8} {'Calmar':>7} {'Wealth':>8} {'vs OPEN':>9}")
print(f"  {'-'*22} {'-'*8} {'-'*7} {'-'*8} {'-'*7} {'-'*8} {'-'*9}")
m_base = None
for label, nav in variants:
    m = metrics(nav, label)
    if m_base is None: m_base = m
    delta = m["cagr_pct"] - m_base["cagr_pct"]
    print(f"  {label:<22} {m['cagr_pct']:>+7.2f}% {m['sharpe']:>+7.2f} "
          f"{m['max_dd_pct']:>+7.1f}% {m['calmar']:>+7.2f} {m['wealth_x']:>+7.2f}x "
          f"{delta:>+7.2f}pp")

# Save NAV paths
out = pd.DataFrame({
    "time": nav_open.index,
    "OPEN":  nav_open.values,
    "T1115_MKT": nav_mkt.reindex(nav_open.index).values,
    "T1115_LIM": nav_lim.reindex(nav_open.index).values,
    "VWAP": nav_vwap.reindex(nav_open.index).values,
})
out_path = os.path.join(WORKDIR, "data", "layer3_t1_buypoint_nav.csv")
out.to_csv(out_path, index=False)
print(f"\nSaved NAV paths: {out_path}")

print("\n" + "=" * 100)
print("  Decision rule: adopt alt-mode if CAGR alpha >= +0.50pp AND Sharpe >= baseline")
print("  AND MaxDD no worse than -2pp vs baseline")
print("=" * 100)
