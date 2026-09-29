# -*- coding: utf-8 -*-
"""Phase-0 part 3: honest-N (episodes), PIT-threshold robustness, subsample + proxy sensitivity, LOO."""
import os
import numpy as np, pandas as pd

D = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/margin_valuation_spread_20260823"
m = pd.read_csv(os.path.join(D, "monthly_spread_series.csv"), parse_dates=["time"]).sort_values("time").reset_index(drop=True)
SP = "spread2p_dypay_dep"   # headline axis: DY(median payer) - 12M deposit

def eps_from_mask(df, mask, bridge=1):
    idx = np.where(mask.values)[0]
    if not len(idx):
        return []
    out, cur = [], [idx[0]]
    for a, b in zip(idx[:-1], idx[1:]):
        if b - a <= bridge + 1:
            cur.append(b)
        else:
            out.append(cur)
            cur = [b]
    out.append(cur)
    return [g for g in out if g]

def ep_table(df, groups, lab):
    rows = []
    for g in groups:
        s = df.iloc[g[0]]
        sub = df.iloc[g[0]:g[-1] + 1]
        rows.append(dict(rule=lab, start=s["time"].date(), end=df.iloc[g[-1]]["time"].date(), n_mo=len(g),
                         vni=round(s["vnindex"], 1), dd52=round(100 * s["dd52"], 1),
                         dt5g=("" if pd.isna(s["state"]) else int(s["state"])),
                         dep=round(s["deposit_use"], 2), src=s["deposit_src"],
                         sp_start=round(s[SP], 2), sp_max=round(sub[SP].max(), 2),
                         fwd12=round(100 * s["fwd12m"], 1) if pd.notna(s["fwd12m"]) else np.nan,
                         net12=round(100 * s["fwd12m"] - s["margin_rate"], 1) if pd.notna(s["fwd12m"]) else np.nan,
                         net24=round(100 * s["fwd24m"] - 2 * s["margin_rate"], 1) if pd.notna(s["fwd24m"]) else np.nan))
    return pd.DataFrame(rows)

print("=" * 100)
print("A3c  HONEST N — top-quintile spread months grouped into INDEPENDENT episodes")
thr_full = m[SP].quantile(0.80)
g_full = eps_from_mask(m, m[SP] >= thr_full)
t_full = ep_table(m, g_full, "Q5 full-sample thr=%.2f" % thr_full)
print(t_full.to_string(index=False))
print("\n=> N_months=%d but N_INDEPENDENT_EPISODES=%d" % (int((m[SP] >= thr_full).sum()), len(g_full)))

# PIT threshold: expanding 80th percentile using only data up to t-1, min 36 months of history
pit = []
for i in range(len(m)):
    hist = m[SP].iloc[:i]
    pit.append(np.nan if len(hist) < 36 else hist.quantile(0.80))
m["pit_thr"] = pit
mask_pit = (m[SP] >= m["pit_thr"]) & m["pit_thr"].notna()
g_pit = eps_from_mask(m, mask_pit)
t_pit = ep_table(m, g_pit, "Q5 PIT-expanding")
print("\n-- PIT (expanding 80th pct, min 36m history; no look-ahead in the threshold) --")
print(t_pit.to_string(index=False))
print("=> N_months=%d  N_EPISODES=%d | net12 median %.1fpp | share>0 %.0f%%" % (
    int(mask_pit.sum()), len(g_pit), t_pit["net12"].median(), 100 * (t_pit["net12"] > 0).mean()))

print("\n" + "=" * 100)
print("A4b  LEAVE-ONE-EPISODE-OUT on the PIT episode set (net12, pp)")
nets = t_pit.dropna(subset=["net12"])["net12"].values
for i in range(len(nets)):
    loo = np.delete(nets, i)
    print("   drop ep#%d (%s): remaining median %.1fpp, share>0 %.0f%%" % (
        i + 1, t_pit.iloc[i]["start"], np.median(loo), 100 * (loo > 0).mean()))

print("\n" + "=" * 100)
print("A1b  SUBSAMPLE + PROXY SENSITIVITY (dose-response must survive without the 2008-10 proxy years)")
def dose(df, col, lab, nq=4):
    sub = df.dropna(subset=[col, "fwd12m"]).copy()
    if len(sub) < 40:
        print("  %s: n=%d too small" % (lab, len(sub))); return
    sub["q"] = pd.qcut(sub[col], nq, labels=[f"Q{i+1}" for i in range(nq)])
    g = sub.groupby("q", observed=True).apply(lambda x: pd.Series({
        "n": len(x), "fwd12_med%": 100 * x["fwd12m"].median(),
        "net12_med": (100 * x["fwd12m"] - x["margin_rate"]).median(),
        "sh>0": 100 * ((100 * x["fwd12m"] - x["margin_rate"]) > 0).mean()}), include_groups=False)
    print("\n-- %s (n=%d) --" % (lab, len(sub)))
    print(g.round(1).to_string())

dose(m, SP, "FULL 2008-2026")
dose(m[m["deposit_src"] == "big4_frozen"], SP, "2011+ ONLY (real Big-4 anchors, no refi proxy)")
dose(m[m["time"] >= "2014-01-01"], SP, "2014+ ONLY (DT5G era)")

# proxy sensitivity: shift 2008-2010 deposit +2pp (real 2008 12M deposit peaked ~17-18% vs proxy)
m2 = m.copy()
adj = m2["deposit_src"] == "refi_proxy"
m2.loc[adj, "deposit_use"] += 2.0
m2.loc[adj, "margin_rate"] += 2.0
m2.loc[adj, SP] -= 2.0
dose(m2, SP, "FULL with 2008-10 deposit proxy +2pp (adverse)")

print("\n" + "=" * 100)
print("A4c  CARRY DETAIL — episodes where borrowing at the assumed margin rate actually paid")
allep = pd.concat([t_full, t_pit], ignore_index=True)
print(allep[["rule", "start", "dep", "src", "sp_start", "fwd12", "net12", "net24", "dd52", "dt5g"]].to_string(index=False))
t_pit.to_csv(os.path.join(D, "episodes_pit_top_quintile.csv"), index=False)
t_full.to_csv(os.path.join(D, "episodes_fullsample_top_quintile.csv"), index=False)
print("\nSaved episodes_pit_top_quintile.csv / episodes_fullsample_top_quintile.csv")
