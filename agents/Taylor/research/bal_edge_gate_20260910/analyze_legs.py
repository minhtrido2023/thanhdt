# -*- coding: utf-8 -*-
"""analyze_legs.py — BUOC 4 analysis: metrics table, per-year, placebo, leave-one-episode-out.

Reads each leg's audit CSV (record_type=METRIC/DAILY/ANNUAL) and recomputes the headline
metrics INDEPENDENTLY from the DAILY combined-NAV column, so the printed table is not just
the harness's own self-report (quant-research skill #16).
"""
import os, sys, io, glob
import numpy as np, pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"; os.chdir(WORKDIR)
BASE = "data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_%s_univpit.csv"
LEGS = ["bg_ctrl", "bg_inert", "bg_g0", "bg_g4", "bg_g6", "bg_g8", "bg_g10", "bg_plac"]
LABEL = {"bg_ctrl": "ctrl (pin R3)", "bg_inert": "inert copy (no mask)", "bg_g0": "g0  slots 12->0",
         "bg_g4": "g4  slots 12->4", "bg_g6": "g6  slots 12->6  <-- PRE-COMMITTED",
         "bg_g8": "g8  slots 12->8", "bg_g10": "g10 slots 12->10", "bg_plac": "placebo (calendar mask, slots 12->6)"}

EPISODES = [("ep6", "2020-10-06", "2021-02-18"), ("ep8", "2021-03-05", "2021-07-23"),
            ("ep14", "2024-01-24", "2024-05-13"), ("ep20", "2026-01-28", "2026-02-12")]


def load(leg):
    f = BASE % leg
    if not os.path.exists(f): return None
    d = pd.read_csv(f, low_memory=False)
    m = d[d.record_type == "METRIC"].set_index("key")["value"].astype(float)
    dl = d[d.record_type == "DAILY"].copy()
    navcol = [c for c in dl.columns if "combined" in c.lower() and "nav" in c.lower()]
    if not navcol:
        num = dl.apply(lambda c: pd.to_numeric(c, errors="coerce"))
        navcol = [max(((c, num[c].notna().sum()) for c in num.columns if "nav" in c.lower()),
                      key=lambda t: t[1])[0]]
    nav = pd.Series(pd.to_numeric(dl[navcol[0]], errors="coerce").values,
                    index=pd.to_datetime(dl["ymd"])).dropna().sort_index()
    return m, nav, navcol[0]


def metrics(nav):
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1 / yrs) - 1
    r = nav.pct_change().dropna()
    spy = len(r) / yrs
    sh = r.mean() / r.std(ddof=1) * np.sqrt(spy) if r.std(ddof=1) > 0 else np.nan
    dd = (nav / nav.cummax() - 1).min()
    return cagr, sh, dd, (cagr / abs(dd) if dd else np.nan), nav.iloc[-1]


data = {}
for leg in LEGS:
    got = load(leg)
    if got is None: print(f"  (missing: {leg})"); continue
    data[leg] = got

print("NAV column used:", {k: v[2] for k, v in data.items()})
print("\n" + "=" * 118)
print("HEADLINE (left = harness METRIC rows; right = INDEPENDENT recompute from the DAILY NAV column)")
print("=" * 118)
hdr = f"{'leg':38s} {'CAGR':>7s} {'Sharpe':>7s} {'MaxDD':>7s} {'Calmar':>7s} {'FinalNAV_B':>11s} | {'reCAGR':>7s} {'reDD':>7s} {'selfchk':>9s}"
print(hdr); print("-" * 118)
ctrl_m = data["bg_ctrl"][0]
rows = {}
for leg in LEGS:
    if leg not in data: continue
    m, nav, _ = data[leg]
    c2, s2, d2, k2, f2 = metrics(nav)
    err = max(abs(m.get("cash_flow_identity_max_err_vnd_BAL", 0)), abs(m.get("cash_flow_identity_max_err_vnd_LAG", 0)),
              abs(m.get("final_nav_identity_err_vnd_BAL", 0)), abs(m.get("final_nav_identity_err_vnd_LAG", 0)))
    rows[leg] = dict(cagr=m["cagr"], sharpe=m["sharpe_252"], dd=m["max_dd"], calmar=m["calmar"], nav=m["final_nav_vnd"])
    print(f"{LABEL[leg]:38s} {m['cagr']*100:6.2f}% {m['sharpe_252']:7.2f} {m['max_dd']*100:6.2f}% "
          f"{m['calmar']:7.2f} {m['final_nav_vnd']/1e9:11.2f} | {c2*100:6.2f}% {d2*100:6.2f}% "
          f"{('0 VND' if err < 1e-3 else f'{err:.1e}'):>9s}")

