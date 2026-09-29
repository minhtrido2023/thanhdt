#!/usr/bin/env python
"""B2-ext — Alpha SAU KHU BETA cua V2.4 co phu thuoc breadth-tercile khong?

Job Taylor_20260822_153901. PAPER-ONLY. Prereg: research/b2_alpha_breadth_prereg_20260822.md
(viet TRUOC khi chay file nay — moi dinh nghia duoi day da chot o do).

H0: alpha (beta-adjusted) doc lap voi breadth-tercile.
H1 (mot duoi): alpha_HIGH - alpha_LOW > 0.

Nguon: panel_daily.csv (pin R3, part-1 job _101400) + b2_breadth.csv (universe_pit CANONICAL).
KHONG dung cot profit_*.
"""
import os, sys
import numpy as np, pandas as pd

W = "/home/trido/thanhdt/WorkingClaude"
OUT = os.path.join(W, "mike", "agents", "Taylor", "research", "strategy_regime_matrix_20260822")
SPY = 249.2785102175346
R3_CAGR_PIN = 0.2886          # pin R3 NEUTRAL-only @50B, universe_pit, 2026-08-03
STRATS = [("BAL", "r_bal"), ("LAG", "r_lag"), ("COMB", "r_comb")]
TILES = ["LOW", "MID", "HIGH"]
PAIRS = [("HIGH", "LOW"), ("HIGH", "MID"), ("MID", "LOW")]
REG_ORD = {"CRISIS": 0, "BEAR": 1, "NEUTRAL": 2, "BULL": 3, "EXBULL": 4}

# ------------------------------------------------------------------ 0. DU LIEU + SELFCHECK
d = pd.read_csv(os.path.join(OUT, "panel_daily.csv"), parse_dates=["time"], low_memory=False)
d = d[d.record_type == "DAILY"].sort_values("time").reset_index(drop=True)
d["yr"] = d.time.dt.year

print("=" * 100)
print("0. SELFCHECK — panel co khop pin R3 khong (dieu kien bat buoc truoc khi dung)")
print("=" * 100)
rc = d.r_comb.dropna()
cagr_full = float((1 + rc).prod()) ** (SPY / len(rc)) - 1
nav_end = 50e9 * float((1 + rc).prod())
print(f"  COMB full-sample: n={len(rc)} phien | CAGR={100*cagr_full:.2f}% "
      f"| NAV cuoi (tu 50B) = {nav_end/1e9:.2f}B")
print(f"  pin R3          : CAGR={100*R3_CAGR_PIN:.2f}%  NAV=1.178,01B")
dev = abs(cagr_full - R3_CAGR_PIN) * 100
print(f"  lech = {dev:.3f}pp  -> {'PASS (<=0,1pp)' if dev <= 0.1 else 'FAIL (>0,1pp) — DUNG LAI'}")
if dev > 0.1:
    sys.exit("SELFCHECK FAIL: panel khong khop pin R3, khong duoc dung tiep.")

# ------------------------------------------------------------------ 1. BREADTH TERCILE (PIT, tre 1 phien)
br = pd.read_csv(os.path.join(OUT, "b2_breadth.csv"), parse_dates=["time"]).sort_values("time").reset_index(drop=True)
b = br.breadth.to_numpy()
pct = np.full(len(b), np.nan)
for i in range(252, len(b)):
    pct[i] = (b[i - 252:i] < b[i]).mean()          # 252 phien TRUOC, khong gom i
br["pct252"] = pct
br["btile_sameday"] = pd.cut(br.pct252, [-0.001, 1/3, 2/3, 1.001], labels=TILES).astype(object)

d = d.merge(br[["time", "breadth", "pct252", "btile_sameday"]], on="time", how="left")
# PREREG §3.1: nhan dung de phan loai phien t la tercile cua phien t-1
d["btile"] = d.btile_sameday.shift(1)
d["breadth_lag1"] = d.breadth.shift(1)

