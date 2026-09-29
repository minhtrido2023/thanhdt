"""Insider CLUSTER BUY scoping (job Taylor_20260830_054316) — dao dau gate ban rong da co.
Tai dung panel PIT da dung cho gate ban (Taylor_20260729_015830, exp_insider/panel2.csv/.sql) —
cung nguon tav2_bq.insider_transaction, cung cua so 90d/180d, cung univ=universe_pit, chi doi
huong dieu kien (mua thay vi ban). KHONG chay BQ moi — panel da co san cot mua (nbuy_90,
nbuy_90_nb, buy_sh_90_nb, oshares) tu panel2.sql goc.

N trials khai bao TRUOC khi nhin ket qua = 4 dinh nghia cluster-buy (A/B/C/D) x 2 horizon
(fwd20/fwd60) x 2 subset (toan universe / dd52<=-20%) = pre-register, khong p-hack sau khi thay so.
"""
import numpy as np, pandas as pd
from scipy import stats

D = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_insider"
df = pd.read_csv(f"{D}/panel2.csv", parse_dates=["time"])
df = df.sort_values(["ticker", "time"]).reset_index(drop=True)

# dd52 = trailing 12-thang (panel EOM hang thang -> ~12 diem) rolling max cua Close, tu chinh panel
df["roll12_max"] = df.groupby("ticker")["Close"].transform(
    lambda s: s.rolling(12, min_periods=6).max())
df["dd52"] = df["Close"] / df["roll12_max"] - 1

df["ey"] = np.where(df.PE > 0, 1.0 / df.PE, np.nan)
df["xs20"] = df.fwd20 - df.groupby("time").fwd20.transform("mean")
df["xs60"] = df.fwd60 - df.groupby("time").fwd60.transform("mean")

# --- 4 dinh nghia cluster-buy, pre-register ---
df["cbuy_A_net"]     = df.nbuy_90 > df.nsell_90                                    # doi xung gate_sell goc
df["cbuy_B_nb2"]      = df.nbuy_90_nb >= 2                                          # >=2 nguoi khac nhau (khu ESOP-bulk)
df["buy_pct_osh"]    = np.where(df.oshares > 0, df.buy_sh_90_nb / df.oshares, np.nan)
df["cbuy_C_pct05"]   = df.buy_pct_osh >= 0.005                                      # >=0,5% CP luu hanh (mirror nguong 0,5% cua sell)
df["cbuy_D_combo"]   = df["cbuy_B_nb2"] & (df.nbuy_90_nb > df.nsell_90_nb)          # cum + net-buy (khu ESOP)

DEFS = ["cbuy_A_net", "cbuy_B_nb2", "cbuy_C_pct05", "cbuy_D_combo"]

print("=== COVERAGE (toan mau, thang) ===")
for c in DEFS:
    n = df[c].sum()
    print(f"  {c:16s}: {n:6d}/{len(df)} ({n/len(df)*100:5.2f}%) — {df[df[c]].groupby('time').size().mean():.1f}/thang trung binh")

print("\n=== IC (rank-corr thang, ctrl ey+rating8l) ===")
def resid(y, X):
    X = np.column_stack([np.ones(len(y))] + [X[:, j] for j in range(X.shape[1])])
    b, *_ = np.linalg.lstsq(X, y, rcond=None); return y - X @ b

