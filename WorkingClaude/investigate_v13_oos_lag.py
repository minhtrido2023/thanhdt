#!/usr/bin/env python3
"""
investigate_v13_oos_lag.py — Diagnose why v13 OOS underperforms v12

Hypotheses:
  H1: Overfit — surprise threshold 0.5 tuned to historical sweet spot
  H2: Regime dependent — v13 excels in bear/sideways, lags in bull (OOS = more bull)
  H3: Statistical noise — small N
  H4: PEAD alpha decay — VN market becoming more efficient

Tests:
  T1: Threshold sensitivity (0.3, 0.5, 0.7, 1.0, 1.5) on IS vs OOS
      → if best threshold flips → overfit
      → if consistent → robust
  T2: Regime-conditional event analysis (bin by VNI 6M return at entry)
      → does v13 win in bear/flat AND lose in bull?
  T3: Year-by-year event WR comparison NPR-only vs NPR+surprise
      → does surprise add value in EVERY year or only specific ones?
  T4: PEAD alpha decay test — IC by 2y bucket
      → is surprise IC weakening over time?
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, pickle
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
INIT_NAV = 50e9

print("="*100)
print("  v13 OOS LAG INVESTIGATION")
print("="*100)

# Load + setup
print("\n[Setup] Loading caches ...")
with open("data/earnings_px.pkl","rb") as f: px_data = pickle.load(f)
px_data["time"] = pd.to_datetime(px_data["time"])
px_close = px_data.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns")
px_close.index = master_idx
all_dates = np.array(master_idx)

with open("data/lagged_pos_ov.pkl","rb") as f: ov = pickle.load(f)
ov["time"] = pd.to_datetime(ov["time"])
px_open = ov.pivot_table(index="time", columns="ticker", values="Open", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
liq = ov.pivot_table(index="time", columns="ticker", values="Volume_3M_P50", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)

with open("data/earnings_surprise_data.pkl","rb") as f: fin = pickle.load(f)
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"])
FLOOR = 1e9
fin["exp_B_MA"] = fin[["NP_P1","NP_P2","NP_P3","NP_P4"]].mean(axis=1)
fin["surprise_B_MA"] = ((fin["NP_P0"] - fin["exp_B_MA"]) / np.maximum(np.abs(fin["exp_B_MA"]), FLOOR)).clip(-5, 5)

ev_class = pd.read_csv("data/earnings_events_classified.csv", parse_dates=["Release_Date"])
ev = ev_class.merge(fin[["ticker","quarter","Release_Date","surprise_B_MA"]],
                     on=["ticker","quarter","Release_Date"], how="left")
ev = ev.sort_values(["ticker","Release_Date"]).reset_index(drop=True)
ev["year"] = ev["Release_Date"].dt.year

# Get VNI regime at each event
vni = pd.read_csv("data/VNINDEX.csv", parse_dates=["time"])
vni = vni.set_index("time").sort_index()
vni["vni_6m_ret"] = vni["Close"].pct_change(126) * 100

# Merge VNI regime at entry_dt (T+5)
def get_vni_6m(rdt):
    target = rdt + pd.Timedelta(days=7)  # approx T+5
    # find closest VNI date
    idx = vni.index.searchsorted(target)
    if idx >= len(vni): idx = len(vni) - 1
    return vni.iloc[idx]["vni_6m_ret"]

print("[Setup] Computing VNI regime per event ...")
ev["vni_6m"] = ev["Release_Date"].apply(get_vni_6m)
ev["regime"] = pd.cut(ev["vni_6m"], bins=[-100, -10, 5, 20, 100],
                      labels=["BEAR", "FLAT", "MILD_BULL", "STRONG_BULL"])

print(f"  Events: {len(ev):,}")
print(f"  With surprise: {ev['surprise_B_MA'].notna().sum():,}")
print(f"  With regime: {ev['regime'].notna().sum():,}")

# ─── T1: Threshold sensitivity ───────────────────────────────────────────
print("\n" + "="*100)
print("  T1: SURPRISE THRESHOLD SENSITIVITY (event-level, NP_R≥15 baseline)")
print("="*100)

base = ev[ev["NP_R"] >= 15].dropna(subset=["surprise_B_MA","post_ret"]).copy()
print(f"  Base universe (NP_R≥15): {len(base):,} events")

# IS = 2014-2018, OOS = 2019-2026
is_mask = (base["year"] >= 2014) & (base["year"] <= 2018)
oos_mask = (base["year"] >= 2019) & (base["year"] <= 2026)

print(f"\n  IS (2014-2018): {is_mask.sum():,}  | OOS (2019-2026): {oos_mask.sum():,}")
print(f"\n  Threshold sensitivity (event-level WR + avg post_ret):")
print(f"  {'Threshold':<12}{'IS_N':>7}{'IS_WR':>9}{'IS_avg':>10}{'OOS_N':>7}{'OOS_WR':>9}{'OOS_avg':>10}{'Δ_avg':>10}")
print("  " + "-"*78)
for thr in [-1.0, 0.0, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0]:
    is_sub = base[is_mask & (base["surprise_B_MA"] >= thr)]
    oos_sub = base[oos_mask & (base["surprise_B_MA"] >= thr)]
    if len(is_sub) < 50 or len(oos_sub) < 50: continue
    is_wr = (is_sub["post_ret"]>0).mean()*100
    is_avg = is_sub["post_ret"].mean()
    oos_wr = (oos_sub["post_ret"]>0).mean()*100
    oos_avg = oos_sub["post_ret"].mean()
    delta = oos_avg - is_avg
    print(f"  {thr:>+8.2f}    {len(is_sub):>6d}{is_wr:>+8.1f}%{is_avg:>+9.2f}%{len(oos_sub):>7d}{oos_wr:>+8.1f}%{oos_avg:>+9.2f}%{delta:>+9.2f}pp")

# ─── T2: Regime-conditional ──────────────────────────────────────────────
print("\n" + "="*100)
print("  T2: REGIME-CONDITIONAL ANALYSIS")
print("="*100)
print("  How does each filter perform in each regime?\n")

filters_to_test = [
    ("NP_R≥15 only",                 base["NP_R"] >= 15),
    ("NP_R≥15 + surprise≥0.3",       (base["NP_R"] >= 15) & (base["surprise_B_MA"] >= 0.3)),
    ("NP_R≥15 + surprise≥0.5 (V5)",  (base["NP_R"] >= 15) & (base["surprise_B_MA"] >= 0.5)),
    ("NP_R≥15 + surprise≥1.0",       (base["NP_R"] >= 15) & (base["surprise_B_MA"] >= 1.0)),
]

for fname, fmask in filters_to_test:
    sub = base[fmask]
    print(f"\n  --- {fname} ---")
    print(f"  {'Regime':<14}{'N':>7}{'WR':>9}{'avg post_ret':>14}")
    for reg in ["BEAR","FLAT","MILD_BULL","STRONG_BULL"]:
        ss = sub[sub["regime"] == reg]
        if len(ss) < 20: continue
        wr = (ss["post_ret"]>0).mean()*100
        avg = ss["post_ret"].mean()
        print(f"  {reg:<14}{len(ss):>7d}{wr:>+8.1f}%{avg:>+13.2f}%")

# ─── T3: Year-by-year WR comparison ─────────────────────────────────────
print("\n" + "="*100)
print("  T3: YEAR-BY-YEAR — NP_R alone vs NP_R + surprise(0.5)")
print("="*100)
print(f"  {'Year':<6}{'NPR_N':>7}{'NPR_WR':>10}{'NPR_avg':>10}{'V5_N':>7}{'V5_WR':>9}{'V5_avg':>10}{'Δ_avg':>10}")
print("  " + "-"*72)
for y in range(2014, 2027):
    npr = base[(base["year"]==y) & (base["NP_R"] >= 15)]
    v5  = base[(base["year"]==y) & (base["NP_R"] >= 15) & (base["surprise_B_MA"] >= 0.5)]
    if len(npr) < 10 or len(v5) < 10: continue
    npr_wr = (npr["post_ret"]>0).mean()*100; npr_avg = npr["post_ret"].mean()
    v5_wr  = (v5["post_ret"]>0).mean()*100;  v5_avg  = v5["post_ret"].mean()
    delta = v5_avg - npr_avg
    print(f"  {y:<6}{len(npr):>7d}{npr_wr:>+9.1f}%{npr_avg:>+9.2f}%{len(v5):>7d}{v5_wr:>+8.1f}%{v5_avg:>+9.2f}%{delta:>+9.2f}pp")

# ─── T4: PEAD alpha decay (IC by 2y bucket) ─────────────────────────────
print("\n" + "="*100)
print("  T4: PEAD ALPHA DECAY — Surprise IC by 2-year bucket")
print("="*100)
print(f"  {'Period':<12}{'N':>8}{'Surprise IC (Spearman)':>30}{'NP_R IC (Spearman)':>22}")
print("  " + "-"*70)
for start_y in [2014, 2016, 2018, 2020, 2022, 2024]:
    end_y = start_y + 1
    sub = ev[(ev["year"] >= start_y) & (ev["year"] <= end_y)].dropna(subset=["surprise_B_MA","NP_R","post_ret"])
    if len(sub) < 200: continue
    sur_ic = sub["surprise_B_MA"].rank().corr(sub["post_ret"].rank())
    npr_ic = sub["NP_R"].rank().corr(sub["post_ret"].rank())
    print(f"  {start_y}-{end_y}    {len(sub):>8d}{sur_ic:>+29.3f}{npr_ic:>+21.3f}")

# ─── T5: Different IS/OOS splits ─────────────────────────────────────────
print("\n" + "="*100)
print("  T5: ALTERNATIVE IS/OOS SPLITS (event-level avg post_ret)")
print("="*100)
print(f"  {'Split':<16}{'Period':<20}{'V5_N':>7}{'V5_avg':>10}{'NPR_N':>7}{'NPR_avg':>10}{'Δ':>8}")
print("  " + "-"*78)
splits = [
    ("Split_2018", ((2014,2017), (2018,2026))),
    ("Split_2020", ((2014,2019), (2020,2026))),
    ("Split_2022", ((2014,2021), (2022,2026))),
    ("Split_2024", ((2014,2023), (2024,2026))),
]
for nm, ((isy1,isy2), (oosy1,oosy2)) in splits:
    for tag, y1, y2 in [("IS", isy1, isy2), ("OOS", oosy1, oosy2)]:
        sub = base[(base["year"] >= y1) & (base["year"] <= y2)]
        npr = sub[sub["NP_R"] >= 15]
        v5  = sub[(sub["NP_R"] >= 15) & (sub["surprise_B_MA"] >= 0.5)]
        if len(npr) < 20 or len(v5) < 20: continue
        npr_avg = npr["post_ret"].mean()
        v5_avg  = v5["post_ret"].mean()
        delta = v5_avg - npr_avg
        print(f"  {nm:<16}{tag} {y1}-{y2:<12}{len(v5):>7d}{v5_avg:>+9.2f}%{len(npr):>7d}{npr_avg:>+9.2f}%{delta:>+7.2f}pp")
    print()

print("\nDone.")
