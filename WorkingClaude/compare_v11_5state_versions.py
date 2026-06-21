# -*- coding: utf-8 -*-
"""
compare_v11_5state_versions.py
==============================
Integrated V11 backtest comparison across 3 different 5-state versions.

Sources tested:
  A) baseline   — original (smooth mode15+min_stay7+gate60) from BQ backup
                  `tav2_bq.vnindex_5state_baseline_pre_v2g_20260517_144254`
  B) v2g        — no-smooth + gate30 + RSI dvg only (deployed 2026-05-17)
                  `tav2_bq.vnindex_5state_baseline_pre_v2g_pe3_20260521_004032`
  C) v2g_pe3c   — current production (no-smooth + gate30 + PE clean 2006+
                  + PE composite 0.03 + S2_bull + mask_2007) — current `tav2_bq.vnindex_5state`

Backtest: V11 (V4 SV_TIGHT + P3 + V6 ETF + 50/50 BAL+VN30) over 2014-2026, 50B NAV, T+1 Open exec.
"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np
import pandas as pd
import bisect

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import simulate, bq, VNI_QUERY
from signal_v10_sql import SIGNAL_V10

START_DATE = "2014-01-01"
END_DATE   = "2026-05-15"
TOTAL_NAV  = 50e9
BOOK_NAV   = 25e9
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}
TIER_BAL = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]
PERIODS = [
    ("FULL 2014-2026",  "2014-01-01", "2026-05-15"),
    ("Pre-OOS 2014-19", "2014-01-01", "2019-12-31"),
    ("Mid 2018-2023",   "2018-01-01", "2023-12-31"),
    ("OOS 2024-2026",   "2024-01-01", "2026-05-15"),
]
STATE_SOURCES = [
    ("A_baseline",   "tav2_bq.vnindex_5state_baseline_pre_v2g_20260517_144254"),
    ("B_v2g",        "tav2_bq.vnindex_5state_v2g_only"),
    ("C_pe3c_raw",   "tav2_bq.vnindex_5state"),
    ("D_pe3c_s3",    "tav2_bq.vnindex_5state_v2g_pe3c_s3"),
    ("E_pe3c_s5",    "tav2_bq.vnindex_5state_v2g_pe3c_s5"),
    ("F_pe3c_s10",   "tav2_bq.vnindex_5state_v2g_pe3c_s10"),
    ("G_pe3c_s15",   "tav2_bq.vnindex_5state_v2g_pe3c_s15"),
]

print("=" * 100)
print("  V11 INTEGRATED COMPARISON — 5-state version sweep")
print(f"  Period: {START_DATE} → {END_DATE}, NAV={TOTAL_NAV/1e9:.0f}B")
print("=" * 100)

# ── Shared loads (signals, releases, prices, open, universe) ────────────────
print("\n[1/5] Loading v10 signals (12y)...")
sig = bq(SIGNAL_V10.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
print(f"  {len(sig):,} signal rows")

print("\n[2/5] Computing days_since_release...")
releases = bq(f"""SELECT tf.ticker, tf.Release_Date FROM tav2_bq.ticker_financial AS tf
WHERE tf.Release_Date BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
ORDER BY tf.ticker, tf.Release_Date""")
releases["Release_Date"] = pd.to_datetime(releases["Release_Date"])
release_by_ticker = releases.sort_values(["ticker", "Release_Date"]).groupby("ticker")["Release_Date"].apply(list).to_dict()

ds = np.full(len(sig), np.nan)
tk_arr = sig["ticker"].values; t_arr = sig["time"].values
for i in range(len(sig)):
    tk = tk_arr[i]; t = t_arr[i]
    arr = release_by_ticker.get(tk, [])
    if not arr: continue
    idx = bisect.bisect_right(arr, pd.Timestamp(t))
    if idx == 0: continue
    ds[i] = (pd.Timestamp(t) - arr[idx-1]).days
sig["days_since_release"] = ds

print("\n[3/5] Loading VNINDEX + Open prices + sectors + top30 (shared)...")
vni_full = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' ORDER BY t.time""")
vni_full["time"] = pd.to_datetime(vni_full["time"])
vni_full["ratio"] = vni_full["Close"] / vni_full["MA200"]

