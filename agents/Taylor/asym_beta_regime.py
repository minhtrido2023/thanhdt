#!/usr/bin/env python3
"""asym_beta_regime.py — job Taylor_20260721_112050, Viec 3 (THAM DO).

Gia thuyet user: co phieu thien huong dau co (beta cao / bien dong cao / turnover cao)
GIAM MANH HON ty le khi thi truong xau so voi muc TANG tuong ung khi thi truong tot
=> beta KHONG doi xung qua regime, khong phai hang so nhu CAPM gia dinh.

Thiet ke:
  - Nhan regime: `tav2_bq.vnindex_5state_dt5g_live` (BANG PRODUCTION DUNG — KHONG dung
    bare `vnindex_5state`, do la base v3.4b, bay du lieu da biet, xem data_registry.md).
    state 1=CRISIS 2=BEAR 3=NEUTRAL 4=BULL 5=EXBULL.
    DOWN={1,2}  NEUTRAL={3}  UP={4,5}
  - Voi moi ticker: 1 hoi quy GOP co dummy regime (ca he so chan LAN do doc):
        r_i = a_D*1D + a_N*1N + a_U*1U + b_D*(1D*m) + b_N*(1N*m) + b_U*(1U*m) + e
    => beta rieng tung regime, do lech asym = b_D - b_U co sai so chuan tinh tu ma tran
    hiep phuong sai cua CHINH hoi quy do (khong ghep 2 hoi quy roi tru bang tay).
  - Lens doi chieu (kinh dien Ang-Chen-Xing 2006): downside beta theo DAU return thi
    truong (tuan m<0 vs m>0), KHONG dung nhan regime. Neu 2 lens cung huong => tin hon.
  - Tuong quan asym voi cac proxy "dau co": beta tong, idio-vol, turnover, mcap, ADV.

Usage: source ./wc_env.sh && $DNA_PYEXE mike/agents/Taylor/asym_beta_regime.py
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, duckdb
from scipy import stats as st

CACHE = "data/bq_cache"
OUT = "mike/agents/Taylor/research/data_asym_beta.csv"
START = "2014-01-01"
MIN_D, MIN_U, MIN_N = 40, 40, 60      # so tuan toi thieu moi regime


def con():
    c = duckdb.connect(); c.execute("SET threads=1"); return c


def load():
    px = con().execute(f"""
        SELECT CAST(time AS DATE) AS d, ticker, Close, VNINDEX
        FROM read_parquet('{CACHE}/ticker/*.parquet')
        WHERE Close > 0 AND VNINDEX IS NOT NULL AND CAST(time AS DATE) >= DATE '{START}'
    """).df()
    px["d"] = pd.to_datetime(px["d"])
    stt = con().execute(f"""
        SELECT CAST(time AS DATE) AS d, state
        FROM read_parquet('{CACHE}/vnindex_5state_dt5g_live.parquet')
        WHERE CAST(time AS DATE) >= DATE '{START}'
    """).df()
    stt["d"] = pd.to_datetime(stt["d"])
    meta = con().execute(f"""
        WITH r AS (SELECT ticker, time, Close, OShares, Trading_Value_1M_P50 AS adv,
                          ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY time DESC) rn
                   FROM read_parquet('{CACHE}/ticker_prune/*.parquet') WHERE Close>0 AND OShares>0)
        SELECT ticker, Close*OShares AS mcap, adv FROM r WHERE rn=1
    """).df()
    return px, stt, meta


def ols(X, y):
    """Tra ve (beta_hat, cov_hat, r2). X da co cot hang so neu can."""
    XtX_inv = np.linalg.pinv(X.T @ X)
    b = XtX_inv @ X.T @ y
    e = y - X @ b
    dof = len(y) - X.shape[1]
    s2 = (e @ e) / dof
    return b, s2 * XtX_inv, 1 - (e @ e) / ((y - y.mean()) ** 2).sum()


def main():
    px, stt, meta = load()

    # ---- weekly panel + nhan regime theo tuan (state phien cuoi tuan) ----
    wide = px.pivot_table(index="d", columns="ticker", values="Close", aggfunc="last")
    mkt = px.drop_duplicates("d").set_index("d")["VNINDEX"].sort_index()
    Rw = wide.resample("W-FRI").last().pct_change()
    mw = mkt.resample("W-FRI").last().pct_change()
    sw = stt.set_index("d")["state"].sort_index().resample("W-FRI").last()
    Rw, mw = Rw.align(mw, axis=0, join="inner")
    sw = sw.reindex(Rw.index).ffill()
    grp = pd.Series(np.where(sw.isin([1, 2]), "D", np.where(sw.isin([4, 5]), "U", "N")),
                    index=Rw.index).where(sw.notna())
    ok = mw.notna() & grp.notna()
    Rw, mw, grp = Rw[ok], mw[ok], grp[ok]
    print(f"[regime] tuan: D={int((grp=='D').sum())} N={int((grp=='N').sum())} U={int((grp=='U').sum())} "
          f"({Rw.index.min():%Y-%m} -> {Rw.index.max():%Y-%m})")
    print(f"[regime] market return TB/tuan: " + "  ".join(
        f"{g}={mw[grp==g].mean()*100:+.2f}%" for g in "DNU"))

    D, N, U = (grp == "D").values, (grp == "N").values, (grp == "U").values
    m = mw.values
    rows = []
    for tk in Rw.columns:
        y_all = Rw[tk].values
        v = ~np.isnan(y_all)
        if v.sum() < MIN_D + MIN_U + MIN_N:
            continue
        d, n, u = D & v, N & v, U & v
        if d.sum() < MIN_D or u.sum() < MIN_U or n.sum() < MIN_N:
            continue
        y = y_all[v]
        Xf = np.column_stack([d[v], n[v], u[v], d[v] * m[v], n[v] * m[v], u[v] * m[v]]).astype(float)
        b, cov, r2 = ols(Xf, y)
        bD, bN, bU = b[3], b[4], b[5]
        var_diff = cov[3, 3] + cov[5, 5] - 2 * cov[3, 5]
        se = np.sqrt(var_diff) if var_diff > 0 else np.nan
        # beta tong + idio vol (de lam proxy dau co)
        Xs = np.column_stack([np.ones(v.sum()), m[v]])
        bs, _, _ = ols(Xs, y)
        resid = y - Xs @ bs
        rows.append(dict(ticker=tk, beta_all=bs[1], idio_vol=resid.std() * np.sqrt(52),
                         beta_D=bD, beta_N=bN, beta_U=bU,
                         asym=bD - bU, se_asym=se, t_asym=(bD - bU) / se if se and se > 0 else np.nan,
                         r2=r2, nD=int(d.sum()), nN=int(n.sum()), nU=int(u.sum())))
    df = pd.DataFrame(rows).merge(meta, on="ticker", how="left")
    df["turnover"] = df["adv"] / df["mcap"]
    import os; os.makedirs(os.path.dirname(OUT), exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"[panel] {len(df)} ma du dieu kien -> {OUT}")

    print("\n" + "=" * 78)
    print("KET QUA 1 — beta trung binh theo regime (toan bo ma du dieu kien)")
    print("=" * 78)
    print(f"  beta_DOWN (CRISIS+BEAR) : {df.beta_D.mean():.3f}  (median {df.beta_D.median():.3f})")
    print(f"  beta_NEUTRAL (baseline) : {df.beta_N.mean():.3f}  (median {df.beta_N.median():.3f})")
    print(f"  beta_UP (BULL+EXBULL)   : {df.beta_U.mean():.3f}  (median {df.beta_U.median():.3f})")
    t = st.ttest_1samp(df.asym.dropna(), 0)
    print(f"\n  asym = beta_D - beta_U  : TB {df.asym.mean():+.3f}  median {df.asym.median():+.3f}")
    print(f"  cross-sectional t-test  : t={t.statistic:+.2f}  p={t.pvalue:.2e}  "
          f"({(df.asym>0).mean()*100:.1f}% so ma co asym>0)")
    sig = df[df.t_asym.abs() > 1.96]
    print(f"  so ma co |t_asym|>1.96  : {len(sig)}/{len(df)} ({len(sig)/len(df)*100:.0f}%)  "
          f"trong do asym>0: {(sig.asym>0).sum()} / asym<0: {(sig.asym<0).sum()}")

    print("\n" + "=" * 78)
    print("KET QUA 2 — asym co lien quan den dac diem 'DAU CO' khong?")
    print("=" * 78)
    d2 = df.dropna(subset=["asym"])
    for col, lab in (("beta_all", "beta tong"), ("idio_vol", "idio-vol (bien dong rieng)"),
                     ("turnover", "turnover (ADV/mcap)"), ("mcap", "von hoa"), ("adv", "thanh khoan ADV")):
        s = d2.dropna(subset=[col])
        if len(s) < 30:
            continue
        sp = st.spearmanr(s[col], s["asym"])
        print(f"  Spearman(asym, {lab:<28}) = {sp.statistic:+.3f}  p={sp.pvalue:.2e}  n={len(s)}")

    print("\n  --- asym theo NGU PHAN VI beta tong (1=beta thap ... 5=beta cao) ---")
    d2 = d2.assign(q=pd.qcut(d2.beta_all.rank(method="first"), 5, labels=range(1, 6)))
    g = d2.groupby("q").agg(n=("asym", "size"), beta_all=("beta_all", "mean"),
                            beta_D=("beta_D", "mean"), beta_N=("beta_N", "mean"),
                            beta_U=("beta_U", "mean"), asym=("asym", "mean"))
    print(g.round(3).to_string())

    print("\n" + "=" * 78)
    print("KET QUA 3 — LENS DOI CHIEU: downside beta theo DAU return thi truong")
    print("=" * 78)
    dn, up = (m < 0), (m > 0)
    rows2 = []
    for tk in Rw.columns:
        y_all = Rw[tk].values; v = ~np.isnan(y_all)
        a, bb = dn & v, up & v
        if a.sum() < 50 or bb.sum() < 50:
            continue
        y = y_all[v]
        X = np.column_stack([a[v], bb[v], a[v] * m[v], bb[v] * m[v]]).astype(float)
        b, cov, _ = ols(X, y)
        vd = cov[2, 2] + cov[3, 3] - 2 * cov[2, 3]
        rows2.append(dict(ticker=tk, beta_dn=b[2], beta_up=b[3], asym_sign=b[2] - b[3],
                          t=(b[2] - b[3]) / np.sqrt(vd) if vd > 0 else np.nan))
    d3 = pd.DataFrame(rows2)
    t3 = st.ttest_1samp(d3.asym_sign.dropna(), 0)
    print(f"  beta khi thi truong GIAM: {d3.beta_dn.mean():.3f} | khi TANG: {d3.beta_up.mean():.3f}")
    print(f"  asym_sign = dn - up     : TB {d3.asym_sign.mean():+.3f}  t={t3.statistic:+.2f}  "
          f"p={t3.pvalue:.2e}  ({(d3.asym_sign>0).mean()*100:.1f}% ma >0, n={len(d3)})")
    j = df.merge(d3[["ticker", "asym_sign"]], on="ticker")
    print(f"  Spearman(asym_regime, asym_sign) = {st.spearmanr(j.asym, j.asym_sign).statistic:+.3f} "
          f"(2 lens co cung huong khong?)")
    jj = j.dropna(subset=["beta_all", "asym_sign"])
    print(f"  Spearman(asym_sign, beta tong)   = {st.spearmanr(jj.beta_all, jj.asym_sign).statistic:+.3f}"
          f"  p={st.spearmanr(jj.beta_all, jj.asym_sign).pvalue:.2e}")


if __name__ == "__main__":
    main()
