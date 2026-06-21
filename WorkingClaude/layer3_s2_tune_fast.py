"""Vectorized S2 grid search — no per-bar Python loops.
Pre-compute features once per ticker, then mask + first-occurrence vector ops per combo.
"""
import os, pickle, itertools
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
CACHE = os.path.join(WORKDIR, "data/intraday_full.pkl")

TOP30 = ["VIC","VHM","HPG","SHB","SSI","FPT","VIX","STB","MWG","MSN",
         "VCB","BSR","MBB","VPB","TCB","HDB","HCM","CTG","NVL","BID",
         "CII","PVS","VNM","GEX","VCI","SHS","DXG","VRE","VJC","DCM"]
MIDCAP = ['OCB','SSB','VDS','HUT','IJC','TCM','SCR','CTR','BVB','BSI',
          'REE','HVN','VFS','BVH','KSB','SZC','PAN','DDV','LCG','OIL',
          'NT2','DXS','VTZ','BCM','YEG','VGS','FCN','BCG','VC3','DCL']
PENNY  = ['MZG','SBS','CRC','CSM','VAB','APS','TIG','DRI','IDI','HHP',
          'DLG','IDJ','DC4','ASM','C69','G36','NVB','TDC','SHI','CRE',
          'APG','SMC','HSL','NDN','HTN']
SEGMENT_MAP = {**{t:"TOP30" for t in TOP30},
               **{t:"MIDCAP" for t in MIDCAP},
               **{t:"PENNY" for t in PENNY}}

