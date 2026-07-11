# -*- coding: utf-8 -*-
"""Phase-2 fa8l re-tune — full-harness comparison + CP2 go/no-go (job Taylor_20260711_133127).

Doc 7 CSV (control + 3 finalist full + 3 finalist legfoot), tinh theo conventions registry
(daily combined_nav, logret, ANN=252 — y het fa8l_compare_20260711.py / dsr_pbo_annex.py):
  1. FULL + IS(2014-19)/OOS(2020+) CAGR/Sharpe/MaxDD/Calmar, so baseline R3.
  2. Per-year + LOO delta vs control (moi nam) + EX-2021 RIENG (chi dao user: coverage
     effect don 2021 +22.4pp — edge khong duoc phu thuoc 1 nam do).
  3. DSR (BLdP) — N=16 (N-ledger du an, khai bao truoc) + N=120/200 stress.
  4. PBO (CSCV S=16) — registry family + 3 finalist.
  5. Bootstrap circular-block L=21 B=4000 seed=12345: 5th-pct CAGR/MaxDD, P(DD<-30%).
  6. CP2 verdict tung finalist (5 tieu chi cung, khai bao truoc trong plan — KHONG noi long):
     (1) OOS CAGR >= base_OOS - 0.5pp VA OOS Calmar >= base_OOS_Calmar
     (2) LOO edge khong am khi bo bat ky nam nao (gom ex-2021)
     (3) P(DD<-30%) <= base + 0.5pp
     (4) PBO < 0.5
     (5) edge khong dao dau duoi ca 2 universe-policy (full vs legfoot)
Read-only, deterministic (seed co dinh).
"""
import os, sys, math
import numpy as np, pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)

from dsr_pbo_annex import (load_nav, daily_logret, moments, expected_max_sr, dsr,
                           cscv_pbo, circular_block_boot, family_paths, ANN)

EXP = "data/fa8l_exp"
FINALISTS = ["F1", "F6", "F12"]
CSVS = {"control": f"{EXP}/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_falegacy_control.csv"}
for f in FINALISTS:
    CSVS[f] = f"{EXP}/v23_fa8l_retune_phase2_{f}_full_r1.csv"
    CSVS[f + "_legfoot"] = f"{EXP}/v23_fa8l_retune_phase2_{f}_legfoot_r1.csv"

N_LEDGER = 16   # khai bao truoc (plan): 2 drop-in + 2 diag 0b + 12 family Phase 1

def metrics(nav):
    r = daily_logret(nav)
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1 / yrs) - 1
    sh = r.mean() / r.std(ddof=1) * math.sqrt(ANN)
    mdd = (nav / nav.cummax() - 1).min()
    return cagr * 100, sh, mdd * 100, (cagr / abs(mdd) if mdd else np.nan)

def window(nav, lo=None, hi=None):
    s = nav
    if lo: s = s[s.index >= lo]
    if hi: s = s[s.index <= hi]
    return s

def annual_returns(nav):
    out = {}
    for y in range(nav.index[0].year, nav.index[-1].year + 1):
        ny = nav[nav.index.year == y]
        if len(ny) >= 5: out[y] = ny.iloc[-1] / ny.iloc[0] - 1
    return out

def loo_cagr(ann_ret, drop_year=None):
    items = [(y, r) for y, r in ann_ret.items() if y != drop_year]
    if not items: return float("nan")
    g = np.prod([1 + r for _, r in items])
    return (g ** (1 / len(items)) - 1) * 100

navs = {}
for k, p in CSVS.items():
    if not os.path.exists(p):
        print(f"MISSING: {p}"); sys.exit(1)
    navs[k] = load_nav(p)
    print(f"loaded {k}: {len(navs[k])} daily obs ({navs[k].index[0].date()} -> {navs[k].index[-1].date()})")

