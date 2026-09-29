# -*- coding: utf-8 -*-
"""
viec_b_live.py -- VIEC B: hieu qua HIEN TAI tu so paper THAT (data/orb_pt_log.csv),
khong phai backtest. So chieu voi ky vong do TU Viec A tren doan PRE-LIVE (khong dung
chinh du lieu live de dung ky vong -- neu khong thi moi ket luan "dung ky vong" la vong tron).
"""
import sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np, pandas as pd
import orb_core as C

OUT = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(20260925)
LOG = "/home/trido/thanhdt/WorkingClaude/data/orb_pt_log.csv"
log = pd.read_csv(LOG); log["dt"] = pd.to_datetime(log["date"])
x = log["net"].values; n = len(x)
res = {"source": LOG, "n_sessions": n, "first": log["date"].iloc[0], "last": log["date"].iloc[-1]}

def st(v, ann=252):
    v = np.asarray(v); m = v.mean(); s = v.std(ddof=1)
    nav = np.cumprod(1+v)
    return dict(n=len(v), mean_bps=m*1e4, sd_bps=s*1e4, sharpe=float(m/s*np.sqrt(ann)) if s>0 else 0.0,
                wr=float((v>0).mean()), cum=float(nav[-1]-1),
                mdd=float((nav/np.maximum.accumulate(nav)-1).min()),
                t=float(m/(s/np.sqrt(len(v)))) if s>0 else 0.0)

print("="*100); print(f"  B1) SO PAPER THAT: {n} phien, {res['first']} -> {res['last']}"); print("="*100)
L = st(x)
print(f"  mean/phien = {L['mean_bps']:+.2f}bps | sd = {L['sd_bps']:.2f}bps | Sharpe_ann = {L['sharpe']:+.2f}")
print(f"  win rate   = {L['wr']*100:.1f}% | cumulative = {L['cum']*100:+.2f}% | MaxDD = {L['mdd']*100:+.2f}%"
      f" | t = {L['t']:+.2f} (p ~ {2*(1-abs(L['t'])/abs(L['t']) if False else 0):.0f})")
# t-test 2 phia khong can scipy
from normstat import ncdf
p2 = 2*(1-ncdf(abs(L["t"])))
print(f"  t-test mot mau (H0: mean=0): t = {L['t']:+.3f}, p ~ {p2:.3f} (normal approx, n={n})")
res["B1_live"] = L; res["B1_p2"] = p2
# doi soat NAV cot trong log (tu tinh lai) -- bat loi ghi log
nav_rec = 1e9*np.cumprod(1+x)
res["B1_nav_check_max_abs_diff_vnd"] = float(np.abs(nav_rec - log["nav"].values).max())
print(f"  Doi soat cot nav trong log (tu tinh lai tu net): lech lon nhat = "
      f"{res['B1_nav_check_max_abs_diff_vnd']:,.2f} VND")

# --- ky vong tu PRE-LIVE ---
days = C.build_days(C.load_bars()); R = C.sim(days)
pre = R[R["date"] < C.LIVE_START]["net"].values
P = st(pre)
print("\n" + "-"*100)
print(f"  KY VONG (tu Viec A, CHI doan pre-live n={len(pre)}): mean {P['mean_bps']:+.2f}bps |"
      f" sd {P['sd_bps']:.2f}bps | Sharpe {P['sharpe']:+.2f} | WR {P['wr']*100:.1f}%")
print(f"  THUC TE live ({n} phien)                          : mean {L['mean_bps']:+.2f}bps |"
      f" sd {L['sd_bps']:.2f}bps | Sharpe {L['sharpe']:+.2f} | WR {L['wr']*100:.1f}%")
