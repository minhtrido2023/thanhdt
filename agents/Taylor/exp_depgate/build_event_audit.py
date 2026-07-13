# -*- coding: utf-8 -*-
"""
build_event_audit.py <D1> [D2 D3 ...] — job Taylor_20260713_145605.
Event-level audit (plan §5.1) for depgate variants, format-identical to event_audit_D0.csv
(built in job Taylor_20260713_141712). Self-verifies by rebuilding D0 and diffing against the
existing episode file before writing any new variant's audit.

sleeve_delta[t] = (w_v[t] - w_pub[t]) * (VNINDEX[t+1]/VNINDEX[t] - 1)   [fraction]
w map: CRISIS(1)=0.0 BEAR(2)=0.2 NEUTRAL(3)=0.7 BULL(4)=1.0 EXBULL(5)=1.3
Episodes: strictly consecutive deviating sessions; any break (>=1 non-deviating session)
starts a new episode (verified: this reproduces the original D0 episode table exactly).
VNINDEX series reused from event_audit_D0.csv (same grid, same vintage).
"""
import sys, os
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
W = {1: 0.0, 2: 0.2, 3: 0.7, 4: 1.0, 5: 1.3}
GAP = 1

vni = pd.read_csv(os.path.join(HERE, "event_audit_D0.csv"), parse_dates=["time"])[["time", "vnindex"]]


def build(vid, write=True):
    v = pd.read_csv(os.path.join(HERE, f"state_{vid}_full.csv"), parse_dates=["time"])
    a = v.merge(vni, on="time", how="left")
    assert a["vnindex"].notna().all(), f"{vid}: vnindex grid mismatch"
    a["w_pub"] = a["state_pub"].map(W)
    a["w_v"] = a["state"].map(W)
    fwd1 = a["vnindex"].shift(-1) / a["vnindex"] - 1
    a["sleeve_delta"] = ((a["w_v"] - a["w_pub"]) * fwd1).fillna(0.0)
    out = a[["time", "state", "state_pub", "dep_cap", "dep_prop", "chg6m", "refi_chg6m",
             "vnindex", "w_pub", "w_v", "sleeve_delta"]]

    dev_idx = a.index[a["state"] != a["state_pub"]].to_numpy()
    eps = []
    if len(dev_idx):
        brk = np.where(np.diff(dev_idx) > GAP)[0]
        starts = np.r_[0, brk + 1]
        ends = np.r_[brk, len(dev_idx) - 1]
        vclose = a["vnindex"].to_numpy()
        for ep, (s, e) in enumerate(zip(starts, ends)):
            lo, hi = dev_idx[s], dev_idx[e]
            seg = a.loc[lo:hi]
            segd = seg[seg["state"] != seg["state_pub"]]
            def fwd(n):
                j = min(lo + n, len(a) - 1)
                return round((vclose[j] / vclose[lo] - 1) * 100, 2)
            eps.append(dict(
                ep=ep, start=str(a.loc[lo, "time"].date()), end=str(a.loc[hi, "time"].date()),
                n=len(segd), cap_min=int(segd["state"].min()),
                pub_states="/".join(str(s_) for s_ in sorted(segd["state_pub"].unique())),
                peak_chg6m=round(float(segd["chg6m"].max()), 2),
                pillarA_silent_pct=round(100.0 * (segd["refi_chg6m"] < 0.5).mean()),
                fwd20=fwd(20), fwd60=fwd(60),
                sleeve_cost_pp=round(float(a.loc[lo:hi, "sleeve_delta"].sum()) * 100, 2),
            ))
    epdf = pd.DataFrame(eps)
    if write:
        out.to_csv(os.path.join(HERE, f"event_audit_{vid}.csv"), index=False)
        epdf.to_csv(os.path.join(HERE, f"event_audit_{vid}_episodes.csv"), index=False)
    return epdf


# self-verify: rebuild D0, diff vs existing episode file
ref = pd.read_csv(os.path.join(HERE, "event_audit_D0_episodes.csv"))
chk = build("D0", write=False)
same = (len(ref) == len(chk)
        and (ref["start"] == chk["start"]).all() and (ref["end"] == chk["end"]).all()
        and (ref["n"] == chk["n"]).all()
        and np.allclose(ref["sleeve_cost_pp"], chk["sleeve_cost_pp"], atol=0.011)
        and np.allclose(ref["fwd60"], chk["fwd60"], atol=0.011))
print(f"[selfverify] D0 rebuild vs existing episodes: {'MATCH' if same else 'MISMATCH'}")
if not same:
    print(ref.to_string()); print(chk.to_string()); sys.exit(1)

for vid in sys.argv[1:]:
    epdf = build(vid)
    print(f"\n=== {vid} ===")
    print(epdf.to_string(index=False) if len(epdf) else "(no deviating sessions)")
    if len(epdf):
        print(f"total sleeve {epdf['sleeve_cost_pp'].sum():+.2f}pp | "
              f"incremental sessions {epdf['n'][epdf['pillarA_silent_pct'] >= 50].sum()}/{epdf['n'].sum()} | "
              f"mean fwd60 {epdf['fwd60'].mean():+.2f}%")
