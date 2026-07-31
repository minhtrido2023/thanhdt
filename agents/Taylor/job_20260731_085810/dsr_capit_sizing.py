"""DSR + PBO cho họ 6 leg CAPIT sizing-base (job Taylor_20260731_085810).

Đọc 6 NAV CSV đã chạy, tính Sharpe + Deflated Sharpe Ratio (Bailey & López de Prado 2014)
và PBO/CSCV (Bailey et al 2017) trên chính họ 6 cấu hình này. Tái sử dụng NGUYÊN hàm của
dsr_pbo_annex.py (không viết lại công thức) để không lệch quy ước với số đã pin trong
data/results_registry.md.
"""
import glob, sys, math
import numpy as np, pandas as pd
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
import dsr_pbo_annex as A

LEGS = [
    ("ctrl (cash = spec pinned)", "*capsz_ctrl*.csv"),
    ("idle (cash+park)",          "*capsz_idle_*.csv"),
    ("booknav (LIVE)",            "*capsz_booknav*.csv"),
    ("nav:0.10",                  "*capsz_nav10*.csv"),
    ("nav:0.20",                  "*capsz_nav20*.csv"),
    ("idlecap:0.30",              "*capsz_idlecap30*.csv"),
]

series = {}
for name, pat in LEGS:
    f = sorted(glob.glob("/home/trido/thanhdt/WorkingClaude/data/" + pat))
    if not f:
        print(f"  [THIEU] {name} ({pat})")
        continue
    s = A.load_nav(f[0])
    if s is None:
        print(f"  [LOI doc NAV] {name}")
        continue
    series[name] = s

rets = {k: A.daily_logret(v) for k, v in series.items()}
N = len(rets)
print(f"\nN_trials (so cau hinh thuc su da so sanh trong ho nay) = {N}")
print(f"T (so phien) = {len(next(iter(rets.values())))}\n")

# Sharpe per-observation cua TOAN ho -> var(SR) dung cho SR_0 (ky vong max duoi null)
srs = {k: A.moments(r)[0] for k, r in rets.items()}
var_sr = float(np.var(np.array(list(srs.values())), ddof=1))
sr0 = A.expected_max_sr(var_sr, N)
print(f"var(SR per-obs) qua {N} leg = {var_sr:.3e}  ->  SR_0 (ky vong max duoi null) = {sr0:.5f}"
      f"  (annualized {sr0*math.sqrt(252):.3f})\n")

print(f"{'leg':<28}{'Sharpe(ann)':>12}{'skew':>8}{'kurt':>8}{'DSR':>9}")
for k, r in rets.items():
    sr, g3, g4 = A.moments(r)
    d, stat = A.dsr(sr, sr0, g3, g4, len(r))
    print(f"{k:<28}{sr*math.sqrt(252):>12.3f}{g3:>8.2f}{g4:>8.2f}{d:>9.4f}")

# PBO / CSCV tren ma tran loi suat ngay cua ca ho
idx = sorted(set.intersection(*[set(s.index) for s in series.values()]))
M = pd.DataFrame({k: np.log(series[k].reindex(idx)).diff() for k in series}).dropna()
pbo, logits, ncombo, ncfg, T2 = A.cscv_pbo(M.values, S=16)
print(f"\nPBO (CSCV, S=16, ho {ncfg} cau hinh, {ncombo} to hop, T={T2}) = {pbo:.4f}")
print(f"  logit trung vi = {np.median(logits):.3f} (>0 = IS-best van tren trung vi OOS)")
