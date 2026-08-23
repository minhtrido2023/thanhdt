"""Pull dữ liệu cho nghiên cứu post-shock base formation (job Taylor_20260823_025658).

Chiến lược nguồn (prereg §2 + coding_guidelines §9):
  - 2007-06-01 .. 2012-12-31 : BQ TRỰC TIẾP (tav2_bq.ticker JOIN tav2_mike.universe_pit)
    -> cache local `data/bq_cache/` chỉ chunk từ 2013.
  - 2013-01-01 trở đi        : cache local DERIVED (mirror của đúng 2 bảng trên),
    `ticker/<year>.parquet` + `universe_pit_q/<year>.parquet`.
  - VNINDEX + fa_ratings_8l  : BQ trực tiếp (bảng nhỏ).
Tính tương đương cache-vs-BQ được kiểm bằng `verify_sources.py` (mẫu ngẫu nhiên, seed cố định).
"""
from pathlib import Path
import pandas as pd
from google.cloud import bigquery

PROJECT, LOCATION = "lithe-record-440915-m9", "asia-southeast1"
WC = Path("/home/trido/thanhdt/WorkingClaude")
OUT = Path(__file__).resolve().parent
client = bigquery.Client(project=PROJECT, location=LOCATION)


def q(sql):
    return client.query(sql, location=LOCATION).result().to_dataframe()


def main():
    if not (OUT / "panel.parquet").exists():
        early = q(f"""
            SELECT t.time, t.ticker, t.Close, t.Volume, u.in_universe
            FROM `{PROJECT}.tav2_bq.ticker` t
            JOIN `{PROJECT}.tav2_mike.universe_pit` u USING (time, ticker)
            WHERE t.time BETWEEN "2007-06-01" AND "2012-12-31"
              AND t.Close IS NOT NULL AND t.Close > 0
        """)
        print(f"[bq] pre-2013: {len(early):,} dòng")

        parts = [early]
        for year in range(2013, 2027):
            tk = pd.read_parquet(WC / f"data/bq_cache/ticker/{year}.parquet",
                                 columns=["time", "ticker", "Close", "Volume"])
            up = pd.read_parquet(WC / f"data/bq_cache/universe_pit_q/{year}.parquet",
                                 columns=["time", "ticker", "in_universe"])
            m = tk.merge(up, on=["time", "ticker"], how="inner")
            m = m[m["Close"].notna() & (m["Close"] > 0)]
            parts.append(m)
            print(f"[cache] {year}: {len(m):,} dòng")

        panel = pd.concat(parts, ignore_index=True)
        panel["time"] = pd.to_datetime(panel["time"])
        panel = panel.sort_values(["ticker", "time"]).reset_index(drop=True)
        panel.to_parquet(OUT / "panel.parquet", index=False)
        print(f"[ok] panel.parquet: {len(panel):,} dòng, "
              f"{panel['ticker'].nunique()} mã, {panel['time'].min().date()} → {panel['time'].max().date()}")

    if not (OUT / "vnindex.parquet").exists():
        v = q(f"""SELECT time, Close AS vni FROM `{PROJECT}.tav2_bq.ticker`
                  WHERE ticker="VNINDEX" AND time >= "2007-06-01" AND Close IS NOT NULL ORDER BY time""")
        v.to_parquet(OUT / "vnindex.parquet", index=False)
        print(f"[ok] vnindex.parquet: {len(v):,} dòng")

    if not (OUT / "ratings8l.parquet").exists():
        r = q(f"""SELECT ticker, time, rating, route, tier
                  FROM `{PROJECT}.tav2_bq.fa_ratings_8l` ORDER BY ticker, time""")
        r.to_parquet(OUT / "ratings8l.parquet", index=False)
        print(f"[ok] ratings8l.parquet: {len(r):,} dòng")


if __name__ == "__main__":
    main()
