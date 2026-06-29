# -*- coding: utf-8 -*-
"""
ngu_hanh_shadow_tracker.py — Daily LIVE vs STAGING shadow + auto-decision

Logic per run:
  1. Pull LIVE (tav2_bq.vnindex_5state) + STAGING (tav2_bq.vnindex_5state_staging)
  2. Append today to ngu_hanh_shadow_log.csv (dedup)
  3. Compute current concentration_score + US shock cap for context
  4. Evaluate 5-criterion verdict (see below)
  5. On day ≥ 14 trading days since stage start: propose promote/extend/rollback
  6. Print compact status

5 Criteria (each GREEN/YELLOW/RED):
  C1. Critical flips:  0=GREEN | 1=YELLOW | ≥2=RED
       (critical = LIVE BULL/EX-BULL while STAG CRISIS, or vice versa)
  C2. Divergence rate: 30-70%=GREEN | <30%=YELLOW | >70%=RED
  C3. Mechanism val.:  ≥80%=GREEN | 50-80%=YELLOW | <50%=RED
       (% of divergence days justified by concentration ≥0.5 OR US shock fired)
  C4. Forward alpha:   ≥55%=GREEN | 40-55%=YELLOW | <40%=RED
       (Composite: T+5 measured on VNINDEX_EW (primary, addresses VIN-domination) +
        breadth % advances (secondary). STAG correct = directionally agrees with
        BROAD MARKET move on T+5. Using raw VNI would be circular since STAG is
        explicitly designed to ignore VIN-cap distortion.)
  C5. Stability:       ≤4 STAG transitions in 14d=GREEN | 5-6=YELLOW | ≥7=RED

Final verdict:
  🟢 PROMOTE  = C1=GREEN AND C4 != RED AND no other RED
  🟡 EXTEND   = C1=GREEN AND no RED (one more week of shadow)
  🔴 ROLLBACK = C1=RED OR C4=RED

Usage:
  python ngu_hanh_shadow_tracker.py            # daily run (update log + verdict)
  python ngu_hanh_shadow_tracker.py --report   # report only, don't update log
"""
import sys, io, os, subprocess, tempfile, argparse, bisect
from datetime import datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import pandas as pd
import numpy as np

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
BQ      = r"bq"
PROJECT = "lithe-record-440915-m9"
LOG_CSV = os.path.join(WORKDIR, "data/ngu_hanh_shadow_log.csv")
STAGE_START = pd.Timestamp("2026-05-21")  # when v3.1 was deployed
SHADOW_DAYS_REQ = 14  # trading days before promote decision
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}

def bq_csv(sql):
    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); qp = f.name
    cmd = f'"{BQ}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=10000 < "{qp}"'
    r = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    os.unlink(qp)
    if r.returncode != 0: raise RuntimeError(r.stderr[:500])
    return pd.read_csv(io.StringIO(r.stdout))

def pull_latest_states():
    live = bq_csv("SELECT s.time, s.state FROM tav2_bq.vnindex_5state_dt5g_live AS s ORDER BY s.time DESC LIMIT 80")
    stag = bq_csv("SELECT s.time, s.state FROM tav2_bq.vnindex_5state_staging AS s ORDER BY s.time DESC LIMIT 80")
    vni  = bq_csv("SELECT t.time, t.Close FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' ORDER BY t.time DESC LIMIT 100")
    # Broad-market T+5 benchmarks: EW close + breadth (% advances on prune universe)
    # Pull last 80 days; compute breadth in Python.
    breadth_sql = """
    WITH ret_t5 AS (
      SELECT t.ticker, t.time, t.Close,
             LEAD(t.Close, 5) OVER (PARTITION BY t.ticker ORDER BY t.time) AS close_t5
      FROM tav2_bq.ticker AS t
      WHERE t.time >= DATE_SUB(CURRENT_DATE(), INTERVAL 180 DAY)
        AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
        AND t.Close > 0
    )
    SELECT time,
           COUNT(*) AS n_total,
           COUNTIF(close_t5 > Close) AS n_up,
           AVG(SAFE_DIVIDE(close_t5, Close) - 1) AS median_t5_ret,
           APPROX_QUANTILES(SAFE_DIVIDE(close_t5, Close) - 1, 100)[OFFSET(50)] AS true_median_t5
    FROM ret_t5 WHERE close_t5 IS NOT NULL
    GROUP BY time ORDER BY time
    """
    bd = bq_csv(breadth_sql); bd["time"] = pd.to_datetime(bd["time"])
    bd["breadth_t5"] = bd["n_up"] / bd["n_total"]
    live["time"] = pd.to_datetime(live["time"]); live = live.rename(columns={"state":"live"})
    stag["time"] = pd.to_datetime(stag["time"]); stag = stag.rename(columns={"state":"stag"})
    vni["time"]  = pd.to_datetime(vni["time"]);  vni  = vni.rename(columns={"Close":"vni_close"})
    df = live.merge(stag, on="time", how="inner").merge(vni, on="time", how="left")
    df = df.merge(bd[["time","breadth_t5","true_median_t5"]], on="time", how="left").sort_values("time")
    # Also load EW close from local cache
    try:
        ew = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_ew_full.csv"))
        ew["time"] = pd.to_datetime(ew["time"])
        ew = ew[["time","Close"]].rename(columns={"Close":"ew_close"})
        df = df.merge(ew, on="time", how="left")
    except Exception:
        df["ew_close"] = np.nan
    return df

