"""VONG 3 BAL — scoring against the 7 pre-registered criteria (PREREG.md §5) + the mandatory
exposure/selection decomposition (§6). job Taylor_20260909_121342, PAPER-ONLY.
Reads only the leg NAV CSVs written by run_leg.sh."""
import hashlib
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from dsr_pbo_annex import load_nav, daily_logret, moments, dsr, expected_max_sr, cscv_pbo  # noqa

B = ("/home/trido/thanhdt/WorkingClaude/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge"
     "_etfliqcustompitg_wtnamecap_advprice_univpit_exp_balgate%s.csv")
LEGS = ["ctrl", "a1", "a2", "a3", "a4", "b1", "b2", "b3"]
CTRL = "ctrl"
N_TRIALS = 7                       # A1-A4 + B1-B3, the whole search width of this job
PIN = dict(cagr=28.8627, final_B=1178.0099, calmar=1.6229, maxdd=-17.785,
           md5="7d053e6201c9d107685ff4d1dd9d2d2a")

nav, raw = {}, {}
for t in LEGS:
    p = B % t
    if not os.path.exists(p):
        print("MISSING", p)
        continue
    nav[t] = load_nav(p)
    raw[t] = pd.read_csv(p, low_memory=False)

md5 = hashlib.md5(open(B % CTRL, "rb").read()).hexdigest()
print("=== C7: CONTROL vs PIN R3 ===")
print(f"  control CSV md5 = {md5}   pin = {PIN['md5']}   -> {'MATCH' if md5 == PIN['md5'] else '*** MISMATCH — STOP ***'}")


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
    rows.append(dict(leg=t, **metrics(s),
                     cagr_IS=metrics(sub(s, "2014-01-01", "2019-12-31"))["cagr"],
                     cagr_OOS=metrics(sub(s, "2020-01-01", "2026-06-19"))["cagr"]))
T = pd.DataFrame(rows)
c = T[T.leg == CTRL].iloc[0]
for k in ["cagr", "cagr_IS", "cagr_OOS", "calmar", "sharpe", "maxdd"]:
    T["d_" + k] = T[k] - c[k]
pd.set_option("display.width", 250)
print(f"  CAGR {c['cagr']:.4f} (pin {PIN['cagr']}) | finalNAV {c['final_B']:.4f}B (pin {PIN['final_B']}) "
      f"| Calmar {c['calmar']:.4f} (pin {PIN['calmar']}) | MaxDD {c['maxdd']:.3f} (pin {PIN['maxdd']})")
print("\n=== A/B metrics (C1/C2/C3) ===")
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
for t in list(Y.columns):
    if t != CTRL:
        Y["d_" + t] = Y[t] - Y[CTRL]
print("\n=== per-year return %% by leg + delta vs ctrl (C4a) ===")
print(Y.round(2).to_string())
Y.to_csv("peryear.csv")

# ---- per-window (C4b) ----
W = pd.read_csv("../bal_2025_diagnosis_20260909/p1_bull_windows.csv", parse_dates=["start", "end"])
starts = list(W["start"]) + [pd.Timestamp("2100-01-01")]


def lr(t):
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
    rec = {"leg": t, "total_dlogret_pp": d.sum() * 100,
           "pre_first_window_pp": d[d.index < starts[0]].sum() * 100}
    for i in range(len(W)):
        seg = d[(d.index >= starts[i]) & (d.index < starts[i + 1])]
        rec[f"W{i+1}_{W['start'].iloc[i].date()}"] = seg.sum() * 100
    pw_rows.append(rec)
PW = pd.DataFrame(pw_rows).set_index("leg")
print("\n=== per-WINDOW delta (sum of daily log-return delta, pp; windows partition the timeline) (C4b) ===")
print(PW.round(3).T.to_string())
PW.to_csv("perwindow.csv")


def concentration(series_by_bucket, total):
    """max |bucket| / |total| — the C4a/C4b test statistic. >0.5 fails."""
    if abs(total) < 1e-12:
        return np.nan
    return float(np.max(np.abs(series_by_bucket)) / abs(total))


