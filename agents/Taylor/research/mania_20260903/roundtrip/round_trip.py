import pandas as pd, numpy as np, os, json

W = os.path.dirname(os.path.abspath(__file__))          # roundtrip/
CRACK = os.path.join(os.path.dirname(W), "crack")
TOPTECH = os.path.join(os.path.dirname(W), "toptech")

RNG = np.random.default_rng(20260903)
COST = 0.001          # 0.1% per side per CLAUDE.md convention
N_BOOT = 200

# ---------------------------------------------------------------------------
# 1. Load panel A (full): crack_daily.csv, 2008-06-02..2026-09-03
# ---------------------------------------------------------------------------
crack = pd.read_csv(os.path.join(CRACK, "crack_daily.csv"), parse_dates=["time"]).sort_values("time").reset_index(drop=True)
tech = pd.read_csv(os.path.join(TOPTECH, "vnindex_tech.csv"), parse_dates=["time"]).sort_values("time").reset_index(drop=True)
d = crack.merge(tech[["time", "D_RSI", "D_RSI_Max3M"]], on="time", how="left")
assert len(d) == len(crack)

# 13 sessions (2008-06/08/09 + 2009-12-07) have NaN vnindex_close -- isolated trading-halt-style gaps
# in the BQ VNINDEX mirror, not clustered near any exit episode. Forward-fill (carry last close);
# documented explicitly, not silently patched.
n_na_px = int(d.vnindex_close.isna().sum())
d["vnindex_close"] = d["vnindex_close"].ffill()
print(f"Forward-filled {n_na_px} missing vnindex_close sessions (isolated 2008/2009 gaps).")

# Reconstruct RSI_DIVERGE_3M margin=0.02 daily flag -- EXACT recipe from analyze_toptech.py family 4
d["rsi_gap_3m"] = d.D_RSI_Max3M - d.D_RSI
d["rsi_diverge_3m_002"] = d.new_high_126.astype(bool) & (d.rsi_gap_3m >= 0.02)
d["diverge_day"] = d.diverge_day.astype(bool)

# ---------------------------------------------------------------------------
# 2. Load + merge CAPIT/DT5G history (2014-01-02..2026-09-03, restricted panel B)
# ---------------------------------------------------------------------------
capit = pd.read_csv(os.path.join(W, "capit_dt5g_hist.csv"), parse_dates=["time"]).sort_values("time").reset_index(drop=True)
d = d.merge(capit[["time", "state", "oversold", "above_ma200"]], on="time", how="left")

PANIC_THRESHOLD = 0.057
WASHOUT_EXTREME = 0.30
# Simplified reconstruction of crisis_capitulation_signal.py's fire condition (STRONG_BUY/STRONG_CAUTION/WATCH,
# excluding DORMANT). Deliberately DROPS the BEAR-guard refinement (VNINDEX rv10 cooling vs 30d peak, needs an
# extra series) -- that guard only ever turns a "fire" into "BEAR_SKIP" in state=BEAR, i.e. it can only make
# capit_fire MORE conservative than what we compute here. Documented as a limitation (see report).
d["capit_fire"] = (d.oversold >= WASHOUT_EXTREME) | ((d.state == 1) & (d.oversold >= PANIC_THRESHOLD))
d["dt5g_reentry"] = d.state.isin([3, 4, 5])   # NEUTRAL / BULL / EX-BULL

panel_b_start = capit.time.min()  # 2014-01-02
d["in_panel_b"] = d.time >= panel_b_start

vni = d.vnindex_close.to_numpy(float)
n = len(vni)
times = d.time.to_numpy()
b0 = int(d.index[d.time == panel_b_start][0])

print(f"Panel A: {n} sessions {pd.Timestamp(times[0]).date()}..{pd.Timestamp(times[-1]).date()}")
print(f"Panel B (DT5G/CAPIT available): starts idx={b0} date={pd.Timestamp(times[b0]).date()}, {n-b0} sessions")
print(f"DIVERGE episodes (from crack_daily flag): {int(d.diverge_day.sum())} flagged days")
print(f"RSI_DIVERGE_3M(0.02) flagged days: {int(d.rsi_diverge_3m_002.sum())}")
print()