print("\n" + "=" * 118)
print("DELTA vs ctrl")
print("=" * 118)
print(f"{'leg':38s} {'dCAGR':>9s} {'dSharpe':>9s} {'dMaxDD':>9s} {'dCalmar':>9s} {'dNAV_B':>10s}")
print("-" * 118)
c = rows["bg_ctrl"]
for leg in LEGS:
    if leg not in rows or leg == "bg_ctrl": continue
    r = rows[leg]
    print(f"{LABEL[leg]:38s} {(r['cagr']-c['cagr'])*100:+8.2f}pp {r['sharpe']-c['sharpe']:+9.2f} "
          f"{(r['dd']-c['dd'])*100:+8.2f}pp {r['calmar']-c['calmar']:+9.2f} {(r['nav']-c['nav'])/1e9:+10.2f}")

# ---------------- per-year & leave-one-out on the LOG-return difference ----------------
if "bg_g6" in data:
    nc = data["bg_ctrl"][1]; ng = data["bg_g6"][1]
    idx = nc.index.intersection(ng.index)
    lc = np.log(nc.loc[idx]).diff().fillna(0.0); lg = np.log(ng.loc[idx]).diff().fillna(0.0)
    diff = lg - lc
    yrs_total = (idx[-1] - idx[0]).days / 365.25
    tot = diff.sum()

    print("\n" + "=" * 118)
    print("PER-YEAR contribution of the gate (g6 - ctrl, log-return difference; +ve = gate helped)")
    print("=" * 118)
    by = diff.groupby(idx.year).sum()
    ga = pd.read_csv("mike/agents/Taylor/research/bal_edge_gate_20260910/gate_mask.csv", parse_dates=["time"])
    gy = ga.groupby(ga.time.dt.year)["gate_active"].sum()
    print(f"{'year':6s} {'gate_days':>10s} {'dlog':>10s} {'LOO dCAGR (drop this year)':>28s}")
    signs = []
    for y in by.index:
        loo = tot - by[y]
        loo_days = (idx[-1] - idx[0]).days - 365.25 * 0  # approximate: keep horizon, drop contribution
        loo_cagr = (np.exp(loo / yrs_total) - 1) * 100
        base_cagr = (np.exp(tot / yrs_total) - 1) * 100
        print(f"{y:6d} {int(gy.get(y,0)):10d} {by[y]:+10.4f} {loo_cagr:+27.2f}pp")
        if int(gy.get(y, 0)) > 0: signs.append(np.sign(by[y]))
    print(f"\n  full-sample dCAGR (log basis) = {(np.exp(tot/yrs_total)-1)*100:+.2f}pp")
    print(f"  years where the gate was active AND contribution > 0: "
          f"{int(sum(1 for s in signs if s>0))}/{len(signs)}")

    print("\n" + "=" * 118)
    print("LEAVE-ONE-EPISODE-OUT (drop one BULL episode's contribution; N=4)")
    print("=" * 118)
    print(f"{'episode':10s} {'window':26s} {'dlog':>10s} {'ep dCAGR':>11s} {'LOO dCAGR':>11s}")
    ep_signs = []
    for name, a, b in EPISODES:
        msk = (idx >= a) & (idx <= b)
        s = diff[msk].sum()
        ep_signs.append(np.sign(s))
        print(f"{name:10s} {a+' -> '+b:26s} {s:+10.4f} {(np.exp(s/yrs_total)-1)*100:+10.2f}pp "
              f"{(np.exp((tot-s)/yrs_total)-1)*100:+10.2f}pp")
    resid = tot - sum(diff[(idx >= a) & (idx <= b)].sum() for _, a, b in EPISODES)
    print(f"{'residual':10s} {'(outside the 4 episodes)':26s} {resid:+10.4f} "
          f"{(np.exp(resid/yrs_total)-1)*100:+10.2f}pp")
    print(f"\n  episodes with positive contribution: {int(sum(1 for s in ep_signs if s>0))}/4"
          f"   sign test p = {0.125 if abs(sum(ep_signs))==4 else 0.625 if abs(sum(ep_signs))==2 else 1.0}")