OPEN_SQL = f"""
SELECT t.ticker, t.time, t.Open AS open_price FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
  AND t.Open IS NOT NULL
"""
opens_df = bq(OPEN_SQL)
opens_df["time"] = pd.to_datetime(opens_df["time"])
open_prices = {tk: dict(zip(g["time"], g["open_price"]))
               for tk, g in opens_df.groupby("ticker")}

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

# ── Per-source: run V11 sim with given state table ──────────────────────────
def run_v11_with_state(label, state_table):
    print(f"\n[4/5] === Running V11 sim with state source: {label} ({state_table}) ===")
    state_df = bq(f"""SELECT s.time, s.state FROM `lithe-record-440915-m9.{state_table}` AS s
WHERE s.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' ORDER BY s.time""")
    state_df["time"] = pd.to_datetime(state_df["time"])
    state_by_date = dict(zip(state_df["time"], state_df["state"]))
    n_state = len(state_df)
    n_crisis = int((state_df["state"]==1).sum())
    n_bull = int((state_df["state"]>=4).sum())
    print(f"  Loaded {n_state} state rows | CRISIS={n_crisis} BULL+={n_bull}")

    vf = vni_full.copy()
    vf["state"] = vf["time"].map(state_by_date)
    vf["overheat"] = ((vf["ratio"] > 1.30) & ((vf["state"] == 5) | (vf["D_RSI"] > 0.75)))
    overheat_dates = set(vf[vf["overheat"]]["time"])
    print(f"  Overheat days: {len(overheat_dates)}")

    sig_l = sig.copy()
    sig_l["state"] = sig_l["time"].map(state_by_date)

    def sv_tight_keep(row):
        s = row["state"]; days = row["days_since_release"]
        if pd.isna(s): return True
        s = int(s)
        if s in (4, 5): return True
        if s == 1: return pd.notna(days) and days <= 30
        if s in (2, 3): return pd.notna(days) and days <= 60
        return True
    mask_bacore = sig_l["play_type"].isin(BUY_TIERS_V11)
    mask_keep = (~mask_bacore) | sig_l.apply(sv_tight_keep, axis=1)
    n_filt = (mask_bacore & ~sig_l.apply(sv_tight_keep, axis=1)).sum()
    sig_f = sig_l[mask_keep].copy()
    mask_p3 = sig_f["time"].isin(overheat_dates) & sig_f["play_type"].isin(BUY_TIERS_V11)
    n_p3 = mask_p3.sum()
    sig_f.loc[mask_p3, "play_type"] = "AVOID_overheated"
    print(f"  SV_TIGHT filtered {n_filt:,} | P3 blocked {n_p3:,}")

    prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_f.groupby("ticker")}
    liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig_f.iterrows()}

    state_ff = {}; last_s = None
    for d in vni_dates:
        s = state_by_date.get(d)
        if s is not None: last_s = s
        state_ff[d] = last_s

    LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
                "liquidity_lookup": liq_map, "exit_slippage_tiered": True}

    sig_vn30 = sig_f[sig_f["ticker"].isin(top30)].copy()
    prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
    liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
    LIQ_V30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}

    # BAL leg
    nav_b, _ = simulate(sig_f, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map,
        deposit_annual=0.01, state_by_date=state_ff,
        cash_etf_states={3: 0.7}, vn30_underlying=vn30_underlying,
        open_prices=open_prices, t1_open_exec=True,
        **LIQ_FULL, name=f"{label}_BAL")

    # VN30 leg
    nav_v, _ = simulate(sig_vn30, prices_vn30, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        ticker_sector_map=sec_map,
        deposit_annual=0.01, state_by_date=state_ff,
        cash_etf_states={3: 0.7}, vn30_underlying=vn30_underlying,
        open_prices=open_prices, t1_open_exec=True,
        **LIQ_V30, name=f"{label}_VN30")

    nav_b["time"] = pd.to_datetime(nav_b["time"])
    nav_v["time"] = pd.to_datetime(nav_v["time"])
    nav_b_s = nav_b.set_index("time")["nav"]
    nav_v_s = nav_v.set_index("time")["nav"]
    common = nav_b_s.index.intersection(nav_v_s.index)
    return nav_b_s.loc[common] + nav_v_s.loc[common]

