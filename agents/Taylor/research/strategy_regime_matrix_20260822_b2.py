#!/usr/bin/env python
"""B2 — Breadth (%>MA200) thay Value Radar lam truc 2. Job Taylor_20260822_141143. PAPER-ONLY.

Nguon (da tra mike/kb/data_registry/index.md):
  - tav2_mike.universe_pit  CANONICAL (point-in-time; ticker_prune la TRAP cho code moi, cutover 07-22)
    JOIN tav2_bq.ticker (Close, MA200) -> breadth = %ma trong universe co Close > MA200.
  - panel_daily.csv (part 1, job _101400): r_bal/r_lag/r_comb/r_vni + state DT5G + zone radar.
Tercile breadth = phan vi cua breadth HOM NAY trong 252 phien TRUOC DO (rolling, PIT, khong nhin truoc).
KHONG dung cot profit_*.
"""
import os, sys
import numpy as np, pandas as pd

W = "/home/trido/thanhdt/WorkingClaude"; sys.path.insert(0, W)
OUT = os.path.join(W, "mike", "agents", "Taylor", "research", "strategy_regime_matrix_20260822")
SPY = 249.2785102175346
REG = ["CRISIS","BEAR","NEUTRAL","BULL","EXBULL"]

d = pd.read_csv(os.path.join(OUT, "panel_daily.csv"), parse_dates=["time"])
d["yr"] = d.time.dt.year
br = pd.read_csv(os.path.join(OUT, "b2_breadth.csv"), parse_dates=["time"])
print(f"[data] breadth {br.time.min().date()}..{br.time.max().date()} n={len(br)} "
      f"| n_univ median {br.n_univ.median():.0f} min {br.n_univ.min()} max {br.n_univ.max()}")

# --- tercile PIT: phan vi cua hom nay trong 252 phien TRUOC (khong gom hom nay -> khong nhin truoc)
br = br.sort_values("time").reset_index(drop=True)
b = br.breadth.to_numpy()
pct = np.full(len(b), np.nan)
for i in range(252, len(b)):
    win = b[i-252:i]                      # 252 phien TRUOC, khong gom i
    pct[i] = (win < b[i]).mean()
br["pct252"] = pct
br["btile"] = pd.cut(br.pct252, [-0.001, 1/3, 2/3, 1.001], labels=["LOW","MID","HIGH"])
print(f"[tercile] NaN (warm-up) = {int(br.pct252.isna().sum())} phien; phan bo = "
      f"{dict(br.btile.value_counts())}")

d = d.merge(br[["time","breadth","pct252","btile"]], on="time", how="left")
d["btile"] = d.btile.astype(object)
print(f"[selfcheck] panel {len(d)} phien | thieu breadth {int(d.breadth.isna().sum())} "
      f"| thieu btile {int(d.btile.isna().sum())}")
# selfcheck khong-nhin-truoc: pct252 chi dung du lieu <= t-1 => tuong quan voi r_vni CUNG NGAY phai ~0
cc = d[["pct252","r_vni"]].dropna()
print(f"[selfcheck no-lookahead] corr(pct252_t, r_vni_t) = {cc.pct252.corr(cc.r_vni):+.4f} "
      f"(gan 0 = tercile khong chua thong tin cua chinh phien do)")

# ---------------------------------------------------------------- ham thong ke (giong part1/part2)
def blocks(flags):
    f = np.asarray(flags, bool)
    return int((f & (~np.r_[False, f[:-1]])).sum())

def stat(sub, col, ref="r_vni"):
    r = sub[col].dropna(); n = len(r)
    if n < 20: return dict(n=n, cagr=np.nan, sharpe=np.nan, dd=np.nan, excess=np.nan)
    cagr = float((1+r).prod()) ** (SPY/n) - 1
    vol = float(r.std(ddof=1))*np.sqrt(SPY)
    sh = (float(r.mean())*SPY)/vol if vol > 0 else np.nan
    eq = (1+r).cumprod(); dd = float((eq/eq.cummax()-1).min())
    ex = np.nan
    rr = sub[[col, ref]].dropna()
    if col != ref and len(rr) >= 20:
        ex = float((1+rr[col]).prod())**(SPY/len(rr)) - float((1+rr[ref]).prod())**(SPY/len(rr))
    return dict(n=n, cagr=cagr, sharpe=sh, dd=dd, excess=ex)

