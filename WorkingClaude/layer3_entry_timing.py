"""When during the trading day is the best moment to BUY?

For each (ticker, session) in top30 universe (~6700 events):
  Compute entry price under multiple intraday strategies:
    OPEN      - first 15m bar close (~09:15)
    15M_AFTER - second 15m bar (~09:30)
    1030      - 10:30 bar
    1115      - morning close (11:15)
    1300      - afternoon open (13:00)
    1400      - 14:00 bar
    ATC       - last bar of session (14:30)
    VWAP      - session VWAP (limit-order proxy)
    DAY_LOW   - oracle: low of day (theoretical best)
    DAY_HIGH  - oracle: worst-case (high of day)

Then measure forward return from entry to:
    T+0 close  (same-day return = how much we 'won' vs late-comers)
    T+5 close
    T+20 close
    T+45 close (BA-system hold)

Conditional analyses:
  - by gap direction (T-1 close vs T open: GAP_UP/FLAT/GAP_DOWN)
  - by prior-day Layer 3 signal (separately)
"""
import os, pickle, sys
import numpy as np
import pandas as pd

sys.path.insert(0, r"/home/trido/thanhdt/WorkingClaude/stockquery")
from stockquery_agent import StockQuery

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
CACHE = os.path.join(WORKDIR, "data/intraday_top30.pkl")

TOP30 = ["VIC","VHM","HPG","SHB","SSI","FPT","VIX","STB","MWG","MSN",
         "VCB","BSR","MBB","VPB","TCB","HDB","HCM","CTG","NVL","BID",
         "CII","PVS","VNM","GEX","VCI","SHS","DXG","VRE","VJC","DCM"]

def fetch_or_load():
    if os.path.exists(CACHE):
        print(f"Loading cached intraday from {CACHE}")
        with open(CACHE, "rb") as f:
            return pickle.load(f)
    print("Fetching intraday for top30 (one-time)...")
    sq = StockQuery()
    out = {}
    for i, tk in enumerate(TOP30):
        try:
            sq.start_date="2025-08-12"; sq.end_date="2026-05-12"
            df = sq.get_historical_symbol(tk, interval="15m")
            if df is not None and len(df) > 50:
                df["time"] = pd.to_datetime(df["time"])
                out[tk] = df
                print(f"  [{i+1}/{len(TOP30)}] {tk}: {len(df)} bars")
        except Exception as e:
            print(f"  [{i+1}/{len(TOP30)}] {tk}: ERROR {e}")
    with open(CACHE, "wb") as f:
        pickle.dump(out, f)
    return out

def session_features(session_df):
    """For one session's bars, compute entry price under each strategy + day stats."""
    if len(session_df) < 5:
        return None
    session_df = session_df.sort_values("time").reset_index(drop=True)
    times = session_df["time"].dt.strftime("%H:%M").values
    closes = session_df["close"].values
    highs = session_df["high"].values
    lows = session_df["low"].values
    opens = session_df["open"].values
    vols = session_df["volume"].values

    # Time-slot lookups (use close of that bar as entry execution proxy)
    def find_close_at(time_str, fallback_first=True):
        idx = np.where(times >= time_str)[0]
        if len(idx) == 0:
            return closes[-1] if fallback_first else np.nan
        return closes[idx[0]]
    def find_close_before_or_at(time_str):
        idx = np.where(times <= time_str)[0]
        if len(idx) == 0: return np.nan
        return closes[idx[-1]]

    day_open = opens[0]
    day_close = closes[-1]
    day_low = lows.min()
    day_high = highs.max()

    # Session VWAP at end of session
    tp = (highs + lows + closes) / 3.0
    vwap = (tp * vols).sum() / max(vols.sum(), 1)

    entries = dict(
        OPEN       = day_open,                       # ATO (open of first bar)
        FIRST_CLOSE= closes[0],                      # close of first bar (~09:30)
        T0930      = find_close_at("09:30"),
        T1000      = find_close_at("10:00"),
        T1030      = find_close_at("10:30"),
        T1100      = find_close_at("11:00"),
        T1115      = find_close_at("11:15"),         # morning close
        T1300      = find_close_at("13:00"),         # afternoon open
        T1330      = find_close_at("13:30"),
        T1400      = find_close_at("14:00"),
        T1430      = find_close_before_or_at("14:30"),
        ATC        = day_close,                      # last bar close
        VWAP       = vwap,
        DAY_LOW    = day_low,                        # oracle low
        DAY_HIGH   = day_high,                       # oracle high
    )
    return entries, day_close, day_low, day_high, day_open

