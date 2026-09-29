# -*- coding: utf-8 -*-
"""CCS Phase 2 STEP 1 — score the ONE pre-registered variant (trim 50% of BOTTOM-tercile target
weight) against the five P3 criteria fixed before any number was seen. N_trials = 8.
Reuses dsr_pbo_annex.py (the registry's DSR/PBO tool) — no reinvented formulas.
Run: $DNA_PYEXE analyze_step1.py
"""
import sys, os, math, json
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
import numpy as np, pandas as pd
from dsr_pbo_annex import moments, dsr, cscv_pbo, expected_max_sr, ANN, daily_logret, circular_block_boot

D = os.path.dirname(os.path.abspath(__file__))
N_TRIALS = 8                 # 7 Phase-1 hypotheses + this post-hoc variant (pre-registered P2)
NOISE_FLOOR_PP = 0.385       # harness noise floor measured at margin-valuation-spread
IS_END = pd.Timestamp("2019-12-31")

def nav(leg):
    d = pd.read_csv(os.path.join(D, f"daily_{leg}_exp.csv"), parse_dates=["ymd"])
    return d.set_index("ymd")["combined_nav"].astype(float)

S = {leg: nav(leg) for leg in ("ctrl", "trim50")}
assert S["ctrl"].index.equals(S["trim50"].index)
idx = S["ctrl"].index
res = {}

