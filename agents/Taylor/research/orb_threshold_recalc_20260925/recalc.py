# -*- coding: utf-8 -*-
"""Tinh lai nguong N cho orb_intraday tren effect size HOP NHAT (1129 trade).

Hai cau hoi KHAC NHAU:
  (A) N de t-stat ky vong cham nguong (quy uoc CU cua job _103217) va N de dat power 80% THAT.
  (B) N de DSR(N_trials=20) tu no vuot 0.95, giu nguyen SR/obs da do.
"""
import json
import numpy as np, pandas as pd
from scipy import stats as st

CSV = "../orb_fiinx_vn30f1m_20260925/orb_trades_extended_20220217_20260925.csv"
a = pd.read_csv(CSV)
x = a["net"].values
n0 = len(x); mu = x.mean(); sd = x.std(ddof=1)
sk = st.skew(x); ku = st.kurtosis(x, fisher=False)
sr = mu / sd
out = {"n_obs": int(n0), "mean_bps": mu*1e4, "sd_bps": sd*1e4,
       "skew": float(sk), "kurt_nonexcess": float(ku), "sr_per_obs": float(sr),
       "sharpe_ann": float(sr*np.sqrt(252)), "t_obs": float(mu/(sd/np.sqrt(n0)))}

# --- doan CU de doi chieu ---
OLD_MU, OLD_SD = 9.06e-4, 93.6e-4
def n_for_t(t, m, s): return (t*s/m)**2
def n_for_power(alpha_one_sided, power, m, s):
    z = st.norm.ppf(1-alpha_one_sided) + st.norm.ppf(power)
    return (z*s/m)**2

out["old_effect"] = {"mean_bps": 9.06, "sd_bps": 93.6,
    "n_t164": n_for_t(1.64, OLD_MU, OLD_SD), "n_t20": n_for_t(2.0, OLD_MU, OLD_SD),
    "n_power80_1s": n_for_power(0.05, 0.80, OLD_MU, OLD_SD),
    "n_power80_2s": n_for_power(0.025, 0.80, OLD_MU, OLD_SD)}
out["new_effect"] = {
    "n_t164": n_for_t(1.64, mu, sd), "n_t20": n_for_t(2.0, mu, sd),
    "n_power80_1s": n_for_power(0.05, 0.80, mu, sd),
    "n_power80_2s": n_for_power(0.025, 0.80, mu, sd),
    "n_power80_2s_extra": n_for_power(0.025, 0.80, mu, sd) - n0}

# --- PSR / DSR ---
G = 0.5772156649
def psr(sr_, sr0, n, sk_, ku_):
    den = np.sqrt(1 - sk_*sr_ + (ku_-1)/4*sr_**2)
    return st.norm.cdf((sr_-sr0)*np.sqrt(n-1)/den)
def sr0_of(N_trials, n):
    e = (1-G)*st.norm.ppf(1-1/N_trials) + G*st.norm.ppf(1-1/(N_trials*np.e))
    return e/np.sqrt(n)          # cung quy uoc voi analyse.py job _111203
def dsr(n, N_trials=20, sr_=None):
    sr_ = sr if sr_ is None else sr_
    return psr(sr_, sr0_of(N_trials, n), n, sk, ku)

out["psr_now"] = float(psr(sr, 0.0, n0, sk, ku))
out["dsr_now"] = {str(N): float(dsr(n0, N)) for N in (12, 20, 40)}

def solve_n(target, N_trials):
    lo, hi = 10, 10**9
    if dsr(hi, N_trials) < target: return None
    while hi - lo > 1:
        mid = (lo+hi)//2
        if dsr(mid, N_trials) >= target: hi = mid
        else: lo = mid
    return hi
out["n_for_dsr095"] = {str(N): solve_n(0.95, N) for N in (12, 20, 40)}
out["n_for_dsr095_old_sr"] = {}
sr_old = OLD_MU/OLD_SD
for N in (20,):
    lo, hi = 10, 10**9
    f = lambda n: psr(sr_old, sr0_of(N, n), n, sk, ku)
    while hi-lo > 1:
        mid=(lo+hi)//2
        if f(mid) >= 0.95: hi=mid
        else: lo=mid
    out["n_for_dsr095_old_sr"][str(N)] = hi

# DSR tai vai moc N de thay duong cong
out["dsr_curve_N20"] = {str(k): float(dsr(k, 20)) for k in (1129, 1500, 2000, 2500, 3000, 4000, 5000, 6000)}

# Bootstrap CI cho mean hop nhat
rng = np.random.default_rng(20260925)
bs = rng.choice(x, size=(20000, n0), replace=True).mean(axis=1)
out["boot_mean_ci95_bps"] = [float(np.percentile(bs,2.5)*1e4), float(np.percentile(bs,97.5)*1e4)]
out["boot_p_mean_le0"] = float((bs <= 0).mean())

# Quy doi phien -> nam (252 phien/nam)
for k in ("n_t164","n_t20","n_power80_1s","n_power80_2s"):
    out["new_effect"][k+"_years"] = out["new_effect"][k]/252
out["years_for_dsr095_N20"] = out["n_for_dsr095"]["20"]/252 if out["n_for_dsr095"]["20"] else None
out["extra_years_for_dsr095_N20"] = (out["n_for_dsr095"]["20"]-n0)/252 if out["n_for_dsr095"]["20"] else None

print(json.dumps(out, indent=2, ensure_ascii=False))
json.dump(out, open("recalc_result.json","w"), indent=2, ensure_ascii=False)
