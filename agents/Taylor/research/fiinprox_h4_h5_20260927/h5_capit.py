"""H5 part B -- retail_capitulation as candidate condition-3 of the Loai-2 margin mandate.
Criteria per PREREG.md §2.4 (written before any of this was computed)."""
import numpy as np, pandas as pd
WC="/home/trido/thanhdt/WorkingClaude"
d=pd.read_csv("h5_retail_daily.csv",parse_dates=["date"]).dropna(subset=["retail_capitulation"])
V=pd.read_csv(f"{WC}/data/VNINDEX.csv",usecols=["time","Close"],parse_dates=["time"]) \
    .rename(columns={"time":"date","Close":"vni"}).dropna().sort_values("date")
v=V.set_index("date")["vni"]
roll_max_1y=v.rolling(252,min_periods=120).max()
dd_from_peak=v/roll_max_1y-1                     # drawdown vs trailing 1Y high

def events(dates,gap=60):
    out=[]
    for t in dates:
        if out and (t-out[-1][-1]).days<gap: out[-1].append(t)
        else: out.append([t])
    return out

print("=== retail_capitulation (z of 20d sum of individual net flow), 2017-01 -> 2026-08 ===")
print(f"n days = {len(d)}   min {d.retail_capitulation.min():.2f}   max {d.retail_capitulation.max():.2f}")
for thr in (-2.0,-2.5):
    fired=d.loc[d.retail_capitulation<=thr,"date"].tolist()
    eps=events(fired)
    print(f"\n--- z <= {thr}: {len(fired)} days, {len(eps)} events (debounce 60d) ---")
    rows=[]
    for ep in eps:
        f0,f1=ep[0],ep[-1]
        zmin=d.loc[(d.date>=f0)&(d.date<=f1),"retail_capitulation"].min()
        # PREREG: a "false extreme" = NOT within +-1 month of a market bottom,
        # where a bottom = VNINDEX >=20% below its trailing 1Y high
        w=dd_from_peak[(dd_from_peak.index>=f0-pd.Timedelta(days=30))&
                       (dd_from_peak.index<=f1+pd.Timedelta(days=30))]
        near_bottom = bool((w<=-0.20).any())
        mindd = w.min()*100 if len(w) else np.nan
        rows.append(dict(first=f0.date(),last=f1.date(),ndays=len(ep),z_min=round(zmin,2),
                         max_dd_vs_1Y_high_pct=round(mindd,1),near_bottom=near_bottom))
    r=pd.DataFrame(rows); print(r.to_string(index=False))
    print(f"  -> false extremes (khong gan day): {int((~r.near_bottom).sum())} / {len(r)}")
    # PREREG target episodes
    for lab,(a,b) in {"2020-03":("2020-02-15","2020-04-15"),
                      "2022-10/11":("2022-10-01","2022-11-30")}.items():
        hit=any((pd.Timestamp(a)<=pd.Timestamp(str(x["first"])+" ")) and
                (pd.Timestamp(str(x["last"])+" ")<=pd.Timestamp(b)) for x in rows) or \
            any(not(pd.Timestamp(str(x["last"]))<pd.Timestamp(a) or pd.Timestamp(str(x["first"]))>pd.Timestamp(b)) for x in rows)
        zw=d[(d.date>=a)&(d.date<=b)]["retail_capitulation"]
        print(f"  {lab}: bat duoc = {hit}   (z min trong cua so = {zw.min():.2f})")
