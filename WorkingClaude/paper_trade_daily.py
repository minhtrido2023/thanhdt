"""Daily paper-trade simulator for Layer 3 timing rules.

Idempotent — safe to run multiple times same day.

Workflow:
  1. Find latest holistic_*.csv (BA-system recommendations)
  2. For each fresh BUY pick not yet logged:
       - Classify play_type -> entry rule (T1115_LIM or ATC_MKT)
       - Fetch today's 15m intraday via vnstock
       - Simulate fill (limit + fallback) AND baseline (09:15 OPEN market)
       - Log to paper_trade_entries.csv
  3. For open positions aged >= 5 trading days: compute short forward return check
  4. For open positions aged >= 45 trading days: simulate exit + finalize P&L

Usage:
  python paper_trade_daily.py               # daily run
  python paper_trade_daily.py --report      # print summary

Designed for Windows Task Scheduler — call after 14:50 (post-close).
"""
import os, sys, json, glob, argparse
from datetime import datetime, date, timedelta
import numpy as np
import pandas as pd

sys.path.insert(0, r"/home/trido/thanhdt/WorkingClaude/stockquery")
from stockquery_agent import StockQuery

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
ENTRIES_FILE = os.path.join(WORKDIR, "data/paper_trade_entries.csv")
EXITS_FILE = os.path.join(WORKDIR, "data/paper_trade_exits.csv")
LOG_FILE = os.path.join(WORKDIR, "paper_trade_log.txt")

# ---- Configuration ----
MAX_PICKS_PER_DAY = 5             # top-N picks per holistic
HOLD_DAYS = 45                    # BA-system avg hold
QUICK_CHECK_DAYS = 5              # short-horizon check
TC_PCT = 0.1                      # commission % per leg
STOP_PCT = -0.20                  # BA-system stop -20%
S2_DAYCHG_THR = -3.0              # S2 oversold trigger: day_chg <= -3%
S2_BOUNCE_MIN_PCT = 0.0           # last 30min close > 30-min-ago close

# Stop mode — backfill on real BA flow showed intraday stop has 40% FP rate
# (vs 17% in synthetic universe backtest), causing -5pp/event avg loss.
# Default: SHADOW only — log when it WOULD fire but don't exit. Build data over time.
# Options: "DISABLED", "SHADOW", "ACTIVE"
STOP_MODE = "SHADOW"

# Map play_type to entry rule
# For DEEP_VALUE_RECOVERY: try S2 anticipation FIRST (if triggers intraday), fallback ATC market
PLAY_RULE = {
    "COMPOUNDER_BUY":      "E1_T1115_LIM",
    "MOMENTUM_N":          "E1_T1115_LIM",
    "MOMENTUM_S":          "E1_T1115_LIM",
    "MOMENTUM_QUALITY":    "E1_T1115_LIM",
    "MOMENTUM":            "E1_T1115_LIM",
    "S_PRO":               "E1_T1115_LIM",
    "MEGA":                "E1_T1115_LIM",
    "DEEP_VALUE_RECOVERY": "E_S2_ANTICIPATE",   # S2 intraday trigger w/ ATC fallback
    "COMPOUNDER_HOLD":     "SKIP",   # not new BUY
    "WAIT":                "SKIP",
    "PASS":                "SKIP",
    "AVOID_faE":           "SKIP",
}

def log(msg):
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def find_holistic_for_exec(exec_date):
    """Return (filepath, signal_date) for holistic file dated strictly before exec_date.
       Look back up to 10 calendar days to handle weekends/holidays."""
    for offset in range(1, 11):
        d = exec_date - timedelta(days=offset)
        fp = os.path.join(WORKDIR, f"holistic_{d.strftime('%Y-%m-%d')}.csv")
        if os.path.exists(fp):
            return fp, d
    return None, None

