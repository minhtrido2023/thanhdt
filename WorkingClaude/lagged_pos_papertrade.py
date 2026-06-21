#!/usr/bin/env python3
"""
lagged_pos_papertrade.py — daily scanner + paper-trade NAV tracker

Strategy (validated honest backtest CAGR ~10%, Sharpe ~1.04, DD -22.5%):
  Universe   : avg_post_good ≥ 8%, n_good ≥ 4 (computed rolling, no lookahead)
  Signal     : new earnings release with NP_R ≥ 15%
  Entry      : T+5 trading days after Release_Date (at Open)
  Exit       : T+30 trading days after Release_Date (i.e., 25 sessions hold)
  Sizing     : 8% NAV/position, max 12 concurrent positions
  Friction   : slip 0.1/0.15%, tax 0.1%, liq cap 20%×5d, deposit 1%/yr cash
  Init NAV   : 50B (configurable)

Usage:
  python lagged_pos_papertrade.py                    # default: run forward from 2026-04-01
  python lagged_pos_papertrade.py --start 2026-04-01 # explicit start date
  python lagged_pos_papertrade.py --report           # show state without re-fetching
  python lagged_pos_papertrade.py --refresh-bq       # force re-fetch from BQ

State files:
  lagged_paper_events.pkl       # all events (cached + freshly pulled)
  lagged_paper_nav.csv          # daily NAV time series
  lagged_paper_trades.csv       # entry/exit log
  lagged_paper_positions.csv    # current open positions
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, subprocess, tempfile, pickle, argparse, json
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from io import StringIO
import pandas as pd, numpy as np

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
PROJECT = "lithe-record-440915-m9"
BQ = r"bq"

# ─── Strategy params (HL_3y + post_min_5 — production spec) ─────────────
# Validated lookahead-free 2026-05-20. Expected CAGR ~19% / Sh 1.43 / DD -15.7%
INIT_NAV       = 50e9
POST_RET_MIN   = 5.0       # was 8.0 — broader universe with HL_3y filtering quality
N_GOOD_MIN     = 4
NPR_MIN        = 0.15      # 15%
ENTRY_OFFSET   = 5
HOLD_DAYS      = 25
MAX_POSITIONS  = 12
POS_PCT        = 0.08      # 8% NAV
LIQ_MIN_VND    = 2e9       # 2B/day
LIQ_CAP_PCT    = 0.20
MAX_FILL_DAYS  = 5
SLIP_IN, SLIP_OUT, TAX_SALE = 0.001, 0.0015, 0.001
DEPOSIT_RATE   = 0.01

# Time-decay profile (HL_3y exp decay)
HALF_LIFE_YEARS = 3.0
import math
LN2 = math.log(2)

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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2026-04-01", help="Paper trade start date")
    ap.add_argument("--report", action="store_true", help="Just print current state")
    ap.add_argument("--refresh-bq", action="store_true", help="Force refresh from BQ")
    args = ap.parse_args()
    start_date = pd.Timestamp(args.start)
    today = pd.Timestamp.today().normalize()
    print(f"[Setup] Paper trade window: {start_date.date()} → {today.date()}", flush=True)

    if args.report:
        return report_state()

    # ─── Step 1: Load + refresh events ───────────────────────────────────
    base_ev = pd.read_csv("data/earnings_events_classified.csv", parse_dates=["Release_Date"])
    last_known = base_ev["Release_Date"].max()
    print(f"[1] Cached events: {len(base_ev):,} (latest release {last_known.date()})")

    cache_new_ev = "data/lagged_paper_new_events.pkl"
    if args.refresh_bq or not os.path.exists(cache_new_ev) or (today - last_known).days > 5:
        print(f"[1] Fetching new events Release_Date > {last_known.date()} ...")
        new_ev_raw = bq_query(f"""
        SELECT f.ticker, f.quarter, f.Release_Date, f.NP_R, f.Revenue_YoY_P0, f.NP_P0, f.NP_P4
        FROM tav2_bq.ticker_financial AS f
        WHERE f.Release_Date IS NOT NULL
          AND f.Release_Date > '{last_known.date()}'
          AND f.NP_R IS NOT NULL
        """)
        new_ev_raw["Release_Date"] = pd.to_datetime(new_ev_raw["Release_Date"])
        print(f"  Fetched {len(new_ev_raw)} new events")
        # Compute pre/release/post returns for new events
        tk_list = "','".join(new_ev_raw["ticker"].unique().tolist()) if len(new_ev_raw)>0 else ""
        if tk_list:
            px_data = bq_query(f"""
            SELECT t.ticker, t.time, t.Close, t.Open, t.Volume_3M_P50
            FROM tav2_bq.ticker AS t
            WHERE t.ticker IN ('{tk_list}') AND t.time >= '{(last_known - pd.Timedelta(days=60)).date()}' AND t.Close > 0
            """)
            px_data["time"] = pd.to_datetime(px_data["time"])
        else:
            px_data = pd.DataFrame(columns=["ticker","time","Close","Open","Volume_3M_P50"])
        new_ev = compute_event_windows(new_ev_raw, px_data)
        # Save
        with open(cache_new_ev,"wb") as f: pickle.dump({"events":new_ev, "px":px_data}, f)
    else:
        with open(cache_new_ev,"rb") as f: c = pickle.load(f)
        new_ev = c["events"]; px_data = c["px"]
        print(f"  Loaded cache: {len(new_ev)} new events")

    # ─── Step 2: Combine + build rolling profile ─────────────────────────
    print(f"\n[2] Combining + computing rolling profile ...")
    base_ev_use = base_ev[["ticker","quarter","Release_Date","NP_R","Rev_YoY","pre_ret","rel_ret","post_ret"]].copy()
    if "Rev_YoY" not in new_ev.columns and "Revenue_YoY_P0" in new_ev.columns:
        new_ev = new_ev.rename(columns={"Revenue_YoY_P0":"Rev_YoY"})
    if "Rev_YoY" not in new_ev.columns: new_ev["Rev_YoY"] = np.nan
    new_ev_use = new_ev[["ticker","quarter","Release_Date","NP_R","Rev_YoY","pre_ret","rel_ret","post_ret"]].copy()
    # Convert: base_ev has NP_R as % already (e.g., 15.0 for 15%); ev_raw NP_R is fraction (0.15)
    # check ranges
    if new_ev_use["NP_R"].abs().max() <= 5:
        new_ev_use["NP_R"] = new_ev_use["NP_R"] * 100
    if "Rev_YoY" in new_ev_use.columns and new_ev_use["Rev_YoY"].abs().max() <= 5:
        new_ev_use["Rev_YoY"] = new_ev_use["Rev_YoY"] * 100

    all_ev = pd.concat([base_ev_use, new_ev_use], ignore_index=True)
    all_ev = all_ev.drop_duplicates(subset=["ticker","quarter"], keep="last")
    all_ev = all_ev.sort_values(["ticker","Release_Date"]).reset_index(drop=True)
    # HL_3y EXP DECAY profile (production)
    all_ev["prior_n_good"] = 0
    all_ev["prior_avg_post_good"] = np.nan
    for tk, g in all_ev.groupby("ticker"):
        idxs = g.index.tolist()
        good_history = []  # list of (release_date, post_ret) for prior GOOD events
        for row_idx in idxs:
            row = all_ev.loc[row_idx]
            cur_date = row["Release_Date"]
            n_good = len(good_history)
            all_ev.at[row_idx, "prior_n_good"] = n_good
            if n_good >= 1:
                dates_arr = pd.to_datetime([d for d,_ in good_history])
                posts_arr = np.array([p for _,p in good_history])
                age_yrs = (cur_date - dates_arr).days.values / 365.25
                w = np.exp(-LN2 * age_yrs / HALF_LIFE_YEARS)
                all_ev.at[row_idx, "prior_avg_post_good"] = (posts_arr * w).sum() / w.sum() if w.sum() > 0 else np.nan
            # Update history AFTER computing (no lookahead)
            if pd.notna(row["NP_R"]) and row["NP_R"] >= 15 and pd.notna(row["post_ret"]):
                good_history.append((cur_date, row["post_ret"]))
    print(f"  Total events: {len(all_ev):,}  | Events with ≥{N_GOOD_MIN} prior good: {(all_ev['prior_n_good']>=N_GOOD_MIN).sum():,}")

    # ─── Step 3: Filter to qualified signals ─────────────────────────────
    qual = all_ev[
        (all_ev["NP_R"] >= NPR_MIN * 100) &
        (all_ev["prior_n_good"] >= N_GOOD_MIN) &
        (all_ev["prior_avg_post_good"] >= POST_RET_MIN) &
        (all_ev["Release_Date"] >= start_date)
    ].copy()
    print(f"  Qualified signals in window: {len(qual)}")
    if len(qual) > 0:
        print(f"  Latest 5 signals:")
        for _, r in qual.sort_values("Release_Date", ascending=False).head(5).iterrows():
            print(f"    {r['Release_Date'].date()}  {r['ticker']:<7}  NP_R={r['NP_R']:+.1f}%  prior_avg={r['prior_avg_post_good']:.1f}%")

    # ─── Step 4: Pull price data for all relevant tickers ────────────────
    print(f"\n[4] Pulling price data for sim ...")
    tk_needed = sorted(qual["ticker"].unique().tolist())
    tk_str = "','".join(tk_needed)
    sim_px = bq_query(f"""
    SELECT t.ticker, t.time, t.Close, t.Open, t.Volume_3M_P50
    FROM tav2_bq.ticker AS t
    WHERE t.ticker IN ('{tk_str}') AND t.time >= '{(start_date - pd.Timedelta(days=10)).date()}' AND t.Close > 0
    ORDER BY t.time
    """)
    sim_px["time"] = pd.to_datetime(sim_px["time"])
    print(f"  Pulled {len(sim_px):,} price rows for {len(tk_needed)} tickers")

    # Also fetch VNI for benchmark
    vni = bq_query(f"""SELECT t.time, t.Close FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' AND t.time >= '{start_date.date()}' AND t.Close > 100 ORDER BY t.time""")
    vni["time"] = pd.to_datetime(vni["time"])

    # Build pivots
    px_close = sim_px.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
    px_open  = sim_px.pivot_table(index="time", columns="ticker", values="Open", aggfunc="first").sort_index().ffill(limit=5)
    liq      = sim_px.pivot_table(index="time", columns="ticker", values="Volume_3M_P50", aggfunc="first").sort_index().ffill(limit=5)
    master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns")
    px_close.index = px_open.index = liq.index = master_idx
    all_dates = np.array(master_idx)

    def offset_date(ref_dt, offset):
        ref = np.datetime64(ref_dt)
        pos = np.searchsorted(all_dates, ref, side="right") - 1
        if pos < 0: return None
        tgt = pos + offset
        if tgt >= len(all_dates) or tgt < 0: return None
        return pd.Timestamp(all_dates[tgt])

    # ─── Step 5: Build schedule ─────────────────────────────────────────
    schedule = []
    for _, row in qual.iterrows():
        tk = row["ticker"]; rdt = row["Release_Date"]
        if tk not in px_open.columns: continue
        entry_dt = offset_date(rdt, ENTRY_OFFSET)
        exit_dt  = offset_date(rdt, ENTRY_OFFSET + HOLD_DAYS)
        if entry_dt is None: continue
        # exit_dt may be in future — that's OK, position remains open
        schedule.append({"ticker":tk, "entry_dt":entry_dt, "exit_dt":exit_dt,
                         "release_dt":rdt, "NP_R":row["NP_R"], "prior_avg":row["prior_avg_post_good"]})
    sched = pd.DataFrame(schedule).sort_values("entry_dt").reset_index(drop=True)
    print(f"\n[5] Schedule built: {len(sched)} planned entries")

    # ─── Step 6: Simulate forward ───────────────────────────────────────
    print(f"\n[6] Simulating forward ...")
    entries_by_day = sched.groupby("entry_dt") if len(sched)>0 else None
    exits_by_day   = sched.groupby("exit_dt")  if len(sched)>0 else None

    sim_days = [d for d in master_idx if start_date <= d <= today]
    cash = INIT_NAV
    positions = {}
    nav_history = []
    trades = []
    daily_rate = (1+DEPOSIT_RATE)**(1/365.25) - 1

    for dt in sim_days:
        cash *= (1 + daily_rate)
        # Process exits
        if exits_by_day is not None and dt in exits_by_day.groups:
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
                trades.append({"dt":dt,"ticker":tk,"side":"SELL","px":fpx,
                                "entry_dt":pos["entry_dt"],"entry_px":pos["entry_px"],
                                "shares":pos["shares"],"ret_pct":ret_pct,
                                "hold_days":(dt-pos["entry_dt"]).days,
                                "release_dt":pos["release_dt"]})
                del positions[tk]
        # Process entries
        if entries_by_day is not None and dt in entries_by_day.groups:
            mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
            nav_now = cash + mtm
            for _, en_row in entries_by_day.get_group(dt).iterrows():
                tk = en_row["ticker"]
                if tk in positions: continue
                if len(positions) >= MAX_POSITIONS: continue
                fpx = px_open.at[dt, tk] if tk in px_open.columns else np.nan
                if pd.isna(fpx) or fpx <= 0: continue
                adv = liq.at[dt, tk] if tk in liq.columns else 0
                if pd.isna(adv) or adv*fpx < LIQ_MIN_VND: continue
                target = POS_PCT * nav_now
                cap = LIQ_CAP_PCT * adv * MAX_FILL_DAYS * fpx
                alloc = min(target, cap)
                if alloc < 1e6 or alloc > cash: continue
                eff_px = fpx*(1+SLIP_IN); shares = alloc/eff_px; cost = shares*eff_px
                cash -= cost
                positions[tk] = {"entry_dt":dt, "exit_dt":en_row["exit_dt"], "shares":shares,
                                  "entry_px":fpx, "release_dt":en_row["release_dt"]}
                trades.append({"dt":dt,"ticker":tk,"side":"BUY","px":fpx,
                                "entry_dt":dt,"entry_px":fpx,"shares":shares,
                                "ret_pct":0,"hold_days":0,
                                "release_dt":en_row["release_dt"]})
        # NAV
        mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
        nav = cash + mtm
        nav_history.append({"date":dt,"nav":nav,"cash":cash,"mtm":mtm,"n_pos":len(positions)})

    nav_df = pd.DataFrame(nav_history).set_index("date")
    trades_df = pd.DataFrame(trades)

    # ─── Step 7: Build open positions snapshot ───────────────────────────
    last_dt = nav_df.index.max() if len(nav_df) > 0 else today
    open_pos_rows = []
    for tk, pos in positions.items():
        cur_px = px_close.at[last_dt, tk] if (tk in px_close.columns and last_dt in px_close.index) else pos["entry_px"]
        if pd.isna(cur_px): cur_px = pos["entry_px"]
        mtm_value = pos["shares"] * cur_px
        unrealized = (cur_px/pos["entry_px"] - 1) * 100
        days_held = (last_dt - pos["entry_dt"]).days
        days_to_exit = (pos["exit_dt"] - last_dt).days if pos["exit_dt"] is not None else None
        open_pos_rows.append({"ticker":tk, "entry_dt":pos["entry_dt"], "entry_px":pos["entry_px"],
                              "cur_px":cur_px, "shares":pos["shares"], "mtm_value":mtm_value,
                              "unrealized_pct":unrealized, "days_held":days_held,
                              "exit_dt":pos["exit_dt"], "days_to_exit":days_to_exit,
                              "release_dt":pos["release_dt"]})
    open_df = pd.DataFrame(open_pos_rows)

    # ─── Step 8: Save outputs ────────────────────────────────────────────
    nav_df.to_csv("data/lagged_paper_nav.csv")
    trades_df.to_csv("data/lagged_paper_trades.csv", index=False)
    open_df.to_csv("data/lagged_paper_positions.csv", index=False)
    qual.to_csv("data/lagged_paper_qualified_signals.csv", index=False)
    with open("lagged_paper_state.json","w") as f:
        json.dump({"start_date": str(start_date.date()), "last_run": str(today.date()),
                   "init_nav": INIT_NAV, "current_nav": float(nav_df["nav"].iloc[-1]) if len(nav_df)>0 else INIT_NAV,
                   "n_positions": len(positions), "n_trades": len(trades_df)}, f, indent=2)

    # ─── Step 9: Report ──────────────────────────────────────────────────
    print_report(nav_df, trades_df, open_df, vni, start_date, today)


