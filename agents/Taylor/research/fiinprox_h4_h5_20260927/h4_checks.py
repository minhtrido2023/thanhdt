"""H4 secondary checks: (c) 2009-2013 gross, (1.8) overlap with existing DT5G caps,
plus descriptive duty-cycle stats. Descriptive only -- decision already fixed by PREREG 1.6(b)."""
import numpy as np, pandas as pd, json
WC = "/home/trido/thanhdt/WorkingClaude"; MIKE = f"{WC}/mike"

d = pd.read_csv("h4_series.csv", parse_dates=["date"])
CONF = {"A20@0.02": ("A20", -0.02), "A20@0.03": ("A20", -0.03),
        "A60@0.015": ("A60", -0.015), "B@2.0": ("z20", -2.0), "B@2.5": ("z20", -2.5)}

# ---- duty cycle + VNINDEX behaviour while ON (with PREREG 1.4 hysteresis: off at -theta/2)
print("=== DUTY CYCLE (hysteresis: on at -theta, off above -theta/2), cap applied t+1 ===")
vr = d.set_index("date")["vni"].pct_change().shift(-1)   # t+1 return, no look-ahead
rows = []
state_on = {}
for name, (col, thr) in CONF.items():
    x = d[col].to_numpy(); on = np.zeros(len(x), bool); cur = False
    for i, v in enumerate(x):
        if np.isnan(v): on[i] = cur; continue
        if not cur and v <= thr: cur = True
        elif cur and v > thr/2: cur = False
        on[i] = cur
    state_on[name] = on
    r = vr.to_numpy()
    ok = ~np.isnan(r)
    rows.append(dict(config=name, pct_time_on=round(100*on.mean(), 1),
                     vni_ann_ret_ON_pct=round(100*(np.nanmean(r[on & ok])*252), 2),
                     vni_ann_ret_OFF_pct=round(100*(np.nanmean(r[~on & ok])*252), 2),
                     n_days_on=int(on.sum())))
print(pd.DataFrame(rows).to_string(index=False))

# ---- (1.8) overlap with the existing DT5G tier-3 cap
dt = pd.read_csv(f"{WC}/data/vnindex_5state_dt5g_live.csv", parse_dates=["time"]).rename(columns={"time":"date"})
base = pd.read_csv(f"{WC}/data/vnindex_5state.csv", parse_dates=["time"]).rename(columns={"time":"date"})
bcol = "state" if "state" in base.columns else base.columns[1]
mg = dt[["date","state"]].merge(base[["date",bcol]].rename(columns={bcol:"base_state"}), on="date", how="left")
mg["existing_cap_active"] = mg["state"] < mg["base_state"]   # DT5G below base => a cap bit
o = d[["date"]].copy()
for n in CONF: o[n] = state_on[n]
o = o.merge(mg[["date","existing_cap_active"]], on="date", how="left")
print("\n=== OVERLAP with existing DT5G cap (DT5G state < v3.4b base state) ===")
print(f"existing cap active on {int(o.existing_cap_active.fillna(False).sum())} / {len(o)} sessions")
for n in CONF:
    a = o[n].fillna(False).to_numpy(); b = o["existing_cap_active"].fillna(False).to_numpy()
    inter = (a & b).sum()
    print(f"  {n:11s} H4-on {a.sum():5d} | both {inter:5d} | H4 NEW (H4 on, existing off) {int((a & ~b).sum()):5d}"
          f" | share of H4-on already covered {100*inter/max(a.sum(),1):5.1f}%")

# ---- (c) 2009-2013 gross cross-check (file F). Gross INCLUDES deals -> descriptive only.
F = pd.read_csv(f"{MIKE}/data/fiinprox_foreign_flow_index_daily_20260914.csv", parse_dates=["date"])
F = F[F.date < "2014-01-01"].dropna(subset=["vnindex_foreign_net_bn"]).sort_values("date").reset_index(drop=True)
g = F["vnindex_foreign_net_bn"]
S20 = g.rolling(20, min_periods=15).sum()
sd = g.rolling(250, min_periods=180).std()
F["z20"] = S20 / (np.sqrt(20)*sd)
V = pd.read_csv(f"{WC}/data/VNINDEX.csv", usecols=["time","Close"], parse_dates=["time"]).rename(columns={"time":"date","Close":"vni"}).dropna()
F = F.merge(V, on="date", how="left")
print("\n=== (c) 2009-2013 gross (file F, INCLUDES deals -> descriptive only) ===")
print(f"coverage {F.date.min().date()} -> {F.date.max().date()}, n={len(F)}")
for thr in (-2.0, -2.5):
    fired = F.loc[F.z20 <= thr, "date"].tolist()
    eps=[]
    for t in fired:
        if eps and (t-eps[-1][-1]).days < 60: eps[-1].append(t)
        else: eps.append([t])
    print(f"  z20 <= {thr}: {len(fired)} days, {len(eps)} events -> "
          + ", ".join(f"{e[0].date()}..{e[-1].date()}" for e in eps))
# Bobby phases: 1B rally 2009-03..2009-08 ; 1C break 2009-09..2009-12
for lab,(a,b) in {"1B rally 2009-03..08":("2009-03-01","2009-08-31"),
                  "1C break 2009-09..12":("2009-09-01","2009-12-31")}.items():
    w = F[(F.date>=a)&(F.date<=b)]
    print(f"  {lab}: min z20 = {w.z20.min():.2f}  (fire@-2.0: {int((w.z20<=-2).sum())} days)")
