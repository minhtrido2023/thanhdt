"""Part B — where do live 90-session book returns sit in the backtest distribution? (see PREREG.md)"""
import gzip, hashlib, io, json
import numpy as np, pandas as pd
WC = "/home/trido/thanhdt/WorkingClaude"
OUT = f"{WC}/mike/agents/Taylor/research/book_regime_fit_20261110"
LEDGERS = {"R3park0": "2026-10-08__R3-park0-pin0pct-SAN__537e349b.csv.gz",
           "park70": "2026-09-28__LICHSU-V2.3A-E1VFVN30-park70-vintage20260625__65e7bb04.csv.gz"}
pa = json.load(open(f"{OUT}/part_a_2026-07-01.json"))
H = pa["BAL"]["n_sessions"]                     # 90
LIVE = {"BAL": pa["BAL"]["ret"], "LAG": pa["LAG"]["ret"]}
LIVE_VNI = pa["BAL"]["vni_ret"]
rng = np.random.default_rng(20261110)

def load(fn):
    raw = gzip.open(f"{WC}/data/pinned_ledgers/{fn}").read()
    assert hashlib.md5(raw).hexdigest()[:8] == fn.split("__")[-1][:8], "md5 mismatch"
    df = pd.read_csv(io.BytesIO(raw), low_memory=False)
    met = df[df.record_type == "METRIC"].set_index("key")["value"].astype(float)
    d = df[df.record_type == "DAILY"].copy()
    d["ymd"] = pd.to_datetime(d["ymd"])
    d = d.set_index("ymd")[["nav_bal_ref", "nav_lag_ref", "combined_nav", "vni_close"]].astype(float)
    days = (d.index[-1] - d.index[0]).days
    cagr = (d.combined_nav.iloc[-1] / d.combined_nav.iloc[0]) ** (365.25 / days) - 1
    return d, dict(cagr_recomputed=cagr, cagr_metric=met["cagr"], diff=abs(cagr - met["cagr"]))

def sbb(r, L, H, B):       # stationary block bootstrap of H-day compounded returns
    n = len(r); out = np.empty(B)
    for b in range(B):
        idx = []; i = rng.integers(n)
        while len(idx) < H:
            idx.append(i); i = (i + 1) % n if rng.random() > 1 / L else rng.integers(n)
        out[b] = np.prod(1 + r[idx]) - 1
    return out

res = {}
for lab, fn in LEDGERS.items():
    d, chk = load(fn); res[lab] = {"control": chk}
    vr = d.vni_close.pct_change()
    for bk, col in [("BAL", "nav_bal_ref"), ("LAG", "nav_lag_ref")]:
        nav = d[col]; r = nav.pct_change()
        roll = nav.shift(-H) / nav - 1; vroll = d.vni_close.shift(-H) / d.vni_close - 1
        ov = pd.DataFrame({"b": roll, "v": vroll}).dropna()
        no = ov.iloc[::H]                                   # non-overlapping
        live = LIVE[bk]
        # conditional regression on non-overlapping windows
        X = np.c_[np.ones(len(no)), no.v]; beta = np.linalg.lstsq(X, no.b, rcond=None)[0]
        resid = no.b - X @ beta; live_res = live - (beta[0] + beta[1] * LIVE_VNI)
        cond = ov[(ov.v >= -0.12) & (ov.v <= -0.03)]
        boot = sbb(r.dropna().values, 21, H, 20000)
        # power: one 90d obs; if true mean shifted to 0 (edge gone, same vol), P(obs < 5th pct of backtest)
        mu, sd = no.b.mean(), no.b.std()
        q05 = np.quantile(no.b, 0.05)
        from math import erf, sqrt
        Phi = lambda z: 0.5 * (1 + erf(z / sqrt(2)))
        # edge-gone = book behaves like beta*VNI with no alpha: mean = beta1*mean(v); same resid sd
        mu_null = beta[1] * no.v.mean() + 0.0
        power_edge_gone = Phi((q05 - mu_null) / sd)
        res[lab][bk] = dict(
            live=live, n_overlap=len(ov), n_nonoverlap=len(no),
            pct_overlap=float((ov.b <= live).mean()), pct_nonoverlap=float((no.b <= live).mean()),
            nonoverlap_mean=float(mu), nonoverlap_sd=float(sd), nonoverlap_min=float(no.b.min()), q05=float(q05),
            pct_boot=float((boot <= live).mean()), boot_q05=float(np.quantile(boot, .05)), boot_q01=float(np.quantile(boot, .01)),
            reg_alpha=float(beta[0]), reg_beta=float(beta[1]), live_pred=float(beta[0] + beta[1] * LIVE_VNI),
            live_resid=float(live_res), pct_resid=float((resid <= live_res).mean()), resid_sd=float(resid.std()),
            z_resid=float(live_res / resid.std()),
            cond_n_overlap=len(cond), cond_n_indep_approx=int(len(cond) / H) if len(cond) else 0,
            cond_pct=float((cond.b <= live).mean()) if len(cond) else None, cond_mean=float(cond.b.mean()) if len(cond) else None,
            excess_live=live - LIVE_VNI, pct_excess_nonoverlap=float(((no.b - no.v) <= live - LIVE_VNI).mean()),
            power_detect_edge_gone_at_5pct=float(power_edge_gone))
        ov.to_csv(f"{OUT}/part_b_roll_{lab}_{bk}.csv")
json.dump(res, open(f"{OUT}/part_b.json", "w"), indent=1, default=float)
print(json.dumps(res, indent=1, default=lambda x: round(float(x), 4)))
