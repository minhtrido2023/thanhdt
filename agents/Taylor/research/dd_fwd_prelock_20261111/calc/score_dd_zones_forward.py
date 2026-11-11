# -*- coding: utf-8 -*-
"""score_dd_zones_forward.py — chấm FORWARD thật sổ mức giá DD (kb/dd_price_zones.json). CHỈ ĐỌC.

Mỗi (mã, dd_date): giữ bản rev cao nhất (sổ append-only, rev cao thắng). Bỏ entry center null.
  t0       = price_date (nếu có) else dd_date; P0 = price_ref (đ/cp, CÙNG hệ CP với center).
  TR_N     = Close_adj(phiên cuối ≤ t0+N tháng) / Close_adj(phiên cuối ≤ t0)   [Close điều chỉnh, gồm cổ tức]
             (Close đ/c đã quy mọi sự kiện CP về hệ hiện tại ⇒ tỉ số không phụ thuộc hệ CP; P0·TR_N là giá
              "tương đương" ở hệ CP của ngày DD — so được với center.)
  x0       = log(P0/center); xN = log(P0·TR_N/center); AE_N = |xN|; closed_N = 1 − |xN|/|x0|
  in_zone_N= zone_low ≤ P0·TR_N ≤ zone_high; touch_center_N = đường giá (tương đương) chạm center trong [t0, t0+N]
  rank IC  = Spearman(log(center/P0), log TR_N) giữa các mã cùng THÁNG dd_date, cần ≥ MIN_IC mã đủ N.
  cờ insufficient_N: t0+N > phiên cuối của dữ liệu giá (hoặc thiếu phiên trong 10 ngày trước t0+N).
Nguồn giá: data/bq_cache/ticker/*.parquet = bản sao tav2_bq.ticker (sync 23:45 ICT; registry
kb/data_registry/bq-cache/bq_cache_parquet.md). Giá chỉ là NHÃN. Không ghi sổ, không sửa dd_price_zones.json.

Run: $DNA_PYEXE score_dd_zones_forward.py [--asof YYYY-MM-DD] [--out DIR]
  --asof: cắt dữ liệu giá tại ngày này (chấm "như thể hôm đó"; dùng cho selfcheck/tái lập).
Mốc chấm đầu tiên có nghĩa: 12 tháng sau mỗi dd_date (sổ bắt đầu 2026-10-26 ⇒ ~10–11/2027);
mốc 3 tháng (~01–02/2027) chỉ MÔ TẢ (N quá ngắn so với chân trời giá trị).
"""
import os, json, argparse
import numpy as np, pandas as pd
import duckdb
from scipy.stats import spearmanr

WC = "/home/trido/thanhdt/WorkingClaude"
ZONES = f"{WC}/mike/kb/dd_price_zones.json"
HZ = (3, 6, 12, 24, 36)
MIN_IC = 8
HERE = os.path.dirname(os.path.abspath(__file__))

ap = argparse.ArgumentParser()
ap.add_argument("--asof", default=None); ap.add_argument("--out", default=os.path.join(HERE, "..", "out", "fwd"))
ap.add_argument("--zones", default=ZONES)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)

Z = json.load(open(a.zones))
E = pd.DataFrame(Z["entries"])
E["rev"] = E["rev"].fillna(1).astype(int)
E = E.sort_values(["ticker", "dd_date", "rev"]).groupby(["ticker", "dd_date"], as_index=False).tail(1)
n_all = len(E)
E = E[E.center.notna() & E.price_ref.notna()].copy()
E["t0"] = pd.to_datetime(E.price_date.where(E.price_date.notna(), E.dd_date))
E["dd_date"] = pd.to_datetime(E.dd_date)

tk = sorted(E.ticker.unique())
px = duckdb.connect().execute(f"""SELECT ticker, CAST(time AS DATE) AS time, Close FROM read_parquet('{WC}/data/bq_cache/ticker/*.parquet')
    WHERE ticker IN ({",".join("'" + t + "'" for t in tk)}) AND time >= DATE '{(E.t0.min() - pd.Timedelta(days=15)).date()}' AND Close > 0""").df()
px["time"] = pd.to_datetime(px.time)
if a.asof:
    px = px[px.time <= pd.Timestamp(a.asof)]