def cagr(s):
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    return (s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1

def maxdd(s):
    return float((s / s.cummax() - 1).min())

def stats(s):
    r = daily_logret(s)
    c = cagr(s); dd = maxdd(s)
    return {"cagr_pct": 100 * c, "maxdd_pct": 100 * dd, "calmar": c / abs(dd),
            "sharpe_252": float(np.mean(r) / np.std(r, ddof=1) * math.sqrt(ANN)),
            "final_nav_bn": s.iloc[-1] / 1e9}

print("=" * 78); print("HEADLINE (full window %s -> %s)" % (idx[0].date(), idx[-1].date())); print("=" * 78)
full = pd.DataFrame({k: stats(v) for k, v in S.items()}).T
full.loc["delta"] = full.loc["trim50"] - full.loc["ctrl"]
print(full.to_string(float_format=lambda v: f"{v:,.4f}"))
d_cagr_full = full.loc["delta", "cagr_pct"]
res["full"] = full.to_dict()

# ---------------- C1 / C2 -------------------------------------------------------------------
c1 = d_cagr_full > NOISE_FLOOR_PP
c2 = full.loc["trim50", "calmar"] >= full.loc["ctrl", "calmar"]
print(f"\nC1 dCAGR {d_cagr_full:+.3f}pp vs floor {NOISE_FLOOR_PP}pp -> {'PASS' if c1 else 'FAIL'}")
print(f"C2 Calmar {full.loc['ctrl','calmar']:.4f} -> {full.loc['trim50','calmar']:.4f} -> {'PASS' if c2 else 'FAIL'}")

# ---------------- C3 IS/OOS -----------------------------------------------------------------
print("\n" + "=" * 78); print("C3  IS 2014-2019 vs OOS 2020+ (each window re-based on its own leg)"); print("=" * 78)
sub = {}
for tag, m in (("IS", idx <= IS_END), ("OOS", idx > IS_END)):
    # OOS starts from the last IS observation so the window return is continuous, not truncated
    if tag == "OOS":
        m = idx >= idx[idx <= IS_END][-1]
    row = {}
    for leg in S:
        row[leg] = stats(S[leg][m])
    t = pd.DataFrame(row).T
    t.loc["delta"] = t.loc["trim50"] - t.loc["ctrl"]
    sub[tag] = t
    print(f"\n-- {tag} ({idx[m][0].date()} -> {idx[m][-1].date()}, {int(m.sum())} sessions) --")
    print(t.to_string(float_format=lambda v: f"{v:,.4f}"))
d_is, d_oos = sub["IS"].loc["delta", "cagr_pct"], sub["OOS"].loc["delta", "cagr_pct"]
c3 = (d_is > 0) == (d_oos > 0)
print(f"\nC3 dCAGR IS {d_is:+.3f}pp / OOS {d_oos:+.3f}pp -> {'PASS (same sign)' if c3 else 'FAIL (sign flip)'}")
res["is_oos"] = {"IS": sub["IS"].to_dict(), "OOS": sub["OOS"].to_dict()}

# ---------------- C4 per-year LOO -----------------------------------------------------------
print("\n" + "=" * 78); print("C4  per-year leave-one-out (same recipe as analyze_r3.py)"); print("=" * 78)
def yearly(s):
    return {y: s[s.index.year == y].iloc[-1] / s[s.index.year == y].iloc[0] - 1
            for y in sorted(set(s.index.year)) if (s.index.year == y).sum() >= 5}
yc = {k: yearly(v) for k, v in S.items()}
def geo(yrs, d):
    return (np.prod([1 + d[y] for y in yrs]) ** (1 / len(yrs)) - 1) * 100
allyrs = sorted(yc["ctrl"])
full_avg = {k: geo(allyrs, yc[k]) for k in yc}
delta_full = full_avg["trim50"] - full_avg["ctrl"]
print(f"FULL avg-annual delta = {delta_full:+.3f}pp (geometric mean of {len(allyrs)} calendar years)")
loo = {}
for y in allyrs:
    keep = [z for z in allyrs if z != y]
    loo[y] = geo(keep, yc["trim50"]) - geo(keep, yc["ctrl"])
    print(f"   drop {y}: delta = {loo[y]:+.3f}pp   (year {y} alone contributes {delta_full - loo[y]:+.3f}pp;"
          f"  ctrl {100*yc['ctrl'][y]:+.2f}% vs trim {100*yc['trim50'][y]:+.2f}%)")
c4_sign = all((v > 0) == (delta_full > 0) for v in loo.values())
mx = max(abs(delta_full - v) for v in loo.values())
frac = mx / abs(delta_full)
print(f"C4 sign preserved on every drop: {'PASS' if c4_sign else 'FAIL'}; "
      f"largest single-year contribution {mx:.3f}pp = {frac:.0%} of full delta "
      f"{'** DOMINATES (>50%) **' if frac > 0.5 else '(<=50%)'}")
c4 = c4_sign and frac <= 0.5
res["loo"] = {"full_delta_pp": delta_full, "loo_pp": loo, "max_single_year_pp": mx, "frac": frac}

# ---------------- C5 DSR / PBO --------------------------------------------------------------
print("\n" + "=" * 78); print(f"C5  DSR (N_trials={N_TRIALS}) + PBO"); print("=" * 78)
r_c, r_t = daily_logret(S["ctrl"]), daily_logret(S["trim50"])
sr_c, _, _ = moments(r_c)
sr_t, g3, g4 = moments(r_t)
T = len(r_t)
p_vs_ctrl, z0 = dsr(sr_t, sr_c, g3, g4, T)
print(f"per-obs SR: ctrl {sr_c:.5f} (ann {sr_c*math.sqrt(ANN):.3f}) | trim50 {sr_t:.5f} (ann {sr_t*math.sqrt(ANN):.3f})")
print(f"   DSR vs SR0=ctrl (beats the pinned baseline), no N-adjustment: P={p_vs_ctrl:.4f} (z={z0:.3f})")
dsr_n = {}
for N in (7, 8, 9):
    sr0 = expected_max_sr(sr_t ** 2, N)
    p_N, z_N = dsr(sr_t, sr0, g3, g4, T)
    dsr_n[N] = p_N
    print(f"   DSR vs SR0=expected_max_sr(N={N}): P={p_N:.4f} (z={z_N:.3f}) "
          f"{'PASS (>=0.95)' if p_N >= 0.95 else 'RED FLAG (<0.95)'}")
c5a = dsr_n[N_TRIALS] >= 0.95

names = ["ctrl", "trim50"]
R = np.column_stack([daily_logret(S[n]) for n in names])
pbo, logits, n_combos, ncfg, T2 = cscv_pbo(R, S=16)
print(f"\nPBO over the 2-config family {names}: N_combos={n_combos} T_used={T2} PBO={pbo:.3f} "
      f"{'PASS (<0.5)' if pbo < 0.5 else 'FAIL (>=0.5)'}")
c5b = pbo < 0.5
res["dsr"] = {"sr_ctrl": sr_c, "sr_trim": sr_t, "p_vs_ctrl": p_vs_ctrl, "dsr_by_N": dsr_n, "pbo": pbo}

# ---------------- supporting: block bootstrap on the daily DELTA ----------------------------
print("\n" + "=" * 78); print("SUPPORT  circular-block bootstrap (L=21) on the daily log-return DELTA"); print("=" * 78)
d = r_t - r_c
# circular_block_boot returns (CAGR, DD) as a TUPLE of arrays — take the CAGR array only.
# (First pass ravel()-ed the tuple and silently mixed drawdowns into the CAGR sample.)
C_boot, _dd_boot = circular_block_boot(d, L=21, B=4000, seed=20260906)
ann = C_boot * 100
print(f"mean daily delta logret = {d.mean():.3e}  -> annualized {100*(math.exp(d.mean()*ANN)-1):+.3f}pp")
lo, hi = np.percentile(ann, [2.5, 97.5])
print(f"bootstrap 95% CI on annualized delta: [{lo:+.3f}pp, {hi:+.3f}pp]   "
      f"P(delta>0) = {(ann > 0).mean():.3f}")
res["boot"] = {"ci_lo_pp": float(lo), "ci_hi_pp": float(hi), "p_gt0": float((ann > 0).mean())}

# ---------------- verdict --------------------------------------------------------------------
print("\n" + "=" * 78); print("P3 SCORECARD (pre-registered, no criterion added or relaxed)"); print("=" * 78)
sc = [("C1 dCAGR > +0.385pp", c1, f"{d_cagr_full:+.3f}pp"),
      ("C2 Calmar not worse", c2, f"{full.loc['ctrl','calmar']:.3f} -> {full.loc['trim50','calmar']:.3f}"),
      ("C3 IS/OOS same sign", c3, f"IS {d_is:+.3f}pp / OOS {d_oos:+.3f}pp"),
      ("C4 per-year LOO sign holds, no 1 year dominates", c4, f"max single-year share {frac:.0%}"),
      ("C5a DSR >= 0.95 at N_trials=8", c5a, f"P={dsr_n[N_TRIALS]:.4f}"),
      ("C5b PBO < 0.5", c5b, f"PBO={pbo:.3f}")]
for n, ok, v in sc:
    print(f"  [{'PASS' if ok else 'FAIL'}] {n:<48} {v}")
allpass = all(x[1] for x in sc)
print(f"\nVERDICT: {'GO' if allpass else 'NO-GO'}  (any single FAIL = NO-GO, no 'nearly there')")
res["scorecard"] = [{"criterion": n, "pass": bool(ok), "value": v} for n, ok, v in sc]
res["verdict"] = "GO" if allpass else "NO-GO"
with open(os.path.join(D, "step1_result_exp.json"), "w") as fh:
    json.dump(res, fh, indent=2, default=float)
print("wrote step1_result_exp.json")
