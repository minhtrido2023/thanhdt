#!/usr/bin/env python3
"""Xác minh ĐỘC LẬP công thức giá tham chiếu UPCOM = bình quân gia quyền phiên trước.

Không tin WebSearch, không tin field broker: dựng lại bình quân gia quyền TỪ dữ liệu khớp lệnh
(bar 1 phút, nguồn VCI qua vnstock — độc lập hoàn toàn với DNSE) rồi so với `q.ref` DNSE đo
sống ngày 2026-08-15.

Hai đại lượng đều là TỈ SỐ (vwap/close) nên BẤT BIẾN với việc bar VCI đã điều chỉnh hồi tố —
đó là lý do so tỉ số chứ không so mức giá.
"""
import json, sys
import pandas as pd

D = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/upcom_ref_anchor_20260815/data"
TK = ["DRI", "SCL", "TV1", "SGP", "ACV", "QNS", "TMG"]
# đo sống 2026-08-15 (probe DNSE): (q.ref, ohlc close 08-14)
DNSE = {"DRI": (13300.0, 13300.0), "SCL": (22900.0, 23700.0), "TV1": (20000.0, 20100.0),
        "SGP": (20400.0, 20500.0), "ACV": (40600.0, 40500.0), "QNS": (46700.0, 46600.0),
        "TMG": (63800.0, 63200.0)}

rows, daily = [], []
for t in TK:
    df = pd.read_csv(f"{D}/{t}_1m.csv", parse_dates=["time"])
    df["d"] = df["time"].dt.date
    g = df.groupby("d")
    agg = pd.DataFrame({
        "vwap": g.apply(lambda x: (x["close"] * x["volume"]).sum() / max(x["volume"].sum(), 1),
                        include_groups=False),
        "close": g["close"].last(),
        "vol": g["volume"].sum(),
        "n_bar": g.size(),
    })
    agg = agg[agg["vol"] > 0].copy()
    agg["ticker"] = t
    agg["dev_pct"] = (agg["vwap"] / agg["close"] - 1.0) * 100
    daily.append(agg.reset_index())
    last = agg.index.max()
    ref, close = DNSE[t]
    rows.append({
        "ticker": t, "phien_cuoi_bar": str(last),
        "vwap_tu_bar1m": round(float(agg.loc[last, "vwap"]), 4),
        "close_tu_bar1m": round(float(agg.loc[last, "close"]), 4),
        "dev_dung_lai_pct": round(float(agg.loc[last, "dev_pct"]), 4),
        "dnse_ref": ref, "dnse_close": close,
        "dev_do_that_pct": round((ref / close - 1) * 100, 4),
        "chenh_lech_pp": round(float(agg.loc[last, "dev_pct"]) - (ref / close - 1) * 100, 4),
        "vol_phien": int(agg.loc[last, "vol"]), "n_bar": int(agg.loc[last, "n_bar"]),
    })

all_d = pd.concat(daily, ignore_index=True)
all_d = all_d[all_d["d"] >= pd.Timestamp("2025-08-01").date()]

print("=== A. DỰNG LẠI bình quân gia quyền phiên 2026-08-14 vs q.ref DNSE đo sống 08-15 ===")
print(f"{'mã':<5} {'vwap/close dựng lại':>20} {'ref/close đo thật':>19} {'chênh (pp)':>11} {'KL phiên':>10}")
for r in rows:
    print(f"{r['ticker']:<5} {r['dev_dung_lai_pct']:>19.4f}% {r['dev_do_that_pct']:>18.4f}% "
          f"{r['chenh_lech_pp']:>11.4f} {r['vol_phien']:>10,}")

print("\n=== B. PHÂN BỐ |vwap−close|/close theo mã, 12 tháng gần nhất (bar 1m) ===")
print(f"{'mã':<5} {'N phiên':>8} {'=0':>5} {'median':>8} {'p90':>8} {'p95':>8} {'max':>8} {'>1%':>6} {'>3%':>6}")
summ = {}
for t in TK:
    a = all_d[all_d["ticker"] == t]["dev_pct"].abs().sort_values()
    if a.empty:
        continue
    s = {"n": int(a.size), "zero": int((a < 1e-9).sum()), "median": float(a.median()),
         "p90": float(a.quantile(.90)), "p95": float(a.quantile(.95)), "max": float(a.max()),
         "gt1": int((a > 1).sum()), "gt3": int((a > 3).sum())}
    summ[t] = s
    print(f"{t:<5} {s['n']:>8} {s['zero']:>5} {s['median']:>7.3f}% {s['p90']:>7.3f}% "
          f"{s['p95']:>7.3f}% {s['max']:>7.3f}% {s['gt1']:>6} {s['gt3']:>6}")
a = all_d["dev_pct"].abs()
print(f"{'GỘP':<5} {a.size:>8} {int((a<1e-9).sum()):>5} {a.median():>7.3f}% {a.quantile(.90):>7.3f}% "
      f"{a.quantile(.95):>7.3f}% {a.max():>7.3f}% {int((a>1).sum()):>6} {int((a>3).sum()):>6}")

json.dump({"A_doi_soat_0814": rows, "B_phan_bo_12m": summ,
           "B_gop": {"n": int(a.size), "median": float(a.median()), "p90": float(a.quantile(.90)),
                     "p95": float(a.quantile(.95)), "max": float(a.max()),
                     "gt1pct": int((a > 1).sum()), "gt3pct": int((a > 3).sum())}},
          open(f"{D}/../vwap_vs_close.json", "w"), ensure_ascii=False, indent=1)
all_d.to_csv(f"{D}/../vwap_daily.csv", index=False)