# ---------------------------------------------------------------------------
# 3. Round-trip engine -- T+1 causal execution (decision at close t-1 -> position for day t)
# ---------------------------------------------------------------------------
def run_engine(exit_flag, reentry_ok_fn, start_idx=0, cost=COST):
    """exit_flag: bool array len n, causal (True at t means info through close t says 'exit').
    reentry_ok_fn(t, sessions_out) -> bool, using info through close t-1 (t-1 array indexing done by caller).
    Position for day t decided using info through close t-1. start_idx: first index of the sub-panel (returns
    before start_idx are ignored; nav resets to 1.0 at start_idx)."""
    pos_in = True
    sessions_out = 0
    nav = np.ones(n)
    pos_series = np.ones(n, dtype=bool)
    n_trades = 0
    for t in range(start_idx + 1, n):
        if pos_in:
            if exit_flag[t - 1]:
                pos_in = False
                sessions_out = 0
        else:
            sessions_out += 1
            if reentry_ok_fn(t, sessions_out):
                pos_in = True
        r = vni[t] / vni[t - 1] - 1.0
        day_ret = r if pos_in else 0.0
        changed = pos_in != pos_series[t - 1]
        if changed:
            day_ret -= cost
            n_trades += 1
        nav[t] = nav[t - 1] * (1.0 + day_ret)
        pos_series[t] = pos_in
    return nav, pos_series, n_trades


def metrics(nav, pos_series, start_idx):
    seg_nav = nav[start_idx:] / nav[start_idx]
    seg_times = times[start_idx:]
    cal_days = (pd.Timestamp(seg_times[-1]) - pd.Timestamp(seg_times[0])).days
    cagr = seg_nav[-1] ** (365.25 / cal_days) - 1.0
    peak = np.maximum.accumulate(seg_nav)
    dd = seg_nav / peak - 1.0
    maxdd = dd.min()
    rets = np.diff(seg_nav) / seg_nav[:-1]
    sharpe = (rets.mean() / rets.std() * np.sqrt(252)) if rets.std() > 0 else np.nan
    calmar = cagr / abs(maxdd) if maxdd != 0 else np.nan
    pct_out = 1.0 - pos_series[start_idx:].mean()
    return dict(cagr=cagr, maxdd=maxdd, sharpe=sharpe, calmar=calmar, pct_time_out=pct_out, final_nav=seg_nav[-1])


# ---------------------------------------------------------------------------
# 4. Self-check: always-IN path must exactly reproduce buy-and-hold
# ---------------------------------------------------------------------------
always_in_flag = np.zeros(n, dtype=bool)
nav_hold, pos_hold, trades_hold = run_engine(always_in_flag, lambda t, s: True, start_idx=0)
bh_true = vni / vni[0]
max_abs_err = np.max(np.abs(nav_hold - bh_true))
assert trades_hold == 0, f"self-check FAILED: always-IN made {trades_hold} trades"
assert max_abs_err < 1e-9, f"self-check FAILED: always-IN NAV diverges from buy-hold by {max_abs_err}"
print(f"SELF-CHECK OK: always-IN path == buy-and-hold exactly (max abs err {max_abs_err:.2e}, 0 trades)\n")

# ---------------------------------------------------------------------------
# 5. Re-entry rules
# ---------------------------------------------------------------------------
breadth = d.breadth_pct252.to_numpy(float)
capit_fire = d.capit_fire.fillna(False).to_numpy(bool)
dt5g_reentry = d.dt5g_reentry.fillna(False).to_numpy(bool)

def r1_fixed(K):
    def f(t, sessions_out):
        return sessions_out >= K
    return f

def r2_breadth(th):
    def f(t, sessions_out):
        v = breadth[t - 1]
        return (not np.isnan(v)) and v >= th
    return f

def r3_capit(t, sessions_out):
    return bool(capit_fire[t - 1])

