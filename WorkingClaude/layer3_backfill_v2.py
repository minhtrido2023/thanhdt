"""More stop variants — try wider stops + shadow comparisons.

V7  : stop -25% intraday hard
V8  : stop -22% intraday hard
V9  : NO intraday stop (rely on journal sell_date for ALL exits)
V10 : EoD close confirms at -20% (no intraday); exit next-day OPEN proxy = sell at -20% from entry
"""
import os, sys, pickle
from datetime import timedelta
import numpy as np
import pandas as pd

sys.path.insert(0, r"/home/trido/thanhdt/WorkingClaude")
from layer3_backfill_simulation import (PLAY_RULE, TC_PCT, simulate_buy, simulate_sell_x1,
                                          prep_session, match_pairs)

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
CACHE = os.path.join(WORKDIR, "intraday_full.pkl")

def run_variant(intraday, pairs, variant, stop_pct):
    rows = []
    for _, p in pairs.iterrows():
        tk = p["ticker"]; buy_d = p["buy_date"]; sell_d = p["sell_date"]
        df_tk = intraday.get(tk)
        if df_tk is None: continue
        df_tk = df_tk.copy()
        df_tk["time"] = pd.to_datetime(df_tk["time"])
        df_tk["date"] = df_tk["time"].dt.date
        buy_bars = prep_session(df_tk[df_tk["date"]==buy_d])
        if len(buy_bars)<5: continue
        rule = PLAY_RULE.get(p["play_type"], "E1_T1115_LIM")
        fill_k, _, _, _ = simulate_buy(buy_bars, rule)
        stop_lvl = fill_k * (1 + stop_pct)
        all_dates = sorted(df_tk["date"].unique())
        intermediate = [d for d in all_dates if buy_d < d <= sell_d]
        exit_type = None; exit_price_k = None; exit_date = None
        if variant in ("V7","V8"):
            # intraday low touches stop
            for d in intermediate:
                sub = prep_session(df_tk[df_tk["date"]==d])
                if len(sub)<5: continue
                if sub["low"].min() <= stop_lvl:
                    exit_type = f"STOP_{variant}"
                    exit_price_k = stop_lvl
                    exit_date = d
                    break
        elif variant == "V10":
            # EoD close <= stop; sell next-day OPEN
            for i, d in enumerate(intermediate):
                sub = prep_session(df_tk[df_tk["date"]==d])
                if len(sub)<5: continue
                eod_close = sub.iloc[-1]["close"]
                if eod_close <= stop_lvl:
                    # next day open
                    next_d = intermediate[i+1] if i+1 < len(intermediate) else d
                    nxt = prep_session(df_tk[df_tk["date"]==next_d])
                    if len(nxt)>=2:
                        exit_price_k = nxt.iloc[0]["open"]
                    else:
                        exit_price_k = eod_close
                    exit_type = f"STOP_{variant}_NEXT_OPEN"
                    exit_date = next_d if i+1 < len(intermediate) else d
                    break
        # V9 has no stop loop; only TIME exit
        if exit_type is None:
            sell_bars = prep_session(df_tk[df_tk["date"]==sell_d])
            if len(sell_bars)<5: continue
            exit_price_k, _ = simulate_sell_x1(sell_bars)
            exit_type = "TIME_X1"; exit_date = sell_d
        gross = (exit_price_k/fill_k - 1)*100
        net = gross - 2*TC_PCT
        rows.append({
            "ticker": tk, "play_type": p["play_type"], "variant": variant,
            "buy_date": buy_d, "exit_date": exit_date, "exit_type": exit_type,
            "new_ret_net": round(net,3),
            "journal_ret_net": round(p["journal_ret_net_pct"],3),
            "lift_pp": round(net - p["journal_ret_net_pct"],3),
            "journal_exit_reason": p["exit_reason_journal"],
        })
    return pd.DataFrame(rows)

def main():
    j = pd.read_csv(os.path.join(WORKDIR, "journal_v6_extended_events.csv"))
    j["date"] = pd.to_datetime(j["date"])
    with open(CACHE,"rb") as f: intraday = pickle.load(f)
    pairs = match_pairs(j)
    pairs = pairs[pairs["buy_date"] >= pd.Timestamp("2025-08-12").date()]
    print(f"{len(pairs)} pairs to test")

    configs = [
        ("V7", -0.25),     # wider -25% intraday hard
        ("V8", -0.22),     # -22% intraday hard
        ("V9", -0.20),     # NO stop (variant unused, stop pct irrelevant)
        ("V10", -0.20),    # EoD close confirms at -20%
    ]
    all_rows = []
    for v, sp in configs:
        print(f"\nVariant {v} (stop_pct={sp})")
        df = run_variant(intraday, pairs, v, sp)
        all_rows.append(df)
        n_stops = df["exit_type"].str.startswith("STOP").sum()
        print(f"  STOP exits={n_stops}, TIME={len(df)-n_stops}, mean lift={df['lift_pp'].mean():+.3f}pp, sum={df['lift_pp'].sum():+.2f}pp")

    combined = pd.concat(all_rows, ignore_index=True)
    combined.to_csv(os.path.join(WORKDIR,"layer3_stop_variants_v2.csv"), index=False)

    print("\n" + "="*100)
    print("FINAL COMPARISON")
    print("="*100)
    g = combined.groupby("variant").agg(
        n=("lift_pp","count"),
        stop_fires=("exit_type", lambda s: s.str.startswith("STOP").sum()),
        mean_lift=("lift_pp","mean"),
        sum_lift=("lift_pp","sum"),
        new_total=("new_ret_net","sum"),
        journal_total=("journal_ret_net","sum"),
        hit_rate=("lift_pp", lambda s:(s>0).mean()*100),
    )
    print(g.round(3).to_string())

    print("\nDetail per variant:")
    for v in ["V7","V8","V9","V10"]:
        sub = combined[combined["variant"]==v]
        stops_fired = sub[sub["exit_type"].str.startswith("STOP")]
        tp = stops_fired[stops_fired["journal_exit_reason"]=="STOP"]
        fp = stops_fired[stops_fired["journal_exit_reason"]!="STOP"]
        print(f"\n  {v}: stop_fires={len(stops_fired)} (TP={len(tp)}, FP={len(fp)})")
        if len(fp): print(f"    FP avg lift = {fp['lift_pp'].mean():+.2f}pp")
        if len(tp): print(f"    TP avg lift = {tp['lift_pp'].mean():+.2f}pp")

if __name__=="__main__":
    main()
