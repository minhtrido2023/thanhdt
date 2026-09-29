"""R3 T1-floor legs: per-year LOO on delta-vs-ctrl + DSR + PBO family + liquidity/universe check.
Job Taylor_20260906_022452. Reuses dsr_pbo_annex.py (already the registry's DSR/PBO tool), no
reinvented formulas. Run from repo root: $DNA_PYEXE .../analyze_r3.py
"""
import sys, math, json
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
import numpy as np, pandas as pd
from dsr_pbo_annex import moments, dsr, cscv_pbo, expected_max_sr, ANN, load_nav, daily_logret

D = "/home/trido/thanhdt/WorkingClaude/data"
FILES = {
    "ctrl": f"{D}/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_ctrl_univpit_exp_ctrl.csv",
    "t1abs": f"{D}/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_t1abs_univpit_exp_t1abs.csv",
    "t1demean": f"{D}/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_t1demean_univpit_exp_t1demean.csv",
}

series = {name: load_nav(path) for name, path in FILES.items()}
for n, s in series.items():
    print(f"loaded {n}: {len(s)} daily obs, {s.index.min().date()}->{s.index.max().date()}")

def yearly_cagr_contrib(s):
    """Per-year simple return (matches engine's own 'YYYY: +NN%' print convention)."""
    out = {}
    for y in range(s.index[0].year, s.index[-1].year + 1):
        ny = s[s.index.year == y]
        if len(ny) < 5: continue
        out[y] = ny.iloc[-1] / ny.iloc[0] - 1
    return out

def cagr_excl_year(yearly, y_excl):
    """Geometric-mean annual return recompute, dropping one year's contribution entirely."""
    yrs = [y for y in yearly if y != y_excl]
    if not yrs: return float("nan")
    g = np.prod([1 + yearly[y] for y in yrs]) ** (1 / len(yrs)) - 1
    return g * 100

print("\n" + "=" * 70)
print("PER-YEAR LOO on delta-vs-ctrl (drop 1 year, recompute annualized-avg return delta)")
print("=" * 70)
yc = {n: yearly_cagr_contrib(s) for n, s in series.items()}
full_avg = {n: (np.prod([1 + v for v in yc[n].values()]) ** (1 / len(yc[n])) - 1) * 100 for n in yc}
for leg in ("t1abs", "t1demean"):
    delta_full = full_avg[leg] - full_avg["ctrl"]
    print(f"\n-- {leg} vs ctrl: FULL avg-annual delta = {delta_full:+.2f}pp --")
    loo_deltas = {}
    for y in sorted(yc["ctrl"]):
        d_t = cagr_excl_year(yc[leg], y) - cagr_excl_year(yc["ctrl"], y)
        loo_deltas[y] = d_t
        carry = (delta_full - d_t)  # how much LEAVING this year out changes the delta
        print(f"   drop {y}: delta_excl_{y} = {d_t:+.2f}pp  (this year alone contributes "
              f"{carry:+.2f}pp of the {delta_full:+.2f}pp full delta)")
    max_single_year_contrib = max(abs(delta_full - d) for d in loo_deltas.values())
    frac = max_single_year_contrib / abs(delta_full) if delta_full != 0 else float("inf")
    print(f"   => largest single-year contribution = {max_single_year_contrib:.2f}pp "
          f"({frac:.0%} of the {delta_full:+.2f}pp full delta) "
          f"{'** DOMINATES (>50%) **' if frac > 0.5 else '(<=50%, not carried by 1 year)'}")

print("\n" + "=" * 70)
print("DSR (per leg vs ctrl anchor) -- N_trials audited: Phase0=4 axes + Phase0b=3 floor variants")
print("= 7 (dispatch floor) ; this R3 job itself explores 2 backtest-level variants (abs/demean)")
print("=> N=9 used as the conservative operative N; N=7 shown for comparison")
print("=" * 70)
r_ctrl = daily_logret(series["ctrl"])
sr_ctrl, _, _ = moments(r_ctrl)
for leg in ("t1abs", "t1demean"):
    r = daily_logret(series[leg])
    T = len(r)
    sr_hat, g3, g4 = moments(r)
    p_vs_ctrl, z = dsr(sr_hat, sr_ctrl, g3, g4, T)
    print(f"\n-- {leg}: per-obs SR={sr_hat:.5f} (ann {sr_hat*math.sqrt(ANN):.3f}) vs "
          f"ctrl SR={sr_ctrl:.5f} (ann {sr_ctrl*math.sqrt(ANN):.3f}) --")
    print(f"   DSR vs SR0=ctrl (beats baseline), no N-adjustment: P={p_vs_ctrl:.4f} (z={z:.3f})")
    # also deflate SR0 upward using expected_max_sr under N trials as a stricter null (accounts
    # for the multi-trial search that preceded this specific leg being tested)
    var_sr = np.var(r, ddof=1) / (np.mean(r) ** 2) if np.mean(r) != 0 else np.var(r, ddof=1)
    for N in (7, 9):
        sr0_N = expected_max_sr(sr_hat ** 2, N)  # var of SR estimator proxy, BLdP convention
        p_N, z_N = dsr(sr_hat, sr0_N, g3, g4, T)
        print(f"   DSR vs SR0=expected_max_sr(N={N}) deflated null: P={p_N:.4f} (z={z_N:.3f}) "
              f"{'RED FLAG (<0.95)' if p_N < 0.95 else 'PASS (>=0.95)'}")

print("\n" + "=" * 70)
print("PBO across 3-leg family {ctrl, t1abs, t1demean}")
print("=" * 70)
names = list(series.keys())
common_idx = None
for s in series.values():
    common_idx = s.index if common_idx is None else common_idx.intersection(s.index)
common_idx = common_idx.sort_values()
R = np.column_stack([daily_logret(series[n].reindex(common_idx).ffill()) for n in names])
pbo, logits, n_combos, ncfg, T2 = cscv_pbo(R, S=16)
print(f"configs={names}  N_combos={n_combos}  T_used={T2}  PBO={pbo:.3f}")
print(f"Read: PBO>=0.5 => family prone to overfitting if picking apparent-best after the fact.")