def load_intraday_today(sq, ticker, target_date):
    """Fetch ~15 days of 15m bars and filter to target_date session."""
    end = pd.Timestamp(target_date)
    start = (end - pd.Timedelta(days=15)).strftime("%Y-%m-%d")
    sq.start_date = start
    sq.end_date = (end + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    df = sq.get_historical_symbol(ticker, interval="15m")
    if df is None or len(df)==0: return None
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)
    df_today = df[df["time"].dt.date == target_date].copy()
    if len(df_today) < 5: return None
    df_today["hhmm"] = df_today["time"].dt.strftime("%H:%M")
    # Require session to have completed (last bar at/after 14:30) — avoid mid-session false misses
    if df_today["hhmm"].max() < "14:30":
        return "INCOMPLETE"
    return df_today

def simulate_buy(bars, rule):
    """Returns (fill_price, slot_filled_idx, missed_flag, baseline_open)."""
    open_px = bars.iloc[0]["open"]
    atc_px = bars.iloc[-1]["close"]
    if rule == "E0_OPEN_MKT":
        return open_px, 0, False, open_px
    if rule == "E3_ATC_MKT":
        return atc_px, len(bars)-1, False, open_px
    if rule == "E1_T1115_LIM":
        times = bars["hhmm"].values
        idx_arr = np.where(times >= "11:15")[0]
        if len(idx_arr)==0 or idx_arr[0] >= len(bars)-1:
            return atc_px, len(bars)-1, True, open_px
        i = idx_arr[0]
        limit = bars.iloc[i]["close"]
        for j in range(i+1, len(bars)):
            if bars.iloc[j]["low"] <= limit:
                return limit, j, False, open_px
        return atc_px, len(bars)-1, True, open_px
    if rule == "E_S2_ANTICIPATE":
        # Tuned S2: day_chg<=-3% AND last 30min bounce>0
        b = bars.reset_index(drop=True).copy()
        sopen = b["open"].iloc[0]
        b["day_chg"] = (b["close"]/sopen - 1)*100
        b["close_2ago"] = b["close"].shift(2)
        b["bounce_30m"] = (b["close"]/b["close_2ago"] - 1)*100
        for k in range(len(b)):
            if k < 3: continue
            row = b.iloc[k]
            if (row["day_chg"] <= S2_DAYCHG_THR
                and pd.notna(row["bounce_30m"]) and row["bounce_30m"] > S2_BOUNCE_MIN_PCT):
                return float(row["close"]), k, False, open_px
        # no trigger today, fallback ATC market
        return atc_px, len(bars)-1, True, open_px
    return None, None, False, open_px

def simulate_sell(bars, rule):
    open_px = bars.iloc[0]["open"]
    atc_px = bars.iloc[-1]["close"]
    if rule == "X0_OPEN_MKT":
        return open_px, 0, False
    if rule == "X2_ATC_MKT":
        return atc_px, len(bars)-1, False
    if rule == "X1_T0945_LIM":
        times = bars["hhmm"].values
        idx_arr = np.where(times >= "09:45")[0]
        if len(idx_arr)==0 or idx_arr[0] >= len(bars)-1:
            return atc_px, len(bars)-1, True
        i = idx_arr[0]
        limit = bars.iloc[i]["close"]
        for j in range(i+1, len(bars)):
            if bars.iloc[j]["high"] >= limit:
                return limit, j, False
        # miss -> next-day OPEN proxy (use ATC of today for now)
        return atc_px, len(bars)-1, True

def is_trading_day(sq, d):
    """Check if d is a trading day by trying to fetch any well-known ticker."""
    try:
        sq.start_date = (d - timedelta(days=3)).strftime("%Y-%m-%d")
        sq.end_date = (d + timedelta(days=1)).strftime("%Y-%m-%d")
        df = sq.get_historical_symbol("VNM", interval="15m")
        if df is None: return False
        df["time"] = pd.to_datetime(df["time"])
        return (df["time"].dt.date == d).any()
    except:
        return False

