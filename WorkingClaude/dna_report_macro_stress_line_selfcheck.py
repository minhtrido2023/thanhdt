#!/usr/bin/env python3
"""Selfcheck dna_report.build_macro_stress_line(): đủ dữ liệu / thiếu dữ liệu / ledger rỗng / lỗi.
Không BQ, không mạng, không ghi sổ thật: dùng macro_stress_ledger.run với df tổng hợp,
MSL_LEDGER trỏ file tạm, state_fn giả. Chạy dưới `env -u TZ` và TZ=Asia/Tokyo."""
import os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TMP = tempfile.mkdtemp()
os.environ["MSL_LEDGER"] = os.path.join(TMP, "ledger.csv")   # TRƯỚC khi import module sổ
import pandas as pd
import dna_report as dr
sys.path.insert(0, dr._HAZ_DIR)
import macro_stress_ledger as msl
N = 0


def check(label, cond):
    global N
    N += 1
    assert cond, f"FAIL [{label}]"
    print(f"  ok: {label}")


def synth(last="2026-11-18", flat=True):
    idx = pd.bdate_range(end=last, periods=400)
    rows = []
    for k, v in (("vn_usdvnd", 25000.0), ("vn_bond_10y", 3.0), ("vn_interbank_3m", 4.0),
                 ("us_dxy", 100.0)):
        rows += [{"k": k, "d": d, "v": v} for d in idx]
    rows += [{"k": "vn_policy_rate", "d": idx[0], "v": 4.5}]
    return pd.DataFrame(rows)


def patch(df):
    def fake_run(write=True, df_=df):
        return orig(write=write, df=df_, asof=pd.Timestamp("2026-11-19"), state_fn=lambda d: ("NEUTRAL", "fake"))
    msl.run = fake_run


orig = msl.run

def reset():
    dr._MSTRESS_CACHE.update(t=0.0, val=None)

# 1) đủ dữ liệu: dòng có nhãn giả thuyết, 4 trigger, KHÔNG FIRE (series phẳng), sổ rỗng ⇒ cụm 0/10
patch(synth()); reset()
line = dr.build_macro_stress_line()
check("đủ dữ liệu: có dòng", isinstance(line, str) and line.startswith("Macro-stress sổ"))
check("giữ nhãn GIẢ THUYẾT CHƯA KIỂM", "GIẢ THUYẾT CHƯA KIỂM" in line)
check("đủ 4 trigger", all(k in line for k in msl.TRIGGERS))
check("không FIRE trên series phẳng", "[FIRE]" not in line)
check("ledger rỗng ⇒ cụm 0/10, 0/5", "cụm 0/10" in line and "0/5" in line)
check("ledger rỗng không tạo file khi không có episode", not os.path.exists(os.environ["MSL_LEDGER"]))
# cache: lần 2 không gọi lại run
msl.run = lambda **k: (_ for _ in ()).throw(AssertionError("không được gọi lại"))
check("cache 900s", dr.build_macro_stress_line() == line)

# 2) thiếu dữ liệu (quan sát cuối cũ >7 ngày) ⇒ run() trả dòng 'không có dữ liệu tươi'
patch(synth(last="2026-10-01")); reset()
line2 = dr.build_macro_stress_line()
check("stale ⇒ 'không có dữ liệu tươi'", isinstance(line2, str) and "không có dữ liệu tươi" in line2)

# 3) lỗi (BQ chết) ⇒ None, không raise
def boom(**k): raise RuntimeError("bq FAIL")
msl.run = boom; reset()
check("lỗi ⇒ None (ẩn dòng)", dr.build_macro_stress_line() is None)

# 4) thêm đúng 1 hàm: các builder anh em vẫn nguyên
check("builder cũ còn nguyên", all(hasattr(dr, n) for n in
      ("build_dt_gate_line", "build_value_radar_line", "build_cap_signal_advisory_line")))
print(f"ALL PASS ({N} checks)")
