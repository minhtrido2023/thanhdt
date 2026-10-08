"""PREREG evaluation (job Taylor_20261008_163222): per carry convention, treatment vs control —
FULL/IS/OOS CAGR (leg_metrics formula = simulate_holistic_nav.metrics, calendar-annualized), Δ, leave-one-year-out
ΔCAGR + drop{2020,2021}, DSR on daily excess (treat−ctl) with N_trials=4 (dsr_pbo_annex BLdP functions)."""
import sys, glob, hashlib, numpy as np, pandas as pd
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/repin_dep1m_20260928")
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from leg_metrics import load_nav
def met(nav):   # unrounded copy of leg_metrics.met (calendar annualization, spy=len(r)/yrs)
    n_yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    r = nav.pct_change().dropna()
    return {"cagr": (nav.iloc[-1] / nav.iloc[0]) ** (1 / n_yrs) - 1,
            "sharpe": r.mean() / r.std() * np.sqrt(len(r) / n_yrs),
            "maxdd": ((nav - nav.cummax()) / nav.cummax()).min()}
import dsr_pbo_annex as A
D = "/home/trido/thanhdt/WorkingClaude/data/"
def f(tag): 
    g = glob.glob(D + f"*_exp_{tag}_univpit*.csv"); assert len(g) == 1, (tag, g); return g[0]
def cagr_from_rets(r, yrs): return (1 + r).prod() ** (1 / yrs) - 1
res, ex = [], {}
for carry in ["off", "1m"]:
    cn = load_nav(f(f"bmx_ctl_{carry}"))
    for m in [16, 20]:
        tag = f"bmx_m{m}_{carry}"; p = f(tag); tn = load_nav(p)
        md5 = hashlib.md5(open(p, "rb").read()).hexdigest()
        row = {"leg": tag, "md5": md5}
        for nm, a, b in [("FULL", "2014-01-01", "2026-12-31"), ("IS", "2014-01-01", "2019-12-31"), ("OOS", "2020-01-01", "2026-12-31")]:
            mt = met(tn[(tn.index >= a) & (tn.index <= b)]); mc = met(cn[(cn.index >= a) & (cn.index <= b)])
            row[f"{nm}_cagr"] = mt["cagr"]; row[f"d{nm}"] = mt["cagr"] - mc["cagr"]
            if nm == "FULL": row.update(sharpe=mt["sharpe"], maxdd=mt["maxdd"], dSharpe=mt["sharpe"] - mc["sharpe"], dMaxDD=mt["maxdd"] - mc["maxdd"])
        rt, rc = tn.pct_change().dropna(), cn.pct_change().dropna()
        yrs = (tn.index[-1] - tn.index[0]).days / 365.25
        loo = {}
        for y in sorted(set(rt.index.year)):
            k = rt.index.year != y; yy = yrs - (k == False).sum() / len(rt) * yrs
            loo[y] = cagr_from_rets(rt[k], yy) - cagr_from_rets(rc[k], yy)
        k = ~rt.index.year.isin([2020, 2021]); yy = yrs * k.mean()
        row["d_drop2021_22"] = None
        row["d_drop2020_21"] = cagr_from_rets(rt[k], yy) - cagr_from_rets(rc[k], yy)
        row["loo_min"] = min(loo.values()); row["loo_min_year"] = min(loo, key=loo.get)
        row["loo_allpos"] = all(v > 0 for v in loo.values()); row["loo_max"]=max(loo.values()); row["loo_max_year"]=max(loo,key=loo.get)
        row["peryear_d"] = {y: round((((1 + rt[rt.index.year == y]).prod()) - ((1 + rc[rc.index.year == y]).prod())) * 100, 3) for y in sorted(set(rt.index.year))}
        e = np.log1p(rt) - np.log1p(rc); ex[tag] = e; row["n_days_nonzero_ex"] = int((e.abs() > 1e-12).sum())
        res.append(row)
# DSR on excess, N=4, var of per-obs SR across the 4 excess series
srs = {k: A.moments(v.values)[0] for k, v in ex.items() if np.abs(v.values).max() > 1e-15}
var_sr = float(np.var(list(srs.values()), ddof=1)) if len(srs) > 1 else 0.0
for row in res:
    e = ex[row["leg"]].values
    if np.abs(e).max() < 1e-15: row["exSR_ann"] = 0.0; row["DSR"] = float('nan'); row.pop("d_drop2021_22"); continue
    sr, g3, g4 = A.moments(e)
    sr0 = A.expected_max_sr(var_sr, 4) if var_sr > 0 else 0.0
    row["exSR_ann"] = sr * np.sqrt(A.annual_obs(ex[row["leg"]])); row["DSR"] = A.dsr(sr, sr0, g3, g4, len(e))
    row.pop("d_drop2021_22")
pd.set_option("display.width", 250)
R = pd.DataFrame(res); print(R.drop(columns=["peryear_d"]).round(4).to_string(index=False))
for r in res: print(r["leg"], "per-year Δ(pp of yearly return):", r["peryear_d"])
R.to_csv("evaluate.csv", index=False)
