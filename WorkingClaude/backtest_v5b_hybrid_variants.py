#!/usr/bin/env python3
"""
backtest_v5b_hybrid_variants.py — V5b + hybrid filter variants

Tests:
  V0  CURRENT_HL3y         : NP_R≥15 + HL_3y≥5
  V5  SURPRISE_05          : NP_R≥15 + surprise≥0.5 (current candidate, mild overfit)
  V5b SURPRISE_03          : NP_R≥15 + surprise≥0.3 (less overfit, robust)
  V5c SURPRISE_03_NPR_only : surprise≥0.3 alone (no NP_R)
  H1  HYBRID_AND           : NP_R≥15 AND HL_3y≥5 AND surprise≥0.3
  H2  HYBRID_AND_strict    : NP_R≥15 AND HL_3y≥5 AND surprise≥0.5
  H3  V5b + HL_3y          : NP_R≥15 AND HL_3y≥5 AND surprise≥0.3 (same as H1)
  H4  HL_3y + surprise≥0.3 : HL_3y≥5 AND surprise≥0.3 (no NP_R)

Hypothesis: V5b should have smaller IS-OOS gap than V5. Hybrid may combine
durability of HL_3y with surprise alpha.
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
print("  V5b + HYBRID VARIANTS")
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

# HL_3y profile
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

print(f"  Events: {len(ev):,} | Surprise: {ev['surprise_B_MA'].notna().sum():,} | HL_3y: {ev['pa_HL3'].notna().sum():,}")

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
            "OOS_24":m(pd.Timestamp("2024-01-01"), pd.Timestamp("2026-05-13")),
            "IS_14_18":m(pd.Timestamp("2014-04-01"), pd.Timestamp("2018-12-31")),
            "Y22":m(pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
            "Y25":m(pd.Timestamp("2025-01-01"), pd.Timestamp("2025-12-31")),
            "final_NAV":nav_df["nav"].iloc[-1]/1e9}

# Define masks
m_NPR  = ev["NP_R"] >= 15
m_HL3  = (ev["prior_n_good"] >= 4) & (ev["pa_HL3"] >= 5)
m_S03  = ev["surprise_B_MA"] >= 0.3
m_S05  = ev["surprise_B_MA"] >= 0.5

variants = [
    ("V0_CURRENT_HL3",      m_NPR & m_HL3,                          "NP_R≥15 + HL_3y≥5"),
    ("V5_NPR+S05",          m_NPR & m_S05,                          "NP_R≥15 + sur≥0.5"),
    ("V5b_NPR+S03",         m_NPR & m_S03,                          "NP_R≥15 + sur≥0.3"),
    ("V5c_S03_alone",       m_S03,                                  "surprise≥0.3 alone"),
    ("H1_NPR+HL3+S03",      m_NPR & m_HL3 & m_S03,                  "NP_R + HL_3y + sur≥0.3"),
    ("H2_NPR+HL3+S05",      m_NPR & m_HL3 & m_S05,                  "NP_R + HL_3y + sur≥0.5 (strict)"),
    ("H4_HL3+S03",          m_HL3 & m_S03,                          "HL_3y + sur≥0.3"),
]

print(f"\n[Running {len(variants)} variants]\n")
print(f"  {'Variant':<22}{'N_sched':>9}{'trades':>8}{'WR':>7}{'avg_ret':>10}{'CAGR':>9}{'Sh':>6}{'DD':>8}{'Cal':>6}{'IS_14-18':>10}{'OOS_24+':>10}{'Y22':>9}{'Y25':>9}")
print("  " + "-"*125)
results = []
for name, mask, desc in variants:
    r = run_bt(mask)
    if r is None: continue
    r["name"] = name; r["desc"] = desc
    results.append(r)
    print(f"  {name:<22}{r['sched_N']:>9d}{r['trades']:>8d}{r['WR']:>6.1f}%{r['avg_ret']:>+9.2f}%{r['CAGR']:>+8.2f}%{r['Sharpe']:>+5.2f}{r['DD']:>+7.1f}%{r['Calmar']:>+5.2f}{r['IS_14_18']:>+9.2f}%{r['OOS_24']:>+9.2f}%{r['Y22']:>+8.1f}%{r['Y25']:>+8.1f}%")

df = pd.DataFrame(results)
df.to_csv("v5b_hybrid_results.csv", index=False)

# IS-OOS gap analysis (key metric)
print(f"\n  Diagnostic: IS_14-18 vs OOS_24+ gap (large gap = overfit risk):")
print(f"  {'Variant':<22}{'IS_CAGR':>10}{'OOS_CAGR':>10}{'GAP':>9}")
for _, r in df.sort_values("OOS_24", ascending=False).iterrows():
    gap = r['OOS_24'] - r['IS_14_18']
    print(f"  {r['name']:<22}{r['IS_14_18']:>+9.2f}%{r['OOS_24']:>+9.2f}%{gap:>+8.2f}pp")

# Best by Calmar (risk-adj)
print(f"\n  🏆 TOP 3 by CAGR:")
print(df.nlargest(3, "CAGR")[["name","CAGR","Sharpe","DD","Calmar","WR","OOS_24","Y22"]].to_string(index=False, float_format="%.2f"))
print(f"\n  🏆 TOP 3 by Calmar:")
print(df.nlargest(3, "Calmar")[["name","CAGR","Sharpe","DD","Calmar","WR","OOS_24","Y22"]].to_string(index=False, float_format="%.2f"))
print(f"\n  🏆 TOP 3 by OOS_24:")
print(df.nlargest(3, "OOS_24")[["name","CAGR","Sharpe","DD","Calmar","WR","OOS_24","Y22"]].to_string(index=False, float_format="%.2f"))

# Walk-forward winner by OOS (most important for forward-looking deploy)
best_idx = df["OOS_24"].idxmax()
best_name = df.iloc[best_idx]["name"]
best_mask = dict([(n, m) for n, m, _ in variants])[best_name]
print(f"\n[Walk-forward] Winner by OOS_24: {best_name}")
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
for wn, sw, ew in windows:
    r = run_bt(best_mask, sw=sw, ew=ew)
    if r is None: continue
    print(f"  {wn:<16}{r['trades']:>8d}{r['WR']:>6.1f}%{r['avg_ret']:>+8.2f}%{r['CAGR']:>+8.2f}%{r['Sharpe']:>+5.2f}{r['DD']:>+7.1f}%")

print("\nSaved: v5b_hybrid_results.csv")