def boot_p(v, nb=20000, L=20, seed=11):
    v = np.asarray(v, float); v = v[np.isfinite(v)]
    if len(v) < 100: return np.nan, np.nan, np.nan, np.nan
    rng = np.random.default_rng(seed); nblk = len(v)//L
    st = rng.integers(0, len(v)-L, (nb, nblk))
    idx = (st[:,:,None] + np.arange(L)[None,None,:]).reshape(nb,-1)
    bs = v[idx].mean(axis=1); obs = v.mean()
    p = float((np.abs(bs-obs) >= abs(obs)).mean())
    return obs*SPY, float(np.percentile(bs,2.5))*SPY, float(np.percentile(bs,97.5))*SPY, p

def bh(ps, q=0.10):
    ps = np.asarray(ps, float); m = int(np.isfinite(ps).sum())
    order = np.argsort(np.where(np.isfinite(ps), ps, 9)); out = np.zeros(len(ps), bool); k = -1
    for rank, i in enumerate(order[:m], 1):
        if ps[i] <= q*rank/m: k = rank
    if k > 0:
        for rank, i in enumerate(order[:m], 1):
            if rank <= k: out[i] = True
    return out

# ---------------------------------------------------------------- 1. CONFOUND: breadth-tile co ~ ky nguyen khong?
print("\n=========== CONFOUND: breadth tercile theo NAM (so sanh voi radar zone ~ ky nguyen) ===========")
ct_b = pd.crosstab(d.yr, d.btile).reindex(columns=["LOW","MID","HIGH"]).fillna(0).astype(int)
print(ct_b.to_string())
ct_z = pd.crosstab(d.yr, d.zone).reindex(columns=["RE","TRUNGTINH","DAT"]).fillna(0).astype(int)
def era_conc(ct):
    """% nam co >=90% phien roi vao MOT nhan duy nhat = do 'dinh ky nguyen'."""
    rs = ct.sum(axis=1); rs = rs[rs > 0]
    frac = ct.loc[rs.index].div(rs, axis=0).max(axis=1)
    return float((frac >= 0.90).mean()), float(frac.mean())
cb, mb = era_conc(ct_b); cz, mz = era_conc(ct_z)
print(f"\n  BREADTH: {100*cb:.0f}% so nam bi MOT nhan chiem >=90% phien | share nhan troi TB = {100*mb:.0f}%")
print(f"  RADAR  : {100*cz:.0f}% so nam bi MOT nhan chiem >=90% phien | share nhan troi TB = {100*mz:.0f}%")
print(f"  -> breadth {'BIEN THIEN TRONG nam' if mb < mz else 'cung dinh ky nguyen nhu radar'} "
      f"(share nhan troi thap hon = tot hon)")

# ---------------------------------------------------------------- 2. ma tran 5x3
rows = []
for reg in REG:
    for tl in ["LOW","MID","HIGH","*ALL*"]:
        msk = (d.regime == reg) if tl == "*ALL*" else ((d.regime == reg) & (d.btile == tl))
        sub = d[msk]
        if len(sub) == 0: continue
        rec = dict(regime=reg, btile=tl, days=len(sub), episodes=blocks(msk.to_numpy()),
                   first=str(sub.time.min().date()), last=str(sub.time.max().date()),
                   n_years=sub.yr.nunique(), breadth_mean=float(sub.breadth.mean()),
                   radar_mean=float(sub.score.mean()) if sub.score.notna().any() else np.nan)
        for nm, col in [("VNI","r_vni"),("BAL","r_bal"),("LAG","r_lag"),("COMB","r_comb")]:
            s = stat(sub, col)
            rec[f"{nm}_cagr"] = s["cagr"]; rec[f"{nm}_sharpe"] = s["sharpe"]
            rec[f"{nm}_dd"] = s["dd"]; rec[f"{nm}_ex"] = s["excess"]
        rows.append(rec)
C = pd.DataFrame(rows); C.to_csv(os.path.join(OUT, "b2_cells.csv"), index=False)

def pc(x): return "  n/a " if pd.isna(x) else f"{100*x:+6.1f}"
print("\n=========== MA TRAN DT5G x BREADTH-TERCILE (CAGR annualised, gross backtest) ===========")
print(f"{'regime':8s} {'btile':7s} {'days':>5s} {'ep':>4s} {'yrs':>4s} {'brd':>5s} {'radar':>6s} | "
      f"{'VNI':>7s} {'BAL':>7s} {'LAG':>7s} {'COMB':>7s} | {'BALex':>7s} {'LAGex':>7s} {'COMBex':>7s} | "
      f"{'BALsh':>6s} {'LAGsh':>6s}")
