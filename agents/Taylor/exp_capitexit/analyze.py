# -*- coding: utf-8 -*-
"""Exit-mechanism evaluation — CAPIT (job Taylor_20260720_164006).
Evaluates E0 baseline + 6 pre-registered exit variants on the position panel.
Signal read at session k (that day's data), exit executed at Open of session k+1 (no look-ahead).
Freed capital earns 0%/day to the end of the 60-session window (conservative primary measure);
robustness variant lets it earn VNINDEX.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

OUT = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_capitexit"
pan = pd.read_csv(f"{OUT}/panel.csv", parse_dates=["time"])
HOLD = 60

VARIANTS = {
    "E0": None,
    "E1": ("signal", lambda r: r["pbz"] >= -0.5),
    "E2": ("signal", lambda r: r["pbz"] >= 0.0),
    "E3": ("signal", lambda r: (r["roe_min5y"] < 0.12) or (r["roic5y"] < 0.10) or (r["fscore"] < 6)),
    "E4": ("signal", lambda r: (r["roe_min5y"] < 0) or (r["fscore"] < 4)),
    "E5": ("decay",  lambda p, ret30: ret30 < 0),
    "E6": ("decay",  lambda p, ret30: p["pbz_at30"] <= p["pbz_entry"]),
}

def px_at(g, k):
    """Open of session k (fallback: last available Open)."""
    s = g[g["k"] == k]
    if len(s) and pd.notna(s.iloc[0]["open"]) and s.iloc[0]["open"] > 0:
        return float(s.iloc[0]["open"])
    s = g[(g["k"] <= k) & g["open"].notna() & (g["open"] > 0)]
    return float(s.iloc[-1]["open"]) if len(s) else np.nan

def vni_at(g, k):
    s = g[(g["k"] <= k) & g["vni"].notna()]
    return float(s.iloc[-1]["vni"]) if len(s) else np.nan

def eval_position(g, vid, redeploy=False):
    """Return (final_return, exit_k or None, sessions_held)."""
    g = g.sort_values("k")
    kmax = int(g["k"].max())
    kend = min(HOLD, kmax)
    px_in = float(g.iloc[0]["px_in"])
    hold_ret = px_at(g, kend) / px_in - 1
    if vid == "E0":
        return hold_ret, None, kend

    kind, fn = VARIANTS[vid]

    if kind == "signal":
        for k in range(1, kend):                       # signal at k, exit at Open k+1
            r = g[g["k"] == k]
            if not len(r): continue
            r = r.iloc[0]
            if pd.isna(r["pbz"]) and vid in ("E1", "E2"): continue
            try:
                fire = bool(fn(r))
            except Exception:
                continue
            if fire:
                px_out = px_at(g, k + 1)
                if not np.isfinite(px_out): continue
                ret = px_out / px_in - 1
                if redeploy:                            # freed capital tracks VNINDEX to window end
                    v0, v1 = vni_at(g, k + 1), vni_at(g, kend)
                    if np.isfinite(v0) and np.isfinite(v1) and v0 > 0:
                        ret = (1 + ret) * (v1 / v0) - 1
                return ret, k + 1, k + 1
        return hold_ret, None, kend

    # time-decay: half-size cut at session 31 if condition met at session 30
    k30 = 30
    if kend <= k30 + 1:
        return hold_ret, None, kend
    r30 = g[g["k"] == k30]
    if not len(r30):
        return hold_ret, None, kend
    px30 = px_at(g, k30 + 1)
    if not np.isfinite(px30):
        return hold_ret, None, kend
    ret30 = px30 / px_in - 1
    p = dict(pbz_at30=float(r30.iloc[0]["pbz"]) if pd.notna(r30.iloc[0]["pbz"]) else np.nan,
             pbz_entry=float(g.iloc[0]["pbz_entry"]))
    try:
        fire = bool(fn(p, ret30))
    except Exception:
        fire = False
    if not fire:
        return hold_ret, None, kend
    half = ret30
    if redeploy:
        v0, v1 = vni_at(g, k30 + 1), vni_at(g, kend)
        if np.isfinite(v0) and np.isfinite(v1) and v0 > 0:
            half = (1 + ret30) * (v1 / v0) - 1
    return 0.5 * half + 0.5 * hold_ret, k30 + 1, kend

def run(redeploy=False):
    recs = []
    for (ev, tk), g in pan.groupby(["event", "ticker"]):
        row = dict(event=ev, ticker=tk)
        for vid in VARIANTS:
            r, xk, held = eval_position(g, vid, redeploy)
            row[vid] = r
            row[f"{vid}_xk"] = xk
        recs.append(row)
    return pd.DataFrame(recs)

def cluster_t(pos, vid):
    """Paired diff vs E0, clustered by event (14 clusters) — the honest power limit."""
    d = pos.groupby("event").apply(lambda x: (x[vid] - x["E0"]).mean(), include_groups=False)
    if d.std(ddof=1) == 0 or len(d) < 3: return np.nan, d
    return d.mean() / (d.std(ddof=1) / np.sqrt(len(d))), d

def report(pos, label):
    print(f"\n{'='*78}\n{label}\n{'='*78}")
    sleeve = pos.groupby("event")[list(VARIANTS)].mean()
    hdr = f"{'variant':6s} {'mean':>8s} {'median':>8s} {'worst':>8s} {'p5_pos':>8s} {'t_clu':>7s} {'nfire':>6s} {'LOOsign':>8s} {'IS':>8s} {'OOS':>8s}"
    print(hdr); print("-" * len(hdr))
    res = {}
    for vid in VARIANTS:
        m = sleeve[vid].mean(); md = sleeve[vid].median(); w = sleeve[vid].min()
        p5 = np.percentile(pos[vid], 5)
        nf = int(pos[f"{vid}_xk"].notna().sum()) if vid != "E0" else 0
        if vid == "E0":
            t, loo, is_, oos = np.nan, "-", np.nan, np.nan
        else:
            t, d = cluster_t(pos, vid)
            # LOO by event: does dropping any one event flip the sign of mean improvement?
            signs = {np.sign(d.drop(e).mean()) for e in d.index}
            loo = "STABLE" if len(signs) == 1 else "FLIP"
            evs = pd.to_datetime(d.index)
            is_ = d[evs < "2020-01-01"].mean(); oos = d[evs >= "2020-01-01"].mean()
        print(f"{vid:6s} {m:+8.2%} {md:+8.2%} {w:+8.2%} {p5:+8.2%} "
              f"{t if np.isfinite(t) else float('nan'):7.2f} {nf:6d} {loo:>8s} "
              f"{is_:+8.2%} {oos:+8.2%}" if vid != "E0" else
              f"{vid:6s} {m:+8.2%} {md:+8.2%} {w:+8.2%} {p5:+8.2%} {'-':>7s} {'-':>6s} {'-':>8s} {'-':>8s} {'-':>8s}")
        res[vid] = dict(mean=m, median=md, worst=w, p5=p5, t=t, nfire=nf,
                        loo=loo if vid != "E0" else "-", is_=is_, oos=oos)
    return sleeve, res

pos = run(redeploy=False)
sleeve, res = report(pos, "PRIMARY — freed capital earns 0% to window end (conservative)")
pos.to_csv(f"{OUT}/positions.csv", index=False)
sleeve.to_csv(f"{OUT}/sleeve_by_event.csv")

pos_r = run(redeploy=True)
report(pos_r, "ROBUSTNESS — freed capital tracks VNINDEX (redeploy proxy)")

# GO/NO-GO scorecard on the primary measure
print(f"\n{'='*78}\nGO/NO-GO vs PRE-REGISTERED CRITERIA (primary measure)\n{'='*78}")
b = res["E0"]
for vid in [v for v in VARIANTS if v != "E0"]:
    r = res[vid]
    c1 = (r["mean"] - b["mean"] >= 0.01) and (r["median"] > b["median"])
    c2 = (r["worst"] >= b["worst"]) and (r["p5"] >= b["p5"])
    c3 = np.isfinite(r["t"]) and r["t"] > 2.6
    c4 = r["loo"] == "STABLE"
    c5 = np.sign(r["is_"]) == np.sign(r["oos"])
    verdict = "GO-candidate" if all([c1, c2, c3, c4, c5]) else (
        "INCONCLUSIVE" if (c1 and c2 and c4 and c5) else "NO-GO")
    print(f"{vid}: (i)improve={c1} (ii)tail_ok={c2} (iii)t>2.6={c3} (iv)LOO={c4} (v)IS/OOS={c5} -> {verdict}")

# intra-event correlation — how much independent power do 66 positions really give?
rr = pan[pan["k"] == 60][["event", "ticker"]].copy()
w = pos.pivot_table(index="event", values="E0")
within = pos.groupby("event")["E0"].std(ddof=1).mean()
across = pos.groupby("event")["E0"].mean().std(ddof=1)
print(f"\nIntra-event dispersion (mean within-event sd of position return) = {within:.2%}")
print(f"Across-event dispersion (sd of event means)                        = {across:.2%}")
print("-> positions inside one washout share the same market shock; effective N is the "
      "14 events, NOT 66 positions.")
