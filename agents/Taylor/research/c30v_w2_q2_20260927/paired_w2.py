#!/usr/bin/env python3
"""W2/Q2 paired block bootstrap over the A/B/C6/C10/D legs — job Taylor_20260927_141318.

PAIRED = ONE block-index sequence per bootstrap path, applied to ALL legs, so every path is the
SAME resampled world seen at different park vehicles. Copied from
`research/park_fraction_grid_20260927/paired_v2.py` (L=21, B=4000, seed=12345, calendar-year
annualisation) — the prereg names that script as the reference implementation, so the arithmetic
here is a re-use, not a re-derivation.

Reads the leg ledgers by EXPLICIT filename map (no glob): a glob would silently pick up a
neighbouring experiment's CSV, which is exactly the §8 failure mode.
"""
import io, json, os, sys
import numpy as np, pandas as pd

DATA = "/home/trido/thanhdt/WorkingClaude/data"
L, B, SEED = 21, 4000, 12345
IS_END = pd.Timestamp("2019-12-31")

LOGS = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/c30v_w2_q2_20260927/logs"

def leg_path(tag):
    """Read the ledger path the engine ITSELF printed for this EXP_TAG.

    Deliberately NOT reconstructed from the env knobs: the filename is assembled from ~20 tag
    fragments in pt_v23_audit_2014.py:710 and one wrong guess silently points the analysis at a
    neighbouring experiment (the §8 failure mode). The log line is the engine's own statement of
    where it wrote, so it cannot drift. Also asserts EXIT=0 for that leg.
    """
    log = os.path.join(LOGS, f"{tag}.log")
    txt = io.open(log, encoding="utf-8", errors="replace").read()
    assert f"EXIT=0 ({tag}" in txt, f"{tag}: leg did not exit 0 — refuse to read its numbers"
    hits = [l.split("->", 1)[1].split("(")[0].strip() for l in txt.splitlines()
            if l.strip().startswith("-> ") and l.strip().endswith("rows)")]
    assert len(hits) == 1, f"{tag}: expected exactly 1 audit-file line, got {hits}"
    return hits[0]

def load_nav(path):
    df = pd.read_csv(path, low_memory=False)
    d = df.dropna(subset=["combined_nav"])
    t = pd.to_datetime(d["ymd"], errors="coerce")
    d = d[t.notna()]; t = t[t.notna()]
    return d.groupby(t.dt.normalize())["combined_nav"].last().astype(float)

def metrics(r, ann):
    nav = np.exp(np.cumsum(r, axis=0)); peak = np.maximum.accumulate(nav, axis=0)
    yrs = r.shape[0] / ann
    cagr = nav[-1] ** (1 / yrs) - 1
    sh = r.mean(axis=0) / r.std(axis=0) * np.sqrt(ann)
    dd = (nav / peak - 1).min(axis=0)
    return cagr, sh, dd, cagr / np.abs(dd)

def boot(R, ann, N):
    rng = np.random.default_rng(SEED); nblk = int(np.ceil(N / L)); off = np.arange(L)
    C = np.empty((B, R.shape[1])); S = np.empty_like(C); D = np.empty_like(C); K = np.empty_like(C)
    for b in range(B):
        st = rng.integers(0, N, nblk)
        ix = ((st[:, None] + off[None, :]) % N).ravel()[:N]
        C[b], S[b], D[b], K[b] = metrics(R[ix], ann)
    return C, S, D, K

