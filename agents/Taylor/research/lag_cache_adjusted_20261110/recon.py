# Đối soát pkl adjusted vs canonical. Chạy: $DNA_PYEXE recon.py > recon.txt
import sys, pandas as pd, numpy as np
sys.path.insert(0, "/home/trido/thanhdt/wt-lagadj-1110/WorkingClaude")
import lagged_cache_adjusted as L
W = "/home/trido/thanhdt/WorkingClaude"; R = sys.path[0] if False else __file__.rsplit("/", 1)[0]
pd.set_option("display.width", 200)
o = pd.read_pickle(f"{W}/data/earnings_px.pkl"); n = pd.read_pickle(f"{R}/earnings_px_adj.pkl")
oo = pd.read_pickle(f"{W}/data/lagged_pos_ov.pkl"); no = pd.read_pickle(f"{R}/lagged_pos_ov_adj.pkl")
for d in (o, n, oo, no): d["time"] = pd.to_datetime(d.time)
m = o.merge(n, on=["ticker", "time"], how="outer", suffixes=("_o", "_n"), indicator=True)
b = m[m._merge == "both"].copy(); b["r"] = b.Close_n / b.Close_o - 1; b["y"] = b.time.dt.year
b["seg"] = np.where(b.time <= "2026-06-18", "<=06-18", ">=06-19")
print("== Close: dòng chung", len(b), "| chỉ-cũ", (m._merge == "left_only").sum(), "| chỉ-mới", (m._merge == "right_only").sum())
print("== Close: tỉ lệ dòng |Δ|>0,1% theo đoạn")
g = b.groupby("seg").apply(lambda d: pd.Series({"rows": len(d), "eq(<=1e-9)": int((d.r.abs() <= 1e-9).sum()),
     "diff>0.1%": int((d.r.abs() > 1e-3).sum()), "tickers_diff": d[d.r.abs() > 1e-3].ticker.nunique()}))
print(g.to_string())
print("== theo năm (diff>0,1%)"); print(b[b.r.abs() > 1e-3].groupby("y").agg(rows=("r", "size"), tickers=("ticker", "nunique")).T.to_string())
mo = oo.merge(no, on=["ticker", "time"], how="inner", suffixes=("_o", "_n"))
ro = (mo.Open_n / mo.Open_o - 1).abs(); rv = (mo.Volume_3M_P50_n / mo.Volume_3M_P50_o - 1).abs()
print(f"== Open: {len(mo)} dòng chung, |Δ|>0,1%: {(ro>1e-3).sum()} | Volume_3M_P50 |Δ|>0,1%: {(rv>1e-3).sum()} (NaN cũ {mo.Volume_3M_P50_o.isna().sum()} / mới {mo.Volume_3M_P50_n.isna().sum()})")
# hệ số mỗi mã ở phiên <=06-18: một mã có đúng 1 hệ số không đổi trên đoạn <=06-18? (= chỉ khác cơ sở, không khác đường đi)
pre = b[b.seg == "<=06-18"]
k = pre.groupby("ticker").r.agg(lambda s: (1 + s).max() / (1 + s).min() - 1)
print(f"== đoạn <=06-18: mã có Δ: {int((pre.groupby('ticker').r.apply(lambda s: (s.abs()>1e-3).any())).sum())}; "
      f"trong đó hệ số KHÔNG hằng (max/min-1 >0,5%): {int((k > 5e-3).sum())}")
print(k[k > 5e-3].sort_values(ascending=False).head(15).to_string())
cnt = n[n.time >= "2026-06-01"].groupby("time").ticker.nunique()
cnto = o[o.time >= "2026-06-01"].groupby("time").ticker.nunique()
print(f"== số mã/phiên từ 2026-06-01: mới min {cnt.min()} ({cnt.idxmin().date()}), phiên <665: {(cnt<665).sum()}/{len(cnt)} | cũ min {cnto.min()}, phiên <665: {(cnto<665).sum()}")
for tag, d in [("CŨ canonical", o), ("MỚI adjusted", n)]:
    print(f"\n== top 20 |ret 1 phiên| Close từ 2026-06-01 — {tag}")
    print(L.one_day_jumps(d, 20, "2026-06-01").to_string(index=False))
fx = {"PHR": ("2026-09-08", "2026-09-16"), "VHM": ("2026-08-03", "2026-08-08"), "DRI": ("2026-09-05", "2026-09-24"), "TRC": ("2026-09-12", "2026-09-17")}
for tk, (a, z) in fx.items():
    x = m[(m.ticker == tk) & (m.time >= a) & (m.time <= z)][["time", "Close_o", "Close_n"]]
    x["ret_o%"] = (x.Close_o.pct_change() * 100).round(2); x["ret_n%"] = (x.Close_n.pct_change() * 100).round(2)
    print(f"\n== fixture {tk}"); print(x.to_string(index=False))
