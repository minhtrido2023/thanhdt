#!/usr/bin/env python3
"""
walkforward_lagged_honest.py — eliminate universe lookahead bias

The original backtest used profile computed from ALL events 2009-2026 to filter
universe at every point in time. This is lookahead — in 2014 we couldn't know
which tickers would have post-release alpha through 2026.

Fix: ROLLING profile. At each event time t, the ticker's `avg_post_good_to_date`
is computed using ONLY events with Release_Date < t. Require ≥4 prior GOOD events
in lookback to qualify.

This is the "honest" version of the walk-forward.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, pickle, subprocess, tempfile
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from io import StringIO
import pandas as pd, numpy as np

PROJECT = "lithe-record-440915-m9"
BQ = r"bq"
INIT_NAV = 50e9

print("[1] Loading data ...")
with open("earnings_px.pkl","rb") as f: px = pickle.load(f)
px["time"] = pd.to_datetime(px["time"])
px_close = px.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns")
px_close.index = master_idx
all_dates = np.array(master_idx)

with open("lagged_pos_ov.pkl","rb") as f: ov = pickle.load(f)
ov["time"] = pd.to_datetime(ov["time"])
px_open = ov.pivot_table(index="time", columns="ticker", values="Open", aggfunc="first").sort_index()
liq     = ov.pivot_table(index="time", columns="ticker", values="Volume_3M_P50", aggfunc="first").sort_index()
px_open = px_open.reindex(master_idx).ffill(limit=5)
liq     = liq.reindex(master_idx).ffill(limit=5)

ev_classified = pd.read_csv("earnings_events_classified.csv", parse_dates=["Release_Date"])
ev_classified = ev_classified.sort_values(["ticker","Release_Date"]).reset_index(drop=True)
print(f"  Events: {len(ev_classified):,}")

# FA for sector
fa = pd.read_csv("fa_ratings_lh.csv", parse_dates=["time"])
fa_uni = fa.sort_values("quarter").drop_duplicates("ticker", keep="last")[["ticker","sub","MktCap"]]
ticker_sub = dict(zip(fa_uni["ticker"], fa_uni["sub"]))

# ─── 2. Build ROLLING profile per (ticker, event_index) ──────────────────
print("\n[2] Computing rolling per-event profile (no lookahead) ...")
# For each ticker, sort events by Release_Date; at each event i,
# profile is built from events[0..i-1] (excluding current).

ev_classified["prior_n_good"] = 0
ev_classified["prior_n_events"] = 0
ev_classified["prior_avg_post_good"] = np.nan
ev_classified["prior_freq_LAGGED_POS"] = np.nan

for tk, g in ev_classified.groupby("ticker"):
    idxs = g.index.tolist()
    pre_n = 0; pre_n_good = 0; pre_sum_post_good = 0.0; pre_n_lagged = 0
    for i, row_idx in enumerate(idxs):
        row = ev_classified.loc[row_idx]
        # write prior stats (BEFORE adding this row)
        ev_classified.at[row_idx, "prior_n_events"] = pre_n
        ev_classified.at[row_idx, "prior_n_good"]   = pre_n_good
        if pre_n_good > 0:
            ev_classified.at[row_idx, "prior_avg_post_good"] = pre_sum_post_good / pre_n_good
        if pre_n > 0:
            ev_classified.at[row_idx, "prior_freq_LAGGED_POS"] = pre_n_lagged / pre_n * 100
        # update accumulators with current event
        pre_n += 1
        if pd.notna(row["NP_R"]) and row["NP_R"] >= 15:
            pre_n_good += 1
            pre_sum_post_good += row["post_ret"]
        if row["pattern"] == "LAGGED_POS":
            pre_n_lagged += 1

# Print distribution of prior_avg_post_good
print(f"  Events with ≥4 prior good events: {(ev_classified['prior_n_good']>=4).sum():,} / {len(ev_classified):,}")
sub = ev_classified[ev_classified["prior_n_good"] >= 4]
print(f"  prior_avg_post_good distribution (n_good≥4):")
print(f"    p25={sub['prior_avg_post_good'].quantile(0.25):.1f}%  "
      f"median={sub['prior_avg_post_good'].median():.1f}%  "
      f"p75={sub['prior_avg_post_good'].quantile(0.75):.1f}%")
for thr in [3, 5, 8, 10]:
    n = ((sub["prior_avg_post_good"] >= thr)).sum()
    print(f"    prior_avg_post_good >= {thr}%: {n:,}")

# ─── 3. Helpers ──────────────────────────────────────────────────────────
def offset_date(ref_dt, offset):
    ref = np.datetime64(ref_dt)
    pos = np.searchsorted(all_dates, ref, side="right") - 1
    if pos < 0: return None
    tgt = pos + offset
    if tgt >= len(all_dates) or tgt < 0: return None
    return pd.Timestamp(all_dates[tgt])

# VNI for filter (not used here but available)
vni_df = bq_query_cache = None  # not needed for honest test

# ─── 4. Backtest function with rolling filter ────────────────────────────
def backtest_honest(cfg, sw, ew):
    POST_RET_MIN = cfg.get("post_ret_min", 8.0)
    N_GOOD_MIN   = cfg.get("n_good_min", 4)
    NPR_MIN      = cfg.get("npr_min", 0.15)
    REV_REQ      = cfg.get("rev_req", False)
    ENTRY_OFFSET = cfg.get("entry_offset", 5)
    HOLD_DAYS    = cfg.get("hold_days", 25)
    MAX_POS      = cfg.get("max_pos", 10)
    POS_PCT      = cfg.get("pos_pct", 0.10)
    SECTOR_BOOST = cfg.get("sector_boost", None)
    LIQ_MIN      = cfg.get("liq_min", 2e9)
    SLIP_IN, SLIP_OUT, TAX_SALE = 0.001, 0.0015, 0.001
    DEPOSIT_RATE = 0.01
    LIQ_CAP_PCT  = 0.20
    MAX_FILL_DAYS = 5

    # Filter events: rolling profile must qualify
    ev = ev_classified.copy()
    ev = ev[ev["NP_R"] >= NPR_MIN * 100]
    if REV_REQ: ev = ev[ev["Rev_YoY"] >= 15]
    ev = ev[ev["prior_n_good"] >= N_GOOD_MIN]
    ev = ev[ev["prior_avg_post_good"] >= POST_RET_MIN]

    # Build schedule
    schedule = []
    for _, row in ev.iterrows():
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
                    sub_v = ticker_sub.get(tk, "DEFAULT")
                    if sub_v in SECTOR_BOOST: pct = SECTOR_BOOST[sub_v]
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

# ─── 5. Run honest walk-forward ──────────────────────────────────────────
configs = {
    "BASELINE":  {"post_ret_min":8, "max_pos":10, "pos_pct":0.10},
    "CAND_A_max14":  {"post_ret_min":8, "max_pos":14, "pos_pct":0.10},
    "CAND_B_pos8_max12":  {"post_ret_min":8, "max_pos":12, "pos_pct":0.08},
    "CAND_C_max12_sec":  {"post_ret_min":8, "max_pos":12, "pos_pct":0.10,
                           "sector_boost":{"SECURITIES":0.12,"REIT_RES":0.12}},
}
windows = [
    ("FULL",      pd.Timestamp("2010-01-01"), pd.Timestamp("2026-05-13")),
    ("P1_IS_10-18",  pd.Timestamp("2010-01-01"), pd.Timestamp("2018-12-31")),
    ("P2_OOS_19-26", pd.Timestamp("2019-01-01"), pd.Timestamp("2026-05-13")),
    ("P3_IS_10-20",  pd.Timestamp("2010-01-01"), pd.Timestamp("2020-12-31")),
    ("P4_OOS_21-26", pd.Timestamp("2021-01-01"), pd.Timestamp("2026-05-13")),
    ("P6_OOS_15-26", pd.Timestamp("2015-01-01"), pd.Timestamp("2026-05-13")),
]
for yr in range(2014, 2026):
    windows.append((f"Y{yr}", pd.Timestamp(f"{yr}-01-01"), pd.Timestamp(f"{yr}-12-31")))

print("\n[5] Honest walk-forward (rolling profile, no lookahead) ...\n")
print(f"{'Config':<22} {'Window':<14} {'CAGR':>8} {'Sharpe':>8} {'MaxDD':>9} {'Calmar':>7} {'WR':>6} {'N':>5}")
print("-"*90)
results = []
for cfg_name, cfg_params in configs.items():
    cfg_params["name"] = cfg_name
    for wn, sw, ew in windows:
        r = backtest_honest(cfg_params, sw, ew)
        if r is None: continue
        results.append({"config":cfg_name,"window":wn, **r})
        print(f"{cfg_name:<22} {wn:<14} {r['CAGR']:>+7.2f}% {r['Sharpe']:>+7.2f} {r['MaxDD']:>+8.2f}% {r['Calmar']:>+6.2f} {r['WR']:>+5.1f}% {r['N']:>5d}")
    print()

res_df = pd.DataFrame(results)
res_df.to_csv("lagged_pos_walkforward_honest.csv", index=False)

print("\n" + "="*120)
print("  IS vs OOS comparison (honest)")
print("="*120)
print(f"{'Config':<22} {'Split':<6} {'IS CAGR':>10} {'OOS CAGR':>10} {'Δ':>6} {'IS Sh':>7} {'OOS Sh':>7} {'IS DD':>8} {'OOS DD':>8}")
splits = [("18/19","P1_IS_10-18","P2_OOS_19-26"),("20/21","P3_IS_10-20","P4_OOS_21-26")]
for cfg in configs:
    for sname, isn, oosn in splits:
        ir = res_df[(res_df["config"]==cfg) & (res_df["window"]==isn)]
        or_ = res_df[(res_df["config"]==cfg) & (res_df["window"]==oosn)]
        if len(ir)==0 or len(or_)==0: continue
        ir = ir.iloc[0]; or_ = or_.iloc[0]
        print(f"{cfg:<22} {sname:<6} {ir['CAGR']:>+9.2f}% {or_['CAGR']:>+9.2f}% {or_['CAGR']-ir['CAGR']:>+5.2f} {ir['Sharpe']:>+6.2f} {or_['Sharpe']:>+6.2f} {ir['MaxDD']:>+7.2f}% {or_['MaxDD']:>+7.2f}%")
    print()

# Annual
print("\n" + "="*120)
print("  Annual CAGR (honest)")
print("="*120)
yr_cols = [f"Y{y}" for y in range(2014, 2026)]
print(f"{'Config':<22}" + "".join(f"{y[-2:]:>7}" for y in yr_cols))
for cfg in configs:
    line = f"{cfg:<22}"
    for yc in yr_cols:
        rr = res_df[(res_df["config"]==cfg) & (res_df["window"]==yc)]
        if len(rr): line += f"{rr.iloc[0]['CAGR']:>+6.1f}%"
        else: line += " " * 7
    print(line)

# Comparison vs biased
print("\n" + "="*120)
print("  HONEST vs BIASED comparison (FULL window 2010-2026)")
print("="*120)
biased = {
    "BASELINE": (15.55, 1.65, -14.51),
    "CAND_A_max14": (16.85, 1.61, -14.19),
    "CAND_B_pos8_max12": (15.43, 1.70, -12.57),
    "CAND_C_max12_sec": (16.75, 1.58, -15.00),
}
print(f"{'Config':<22} {'Biased CAGR':>12} {'Honest CAGR':>12} {'Δ CAGR':>8} {'Biased Sh':>10} {'Honest Sh':>10}")
for cfg, (bc, bs, bd) in biased.items():
    rr = res_df[(res_df["config"]==cfg) & (res_df["window"]=="FULL")]
    if len(rr) == 0: continue
    hc = rr.iloc[0]["CAGR"]; hs = rr.iloc[0]["Sharpe"]
    print(f"{cfg:<22} {bc:>+11.2f}% {hc:>+11.2f}% {hc-bc:>+7.2f} {bs:>+10.2f} {hs:>+10.2f}")

print("\nSaved: lagged_pos_walkforward_honest.csv")
