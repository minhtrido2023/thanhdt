#!/usr/bin/env python3
"""ic_panel_lowbeta_q3.py — job Taylor_20260720_121019.

Candidate #4 (low-beta / BAB, Frazzini-Pedersen 2014) tu factor_gap_audit_20260718.md.
Rider tuy chon: candidate #15 (idiosyncratic volatility, Ang et al. 2006) — tinh gan nhu
mien phi tu CUNG hoi quy beta (residual std), nen chay luon theo ghi chu audit doc.

MULTIPLE-TESTING DISCIPLINE (khai bao TRUOC khi chay, kb/context_pack.md §Quy chuan 5):
  N trials = 2  (F3 low-beta = candidate chinh; F4 idio-vol = rider da pre-register trong
  audit doc "gop cung vong nghien cuu voi #4"). KHONG sweep cua so (chi 260 tuan), KHONG
  sweep tham so Blume (chi 0.67b+0.33), KHONG thu bien the daily/monthly roi chon cai dep.
  Khung tinh beta da duoc CHOT TU TRUOC boi job Taylor_20260720_111429 (weekly 5Y thang
  8/8 quy khi reverse-engineer risk_rating.Beta) — day khong phai lua chon post-hoc.

INPUT: beta LIEN TUC tu tinh. KHONG dung field bin `risk_rating.Beta` lam input
(job Taylor_20260720_111429: no la SO NGUYEN 1..5, khong du phan giai de rank/shrink).
Field bin chi dung lam CROSS-CHECK do khop.

TEST QUYET DINH (theo canh bao §4 audit doc + bai hoc accruals bi 1/PCF nuot):
  L0 raw IC | L1 marginal vs value {ey,cfy,ps,neg_pbz} | L2 marginal vs value+neg_rating.
  Beta thap thuong tuong quan voi co phieu phong thu / dinh gia CAO hon => L2 la gate that.
Walk-forward IS(2014-19)/OOS(2020+), per-year LOO.

KHONG WIRE PRODUCTION du ket qua the nao — vong tham do.
Usage: source ./wc_env.sh && BQ_CACHE_THREADS=1 $DNA_PYEXE ic_panel_lowbeta_q3.py
"""
import warnings; warnings.filterwarnings("ignore")
import os, importlib.util
import numpy as np, pandas as pd, duckdb
from scipy import stats

WORKDIR = os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude")
spec = importlib.util.spec_from_file_location("ic8l", os.path.join(WORKDIR, "ic_panel_8l.py"))
ic8l = importlib.util.module_from_spec(spec); spec.loader.exec_module(ic8l)
bq, load, summ, ic_series = ic8l.bq, ic8l.load, ic8l.summ, ic8l.ic_series
TARGET, CRASH, N_MIN, _rank = ic8l.TARGET, ic8l.CRASH, ic8l.N_MIN, ic8l._rank

CACHE = os.path.join(WORKDIR, "data", "bq_cache")
CONTROLS_VALUE = ["ey", "cfy", "ps", "neg_pbz"]
CONTROLS_FULL  = CONTROLS_VALUE + ["neg_rating"]

WIN_WEEKS = 260          # Value Line 5Y weekly — CHOT truoc tu job Taylor_20260720_111429
MIN_WEEKS = 156          # 60% cua cua so, cung nguong voi beta_reverse_engineer.py
BLUME_A, BLUME_B = 0.67, 0.33

FACTORS = [  # (tag, col, ky vong dau IC)
    ("F3_low_beta",  "neg_beta",    "pos"),   # BAB: beta THAP -> lai cao hon => -beta co IC duong
    ("F4_neg_idiovol", "neg_idiovol", "pos"), # Ang: idio-vol THAP -> lai cao hon
]