# phan vi cua ket qua live trong phan phoi k=n phien lien tiep rut tu pre-live
K = len(pre); starts = rng.integers(0, K-n+1, size=50000)
S = pre[starts[:,None] + np.arange(n)]
cums = np.prod(1+S, axis=1)-1
mus  = S.mean(axis=1)
sds  = S.std(axis=1, ddof=1); shs = np.where(sds>0, mus/sds*np.sqrt(252), 0.0)
pct = lambda arr, v: float((arr < v).mean())*100
print(f"\n  Vi tri ket qua live trong phan phoi {n} phien LIEN TIEP rut tu pre-live (50.000 lan):")
print(f"    cumulative {L['cum']*100:+.2f}%  -> phan vi {pct(cums, L['cum']):.0f}%"
      f"  (p5 {np.percentile(cums,5)*100:+.2f}% / p50 {np.percentile(cums,50)*100:+.2f}%"
      f" / p95 {np.percentile(cums,95)*100:+.2f}%)")
print(f"    mean/phien {L['mean_bps']:+.2f}bps -> phan vi {pct(mus*1e4, L['mean_bps']):.0f}%")
print(f"    Sharpe     {L['sharpe']:+.2f}      -> phan vi {pct(shs, L['sharpe']):.0f}%")
print(f"    => P(ket qua te hon live | ky vong dung) = {pct(cums, L['cum'])/100:.2f}."
      f" Live KHONG o duoi ({'TRONG' if 5<=pct(cums,L['cum'])<=95 else 'NGOAI'}) khoang p5-p95.")
res["B1_expectation_prelive"] = P
res["B1_percentile_in_prelive_dist"] = {"cum": pct(cums, L["cum"]), "mean": pct(mus*1e4, L["mean_bps"]),
                                        "sharpe": pct(shs, L["sharpe"]),
                                        "p5_cum_pct": float(np.percentile(cums,5))*100,
                                        "p50_cum_pct": float(np.percentile(cums,50))*100,
                                        "p95_cum_pct": float(np.percentile(cums,95))*100}

# ---------- B2) 3 cua so lien tiep ----------
print("\n" + "="*100); print("  B2) XU HUONG THEO THOI GIAN -- 3 cua so lien tiep (25/25/25 phien)"); print("="*100)
W = [(0,25),(25,50),(50,75)]
wres = {}
print(f"  {'cua so':<26}{'n':>4}{'mean':>9}{'Sharpe':>9}{'WR':>8}{'cum':>9}{'MaxDD':>9}")
print("  "+"-"*74)
for i,(a,b) in enumerate(W,1):
    sub = log.iloc[a:b]; s = st(sub["net"].values); wres[f"W{i}"] = dict(
        start=sub["date"].iloc[0], end=sub["date"].iloc[-1], **s)
    print(f"  W{i} {sub['date'].iloc[0]}..{sub['date'].iloc[-1]:<9}{s['n']:>4}{s['mean_bps']:>+8.2f}"
          f"{s['sharpe']:>+9.2f}{s['wr']*100:>7.1f}%{s['cum']*100:>+8.2f}%{s['mdd']*100:>+8.2f}%")
tr = [wres[f"W{i}"]["mean_bps"] for i in (1,2,3)]
print(f"\n  mean/phien theo cua so: {tr[0]:+.2f} -> {tr[1]:+.2f} -> {tr[2]:+.2f} bps")
# test xu huong: Spearman rho giua thu tu phien va net (khong can scipy)
rk = pd.Series(x).rank().values; ri = np.arange(1., n+1)
rho = float(np.corrcoef(rk, ri)[0,1]); tt = rho*np.sqrt((n-2)/max(1e-12,1-rho**2))
print(f"  Spearman(thu tu phien, net) rho = {rho:+.3f}, t = {tt:+.2f}, p ~ {2*(1-ncdf(abs(tt))):.3f}"
      f"  => {'khong' if 2*(1-ncdf(abs(tt)))>0.05 else 'CO'} bang chung xu huong don dieu")
