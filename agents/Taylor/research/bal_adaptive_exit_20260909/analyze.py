"""VONG 2 BAL adaptive exit — scoring against the 7 pre-registered criteria (PREREG.md §5).
job Taylor_20260909_112201, PAPER-ONLY. Reads only the leg NAV CSVs written by run_leg.sh."""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from dsr_pbo_annex import load_nav, daily_logret, moments, dsr, expected_max_sr, cscv_pbo  # noqa

B = ("/home/trido/thanhdt/WorkingClaude/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge"
     "_etfliqcustompitg_wtnamecap_advprice_univpit_exp_baladapt%s.csv")
LEGS = ["ctrl", "a", "b", "c", "d"]   # AUDIT_EXP_TAG is lowercased by the engine
CTRL = "ctrl"
N_TRIALS = 4
PIN = dict(cagr=28.8627, final_B=1178.0099, calmar=1.6229, maxdd=-17.785)

nav = {}
for t in LEGS:
    p = B % t
    if not os.path.exists(p):
        print("MISSING", p)
        continue
    nav[t] = load_nav(p)


def metrics(s):
    r = daily_logret(s)
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    cagr = (s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1
    dd = (s / s.cummax() - 1).min()
    return dict(cagr=cagr * 100, maxdd=dd * 100, calmar=cagr / abs(dd),
                sharpe=r.mean() / r.std(ddof=1) * np.sqrt(252), final_B=s.iloc[-1] / 1e9)


def sub(s, a, b):
    return s[(s.index >= a) & (s.index <= b)]


rows = []
for t in LEGS:
    if t not in nav:
        continue
    s = nav[t]
    m = metrics(s)
    rows.append(dict(leg=t, **m,
                     cagr_IS=metrics(sub(s, "2014-01-01", "2019-12-31"))["cagr"],
                     cagr_OOS=metrics(sub(s, "2020-01-01", "2026-06-19"))["cagr"]))
T = pd.DataFrame(rows)
c = T[T.leg == CTRL].iloc[0]
for k in ["cagr", "cagr_IS", "cagr_OOS", "calmar", "sharpe", "maxdd"]:
    T["d_" + k] = T[k] - c[k]
pd.set_option("display.width", 250)
print("=== CONTROL vs PIN R3 (must be byte-identical) ===")
print(f"  CAGR {c['cagr']:.4f} (pin {PIN['cagr']}) | finalNAV {c['final_B']:.4f}B (pin {PIN['final_B']}) "
      f"| Calmar {c['calmar']:.4f} (pin {PIN['calmar']}) | MaxDD {c['maxdd']:.3f} (pin {PIN['maxdd']})")
print("\n=== A/B metrics ===")
print(T.round(4).to_string(index=False))
T.to_csv("ab_metrics.csv", index=False)

# ---- per-year (C4a) ----
yr = {}
for t in LEGS:
    if t not in nav:
        continue
    s = nav[t]
    out = {}
    for y, g in s.groupby(s.index.year):
        prev = s[s.index < g.index[0]]
        s0 = prev.iloc[-1] if len(prev) else g.iloc[0]
        out[y] = (g.iloc[-1] / s0 - 1) * 100
    yr[t] = pd.Series(out)
Y = pd.DataFrame(yr)
for t in Y.columns:
    if t != CTRL and not t.startswith("d_"):
        Y["d_" + t] = Y[t] - Y[CTRL]
print("\n=== per-year return %% by leg + delta vs ctrl ===")
print(Y.round(2).to_string())
Y.to_csv("peryear.csv")

# ---- per-window (C4b): partition the whole timeline by the 10 BULL/EXBULL entry windows.
# Each window OWNS [its start, next window start); the delta is summed daily log-return delta over
# that span, so the 10 spans + the pre-first-window head add up to the full-period delta exactly.
W = pd.read_csv("../bal_2025_diagnosis_20260909/p1_bull_windows.csv", parse_dates=["start", "end"])
starts = list(W["start"]) + [pd.Timestamp("2100-01-01")]
def lr(t):
    """log-returns as a dated Series (daily_logret returns a bare ndarray)."""
    v = daily_logret(nav[t])
    assert len(v) == len(nav[t]) - 1, (len(v), len(nav[t]))
    return pd.Series(v, index=nav[t].index[1:])

rc_s = lr(CTRL)
rc = daily_logret(nav[CTRL])
pw_rows = []
for t in LEGS:
    if t == CTRL or t not in nav:
        continue
    d = (lr(t) - rc_s).dropna()
    tot = d.sum()
    head = d[d.index < starts[0]].sum()
    rec = {"leg": t, "total_dlogret_pp": tot * 100, "pre_first_window_pp": head * 100}
    for i in range(len(W)):
        seg = d[(d.index >= starts[i]) & (d.index < starts[i + 1])]
        rec[f"W{i+1}_{W['start'].iloc[i].date()}"] = seg.sum() * 100
    pw_rows.append(rec)
PW = pd.DataFrame(pw_rows).set_index("leg")
print("\n=== per-WINDOW delta (sum of daily log-return delta, pp; windows partition the timeline) ===")
print(PW.round(3).T.to_string())
PW.to_csv("perwindow.csv")

# ---- DSR / PBO / bootstrap on the best leg ----
treat = [t for t in LEGS if t != CTRL and t in nav]
if treat:
    best = T[T.leg != CTRL].sort_values("cagr", ascending=False).iloc[0]["leg"]
    print(f"\n=== DSR / PBO / bootstrap (best leg = {best}, N_trials={N_TRIALS}) ===")
    rb = daily_logret(nav[best])
    sr_hat, g3, g4 = moments(rb)
    Tn = len(rb)
    srs = [daily_logret(nav[t]).mean() / daily_logret(nav[t]).std(ddof=1) for t in treat]
    var_sr = np.var(srs, ddof=1) if len(srs) > 1 else 0.0
    sr0 = expected_max_sr(var_sr, N_TRIALS) if var_sr > 0 else 0.0
    sr_c = rc.mean() / rc.std(ddof=1)
    print("sr_hat/obs=%.5f  var_sr(family)=%.3e  SR0(N=%d)=%.5f  sr_ctrl/obs=%.5f"
          % (sr_hat, var_sr, N_TRIALS, sr0, sr_c))
    print("DSR vs 0             = %.6f   (VO NGHIA o day - dung cho ca control)" % dsr(sr_hat, 0.0, g3, g4, Tn)[0])
    print("DSR vs SR0(N=%d)      = %.6f" % (N_TRIALS, dsr(sr_hat, sr0, g3, g4, Tn)[0]))
    print("DSR vs SR_ctrl       = %.6f   <-- C5a, nguong 0,95" % dsr(sr_hat, sr_c, g3, g4, Tn)[0])
    M = np.column_stack([daily_logret(nav[t]) for t in LEGS if t in nav])
    print("PBO (CSCV S=16, %d cau hinh) = %.4f   <-- C5b, nguong <0,5" % (M.shape[1], cscv_pbo(M, S=16)[0]))

    def cbb(r, L=21, Bn=4000, seed=12345):
        rng = np.random.default_rng(seed)
        n = len(r)
        nb = int(np.ceil(n / L))
        out = np.empty(Bn)
        for b in range(Bn):
            st = rng.integers(0, n, nb)
            idx = np.concatenate([(np.arange(s, s + L) % n) for s in st])[:n]
            out[b] = r[idx].sum()
        return out

    yrs = (nav[CTRL].index[-1] - nav[CTRL].index[0]).days / 365.25
    print("\n--- C6 block bootstrap L=21 on the delta log-return series ---")
    for t in treat:
        d = (lr(t) - rc_s).dropna().values
        bs = cbb(d) / yrs * 100
        lo, hi = np.percentile(bs, 2.5), np.percentile(bs, 97.5)
        print("  %-5s point=%+.3f pp/yr  CI95=[%+.3f, %+.3f]  P(d>0)=%.3f  %s"
              % (t, d.sum() / yrs * 100, lo, hi, (bs > 0).mean(),
                 "EXCLUDES 0" if (lo > 0 or hi < 0) else "om 0 -> C6 FAIL"))
