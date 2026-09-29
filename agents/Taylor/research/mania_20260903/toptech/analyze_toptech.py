import pandas as pd, numpy as np, os

W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # mania_20260903
CW = os.path.dirname(os.path.abspath(__file__))                    # mania_20260903/toptech
CRACK = os.path.join(W, "crack")

# ---------------------------------------------------------------------------
# 1. Panel: canonical price/breadth/DIVERGE flags from crack_daily.csv (2008-06-02..2026-09-03,
#    price series = ANY_VALUE(t.VNINDEX) mirror, SAME series used for §2/§3 of mania_deep_dive).
#    Tech indicators (RSI/Volume/Trading_Value/VAP) come from a FRESH BQ pull of the ticker='VNINDEX'
#    pseudo-row (vnindex_tech.csv) -- confirmed via spot check that Close on that row differs from
#    the crack_daily.csv vnindex_close mirror by up to ~2% (different internal source column), so we
#    keep crack's vnindex_close as the SOLE price series for all outcome measurement (consistent with
#    §3), and only pull RSI/Volume/TradingValue/VAP levels from the fresh pull to build signals.
# ---------------------------------------------------------------------------
crack = pd.read_csv(os.path.join(CRACK, "crack_daily.csv"), parse_dates=["time"]).sort_values("time").reset_index(drop=True)
tech = pd.read_csv(os.path.join(CW, "vnindex_tech.csv"), parse_dates=["time"]).sort_values("time").reset_index(drop=True)

d = crack.merge(tech.drop(columns=["Close"]), on="time", how="left")
assert len(d) == len(crack), f"merge dropped rows: {len(d)} vs {len(crack)}"
n_na = d[["D_RSI", "D_RSI_Max3M", "Volume_1M", "Trading_Value_Total_1W", "VAP1M", "VAP1W"]].isna().sum()
print("NaN counts after merge (should be 0 given panel starts well after warmup):")
print(n_na.to_string())
assert n_na.sum() == 0, "unexpected NaN in tech columns within crack panel window"

vni = d.vnindex_close.to_numpy()
n = len(vni)
times = d.time.to_numpy()
new_high_126 = d.new_high_126.to_numpy()  # reuse from crack_daily.csv (already computed identically)

# ---------------------------------------------------------------------------
# Causal percentile-rank helper -- EXACT same convention as analyze_crack.py's breadth_pct252:
# pct[i] = fraction of the 252 days STRICTLY BEFORE i (i-252..i-1, excludes i) that are < value[i].
# ---------------------------------------------------------------------------
def pct252(arr):
    a = np.asarray(arr, dtype=float)
    out = np.full(len(a), np.nan)
    for i in range(252, len(a)):
        win = a[i-252:i]
        win = win[~np.isnan(win)]
        if len(win) > 50 and not np.isnan(a[i]):
            out[i] = (win < a[i]).mean()
    return out

def recent_max_63(pctarr):
    a = np.asarray(pctarr, dtype=float)
    out = np.full(len(a), np.nan)
    for i in range(63, len(a)):
        out[i] = np.nanmax(a[i-62:i+1])
    return out

# ---------------------------------------------------------------------------
# 2. Candidates
# ---------------------------------------------------------------------------
N_TRIALS = 0  # count every variant evaluated below (declared honestly, per coding_guidelines §quant-research step 4/13)

# --- Family 1: Volume divergence (same recipe as DIVERGE_DAY, substituting breadth->volume) ---
d["vol_pct252"] = pct252(d.Volume_1M.to_numpy())
d["vol_recent_max_63"] = recent_max_63(d.vol_pct252.to_numpy())
d["vol_drop"] = d.vol_recent_max_63 - d.vol_pct252
VOL_DROP_MIN = 0.30  # reused from DIVERGE_DAY's pre-registered threshold, NOT re-optimized here
d["vol_diverge_day"] = new_high_126 & (d.vol_drop >= VOL_DROP_MIN)
N_TRIALS += 1

# --- Family 2: Trading-value divergence (same recipe, Trading_Value_Total_1W = trailing 1W sum) ---
d["tv_pct252"] = pct252(d.Trading_Value_Total_1W.to_numpy())
d["tv_recent_max_63"] = recent_max_63(d.tv_pct252.to_numpy())
d["tv_drop"] = d.tv_recent_max_63 - d.tv_pct252
TV_DROP_MIN = 0.30
d["tv_diverge_day"] = new_high_126 & (d.tv_drop >= TV_DROP_MIN)
N_TRIALS += 1