def compute_event_windows(events, px_data):
    """For each new event, compute pre/release/post returns from price data."""
    px_piv = px_data.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5) if len(px_data)>0 else pd.DataFrame()
    all_dates = np.array(px_piv.index) if len(px_piv) > 0 else np.array([])
    rows = []
    for _, row in events.iterrows():
        tk = row["ticker"]; rdt = row["Release_Date"]
        def get_off(off):
            if tk not in px_piv.columns or len(all_dates)==0: return np.nan
            pos = np.searchsorted(all_dates, np.datetime64(rdt), side="right") - 1
            if pos < 0: return np.nan
            tgt = pos + off
            if tgt < 0 or tgt >= len(all_dates): return np.nan
            return px_piv.iloc[tgt][tk]
        p_m30, p_m1, p_p5, p_p30 = get_off(-30), get_off(-1), get_off(+5), get_off(+30)
        if any(pd.isna(p) for p in [p_m1]) or p_m1 is None or p_m1 <= 0:
            continue
        pre_ret = (p_m1/p_m30 - 1)*100 if pd.notna(p_m30) and p_m30 > 0 else np.nan
        rel_ret = (p_p5/p_m1 - 1)*100 if pd.notna(p_p5) and p_p5 > 0 else np.nan
        post_ret= (p_p30/p_p5 - 1)*100 if pd.notna(p_p30) and pd.notna(p_p5) and p_p5 > 0 else np.nan
        rows.append({"ticker":tk, "quarter":row["quarter"], "Release_Date":rdt,
                     "NP_R":row["NP_R"]*100 if pd.notna(row["NP_R"]) else np.nan,
                     "Rev_YoY":row["Revenue_YoY_P0"]*100 if pd.notna(row["Revenue_YoY_P0"]) else np.nan,
                     "pre_ret":pre_ret, "rel_ret":rel_ret, "post_ret":post_ret})
    return pd.DataFrame(rows)