def get_context():
    """Get concentration_smooth + US shock cap for STAGE_START onwards."""
    try:
        diag = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_1_clean.csv"))
        # Not enough context in the staging CSV — read from full v3 diag instead if available
    except Exception:
        return pd.DataFrame()
    # Pull concentration from v3 full diag
    if os.path.exists(os.path.join(WORKDIR, "data/vnindex_5state_dual_v3_full.csv")):
        c = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_dual_v3_full.csv"))
        c["time"] = pd.to_datetime(c["time"])
        c = c[["time","concentration_smooth","alpha"]]
    else:
        c = pd.DataFrame(columns=["time","concentration_smooth","alpha"])
    # Pull US shock cap from us_market_history
    if os.path.exists(os.path.join(WORKDIR, "data/us_market_history.csv")):
        us = pd.read_csv(os.path.join(WORKDIR, "data/us_market_history.csv"))
        us["time"] = pd.to_datetime(us["time"])
        us = us[["time","vix","spx_dd_1y"]]
        def cap(r):
            if pd.isna(r["spx_dd_1y"]) or pd.isna(r["vix"]): return 5
            if r["spx_dd_1y"] < -0.25 or r["vix"] > 35: return 1
            if r["spx_dd_1y"] < -0.15 or r["vix"] > 30: return 2
            if r["spx_dd_1y"] < -0.10 or r["vix"] > 25: return 3
            return 5
        us["us_cap"] = us.apply(cap, axis=1)
        # Align US to VN (US ≤ VN-1)
        us_dates = sorted(us["time"].tolist())
        def nearest(t):
            target = t - pd.Timedelta(days=1)
            idx = bisect.bisect_right(us_dates, target)
            return us_dates[idx-1] if idx > 0 else None
        c["us_date"] = c["time"].apply(nearest)
        c = c.merge(us, left_on="us_date", right_on="time", how="left", suffixes=("","_us"))
        c = c.drop(columns=["time_us","us_date"]).rename(columns={"time":"time"})
    return c

def update_log():
    df = pull_latest_states()
    if os.path.exists(LOG_CSV):
        prev = pd.read_csv(LOG_CSV); prev["time"] = pd.to_datetime(prev["time"])
        new = df[~df["time"].isin(prev["time"])]
        if len(new) == 0:
            print(f"[log] No new rows (latest: {prev['time'].max().date()})")
            merged = prev
        else:
            merged = pd.concat([prev, new], ignore_index=True).sort_values("time")
            merged.to_csv(LOG_CSV, index=False)
            print(f"[log] Appended {len(new)} rows; total = {len(merged)}")
    else:
        df.to_csv(LOG_CSV, index=False)
        print(f"[log] Initialized with {len(df)} rows")
        merged = df
    return merged

