"""Kéo dữ liệu MỘT lần cho impact_v2.py (job Taylor_20261030_041731) ⇒ data/*.csv|parquet bất biến.
(a) Close/Price tại 52 ngày cuối quý của rổ v1 (lợi suất kỳ sau cho IC) [BQ].
(b) Price/Close/OShares 2026-06-30 vs 2026-10-29 của rổ asof (kiểm lệch OShares sau sự kiện) [BQ].
(c) Giá asof của mã live/plan/custom30V ngoài rổ [BQ].
(d) Bản chụp ticker_financial (cột fair_value dùng) cho mọi mã cần [local data/bq_cache, md5 ghi SELFCHECK]."""
import os, subprocess, io, json
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, "data"); os.makedirs(DATA, exist_ok=True)
WC = "/home/trido/thanhdt/WorkingClaude"; PRJ = "lithe-record-440915-m9"
SNAP = os.path.join(HERE, "..", "erp_domestic_20261030", "data", "snap_universe_pit_qe.csv")
LIVE = ["DRI", "HT1", "MBB", "MCH", "SCL", "TPB", "TV1", "VIB", "VPB", "DGC", "ACB", "FPT", "HDB", "HPG", "VNM"]


def q(sql):
    o = subprocess.run(["bq", "query", "--use_legacy_sql=false", f"--project_id={PRJ}", "--format=csv", "--max_rows=1000000", sql],
                       capture_output=True, text=True)
    if o.returncode:
        raise RuntimeError(f"bq lỗi rc={o.returncode}: {o.stderr[-800:]} {o.stdout[-800:]}")
    return pd.read_csv(io.StringIO(o.stdout))


s = pd.read_csv(SNAP)
dates = sorted(s.time.unique())
c30 = pd.read_csv(os.path.join(WC, "data", "custom30v_8l_publish.csv"))
c30_last = c30[c30.rebal_date == c30.rebal_date.max()]
tick = sorted(set(s.ticker) | set(LIVE) | set(c30_last.get("ticker", [])))
tl = ",".join(f"'{t}'" for t in tick); dl = ",".join(f"DATE '{d}'" for d in dates)
a = q(f"SELECT t.time, t.ticker, t.Close, t.Price FROM tav2_bq.ticker AS t WHERE t.time IN ({dl}) AND t.ticker IN ({tl}) ORDER BY t.time, t.ticker")
a.to_csv(os.path.join(DATA, "close_qe.csv"), index=False)
b = q(f"""SELECT t.time, t.ticker, t.Close, t.Price, t.OShares FROM tav2_bq.ticker AS t
WHERE t.time IN (DATE '2026-06-30', DATE '2026-10-29') AND t.ticker IN ({tl}) ORDER BY t.ticker, t.time""")
b.to_csv(os.path.join(DATA, "oshares_check.csv"), index=False)
import duckdb
fin = duckdb.connect(":memory:").execute(
    f"SELECT * FROM read_parquet('{WC}/data/bq_cache/ticker_financial.parquet') WHERE ticker IN ({tl})").df()
cols = ["ticker", "time", "quarter", "OShares"] + [c for c in fin.columns if c.startswith(("NP_P", "CF_OA_", "CF_Invest_"))]
fin = fin[cols].sort_values(["ticker", "time"]).reset_index(drop=True)
fin.to_parquet(os.path.join(DATA, "fin_snapshot.parquet"), index=False)
json.dump({"c30_last_rows": len(c30_last), "c30_cols": list(c30.columns), "n_tick": len(tick)}, open(os.path.join(DATA, "fetch_meta.json"), "w"))
print(len(a), len(b), len(fin), len(tick), list(c30.columns)[:6], len(c30_last))
