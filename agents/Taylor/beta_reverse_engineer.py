#!/usr/bin/env python3
"""beta_reverse_engineer.py — job Taylor_20260720_111429, Viec 1.

Cau hoi: `tav2_bq.risk_rating.Beta` duoc tinh theo khung thoi gian nao?
Khong co script builder trong repo, khong co dong nao trong bigquery_dictionary.json
mo ta Beta (chi mo ta Risk_Rating la composite cua Beta+Dev bins).

=> Reverse-engineer: tinh beta cho tung ticker tai tung quy-end theo 5 khung chuan
quoc te pho bien, roi do muc do khop voi gia tri Beta THAT dang luu.

LUU Y QUAN TRONG phat hien truoc khi chay: risk_rating.Beta la SO NGUYEN 1..5
(bin/decile-like), KHONG phai he so beta lien tuc. Vi vay tieu chi khop = Spearman
rank correlation giua beta tinh duoc va bin luu (bin cao = beta cao?), khong phai RMSE
tren gia tri tuyet doi. Bo sung: uoc luong bien bin bang cach nhin phan phoi beta
tinh duoc trong tung bin.

Usage: source ./wc_env.sh && BQ_CACHE_THREADS=1 $DNA_PYEXE mike/agents/Taylor/beta_reverse_engineer.py
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, duckdb
from scipy import stats

CACHE = "data/bq_cache"
# Quy dung de kiem tra: chon quy gan day (du lich su cache tu 2013 cho cua so 5Y monthly)
TEST_QUARTERS = ["2019Q1", "2020Q1", "2021Q1", "2022Q1", "2023Q1", "2024Q1", "2025Q1", "2026Q1"]

FRAMEWORKS = {
    "daily_1y":    dict(freq="D", n=252),    # daily, 1 nam
    "daily_2y":    dict(freq="D", n=504),    # daily, 2 nam
    "weekly_2y":   dict(freq="W", n=104),    # weekly 2 nam - Bloomberg default
    "weekly_5y":   dict(freq="W", n=260),    # weekly 5 nam - Value Line
    "monthly_5y":  dict(freq="M", n=60),     # monthly 5 nam - Ibbotson
}


def q_end(q):
    return pd.Period(q, freq="Q").end_time.normalize()


def load_prices(start_year=2013):
    con = duckdb.connect()
    px = con.execute(f"""
        SELECT time, ticker, Close, VNINDEX
        FROM read_parquet('{CACHE}/ticker/*.parquet')
        WHERE Close IS NOT NULL AND VNINDEX IS NOT NULL
    """).df()
    px["time"] = pd.to_datetime(px["time"])
    return px.sort_values(["ticker", "time"])


def load_beta():
    con = duckdb.connect()
    rr = con.execute(f"""
        SELECT DISTINCT ticker, quarter, Beta, Dev, Risk_Rating
        FROM read_parquet('{CACHE}/risk_rating.parquet') WHERE Beta IS NOT NULL
    """).df()
    return rr


def resample_ret(s, freq):
    """s = Series indexed by date. Tra ve chuoi return theo tan suat."""
    if freq == "D":
        r = s.pct_change()
    elif freq == "W":
        r = s.resample("W-FRI").last().pct_change()
    else:
        r = s.resample("ME").last().pct_change()
    return r.dropna()


def compute_betas(px, asof, fw):
    """Tinh beta cho moi ticker tai ngay asof theo framework fw. Causal: chi dung data <= asof."""
    sub = px[px["time"] <= asof]
    # market series
    mkt = sub.drop_duplicates("time").set_index("time")["VNINDEX"].sort_index()
    mr = resample_ret(mkt, fw["freq"]).iloc[-fw["n"]:]
    if len(mr) < fw["n"] * 0.6:
        return {}
    out = {}
    for tk, g in sub.groupby("ticker"):
        s = g.set_index("time")["Close"].sort_index()
        r = resample_ret(s, fw["freq"]).iloc[-fw["n"]:]
        # can it nhat 60% so quan sat yeu cau, va phai align duoc voi market
        j = pd.concat([r.rename("a"), mr.rename("m")], axis=1, join="inner").dropna()
        if len(j) < max(20, fw["n"] * 0.6):
            continue
        vm = j["m"].var()
        if vm <= 0:
            continue
        out[tk] = j["a"].cov(j["m"]) / vm
    return out


def main():
    print("Loading prices from cache (2013+) ...", flush=True)
    px = load_prices()
    rr = load_beta()
    print(f"px rows={len(px):,}  tickers={px.ticker.nunique()}  "
          f"risk_rating rows w/ Beta={len(rr):,}", flush=True)

    rows = []
    for q in TEST_QUARTERS:
        asof = q_end(q)
        stored = rr[rr["quarter"] == q].set_index("ticker")["Beta"]
        if stored.empty:
            print(f"  {q}: no stored Beta, skip"); continue
        for name, fw in FRAMEWORKS.items():
            b = compute_betas(px, asof, fw)
            if not b:
                continue
            s = pd.Series(b)
            common = stored.index.intersection(s.index)
            if len(common) < 30:
                continue
            rho, p = stats.spearmanr(s[common], stored[common])
            # cung do bang Kendall tau (robust hon voi ties cua bin)
            tau, pt = stats.kendalltau(s[common], stored[common])
            rows.append(dict(quarter=q, framework=name, n=len(common),
                             spearman=rho, p_spearman=p, kendall=tau))
            print(f"  {q} {name:11s} n={len(common):4d} rho={rho:+.3f} (p={p:.1e}) tau={tau:+.3f}",
                  flush=True)

    df = pd.DataFrame(rows)
    if df.empty:
        print("NO RESULT"); return
    print("\n=== TRUNG BINH THEO FRAMEWORK (across quarters) ===")
    agg = df.groupby("framework").agg(mean_rho=("spearman", "mean"),
                                      med_rho=("spearman", "median"),
                                      min_rho=("spearman", "min"),
                                      mean_tau=("kendall", "mean"),
                                      nq=("quarter", "nunique")).sort_values("mean_rho", ascending=False)
    print(agg.to_string())

    out = "mike/agents/Taylor/beta_reverse_engineer_results.csv"
    df.to_csv(out, index=False)
    print(f"\nsaved -> {out}")

    # Bin-edge probe cho framework khop nhat
    best = agg.index[0]
    print(f"\n=== BIN EDGES cho framework khop nhat ({best}) — quy 2025Q1 ===")
    fw = FRAMEWORKS[best]
    b = pd.Series(compute_betas(px, q_end("2025Q1"), fw))
    st = rr[rr["quarter"] == "2025Q1"].set_index("ticker")["Beta"]
    c = st.index.intersection(b.index)
    tab = pd.DataFrame({"beta_calc": b[c], "bin_stored": st[c]})
    print(tab.groupby("bin_stored")["beta_calc"].describe()[["count", "min", "25%", "50%", "75%", "max"]].to_string())


if __name__ == "__main__":
    main()
