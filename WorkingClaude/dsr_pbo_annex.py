"""DSR / PBO Robustness Annex — meta-analysis of multiple-testing risk for V2.4.

ZERO-RISK: reads only frozen daily-NAV CSVs already pinned in data/results_registry.md.
Does NOT run pt_v23 harness, does NOT touch production, does NOT re-run any backtest.

Implements:
  1. Trial count N          — distinct config CSVs in the V2.3A/V2.4 search family.
  2. Deflated Sharpe Ratio   — Bailey & Lopez de Prado (2014) on the pinned R3 NAV.
  3. CSCV / PBO             — Bailey, Borwein, Lopez de Prado, Zhu (2017) over the
                              config-family daily-return matrix (genuine, not per-year proxy).
  4. Stationary bootstrap   — Politis & Romano (1994) vs the circular block bootstrap
                              (bootstrap_nav.py, L=21) already used for the 5th-pct anchor.

Deterministic: fixed seeds. Reproducible: run `python dsr_pbo_annex.py`.
"""
import sys, glob, math
import numpy as np, pandas as pd

DATA = "data"
R3_CSV = f"{DATA}/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap.csv"
ANN = 252.0  # trading days / year used across the registry's Sharpe convention

# ---------- NAV loading (mirror bootstrap_nav.py collapse-to-daily) ----------
def load_nav(path):
    df = pd.read_csv(path, low_memory=False)
    if "combined_nav" not in df.columns:
        return None
    d = df[df["combined_nav"].notna()].copy()
    tc = [c for c in d.columns if c.lower() in ("time", "ymd", "date")]
    if tc:
        t = pd.to_datetime(d[tc[0]], errors="coerce")
        d = d[t.notna()]
        t = t[t.notna()]
        s = d.groupby(t.dt.normalize())["combined_nav"].last().astype(float)
        return s
    return None

def daily_logret(s):
    return np.diff(np.log(s.values))

# ---------- 1. Trial family ----------
def family_paths():
    paths = sorted(glob.glob(f"{DATA}/v23_golive_audit_2014_now_*.csv"))
    keep = []
    for p in paths:
        base = p.split("/")[-1]
        # exclude alternate-NAV and alternate-period cuts (not the same 50B full-history run)
        if any(f"nav{n}" in base for n in
               ("1B","5B","10B","20B","100B","150B","200B","300B","500B")):
            continue
        if "from20" in base:
            continue
        keep.append(p)
    return keep

# ---------- 2. Deflated Sharpe Ratio (BLdP 2014) ----------
def moments(r):
    """Per-observation Sharpe (non-annualized), skew gamma3, kurtosis gamma4 (Pearson, normal=3)."""
    mu = r.mean(); sd = r.std(ddof=1)
    sr = mu / sd
    z = (r - mu)
    sd0 = r.std(ddof=0)
    g3 = np.mean(z**3) / sd0**3
    g4 = np.mean(z**4) / sd0**4
    return sr, g3, g4

def norm_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

