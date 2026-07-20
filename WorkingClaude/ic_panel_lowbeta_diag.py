#!/usr/bin/env python3
"""ic_panel_lowbeta_diag.py — job Taylor_20260720_121019, CHAN DOAN (khong phai tim cau hinh dep).

4 cau hoi bat buoc phai tra loi TRUOC khi ket luan, sinh ra tu ket qua vong 1:

D1. beta_adj median 0.568 (=> beta_raw ~0.36) qua THAP so voi ky vong ~1.0.
    Loi tinh, hay la hieu ung non-synchronous trading cua duoi illiquid? Kiem tra beta
    theo nhom thanh khoan: neu top-60 co beta ~0.9-1.0 thi calc DUNG, muc thap toan cuc
    la do duoi illiquid (Scholes-Williams bias) — dieu nay TU NO da la canh bao cho BAB.

D2. Cache chi co gia tu 2013-01 => 8 quy dau panel (2014-2015) khong du 260 tuan va bi
    LOAI. IS that su = 2016-2019 chu khong phai 2014-2019. Do lon anh huong.

D3. F4 idio-vol: IC duong (rank) NHUNG fwd_mean Q5 (2.60) < Q1 (3.86). Phan ky mean-vs-rank.
    Kiem tra: idio-vol thap co that su cho lai cao hon khong, hay chi la "it duoi trai"?

D4. TRUNG LAP — cau hoi quyet dinh cho F4:
    (a) risk_rating.Dev la bin DO LECH (volatility) — 8L/Risk_Rating da an phan nay chua?
    (b) idio-vol noi tieng la proxy cua SIZE/THANH KHOAN. Trong pool THAT cua ta (custom30V
        chon tu top thanh khoan) lieu edge co con? Test IC RIENG trong top-100 turnover.

Usage: source ./wc_env.sh && BQ_CACHE_THREADS=1 $DNA_PYEXE ic_panel_lowbeta_diag.py
"""
import warnings; warnings.filterwarnings("ignore")
import os, importlib.util
import numpy as np, pandas as pd, duckdb
from scipy import stats

WORKDIR = os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude")
spec = importlib.util.spec_from_file_location("ic8l", os.path.join(WORKDIR, "ic_panel_8l.py"))
ic8l = importlib.util.module_from_spec(spec); spec.loader.exec_module(ic8l)
load, summ = ic8l.load, ic8l.summ
TARGET, CRASH, N_MIN, _rank = ic8l.TARGET, ic8l.CRASH, ic8l.N_MIN, ic8l._rank

CACHE = os.path.join(WORKDIR, "data", "bq_cache")
CONTROLS_VALUE = ["ey", "cfy", "ps", "neg_pbz"]
CONTROLS_FULL  = CONTROLS_VALUE + ["neg_rating"]


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
        b, *_ = np.linalg.lstsq(Xr, xr, rcond=None)
        ic = np.corrcoef(xr - Xr @ b, _rank(y[ok]))[0, 1]
        if np.isfinite(ic):
            ics.append(ic); qs.append(q)
    return np.array(ics), qs


def rep(lab, ics, qs):
    IS  = np.array([ics[i] for i, q in enumerate(qs) if q.year <= 2019])
    OOS = np.array([ics[i] for i, q in enumerate(qs) if q.year >= 2020])
    a, b, c = summ(ics), summ(IS), summ(OOS)
    print(f"  {lab:34s} ALL ic={a['ic']:+.4f} t={a['t']:+.2f} n={a['n']:3d} | "
          f"IS ic={b['ic']:+.4f} n={b['n']:2d} | OOS ic={c['ic']:+.4f} t={c['t']:+.2f} n={c['n']:2d}", flush=True)


