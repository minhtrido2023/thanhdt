#!/usr/bin/env python3
"""size_premium_vn.py — job Taylor_20260721_112050, Viec 2.

Do SIZE PREMIUM thuc te cua thi truong VN bang chinh du lieu ticker_prune —
KHONG be nguyen so Ibbotson/Duff&Phelps cua My.

Thiet ke (causal, khong look-ahead):
  - Tan suat: thang. Ngay formation = phien cuoi thang t. Do return thang t+1.
  - Universe point-in-time: chi cac ma CO MAT trong ticker_prune tai phien formation
    (membership prune bien thien theo thoi gian -> phai lay PIT, khong lay snapshot cuoi).
  - mcap = Price * OShares (Price = gia KHONG dieu chinh; Close da adjust co tuc/chia tach
    nen nhan voi OShares se ra von hoa qua khu bi THAP). Return van dung Close (adjusted).
  - KIEM SOAT BETA: alpha_i = r_i - rf - beta_i*(r_m - rf), beta_i = hoi quy tuan
    rolling 260 tuan (min 104) TINH DEN formation. Do trung binh alpha (residual CAPM)
    theo nhom, KHONG do return tho -> tranh nham size premium voi beta premium.
  - Tach ao giac thanh khoan: double-sort size x thanh khoan (Trading_Value_1M_P50).
    Neu premium chi ton tai o nua kem thanh khoan => do la illiquidity premium
    (khong the thu hoach voi size lenh cua minh), khong phai size risk premium.
  - Walk-forward: IS 2014-2019, OOS 2020-now (chuan doi).
  - Multiple testing: N trials khai bao ro + DSR tren chuoi alpha long-short.

Usage: source ./wc_env.sh && $DNA_PYEXE mike/agents/Taylor/size_premium_vn.py
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, duckdb
from scipy import stats as st

CACHE = "data/bq_cache"
OUT = "mike/agents/Taylor/data_size_premium.csv"
START = "2009-01-01"          # can 5 nam warm-up beta truoc khi do tu 2014
EVAL_START = "2014-01-01"
IS_END = "2019-12-31"
RF_ANNUAL = 0.06              # lai suat phi rui ro danh dinh VN (~TPCP 10Y/tien gui)
WIN, MINW = 260, 104


def con():
    c = duckdb.connect(); c.execute("SET threads=1"); return c


def load():
    px = con().execute(f"""
        SELECT CAST(time AS DATE) AS d, ticker, Close, VNINDEX
        FROM read_parquet('{CACHE}/ticker/*.parquet')
        WHERE Close > 0 AND VNINDEX IS NOT NULL AND CAST(time AS DATE) >= DATE '{START}'
    """).df()
    px["d"] = pd.to_datetime(px["d"])
    pr = con().execute(f"""
        SELECT CAST(time AS DATE) AS d, ticker, Price, OShares, Trading_Value_1M_P50 AS adv
        FROM read_parquet('{CACHE}/ticker_prune/*.parquet')
        WHERE Price > 0 AND OShares > 0 AND CAST(time AS DATE) >= DATE '{EVAL_START}'
    """).df()
    pr["d"] = pd.to_datetime(pr["d"])
    return px, pr


def rolling_beta(Rw, mw):
    """Rolling OLS beta cua tung cot Rw vs mw. Tra ve DataFrame cung shape."""
    r = Rw.rolling(WIN, min_periods=MINW)
    m = mw.rolling(WIN, min_periods=MINW)
    # dung mean cua tich de lay cov (bien the sample-mean; du chinh xac cho muc dich nay)
    prod = Rw.mul(mw, axis=0).rolling(WIN, min_periods=MINW).mean()
    cov = prod.sub(r.mean().mul(m.mean(), axis=0))
    var = (mw.pow(2).rolling(WIN, min_periods=MINW).mean() - m.mean() ** 2)
    return cov.div(var, axis=0)


def perf(a, label):
    """a = chuoi alpha thang. Tra ve dict thong ke."""
    a = a.dropna()
    if len(a) < 12:
        return dict(label=label, n=len(a))
    t = st.ttest_1samp(a, 0)
    return dict(label=label, n=len(a), ann_pp=a.mean() * 12 * 100,
                t=t.statistic, p=t.pvalue, sd_m=a.std())


def main():
    px, pr = load()

    # ---- tuan: return + rolling beta ----
    wide = px.pivot_table(index="d", columns="ticker", values="Close", aggfunc="last")
    mkt = px.drop_duplicates("d").set_index("d")["VNINDEX"].sort_index()
    Wp = wide.resample("W-FRI").last()
    Rw = Wp.pct_change()
    mw = mkt.resample("W-FRI").last().pct_change()
    Rw, mw = Rw.align(mw, axis=0, join="inner")
    B = rolling_beta(Rw, mw)
    print(f"[load] weekly {Rw.shape}, beta panel ready")

    # ---- thang: return ----
    Mp = wide.resample("ME").last()
    Rm = Mp.pct_change()
    mm = mkt.resample("ME").last().pct_change()
    rf = RF_ANNUAL / 12

    # beta as-of cuoi thang (lay quan sat tuan gan nhat <= cuoi thang)
    Bm = B.reindex(Rm.index, method="ffill")

    # ---- dac trung PIT tu prune: mcap, adv, membership ----
    pr["ym"] = pr["d"].values.astype("datetime64[M]")
    last = pr.sort_values("d").groupby(["ym", "ticker"]).tail(1)
    last["mcap"] = last["Price"] * last["OShares"]   # Price = gia KHONG dieu chinh (Close da adjust co tuc -> mcap qua khu bi thap); Price DA la VND, KHONG nhan 1000
    feat = last.set_index(["ym", "ticker"])[["mcap", "adv"]]

    months = [m for m in Rm.index if m >= pd.Timestamp(EVAL_START)]
    recs = []
    for i, t in enumerate(months[:-1]):
        ym = np.datetime64(t.to_period("M").to_timestamp(), "M")
        if ym not in feat.index.get_level_values(0):
            continue
        f = feat.loc[ym].copy()
        nxt = months[i + 1]
        f["fwd"] = Rm.loc[nxt].reindex(f.index)
        f["beta"] = Bm.loc[t].reindex(f.index)
        f = f.dropna(subset=["mcap", "fwd", "beta"])
        if len(f) < 50:
            continue
        f["alpha"] = f["fwd"] - rf - f["beta"] * (mm.loc[nxt] - rf)
        f["month"] = nxt
        recs.append(f.reset_index().rename(columns={"index": "ticker"}))
    panel = pd.concat(recs, ignore_index=True)
    panel.to_csv(OUT, index=False)
    print(f"[panel] {len(panel):,} obs, {panel.month.nunique()} thang, "
          f"{panel.ticker.nunique()} ma, {panel.month.min():%Y-%m} -> {panel.month.max():%Y-%m}")
    print(f"[panel] ma/thang: median {panel.groupby('month').size().median():.0f}")

    def bucket(g, k, col="mcap"):
        return pd.qcut(g[col].rank(method="first"), k, labels=range(1, k + 1))

    # ================= N TRIALS: 3 cach chia (tercile/quintile/decile) =================
    out = {}
    for k, name in ((3, "tercile"), (5, "quintile"), (10, "decile")):
        panel[f"g{k}"] = panel.groupby("month", group_keys=False).apply(lambda g: bucket(g, k))
        tab = panel.groupby(["month", f"g{k}"]).agg(
            alpha=("alpha", "mean"), beta=("beta", "mean"),
            mcap=("mcap", "median"), n=("alpha", "size")).reset_index()
        piv = tab.pivot(index="month", columns=f"g{k}", values="alpha")
        ls = piv[1] - piv[k]          # small minus big
        out[name] = dict(piv=piv, ls=ls, tab=tab, k=k)

    print("\n" + "=" * 78)
    print("SIZE PREMIUM (alpha CAPM residual, EW, %/nam) — FULL 2014->now")
    print("=" * 78)
    for name, o in out.items():
        piv, k = o["piv"], o["k"]
        row = {g: piv[g].mean() * 12 * 100 for g in piv.columns}
        print(f"\n[{name}] (1=nho nhat ... {k}=lon nhat)")
        print("  alpha %/nam : " + "  ".join(f"g{g}={v:+.2f}" for g, v in row.items()))
        med = o["tab"].groupby(o["tab"].columns[1]).agg(mcap=("mcap", "median"), beta=("beta", "mean"), n=("n", "median"))
        print("  mcap trung vi (ty): " + "  ".join(f"g{g}={r.mcap/1e9:,.0f}" for g, r in med.iterrows()))
        print("  beta TB nhom      : " + "  ".join(f"g{g}={r.beta:.2f}" for g, r in med.iterrows()))
        print("  n TB/thang        : " + "  ".join(f"g{g}={r.n:.0f}" for g, r in med.iterrows()))
        for lab, sl in (("FULL", slice(None)),
                        ("IS 2014-19", slice(None, IS_END)),
                        ("OOS 2020+", slice("2020-01-01", None))):
            s = perf(o["ls"].loc[sl], lab)
            if s.get("n", 0) >= 12:
                print(f"  L/S small-big {lab:<11}: {s['ann_pp']:+.2f} pp/nam  t={s['t']:+.2f}  p={s['p']:.3f}  n={s['n']}")

    # ================= TACH SIZE vs THANH KHOAN =================
    print("\n" + "=" * 78)
    print("TACH SIZE-RISK vs ILLIQUIDITY: double-sort size(quintile) x ADV(median trong nhom)")
    print("=" * 78)
    p = panel.dropna(subset=["adv"]).copy()
    p["liq"] = p.groupby(["month", "g5"], group_keys=False).apply(
        lambda g: pd.Series(np.where(g["adv"] >= g["adv"].median(), "HI", "LO"), index=g.index))
    d = p.groupby(["month", "g5", "liq"]).alpha.mean().unstack("liq")
    agg = d.groupby(level="g5").mean() * 12 * 100
    print("\n  alpha %/nam theo (size x thanh khoan):")
    print("  size   ADV-thap(LO)   ADV-cao(HI)   chenh(LO-HI)")
    for g in agg.index:
        print(f"  g{g}      {agg.loc[g,'LO']:+7.2f}       {agg.loc[g,'HI']:+7.2f}      {agg.loc[g,'LO']-agg.loc[g,'HI']:+7.2f}")
    # L/S size trong tung nua thanh khoan
    for lq in ("LO", "HI"):
        s_ = d[lq].unstack("g5") if isinstance(d.index, pd.MultiIndex) else None
        ls_ = d[lq].xs(1, level="g5") - d[lq].xs(5, level="g5")
        for lab, sl in (("FULL", slice(None)), ("IS", slice(None, IS_END)), ("OOS", slice("2020-01-01", None))):
            s = perf(ls_.loc[sl], lab)
            if s.get("n", 0) >= 12:
                print(f"  L/S size (small-big) trong nua ADV-{lq} {lab:<5}: "
                      f"{s['ann_pp']:+.2f} pp/nam  t={s['t']:+.2f}  p={s['p']:.3f}")
    # nguoc lai: L/S thanh khoan trong nhom cung size
    ill = (d["LO"] - d["HI"]).groupby(level="month").mean()
    for lab, sl in (("FULL", slice(None)), ("IS 2014-19", slice(None, IS_END)),
                    ("OOS 2020+", slice("2020-01-01", None))):
        s = perf(ill.loc[sl], lab)
        if s.get("n", 0) >= 12:
            print(f"\n  L/S illiquidity (ADV thap - cao, TRUNG HOA size) {lab:<11}: "
                  f"{s['ann_pp']:+.2f} pp/nam  t={s['t']:+.2f}  p={s['p']:.3f}  n={s['n']}")
    print(f"  -> DSR(illiquidity, N=3) = {dsr(ill, 3):.3f}   SR_ann = {sharpe(ill):.3f}")

    # ========== ROBUSTNESS: beta co bi UOC LUONG THAP o small-cap khong? ==========
    # Non-synchronous trading (Dimson 1979): ma giao dich thua phan ung tre voi thi truong
    # => beta tuan bi keo xuong => phan du "alpha" bi thoi phong. Kiem tra bang beta tan
    # suat THANG (rolling 60 thang, min 24) — tan suat thap gan nhu triet tieu bias nay.
    print("\n" + "=" * 78)
    print("ROBUSTNESS: beta tan suat THANG (rolling 60m) thay cho beta tuan")
    print("=" * 78)
    Rm_ = Rm.copy()
    prod = Rm_.mul(mm, axis=0).rolling(60, min_periods=24).mean()
    covM = prod.sub(Rm_.rolling(60, min_periods=24).mean().mul(mm.rolling(60, min_periods=24).mean(), axis=0))
    varM = mm.pow(2).rolling(60, min_periods=24).mean() - mm.rolling(60, min_periods=24).mean() ** 2
    BM = covM.div(varM, axis=0)

    q = panel.copy()
    bm_long = BM.stack().rename("beta_m").reset_index()
    bm_long.columns = ["month_form", "ticker", "beta_m"]
    # beta as-of formation = thang truoc month (fwd return)
    q["month_form"] = q["month"] - pd.offsets.MonthEnd(1)
    q = q.merge(bm_long, on=["month_form", "ticker"], how="left").dropna(subset=["beta_m"])
    q["alpha_m"] = q["fwd"] - rf - q["beta_m"] * q["month"].map(mm) + q["beta_m"] * rf
    tabm = q.groupby(["month", "g5"]).agg(alpha=("alpha_m", "mean"), beta=("beta_m", "mean")).reset_index()
    pm = tabm.pivot(index="month", columns="g5", values="alpha")
    bmn = tabm.groupby("g5").beta.mean()
    print("  beta TB nhom (thang): " + "  ".join(f"g{g}={v:.2f}" for g, v in bmn.items()))
    print("  alpha %/nam         : " + "  ".join(f"g{g}={pm[g].mean()*12*100:+.2f}" for g in pm.columns))
    lsm = pm[1] - pm[5]
    for lab, sl in (("FULL", slice(None)), ("IS 2014-19", slice(None, IS_END)), ("OOS 2020+", slice("2020-01-01", None))):
        s = perf(lsm.loc[sl], lab)
        if s.get("n", 0) >= 12:
            print(f"  L/S small-big {lab:<11}: {s['ann_pp']:+.2f} pp/nam  t={s['t']:+.2f}  p={s['p']:.3f}  n={s['n']}")
    print(f"  => chenh beta small(g1) vs large(g5): tuan {out['quintile']['tab'].groupby('g5').beta.mean().iloc[0]:.2f} vs "
          f"{out['quintile']['tab'].groupby('g5').beta.mean().iloc[-1]:.2f} | thang {bmn.iloc[0]:.2f} vs {bmn.iloc[-1]:.2f}")

    # ================= DSR =================
    print("\n" + "=" * 78)
    print("DEFLATED SHARPE RATIO (N trials = 3 cach chia size)")
    print("=" * 78)
    N = 3
    for name, o in out.items():
        print(f"  {name:<9}: DSR = {dsr(o['ls'], N):.3f}   SR_ann = {sharpe(o['ls']):.3f}")


def sharpe(a):
    a = a.dropna()
    return a.mean() / a.std() * np.sqrt(12) if a.std() > 0 else np.nan


def dsr(a, n_trials):
    """Deflated Sharpe Ratio (Bailey & Lopez de Prado 2014), chuoi thang."""
    a = a.dropna()
    T = len(a)
    if T < 24 or a.std() == 0:
        return np.nan
    sr = a.mean() / a.std()                      # per-period
    g3, g4 = st.skew(a), st.kurtosis(a, fisher=False)
    e, g = 0.5772156649, None
    z = st.norm.ppf(1 - 1.0 / n_trials) if n_trials > 1 else 0
    z2 = st.norm.ppf(1 - 1.0 / (n_trials * np.e)) if n_trials > 1 else 0
    sr0 = np.sqrt(1.0 / (T - 1)) * ((1 - e) * z + e * z2)   # ky vong SR max qua N trials
    den = np.sqrt(1 - g3 * sr + (g4 - 1) / 4 * sr ** 2)
    return st.norm.cdf((sr - sr0) * np.sqrt(T - 1) / den)


if __name__ == "__main__":
    main()
