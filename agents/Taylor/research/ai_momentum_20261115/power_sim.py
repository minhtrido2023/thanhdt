"""P0 power/MDE: mo phong tren phan phoi ex20/ex60 THAT cua su kien R4 (events.csv), giu cum thang.
Test = chenh trung binh (winsor 1/99) nhom A (pipeline gan nhan, vd CONT/EARNINGS) - nhom B; p-value bang
hoan vi KHOI THANG (giu nguyen chuoi nhan cua tung thang, doi thu tu thang). alpha = 0.05/3 mot phia
(nguong BH buoc 1 cho 3 phep thu, cau hinh xau nhat). seed co dinh, threads=1."""
import os; os.environ["OMP_NUM_THREADS"] = "1"
import sys, numpy as np, pandas as pd
D = sys.argv[1]; rng = np.random.default_rng(20261115)
ev = pd.read_csv(f"{D}/events.csv", parse_dates=["time"]); ev = ev[ev.variant == "R4"].sort_values("time")
ev["ym"] = ev.time.dt.strftime("%Y-%m")
ALPHA = 0.05 / 3; NPERM = 400; NSIM = 200

def icc(x, g):
    df = pd.DataFrame({"x": x, "g": g}).dropna(); k = df.groupby("g").x
    n0 = (len(df) - (k.size() ** 2).sum() / len(df)) / (k.ngroups - 1)
    msb = (k.size() * (k.mean() - df.x.mean()) ** 2).sum() / (k.ngroups - 1)
    msw = ((df.x - k.transform("mean")) ** 2).sum() / (len(df) - k.ngroups)
    return (msb - msw) / (msb + (n0 - 1) * msw)

def block_perm_p(y, lab, months, nperm):
    obs = y[lab].mean() - y[~lab].mean()
    um = pd.unique(months); blocks = [lab[months == m] for m in um]
    cnt = 0
    for _ in range(nperm):
        perm = np.concatenate([blocks[i] for i in rng.permutation(len(blocks))])
        cnt += (y[perm].mean() - y[~perm].mean()) >= obs
    return (cnt + 1) / (nperm + 1)

for col in ["ex20", "ex60"]:
    e = ev.dropna(subset=[col]); y0 = e[col].clip(e[col].quantile(.01), e[col].quantile(.99)).to_numpy()
    print(f"== {col}: N_hist={len(e)} sd_winsor={y0.std():.4f} ICC_thang={icc(e[col], e.ym):.3f} "
          f"mean_size_thang={e.groupby('ym').size().mean():.1f}")
    for N in [40, 80, 150, 250]:
        row = []
        for delta in [0.03, 0.05, 0.08, 0.12, 0.20]:
            hits = 0
            for s in range(NSIM):
                # lay N su kien lien tiep theo thoi gian (giu cum thang that), vong tron
                st = rng.integers(len(e)); idx = (np.arange(N) + st) % len(e)
                y = y0[idx].copy(); m = e.ym.to_numpy()[idx]
                # nhan cum theo thang: xac suat A cua thang ~ Beta (cung mot che do), p trung binh 0.5
                pm = {mm: rng.beta(2, 2) for mm in pd.unique(m)}
                lab = rng.random(N) < np.array([pm[mm] for mm in m])
                if lab.sum() < 5 or (~lab).sum() < 5: continue
                y[lab] += delta
                hits += block_perm_p(y, lab, m, NPERM) <= ALPHA
            row.append(f"d={delta:.2f}:{hits/NSIM:.2f}")
        print(f"  N={N:4d} power " + " ".join(row))
# nhi phan: hit-rate view co huong vs B0 (CONT moi su kien); MDE xap xi chuan, deff tu ICC chi bao
from statistics import NormalDist; _n = NormalDist()
for N in [40, 80, 150, 250]:
    za, zb = _n.inv_cdf(1 - ALPHA), _n.inv_cdf(.8)
    print(f"  binary N={N}: MDE hit-rate ~ +{(za+zb)*np.sqrt(.25/N)*100:.1f}pp (truoc deff)")
# toc do su kien: 6 thang day du gan nhat
m = ev.groupby("ym").size(); last6 = m.loc["2026-05":"2026-10"]
print("R4 6 thang gan (05-10/2026):", last6.to_dict(), "TB", round(last6.mean(), 2), "| TB toan ky", round(m.mean(), 2))
