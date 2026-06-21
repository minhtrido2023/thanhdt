# -*- coding: utf-8 -*-
"""
shadow_track_v3_4b.py
=====================
Daily shadow tracker for Tam Quan v3.4b "Định Tâm" (STAGING NEXT).

Run daily (e.g. 15:30 after market close) for 2 weeks before promote-to-live.

Each run:
  1. Pulls today's state from BQ `tav2_bq.vnindex_5state` (LIVE = Tinh Tế)
     and `tav2_bq.vnindex_5state_tam_quan_v34b_clean` (STAGING NEXT)
  2. Reports today's state diff (and history of all diffs in the shadow window)
  3. Computes cumulative VN-Index alpha if user had switched to v3.4b
  4. Appends today's snapshot to shadow_log_v3_4b.csv

Promote decision criteria (after 2 weeks):
  - No catastrophic divergence (v3.4b cum alpha vs LIVE within [-3%, +3%])
  - Gate fires count > 0 (rule is firing on real signals)
  - No sustained bull-psychology failure mode (per feedback_bull_market_psychology)

Usage:
  python shadow_track_v3_4b.py             # daily report
  python shadow_track_v3_4b.py --backfill  # rebuild log from start_date
"""
import sys, io, os, subprocess, argparse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
from datetime import datetime, timedelta

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
BQ = r"bq"
PROJECT = "lithe-record-440915-m9"

STATE_NAMES = {1:"CRISIS", 2:"BEAR", 3:"NEUTRAL", 4:"BULL", 5:"EX-BULL"}
STATE_WEIGHT = {1:0.0, 2:0.2, 3:0.7, 4:1.0, 5:1.3}

SHADOW_START = pd.Timestamp("2026-05-21")   # day v3.4b promoted to STAGING NEXT
SHADOW_END   = pd.Timestamp("2026-06-04")   # +2 weeks
LOG_FILE     = os.path.join(WORKDIR, "data/shadow_log_v3_4b.csv")

def bq_query(sql):
    # Use stdin for SQL — avoids Windows cmd quoting issues
    cmd = f'"{BQ}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=100000'
    result = subprocess.run(cmd, input=sql, capture_output=True, text=True,
                            timeout=120, shell=True)
    if result.returncode != 0:
        raise RuntimeError(f"BQ error: {result.stderr or '(no stderr)'} | stdout: {result.stdout[:200]}")
    from io import StringIO
    if not result.stdout.strip():
        return pd.DataFrame()
    return pd.read_csv(StringIO(result.stdout))


def fetch_states_and_close(start_d, end_d):
    """Pull v3.1 LIVE, v3.4b STAGING, and VNINDEX close for date range."""
    sql = f"""
    SELECT live.time, live.state AS state_live,
           v34b.state AS state_v34b, t.Close
    FROM tav2_bq.vnindex_5state AS live
    LEFT JOIN tav2_bq.vnindex_5state_tam_quan_v34b_clean AS v34b ON v34b.time = live.time
    LEFT JOIN tav2_bq.ticker AS t ON t.time = live.time AND t.ticker = 'VNINDEX'
    WHERE live.time BETWEEN DATE '{start_d}' AND DATE '{end_d}'
    ORDER BY live.time
    """
    df = bq_query(sql)
    df["time"] = pd.to_datetime(df["time"])
    return df


def simulate_nav_pair(df, init=1e9, tc=0.001):
    """Compute paper NAV for both state series, capital-allocation only."""
    n = len(df); close = df["Close"].values
    ret = np.zeros(n); ret[1:] = close[1:]/close[:-1] - 1
    out = df.copy()
    for col in ["live", "v34b"]:
        state_col = f"state_{col}"
        target_w = df[state_col].map(STATE_WEIGHT).values
        pv = np.zeros(n); w = np.zeros(n); pv[0]=init; w[0]=target_w[0]
        for t in range(1, n):
            tgt = target_w[t]; w_new = tgt  # snap (shadow only — no ramp)
            trade = abs(w_new - w[t-1])
            daily = w_new * ret[t] - trade*tc
            pv[t] = pv[t-1]*(1+daily); w[t] = w_new
        out[f"nav_{col}"] = pv
    out["alpha_pct"] = (out["nav_v34b"] / out["nav_live"] - 1) * 100
    return out


