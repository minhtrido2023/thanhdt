# -*- coding: utf-8 -*-
"""Phase 4b — Realistic ATC alpha with liquidity gating.

ATC alt-fill price applies ONLY when ATC bar volume × 20% >= position size.
Otherwise fall back to OPEN. Compares to:
  - Phase 3 baseline OPEN
  - Phase 3 fully-optimistic ATC (no fill gate)
  - Realistic ATC (with liquidity gate)
  - Realistic T1115_LIM (more lenient, fills across morning)
  - Combined hybrid: ATC for T1_TOP, T1115_LIM for others
"""
import os, sys, io, pickle, time
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
POSITION_VND = 1.25e9      # per book leg
FILL_CAP = 0.20            # 20% of bar volume
T1_TOP_ADV = 50e9          # liquidity tier T1 cutoff (>=50B/day)

INTRADAY_PKL = os.path.join(WORKDIR, "data/intraday_full.pkl")
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]

print("=" * 100)
print("  Phase 4b: realistic ATC + LIM with liquidity gating")
print("=" * 100)

# ============================================================================
# 1) Build alt-fill dicts WITH liquidity gating
# ============================================================================
print("\n[1/4] Building gated alt-fill dicts...")
with open(INTRADAY_PKL, "rb") as f:
    intraday = pickle.load(f)

# Per-ticker ADV (full-session VND traded)
adv_by_ticker = {}
# Slot price + per-slot volume per (tk, date_ts)
slot_price = {"atc": {}, "t1115": {}, "vwap": {}}
slot_vol_vnd = {"atc": {}, "t1115": {}, "session": {}}
t0 = time.time()
for i, (tk, bars) in enumerate(intraday.items()):
    if bars is None or bars.empty: continue
    b = bars.copy()
    b["time"] = pd.to_datetime(b["time"])
    b["date_ts"] = b["time"].dt.normalize()
    b["hm"] = b["time"].dt.strftime("%H:%M")
    b["close_vnd"] = b["close"].astype(float) * 1000.0
    b["vnd_traded"] = b["close_vnd"] * b["volume"].astype(float)
    sess = b.groupby("date_ts", sort=False)["vnd_traded"].sum()
    adv_by_ticker[tk] = float(sess.mean())
    # Per-slot price + volume
    for label, hm in [("atc","14:45"), ("t1115","11:15")]:
        sub = b[b["hm"] == hm]
        if sub.empty: continue
        for _, row in sub.iterrows():
            d_ts = row["date_ts"]
            slot_price[label].setdefault(tk, {})[d_ts] = float(row["close_vnd"])
            slot_vol_vnd[label].setdefault(tk, {})[d_ts] = float(row["vnd_traded"])
    # VWAP per day
    vwap_grp = b.groupby("date_ts", sort=False)
    vsum = vwap_grp["vnd_traded"].sum()
    psum = vwap_grp.apply(lambda g: (g["close_vnd"]*g["volume"]).sum())
    vbase = vwap_grp["volume"].sum()
    vwap = (psum / vbase.replace(0, np.nan)).ffill().bfill()
    for d_ts, v in vwap.items():
        if not pd.isna(v):
            slot_price["vwap"].setdefault(tk, {})[d_ts] = float(v)
    # Session vol
    for d_ts, v in sess.items():
        slot_vol_vnd["session"].setdefault(tk, {})[d_ts] = float(v)
    if (i+1) % 100 == 0:
        print(f"  {i+1}/{len(intraday)} ({time.time()-t0:.0f}s)")
print(f"  Done: {time.time()-t0:.0f}s")

def gated_alt(slot_label):
    """Return alt_prices dict only for (tk, d_ts) where bar volume × FILL_CAP >= POSITION_VND."""
    px = slot_price[slot_label]
    vol = slot_vol_vnd.get(slot_label, {})
    out = {}
    n_pass = 0; n_total = 0
    for tk, d_px in px.items():
        for d_ts, p in d_px.items():
            n_total += 1
            v = vol.get(tk, {}).get(d_ts)
            if v is None or v * FILL_CAP < POSITION_VND:
                continue  # fill capacity insufficient -> fall back to OPEN
            out.setdefault(tk, {})[d_ts] = p
            n_pass += 1
    print(f"  Gated {slot_label}: {n_pass:,} / {n_total:,} fills pass ({100*n_pass/max(n_total,1):.1f}%)")
    return out