def norm_ppf(p):
    # Acklam's rational approximation (adequate for our range)
    a=[-3.969683028665376e+01,2.209460984245205e+02,-2.759285104469687e+02,
       1.383577518672690e+02,-3.066479806614716e+01,2.506628277459239e+00]
    b=[-5.447609879822406e+01,1.615858368580409e+02,-1.556989798598866e+02,
       6.680131188771972e+01,-1.328068155288572e+01]
    c=[-7.784894002430293e-03,-3.223964580411365e-01,-2.400758277161838e+00,
       -2.549732539343734e+00,4.374664141464968e+00,2.938163982698783e+00]
    d=[7.784695709041462e-03,3.224671290700398e-01,2.445134137142996e+00,
       3.754408661907416e+00]
    pl=0.02425
    if p < pl:
        q=math.sqrt(-2*math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5])/((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > 1-pl:
        q=math.sqrt(-2*math.log(1-p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5])/((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q=p-0.5; r=q*q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q/(((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)

def expected_max_sr(var_sr, N):
    """SR_0: expected maximum Sharpe under the null of zero skill across N trials (BLdP)."""
    g = 0.5772156649015329  # Euler-Mascheroni
    e = math.e
    return math.sqrt(var_sr) * ((1-g)*norm_ppf(1 - 1.0/N) + g*norm_ppf(1 - 1.0/(N*e)))

def dsr(sr_hat, sr0, g3, g4, T):
    """Deflated Sharpe Ratio = P(true per-obs SR > sr0)."""
    denom = math.sqrt(max(1e-12, 1 - g3*sr_hat + (g4-1)/4.0*sr_hat**2))
    stat = (sr_hat - sr0) * math.sqrt(T - 1) / denom
    return norm_cdf(stat), stat

# ---------- 3. CSCV / PBO (Bailey et al 2017) ----------
from itertools import combinations
def cscv_pbo(M, S=16):
    """M: (T, Nstrat) matrix of daily returns. Returns PBO + logit distribution.
    Performance metric per block = per-obs Sharpe (mean/std)."""
    T, Ncfg = M.shape
    # trim to a multiple of S, split into S contiguous sub-blocks
    T2 = (T // S) * S
    M = M[:T2]
    blocks = np.array_split(M, S, axis=0)
    def sr_of(mat):
        mu = mat.mean(axis=0); sd = mat.std(axis=0, ddof=1)
        sd = np.where(sd == 0, np.nan, sd)
        return mu / sd
    idx = list(range(S))
    logits = []
    n_is_best_fail = 0
    combos = list(combinations(idx, S//2))
    for cis in combos:
        cis = set(cis)
        cos = [b for b in idx if b not in cis]
        IS = np.vstack([blocks[b] for b in cis])
        OS = np.vstack([blocks[b] for b in cos])
        sris = sr_of(IS); sros = sr_of(OS)
        n_star = int(np.nanargmax(sris))          # best config IS
        # OOS rank of that config (1=worst ... Ncfg=best)
        order = np.argsort(np.argsort(np.nan_to_num(sros, nan=-1e9)))
        rank = order[n_star] + 1
        w = rank / (Ncfg + 1.0)                    # relative rank in (0,1)
        w = min(max(w, 1e-6), 1-1e-6)
        lam = math.log(w/(1-w))
        logits.append(lam)
        if lam < 0:                                # IS-best below OOS median
            n_is_best_fail += 1
    pbo = n_is_best_fail / len(combos)
    return pbo, np.array(logits), len(combos), Ncfg, T2

# ---------- 4. Stationary bootstrap (Politis-Romano) ----------
def cagr_dd_sharpe(logp):
    nav = np.exp(np.cumsum(logp)); peak = np.maximum.accumulate(nav)
    yrs = len(logp)/ANN
    cagr = nav[-1]**(1/yrs) - 1
    dd = (nav/peak - 1).min()
    sh = logp.mean()/logp.std()*math.sqrt(ANN)
    return cagr, dd, sh

def circular_block_boot(r, L=21, B=4000, seed=12345):
    N=len(r); rng=np.random.default_rng(seed); nblk=int(np.ceil(N/L))
    C=np.empty(B); D=np.empty(B)
    for b in range(B):
        st=rng.integers(0,N,nblk)
        p=np.concatenate([np.take(r,np.arange(s0,s0+L),mode="wrap") for s0 in st])[:N]
        c,d,_=cagr_dd_sharpe(p); C[b]=c; D[b]=d
    return C,D

def stationary_boot(r, mean_L=21, B=4000, seed=12345):
    """Politis-Romano: geometric block lengths (p=1/mean_L), circular wrap."""
    N=len(r); rng=np.random.default_rng(seed); p_geom=1.0/mean_L
    C=np.empty(B); D=np.empty(B)
    for b in range(B):
        out=[]
        while len(out)<N:
            start=rng.integers(0,N)
            Lb=rng.geometric(p_geom)
            out.extend(np.take(r,np.arange(start,start+Lb),mode="wrap"))
        p=np.array(out[:N])
        c,d,_=cagr_dd_sharpe(p); C[b]=c; D[b]=d
    return C,D

# ==================== RUN ====================
def main():
    print("="*78)
    print("DSR / PBO ROBUSTNESS ANNEX — computation log")
    print("="*78)

    fam = family_paths()
    # load all family series, keep only full-history (>=2500 daily obs ~10y) at 50B
    series = {}
    for p in fam:
        s = load_nav(p)
        if s is None: continue
        if len(s) < 2500:   # drop short cuts / paper stubs
            continue
        series[p] = s
    print(f"\n[1] TRIAL FAMILY: {len(fam)} candidate CSVs globbed, "
          f"{len(series)} pass full-history (>=2500 daily obs) filter.")

    # align all series to a common date index for the PBO matrix
    common = None
    for s in series.values():
        common = s.index if common is None else common.intersection(s.index)
    common = common.sort_values()
    print(f"    Common aligned trading days across all trials: {len(common)}")

    # R3 pinned
    r3 = load_nav(R3_CSV)
    r3r = daily_logret(r3)
    T = len(r3r)
    sr_hat, g3, g4 = moments(r3r)
    sr_ann = sr_hat*math.sqrt(ANN)
    print(f"\n[2] R3 PINNED ({R3_CSV.split('/')[-1]})")
    print(f"    daily obs T = {T}  ({T/ANN:.1f}y)")
    print(f"    per-day Sharpe = {sr_hat:.5f}  -> annualized = {sr_ann:.3f}")
    print(f"    skewness  gamma3 = {g3:.4f}")
    print(f"    kurtosis  gamma4 = {g4:.4f}  (excess = {g4-3:.4f})")

    # variance of Sharpe across trials (per-day, annualize for display)
    srs = []
    for p,s in series.items():
        rr = daily_logret(s)
        mu=rr.mean(); sd=rr.std(ddof=1)
        srs.append(mu/sd)
    srs=np.array(srs)
    var_sr = srs.var(ddof=1)
    print(f"\n    Trial Sharpe dispersion (per-day, N_csv={len(srs)}):")
    print(f"      mean ann-SR = {srs.mean()*math.sqrt(ANN):.3f}, "
          f"sd ann-SR = {srs.std(ddof=1)*math.sqrt(ANN):.3f}, "
          f"Var(per-day SR) = {var_sr:.3e}")

    # DSR under two N: empirical CSV count and a larger registry-documented count
    for label, N in [("N_csv (surviving daily CSVs)", len(srs)),
                     ("N_reg=120 (registry-documented search)", 120),
                     ("N_reg=200 (conservative upper)", 200)]:
        sr0 = expected_max_sr(var_sr, N)
        p_dsr, stat = dsr(sr_hat, sr0, g3, g4, T)
        flag = "  <<< RED FLAG (DSR<0.95)" if p_dsr < 0.95 else ""
        print(f"    DSR @ {label:42s}: SR0(ann)={sr0*math.sqrt(ANN):.3f}  "
              f"DSR={p_dsr:.4f}{flag}")

    # PBO
    print("\n[3] CSCV / PBO")
    M = np.column_stack([daily_logret(series[p].reindex(common)) for p in series])
    # reindex loses one row via diff; recompute on aligned levels
    lvl = np.column_stack([series[p].reindex(common).values for p in series])
    Mret = np.diff(np.log(lvl), axis=0)
    pbo, logits, ncomb, ncfg, T2 = cscv_pbo(Mret, S=16)
    print(f"    matrix: {Mret.shape[0]} daily obs x {ncfg} configs; S=16 blocks, "
          f"{ncomb} IS/OOS combinations")
    print(f"    PBO = {pbo:.4f}  (fraction of splits where IS-best config lands "
          f"below OOS median)")
    print(f"    logit lambda: median={np.median(logits):.2f}, "
          f"mean={logits.mean():.2f}, P(lambda<0)={ (logits<0).mean():.4f}")

    # Bootstrap comparison on R3
    print("\n[4] BOOTSTRAP: circular block (L=21) vs stationary (mean L=21)")
    Cb,Db = circular_block_boot(r3r, L=21, B=4000, seed=12345)
    Cs,Ds = stationary_boot(r3r, mean_L=21, B=4000, seed=12345)
    def line(tag,C,D):
        print(f"    {tag:18s} CAGR 5th={np.percentile(C,5)*100:5.1f}%  "
              f"med={np.percentile(C,50)*100:5.1f}%  | "
              f"MaxDD 5th={np.percentile(D,5)*100:6.1f}%  "
              f"med={np.percentile(D,50)*100:6.1f}%  | "
              f"P(DD<-30%)={ (D<-0.30).mean()*100:4.1f}%")
    line("circular block", Cb, Db)
    line("stationary(PR)", Cs, Ds)

    print("\n"+"="*78)
    print("DONE. Numbers above feed the registry annex section.")
    print("="*78)

if __name__ == "__main__":
    main()
