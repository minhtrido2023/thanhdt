#!/usr/bin/env python3
"""E2 — (i) độ nhạy nhãn theo cửa sổ (5Y/7Y/10Y) và cắt tercile 25/75 vs 33/67; (ii) bảng 36 mã trước/sau v2.
"giữ" = nhãn y hệt cấu hình gốc (10Y, 33/67). Cả nhãn v1 (trước hạ) và v2 (sau hạ). Không đọc đồng hồ."""
import os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "bin"))
import pandas as pd
import dd_history_label as L

base, meta = L.run(None)
cfg = {"5Y": dict(win_years=5), "7Y": dict(win_years=7), "tercile25/75": dict(lo=25.0, hi=75.0)}
out = []
for name, kw in cfg.items():
    v, _ = L.run(None, **kw)
    m = base.merge(v, on="ticker", suffixes=("", "_v"))
    k1 = int((m.label_v1 == m.label_v1_v).sum())
    k2 = int((m.label == m.label_v).sum())
    # chỉ trong các mã có nhãn v1 xác định ở gốc
    d = m[m.label_v1.isin(L.DEFINITE)]
    kd = int((d.label_v1 == d.label_v1_v).sum())
    out.append((name, k1, k2, kd, len(d)))
    print(f"{name}: giữ nhãn v1 {k1}/36 · giữ nhãn v2 {k2}/36 · (trong {len(d)} mã v1 xác định: giữ {kd})")
# trước/sau
b = base
dem = b[(b.label != b.label_v1)]
print(f"\nnhãn v1 → v2: {len(dem)}/36 mã bị hạ. v1 xác định (RẺ/TT/ĐẮT) = {int(b.label_v1.isin(L.DEFINITE).sum())}")
print("theo lý do (mã có thể có cả hai):  proxy lệch k:", int(dem.demote_k.sum()), " N_eff<2,5:", int(dem.demote_neff.sum()),
      " chỉ k:", int(((dem.demote_k == 1) & (dem.demote_neff == 0)).sum()),
      " chỉ Neff:", int(((dem.demote_k == 0) & (dem.demote_neff == 1)).sum()),
      " cả hai:", int(((dem.demote_k == 1) & (dem.demote_neff == 1)).sum()))
cls = lambda s: "KHÔNG CHẮC" if s.startswith("KHÔNG CHẮC") else s  # noqa: E731
print("phân bố v1:", b.label_v1.map(cls).value_counts().to_dict())
print("phân bố v2:", b.label.map(cls).value_counts().to_dict())
skp = ["CST","CSV","DGC","HHS","MVC","PAT","PNJ","QTP","TCH","TV1"]
kout = sorted(b[b.demote_k == 1].ticker) if False else sorted(b[b.reasons.fillna("").str.contains("proxy")].ticker)
print("mã có cờ k ngoài [0,5;2]:", len(kout), kout, "· khớp danh sách skeptic:", kout == sorted(skp))
dec = b[b.warn.fillna("").str.contains("SỤT")]
print("cờ SỤT:", sorted(dec.ticker), "· nhãn v1 RẺ trong đó:", sorted(dec[dec.label_v1 == "RẺ"].ticker))
os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
b[["ticker", "label_v1", "label", "reasons", "demote_k", "demote_neff", "warn", "pct_fade", "pct_hold", "n_eff_hold",
   "k_fade", "k_hold"]].to_csv(os.path.join(HERE, "out", "before_after_v2_2026-11-20.csv"), index=False, float_format="%.6g")
pd.DataFrame(out, columns=["variant", "keep_v1", "keep_v2", "keep_v1_among_definite", "n_definite"]).to_csv(
    os.path.join(HERE, "out", "sensitivity_v2_2026-11-20.csv"), index=False)

# SIP caveat: cổ tức tiền 4.500đ/cp ex 19/11 (trước asof 20/11) trong khi BVPS còn quý trước ⇒ trừ 4.500 khỏi BV/cp
# CHỈ ở dòng asof (BV/cp = Price/PB), tâm + lịch sử giữ nguyên. Số 4.500 do Mike/skeptic cung cấp trong brief, chưa tự đối soát nguồn.
panel = pd.read_parquet(L.resolve(L.PANEL_REL))
T = panel.time.max()
m = (panel.ticker == "SIP") & (panel.time == T)
px, pb = float(panel.loc[m, "Price"].iloc[0]), float(panel.loc[m, "PB"].iloc[0])
print("\nSIP caveat (BV/cp asof = %.0f)" % (px / pb))
for div in (0, 4500):
    pn = panel.copy()
    pn.loc[m, "PB"] = px / (px / pb - div)
    r = L.run(["SIP"], panel_df=pn)[0].iloc[0]
    print(f"  trừ {div}: p[fade {r.pct_fade:.0f}, hold {r.pct_hold:.0f}] · nhãn v1 {r.label_v1} · nhãn v2 {r.label}")
