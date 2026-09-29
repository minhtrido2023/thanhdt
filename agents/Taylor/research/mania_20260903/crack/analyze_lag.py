import pandas as pd, numpy as np, os

CW = os.path.dirname(os.path.abspath(__file__))  # mania_20260903/crack

d = pd.read_csv(os.path.join(CW, "crack_daily.csv"), parse_dates=["time"]).sort_values("time").reset_index(drop=True)
vni = d.vnindex_close.to_numpy()
n = len(vni)
times = d.time.to_numpy()
last_date = pd.Timestamp(times[-1])

ev = pd.read_csv(os.path.join(CW, "events_diverge_day.csv"), parse_dates=["start", "end"]).sort_values("start").reset_index(drop=True)

FWD = 126


def lag_metrics(t0_idx, label=""):
    """From t0_idx (inclusive), look forward up to FWD sessions (or end of panel).
    Returns dict with trough info, peak-before-trough info, DD-from-t0, and a truncation flag."""
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

    # peak reached strictly before (or at) the trough, i.e. the run-up that happens
    # between the signal firing and the eventual low
    pre_trough_seg = vni[t0_idx:trough_idx + 1]
    pre_trough_idx = np.arange(t0_idx, trough_idx + 1)
    peak_pos = int(np.argmax(pre_trough_seg))
    peak_idx = pre_trough_idx[peak_pos]
    peak_px = pre_trough_seg[peak_pos]
    peak_after_signal_pct = peak_px / px0 - 1
    sessions_to_peak = peak_idx - t0_idx

    return dict(
        t0=pd.Timestamp(times[t0_idx]).date(),
        px0=px0,
        trough_date=pd.Timestamp(times[trough_idx]).date(),
        trough_px=trough_px,
        lag_sessions=lag_sessions,
        lag_calendar_days=lag_calendar_days,
        peak_after_signal_pct=peak_after_signal_pct,
        sessions_to_peak=sessions_to_peak,
        dd_from_t0=dd_from_t0,
        truncated=truncated,
        window_sessions=window_end - t0_idx,
    )


def dist(vals):
    v = np.array([x for x in vals if x is not None and not (isinstance(x, float) and np.isnan(x))])
    if len(v) == 0:
        return dict(n=0)
    return dict(n=len(v), min=v.min(), p25=np.percentile(v, 25), median=np.median(v),
                p75=np.percentile(v, 75), max=v.max(), mean=v.mean())


# ---- Variant A (primary): t0 = FIRST DIVERGE_DAY of each episode ----
rows_A = []
for _, r in ev.iterrows():
    t0_date = r.start
    idx = d.index[d.time == t0_date]
    if len(idx) == 0:
        continue
    m = lag_metrics(int(idx[0]))
    rows_A.append(m)
RA = pd.DataFrame(rows_A)
RA.to_csv(os.path.join(CW, "lag_events_t0_first.csv"), index=False)

# ---- Variant B: t0 = LAST DIVERGE_DAY of each episode (confirmed/end of run) ----
rows_B = []
for _, r in ev.iterrows():
    t0_date = r.end
    idx = d.index[d.time == t0_date]
    if len(idx) == 0:
        continue
    m = lag_metrics(int(idx[0]))
    rows_B.append(m)
RB = pd.DataFrame(rows_B)
RB.to_csv(os.path.join(CW, "lag_events_t0_last.csv"), index=False)

# ---- Base rate: sample every 21 sessions, same 3 metrics ----
sample_idx = list(range(252 + 63, n, 21))  # start after warm-up needed for diverge flag panel, though not required here; keep consistent with §2.5
rows_base = []
for i in sample_idx:
    m = lag_metrics(i)
    rows_base.append(m)
RBase = pd.DataFrame(rows_base)
RBase.to_csv(os.path.join(CW, "lag_base_rate.csv"), index=False)

print(f"Panel: {n} sessions {pd.Timestamp(times[0]).date()}..{last_date.date()}")
print(f"N episodes (start-of-run t0): {len(RA)}  | truncated: {int(RA.truncated.sum())}")
print(f"N base-rate samples: {len(RBase)}  | truncated: {int(RBase.truncated.sum())}")
print()

for name, R in [("Variant A (t0=first DIVERGE day)", RA), ("Variant B (t0=last DIVERGE day)", RB), ("Base rate (every 21 sessions)", RBase)]:
    print(f"=== {name} ===")
    Rc = R[~R.truncated] if "truncated" in R else R
    n_excl = int(R.truncated.sum())
    print(f"  n={len(R)}  excluded (truncated window)={n_excl}  n_used={len(Rc)}")
    for col, label in [("lag_sessions", "lag_sessions (t0->trough)"),
                        ("lag_calendar_days", "lag_calendar_days"),
                        ("peak_after_signal_pct", "peak_after_signal_pct"),
                        ("sessions_to_peak", "sessions_to_peak"),
                        ("dd_from_t0", "dd_from_t0")]:
        s = dist(Rc[col].to_numpy())
        if s.get("n", 0) == 0:
            print(f"    {label}: n=0")
            continue
        print(f"    {label}: n={s['n']} min={s['min']:.3f} p25={s['p25']:.3f} median={s['median']:.3f} "
              f"p75={s['p75']:.3f} max={s['max']:.3f} mean={s['mean']:.3f}")
    print()

print("=== Per-episode table (Variant A) ===")
print(RA[["t0", "trough_date", "lag_sessions", "lag_calendar_days", "peak_after_signal_pct", "sessions_to_peak", "dd_from_t0", "truncated"]].to_string(index=False))