def hybrid_atc_for_top_t1115_for_others():
    """ATC for T1_TOP tickers, T1115_LIM (limit @ p_open i.e. baseline price) for others.
    For T1115_LIM mode, we use t1115 price as the alt-fill (a passive market BUY at
    11:15, more lenient on fill across morning bars)."""
    out = {}
    for tk, d_px in slot_price["atc"].items():
        adv = adv_by_ticker.get(tk, 0)
        for d_ts, p in d_px.items():
            v = slot_vol_vnd["atc"].get(tk, {}).get(d_ts)
            if adv >= T1_TOP_ADV and v is not None and v*FILL_CAP >= POSITION_VND:
                out.setdefault(tk, {})[d_ts] = p
    # For all other tickers (non-TOP), use t1115 with own gate
    for tk, d_px in slot_price["t1115"].items():
        adv = adv_by_ticker.get(tk, 0)
        if adv >= T1_TOP_ADV: continue   # already covered by ATC above
        for d_ts, p in d_px.items():
            v = slot_vol_vnd["t1115"].get(tk, {}).get(d_ts)
            if v is not None and v*FILL_CAP >= POSITION_VND:
                out.setdefault(tk, {})[d_ts] = p
    n = sum(len(v) for v in out.values())
    print(f"  Hybrid (ATC for TOP, T1115 for mid/thin): {n:,} fills")
    return out

print("\n  Building 4 gated variants...")
alt_atc_gated  = gated_alt("atc")
alt_t1115_gated = gated_alt("t1115")
alt_atc_optimistic = {tk: dict(d_px) for tk, d_px in slot_price["atc"].items()}  # no gate
alt_hybrid = hybrid_atc_for_top_t1115_for_others()

# ============================================================================
# 2) v11 stack setup
# ============================================================================
print("\n[2/4] Loading v11 signals...")
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

print("\n[3/4] Running 5 variants...")
print("  Running OPEN baseline...")
nav_open = run_variant("open", None)
print("  Running ATC OPTIMISTIC (no fill gate - matches Phase 3)...")
nav_atc_opt = run_variant("atc_optimistic", alt_atc_optimistic)
print("  Running ATC REALISTIC (gated)...")
nav_atc_real = run_variant("atc_realistic", alt_atc_gated)
print("  Running T1115 REALISTIC (gated)...")
nav_t1115_real = run_variant("t1115_realistic", alt_t1115_gated)
print("  Running HYBRID (ATC for TOP, T1115 for others)...")
nav_hybrid = run_variant("hybrid", alt_hybrid)

# ============================================================================
# Metrics
# ============================================================================
def metrics(nav, start=None, end=None):
    if start: nav = nav[nav.index >= pd.Timestamp(start)]
    if end:   nav = nav[nav.index <= pd.Timestamp(end)]
    if len(nav) < 30: return None
    rets = nav.pct_change().dropna()
    yrs = (nav.index[-1]-nav.index[0]).days/365.25
    spy = len(rets)/yrs if yrs > 0 else 252
    cagr = (nav.iloc[-1]/nav.iloc[0])**(1/yrs)-1 if yrs > 0 else 0
    sh = rets.mean()/rets.std()*np.sqrt(spy) if rets.std() > 0 else 0
    dd = ((nav-nav.cummax())/nav.cummax()).min()
    cal = cagr/abs(dd) if dd < 0 else 0
    return {"cagr_pct": cagr*100, "sharpe": sh, "max_dd_pct": dd*100, "calmar": cal,
            "wealth_x": nav.iloc[-1]/nav.iloc[0]}

variants = [
    ("OPEN (baseline)",           nav_open),
    ("ATC OPTIMISTIC (Phase 3)",  nav_atc_opt),
    ("ATC REALISTIC (gated)",     nav_atc_real),
    ("T1115 REALISTIC (gated)",   nav_t1115_real),
    ("HYBRID (TOP=ATC, rest=T1115)", nav_hybrid),
]

PERIODS = [
    ("FULL 2.5y",   START_DATE, END_DATE),
    ("Sub 2024",    "2024-01-01", "2024-12-31"),
    ("Sub 2025",    "2025-01-01", "2025-12-31"),
    ("Sub 2026",    "2026-01-01", END_DATE),
]

print("\n[4/4] Results")
for plabel, ps, pe in PERIODS:
    m_base = metrics(nav_open, ps, pe)
    if m_base is None: continue
    print(f"\n{'='*92}")
    print(f"  {plabel} -- baseline CAGR {m_base['cagr_pct']:+.2f}% / Sh {m_base['sharpe']:+.2f}")
    print(f"{'='*92}")
    print(f"  {'Variant':<32} {'CAGR':>8} {'Sharpe':>7} {'MaxDD':>8} {'Calmar':>7} {'vs OPEN':>9}")
    print(f"  {'-'*32} {'-'*8} {'-'*7} {'-'*8} {'-'*7} {'-'*9}")
    for label, nav in variants:
        m = metrics(nav, ps, pe)
        if m is None: continue
        delta = m["cagr_pct"] - m_base["cagr_pct"]
        print(f"  {label:<32} {m['cagr_pct']:>+7.2f}% {m['sharpe']:>+7.2f} "
              f"{m['max_dd_pct']:>+7.1f}% {m['calmar']:>+7.2f} {delta:>+7.2f}pp")