print("\n" + "=" * 100)
print("1. BREADTH TERCILE — PIT, tre 1 phien (prereg §3.1)")
print("=" * 100)
print(f"  breadth: {br.time.min().date()}..{br.time.max().date()} n={len(br)} "
      f"| warm-up NaN = {int(br.pct252.isna().sum())} phien")
print(f"  panel {len(d)} phien | thieu btile = {int(d.btile.isna().sum())}")
cc = d[["pct252", "r_vni"]].dropna()
cc2 = d[["breadth_lag1", "r_vni"]].dropna()
print(f"  [no-lookahead] corr(pct252_t SAME-DAY, r_vni_t) = {cc.pct252.corr(cc.r_vni):+.4f}   <- kenh nhiem B2 do (+0,109 tren breadth tho)")
b1 = d[["btile", "r_vni"]].dropna()
print(f"  [no-lookahead] corr(breadth_{{t-1}}, r_vni_t)     = {cc2.breadth_lag1.corr(cc2.r_vni):+.4f}   <- nhan da tre 1 phien")

# ------------------------------------------------------------------ 2. ROLLING BETA + ALPHA
def rolling_beta(rs, rv, win=252, minobs=126):
    n = len(rs); out = np.full(n, np.nan)
    for i in range(n):
        lo = i - win + 1
        if lo < 0: continue
        x = rv[lo:i+1]; y = rs[lo:i+1]
        m = np.isfinite(x) & np.isfinite(y)
        if m.sum() < minobs: continue
        xx = x[m]; yy = y[m]
        vx = xx.var(ddof=1)
        if vx <= 0: continue
        out[i] = float(np.cov(yy, xx, ddof=1)[0, 1] / vx)
    return out

rv = d.r_vni.to_numpy(float)
for nm, col in STRATS:
    bt = rolling_beta(d[col].to_numpy(float), rv)
    d[f"beta_{nm}"] = bt
    d[f"beta_{nm}_lag1"] = pd.Series(bt).shift(1)           # PREREG §3.2: dung beta_{t-1}
    d[f"alpha_{nm}"] = d[col] - d[f"beta_{nm}_lag1"] * d.r_vni

print("\n" + "=" * 100)
print("2. ROLLING BETA 252 phien (min 126 obs), dung beta_{t-1} de khu beta cho phien t")
print("=" * 100)
for nm, _ in STRATS:
    s = d[f"beta_{nm}"].dropna()
    print(f"  beta_{nm:4s}: n={len(s):4d} | median {s.median():.3f} | P10 {s.quantile(.10):.3f} "
          f"P90 {s.quantile(.90):.3f} | min {s.min():.3f} max {s.max():.3f} "
          f"| bat dau {d.loc[d[f'beta_{nm}'].notna(),'time'].min().date()}")

# mau hieu dung: can CA btile_{t-1} VA beta_{t-1}
d["in_sample"] = d.btile.notna() & d.beta_COMB_lag1.notna() & d.r_vni.notna() & d.r_comb.notna()
E = d[d.in_sample].copy()
print(f"\n  mau hieu dung (co btile_{{t-1}} + beta_{{t-1}}): n={len(E)} phien, "
      f"{E.time.min().date()}..{E.time.max().date()}, {E.yr.nunique()} nam")
print(f"  phan bo tercile: {dict(E.btile.value_counts())}")

# ------------------------------------------------------------------ 3. HAM THONG KE
def blocks(flags):
    f = np.asarray(flags, bool)
    return int((f & (~np.r_[False, f[:-1]])).sum())

