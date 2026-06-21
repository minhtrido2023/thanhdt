#!/usr/bin/env python3
"""
validate_lagged_hl3y.py — Full validation of HL_3y filter for LAGGED system

Tests:
  A. Walk-forward IS/OOS — confirm OOS doesn't degrade vs IS
  B. Re-tune CAND_B params under HL_3y (max_pos, pos_pct, hold)
  C. Annual breakdown 2014-2025 — detect lucky-year effect

Uses HL_3y profile (exp decay, half-life 3 years).
Baseline CAND_B: max_pos=12, pos_pct=0.08, hold=25, entry=T+5, NPR≥15%, prior≥4
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, pickle
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
INIT_NAV = 50e9

# ─── Load data ───────────────────────────────────────────────────────────
print("[Setup] Loading shared data ...", flush=True)
with open("data/earnings_px.pkl","rb") as f: px_data = pickle.load(f)
px_data["time"] = pd.to_datetime(px_data["time"])
px_close = px_data.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns")
px_close.index = master_idx
all_dates = np.array(master_idx)

with open("data/lagged_pos_ov.pkl","rb") as f: ov = pickle.load(f)
ov["time"] = pd.to_datetime(ov["time"])
px_open = ov.pivot_table(index="time", columns="ticker", values="Open", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
liq     = ov.pivot_table(index="time", columns="ticker", values="Volume_3M_P50", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)

ev = pd.read_csv("data/earnings_events_classified.csv", parse_dates=["Release_Date"])
ev = ev.sort_values(["ticker","Release_Date"]).reset_index(drop=True)

# ─── Compute HL_3y profile (no lookahead) ────────────────────────────────
print("[Setup] Computing HL_3y profile ...", flush=True)
LN2 = np.log(2)
HALF_LIFE = 3.0  # years
ev["pa_HL3"] = np.nan
ev["prior_n_good"] = 0
for tk, g in ev.groupby("ticker"):
    idxs = g.index.tolist()
    good_history = []  # (date, post_ret)
    for row_idx in idxs:
        row = ev.loc[row_idx]
        cur_date = row["Release_Date"]
        n_good = len(good_history)
        ev.at[row_idx, "prior_n_good"] = n_good
        if n_good >= 1:
            dates = pd.to_datetime([d for d,_ in good_history])
            posts = np.array([p for _,p in good_history])
            age_yrs = (cur_date - dates).days.values / 365.25
            w = np.exp(-LN2 * age_yrs / HALF_LIFE)
            ev.at[row_idx, "pa_HL3"] = (posts * w).sum() / w.sum() if w.sum() > 0 else np.nan
        if pd.notna(row["NP_R"]) and row["NP_R"] >= 15 and pd.notna(row["post_ret"]):
            good_history.append((cur_date, row["post_ret"]))
print(f"  Events: {len(ev):,}  | with prior_n_good>=4: {(ev['prior_n_good']>=4).sum():,}")

def offset_date(ref_dt, offset):
    ref = np.datetime64(ref_dt)
    pos = np.searchsorted(all_dates, ref, side="right") - 1
    if pos < 0: return None
    tgt = pos + offset
    if tgt >= len(all_dates) or tgt < 0: return None
    return pd.Timestamp(all_dates[tgt])

# ─── Backtest function ───────────────────────────────────────────────────
def run_bt(cfg, sw, ew, profile_col="pa_HL3"):
    POST_MIN  = cfg.get("post_min", 8.0)
    N_GOOD    = cfg.get("n_good", 4)
    NPR_MIN   = cfg.get("npr_min", 0.15)
    ENTRY     = cfg.get("entry", 5)
    HOLD      = cfg.get("hold", 25)
    MAX_POS   = cfg.get("max_pos", 12)
    POS_PCT   = cfg.get("pos_pct", 0.08)
    LIQ_MIN   = 2e9
    SLIP_IN, SLIP_OUT, TAX = 0.001, 0.0015, 0.001
    DEPOSIT = 0.01; LIQ_CAP=0.20; MAX_FILL=5

    e = ev[(ev["NP_R"] >= NPR_MIN*100) & (ev["prior_n_good"] >= N_GOOD) & (ev[profile_col] >= POST_MIN)].copy()
    schedule = []
    for _, row in e.iterrows():
        tk = row["ticker"]; rdt = row["Release_Date"]
        if tk not in px_open.columns: continue
        entry_dt = offset_date(rdt, ENTRY)
        exit_dt  = offset_date(rdt, ENTRY + HOLD)
        if entry_dt is None or exit_dt is None: continue
        schedule.append({"ticker":tk, "entry_dt":entry_dt, "exit_dt":exit_dt})
    sched = pd.DataFrame(schedule).sort_values("entry_dt").reset_index(drop=True)
    if len(sched)==0: return None
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
                ret_pct = (fpx/pos["entry_px"]-1)*100
                trades.append({"dt":dt,"ticker":tk,"side":"SELL","ret_pct":ret_pct})
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
                target = POS_PCT * nav_now
                cap = LIQ_CAP * adv * MAX_FILL * fpx
                alloc = min(target, cap)
                if alloc < 1e6 or alloc > cash: continue
                eff_px = fpx*(1+SLIP_IN); shares = alloc/eff_px; cost = shares*eff_px
                cash -= cost
                positions[tk] = {"entry_dt":dt, "exit_dt":en_row["exit_dt"], "shares":shares, "entry_px":fpx}
                trades.append({"dt":dt,"ticker":tk,"side":"BUY","ret_pct":0})
        mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
        nav_history.append({"date":dt,"nav":cash+mtm})

    nav_df = pd.DataFrame(nav_history).set_index("date")
    trades_df = pd.DataFrame(trades)
    sells = trades_df[trades_df["side"]=="SELL"]
    if len(nav_df) < 30: return None
    yrs = (nav_df.index[-1]-nav_df.index[0]).days/365.25
    cagr = (nav_df["nav"].iloc[-1]/nav_df["nav"].iloc[0])**(1/yrs)-1
    rets = nav_df["nav"].pct_change().dropna(); spy = len(rets)/yrs
    sh = rets.mean()/rets.std()*np.sqrt(spy) if rets.std()>0 else 0
    dd = (nav_df["nav"]-nav_df["nav"].cummax())/nav_df["nav"].cummax(); mdd = dd.min()
    cal = cagr/abs(mdd) if mdd<0 else 0
    wr = (sells["ret_pct"]>0).mean()*100 if len(sells)>0 else 0
    return {"CAGR":cagr*100,"Sharpe":sh,"DD":mdd*100,"Calmar":cal,"WR":wr,"N":len(sells),"finalNAV":nav_df["nav"].iloc[-1]/1e9}

# ───────────────────────────────────────────────────────────────────────
# PART A: Walk-forward IS/OOS
# ───────────────────────────────────────────────────────────────────────
print("\n" + "="*100)
print("  PART A: WALK-FORWARD with HL_3y (CAND_B baseline)")
print("="*100)
cand_b = {"post_min":8, "n_good":4, "max_pos":12, "pos_pct":0.08}
windows = [
    ("FULL_10-26",     pd.Timestamp("2010-01-01"), pd.Timestamp("2026-05-13")),
    ("FULL_14-26",     pd.Timestamp("2014-04-01"), pd.Timestamp("2026-05-13")),
    ("P1_IS_10-18",    pd.Timestamp("2010-01-01"), pd.Timestamp("2018-12-31")),
    ("P2_OOS_19-26",   pd.Timestamp("2019-01-01"), pd.Timestamp("2026-05-13")),
    ("P3_IS_10-20",    pd.Timestamp("2010-01-01"), pd.Timestamp("2020-12-31")),
    ("P4_OOS_21-26",   pd.Timestamp("2021-01-01"), pd.Timestamp("2026-05-13")),
    ("P5_IS_10-22",    pd.Timestamp("2010-01-01"), pd.Timestamp("2022-12-31")),
    ("P6_OOS_23-26",   pd.Timestamp("2023-01-01"), pd.Timestamp("2026-05-13")),
]
print(f"\n  {'Window':<18}{'CAGR':>10}{'Sharpe':>10}{'DD':>10}{'Calmar':>10}{'WR':>8}{'N':>6}")
print("  " + "-"*72)
wf_results = []
for wn, sw, ew in windows:
    r = run_bt(cand_b, sw, ew)
    if r is None: continue
    r["window"] = wn
    wf_results.append(r)
    print(f"  {wn:<18}{r['CAGR']:>+9.2f}%{r['Sharpe']:>+10.2f}{r['DD']:>+9.2f}%{r['Calmar']:>+10.2f}{r['WR']:>+7.1f}%{r['N']:>6d}")

# IS vs OOS comparison
print(f"\n  IS vs OOS deltas:")
splits = [("18/19","P1_IS_10-18","P2_OOS_19-26"),
          ("20/21","P3_IS_10-20","P4_OOS_21-26"),
          ("22/23","P5_IS_10-22","P6_OOS_23-26")]
wf_df = pd.DataFrame(wf_results).set_index("window")
for nm, isn, oosn in splits:
    if isn in wf_df.index and oosn in wf_df.index:
        d = wf_df.loc[oosn, "CAGR"] - wf_df.loc[isn, "CAGR"]
        print(f"    {nm}: IS_CAGR={wf_df.loc[isn,'CAGR']:+.2f}%  →  OOS_CAGR={wf_df.loc[oosn,'CAGR']:+.2f}%  Δ={d:+.2f}pp")

# ───────────────────────────────────────────────────────────────────────
# PART B: Re-tune CAND_B params under HL_3y
# ───────────────────────────────────────────────────────────────────────
print("\n" + "="*100)
print("  PART B: PARAM TUNE under HL_3y (FULL 2014-2026)")
print("="*100)
tune_configs = [
    ("BASELINE_b",    {"max_pos":12, "pos_pct":0.08}),
    # max_pos
    ("max_pos_10",    {"max_pos":10, "pos_pct":0.08}),
    ("max_pos_14",    {"max_pos":14, "pos_pct":0.08}),
    ("max_pos_16",    {"max_pos":16, "pos_pct":0.08}),
    # pos_pct
    ("pos_pct_0.07",  {"max_pos":12, "pos_pct":0.07}),
    ("pos_pct_0.10",  {"max_pos":12, "pos_pct":0.10}),
    ("pos_pct_0.12",  {"max_pos":12, "pos_pct":0.12}),
    # hold
    ("hold_20",       {"max_pos":12, "pos_pct":0.08, "hold":20}),
    ("hold_30",       {"max_pos":12, "pos_pct":0.08, "hold":30}),
    # combos
    ("max14_pos07",   {"max_pos":14, "pos_pct":0.07}),
    ("max14_pos10",   {"max_pos":14, "pos_pct":0.10}),
    ("max16_pos07",   {"max_pos":16, "pos_pct":0.07}),
    ("max16_pos06",   {"max_pos":16, "pos_pct":0.06}),
    # post_min variations
    ("post_min_5",    {"max_pos":12, "pos_pct":0.08, "post_min":5}),
    ("post_min_10",   {"max_pos":12, "pos_pct":0.08, "post_min":10}),
]
print(f"\n  {'Config':<18}{'CAGR':>10}{'Sharpe':>10}{'DD':>10}{'Calmar':>10}{'WR':>8}{'N':>6}")
print("  " + "-"*72)
tune_results = []
for nm, cfg in tune_configs:
    cfg_full = {**cand_b, **cfg}
    r = run_bt(cfg_full, pd.Timestamp("2014-04-01"), pd.Timestamp("2026-05-13"))
    if r is None: continue
    r["name"] = nm
    tune_results.append(r)
    print(f"  {nm:<18}{r['CAGR']:>+9.2f}%{r['Sharpe']:>+10.2f}{r['DD']:>+9.2f}%{r['Calmar']:>+10.2f}{r['WR']:>+7.1f}%{r['N']:>6d}")

# Top by Calmar (best risk-adj)
tune_df = pd.DataFrame(tune_results)
print(f"\n  TOP 5 by CALMAR:")
print(tune_df.nlargest(5, "Calmar")[["name","CAGR","Sharpe","DD","Calmar","WR","N"]].to_string(index=False, float_format="%.2f"))
print(f"\n  TOP 5 by CAGR:")
print(tune_df.nlargest(5, "CAGR")[["name","CAGR","Sharpe","DD","Calmar","WR","N"]].to_string(index=False, float_format="%.2f"))

# ───────────────────────────────────────────────────────────────────────
# PART C: Annual breakdown
# ───────────────────────────────────────────────────────────────────────
print("\n" + "="*100)
print("  PART C: ANNUAL BREAKDOWN (CAND_B with HL_3y)")
print("="*100)
print(f"\n  {'Year':<6}{'CAGR':>10}{'Sharpe':>10}{'DD':>10}{'WR':>8}{'N':>6}")
print("  " + "-"*48)
annual_results = []
for yr in range(2014, 2026):
    r = run_bt(cand_b, pd.Timestamp(f"{yr}-01-01"), pd.Timestamp(f"{yr}-12-31"))
    if r is None: continue
    r["year"] = yr
    annual_results.append(r)
    print(f"  {yr:<6}{r['CAGR']:>+9.2f}%{r['Sharpe']:>+10.2f}{r['DD']:>+9.2f}%{r['WR']:>+7.1f}%{r['N']:>6d}")

an_df = pd.DataFrame(annual_results)
print(f"\n  Avg annual CAGR: {an_df['CAGR'].mean():+.2f}%  | Std: {an_df['CAGR'].std():.2f}")
print(f"  Years positive: {(an_df['CAGR']>0).sum()}/{len(an_df)}  | Worst year: {an_df.loc[an_df['CAGR'].idxmin(),'year']} {an_df['CAGR'].min():+.2f}%")
print(f"  Best year: {an_df.loc[an_df['CAGR'].idxmax(),'year']} {an_df['CAGR'].max():+.2f}%")

# Save
pd.DataFrame(wf_results).to_csv("data/validate_hl3y_walkforward.csv", index=False)
pd.DataFrame(tune_results).to_csv("data/validate_hl3y_tune.csv", index=False)
pd.DataFrame(annual_results).to_csv("data/validate_hl3y_annual.csv", index=False)
print("\nSaved: validate_hl3y_walkforward.csv, validate_hl3y_tune.csv, validate_hl3y_annual.csv")
