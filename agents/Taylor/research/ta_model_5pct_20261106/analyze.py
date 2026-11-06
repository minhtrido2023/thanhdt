"""Phân tích deals.parquet theo PREREG §4. Ghi results.csv, byyear.csv, calib.csv, summary.json."""
import itertools, json, os
import numpy as np, pandas as pd
from scipy.stats import norm
from sklearn.linear_model import LogisticRegression

OUT = os.path.dirname(os.path.abspath(__file__))
FEE = 0.00097
PATS = ["BRK", "PB20", "PB50", "SQZ", "OSB", "FTD"]
TIERS = {"L20": 20e9, "L50": 50e9, "L100": 100e9}
SLIPS = [0.001, 0.002, 0.003]
S0 = 0.002
B = 2000
rng = np.random.default_rng(20261106)
d = pd.read_parquet(f"{OUT}/deals.parquet")
d["year"] = d.time.dt.year
d["month"] = d.time.dt.to_period("M")
d["oos"] = d.year >= 2020


def be(s):
    a = (1 - FEE - s) / (1 + FEE + s)
    return (1 - 0.95 * a) / (0.10 * a)


def net(sub, t, s):
    return sub[f"ex_{t}"] * (1 - FEE - s) / (sub[f"ent_{t}"] * (1 + FEE + s)) - 1


def boot_mean(dates_val, months):
    """bootstrap khối tháng trên chuỗi giá trị cấp ngày; trả (lo, hi, p_le0)."""
    dfm = pd.DataFrame({"v": dates_val, "m": months})
    agg = dfm.groupby("m").v.agg(["sum", "count"])
    s, cnt = agg["sum"].to_numpy(), agg["count"].to_numpy()
    k = len(s)
    if k < 5:
        return np.nan, np.nan, np.nan
    ix = rng.integers(0, k, (B, k))
    bm = s[ix].sum(1) / cnt[ix].sum(1)
    return np.quantile(bm, 0.025), np.quantile(bm, 0.975), float((bm <= 0).mean())


rows, series = [], {}
for tier, thr in TIERS.items():
    dt = d[d.mdv60 >= thr]
    for H in [10, 20]:
        for mode in ["C", "HL"]:
            t = f"{mode}{H}"
            base = dt[dt[f"rs_{t}"].isin([0, 1, 2, 3])]
            done = base[base[f"rs_{t}"] > 0].copy()
            for s in SLIPS:
                done["R"] = net(done, t, s)
                done["TP"] = (done[f"rs_{t}"] == 1).astype(float)
                ctrl = done.groupby("time")[["R", "TP"]].mean().rename(columns={"R": "cR", "TP": "cTP"})
                for p in PATS:
                    sg = done[done[p]]
                    if len(sg) == 0:
                        continue
                    att = base[base[p]]
                    dl = sg.groupby("time")[["R", "TP"]].mean().join(ctrl)
                    dl["exR"], dl["exP"] = dl.R - dl.cR, dl.TP - dl.cTP
                    dl["m"] = dl.index.to_period("M")
                    dl["oos"] = dl.index.year >= 2020
                    r = dict(pattern=p, tier=tier, H=H, mode=mode, slip=s, N_rows=len(sg), N_dates=len(dl),
                             N_months=dl.m.nunique(), unfilled=float((att[f"rs_{t}"] == 0).mean()),
                             P_TP=sg.TP.mean(), P_SL=(sg[f"rs_{t}"] == 2).mean(), P_TO=(sg[f"rs_{t}"] == 3).mean(),
                             R_mean=sg.R.mean(), R_med=sg.R.median(), ctrl_P_TP=dl.cTP.mean(), ctrl_R=dl.cR.mean(),
                             exP=dl.exP.mean(), exR=dl.exR.mean(), p_star=be(s),
                             mdv60_med=sg.mdv60.median())
                    for lab, msk in [("IS", ~dl.oos), ("OOS", dl.oos)]:
                        x = dl[msk]; sx = sg[sg.oos == (lab == "OOS")]
                        r[f"N_dates_{lab}"] = len(x)
                        r[f"P_TP_{lab}"] = sx.TP.mean() if len(sx) else np.nan
                        r[f"R_{lab}"] = sx.R.mean() if len(sx) else np.nan
                        r[f"exR_{lab}"] = x.exR.mean() if len(x) else np.nan
                        r[f"exP_{lab}"] = x.exP.mean() if len(x) else np.nan
                        r[f"ctrlP_{lab}"] = x.cTP.mean() if len(x) else np.nan
                        lo, hi, pv = boot_mean(x.exR.to_numpy(), x.m.to_numpy()) if len(x) else (np.nan,) * 3
                        r[f"exR_{lab}_lo"], r[f"exR_{lab}_hi"], r[f"p_exR_{lab}"] = lo, hi, pv
                    lo, hi, pv = boot_mean(dl.exR.to_numpy(), dl.m.to_numpy())
                    r["exR_lo"], r["exR_hi"], r["p_exR"] = lo, hi, pv
                    lo, hi, pv = boot_mean(dl.R.to_numpy(), dl.m.to_numpy())
                    r["R_lo"], r["R_hi"], r["p_R"] = lo, hi, pv
                    # LOYO
                    yrs = sorted(set(dl.index.year))
                    full = np.sign(dl.exR.mean())
                    r["loyo_flips"] = int(sum(np.sign(dl[dl.index.year != y].exR.mean()) != full for y in yrs))
                    yr = dl.groupby(dl.index.year).exR.mean()
                    r["years_pos_exR"] = f"{int((yr > 0).sum())}/{len(yr)}"
                    # post-FTSE
                    fx = sg[sg.time >= "2026-09-21"]
                    r["N_postFTSE"] = len(fx)
                    r["P_TP_postFTSE"] = fx.TP.mean() if len(fx) else np.nan
                    rows.append(r)
                    if s == S0:
                        series[(p, tier, H, mode)] = dl[["R", "exR"]]