print("\n=== C4a / C4b concentration (max single bucket share of total delta; FAIL if > 0.50) ===")
for t in [x for x in LEGS if x != CTRL and x in nav]:
    ca = concentration(Y["d_" + t].values, Y["d_" + t].sum())
    cb = concentration(PW.loc[t].drop("total_dlogret_pp").values, PW.loc[t, "total_dlogret_pp"])
    print(f"  {t:4s} C4a_year={ca:6.2f}  C4b_window={cb:6.2f}   "
          f"{'PASS' if (ca <= 0.5 and cb <= 0.5) else 'FAIL'}")

# ---- DSR / PBO / bootstrap ----
treat = [t for t in LEGS if t != CTRL and t in nav]
sr_c = rc.mean() / rc.std(ddof=1)
srs = [daily_logret(nav[t]).mean() / daily_logret(nav[t]).std(ddof=1) for t in treat]
var_sr = np.var(srs, ddof=1) if len(srs) > 1 else 0.0
sr0 = expected_max_sr(var_sr, N_TRIALS) if var_sr > 0 else 0.0
print(f"\n=== C5a DSR (null = SR of control = {sr_c:.5f}/obs; SR0(N={N_TRIALS})={sr0:.5f}) ===")
for t in treat:
    rb = daily_logret(nav[t])
    sr_hat, g3, g4 = moments(rb)
    print(f"  {t:4s} DSR_vs_SRctrl={dsr(sr_hat, sr_c, g3, g4, len(rb))[0]:.6f}  "
          f"DSR_vs_SR0={dsr(sr_hat, sr0, g3, g4, len(rb))[0]:.6f}  "
          f"{'PASS' if dsr(sr_hat, sr_c, g3, g4, len(rb))[0] > 0.95 else 'FAIL'}")
M = np.column_stack([daily_logret(nav[t]) for t in LEGS if t in nav])
print(f"\n=== C5b PBO (CSCV S=16, {M.shape[1]} configs) = {cscv_pbo(M, S=16)[0]:.4f}  "
      f"{'PASS' if cscv_pbo(M, S=16)[0] < 0.5 else 'FAIL'} ===")


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
print("\n=== C6 block bootstrap L=21 B=4000 on the delta log-return series ===")
for t in treat:
    d = (lr(t) - rc_s).dropna().values
    bs = cbb(d) / yrs * 100
    lo, hi = np.percentile(bs, 2.5), np.percentile(bs, 97.5)
    print("  %-4s point=%+.3f pp/yr  CI95=[%+.3f, %+.3f]  P(d>0)=%.3f  %s"
          % (t, d.sum() / yrs * 100, lo, hi, (bs > 0).mean(),
             "EXCLUDES 0 -> PASS" if (lo > 0 or hi < 0) else "om 0 -> C6 FAIL"))

# ---- §6 exposure vs selection decomposition, NEUTRAL sessions only ----
print("\n=== §6 phan ra EXPOSURE vs SELECTION tren phien state=3 (NEUTRAL) ===")
dec = []
for t in LEGS:
    if t not in raw:
        continue
    D = raw[t]
    D = D[D.record_type.astype(str).str.lower().str.startswith("daily")] if "record_type" in D else D
    D = D[D["nav_bal_ref"].notna()].copy()
    D["ymd"] = pd.to_datetime(D["ymd"])
    D = D.drop_duplicates("ymd").set_index("ymd").sort_index()
    n3 = D["state"] == 3
    ws = (D["bal_stocks_ref"] / D["nav_bal_ref"])[n3]
    wp = (D["bal_etf_ref"] / D["nav_bal_ref"])[n3]
    nb = D["nav_bal_ref"]
    r3 = np.log(nb / nb.shift(1))[n3].dropna()
    dec.append(dict(leg=t, n_neutral_sessions=int(n3.sum()),
                    w_stock=ws.mean() * 100, w_park=wp.mean() * 100,
                    w_equity=(ws + wp).mean() * 100,
                    bal_ann_ret_in_neutral=(np.exp(r3.mean() * 252) - 1) * 100))
DEC = pd.DataFrame(dec).set_index("leg")
for k in ["w_stock", "w_park", "w_equity", "bal_ann_ret_in_neutral"]:
    DEC["d_" + k] = DEC[k] - DEC.loc[CTRL, k]
print(DEC.round(3).to_string())
DEC.to_csv("exposure_decomp.csv")
print("\nQuy tac dien giai chot truoc (PREREG §6.3): |d_w_equity| <= 2pp => hoan doi ro (SELECTION);"
      "\n  d_w_equity > +2pp va dCAGR>0 => phai quy phan delta cho tang exposure rong.")