# --- Family 3: VAP extension (Close detached above its own volume-at-price center) ---
# "VAPM" as literally named does not exist in bigquery_dictionary.json / data_registry -- closest
# real columns are VAP1W/VAP1M/VAP3M ("Close in the largest trading area" = volume-profile point of
# control). Proxy used here: how far Close sits above VAP, itself rank-normalized causally.
VAP_EXT_TH = 0.90
for label, col in [("w", "VAP1W"), ("m", "VAP1M")]:
    ext = d.Close if "Close" in d.columns else d.vnindex_close  # Close not merged in; use vnindex_close
    ext = d.vnindex_close / d[col] - 1
    d[f"vapext_{label}"] = ext
    pct = pct252(ext.to_numpy())
    d[f"vapext_{label}_pct252"] = pct
    d[f"vap_ext_{label}_day"] = new_high_126 & (pct >= VAP_EXT_TH)
    N_TRIALS += 1

# --- Family 4: RSI divergence (primary family per dispatch) ---
# When new_high_126(t) is True, Close(t) is by construction >= any close in the trailing 126 days,
# hence >= D_RSI_Max3M_Close(t) (peak within a 63d sub-window) automatically -- so "price higher
# high" is already implied and does not need a separate price condition. The only free parameter is
# the RSI gap margin. Grid pre-registered below (not cherry-picked): report ALL margins, pick the
# smallest that must-catches both 2018-04 and 2022-01-06.
RSI_MARGIN_GRID = [0.02, 0.03, 0.05, 0.08, 0.10]
d["rsi_gap_3m"] = d.D_RSI_Max3M - d.D_RSI
for m in RSI_MARGIN_GRID:
    d[f"rsi_diverge_3m_{m}"] = new_high_126 & (d.rsi_gap_3m >= m)
    N_TRIALS += 1
# 1-week variant (expected too noisy -- reported for completeness, not the primary pick)
d["rsi_gap_1w"] = d.D_RSI_Max1W - d.D_RSI
RSI_1W_MARGIN = 0.05
d["rsi_diverge_1w"] = new_high_126 & (d.rsi_gap_1w >= RSI_1W_MARGIN)
N_TRIALS += 1

print(f"\nN_TRIALS (variants evaluated across families 1-4, before any combo): {N_TRIALS}\n")

# ---------------------------------------------------------------------------
# 3. Event clustering (verbatim recipe from analyze_crack.py, gap<=10 sessions)
# ---------------------------------------------------------------------------
def cluster_events(flag_arr, gap=10):
    flag = np.asarray(flag_arr, dtype=bool)
    nn = len(flag)
    events = []
    i = 0
    while i < nn:
        if flag[i]:
            start = i
            j = i
            while j + 1 < nn:
                nxt = None
                for k in range(j+1, min(j+1+gap, nn)):
                    if flag[k]:
                        nxt = k
                        break
                if nxt is None:
                    break
                j = nxt
            events.append((start, j))
            i = j + 1
        else:
            i += 1
    return events

# ---------------------------------------------------------------------------
# 4. Outcome metrics -- SAME two toolkits as prior work, on the SAME vnindex_close series:
#    (a) outcome_row: 1M/3M/6M return + maxDD-6M (§2 style, from analyze_crack.py)
#    (b) lag_metrics: lag-to-trough, peak_after_signal_pct, dd_from_t0 (§3 style, from analyze_lag.py)
# ---------------------------------------------------------------------------
def outcome_row(e):
    out = {}
    for name, h in [("1M", 21), ("2M", 42), ("3M", 63), ("6M", 126)]:
        idx = e + h
        out[name] = vni[idx] / vni[e] - 1 if idx < n else np.nan
    window_end = min(e + 126, n - 1)
    if window_end > e:
        seg = vni[e:window_end+1]
        peak = np.maximum.accumulate(seg)
        out["maxdd_6m"] = (seg / peak - 1).min()
    else:
        out["maxdd_6m"] = np.nan
    return out

