"""Bang so sanh + DSR/PBO/LOO cho ho cau hinh Aggressive (job Taylor_20260804_012953).

ZERO-RISK: chi doc CSV NAV da sinh trong data/ (khong chay lai engine, khong dung production).
Ham DSR / CSCV-PBO / bootstrap COPY nguyen tu dsr_pbo_annex.py (Bailey & Lopez de Prado 2014,
Bailey-Borwein-LdP-Zhu 2017) de so sanh duoc voi annex da pin trong data/results_registry.md.

Chay:  $DNA_PYEXE agg_metrics.py
"""
import math
import os
import sys
from itertools import combinations

import numpy as np
import pandas as pd

DATA = "/home/trido/thanhdt/WorkingClaude/data"
PRE = "v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_"
SUF = "_univpit.csv"
ANN = 252.0

# ---- ho cau hinh cua VONG NAY (truc target park x truc deadband) -------------------
# (label, tag, park_target_NEUTRAL, deadband, co_phai_trial_moi)
FAMILY = [
    ("A0 gate (=A, 0 param moi)", "agg_A0_gate",   0.70, 0.005, False),
    ("F1  target 0.80",           "agg_F1_t80",    0.80, 0.005, True),
    ("F2  target 0.85",           "agg_F2_t85",    0.85, 0.005, True),
    ("F3  target 0.90",           "agg_F3_t90",    0.90, 0.005, True),
    ("G1  band 3,0%",             "agg_G1_b03",    0.70, 0.030, True),
    ("G2  band 6,0%",             "agg_G2_b06",    0.70, 0.060, True),
    ("H1  target 0.85 + band 3%", "agg_H1_t85b03", 0.85, 0.030, True),
]
# park_tag do pt_v23_audit_2014.py tu them khi PARK_STATES != {3:0.7}
PARKTAG = {0.70: "", 0.80: "_park3-80", 0.85: "_park3-85", 0.90: "_park3-90"}

# ---- chan doi chieu tu vong 2x2 (§E cua bao cao 2026-08-03) ------------------------
REF = [
    ("A  control (= so pin R3)", "v3_A_control"),
    ("C  L1 only (JIT skip)",    "v2_C_skip"),
    ("D  L2 only (prefill off)", "v3_D_prefill_off"),
    ("E  LIVE hom nay",          "v3_E_both_off"),
]


def path_family(tag, frac):
    return os.path.join(DATA, PRE.replace("_advprice_exp_", "_advprice") + "")  # placeholder


def build_path(tag, parktag=""):
    # thu tu that trong pt_v23_audit_2014.py: ..._etfliqcustompitg[_park3-XX]_wtnamecap_advprice_exp_<tag>_univpit
    base = ("v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg"
            + parktag + "_wtnamecap_advprice_exp_" + tag + "_univpit.csv")
    return os.path.join(DATA, base)


def load_nav(path):
    df = pd.read_csv(path, low_memory=False)
    d = df[df["combined_nav"].notna() & df["ymd"].notna()].copy()
    d["ymd"] = pd.to_datetime(d["ymd"], errors="coerce")
    d = d.dropna(subset=["ymd"]).sort_values("ymd")
    return d.groupby("ymd")["combined_nav"].last().astype(float)


def metrics(nav):
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1 / yrs) - 1
    # Sharpe theo DUNG cong thuc engine (pt_v23_audit_2014.py:2407): SIMPLE daily return,
    # mean/std*sqrt(252). Dung log-return se ra 1,83 thay vi 1,90 -> lech voi so pin.
    r = nav.values[1:] / nav.values[:-1] - 1.0
    sharpe = r.mean() / r.std(ddof=1) * math.sqrt(ANN)
    dd = (nav / nav.cummax() - 1).min()
    return dict(cagr=cagr * 100, sharpe=sharpe, maxdd=dd * 100,
                calmar=(cagr / abs(dd)) if dd < 0 else float("nan"),
                final=nav.iloc[-1])