def main():
    print("Loading + preparing features once...")
    with open(CACHE,"rb") as f: intraday = pickle.load(f)

    # Build one big dataframe with all bars, ticker tagged
    all_bars = []
    for tk, df in intraday.items():
        d = df.copy()
        d["time"] = pd.to_datetime(d["time"])
        d = d.sort_values("time").reset_index(drop=True)
        d["ticker"] = tk
        d["segment"] = SEGMENT_MAP.get(tk,"?")
        d["date"] = d["time"].dt.date
        d["session_open"] = d.groupby("date")["open"].transform("first")
        d["day_chg_so_far"] = (d["close"]/d["session_open"] - 1)*100
        d["bars_so_far"] = d.groupby("date").cumcount() + 1
        d["close_2ago"] = d.groupby("date")["close"].shift(2)
        d["close_4ago"] = d.groupby("date")["close"].shift(4)
        d["bounce_30m"] = (d["close"]/d["close_2ago"] - 1)*100
        d["bounce_1h"] = (d["close"]/d["close_4ago"] - 1)*100
        all_bars.append(d[["ticker","segment","date","bars_so_far","close","high","low",
                            "day_chg_so_far","bounce_30m","bounce_1h"]])
    bars = pd.concat(all_bars, ignore_index=True)
    print(f"  Total bars: {len(bars)}")

    # forward returns for each (ticker, session_date)
    daily = pd.read_csv(os.path.join(WORKDIR,"data/daily_forward_full.csv"))
    daily["time"] = pd.to_datetime(daily["time"]).dt.date
    daily["Close"] = daily["Close"]/1000.0
    daily = daily.sort_values(["ticker","time"]).reset_index(drop=True)
    daily["Close_T45"] = daily.groupby("ticker")["Close"].shift(-45)
    fwd_idx = daily.set_index(["ticker","time"])["Close_T45"]

    grid = list(itertools.product(
        [-1, -2, -3, -4, -5],
        ["30m", "1h"],
        [0, 0.5, 1.0],
    ))
    print(f"Grid size: {len(grid)}\n")

    results = []
    for (dthr, bwin, bmin) in grid:
        bcol = f"bounce_{bwin}"
        cond = ((bars["bars_so_far"]>=3) &
                (bars["day_chg_so_far"]<=dthr) &
                (bars[bcol]>=bmin) & bars[bcol].notna())
        # first fire per (ticker, date)
        bars_c = bars.assign(cond=cond)
        fired = bars_c[bars_c["cond"]].groupby(["ticker","date"]).head(1)
        # EoD condition
        eod_bars = bars_c.groupby(["ticker","date"]).tail(1)
        eod_cond = eod_bars[eod_bars["cond"]]
        # forward returns
        fired_with_fwd = fired.copy()
        fired_with_fwd["fwd_close"] = fired_with_fwd.apply(
            lambda r: fwd_idx.get((r["ticker"], r["date"]), np.nan), axis=1)
        fired_with_fwd["fwd_ret"] = (fired_with_fwd["fwd_close"]/fired_with_fwd["close"] - 1)*100
        eod_with_fwd = eod_cond.copy()
        eod_with_fwd["fwd_close"] = eod_with_fwd.apply(
            lambda r: fwd_idx.get((r["ticker"], r["date"]), np.nan), axis=1)
        eod_with_fwd["fwd_ret"] = (eod_with_fwd["fwd_close"]/eod_with_fwd["close"] - 1)*100

        n_fire = len(fired)
        # TP/FP
        eod_keys = set(zip(eod_cond["ticker"], eod_cond["date"]))
        fired["is_tp"] = list(zip(fired["ticker"], fired["date"]))
        fired["is_tp"] = fired["is_tp"].apply(lambda k: k in eod_keys)
        n_tp = fired["is_tp"].sum(); n_fp = n_fire - n_tp
        row = {"d_thr": dthr, "b_win": bwin, "b_min": bmin,
                "n_fire": n_fire, "TP": int(n_tp), "FP": int(n_fp),
                "FP_rate": round(n_fp/max(n_fire,1)*100,1)}
        for seg in ["TOP30","MIDCAP","PENNY","ALL"]:
            er = fired_with_fwd if seg=="ALL" else fired_with_fwd[fired_with_fwd["segment"]==seg]
            ed = eod_with_fwd if seg=="ALL" else eod_with_fwd[eod_with_fwd["segment"]==seg]
            er = er.dropna(subset=["fwd_ret"])
            ed = ed.dropna(subset=["fwd_ret"])
            if len(er) and len(ed):
                lift = er["fwd_ret"].mean() - ed["fwd_ret"].mean()
                row[f"{seg}_n_fire"] = len(er)
                row[f"{seg}_early_mean"] = round(er["fwd_ret"].mean(),3)
                row[f"{seg}_eod_mean"]   = round(ed["fwd_ret"].mean(),3)
                row[f"{seg}_lift"] = round(lift,3)
        results.append(row)
        print(f"  d_thr={dthr:>3} b_win={bwin} b_min={bmin}: n_fire={n_fire:>5} FP={row['FP_rate']:>5.1f}% lift_ALL={row.get('ALL_lift',np.nan):+.3f}pp  lift_TOP30={row.get('TOP30_lift',np.nan):+.3f}pp")

    df = pd.DataFrame(results)
    df.to_csv(os.path.join(WORKDIR,"data/layer3_s2_grid.csv"), index=False)

    print("\n" + "="*110)
    print("TOP 10 by TOP30 lift T+45 (n_fire >= 50)")
    print("="*110)
    f = df.dropna(subset=["TOP30_lift"])
    f = f[f["TOP30_n_fire"]>=50].sort_values("TOP30_lift", ascending=False)
    cols = ["d_thr","b_win","b_min","n_fire","FP_rate","TOP30_n_fire","TOP30_lift","TOP30_early_mean","ALL_lift"]
    print(f[cols].head(10).to_string(index=False))

    print("\nTOP 10 by ALL_lift (n_fire >= 200)")
    f2 = df.dropna(subset=["ALL_lift"])
    f2 = f2[f2["n_fire"]>=200].sort_values("ALL_lift", ascending=False)
    print(f2[cols].head(10).to_string(index=False))

if __name__=="__main__":
    main()