def entry_phase(sq, today):
    """Process new BUY picks. signal_date = T-1 trading day, exec_date = today."""
    holistic, signal_date = find_holistic_for_exec(today)
    if not holistic:
        log(f"No holistic recommendation file dated before {today}, skipping entry phase")
        return
    file_date = signal_date.strftime("%Y-%m-%d")
    log(f"Using holistic recommendations: {os.path.basename(holistic)} (signal date: {file_date}; exec date: {today})")

    df = pd.read_csv(holistic)
    if "play_type" not in df.columns:
        log(f"  {os.path.basename(holistic)} missing play_type col, skip")
        return

    # filter to BUY-worthy picks
    df = df[df["play_type"].map(lambda p: PLAY_RULE.get(p, "SKIP")) != "SKIP"].copy()
    df = df.sort_values(["conviction","ta_score"], ascending=False).head(MAX_PICKS_PER_DAY)
    log(f"  {len(df)} BUY candidates today: {df['ticker'].tolist()}")

    # idempotency: don't re-enter
    if os.path.exists(ENTRIES_FILE):
        existing = pd.read_csv(ENTRIES_FILE)
        already = set(zip(existing["signal_date"], existing["ticker"]))
    else:
        already = set()

    new_rows = []
    for _, r in df.iterrows():
        key = (file_date, r["ticker"])
        if key in already:
            log(f"  {r['ticker']}: already logged for {file_date}, skip")
            continue
        rule = PLAY_RULE.get(r["play_type"], "E1_T1115_LIM")
        log(f"  {r['ticker']} ({r['play_type']}): rule={rule}")
        bars = load_intraday_today(sq, r["ticker"], today)
        if isinstance(bars, str) and bars == "INCOMPLETE":
            log(f"    Session not complete yet (run again after 14:50) -- skip")
            continue
        if bars is None or len(bars) < 5:
            log(f"    NO intraday data -- skip")
            continue
        # simulate fill under rule
        fill, slot_i, missed, baseline_open = simulate_buy(bars, rule)
        atc_px = bars.iloc[-1]["close"]
        new_rows.append({
            "signal_date": file_date,
            "exec_date": today.strftime("%Y-%m-%d"),
            "ticker": r["ticker"],
            "play_type": r["play_type"],
            "conviction": r.get("conviction", None),
            "ta_score": r.get("ta_score", None),
            "rule": rule,
            "fill_price": round(fill,3),
            "fill_slot_idx": int(slot_i) if slot_i is not None else None,
            "missed": int(missed),
            "baseline_open_price": round(baseline_open,3),
            "atc_close_price": round(atc_px,3),
            "day_low": round(bars["low"].min(),3),
            "day_high": round(bars["high"].max(),3),
            "n_bars": len(bars),
        })
        log(f"    fill={fill:.3f} (vs OPEN={baseline_open:.3f}, ATC={atc_px:.3f}), missed={missed}")

    if new_rows:
        out = pd.DataFrame(new_rows)
        if os.path.exists(ENTRIES_FILE):
            existing = pd.read_csv(ENTRIES_FILE)
            out = pd.concat([existing, out], ignore_index=True)
        out.to_csv(ENTRIES_FILE, index=False)
        log(f"  Logged {len(new_rows)} new entries -> {ENTRIES_FILE}")

