"""Backtest: fire BUY signal intraday vs wait till EoD close.

Hypothesis: For tickers near BUY condition, firing the moment the condition is met
intraday is better than waiting till market close.

Three signals tested (rolling, per-bar, bars-so-far):
  S1_STRONG_COMBO  : pct_above_vwap>=60 AND day_chg ∈ [-1,+2] AND macdh>0  (momentum)
  S2_OVERSOLD_REV  : day_chg<=-2 AND last 30min bounce (close > 2-bar-ago close) (reversal)
  S3_VOL_BREAKOUT  : day_chg>=+1 AND vol_so_far / vol_avg_session > 1.5  (breakout)

For each (ticker, session) and each signal:
  - Find first bar k where signal becomes TRUE
  - Check if signal still TRUE at EoD (validation status)

Strategies:
  EARLY_FIRE       : buy at bar k close (when signal first triggers)
  WAIT_EOD         : buy at session close ONLY if EoD signal still valid
  HYBRID           : buy at bar k; if signal invalidated at EoD, sell at close (cut loss)

Compare forward returns T+5/T+20/T+45.
"""
import os, pickle, sys
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


def compute_per_bar(df):
    """For one ticker's full history of 15m bars, compute features bar-by-bar."""
    df = df.copy()
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)
    df["date"] = df["time"].dt.date

    # cross-session features
    df["EMA12"] = df["close"].ewm(span=12, adjust=False).mean()
    df["EMA26"] = df["close"].ewm(span=26, adjust=False).mean()
    df["MACD"]  = df["EMA12"] - df["EMA26"]
    df["MACDsig"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACDh"] = df["MACD"] - df["MACDsig"]
    df["VolMA20"] = df["volume"].rolling(20).mean()

    # per-session running features
    df["session_open"] = df.groupby("date")["open"].transform("first")
    df["session_open_first_close"] = df.groupby("date")["close"].transform("first")  # for day_chg using close vs open

    # cumulative session VWAP and pct_above_vwap_so_far
    df["tp"] = (df["high"]+df["low"]+df["close"])/3.0
    df["pv"] = df["tp"]*df["volume"]
    df["cum_pv"] = df.groupby("date")["pv"].cumsum()
    df["cum_vol"] = df.groupby("date")["volume"].cumsum()
    df["session_vwap"] = df["cum_pv"]/df["cum_vol"].replace(0,np.nan)
    df["above_vwap"] = (df["close"] > df["session_vwap"]).astype(int)
    df["bars_so_far"] = df.groupby("date").cumcount() + 1
    df["bars_above_so_far"] = df.groupby("date")["above_vwap"].cumsum()
    df["pct_above_vwap_so_far"] = df["bars_above_so_far"]/df["bars_so_far"]*100

    # day_chg using session open vs current close
    df["day_chg_so_far"] = (df["close"]/df["session_open"] - 1)*100

    # session vol so far + avg vol per bar over session (proxy)
    df["session_vol_so_far"] = df["cum_vol"]
    avg_bars_per_sess = 18  # rough
    df["vol_burst_so_far"] = df["session_vol_so_far"] / (df["VolMA20"]*df["bars_so_far"]).replace(0,np.nan)

    # 30min-ago bounce indicator (2 bars back)
    df["close_2ago"] = df.groupby("date")["close"].shift(2)
    df["bounce_30m"] = (df["close"] > df["close_2ago"]).astype(int)

    # session min/max so far for oversold check
    df["session_low_so_far"] = df.groupby("date")["low"].cummin()

    df["hhmm"] = df["time"].dt.strftime("%H:%M")
    return df


def signal_funcs():
    """Return dict of signal name -> bar-row test function."""
    def s1(bar):
        return (bar["bars_so_far"]>=3 and
                bar["pct_above_vwap_so_far"]>=60 and
                -1 <= bar["day_chg_so_far"] <= 2 and
                bar["MACDh"]>0)
    def s2(bar):
        return (bar["bars_so_far"]>=3 and
                bar["day_chg_so_far"]<=-2 and
                bar["bounce_30m"]==1)
    def s3(bar):
        return (bar["bars_so_far"]>=3 and
                bar["day_chg_so_far"]>=1 and
                pd.notna(bar["vol_burst_so_far"]) and
                bar["vol_burst_so_far"]>1.5)
    return {"S1_STRONG_COMBO": s1, "S2_OVERSOLD_REV": s2, "S3_VOL_BREAKOUT": s3}


def scan_sessions(per_bar, signals):
    """For each (ticker, session) yield records about early fire + EoD status."""
    rows = []
    for tk, df in per_bar.items():
        seg = SEGMENT_MAP.get(tk,"?")
        for sess_date, sub in df.groupby("date"):
            sub = sub.reset_index(drop=True)
            if len(sub)<5: continue
            session_open = sub["session_open"].iloc[0]
            session_close = sub["close"].iloc[-1]
            day_high = sub["high"].max()
            day_low = sub["low"].min()
            for sname, fn in signals.items():
                # find first bar where signal True
                first_idx, first_bar = None, None
                for i in range(len(sub)):
                    row = sub.iloc[i]
                    try:
                        if fn(row):
                            first_idx, first_bar = i, row
                            break
                    except Exception: pass
                if first_idx is None:
                    eod_signal = False
                    try: eod_signal = fn(sub.iloc[-1])
                    except: pass
                    # also record sessions where signal NEVER fires for EoD-only check
                    if eod_signal:
                        # signal only valid AT the last bar
                        rows.append({"ticker": tk, "segment": seg, "date": sess_date,
                                      "signal": sname, "fire_bar_idx": None,
                                      "fire_hhmm": None, "fire_price": None,
                                      "eod_signal": True, "eod_price": session_close,
                                      "session_open": session_open,
                                      "day_high": day_high, "day_low": day_low})
                    continue
                try: eod_signal = bool(fn(sub.iloc[-1]))
                except: eod_signal = False
                rows.append({"ticker": tk, "segment": seg, "date": sess_date,
                              "signal": sname, "fire_bar_idx": int(first_idx),
                              "fire_hhmm": first_bar["hhmm"], "fire_price": float(first_bar["close"]),
                              "eod_signal": eod_signal, "eod_price": float(session_close),
                              "session_open": float(session_open),
                              "day_high": float(day_high), "day_low": float(day_low)})
    return pd.DataFrame(rows)


def add_forward_returns(events, daily):
    daily = daily.copy()
    daily["time"] = pd.to_datetime(daily["time"]).dt.date
    daily["Close"] = daily["Close"]/1000.0
    daily = daily.sort_values(["ticker","time"]).reset_index(drop=True)
    for k in [1,5,20,45]:
        daily[f"Close_T{k}"] = daily.groupby("ticker")["Close"].shift(-k)
    events["date"] = pd.to_datetime(events["date"]).dt.date
    events = events.merge(daily[["ticker","time"] + [f"Close_T{k}" for k in [1,5,20,45]]],
                          left_on=["ticker","date"], right_on=["ticker","time"], how="left")
    return events


def analyze(df):
    print("="*100)
    print("Early-fire detection summary (across all signals)")
    print("="*100)
    fired = df.dropna(subset=["fire_price"])
    print(f"Total events with at least one trigger: {len(fired)}")
    print(f"\nBreakdown by signal × segment:")
    g = fired.groupby(["signal","segment"]).size().unstack(fill_value=0)
    print(g.to_string())

    print(f"\nFire-time distribution (HH:MM of first signal):")
    for sname in ["S1_STRONG_COMBO","S2_OVERSOLD_REV","S3_VOL_BREAKOUT"]:
        sub = fired[fired["signal"]==sname]
        if len(sub)==0: continue
        hours = sub["fire_hhmm"].value_counts().sort_index()
        print(f"\n  [{sname}] n={len(sub)}")
        print(hours.head(8).to_string())

    print("\n" + "="*100)
    print("STRATEGY COMPARISON — Forward T+5 return")
    print("="*100)
    for sname in ["S1_STRONG_COMBO","S2_OVERSOLD_REV","S3_VOL_BREAKOUT"]:
        print(f"\n--- Signal: {sname} ---")
        sub = df[df["signal"]==sname].copy()
        # categorize
        cat_TP = sub[(sub["fire_bar_idx"].notna()) & (sub["eod_signal"]==True)]
        cat_FP = sub[(sub["fire_bar_idx"].notna()) & (sub["eod_signal"]==False)]
        cat_EoDonly = sub[(sub["fire_bar_idx"].isna()) & (sub["eod_signal"]==True)]
        cat_None = sub[(sub["fire_bar_idx"].isna()) & (sub["eod_signal"]==False)]
        print(f"  TP (early fire + eod confirms):  n={len(cat_TP)}")
        print(f"  FP (early fire, eod invalidates): n={len(cat_FP)}")
        print(f"  EoD-only (signal at close only):  n={len(cat_EoDonly)}")
        print(f"  Never:                             n={len(cat_None)}")
        if len(cat_TP)+len(cat_FP)==0: continue
        # strategy returns
        def fwd(df_, price_col, k=5):
            r = (df_[f"Close_T{k}"]/df_[price_col] - 1)*100
            return r.dropna()
        # WAIT_EOD: buy at eod_price only on TP+EoDonly
        eod_buy = pd.concat([cat_TP, cat_EoDonly])
        r_eod = fwd(eod_buy, "eod_price", 5)
        # EARLY_FIRE: buy at fire_price on TP+FP
        early_buy = pd.concat([cat_TP, cat_FP])
        r_early = fwd(early_buy, "fire_price", 5)
        # HYBRID: buy at fire_price on TP+FP; if FP, sell at eod_price (same-day loss); if TP, hold to T+5
        # → for TP: T+5 return from fire_price ; for FP: same-day loss from fire→eod
        tp_r = fwd(cat_TP, "fire_price", 5)
        fp_intraday_loss = (cat_FP["eod_price"]/cat_FP["fire_price"] - 1)*100
        r_hybrid = pd.concat([tp_r, fp_intraday_loss.dropna()])
        # IDEAL_EARLY (oracle, assumes early fire works): buy at fire_price on TP+FP, treat both as if held T+5
        # — same as EARLY_FIRE actually
        for name, r in [("WAIT_EOD", r_eod), ("EARLY_FIRE", r_early),
                          ("HYBRID(early w/ same-day cut on FP)", r_hybrid),
                          ("TP-only ideal", tp_r)]:
            if len(r)==0:
                print(f"    {name:40} n=0"); continue
            print(f"    {name:40} n={len(r):>4}  mean={r.mean():>7.3f}%  median={r.median():>7.3f}%  hit={(r>0).mean()*100:>5.1f}%")

    # Per-segment for S1
    print("\n" + "="*100)
    print("SEGMENT BREAKDOWN — S1_STRONG_COMBO, T+5")
    print("="*100)
    sub_s1 = df[df["signal"]=="S1_STRONG_COMBO"]
    for seg in ["TOP30","MIDCAP","PENNY"]:
        s = sub_s1[sub_s1["segment"]==seg]
        cat_TP = s[(s["fire_bar_idx"].notna()) & (s["eod_signal"]==True)]
        cat_FP = s[(s["fire_bar_idx"].notna()) & (s["eod_signal"]==False)]
        cat_EoDonly = s[(s["fire_bar_idx"].isna()) & (s["eod_signal"]==True)]
        eod_buy = pd.concat([cat_TP, cat_EoDonly])
        early_buy = pd.concat([cat_TP, cat_FP])
        r_eod = ((eod_buy["Close_T5"]/eod_buy["eod_price"] - 1)*100).dropna()
        r_early = ((early_buy["Close_T5"]/early_buy["fire_price"] - 1)*100).dropna()
        print(f"\n[{seg}] TP={len(cat_TP)} FP={len(cat_FP)} EoDonly={len(cat_EoDonly)}")
        if len(r_eod): print(f"  WAIT_EOD   mean={r_eod.mean():>7.3f}%  hit={(r_eod>0).mean()*100:>5.1f}%")
        if len(r_early): print(f"  EARLY_FIRE mean={r_early.mean():>7.3f}%  hit={(r_early>0).mean()*100:>5.1f}%")
        if len(r_eod)>0 and len(r_early)>0:
            print(f"  LIFT (early - eod) = {r_early.mean()-r_eod.mean():+.3f}pp")


def main():
    print("Loading intraday cache...");
    with open(CACHE,"rb") as f: intraday = pickle.load(f)
    print(f"  {len(intraday)} tickers")

    print("Computing per-bar features...")
    per_bar = {tk: compute_per_bar(df) for tk, df in intraday.items()}
    print(f"  done")

    print("Scanning sessions for signal triggers...")
    signals = signal_funcs()
    events = scan_sessions(per_bar, signals)
    print(f"  {len(events)} signal-events found")

    print("Adding forward returns...")
    daily = pd.read_csv(os.path.join(WORKDIR,"daily_forward_full.csv"))
    events = add_forward_returns(events, daily)
    events.to_csv(os.path.join(WORKDIR,"layer3_early_fire_events.csv"), index=False)

    analyze(events)
    print("\nSaved: layer3_early_fire_events.csv")


if __name__=="__main__":
    main()
