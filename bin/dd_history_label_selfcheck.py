#!/usr/bin/env python3
"""Selfcheck cho bin/dd_history_label.py. Chạy: $DNA_PYEXE bin/dd_history_label_selfcheck.py
Kiểm: (1) parity hàm V/BV với D1 proxy.py · (2) parity k_mã/pv hôm nay với D2 g1_dd_vs_proxy_d2.csv (cơ sở avg5,
Big-4) cho FPT, VCB và cả sổ · (3) nhân quả/PIT: cắt panel tại T ≡ asof=T trên panel đủ; dữ liệu SAU T bị phá
không đổi kết quả · (4) mutation: ROE5Y lịch sử dời ⇒ nhãn đổi; k lệch giữa lịch sử và hôm nay ⇒ nhãn đổi;
k đổi NHẤT QUÁN (tâm ×1,3) ⇒ nhãn KHÔNG đổi (tính chất thiết kế) · (5) luật nhãn tổng hợp (tercile, vắt ngưỡng,
<36 tháng) · (6) tất định: 2 lần chạy md5 CSV trùng. Không đọc đồng hồ; chạy dưới env -u TZ và TZ=Asia/Ho_Chi_Minh.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import hashlib
import sys
import tempfile

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import dd_history_label as L  # noqa: E402

FAIL = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAIL.append(msg)


# (1) parity hàm với D1
sys.path.insert(0, os.path.dirname(L.resolve(os.path.join(L.RES, "D1", "calc", "proxy.py"))))
import proxy as P  # noqa: E402
rng = np.random.default_rng(7)
roe = rng.uniform(-0.2, 0.45, 500)
r = rng.uniform(0.09, 0.2, 500)
g = 0.5 * np.clip(roe, 0, None)
check(np.allclose(L.vbv_dd(roe, r, g), P.vbv_dd(roe, r, g), rtol=0, atol=1e-12)
      and np.allclose(L.vbv_fade(roe, r), P.vbv_fade(roe, r), rtol=0, atol=1e-12),
      "(1) vbv_dd/vbv_fade trùng D1 proxy.py trên 500 điểm ngẫu nhiên (atol 1e-12)")

# (2)+ chạy trên SỔ ĐÓNG BĂNG đúng vintage D2: sổ sống đổi tâm theo từng lượt DD recheck ⇒ parity k so D2 đỏ oan
L.LEDGER_REL = os.path.join("bin", "fixtures", "dd_history_label", "ledger_d2.json")

# (2) parity với D2
df, meta = L.run(None)
check(len(df) == 36 and (df.label.notna()).all(), f"(2a) sổ có 36 mã có tâm, mỗi mã có nhãn (n={len(df)})")
d2 = pd.read_csv(L.resolve(os.path.join(L.RES, "rerun", "D2", "out", "g1_dd_vs_proxy_d2.csv"))).set_index("ticker")
m = df.set_index("ticker").join(d2[["ddop_avg5_b4_hold", "ddop_avg5_b4_fade", "pc_asof", "center"]], rsuffix="_d2")
for tk in ("FPT", "VCB"):
    x = m.loc[tk]
    check(abs(x.k_hold / x.ddop_avg5_b4_hold - 1) < 1e-4 and abs(x.k_fade / x.ddop_avg5_b4_fade - 1) < 1e-4
          and abs(x.pc_asof / x.pc_asof_d2 - 1) < 1e-4,
          f"(2b) {tk}: k_hold {x.k_hold:.5g}≈D2 {x.ddop_avg5_b4_hold:.5g}, k_fade {x.k_fade:.5g}≈D2 "
          f"{x.ddop_avg5_b4_fade:.5g}, giá/tâm {x.pc_asof:.5g}≈D2 {x.pc_asof_d2:.5g}")
mm = m.dropna(subset=["ddop_avg5_b4_hold", "k_hold"])
rel = np.nanmax(np.abs(np.r_[mm.k_hold / mm.ddop_avg5_b4_hold, mm.k_fade / mm.ddop_avg5_b4_fade] - 1))
check(rel < 1e-4, f"(2c) parity k toàn sổ với D2: {len(mm)} mã, lệch tương đối max {rel:.2e} (<1e-4, CSV D2 5 chữ số)")
med_k = float(np.median(mm.k_fade))
check(abs(med_k - 0.954) < 0.005, f"(2d) trung vị k_fade sổ = {med_k:.4f} ≈ k universe D2 §6 TB5Y fade 0,954")

# (3) nhân quả / PIT
panel = pd.read_parquet(meta["inputs_path"]["panel"])
T = pd.Timestamp("2025-06-30")
assert (panel.time == T).any()
a, _ = L.run(None, asof=T)
cut, _ = L.run(None, asof=T, panel_df=panel[panel.time <= T])
bad = panel.copy()
fut = bad.time > T
bad.loc[fut, ["PB", "PE", "ROE5Y", "Price"]] = bad.loc[fut, ["PB", "PE", "ROE5Y", "Price"]] * 7.0
pois, _ = L.run(None, asof=T, panel_df=bad)
cols = ["ticker", "label", "pct_fade", "pct_hold", "n_hold", "k_hold"]
same = lambda u, v: u[cols].fillna(-9).round(9).equals(v[cols].fillna(-9).round(9))  # noqa: E731
check(same(a, cut), f"(3a) asof={T.date()} trên panel đủ ≡ panel cắt tại T (36 mã)")
check(same(a, pois), "(3b) phá dữ liệu SAU T (×7 PB/PE/ROE5Y/Price) không đổi kết quả tại T")
check(int(a.n_hold.max()) <= 119, f"(3c) cửa sổ chỉ quá khứ: n_hold max tại T = {int(a.n_hold.max())} (≤119, loại tháng T)")

# (4) mutation
base = df.set_index("ticker")
shift = panel.copy()
shift.loc[shift.time < panel.time.max(), "ROE5Y"] = shift.loc[shift.time < panel.time.max(), "ROE5Y"] + 0.05
ms, _ = L.run(None, panel_df=shift)
nchg = int((ms.set_index("ticker").label != base.label).sum())
check(nchg >= 3, f"(4a) mutation ROE5Y lịch sử +5đpt ⇒ nhãn đổi ở {nchg}/36 mã (≥3)")
ok_rows = base[base.pct_hold.notna()]
k_bad = []
k_same = []
rows = L.add_proxy(panel, pd.read_csv(meta["inputs_path"]["deposit_big4"], parse_dates=["time"]))[0]
for tk, x in ok_rows.iterrows():
    rt = rows[rows.ticker == tk]
    asof = rows.time.max()
    w = rt[(rt.time > asof - pd.DateOffset(years=10)) & (rt.time < asof)].pv_hold.dropna()
    w = w[w > 0].values
    x0 = x.price_asof / x.center
    k_bad.append(L.tercile(L.pct_rank(w / (1.2 * x.k_hold), x0)) != L.tercile(x.pct_hold))
    k_same.append(abs(L.pct_rank(w / x.k_hold, x0) - x.pct_hold) < 1e-9)
check(all(k_same), f"(4b) tính lại độc lập phân vị hold (k nhất quán) khớp tool ở {sum(k_same)}/{len(k_same)} mã")
check(sum(k_bad) >= 3, f"(4c) mutation k lệch (lịch sử dùng 1,2k, hôm nay k) ⇒ tercile hold đổi ở {sum(k_bad)}/{len(k_bad)} mã (≥3)")
led = L.resolve(L.LEDGER_REL)
import json  # noqa: E402
z = json.load(open(led))
for e in z["entries"]:
    if e.get("center"):
        e["center"] = e["center"] * 1.3
with tempfile.TemporaryDirectory() as td:
    lp = os.path.join(td, "z.json")
    json.dump(z, open(lp, "w"))
    sc, _ = L.run(None, ledger_path=lp)
sc = sc.set_index("ticker")
inv = (sc.label_v1 == base.label_v1).all() and np.allclose(sc.pct_hold.fillna(-1), base.pct_hold.fillna(-1))
lvl = np.allclose((sc.hist_med_hold * 1.3).dropna(), base.hist_med_hold.dropna(), rtol=1e-9)
check(inv and lvl, "(4d) tâm ×1,3 (k đổi nhất quán) ⇒ nhãn v1/phân vị KHÔNG đổi, chỉ thang trung vị lịch sử ÷1,3 "
      "(nhãn độc lập tâm — tính chất thiết kế, ghi trong REPORT)")

# (5) luật nhãn
check(L.tercile(32.9) == "RẺ" and L.tercile(33) == "TRUNG TÍNH" and L.tercile(67) == "TRUNG TÍNH"
      and L.tercile(67.1) == "ĐẮT", "(5a) tercile <33 / 33–67 / >67")
check(L.combine("ĐẮT", "RẺ") == "KHÔNG CHẮC (rẻ…đắt)" and L.combine("RẺ", "RẺ") == "RẺ",
      "(5b) vắt ngưỡng ⇒ KHÔNG CHẮC (thứ tự rẻ→đắt); cùng tercile ⇒ gán")
t = pd.date_range("2020-01-31", periods=37, freq="ME")
syn = pd.DataFrame({"time": t, "ticker": "ZZZ", "Price": 100.0, "PB": np.linspace(1, 2, 37), "PE": 10.0,
                    "ROE5Y": 0.15, "ICB_Code": 0.0})
synp, _ = L.add_proxy(syn, pd.DataFrame({"time": [pd.Timestamp("2010-01-01")], "deposit_rate": [6.8]}))
r36 = L.label_ticker(synp, 100.0, t[-1])
r35 = L.label_ticker(synp.iloc[1:], 100.0, t[-1])
check(r36["n_hold"] == 36 and r36["label_v1"] == "ĐẮT" and r36["pct_hold"] == 100.0,
      f"(5c) chuỗi tổng hợp PB tăng dần, 36 tháng quá khứ ⇒ p100 ĐẮT (được: {r36['label_v1']}, n={r36['n_hold']})")
check(r35["label"] == "KHÔNG ĐỦ LỊCH SỬ", f"(5d) 35 tháng ⇒ KHÔNG ĐỦ LỊCH SỬ (được: {r35['label']})")

# (7) v2 — cờ k-band, cờ sụt/đỉnh, cổng N_eff, display
DEF = L.DEFINITE
skp = ["CST", "CSV", "DGC", "HHS", "MVC", "PAT", "PNJ", "QTP", "TCH", "TV1"]
kflag = sorted(base[base.reasons.fillna("").str.contains("proxy lệch DD")].index)
check(kflag == sorted(skp), f"(7a) cờ k ngoài [0,5;2] (k_fade hoặc k_hold) = đúng 10 mã skeptic nêu: {kflag}")
okk = all(str(base.loc[t, "label"]).startswith("KHÔNG CHẮC (") for t in skp if base.loc[t, "label_v1"] in DEF)
check(okk and all("proxy lệch DD" in base.loc[t, "label"] for t in skp if base.loc[t, "label_v1"] in DEF),
      "(7b) mã ngoài dải k mà v1 xác định ⇒ nhãn v2 = KHÔNG CHẮC (proxy lệch DD, k=…) (không còn RẺ/ĐẮT trần)")
ne_lo = base[(base.n_eff_hold < L.NEFF_MIN) & base.label_v1.isin(DEF)]
check(len(ne_lo) > 0 and ne_lo.label.str.contains("N hiệu dụng thấp").all(),
      f"(7c) N_eff(hold)<{L.NEFF_MIN} & v1 xác định ⇒ KHÔNG CHẮC (N hiệu dụng thấp): {len(ne_lo)} mã")
keep = base[(base.n_eff_hold >= L.NEFF_MIN) & ~base.reasons.fillna("").str.contains("proxy") & base.label_v1.isin(DEF)]
check(len(keep) > 0 and (keep.label == keep.label_v1).all(),
      f"(7d) N_eff≥{L.NEFF_MIN} & k trong dải ⇒ nhãn v1 giữ nguyên: {len(keep)} mã")
und = base[~base.label_v1.isin(DEF)]
check((und.label == und.label_v1).all(), f"(7e) nhãn v1 đã KHÔNG CHẮC/khác ⇒ v2 không đổi chữ ({len(und)} mã)")
# cờ sụt/đỉnh: biên đối xứng, dựng bằng cách chỉnh PE dòng asof của FPT
def flag_at(ratio):
    pn = panel.copy()
    msk = (pn.ticker == "FPT") & (pn.time == pn.time.max())
    pn.loc[msk, "PE"] = pn.loc[msk, "PB"] / (ratio * pn.loc[msk, "ROE5Y"])
    return str(L.run(["FPT"], panel_df=pn)[0].iloc[0].warn)
check("SỤT" in flag_at(0.76) and "SỤT" not in flag_at(0.78) and "ĐỈNH" not in flag_at(0.76),
      "(7f) cờ SỤT bật ở ROE TTM/5Y=0,76, tắt ở 0,78 (ngưỡng 1/1,3=0,769)")
check("ĐỈNH" in flag_at(1.31) and "ĐỈNH" not in flag_at(1.29) and "SỤT" not in flag_at(1.31),
      "(7g) cờ ĐỈNH bật ở 1,31, tắt ở 1,29 (đối xứng, không dính cờ SỤT)")
sut = sorted(base[base.warn.fillna("").str.contains("SỤT")].index)
check(sut == ["CST", "DGC", "HHS", "PAT", "PNJ"], f"(7h) cờ SỤT trên sổ thật = {sut} (skeptic: HHS/DGC/CST/PAT/PNJ; PNJ 0,59 thuộc)")
# mutation: tắt cổng ⇒ không hạ; tắt ngưỡng cực cao ⇒ hạ mọi nhãn xác định
sv = (L.K_BAND, L.NEFF_MIN)
L.K_BAND, L.NEFF_MIN = (0.0, 1e9), 0.0
off, _ = L.run(None)
L.K_BAND, L.NEFF_MIN = (1e9, 2e9), 1e9
allx, _ = L.run(None)
L.K_BAND, L.NEFF_MIN = sv
check((off.label == off.label_v1).all(), "(7i) mutation: nới cổng (k-band rộng vô hạn, N_eff≥0) ⇒ v2 ≡ v1 36/36")
dd_ = allx[allx.label_v1.isin(DEF)]
check(len(dd_) > 0 and dd_.label.str.startswith("KHÔNG CHẮC").all(), "(7j) mutation: siết cổng cực đoan ⇒ MỌI nhãn xác định bị hạ")
# nhân tâm ×3: nhãn v1 giữ, nhưng k ra ngoài dải ⇒ cờ k bật (cờ k là thuộc tính của tâm, nhãn v1 thì không)
z3 = json.load(open(led))
for e in z3["entries"]:
    if e.get("center"):
        e["center"] = e["center"] * 3
with tempfile.TemporaryDirectory() as td:
    lp = os.path.join(td, "z3.json")
    json.dump(z3, open(lp, "w"))
    s3, _ = L.run(["FPT"], ledger_path=lp)
r3 = s3.iloc[0]
check(r3.label_v1 == base.loc["FPT", "label_v1"] and "proxy lệch DD" in r3.label,
      f"(7k) FPT tâm ×3: nhãn v1 {r3.label_v1} không đổi, k_hold={r3.k_hold:.2f}>2 ⇒ v2 hạ: {r3.label}")
ln = [L.display_line(r) for _, r in df.iterrows()]
check(all("trung vị" not in x and "× tâm" not in x and "×tâm" not in x and "KHÔNG dùng tâm DD" in x for x in ln),
      "(7l) dòng hiển thị 36 mã: không có mệnh đề 'trung vị … × tâm', có nhãn 'thước cơ học … KHÔNG dùng tâm DD'")

# (6) tất định
with tempfile.TemporaryDirectory() as td:
    h = []
    for i in range(2):
        d_, m_ = L.run(None)
        c, _ = L.write_out(d_, m_, os.path.join(td, str(i)), "all")
        h.append(hashlib.md5(open(c, "rb").read()).hexdigest())
check(h[0] == h[1], f"(6) 2 lần chạy ⇒ md5 CSV trùng {h[0]}")

print(f"TZ={os.environ.get('TZ', '<unset>')} · {'ALL PASS' if not FAIL else f'{len(FAIL)} FAIL'}")
sys.exit(1 if FAIL else 0)