def report(df_shadow):
    """Print summary of shadow window."""
    n = len(df_shadow); last = df_shadow.iloc[-1]
    print("="*80)
    print(f"📡 Shadow track Tam Quan v3.4b — report {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*80)
    print(f"Window: {df_shadow['time'].iloc[0].date()} → {df_shadow['time'].iloc[-1].date()}  ({n} sessions)")
    print(f"\n📅 Today ({last['time'].date()}):")
    sl = int(last["state_live"]); sv = int(last["state_v34b"])
    sl_name = STATE_NAMES.get(sl,"?"); sv_name = STATE_NAMES.get(sv,"?")
    diff = "🟢 SAME" if sl == sv else f"🟠 DIFF ({sl_name} vs {sv_name})"
    print(f"  LIVE Tinh Tế:  {sl_name} ({sl})    weight {STATE_WEIGHT[sl]:.0%}")
    print(f"  v3.4b Định Tâm: {sv_name} ({sv})    weight {STATE_WEIGHT[sv]:.0%}")
    print(f"  → {diff}")

    # Count diff sessions
    n_diff = int((df_shadow["state_live"] != df_shadow["state_v34b"]).sum())
    print(f"\n📊 Shadow window statistics:")
    print(f"  Sessions with state diff: {n_diff}/{n}  ({n_diff/n*100:.0f}%)")
    print(f"  Cumulative alpha (v3.4b vs LIVE): {last['alpha_pct']:+.2f}%")
    final_live = last["nav_live"]/1e9; final_v34b = last["nav_v34b"]/1e9
    print(f"  Paper NAV (1B init): LIVE {final_live:.3f}B  |  v3.4b {final_v34b:.3f}B")

    # Days with diff
    diff_df = df_shadow[df_shadow["state_live"] != df_shadow["state_v34b"]]
    if len(diff_df) > 0:
        print(f"\n📋 Days with state diff (last 10):")
        for _, r in diff_df.tail(10).iterrows():
            sl = STATE_NAMES.get(int(r["state_live"]),"?")
            sv = STATE_NAMES.get(int(r["state_v34b"]),"?")
            print(f"  {r['time'].date()}: LIVE {sl:<8}  v3.4b {sv:<8}  (alpha: {r['alpha_pct']:+.2f}%)")

    # Decision guidance
    days_into_shadow = (last["time"] - SHADOW_START).days
    days_remaining = max(0, (SHADOW_END - last["time"]).days)
    print(f"\n🎯 Shadow progress: day {days_into_shadow}/14  ({days_remaining} days remaining)")
    if days_remaining == 0:
        print(f"  ▶ DECISION POINT REACHED. Promote criteria:")
        cum_alpha = last["alpha_pct"]
        if -3.0 <= cum_alpha <= 3.0:
            print(f"    ✓ Cum alpha {cum_alpha:+.2f}% within [-3%, +3%]")
        else:
            print(f"    ✗ Cum alpha {cum_alpha:+.2f}% OUT OF [-3%, +3%] — investigate before promote")
        if n_diff > 0:
            print(f"    ✓ Gate fires confirmed ({n_diff} diff sessions)")
        else:
            print(f"    ⚠ No diff yet — gate hasn't fired, can't validate behavior")
    print("="*80)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backfill", action="store_true", help="Rebuild log from SHADOW_START")
    ap.add_argument("--start", help="Override start date (YYYY-MM-DD)")
    ap.add_argument("--end", help="Override end date (YYYY-MM-DD), default=today")
    args = ap.parse_args()

    start_d = pd.Timestamp(args.start) if args.start else SHADOW_START
    end_d   = pd.Timestamp(args.end)   if args.end   else pd.Timestamp(datetime.now().date())

    print(f"Fetching states + close: {start_d.date()} → {end_d.date()} ...")
    df = fetch_states_and_close(start_d.date(), end_d.date())
    if df.empty:
        print("⚠ No data returned — BQ may be empty for this range")
        return
    df_nav = simulate_nav_pair(df)
    df_nav.to_csv(LOG_FILE, index=False)
    print(f"  Saved {len(df_nav)} sessions → {LOG_FILE}")
    report(df_nav)


if __name__ == "__main__":
    main()
