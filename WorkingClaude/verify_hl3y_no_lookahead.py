#!/usr/bin/env python3
"""
verify_hl3y_no_lookahead.py — Rigorous lookahead verification for HL_3y

Tests:
  CONTROL    : HL_3y profile + T+5 entry (current/proposed config)
  STRICT_BUF : HL_3y profile with 45-day buffer (skip events not yet matured) + T+5
  ENTRY_T45  : HL_3y profile + T+45 entry (delay so all prior events matured before peek)
  STRICT+T45 : both safeguards combined (most paranoid)
  EQUAL_baseline : for sanity reference

Pass criteria: STRICT_BUF and ENTRY_T45 CAGR should be within ~1-2pp of CONTROL.
              If they drop >3pp → lookahead is contributing meaningfully.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, pickle
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
INIT_NAV = 50e9

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

# ─── Compute 3 profile variants ──────────────────────────────────────────
print("[Setup] Computing profiles (EQUAL, HL_3y, HL_3y_STRICT) ...", flush=True)
LN2 = np.log(2); HL = 3.0
BUFFER_DAYS = 45  # post window ~42 cal days, +3 day safety
ev["pa_EQUAL"] = np.nan
ev["pa_HL3"] = np.nan
ev["pa_HL3_STRICT"] = np.nan
ev["prior_n_good"] = 0
ev["prior_n_good_STRICT"] = 0

for tk, g in ev.groupby("ticker"):
    idxs = g.index.tolist()
    good_history = []  # all prior good events
    for row_idx in idxs:
        row = ev.loc[row_idx]
        cur_date = row["Release_Date"]
        # FULL: all prior events (current profile)
        n_good = len(good_history)
        ev.at[row_idx, "prior_n_good"] = n_good
        if n_good >= 1:
            dates = pd.to_datetime([d for d,_ in good_history])
            posts = np.array([p for _,p in good_history])
            age_yrs = (cur_date - dates).days.values / 365.25
            w_eq = np.ones(len(posts))
            w_hl = np.exp(-LN2 * age_yrs / HL)
            ev.at[row_idx, "pa_EQUAL"] = (posts * w_eq).sum() / w_eq.sum()
            ev.at[row_idx, "pa_HL3"]   = (posts * w_hl).sum() / w_hl.sum()
        # STRICT: only events fully matured (T_i - T_j >= 45 calendar days)
        strict_history = [(d,p) for d,p in good_history
                          if (cur_date - d).days >= BUFFER_DAYS]
        n_strict = len(strict_history)
        ev.at[row_idx, "prior_n_good_STRICT"] = n_strict
        if n_strict >= 1:
            dates_s = pd.to_datetime([d for d,_ in strict_history])
            posts_s = np.array([p for _,p in strict_history])
            age_yrs_s = (cur_date - dates_s).days.values / 365.25
            w_s = np.exp(-LN2 * age_yrs_s / HL)
            ev.at[row_idx, "pa_HL3_STRICT"] = (posts_s * w_s).sum() / w_s.sum()
        # update history
        if pd.notna(row["NP_R"]) and row["NP_R"] >= 15 and pd.notna(row["post_ret"]):
            good_history.append((cur_date, row["post_ret"]))

# Diagnostic: how many events affected by strict filter?
both_have = (ev["prior_n_good"] >= 4) & (ev["prior_n_good_STRICT"] >= 4)
diff_count = (ev["prior_n_good"] != ev["prior_n_good_STRICT"]).sum()
both_qualify_h = ((ev["prior_n_good"] >= 4) & (ev["pa_HL3"] >= 8)).sum()
both_qualify_s = ((ev["prior_n_good_STRICT"] >= 4) & (ev["pa_HL3_STRICT"] >= 8)).sum()
print(f"  Events with prior_n_good differs strict-vs-full: {diff_count:,}")
print(f"  Qualify (HL_3y ≥8 + n≥4): {both_qualify_h:,}")
print(f"  Qualify (STRICT ≥8 + n_strict≥4): {both_qualify_s:,}  → Δ {both_qualify_s-both_qualify_h:+d}")

# ─── Backtest helper ─────────────────────────────────────────────────────
def offset_date(ref_dt, offset):
    ref = np.datetime64(ref_dt)
    pos = np.searchsorted(all_dates, ref, side="right") - 1
    if pos < 0: return None
    tgt = pos + offset
    if tgt >= len(all_dates) or tgt < 0: return None
    return pd.Timestamp(all_dates[tgt])

def run_bt(profile_col, n_good_col, entry_offset, hold_days=25,
           post_min=8, n_min=4, max_pos=12, pos_pct=0.08,
           sw=pd.Timestamp("2014-04-01"), ew=pd.Timestamp("2026-05-13")):
    NPR_MIN=0.15; LIQ_MIN=2e9
    SLIP_IN, SLIP_OUT, TAX = 0.001, 0.0015, 0.001
    DEPOSIT=0.01; LIQ_CAP=0.20; MAX_FILL=5

    e = ev[(ev["NP_R"] >= NPR_MIN*100) & (ev[n_good_col] >= n_min) & (ev[profile_col] >= post_min)].copy()
    schedule = []
    for _, row in e.iterrows():
        tk = row["ticker"]; rdt = row["Release_Date"]
        if tk not in px_open.columns: continue
        entry_dt = offset_date(rdt, entry_offset)
        exit_dt  = offset_date(rdt, entry_offset + hold_days)
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

    # subperiods
    def m(start, end):
        s = nav_df["nav"][(nav_df.index>=start) & (nav_df.index<=end)]
        if len(s) < 30: return None
        y = (s.index[-1]-s.index[0]).days/365.25
        c = (s.iloc[-1]/s.iloc[0])**(1/y)-1
        return c*100
    return {"CAGR":cagr*100,"Sharpe":sh,"DD":mdd*100,"Calmar":cal,"WR":wr,"N":len(sells),
            "finalNAV":nav_df["nav"].iloc[-1]/1e9,
            "OOS":m(pd.Timestamp("2024-01-01"), pd.Timestamp("2026-05-13")),
            "Y22":m(pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
            "Q126":m(pd.Timestamp("2025-12-30"), pd.Timestamp("2026-03-30"))}

# ─── Run 5 variants ──────────────────────────────────────────────────────
print("\n[Test] Running 5 variants ...")
configs = [
    ("EQUAL_T5",        "pa_EQUAL",       "prior_n_good",       5),
    ("HL3_T5_CONTROL",  "pa_HL3",         "prior_n_good",       5),
    ("HL3_STRICT_T5",   "pa_HL3_STRICT",  "prior_n_good_STRICT",5),
    ("HL3_T45",         "pa_HL3",         "prior_n_good",      45),
    ("HL3_STRICT_T45",  "pa_HL3_STRICT",  "prior_n_good_STRICT",45),
]
results = []
print(f"\n  {'Config':<22}{'CAGR':>10}{'Sharpe':>10}{'DD':>10}{'Calmar':>10}{'OOS':>10}{'Y22':>9}{'Q126':>9}{'N':>5}")
print("  " + "-"*94)
for nm, pcol, ncol, eoff in configs:
    r = run_bt(pcol, ncol, eoff)
    if r is None:
        print(f"  {nm:<22} no schedule"); continue
    r["name"] = nm
    results.append(r)
    print(f"  {nm:<22}{r['CAGR']:>+9.2f}%{r['Sharpe']:>+10.2f}{r['DD']:>+9.2f}%{r['Calmar']:>+10.2f}"
          f"{r['OOS']:>+9.2f}%{r['Y22']:>+8.2f}%{r['Q126']:>+8.2f}%{r['N']:>5d}")

df = pd.DataFrame(results)
df.to_csv("data/verify_hl3y_results.csv", index=False)

# ─── Δ analysis ──────────────────────────────────────────────────────────
control = df[df["name"]=="HL3_T5_CONTROL"].iloc[0]
print("\n" + "="*94)
print("  Δ CAGR vs HL3_T5_CONTROL (CAGR delta — if STRICT/T45 << CONTROL → lookahead suspected)")
print("="*94)
for _, r in df.iterrows():
    nm = r["name"]
    d = r["CAGR"] - control["CAGR"]
    flag = "✓ clean" if abs(d) < 1.5 or nm == "HL3_T5_CONTROL" else ("⚠️ moderate" if abs(d) < 3 else "❌ SUSPECT")
    print(f"  {nm:<22}{d:>+8.2f}pp  {flag}")
print("\nSaved: verify_hl3y_results.csv")