def build_entry_panel(intraday):
    """Build long panel: one row per (ticker, session, strategy) with entry price."""
    rows = []
    for tk, df in intraday.items():
        df = df.copy()
        df["time"] = pd.to_datetime(df["time"])
        df["date"] = df["time"].dt.date
        prev_close = None
        for d, sub in df.groupby("date"):
            r = session_features(sub)
            if r is None: continue
            entries, day_close, day_low, day_high, day_open = r
            # gap direction
            if prev_close is None:
                gap = 0
            else:
                gap = (day_open / prev_close - 1) * 100
            row = {"ticker": tk, "date": d, "day_open": day_open, "day_close": day_close,
                    "day_low": day_low, "day_high": day_high, "gap_pct": gap}
            for k, v in entries.items():
                row[f"entry_{k}"] = v
            rows.append(row)
            prev_close = day_close
    return pd.DataFrame(rows)

def add_forward_closes(panel):
    daily = pd.read_csv(os.path.join(WORKDIR, "data/daily_forward.csv"))
    daily["time"] = pd.to_datetime(daily["time"]).dt.date
    daily = daily.sort_values(["ticker","time"]).reset_index(drop=True)
    # BigQuery daily Close is in raw VND; vnstock 15m close is in thousand VND.
    # Normalize daily to thousand VND so all prices share scale.
    for col in ["Close","Open"]:
        daily[col] = daily[col] / 1000.0
    for k in [1,5,10,20,45]:
        daily[f"Close_T{k}"] = daily.groupby("ticker")["Close"].shift(-k)
    panel = panel.merge(daily[["ticker","time","Close","Close_T1","Close_T5","Close_T10","Close_T20","Close_T45"]],
                        left_on=["ticker","date"], right_on=["ticker","time"], how="left")
    return panel

