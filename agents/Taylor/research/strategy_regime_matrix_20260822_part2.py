#!/usr/bin/env python
"""Part 2 — kiem dinh do manh cua ma tran: confound zone~era, BH multiple-testing,
Tier-1 lead/lag, rate sensitivity. Doc panel_daily.csv do part 1 sinh ra."""
import os, sys
import numpy as np, pandas as pd
W = "/home/trido/thanhdt/WorkingClaude"; sys.path.insert(0, W)
OUT = os.path.join(W,"mike","agents","Taylor","research","strategy_regime_matrix_20260822")
SPY = 249.2785102175346
d = pd.read_csv(os.path.join(OUT,"panel_daily.csv"), parse_dates=["time"])
d["yr"] = d.time.dt.year
pd.set_option("display.width",250,"display.max_columns",40)

print("=========== CONFOUND 1: zone ~ NAM (radar zone co phai chi la 'thoi ky' khong?) ===========")
ct = pd.crosstab(d.yr, d.zone).reindex(columns=["RE","TRUNGTINH","DAT"]).fillna(0).astype(int)
print(ct.to_string())
print("\n=========== CONFOUND 2: regime x zone — so phien theo NAM cua o NEUTRAL ===========")
print(pd.crosstab(d[d.regime=="NEUTRAL"].yr, d[d.regime=="NEUTRAL"].zone).to_string())

print("\n=========== CONFOUND 3: DT5G state la HAM cua gia => VNI return theo state la CO HOC ===========")
for s in ["CRISIS","BEAR","NEUTRAL","BULL","EXBULL"]:
    r = d[d.regime==s].r_vni.dropna()
    print(f"  {s:8s} n={len(r):5d} VNI ann={100*((1+r).prod()**(SPY/len(r))-1):+7.1f}%  "
          f"(day la DINH NGHIA cua state, khong phai edge)")

# ---------------- block bootstrap p-value + BH
def boot_p(v, nb=20000, L=20, seed=11):
    v = np.asarray(v, float); v = v[np.isfinite(v)]
    if len(v) < 100: return np.nan, np.nan, np.nan, np.nan   # mau qua nho => KHONG kiem dinh
    rng = np.random.default_rng(seed); nblk = len(v)//L
    starts = rng.integers(0, len(v)-L, (nb, nblk))
    idx = (starts[:,:,None] + np.arange(L)[None,None,:]).reshape(nb,-1)
    bs = v[idx].mean(axis=1)
    obs = v.mean()
    # p 2 phia quanh 0, dung phan phoi bootstrap tam ve 0
    centered = bs - obs
    p = float((np.abs(centered) >= abs(obs)).mean())
    return obs*SPY, float(np.percentile(bs,2.5))*SPY, float(np.percentile(bs,97.5))*SPY, p

def bh(ps, q=0.10):
    ps = np.asarray(ps, float); m = np.isfinite(ps).sum()
    order = np.argsort(np.where(np.isfinite(ps), ps, 9))
    thr = np.full(len(ps), False); k_max = -1
    for rank, i in enumerate(order[:m], start=1):
        if ps[i] <= q*rank/m: k_max = rank
    if k_max > 0:
        for rank, i in enumerate(order[:m], start=1):
            if rank <= k_max: thr[i] = True
    return thr

print("\n=========== BH(FDR 10%) tren 15 o x 3 chien luoc: H0 = excess vs VNI = 0 ===========")
tests = []
for reg in ["CRISIS","BEAR","NEUTRAL","BULL","EXBULL"]:
    for zn in ["RE","TRUNGTINH","DAT"]:
        sub = d[(d.regime==reg)&(d.zone==zn)]
        for nm, col in [("BAL","r_bal"),("LAG","r_lag"),("AL4","r_al")]:
            v = (sub[col] - sub["r_vni"]).dropna()
            m, lo, hi, p = boot_p(v)
            tests.append(dict(regime=reg, zone=zn, strat=nm, n=len(v), ann=m, lo=lo, hi=hi, p=p))
T = pd.DataFrame(tests)
T["pass_BH10"] = bh(T.p.to_numpy(), 0.10)
T["pass_bonf"] = T.p < 0.05/T.p.notna().sum()
T = T.sort_values("p")
for _, r in T.iterrows():
    if not np.isfinite(r.p): 
        print(f"  {r.regime:8s} {r.zone:10s} {r.strat:4s} n={r.n:4d}  MAU QUA NHO (bo)")
        continue
    print(f"  {r.regime:8s} {r.zone:10s} {r.strat:4s} n={r.n:4d} excess_ann={100*r.ann:+7.1f}% "
          f"CI[{100*r.lo:+6.1f},{100*r.hi:+6.1f}] p={r.p:.4f} BH10={'PASS' if r.pass_BH10 else 'fail'} "
          f"Bonf={'PASS' if r.pass_bonf else 'fail'}")
T.to_csv(os.path.join(OUT,"bh_tests.csv"), index=False)
print(f"\n  N_trials khai bao = {T.p.notna().sum()} (15 o x 3 chien luoc, bo o thieu mau). "
      f"So PASS BH10 = {int(T.pass_BH10.sum())}, PASS Bonferroni = {int(T.pass_bonf.sum())}")