def main():
    d = load()
    bp = pd.read_csv(os.path.join(WORKDIR, "data", "beta_panel_continuous.csv"))
    bp["q"] = pd.PeriodIndex(bp["q"], freq="Q")
    d = d.merge(bp[["ticker", "q", "beta_raw", "beta_adj", "neg_beta", "idiovol", "neg_idiovol"]],
                on=["ticker", "q"], how="left")
    d["liq_rank"] = d.groupby("q")["turnover"].rank(ascending=False, method="first")
    gate = (d["rating"] <= 3)

    # ---------------- D1: beta theo nhom thanh khoan ----------------
    print("=" * 74)
    print("D1. beta_raw theo nhom thanh khoan (kiem tra calc dung hay bias illiquid)")
    print("=" * 74)
    for lo, hi, lab in [(1, 30, "top-30"), (1, 60, "top-60"), (61, 150, "61-150"),
                        (151, 400, "151-400"), (401, 99999, "401+")]:
        s = d[(d["liq_rank"] >= lo) & (d["liq_rank"] <= hi) & d["beta_raw"].notna()]
        if len(s) < 50: continue
        print(f"  {lab:9s} n={len(s):6,}  beta_raw med={s.beta_raw.median():.3f} "
              f"mean={s.beta_raw.mean():.3f}  idiovol med={s.idiovol.median():.4f}", flush=True)
    print("  => Neu top-30/60 co beta ~0.9-1.0 thi CALC DUNG; muc thap toan cuc = duoi illiquid.")

    # ---------------- D2: quy nao bi mat ----------------
    print("\n" + "=" * 74)
    print("D2. Do phu theo quy (cache gia chi tu 2013-01 => quy dau thieu 260 tuan)")
    print("=" * 74)
    cov = d.groupby("q").agg(n=("ticker", "size"), have_beta=("beta_adj", lambda s: s.notna().sum()))
    cov["pct"] = 100.0 * cov["have_beta"] / cov["n"]
    print("  " + cov.head(12).to_string().replace("\n", "\n  "), flush=True)
    print(f"  ... IS that su = {sorted({q.year for q in d[d.beta_adj.notna()].q})[:6]}")

    # ---------------- D3: mean vs rank cho idio-vol ----------------
    print("\n" + "=" * 74)
    print("D3. F4 idio-vol: phan ky mean-vs-rank (IC duong nhung Q5 mean < Q1 mean?)")
    print("=" * 74)
    g = d[gate & d["neg_idiovol"].notna() & d[TARGET].notna()].copy()
    g["Q"] = g.groupby("q")["neg_idiovol"].transform(
        lambda s: pd.qcut(s.rank(method="first"), 5, labels=[1, 2, 3, 4, 5]) if s.notna().sum() >= 25 else np.nan)
    rows = []
    for q in [1, 2, 3, 4, 5]:
        s = g[g["Q"] == q]
        rows.append(dict(Q=q, n=len(s), idiovol_med=s.idiovol.median(),
                         fwd_mean=s[TARGET].mean(), fwd_med=s[TARGET].median(),
                         fwd_p25=s[TARGET].quantile(.25), fwd_p75=s[TARGET].quantile(.75),
                         crash_pct=100.0 * (s[TARGET] < CRASH).mean(),
                         moon_pct=100.0 * (s[TARGET] > 30).mean()))
    qt = pd.DataFrame(rows)
    print("  (Q ngu phan vi TRONG TUNG QUY; Q5 = idio-vol THAP nhat)")
    print("  " + qt.to_string(index=False).replace("\n", "\n  "), flush=True)
    print("  => Neu crash% giam don dieu nhung fwd_mean khong tang: LANG KINH RUI RO, khong phai return-factor.")

    # ---------------- D4: trung lap ----------------
    print("\n" + "=" * 74)
    print("D4. TRUNG LAP — cau hoi quyet dinh cho F4")
    print("=" * 74)
    con = duckdb.connect()
    rr = con.execute(f"""SELECT DISTINCT ticker, quarter, Beta, Dev, Risk_Rating
                         FROM read_parquet('{CACHE}/risk_rating.parquet') WHERE Dev IS NOT NULL""").df()
    rr["q"] = pd.PeriodIndex(rr["quarter"], freq="Q")
    d = d.merge(rr[["ticker", "q", "Dev", "Risk_Rating"]], on=["ticker", "q"], how="left")
    d["neg_dev"] = -pd.to_numeric(d["Dev"], errors="coerce")
    d["neg_rr"]  = -pd.to_numeric(d["Risk_Rating"], errors="coerce")
    d["neg_liqrank"] = -d["liq_rank"]     # thanh khoan cao = diem cao

    ch = d[d.idiovol.notna() & d.Dev.notna()]
    print(f"  (a) corr(idio-vol, Dev bin) spearman={stats.spearmanr(ch.idiovol, ch.Dev)[0]:+.3f} (n={len(ch):,})")
    ch2 = d[d.idiovol.notna() & d.liq_rank.notna()]
    print(f"      corr(idio-vol, liq_rank) spearman={stats.spearmanr(ch2.idiovol, ch2.liq_rank)[0]:+.3f} "
          f"(duong = it thanh khoan thi idio-vol cao)")
    ch3 = d[d.idiovol.notna() & d.beta_adj.notna()]
    print(f"      corr(idio-vol, beta_adj) spearman={stats.spearmanr(ch3.idiovol, ch3.beta_adj)[0]:+.3f}")

    print("\n  (b) IC bien cua neg_idiovol khi THEM tung control (gate rating<=3):")
    for lab, ctrl in [("vs value+rating (goc)", CONTROLS_FULL),
                      ("  + neg_dev (Dev bin)", CONTROLS_FULL + ["neg_dev"]),
                      ("  + neg_liqrank", CONTROLS_FULL + ["neg_liqrank"]),
                      ("  + neg_beta", CONTROLS_FULL + ["neg_beta"]),
                      ("  + dev+liq+beta (het)", CONTROLS_FULL + ["neg_dev", "neg_liqrank", "neg_beta"])]:
        ics, qs = marginal_ic(d, "neg_idiovol", TARGET, ctrl, mask=gate)
        rep(lab, ics, qs)

    print("\n  (c) IC RIENG trong pool thanh khoan that (universe ta thuc su giao dich):")
    for lo, hi, lab in [(1, 60, "top-60 turnover"), (1, 100, "top-100"), (1, 200, "top-200")]:
        m = gate & (d["liq_rank"] >= lo) & (d["liq_rank"] <= hi)
        for tag, ctrl in [("L0 raw", None), ("L2 value+rating", CONTROLS_FULL)]:
            if ctrl is None:
                ics, qs = [], []
                for q, gg in d[m].groupby("q"):
                    x = pd.to_numeric(gg["neg_idiovol"], errors="coerce")
                    y = pd.to_numeric(gg[TARGET], errors="coerce")
                    ok = x.notna() & y.notna()
                    if ok.sum() < N_MIN: continue
                    ic = np.corrcoef(_rank(x[ok]), _rank(y[ok]))[0, 1]
                    if np.isfinite(ic): ics.append(ic); qs.append(q)
                ics = np.array(ics)
            else:
                ics, qs = marginal_ic(d, "neg_idiovol", TARGET, ctrl, mask=m)
            rep(f"{lab:16s} {tag}", ics, qs)

    print("\n  (d) F3 low-beta trong pool thanh khoan (kiem tra lai candidate chinh):")
    for lo, hi, lab in [(1, 60, "top-60 turnover"), (1, 100, "top-100")]:
        m = gate & (d["liq_rank"] >= lo) & (d["liq_rank"] <= hi)
        ics, qs = marginal_ic(d, "neg_beta", TARGET, CONTROLS_FULL, mask=m)
        rep(f"{lab:16s} L2 value+rating", ics, qs)

    d[["ticker", "q", "beta_adj", "idiovol", "Dev", "liq_rank", TARGET]].to_csv(
        os.path.join(WORKDIR, "data", "ic_panel_lowbeta_diag.csv"), index=False)
    print("\nsaved -> data/ic_panel_lowbeta_diag.csv")


if __name__ == "__main__":
    main()