res = pd.DataFrame(rows)

# ---------------------------------------------- DSR (họ 72 ở s=0,2%)
def dsr_family(col):
    srs, info = {}, {}
    for k, x in series.items():
        v = x[col].to_numpy()
        if len(v) < 30:
            continue
        sr = v.mean() / v.std(ddof=1)
        sk = pd.Series(v).skew(); ku = pd.Series(v).kurt() + 3
        srs[k] = sr; info[k] = (len(v), sk, ku)
    N = len(srs); V = np.var(list(srs.values()), ddof=1); g = 0.5772156649
    sr0 = np.sqrt(V) * ((1 - g) * norm.ppf(1 - 1 / N) + g * norm.ppf(1 - 1 / (N * np.e)))
    out = {}
    for k, sr in srs.items():
        T, sk, ku = info[k]
        out[k] = (sr, float(norm.cdf((sr - sr0) * np.sqrt(T - 1) / np.sqrt(1 - sk * sr + (ku - 1) / 4 * sr ** 2))))
    return out, sr0, N
dsr_R, sr0_R, NR = dsr_family("R")
dsr_X, sr0_X, NX = dsr_family("exR")
prim = res.slip == S0
for k in series:
    m = prim & (res.pattern == k[0]) & (res.tier == k[1]) & (res.H == k[2]) & (res["mode"] == k[3])
    if k in dsr_R: res.loc[m, "SR_R"], res.loc[m, "DSR_R"] = dsr_R[k]
    if k in dsr_X: res.loc[m, "SR_exR"], res.loc[m, "DSR_exR"] = dsr_X[k]

# ---------------------------------------------- PBO (CSCV S=16, metric exR)
keys = list(series.keys())
alld = sorted(set().union(*[set(series[k].index) for k in keys]))
edges = np.array_split(np.arange(len(alld)), 16)
blk = {dt: i for i, e in enumerate(edges) for dt in np.array(alld)[e]}
M = np.zeros((len(keys), 16))
for j, k in enumerate(keys):
    x = series[k].exR
    bm = x.groupby(x.index.map(blk)).mean()
    M[j, bm.index] = bm.to_numpy()
logits = []
for comb in itertools.combinations(range(16), 8):
    isb = list(comb); oob = [i for i in range(16) if i not in comb]
    best = np.argmax(M[:, isb].mean(1))
    oos = M[:, oob].mean(1)
    rk = (oos < oos[best]).sum() + 0.5 * ((oos == oos[best]).sum() - 1)
    w = (rk + 0.5) / (len(keys) + 1)
    logits.append(np.log(w / (1 - w)))
