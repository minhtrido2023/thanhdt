#!/usr/bin/env python3
"""Selfcheck cho dna_report.build_vn_liquidity_line() (D1, 05/11/2026) + dây nối deposit_cctg_trend_check.
Không BQ/mạng: loader giả trả DataFrame[k,d,v]. 'Hôm nay' truyền tường minh; chạy dưới env -u TZ và
TZ=America/New_York (§16/§19). Phân vị kiểm bằng tính độc lập (đếm tay), không gọi lại hàm đang test."""
import os, sys, datetime as dt
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dna_report as dr

F = 0
def ok(name, cond, extra=""):
    global F
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  " + str(extra))); F += 0 if cond else 1

TODAY = dt.date(2026, 11, 5)

def mk(last_ib="2026-11-02", ib_last_val=6.83, po_last="2026-10-31", n_years=14, drop=(), po_val=4.5):
    """interbank hằng ngày (T2-T6) 2012-02→last_ib; spread lịch sử = 0,5 +/- chu kỳ, giá trị cuối = ib_last_val."""
    days = pd.bdate_range("2012-02-01", last_ib)
    ib = [5.0 + (i % 10) * 0.1 for i in range(len(days))]   # 5.0..5.9 → spread 0.5..1.4 khi po=4.5
    ib[-1] = ib_last_val
    rows = [("vn_interbank_3m", d, v) for d, v in zip(days, ib)]
    for d in pd.date_range("2011-12-31", po_last, freq="ME"):   # policy tháng, hằng 4.5
        rows.append(("vn_policy_rate", d, po_val))
    df = pd.DataFrame(rows, columns=["k", "d", "v"])
    return df[~df.k.isin(drop)]

def line(df, html=False, today=TODAY):
    return dr.build_vn_liquidity_line(html=html, today=today, loader=lambda: df)

LAB = "GIẢ THUYẾT CHƯA KIỂM — chỉ hiển thị, không gate"
df = mk()
L = line(df)
ok("hiển thị: có spread +2.33pp", "+2.33pp" in L and "6.83%" in L and "4.50%" in L, L)
ok("có nhãn GIẢ THUYẾT CHƯA KIỂM", LAB in L, L)
ok("có ngày quan sát cuối + mốc 2012-01", "2026-11-02" in L and "từ 2012-01" in L, L)
# phân vị độc lập: giá trị cuối 2.33 > mọi spread cũ (<=1.4) ⇒ chỉ chính nó ≤ ⇒ 100%
ib = df[df.k == "vn_interbank_3m"]; n = len(ib)
ok("phân vị = 100% khi cao nhất mẫu (đếm tay)", "phân vị 100%" in L and "n=%d" % n in L, L)
# giá trị giữa mẫu: đặt cuối = 1.0pp ⇒ spread cũ ≤1.0 gồm 0.5..1.0 = 6/10 của mỗi chu kỳ
L2 = line(mk(ib_last_val=5.5))
vals = [5.0 + (i % 10) * 0.1 for i in range(n - 1)]
exp = (sum(1 for v in vals if v - 4.5 <= 1.0 + 1e-9) + 1) / n * 100
ok("phân vị giữa mẫu khớp tính tay (%.0f%%)" % exp, "phân vị %.0f%%" % exp in L2, L2)
ok("html=True có <b>/<i>, html=False không", "<b>" in line(df, True) and "<i>" in line(df, True) and "<b>" not in L and "<i>" not in L)
# fail-closed
nodata = lambda s: s.startswith("Thanh khoản VN: không có dữ liệu") and LAB in s and "pp" not in s.split("(")[0]
L = line(mk(last_ib="2026-10-30"), today=dt.date(2026, 11, 4)); ok("interbank cách 5d (biên) → vẫn hiển thị", "+" in L and "không có dữ liệu" not in L, L)
L = line(mk(last_ib="2026-10-30")); ok("interbank cách 6d → 'không có dữ liệu', không điền số cũ", nodata(L) and "6.83" not in L and "cách 6 ngày" in L, L)
L = line(mk(po_last="2026-07-31")); ok("policy cách >75d → không có dữ liệu", nodata(L) and "policy cuối" in L, L)
L = line(mk(po_last="2026-08-31")); ok("policy cách 66d (≤75) → hiển thị", "không có dữ liệu" not in L, L)
L = line(mk(drop=("vn_policy_rate",))); ok("thiếu policy → không có dữ liệu", nodata(L) and "thiếu series" in L, L)
L = line(mk(drop=("vn_interbank_3m",))); ok("thiếu interbank → không có dữ liệu", nodata(L), L)
L = line(pd.DataFrame(columns=["k", "d", "v"])); ok("DataFrame rỗng → không có dữ liệu", nodata(L), L)
def boom(): raise RuntimeError("bq boom123")
L = dr.build_vn_liquidity_line(html=False, today=TODAY, loader=boom)
ok("BQ lỗi → không có dữ liệu + trích nguyên văn (§29)", nodata(L) and "boom123" in L and "RuntimeError" in L, L)
short = mk(); short = short[(short.k != "vn_interbank_3m") | (short.d >= "2025-01-01") | (short.d == short[short.k == "vn_interbank_3m"].d.iloc[0])]
L = line(short); ok("mẫu <500 → không có dữ liệu", nodata(L) and "mẫu quá nhỏ" in L, L)
# không nhìn quá hôm nay: thêm obs tương lai không được dùng
fut = pd.concat([mk(), pd.DataFrame([("vn_interbank_3m", pd.Timestamp("2026-12-01"), 9.9)], columns=["k", "d", "v"])])
L = line(fut); ok("obs sau hôm nay bị bỏ", "9.90" not in L and "2026-11-02" in L, L)
# live path mặc định dùng ICT, không crash dưới TZ lạ (BQ có thể lỗi ⇒ vẫn là 1 dòng hợp lệ)
dr._LIQ_CACHE.update(t=0.0, val=None)
L = dr.build_vn_liquidity_line(html=False, loader=lambda: mk(last_ib="2026-01-02", po_last="2026-01-31"))
ok("today mặc định (ICT) chạy được, ra dòng hợp lệ", L.startswith("Thanh khoản VN:"), L)
# cache chỉ cho đường live (today/loader=None): đường test không đụng cache
dr._LIQ_CACHE.update(t=0.0, val=None); line(mk()); ok("đường test không ghi cache", dr._LIQ_CACHE["val"] is None)
# dây nối
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dna_report.py")).read()
ok("build_report gọi build_vn_liquidity_line", src.count("build_vn_liquidity_line()") == 1)
dep = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "deposit_cctg_trend_check.py")).read()
ok("deposit_cctg: dòng chỉ in ra stdout (không vào msg/state/exit)", "print(_liquidity_line())" in dep and "_liquidity_line" not in dep.split("def main")[1].replace("print(_liquidity_line())", ""))
import deposit_cctg_trend_check as dc
real = dr.build_vn_liquidity_line
dr.build_vn_liquidity_line = lambda **k: (_ for _ in ()).throw(RuntimeError("x9"))
o = dc._liquidity_line(); dr.build_vn_liquidity_line = real
ok("deposit_cctg: lỗi dna_report không làm hỏng, ra 'không có dữ liệu'", "không có dữ liệu" in o and LAB in o, o)
print("FAILS=%d" % F); sys.exit(1 if F else 0)