print("\n" + "=" * 112)
print("[1] HEADLINE + WALK-FORWARD — baseline R3 pin 28.82/1.90/-15.7/1.83, OOS 31.59/Calmar 2.01")
print("=" * 112)
stats = {}
for k, nav in navs.items():
    full = metrics(nav); is_ = metrics(window(nav, hi="2019-12-31")); oos = metrics(window(nav, lo="2020-01-01"))
    stats[k] = dict(full=full, is_=is_, oos=oos)
    print(f"{k:12s} FULL: {full[0]:6.2f}%/Sh{full[1]:.2f}/DD{full[2]:6.1f}%/Cal{full[3]:.2f}"
          f" | IS: {is_[0]:6.2f}%/Cal{is_[3]:.2f} | OOS: {oos[0]:6.2f}%/Sh{oos[1]:.2f}/DD{oos[2]:6.1f}%/Cal{oos[3]:.2f}")

base_oos_cagr, base_oos_cal = stats["control"]["oos"][0], stats["control"]["oos"][3]

print("\n" + "=" * 112)
print("[2] PER-YEAR + LOO (delta vs control) + EX-2021 RIENG")
print("=" * 112)
ann = {k: annual_returns(nav) for k, nav in navs.items()}
years = sorted(ann["control"].keys())
print("year   control " + "".join(f"{f:>9s} {'d'+f:>8s}" for f in FINALISTS))
for y in years:
    line = f"{y}  {ann['control'].get(y, np.nan)*100:8.2f}%"
    for f in FINALISTS:
        v = ann[f].get(y, np.nan) * 100
        d = v - ann["control"].get(y, np.nan) * 100
        line += f"{v:8.2f}% {d:+7.2f}"
    print(line)

loo_results = {}
for f in FINALISTS:
    base_edge = loo_cagr(ann[f]) - loo_cagr(ann["control"])
    drops = [(y, loo_cagr(ann[f], y) - loo_cagr(ann["control"], y)) for y in years]
    neg = [y for y, e in drops if e < 0]
    ex21 = next(e for y, e in drops if y == 2021)
    loo_results[f] = dict(base=base_edge, drops=drops, neg=neg, ex2021=ex21,
                          min_edge=min(e for _, e in drops))
    print(f"\nLOO {f}: full-geo edge {base_edge:+.2f}pp | ex-2021 edge {ex21:+.2f}pp"
          f" | min sau bo 1 nam bat ky {loo_results[f]['min_edge']:+.2f}pp"
          f" | nam lam edge AM: {neg if neg else 'KHONG CO'}")
    print("   " + "  ".join(f"{y}:{e:+.2f}" for y, e in drops))

print("\n" + "=" * 112)
print("[3] DSR (BLdP) — N=16 ledger du an (primary) + stress N")
print("=" * 112)
fam_series = {}
for p in family_paths():
    s = load_nav(p)
    if s is not None and len(s) >= 2500: fam_series[p] = s
for f in FINALISTS:
    fam_series[CSVS[f]] = navs[f]
srs = np.array([daily_logret(s).mean() / daily_logret(s).std(ddof=1) for s in fam_series.values()])
var_sr = srs.var(ddof=1)
print(f"family variance basis: {len(fam_series)} configs (registry family + 3 finalist); Var(per-day SR)={var_sr:.3e}")
dsr_results = {}
for k in ["control"] + FINALISTS:
    r = daily_logret(navs[k]); T = len(r)
    sr_hat, g3, g4 = moments(r)
    out = []
    for label, N in [("N=16", N_LEDGER), (f"N={len(fam_series)}", len(fam_series)), ("N=120", 120), ("N=200", 200)]:
        p_dsr, _ = dsr(sr_hat, expected_max_sr(var_sr, N), g3, g4, T)
        if label == "N=16": dsr_results[k] = p_dsr
        out.append(f"{label}: {p_dsr:.4f}{' <<<RED' if p_dsr < 0.95 else ''}")
    print(f"{k:12s} ann-SR {sr_hat*math.sqrt(ANN):.3f}  DSR  " + "   ".join(out))

print("\n" + "=" * 112)
print("[4] PBO (CSCV S=16) — registry family + 3 finalist")
print("=" * 112)
common = None
for s in fam_series.values():
    common = s.index if common is None else common.intersection(s.index)
