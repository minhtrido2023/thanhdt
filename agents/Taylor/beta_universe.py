#!/usr/bin/env python3
"""beta_universe.py — job Taylor_20260721_112050, Viec 1.

Tinh RAW BETA (he so hoi quy that, KHONG phai bin 1-5 cua risk_rating.Beta) cho toan
bo universe `ticker_prune`, de Mike/DollarBill tra khi lam full-report ticker.

Cong thuc: beta = Cov(r_stock, r_market) / Var(r_market), return TUAN (W-FRI last
close, Close da dieu chinh), market = cot VNINDEX cung bang (khong can join).

Cua so & nguong toi thieu (chot o day, dung doan lai moi lan chay):
  - Cua so chinh   : 5 nam  = 260 tuan gan nhat  -> cot beta_5y
  - Cua so phu     : 3 nam  = 156 tuan gan nhat  -> cot beta_3y (kiem tra on dinh)
  - Toi thieu       : 104 tuan (~2 nam) co return hop le trong cua so -> moi tinh.
    Ticker moi niem yet <2 nam: KHONG tinh beta, ghi status=INSUFFICIENT_HISTORY va
    n_weeks that co. Cach xu ly: dung beta trung vi cua NGANH (ICB_Code) hoac cua
    TIER von hoa lam proxy, KHONG dung bin risk_rating (bin cung can lich su).
  - Beta chi dang tin khi R2 >= 0.10 VA ADV >= 2 ty/ngay (xem canh bao ao giac
    thanh khoan trong valuation_methodology_router.md §1.2).

Output: mike/agents/Taylor/data_beta_universe.csv  (1 dong / ticker)
        mike/agents/Taylor/data_beta_bin_map.csv   (doi chieu bin 1-5 vs beta that)

Usage: source ./wc_env.sh && $DNA_PYEXE mike/agents/Taylor/beta_universe.py
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, duckdb, datetime as dt

CACHE = "data/bq_cache"
OUT_BETA = "mike/agents/Taylor/data_beta_universe.csv"
OUT_MAP = "mike/agents/Taylor/data_beta_bin_map.csv"

WIN_5Y, WIN_3Y, MIN_WEEKS = 260, 156, 104


def con():
    c = duckdb.connect(); c.execute("SET threads=1"); return c


def load_panel(years_back=7):
    """Gia lay tu bang `ticker` DAY DU (khong phai `ticker_prune`).

    Ly do: ticker_prune la universe LOC CHAT LUONG bien thien theo thoi gian — mot ma
    ra/vao ro nhieu lan nen chuoi gia trong prune bi thung, lam 183/492 ma bi
    INSUFFICIENT_HISTORY GIA (do thung prune, khong phai do moi niem yet). Beta phai
    tinh tren chuoi gia lien tuc => doc `ticker`. Tu cach thanh vien prune giu rieng
    o cot in_prune (co mat trong prune trong 60 phien gan nhat).
    """
    y0 = dt.date.today().year - years_back
    c = con()
    px = c.execute(f"""
        SELECT time, ticker, Close, VNINDEX, ICB_Code
        FROM read_parquet('{CACHE}/ticker/*.parquet')
        WHERE Close IS NOT NULL AND VNINDEX IS NOT NULL AND Close > 0
          AND CAST(time AS DATE) >= DATE '{y0}-01-01'
    """).df()
    px["time"] = pd.to_datetime(px["time"])
    return px.sort_values(["ticker", "time"])


def load_meta():
    """ADV / mcap / co mat trong prune — lay tu ticker_prune (ban ghi moi nhat/ma)."""
    c = con()
    m = c.execute(f"""
        WITH r AS (
          SELECT ticker, time, Close, OShares, Trading_Value_1M_P50,
                 ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY time DESC) rn,
                 MAX(time) OVER () tmax
          FROM read_parquet('{CACHE}/ticker_prune/*.parquet')
          WHERE Close IS NOT NULL
        )
        SELECT ticker, time AS prune_last_bar, Trading_Value_1M_P50 AS adv_vnd,
               Price * OShares AS mcap_vnd,
               (date_diff('day', time, tmax) <= 90) AS in_prune
        FROM r WHERE rn = 1
    """).df()
    m["prune_last_bar"] = pd.to_datetime(m["prune_last_bar"]).dt.date
    return m


def weekly(s):
    """Series indexed by date -> weekly (W-FRI last) return."""
    return s.resample("W-FRI").last().pct_change()


def ols_beta(r_s, r_m):
    """Tra ve (beta, alpha, r2, se_beta, t_beta, n)."""
    ok = r_s.notna() & r_m.notna()
    x, y = r_m[ok].values, r_s[ok].values
    n = len(x)
    if n < MIN_WEEKS or x.var() == 0:
        return (np.nan,) * 5 + (n,)
    b = np.cov(y, x, ddof=1)[0, 1] / x.var(ddof=1)
    a = y.mean() - b * x.mean()
    resid = y - (a + b * x)
    ss_res, ss_tot = (resid ** 2).sum(), ((y - y.mean()) ** 2).sum()
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
    se = np.sqrt((ss_res / (n - 2)) / (((x - x.mean()) ** 2).sum()))
    return b, a, r2, se, b / se if se > 0 else np.nan, n


def main():
    px = load_panel()
    asof = px["time"].max()
    print(f"[beta_universe] asof = {asof.date()}  rows={len(px):,}  tickers={px.ticker.nunique()}")

    mkt = px.drop_duplicates("time").set_index("time")["VNINDEX"].sort_index()
    mr_all = weekly(mkt)

    rows = []
    for tk, g in px.groupby("ticker"):
        s = g.set_index("time")["Close"].sort_index()
        sr_all = weekly(s)
        last = g.iloc[-1]
        rec = dict(ticker=tk, asof=asof.date(), last_bar=last["time"].date(),
                   icb=last.get("ICB_Code"))
        for tag, win in (("5y", WIN_5Y), ("3y", WIN_3Y)):
            idx = mr_all.index[-win:]
            b, a, r2, se, t, n = ols_beta(sr_all.reindex(idx), mr_all.reindex(idx))
            rec.update({f"beta_{tag}": b, f"r2_{tag}": r2, f"se_{tag}": se,
                        f"t_{tag}": t, f"nweeks_{tag}": n})
        rows.append(rec)

    df = pd.DataFrame(rows).merge(load_meta(), on="ticker", how="left")

    def status(r):
        if np.isnan(r["beta_5y"]) and np.isnan(r["beta_3y"]):
            return "INSUFFICIENT_HISTORY"
        if np.isnan(r["beta_5y"]):
            return "SHORT_HISTORY_3Y_ONLY"
        if (r["r2_5y"] < 0.10) or (pd.notna(r["adv_vnd"]) and r["adv_vnd"] < 2e9):
            return "LOW_CONFIDENCE_ILLIQUID"
        return "OK"
    df["status"] = df.apply(status, axis=1)

    # --- doi chieu vs bin risk_rating (quy gan nhat co du lieu) ---
    rr = con().execute(f"""
        SELECT DISTINCT ticker, quarter, Beta AS bin FROM read_parquet('{CACHE}/risk_rating.parquet')
        WHERE Beta IS NOT NULL
    """).df()
    latest_q = sorted(rr["quarter"].unique())[-1]
    rr = rr[rr["quarter"] == latest_q][["ticker", "bin"]].drop_duplicates("ticker")
    df = df.merge(rr, on="ticker", how="left")
    df["bin_quarter"] = latest_q

    df = df.sort_values("ticker")
    df.to_csv(OUT_BETA, index=False)
    print(f"[beta_universe] wrote {OUT_BETA}  n={len(df)}  "
          f"OK={sum(df.status=='OK')}  LOWCONF={sum(df.status=='LOW_CONFIDENCE_ILLIQUID')}  "
          f"SHORT3Y={sum(df.status=='SHORT_HISTORY_3Y_ONLY')}  INSUF={sum(df.status=='INSUFFICIENT_HISTORY')}")

    # --- bang quy doi bin -> beta that, + do lech ---
    sub = df[df["beta_5y"].notna() & df["bin"].notna()]
    m = sub.groupby("bin")["beta_5y"].agg(
        n="count", p25=lambda x: x.quantile(.25), median="median",
        p75=lambda x: x.quantile(.75), iqr=lambda x: x.quantile(.75) - x.quantile(.25),
        sd="std").reset_index()
    m["bin_quarter"] = latest_q
    m.to_csv(OUT_MAP, index=False)
    from scipy import stats as st
    sp = st.spearmanr(sub["bin"], sub["beta_5y"])
    print(f"\n[bin -> beta that] quarter={latest_q}  n={len(sub)}  "
          f"Spearman(bin, beta_5y) = {sp.statistic:.3f} (p={sp.pvalue:.2e})")
    print(m.to_string(index=False))

    # do on dinh 5y vs 3y
    both = df[df.beta_5y.notna() & df.beta_3y.notna()]
    d = (both.beta_3y - both.beta_5y).abs()
    print(f"\n[on dinh] |beta_3y - beta_5y|: median={d.median():.3f} p90={d.quantile(.9):.3f} "
          f"corr={both.beta_5y.corr(both.beta_3y):.3f} (n={len(both)})")
    print(f"[R2] median={df.r2_5y.median():.3f}  <0.10: {int((df.r2_5y<0.10).sum())} ma")


if __name__ == "__main__":
    main()
