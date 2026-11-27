#!/usr/bin/env python3
"""Selfcheck B1+B2 của Value Radar (job Taylor_20261123_174706). Không cần BQ (panel R1 đóng băng + cache radar).
Chạy: env -u TZ python3 value_radar_norm5_selfcheck.py ; TZ=Asia/Ho_Chi_Minh python3 value_radar_norm5_selfcheck.py"""
import json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import value_radar as v

# Fixture đóng băng NẰM TRONG GIT (data/fixtures/value_radar_norm5/README.md). Trước 11-27 đọc thẳng thư mục
# research của mike; file tham chiếu bị xoá khỏi đó 25/11 ⇒ selfcheck đỏ dù production không đổi.
FIX = os.path.join(HERE, "data", "fixtures", "value_radar_norm5")
fails = []
def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not ok: fails.append(name)

# ---- B1 parity: panel R1 đóng băng -> norm5_series == R1 basket_monthly (mọi tháng)
p = pd.read_parquet(f"{FIX}/panel.parquet"); p["time"] = pd.to_datetime(p["time"])
p["mcap"] = p["Price"] * p["OShares"]; p["book"] = p["BVPS"] * p["OShares"]
p["np_ttm"] = p[["NP_P0", "NP_P1", "NP_P2", "NP_P3"]].sum(axis=1, min_count=4)
P = p[["time", "ticker", "mcap", "book", "np_ttm"]]
b = v.norm5_series(P)
ref = pd.read_csv(f"{FIX}/basket_monthly.csv", parse_dates=["time"])
m = b.merge(ref, on="time")
d1 = (m["pe_norm5"] - m["pe_norm_np5"]).abs().max(); d2 = (m["eps_ratio5"] - m["eps_ttm_over_avg5"]).abs().max()
d3 = (m["p_pe_norm5"] - m["p10_pe_norm_np5"]).abs().max(); d4 = (m["p_eps_ratio5"] - m["p10_eps_ttm_over_avg5"]).abs().max()
check("B1 parity vs R1 basket_monthly (pe, eps, 2 phân vị) %d tháng" % len(m),
      max(d1 / 14, d2, d3, d4) < 1e-4 and len(m) >= 220, f"maxdiff={d1:.1e},{d2:.1e},{d3:.1e},{d4:.1e}; ref CSV ghi %.6g nên tol 1e-4")
S = json.load(open(f"{FIX}/summary.json"))["now"]; last = b.iloc[-1]
check("B1 hôm nay == R1 summary.json (14,26 / p1,7 / 1,584 / p100)",
      abs(last.pe_norm5 - S["pe_norm_np5"]) < 1e-9 and abs(last.p_pe_norm5 - S["p10_pe_norm_np5"]) < 1e-9
      and abs(last.eps_ratio5 - S["eps_ttm_over_avg5"]) < 1e-9, f"{last.pe_norm5:.2f} p{last.p_pe_norm5:.1f} {last.eps_ratio5:.3f}")
# ---- nhân quả: cắt panel tại tháng k thì giá trị tại ≤k KHÔNG đổi (không look-ahead)
cut = pd.Timestamp("2022-06-30"); bc = v.norm5_series(P[P["time"] <= cut])
mm = bc.merge(b, on="time", suffixes=("_c", ""))
check("B1 nhân quả: cắt panel ≤2022-06 -> số tháng ≤ đó giữ nguyên", len(mm) > 100 and
      np.nanmax(np.abs(mm.pe_norm5_c - mm.pe_norm5)) < 1e-12 and np.nanmax(np.abs(mm.p_pe_norm5_c - mm.p_pe_norm5)) < 1e-12)
# ---- mutation: 4 mốc thay 5 => số phải đổi (selfcheck có răng)
orig = v._lagged_mean5
def mut(s):
    vals = []
    for k in range(4):
        x = s.copy(); x.index = pd.MultiIndex.from_arrays([x.index.get_level_values(0), x.index.get_level_values(1) + 12 * k]); vals.append(x.rename(f"l{k}"))
    mm_ = pd.concat(vals, axis=1).reindex(s.index); return mm_.mean(axis=1).where(mm_.notna().sum(axis=1) >= 4)
