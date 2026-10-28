"""Độ bền ô duy nhất có tín hiệu: hàng hóa (ICB<2000) × YTD cao. Tách IS/OOS, tier, universe_pit, năm."""
import os, numpy as np, pandas as pd
OUT = os.path.dirname(os.path.abspath(__file__))
P = pd.read_csv(f"{OUT}/panel.csv", parse_dates=["rel"])
rng = np.random.default_rng(7); B = 2000
def boot(df, fl):
    g = {k: (v.excess.to_numpy(), v[fl].to_numpy()) for k, v in df.groupby("quarter")}; ks = list(g)
    est = df[df[fl]].excess.mean() - df[~df[fl]].excess.mean(); bs = []
    for _ in range(B):
        s = rng.choice(ks, len(ks)); y = np.concatenate([g[k][0] for k in s]); f = np.concatenate([g[k][1] for k in s])
        if f.sum() and (~f).sum(): bs.append(y[f].mean() - y[~f].mean())
    return round(est, 2), *np.round(np.percentile(bs, [2.5, 97.5]), 2)
C = P[P.commodity].copy(); out = []
for th in [50, 80, 100, 150]:
    C["fl"] = C.ytd > th
    for name, m in {"ALL": C.index == C.index, "IS": ~C.oos, "OOS": C.oos, "HI": C.tier == "LAG_HI", "LO": C.tier == "LAG_LO", "IN_UNI": C.in_uni}.items():
        D = C[m]; nf = int(D.fl.sum())
        if nf < 5: out.append(dict(th=th, sub=name, n_flag=nf)); continue
        e, lo, hi = boot(D, "fl")
        out.append(dict(th=th, sub=name, n_flag=nf, n_q=D[D.fl].quarter.nunique(), n_tk=D[D.fl].ticker.nunique(),
                        exc_flag=round(D[D.fl].excess.mean(), 2), med_flag=round(D[D.fl].excess.median(), 2), diff=e, lo=lo, hi=hi))
R = pd.DataFrame(out); R.to_csv(f"{OUT}/commod_ytd_robust.csv", index=False); print(R.to_string(index=False))
f = C[C.ytd > 100]
print(f.groupby(f.rel.dt.year).agg(n=("excess", "size"), exc=("excess", "mean")).round(2).T.to_string())
print("tickers:", f.ticker.value_counts().head(12).to_dict())
# phi-hàng hóa đối chứng cùng ngưỡng theo năm
