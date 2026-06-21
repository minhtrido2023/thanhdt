#!/usr/bin/env python3
"""
test_lagged_timedecay.py — Time-decay variants for LAGGED universe filter

Problem: current filter uses equal-weighted mean of post_ret across ALL prior good events.
A ticker with strong alpha 5+ years ago + weak alpha recent → falsely qualifies.

Test 8 variants:
  EQUAL       : baseline (current production)
  EXP_HL_2y   : exponential decay, half-life 2 years
  EXP_HL_3y   : exponential decay, half-life 3 years ★ user pick
  EXP_HL_4y   : exponential decay, half-life 4 years
  ROLL_N12    : rolling window, last 12 good events
  ROLL_N16    : rolling window, last 16 good events
  TIME_4y     : time window, only events in last 4 years
  TREND       : EQUAL + recent_4_avg ≥ 0.7 × prior_4_avg

Backtest each on CAND_B config (max_pos=12, pos_pct=0.08, hold=25d, T+5 entry)
Period: 2010-2026. Init: 50B.
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

print("="*100)
print("  LAGGED PROFILE TIME-DECAY VARIANT TEST")
print("="*100)

# ─── 1. Load data ────────────────────────────────────────────────────────
print("\n[1] Loading shared data ...")
with open("earnings_px.pkl","rb") as f: px_data = pickle.load(f)
px_data["time"] = pd.to_datetime(px_data["time"])
px_close = px_data.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns")
px_close.index = master_idx
all_dates = np.array(master_idx)

with open("lagged_pos_ov.pkl","rb") as f: ov = pickle.load(f)
ov["time"] = pd.to_datetime(ov["time"])
px_open = ov.pivot_table(index="time", columns="ticker", values="Open", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
liq     = ov.pivot_table(index="time", columns="ticker", values="Volume_3M_P50", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)

ev = pd.read_csv("earnings_events_classified.csv", parse_dates=["Release_Date"])
ev = ev.sort_values(["ticker","Release_Date"]).reset_index(drop=True)
print(f"  Events: {len(ev):,}  | Tickers: {ev['ticker'].nunique()}")

# ─── 2. Compute ALL variant profiles in one pass ─────────────────────────
print("\n[2] Computing 8 profile variants per event (no lookahead) ...")
# Add empty cols
for c in ["pa_EQUAL","pa_EXP2","pa_EXP3","pa_EXP4","pa_ROLL12","pa_ROLL16","pa_TIME4","pa_TREND_OK"]:
    ev[c] = np.nan
ev["prior_n_good"] = 0

LN2 = np.log(2)

for tk, g in ev.groupby("ticker"):
    idxs = g.index.tolist()
    # accumulator: list of (event_date, post_ret) for good events
    good_history = []
    for i, row_idx in enumerate(idxs):
        row = ev.loc[row_idx]
        cur_date = row["Release_Date"]
        n_good = len(good_history)
        ev.at[row_idx, "prior_n_good"] = n_good

        if n_good >= 1:
            dates = np.array([d for d,_ in good_history])
            posts = np.array([p for _,p in good_history])
            age_yrs = (cur_date - pd.to_datetime(dates)).days.values / 365.25  # numpy days
            # EQUAL
            ev.at[row_idx, "pa_EQUAL"] = posts.mean()
            # EXP variants (half-life)
            for hl, col in [(2, "pa_EXP2"), (3, "pa_EXP3"), (4, "pa_EXP4")]:
                w = np.exp(-LN2 * age_yrs / hl)
                ev.at[row_idx, col] = (posts * w).sum() / w.sum() if w.sum() > 0 else np.nan
            # ROLL N
            for n, col in [(12, "pa_ROLL12"), (16, "pa_ROLL16")]:
                if n_good >= 4:
                    last = posts[-n:]
                    ev.at[row_idx, col] = last.mean()
            # TIME 4y
            mask4 = age_yrs <= 4
            if mask4.sum() >= 4:
                ev.at[row_idx, "pa_TIME4"] = posts[mask4].mean()
            # TREND: recent 4 avg vs prior 4 avg
            if n_good >= 8:
                recent4 = posts[-4:].mean()
                prior4 = posts[-8:-4].mean()
                ev.at[row_idx, "pa_TREND_OK"] = 1 if (recent4 >= prior4 * 0.7) else 0

        # update accumulator with current event
        if pd.notna(row["NP_R"]) and row["NP_R"] >= 15 and pd.notna(row["post_ret"]):
            good_history.append((cur_date, row["post_ret"]))

print(f"  Done. Sample distribution at threshold 8% (with prior_n_good >= 4):")
sub = ev[ev["prior_n_good"] >= 4]
for col in ["pa_EQUAL","pa_EXP2","pa_EXP3","pa_EXP4","pa_ROLL12","pa_ROLL16","pa_TIME4"]:
    n_qual = (sub[col] >= 8).sum()
    pct = n_qual / len(sub) * 100
    print(f"    {col:<12}: median={sub[col].median():+5.2f}%  | %≥8%: {pct:>5.1f}%  ({n_qual:>5} events)")

# ─── 3. Backtest helper ──────────────────────────────────────────────────
def offset_date(ref_dt, offset):
    ref = np.datetime64(ref_dt)
    pos = np.searchsorted(all_dates, ref, side="right") - 1
    if pos < 0: return None
    tgt = pos + offset
    if tgt >= len(all_dates) or tgt < 0: return None
    return pd.Timestamp(all_dates[tgt])

# CAND_B params (winner from R3 tuning)
HOLD_DAYS=25; ENTRY_OFFSET=5; MAX_POS=12; POS_PCT=0.08
NPR_MIN=0.15; N_GOOD_MIN=4; POST_RET_MIN=8.0
SLIP_IN, SLIP_OUT, TAX_SALE = 0.001, 0.0015, 0.001
DEPOSIT_RATE=0.01; LIQ_CAP_PCT=0.20; MAX_FILL_DAYS=5; LIQ_MIN=2e9

def backtest_variant(variant_col, use_trend=False):
    # Filter
    e = ev[ev["NP_R"] >= NPR_MIN*100].copy()
    e = e[e["prior_n_good"] >= N_GOOD_MIN]
    e = e[e[variant_col] >= POST_RET_MIN]
    if use_trend:
        e = e[e["pa_TREND_OK"] == 1]
    # Build schedule
    schedule = []
    for _, row in e.iterrows():
        tk = row["ticker"]; rdt = row["Release_Date"]
        if tk not in px_open.columns: continue
        entry_dt = offset_date(rdt, ENTRY_OFFSET)
        exit_dt  = offset_date(rdt, ENTRY_OFFSET + HOLD_DAYS)
        if entry_dt is None or exit_dt is None: continue
        schedule.append({"ticker":tk, "entry_dt":entry_dt, "exit_dt":exit_dt})
    sched = pd.DataFrame(schedule).sort_values("entry_dt").reset_index(drop=True)
    if len(sched) == 0: return None
    entries_by_day = sched.groupby("entry_dt")
    exits_by_day = sched.groupby("exit_dt")

    sw, ew = pd.Timestamp("2010-01-01"), pd.Timestamp("2026-05-13")
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
                cap = LIQ_CAP_PCT * adv * MAX_FILL_DAYS * fpx
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

    def m(start, end):
        s = nav_df["nav"][(nav_df.index>=start) & (nav_df.index<=end)]
        if len(s) < 30: return None
        yrs = (s.index[-1]-s.index[0]).days/365.25
        cagr = (s.iloc[-1]/s.iloc[0])**(1/yrs) - 1
        rets = s.pct_change().dropna(); spy = len(rets)/yrs
        sh = rets.mean()/rets.std()*np.sqrt(spy) if rets.std()>0 else 0
        dd = (s - s.cummax())/s.cummax(); mdd = dd.min()
        cal = cagr/abs(mdd) if mdd<0 else 0
        return cagr*100, sh, mdd*100, cal
    full = m(pd.Timestamp("2014-04-01"), pd.Timestamp("2026-05-13"))
    oos  = m(pd.Timestamp("2024-01-01"), pd.Timestamp("2026-05-13"))
    y22  = m(pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31"))
    q126 = m(pd.Timestamp("2025-12-30"), pd.Timestamp("2026-03-30"))
    return {
        "n_sched": len(sched), "n_trades": len(sells),
        "WR": (sells['ret_pct']>0).mean()*100 if len(sells)>0 else 0,
        "avg_ret": sells['ret_pct'].mean() if len(sells)>0 else 0,
        "full_CAGR": full[0] if full else 0,
        "full_Sharpe": full[1] if full else 0,
        "full_DD": full[2] if full else 0,
        "full_Calmar": full[3] if full else 0,
        "oos_CAGR": oos[0] if oos else 0,
        "y22_CAGR": y22[0] if y22 else 0,
        "q126_CAGR": q126[0] if q126 else 0,
        "final_nav": nav_df["nav"].iloc[-1]/1e9,
    }

# ─── 4. Run all variants ─────────────────────────────────────────────────
configs = [
    ("EQUAL_baseline", "pa_EQUAL", False),
    ("EXP_HL_2y",      "pa_EXP2", False),
    ("EXP_HL_3y",      "pa_EXP3", False),
    ("EXP_HL_4y",      "pa_EXP4", False),
    ("ROLL_N12",       "pa_ROLL12", False),
    ("ROLL_N16",       "pa_ROLL16", False),
    ("TIME_4y",        "pa_TIME4", False),
    ("TREND",          "pa_EQUAL", True),
]

print(f"\n[3] Running {len(configs)} backtests (CAND_B config, 16y) ...\n")
results = []
for name, col, use_trend in configs:
    r = backtest_variant(col, use_trend)
    if r is None:
        print(f"  {name}: no schedule"); continue
    r["name"] = name
    results.append(r)
    print(f"  {name:<18}  N_sched={r['n_sched']:>4}  trades={r['n_trades']:>4}  "
          f"WR={r['WR']:>5.1f}%  CAGR={r['full_CAGR']:>+6.2f}%  Sh={r['full_Sharpe']:>+5.2f}  "
          f"DD={r['full_DD']:>+6.1f}%  OOS={r['oos_CAGR']:>+6.2f}%  Y22={r['y22_CAGR']:>+6.1f}%  Q126={r['q126_CAGR']:>+6.1f}%")

df = pd.DataFrame(results)
df.to_csv("lagged_timedecay_results.csv", index=False)

print("\n" + "="*120)
print("  RANKING by FULL CAGR")
print("="*120)
print(df.sort_values("full_CAGR", ascending=False)[["name","n_sched","n_trades","WR","avg_ret","full_CAGR","full_Sharpe","full_DD","full_Calmar","oos_CAGR","y22_CAGR","q126_CAGR","final_nav"]].to_string(index=False, float_format="%.2f"))
print("\n" + "="*120)
print("  RANKING by SHARPE")
print("="*120)
print(df.sort_values("full_Sharpe", ascending=False)[["name","full_CAGR","full_Sharpe","full_DD","full_Calmar","oos_CAGR","q126_CAGR"]].to_string(index=False, float_format="%.2f"))
print("\nSaved: lagged_timedecay_results.csv")
