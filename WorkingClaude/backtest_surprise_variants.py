#!/usr/bin/env python3
"""
backtest_surprise_variants.py — Surprise-based LAGGED variants

Tests:
  (A) 6 variants comparing surprise vs NP_R thresholds:
      V0  CURRENT_HL3y       : NP_R ≥ 15 + HL_3y ≥ 5%        (baseline)
      V1  SURPRISE_05        : surprise_B_MA ≥ 0.5
      V2  SURPRISE_10        : surprise_B_MA ≥ 1.0  (strict)
      V3  SURPRISE_05_HL3    : surprise_B_MA ≥ 0.5 + HL_3y ≥ 5%
      V4  SURPRISE_10_HL3    : surprise_B_MA ≥ 1.0 + HL_3y ≥ 5%
      V5  SUR+NPR_combined   : surprise_B_MA ≥ 0.5 + NP_R ≥ 15

  (B) Walk-forward IS/OOS on winner

  (C) Extended post_ret T+5→T+60 analysis (drift duration)

Surprise formula: (NP_P0 - mean(NP_P1..P4)) / max(|mean|, 1e9 floor)
Absolute thresholds (not percentile) → no lookahead from quintile rank.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, pickle, subprocess, tempfile
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from io import StringIO
import pandas as pd, numpy as np

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
PROJECT = "lithe-record-440915-m9"
BQ = r"bq"
INIT_NAV = 50e9

def bq_query(sql):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        cmd = f'type "{tmp}" | "{BQ}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=10000000'
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800, shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    if r.returncode != 0: raise RuntimeError(r.stderr[:500])
    return pd.read_csv(StringIO(r.stdout.strip()))

print("="*100)
print("  SURPRISE-BASED LAGGED VARIANTS — (A) Backtest + (B) Walk-forward + (C) T+60")
print("="*100)

# ─── Load data ───────────────────────────────────────────────────────────
print("\n[Setup] Loading price + financial caches ...")
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

# Surprise data
with open("data/earnings_surprise_data.pkl","rb") as f: fin = pickle.load(f)
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"])
FLOOR = 1e9
fin["exp_B_MA"] = fin[["NP_P1","NP_P2","NP_P3","NP_P4"]].mean(axis=1)
fin["surprise_B_MA"] = (fin["NP_P0"] - fin["exp_B_MA"]) / np.maximum(np.abs(fin["exp_B_MA"]), FLOOR)
fin["surprise_B_MA"] = fin["surprise_B_MA"].clip(-5, 5)
print(f"  Events with B_MA surprise: {fin['surprise_B_MA'].notna().sum():,}")

# Existing classified events (has pre/rel/post returns)
ev_class = pd.read_csv("data/earnings_events_classified.csv", parse_dates=["Release_Date"])
ev_class = ev_class.sort_values(["ticker","Release_Date"]).reset_index(drop=True)
print(f"  Classified events: {len(ev_class):,}")

# Merge surprise into classified
ev = ev_class.merge(
    fin[["ticker","quarter","Release_Date","surprise_B_MA"]],
    on=["ticker","quarter","Release_Date"], how="left")
print(f"  Merged: {len(ev):,}, with surprise: {ev['surprise_B_MA'].notna().sum():,}")

# ─── (C) Compute post_ret_60d (T+5 → T+60) ──────────────────────────────
print("\n[C] Computing extended T+5→T+60 returns ...")
def get_offset(tk, ref_dt, offset):
    if tk not in px_close.columns: return np.nan
    ref = np.datetime64(ref_dt)
    pos = np.searchsorted(all_dates, ref, side="right") - 1
    if pos < 0: return np.nan
    tgt = pos + offset
    if tgt < 0 or tgt >= len(all_dates): return np.nan
    return px_close.iloc[tgt][tk]

ev["px_p5"] = np.nan
ev["px_p30"] = np.nan
ev["px_p60"] = np.nan
ev["px_p90"] = np.nan
for i, row in ev.iterrows():
    tk = row["ticker"]; rdt = row["Release_Date"]
    if tk not in px_close.columns: continue
    p5 = get_offset(tk, rdt, +5); p30 = get_offset(tk, rdt, +30)
    p60 = get_offset(tk, rdt, +60); p90 = get_offset(tk, rdt, +90)
    ev.at[i, "px_p5"] = p5
    ev.at[i, "px_p30"] = p30
    ev.at[i, "px_p60"] = p60
    ev.at[i, "px_p90"] = p90
    if i % 10000 == 0: print(f"  {i}/{len(ev)} ...", flush=True)
ev["post_ret_30"] = (ev["px_p30"] / ev["px_p5"] - 1) * 100
ev["post_ret_60"] = (ev["px_p60"] / ev["px_p5"] - 1) * 100
ev["post_ret_90"] = (ev["px_p90"] / ev["px_p5"] - 1) * 100

# Drift duration analysis
print("\n  Drift duration by surprise level:")
print(f"  {'Surprise level':<24}{'N':>8}{'ret_30':>10}{'ret_60':>10}{'ret_90':>10}")
print("  " + "-"*62)
for label, mask in [
    ("Surprise ≥ 0.5", ev["surprise_B_MA"] >= 0.5),
    ("Surprise ≥ 1.0", ev["surprise_B_MA"] >= 1.0),
    ("Surprise ≥ 2.0", ev["surprise_B_MA"] >= 2.0),
    ("Surprise < 0 (neg)", ev["surprise_B_MA"] < 0),
    ("NP_R ≥ 15", ev["NP_R"] >= 15),
    ("All events", ev["surprise_B_MA"].notna()),
]:
    sub = ev[mask]
    if len(sub) < 100: continue
    print(f"  {label:<24}{len(sub):>8d}{sub['post_ret_30'].mean():>+9.2f}%{sub['post_ret_60'].mean():>+9.2f}%{sub['post_ret_90'].mean():>+9.2f}%")

# ─── (B) Compute HL_3y profile (no lookahead) ───────────────────────────
print("\n[Profile] Computing HL_3y rolling ...")
ev = ev.sort_values(["ticker","Release_Date"]).reset_index(drop=True)
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

# ─── (A) Backtest variants ───────────────────────────────────────────────
print("\n[A] Setting up backtest infrastructure ...")

def offset_date(ref_dt, offset):
    ref = np.datetime64(ref_dt); pos = np.searchsorted(all_dates, ref, side="right") - 1
    if pos < 0: return None
    tgt = pos + offset
    if tgt >= len(all_dates) or tgt < 0: return None
    return pd.Timestamp(all_dates[tgt])

def run_bt(event_filter_mask, sw=pd.Timestamp("2014-04-01"), ew=pd.Timestamp("2026-05-13"),
           hold=25, entry_offset=5, max_pos=12, pos_pct=0.08):
    LIQ_MIN=2e9; SLIP_IN, SLIP_OUT, TAX = 0.001, 0.0015, 0.001
    DEPOSIT=0.01; LIQ_CAP=0.20; MAX_FILL=5

    e = ev[event_filter_mask].copy()
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
                trades.append({"dt":dt,"ticker":tk,"side":"SELL","ret_pct":(fpx/pos["entry_px"]-1)*100})
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
                trades.append({"dt":dt,"ticker":tk,"side":"BUY","ret_pct":0})
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

# Define variants
print("\n[A] Running 6 variants ...")
variants = [
    ("V0_CURRENT_HL3y",      (ev["NP_R"] >= 15) & (ev["prior_n_good"] >= 4) & (ev["pa_HL3"] >= 5)),
    ("V1_SURPRISE_05",       (ev["surprise_B_MA"] >= 0.5)),
    ("V2_SURPRISE_10",       (ev["surprise_B_MA"] >= 1.0)),
    ("V3_SURPRISE_05_HL3",   (ev["surprise_B_MA"] >= 0.5) & (ev["prior_n_good"] >= 4) & (ev["pa_HL3"] >= 5)),
    ("V4_SURPRISE_10_HL3",   (ev["surprise_B_MA"] >= 1.0) & (ev["prior_n_good"] >= 4) & (ev["pa_HL3"] >= 5)),
    ("V5_SUR_NPR_combined",  (ev["surprise_B_MA"] >= 0.5) & (ev["NP_R"] >= 15)),
]
print(f"  {'Variant':<24}{'N_sched':>10}{'trades':>8}{'WR':>7}{'avg_ret':>10}{'CAGR':>9}{'Sh':>7}{'DD':>8}{'Cal':>7}{'OOS24':>9}{'Y22':>9}{'Q126':>9}")
print("  " + "-"*125)
results = []
for name, mask in variants:
    r = run_bt(mask)
    if r is None:
        print(f"  {name:<24} no schedule")
        continue
    r["name"] = name
    results.append(r)
    print(f"  {name:<24}{r['sched_N']:>10d}{r['trades']:>8d}{r['WR']:>6.1f}%{r['avg_ret']:>+9.2f}%{r['CAGR']:>+8.2f}%{r['Sharpe']:>+7.2f}{r['DD']:>+7.1f}%{r['Calmar']:>+7.2f}{r['OOS_24']:>+8.1f}%{r['Y22']:>+8.1f}%{r['Q126']:>+8.1f}%")

results_df = pd.DataFrame(results)
results_df.to_csv("data/surprise_variants_results.csv", index=False)

# Best by CAGR
if len(results_df) > 0:
    best_idx = results_df["CAGR"].idxmax()
    best = results_df.iloc[best_idx]
    print(f"\n  🏆 Best CAGR: {best['name']} → {best['CAGR']:+.2f}% / Sh {best['Sharpe']:+.2f} / DD {best['DD']:+.2f}%")

# ─── (B) Walk-forward on winner ──────────────────────────────────────────
if len(results_df) > 0:
    best_name = results_df.iloc[results_df["CAGR"].idxmax()]["name"]
    best_mask = dict(variants)[best_name]
    print(f"\n[B] Walk-forward IS/OOS for winner: {best_name}")
    windows = [
        ("FULL_14-26",    pd.Timestamp("2014-04-01"), pd.Timestamp("2026-05-13")),
        ("P1_IS_14-18",   pd.Timestamp("2014-01-01"), pd.Timestamp("2018-12-31")),
        ("P2_OOS_19-26",  pd.Timestamp("2019-01-01"), pd.Timestamp("2026-05-13")),
        ("P3_IS_14-20",   pd.Timestamp("2014-01-01"), pd.Timestamp("2020-12-31")),
        ("P4_OOS_21-26",  pd.Timestamp("2021-01-01"), pd.Timestamp("2026-05-13")),
        ("P5_IS_14-22",   pd.Timestamp("2014-01-01"), pd.Timestamp("2022-12-31")),
        ("P6_OOS_23-26",  pd.Timestamp("2023-01-01"), pd.Timestamp("2026-05-13")),
    ]
    print(f"\n  {'Window':<16}{'trades':>8}{'WR':>7}{'avg_ret':>10}{'CAGR':>9}{'Sh':>7}{'DD':>8}")
    print("  " + "-"*65)
    for wn, sw, ew in windows:
        r = run_bt(best_mask, sw, ew)
        if r is None: continue
        print(f"  {wn:<16}{r['trades']:>8d}{r['WR']:>6.1f}%{r['avg_ret']:>+9.2f}%{r['CAGR']:>+8.2f}%{r['Sharpe']:>+7.2f}{r['DD']:>+7.1f}%")

print("\nSaved: surprise_variants_results.csv")
