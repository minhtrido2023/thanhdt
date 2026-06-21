#!/usr/bin/env python3
"""
backtest_surprise_v6_extended.py — V6 triple stack + extended hold variants

Tests:
  V0  CURRENT_HL3y     : NP_R≥15 + HL_3y≥5, hold 25 (baseline)
  V5  SUR+NPR          : NP_R≥15 + sur≥0.5, hold 25 (winner so far)
  V6  TRIPLE_25        : NP_R≥15 + sur≥0.5 + HL_3y≥5, hold 25
  V7  V5_hold35        : V5 with hold 35
  V8  V5_hold45        : V5 with hold 45
  V9  V5_hold60        : V5 with hold 60
  V10 V5_hold75        : V5 with hold 75
  V11 V6_hold45        : Triple stack with hold 45
  V12 V6_hold60        : Triple stack with hold 60
  V13 SUR10_hold60     : Strict surprise 1.0 + hold 60

Same execution params, just vary filter + hold_days.
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
print("  V6 TRIPLE STACK + EXTENDED HOLD VARIANTS")
print("="*100)

# Load data
print("\n[Setup] Loading caches ...")
with open("data/earnings_px.pkl","rb") as f: px_data = pickle.load(f)
px_data["time"] = pd.to_datetime(px_data["time"])
px_close = px_data.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns")
px_close.index = master_idx
all_dates = np.array(master_idx)

with open("data/lagged_pos_ov.pkl","rb") as f: ov = pickle.load(f)
ov["time"] = pd.to_datetime(ov["time"])
px_open = ov.pivot_table(index="time", columns="ticker", values="Open", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
liq = ov.pivot_table(index="time", columns="ticker", values="Volume_3M_P50", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)

# Compute surprise + HL_3y profile
with open("data/earnings_surprise_data.pkl","rb") as f: fin = pickle.load(f)
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"])
FLOOR = 1e9
fin["exp_B_MA"] = fin[["NP_P1","NP_P2","NP_P3","NP_P4"]].mean(axis=1)
fin["surprise_B_MA"] = ((fin["NP_P0"] - fin["exp_B_MA"]) / np.maximum(np.abs(fin["exp_B_MA"]), FLOOR)).clip(-5, 5)

ev_class = pd.read_csv("data/earnings_events_classified.csv", parse_dates=["Release_Date"])
ev = ev_class.merge(fin[["ticker","quarter","Release_Date","surprise_B_MA"]],
                     on=["ticker","quarter","Release_Date"], how="left")
ev = ev.sort_values(["ticker","Release_Date"]).reset_index(drop=True)
print(f"  Events: {len(ev):,}")

# HL_3y profile
LN2 = np.log(2); HL = 3.0
ev["prior_n_good"] = 0
ev["pa_HL3"] = np.nan
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

print(f"  Surprise: {ev['surprise_B_MA'].notna().sum():,} | HL_3y: {ev['pa_HL3'].notna().sum():,}")

# ─── Backtest function with variable hold ────────────────────────────────
def offset_date(ref_dt, offset):
    ref = np.datetime64(ref_dt); pos = np.searchsorted(all_dates, ref, side="right") - 1
    if pos < 0: return None
    tgt = pos + offset
    if tgt >= len(all_dates) or tgt < 0: return None
    return pd.Timestamp(all_dates[tgt])

def run_bt(event_mask, hold=25, sw=pd.Timestamp("2014-04-01"), ew=pd.Timestamp("2026-05-13"),
           entry_offset=5, max_pos=12, pos_pct=0.08):
    LIQ_MIN=2e9; SLIP_IN, SLIP_OUT, TAX = 0.001, 0.0015, 0.001
    DEPOSIT=0.01; LIQ_CAP=0.20; MAX_FILL=5

    e = ev[event_mask].copy()
    schedule = []
    for _, row in e.iterrows():
        tk = row["ticker"]; rdt = row["Release_Date"]
        if tk not in px_open.columns: continue
        entry_dt = offset_date(rdt, entry_offset); exit_dt = offset_date(rdt, entry_offset + hold)
        if entry_dt is None or exit_dt is None: continue
        schedule.append({"ticker":tk, "entry_dt":entry_dt, "exit_dt":exit_dt})
    if not schedule: return None
    sched = pd.DataFrame(schedule).sort_values("entry_dt").reset_index(drop=True)
    entries_by_day = sched.groupby("entry_dt")
    exits_by_day = sched.groupby("exit_dt")
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
            for _, en_row in entries_by_day.get_group(dt).iterrows():
                tk = en_row["ticker"]
                if tk in positions or len(positions) >= max_pos: continue
                fpx = px_open.at[dt, tk] if tk in px_open.columns else np.nan
                if pd.isna(fpx) or fpx <= 0: continue
                adv = liq.at[dt, tk] if tk in liq.columns else 0
                if pd.isna(adv) or adv*fpx < LIQ_MIN: continue
                target = pos_pct * nav_now
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
    return {"sched_N":len(sched), "trades":len(sells_only), "WR":wr, "avg_ret":avg_ret,
            "CAGR":cagr*100, "Sharpe":sh, "DD":dd*100, "Calmar":cal,
            "OOS_24": m(pd.Timestamp("2024-01-01"), pd.Timestamp("2026-05-13")),
            "Y22":    m(pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
            "Q126":   m(pd.Timestamp("2025-12-30"), pd.Timestamp("2026-03-30")),
            "final_NAV": nav_df["nav"].iloc[-1]/1e9}

# Define masks (reusable)
m_NPR = ev["NP_R"] >= 15
m_HL3 = (ev["prior_n_good"] >= 4) & (ev["pa_HL3"] >= 5)
m_S05 = ev["surprise_B_MA"] >= 0.5
m_S10 = ev["surprise_B_MA"] >= 1.0

variants = [
    ("V0_current",     m_NPR & m_HL3,        25),
    ("V5_NPR+S05",     m_NPR & m_S05,        25),
    ("V6_TRIPLE",      m_NPR & m_S05 & m_HL3, 25),
    ("V7_V5_hold35",   m_NPR & m_S05,        35),
    ("V8_V5_hold45",   m_NPR & m_S05,        45),
    ("V9_V5_hold60",   m_NPR & m_S05,        60),
    ("V10_V5_hold75",  m_NPR & m_S05,        75),
    ("V11_V6_hold45",  m_NPR & m_S05 & m_HL3, 45),
    ("V12_V6_hold60",  m_NPR & m_S05 & m_HL3, 60),
    ("V13_SUR10_h60",  m_NPR & m_S10,        60),
]

print("\n[Running 10 variants] ...")
print(f"  {'Variant':<22}{'Hold':>6}{'Sched':>8}{'Trades':>8}{'WR':>7}{'avg_ret':>10}{'CAGR':>9}{'Sh':>6}{'DD':>8}{'Cal':>6}{'Y22':>8}{'Q126':>9}")
print("  " + "-"*115)
results = []
for name, mask, hold in variants:
    r = run_bt(mask, hold=hold)
    if r is None:
        print(f"  {name:<22} {hold:>6} no schedule"); continue
    r["name"] = name; r["hold"] = hold
    results.append(r)
    print(f"  {name:<22}{hold:>6}{r['sched_N']:>8d}{r['trades']:>8d}{r['WR']:>6.1f}%{r['avg_ret']:>+9.2f}%{r['CAGR']:>+8.2f}%{r['Sharpe']:>+5.2f}{r['DD']:>+7.1f}%{r['Calmar']:>+5.2f}{r['Y22']:>+7.1f}%{r['Q126']:>+8.1f}%")

df = pd.DataFrame(results)
df.to_csv("data/surprise_v6_extended_results.csv", index=False)

# Top by Calmar (best risk-adj)
print(f"\n  🏆 TOP 3 by CAGR:")
print(df.nlargest(3, "CAGR")[["name","hold","CAGR","Sharpe","DD","Calmar","WR"]].to_string(index=False, float_format="%.2f"))
print(f"\n  🏆 TOP 3 by SHARPE:")
print(df.nlargest(3, "Sharpe")[["name","hold","CAGR","Sharpe","DD","Calmar","WR"]].to_string(index=False, float_format="%.2f"))
print(f"\n  🏆 TOP 3 by CALMAR:")
print(df.nlargest(3, "Calmar")[["name","hold","CAGR","Sharpe","DD","Calmar","WR"]].to_string(index=False, float_format="%.2f"))

# Walk-forward on winner
best_idx = df["CAGR"].idxmax()
best_name = df.iloc[best_idx]["name"]
best_hold = int(df.iloc[best_idx]["hold"])
best_mask = dict([(n, (m, h)) for n, m, h in variants])[best_name][0]
print(f"\n[Walk-forward] Winner: {best_name} (hold={best_hold})")
windows = [
    ("FULL_14-26",    pd.Timestamp("2014-04-01"), pd.Timestamp("2026-05-13")),
    ("P1_IS_14-18",   pd.Timestamp("2014-01-01"), pd.Timestamp("2018-12-31")),
    ("P2_OOS_19-26",  pd.Timestamp("2019-01-01"), pd.Timestamp("2026-05-13")),
    ("P3_IS_14-20",   pd.Timestamp("2014-01-01"), pd.Timestamp("2020-12-31")),
    ("P4_OOS_21-26",  pd.Timestamp("2021-01-01"), pd.Timestamp("2026-05-13")),
    ("P5_IS_14-22",   pd.Timestamp("2014-01-01"), pd.Timestamp("2022-12-31")),
    ("P6_OOS_23-26",  pd.Timestamp("2023-01-01"), pd.Timestamp("2026-05-13")),
]
print(f"\n  {'Window':<16}{'Trades':>8}{'WR':>7}{'avg':>9}{'CAGR':>9}{'Sh':>6}{'DD':>8}")
print("  " + "-"*60)
for wn, sw, ew in windows:
    r = run_bt(best_mask, hold=best_hold, sw=sw, ew=ew)
    if r is None: continue
    print(f"  {wn:<16}{r['trades']:>8d}{r['WR']:>6.1f}%{r['avg_ret']:>+8.2f}%{r['CAGR']:>+8.2f}%{r['Sharpe']:>+5.2f}{r['DD']:>+7.1f}%")

print("\nSaved: surprise_v6_extended_results.csv")