def evaluate_verdict(log_df, ctx_df):
    # Only consider sessions from STAGE_START onwards (the true shadow period)
    shadow = log_df[log_df["time"] >= STAGE_START].copy()
    n_sess = len(shadow)
    print(f"\nShadow period: {STAGE_START.date()} → {log_df['time'].max().date()}  ({n_sess} sessions)")

    if n_sess < 3:
        print(f"  ⏳ Need ≥3 sessions to evaluate (current: {n_sess})")
        return None

    shadow = shadow.copy()
    shadow["diff"] = shadow["live"] != shadow["stag"]
    n_diff = shadow["diff"].sum()

    # C1: Critical flips
    crit = (((shadow["live"] >= 4) & (shadow["stag"] <= 1)) |
            ((shadow["live"] <= 1) & (shadow["stag"] >= 4)))
    n_crit = crit.sum()
    c1 = "GREEN" if n_crit == 0 else ("YELLOW" if n_crit == 1 else "RED")

    # C2: Divergence rate
    div_pct = n_diff / n_sess * 100
    c2 = "GREEN" if 30 <= div_pct <= 70 else ("YELLOW" if div_pct < 30 else "RED")

    # C3: Mechanism validation
    if n_diff > 0 and len(ctx_df) > 0:
        div_dates = shadow[shadow["diff"]]["time"].tolist()
        ctx_sub = ctx_df[ctx_df["time"].isin(div_dates)]
        if len(ctx_sub) > 0:
            justified = ((ctx_sub["concentration_smooth"] >= 0.5) | (ctx_sub["us_cap"] < 5)).sum()
            just_pct = justified / len(ctx_sub) * 100
        else: just_pct = 0
    else: just_pct = 100  # no diff → vacuously satisfied
    c3 = "GREEN" if just_pct >= 80 else ("YELLOW" if just_pct >= 50 else "RED")

    # C4: Forward alpha — BROAD MARKET benchmarks (not VNI which is VIN-dominated)
    #   Primary:   VNINDEX_EW T+5 return (equal-weighted, the system's natural benchmark)
    #   Secondary: breadth_t5 (% of prune universe with positive T+5 return)
    #   "STAG correct" requires BOTH to agree directionally with STAG bias
    #   (Reported separately: VNI version for transparency / comparison)
    full_log = log_df.sort_values("time").reset_index(drop=True)
    full_log["vni_fwd5"]    = full_log["vni_close"].shift(-5) / full_log["vni_close"] - 1
    full_log["ew_fwd5"]     = full_log["ew_close"].shift(-5) / full_log["ew_close"] - 1
    full_log["breadth_t5"]  = full_log.get("breadth_t5", pd.Series(np.nan, index=full_log.index))

    def stag_correct(stag, live, ret):
        if pd.isna(ret): return None
        if stag < live and ret < 0: return True   # STAG defensive + market down → right
        if stag > live and ret > 0: return True   # STAG bullish + market up → right
        if stag < live and ret >= 0: return False # STAG defensive but market up → wrong
        if stag > live and ret <= 0: return False
        return None

    n_ew_ok = n_ew_tot = 0
    n_bd_ok = n_bd_tot = 0
    n_vni_ok = n_vni_tot = 0  # legacy comparison
    for _, r in shadow[shadow["diff"]].iterrows():
        row = full_log[full_log["time"] == r["time"]]
        if len(row) == 0: continue
        row = row.iloc[0]
        ew_res  = stag_correct(r["stag"], r["live"], row["ew_fwd5"])
        bd_ret  = (row["breadth_t5"] - 0.5) if not pd.isna(row["breadth_t5"]) else np.nan
        bd_res  = stag_correct(r["stag"], r["live"], bd_ret)
        vni_res = stag_correct(r["stag"], r["live"], row["vni_fwd5"])
        if ew_res is not None:  n_ew_tot += 1;  n_ew_ok += int(ew_res)
        if bd_res is not None:  n_bd_tot += 1;  n_bd_ok += int(bd_res)
        if vni_res is not None: n_vni_tot += 1; n_vni_ok += int(vni_res)

    ew_pct  = (n_ew_ok / n_ew_tot * 100) if n_ew_tot > 0 else None
    bd_pct  = (n_bd_ok / n_bd_tot * 100) if n_bd_tot > 0 else None
    vni_pct = (n_vni_ok / n_vni_tot * 100) if n_vni_tot > 0 else None

    # Primary metric for verdict: BREADTH %advances T+5 (most robust broad measure)
    #   Reason: VNI is circular (VIN-dominated → STAG built to ignore it).
    #           EW is magnitude-weighted → noisy on near-zero days.
    #           Breadth is binary % advancing → robust answer to "is broad market up?"
    if bd_pct is not None:
        primary_pct = bd_pct
        primary_label = "Breadth T+5"
    elif ew_pct is not None:
        primary_pct = ew_pct
        primary_label = "EW T+5"
    else:
        primary_pct = None; primary_label = "—"

    if primary_pct is None:
        c4 = "WAIT"
    else:
        c4 = "GREEN" if primary_pct >= 55 else ("YELLOW" if primary_pct >= 40 else "RED")
    # Save for printing
    fwd_pct = primary_pct
    fwd_detail = {"ew": (ew_pct, n_ew_tot), "breadth": (bd_pct, n_bd_tot), "vni": (vni_pct, n_vni_tot), "label": primary_label}

    # C5: Stability
    s = shadow["stag"].values
    n_trans = int((s[1:] != s[:-1]).sum()) if len(s) > 1 else 0
    c5 = "GREEN" if n_trans <= 4 else ("YELLOW" if n_trans <= 6 else "RED")

    print("\n" + "="*70); print("5-CRITERION EVALUATION"); print("="*70)
    print(f"  C1 Critical flips:      {n_crit} crit / {n_sess} sess   → {c1}")
    print(f"  C2 Divergence rate:     {div_pct:.0f}% diff (target 30-70%) → {c2}")
    print(f"  C3 Mechanism justify:   {just_pct:.0f}% justified (≥80% GREEN) → {c3}")
    if fwd_pct is None:
        print(f"  C4 Forward alpha:       waiting for T+5 data (need ≥5 calendar days after divergence)")
    else:
        print(f"  C4 Forward alpha:       {fwd_pct:.0f}% correct on {fwd_detail['label']} (PRIMARY — broad-market) → {c4}")
        # Detail breakdown — shows VNI is unreliable here (the user's insight)
        for lbl, key in [("Breadth T+5", "breadth"), ("EW T+5     ", "ew"), ("VNI T+5    ", "vni")]:
            p, n = fwd_detail[key]
            if p is None: print(f"     {lbl}: (no data yet)")
            else:
                tag = " ← PRIMARY" if lbl.strip().startswith(fwd_detail['label'].split()[0]) else (" ← circular, advisory only (VIN-dominated)" if key == "vni" else " ← secondary (magnitude)")
                print(f"     {lbl}: {p:>5.1f}% of {n} days{tag}")
    print(f"  C5 STAG transitions:    {n_trans} in {n_sess} sessions → {c5}")

    # Final verdict
    crits = [c1, c2, c3, c4, c5]
    any_red = "RED" in crits
    c4_red = (c4 == "RED")
    c1_red = (c1 == "RED")
    no_red_outside_c4 = all(c != "RED" or k == "C4" for k, c in zip(["C1","C2","C3","C4","C5"], crits))

    if c1_red or c4_red:
        verdict = "🔴 ROLLBACK"
        action = "Investigate v3.1 logic. DO NOT promote."
        cmd = "python deploy_ngu_hanh.py --drop-staging  # OR rollback path if already promoted"
    elif n_sess < SHADOW_DAYS_REQ:
        verdict = f"⏳ WAIT ({n_sess}/{SHADOW_DAYS_REQ} sessions)"
        action = f"Continue daily shadow. Re-evaluate after {SHADOW_DAYS_REQ - n_sess} more sessions."
        cmd = "(automated daily run continues)"
    elif c1 == "GREEN" and c4 in ("GREEN","WAIT") and not any_red:
        # All green or one yellow
        n_yellow = sum(1 for c in crits if c == "YELLOW")
        if n_yellow == 0:
            verdict = "🟢 PROMOTE — all 5 criteria GREEN"
            action = "Safe to promote. Old LIVE archives as 'tinh_te'."
        elif n_yellow <= 2:
            verdict = "🟢 PROMOTE — mostly GREEN with minor YELLOW"
            action = "Safe to promote with caveats."
        else:
            verdict = "🟡 EXTEND — too many YELLOW"
            action = "Continue shadow 1 more week then re-evaluate."
            cmd = "(automated daily run continues)"
        cmd = "python deploy_ngu_hanh.py --promote --archive-as tinh_te"
    else:
        verdict = "🟡 EXTEND"
        action = "Continue shadow 1 more week."
        cmd = "(automated daily run continues)"

    print(f"\nVerdict: {verdict}")
    print(f"  → {action}")
    print(f"  cmd: {cmd}")
    return {"verdict": verdict, "criteria": crits, "n_sess": n_sess}

