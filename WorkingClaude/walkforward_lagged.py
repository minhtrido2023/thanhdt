#!/usr/bin/env python3
"""
walkforward_lagged.py — walk-forward stability check for tuned LAGGED_POS configs

Tests 4 configs:
  BASELINE   : post8 + max10 + pos10% + npr15 + hold25
  CAND_A     : max_pos=14 (CAGR leader)
  CAND_B     : pos_pct=0.08, max_pos=12 (Sharpe leader)
  CAND_C     : max_pos=12 + secboost (balanced)

Walk-forward windows:
  P1_IS_2010-2018 (9y)
  P2_OOS_2019-2026 (7.5y)
  P3_IS_2010-2020 (11y)
  P4_OOS_2021-2026 (5.5y)
  Y2014, Y2015, Y2016, Y2017, Y2018, Y2019, Y2020, Y2021, Y2022, Y2023, Y2024, Y2025 (annual)
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, pickle, subprocess, tempfile
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from io import StringIO
import pandas as pd, numpy as np

sys.path.insert(0, ".")
exec(open("tune_lagged_pos.py").read().split("# ─── Run experiments ─")[0])

# Wrap backtest to accept custom start/end windows
def backtest_window(cfg, sw, ew):
    """Run backtest restricted to [sw, ew] sim window."""
    nm = cfg["name"]
    POST_RET_MIN = cfg.get("post_ret_min", 5.0)
    N_GOOD_MIN = cfg.get("n_good_min", 4)
    NPR_MIN = cfg.get("npr_min", 0.15)
    REV_REQ = cfg.get("rev_req", False)
    PRE_DIP_MAX = cfg.get("pre_dip_max", None)
    ENTRY_OFFSET = cfg.get("entry_offset", 5)
    HOLD_DAYS = cfg.get("hold_days", 25)
    MAX_POS = cfg.get("max_pos", 8)
    POS_PCT = cfg.get("pos_pct", 0.10)
    SECTOR_BOOST = cfg.get("sector_boost", None)
    VNI_6M_MAX = cfg.get("vni_6m_max", None)
    TOP_N_UNI = cfg.get("top_n_uni", None)
    LIQ_MIN = cfg.get("liq_min", 2e9)
    SLIP_IN, SLIP_OUT, TAX_SALE = 0.001, 0.0015, 0.001
    DEPOSIT_RATE = 0.01
    LIQ_CAP_PCT = 0.20
    MAX_FILL_DAYS = 5

    mask = (prof["avg_post_good"] >= POST_RET_MIN) & (prof["n_good"] >= N_GOOD_MIN)
    if TOP_N_UNI:
        universe = prof[mask].nlargest(TOP_N_UNI, "avg_post_good").index.tolist()
    else:
        universe = prof[mask].index.tolist()

    ev = events_all[events_all["ticker"].isin(universe)].copy()
    ev = ev[ev["NP_R"] >= NPR_MIN * 100]
    if REV_REQ: ev = ev[ev["Rev_YoY"] >= 15]

    schedule = []
    for _, row in ev.iterrows():
        tk = row["ticker"]; rdt = row["Release_Date"]
        if tk not in px_open.columns: continue
        if PRE_DIP_MAX is not None:
            p_m30 = get_offset_close(tk, rdt, -30); p_m1 = get_offset_close(tk, rdt, -1)
            if pd.isna(p_m30) or pd.isna(p_m1) or p_m30 <= 0: continue
            if (p_m1/p_m30 - 1)*100 >= PRE_DIP_MAX: continue
        entry_dt = offset_date(rdt, ENTRY_OFFSET); exit_dt = offset_date(rdt, ENTRY_OFFSET + HOLD_DAYS)
        if entry_dt is None or exit_dt is None: continue
        if VNI_6M_MAX is not None:
            v = vni_6m.get(entry_dt, np.nan)
            if pd.notna(v) and v > VNI_6M_MAX: continue
        schedule.append({"ticker":tk, "entry_dt":entry_dt, "exit_dt":exit_dt, "release_dt":rdt})
    sched = pd.DataFrame(schedule).sort_values("entry_dt").reset_index(drop=True)
    entries_by_day = sched.groupby("entry_dt")
    exits_by_day = sched.groupby("exit_dt")

    sim_days = [d for d in master_idx if sw <= d <= ew]
    cash = INIT_NAV; positions = {}; nav_history = []; trades = []
    daily_rate = (1+DEPOSIT_RATE)**(1/365.25) - 1

    for dt in sim_days:
        cash *= (1 + daily_rate)
        if dt in exits_by_day.groups:
            for _, ex_row in exits_by_day.get_group(dt).iterrows():
                tk = ex_row["ticker"]
                if tk not in positions: continue
                pos = positions[tk]
                if pos["exit_dt"] != dt: continue
                fpx = px_open.at[dt, tk] if tk in px_open.columns else np.nan
                if pd.isna(fpx) or fpx <= 0:
                    fpx = px_close.at[dt, tk] if tk in px_close.columns else np.nan
                    if pd.isna(fpx) or fpx <= 0: continue
                gross = pos["shares"]*fpx*(1-SLIP_OUT); net = gross*(1-TAX_SALE); cash += net
                ret_pct = (fpx/pos["entry_px"]-1)*100
                trades.append({"dt":dt,"ticker":tk,"side":"SELL","ret_pct":ret_pct,"hold_days":(dt-pos["entry_dt"]).days})
                del positions[tk]
        if dt in entries_by_day.groups:
            mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
            nav_now = cash + mtm
            for _, en_row in entries_by_day.get_group(dt).iterrows():
                tk = en_row["ticker"]
                if tk in positions: continue
                if len(positions) >= MAX_POS: continue
                fpx = px_open.at[dt, tk] if tk in px_open.columns else np.nan
                if pd.isna(fpx) or fpx <= 0: continue
                adv = liq.at[dt, tk] if tk in liq.columns else 0
                if pd.isna(adv) or adv*fpx < LIQ_MIN: continue
                pct = POS_PCT
                if SECTOR_BOOST is not None:
                    sub = ticker_sub.get(tk, "DEFAULT")
                    if sub in SECTOR_BOOST: pct = SECTOR_BOOST[sub]
                target = pct * nav_now
                cap = LIQ_CAP_PCT * adv * MAX_FILL_DAYS * fpx
                alloc = min(target, cap)
                if alloc < 1e6 or alloc > cash: continue
                eff_px = fpx*(1+SLIP_IN); shares = alloc/eff_px; cost = shares*eff_px
                cash -= cost
                positions[tk] = {"entry_dt":dt, "exit_dt":en_row["exit_dt"], "shares":shares, "entry_px":fpx}
                trades.append({"dt":dt,"ticker":tk,"side":"BUY","ret_pct":0,"hold_days":0})
        mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
        nav_history.append({"date":dt,"nav":cash+mtm})

    nav_df = pd.DataFrame(nav_history).set_index("date")
    trades_df = pd.DataFrame(trades)
    sells = trades_df[trades_df["side"]=="SELL"]

    if len(nav_df) < 30: return None
    yrs = (nav_df.index[-1]-nav_df.index[0]).days/365.25
    cagr = (nav_df["nav"].iloc[-1]/nav_df["nav"].iloc[0])**(1/yrs)-1
    rets = nav_df["nav"].pct_change().dropna()
    spy = len(rets)/yrs
    sh = rets.mean()/rets.std()*np.sqrt(spy) if rets.std()>0 else 0
    dd = (nav_df["nav"]-nav_df["nav"].cummax())/nav_df["nav"].cummax()
    mdd = dd.min()
    cal = cagr/abs(mdd) if mdd<0 else 0
    wr = (sells["ret_pct"]>0).mean()*100 if len(sells)>0 else 0
    return {"CAGR":cagr*100, "Sharpe":sh, "MaxDD":mdd*100, "Calmar":cal,
            "WR":wr, "N":len(sells), "final_nav":nav_df["nav"].iloc[-1]/1e9}

# Configs
configs = {
    "BASELINE":  {"post_ret_min":8, "max_pos":10, "pos_pct":0.10},
    "CAND_A_max14":  {"post_ret_min":8, "max_pos":14, "pos_pct":0.10},
    "CAND_B_pos8_max12":  {"post_ret_min":8, "max_pos":12, "pos_pct":0.08},
    "CAND_C_max12_sec":  {"post_ret_min":8, "max_pos":12, "pos_pct":0.10,
                           "sector_boost":{"SECURITIES":0.12,"REIT_RES":0.12}},
}

# Walk-forward windows
windows = [
    ("FULL",      pd.Timestamp("2010-01-01"), pd.Timestamp("2026-05-13")),
    ("P1_IS_10-18",  pd.Timestamp("2010-01-01"), pd.Timestamp("2018-12-31")),
    ("P2_OOS_19-26", pd.Timestamp("2019-01-01"), pd.Timestamp("2026-05-13")),
    ("P3_IS_10-20",  pd.Timestamp("2010-01-01"), pd.Timestamp("2020-12-31")),
    ("P4_OOS_21-26", pd.Timestamp("2021-01-01"), pd.Timestamp("2026-05-13")),
    ("P5_IS_10-14",  pd.Timestamp("2010-01-01"), pd.Timestamp("2014-12-31")),
    ("P6_OOS_15-26", pd.Timestamp("2015-01-01"), pd.Timestamp("2026-05-13")),
]
# Annual blocks
for yr in range(2014, 2026):
    windows.append((f"Y{yr}", pd.Timestamp(f"{yr}-01-01"), pd.Timestamp(f"{yr}-12-31")))

# Run
print("\nWalk-forward stability test ...")
print(f"{'Config':<22} {'Window':<14} {'CAGR':>8} {'Sharpe':>8} {'MaxDD':>9} {'Calmar':>7} {'WR':>6} {'N':>5}")
print("-"*90)
results = []
for cfg_name, cfg_params in configs.items():
    cfg_params["name"] = cfg_name
    for wn, sw, ew in windows:
        r = backtest_window(cfg_params, sw, ew)
        if r is None: continue
        results.append({"config":cfg_name,"window":wn,"start":sw,"end":ew, **r})
        print(f"{cfg_name:<22} {wn:<14} {r['CAGR']:>+7.2f}% {r['Sharpe']:>+7.2f} {r['MaxDD']:>+8.2f}% {r['Calmar']:>+6.2f} {r['WR']:>+5.1f}% {r['N']:>5d}")
    print()

res_df = pd.DataFrame(results)
res_df.to_csv("data/lagged_pos_walkforward.csv", index=False)

# Summary: IS vs OOS comparison
print("\n" + "="*100)
print("  IS vs OOS comparison per config (split at 2018 / 2020 / 2014)")
print("="*100)
print(f"{'Config':<22} {'Split':<6} {'IS CAGR':>10} {'OOS CAGR':>10} {'Δ':>6} {'IS Sh':>7} {'OOS Sh':>7} {'IS DD':>8} {'OOS DD':>8}")
splits = [
    ("18/19", "P1_IS_10-18", "P2_OOS_19-26"),
    ("20/21", "P3_IS_10-20", "P4_OOS_21-26"),
    ("14/15", "P5_IS_10-14", "P6_OOS_15-26"),
]
for cfg in configs:
    for sname, isn, oosn in splits:
        ir = res_df[(res_df["config"]==cfg) & (res_df["window"]==isn)].iloc[0]
        or_ = res_df[(res_df["config"]==cfg) & (res_df["window"]==oosn)].iloc[0]
        print(f"{cfg:<22} {sname:<6} {ir['CAGR']:>+9.2f}% {or_['CAGR']:>+9.2f}% {or_['CAGR']-ir['CAGR']:>+5.2f} {ir['Sharpe']:>+6.2f} {or_['Sharpe']:>+6.2f} {ir['MaxDD']:>+7.2f}% {or_['MaxDD']:>+7.2f}%")
    print()

# Annual stability
print("\n" + "="*100)
print("  Annual CAGR per config (consistency check)")
print("="*100)
yr_cols = [f"Y{y}" for y in range(2014, 2026)]
print(f"{'Config':<22}" + "".join(f"{y[-2:]:>7}" for y in yr_cols))
for cfg in configs:
    line = f"{cfg:<22}"
    for yc in yr_cols:
        rr = res_df[(res_df["config"]==cfg) & (res_df["window"]==yc)]
        if len(rr): line += f"{rr.iloc[0]['CAGR']:>+6.1f}%"
        else: line += " " * 7
    print(line)

# Worst year
print(f"\n  {'Config':<22}{'Worst Yr':<10}{'CAGR':>8}{'Best Yr':<10}{'CAGR':>8}{'Avg Yr CAGR':>12}{'Std':>8}")
for cfg in configs:
    yrs = res_df[(res_df["config"]==cfg) & (res_df["window"].str.startswith("Y"))]
    if len(yrs) > 0:
        worst = yrs.loc[yrs["CAGR"].idxmin()]
        best = yrs.loc[yrs["CAGR"].idxmax()]
        avg = yrs["CAGR"].mean(); std = yrs["CAGR"].std()
        print(f"  {cfg:<22}{worst['window']:<10}{worst['CAGR']:>+7.1f}%{best['window']:<10}{best['CAGR']:>+7.1f}%{avg:>+11.1f}%{std:>+7.1f}")
print("\nSaved: lagged_pos_walkforward.csv")
