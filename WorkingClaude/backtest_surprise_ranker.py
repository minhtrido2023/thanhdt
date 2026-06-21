#!/usr/bin/env python3
"""
backtest_surprise_ranker.py — Use surprise as RANKER (not gate) within HL_3y universe

Hypothesis: HL_3y filter is DURABLE (best OOS). Surprise is decaying but still
positive IC short-term. Use surprise to RANK signals when capacity binds.

Variants:
  V0  baseline           : NP_R≥15 + HL_3y≥5, FIFO order (current production)
  R1  rank_daily         : same filter, prefer higher surprise within day
  R2  rank_strict_top    : when >max_pos signals qualify same day, take top-surprise
  S1  sizing_modulate    : pos_pct varies by surprise quintile
                           Q5 (surprise>1.0): 12%
                           Q4 (0.5-1.0):       10%
                           Q3 (0-0.5):          8% (baseline)
                           Q2 (-0.5-0):         6%
                           Q1 (<-0.5):          4%
  S2  sizing_modulate_v2 : simpler — high surprise (>0.5) → 10% else 8%
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, pickle
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
INIT_NAV = 50e9

print("="*100)
print("  SURPRISE AS RANKER (not gate) — within HL_3y universe")
print("="*100)

# Setup
with open("earnings_px.pkl","rb") as f: px_data = pickle.load(f)
px_data["time"] = pd.to_datetime(px_data["time"])
px_close = px_data.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns")
px_close.index = master_idx
all_dates = np.array(master_idx)
with open("lagged_pos_ov.pkl","rb") as f: ov = pickle.load(f)
ov["time"] = pd.to_datetime(ov["time"])
px_open = ov.pivot_table(index="time", columns="ticker", values="Open", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
liq = ov.pivot_table(index="time", columns="ticker", values="Volume_3M_P50", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)

with open("earnings_surprise_data.pkl","rb") as f: fin = pickle.load(f)
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"])
FLOOR = 1e9
fin["exp_B_MA"] = fin[["NP_P1","NP_P2","NP_P3","NP_P4"]].mean(axis=1)
fin["surprise_B_MA"] = ((fin["NP_P0"] - fin["exp_B_MA"]) / np.maximum(np.abs(fin["exp_B_MA"]), FLOOR)).clip(-5, 5)

ev_class = pd.read_csv("earnings_events_classified.csv", parse_dates=["Release_Date"])
ev = ev_class.merge(fin[["ticker","quarter","Release_Date","surprise_B_MA"]],
                     on=["ticker","quarter","Release_Date"], how="left")
ev = ev.sort_values(["ticker","Release_Date"]).reset_index(drop=True)

LN2 = np.log(2); HL = 3.0
ev["prior_n_good"] = 0; ev["pa_HL3"] = np.nan
for tk, g in ev.groupby("ticker"):
    good_history = []
    for row_idx in g.index.tolist():
        row = ev.loc[row_idx]
        cur_date = row["Release_Date"]
        n_good = len(good_history)
        ev.at[row_idx, "prior_n_good"] = n_good
        if n_good >= 1:
            dates_arr = pd.to_datetime([d for d,_ in good_history])
            posts_arr = np.array([p for _,p in good_history])
            age_yrs = (cur_date - dates_arr).days.values / 365.25
            w = np.exp(-LN2 * age_yrs / HL)
            ev.at[row_idx, "pa_HL3"] = (posts_arr * w).sum() / w.sum() if w.sum() > 0 else np.nan
        if pd.notna(row["NP_R"]) and row["NP_R"] >= 15 and pd.notna(row["post_ret"]):
            good_history.append((cur_date, row["post_ret"]))

# V0 base mask
base_mask = (ev["NP_R"] >= 15) & (ev["prior_n_good"] >= 4) & (ev["pa_HL3"] >= 5)
base = ev[base_mask].copy()
base["surprise_B_MA"] = base["surprise_B_MA"].fillna(0)
print(f"  V0 base events (NP_R+HL_3y): {len(base):,}")

# Check same-day clustering
print(f"\n  Same-day signal clusters:")
day_counts = base.groupby("Release_Date").size()
print(f"    Single signal days: {(day_counts==1).sum():,}")
print(f"    2-3 signal days: {((day_counts>=2)&(day_counts<=3)).sum():,}")
print(f"    4+ signal days: {(day_counts>=4).sum():,}  | max={day_counts.max()}")

def offset_date(ref_dt, offset):
    ref = np.datetime64(ref_dt); pos = np.searchsorted(all_dates, ref, side="right") - 1
    if pos < 0: return None
    tgt = pos + offset
    if tgt >= len(all_dates) or tgt < 0: return None
    return pd.Timestamp(all_dates[tgt])

def run_bt(schedule_df, mode="default", hold=25, sw=pd.Timestamp("2014-04-01"), ew=pd.Timestamp("2026-05-13"),
           entry_offset=5, max_pos=12, default_pos_pct=0.08):
    LIQ_MIN=2e9; SLIP_IN, SLIP_OUT, TAX = 0.001, 0.0015, 0.001
    DEPOSIT=0.01; LIQ_CAP=0.20; MAX_FILL=5

    sched = schedule_df.sort_values(["entry_dt","priority"], ascending=[True, False]).reset_index(drop=True)
    if len(sched) == 0: return None
    entries_by_day = sched.groupby("entry_dt"); exits_by_day = sched.groupby("exit_dt")
    sim_days = [d for d in master_idx if sw <= d <= ew]
    cash = INIT_NAV; positions = {}; nav_history = []; trades = []
    daily_rate = (1+DEPOSIT)**(1/365.25) - 1
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
                gross = pos["shares"]*fpx*(1-SLIP_OUT); net = gross*(1-TAX); cash += net
                trades.append({"side":"SELL","ret_pct":(fpx/pos["entry_px"]-1)*100})
                del positions[tk]
        if dt in entries_by_day.groups:
            mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
            nav_now = cash + mtm
            todays_signals = entries_by_day.get_group(dt)
            # Sort: rank modes prefer higher surprise
            if mode in ("rank_daily","rank_strict","sizing"):
                todays_signals = todays_signals.sort_values("priority", ascending=False)
            for _, en_row in todays_signals.iterrows():
                tk = en_row["ticker"]
                if tk in positions or len(positions) >= max_pos: continue
                fpx = px_open.at[dt, tk] if tk in px_open.columns else np.nan
                if pd.isna(fpx) or fpx <= 0: continue
                adv = liq.at[dt, tk] if tk in liq.columns else 0
                if pd.isna(adv) or adv*fpx < LIQ_MIN: continue
                # Determine sizing
                pct = default_pos_pct
                if mode == "sizing":
                    sur = en_row.get("surprise", 0)
                    if sur > 1.0: pct = 0.12
                    elif sur > 0.5: pct = 0.10
                    elif sur > 0: pct = 0.08
                    elif sur > -0.5: pct = 0.06
                    else: pct = 0.04
                elif mode == "sizing_v2":
                    sur = en_row.get("surprise", 0)
                    pct = 0.10 if sur > 0.5 else 0.08
                target = pct * nav_now
                cap = LIQ_CAP * adv * MAX_FILL * fpx
                alloc = min(target, cap)
                if alloc < 1e6 or alloc > cash: continue
                eff_px = fpx*(1+SLIP_IN); shares = alloc/eff_px; cost = shares*eff_px
                cash -= cost
                positions[tk] = {"entry_dt":dt, "exit_dt":en_row["exit_dt"], "shares":shares, "entry_px":fpx}
                trades.append({"side":"BUY","ret_pct":0})
        mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
        nav_history.append({"date":dt,"nav":cash+mtm})
    nav_df = pd.DataFrame(nav_history).set_index("date")
    sells = pd.DataFrame(trades)
    sells_only = sells[sells["side"]=="SELL"] if len(sells) > 0 else pd.DataFrame()
    if len(nav_df) < 30: return None
    yrs = (nav_df.index[-1]-nav_df.index[0]).days/365.25
    cagr = (nav_df["nav"].iloc[-1]/nav_df["nav"].iloc[0])**(1/yrs)-1
    rets = nav_df["nav"].pct_change().dropna()
    sh = rets.mean()/rets.std()*np.sqrt(len(rets)/yrs) if rets.std()>0 else 0
    dd = ((nav_df["nav"]-nav_df["nav"].cummax())/nav_df["nav"].cummax()).min()
    cal = cagr/abs(dd) if dd<0 else 0
    wr = (sells_only["ret_pct"]>0).mean()*100 if len(sells_only)>0 else 0
    avg_ret = sells_only["ret_pct"].mean() if len(sells_only)>0 else 0
    def m(start, end):
        s = nav_df["nav"][(nav_df.index>=start) & (nav_df.index<=end)]
        if len(s) < 30: return None
        y = (s.index[-1]-s.index[0]).days/365.25
        return (s.iloc[-1]/s.iloc[0])**(1/y)*100 - 100
    return {"trades":len(sells_only), "WR":wr, "avg_ret":avg_ret,
            "CAGR":cagr*100, "Sharpe":sh, "DD":dd*100, "Calmar":cal,
            "OOS_24":m(pd.Timestamp("2024-01-01"), pd.Timestamp("2026-05-13")),
            "IS_14_18":m(pd.Timestamp("2014-04-01"), pd.Timestamp("2018-12-31")),
            "Y22":m(pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
            "Y25":m(pd.Timestamp("2025-01-01"), pd.Timestamp("2025-12-31")),
            "final_NAV":nav_df["nav"].iloc[-1]/1e9}

# Build base schedule (priority by surprise for ranker variants)
schedule = []
for _, row in base.iterrows():
    tk = row["ticker"]; rdt = row["Release_Date"]
    if tk not in px_open.columns: continue
    entry_dt = offset_date(rdt, 5); exit_dt = offset_date(rdt, 30)
    if entry_dt is None or exit_dt is None: continue
    schedule.append({"ticker":tk, "entry_dt":entry_dt, "exit_dt":exit_dt,
                     "surprise":row["surprise_B_MA"], "priority":row["surprise_B_MA"]})
sched_df = pd.DataFrame(schedule)
print(f"\n  Schedule built: {len(sched_df):,} entries")

# Variants
variants = [
    ("V0_baseline_FIFO",        "default"),
    ("R1_rank_within_day",      "rank_daily"),
    ("R2_rank_strict",          "rank_strict"),
    ("S1_sizing_modulate_q5",   "sizing"),
    ("S2_sizing_modulate_v2",   "sizing_v2"),
]

print(f"\n  {'Variant':<24}{'Trades':>8}{'WR':>7}{'avg_ret':>10}{'CAGR':>9}{'Sh':>6}{'DD':>8}{'Cal':>6}{'IS_14-18':>10}{'OOS_24+':>10}{'Y22':>9}{'Y25':>9}")
print("  " + "-"*118)
results = []
for name, mode in variants:
    r = run_bt(sched_df, mode=mode)
    if r is None: continue
    r["name"] = name
    results.append(r)
    print(f"  {name:<24}{r['trades']:>8d}{r['WR']:>6.1f}%{r['avg_ret']:>+9.2f}%{r['CAGR']:>+8.2f}%{r['Sharpe']:>+5.2f}{r['DD']:>+7.1f}%{r['Calmar']:>+5.2f}{r['IS_14_18']:>+9.2f}%{r['OOS_24']:>+9.2f}%{r['Y22']:>+8.1f}%{r['Y25']:>+8.1f}%")

df = pd.DataFrame(results)
df.to_csv("surprise_ranker_results.csv", index=False)

print(f"\n  Diagnostic: IS-OOS gap (overfit indicator):")
for _, r in df.iterrows():
    gap = r['OOS_24'] - r['IS_14_18']
    flag = "✅" if gap > 1 else ("⚠️" if gap > -1 else "❌")
    print(f"    {r['name']:<24}IS={r['IS_14_18']:>+6.2f}%  OOS={r['OOS_24']:>+6.2f}%  Δ={gap:>+6.2f}pp {flag}")

print(f"\n  🏆 Best by OOS_24:")
print(df.nlargest(3, "OOS_24")[["name","CAGR","Sharpe","DD","Calmar","OOS_24","Y22","Y25"]].to_string(index=False, float_format="%.2f"))

print("\nSaved: surprise_ranker_results.csv")
