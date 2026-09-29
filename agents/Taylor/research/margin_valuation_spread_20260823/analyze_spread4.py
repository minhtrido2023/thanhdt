# -*- coding: utf-8 -*-
"""Phase-0 part 4: ABSOLUTE (no-look-ahead) spread ladder, episodes, LOO, DT5G intersection, today's reading."""
import os
import numpy as np, pandas as pd

D = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/margin_valuation_spread_20260823"
m = pd.read_csv(os.path.join(D, "monthly_spread_series.csv"), parse_dates=["time"]).sort_values("time").reset_index(drop=True)
SP = "spread2p_dypay_dep"

def eps_from_mask(df, mask, bridge=1):
    idx = np.where(mask.values)[0]
    if not len(idx):
        return []
    out, cur = [], [idx[0]]
    for a, b in zip(idx[:-1], idx[1:]):
        if b - a <= bridge + 1:
            cur.append(b)
        else:
            out.append(cur); cur = [b]
    out.append(cur)
    return out

def ep_table(df, groups, lab):
    rows = []
    for g in groups:
        s, sub = df.iloc[g[0]], df.iloc[g[0]:g[-1] + 1]
        rows.append(dict(rule=lab, start=s["time"].date(), end=df.iloc[g[-1]]["time"].date(), n_mo=len(g),
                         vni=round(s["vnindex"], 1), dd52=round(100 * s["dd52"], 1),
                         dt5g=("na" if pd.isna(s["state"]) else int(s["state"])),
                         dep=round(s["deposit_use"], 2), mgn=round(s["margin_rate"], 2), src=s["deposit_src"],
                         dy_pay=round(s["dy_med_payers_pct"], 2), ey_med=round(s["ey_med_pct"], 2),
                         sp=round(s[SP], 2), sp_max=round(sub[SP].max(), 2),
                         brd=round(s["breadth_dy_ge_dep_pct"], 1),
                         fwd6=round(100 * s["fwd6m"], 1) if pd.notna(s["fwd6m"]) else np.nan,
                         fwd12=round(100 * s["fwd12m"], 1) if pd.notna(s["fwd12m"]) else np.nan,
                         net12=round(100 * s["fwd12m"] - s["margin_rate"], 1) if pd.notna(s["fwd12m"]) else np.nan,
                         net24=round(100 * s["fwd24m"] - 2 * s["margin_rate"], 1) if pd.notna(s["fwd24m"]) else np.nan))
    return pd.DataFrame(rows)

print("=" * 105)
print("A2c  ABSOLUTE THRESHOLD LADDER on DY(median payer) - deposit — NO fitted parameter, NO look-ahead")
print("     (threshold is an economic anchor, not a data-estimated percentile)")
tabs = {}
for thr in (-1.0, -0.5, 0.0, 0.5, 1.0):
    g = eps_from_mask(m, m[SP] >= thr)
    t = ep_table(m, g, "sp>=%+.1fpp" % thr)
    tabs[thr] = t
    tt = t.dropna(subset=["net12"])
    print("  sp>=%+.1fpp : n_months=%3d  N_EPISODES=%2d | fwd12 med %6.1f%% | net12 med %6.1fpp | share net12>0 %3.0f%% (%d/%d)"
          % (thr, int((m[SP] >= thr).sum()), len(g),
             tt["fwd12"].median(), tt["net12"].median(), 100 * (tt["net12"] > 0).mean(),
             int((tt["net12"] > 0).sum()), len(tt)))
base = m.dropna(subset=["fwd12m"])
print("  BASELINE   : n_months=%3d              | fwd12 med %6.1f%% | net12 med %6.1fpp | share net12>0 %3.0f%%"
      % (len(base), 100 * base["fwd12m"].median(),
         (100 * base["fwd12m"] - base["margin_rate"]).median(),
         100 * ((100 * base["fwd12m"] - base["margin_rate"]) > 0).mean()))

t0 = tabs[0.0]
print("\n-- EPISODE DETAIL at the natural anchor sp >= 0 (DY of median payer >= 12M deposit) --")
print(t0.to_string(index=False))
t0.to_csv(os.path.join(D, "episodes_absolute_sp0.csv"), index=False)

print("\nA4d  LEAVE-ONE-EPISODE-OUT (sp>=0, net12):")
tt = t0.dropna(subset=["net12"])
for i in range(len(tt)):
    loo = np.delete(tt["net12"].values, i)
    print("   drop %s -> remaining median %.1fpp, share>0 %.0f%% (n=%d)" %
          (tt.iloc[i]["start"], np.median(loo), 100 * (loo > 0).mean(), len(loo)))

print("\n" + "=" * 105)
print("A5c  DT5G INTERSECTION at episode start (1=CRISIS 0% 2=BEAR 20% 3=NEUTRAL 70% 4=BULL 5=EXBULL)")
for _, r in t0.iterrows():
    print("   %s  DT5G=%s  dd52=%+.1f%%  sp=%+.2fpp  net12=%s" % (r["start"], r["dt5g"], r["dd52"], r["sp"], r["net12"]))
print("\n   months with sp>=0 by DT5G state (2014+ only):")
sub = m[(m["time"] >= "2014-01-01") & (m[SP] >= 0)]
print("   ", sub["state"].value_counts().sort_index().to_dict() or "NONE")
print("   all months 2014+ by state:", m[m["time"] >= "2014-01-01"]["state"].value_counts().sort_index().to_dict())

print("\n" + "=" * 105)
print("TODAY — last 8 months of the series")
cols = ["time", "vnindex", "dd52", "deposit_use", "margin_rate", "ey_med_pct", "ey_agg_pct",
        "dy_med_payers_pct", "dy_agg_pct", SP, "breadth_dy_ge_dep_pct", "state"]
tl = m[cols].tail(8).copy(); tl["time"] = tl["time"].dt.date
print(tl.round(2).to_string(index=False))