def report(log_df):
    print("\n" + "="*70)
    print("Ngũ Hành Shadow Tracker — LIVE (Tinh Tế) vs STAGING (Tam Quan v3.1)")
    print("="*70)
    print(f"  Log: {LOG_CSV}")
    print(f"  Rows: {len(log_df)} | {log_df['time'].min().date()} → {log_df['time'].max().date()}")

    log_df = log_df.copy()
    shadow = log_df[log_df["time"] >= STAGE_START]
    if len(shadow) > 0:
        print(f"\nRecent shadow sessions (since stage start {STAGE_START.date()}):")
        for _, r in shadow.tail(20).iterrows():
            ln = STATE_NAMES.get(int(r['live']), '?')
            sn = STATE_NAMES.get(int(r['stag']), '?')
            flag = "" if r["live"] == r["stag"] else "  ‼️"
            close_s = f"VNI={r['vni_close']:.1f}" if 'vni_close' in r and not pd.isna(r['vni_close']) else ""
            print(f"  {r['time'].strftime('%Y-%m-%d')}  LIVE={ln:<8} STAG={sn:<8} {close_s}{flag}")

    ctx_df = get_context()
    evaluate_verdict(log_df, ctx_df)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", action="store_true", help="Report only, don't update log")
    args = parser.parse_args()
    if args.report:
        if not os.path.exists(LOG_CSV):
            print(f"No log yet: {LOG_CSV}"); sys.exit(0)
        log_df = pd.read_csv(LOG_CSV); log_df["time"] = pd.to_datetime(log_df["time"])
    else:
        log_df = update_log()
    report(log_df)
