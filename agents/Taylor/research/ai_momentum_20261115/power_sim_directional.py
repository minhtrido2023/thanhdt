"""P1 task1: power sim lai voi ty le view CO HUONG (CONT/REV) p_dir ~40% (M1 dry-run: NO_VIEW 5/10 @20s, 10/10 @60s).
Khac power_sim.py (P0): N_scored chi dem su kien co view co huong; thoi gian toi N = N / (nhip su kien * p_dir).
T1 (view_20s=CONT vs {REV,NO_VIEW}) dung N_scored(directional) cho nhom A; test dung toan bo su kien da cham nhung
nhom A chi ~ p_dir*P(CONT|dir). Mo hinh: moi su kien co view co huong voi xs p_dir; trong do CONT voi xs 0.5.
Nhom A = {CONT}; nhom B = con lai. ex20 cong delta cho nhom A. P hoan vi KHOI THANG, alpha=0.05/3 mot phia.
Dem N_scored = so su kien CO VIEW CO HUONG (dinh nghia N dung cho look L1/L2 sau khi sua)."""
import os; os.environ["OMP_NUM_THREADS"] = "1"
import sys, numpy as np, pandas as pd
D = sys.argv[1]; rng = np.random.default_rng(20261115)
ev = pd.read_csv(f"{D}/events.csv", parse_dates=["time"]); ev = ev[ev.variant == "R4"].sort_values("time")
ev["ym"] = ev.time.dt.strftime("%Y-%m")
ALPHA = 0.05/3; NPERM = 300; NSIM = 150
def bpp(y, lab, months):
    obs = y[lab].mean() - y[~lab].mean(); um = pd.unique(months); blocks = [lab[months == m] for m in um]; c = 0
    for _ in range(NPERM):
        perm = np.concatenate([blocks[i] for i in rng.permutation(len(blocks))]); c += (y[perm].mean()-y[~perm].mean()) >= obs
    return (c+1)/(NPERM+1)
def power(col, Ndir, p_dir, delta):
    e = ev.dropna(subset=[col]); y0 = e[col].clip(e[col].quantile(.01), e[col].quantile(.99)).to_numpy(); months = e.ym.to_numpy()
    Ntot = int(round(Ndir / p_dir)); h = 0; n = 0
    for _ in range(NSIM):
        st = rng.integers(len(e)); idx = (np.arange(Ntot)+st) % len(e); y = y0[idx].copy(); m = months[idx]
        pm = {mm: rng.beta(2, 2) for mm in pd.unique(m)}      # che do thang: xs co view ~Beta tam 0.5 -> nhan cum
        has = rng.random(Ntot) < np.clip(np.array([pm[mm] for mm in m])*2*p_dir, 0, 1)  # ky vong ~ p_dir
        cont = has & (rng.random(Ntot) < 0.5)
        if cont.sum() < 5 or (~cont).sum() < 5: continue
        y[cont] += delta; n += 1; h += bpp(y, cont, m) <= ALPHA
    return h/max(n, 1), Ntot
p_dir_list = [0.4, 0.6, 1.0]
print("ex20 T1 (CONT vs rest), delta=8pp / 12pp ; N = SO SU KIEN CO VIEW CO HUONG; Ntot = su kien can xu ly")
for p in p_dir_list:
    for Nd in [40, 80, 150]:
        a, nt = power("ex20", Nd, p, .08); b, _ = power("ex20", Nd, p, .12)
        print(f"  p_dir={p:.1f} N_dir={Nd:4d} Ntot={nt:4d}  power d8={a:.2f} d12={b:.2f}")
# thoi gian
rate_all = {"TB toan ky 13.1/thang": 13.1, "6 thang gan 6.3/thang": 6.3}
print("thang de toi N_dir (= N_dir / (rate*p_dir)); cong 3 thang cho ex60; hang doi toi da 10/tuan ~43/thang khong chan:")
for nm, r in rate_all.items():
    for p in p_dir_list:
        print(f"  {nm} p_dir={p:.1f}: " + " ".join(f"N{N}={N/(r*p):.1f}m" for N in [80, 150, 250]))
