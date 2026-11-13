"""Áp vá knob LAG_ADV_SRC (bq|fill|pit) vào pt_v23_audit_2014.py. Usage: python patch_advsrc.py <file>"""
import sys
p = sys.argv[1]; s = open(p, encoding="utf-8").read()
A = 'elif LAG_ADV_BASIS != "close": raise SystemExit(f"LAG_ADV_BASIS không hợp lệ: {LAG_ADV_BASIS!r} (price|close)")\n'
assert s.count(A) == 1, "anchor A"
s = s.replace(A, A + '''# LAG_ADV_SRC (2026-11-13, job Taylor_20261112_181209, Luồng A2 — RESEARCH; mặc định `bq` = byte-identical):
# nguồn số lượng CP của ADV book LAG. Đo trên cache 0729: BQ `Volume_3M_P50` = trung vị 60 DÒNG GỒM ngày t
# (khớp chính xác 98,3% dòng) và NULL trên ngày có giao dịch 2015Q3-2016Q2 (2015Q4 ~16K dòng) ⇒ LIQ_ZERO_BLOCK=lag
# chặn oan mã thanh khoản tốt. Engine tra ADV ở NGÀY FILL (T+1) ⇒ bản BQ gồm cả khối lượng ngày fill.
#   bq   = Volume_3M_P50 (hành vi cũ, không tag)
#   fill = COALESCE(Volume_3M_P50, trung vị Volume 60 dòng gồm t) × PxAdv(t) — CHỈ vá lỗ NULL, giữ định nghĩa BQ
#   pit  = trung vị Volume 60 dòng TRƯỚC t (t-60..t-1) × PxAdv(t-1) — không gồm ngày fill (PIT tại giờ mở cửa)
# min_periods = LAG_ADV_MINP (mặc định 20 dòng) cho đường tự tính.
LAG_ADV_SRC = os.environ.get("LAG_ADV_SRC", "bq").strip().lower()
LAG_ADV_MINP = int(os.environ.get("LAG_ADV_MINP", "20"))
if LAG_ADV_SRC not in ("bq", "fill", "pit"): raise SystemExit(f"LAG_ADV_SRC không hợp lệ: {LAG_ADV_SRC!r} (bq|fill|pit)")
if LAG_ADV_SRC != "bq": _qs_tag += f"_advsrc{LAG_ADV_SRC}" + ("" if LAG_ADV_MINP == 20 else f"mp{LAG_ADV_MINP}")
''')
B = 'LIQ_LAG = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,\n           "liquidity_lookup": liq_lag,'
assert s.count(B) == 1, "anchor B"
s = s.replace(B, '''if LAG_ADV_SRC != "bq":
    _vstart = (pd.Timestamp(START_DATE) - pd.Timedelta(days=200)).date()
    _vp = []
    for ci, ch in enumerate(_chunks):
        in_list = ",".join(f"'{t}'" for t in ch)
        _vp.append(bq(f"""SELECT t.ticker, t.time, t.Volume, t.Volume_3M_P50, COALESCE(t.Price, t.Close) AS PxAdv
FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '{_vstart}' AND DATE '{END_DATE}' AND t.ticker IN ({in_list})"""))
    _vv = pd.concat(_vp, ignore_index=True)
    _vv["time"] = pd.to_datetime(_vv["time"])
    _vv = _vv.sort_values(["ticker", "time"], kind="mergesort").reset_index(drop=True)
    _gv = _vv.groupby("ticker", sort=False)
    if LAG_ADV_SRC == "fill":
        _med = _gv["Volume"].transform(lambda x: x.rolling(60, min_periods=LAG_ADV_MINP).median())
        _vv["_advq"] = _vv["Volume_3M_P50"].where(_vv["Volume_3M_P50"].notna(), _med)
        _vv["_px"] = _vv["PxAdv"]
    else:
        _vv["_advq"] = _gv["Volume"].transform(lambda x: x.shift(1).rolling(60, min_periods=LAG_ADV_MINP).median())
        _vv["_px"] = _gv["PxAdv"].shift(1)
    _vv = _vv[(_vv["time"] >= pd.Timestamp(START_DATE)) & _vv["_advq"].notna() & _vv["_px"].notna()]
    _n_old = len(liq_lag)
    liq_lag = {(tk, d): float(a) * float(px) for tk, d, a, px in zip(_vv["ticker"], _vv["time"], _vv["_advq"], _vv["_px"])}
    print(f"  [LAG_ADV_SRC={LAG_ADV_SRC} minp={LAG_ADV_MINP}] liq_lag keys {_n_old:,} -> {len(liq_lag):,}; "
          f"<=0: {sum(1 for v in liq_lag.values() if v <= 0):,}", flush=True)
''' + B)
open(p, "w", encoding="utf-8").write(s)
print("patched", p)
