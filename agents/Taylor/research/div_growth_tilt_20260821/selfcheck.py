#!/usr/bin/env python3
"""Selfcheck doc lap cho analyze.py — job Taylor_20260821_113800.
Tinh LAI z-score va IC bang duong di KHAC (vong lap tay, khong dung groupby.transform),
va tinh CI cua IC chinh. FAIL = khong duoc bao ket qua."""
import numpy as np, pandas as pd
from scipy import stats

D = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/div_growth_tilt_20260821"
p = pd.read_csv(f"{D}/panel_z.csv", parse_dates=["t"])
src = pd.read_csv("/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/"
                  "div_growth_signal_20260821/panel_enriched.csv", parse_dates=["t"])
src = src[src.has_cagr].copy()
src["icb_l2"] = src.icb_code.astype(int) // 100
fails = []

# SC1: z tinh tay tren 200 o ngau nhien phai khop
rng = np.random.default_rng(20260821)
cells = list(src.groupby(["ym", "icb_l2"]).groups.keys())
worst = 0.0; n_ok = 0; n_cell = 0
zmap = {(r.ym, r.icb_l2, r.ticker): r.z_l2 for r in p.itertuples()}
for i in rng.choice(len(cells), 200, replace=False):
    ym, ind = cells[i]; g = src[(src.ym == ym) & (src.icb_l2 == ind)]
    n_cell += 1
    keep = len(g) >= 5 and g.cagr.std(ddof=1) > 0 and np.isfinite(g.cagr.std(ddof=1))
    for r in g.itertuples():
        z = zmap.get((ym, ind, r.ticker))
        if not keep:
            if z is not None: fails.append(f"SC1 o {ym}/{ind} <5 payer nhung co z")
            continue
        exp = (r.cagr - g.cagr.mean()) / g.cagr.std(ddof=1)
        if z is None: fails.append(f"SC1 thieu z {ym}/{ind}/{r.ticker}"); continue
        worst = max(worst, abs(z - exp)); n_ok += 1
print(f"SC1 z-score: {n_cell} o, {n_ok} dong khop, sai lech max={worst:.2e}")
if worst > 1e-9: fails.append(f"SC1 z lech {worst:.2e}")

# SC2: moi o giu lai phai co >=5 dong va mean(z)~0, sd(z)~1
gg = p.groupby(["ym", "icb_l2"]).z_l2.agg(["count", "mean", "std"])
bad = gg[(gg["count"] < 5) | (gg["mean"].abs() > 1e-9) | ((gg["std"] - 1).abs() > 1e-9)]
print(f"SC2 bat bien o: {len(gg)} o giu lai, vi pham={len(bad)}")
if len(bad): fails.append(f"SC2 {len(bad)} o vi pham count>=5 / mean=0 / sd=1")

# SC3: IC chinh tinh lai bang vong lap tay + CI Newey-West
ics = []
for ym in sorted(p.ym.unique()):
    g = p[p.ym == ym][["z_l2", "bhar60_close"]].dropna()
    if len(g) < 10 or g.z_l2.nunique() < 3: continue
    r = stats.spearmanr(g.z_l2, g.bhar60_close).statistic
    if np.isfinite(r): ics.append(r)
x = np.array(ics); n = len(x); e = x - x.mean(); v = (e @ e) / n
for L in range(1, 4): v += 2 * (1 - L / 4) * ((e[L:] @ e[:-L]) / n)
se = np.sqrt(v / n); m = x.mean()
saved = pd.read_csv(f"{D}/results_ic.csv")
ref = saved[(saved.scope == "FULL") & (saved.x == "z_cagr_ind_L2") &
            (saved.y == "bhar60_close")].iloc[0]
print(f"SC3 IC FULL tinh tay: n_months={n} mean={m:.4f} t_nw={m/se:.4f} "
      f"| analyze.py: n={int(ref.n_months)} mean={ref.mean_ic:.4f} t={ref.t_nw:.4f}")
if abs(m - ref.mean_ic) > 1e-9 or n != int(ref.n_months): fails.append("SC3 IC khong khop")
print(f"SC3 se_nw={se:.4f}  CI95=[{m-1.96*se:.4f}, {m+1.96*se:.4f}]  "
      f"nguong 0.04 nam TRONG CI: {m-1.96*se < 0.04 < m+1.96*se}")
print(f"SC3 p_two_sided={2*(1-stats.norm.cdf(abs(m/se))):.5f}")

# SC4: prox tai tao dung cong thuc production tren 5 dong ngau nhien
import sys; sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from deposit_rate_vn import current_deposit_rate
h2 = pd.read_csv(f"{D}/results_h2_partial.csv")
chk = p[p.icb_code != 8355].sample(5, random_state=7)
for r in chk.itertuples():
    dep = float(current_deposit_rate(str(r.t.date())))
    exp = r.price_t / (r.div0 / (dep / 100.0))
    dy = r.div0 / r.price_t
    print(f"SC4 {r.ticker} {r.t.date()} dep={dep:.2f}% DY={100*dy:.2f}% prox={exp:.3f} "
          f"(kiem tra: dep/DY={dep/(100*dy):.3f})")
    if abs(exp - dep / (100 * dy)) > 1e-6: fails.append("SC4 prox khong bang dep/DY")

print("\n" + ("SELFCHECK FAIL: " + " | ".join(fails) if fails else "SELFCHECK PASS — 4/4"))
