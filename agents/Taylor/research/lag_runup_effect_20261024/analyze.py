"""Phân tích run-up vs drift LAG. Outcome chính = excess (post_ret − VNINDEX cùng cửa sổ R+5→R+30).
Quintile TRONG từng quý (nhãn `quarter`), bootstrap cụm theo quý (B=2000, seed cố định)."""
import os, json, itertools, numpy as np, pandas as pd
from scipy import stats
OUT = os.path.dirname(os.path.abspath(__file__))
P = pd.read_csv(f"{OUT}/panel.csv", parse_dates=["rel"])
rng = np.random.default_rng(20261024); B = 2000
FEATS = ["r60", "r120", "ytd", "r60_x", "r120_x", "ytd_x", "dist_hi250", "pos250", "pre_ret", "rel_ret", "pre_minus_rel", "sur_gap"]
SUBS = {"ALL": P.index == P.index, "HI": P.tier == "LAG_HI", "LO": P.tier == "LAG_LO",
        "COMMOD": P.commodity, "NONCOMMOD": ~P.commodity, "IS": ~P.oos, "OOS": P.oos, "IN_UNI": P.in_uni}

def boot_diff(df, flag, y="excess"):
    """mean(y|flag) − mean(y|~flag), bootstrap cụm quý."""
    g = {k: (v[y].to_numpy(), v[flag].to_numpy()) for k, v in df.groupby("quarter")}
    keys = list(g); est = df.loc[df[flag], y].mean() - df.loc[~df[flag], y].mean()
    bs = []
    for _ in range(B):
        ks = rng.choice(keys, len(keys))
        ys = np.concatenate([g[k][0] for k in ks]); fs = np.concatenate([g[k][1] for k in ks])
        if fs.sum() and (~fs).sum(): bs.append(ys[fs].mean() - ys[~fs].mean())
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return est, lo, hi

def quint(df, f):
    d = df.dropna(subset=[f]).copy()
    d["qn"] = d.groupby("quarter")[f].transform(lambda s: pd.qcut(s.rank(method="first"), 5, labels=False) + 1 if len(s) >= 5 else np.nan)
    return d.dropna(subset=["qn"])

rows = []
for sub, msk in SUBS.items():
    D = P[msk]
    for f in FEATS:
        d = quint(D, f)
        if len(d) < 50: continue
        means = d.groupby("qn").excess.mean()
        d["top"] = d.qn == 5; dd = d[d.qn.isin([1, 5])]
        est, lo, hi = boot_diff(dd, "top")
        ics = d.groupby("quarter").apply(lambda g: stats.spearmanr(g[f], g.excess)[0] if len(g) >= 5 else np.nan).dropna()
        rows.append(dict(sub=sub, feat=f, n=len(d), n_q=d.quarter.nunique(), **{f"Q{i}": round(means.get(i, np.nan), 2) for i in range(1, 6)},
                         Q5_Q1=round(est, 2), ci_lo=round(lo, 2), ci_hi=round(hi, 2), sig=bool(lo > 0 or hi < 0),
                         IC=round(ics.mean(), 3), IC_t=round(ics.mean() / ics.std() * np.sqrt(len(ics)), 2)))
Q = pd.DataFrame(rows); Q.to_csv(f"{OUT}/quintiles.csv", index=False)

# ngưỡng cứng
TH = {"r120>50": P.r120 > 50, "r120>30": P.r120 > 30, "r60>40": P.r60 > 40, "ytd>100": P.ytd > 100, "ytd>50": P.ytd > 50,
      "r120_x>40": P.r120_x > 40, "ytd_x>50": P.ytd_x > 50, "pre30>20": P.pre_ret > 20, "pre30>40": P.pre_ret > 40,
      "near_hi250(>-3%)": P.dist_hi250 > -3, "consec100": P.consec100, "pre>20&rel<0": (P.pre_ret > 20) & (P.rel_ret < 0)}