for _, r in C.iterrows():
    print(f"{r.regime:8s} {r.btile:7s} {r.days:5.0f} {r.episodes:4.0f} {r.n_years:4.0f} "
          f"{100*r.breadth_mean:5.1f} {r.radar_mean:6.1f} | "
          f"{pc(r.VNI_cagr)} {pc(r.BAL_cagr)} {pc(r.LAG_cagr)} {pc(r.COMB_cagr)} | "
          f"{pc(r.BAL_ex)} {pc(r.LAG_ex)} {pc(r.COMB_ex)} | {r.BAL_sharpe:6.2f} {r.LAG_sharpe:6.2f}")

# ---------------------------------------------------------------- 3. BH FDR 10%
print("\n=========== BH(FDR 10%) 15 o x 3 chien luoc — H0: excess vs VNI = 0 ===========")
tests = []
for reg in REG:
    for tl in ["LOW","MID","HIGH"]:
        sub = d[(d.regime == reg) & (d.btile == tl)]
        ep = blocks(((d.regime == reg) & (d.btile == tl)).to_numpy())
        for nm, col in [("BAL","r_bal"),("LAG","r_lag"),("COMB","r_comb")]:
            v = (sub[col] - sub["r_vni"]).dropna()
            m, lo, hi, p = boot_p(v)
            tests.append(dict(regime=reg, btile=tl, strat=nm, n=len(v), episodes=ep,
                              ann=m, lo=lo, hi=hi, p=p))
T = pd.DataFrame(tests)
T["pass_BH10"] = bh(T.p.to_numpy(), 0.10)
T["pass_bonf"] = T.p < 0.05/max(1, int(T.p.notna().sum()))
T = T.sort_values("p")
for _, r in T.iterrows():
    if not np.isfinite(r.p):
        print(f"  {r.regime:8s} {r.btile:5s} {r.strat:4s} n={r.n:4d} ep={r.episodes:3.0f}  MAU QUA NHO (bo)")
        continue
    print(f"  {r.regime:8s} {r.btile:5s} {r.strat:4s} n={r.n:4d} ep={r.episodes:3.0f} "
          f"excess_ann={100*r.ann:+7.1f}% CI[{100*r.lo:+6.1f},{100*r.hi:+6.1f}] p={r.p:.4f} "
          f"BH10={'PASS' if r.pass_BH10 else 'fail'} Bonf={'PASS' if r.pass_bonf else 'fail'}")
T.to_csv(os.path.join(OUT, "b2_bh_tests.csv"), index=False)
nb_pass = int(T.pass_BH10.sum()); nt = int(T.p.notna().sum())
print(f"\n  N_trials = {nt} | PASS BH10 = {nb_pass} | PASS Bonferroni = {int(T.pass_bonf.sum())}")

# so sanh voi ma tran radar
Z = pd.read_csv(os.path.join(OUT, "bh_tests.csv"))
print(f"  [SO SANH] ma tran RADAR (job _101400): N_trials={int(Z.p.notna().sum())} "
      f"PASS BH10={int(Z.pass_BH10.sum())}")

# ---------------------------------------------------------------- 4. n_effective
print("\n=========== N_EFFECTIVE: so episode doc lap / so NAM co mat, breadth vs radar ===========")
def eff(col, labs):
    out = []
    for reg in REG:
        for lb in labs:
            msk = ((d.regime == reg) & (d[col] == lb))
            if msk.sum() == 0: continue
            out.append(dict(cell=f"{reg}+{lb}", days=int(msk.sum()), ep=blocks(msk.to_numpy()),
                            yrs=d[msk].yr.nunique()))
    return pd.DataFrame(out)
EB = eff("btile", ["LOW","MID","HIGH"]); EZ = eff("zone", ["RE","TRUNGTINH","DAT"])
print(f"  BREADTH: {len(EB)} o | episode: median {EB.ep.median():.0f} min {EB.ep.min()} max {EB.ep.max()} "
      f"tong {EB.ep.sum()} | nam/o: median {EB.yrs.median():.0f}")
print(f"  RADAR  : {len(EZ)} o | episode: median {EZ.ep.median():.0f} min {EZ.ep.min()} max {EZ.ep.max()} "
      f"tong {EZ.ep.sum()} | nam/o: median {EZ.yrs.median():.0f}")
EB.to_csv(os.path.join(OUT,"b2_neff_breadth.csv"), index=False)
EZ.to_csv(os.path.join(OUT,"b2_neff_radar.csv"), index=False)

# ---------------------------------------------------------------- 5. marginal theo tercile + IS/OOS + LOO
print("\n=========== MARGINAL theo BREADTH-TERCILE (gop moi regime) ===========")
for tl in ["LOW","MID","HIGH"]:
    sub = d[d.btile == tl]
    line = f"  {tl:5s} days={len(sub):5d} ep={blocks((d.btile==tl).to_numpy()):3d} "
    for nm, col in [("VNI","r_vni"),("BAL","r_bal"),("LAG","r_lag"),("COMB","r_comb")]:
        s = stat(sub, col); line += f"{nm}={pc(s['cagr'])}({pc(s['excess'])}) "
    print(line)