def boot_diff(alpha, tile, A, B, nb=10000, L=20, seed=20260822):
    """Block bootstrap tren CHUOI CHUNG (alpha_t, tile_t) -> phan phoi cua Delta = mean(A)-mean(B).
    p mot duoi = P( (Delta* - mean(Delta*)) >= Delta_obs )  [dich phan phoi ve H0: Delta=0]."""
    a = np.asarray(alpha, float); t = np.asarray(tile, object)
    ok = np.isfinite(a); a = a[ok]; t = t[ok]
    mA = (t == A); mB = (t == B)
    if mA.sum() < 60 or mB.sum() < 60:
        return dict(dA=np.nan, dB=np.nan, diff=np.nan, lo=np.nan, hi=np.nan, p=np.nan,
                    nA=int(mA.sum()), nB=int(mB.sum()))
    obs = a[mA].mean() - a[mB].mean()
    rng = np.random.default_rng(seed); n = len(a); nblk = max(1, n // L)
    st = rng.integers(0, n - L, (nb, nblk))
    idx = (st[:, :, None] + np.arange(L)[None, None, :]).reshape(nb, -1)
    aa = a[idx]; tt = t[idx]
    isA = (tt == A); isB = (tt == B)
    cA = isA.sum(axis=1); cB = isB.sum(axis=1)
    good = (cA >= 20) & (cB >= 20)
    mA_bs = np.where(good, np.where(isA, aa, 0).sum(axis=1) / np.maximum(cA, 1), np.nan)
    mB_bs = np.where(good, np.where(isB, aa, 0).sum(axis=1) / np.maximum(cB, 1), np.nan)
    dif = (mA_bs - mB_bs); dif = dif[np.isfinite(dif)]
    if len(dif) < 1000:
        return dict(dA=a[mA].mean()*SPY, dB=a[mB].mean()*SPY, diff=obs*SPY, lo=np.nan, hi=np.nan,
                    p=np.nan, nA=int(mA.sum()), nB=int(mB.sum()))
    p = float(((dif - dif.mean()) >= obs).mean())
    return dict(dA=a[mA].mean()*SPY, dB=a[mB].mean()*SPY, diff=obs*SPY,
                lo=float(np.percentile(dif, 2.5))*SPY, hi=float(np.percentile(dif, 97.5))*SPY,
                p=p, nA=int(mA.sum()), nB=int(mB.sum()))

def bh(ps, q=0.10):
    ps = np.asarray(ps, float); m = int(np.isfinite(ps).sum())
    order = np.argsort(np.where(np.isfinite(ps), ps, 9)); out = np.zeros(len(ps), bool); k = -1
    for rank, i in enumerate(order[:m], 1):
        if ps[i] <= q * rank / m: k = rank
    if k > 0:
        for rank, i in enumerate(order[:m], 1):
            if rank <= k: out[i] = True
    return out

# ------------------------------------------------------------------ 4. BANG ALPHA THEO TERCILE
print("\n" + "=" * 100)
print("4. ALPHA (nam hoa) THEO BREADTH-TERCILE — mau hieu dung")
print("=" * 100)
rows = []
print(f"  {'tile':5s} {'days':>5s} {'ep':>4s} {'yrs':>4s} {'brd':>6s} | "
      + " ".join(f"{nm+'_a':>9s} {nm+'_b':>6s}" for nm, _ in STRATS) + f" | {'VNI':>8s}")
for tl in TILES:
    sub = E[E.btile == tl]
    rec = dict(tile=tl, days=len(sub), episodes=blocks((E.btile == tl).to_numpy()),
               n_years=sub.yr.nunique(), breadth_mean=float(sub.breadth_lag1.mean()),
               vni_cagr=float((1+sub.r_vni).prod())**(SPY/len(sub))-1,
               vni_mean_ann=float(sub.r_vni.mean())*SPY)
    line = (f"  {tl:5s} {len(sub):5d} {rec['episodes']:4d} {rec['n_years']:4d} "
            f"{100*rec['breadth_mean']:5.1f}% |")
    for nm, col in STRATS:
        a = sub[f"alpha_{nm}"].dropna()
        rec[f"{nm}_alpha_ann"] = float(a.mean()) * SPY
        rec[f"{nm}_alpha_t"] = float(a.mean() / (a.std(ddof=1) / np.sqrt(len(a))))
        rec[f"{nm}_beta_mean"] = float(sub[f"beta_{nm}_lag1"].mean())
        rec[f"{nm}_ret_ann"] = float(sub[col].mean()) * SPY
        line += f" {100*rec[f'{nm}_alpha_ann']:+8.1f}% {rec[f'{nm}_beta_mean']:6.2f}"
    line += f" | {100*rec['vni_mean_ann']:+7.1f}%"
    print(line)
    rows.append(rec)
A = pd.DataFrame(rows)
print("  (cot _a = alpha nam hoa tu mean(alpha_t)*249,28; _b = beta_{t-1} trung binh trong o; "
      "VNI = mean(r_vni)*249,28)")

# ------------------------------------------------------------------ 5. TEST CHINH — 9 tests, BH FDR 10%
print("\n" + "=" * 100)
print("5. TEST CHINH (prereg §4) — 3 chien luoc x 3 cap, block bootstrap L=20 x10.000, p MOT DUOI")
print("=" * 100)
tests = []
for nm, _ in STRATS:
    for A_, B_ in PAIRS:
        r = boot_diff(E[f"alpha_{nm}"], E.btile, A_, B_)
        r.update(strat=nm, pair=f"{A_}-{B_}")
        tests.append(r)
T = pd.DataFrame(tests)
T["pass_BH10"] = bh(T.p.to_numpy(), 0.10)
T["pass_p05"] = T.p < 0.05
for _, r in T.iterrows():
    print(f"  {r.strat:4s} {r.pair:9s} nA={r.nA:4d} nB={r.nB:4d} | "
          f"alpha_A={100*r.dA:+7.1f}% alpha_B={100*r.dB:+7.1f}% | "
          f"Delta={100*r['diff']:+7.1f}% CI95[{100*r.lo:+6.1f},{100*r.hi:+6.1f}] "
          f"p1={r.p:.4f} {'BH10=PASS' if r.pass_BH10 else 'BH10=fail'}")
print(f"\n  N_trials = {int(T.p.notna().sum())} | PASS p<0,05 = {int(T.pass_p05.sum())} "
      f"| PASS BH FDR 10% = {int(T.pass_BH10.sum())}")

# ------------------------------------------------------------------ 6. IS/OOS
print("\n" + "=" * 100)
print("6. WALK-FORWARD: IS 2014-2019 vs OOS 2020+ (mau hieu dung bat dau ~2015)")
print("=" * 100)
wf = []
for nm, _ in STRATS:
    for lbl, msk in [("IS", E.yr <= 2019), ("OOS", E.yr >= 2020)]:
        S = E[msk]
        rec = dict(strat=nm, split=lbl, n=len(S))
        for tl in TILES:
            a = S.loc[S.btile == tl, f"alpha_{nm}"].dropna()
            rec[f"alpha_{tl}"] = float(a.mean())*SPY if len(a) >= 40 else np.nan
            rec[f"n_{tl}"] = len(a)
        rec["diff_HL"] = rec["alpha_HIGH"] - rec["alpha_LOW"]
        wf.append(rec)
        print(f"  {nm:4s} {lbl:3s} n={len(S):4d} | " +
              " ".join(f"{tl}={100*rec[f'alpha_{tl}']:+7.1f}%(n={rec[f'n_{tl}']:4d})" for tl in TILES) +
              f" | HIGH-LOW={100*rec['diff_HL']:+7.1f}%")
WF = pd.DataFrame(wf)
for nm, _ in STRATS:
    i = WF[(WF.strat == nm) & (WF.split == "IS")].diff_HL.iloc[0]
    o = WF[(WF.strat == nm) & (WF.split == "OOS")].diff_HL.iloc[0]
    print(f"  -> {nm}: IS={100*i:+.1f}% OOS={100*o:+.1f}% : "
          f"{'CUNG DAU' if np.isfinite(i) and np.isfinite(o) and i*o > 0 else 'DOI DAU / thieu du lieu'}")

# ------------------------------------------------------------------ 7. LOO theo nam
print("\n" + "=" * 100)
print("7. LOO THEO NAM — bo tung nam, tinh lai Delta(HIGH-LOW)")
print("=" * 100)
loo_rows = []
for nm, _ in STRATS:
    vals = []
    for y in sorted(E.yr.unique()):
        S = E[E.yr != y]
        aH = S.loc[S.btile == "HIGH", f"alpha_{nm}"].dropna()
        aL = S.loc[S.btile == "LOW", f"alpha_{nm}"].dropna()
        if len(aH) >= 100 and len(aL) >= 100:
            v = float(aH.mean() - aL.mean())*SPY
            vals.append((y, v)); loo_rows.append(dict(strat=nm, drop_year=y, diff_HL=v))
    arr = np.array([v for _, v in vals])
    pos = float((arr > 0).mean())
    print(f"  {nm:4s} n_year={len(arr)} | %duong={100*pos:.0f}% | min {100*arr.min():+6.1f}% "
          f"max {100*arr.max():+6.1f}% | " + " ".join(f"{y}:{100*v:+.0f}" for y, v in vals))
LOO = pd.DataFrame(loo_rows)

# ------------------------------------------------------------------ 8. ALIAS CHECK: breadth vs DT5G
print("\n" + "=" * 100)
print("8. ALIAS CHECK — breadth co phai chi la DT5G doi lot khong? (prereg §7.1)")
print("=" * 100)
E["reg_ord"] = E.regime.map(REG_ORD)
E["tile_ord"] = E.btile.map({"LOW": 0, "MID": 1, "HIGH": 2})
c_pear = E[["breadth_lag1", "reg_ord"]].dropna().corr().iloc[0, 1]
c_spear = E[["breadth_lag1", "reg_ord"]].dropna().corr(method="spearman").iloc[0, 1]
c_tile = E[["tile_ord", "reg_ord"]].dropna().corr(method="spearman").iloc[0, 1]
print(f"  corr(breadth_{{t-1}}, DT5G ordinal): Pearson {c_pear:+.3f} | Spearman {c_spear:+.3f}")
print(f"  corr(tercile_ord, DT5G ordinal)   : Spearman {c_tile:+.3f}")
print(f"  -> {'CAO (>0,5): phai kiem tra conditional-on-state' if abs(c_spear) > 0.5 else 'THAP (<=0,5): breadth khong phai alias cua regime'}")
print("\n  crosstab % phien (hang = DT5G, cot = breadth tercile):")
ct = pd.crosstab(E.regime, E.btile).reindex(index=list(REG_ORD), columns=TILES).fillna(0).astype(int)
ctp = ct.div(ct.sum(axis=1).replace(0, np.nan), axis=0) * 100
for reg in ct.index:
    print(f"    {reg:8s} n={int(ct.loc[reg].sum()):5d} | " +
          " ".join(f"{tl}={ctp.loc[reg, tl]:5.1f}%" for tl in TILES))

print("\n  CONDITIONAL: Delta alpha COMB (HIGH-LOW) TRONG cung mot DT5G state:")
cond_rows = []
for reg in REG_ORD:
    S = E[E.regime == reg]
    aH = S.loc[S.btile == "HIGH", "alpha_COMB"].dropna(); aL = S.loc[S.btile == "LOW", "alpha_COMB"].dropna()
    if len(aH) >= 60 and len(aL) >= 60:
        r = boot_diff(S.alpha_COMB, S.btile, "HIGH", "LOW")
        cond_rows.append(dict(regime=reg, **{k: r[k] for k in ("nA","nB","dA","dB","diff","p")}))
        print(f"    {reg:8s} nH={r['nA']:4d} nL={r['nB']:4d} aH={100*r['dA']:+7.1f}% aL={100*r['dB']:+7.1f}% "
              f"Delta={100*r['diff']:+7.1f}% p1={r['p']:.4f}")
    else:
        print(f"    {reg:8s} nH={len(aH):4d} nL={len(aL):4d} — MAU QUA NHO (bo)")
COND = pd.DataFrame(cond_rows)

# ------------------------------------------------------------------ 9. ROBUSTNESS
print("\n" + "=" * 100)
print("9. ROBUSTNESS (prereg §7.2-7.5) — Delta alpha COMB (HIGH-LOW) duoi cac bien the")
print("=" * 100)
rob = []

def add_rob(name, alpha_ser, tile_ser, note=""):
    r = boot_diff(alpha_ser, tile_ser, "HIGH", "LOW")
    rob.append(dict(variant=name, **{k: r[k] for k in ("nA","nB","dA","dB","diff","lo","hi","p")}, note=note))
    print(f"  {name:34s} aH={100*r['dA']:+7.1f}% aL={100*r['dB']:+7.1f}% "
          f"Delta={100*r['diff']:+7.1f}% p1={r['p']:.4f}  {note}")

add_rob("BASE (prereg)", E.alpha_COMB, E.btile, "rolling beta_{t-1} + tercile_{t-1}")

# 7.2a beta toan mau
bfull = float(np.cov(d.r_comb.dropna(), d.loc[d.r_comb.notna(), "r_vni"], ddof=1)[0,1] /
              d.loc[d.r_comb.notna(), "r_vni"].var(ddof=1))
E["alpha_fullbeta"] = E.r_comb - bfull * E.r_vni
add_rob("beta TOAN MAU (look-ahead)", E.alpha_fullbeta, E.btile, f"beta={bfull:.3f}")

# 7.2b beta rieng theo tercile (cach B2)
E["alpha_tilebeta"] = np.nan
tb = {}
for tl in TILES:
    S = E[E.btile == tl]
    bt = float(np.cov(S.r_comb, S.r_vni, ddof=1)[0,1] / S.r_vni.var(ddof=1)); tb[tl] = bt
    E.loc[E.btile == tl, "alpha_tilebeta"] = S.r_comb - bt * S.r_vni
add_rob("beta RIENG theo tercile (B2)", E.alpha_tilebeta, E.btile,
        "beta " + " ".join(f"{k}={v:.2f}" for k, v in tb.items()))

# 7.3 tercile toan mau (non-PIT)
q1, q2 = br.breadth.quantile([1/3, 2/3])
br["btile_global"] = pd.cut(br.breadth, [-9, q1, q2, 9], labels=TILES).astype(object)
g = d.merge(br[["time","btile_global"]], on="time", how="left")
E["btile_global"] = g.btile_global.shift(1).reindex(E.index)
add_rob("tercile TOAN MAU (non-PIT)", E.alpha_COMB, E.btile_global, f"cutoff {q1:.3f}/{q2:.3f}")

# 7.4 nhan cung phien (nhu B2)
add_rob("tercile CUNG PHIEN (nhu B2)", E.alpha_COMB, E.btile_sameday, "co same-day contamination")

# beta lag khac
for wnd in (126, 504):
    bt = rolling_beta(d.r_comb.to_numpy(float), rv, win=wnd, minobs=max(63, wnd//4))
    d[f"_b{wnd}"] = pd.Series(bt).shift(1)
    E[f"alpha_w{wnd}"] = E.r_comb - d[f"_b{wnd}"].reindex(E.index) * E.r_vni
    add_rob(f"rolling beta cua so {wnd} phien", E[f"alpha_w{wnd}"], E.btile)

# excess THO (khong khu beta) — de doi chieu voi B2
E["excess_raw"] = E.r_comb - E.r_vni
add_rob("EXCESS THO (khong khu beta)", E.excess_raw, E.btile, "<- huong B2 quan sat ban dau")
ROB = pd.DataFrame(rob)

# 7.5 phan ra ty trong dau tu
print("\n  PHAN RA — ty trong DAU TU va return tho theo tercile:")
E["inv_bal"] = (E.bal_stocks_ref + E.bal_etf_ref) / E.nav_bal_ref
E["inv_lag"] = (E.lag_stocks_ref + E.lag_etf_ref) / E.nav_lag_ref
for tl in TILES:
    S = E[E.btile == tl]
    print(f"    {tl:5s} inv_BAL={100*S.inv_bal.mean():5.1f}% inv_LAG={100*S.inv_lag.mean():5.1f}% "
          f"| r_COMB_ann={100*S.r_comb.mean()*SPY:+7.1f}% r_VNI_ann={100*S.r_vni.mean()*SPY:+7.1f}% "
          f"excess_tho={100*(S.r_comb.mean()-S.r_vni.mean())*SPY:+7.1f}% "
          f"alpha={100*S.alpha_COMB.mean()*SPY:+7.1f}%")

# ------------------------------------------------------------------ 10. VERDICT
print("\n" + "=" * 100)
print("10. VERDICT theo tieu chi prereg §5 (ap cho COMB)")
print("=" * 100)
tc = T[(T.strat == "COMB") & (T.pair == "HIGH-LOW")].iloc[0]
loo_c = LOO[LOO.strat == "COMB"].diff_HL
pos = float((loo_c > 0).mean())
is_d = WF[(WF.strat == "COMB") & (WF.split == "IS")].diff_HL.iloc[0]
oos_d = WF[(WF.strat == "COMB") & (WF.split == "OOS")].diff_HL.iloc[0]
c_a = tc["diff"] > 0.05
c_b = (tc.p < 0.05) and bool(tc.pass_BH10)
c_c = pos > 0.75
c_d = np.isfinite(is_d) and np.isfinite(oos_d) and is_d * oos_d > 0
print(f"  (a) Delta_HIGH-LOW > 5pp/nam : {100*tc['diff']:+.1f}%  -> {'DAT' if c_a else 'KHONG DAT'}")
print(f"  (b) p<0,05 mot duoi + qua BH10: p={tc.p:.4f}, BH10={'PASS' if tc.pass_BH10 else 'fail'} -> {'DAT' if c_b else 'KHONG DAT'}")
print(f"  (c) LOO >75% nam duong       : {100*pos:.0f}%  -> {'DAT' if c_c else 'KHONG DAT'}")
print(f"  (d) OOS cung dau IS          : IS={100*is_d:+.1f}% OOS={100*oos_d:+.1f}% -> {'DAT' if c_d else 'KHONG DAT'}")
if c_a and c_b and c_c and c_d:
    verdict = "CONFIRM"
elif (not np.isfinite(tc.p)) or tc.p > 0.10 or pos < 0.50 or (not c_d):
    verdict = "REFUTE"
else:
    verdict = "INCONCLUSIVE"
print(f"\n  ==> VERDICT (COMB): {verdict}")

# ------------------------------------------------------------------ XUAT
A.to_csv(os.path.join(OUT, "b2ext_alpha_tercile.csv"), index=False)
T.to_csv(os.path.join(OUT, "b2ext_tests.csv"), index=False)
WF.to_csv(os.path.join(OUT, "b2ext_walkforward.csv"), index=False)
LOO.to_csv(os.path.join(OUT, "b2ext_loo.csv"), index=False)
ROB.to_csv(os.path.join(OUT, "b2ext_robustness.csv"), index=False)
if len(COND): COND.to_csv(os.path.join(OUT, "b2ext_conditional.csv"), index=False)
print("\n[done] b2ext_alpha_tercile.csv / b2ext_tests.csv / b2ext_walkforward.csv / "
      "b2ext_loo.csv / b2ext_robustness.csv / b2ext_conditional.csv")
print(f"[VERDICT_MACHINE] {verdict} diff={tc['diff']:.6f} p={tc.p:.6f} loo_pos={pos:.4f} "
      f"is={is_d:.6f} oos={oos_d:.6f}")

# ------------------------------------------------------------------ 11. ATTRIBUTION: B2 (+11,8pp) -> BASE (+3,7pp)
# B2 dung: alpha = CAGR_comb - beta_o * CAGR_vni  (HINH HOC, gop) + nhan tercile CUNG PHIEN.
# BASE dung: alpha = mean(r_comb_t - beta_{t-1} r_vni_t)*SPY (SO HOC, ngay) + nhan tercile TRE 1 phien.
# Tach 2 nguon khac biet.
print("\n" + "=" * 100)
print("11. ATTRIBUTION — vi sao B2 ra ~+11,8pp con thiet ke prereg ra +3,7pp?")
print("=" * 100)

def cagr_of(r):
    r = pd.Series(r).dropna()
    return float((1 + r).prod()) ** (SPY / len(r)) - 1

def b2_style(frame, tilecol):
    """Y HET B2: beta OLS toan-o + alpha = CAGR_comb - beta*CAGR_vni."""
    o = {}
    for tl in TILES:
        S = frame[frame[tilecol] == tl].dropna(subset=["r_comb", "r_vni"])
        if len(S) < 60: o[tl] = (np.nan, np.nan); continue
        bt = float(np.polyfit(S.r_vni, S.r_comb, 1)[0])
        o[tl] = (cagr_of(S.r_comb) - bt * cagr_of(S.r_vni), bt)
    return o

att = []
for lbl, frame, tilecol, mode in [
    ("B2 nguyen ban (CAGR + nhan cung phien)", E, "btile_sameday", "geo"),
    ("  doi sang nhan TRE 1 phien",            E, "btile",         "geo"),
    ("  doi tiep sang alpha SO HOC ngay",      E, "btile",         "ari"),
]:
    if mode == "geo":
        o = b2_style(frame, tilecol)
        vals = {tl: o[tl][0] for tl in TILES}; betas = {tl: o[tl][1] for tl in TILES}
    else:
        vals, betas = {}, {}
        for tl in TILES:
            S = frame[frame[tilecol] == tl]
            bt = float(np.polyfit(S.r_vni.dropna(), S.r_comb.dropna(), 1)[0])
            vals[tl] = float((S.r_comb - bt * S.r_vni).mean()) * SPY; betas[tl] = bt
    dif = vals["HIGH"] - vals["LOW"]
    att.append(dict(step=lbl, **{f"alpha_{t}": vals[t] for t in TILES},
                    **{f"beta_{t}": betas[t] for t in TILES}, diff_HL=dif))
    print(f"  {lbl:42s} LOW={100*vals['LOW']:+6.1f}% MID={100*vals['MID']:+6.1f}% "
          f"HIGH={100*vals['HIGH']:+6.1f}% | HIGH-LOW={100*dif:+6.1f}% "
          f"| beta {betas['LOW']:.2f}/{betas['MID']:.2f}/{betas['HIGH']:.2f}")
print(f"  {'BASE prereg (rolling beta_{t-1}, ngay)':42s} "
      f"LOW={100*A.loc[A.tile=='LOW','COMB_alpha_ann'].iloc[0]:+6.1f}% "
      f"MID={100*A.loc[A.tile=='MID','COMB_alpha_ann'].iloc[0]:+6.1f}% "
      f"HIGH={100*A.loc[A.tile=='HIGH','COMB_alpha_ann'].iloc[0]:+6.1f}% | HIGH-LOW=  +3.7%")
pd.DataFrame(att).to_csv(os.path.join(OUT, "b2ext_attribution.csv"), index=False)

# monotonic? kiem tra hinh dang
print("\n  HINH DANG quan he (prereg gia dinh DON DIEU tang):")
for nm, _ in STRATS:
    v = [float(A.loc[A.tile == t, f"{nm}_alpha_ann"].iloc[0]) for t in TILES]
    shape = "DON DIEU TANG" if v[0] < v[1] < v[2] else ("CHU U (MID thap nhat)" if v[1] < min(v[0], v[2]) else "khac")
    print(f"    {nm:4s} LOW={100*v[0]:+6.1f}% MID={100*v[1]:+6.1f}% HIGH={100*v[2]:+6.1f}%  -> {shape}")
print("[done] b2ext_attribution.csv")