def r4_dt5g(t, sessions_out):
    return bool(dt5g_reentry[t - 1])

REENTRY_RULES = {
    "R1_K21": r1_fixed(21),
    "R1_K63": r1_fixed(63),
    "R1_K126": r1_fixed(126),
    "R2_breadth050": r2_breadth(0.50),
    "R3_capit": r3_capit,
    "R4_dt5g": r4_dt5g,
}
REENTRY_PANEL = {  # which panel each rule is valid on
    "R1_K21": "A", "R1_K63": "A", "R1_K126": "A", "R2_breadth050": "A",
    "R3_capit": "B", "R4_dt5g": "B",
}

EXIT_TRIGGERS = {
    "DIVERGE_DAY": d.diverge_day.to_numpy(bool),
    "RSI_DIVERGE_3M_m002": d.rsi_diverge_3m_002.to_numpy(bool),
}

# ---------------------------------------------------------------------------
# 6. Bootstrap controls
# ---------------------------------------------------------------------------
def cluster_starts(flag, gap=10):
    """First-day-of-episode indices, gap<=10 clustering (same convention as prior work)."""
    idx = np.where(flag)[0]
    if len(idx) == 0:
        return []
    starts = [idx[0]]
    last = idx[0]
    for i in idx[1:]:
        if i - last > gap:
            starts.append(i)
        last = i
    return starts

def random_exit_flag(n_events, start_idx, rng):
    """Control (2): n_events random single-day exit flags scattered in [start_idx+315, n).
    +315 mirrors the 252+63 warmup used for breadth/RSI signals, so random draws live in the
    same 'reachable' region as the real signals (not literally required for R1/R3/R4/buy-hold,
    but keeps the comparison apples-to-apples)."""
    lo = start_idx + 315
    if lo >= n:
        lo = start_idx
    choices = rng.choice(np.arange(lo, n), size=n_events, replace=False)
    flag = np.zeros(n, dtype=bool)
    flag[choices] = True
    return flag

def random_reentry_fn(rng):
    """Control (3): once OUT, wait a random number of sessions ~ Uniform[1,126] (matches the FWD
    window used throughout this line of work) instead of the tested re-entry rule."""
    draws = {}
    def f(t, sessions_out):
        # need a stable per-exit-episode random K -- key by t - sessions_out (the exit transition day)
        key = t - sessions_out
        if key not in draws:
            draws[key] = rng.integers(1, 127)
        return sessions_out >= draws[key]
    return f

