"""Fine-tune S2 OVERSOLD_REVERSAL signal — grid over:
  - day_chg threshold: -1, -2, -3, -4, -5
  - bounce window: 30min (2 bars), 1h (4 bars)
  - bounce magnitude: >0, >+0.5%, >+1%
  - optional volume confirm: vol_so_far / avg > 1.2

Goal: find lowest-FP variant with high T+45 lift.
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


def compute_per_bar(df):
    df = df.copy()
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)
    df["date"] = df["time"].dt.date
    df["VolMA20"] = df["volume"].rolling(20).mean()
    df["session_open"] = df.groupby("date")["open"].transform("first")
    df["day_chg_so_far"] = (df["close"]/df["session_open"] - 1)*100
    df["bars_so_far"] = df.groupby("date").cumcount() + 1
    df["session_vol_so_far"] = df.groupby("date")["volume"].cumsum()
    df["close_2ago"] = df.groupby("date")["close"].shift(2)
    df["close_4ago"] = df.groupby("date")["close"].shift(4)
    df["session_low_so_far"] = df.groupby("date")["low"].cummin()
    df["bounce_30m_pct"] = (df["close"]/df["close_2ago"] - 1)*100
    df["bounce_1h_pct"] = (df["close"]/df["close_4ago"] - 1)*100
    df["vol_intensity"] = df["session_vol_so_far"] / (df["VolMA20"]*df["bars_so_far"]).replace(0,np.nan)
    return df


def fire_first(sub, dchg_threshold, bounce_window, bounce_min, vol_min):
    """Walk bars; return (first_fire_idx, first_fire_row, eod_signal_bool)."""
    bcol = f"bounce_{bounce_window}_pct"
    first_idx = None; first_row = None
    for i in range(len(sub)):
        row = sub.iloc[i]
        if row["bars_so_far"] < 3: continue
        cond = (row["day_chg_so_far"] <= dchg_threshold
                and pd.notna(row[bcol]) and row[bcol] >= bounce_min
                and (vol_min is None or (pd.notna(row["vol_intensity"]) and row["vol_intensity"] >= vol_min)))
        if cond:
            first_idx, first_row = i, row
            break
    if first_idx is None:
        # also check EoD-only
        last = sub.iloc[-1]
        eod = (last["day_chg_so_far"] <= dchg_threshold
               and pd.notna(last[bcol]) and last[bcol] >= bounce_min
               and (vol_min is None or (pd.notna(last["vol_intensity"]) and last["vol_intensity"] >= vol_min)))
        return None, None, eod
    last = sub.iloc[-1]
    eod = (last["day_chg_so_far"] <= dchg_threshold
           and pd.notna(last[bcol]) and last[bcol] >= bounce_min
           and (vol_min is None or (pd.notna(last["vol_intensity"]) and last["vol_intensity"] >= vol_min)))
    return first_idx, first_row, eod


def run_grid(per_bar, daily_close_T45, grid):
    """For each grid combo, scan all sessions, compute lift."""
    rows = []
    for (dthr, bwin, bmin, vmin) in grid:
        n_fire = n_tp = n_fp = 0
        early_rets = []
        eod_rets = []
        for tk, df in per_bar.items():
            seg = SEGMENT_MAP.get(tk,"?")
            for sess_date, sub in df.groupby("date"):
                if len(sub)<5: continue
                fid, frow, eod = fire_first(sub.reset_index(drop=True), dthr, bwin, bmin, vmin)
                eod_price = sub.iloc[-1]["close"]
                # forward close
                fwd = daily_close_T45.get((tk, sess_date))
                if pd.isna(fwd) or fwd is None: continue
                if fid is not None:
                    n_fire += 1
                    if eod: n_tp += 1
                    else: n_fp += 1
                    fire_price = frow["close"]
                    early_rets.append({"seg":seg, "r":(fwd/fire_price-1)*100})
                if eod:
                    eod_rets.append({"seg":seg, "r":(fwd/eod_price-1)*100})
        er = pd.DataFrame(early_rets); ed = pd.DataFrame(eod_rets)
        row = {"d_thr": dthr, "b_win": bwin, "b_min": bmin, "v_min": vmin,
                "n_fire": n_fire, "TP": n_tp, "FP": n_fp,
                "FP_rate": round(n_fp/max(n_fire,1)*100,1)}
        for seg in ["TOP30","MIDCAP","PENNY","ALL"]:
            er_seg = er if seg=="ALL" else er[er["seg"]==seg]
            ed_seg = ed if seg=="ALL" else ed[ed["seg"]==seg]
            if len(er_seg) and len(ed_seg):
                lift = er_seg["r"].mean() - ed_seg["r"].mean()
                row[f"{seg}_early_mean"] = round(er_seg["r"].mean(),3)
                row[f"{seg}_eod_mean"] = round(ed_seg["r"].mean(),3)
                row[f"{seg}_lift"] = round(lift,3)
                row[f"{seg}_n_fire"] = len(er_seg)
        rows.append(row)
        print(f"  d_thr={dthr} b_win={bwin} b_min={bmin} v_min={vmin}: n_fire={n_fire} FP={n_fp/max(n_fire,1)*100:.0f}%")
    return pd.DataFrame(rows)


def main():
    print("Loading intraday cache...")
    with open(CACHE,"rb") as f: intraday = pickle.load(f)
    print(f"  {len(intraday)} tickers")
    print("Computing per-bar features...")
    per_bar = {tk: compute_per_bar(df) for tk, df in intraday.items()}

    daily = pd.read_csv(os.path.join(WORKDIR,"data/daily_forward_full.csv"))
    daily["time"] = pd.to_datetime(daily["time"]).dt.date
    daily["Close"] = daily["Close"]/1000.0
    daily = daily.sort_values(["ticker","time"]).reset_index(drop=True)
    daily["Close_T45"] = daily.groupby("ticker")["Close"].shift(-45)
    fwd_map = daily.set_index(["ticker","time"])["Close_T45"].to_dict()

    print("Running grid...")
    grid = list(itertools.product(
        [-1, -2, -3, -4, -5],          # d_thr
        ["30m", "1h"],                  # b_win
        [0, 0.5, 1.0],                  # b_min
        [None, 1.2],                    # v_min
    ))
    print(f"Total combos: {len(grid)}")
    df_res = run_grid(per_bar, fwd_map, grid)
    df_res.to_csv(os.path.join(WORKDIR,"data/layer3_s2_grid.csv"), index=False)

    print("\n" + "="*100)
    print("TOP S2 variants by TOP30 lift T+45 (n_fire >= 100, FP_rate < 80%)")
    print("="*100)
    f = df_res.dropna(subset=["TOP30_lift"])
    f = f[(f["n_fire"]>=100) & (f["FP_rate"]<80)].sort_values("TOP30_lift", ascending=False)
    cols = ["d_thr","b_win","b_min","v_min","n_fire","FP_rate","TOP30_n_fire","TOP30_lift","TOP30_early_mean","ALL_lift","ALL_n_fire"]
    print(f[cols].head(15).to_string(index=False))

    print("\n" + "="*100)
    print("TOP variants by ALL_lift")
    print("="*100)
    f2 = df_res.dropna(subset=["ALL_lift"]).sort_values("ALL_lift", ascending=False)
    print(f2[cols].head(15).to_string(index=False))

    print("\nSaved: layer3_s2_grid.csv")

if __name__=="__main__":
    main()
