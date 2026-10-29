"""Phân phối tỉ lệ pha loãng theo phương thức + pha loãng THU TIỀN 12 tháng/mã → chọn ngưỡng X."""
import sys
import pandas as pd

d = pd.read_csv(sys.argv[1]); d["ex"] = pd.to_datetime(d.ex, errors="coerce")
WARN = {"Rights", "PP", "EMPL", "PUBL", "TRANS", "MERGER", "ICRE", "BBOD"}
print("tỉ lệ exercise_ratio theo phương thức (dòng D, 2025-26):")
for m, g in d[d.st == "D"].groupby("m"):
    r = g.ratio.dropna()
    print(f"  {m:7s} n={len(r):4d} med={r.median():.3f} p90={r.quantile(.9):.3f} max={r.max():.3f} 0-ratio={int((r == 0).sum())}")
asof = pd.Timestamp("2026-10-29")
w = d[(d.st == "D") & d.m.isin(WARN) & (d.ex > asof - pd.Timedelta(days=365)) & (d.ex <= asof)]
agg = w.groupby("ticker").ratio.apply(lambda s: (1 + s.fillna(0)).prod() - 1)
print(f"\nmã có ≥1 sự kiện WARN thực hiện trong 12 tháng: {len(agg)}; pha loãng THU TIỀN tích luỹ:")
for x in [0.02, 0.05, 0.10, 0.15, 0.20, 0.30]:
    print(f"  >{x:.0%}: {(agg > x).sum()}")
print("  quantiles", agg.quantile([.5, .75, .9]).round(3).to_dict())
print("  nêu tên:", agg.reindex(["SCL", "MBB", "VIB", "DSC", "VPB"]).round(4).to_dict())
emp = agg[w.groupby("ticker").m.apply(lambda s: set(s) == {"EMPL"})]
print(f"  mã CHỈ có ESOP: n={len(emp)} max={emp.max():.3f} p90={emp.quantile(.9):.3f}")