LAST = px.time.max()
pb = {t: g.sort_values("time").reset_index(drop=True) for t, g in px.groupby("ticker")}

rows = []
for _, e in E.iterrows():
    g = pb.get(e.ticker)
    r = {"ticker": e.ticker, "dd_date": e.dd_date.date(), "rev": int(e.rev), "t0": e.t0.date(),
         "P0": float(e.price_ref), "center": float(e.center), "center_kind": e.center_kind,
         "zone_low": e.zone_low, "zone_high": e.zone_high, "x0": float(np.log(e.price_ref / e.center))}
    if g is None or not (g.time <= e.t0).any():
        r["note"] = "no_price"; rows.append(r); continue
    c0 = g[g.time <= e.t0].iloc[-1]
    r["close0_date"] = c0.time.date(); r["lag0_days"] = int((e.t0 - c0.time).days)
    for N in HZ:
        end = e.t0 + pd.DateOffset(months=N)
        seg = g[(g.time > c0.time) & (g.time <= end)]
        ok = (LAST >= end) and len(seg) and (seg.time.iloc[-1] >= end - pd.Timedelta(days=10))
        r[f"insufficient_{N}"] = not ok
        if not ok:
            continue
        tr = float(seg.Close.iloc[-1] / c0.Close)
        path = e.price_ref * seg.Close.values / c0.Close
        xN = float(np.log(e.price_ref * tr / e.center))
        r.update({f"TR_{N}": tr, f"xN_{N}": xN, f"AE_{N}": abs(xN),
                  f"closed_{N}": 1 - abs(xN) / abs(r["x0"]) if r["x0"] != 0 else np.nan,
                  f"in_zone_{N}": bool(pd.notna(e.zone_low) and pd.notna(e.zone_high) and
                                       e.zone_low <= e.price_ref * tr <= e.zone_high),
                  f"touch_center_{N}": bool(path.max() >= e.center) if e.price_ref < e.center else bool(path.min() <= e.center)})
    rows.append(r)
R = pd.DataFrame(rows)
R.to_csv(os.path.join(a.out, "dd_zones_forward_rows.csv"), index=False)

summ = {"zones_md5": __import__("hashlib").md5(open(a.zones, "rb").read()).hexdigest(),
        "price_last": str(LAST.date()), "asof_cut": a.asof, "n_entries_latest_rev": n_all, "n_scored": len(R),
        "dd_date_range": [str(E.dd_date.min().date()), str(E.dd_date.max().date())], "by_N": {}}
R["month"] = pd.to_datetime(R.dd_date).dt.to_period("M").astype(str)
for N in HZ:
    k = R[~R.get(f"insufficient_{N}", pd.Series(True, index=R.index)).astype(bool)] if f"insufficient_{N}" in R else R.iloc[:0]
    first = (E.t0.min() + pd.DateOffset(months=N)).date(); last = (E.t0.max() + pd.DateOffset(months=N)).date()
    o = {"n_full": int(len(k)), "first_scorable_date": str(first), "all_scorable_date": str(last)}
    if len(k):
        o.update({"median_AE": float(k[f"AE_{N}"].median()), "median_x0_abs": float(k.x0.abs().median()),
                  "frac_in_zone": float(k[f"in_zone_{N}"].mean()), "frac_touch_center": float(k[f"touch_center_{N}"].mean())})
        ic = {}
        for m_, gg in k.groupby("month"):
            if len(gg) >= MIN_IC:
                ic[m_] = {"n": int(len(gg)), "rank_ic": float(spearmanr(-gg.x0, np.log(gg[f"TR_{N}"]))[0])}
            else:
                ic[m_] = {"n": int(len(gg)), "rank_ic": None, "flag": f"<{MIN_IC} mã"}
        o["rank_ic_by_month"] = ic
    o["descriptive_only"] = N < 12
    summ["by_N"][str(N)] = o
json.dump(summ, open(os.path.join(a.out, "dd_zones_forward_summary.json"), "w"), indent=1, default=str)
print(json.dumps({k: v for k, v in summ.items() if k != "by_N"}, default=str))
for N, o in summ["by_N"].items():
    print(f"N={N:>2}m n_full={o['n_full']:3d} first_scorable={o['first_scorable_date']} all={o['all_scorable_date']}"
          + (" (MÔ TẢ)" if o["descriptive_only"] else ""))
