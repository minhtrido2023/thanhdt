# -*- coding: utf-8 -*-
"""Phase-0 descriptive evidence: valuation spread (EY/DY vs deposit/margin) vs forward VNINDEX.
NO strategy backtest, NO parameter search. Descriptive only."""
import sys, os
import numpy as np, pandas as pd

WC = "/home/trido/thanhdt/WorkingClaude"
D = os.path.join(WC, "mike/agents/Taylor/research/margin_valuation_spread_20260823")
sys.path.insert(0, WC)
from deposit_rate_vn import deposit_events_df
from sbv_macro_overlay import SBV_REFI_EVENTS

MARGIN_SPREAD_PP = 5.0          # ASSUMPTION: margin rate = deposit12m + 5.0pp (see plan §B2)
MARGIN_SPREAD_LO, MARGIN_SPREAD_HI = 4.0, 6.0

# ---------- load ----------
m = pd.read_csv(os.path.join(D, "_raw_monthly.csv"), parse_dates=["time"])
vni = pd.read_csv(os.path.join(D, "_vnindex_daily.csv"), parse_dates=["time"]).sort_values("time")
dt5 = pd.read_csv(os.path.join(D, "_dt5g_daily.csv"), parse_dates=["time"]).sort_values("time")

dep = deposit_events_df()
dep.columns = [c.lower() for c in dep.columns]
dcol = [c for c in dep.columns if c not in ("time", "effective_date", "date")][0]
tcol = [c for c in dep.columns if c in ("time", "effective_date", "date")][0]
dep = dep[[tcol, dcol]].rename(columns={tcol: "time", dcol: "deposit"}).sort_values("time")
dep["time"] = pd.to_datetime(dep["time"])

refi = pd.DataFrame(SBV_REFI_EVENTS, columns=["time", "refi"])
refi["time"] = pd.to_datetime(refi["time"])

# ---------- daily VNINDEX derived: dd52 + forward returns ----------
vni = vni.set_index("time")
vni["max252"] = vni["Close"].rolling(252, min_periods=60).max()
vni["dd52"] = vni["Close"] / vni["max252"] - 1.0
vni = vni.reset_index()

def fwd(d, months):
    tgt = d + pd.DateOffset(months=months)
    if tgt > vni["time"].iloc[-1]:
        return np.nan
    sub = vni[vni["time"] <= tgt]
    p0 = vni.loc[vni["time"] <= d, "Close"].iloc[-1]
    return sub["Close"].iloc[-1] / p0 - 1.0

# ---------- monthly merge ----------
m = m.sort_values("time")
m = pd.merge_asof(m, dep, on="time")                    # step series, ffill by asof
m = pd.merge_asof(m, refi, on="time")
m = pd.merge_asof(m, vni[["time", "dd52"]], on="time")
dt5["state"] = dt5["state"].astype(float)
m = pd.merge_asof(m, dt5, on="time", tolerance=pd.Timedelta("7D"))

# deposit proxy pre-2011 from refi + measured overlap spread
ov = m.dropna(subset=["deposit", "refi"])
sp_med = float((ov["deposit"] - ov["refi"]).median())
sp_iqr = (float((ov["deposit"] - ov["refi"]).quantile(.25)), float((ov["deposit"] - ov["refi"]).quantile(.75)))
m["deposit_src"] = np.where(m["deposit"].notna(), "big4_frozen", "refi_proxy")
m["deposit_use"] = m["deposit"].fillna(m["refi"] + sp_med)
m["margin_rate"] = m["deposit_use"] + MARGIN_SPREAD_PP

# yields in PERCENT for readability
for c in ["ey_med", "ey_p75", "ey_agg", "dy_med_all", "dy_p75_all", "dy_med_payers", "dy_ew", "dy_agg"]:
    m[c + "_pct"] = m[c] * 100.0

m["spread1_ey_dep"] = m["ey_agg_pct"] - m["deposit_use"]          # EY(cap-wtd) - deposit
m["spread1m_eymed_dep"] = m["ey_med_pct"] - m["deposit_use"]      # EY(median) - deposit
m["spread2_dy_dep"] = m["dy_agg_pct"] - m["deposit_use"]          # DY(cap-wtd) - deposit
m["spread2p_dypay_dep"] = m["dy_med_payers_pct"] - m["deposit_use"]
m["spread3_ey_mgn"] = m["ey_agg_pct"] - m["margin_rate"]          # borrow-decision spread
m["spread3m_eymed_mgn"] = m["ey_med_pct"] - m["margin_rate"]

for h in (6, 12, 24):
    m[f"fwd{h}m"] = [fwd(d, h) for d in m["time"]]

m.to_csv(os.path.join(D, "monthly_spread_series.csv"), index=False)