trow = []
for sub in ["ALL", "HI", "LO", "COMMOD", "NONCOMMOD", "IS", "OOS"]:
    D = P[SUBS[sub]].copy()
    for name, fl in TH.items():
        D["fl"] = fl[SUBS[sub]].fillna(False).astype(bool)
        nf = int(D.fl.sum())
        if nf < 10: trow.append(dict(sub=sub, rule=name, n_flag=nf)); continue
        est, lo, hi = boot_diff(D, "fl")
        trow.append(dict(sub=sub, rule=name, n_flag=nf, n_q_flag=D[D.fl].quarter.nunique(),
                         exc_flag=round(D[D.fl].excess.mean(), 2), exc_rest=round(D[~D.fl].excess.mean(), 2),
                         post_flag=round(D[D.fl].post_ret.mean(), 2), wr_flag=round((D[D.fl].excess > 0).mean(), 2),
                         diff=round(est, 2), ci_lo=round(lo, 2), ci_hi=round(hi, 2), sig=bool(lo > 0 or hi < 0)))
T = pd.DataFrame(trow); T.to_csv(f"{OUT}/thresholds.csv", index=False)

# ---- họ bộ lọc "loại sự kiện run-up" — DSR/PBO. Mỗi variant = loại cờ; metric/quý = mean(kept) − mean(all)
fam = {k: TH[k] for k in TH if k not in ("consec100",)}
qs = sorted(P.quarter.unique())
M = pd.DataFrame(index=qs, columns=list(fam), dtype=float)
for k, fl in fam.items():
    fl = fl.fillna(False)
    for qq, g in P.groupby("quarter"):
        kept = g[~fl[g.index]]
        M.at[qq, k] = (kept.excess.mean() - g.excess.mean()) if len(kept) else 0.0
M = M.fillna(0.0)
sr = M.mean() / M.std(ddof=1)
N = len(fam); T_ = len(M)
best = sr.idxmax(); srb = sr.max()
emc = 0.5772156649
sr0 = np.sqrt(sr.var(ddof=1)) * ((1 - emc) * stats.norm.ppf(1 - 1 / N) + emc * stats.norm.ppf(1 - 1 / (N * np.e)))
x = M[best]; sk, ku = stats.skew(x), stats.kurtosis(x, fisher=False)
dsr = stats.norm.cdf((srb - sr0) * np.sqrt(T_ - 1) / np.sqrt(1 - sk * srb + (ku - 1) / 4 * srb ** 2))
# PBO — CSCV S=8
S = 8; blocks = np.array_split(np.arange(T_), S); lam = []
for comb in itertools.combinations(range(S), S // 2):
    isx = np.concatenate([blocks[i] for i in comb]); oos = np.setdiff1d(np.arange(T_), isx)
    a = M.iloc[isx].mean() / M.iloc[isx].std(); b = M.iloc[oos].mean() / M.iloc[oos].std()
    r = b.rank()[a.idxmax()] / (N + 1); lam.append(np.log(r / (1 - r)))
pbo = float(np.mean(np.array(lam) <= 0))
# LOO năm cho variant tốt nhất
P["yr"] = P.rel.dt.year; loo = {}
for y in sorted(P.yr.unique()):
    s = P[P.yr != y]; fl = fam[best][s.index].fillna(False)
    loo[int(y)] = round(s[~fl].excess.mean() - s.excess.mean(), 3)
fam_out = dict(N_trials=N, T_quarters=T_, sharpe_per_q={k: round(v, 3) for k, v in sr.items()},
               mean_improve_pp={k: round(v, 3) for k, v in M.mean().items()}, best=best, DSR=round(float(dsr), 3),
               PBO=round(pbo, 3), LOO_year_best=loo)

# ---- MSR
msr = P[P.ticker == "MSR"][["quarter", "rel", "tier", "NP_R", "NP_R_prev", "surprise_B_MA", "surprise_prevQ", "r120", "ytd", "pre_ret", "rel_ret", "post_ret", "excess"]]
msr.to_csv(f"{OUT}/msr_events.csv", index=False)
json.dump(dict(family=fam_out, n_events=len(P), n_quarters=int(P.quarter.nunique())), open(f"{OUT}/summary.json", "w"), indent=1, default=str)

pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200)
print(Q[Q["sub"] == "ALL"].to_string(index=False))
print(Q[(Q["sub"] != "ALL") & Q.feat.isin(["r120", "ytd", "r120_x", "dist_hi250", "pre_ret", "sur_gap"])].to_string(index=False))
print(T.to_string(index=False))
print(json.dumps(fam_out, indent=1))
print(msr.round(2).to_string(index=False))
