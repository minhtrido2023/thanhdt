import pandas as pd, numpy as np, os

W = os.path.dirname(os.path.abspath(__file__))
CRACK = os.path.join(os.path.dirname(W), "crack")
TOPTECH = os.path.join(os.path.dirname(W), "toptech")

crack = pd.read_csv(os.path.join(CRACK, "crack_daily.csv"), parse_dates=["time"]).sort_values("time").reset_index(drop=True)
tech = pd.read_csv(os.path.join(TOPTECH, "vnindex_tech.csv"), parse_dates=["time"]).sort_values("time").reset_index(drop=True)
d = crack.merge(tech[["time", "D_RSI", "D_RSI_Max3M"]], on="time", how="left")
d["vnindex_close"] = d["vnindex_close"].ffill()
d["rsi_gap_3m"] = d.D_RSI_Max3M - d.D_RSI
d["rsi_diverge_3m_002"] = d.new_high_126.astype(bool) & (d.rsi_gap_3m >= 0.02)
d["diverge_day"] = d.diverge_day.astype(bool)

vni = d.vnindex_close.to_numpy(float)
times = d.time.to_numpy()
n = len(vni)

def cluster_starts(flag, gap=10):
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

HOLD = 21  # sessions must stay >= t0 price to count as "genuinely stable" (ex-post only)

def stability_lag(t0):
    for j in range(t0, n):
        if vni[j] >= vni[t0]:
            end = min(j + HOLD, n)
            if end - j < HOLD:
                return np.nan, True  # ran out of panel before confirming HOLD sessions
            if np.all(vni[j:end] >= vni[t0]):
                return j - t0, False
    return np.nan, True

rows = []
for trig_name, flag in [("DIVERGE_DAY", d.diverge_day.to_numpy(bool)),
                         ("RSI_DIVERGE_3M_m002", d.rsi_diverge_3m_002.to_numpy(bool))]:
    for t0 in cluster_starts(flag):
        lag, trunc = stability_lag(t0)
        rows.append(dict(trigger=trig_name, t0=pd.Timestamp(times[t0]).date(), lag_sessions=lag, truncated=trunc))

R = pd.DataFrame(rows)
R.to_csv(os.path.join(W, "venc_stability_lag.csv"), index=False)
print(R.to_string(index=False))
print()
for trig in R.trigger.unique():
    sub = R[(R.trigger == trig) & (~R.truncated)]
    v = sub.lag_sessions.dropna().to_numpy()
    if len(v):
        print(f"{trig}: n={len(v)} (excl {int(R[R.trigger==trig].truncated.sum())} truncated) "
              f"median={np.median(v):.1f} p25={np.percentile(v,25):.1f} p75={np.percentile(v,75):.1f} "
              f"min={v.min():.0f} max={v.max():.0f}")