# Run 3 sources
navs = {}
for label, table in STATE_SOURCES:
    navs[label] = run_v11_with_state(label, table)
    print(f"  → {label} final NAV: {navs[label].iloc[-1]/1e9:.2f}B (×{navs[label].iloc[-1]/TOTAL_NAV:.2f})")

# ── Metrics per window ───────────────────────────────────────────────────────
def window_metrics(nav, label):
    rets = nav.pct_change().dropna()
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    spy = len(rets)/yrs if yrs > 0 else 252
    cagr = (nav.iloc[-1]/nav.iloc[0])**(1/yrs) - 1 if yrs > 0 else 0
    sh = rets.mean()/rets.std() * np.sqrt(spy) if rets.std() > 0 else 0
    dd = ((nav - nav.cummax())/nav.cummax()).min()
    cal = cagr/abs(dd) if dd < 0 else 0
    return {"label": label, "cagr": cagr*100, "sh": sh, "dd": dd*100, "cm": cal,
            "wealth": nav.iloc[-1]/nav.iloc[0]}

print("\n" + "=" * 110)
print("  V11 INTEGRATED RESULTS — across 5-state versions, by period")
print("=" * 110)
print()
print(f"  {'Period':<22} {'Source':<14} {'CAGR':>8} {'Sharpe':>7} {'DD':>9} {'Calmar':>7} {'Wealth':>9}")
print(f"  {'-'*22} {'-'*14} {'-'*8} {'-'*7} {'-'*9} {'-'*7} {'-'*9}")

all_results = []
for plabel, ps, pe in PERIODS:
    ps_ts = pd.Timestamp(ps); pe_ts = pd.Timestamp(pe)
    per_period = {}
    for label, _ in STATE_SOURCES:
        sub = navs[label][(navs[label].index >= ps_ts) & (navs[label].index <= pe_ts)]
        if len(sub) < 30: continue
        m = window_metrics(sub, label)
        per_period[label] = m
    for label, _ in STATE_SOURCES:
        if label not in per_period: continue
        m = per_period[label]
        print(f"  {plabel:<22} {label:<14} {m['cagr']:>+7.2f}% {m['sh']:>+7.2f} {m['dd']:>+8.1f}% {m['cm']:>+7.2f} {m['wealth']:>+7.2f}×")
        all_results.append({"period": plabel, "source": label,
                            "cagr": m['cagr'], "sharpe": m['sh'], "dd": m['dd'],
                            "calmar": m['cm'], "wealth": m['wealth']})
    # Deltas vs baseline
    if "A_baseline" in per_period:
        base = per_period["A_baseline"]
        for label, _ in STATE_SOURCES:
            if label == "A_baseline" or label not in per_period: continue
            m = per_period[label]
            dc = m['cagr'] - base['cagr']; ds = m['sh'] - base['sh']; dd_ = m['dd'] - base['dd']
            print(f"  {'':<22} Δ{label}-baseline   ΔCAGR{dc:+.2f}pp  ΔSh{ds:+.2f}  ΔDD{dd_:+.1f}pp")
    print()

df = pd.DataFrame(all_results)
df.to_csv(os.path.join(WORKDIR, "compare_v11_5state_versions.csv"), index=False)
print(f"\nSaved → compare_v11_5state_versions.csv")

# Per-source state distribution log (sanity check)
print("\n=== State distribution check ===")
for label, table in STATE_SOURCES:
    sd = bq(f"""SELECT s.state, COUNT(*) as n FROM `lithe-record-440915-m9.{table}` AS s
WHERE s.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' GROUP BY s.state ORDER BY s.state""")
    total = sd["n"].sum()
    pcts = " ".join(f"{int(r['state'])}={r['n']/total*100:.1f}%" for _, r in sd.iterrows())
    print(f"  {label:<14} {pcts}")