v._lagged_mean5 = mut; bm = v.norm5_series(P); v._lagged_mean5 = orig
check("B1 mutation (4 mốc thay 5) bị bắt", abs(bm.iloc[-1].pe_norm5 - last.pe_norm5) > 0.05)
# ---- cờ đỉnh
check("B1 cờ LỢI NHUẬN ĐỈNH bật khi p≥90 (hôm nay p100)", bool(last.p_eps_ratio5 >= v.PEAK_PCT))
# ---- B2: knob
os.environ.pop("VALUE_RADAR_DEP_BASIS", None)
dn = v.load_series(update=False)
os.environ["VALUE_RADAR_DEP_BASIS"] = "effective"; de = v.load_series(update=False)
os.environ.pop("VALUE_RADAR_DEP_BASIS")
chg = dn.loc[(dn.deposit_rate - de.deposit_rate).abs() > 1e-9, "time"]
check("B2 mặc định: nguồn lãi huy động = big4_12m suốt chuỗi", (dn["deposit_rate_source"] == "big4_12m").all())
check("B2 knob effective khôi phục CCTG (hôm nay 7,4, tag cctg)", abs(de.iloc[-1].deposit_rate - 7.4) < 1e-9 and de.iloc[-1].deposit_rate_source.startswith("cctg"),
      f"{de.iloc[-1].deposit_rate} {de.iloc[-1].deposit_rate_source}")
check("B2 chỉ khác từ 2026-09-30 (trước đó byte-giống)", len(chg) > 0 and chg.min() >= pd.Timestamp("2026-09-30"), f"{len(chg)} phiên từ {chg.min().date()}")
check("B2 pe_cap10/pb_cap10/p_pe/p_pb KHÔNG đổi giữa 2 cơ sở", np.allclose(dn.p_pe.fillna(-1), de.p_pe.fillna(-1)) and np.allclose(dn.p_pb.fillna(-1), de.p_pb.fillna(-1)))
# ---- định dạng dòng
v._CACHE_NOW.update(t=0, val=None)
os.environ["VALUE_RADAR_NORM5_CACHE"] = os.environ.get("VALUE_RADAR_NORM5_CACHE", "")
import time as _t
fake = dict(pe_norm5=14.26, p_pe_norm5=1.7, eps_ratio5=1.58, p_eps_ratio5=100.0, cov5=.94, peak=True, asof="2026-11-23")
v._NORM5_NOW.update(t=_t.time() + 1e6, val=fake)
cur = dict(score=1.0, label="CHEAP", score_expanding=8.2, label_expanding="CHEAP", pe_cap10=9.66, p_pe=0, pb_cap10=1.68, p_pb=2,
           spread=3.56, p_sp=1, deposit_rate=6.8, deposit_rate_source="big4_12m", asof="2026-11-23", window="rolling-10Y")
v._CACHE_NOW.update(t=_t.time() + 1e6, val=cur)
base = v.build_value_radar_line(html=False)
withn = v.build_value_radar_line(html=False, with_norm5=True)
check("Định dạng: mặc định KHÔNG có dòng norm5 (consumer không đổi)", "chuẩn hoá" not in base and base.count("\n") == 1)
check("Định dạng: with_norm5 = dòng chính nguyên vẹn + 1 dòng phụ có cờ", withn.startswith(base) and withn.count("\n") == 2 and "LỢI NHUẬN ĐỈNH" in withn)
# val=None KHÔNG phải cache hit (value_radar_norm5_now tính lại, gọi BQ thật) ⇒ ép nguồn panel NÉM LỖI
# để đi đúng nhánh try/except của production.
def _boom(*a, **k): raise RuntimeError("selfcheck: nguồn norm5 hỏng")
orig_up = v.update_norm5_panel; v.update_norm5_panel = _boom
v._NORM5_NOW.update(t=0.0, val=None)
check("Fail-safe: norm5 None -> chỉ còn dòng chính", v.build_value_radar_line(html=False, with_norm5=True) == base)
v.update_norm5_panel = orig_up
print("TZ=%r -> %s" % (os.environ.get("TZ"), "ALL PASS" if not fails else f"FAIL {fails}"))
sys.exit(1 if fails else 0)