# ---------------- beta panel lien tuc ----------------
def weekly_returns():
    """Ma tran return TUAN (W-FRI) tu bq cache. Tu 2008 de co du 260 tuan truoc quy 2014Q1."""
    con = duckdb.connect()
    px = con.execute(f"""
        SELECT time, ticker, Close, VNINDEX
        FROM read_parquet('{CACHE}/ticker/*.parquet')
        WHERE Close IS NOT NULL AND VNINDEX IS NOT NULL AND CAST(time AS DATE) >= DATE '2008-01-01'
    """).df()
    px["time"] = pd.to_datetime(px["time"])
    wide = px.pivot_table(index="time", columns="ticker", values="Close", aggfunc="last").sort_index()
    mkt = px.drop_duplicates("time").set_index("time")["VNINDEX"].sort_index()
    wk  = wide.resample("W-FRI").last()
    mw  = mkt.resample("W-FRI").last()
    R = wk.pct_change().replace([np.inf, -np.inf], np.nan)
    m = mw.pct_change().replace([np.inf, -np.inf], np.nan)
    return R, m


def beta_at(R, m, asof):
    """Beta + idio-vol cho moi ticker tai asof, dung 260 tuan gan nhat <= asof (causal).

    Vectorized OLS mot bien: beta = cov(r,m)/var(m); idio = std(r - a - b*m).
    NaN xu ly theo tung cot (pairwise) — moi ticker dung dung so tuan no co du lieu.
    """
    idx = R.index[R.index <= asof]
    if len(idx) < MIN_WEEKS:
        return pd.DataFrame(columns=["beta_raw", "idiovol", "nobs"])
    win = idx[-WIN_WEEKS:]
    Rw = R.loc[win]
    mw = m.loc[win]
    ok_m = mw.notna()
    Rw, mw = Rw[ok_m], mw[ok_m]

    M = Rw.notna().values                       # mask quan sat hop le (T x N)
    n = M.sum(axis=0).astype(float)             # so tuan moi ticker
    X = np.where(M, Rw.values, 0.0)
    mv = mw.values[:, None]
    mvm = np.where(M, mv, 0.0)

    sum_x  = X.sum(axis=0)
    sum_m  = mvm.sum(axis=0)
    sum_xm = (X * mvm).sum(axis=0)
    sum_mm = (mvm * mvm).sum(axis=0)
    sum_xx = (X * X).sum(axis=0)

    with np.errstate(invalid="ignore", divide="ignore"):
        mean_x, mean_m = sum_x / n, sum_m / n
        cov = sum_xm / n - mean_x * mean_m
        var_m = sum_mm / n - mean_m ** 2
        beta = np.where(var_m > 0, cov / var_m, np.nan)
        var_x = sum_xx / n - mean_x ** 2
        # var(resid) = var(x) - beta^2 * var(m)   (OLS mot bien, co he so chan)
        var_e = var_x - (beta ** 2) * var_m
        idio = np.sqrt(np.clip(var_e, 0, None))

    out = pd.DataFrame({"beta_raw": beta, "idiovol": idio, "nobs": n}, index=Rw.columns)
    return out[out["nobs"] >= MIN_WEEKS].dropna(subset=["beta_raw"])


def build_beta_panel(quarters):
    R, m = weekly_returns()
    print(f"weekly panel: {R.shape[0]} tuan x {R.shape[1]} ticker "
          f"({R.index.min().date()} -> {R.index.max().date()})", flush=True)
    frames = []
    for q in quarters:
        asof = q.end_time.normalize()
        b = beta_at(R, m, asof)
        if b.empty:
            continue
        b = b.reset_index().rename(columns={"index": "ticker"})
        b["q"] = q
        frames.append(b)
    bp = pd.concat(frames, ignore_index=True)
    # Blume shrink ve 1 (chuan BAB: beta tho nhieu, phai shrink truoc khi rank)
    bp["beta_adj"] = BLUME_A * bp["beta_raw"] + BLUME_B
    bp["neg_beta"] = -bp["beta_adj"]
    bp["neg_idiovol"] = -bp["idiovol"]
    return bp


