"""Vong 2 — job Taylor_20260729_015830.
(a) khu ESOP-bulk co cuu duoc phia MUA khong?  (b) phia BAN co dung lam GATE due-diligence khong?
N trials vong 2 khai bao truoc = 4 (S2_nb, sell_intensity, buy_nb, gate binary) tren fwd20 + fwd60.
"""
import numpy as np, pandas as pd
from scipy import stats

D = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_insider"
df = pd.read_csv(f"{D}/panel2.csv", parse_dates=["time"])
df = df[df.fwd20.notna()].copy()
df["ey"] = np.where(df.PE > 0, 1.0 / df.PE, np.nan)
df["S2_netpers_90"]    = df.nbuy_90 - df.nsell_90
df["S7_netpers_90_nb"] = df.nbuy_90_nb - df.nsell_90_nb          # khu ESOP-bulk
df["S8_sell_int"]      = -np.where(df.oshares > 0, df.sell_sh_90 / df.oshares, np.nan)  # cang ban nhieu cang am
df["S9_buy_nb"]        = np.where(df.oshares > 0, df.buy_sh_90_nb / df.oshares, np.nan)

def resid(y, X):
    X = np.column_stack([np.ones(len(y))] + [X[:, j] for j in range(X.shape[1])])
    b, *_ = np.linalg.lstsq(X, y, rcond=None); return y - X @ b

def ic(col, ret, ctrl=()):
    out = []
    for d, g in df.groupby("time"):
        g = g.dropna(subset=[col, ret, *ctrl])
        if len(g) < 30 or g[col].nunique() < 2: continue
        s = stats.rankdata(g[col]); r = stats.rankdata(g[ret])
        if ctrl:
            C = np.column_stack([stats.rankdata(g[c]) for c in ctrl])
            s = resid(s, C); r = resid(r, C)
            if np.std(s) < 1e-9: continue
        out.append((d, np.corrcoef(s, r)[0, 1]))
    s = pd.DataFrame(out, columns=["time", "ic"]).set_index("time").ic
    t = s.mean()/s.std(ddof=1)*np.sqrt(len(s))
    return dict(sig=col, h=ret, ctrl="+".join(ctrl) or "raw", n=len(s), IC=round(s.mean(),4),
                t=round(t,2), IS=round(s[s.index<"2020-01-01"].mean(),4),
                OOS=round(s[s.index>="2020-01-01"].mean(),4))

rows=[]
for c in ["S2_netpers_90","S7_netpers_90_nb","S8_sell_int","S9_buy_nb"]:
    for h in ["fwd20","fwd60"]:
        rows.append(ic(c,h)); rows.append(ic(c,h,("ey","rating8l")))
print("=== IC vong 2 ===")
print(pd.DataFrame(rows).to_string(index=False))

print("\n=== (a) KHU ESOP: spread fwd20 demeaned, phia MUA ===")
d = df.copy(); d["xs20"] = d.fwd20 - d.groupby("time").fwd20.transform("mean")
d["xs60"] = d.fwd60 - d.groupby("time").fwd60.transform("mean")
for lbl, col in [("raw (co ESOP)","nbuy_90"), ("da khu ESOP-bulk","nbuy_90_nb")]:
    g = d[(d.nsell_90 == 0)]
    b = g[g[col] > 0]; n = g[g[col] == 0]
    print(f"{lbl:20s} mua-thuan n={len(b):5d} xs20={b.xs20.mean():+.5f}  vs khong-tin-hieu n={len(n):5d} xs20={n.xs20.mean():+.5f}")

print("\n=== (b) GATE: ban rong 90d truoc, tren TOAN universe ===")
d["gate_sell"] = (d.nsell_90 > d.nbuy_90)
for h in ["xs20","xs60"]:
    a = d[d.gate_sell][h].dropna(); b = d[~d.gate_sell][h].dropna()
    tt = stats.ttest_ind(a, b, equal_var=False)
    print(f"{h}: co ban rong n={len(a)} mean={a.mean():+.5f} | khong n={len(b)} mean={b.mean():+.5f} | "
          f"delta={a.mean()-b.mean():+.5f} t={tt.statistic:.2f}")

print("\n=== (b2) GATE trong RO UNG VIEN MUA (rating8l<=3 & ey top-tercile trong thang) ===")
d["ey_rk"] = d.groupby("time").ey.rank(pct=True)
cand = d[(d.rating8l <= 3) & (d.ey_rk >= 2/3)].copy()
for h in ["xs20","xs60"]:
    a = cand[cand.gate_sell][h].dropna(); b = cand[~cand.gate_sell][h].dropna()
    tt = stats.ttest_ind(a, b, equal_var=False)
    print(f"{h}: co ban rong n={len(a)} mean={a.mean():+.5f} | khong n={len(b)} mean={b.mean():+.5f} | "
          f"delta={a.mean()-b.mean():+.5f} t={tt.statistic:.2f}")