print("\n=========== WALK-FORWARD: excess ann theo tercile, IS 2014-2019 vs OOS 2020+ ===========")
for tl in ["LOW","MID","HIGH"]:
    for lbl, msk in [("IS 14-19", d.yr <= 2019), ("OOS 20+", d.yr >= 2020)]:
        sub = d[(d.btile == tl) & msk]
        line = f"  {tl:5s} {lbl:9s} n={len(sub):5d} "
        for nm, col in [("BAL","r_bal"),("LAG","r_lag"),("COMB","r_comb")]:
            v = (sub[col]-sub["r_vni"]).dropna()
            line += f"{nm}={100*v.mean()*SPY:+7.1f}% " if len(v) >= 40 else f"{nm}=   n/a  "
        print(line)

print("\n=========== LOO theo NAM: excess ann COMB theo tercile khi BO tung nam ===========")
for tl in ["LOW","MID","HIGH"]:
    vals = []
    for y in sorted(d.yr.unique()):
        sub = d[(d.btile == tl) & (d.yr != y)]
        v = (sub.r_comb - sub.r_vni).dropna()
        if len(v) >= 100: vals.append((y, v.mean()*SPY))
    if vals:
        arr = np.array([v for _, v in vals])
        print(f"  {tl:5s} min {100*arr.min():+6.1f}%  max {100*arr.max():+6.1f}%  "
              f"dao dau = {'CO' if arr.min()*arr.max() < 0 else 'khong'}  | " +
              " ".join(f"{y}:{100*v:+.0f}" for y, v in vals))
print("\n[done] b2_cells.csv / b2_bh_tests.csv / b2_neff_*.csv")

# ---------------------------------------------------------------- 6. ROBUSTNESS: tercile TRE 1 phien
# breadth_t dung Close cua CHINH phien t => corr(pct252_t, r_vni_t) != 0. Voi bat ky y dinh WIRE nao
# thi phai dung nhan TRE 1 phien. Kiem tra ket luan co song khong.
d["btile_lag1"] = d.btile.shift(1)
print("\n=========== ROBUSTNESS: tercile TRE 1 PHIEN (bat buoc neu muon wire) ===========")
for tl in ["LOW","MID","HIGH"]:
    sub = d[d.btile_lag1 == tl]
    line = f"  {tl:5s} days={len(sub):5d} "
    for nm, col in [("VNI","r_vni"),("COMB","r_comb")]:
        s = stat(sub, col); line += f"{nm}={pc(s['cagr'])}({pc(s['excess'])}) "
    for lbl, msk in [("IS", d.yr <= 2019), ("OOS", d.yr >= 2020)]:
        v = (d[(d.btile_lag1 == tl) & msk].r_comb - d[(d.btile_lag1 == tl) & msk].r_vni).dropna()
        line += f"{lbl}ex={100*v.mean()*SPY:+7.1f}% "
    print(line)

# ---------------------------------------------------------------- 7. excess co phai chi la 'it dau tu' khong?
print("\n=========== PHAN RA: ty trong DAU TU (co phieu+ETF / NAV) cua so BAL theo tercile ===========")
d["inv_bal"] = (d.bal_stocks_ref + d.bal_etf_ref) / d.nav_bal_ref
d["inv_lag"] = (d.lag_stocks_ref + d.lag_etf_ref) / d.nav_lag_ref
for tl in ["LOW","MID","HIGH"]:
    sub = d[d.btile == tl]
    s_c = stat(sub, "r_comb"); s_v = stat(sub, "r_vni")
    # beta cua COMB voi VNI trong o
    rr = sub[["r_comb","r_vni"]].dropna()
    beta = float(np.polyfit(rr.r_vni, rr.r_comb, 1)[0]) if len(rr) > 30 else np.nan
    # excess "co hoc" neu chi la beta<1: beta*VNI, phan con lai = alpha
    alpha = s_c["cagr"] - beta*s_v["cagr"]
    print(f"  {tl:5s} inv_BAL={100*sub.inv_bal.mean():5.1f}% inv_LAG={100*sub.inv_lag.mean():5.1f}% "
          f"beta_COMB={beta:5.2f} | COMB={pc(s_c['cagr'])} VNI={pc(s_v['cagr'])} "
          f"excess_tho={pc(s_c['cagr']-s_v['cagr'])} alpha_sau_beta={pc(alpha)}")
