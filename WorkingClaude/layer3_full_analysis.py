"""Full BUY + SELL timing analysis across top30 / midcap / penny + slippage model.

Universe (all via vnstock for intraday, BQ used only for daily forward returns & liquidity ranking):
  TOP30   - ADV >= 270B VND/day
  MIDCAP  - ADV 25-50B VND/day
  PENNY   - ADV 5-10B VND/day, price < 15k VND

For each segment, for each (ticker, session_date):
  1. Compute entry price at each 15m slot (OPEN, T0930, ..., ATC, VWAP)
  2. Compute exit price at each slot (same, but we want HIGHEST for SELL)
  3. Compute volume profile at each slot (for slippage modeling)
  4. Match forward closes from daily for hold-period analysis

Slippage hypothesis:
  position_size_vnd = (say) 1B VND
  fill_rate = position_size / bar_volume_vnd
  expected_impact_pct = sqrt(fill_rate) * (bar_range_pct/2) * 100   (Almgren-Chriss-like)
  net_advantage_pct = timing_benefit_pct - expected_impact_pct
"""
import os, pickle, sys, time
import numpy as np
import pandas as pd

sys.path.insert(0, r"/home/trido/thanhdt/WorkingClaude/stockquery")
from stockquery_agent import StockQuery

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
CACHE_BIG = os.path.join(WORKDIR, "data/intraday_full.pkl")
CACHE_TOP30 = os.path.join(WORKDIR, "data/intraday_top30.pkl")

TOP30 = ["VIC","VHM","HPG","SHB","SSI","FPT","VIX","STB","MWG","MSN",
         "VCB","BSR","MBB","VPB","TCB","HDB","HCM","CTG","NVL","BID",
         "CII","PVS","VNM","GEX","VCI","SHS","DXG","VRE","VJC","DCM"]
MIDCAP = ['OCB','SSB','VDS','HUT','IJC','TCM','SCR','CTR','BVB','BSI',
          'REE','HVN','VFS','BVH','KSB','SZC','PAN','DDV','LCG','OIL',
          'NT2','DXS','VTZ','BCM','YEG','VGS','FCN','BCG','VC3','DCL']
PENNY  = ['MZG','SBS','CRC','CSM','VAB','APS','TIG','DRI','IDI','HHP',
          'DLG','IDJ','DC4','ASM','C69','G36','NVB','TDC','SHI','CRE',
          'APG','SMC','HSL','NDN','HTN']

SEGMENT_MAP = {**{t: "TOP30" for t in TOP30},
               **{t: "MIDCAP" for t in MIDCAP},
               **{t: "PENNY" for t in PENNY}}

# 15m slot names (Vietnam session 09:15-11:30 + 13:00-14:45)
SLOTS = [("OPEN","09:15"),("T0930","09:30"),("T0945","09:45"),("T1000","10:00"),
         ("T1015","10:15"),("T1030","10:30"),("T1045","10:45"),("T1100","11:00"),
         ("T1115","11:15"),("T1130","11:30"),
         ("T1300","13:00"),("T1315","13:15"),("T1330","13:30"),("T1345","13:45"),
         ("T1400","14:00"),("T1415","14:15"),("T1430","14:30"),("ATC","14:45")]

def fetch_segment(tickers, label, cache_existing=None):
    """Fetch 15m for given tickers, merge with existing cache."""
    out = {}
    if cache_existing:
        out.update(cache_existing)
    sq = StockQuery()
    need = [t for t in tickers if t not in out]
    print(f"\nFetching {len(need)} {label} tickers (already have {len(tickers)-len(need)})...")
    for i, tk in enumerate(need):
        try:
            sq.start_date="2025-08-12"; sq.end_date="2026-05-12"
            df = sq.get_historical_symbol(tk, interval="15m")
            if df is not None and len(df) > 50:
                df["time"] = pd.to_datetime(df["time"])
                out[tk] = df
                print(f"  [{i+1}/{len(need)}] {tk}: {len(df)} bars")
            else:
                print(f"  [{i+1}/{len(need)}] {tk}: NO DATA")
        except Exception as e:
            print(f"  [{i+1}/{len(need)}] {tk}: ERROR {str(e)[:60]}")
        time.sleep(0.1)
    return out

