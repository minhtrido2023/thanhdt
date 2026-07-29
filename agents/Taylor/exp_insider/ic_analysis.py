"""IC panel so bo cho tin hieu insider (DDIND+DDRP) — job Taylor_20260729_015830.
N trials khai bao TRUOC = 6 bien the tin hieu x 1 horizon chinh (fwd20). fwd60 chi bao cao tham khao.
KHONG sweep tham so: cua so 180d/90d chon truoc theo ly thuyet (ban cong bo ket qua ~5d sau end_date).
"""
import numpy as np, pandas as pd
from scipy import stats

D = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_insider"
df = pd.read_csv(f"{D}/panel.csv", parse_dates=["time"])
df = df[df.fwd20.notna()].copy()

df["ey"] = np.where(df.PE > 0, 1.0 / df.PE, np.nan)
df["adv_sh"] = df.Volume_1M * 20.0

SIG = {}
SIG["S1_netpers_180"] = df.nbuy_180 - df.nsell_180
SIG["S2_netpers_90"]  = df.nbuy_90 - df.nsell_90
SIG["S3_netsh_osh"]   = np.where(df.oshares > 0, df.net_sh_180 / df.oshares, np.nan)
SIG["S4_netsh_adv"]   = np.where(df.adv_sh > 0, df.net_sh_180 / df.adv_sh, np.nan)
SIG["S5_sign_180"]    = np.sign(df.nbuy_180 - df.nsell_180)
SIG["S6_buyonly_180"] = ((df.nbuy_180 > 0) & (df.nsell_180 == 0)).astype(float)
for k, v in SIG.items():
    df[k] = v

def resid(y, X):
    """residual cua y sau khi bo phan giai thich boi X (co intercept). NaN-safe da loc truoc."""
    X = np.column_stack([np.ones(len(y))] + [X[:, j] for j in range(X.shape[1])])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return y - X @ beta

def ic_series(sub_col, ret_col, controls=()):
    out = []
    for d, g in df.groupby("time"):
        cols = [sub_col, ret_col, *controls]
        g = g.dropna(subset=cols)
        if len(g) < 30 or g[sub_col].nunique() < 3:
            continue
        s = stats.rankdata(g[sub_col]); r = stats.rankdata(g[ret_col])
        if controls:
            C = np.column_stack([stats.rankdata(g[c]) for c in controls])
            s = resid(s, C); r = resid(r, C)
            if np.std(s) < 1e-9:
                continue
        out.append((d, np.corrcoef(s, r)[0, 1], len(g)))
    return pd.DataFrame(out, columns=["time", "ic", "n"]).set_index("time")

def summarise(ics, label):
    if len(ics) < 12:
        return dict(sig=label, n_months=len(ics), ic="NA")
    ic = ics.ic
    t = ic.mean() / ic.std(ddof=1) * np.sqrt(len(ic))
    is_m = ic[ic.index < "2020-01-01"]; oos_m = ic[ic.index >= "2020-01-01"]
    return dict(sig=label, n_months=len(ic), avg_n=round(ics.n.mean()),
                IC=round(ic.mean(), 4), t=round(t, 2), hit=round((ic > 0).mean(), 3),
                IC_IS=round(is_m.mean(), 4) if len(is_m) else None,
                IC_OOS=round(oos_m.mean(), 4) if len(oos_m) else None)

print("=== COVERAGE ===")
cov = df.groupby(df.time.dt.year).apply(
    lambda g: pd.Series({
        "n_obs": len(g), "n_tk": g.ticker.nunique(),
        "pct_any_evt": round((g.nevt_180 > 0).mean(), 3),
        "pct_netbuy": round((g.S1_netpers_180 > 0).mean(), 3),
        "pct_netsell": round((g.S1_netpers_180 < 0).mean(), 3)}), include_groups=False)
print(cov.to_string())

rows = []
for h in ["fwd20", "fwd60"]:
    for k in SIG:
        rows.append({**summarise(ic_series(k, h), k), "h": h, "ctrl": "raw"})
        rows.append({**summarise(ic_series(k, h, controls=("ey",)), k), "h": h, "ctrl": "ey"})
        rows.append({**summarise(ic_series(k, h, controls=("ey", "rating8l")), k), "h": h, "ctrl": "ey+rat8l"})
res = pd.DataFrame(rows)[["h", "ctrl", "sig", "n_months", "avg_n", "IC", "t", "hit", "IC_IS", "IC_OOS"]]
print("\n=== IC PANEL (Spearman, monthly cross-section, universe_pit) ===")
print(res.sort_values(["h", "ctrl", "sig"]).to_string(index=False))
res.to_csv(f"{D}/ic_results.csv", index=False)

print("\n=== SPREAD fwd20 theo nhom (demeaned trong thang) ===")
d2 = df.dropna(subset=["fwd20"]).copy()
d2["xs"] = d2.fwd20 - d2.groupby("time").fwd20.transform("mean")
grp = pd.cut(d2.S1_netpers_180, [-99, -0.5, 0.5, 1.5, 99],
             labels=["net_sell", "no_signal/flat", "net_buy_1", "net_buy_2+"])
print(d2.groupby(grp, observed=True).agg(n=("xs", "size"), mean_xs=("xs", "mean"),
                                         t=("xs", lambda x: x.mean()/x.std(ddof=1)*np.sqrt(len(x)))).round(5).to_string())