def quick_check_and_exit_phase(sq, today):
    """For open positions:
        - age >= QUICK_CHECK_DAYS: record T+5 close check
        - age >= HOLD_DAYS: simulate exit + finalize P&L
    """
    if not os.path.exists(ENTRIES_FILE):
        return
    entries = pd.read_csv(ENTRIES_FILE)
    if not len(entries): return
    entries["exec_date"] = pd.to_datetime(entries["exec_date"]).dt.date

    closed_tickers_dates = set()
    if os.path.exists(EXITS_FILE):
        closed = pd.read_csv(EXITS_FILE)
        closed_tickers_dates = set(zip(closed["exec_date"], closed["ticker"]))

    new_exits = []
    for _, e in entries.iterrows():
        if (str(e["exec_date"]), e["ticker"]) in closed_tickers_dates: continue
        age_calendar = (today - e["exec_date"]).days
        if age_calendar < 1:  # not yet had a chance to trade
            continue
        bars = load_intraday_today(sq, e["ticker"], today)
        if bars is None or isinstance(bars, str):
            continue
        # ---- STOP-LOSS check ----
        # NOTE: backfill on real BA-system flow showed intraday stop has high FP rate (40%)
        # vs synthetic backtest (17%). Default mode = SHADOW: log but don't exit.
        # Real exit happens via journal-style EoD-close stop OR TIME exit.
        stop_lvl = e["fill_price"] * (1 + STOP_PCT)
        intraday_low = float(bars["low"].min())
        eod_close = float(bars.iloc[-1]["close"])
        baseline_open = float(bars.iloc[0]["open"])
        intraday_hit = intraday_low <= stop_lvl
        eod_hit = eod_close <= stop_lvl

        # Always log shadow stop event (TP/FP analysis later)
        if intraday_hit:
            log(f"  SHADOW STOP {e['ticker']} age={age_calendar}d: intraday_low={intraday_low:.3f} <= stop={stop_lvl:.3f}, "
                f"eod_close={eod_close:.3f}, eod_confirms={'YES' if eod_hit else 'NO (would be FP)'}, mode={STOP_MODE}")

        if STOP_MODE == "ACTIVE" and intraday_hit:
            # exit at stop level intraday (the risky rule)
            exit_px = stop_lvl
            gross = (exit_px/e["fill_price"] - 1)*100
            gross_baseline = (eod_close/e["fill_price"] - 1)*100
            net = gross - 2*TC_PCT
            net_baseline = gross_baseline - 2*TC_PCT
            new_exits.append({
                "signal_date": e["signal_date"], "exec_date": str(e["exec_date"]),
                "exit_date": today.strftime("%Y-%m-%d"),
                "ticker": e["ticker"], "rule_in": e["rule"],
                "exit_type": "STOP_INTRADAY_ACTIVE",
                "fill_price": e["fill_price"], "exit_price": round(exit_px,3),
                "exit_missed": 0, "age_calendar_days": age_calendar,
                "intraday_low": round(intraday_low,3), "eod_close_today": round(eod_close,3),
                "eod_confirms_stop": int(eod_hit),
                "gross_ret_pct": round(gross,3), "net_ret_pct": round(net,3),
                "baseline_open_in": e["baseline_open_price"],
                "baseline_open_out": round(baseline_open,3),
                "baseline_net_ret_pct": round(net_baseline,3),
                "lift_vs_baseline_pp": round(net - net_baseline,3),
            })
            continue
        if eod_hit:
            # EoD-confirmed stop → exit at next-day OPEN (T+1 execution)
            # For paper, log shadow event; actual exit will be next session
            exit_px = eod_close  # proxy for next-day open
            gross = (exit_px/e["fill_price"] - 1)*100
            net = gross - 2*TC_PCT
            new_exits.append({
                "signal_date": e["signal_date"], "exec_date": str(e["exec_date"]),
                "exit_date": today.strftime("%Y-%m-%d"),
                "ticker": e["ticker"], "rule_in": e["rule"],
                "exit_type": "STOP_EOD_CONFIRMED",
                "fill_price": e["fill_price"], "exit_price": round(exit_px,3),
                "exit_missed": 0, "age_calendar_days": age_calendar,
                "intraday_low": round(intraday_low,3), "eod_close_today": round(eod_close,3),
                "eod_confirms_stop": 1,
                "gross_ret_pct": round(gross,3), "net_ret_pct": round(net,3),
                "baseline_open_in": e["baseline_open_price"],
                "baseline_open_out": round(baseline_open,3),
                "baseline_net_ret_pct": round(net,3),
                "lift_vs_baseline_pp": 0.0,
            })
            log(f"  STOP EOD-CONFIRMED {e['ticker']} age={age_calendar}d: eod_close={eod_close:.3f} <= stop={stop_lvl:.3f}, exit_net={net:.2f}%")
            continue
        # ---- Time-based exit at HOLD_DAYS ----
        if age_calendar < HOLD_DAYS - 5:
            continue
        # exit at X1_T0945_LIM
        exit_px, slot_i, missed = simulate_sell(bars, "X1_T0945_LIM")
        baseline_open = bars.iloc[0]["open"]
        gross = (exit_px/e["fill_price"] - 1)*100
        gross_baseline = (baseline_open/e["baseline_open_price"] - 1)*100
        net = gross - 2*TC_PCT
        net_baseline = gross_baseline - 2*TC_PCT
        new_exits.append({
            "signal_date": e["signal_date"],
            "exec_date": str(e["exec_date"]),
            "exit_date": today.strftime("%Y-%m-%d"),
            "ticker": e["ticker"], "rule_in": e["rule"],
            "exit_type": "TIME_HOLD",
            "fill_price": e["fill_price"], "exit_price": round(exit_px,3),
            "stop_bar_idx": None, "exit_missed": int(missed),
            "age_calendar_days": age_calendar,
            "gross_ret_pct": round(gross,3), "net_ret_pct": round(net,3),
            "baseline_open_in": e["baseline_open_price"],
            "baseline_open_out": round(baseline_open,3),
            "eod_close_today": round(bars.iloc[-1]["close"],3),
            "baseline_net_ret_pct": round(net_baseline,3),
            "lift_vs_baseline_pp": round(net - net_baseline,3),
        })
        log(f"  TIME EXIT {e['ticker']} age={age_calendar}d: rule_net={net:.2f}%  baseline_net={net_baseline:.2f}%  lift={net-net_baseline:+.2f}pp")

    if new_exits:
        out = pd.DataFrame(new_exits)
        if os.path.exists(EXITS_FILE):
            existing = pd.read_csv(EXITS_FILE)
            out = pd.concat([existing, out], ignore_index=True)
        out.to_csv(EXITS_FILE, index=False)
        log(f"  Logged {len(new_exits)} exits -> {EXITS_FILE}")