FWD = 126
def lag_metrics(t0_idx):
    window_end = min(t0_idx + FWD, n - 1)
    truncated = (t0_idx + FWD) > (n - 1)
    seg = vni[t0_idx:window_end + 1]
    seg_idx = np.arange(t0_idx, window_end + 1)
    trough_pos = int(np.argmin(seg))
    trough_idx = seg_idx[trough_pos]
    trough_px = seg[trough_pos]
    px0 = vni[t0_idx]
    lag_sessions = trough_idx - t0_idx
    lag_calendar_days = (pd.Timestamp(times[trough_idx]) - pd.Timestamp(times[t0_idx])).days
    dd_from_t0 = trough_px / px0 - 1
    pre_trough_seg = vni[t0_idx:trough_idx + 1]
    pre_trough_idx = np.arange(t0_idx, trough_idx + 1)
    peak_pos = int(np.argmax(pre_trough_seg))
    peak_idx = pre_trough_idx[peak_pos]
    peak_px = pre_trough_seg[peak_pos]
    peak_after_signal_pct = peak_px / px0 - 1
    return dict(
        t0=pd.Timestamp(times[t0_idx]).date(), px0=px0,
        trough_date=pd.Timestamp(times[trough_idx]).date(), trough_px=trough_px,
        lag_sessions=lag_sessions, lag_calendar_days=lag_calendar_days,
        peak_after_signal_pct=peak_after_signal_pct, dd_from_t0=dd_from_t0,
        truncated=truncated,
    )

def dist(vals):
    v = np.array([x for x in vals if x is not None and not (isinstance(x, float) and np.isnan(x))])
    if len(v) == 0:
        return dict(n=0)
    return dict(n=len(v), min=v.min(), p25=np.percentile(v, 25), median=np.median(v),
                p75=np.percentile(v, 75), max=v.max(), mean=v.mean())

CANDIDATES = [
    ("VOL_DIVERGE (fam1, Volume_1M, drop>=0.30)", "vol_diverge_day"),
    ("TV_DIVERGE (fam2, TradingValue1W, drop>=0.30)", "tv_diverge_day"),
    ("VAP_EXT_1W (fam3, Close/VAP1W-1, pct>=0.90)", "vap_ext_w_day"),
    ("VAP_EXT_1M (fam3, Close/VAP1M-1, pct>=0.90)", "vap_ext_m_day"),
] + [(f"RSI_DIVERGE_3M margin={m}", f"rsi_diverge_3m_{m}") for m in RSI_MARGIN_GRID] + [
    ("RSI_DIVERGE_1W margin=0.05", "rsi_diverge_1w"),
]

summary_rows = []
must_catch_rows = []
apr2018 = d[(d.time >= "2018-02-27") & (d.time <= "2018-04-09")]
jan2022_idx = d.index[d.time == "2022-01-06"]

all_events_out = {}
for label, col in CANDIDATES:
    flag = d[col].fillna(False).to_numpy()
    evs = cluster_events(flag)
    rows = []
    for (s, e) in evs:
        out = outcome_row(e)
        lm = lag_metrics(s)  # t0 = first flagged day of episode (Variant A convention, matches §3)
        rows.append(dict(start=pd.Timestamp(d.time.iloc[s]).date(), end=pd.Timestamp(d.time.iloc[e]).date(),
                          span=e-s+1, vni_start=vni[s], vni_end=vni[e], **out, **{f"lag_{k}": v for k, v in lm.items()}))
    R = pd.DataFrame(rows)
    fname = os.path.join(CW, f"events_{col}.csv")
    R.to_csv(fname, index=False)
    all_events_out[col] = R

    n_flag_days = int(flag.sum())
    n_ep = len(evs)
    catch_2018 = int(apr2018[col].sum()) if col in apr2018 else 0
    catch_2022 = bool(d.loc[jan2022_idx[0], col]) if len(jan2022_idx) else False
    must_catch_rows.append(dict(candidate=label, n_flag_days=n_flag_days, pct_days=100*flag.mean(),
                                 n_episodes=n_ep, catch_2018_days=catch_2018, catch_2022=catch_2022))

    Rc = R[~R.lag_truncated] if len(R) and "lag_truncated" in R else R
    n_excl = int(R.lag_truncated.sum()) if len(R) else 0
    row = dict(candidate=label, n_episodes=len(R), n_excl_truncated=n_excl, n_used=len(Rc))
    if len(Rc):
        for c in ["1M", "3M", "6M", "maxdd_6m"]:
            v = Rc[c].dropna()
            row[f"{c}_mean"] = v.mean() if len(v) else np.nan
            row[f"{c}_median"] = v.median() if len(v) else np.nan
        for c in ["lag_lag_sessions", "lag_peak_after_signal_pct", "lag_dd_from_t0"]:
            v = Rc[c].dropna()
            row[f"{c}_median"] = v.median() if len(v) else np.nan
            row[f"{c}_mean"] = v.mean() if len(v) else np.nan
    summary_rows.append(row)