def ic(sig_mask_col, ret, ctrl=("ey","rating8l")):
    d = df.copy()
    d["sig"] = d[sig_mask_col].astype(float)
    out = []
    for t, g in d.groupby("time"):
        g = g.dropna(subset=["sig", ret, *ctrl])
        if len(g) < 30 or g["sig"].nunique() < 2: continue
        s = stats.rankdata(g["sig"]); r = stats.rankdata(g[ret])
        C = np.column_stack([stats.rankdata(g[c]) for c in ctrl])
        s = resid(s, C); r = resid(r, C)
        if np.std(s) < 1e-9: continue
        out.append((t, np.corrcoef(s, r)[0, 1]))
    s = pd.DataFrame(out, columns=["time", "ic"]).set_index("time").ic
    if len(s) == 0: return dict(sig=sig_mask_col, h=ret, n=0, IC=np.nan, t=np.nan, IS=np.nan, OOS=np.nan)
    tt = s.mean()/s.std(ddof=1)*np.sqrt(len(s))
    return dict(sig=sig_mask_col, h=ret, n=len(s), IC=round(s.mean(),4), t=round(tt,2),
                IS=round(s[s.index<"2020-01-01"].mean(),4), OOS=round(s[s.index>="2020-01-01"].mean(),4))

rows = []
for c in DEFS:
    for h in ["fwd20", "fwd60"]:
        rows.append(ic(c, h))
print(pd.DataFrame(rows).to_string(index=False))

print("\n=== SPREAD demeaned (co cluster-buy vs khong), toan universe ===")
for c in DEFS:
    for h in ["xs20", "xs60"]:
        a = df[df[c]][h].dropna(); b = df[~df[c].fillna(False)][h].dropna()
        if len(a) < 20: continue
        tt = stats.ttest_ind(a, b, equal_var=False)
        print(f"  {c:16s} {h}: co n={len(a):5d} mean={a.mean():+.5f} | khong n={len(b):6d} mean={b.mean():+.5f} | "
              f"delta={a.mean()-b.mean():+.5f} t={tt.statistic:.2f}")

print("\n=== SPREAD trong subset dd52<=-20% (dung mach fear-buy sleeve) ===")
sub = df[df.dd52 <= -0.20].copy()
print(f"  n quan sat trong subset dd52<=-20%: {len(sub)} ({len(sub)/len(df)*100:.2f}% toan mau)")
for c in DEFS:
    for h in ["xs20", "xs60"]:
        a = sub[sub[c]][h].dropna(); b = sub[~sub[c].fillna(False)][h].dropna()
        if len(a) < 10:
            print(f"  {c:16s} {h}: n qua nho ({len(a)}) de danh gia")
            continue
        tt = stats.ttest_ind(a, b, equal_var=False)
        print(f"  {c:16s} {h}: co n={len(a):5d} mean={a.mean():+.5f} | khong n={len(b):6d} mean={b.mean():+.5f} | "
              f"delta={a.mean()-b.mean():+.5f} t={tt.statistic:.2f}")

print("\n=== ON DINH IS/OOS cua spread (dinh nghia manh nhat se chon o buoc sau) ===")
for c in DEFS:
    for per, m in [("IS", df.time < "2020-01-01"), ("OOS", df.time >= "2020-01-01")]:
        s = df[m]; a, b = s[s[c]].xs60.dropna(), s[~s[c].fillna(False)].xs60.dropna()
        if len(a) < 20: continue
        print(f"  {c:16s} {per}: n={len(a):5d} mean={a.mean():+.5f} vs {b.mean():+.5f} delta={a.mean()-b.mean():+.5f}")

print("\n=== OVERLAP voi gate ban rong hien co (nsell_90>nbuy_90) ===")
df["gate_sell"] = df.nsell_90 > df.nbuy_90
for c in DEFS:
    both = (df[c] & df.gate_sell).sum()
    print(f"  {c:16s}: {both} dong VUA cluster-buy VUA gate-sell cu (trung {both/max(df[c].sum(),1)*100:.1f}% cua cluster-buy)")

print("\n=== COVERAGE THUC TE — so ticker-thang qua nguong D (manh nhat, cum+net), quy doi /quy ===")
d_flag = df[df.cbuy_D_combo]
per_q = d_flag.groupby(d_flag.time.dt.to_period("Q")).ticker.nunique()
print(f"  trung vi ma/quy: {per_q.median():.1f} | max: {per_q.max()} | min: {per_q.min()} | so quy co >=1 ca: {(per_q>0).sum()}/{len(per_q)}")
print(per_q.describe())
