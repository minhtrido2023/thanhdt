# -*- coding: utf-8 -*-
"""Tổng hợp A/B trần anchor NAV-level: metrics + per-year + LOO + DSR + PBO(CSCV).

Đọc THẲNG CSV audit của từng chân (không tin số in ra log) — §6/§18 "verify artifact".
Chạy: $DNA_PYEXE summarize.py
"""
import os, sys, itertools
import numpy as np, pandas as pd
from math import erf, sqrt, log, exp

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
BASE = ("v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_"
        "wtnamecap_advprice_exp_{tag}_univpit.csv")

LEGS = [
    ("L0  không trần (= pin R3)",      "anch_L0control", None),
    ("LA  trần = anchor (luật LIVE)",  "anch_LA_cap000", 0.00),
    ("LB  trần = anchor ×1,01",        "anch_LB_cap001", 0.01),
    ("LC  trần = anchor ×1,02",        "anch_LC_cap002", 0.02),
    ("LD  trần = anchor ×1,03 (đề xuất)", "anch_LD_cap003", 0.03),
    ("LE  trần = anchor ×1,05",        "anch_LE_cap005", 0.05),
]

SPY = 252.0


def _norm_cdf(x):
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


def _norm_ppf(p):
    # Acklam inverse-normal, đủ chính xác cho mục đích ở đây
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    pl, ph = 0.02425, 1 - 0.02425
    if p < pl:
        q = sqrt(-2 * log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > ph:
        q = sqrt(-2 * log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


def load_nav(tag):
    path = os.path.join(WORKDIR, "data", BASE.format(tag=tag))
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path, low_memory=False)
    d = df[df["combined_nav"].notna() & df["ymd"].notna()].copy()
    d["ymd"] = pd.to_datetime(d["ymd"], errors="coerce")
    d = d.dropna(subset=["ymd"]).sort_values("ymd")
    return d.groupby("ymd")["combined_nav"].last().astype(float)


def metrics(nav):
    r = nav.pct_change().dropna()
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    cagr = ((nav.iloc[-1] / nav.iloc[0]) ** (1 / yrs) - 1) * 100
    sharpe = r.mean() / r.std() * sqrt(SPY) if r.std() > 0 else float("nan")
    dd = (nav / nav.cummax() - 1) * 100
    mdd = dd.min()
    return dict(cagr=cagr, sharpe=sharpe, mdd=mdd, calmar=cagr / abs(mdd) if mdd else float("nan"),
                final=nav.iloc[-1] / 1e9, n=len(r))


def cagr_of(nav):
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    return ((nav.iloc[-1] / nav.iloc[0]) ** (1 / yrs) - 1) * 100


def yearly(nav):
    out = {}
    for y in sorted(set(nav.index.year)):
        ny = nav[nav.index.year == y]
        if len(ny) < 5:
            continue
        out[y] = ny.iloc[-1] / ny.iloc[0] - 1
    return out


def loo_cagr(yr):
    """CAGR khi bỏ 1 năm: ghép hình học các năm còn lại, chuẩn hoá theo số năm còn lại."""
    res = {}
    ys = sorted(yr)
    for drop in ys:
        keep = [1 + yr[y] for y in ys if y != drop]
        res[drop] = (np.prod(keep) ** (1 / len(keep)) - 1) * 100
    return res


def dsr(r, n_trials, sr_var):
    """Deflated Sharpe Ratio (Bailey & López de Prado 2014), r = daily returns."""
    r = np.asarray(r, dtype=float)
    N = len(r)
    sr = r.mean() / r.std(ddof=1)
    g3 = pd.Series(r).skew()
    g4 = pd.Series(r).kurtosis() + 3.0     # pandas trả excess kurtosis
    gamma = 0.5772156649
    e = exp(1.0)
    sr0 = sqrt(sr_var) * ((1 - gamma) * _norm_ppf(1 - 1.0 / n_trials)
                          + gamma * _norm_ppf(1 - 1.0 / (n_trials * e)))
    denom = sqrt(max(1e-12, 1 - g3 * sr + (g4 - 1) / 4.0 * sr ** 2))
    z = (sr - sr0) * sqrt(N - 1) / denom
    return _norm_cdf(z), sr * sqrt(SPY), sr0 * sqrt(SPY)


def pbo_cscv(ret_mat, S=16):
    """PBO qua CSCV. ret_mat: DataFrame (index=ngày, cột=config) daily returns."""
    T = len(ret_mat)
    m = T - (T % S)
    blocks = np.array_split(np.arange(m), S)
    idx = list(range(S))
    logits = []
    for comb in itertools.combinations(idx, S // 2):
        is_rows = np.concatenate([blocks[i] for i in comb])
        oos_rows = np.concatenate([blocks[i] for i in idx if i not in comb])
        R_is, R_oos = ret_mat.iloc[is_rows], ret_mat.iloc[oos_rows]
        sr_is = R_is.mean() / R_is.std(ddof=1)
        sr_oos = R_oos.mean() / R_oos.std(ddof=1)
        n_star = sr_is.values.argmax()
        rank = (sr_oos.rank(ascending=True).values[n_star]) / (len(sr_oos) + 1)
        rank = min(max(rank, 1e-6), 1 - 1e-6)
        logits.append(log(rank / (1 - rank)))
    logits = np.array(logits)
    return (logits <= 0).mean(), len(logits)


def main():
    data = {}
    for name, tag, cap in LEGS:
        nav = load_nav(tag)
        if nav is None:
            print(f"  [THIẾU] {name} ({tag})")
            continue
        data[name] = (nav, cap)

    print("\n=== BẢNG CHÍNH (NAV 50B, AUDIT_END=2026-06-19, universe_pit, threads=1) ===")
    print(f"{'Chân':<38}{'CAGR':>8}{'Sharpe':>8}{'MaxDD':>9}{'Calmar':>8}"
          f"{'FinalB':>10}{'IS14-19':>9}{'OOS20+':>9}{'ΔvsLA':>8}")
    base_la = None
    rows = {}
    for name, (nav, cap) in data.items():
        m = metrics(nav)
        is_c = cagr_of(nav[nav.index <= "2019-12-31"])
        oos_c = cagr_of(nav[nav.index >= "2020-01-01"])
        rows[name] = dict(m, is_c=is_c, oos_c=oos_c, nav=nav, cap=cap)
        if name.startswith("LA"):
            base_la = m["cagr"]
    for name in data:
        m = rows[name]
        dlt = "" if base_la is None else f"{m['cagr']-base_la:+7.2f}"
        print(f"{name:<38}{m['cagr']:>7.2f}%{m['sharpe']:>8.2f}{m['mdd']:>8.1f}%"
              f"{m['calmar']:>8.2f}{m['final']:>10.2f}{m['is_c']:>8.2f}%{m['oos_c']:>8.2f}%{dlt:>8}")

    print("\n=== PER-YEAR (%) ===")
    yrs_all = {n: yearly(rows[n]["nav"]) for n in rows}
    years = sorted(set().union(*[set(v) for v in yrs_all.values()]))
    print(f"{'Chân':<38}" + "".join(f"{y:>8}" for y in years))
    for n in rows:
        print(f"{n:<38}" + "".join(f"{yrs_all[n].get(y, float('nan'))*100:>7.1f}" + " " for y in years))

    la_name = [n for n in rows if n.startswith("LA")]
    ld_name = [n for n in rows if n.startswith("LD")]
    if la_name and ld_name:
        la, ld = la_name[0], ld_name[0]
        print(f"\n=== LEAVE-ONE-YEAR-OUT: Δ CAGR ({ld}) − ({la}) ===")
        loo_la, loo_ld = loo_cagr(yrs_all[la]), loo_cagr(yrs_all[ld])
        full = (np.prod([1+v for v in yrs_all[ld].values()])**(1/len(yrs_all[ld])) - 1) * 100 \
             - (np.prod([1+v for v in yrs_all[la].values()])**(1/len(yrs_all[la])) - 1) * 100
        print(f"  toàn mẫu (ghép hình học năm): {full:+.2f}pp")
        for y in sorted(loo_la):
            print(f"  bỏ {y}: {loo_ld[y]-loo_la[y]:+.2f}pp", end="   ")
        print()
        wins = sum(1 for y in yrs_all[la] if yrs_all[ld][y] > yrs_all[la][y])
        print(f"  số năm LD > LA: {wins}/{len(yrs_all[la])}")

    # ── DSR / PBO trên họ biến thể ──────────────────────────────────────────────
    fam = {n: rows[n]["nav"].pct_change().dropna() for n in rows}
    ret_mat = pd.DataFrame(fam).dropna()
    n_trials = len(fam)
    srs = np.array([ret_mat[c].mean() / ret_mat[c].std(ddof=1) for c in ret_mat.columns])
    sr_var = srs.var(ddof=1)
    print(f"\n=== MULTIPLE TESTING (N_trials = {n_trials} cấu hình cùng họ) ===")
    print(f"  Var(SR) giữa các chân (daily): {sr_var:.3e}")
    for n in rows:
        p, sr_ann, sr0_ann = dsr(fam[n].values, n_trials, sr_var)
        print(f"  DSR {n:<38} = {p:.4f}   (SR ann {sr_ann:.2f}, ngưỡng kỳ vọng SR0 ann {sr0_ann:.2f})")
    pbo, ncomb = pbo_cscv(ret_mat, S=16)
    print(f"  PBO (CSCV, S=16, {ncomb} tổ hợp) = {pbo:.3f}")


if __name__ == "__main__":
    main()