def report():
    """Summary of paper-trade results so far."""
    print("\n" + "="*80); print("PAPER-TRADE SUMMARY"); print("="*80)
    if not os.path.exists(ENTRIES_FILE):
        print("No entries logged yet."); return
    e = pd.read_csv(ENTRIES_FILE)
    print(f"\nEntries logged: {len(e)}")
    print(f"Date range: {e['exec_date'].min()} -> {e['exec_date'].max()}")
    print(f"Rule distribution: {e['rule'].value_counts().to_dict()}")
    print(f"Miss rate: {e['missed'].mean()*100:.2f}% ({e['missed'].sum()} / {len(e)})")
    # fill quality vs baseline (for limit orders)
    e["fill_save_pct"] = (e["baseline_open_price"] - e["fill_price"]) / e["baseline_open_price"] * 100
    print(f"\nFill price savings vs OPEN baseline (per entry):")
    print(e.groupby("rule")["fill_save_pct"].agg(["count","mean","median","std"]).round(3).to_string())

    if os.path.exists(EXITS_FILE):
        x = pd.read_csv(EXITS_FILE)
        print(f"\nExits completed: {len(x)}")
        print(f"Mean net return rule:     {x['net_ret_pct'].mean():.3f}%")
        print(f"Mean net return baseline: {x['baseline_net_ret_pct'].mean():.3f}%")
        print(f"Mean lift:                {x['lift_vs_baseline_pp'].mean():+.3f}pp")
        print(f"Lift hit rate (rule > baseline): {(x['lift_vs_baseline_pp']>0).mean()*100:.1f}%")
    else:
        print("\nNo completed roundtrips yet (need 45 trading days hold).")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--report", action="store_true", help="Print summary and exit")
    p.add_argument("--date", default=None, help="Override today (YYYY-MM-DD) for backfill")
    args = p.parse_args()

    if args.report:
        report(); return

    today = pd.Timestamp(args.date).date() if args.date else date.today()
    log(f"=== Paper-trade daily run for {today} ===")

    sq = StockQuery()
    if not is_trading_day(sq, today):
        log(f"{today} is not a trading day (no intraday for VNM), skip")
        return

    entry_phase(sq, today)
    quick_check_and_exit_phase(sq, today)
    log(f"=== Done ===\n")

if __name__=="__main__":
    main()
