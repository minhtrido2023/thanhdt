#!/usr/bin/env python3
"""Test sector_limit Fin/RE variants on Jun 2025 → Mar 2026 OOS period."""
import warnings; warnings.filterwarnings("ignore")
import os, sys, bisect
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import simulate, bq, VNI_QUERY
from test_round14_stability import SIGNAL_V10

START = "2025-06-09"; END = "2026-05-14"
INIT_NAV = 50e9
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
BUY_TIERS = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
             "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}
FRESH_Q_BY_STATE = {1: 30, 2: 60, 3: 60}

# ─── Load and prepare V11-filtered signals (reuse from sim_v11_from_jun2025) ───
print("Loading signals + applying V11 filters ...")
sig = bq(SIGNAL_V10.format(start="2024-01-01", end=END))
sig["time"] = pd.to_datetime(sig["time"])

releases = bq(f"""SELECT tf.ticker, tf.Release_Date FROM tav2_bq.ticker_financial AS tf
WHERE tf.Release_Date BETWEEN DATE '2023-01-01' AND DATE '{END}'""")
releases["Release_Date"] = pd.to_datetime(releases["Release_Date"])
release_by_ticker = releases.groupby("ticker")["Release_Date"].apply(sorted).to_dict()

ds = np.empty(len(sig))
for i, (tk, t) in enumerate(zip(sig["ticker"].values, sig["time"].values)):
    arr = release_by_ticker.get(tk)
    if not arr: ds[i] = np.nan; continue
    idx = bisect.bisect_right(arr, pd.Timestamp(t))
    if idx == 0: ds[i] = np.nan; continue
    ds[i] = (pd.Timestamp(t) - arr[idx-1]).days
sig["days_since_release"] = ds

state_df = bq(f"""SELECT s.time, s.state FROM tav2_bq.vnindex_5state AS s
                  WHERE s.time BETWEEN DATE '2024-01-01' AND DATE '{END}'""")
state_df["time"] = pd.to_datetime(state_df["time"])
state_by_date = dict(zip(state_df["time"], state_df["state"]))

vni = bq(f"""SELECT t.time, t.Close, t.D_RSI, t.MA200 FROM tav2_bq.ticker AS t
             WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '2023-01-01' AND DATE '{END}'""")
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
if vni["MA200"].isna().all():
    vni["MA200"] = vni["Close"].rolling(200, min_periods=200).mean()
vni["ratio"] = vni["Close"] / vni["MA200"]
vni_ratio_today = dict(zip(vni["time"], vni["ratio"]))
vni_rsi_today = dict(zip(vni["time"], vni["D_RSI"]))

# Apply V11 filter
sig["state"] = sig["time"].map(state_by_date)
sig["vni_ratio"] = sig["time"].map(vni_ratio_today)
sig["vni_rsi"] = sig["time"].map(vni_rsi_today)
keep = sig["state"].isin([4, 5])
has_rel = sig["days_since_release"].notna()
keep |= (sig["state"] == 1) & has_rel & (sig["days_since_release"] <= 30)
keep |= sig["state"].isin([2, 3]) & has_rel & (sig["days_since_release"] <= 60)
sig = sig[keep].copy()

overheat = (sig["vni_ratio"] > 1.30).fillna(False)
regime = ((sig["state"] == 5) | (sig["vni_rsi"] > 0.75)).fillna(False)
sig.loc[overheat & regime & sig["play_type"].isin(BUY_TIERS), "play_type"] = "AVOID_overheated"

prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}
vni_dates_q = bq(VNI_QUERY.format(start=START, end=END))
vni_dates_q["time"] = pd.to_datetime(vni_dates_q["time"])
vni_dates = sorted(vni_dates_q["time"].unique())
sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
                AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
            """).set_index("ticker")["s"].to_dict()
LIQ_FULL = {"liquidity_volume_pct":0.20, "max_fill_days":5,
            "liquidity_lookup":liq_map, "exit_slippage_tiered":True}

state_by_date_ts = {pd.Timestamp(k): int(v) for k,v in state_by_date.items()}

# ─── Run variants ────────────────────────────────────────────────────
def run(label, fin_re_cap):
    print(f"\nRunning {label} (sec 8 cap={fin_re_cap}) ...", flush=True)
    nav_df, trades_df = simulate(sig, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=INIT_NAV,
        sector_limit_per_sector={8: fin_re_cap}, ticker_sector_map=sec_map,
        state_by_date=state_by_date_ts,
        **LIQ_FULL)
    nav_df["time"] = pd.to_datetime(nav_df["time"])
    trades_df["entry_date"] = pd.to_datetime(trades_df["entry_date"])
    trades_df = trades_df[trades_df["entry_date"] >= pd.Timestamp(START)].copy()
    return nav_df, trades_df

variants = [("8:2", 2), ("8:3", 3), ("8:4 (baseline)", 4), ("8:5", 5), ("8:10 (~no cap)", 10)]
results = {}
for label, cap in variants:
    nav_df, trades_df = run(label, cap)
    results[label] = (nav_df, trades_df)

# ─── Compare ─────────────────────────────────────────────────────────
print("\n" + "═"*100)
print(f"  SECTOR_LIMIT Fin/RE comparison — period {START} → {END}, init {INIT_NAV/1e9:.0f}B")
print("═"*100)
print(f"\n  {'Variant':<22}{'Final NAV':>12}{'Total Ret':>11}{'CAGR':>9}{'Sharpe':>8}{'MaxDD':>9}{'Trades':>8}{'WR':>7}{'Stops':>7}")
print("  " + "-"*94)
for label, (nav_df, trades_df) in results.items():
    nav_w = nav_df[(nav_df["time"]>=pd.Timestamp(START)) & (nav_df["time"]<=pd.Timestamp(END))]
    if len(nav_w) < 2: continue
    final = nav_w["nav"].iloc[-1]
    tot = (final/INIT_NAV - 1)*100
    yrs = (nav_w["time"].iloc[-1] - nav_w["time"].iloc[0]).days / 365.25
    cagr = (final/INIT_NAV)**(1/yrs) - 1 if yrs > 0 else 0
    rets = nav_w["nav"].pct_change().dropna()
    sharpe = rets.mean()/rets.std() * np.sqrt(252) if rets.std() > 0 else 0
    dd = ((nav_w["nav"] - nav_w["nav"].cummax()) / nav_w["nav"].cummax()).min()
    ntr = len(trades_df)
    wr = (trades_df["ret_net"]>0).mean()*100 if ntr > 0 else 0
    stops = (trades_df["reason"]=="STOP").sum()
    print(f"  {label:<22}{final/1e9:>11.3f}B{tot:>+10.2f}%{cagr*100:>+8.2f}%{sharpe:>8.2f}{dd*100:>+8.2f}%"
          f"{ntr:>8d}{wr:>+6.1f}%{stops:>7d}")

# Per-variant trade-level analysis on Đợt 2/3
print("\n" + "─"*100)
print("  Trade composition by sector for ĐỢT 2 (12-14/08/2025) and ĐỢT 3 (09-15/01/2026)")
print("─"*100)
for label, (nav_df, trades_df) in results.items():
    d2 = trades_df[(trades_df["entry_date"] >= "2025-08-12") & (trades_df["entry_date"] <= "2025-08-14")]
    d3 = trades_df[(trades_df["entry_date"] >= "2026-01-09") & (trades_df["entry_date"] <= "2026-01-15")]
    print(f"\n  {label}:")
    for name, batch in [("Đợt 2", d2), ("Đợt 3", d3)]:
        sec_breakdown = batch["ticker"].map(sec_map).value_counts().to_dict()
        avg = batch["ret_net"].mean()*100 if len(batch) > 0 else 0
        wr = (batch["ret_net"]>0).mean()*100 if len(batch) > 0 else 0
        print(f"    {name}: N={len(batch)}, avg={avg:+.2f}%, WR={wr:.1f}%, sectors={sec_breakdown}")

# Save
for label, (nav_df, trades_df) in results.items():
    safe = label.replace(":","_").replace(" ","_").replace("(","").replace(")","")
    trades_df.to_csv(f"sim_sec_limit_{safe}_trades.csv", index=False)
print("\n💾 Saved per-variant trade CSVs")
