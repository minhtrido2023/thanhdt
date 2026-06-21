"""Apply timing rules to the 18 actual BA-system BUYs in journal_v6_extended_events.
Match each BUY with its SELL pair; simulate alternative entry+exit prices; compute new realized P&L.
"""
import os, pickle
import numpy as np
import pandas as pd
import sys
sys.path.insert(0, r"/home/trido/thanhdt/WorkingClaude")
from layer3_backtest_rules import (simulate_buy, simulate_sell, SEGMENT_MAP, POS_VND,
                                     prep_session, load_intraday)

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

# Wider segment map: include BUY tickers not in original 85
def seg_for(tk):
    if tk in SEGMENT_MAP: return SEGMENT_MAP[tk]
    return "MIDCAP"  # treat unknown midcap-ish; for these we use 1B pos

def pos_for(seg):
    return POS_VND.get(seg, 1_000_000_000)

def main():
    j = pd.read_csv(os.path.join(WORKDIR, "journal_v6_extended_events.csv"))
    j["date"] = pd.to_datetime(j["date"])
    buys = j[j["action"]=="BUY"].sort_values("date").reset_index(drop=True)
    sells = j[j["action"]=="SELL"].sort_values("date").reset_index(drop=True)
    pairs = []
    used = set()
    for _, b in buys.iterrows():
        m = sells[(sells["ticker"]==b["ticker"]) & (sells["date"]>b["date"]) & (~sells.index.isin(used))]
        if not len(m): continue
        s = m.iloc[0]; used.add(s.name)
        pairs.append({"ticker": b["ticker"], "buy_date": b["date"], "sell_date": s["date"],
                       "play_type": b["play_type"], "exit_reason": s["exit_reason"],
                       "buy_price": b["price"], "ret_journal": s["ret_net_pct"]})
    pairs = pd.DataFrame(pairs)
    # derive journal sell price
    pairs["sell_price"] = pairs["buy_price"] * (1 + pairs["ret_journal"]/100)

    intraday = load_intraday()
    # session index
    sessions_idx = {}
    for tk, raw in intraday.items():
        d = prep_session(raw); d["ticker"]=tk
        for sd, sub in d.groupby("date"):
            sessions_idx[(tk, sd)] = sub.sort_values("time").reset_index(drop=True)

    entry_strats = ["E0_OPEN_MKT","E1_T1115_LIM","E3_ATC_MKT","E5_SEG_AWARE"]
    exit_strats = ["X0_OPEN_MKT","X1_T0945_LIM","X2_ATC_MKT","X3_SEG_AWARE"]

    rows = []
    skipped = 0
    for _, p in pairs.iterrows():
        seg = seg_for(p["ticker"])
        pos_vnd = pos_for(seg)
        bd = p["buy_date"].date(); sd = p["sell_date"].date()
        b_sub = sessions_idx.get((p["ticker"], bd))
        s_sub = sessions_idx.get((p["ticker"], sd))
        if b_sub is None or s_sub is None:
            skipped += 1
            continue
        for e in entry_strats:
            fe, _, miss_e = simulate_buy(b_sub, e, pos_vnd, 0)
            if fe is None: continue
            # convert intraday fe (thousand VND) to raw VND to match journal_price scale
            fe_vnd = fe * 1000
            for x in exit_strats:
                fx, _, miss_x = simulate_sell(s_sub, x, pos_vnd)
                if fx is None:
                    # next-day OPEN proxy: use journal's sell_price
                    fx_vnd = p["sell_price"]
                else:
                    fx_vnd = fx * 1000
                ret = (fx_vnd/fe_vnd - 1)*100 - 0.2  # 2 × 0.1% TC
                rows.append({"ticker": p["ticker"], "seg": seg, "buy_date": bd, "sell_date": sd,
                              "play_type": p["play_type"], "exit_reason": p["exit_reason"],
                              "entry": e, "exit": x, "fe_vnd": round(fe_vnd,0), "fx_vnd": round(fx_vnd,0),
                              "ret_pct": round(ret,3), "ret_journal": p["ret_journal"]})
    df = pd.DataFrame(rows)
    print(f"Pairs with intraday on BOTH buy_date & sell_date: {df['ticker'].nunique()} tickers, "
          f"{df.groupby(['ticker','buy_date']).ngroups} pairs (skipped {skipped})")

    print("\nPER-PAIR results (each row = one historical BA BUY × one entry/exit strategy):")
    print("Total combinations:", len(df))

    print("\n" + "="*100)
    print("Mean P&L per entry+exit strategy (across 18 real BA-system BUYs)")
    print("="*100)
    g = df.groupby(["entry","exit"]).agg(
        n=("ret_pct","count"), mean=("ret_pct","mean"), median=("ret_pct","median"),
        sum_pct=("ret_pct","sum"), hit=("ret_pct", lambda s:(s>0).mean()*100))
    print(g.round(3).to_string())

    print("\nLift vs baseline E0_OPEN_MKT + X0_OPEN_MKT:")
    base = df[(df["entry"]=="E0_OPEN_MKT")&(df["exit"]=="X0_OPEN_MKT")]["ret_pct"].mean()
    print(f"  Baseline mean = {base:.3f}%")
    for e in entry_strats:
        for x in exit_strats:
            sub = df[(df["entry"]==e)&(df["exit"]==x)]
            if not len(sub): continue
            m = sub["ret_pct"].mean()
            print(f"  {e:18} + {x:18}  mean={m:>7.3f}%  lift={m-base:+.3f}pp")

    df.to_csv(os.path.join(WORKDIR, "backtest_real_buys.csv"), index=False)
    print("\nSaved: backtest_real_buys.csv")

if __name__=="__main__":
    main()
