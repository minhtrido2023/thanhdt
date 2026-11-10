"""Part D — did existing regime indicators warn in 07->11/2026; how does this decline compare to history (descriptive)."""
import json, sys
import numpy as np, pandas as pd
WC = "/home/trido/thanhdt/WorkingClaude"; sys.path.insert(0, WC)
OUT = f"{WC}/mike/agents/Taylor/research/book_regime_fit_20261110"
vni = pd.read_csv(f"{OUT}/data/vnindex.csv", parse_dates=["time"]).set_index("time")
dt5 = pd.read_csv(f"{OUT}/data/dt5g.csv", parse_dates=["time"]).set_index("time")
xs = pd.read_csv(f"{OUT}/data/xsec.csv", parse_dates=["time"]).set_index("time")
from value_radar import load_series
vr = load_series(update=False).set_index("time")
c = vni.Close
D = pd.DataFrame({"vni": c, "ret90": c / c.shift(90) - 1, "dd252": c / c.rolling(252, min_periods=120).max() - 1,
                  "ma200dev": c / vni.MA200 - 1}).join(xs[["breadth", "disp21", "ew_r1"]]).join(dt5[["state", "state_raw"]]).join(vr[["score", "label"]], how="left")
D["ew_idx"] = (1 + D.ew_r1.fillna(0)).cumprod()
D["ew_ret90"] = D.ew_idx / D.ew_idx.shift(90) - 1
D = D[D.index >= "2008-01-01"]

# (1) live window trajectory, weekly sample
L = D["2026-06-25":]
traj = L.iloc[::5][["vni", "ret90", "dd252", "ma200dev", "breadth", "ew_ret90", "state", "state_raw", "score", "label"]]
traj = pd.concat([traj, L.iloc[[-1]][traj.columns]]).drop_duplicates()
traj.round(3).to_csv(f"{OUT}/part_d_live_traj.csv")
print(traj.round(3).to_string())
print("state counts since 2026-07-01:", L["2026-07-01":].state.value_counts().to_dict(), "raw:", L["2026-07-01":].state_raw.value_counts().to_dict())

# (2) historical episodes: contiguous runs with ret90 <= -7%
trig = (D.ret90 <= -0.07)
# merge trigger runs separated by <= 60 sessions into one episode (prereg said "gộp thành đợt rời")
pos = np.flatnonzero(trig.values); ep_id = np.r_[0, np.cumsum(np.diff(pos) > 60)]
runs = pd.Series(ep_id, index=D.index[pos])
eps = []
for _, g in D[trig].groupby(runs):
    t0 = g.index[0]; i0 = D.index.get_loc(t0)
    w = D.iloc[max(0, i0 - 90):i0 + 1]
    pk = w.vni.idxmax(); seg = D.loc[pk:g.index[-1]]
    tr = seg.vni.idxmin()
    fwd = D.vni.iloc[min(i0 + 60, len(D) - 1)] / D.vni.iloc[i0] - 1 if i0 + 60 < len(D) else np.nan
    eps.append(dict(trigger=str(t0.date()), run_sessions=len(g), peak=str(pk.date()), trough=str(tr.date()),
                    depth=float(seg.vni.min() / D.vni[pk] - 1), sess_peak_to_trough=int(D.index.get_loc(tr) - D.index.get_loc(pk)),
                    sess_peak_to_trigger=int(i0 - D.index.get_loc(pk)),
                    breadth_at_peak=float(D.breadth[pk]), breadth_at_trigger=float(D.breadth[t0]),
                    ew_ret90_at_trigger=float(D.ew_ret90[t0]), vni_ret90_at_trigger=float(D.ret90[t0]),
                    state_at_trigger=None if pd.isna(D.state[t0]) else int(D.state[t0]),
                    state_min_in_run=None if g.state.isna().all() else int(g.state.min()),
                    radar_at_trigger=None if pd.isna(D.score[t0]) else float(D.score[t0]),
                    vni_fwd60_from_trigger=float(fwd) if fwd == fwd else None))
E = pd.DataFrame(eps)
E.to_csv(f"{OUT}/part_d_episodes.csv", index=False)
pd.set_option("display.width", 250)
print(E.round(3).to_string(index=False))
cur = E.iloc[-1]
hist = E.iloc[:-1] if str(cur.trigger) >= "2026-07-01" else E
summ = dict(n_episodes_hist=len(hist), current=cur.to_dict(),
            hist_median=hist[["depth", "sess_peak_to_trough", "sess_peak_to_trigger", "breadth_at_trigger", "ew_ret90_at_trigger", "vni_fwd60_from_trigger"]].median().to_dict(),
            pct_hist_state3_at_trigger=float((hist.dropna(subset=["state_at_trigger"]).state_at_trigger == 3).mean()),
            n_hist_with_state=int(hist.state_at_trigger.notna().sum()),
            pct_hist_ever_below3=float((hist.dropna(subset=["state_min_in_run"]).state_min_in_run < 3).mean()),
            hist_2014_breadth_trigger_median=float(hist[hist.trigger >= "2014"].breadth_at_trigger.median()),
            hist_2014_ew_minus_vni_median=float((hist[hist.trigger >= "2014"].ew_ret90_at_trigger - hist[hist.trigger >= "2014"].vni_ret90_at_trigger).median()),
            breadth_now=float(D.breadth.iloc[-1]), breadth_pct_rank_since2008=float((D.breadth <= D.breadth.iloc[-1]).mean()),
            ew_ret90_now=float(D.ew_ret90.iloc[-1]), asof=str(D.index[-1].date()))
json.dump(summ, open(f"{OUT}/part_d.json", "w"), indent=1, default=str)
print(json.dumps(summ, indent=1, default=str))
try:
    from dna_report import build_dt_gate_line
    print("GATE_CLOCK_NOW:", build_dt_gate_line(html=False))
except Exception as e:
    print("gate clock unavailable:", repr(e))
