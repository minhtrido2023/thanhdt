"""Backtest the proposed BUY/SELL timing rules with realistic limit-order miss model.

Strategies:
  ENTRY:
    E0_OPEN_MKT       Market @ session open (BASELINE)
    E1_T1115_LIM      Limit @ 11:15 close, fallback ATC market if miss
    E2_T1300_LIM      Limit @ 13:00 close, fallback ATC market if miss
    E3_ATC_MKT        Market @ ATC
    E4_TWAP_LUNCH     TWAP 5 bars 10:30-11:30
    E5_SEG_AWARE      TOP30→E1, MIDCAP/PENNY→E3
    E6_GAP_AWARE      gap<-1% → E0, gap>+1% → E3, else → E5
  EXIT (mirror):
    X0_OPEN_MKT       Market @ session open (BASELINE)
    X1_T0945_LIM      Limit @ 09:45 close, fallback OPEN_MKT next day if miss
    X2_ATC_MKT        Market @ ATC
    X3_SEG_AWARE      TOP30/MIDCAP→X1, PENNY→X2

Fill mechanics:
  BUY limit @ X: any subsequent bar with low ≤ X fills at X. Miss → fallback to ATC market.
  SELL limit @ X: any subsequent bar with high ≥ X fills at X. Miss → next-day OPEN market.
Slippage (only on market orders, since limit fills at limit price exactly):
  impact_pct = sqrt(min(pos / bar_vol_vnd, 5)) × bar_range_pct/2
  Applied as: market BUY fill = bar_close × (1 + impact); market SELL fill = bar_close × (1 - impact)

Position size (per BA-system, 50B NAV / 10 positions = 5B per ticker, but capped at 20% ADV):
  TOP30:  5B VND
  MIDCAP: capped via ADV → use 1B VND (typical actual size after cap)
  PENNY:  capped → 0.5B VND
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
POS_VND = {"TOP30": 5_000_000_000, "MIDCAP": 1_000_000_000, "PENNY": 500_000_000}

def slot_idx_at(times_hhmm, hhmm_target):
    """Index of first bar at or after hhmm_target. -1 if none."""
    idx = np.where(times_hhmm >= hhmm_target)[0]
    return idx[0] if len(idx) else -1

def market_slippage(bar, pos_vnd, side):
    """Adjustment factor for market order at bar. side=+1 buy, -1 sell."""
    px = bar["close"]
    vol_vnd = bar["volume"] * px * 1000  # vol shares × k VND × 1000 = VND
    if vol_vnd <= 0: return px
    fill = pos_vnd / vol_vnd
    rng_pct = (bar["high"] - bar["low"]) / px
    impact = np.sqrt(min(fill,5.0)) * rng_pct/2
    return px * (1 + side * impact)

def simulate_buy(bars, strategy, pos_vnd, gap_pct=0):
    """Returns (fill_price, slot_filled, missed).
       bars: DataFrame sorted ascending by time, with hhmm column."""
    if len(bars) < 2: return None, None, True
    times = bars["hhmm"].values
    open_bar = bars.iloc[0]
    atc_bar = bars.iloc[-1]

    def lim_buy(slot_hhmm):
        i = slot_idx_at(times, slot_hhmm)
        if i < 0 or i >= len(bars)-1: return None, None
        limit = bars.iloc[i]["close"]
        for j in range(i+1, len(bars)):
            if bars.iloc[j]["low"] <= limit:
                return limit, j
        return None, None

    def twap(start_hhmm, n):
        i = slot_idx_at(times, start_hhmm)
        if i<0: return None
        sl = bars.iloc[i:i+n]
        if len(sl)==0: return None
        # apply slippage per bar (avg over n bars, each with pos/n)
        per = pos_vnd / max(len(sl),1)
        fills = [market_slippage(b, per, +1) for _,b in sl.iterrows()]
        return np.mean(fills)

    if strategy == "E0_OPEN_MKT":
        return market_slippage(open_bar, pos_vnd, +1), 0, False
    if strategy == "E1_T1115_LIM":
        p, j = lim_buy("11:15")
        if p is None:  # miss → ATC market
            return market_slippage(atc_bar, pos_vnd, +1), len(bars)-1, True
        return p, j, False
    if strategy == "E2_T1300_LIM":
        p, j = lim_buy("13:00")
        if p is None:
            return market_slippage(atc_bar, pos_vnd, +1), len(bars)-1, True
        return p, j, False
    if strategy == "E3_ATC_MKT":
        return market_slippage(atc_bar, pos_vnd, +1), len(bars)-1, False
    if strategy == "E4_TWAP_LUNCH":
        p = twap("10:30", 5)
        return (p, None, False) if p else (market_slippage(atc_bar, pos_vnd, +1), len(bars)-1, True)
    if strategy == "E5_SEG_AWARE":
        seg = SEGMENT_MAP.get(bars.iloc[0]["ticker"], "TOP30")
        if seg == "TOP30":
            return simulate_buy(bars, "E1_T1115_LIM", pos_vnd, gap_pct)
        else:
            return simulate_buy(bars, "E3_ATC_MKT", pos_vnd, gap_pct)
    if strategy == "E6_GAP_AWARE":
        if gap_pct < -1.0:
            return simulate_buy(bars, "E0_OPEN_MKT", pos_vnd, gap_pct)
        if gap_pct > 1.0:
            return simulate_buy(bars, "E3_ATC_MKT", pos_vnd, gap_pct)
        return simulate_buy(bars, "E5_SEG_AWARE", pos_vnd, gap_pct)

def simulate_sell(bars, strategy, pos_vnd):
    if len(bars) < 2: return None, None, True
    times = bars["hhmm"].values
    open_bar = bars.iloc[0]
    atc_bar = bars.iloc[-1]

    def lim_sell(slot_hhmm):
        i = slot_idx_at(times, slot_hhmm)
        if i<0 or i>=len(bars)-1: return None, None
        limit = bars.iloc[i]["close"]
        for j in range(i+1, len(bars)):
            if bars.iloc[j]["high"] >= limit:
                return limit, j
        return None, None

    if strategy == "X0_OPEN_MKT":
        return market_slippage(open_bar, pos_vnd, -1), 0, False
    if strategy == "X1_T0945_LIM":
        p, j = lim_sell("09:45")
        if p is None:
            return None, None, True  # miss; caller falls back next-day
        return p, j, False
    if strategy == "X2_ATC_MKT":
        return market_slippage(atc_bar, pos_vnd, -1), len(bars)-1, False
    if strategy == "X3_SEG_AWARE":
        seg = SEGMENT_MAP.get(bars.iloc[0]["ticker"], "TOP30")
        if seg in ("TOP30","MIDCAP"):
            return simulate_sell(bars, "X1_T0945_LIM", pos_vnd)
        else:
            return simulate_sell(bars, "X2_ATC_MKT", pos_vnd)

# ---------- Backtest ----------
def load_intraday():
    with open(CACHE,"rb") as f:
        return pickle.load(f)

def prep_session(df):
    df = df.copy()
    df["time"] = pd.to_datetime(df["time"])
    df["hhmm"] = df["time"].dt.strftime("%H:%M")
    df["date"] = df["time"].dt.date
    return df

def backtest_entry(intraday, hold_days=45):
    """For each (ticker, session), simulate each entry strategy → realized return at T+hold close."""
    # daily forwards
    daily = pd.read_csv(os.path.join(WORKDIR, "daily_forward_full.csv"))
    daily["time"] = pd.to_datetime(daily["time"]).dt.date
    daily = daily.sort_values(["ticker","time"]).reset_index(drop=True)
    daily["Close"] = daily["Close"]/1000.0
    daily[f"Close_T{hold_days}"] = daily.groupby("ticker")["Close"].shift(-hold_days)
    fwd = daily.set_index(["ticker","time"])[f"Close_T{hold_days}"].to_dict()

    strategies = ["E0_OPEN_MKT","E1_T1115_LIM","E2_T1300_LIM","E3_ATC_MKT",
                  "E4_TWAP_LUNCH","E5_SEG_AWARE","E6_GAP_AWARE"]
    rows = []
    for tk, raw in intraday.items():
        d = prep_session(raw)
        d["ticker"] = tk
        prev_close = None
        for sess_date, sub in d.groupby("date"):
            sub = sub.sort_values("time").reset_index(drop=True)
            if len(sub) < 5:
                prev_close = sub["close"].iloc[-1] if len(sub) else prev_close
                continue
            gap = (sub["open"].iloc[0]/prev_close-1)*100 if prev_close else 0
            prev_close = sub["close"].iloc[-1]
            fwd_close = fwd.get((tk, sess_date))
            if pd.isna(fwd_close) or fwd_close is None: continue
            seg = SEGMENT_MAP.get(tk,"?")
            pos_vnd = POS_VND.get(seg, 5_000_000_000)
            for s in strategies:
                fill, _, missed = simulate_buy(sub, s, pos_vnd, gap)
                if fill is None: continue
                ret = (fwd_close/fill - 1)*100
                rows.append({"ticker": tk, "segment": seg, "date": sess_date,
                              "strategy": s, "fill_price": fill, "ret_pct": ret,
                              "missed": missed, "gap_pct": gap})
    return pd.DataFrame(rows)

def backtest_exit(intraday, entry_date_field="date"):
    """For each session, simulate each EXIT strategy at that session.
       Compares fill_price across strategies vs day OPEN baseline."""
    strategies = ["X0_OPEN_MKT","X1_T0945_LIM","X2_ATC_MKT","X3_SEG_AWARE"]
    rows = []
    for tk, raw in intraday.items():
        d = prep_session(raw)
        d["ticker"] = tk
        for sess_date, sub in d.groupby("date"):
            sub = sub.sort_values("time").reset_index(drop=True)
            if len(sub)<5: continue
            seg = SEGMENT_MAP.get(tk,"?")
            pos_vnd = POS_VND.get(seg, 5_000_000_000)
            for s in strategies:
                fill, _, missed = simulate_sell(sub, s, pos_vnd)
                if fill is None: continue  # X1 miss with no fallback handled later
                rows.append({"ticker": tk, "segment": seg, "date": sess_date,
                              "strategy": s, "fill_price": fill, "missed": missed,
                              "day_open": sub["open"].iloc[0]})
    return pd.DataFrame(rows)

def combine_entry_exit(intraday, hold_days=45):
    """End-to-end: entry on day D + exit on day D+hold → realized P&L per strategy combo."""
    daily = pd.read_csv(os.path.join(WORKDIR, "daily_forward_full.csv"))
    daily["time"] = pd.to_datetime(daily["time"]).dt.date
    daily = daily.sort_values(["ticker","time"]).reset_index(drop=True)
    daily["Close"] = daily["Close"]/1000.0
    # map (ticker, date) → next 45-trading-day date
    daily["exit_date"] = daily.groupby("ticker")["time"].shift(-hold_days)
    exit_map = daily.set_index(["ticker","time"])["exit_date"].to_dict()

    entry_strats = ["E0_OPEN_MKT","E1_T1115_LIM","E5_SEG_AWARE","E6_GAP_AWARE"]
    exit_strats = ["X0_OPEN_MKT","X1_T0945_LIM","X2_ATC_MKT","X3_SEG_AWARE"]
    rows = []

    # index intraday sessions by (ticker, date)
    sessions_idx = {}
    for tk, raw in intraday.items():
        d = prep_session(raw)
        d["ticker"] = tk
        for sess_date, sub in d.groupby("date"):
            sessions_idx[(tk, sess_date)] = sub.sort_values("time").reset_index(drop=True)

    for (tk, sess_date), sub in sessions_idx.items():
        if len(sub)<5: continue
        seg = SEGMENT_MAP.get(tk,"?")
        pos_vnd = POS_VND.get(seg, 5_000_000_000)
        # gap
        # previous-day prev_close not easily available — skip gap-aware enhancement here
        gap = 0
        exit_d = exit_map.get((tk, sess_date))
        if exit_d is None or pd.isna(exit_d): continue
        exit_sub = sessions_idx.get((tk, exit_d))
        if exit_sub is None: continue
        for e in entry_strats:
            fill_e, _, miss_e = simulate_buy(sub, e, pos_vnd, gap)
            if fill_e is None: continue
            for x in exit_strats:
                fill_x, _, miss_x = simulate_sell(exit_sub, x, pos_vnd)
                if fill_x is None:
                    # next-day OPEN fallback
                    fill_x = exit_sub.iloc[-1]["close"] * (1 - 0.0005)  # crude fallback proxy
                ret = (fill_x/fill_e - 1)*100 - 0.2  # 2 × 0.1% TC
                rows.append({"ticker": tk, "segment": seg, "date": sess_date,
                              "entry": e, "exit": x, "ret_net_pct": ret,
                              "miss_entry": miss_e, "miss_exit": miss_x})
    return pd.DataFrame(rows)

def report(df_entry, df_exit, df_combined):
    print("="*100)
    print("ENTRY backtest — mean realized return at T+45 close, by segment × strategy")
    print("="*100)
    g = df_entry.groupby(["segment","strategy"]).agg(
        n=("ret_pct","count"), mean=("ret_pct","mean"), median=("ret_pct","median"),
        hit=("ret_pct", lambda s:(s>0).mean()*100), miss_rate=("missed", lambda s:s.mean()*100))
    print(g.round(3).to_string())
    print("\nEntry lift vs E0_OPEN_MKT (baseline) per segment:")
    base = df_entry[df_entry["strategy"]=="E0_OPEN_MKT"].groupby("segment")["ret_pct"].mean()
    for seg in ["TOP30","MIDCAP","PENNY"]:
        b = base.get(seg)
        print(f"\n  [{seg}] baseline mean={b:.3f}%")
        for s in ["E1_T1115_LIM","E2_T1300_LIM","E3_ATC_MKT","E4_TWAP_LUNCH","E5_SEG_AWARE","E6_GAP_AWARE"]:
            m = df_entry[(df_entry["segment"]==seg)&(df_entry["strategy"]==s)]["ret_pct"].mean()
            miss = df_entry[(df_entry["segment"]==seg)&(df_entry["strategy"]==s)]["missed"].mean()*100
            print(f"    {s:18} mean={m:>7.3f}%  lift={m-b:+.3f}pp  miss={miss:.1f}%")

    print("\n" + "="*100)
    print("EXIT backtest — sell fill vs day OPEN baseline (positive = better sell price)")
    print("="*100)
    df = df_exit.copy()
    df["pct_vs_open"] = (df["fill_price"]/df["day_open"]-1)*100  # positive = sold above open
    g = df.groupby(["segment","strategy"]).agg(
        n=("pct_vs_open","count"), mean=("pct_vs_open","mean"), median=("pct_vs_open","median"),
        miss_rate=("missed", lambda s:s.mean()*100))
    print(g.round(3).to_string())

    print("\n" + "="*100)
    print("COMBINED entry+exit — net P&L at T+45 (after 0.2% TC)")
    print("="*100)
    g = df_combined.groupby(["segment","entry","exit"]).agg(
        n=("ret_net_pct","count"), mean=("ret_net_pct","mean"),
        median=("ret_net_pct","median"),
        hit=("ret_net_pct", lambda s:(s>0).mean()*100))
    print(g.round(3).to_string())

    # Best combos per segment
    print("\nBest entry+exit combo per segment (by mean):")
    for seg in ["TOP30","MIDCAP","PENNY"]:
        sub = df_combined[df_combined["segment"]==seg]
        top = sub.groupby(["entry","exit"])["ret_net_pct"].mean().sort_values(ascending=False).head(5)
        base = sub[(sub["entry"]=="E0_OPEN_MKT")&(sub["exit"]=="X0_OPEN_MKT")]["ret_net_pct"].mean()
        print(f"\n  [{seg}] baseline E0+X0 mean = {base:.3f}%")
        for (e,x), v in top.items():
            print(f"    {e:18} + {x:18}  mean={v:>7.3f}%  lift={v-base:+.3f}pp")

def main():
    print("Loading intraday cache...")
    intraday = load_intraday()
    print(f"Loaded {len(intraday)} tickers\n")

    print("Running ENTRY backtest...")
    df_e = backtest_entry(intraday, hold_days=45)
    df_e.to_csv(os.path.join(WORKDIR,"backtest_entry.csv"), index=False)
    print(f"  {len(df_e)} entry-strategy events")

    print("\nRunning EXIT backtest...")
    df_x = backtest_exit(intraday)
    df_x.to_csv(os.path.join(WORKDIR,"backtest_exit.csv"), index=False)
    print(f"  {len(df_x)} exit-strategy events")

    print("\nRunning COMBINED entry+exit backtest (slower)...")
    df_c = combine_entry_exit(intraday, hold_days=45)
    df_c.to_csv(os.path.join(WORKDIR,"backtest_combined.csv"), index=False)
    print(f"  {len(df_c)} entry×exit combo events")

    report(df_e, df_x, df_c)

if __name__=="__main__":
    main()