def build_panel(intraday):
    """Long panel of (ticker, session_date, slot, close_price, bar_volume, bar_range)."""
    rows = []
    for tk, df in intraday.items():
        df = df.copy()
        df["time"] = pd.to_datetime(df["time"])
        df["date"] = df["time"].dt.date
        df["hhmm"] = df["time"].dt.strftime("%H:%M")
        prev_close = None
        for d, sub in df.groupby("date"):
            sub = sub.sort_values("time").reset_index(drop=True)
            if len(sub) < 5:
                prev_close = sub["close"].iloc[-1] if len(sub) else prev_close
                continue
            day_open = sub["open"].iloc[0]
            day_close = sub["close"].iloc[-1]
            day_low = sub["low"].min()
            day_high = sub["high"].max()
            tp = (sub["high"]+sub["low"]+sub["close"])/3.0
            vwap = (tp * sub["volume"]).sum() / max(sub["volume"].sum(),1)
            gap = (day_open/prev_close - 1)*100 if prev_close else 0
            # find each slot bar
            slot_data = {}
            for sname, hh in SLOTS:
                idx = sub[sub["hhmm"] >= hh].index
                if len(idx)==0:
                    bar = sub.iloc[-1]
                else:
                    bar = sub.loc[idx[0]]
                slot_data[sname] = dict(price=bar["close"], vol=bar["volume"], rng=(bar["high"]-bar["low"]))
            row = {"ticker": tk, "segment": SEGMENT_MAP.get(tk,"?"),
                   "date": d, "day_open": day_open, "day_close": day_close,
                   "day_low": day_low, "day_high": day_high, "gap_pct": gap,
                   "session_vol_vnd": (sub["close"]*sub["volume"]).sum()*1000,
                   "vwap": vwap}
            for sname, d2 in slot_data.items():
                row[f"px_{sname}"] = d2["price"]
                row[f"vol_{sname}"] = d2["vol"]
                row[f"rng_{sname}"] = d2["rng"]
            rows.append(row)
            prev_close = day_close
    return pd.DataFrame(rows)

def add_forward_closes(panel):
    daily = pd.read_csv(os.path.join(WORKDIR, "data/daily_forward_full.csv"))
    daily["time"] = pd.to_datetime(daily["time"]).dt.date
    daily = daily.sort_values(["ticker","time"]).reset_index(drop=True)
    for col in ["Close","Open"]:
        daily[col] = daily[col]/1000.0   # match thousand VND scale
    for k in [1,5,10,20,45]:
        daily[f"Close_T{k}"] = daily.groupby("ticker")["Close"].shift(-k)
    panel = panel.merge(daily[["ticker","time","Close","Close_T1","Close_T5","Close_T10","Close_T20","Close_T45"]],
                        left_on=["ticker","date"], right_on=["ticker","time"], how="left")
    return panel

# ---------- Analysis ----------
def buy_timing(panel, segment):
    """For a given segment, what's the cheapest entry slot?"""
    sub = panel[panel["segment"]==segment]
    print(f"\n{'='*100}\nBUY TIMING — segment {segment} (n={len(sub)} sessions)\n{'='*100}")
    print(f"{'Slot':10} {'mean_pct_vs_open':>20} {'median_%':>10} {'pct_better':>12} {'T+45_ret_%':>12} {'sharpe_T45':>12}")
    for sname,_ in SLOTS + [("VWAP","vwap"),("DAY_LOW","low"),("DAY_HIGH","high")]:
        if sname=="VWAP": ent = sub["vwap"]
        elif sname=="DAY_LOW": ent = sub["day_low"]
        elif sname=="DAY_HIGH": ent = sub["day_high"]
        else: ent = sub.get(f"px_{sname}")
        if ent is None or ent.isna().all(): continue
        diff = (ent/sub["day_open"]-1)*100
        pct_better = (diff<0).mean()*100
        r45 = (sub["Close_T45"]/ent - 1)*100
        sh = r45.mean()/r45.std() if r45.std()>0 else 0
        print(f"{sname:10} {diff.mean():>20.3f} {diff.median():>10.3f} {pct_better:>12.2f} {r45.mean():>12.3f} {sh:>12.4f}")

def sell_timing(panel, segment):
    """For a given segment, what's the highest-price slot (best to SELL)?"""
    sub = panel[panel["segment"]==segment]
    print(f"\n{'='*100}\nSELL TIMING — segment {segment} (n={len(sub)} sessions)\n{'='*100}")
    print(f"{'Slot':10} {'mean_pct_vs_open':>20} {'pct_higher_than_open':>22} {'pct_at_day_high':>16}")
    for sname,_ in SLOTS + [("VWAP","vwap"),("DAY_HIGH","high")]:
        if sname=="VWAP": ent = sub["vwap"]
        elif sname=="DAY_HIGH": ent = sub["day_high"]
        else: ent = sub.get(f"px_{sname}")
        if ent is None or ent.isna().all(): continue
        diff = (ent/sub["day_open"]-1)*100
        pct_higher = (diff>0).mean()*100
        pct_at_high = ((ent - sub["day_high"]).abs() < 1e-6).mean()*100
        print(f"{sname:10} {diff.mean():>20.3f} {pct_higher:>22.2f} {pct_at_high:>16.2f}")