def cagr_of(nav):
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    return ((nav.iloc[-1] / nav.iloc[0]) ** (1 / yrs) - 1) * 100


def per_year(nav):
    out = {}
    for y in sorted(set(nav.index.year)):
        s = nav[nav.index.year == y]
        if len(s) < 5:
            continue
        out[y] = math.log(s.iloc[-1] / s.iloc[0])
    return out


def loo_cagr(nav):
    """CAGR khi BO tung nam (chain-link log-return cua cac nam con lai)."""
    py = per_year(nav)
    tot = sum(py.values())
    n = len(py)
    full = (math.exp(tot / n) - 1) * 100
    return full, {y: (math.exp((tot - v) / (n - 1)) - 1) * 100 for y, v in py.items()}


# ---------------- DSR (BLdP 2014) — copy tu dsr_pbo_annex.py ----------------
def moments(r):
    mu, sd = r.mean(), r.std(ddof=1)
    sr = mu / sd
    z = r - mu
    sd0 = r.std(ddof=0)
    return sr, np.mean(z**3) / sd0**3, np.mean(z**4) / sd0**4


def norm_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def norm_ppf(p):
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    pl = 0.02425
    if p < pl:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > 1 - pl:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


def expected_max_sr(var_sr, N):
    g = 0.5772156649015329
    return math.sqrt(var_sr) * ((1-g)*norm_ppf(1 - 1.0/N) + g*norm_ppf(1 - 1.0/(N*math.e)))


def dsr(sr_hat, sr0, g3, g4, T):
    denom = math.sqrt(max(1e-12, 1 - g3*sr_hat + (g4-1)/4.0*sr_hat**2))
    return norm_cdf((sr_hat - sr0) * math.sqrt(T - 1) / denom)