def print_report(nav_df, trades_df, open_df, vni, start_date, today):
    print("\n" + "="*90)
    print(f"  📊 LAGGED_POS PAPER-TRADE STATE (as of {today.date()})")
    print("="*90)
    if len(nav_df) == 0:
        print("  No data yet — sim window not started")
        return
    cur_nav = nav_df["nav"].iloc[-1]
    days = (today - start_date).days
    nav_change_pct = (cur_nav/INIT_NAV - 1) * 100
    print(f"  Start NAV: {INIT_NAV/1e9:.2f}B  →  Current NAV: {cur_nav/1e9:.2f}B  ({nav_change_pct:+.2f}%)")
    print(f"  Days elapsed: {days}  | Cash: {nav_df['cash'].iloc[-1]/1e9:.2f}B  | Equity: {nav_df['mtm'].iloc[-1]/1e9:.2f}B")
    print(f"  Open positions: {nav_df['n_pos'].iloc[-1]}")
    yrs = days/365.25
    if yrs > 0.05:
        cagr = (cur_nav/INIT_NAV)**(1/yrs) - 1
        print(f"  Annualized: {cagr*100:+.2f}% CAGR")

    # VNI benchmark
    vni_aligned = vni.set_index("time")["Close"].reindex(nav_df.index).ffill()
    if len(vni_aligned.dropna()) > 1:
        vni_start = vni_aligned.dropna().iloc[0]
        vni_end = vni_aligned.dropna().iloc[-1]
        vni_pct = (vni_end/vni_start - 1) * 100
        print(f"  VNI same period: {vni_pct:+.2f}%  | Alpha: {nav_change_pct - vni_pct:+.2f}pp")

    if len(open_df) > 0:
        print(f"\n  📌 OPEN POSITIONS ({len(open_df)}):")
        print(f"  {'Ticker':<8}{'Entry Date':<12}{'Entry Px':>10}{'Cur Px':>10}{'Shares':>12}{'Unrealized':>12}{'Days Held':>11}{'Exit ETA':<12}")
        for _, r in open_df.sort_values("days_to_exit").iterrows():
            ed = r["exit_dt"].date() if pd.notna(r["exit_dt"]) else "?"
            print(f"  {r['ticker']:<8}{str(r['entry_dt'].date()):<12}{r['entry_px']:>10.0f}{r['cur_px']:>10.0f}{int(r['shares']):>12,d}{r['unrealized_pct']:>+11.2f}%{int(r['days_held']):>11d}{str(ed):<12}")

    if len(trades_df) > 0:
        sells = trades_df[trades_df["side"]=="SELL"]
        print(f"\n  📈 TRADE STATS ({len(trades_df)} events, {len(sells)} closed):")
        if len(sells) > 0:
            print(f"     Win rate: {(sells['ret_pct']>0).mean()*100:.1f}%  | Avg ret: {sells['ret_pct'].mean():+.2f}%")
            print(f"     Best: {sells['ret_pct'].max():+.1f}% ({sells.loc[sells['ret_pct'].idxmax(), 'ticker']})  | Worst: {sells['ret_pct'].min():+.1f}% ({sells.loc[sells['ret_pct'].idxmin(), 'ticker']})")
            print(f"\n  Last 10 closed trades:")
            for _, r in sells.sort_values("dt", ascending=False).head(10).iterrows():
                print(f"    {r['dt'].date()}  {r['ticker']:<7}  {r['ret_pct']:>+6.1f}%  ({r['hold_days']}d hold)")
    print()


def report_state():
    """Just print existing state without re-running."""
    if not os.path.exists("lagged_paper_state.json"):
        print("No state file. Run with --start first.")
        return
    with open("lagged_paper_state.json") as f: state = json.load(f)
    print(f"📄 State summary:")
    for k,v in state.items(): print(f"  {k}: {v}")
    if os.path.exists("data/lagged_paper_positions.csv"):
        op = pd.read_csv("data/lagged_paper_positions.csv", parse_dates=["entry_dt","exit_dt","release_dt"])
        print(f"\n📌 {len(op)} open positions:"); print(op.to_string(index=False))
    if os.path.exists("data/lagged_paper_trades.csv"):
        tr = pd.read_csv("data/lagged_paper_trades.csv", parse_dates=["dt","entry_dt","release_dt"])
        sells = tr[tr["side"]=="SELL"]
        print(f"\n📈 {len(tr)} events / {len(sells)} closed trades")
        if len(sells):
            print(f"  WR: {(sells['ret_pct']>0).mean()*100:.1f}%  | Avg: {sells['ret_pct'].mean():+.2f}%")


if __name__ == "__main__":
    main()