# theo thang
log["ym"] = log["dt"].dt.to_period("M").astype(str)
mres = {}
print(f"\n  Theo THANG:  {'thang':<10}{'n':>4}{'mean':>9}{'cum':>9}{'WR':>8}")
for ym, gg in log.groupby("ym"):
    s = st(gg["net"].values); mres[ym] = s
    print(f"               {ym:<10}{s['n']:>4}{s['mean_bps']:>+8.2f}{s['cum']*100:>+8.2f}%{s['wr']*100:>7.1f}%")
res["B2_windows"] = wres; res["B2_spearman"] = {"rho": rho, "t": tt, "p": 2*(1-ncdf(abs(tt)))}
res["B2_months"] = mres

# ---------- B3) so voi TAPE VN30F cung ky ----------
print("\n" + "="*100); print("  B3) ORB vs TAPE VN30F (buy&hold F1M) cung ky -- co tuong quan bat thuong?"); print("="*100)
df = C.load_bars()
dd = df.sort_values("time").groupby("date").agg(close=("close","last")).reset_index()
dd["date"] = dd["date"].astype(str); dd["bh"] = dd["close"].pct_change()
mrg = log.merge(dd[["date","bh","close"]], on="date", how="left")
mrg["ym"] = mrg["dt"].dt.to_period("M").astype(str)
print(f"  {'thang':<10}{'ORB cum':>11}{'TAPE cum':>11}{'n':>5}")
for ym, gg in mrg.groupby("ym"):
    orb = np.prod(1+gg["net"].values)-1
    tape = np.prod(1+gg["bh"].dropna().values)-1
    print(f"  {ym:<10}{orb*100:>+10.2f}%{tape*100:>+10.2f}%{len(gg):>5}")
    res.setdefault("B3_month", {})[ym] = {"orb_cum_pct": orb*100, "tape_cum_pct": tape*100, "n": int(len(gg))}
cc = mrg[["net","bh"]].dropna()
r_pear = float(np.corrcoef(cc["net"], cc["bh"])[0,1])
r_abs  = float(np.corrcoef(cc["net"], cc["bh"].abs())[0,1])
print(f"\n  corr(ORB net, tape daily ret)      = {r_pear:+.3f}  (n={len(cc)})"
      f"  -- ky vong ~0: ORB long/short doi xung, khong phai beta an")
print(f"  corr(ORB net, |tape daily ret|)    = {r_abs:+.3f}"
      f"  -- duong = ORB an bien do (momentum thuc), am = bi bien do lam hai")
# so lai tren pre-live de biet 2 con so tren co bat thuong khong
pre_r = R[R["date"] < C.LIVE_START].merge(dd[["date","bh"]], on="date", how="left").dropna(subset=["bh"])
pp = float(np.corrcoef(pre_r["net"], pre_r["bh"])[0,1]); pa = float(np.corrcoef(pre_r["net"], pre_r["bh"].abs())[0,1])
print(f"  Cung 2 con so tren doan PRE-LIVE   = {pp:+.3f} / {pa:+.3f} (n={len(pre_r)})"
      f"  => live {'KHOP' if abs(r_pear-pp)<0.25 and abs(r_abs-pa)<0.25 else 'LECH'} nen lich su")
res["B3_corr"] = {"live_corr_tape": r_pear, "live_corr_abs_tape": r_abs,
                  "prelive_corr_tape": pp, "prelive_corr_abs_tape": pa}
# thang tape am nhat
tm = mrg.groupby("ym").apply(lambda g: np.prod(1+g["bh"].dropna().values)-1, include_groups=False)
worst = tm.idxmin()
print(f"\n  Thang tape te nhat trong cua so live: {worst} ({tm[worst]*100:+.2f}%)"
      f" -> ORB thang do {res['B3_month'][worst]['orb_cum_pct']:+.2f}%")
res["B3_worst_tape_month"] = {"month": worst, "tape_pct": float(tm[worst])*100,
                              "orb_pct": res["B3_month"][worst]["orb_cum_pct"]}

with open(os.path.join(OUT,"viec_b_result.json"),"w") as f: json.dump(res,f,indent=1,default=str)
print("\nDone. -> viec_b_result.json")