# ---------------- CSCV / PBO (Bailey et al 2017) ----------------
def cscv_pbo(M, S=16, metric="sharpe"):
    T, Ncfg = M.shape
    M = M[:(T // S) * S]
    blocks = np.array_split(M, S, axis=0)

    def perf(mat):
        if metric == "sharpe":
            sd = mat.std(axis=0, ddof=1)
            return mat.mean(axis=0) / np.where(sd == 0, np.nan, sd)
        return mat.mean(axis=0)          # metric="cagr" -> mean log-return

    idx = list(range(S))
    logits, fails = [], 0
    combos = list(combinations(idx, S // 2))
    for cis in combos:
        cis = set(cis)
        IS = np.vstack([blocks[b] for b in cis])
        OS = np.vstack([blocks[b] for b in idx if b not in cis])
        sris, sros = perf(IS), perf(OS)
        n_star = int(np.nanargmax(sris))
        order = np.argsort(np.argsort(np.nan_to_num(sros, nan=-1e9)))
        w = min(max((order[n_star] + 1) / (Ncfg + 1.0), 1e-6), 1 - 1e-6)
        lam = math.log(w / (1 - w))
        logits.append(lam)
        fails += (lam < 0)
    return fails / len(combos), np.array(logits), len(combos)


# ---------------- Stationary bootstrap (Politis-Romano 1994) ----------------
def _cagr_dd(logp):
    nav = np.exp(np.cumsum(logp))
    peak = np.maximum.accumulate(nav)
    yrs = len(logp) / ANN
    return nav[-1] ** (1 / yrs) - 1, (nav / peak - 1).min()


def stationary_boot(r, mean_L=21, B=4000, seed=12345):
    N = len(r)
    rng = np.random.default_rng(seed)
    p_geom = 1.0 / mean_L
    C = np.empty(B); D = np.empty(B)
    for b in range(B):
        out = []
        while len(out) < N:
            start = rng.integers(0, N)
            Lb = rng.geometric(p_geom)
            out.extend(np.take(r, np.arange(start, start + Lb), mode="wrap"))
        C[b], D[b] = _cagr_dd(np.array(out[:N]))
    return C, D


# ==================== RUN ====================
def main():
    print("=" * 100)
    print("AGGRESSIVE FAMILY SWEEP — job Taylor_20260804_012953")
    print("Cau hinh chung: AUDIT_END=2026-06-19, NAV=50B, universe_pit,")
    print("BQ_LOCAL_CACHE=bq_cache_asof20260729_postrestate, threads=1, LAG_ADV_BASIS=price (mac dinh)")
    print("=" * 100)

    # ---- 1. GATE no-op ----
    p_gate = build_path("agg_A0_gate", "")
    p_ref = build_path("v3_A_control", "")
    import hashlib
    def md5(p):
        return hashlib.md5(open(p, "rb").read()).hexdigest()
    if os.path.exists(p_gate) and os.path.exists(p_ref):
        m1, m2 = md5(p_gate), md5(p_ref)
        ok = "PASS" if m1 == m2 else "*** FAIL ***"
        print(f"\n[GATE] no-op PARK_BAND=0.005 & PARK_STATES=3:0.7 -> md5 {m1[:8]} vs chan A {m2[:8]}  => {ok}")
        if m1 != m2:
            print("       => SWITCH KHONG NO-OP. Moi so cua vong nay PHAI VUT BO.")
            sys.exit(1)
    else:
        print("\n[GATE] *** thieu file, khong kiem tra duoc ***")
        sys.exit(1)

    # ---- 2. Bang metric ----
    rows, series = [], {}
    print("\n" + "-" * 100)
    print(f"{'Cau hinh':30s} {'target':>7s} {'band':>6s} {'CAGR':>8s} {'Sharpe':>7s} "
          f"{'MaxDD':>8s} {'Calmar':>7s} {'FinalNAV':>10s} {'IS':>7s} {'OOS':>7s}")
    print("-" * 100)
    for label, tag, frac, band, is_trial in FAMILY:
        p = build_path(tag, PARKTAG[frac])
        if not os.path.exists(p):
            print(f"{label:30s}  *** THIEU FILE {os.path.basename(p)}")
            continue
        nav = load_nav(p)
        series[label] = nav
        m = metrics(nav)
        isr = cagr_of(nav[nav.index <= "2019-12-31"])
        oos = cagr_of(nav[nav.index >= "2020-01-01"])
        rows.append((label, tag, frac, band, is_trial, m, isr, oos))
        print(f"{label:30s} {frac:>7.2f} {band:>6.3f} {m['cagr']:>7.2f}% {m['sharpe']:>7.2f} "
              f"{m['maxdd']:>7.1f}% {m['calmar']:>7.2f} {m['final']/1e9:>9.1f}B {isr:>6.2f}% {oos:>6.2f}%")

    print("-" * 100)
    print("Chan doi chieu (vong 2x2, §E):")
    for label, tag in REF:
        p = build_path(tag, "")
        if not os.path.exists(p):
            print(f"{label:30s}  *** THIEU {os.path.basename(p)}")
            continue
        nav = load_nav(p)
        series[label] = nav
        m = metrics(nav)
        isr = cagr_of(nav[nav.index <= "2019-12-31"])
        oos = cagr_of(nav[nav.index >= "2020-01-01"])
        print(f"{label:30s} {'-':>7s} {'-':>6s} {m['cagr']:>7.2f}% {m['sharpe']:>7.2f} "
              f"{m['maxdd']:>7.1f}% {m['calmar']:>7.2f} {m['final']/1e9:>9.1f}B {isr:>6.2f}% {oos:>6.2f}%")
    print("-" * 100)

    # ---- 3. DSR ----
    fam_labels = [r[0] for r in rows]
    srs = []
    for lb in fam_labels:
        r = np.diff(np.log(series[lb].values))
        srs.append(r.mean() / r.std(ddof=1))
    var_sr = np.var(srs, ddof=1)
    N_TRIALS = len(fam_labels)          # ho cau hinh cua VONG NAY (gom ca corner A0)

    # Var(SR) uoc tu 7 cau hinh gan-giong-nhau la uoc luong THIEU (bias xuong) -> SR0 nho ->
    # DSR bi thoi phong len 1,0. Uoc luong trung thuc hon: dung do phan tan SR cua CA HO
    # tim kiem V2.3A/V2.4 da ghi trong registry (cung glob nhu dsr_pbo_annex.py).
    import glob as _glob
    wide = []
    for p in sorted(_glob.glob(os.path.join(DATA, "v23_golive_audit_2014_now_*.csv"))):
        b = os.path.basename(p)
        if any(f"nav{n}" in b for n in ("1B", "5B", "10B", "20B", "100B", "150B",
                                        "200B", "300B", "500B")) or "from20" in b:
            continue
        try:
            s = load_nav(p)
        except Exception:
            continue
        if len(s) < 2500:
            continue
        rr = np.diff(np.log(s.values))
        wide.append(rr.mean() / rr.std(ddof=1))
    var_sr_wide = np.var(wide, ddof=1) if len(wide) > 2 else var_sr

    print(f"\n[DSR] N_trials (ho cau hinh vong nay, ke ca corner A0) = {N_TRIALS}")
    print(f"      Var(per-day SR) trong ho hep (n={len(srs)})  = {var_sr:.3e}  "
          f"(sd ann-SR = {np.std(srs, ddof=1)*math.sqrt(ANN):.3f})")
    print(f"      Var(per-day SR) ho tim kiem rong (n={len(wide)}) = {var_sr_wide:.3e}  "
          f"(sd ann-SR = {np.std(wide, ddof=1)*math.sqrt(ANN):.3f})  <- dung cho cot 'rong'")
    print(f"\n{'Cau hinh':30s} {'DSR@N=' + str(N_TRIALS) + ' hep':>15s} "
          f"{'DSR@N=7 rong':>13s} {'DSR@N=120 rong':>15s} {'DSR@N=200 rong':>15s}")
    for lb in fam_labels:
        r = np.diff(np.log(series[lb].values))
        sr_hat, g3, g4 = moments(r)
        T = len(r)
        v_narrow = dsr(sr_hat, expected_max_sr(var_sr, N_TRIALS), g3, g4, T)
        vals = [dsr(sr_hat, expected_max_sr(var_sr_wide, N), g3, g4, T) for N in (N_TRIALS, 120, 200)]
        flag = "" if min(vals) >= 0.95 else "  <<< RED FLAG"
        print(f"{lb:30s} {v_narrow:>15.4f} {vals[0]:>13.4f} {vals[1]:>15.4f} {vals[2]:>15.4f}{flag}")

    # ---- 4. PBO (CSCV) ----
    print("\n[PBO] CSCV tren ho cau hinh vong nay (S=16 block)")
    common = None
    for lb in fam_labels:
        common = series[lb].index if common is None else common.intersection(series[lb].index)
    common = common.sort_values()
    lvl = np.column_stack([series[lb].reindex(common).values for lb in fam_labels])
    Mret = np.diff(np.log(lvl), axis=0)
    for met in ("sharpe", "cagr"):
        pbo, logits, ncomb = cscv_pbo(Mret, S=16, metric=met)
        print(f"      metric={met:6s}  matrix {Mret.shape[0]}d x {len(fam_labels)}cfg, {ncomb} split  "
              f"-> PBO = {pbo:.4f}   logit median = {np.median(logits):+.2f}")

    # ---- 4b. Per-config IS->OOS rank degradation (PBO la thong ke CUA CA HO, khong xep hang
    #          duoc tung cau hinh; day la proxy per-config: cau hinh nao "dep IS, xau OOS") ----
    print("\n[rank-drop] Do tut hang IS->OOS cua TUNG cau hinh (CSCV S=16, metric=CAGR)")
    print("            rank 1 = te nhat, 7 = tot nhat. d<0 = dep trong IS hon la trong OOS.")
    S = 16
    T = Mret.shape[0]
    blocks = np.array_split(Mret[:(T // S) * S], S, axis=0)
    idx = list(range(S))
    drops = {lb: [] for lb in fam_labels}
    for cis in combinations(idx, S // 2):
        cis = set(cis)
        IS = np.vstack([blocks[b] for b in cis])
        OS = np.vstack([blocks[b] for b in idx if b not in cis])
        ri = np.argsort(np.argsort(IS.mean(axis=0))) + 1
        ro = np.argsort(np.argsort(OS.mean(axis=0))) + 1
        for j, lb in enumerate(fam_labels):
            drops[lb].append(ro[j] - ri[j])
    print(f"{'Cau hinh':30s} {'d_rank tb':>10s} {'P(tut hang)':>12s}")
    for lb in fam_labels:
        d = np.array(drops[lb])
        print(f"{lb:30s} {d.mean():>+10.3f} {(d < 0).mean():>11.1%}")

    # ---- 4c. Stationary bootstrap (Politis-Romano) — rui ro duoi, so voi neo DD ----
    print("\n[bootstrap] stationary (Politis-Romano, mean L=21, B=4000, seed=12345)")
    print(f"{'Cau hinh':30s} {'CAGR p5':>9s} {'CAGR p50':>9s} {'DD p5':>8s} {'DD p50':>8s} {'P(DD<-30%)':>11s}")
    boot_targets = fam_labels + [lb for lb, _ in REF if lb in series and lb.startswith("E")]
    for lb in boot_targets:
        r = np.diff(np.log(series[lb].values))
        C, D = stationary_boot(r, mean_L=21, B=4000, seed=12345)
        print(f"{lb:30s} {np.percentile(C,5)*100:>8.1f}% {np.percentile(C,50)*100:>8.1f}% "
              f"{np.percentile(D,5)*100:>7.1f}% {np.percentile(D,50)*100:>7.1f}% "
              f"{(D < -0.30).mean()*100:>10.1f}%")

    # ---- 5. Per-year LOO ----
    print("\n[LOO] CAGR khi BO tung nam (do phu thuoc mot nam) — chenh so voi A0/Conservative")
    base_full, base_loo = loo_cagr(series[fam_labels[0]])
    years = sorted(base_loo)
    print(f"{'Cau hinh':30s} {'full*':>7s} " + " ".join(f"{y:>6d}" for y in years))
    for lb in fam_labels:
        full, loo = loo_cagr(series[lb])
        print(f"{lb:30s} {full:>6.2f}% " + " ".join(f"{loo[y]:>6.2f}" for y in years))
    print("      (*full = CAGR chain-link theo nam, khac nhe CAGR lich vi dem nam tron)")

    print("\n[LOO-delta] (cau hinh − A0) CAGR khi bo tung nam — edge con lai bao nhieu?")
    print(f"{'Cau hinh':30s} {'d_full':>7s} " + " ".join(f"{y:>6d}" for y in years))
    for lb in fam_labels[1:]:
        full, loo = loo_cagr(series[lb])
        print(f"{lb:30s} {full-base_full:>+6.2f}pp " + " ".join(f"{loo[y]-base_loo[y]:>+6.2f}" for y in years))

    # ---- 6. Per-year returns ----
    print("\n[per-year] loi nhuan tung nam (%)")
    print(f"{'Cau hinh':30s} " + " ".join(f"{y:>7d}" for y in years))
    for lb in fam_labels + [r[0] for r in REF if r[0] in series]:
        py = per_year(series[lb])
        print(f"{lb:30s} " + " ".join(f"{(math.exp(py[y])-1)*100:>+7.1f}" for y in years))

    print("\n" + "=" * 100)


if __name__ == "__main__":
    main()