MC = pd.DataFrame(must_catch_rows)
MC.to_csv(os.path.join(CW, "must_catch_summary.csv"), index=False)
print("=== Must-catch + frequency summary ===")
print(MC.to_string(index=False))
print()

SUM = pd.DataFrame(summary_rows)
SUM.to_csv(os.path.join(CW, "candidate_summary.csv"), index=False)
print("=== Outcome summary (medians) ===")
show_cols = ["candidate", "n_used", "6M_median", "maxdd_6m_median", "lag_lag_sessions_median",
             "lag_peak_after_signal_pct_median", "lag_dd_from_t0_median"]
print(SUM[show_cols].to_string(index=False))
print()

# ---------------------------------------------------------------------------
# 5. Combination: RSI_DIVERGE_3M (chosen margin) AND TV_DIVERGE -- ONE pre-specified combo only
# ---------------------------------------------------------------------------
CHOSEN_MARGIN = None
for m in RSI_MARGIN_GRID:
    row = MC[MC.candidate == f"RSI_DIVERGE_3M margin={m}"].iloc[0]
    if row.catch_2018_days > 0 and row.catch_2022:
        CHOSEN_MARGIN = m
        break
print(f"Smallest RSI margin that must-catches BOTH 2018-04 and 2022-01-06: {CHOSEN_MARGIN}")

if CHOSEN_MARGIN is not None:
    combo_flag = (d[f"rsi_diverge_3m_{CHOSEN_MARGIN}"].fillna(False) & d["tv_diverge_day"].fillna(False)).to_numpy()
    evs = cluster_events(combo_flag)
    rows = []
    for (s, e) in evs:
        out = outcome_row(e)
        lm = lag_metrics(s)
        rows.append(dict(start=pd.Timestamp(d.time.iloc[s]).date(), end=pd.Timestamp(d.time.iloc[e]).date(),
                          span=e-s+1, vni_start=vni[s], vni_end=vni[e], **out, **{f"lag_{k}": v for k, v in lm.items()}))
    RC = pd.DataFrame(rows)
    RC.to_csv(os.path.join(CW, "events_combo_rsi_tv.csv"), index=False)
    print(f"\n=== COMBO: RSI_DIVERGE_3M(margin={CHOSEN_MARGIN}) AND TV_DIVERGE: {len(RC)} episode(s) ===")
    if len(RC):
        print(RC[["start", "end", "span", "6M", "maxdd_6m", "lag_lag_sessions", "lag_peak_after_signal_pct", "lag_dd_from_t0"]].to_string(index=False))
    catch_2022_combo = bool(d.loc[jan2022_idx[0], "tv_diverge_day"] and d.loc[jan2022_idx[0], f"rsi_diverge_3m_{CHOSEN_MARGIN}"]) if len(jan2022_idx) else False
    catch_2018_combo = int((apr2018[f"rsi_diverge_3m_{CHOSEN_MARGIN}"] & apr2018["tv_diverge_day"]).sum())
    print(f"must-catch 2022-01-06: {catch_2022_combo} | must-catch 2018-04 window days: {catch_2018_combo}")

# ---------------------------------------------------------------------------
# 6. Base rate + DIVERGE reference (load existing §2/§3 artifacts, do NOT recompute)
# ---------------------------------------------------------------------------
base = pd.read_csv(os.path.join(CRACK, "lag_base_rate.csv"))
base_c = base[~base.truncated]
diverge_lag = pd.read_csv(os.path.join(CRACK, "lag_events_t0_first.csv"))
diverge_lag_c = diverge_lag[~diverge_lag.truncated]
diverge_ev = pd.read_csv(os.path.join(CRACK, "events_diverge_day.csv"))

print("\n=== Reference (loaded, not recomputed): base rate (N=203, excl trunc) & DIVERGE (N=13, excl trunc->12) ===")
for name, df_ in [("base_rate", base_c), ("DIVERGE_lag", diverge_lag_c)]:
    print(f"{name}: n={len(df_)} lag_sessions_median={df_.lag_sessions.median():.1f} "
          f"peak_after_signal_median={df_.peak_after_signal_pct.median()*100:.1f}% "
          f"dd_from_t0_median={df_.dd_from_t0.median()*100:.1f}%")
print(f"DIVERGE outcome (events_diverge_day.csv): 6M_median={diverge_ev['6M'].median()*100:.1f}% "
      f"maxdd_6m_median={diverge_ev['maxdd_6m'].median()*100:.1f}%")

print("\nDone.")