def analyze(panel):
    STRATEGIES = ["OPEN","T0930","T1000","T1030","T1100","T1115","T1300","T1330","T1400","T1430","ATC","VWAP","DAY_LOW","DAY_HIGH"]
    # ---- Part 1: entry price vs OPEN baseline ----
    print("="*100)
    print(f"PART 1: Entry price vs day OPEN baseline (n={len(panel)} sessions)")
    print("="*100)
    print(f"{'Strategy':12} {'mean_diff_vs_open_%':>22} {'median_%':>12} {'std_%':>10} {'pct_better_than_open':>22} {'pct_at_day_low':>16}")
    for s in STRATEGIES:
        ent = panel[f"entry_{s}"]
        valid = ent.notna() & panel["day_open"].notna()
        diff = (ent / panel["day_open"] - 1) * 100
        d = diff[valid]
        pct_better = (d < 0).mean()*100  # cheaper than open
        pct_at_low = ((ent[valid] - panel["day_low"][valid]).abs() < 1e-6).mean()*100
        print(f"{s:12} {d.mean():>22.3f} {d.median():>12.3f} {d.std():>10.3f} {pct_better:>22.2f} {pct_at_low:>16.2f}")

    # ---- Part 2: forward return from entry → T+N close ----
    print("\n" + "="*100)
    print("PART 2: Forward return from entry to T+N close (avg %)")
    print("="*100)
    print(f"{'Strategy':12} {'T+0 close':>12} {'T+1 close':>12} {'T+5 close':>12} {'T+20 close':>12} {'T+45 close':>12}")
    for s in STRATEGIES:
        ent = panel[f"entry_{s}"]
        r0 = (panel["day_close"]/ent - 1)*100  # same-day from entry to close
        r1 = (panel["Close_T1"]/ent - 1)*100
        r5 = (panel["Close_T5"]/ent - 1)*100
        r20 = (panel["Close_T20"]/ent - 1)*100
        r45 = (panel["Close_T45"]/ent - 1)*100
        print(f"{s:12} {r0.mean():>12.3f} {r1.mean():>12.3f} {r5.mean():>12.3f} {r20.mean():>12.3f} {r45.mean():>12.3f}")

    # ---- Part 3: Sharpe-like (mean/std) for T+45 horizon ----
    print("\n" + "="*100)
    print("PART 3: Risk-adjusted T+45 return (mean / std)")
    print("="*100)
    print(f"{'Strategy':12} {'mean_%':>10} {'std_%':>10} {'sharpe-like':>12} {'hit_%':>8}")
    for s in STRATEGIES:
        ent = panel[f"entry_{s}"]
        r45 = (panel["Close_T45"]/ent - 1)*100
        r = r45.dropna()
        if len(r)==0: continue
        sh = r.mean()/r.std() if r.std()>0 else 0
        hit = (r>0).mean()*100
        print(f"{s:12} {r.mean():>10.3f} {r.std():>10.3f} {sh:>12.4f} {hit:>8.2f}")

    # ---- Part 4: Conditional on gap direction ----
    print("\n" + "="*100)
    print("PART 4: Entry strategy by gap direction (gap = T open vs T-1 close)")
    print("="*100)
    panel["gap_bucket"] = pd.cut(panel["gap_pct"], bins=[-100,-1.0,-0.2,0.2,1.0,100],
                                  labels=["GAP_DN_BIG","GAP_DN","FLAT","GAP_UP","GAP_UP_BIG"])
    for bucket in ["GAP_DN_BIG","GAP_DN","FLAT","GAP_UP","GAP_UP_BIG"]:
        sub = panel[panel["gap_bucket"]==bucket]
        if len(sub)<50: continue
        print(f"\n  [{bucket}] n={len(sub)}")
        print(f"  {'Strategy':12} {'mean_diff_vs_open_%':>22} {'pct_better_than_open':>22}")
        for s in ["OPEN","T0930","T1000","T1030","T1100","T1300","T1400","ATC","VWAP"]:
            ent = sub[f"entry_{s}"]
            diff = (ent/sub["day_open"] - 1)*100
            pct_better = (diff<0).mean()*100
            print(f"  {s:12} {diff.mean():>22.3f} {pct_better:>22.2f}")

    # ---- Part 5: Forward T+45 return by gap bucket, for OPEN vs best alt ----
    print("\n" + "="*100)
    print("PART 5: T+45 return by gap bucket — OPEN vs best alternative")
    print("="*100)
    for bucket in ["GAP_DN_BIG","GAP_DN","FLAT","GAP_UP","GAP_UP_BIG"]:
        sub = panel[panel["gap_bucket"]==bucket]
        if len(sub)<50: continue
        print(f"\n  [{bucket}] n={len(sub)}")
        for s in ["OPEN","T0930","T1000","T1100","T1300","T1400","ATC","VWAP"]:
            ent = sub[f"entry_{s}"]
            r45 = (sub["Close_T45"]/ent - 1)*100
            r = r45.dropna()
            if len(r)==0: continue
            print(f"  {s:12} mean_T45={r.mean():>7.3f}%  median={r.median():>7.3f}%  hit={(r>0).mean()*100:>5.2f}%")

def main():
    intraday = fetch_or_load()
    print(f"\n{len(intraday)} tickers loaded")
    panel = build_entry_panel(intraday)
    print(f"Built panel: {len(panel)} (ticker, session) entries")
    panel = add_forward_closes(panel)
    panel.to_csv(os.path.join(WORKDIR, "data/layer3_entry_panel.csv"), index=False)
    analyze(panel)

if __name__=="__main__":
    main()