pbo = float((np.array(logits) <= 0).mean())

# ---------------------------------------------- by-year (primary C20 L20 s=0,2%)
by = []
dt = d[d.mdv60 >= TIERS["L20"]]
done = dt[dt["rs_C20"] > 0].copy()
done["R"] = net(done, "C20", S0); done["TP"] = (done.rs_C20 == 1).astype(float)
ctrl = done.groupby("time")[["R", "TP"]].mean()
cy = done.groupby("year").agg(N=("R", "size"), P_TP=("TP", "mean"), R=("R", "mean"))
cy["pattern"] = "CTRL"; by.append(cy.reset_index())
for p in PATS:
    sg = done[done[p]]
    y = sg.groupby("year").agg(N=("R", "size"), P_TP=("TP", "mean"), R=("R", "mean"))
    y["pattern"] = p; by.append(y.reset_index())
byyear = pd.concat(by)

# ---------------------------------------------- calibration (C20, L20, s=0,2%)
sig = done[done[PATS].any(axis=1)].copy()
def feats(x):
    F = x[PATS].astype(float).copy()
    F["lmdv"] = np.log10(x.mdv60) - 10
    F["vni_up"] = x.vni_up.astype(float)
    F["cma50"] = (x.c_ma50 - 1).clip(-0.5, 0.5)
    return F.fillna(0)
cal = {}
for nm, pool in [("signals", sig), ("all_eligible", done)]:
    tr, te = pool[~pool.oos], pool[pool.oos]
    lr = LogisticRegression(C=1.0, max_iter=2000).fit(feats(tr), tr.TP)
    pr = lr.predict_proba(feats(te))[:, 1]
    clim = tr.TP.mean()
    bs = float(np.mean((pr - te.TP) ** 2)); bc = float(np.mean((clim - te.TP) ** 2))
    bcoin = float(np.mean((0.5 - te.TP) ** 2))
    q = pd.qcut(pr, 10, duplicates="drop")
    rel = pd.DataFrame({"p": pr, "y": te.TP.to_numpy(), "b": q}).groupby("b", observed=True).agg(pred=("p", "mean"), obs=("y", "mean"), n=("y", "size"))
    # Brier trên trung bình cấp ngày (N độc lập) — tránh đếm dòng
    te2 = te.assign(pr=pr)
    dlv = te2.groupby("time").apply(lambda z: pd.Series({"bs": np.mean((z.pr - z.TP) ** 2), "bc": np.mean((clim - z.TP) ** 2)}), include_groups=False)
    cal[nm] = dict(n_train=len(tr), n_test=len(te), n_test_dates=int(te.time.nunique()), base_IS=float(clim),
                   base_OOS=float(te.TP.mean()), brier_model=bs, brier_clim=bc, brier_coin=bcoin,
                   BSS_vs_clim=1 - bs / bc, date_mean_BSS=float(1 - dlv.bs.mean() / dlv.bc.mean()),
                   pred_range=[float(pr.min()), float(pr.max())],
                   coef=dict(zip(feats(tr).columns, np.round(lr.coef_[0], 3).tolist())),
                   reliability=rel.reset_index(drop=True).round(4).to_dict("records"))

res.to_csv(f"{OUT}/results.csv", index=False)
byyear.to_csv(f"{OUT}/byyear.csv", index=False)
json.dump(dict(PBO=pbo, n_trials_dsr=NR, sr0_R=sr0_R, sr0_exR=sr0_X, n_trials_pbo=len(keys),
               p_star={str(s): be(s) for s in SLIPS}, calibration=cal,
               ctrl_C20_L20=dict(P_TP=float(done.TP.mean()), R=float(done.R.mean()),
                                 P_TP_IS=float(done[~done.oos].TP.mean()), P_TP_OOS=float(done[done.oos].TP.mean()))),
          open(f"{OUT}/summary.json", "w"), indent=1, default=float)
print("PBO", pbo, "N", len(keys), "p*", {s: round(be(s), 4) for s in SLIPS})
print(json.dumps(cal, indent=1, default=float)[:3000])
