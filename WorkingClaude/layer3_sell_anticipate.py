"""SELL anticipation backtest: fire stop-loss/take-profit intraday vs wait EoD.

Setup: for each (ticker, day D), simulate a HYPOTHETICAL position bought at D-N close (N = lookback hold).
During day D intraday, check if stop/TP triggers. Compare:

  S_BASE       wait until EoD; if D-close hits stop/TP threshold, sell at D close
  S_INTRADAY   fire stop/TP the moment bar crosses threshold; sell at trigger price
  S_NEXT_OPEN  fire intraday but execute next-day OPEN (Vietnam T+2.5 reality proxy)

Stops tested:
  STOP_PCT     -10%, -15%, -20% (BA-system uses -20%)
  TP_PCT       +15%, +25%, +40% (BA-system bracket-stop trail)
  TRAIL_PCT    after position +10%, trail at -7% from peak (custom)

Lookback N = 30 days (typical BA hold halfway point), 45 days (full hold).

Key question: does intraday firing save losses vs waiting EoD close?
False positives = stop triggered intraday but price recovered by EoD (would not have stopped if waited).
Net = (avoided drawdowns) − (locked-in losses on FP recoveries).
"""
import os, pickle
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
CACHE = os.path.join(WORKDIR, "intraday_full.pkl")

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
    print("Loading intraday + daily...")
    with open(CACHE,"rb") as f: intraday = pickle.load(f)
    daily = pd.read_csv(os.path.join(WORKDIR,"daily_forward_full.csv"))
    daily["time"] = pd.to_datetime(daily["time"]).dt.date
    daily["Close"] = daily["Close"]/1000.0
    daily = daily.sort_values(["ticker","time"]).reset_index(drop=True)
    # Look back N days to get hypothetical entry price
    for N in [30, 45]:
        daily[f"Close_lookback_{N}"] = daily.groupby("ticker")["Close"].shift(N)
    # Also forward close T+5 after the trigger day (for "if we waited" comparison)
    daily["Close_T1"] = daily.groupby("ticker")["Close"].shift(-1)
    daily["Close_T5"] = daily.groupby("ticker")["Close"].shift(-5)
    daily["Open_T1"] = daily.groupby("ticker")["Open"].shift(-1)/1000.0
    lookup = daily.set_index(["ticker","time"])

    # For each (ticker, day), synthesize position from N days ago
    # Test stop level on intraday vs EoD
    STOPS = [(-0.10, "STOP10"), (-0.15, "STOP15"), (-0.20, "STOP20")]
    TPS   = [(0.15, "TP15"), (0.25, "TP25"), (0.40, "TP40")]
    LOOKBACKS = [30, 45]

    all_rows = []
    for tk, raw in intraday.items():
        seg = SEGMENT_MAP.get(tk,"?")
        df = raw.copy()
        df["time"] = pd.to_datetime(df["time"])
        df = df.sort_values("time")
        df["date"] = df["time"].dt.date
        for sess_date, sub in df.groupby("date"):
            sub = sub.sort_values("time").reset_index(drop=True)
            if len(sub) < 5: continue
            day_open = sub["open"].iloc[0]
            day_close = sub["close"].iloc[-1]
            day_low = sub["low"].min()
            day_high = sub["high"].max()
            try:
                d_row = lookup.loc[(tk, sess_date)]
            except KeyError: continue
            for N in LOOKBACKS:
                entry_price = d_row[f"Close_lookback_{N}"]
                if pd.isna(entry_price) or entry_price <= 0: continue
                # P&L levels in price space (in thousand VND, matching intraday)
                for stop_pct, stop_name in STOPS:
                    stop_lvl = entry_price * (1 + stop_pct)
                    # find first bar where low <= stop_lvl
                    hit_idx = sub[sub["low"] <= stop_lvl].index
                    intraday_hit = len(hit_idx) > 0
                    eod_hit = day_close <= stop_lvl
                    if not intraday_hit and not eod_hit:
                        continue   # neither triggers — no event
                    # Strategy fills
                    s_base_fill = day_close if eod_hit else None
                    s_intra_fill = stop_lvl if intraday_hit else None  # limit sell at stop_lvl, assume fill
                    # next-day open fill (for "intraday signal but T+1 execution" proxy)
                    s_next_open_fill = d_row["Open_T1"] if intraday_hit else None
                    # If we had NOT stopped, where'd we be at T+5? (Counterfactual)
                    fwd5 = d_row["Close_T5"]
                    for fill_name, fill_px in [("S_BASE_EoD",s_base_fill),
                                                ("S_INTRADAY",s_intra_fill),
                                                ("S_NEXT_OPEN",s_next_open_fill)]:
                        if fill_px is None: continue
                        realized_ret = (fill_px/entry_price - 1)*100
                        # vs "no stop, hold to T+5"
                        fwd_ret = (fwd5/entry_price - 1)*100 if pd.notna(fwd5) else None
                        all_rows.append({
                            "ticker":tk, "segment":seg, "date":sess_date,
                            "hold_N":N, "stop_or_tp":stop_name, "side":"STOP",
                            "entry_price":entry_price, "intraday_hit":intraday_hit, "eod_hit":eod_hit,
                            "strategy":fill_name, "fill_price":fill_px,
                            "realized_ret_pct":realized_ret,
                            "noaction_T5_ret_pct":fwd_ret,
                            "diff_vs_holding": realized_ret - (fwd_ret if fwd_ret is not None else 0),
                            "day_close":day_close, "day_low":day_low,
                        })
                for tp_pct, tp_name in TPS:
                    tp_lvl = entry_price * (1 + tp_pct)
                    hit_idx = sub[sub["high"] >= tp_lvl].index
                    intraday_hit = len(hit_idx) > 0
                    eod_hit = day_close >= tp_lvl
                    if not intraday_hit and not eod_hit: continue
                    s_base_fill = day_close if eod_hit else None
                    s_intra_fill = tp_lvl if intraday_hit else None
                    s_next_open_fill = d_row["Open_T1"] if intraday_hit else None
                    fwd5 = d_row["Close_T5"]
                    for fill_name, fill_px in [("S_BASE_EoD",s_base_fill),
                                                ("S_INTRADAY",s_intra_fill),
                                                ("S_NEXT_OPEN",s_next_open_fill)]:
                        if fill_px is None: continue
                        realized_ret = (fill_px/entry_price - 1)*100
                        fwd_ret = (fwd5/entry_price - 1)*100 if pd.notna(fwd5) else None
                        all_rows.append({
                            "ticker":tk, "segment":seg, "date":sess_date,
                            "hold_N":N, "stop_or_tp":tp_name, "side":"TP",
                            "entry_price":entry_price, "intraday_hit":intraday_hit, "eod_hit":eod_hit,
                            "strategy":fill_name, "fill_price":fill_px,
                            "realized_ret_pct":realized_ret,
                            "noaction_T5_ret_pct":fwd_ret,
                            "diff_vs_holding": realized_ret - (fwd_ret if fwd_ret is not None else 0),
                            "day_close":day_close, "day_high":day_high,
                        })

    df_res = pd.DataFrame(all_rows)
    df_res.to_csv(os.path.join(WORKDIR,"layer3_sell_anticipate.csv"), index=False)
    print(f"\nTotal sell-event rows: {len(df_res)}")

    print("\n" + "="*100)
    print("STOP-LOSS RESULTS — realized return per strategy")
    print("="*100)
    stops = df_res[df_res["side"]=="STOP"]
    for hold_N in [30, 45]:
        for sname in ["STOP10","STOP15","STOP20"]:
            sub = stops[(stops["hold_N"]==hold_N) & (stops["stop_or_tp"]==sname)]
            if not len(sub): continue
            print(f"\n[hold_N={hold_N} {sname}]")
            g = sub.groupby("strategy").agg(
                n=("realized_ret_pct","count"),
                mean=("realized_ret_pct","mean"),
                median=("realized_ret_pct","median"),
                diff_vs_hold=("diff_vs_holding","mean"))
            print(g.round(3).to_string())
            # FP analysis: intraday_hit but not eod_hit
            fp = sub[(sub["intraday_hit"]==True) & (sub["eod_hit"]==False) & (sub["strategy"]=="S_INTRADAY")]
            tp = sub[(sub["intraday_hit"]==True) & (sub["eod_hit"]==True)  & (sub["strategy"]=="S_INTRADAY")]
            if len(fp)+len(tp)>0:
                print(f"  TP (both intraday+EoD hit): {len(tp)}  | FP (intraday hit only, EoD recover): {len(fp)}  FP_rate={len(fp)/(len(tp)+len(fp))*100:.1f}%")

    print("\n" + "="*100)
    print("TAKE-PROFIT RESULTS")
    print("="*100)
    tps = df_res[df_res["side"]=="TP"]
    for hold_N in [30, 45]:
        for tname in ["TP15","TP25","TP40"]:
            sub = tps[(tps["hold_N"]==hold_N) & (tps["stop_or_tp"]==tname)]
            if not len(sub): continue
            print(f"\n[hold_N={hold_N} {tname}]")
            g = sub.groupby("strategy").agg(
                n=("realized_ret_pct","count"),
                mean=("realized_ret_pct","mean"),
                median=("realized_ret_pct","median"),
                diff_vs_hold=("diff_vs_holding","mean"))
            print(g.round(3).to_string())
            fp = sub[(sub["intraday_hit"]==True) & (sub["eod_hit"]==False) & (sub["strategy"]=="S_INTRADAY")]
            tp = sub[(sub["intraday_hit"]==True) & (sub["eod_hit"]==True)  & (sub["strategy"]=="S_INTRADAY")]
            if len(fp)+len(tp)>0:
                print(f"  TP (both intraday+EoD): {len(tp)}  | FP (intraday only): {len(fp)}  FP_rate={len(fp)/(len(tp)+len(fp))*100:.1f}%")

    print("\nSaved: layer3_sell_anticipate.csv")

if __name__=="__main__":
    main()