rows = []
for trig_name, exit_flag in EXIT_TRIGGERS.items():
    real_starts = cluster_starts(exit_flag)
    n_events = len(real_starts)
    for rule_name, rule_fn in REENTRY_RULES.items():
        panel = REENTRY_PANEL[rule_name]
        start_idx = 0 if panel == "A" else b0
        # skip if no exit events happen within this panel
        events_in_panel = [s for s in real_starts if s >= start_idx]
        if len(events_in_panel) == 0:
            continue

        # --- MAIN: real exit x real reentry rule ---
        nav_m, pos_m, tr_m = run_engine(exit_flag, rule_fn, start_idx=start_idx)
        met_m = metrics(nav_m, pos_m, start_idx)
        met_m.update(kind="MAIN", exit_trigger=trig_name, reentry_rule=rule_name, panel=panel,
                      n_events=len(events_in_panel), n_trades=tr_m)
        rows.append(met_m)

        # --- CONTROL 2: random exit day (same count), same reentry rule ---
        boot2 = []
        for b in range(N_BOOT):
            rf = random_exit_flag(len(events_in_panel), start_idx, RNG)
            nav_b, pos_b, tr_b = run_engine(rf, rule_fn, start_idx=start_idx)
            boot2.append(metrics(nav_b, pos_b, start_idx))
        c2 = pd.DataFrame(boot2)
        rows.append(dict(kind="CTRL2_random_exit_mean", exit_trigger=trig_name, reentry_rule=rule_name,
                          panel=panel, n_events=len(events_in_panel), n_trades=np.nan,
                          cagr=c2.cagr.mean(), maxdd=c2.maxdd.mean(), sharpe=c2.sharpe.mean(),
                          calmar=c2.calmar.mean(), pct_time_out=c2.pct_time_out.mean(), final_nav=c2.final_nav.mean()))
        rows.append(dict(kind="CTRL2_random_exit_p05_p95", exit_trigger=trig_name, reentry_rule=rule_name,
                          panel=panel, n_events=len(events_in_panel), n_trades=np.nan,
                          cagr=f"{c2.cagr.quantile(.05):.4f}/{c2.cagr.quantile(.95):.4f}",
                          maxdd=f"{c2.maxdd.quantile(.05):.4f}/{c2.maxdd.quantile(.95):.4f}",
                          sharpe=np.nan, calmar=np.nan, pct_time_out=np.nan, final_nav=np.nan))

        # --- CONTROL 3: real exit signal, random reentry wait ---
        boot3 = []
        for b in range(N_BOOT):
            rrf = random_reentry_fn(RNG)
            nav_c, pos_c, tr_c = run_engine(exit_flag, rrf, start_idx=start_idx)
            boot3.append(metrics(nav_c, pos_c, start_idx))
        c3 = pd.DataFrame(boot3)
        rows.append(dict(kind="CTRL3_random_reentry_mean", exit_trigger=trig_name, reentry_rule=rule_name,
                          panel=panel, n_events=len(events_in_panel), n_trades=np.nan,
                          cagr=c3.cagr.mean(), maxdd=c3.maxdd.mean(), sharpe=c3.sharpe.mean(),
                          calmar=c3.calmar.mean(), pct_time_out=c3.pct_time_out.mean(), final_nav=c3.final_nav.mean()))

# --- Buy-and-hold reference, both panels ---
for panel, start_idx in [("A", 0), ("B", b0)]:
    met_bh = metrics(nav_hold, pos_hold, start_idx)
    met_bh.update(kind="BUY_HOLD", exit_trigger="-", reentry_rule="-", panel=panel, n_events=0, n_trades=0)
    rows.append(met_bh)

RES = pd.DataFrame(rows)
RES.to_csv(os.path.join(W, "roundtrip_results.csv"), index=False)
print(RES.to_string(index=False))
print("\nSaved -> roundtrip_results.csv")

# ---------------------------------------------------------------------------
# 7. Re-entry timing distributions (median/IQR of sessions-to-reentry) per rule, using REAL
#    DIVERGE_DAY exit events (primary reference trigger)
# ---------------------------------------------------------------------------
print("\n=== Re-entry timing distribution (DIVERGE_DAY exits, sessions OUT until reentry) ===")
timing_rows = []
for rule_name, rule_fn in REENTRY_RULES.items():
    panel = REENTRY_PANEL[rule_name]
    start_idx = 0 if panel == "A" else b0
    exit_flag = EXIT_TRIGGERS["DIVERGE_DAY"]
    real_starts = [s for s in cluster_starts(exit_flag) if s >= start_idx]
    waits = []
    for s in real_starts:
        # simulate forward from this single exit until reentry fires (independent per-episode probe,
        # not the cumulative engine -- just measuring "how many sessions would this rule keep you out")
        sessions_out = 0
        t = s + 1
        while t < n:
            sessions_out += 1
            if rule_fn(t, sessions_out):
                waits.append(sessions_out)
                break
            t += 1
        else:
            waits.append(np.nan)  # never fired before panel end
    w = np.array([x for x in waits if not np.isnan(x)])
    n_never = sum(np.isnan(x) for x in waits)
    if len(w):
        timing_rows.append(dict(rule=rule_name, panel=panel, n_episodes=len(real_starts), n_never_fired=n_never,
                                 median=np.median(w), p25=np.percentile(w, 25), p75=np.percentile(w, 75),
                                 min=w.min(), max=w.max()))
TIM = pd.DataFrame(timing_rows)
TIM.to_csv(os.path.join(W, "reentry_timing_dist.csv"), index=False)
print(TIM.to_string(index=False))

print("\nDone.")