print("\n=== (b3) TAIL RISK — P(fwd60 < -20%) ===")
for name, sub in [("toan universe", d), ("ro ung vien", cand)]:
    x = sub.dropna(subset=["fwd60"])
    a = x[x.gate_sell]; b = x[~x.gate_sell]
    pa = (a.fwd60 < -0.20).mean(); pb = (b.fwd60 < -0.20).mean()
    # z-test 2 ty le
    p = ((a.fwd60 < -0.20).sum() + (b.fwd60 < -0.20).sum()) / (len(a)+len(b))
    z = (pa-pb)/np.sqrt(p*(1-p)*(1/len(a)+1/len(b)))
    print(f"{name:15s} co ban rong n={len(a):5d} P={pa:.4f} | khong n={len(b):5d} P={pb:.4f} | "
          f"lift={pa/pb:.3f}x z={z:.2f}")

print("\n=== (b4) FALSE-POSITIVE: bao nhieu % ro ung vien bi co ban rong bat ===")
print(f"toan universe: {d.gate_sell.mean():.3f} | ro ung vien: {cand.gate_sell.mean():.3f}")
print(f"so quan sat ro ung vien/thang (trung binh): {cand.groupby('time').size().mean():.1f}")

print("\n=== (c) KIEM CHUNG CONFOUND: tail-lift co phai chi la proxy cua size/vol khong? ===")
d["mcap"] = d.Close * d.oshares
d["turn"] = d.Volume_1M / d.oshares          # proxy thanh khoan/vol
x = d.dropna(subset=["fwd60","mcap","turn"]).copy()
x["bad"] = (x.fwd60 < -0.20)
for key, lab in [("mcap","von hoa"), ("turn","turnover")]:
    x[key+"_q"] = x.groupby("time")[key].transform(lambda s: pd.qcut(s.rank(method="first"), 4, labels=[1,2,3,4]))
    print(f"\n-- phan tang theo {lab} (Q1 thap -> Q4 cao) --")
    for q in [1,2,3,4]:
        s = x[x[key+"_q"] == q]
        a, b = s[s.gate_sell], s[~s.gate_sell]
        if len(a) < 100 or len(b) < 100: continue
        pa, pb = a.bad.mean(), b.bad.mean()
        p = (a.bad.sum()+b.bad.sum())/(len(a)+len(b))
        z = (pa-pb)/np.sqrt(p*(1-p)*(1/len(a)+1/len(b)))
        print(f"  Q{q}: co-ban n={len(a):5d} P={pa:.4f} | khong n={len(b):5d} P={pb:.4f} | lift={pa/pb:.3f}x z={z:.2f}")

print("\n-- on dinh IS(2015-19) vs OOS(2020+) cua tail-lift --")
for lab, sub in [("toan universe", x), ("ro ung vien", x[(x.rating8l<=3)&(x.ey_rk>=2/3)])]:
    for per, m in [("IS", sub.time < "2020-01-01"), ("OOS", sub.time >= "2020-01-01")]:
        s = sub[m]; a, b = s[s.gate_sell], s[~s.gate_sell]
        if len(a) < 50: continue
        pa, pb = a.bad.mean(), b.bad.mean()
        p = (a.bad.sum()+b.bad.sum())/(len(a)+len(b))
        z = (pa-pb)/np.sqrt(p*(1-p)*(1/len(a)+1/len(b)))
        print(f"  {lab:14s} {per:3s}: n_flag={len(a):5d} P={pa:.4f} vs {pb:.4f} lift={pa/pb:.3f}x z={z:.2f}")

print("\n-- nguong khac cho 'ban manh' (chat hon = it false-positive hon?) --")
for lab, mask in [("nsell>nbuy (goc)", x.gate_sell),
                  ("nsell>=2 & nsell>nbuy", (x.nsell_90 >= 2) & x.gate_sell),
                  ("ban >=0,5% CP luu hanh", (x.sell_sh_90/x.oshares >= 0.005) & x.gate_sell),
                  ("ban >=1% CP luu hanh", (x.sell_sh_90/x.oshares >= 0.01) & x.gate_sell)]:
    a = x[mask.fillna(False)]; b = x[~mask.fillna(False)]
    pa, pb = a.bad.mean(), b.bad.mean()
    p = (a.bad.sum()+b.bad.sum())/(len(a)+len(b))
    z = (pa-pb)/np.sqrt(p*(1-p)*(1/len(a)+1/len(b)))
    print(f"  {lab:24s}: n_flag={len(a):5d} ({len(a)/len(x)*100:4.1f}%) P={pa:.4f} vs {pb:.4f} lift={pa/pb:.3f}x z={z:.2f}")