# ---------------- marginal IC ----------------
def marginal_ic(d, lens, target, controls, mask=None):
    sub = d if mask is None else d[mask]
    others = [c for c in controls if c != lens]
    ics, qs = [], []
    for q, g in sub.groupby("q"):
        y = pd.to_numeric(g[target], errors="coerce")
        x = pd.to_numeric(g[lens], errors="coerce")
        X = g[others].apply(pd.to_numeric, errors="coerce")
        ok = x.notna() & y.notna() & X.notna().all(axis=1)
        if ok.sum() < N_MIN:
            continue
        xr = _rank(x[ok]).values
        Xr = np.column_stack([np.ones(int(ok.sum()))] + [_rank(X[c][ok]).values for c in others])
        beta, *_ = np.linalg.lstsq(Xr, xr, rcond=None)
        ic = np.corrcoef(xr - Xr @ beta, _rank(y[ok]))[0, 1]
        if np.isfinite(ic):
            ics.append(ic); qs.append(q)
    return np.array(ics), qs


def quintile_table(d, lens, mask):
    g = d[mask & d[lens].notna() & d[TARGET].notna()].copy()
    if len(g) < 100:
        return None
    g["Q"] = pd.qcut(g[lens].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    rows = []
    for q in [1, 2, 3, 4, 5]:
        s = g[g["Q"] == q]
        rows.append(dict(Q=q, n=len(s), lens_mean=s[lens].mean(),
                         fwd_mean=s[TARGET].mean(), fwd_med=s[TARGET].median(),
                         crash_pct=100.0 * (s[TARGET] < CRASH).mean()))
    return pd.DataFrame(rows)


def split(ics, qs, lo=None, hi=None):
    sel = [i for i, q in enumerate(qs)
           if (lo is None or q.year >= lo) and (hi is None or q.year <= hi)]
    return np.array([ics[i] for i in sel])


def main():
    print("=== Loading 8L value panel ===", flush=True)
    d = load()
    quarters = sorted(d["q"].unique())
    print(f"panel: {len(d):,} obs, {len(quarters)} quy, {d.ticker.nunique()} ticker", flush=True)

    print("\n=== Building continuous beta panel (weekly 260w, Blume-adjusted) ===", flush=True)
    bp = build_beta_panel(quarters)
    print(f"beta panel: {len(bp):,} obs, {bp.ticker.nunique()} ticker, {bp.q.nunique()} quy", flush=True)
    print(f"beta_adj: mean={bp.beta_adj.mean():.3f} med={bp.beta_adj.median():.3f} "
          f"p5={bp.beta_adj.quantile(.05):.3f} p95={bp.beta_adj.quantile(.95):.3f}", flush=True)
    print(f"idiovol (weekly): med={bp.idiovol.median():.4f} "
          f"p5={bp.idiovol.quantile(.05):.4f} p95={bp.idiovol.quantile(.95):.4f}", flush=True)

    d = d.merge(bp[["ticker", "q", "beta_raw", "beta_adj", "neg_beta", "idiovol", "neg_idiovol", "nobs"]],
                on=["ticker", "q"], how="left")

    # ---- SANITY 1: cross-check voi field bin risk_rating.Beta (khong dung lam input) ----
    con = duckdb.connect()
    rr = con.execute(f"""SELECT DISTINCT ticker, quarter, Beta FROM read_parquet('{CACHE}/risk_rating.parquet')
                         WHERE Beta IS NOT NULL""").df()
    rr["q"] = pd.PeriodIndex(rr["quarter"], freq="Q")
    chk = d.merge(rr[["ticker", "q", "Beta"]], on=["ticker", "q"], how="inner").dropna(subset=["beta_adj", "Beta"])
    if len(chk) > 100:
        rho = stats.spearmanr(chk["beta_adj"], chk["Beta"])[0]
        print(f"\n[SANITY 1] beta tu tinh vs field bin risk_rating.Beta: "
              f"spearman={rho:+.3f} (n={len(chk):,}) — ky vong ~+0.8 theo job truoc", flush=True)

    # ---- SANITY 2: do phu tren pool thanh khoan that ----
    print("\n[SANITY 2] Do phu beta theo nhom thanh khoan (turnover trong tung quy):", flush=True)
    dd = d[d["turnover"].notna()].copy()
    dd["liq_rank"] = dd.groupby("q")["turnover"].rank(ascending=False, method="first")
    for lo, hi, lab in [(1, 60, "top-60"), (1, 100, "top-100"), (1, 300, "top-300")]:
        s = dd[(dd["liq_rank"] >= lo) & (dd["liq_rank"] <= hi)]
        print(f"   {lab:8s} n={len(s):6,}  co beta = {100.0*s['beta_adj'].notna().mean():5.1f}%", flush=True)

    gate = (d["rating"] <= 3)
    print(f"\ngate rating<=3: {int(gate.sum()):,} obs. "
          f"coverage beta={d.loc[gate,'beta_adj'].notna().mean():.2f} "
          f"idiovol={d.loc[gate,'neg_idiovol'].notna().mean():.2f}", flush=True)

    # ---- 3 tang IC ----
    rows = []
    for tag, col, exp in FACTORS:
        print(f"\n{'='*70}\n{tag}  ({col}, ky vong IC {exp})\n{'='*70}", flush=True)
        for lab, ctrl in [("L0_raw", None), ("L1_vs_value", CONTROLS_VALUE), ("L2_vs_value_rating", CONTROLS_FULL)]:
            if ctrl is None:
                ics, qs = [], []
                for q, g in d[gate].groupby("q"):
                    x = pd.to_numeric(g[col], errors="coerce"); y = pd.to_numeric(g[TARGET], errors="coerce")
                    ok = x.notna() & y.notna()
                    if ok.sum() < N_MIN: continue
                    ic = np.corrcoef(_rank(x[ok]), _rank(y[ok]))[0, 1]
                    if np.isfinite(ic): ics.append(ic); qs.append(q)
                ics = np.array(ics)
            else:
                ics, qs = marginal_ic(d, col, TARGET, ctrl, mask=gate)
            IS  = split(ics, qs, hi=2019)
            OOS = split(ics, qs, lo=2020)
            a, b, c = summ(ics), summ(IS), summ(OOS)
            print(f"  {lab:20s} ALL ic={a['ic']:+.4f} t={a['t']:+.2f} hit={a['hit']:.2f} n={a['n']:3d} | "
                  f"IS ic={b['ic']:+.4f} n={b['n']:2d} | OOS ic={c['ic']:+.4f} t={c['t']:+.2f} n={c['n']:2d}",
                  flush=True)
            rows.append(dict(factor=tag, layer=lab, ic_all=a["ic"], t_all=a["t"], hit_all=a["hit"],
                             n_all=a["n"], ic_is=b["ic"], ic_oos=c["ic"], t_oos=c["t"], n_oos=c["n"]))

        qt = quintile_table(d, col, gate)
        if qt is not None:
            print(f"\n  Ngu phan vi theo {col} (Q1=thap nhat ... Q5=cao nhat):")
            print("  " + qt.to_string(index=False).replace("\n", "\n  "), flush=True)

        # per-year LOO tren L2
        ics, qs = marginal_ic(d, col, TARGET, CONTROLS_FULL, mask=gate)
        yrs = sorted({q.year for q in qs})
        loo = []
        for y in yrs:
            keep = np.array([ics[i] for i, q in enumerate(qs) if q.year != y])
            loo.append(dict(factor=tag, drop_year=y, ic_ex_year=float(np.mean(keep)),
                            ic_that_year=float(np.mean([ics[i] for i, q in enumerate(qs) if q.year == y]))))
        lo_df = pd.DataFrame(loo)
        print(f"\n  LOO per-year (L2 marginal IC): full={np.mean(ics):+.4f}")
        print("  " + lo_df.to_string(index=False).replace("\n", "\n  "), flush=True)
        lo_df.to_csv(os.path.join(WORKDIR, "data", f"ic_panel_lowbeta_loo_{tag}.csv"), index=False)

    res = pd.DataFrame(rows)
    out = os.path.join(WORKDIR, "data", "ic_panel_lowbeta_q3.csv")
    res.to_csv(out, index=False)
    bp.to_csv(os.path.join(WORKDIR, "data", "beta_panel_continuous.csv"), index=False)
    print(f"\nsaved -> {out}", flush=True)
    print("\n=== TOM TAT ===")
    print(res.to_string(index=False))


if __name__ == "__main__":
    main()