# ---------------- IS/OOS stability cua ket luan zone
print("\n=========== WALK-FORWARD: excess theo zone, IS 2014-2019 vs OOS 2020+ ===========")
for zn in ["RE","TRUNGTINH","DAT"]:
    for lbl, msk in [("IS 14-19", d.yr<=2019), ("OOS 20+", d.yr>=2020)]:
        sub = d[(d.zone==zn)&msk]
        line = f"  {zn:10s} {lbl:9s} n={len(sub):5d} "
        for nm, col in [("BAL","r_bal"),("LAG","r_lag"),("AL4","r_al")]:
            v = (sub[col]-sub["r_vni"]).dropna()
            line += f"{nm}={100*v.mean()*SPY:+7.1f}% " if len(v)>=40 else f"{nm}=   n/a  "
        print(line)

# ---------------- Tier-1 lead/lag quanh transition
print("\n=========== TIER-1 LEAD/LAG quanh DT5G transition (cum ret, phien tuong doi) ===========")
d["st_prev"] = d.state.shift(1)
tr = d.index[(d.state != d.st_prev) & d.st_prev.notna()].to_numpy()
groups = {"vao xau (->CRISIS/BEAR)": [(a,b) for a,b in zip(d.st_prev[tr], d.state[tr])],}
def around(idxs, col, lo=-20, hi=20):
    m = []
    for i in idxs:
        if i+lo < 0 or i+hi >= len(d): continue
        seg = d[col].iloc[i+lo:i+hi+1].fillna(0).to_numpy()
        m.append(np.cumprod(1+seg)-1)
    return np.array(m)
down = [i for i in tr if d.state.iloc[i] < d.st_prev.iloc[i]]
up   = [i for i in tr if d.state.iloc[i] > d.st_prev.iloc[i]]
for nm, idxs in [("XUONG state (n=%d)"%len(down), down), ("LEN state (n=%d)"%len(up), up)]:
    print(f"  --- {nm} ---")
    for col, lab in [("r_al","AL4"),("r_vni","VNI"),("r_bal","BAL"),("r_lag","LAG")]:
        a = around(idxs, col)
        if len(a)==0: continue
        mu = a.mean(axis=0)
        print(f"    {lab:4s} T-20={100*mu[0]:+6.2f}% T-10={100*mu[10]:+6.2f}% T0={100*mu[20]:+6.2f}% "
              f"T+10={100*mu[30]:+6.2f}% T+20={100*mu[40]:+6.2f}%")

# ---------------- Banking vs rate regime
print("\n=========== BANKING (ACB/MBB/HDB) vs FPT theo che do LAI SUAT + zone ===========")
import value_radar
vr = value_radar.load_series(update=False)[["time","deposit_rate"]]
vr["time"]=pd.to_datetime(vr["time"]); d = d.merge(vr, on="time", how="left")
d["rate_bucket"] = pd.cut(d.deposit_rate, [0,5.5,6.5,8.0,99], labels=["<5.5%","5.5-6.5%","6.5-8%",">8%"])
d["r_bank"] = d[["r_ACB","r_MBB","r_HDB"]].mean(axis=1, skipna=True)
for b in ["<5.5%","5.5-6.5%","6.5-8%",">8%"]:
    sub = d[d.rate_bucket==b]
    if len(sub)<60: continue
    f = lambda c: 100*((1+sub[c].dropna()).prod()**(SPY/sub[c].notna().sum())-1)
    print(f"  rate {b:9s} n={len(sub):5d} BANK={f('r_bank'):+7.1f}% FPT={f('r_FPT'):+7.1f}% "
          f"VNI={f('r_vni'):+7.1f}% | BANKex={f('r_bank')-f('r_vni'):+7.1f}pp FPTex={f('r_FPT')-f('r_vni'):+7.1f}pp")
print("\n  BANK vs FPT theo zone:")
for zn in ["RE","TRUNGTINH","DAT"]:
    sub = d[d.zone==zn]
    f = lambda c: 100*((1+sub[c].dropna()).prod()**(SPY/sub[c].notna().sum())-1)
    print(f"    {zn:10s} n={len(sub):5d} BANK={f('r_bank'):+7.1f}% FPT={f('r_FPT'):+7.1f}% VNI={f('r_vni'):+7.1f}%")

# ---------------- current cell forward behaviour
print("\n=========== O HIEN TAI NEUTRAL+RE: 18 doan, forward 60 phien tu ngay VAO o ===========")
flag = ((d.regime=="NEUTRAL")&(d.zone=="RE")).to_numpy()
entries = np.where(flag & ~np.r_[False, flag[:-1]])[0]
rowsx=[]
for i in entries:
    if i+60 >= len(d): continue
    seg = lambda c: float(np.prod(1+d[c].iloc[i:i+60].fillna(0))-1)
    rowsx.append(dict(date=str(d.time.iloc[i].date()), COMB=seg("r_comb"), BAL=seg("r_bal"),
                      LAG=seg("r_lag"), AL4=seg("r_al"), VNI=seg("r_vni"), radar=float(d.score.iloc[i])))
E = pd.DataFrame(rowsx)
print(E.to_string(index=False, float_format=lambda x: f"{x:+.3f}"))
print(f"\n  MEDIAN f60: COMB={E.COMB.median():+.3f} BAL={E.BAL.median():+.3f} LAG={E.LAG.median():+.3f} "
      f"AL4={E.AL4.median():+.3f} VNI={E.VNI.median():+.3f}  (n={len(E)} doan, KHONG doc lap hoan toan)")
print(f"  hit>VNI: COMB={100*(E.COMB>E.VNI).mean():.0f}% BAL={100*(E.BAL>E.VNI).mean():.0f}% "
      f"LAG={100*(E.LAG>E.VNI).mean():.0f}% AL4={100*(E.AL4>E.VNI).mean():.0f}%")
E.to_csv(os.path.join(OUT,"neutral_re_entries.csv"), index=False)