common = common.sort_values()
lvl = np.column_stack([s.reindex(common).values for s in fam_series.values()])
Mret = np.diff(np.log(lvl), axis=0)
pbo, logits, ncomb, ncfg, T2 = cscv_pbo(Mret, S=16)
print(f"matrix {Mret.shape[0]} x {ncfg}; PBO = {pbo:.4f} (median logit {np.median(logits):.2f}, P(lambda<0)={(logits<0).mean():.4f})")

print("\n" + "=" * 112)
print("[5] BOOTSTRAP circular-block L=21 B=4000 seed=12345")
print("=" * 112)
boot = {}
for k in ["control"] + FINALISTS:
    C, D = circular_block_boot(daily_logret(navs[k]), L=21, B=4000, seed=12345)
    boot[k] = dict(c5=np.percentile(C, 5) * 100, d5=np.percentile(D, 5) * 100,
                   p30=(D < -0.30).mean() * 100)
    print(f"{k:12s} CAGR 5th={boot[k]['c5']:5.1f}%  | MaxDD 5th={boot[k]['d5']:6.1f}%  P(DD<-30%)={boot[k]['p30']:4.1f}%")

print("\n" + "=" * 112)
print("[6] CP2 VERDICT (5 tieu chi cung khai bao truoc — KHONG noi long)")
print("=" * 112)
for f in FINALISTS:
    oos = stats[f]["oos"]
    c1 = (oos[0] >= base_oos_cagr - 0.5) and (oos[3] >= base_oos_cal)
    c2 = loo_results[f]["min_edge"] >= 0
    c3 = boot[f]["p30"] <= boot["control"]["p30"] + 0.5
    c4 = pbo < 0.5
    edge_full = stats[f]["full"][0] - stats["control"]["full"][0]
    edge_leg = stats[f + "_legfoot"]["full"][0] - stats["control"]["full"][0]
    oos_edge_full = stats[f]["oos"][0] - stats["control"]["oos"][0]
    oos_edge_leg = stats[f + "_legfoot"]["oos"][0] - stats["control"]["oos"][0]
    c5 = (edge_full * edge_leg > 0 or (edge_full >= 0 and edge_leg >= 0)) and \
         (oos_edge_full * oos_edge_leg > 0 or (oos_edge_full >= 0 and oos_edge_leg >= 0))
    allpass = all([c1, c2, c3, c4, c5])
    print(f"\n{f}:  {'*** GO ***' if allpass else '*** NO-GO ***'}")
    print(f"  1. OOS CAGR {oos[0]:.2f} >= {base_oos_cagr-0.5:.2f} va OOS Calmar {oos[3]:.2f} >= {base_oos_cal:.2f}: {'PASS' if c1 else 'FAIL'}")
    print(f"  2. LOO min edge {loo_results[f]['min_edge']:+.2f}pp >= 0 (ex-2021 {loo_results[f]['ex2021']:+.2f}pp): {'PASS' if c2 else 'FAIL'}")
    print(f"  3. P(DD<-30%) {boot[f]['p30']:.1f}% <= {boot['control']['p30']+0.5:.1f}%: {'PASS' if c3 else 'FAIL'}")
    print(f"  4. PBO {pbo:.3f} < 0.5: {'PASS' if c4 else 'FAIL'}")
    print(f"  5. edge FULL {edge_full:+.2f}pp / legfoot {edge_leg:+.2f}pp (OOS {oos_edge_full:+.2f}/{oos_edge_leg:+.2f}): {'PASS' if c5 else 'FAIL'}")

print("\n" + "=" * 112)
print("[7] CONSISTENCY — per-year delta correlation giua finalist (tinh phoi hop/tong the)")
print("=" * 112)
d = pd.DataFrame({f: {y: ann[f].get(y, np.nan) - ann["control"].get(y, np.nan) for y in years}
                  for f in FINALISTS})
print((d * 100).round(2).to_string())
print("\ncorrelation matrix (per-year delta):")
print(d.corr().round(3).to_string())

print("\nDONE phase2 compare.")
