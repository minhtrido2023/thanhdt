"""Test stop variants on the 18 journal events to reduce FP.

Variants:
  V1_HARD       : original — any bar low <= stop_lvl
  V2_AFTER13    : only check stop after 13:00
  V3_CONFIRMED  : require bar.close <= stop_lvl (not just low touch)
  V4_AFTER13_CONFIRMED : combine V2+V3
  V5_EOD_CONFIRMED : only fire if eod_close <= stop_lvl × 0.98 (sell next day open)
  V6_VOLSPIKE   : fire only if stop break + volume in bar > 1.5× avg
"""
import os, sys, pickle
from datetime import timedelta
import numpy as np
import pandas as pd

sys.path.insert(0, r"/home/trido/thanhdt/WorkingClaude")
from layer3_backfill_simulation import (PLAY_RULE, STOP_PCT, S2_DAYCHG_THR, S2_BOUNCE_MIN_PCT,
                                          TC_PCT, simulate_buy, simulate_sell_x1,
                                          prep_session, match_pairs)

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
CACHE = os.path.join(WORKDIR, "data/intraday_full.pkl")

def check_stop_variants(day_bars, stop_lvl):
    """Return dict variant -> hit_price or None."""
    if len(day_bars)<5: return {v: None for v in ["V1","V2","V3","V4","V5","V6"]}
    bars = day_bars.copy()
    if "hhmm" not in bars.columns:
        bars["time"] = pd.to_datetime(bars["time"])
        bars["hhmm"] = bars["time"].dt.strftime("%H:%M")
    res = {}
    # V1 hard: any low touches
    hit_v1 = bars["low"].min() <= stop_lvl
    res["V1"] = stop_lvl if hit_v1 else None
    # V2 after 13:00
    aft = bars[bars["hhmm"]>="13:00"]
    res["V2"] = stop_lvl if (len(aft) and aft["low"].min() <= stop_lvl) else None
    # V3 confirmed close <= stop_lvl
    conf = bars[(bars["low"]<=stop_lvl) & (bars["close"]<=stop_lvl)]
    res["V3"] = stop_lvl if len(conf) else None
    # V4 after 13:00 AND confirmed
    conf2 = bars[(bars["hhmm"]>="13:00") & (bars["low"]<=stop_lvl) & (bars["close"]<=stop_lvl)]
    res["V4"] = stop_lvl if len(conf2) else None
    # V5 EoD confirmed (sell next day OPEN proxy = day close × 1.000)
    eod_close = bars["iloc"](-1) if False else bars.iloc[-1]["close"]
    res["V5"] = eod_close if eod_close <= stop_lvl * 0.98 else None
    # V6 vol spike with break
    bars["volMA20"] = bars["volume"].rolling(20).mean()
    vol_break = bars[(bars["low"]<=stop_lvl) & (bars["volume"] > 1.5 * bars["volMA20"].mean())]
    res["V6"] = stop_lvl if len(vol_break) else None
    return res

def run_variant(intraday, pairs, variant):
    rows = []
    for _, p in pairs.iterrows():
        tk = p["ticker"]; buy_d = p["buy_date"]; sell_d = p["sell_date"]
        df_tk = intraday.get(tk)
        if df_tk is None: continue
        df_tk = df_tk.copy()
        df_tk["time"] = pd.to_datetime(df_tk["time"])
        df_tk["date"] = df_tk["time"].dt.date
        # buy fill
        buy_bars = prep_session(df_tk[df_tk["date"]==buy_d])
        if len(buy_bars)<5: continue
        rule = PLAY_RULE.get(p["play_type"], "E1_T1115_LIM")
        fill_k, missed, fill_detail, baseline_open = simulate_buy(buy_bars, rule)
        stop_lvl = fill_k * (1 + STOP_PCT)
        # iterate days
        all_dates = sorted(df_tk["date"].unique())
        intermediate = [d for d in all_dates if buy_d < d <= sell_d]
        exit_type=None; exit_price_k=None; exit_date=None
        for d in intermediate:
            sub = prep_session(df_tk[df_tk["date"]==d])
            res = check_stop_variants(sub, stop_lvl)
            hit_price = res.get(variant)
            if hit_price is not None:
                exit_type = f"STOP_{variant}"
                exit_price_k = hit_price
                exit_date = d
                break
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
    print("Loading...")
    j = pd.read_csv(os.path.join(WORKDIR, "data/journal_v6_extended_events.csv"))
    j["date"] = pd.to_datetime(j["date"])
    with open(CACHE,"rb") as f: intraday = pickle.load(f)
    pairs = match_pairs(j)
    pairs = pairs[pairs["buy_date"] >= pd.Timestamp("2025-08-12").date()]
    print(f"  {len(pairs)} pairs to test")

    all_rows = []
    for v in ["V1","V2","V3","V4","V5","V6"]:
        print(f"\nRunning variant {v}...")
        df = run_variant(intraday, pairs, v)
        all_rows.append(df)
        n_stops = df["exit_type"].str.startswith("STOP").sum()
        n_time = (df["exit_type"]=="TIME_X1").sum()
        print(f"  exits: {n_stops} STOP, {n_time} TIME")
        print(f"  mean lift: {df['lift_pp'].mean():+.3f}pp  sum: {df['lift_pp'].sum():+.2f}pp  hit_rate: {(df['lift_pp']>0).mean()*100:.1f}%")

    combined = pd.concat(all_rows, ignore_index=True)
    combined.to_csv(os.path.join(WORKDIR,"data/layer3_stop_variants.csv"), index=False)

    print("\n" + "="*100)
    print("VARIANT COMPARISON")
    print("="*100)
    g = combined.groupby("variant").agg(
        n=("lift_pp","count"),
        stop_fires=("exit_type", lambda s: s.str.startswith("STOP").sum()),
        mean_lift=("lift_pp","mean"),
        sum_lift=("lift_pp","sum"),
        new_mean=("new_ret_net","mean"),
        journal_mean=("journal_ret_net","mean"),
        hit_rate=("lift_pp", lambda s:(s>0).mean()*100),
    )
    print(g.round(3).to_string())

    # FP check per variant (intraday stop fired but journal didn't have STOP)
    print("\nFP analysis (new fires stop, but journal exit was NOT STOP):")
    for v in ["V1","V2","V3","V4","V5","V6"]:
        sub = combined[(combined["variant"]==v) & (combined["exit_type"].str.startswith("STOP"))]
        fp = sub[sub["journal_exit_reason"]!="STOP"]
        tp = sub[sub["journal_exit_reason"]=="STOP"]
        print(f"  {v}: STOP fires={len(sub)}, TP(journal also STOP)={len(tp)}, FP={len(fp)}, FP_lift_mean={fp['lift_pp'].mean() if len(fp) else 0:+.2f}pp")

    # detail for V1 vs V4 (best contender)
    print("\nDetail: V1 (HARD) vs V4 (AFTER13_CONFIRMED):")
    v1 = combined[combined["variant"]=="V1"].set_index(["ticker","buy_date"])
    v4 = combined[combined["variant"]=="V4"].set_index(["ticker","buy_date"])
    cmp = pd.DataFrame({"V1_exit":v1["exit_type"], "V1_ret":v1["new_ret_net"],
                          "V4_exit":v4["exit_type"], "V4_ret":v4["new_ret_net"],
                          "journal_ret":v1["journal_ret_net"],
                          "journal_exit":v1["journal_exit_reason"]})
    print(cmp.to_string())

if __name__=="__main__":
    main()