def slippage_model(panel, segment, position_size_vnd):
    """For a given segment + position size, compute expected slippage at each slot.
       Model: fill_rate = pos / bar_vol_vnd ; impact_pct = sqrt(fill_rate) * (rng_pct/2)
    """
    sub = panel[panel["segment"]==segment]
    print(f"\n{'='*100}\nSLIPPAGE — {segment} | position={position_size_vnd/1e9:.1f}B VND ({position_size_vnd/1e6:.0f}M)\n{'='*100}")
    print(f"{'Slot':10} {'avg_bar_vol_M_vnd':>20} {'avg_fill_rate_%':>18} {'med_impact_pct':>16} {'avg_impact_pct':>16}")
    for sname,_ in SLOTS:
        col_v = f"vol_{sname}"; col_p = f"px_{sname}"; col_r = f"rng_{sname}"
        if col_v not in sub.columns: continue
        bar_vol_vnd = sub[col_v]*sub[col_p]*1000  # vol shares * price in k VND * 1000 = VND
        fill = position_size_vnd / bar_vol_vnd.replace(0,np.nan)
        rng_pct = sub[col_r]/sub[col_p]*100
        impact = np.sqrt(fill.clip(0,5)) * rng_pct/2  # cap fill_rate at 5x for stability
        print(f"{sname:10} {bar_vol_vnd.mean()/1e6:>20.1f} {fill.mean()*100:>18.2f} {impact.median():>16.3f} {impact.mean():>16.3f}")

def net_advantage(panel, segment, position_size_vnd):
    """Net = (price_savings_vs_open) - (slippage_impact_at_slot)"""
    sub = panel[panel["segment"]==segment]
    print(f"\n{'='*100}\nNET BUY ADVANTAGE — {segment} | position={position_size_vnd/1e9:.1f}B VND\n{'='*100}")
    print(f"{'Slot':10} {'timing_save_%':>15} {'expected_impact_%':>18} {'NET_advantage_%':>18}")
    rows = []
    for sname,_ in SLOTS:
        ent = sub[f"px_{sname}"]
        diff = (ent/sub["day_open"]-1)*100
        timing = -diff.mean()  # positive = we save by waiting
        bar_vol_vnd = sub[f"vol_{sname}"]*ent*1000
        fill = position_size_vnd / bar_vol_vnd.replace(0,np.nan)
        rng_pct = sub[f"rng_{sname}"]/ent*100
        impact = np.sqrt(fill.clip(0,5)) * rng_pct/2
        net = timing - impact.mean()
        rows.append({"slot": sname, "timing_save": round(timing,3),
                    "impact": round(impact.mean(),3), "net": round(net,3)})
    df = pd.DataFrame(rows).sort_values("net", ascending=False)
    print(df.to_string(index=False))
    return df

def main():
    # Step 1: Cache top30 if not present
    intraday = {}
    if os.path.exists(CACHE_BIG):
        with open(CACHE_BIG,"rb") as f:
            intraday = pickle.load(f)
        print(f"Loaded {len(intraday)} tickers from cache")
    elif os.path.exists(CACHE_TOP30):
        with open(CACHE_TOP30,"rb") as f:
            intraday = pickle.load(f)
        print(f"Loaded {len(intraday)} top30 tickers from existing cache")

    # Fetch missing
    all_tickers = TOP30 + MIDCAP + PENNY
    intraday = fetch_segment(all_tickers, "all", cache_existing=intraday)
    with open(CACHE_BIG,"wb") as f:
        pickle.dump(intraday, f)
    print(f"\nTotal cached: {len(intraday)} tickers")

    # Step 2: Get daily forward closes via BQ
    if not os.path.exists(os.path.join(WORKDIR, "data/daily_forward_full.csv")):
        print("\nFetching daily forward closes from BQ...")
        import subprocess
        tickers_sql = ",".join([f'"{t}"' for t in all_tickers])
        sql = f"SELECT t.ticker, t.time, t.Open, t.Close FROM tav2_bq.ticker AS t WHERE t.ticker IN ({tickers_sql}) AND t.time >= \"2025-08-01\" ORDER BY t.ticker, t.time"
        result = subprocess.run(["bash","-c",
            f'source ~/.bashrc 2>/dev/null; bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 --format=csv --max_rows=50000 \'{sql}\' > daily_forward_full.csv'],
            capture_output=True, text=True, timeout=180)
        print(result.stdout[-500:] if result.stdout else "")
        print(result.stderr[-500:] if result.stderr else "")

    # Step 3: Build panel
    panel = build_panel(intraday)
    print(f"\nBuilt panel: {len(panel)} sessions across {panel['ticker'].nunique()} tickers")
    print(f"  TOP30: {(panel['segment']=='TOP30').sum()}, MIDCAP: {(panel['segment']=='MIDCAP').sum()}, PENNY: {(panel['segment']=='PENNY').sum()}")
    panel = add_forward_closes(panel)

    # Step 4: Per-segment analyses
    for seg in ["TOP30","MIDCAP","PENNY"]:
        buy_timing(panel, seg)
    print()
    for seg in ["TOP30","MIDCAP","PENNY"]:
        sell_timing(panel, seg)
    print()
    # Slippage at typical BA-system position sizes
    for seg, pos_vnd in [("TOP30",1_000_000_000),("MIDCAP",500_000_000),("PENNY",200_000_000)]:
        slippage_model(panel, seg, pos_vnd)
        net_advantage(panel, seg, pos_vnd)

    panel.to_csv(os.path.join(WORKDIR,"data/layer3_full_panel.csv"), index=False)
    print(f"\nSaved panel: layer3_full_panel.csv  ({len(panel)} rows)")

if __name__=="__main__":
    main()
