"""Viec 1 — DSR + PBO(CSCV) tren ho N=10 leg CAPIT sizing (job Taylor_20260731_111654).

Doc DAILY combined_nav tu 10 audit CSV da co (KHONG chay lai backtest).
DSR: Bailey & Lopez de Prado (2014). PBO: CSCV, S=16 subset.
"""
import glob, itertools, os, sys
import numpy as np
import pandas as pd
from scipy.stats import norm, skew, kurtosis

D = "/home/trido/thanhdt/WorkingClaude/data"
LEGS = [
    ("capsz_ctrl", "cash", ""),
    ("capsz_idle", "idle", "szbidle"),
    ("capsz_booknav", "booknav", "szbbooknav"),
    ("capsz_nav10", "nav:0.10", "szbnav010"),
    ("capsz_nav20", "nav:0.20", "szbnav020"),
    ("capsz_idlecap30", "idlecap:0.30", "szbidlecap030"),
    ("capsz_park25", "park:0.25", "szbpark025"),
    ("capsz_park50", "park:0.50", "szbpark050"),
    ("capsz_navsize25", "navsize:0.25", "szbnavsize025"),
    ("capsz_navsize40", "navsize:0.40", "szbnavsize040"),
    # legs bo sung job nay (Viec 3) — chi tinh neu file da ton tai
    ("capsz_navsize15", "navsize:0.15", "szbnavsize015"),
    ("capsz_navsize30", "navsize:0.30", "szbnavsize030"),
    ("capsz_navsize35", "navsize:0.35", "szbnavsize035"),
]


def load_nav(tag):
    pat = os.path.join(D, f"v23_golive_audit_2014_now_*_exp_{tag}_univpit.csv")
    f = glob.glob(pat)
    if not f:
        return None
    df = pd.read_csv(f[0], low_memory=False)
    d = df[df.record_type == "DAILY"][["ymd", "combined_nav"]].copy()
    d["combined_nav"] = pd.to_numeric(d.combined_nav)
    d = d.sort_values("ymd").reset_index(drop=True)
    return d.set_index("ymd")["combined_nav"]


navs = {}
for tag, base, _ in LEGS:
    s = load_nav(tag)
    if s is not None:
        navs[base] = s
print(f"legs loaded: {len(navs)} -> {list(navs)}")

idx = None
for s in navs.values():
    idx = s.index if idx is None else idx.intersection(s.index)
R = pd.DataFrame({k: np.log(v.reindex(idx)).diff() for k, v in navs.items()}).dropna()
# dung simple return cho Sharpe (khop quy uoc engine); log-ret chi de dedup index
R = pd.DataFrame({k: navs[k].reindex(idx).pct_change() for k in navs}).dropna()
T, N = R.shape
print(f"T={T} phien, N={N} trial")

# ---------- Sharpe per leg (daily + annualized 252) ----------
sr_d = R.mean() / R.std(ddof=1)
sr_a = sr_d * np.sqrt(252)
print("\nSharpe(252) moi leg:")
for k in R.columns:
    print(f"  {k:16s} {sr_a[k]:.4f}")

# ---------- DSR ----------
# SR0 = expected max Sharpe under null (all trials have true SR=0), Bailey et al.
GAMMA = 0.5772156649
var_sr = sr_d.var(ddof=1)          # variance of the trial Sharpes (daily units)
sr0 = np.sqrt(var_sr) * ((1 - GAMMA) * norm.ppf(1 - 1.0 / N)
                         + GAMMA * norm.ppf(1 - 1.0 / (N * np.e)))
print(f"\nVar(SR_trials) daily = {var_sr:.3e}; SR0(daily) = {sr0:.5f}"
      f"  (annualized {sr0*np.sqrt(252):.4f})")

print("\nDSR moi leg (SR0 chung cua ho N=%d):" % N)
dsr = {}
for k in R.columns:
    r = R[k].values
    g3 = skew(r, bias=False)
    g4 = kurtosis(r, fisher=False, bias=False)
    s = sr_d[k]
    denom = np.sqrt(1 - g3 * s + (g4 - 1) / 4.0 * s ** 2)
    z = (s - sr0) * np.sqrt(T - 1) / denom
    dsr[k] = norm.cdf(z)
    print(f"  {k:16s} SR_d={s:.5f} skew={g3:+.3f} kurt={g4:6.2f} z={z:7.3f} DSR={dsr[k]:.4f}")

# ---------- PBO (CSCV) ----------
S = 16
n = T // S
blocks = [R.iloc[i * n:(i + 1) * n] for i in range(S)]
combos = list(itertools.combinations(range(S), S // 2))
print(f"\nCSCV: S={S}, block={n} phien, so combo={len(combos)}")

logits, ranks = [], []
for c in combos:
    isb = [blocks[i] for i in c]
    oob = [blocks[i] for i in range(S) if i not in c]
    Ris = pd.concat(isb)
    Ros = pd.concat(oob)
    sr_is = Ris.mean() / Ris.std(ddof=1)
    sr_os = Ros.mean() / Ros.std(ddof=1)
    best = sr_is.idxmax()
    # rank OOS cua config tot nhat IS: 1 = te nhat ... N = tot nhat
    rk = sr_os.rank().loc[best]
    w = rk / (N + 1.0)
    ranks.append(rk)
    logits.append(np.log(w / (1 - w)))

logits = np.array(logits)
pbo = float((logits <= 0).mean())
print(f"PBO = {pbo:.4f}   (median OOS-rank cua IS-best = {np.median(ranks):.1f}/{N})")
print(f"logit mean={logits.mean():+.4f}")

# tan suat leg nao thang IS
from collections import Counter
wins = Counter()
for c in combos:
    Ris = pd.concat([blocks[i] for i in c])
    wins[(Ris.mean() / Ris.std(ddof=1)).idxmax()] += 1
print("\nTan suat thang IS (CSCV):")
for k, v in wins.most_common():
    print(f"  {k:16s} {v:5d}/{len(combos)}  ({100*v/len(combos):.1f}%)")

# ---------- correlation cua ho (de dien giai PBO) ----------
print(f"\nTuong quan daily-return giua cac leg: min={R.corr().values[np.triu_indices(N,1)].min():.6f}"
      f"  median={np.median(R.corr().values[np.triu_indices(N,1)]):.6f}")
nd = (R.sub(R["cash"], axis=0).abs() > 1e-12).sum()
print("So phien khac baseline `cash`:")
for k in R.columns:
    print(f"  {k:16s} {nd[k]:5d}/{T} phien ({100*nd[k]/T:.1f}%)")
