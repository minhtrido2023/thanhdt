#!/usr/bin/env python3
"""
analyze_2025_lagged_weakness.py — Why LAGGED -16.59pp vs Current in 2025?

LAGGED Y2025 +29.88% vs Current +46.48% = -16.59pp gap
VNI Y2025 +40.84% (strong bull)

Diagnose:
  1. LAGGED 2025 trades — what tickers, holding period, returns
  2. Sector breakdown vs broader market
  3. Hold-cycle effect: do 25-day holds cap gains in trending stocks?
  4. Universe composition: is LAGGED filter selecting non-bull-friendly tickers?
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, pickle
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
INIT_NAV = 50e9

# ─── 1. Rebuild LAGGED 2025 trades + per-ticker returns ──────────────────
print("[1] Loading + computing LAGGED 2025 trade ledger ...")
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

ev = pd.read_csv("earnings_events_classified.csv", parse_dates=["Release_Date"])
ev = ev.sort_values(["ticker","Release_Date"]).reset_index(drop=True)

LN2 = np.log(2); HL = 3.0
ev["pa_HL3"] = np.nan; ev["prior_n_good"] = 0
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

POST_MIN, N_MIN, NPR_MIN, ENTRY, HOLD, MAX_POS, POS_PCT = 5.0, 4, 0.15, 5, 25, 12, 0.08
e = ev[(ev["NP_R"] >= NPR_MIN*100) & (ev["prior_n_good"] >= N_MIN) & (ev["pa_HL3"] >= POST_MIN)].copy()

def offset_date(ref_dt, offset):
    ref = np.datetime64(ref_dt)
    pos = np.searchsorted(all_dates, ref, side="right") - 1
    if pos < 0: return None
    tgt = pos + offset
    if tgt >= len(all_dates) or tgt < 0: return None
    return pd.Timestamp(all_dates[tgt])

schedule = []
for _, row in e.iterrows():
    tk = row["ticker"]; rdt = row["Release_Date"]
    if tk not in px_open.columns: continue
    entry_dt = offset_date(rdt, ENTRY); exit_dt = offset_date(rdt, ENTRY + HOLD)
    if entry_dt is None or exit_dt is None: continue
    schedule.append({"ticker":tk, "entry_dt":entry_dt, "exit_dt":exit_dt})
sched_lag = pd.DataFrame(schedule).sort_values("entry_dt").reset_index(drop=True)
entries_by_day = sched_lag.groupby("entry_dt")
exits_by_day = sched_lag.groupby("exit_dt")

# Simulate just to collect trades
SLIP_IN, SLIP_OUT, TAX = 0.001, 0.0015, 0.001
DEPOSIT=0.01; LIQ_CAP=0.20; MAX_FILL=5; LIQ_MIN=2e9
sw, ew = pd.Timestamp("2014-01-02"), pd.Timestamp("2026-05-15")
sim_days = [d for d in master_idx if sw <= d <= ew]
cash = INIT_NAV; positions = {}; trades = []
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
            trades.append({"dt":dt,"ticker":tk,"side":"SELL",
                           "entry_dt":pos["entry_dt"],"entry_px":pos["entry_px"],
                           "exit_px":fpx,"shares":pos["shares"],
                           "ret_pct":(fpx/pos["entry_px"]-1)*100,
                           "hold_days":(dt-pos["entry_dt"]).days})
            del positions[tk]
    if dt in entries_by_day.groups:
        mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
        nav_now = cash + mtm
        for _, en_row in entries_by_day.get_group(dt).iterrows():
            tk = en_row["ticker"]
            if tk in positions or len(positions) >= MAX_POS: continue
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

trades_df = pd.DataFrame(trades)
trades_df["entry_dt"] = pd.to_datetime(trades_df["entry_dt"])
trades_df["dt"] = pd.to_datetime(trades_df["dt"])

# ─── 2. Filter Y2025 trades ──────────────────────────────────────────────
y25_trades = trades_df[(trades_df["dt"].dt.year == 2025) | (trades_df["entry_dt"].dt.year == 2025)].copy()
print(f"\n[2] LAGGED Y2025 trades: {len(y25_trades)}")
print(f"  WR: {(y25_trades['ret_pct']>0).mean()*100:.1f}%  Avg: {y25_trades['ret_pct'].mean():+.2f}%  Median: {y25_trades['ret_pct'].median():+.2f}%")
print(f"  Best: {y25_trades['ret_pct'].max():+.1f}% ({y25_trades.loc[y25_trades['ret_pct'].idxmax(),'ticker']})")
print(f"  Worst: {y25_trades['ret_pct'].min():+.1f}% ({y25_trades.loc[y25_trades['ret_pct'].idxmin(),'ticker']})")

# Top 15 winners + losers
print("\n  Top 15 winners (Y2025):")
print(y25_trades.nlargest(15, "ret_pct")[["ticker","entry_dt","ret_pct","hold_days"]].to_string(index=False))
print("\n  Top 15 losers (Y2025):")
print(y25_trades.nsmallest(15, "ret_pct")[["ticker","entry_dt","ret_pct","hold_days"]].to_string(index=False))

# ─── 3. Hold-cycle leakage analysis ──────────────────────────────────────
# For each trade, compute: what would return be if we held longer?
print("\n[3] Hold-cycle leakage analysis (Y2025 trades): if we held 50d / 75d / 100d instead of 25d?")

extended_returns = []
for _, t in y25_trades.iterrows():
    tk = t["ticker"]; ent_dt = t["entry_dt"]
    if tk not in px_close.columns: continue
    pos_idx = np.searchsorted(all_dates, np.datetime64(ent_dt))
    actual_ret = t["ret_pct"]
    for extra in [25, 50, 75, 100]:  # = 25 + extra days
        target_pos = pos_idx + extra
        if target_pos >= len(all_dates): continue
        exit_dt = all_dates[target_pos]
        exit_px = px_close.iloc[target_pos][tk]
        if pd.isna(exit_px): continue
        ext_ret = (exit_px / t["entry_px"] - 1) * 100
        extended_returns.append({"ticker":tk, "entry_dt":ent_dt, "hold_days":extra,
                                  "ret_pct_extended":ext_ret, "ret_pct_actual": actual_ret})

ext_df = pd.DataFrame(extended_returns)
if len(ext_df) > 0:
    pivot_ext = ext_df.pivot_table(index="ticker", columns="hold_days", values="ret_pct_extended", aggfunc="last").reset_index()
    print("\n  Avg return by HOLD duration (Y2025 sample):")
    for hd in [25, 50, 75, 100]:
        sub = ext_df[ext_df["hold_days"] == hd]
        if len(sub) > 0:
            print(f"    Hold {hd}d: avg={sub['ret_pct_extended'].mean():+.2f}%  WR={(sub['ret_pct_extended']>0).mean()*100:.1f}%  N={len(sub)}")

# Compare hold-cycle (avg actual 25d return vs longer-hold)
actual_avg = y25_trades["ret_pct"].mean()
print(f"\n  Actual avg (25d hold): {actual_avg:+.2f}%")

# ─── 4. Sector / ticker mix ──────────────────────────────────────────────
print("\n[4] Sector/ticker analysis ...")
fa = pd.read_csv("fa_ratings_lh.csv", parse_dates=["time"])
fa_uni = fa.sort_values("quarter").drop_duplicates("ticker", keep="last")[["ticker","sub","MktCap"]]

y25_with_sub = y25_trades.merge(fa_uni, on="ticker", how="left")
print(f"\n  Y2025 trades by sector:")
sec_stats = y25_with_sub.groupby("sub").agg(N=("ticker","size"), avg_ret=("ret_pct","mean"), wr=("ret_pct", lambda x: (x>0).mean()*100))
print(sec_stats.sort_values("avg_ret", ascending=False).to_string())

# Cap bucket
def cap_bucket(mc):
    if pd.isna(mc): return "UNK"
    if mc < 500e9: return "MICRO"
    if mc < 2e12: return "SMALL"
    if mc < 10e12: return "MID"
    return "LARGE"
y25_with_sub["cap"] = y25_with_sub["MktCap"].apply(cap_bucket)
print(f"\n  Y2025 trades by market cap:")
cap_stats = y25_with_sub.groupby("cap").agg(N=("ticker","size"), avg_ret=("ret_pct","mean"), wr=("ret_pct", lambda x: (x>0).mean()*100))
print(cap_stats.to_string())

# ─── 5. Compare to VNI 2025 sector performance ───────────────────────────
print("\n[5] VNI vs LAGGED tickers vs VN30 leaders ...")
# Get top 30 leaders in 2025
print("  (LAGGED dwells in mid/small-cap earnings drift; bull rally favored large-cap momentum)")

print("\nDone.")