# ---------- helper: episodes ----------
def episodes(df, mask, name, min_len=1, bridge=1):
    idx = np.where(mask.values)[0]
    if len(idx) == 0:
        return pd.DataFrame()
    groups, cur = [], [idx[0]]
    for a, b in zip(idx[:-1], idx[1:]):
        if b - a <= bridge + 1:
            cur.append(b)
        else:
            groups.append(cur); cur = [b]
    groups.append(cur)
    rows = []
    for g in groups:
        if len(g) < min_len:
            continue
        sub = df.iloc[g[0]:g[-1] + 1]
        s = df.iloc[g[0]]
        rows.append(dict(
            rule=name, start=s["time"].date(), end=df.iloc[g[-1]]["time"].date(), n_months=len(g),
            vni_start=round(s["vnindex"], 1), dd52_start=round(100 * s["dd52"], 1),
            dd52_min=round(100 * sub["dd52"].min(), 1),
            dt5g_start=("" if pd.isna(s["state"]) else int(s["state"])),
            deposit=round(s["deposit_use"], 2), deposit_src=s["deposit_src"],
            margin=round(s["margin_rate"], 2),
            ey_agg=round(s["ey_agg_pct"], 2), ey_med=round(s["ey_med_pct"], 2),
            dy_agg=round(s["dy_agg_pct"], 2), dy_payers=round(s["dy_med_payers_pct"], 2),
            sp1=round(s["spread1_ey_dep"], 2), sp2=round(s["spread2_dy_dep"], 2), sp3=round(s["spread3_ey_mgn"], 2),
            fwd6=round(100 * s["fwd6m"], 1) if pd.notna(s["fwd6m"]) else np.nan,
            fwd12=round(100 * s["fwd12m"], 1) if pd.notna(s["fwd12m"]) else np.nan,
            fwd24=round(100 * s["fwd24m"], 1) if pd.notna(s["fwd24m"]) else np.nan,
            net6=round(100 * s["fwd6m"] - s["margin_rate"] * 0.5, 1) if pd.notna(s["fwd6m"]) else np.nan,
            net12=round(100 * s["fwd12m"] - s["margin_rate"], 1) if pd.notna(s["fwd12m"]) else np.nan,
            net24=round(100 * s["fwd24m"] - s["margin_rate"] * 2, 1) if pd.notna(s["fwd24m"]) else np.nan,
        ))
    return pd.DataFrame(rows)

mm = m[m["time"] >= "2008-01-01"].reset_index(drop=True)   # PE coverage starts 2007; use 2008+
rules = {
    "A_DYagg>=dep":      mm["dy_agg_pct"] >= mm["deposit_use"],
    "B_DYpayers>=dep":   mm["dy_med_payers_pct"] >= mm["deposit_use"],
    "C_EYagg-mgn>=0":    mm["spread3_ey_mgn"] >= 0,
    "D_EYagg-mgn>=3pp":  mm["spread3_ey_mgn"] >= 3,
    "E_EYmed-mgn>=8pp":  mm["spread3m_eymed_mgn"] >= 8,
}
eps = pd.concat([episodes(mm, v, k) for k, v in rules.items()], ignore_index=True)
eps.to_csv(os.path.join(D, "episodes.csv"), index=False)

# ---------- report ----------
pd.set_option("display.width", 220, "display.max_columns", 60)
print("=" * 100)
print("A1  MONTHLY SERIES  n=%d  %s -> %s" % (len(mm), mm['time'].min().date(), mm['time'].max().date()))
print("deposit-refi overlap spread: median %.2fpp  IQR[%.2f, %.2f]  (n=%d months, 2011+)" % (sp_med, *sp_iqr, len(ov)))
print("deposit source split:", mm["deposit_src"].value_counts().to_dict())
print("\nmedians over sample (pct/pp):")
cols = ["ey_agg_pct", "ey_med_pct", "dy_agg_pct", "dy_med_payers_pct", "deposit_use", "margin_rate",
        "spread1_ey_dep", "spread2_dy_dep", "spread3_ey_mgn"]
print(mm[cols].describe().T[["min", "25%", "50%", "75%", "max"]].round(2))

print("\n" + "=" * 100)
print("A2  EPISODES  (grouped consecutive months, bridge<=1 gap)")
for k in rules:
    sub = eps[eps["rule"] == k]
    nm = int(rules[k].sum())
    print("  %-20s n_months=%3d   n_episodes=%2d" % (k, nm, len(sub)))
print()
if len(eps):
    print(eps.to_string(index=False))

print("\n" + "=" * 100)
print("A3/A4  FORWARD RETURN + NET CARRY vs UNCONDITIONAL BASELINE")
base = mm.dropna(subset=["fwd12m"])
print("baseline (all months, n=%d): fwd6 med %.1f%% | fwd12 med %.1f%% mean %.1f%% | fwd24 med %.1f%%" % (
    len(base), 100 * base["fwd6m"].median(), 100 * base["fwd12m"].median(),
    100 * base["fwd12m"].mean(), 100 * base["fwd24m"].median()))
print("baseline net12 (fwd12 - margin_rate): med %.1fpp | share>0 %.0f%%" % (
    (100 * base["fwd12m"] - base["margin_rate"]).median(),
    100 * ((100 * base["fwd12m"] - base["margin_rate"]) > 0).mean()))
for k in rules:
    sub = eps[eps["rule"] == k].dropna(subset=["fwd12"])
    if not len(sub):
        continue
    print("  %-20s N_ep=%2d | fwd12 med %6.1f%% | net12 med %6.1fpp | share net12>0 %3.0f%% | net24>0 %3.0f%%" % (
        k, len(sub), sub["fwd12"].median(), sub["net12"].median(),
        100 * (sub["net12"] > 0).mean(),
        100 * (sub.dropna(subset=["net24"])["net24"] > 0).mean() if sub["net24"].notna().any() else np.nan))

print("\n" + "=" * 100)
print("A5  DT5G STATE AT EPISODE START (1=CRISIS 2=BEAR 3=NEUTRAL 4=BULL 5=EXBULL; blank = pre-2014)")
if len(eps):
    print(eps.groupby(["rule", "dt5g_start"]).size().to_string())
print("\nSaved: monthly_spread_series.csv, episodes.csv")
