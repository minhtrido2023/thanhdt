# -*- coding: utf-8 -*-
"""Phase 3 — Full intraday alpha curve.

Test market-order fill at every 15m slot from 09:15 -> 14:45 and report CAGR
alpha curve. Confirms whether the +1.27pp T1115 result is slot-specific or
a generic 'avoid ATO' effect.

Sub-period validation (2024 / 2025 / 2026) included to check robustness.
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

# Time slots to test (HH:MM strings; bar close price at that minute)
SLOTS = ["09:15","09:30","09:45","10:00","10:15","10:30","10:45",
         "11:00","11:15","13:00","13:15","13:30","14:00","14:15","14:30","14:45"]

print("=" * 100)
print("  Phase 3: full intraday alpha curve (16 time slots)")
print(f"  Window: {START_DATE} -> {END_DATE}, 50B v11 stack")
print("=" * 100)

# ============================================================================
# 1) Build per-slot alt fill dict from intraday_full.pkl
# ============================================================================
print("\n[1/4] Building 16 alt-fill price dicts (one per time slot)...")
with open(INTRADAY_PKL, "rb") as f:
    intraday = pickle.load(f)

# {slot_label: {ticker: {date: close_price_at_that_slot}}}
alt_per_slot = {s: {} for s in SLOTS}

for tk, bars in intraday.items():
    if bars is None or bars.empty: continue
    b = bars.copy()
    b["time"] = pd.to_datetime(b["time"])
    b["date"] = b["time"].dt.date
    b["hm"]   = b["time"].dt.strftime("%H:%M")
    for c in ("open","high","low","close"):
        b[c] = b[c].astype(float) * 1000.0  # scale to raw VND
    for d, g in b.groupby("date"):
        g = g.sort_values("time").reset_index(drop=True)
        d_ts = pd.Timestamp(d)
        for slot in SLOTS:
            bar = g[g["hm"] == slot]
            if len(bar) == 0: continue
            px = float(bar.iloc[0]["close"])
            if not pd.isna(px) and px > 0:
                alt_per_slot[slot].setdefault(tk, {})[d_ts] = px

print(f"  Built {len(alt_per_slot)} slot dicts.")
for s in SLOTS[::3]:
    n = sum(len(v) for v in alt_per_slot[s].values())
    print(f"    {s}: {n:,} ticker-sessions")

# ============================================================================
# 2) v11 stack setup (mirror earlier scripts)
# ============================================================================
print("\n[2/4] Loading v11 signals + filters...")
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
# 3) Run sims for each slot
# ============================================================================
def run_variant(label, alt):
    sig_vn30 = sig_f[sig_f["ticker"].isin(top30)].copy()
    prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
    liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
    LIQ_V30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}
    nav_b, _ = simulate(sig_f, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
        deposit_annual=0.01, state_by_date=state_ff,
        cash_etf_states={3: 0.7}, vn30_underlying=vn30_underlying,
        open_prices=open_prices, t1_open_exec=True,
        entry_alt_prices=alt, entry_fill_mode=label,
        **LIQ_FULL, name=f"{label}_BAL")
    nav_v, _ = simulate(sig_vn30, prices_vn30, vni_dates,
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
    return s_b.loc[common] + s_v.loc[common]

print("\n[3/4] Running OPEN baseline + 16 slot variants...")
nav_open = run_variant("open", None)
print("  OPEN done")

slot_navs = {}
for s in SLOTS:
    slot_navs[s] = run_variant(f"slot_{s}", alt_per_slot[s])
    print(f"  {s} done")

# ============================================================================
# 4) Metrics per slot, full + sub-periods
# ============================================================================
def metrics(nav, start=None, end=None):
    if start: nav = nav[nav.index >= pd.Timestamp(start)]
    if end:   nav = nav[nav.index <= pd.Timestamp(end)]
    if len(nav) < 30: return None
    rets = nav.pct_change().dropna()
    yrs  = (nav.index[-1] - nav.index[0]).days/365.25
    spy  = len(rets)/yrs if yrs > 0 else 252
    cagr = (nav.iloc[-1]/nav.iloc[0])**(1/yrs) - 1 if yrs > 0 else 0
    sh   = rets.mean()/rets.std()*np.sqrt(spy) if rets.std() > 0 else 0
    dd   = ((nav - nav.cummax())/nav.cummax()).min()
    cal  = cagr/abs(dd) if dd < 0 else 0
    return {"cagr_pct": cagr*100, "sharpe": sh, "max_dd_pct": dd*100, "calmar": cal,
            "wealth_x": nav.iloc[-1]/nav.iloc[0]}

PERIODS = [
    ("FULL 2.5y",   START_DATE, END_DATE),
    ("Sub 2024",    "2024-01-01", "2024-12-31"),
    ("Sub 2025",    "2025-01-01", "2025-12-31"),
    ("Sub 2026",    "2026-01-01", END_DATE),
]

print("\n[4/4] Building alpha curve...")
for plabel, ps, pe in PERIODS:
    m_base = metrics(nav_open, ps, pe)
    if m_base is None:
        print(f"\n--- {plabel}: insufficient data ---"); continue
    print(f"\n{'='*88}")
    print(f"  {plabel} -- baseline CAGR {m_base['cagr_pct']:+.2f}% / Sh {m_base['sharpe']:+.2f}")
    print(f"{'='*88}")
    print(f"  {'Slot':<8} {'CAGR':>8} {'Sharpe':>7} {'MaxDD':>8} {'Calmar':>7} {'vs OPEN':>9}")
    print(f"  {'-'*8} {'-'*8} {'-'*7} {'-'*8} {'-'*7} {'-'*9}")
    for s in SLOTS:
        m = metrics(slot_navs[s], ps, pe)
        if m is None: continue
        delta = m["cagr_pct"] - m_base["cagr_pct"]
        print(f"  {s:<8} {m['cagr_pct']:>+7.2f}% {m['sharpe']:>+7.2f} "
              f"{m['max_dd_pct']:>+7.1f}% {m['calmar']:>+7.2f} {delta:>+7.2f}pp")

# Save full data
all_rows = []
for plabel, ps, pe in PERIODS:
    m_base = metrics(nav_open, ps, pe)
    if m_base is None: continue
    base_row = {"period": plabel, "slot": "OPEN", **m_base, "alpha_pp": 0.0}
    all_rows.append(base_row)
    for s in SLOTS:
        m = metrics(slot_navs[s], ps, pe)
        if m is None: continue
        all_rows.append({"period": plabel, "slot": s, **m,
                          "alpha_pp": m["cagr_pct"] - m_base["cagr_pct"]})
out = pd.DataFrame(all_rows)
out_path = os.path.join(WORKDIR, "data", "layer3_t1_buypoint_curve.csv")
out.to_csv(out_path, index=False)
print(f"\nSaved curve data: {out_path}")
