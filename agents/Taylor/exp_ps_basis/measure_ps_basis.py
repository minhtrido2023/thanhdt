#!/usr/bin/env python3
"""Job Taylor_20260802_081308 — do doc lap co so gia dung cho lens `ps` trong rating_8l.py.

3 phep do (KHONG copy so cu cua job Taylor_20260802_063752, tu keo lai tu BQ):
  (A) IDENTITY  : PS luu trong ticker_financial nam o co so `Price` (tho, PIT) hay `Close` (da adjust)?
                  So sanh Price*OShares/Rev_ttm vs PS luu, va Close*OShares/Rev_ttm vs PS luu.
  (B) LICH SU   : tai lap dung cong thuc rating_8l (`ps = <basis>*OShares/Rev_ttm`, sales_yield=1/ps)
                  tren 3 ngay cat 2014/2015/2016 -> lech sales_yield + Spearman + so ten doi trong
                  top-30 re nhat theo truc PS.
  (C) LIVE      : hom nay Price vs Close tren ticker_1m@MAX(time) -> tac dong live.

Chay: /home/trido/thanhdt/wc_venv/bin/python measure_ps_basis.py
"""
import io, os, subprocess, sys
import numpy as np
import pandas as pd

PROJECT = "lithe-record-440915-m9"
BQ = "/home/trido/google-cloud-sdk/bin/bq"
OUT = os.path.dirname(os.path.abspath(__file__))


def bq(sql: str) -> pd.DataFrame:
    r = subprocess.run([BQ, "query", "--use_legacy_sql=false", f"--project_id={PROJECT}",
                        "--format=csv", "--max_rows=200000", sql],
                       capture_output=True, text=True, timeout=600)
    if not r.stdout.strip():
        raise RuntimeError("bq no rows:\n" + r.stderr[-2000:])
    return pd.read_csv(io.StringIO(r.stdout.strip()))


# ---------------------------------------------------------------- (A) identity
SQL_A = """
SELECT f.ticker, f.time, f.PS, f.OShares,
       f.Revenue_P0, f.Revenue_P1, f.Revenue_P2, f.Revenue_P3,
       t.Close, t.Price
FROM tav2_bq.ticker_financial AS f
JOIN tav2_bq.ticker AS t USING (ticker, time)
WHERE f.time BETWEEN DATE '2014-01-01' AND DATE '2016-12-31'
  AND f.PS > 0 AND f.OShares > 0 AND t.Close > 0 AND t.Price > 0
"""


def part_a():
    d = bq(SQL_A)
    rev = d[[f"Revenue_P{i}" for i in range(4)]].sum(axis=1, min_count=1)
    d = d[rev > 0].copy()
    rev = rev[rev > 0]
    for basis in ("Price", "Close"):
        ps = d[basis] * d["OShares"] / rev
        d[f"relerr_{basis}"] = (ps / d["PS"] - 1.0).abs()
    n = len(d)
    print(f"\n=== (A) IDENTITY vs PS luu (ticker_financial), 2014-01-01..2016-12-31 ===")
    print(f"n_rows = {n:,}")
    for basis in ("Price", "Close"):
        e = d[f"relerr_{basis}"]
        print(f"  {basis}*OShares/Rev_ttm khop PS luu (sai so <2%): {(e < 0.02).mean()*100:6.1f}%"
              f"   | sai so tuong doi trung vi: {e.median():.4f}")
    d.to_csv(os.path.join(OUT, "identity_2014_2016.csv"), index=False)
    return n


# ---------------------------------------------------------------- (B) lich su
SQL_B = """
WITH F AS (
  SELECT ticker, Revenue_P0, Revenue_P1, Revenue_P2, Revenue_P3,
         ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY time DESC) rn
  FROM tav2_bq.ticker_financial WHERE time <= DATE '{d}')
SELECT t.ticker, t.Close, t.Price, t.OShares,
       F.Revenue_P0, F.Revenue_P1, F.Revenue_P2, F.Revenue_P3
FROM tav2_bq.ticker AS t JOIN F ON F.ticker = t.ticker AND F.rn = 1
WHERE t.time = DATE '{d}' AND t.Close > 0 AND t.Price > 0 AND t.OShares > 0
"""


def part_b():
    print("\n=== (B) LICH SU — tai lap cong thuc rating_8l tren 3 ngay cat ===")
    print(f"{'ngay':<12}{'n':>5}{'F=Price/Close med':>20}{'sales_yield lech med':>23}"
          f"{'Spearman':>11}{'top30 doi':>11}")
    rows = []
    for day in ("2014-06-30", "2015-06-30", "2016-06-30"):
        d = bq(SQL_B.format(d=day))
        rev = d[[f"Revenue_P{i}" for i in range(4)]].sum(axis=1, min_count=1)
        d = d[rev > 0].copy()
        rev = rev[rev > 0]
        # dung cong thuc y het rating_8l.py:533-535 cho ca 2 co so
        for basis, tag in (("Price", "fix"), ("Close", "bug")):
            ps = np.where((rev > 0) & d["OShares"].notna() & d[basis].notna(),
                          d[basis] * d["OShares"] / rev, np.nan)
            d[f"ps_{tag}"] = ps
            d[f"sy_{tag}"] = np.where(d[f"ps_{tag}"] > 0, (1.0 / d[f"ps_{tag}"]).round(4), np.nan)
        v = d.dropna(subset=["sy_fix", "sy_bug"]).copy()
        lech = ((v["sy_fix"] / v["sy_bug"]) - 1.0).abs().median()
        rho = v["sy_fix"].rank().corr(v["sy_bug"].rank())
        # "re nhat theo truc PS" = sales_yield CAO nhat
        top_fix = set(v.nlargest(30, "sy_fix")["ticker"])
        top_bug = set(v.nlargest(30, "sy_bug")["ticker"])
        chg = 30 - len(top_fix & top_bug)
        fmed = (v["Price"] / v["Close"]).median()
        print(f"{day:<12}{len(v):>5}{fmed:>20.3f}{lech*100:>22.1f}%{rho:>11.3f}{chg:>8}/30")
        rows.append(dict(day=day, n=len(v), f_med=fmed, sy_diff_med=lech, spearman=rho, top30_changed=chg))
        v.to_csv(os.path.join(OUT, f"hist_{day}.csv"), index=False)
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "hist_summary.csv"), index=False)


# ---------------------------------------------------------------- (C) live
SQL_C = """
WITH L AS (SELECT MAX(time) mx FROM tav2_bq.ticker_1m)
SELECT t.ticker, t.time, t.Close, t.Price, t.OShares
FROM tav2_bq.ticker_1m AS t, L WHERE t.time = L.mx
"""


def part_c():
    d = bq(SQL_C)
    v = d.dropna(subset=["Close", "Price"])
    v = v[(v["Close"] > 0) & (v["Price"] > 0)]
    same = (v["Price"] == v["Close"]).sum()
    print(f"\n=== (C) LIVE ({d['time'].iloc[0]}) ===")
    print(f"  n co ca Price & Close: {len(v)}   | Price == Close: {same}/{len(v)}"
          f"   | max |Price/Close-1|: {((v['Price']/v['Close'])-1).abs().max():.6f}")
    return same, len(v)


if __name__ == "__main__":
    part_a()
    part_b()
    part_c()
    print("\n[done] artifacts ->", OUT)