def run(legs, label, out_json):
    """legs: list of (name, path). The FIRST leg named 'D' is the reference for P(X>D)."""
    navs = {}
    for nm, p in legs:
        assert os.path.exists(p), f"MISSING leg ledger: {p}"
        navs[nm] = load_nav(p)
    names = [nm for nm, _ in legs]
    idx0 = navs[names[0]].index
    for nm in names:
        assert navs[nm].index.equals(idx0), f"{nm}: date index differs — paired bootstrap invalid"
    R = np.column_stack([np.diff(np.log(navs[nm].values)) for nm in names])
    N = R.shape[0]; YRS = (idx0[-1] - idx0[0]).days / 365.25; ANN = N / YRS
    print(f"\n=== {label} === {len(names)} legs aligned on {len(idx0)} days "
          f"{idx0[0].date()}..{idx0[-1].date()}  N_ret={N} yrs={YRS:.3f} obs/yr={ANN:.1f}")
    ACT = metrics(R, ANN)
    C, S, D, K = boot(R, ANN, N)
    jD = names.index("D")
    EK = K.mean(axis=0); D5 = np.percentile(D, 5, axis=0); C5 = np.percentile(C, 5, axis=0)
    PgtD = (K > K[:, [jD]]).mean(axis=0)
    dd_gate = D5[jD] - 0.02
    # IS / OOS split on the SAME return vector (not a re-run)
    dts = idx0[1:]
    m_is = dts <= IS_END; m_oos = ~m_is
    res = {}
    print(f"{'leg':<6} {'CAGR':>7} {'Sharpe':>7} {'MaxDD':>7} {'Calmar':>7} {'E[Calmar]':>9} "
          f"{'P(X>D)':>7} {'DD5th':>7} {'CAGR5th':>8} {'IS':>7} {'OOS':>7} {'DDgate':>7}")
    for i, nm in enumerate(names):
        cis = metrics(R[m_is][:, [i]], ANN)[0][0]; coos = metrics(R[m_oos][:, [i]], ANN)[0][0]
        ok = "PASS" if D5[i] >= dd_gate else "FAIL"
        print(f"{nm:<6} {ACT[0][i]*100:6.2f}% {ACT[1][i]:7.2f} {ACT[2][i]*100:6.1f}% {ACT[3][i]:7.3f} "
              f"{EK[i]:9.3f} {PgtD[i]:7.3f} {D5[i]*100:6.1f}% {C5[i]*100:7.2f}% "
              f"{cis*100:6.2f}% {coos*100:6.2f}% {ok:>7}")
        res[nm] = {"cagr_pct": round(float(ACT[0][i])*100, 3), "sharpe": round(float(ACT[1][i]), 3),
                   "maxdd_pct": round(float(ACT[2][i])*100, 2), "calmar": round(float(ACT[3][i]), 4),
                   "E_calmar": round(float(EK[i]), 4), "P_gt_D": round(float(PgtD[i]), 4),
                   "dd5th_pct": round(float(D5[i])*100, 2), "cagr5th_pct": round(float(C5[i])*100, 3),
                   "cagr_IS_2014_19_pct": round(float(cis)*100, 3),
                   "cagr_OOS_2020p_pct": round(float(coos)*100, 3),
                   "dd_gate_pass": bool(D5[i] >= dd_gate)}
    # leave-one-year-out on E[Calmar] rank stability
    loyo = {}
    yrs_all = sorted(set(dts.year))
    for y in yrs_all:
        keep = dts.year != y
        Ck, Sk, Dk, Kk = boot(R[keep], ANN, int(keep.sum()))   # same obs/yr; only the sample shrinks
        loyo[str(y)] = {nm: round(float(Kk.mean(axis=0)[i]), 4) for i, nm in enumerate(names)}
    res["_loyo_E_calmar"] = loyo
    res["_dd_gate_threshold_pct"] = round(float(dd_gate)*100, 2)
    res["_legs"] = {nm: p for nm, p in legs}
    res["_n_ret"] = int(N); res["_yrs"] = round(float(YRS), 4)
    json.dump(res, open(out_json, "w"), indent=1)
    print(f"-> {out_json}")
    print("  LOYO E[Calmar] (drop one year): " + "; ".join(
        f"{y}:" + "/".join(f"{loyo[y][nm]:.2f}" for nm in names) for y in list(loyo)[:4]) + " ...")
    return res

if __name__ == "__main__":
    tier = sys.argv[1]            # baseline | floor
    HERE = os.path.dirname(os.path.abspath(__file__))
    legs = [(nm, leg_path(f"w2{k}_{tier}"))
            for nm, k in [("D", "d"), ("A", "a"), ("B", "b"), ("C6", "c6"), ("C10", "c10")]]
    run(legs, f"tier={tier}", os.path.join(HERE, f"paired_{tier}.json"))
