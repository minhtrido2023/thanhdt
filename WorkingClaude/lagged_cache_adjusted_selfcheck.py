# -*- coding: utf-8 -*-
"""Selfcheck lagged_cache_adjusted.py + refresh_lagged_caches.py bước [1+2] (dựng lại toàn lịch sử, giá điều chỉnh).
  $DNA_PYEXE lagged_cache_adjusted_selfcheck.py            # unit + tích hợp
  $DNA_PYEXE lagged_cache_adjusted_selfcheck.py --mutate   # mỗi mutation phải làm ≥1 kiểm FAIL
Fixture GIÁ THẬT (đo 2026-11-10): FIX_NEW = tav2_bq.ticker sống (Close/Open điều chỉnh), FIX_OLD = pkl canonical
af4b8c1b/afb2484e (cơ sở lúc fetch) — PHR GDKHQ 09-11, VHM thưởng 2:1 08-06, DRI 09-22, TRC 09-15.
Chạy được dưới env -u TZ / TZ lạ (không đọc giờ hệ thống)."""
import os, sys, re, shutil, subprocess, tempfile, hashlib, pickle, fcntl
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.environ.get("LCA_MODULE_DIR", HERE)
sys.path.insert(0, MOD)
import lagged_cache_adjusted as L
FIX_NEW = [('PHR', '2026-09-08', 33670.0, 33990.0, 295300.0), ('PHR', '2026-09-09', 33340.0, 33720.0, 305200.0), ('PHR', '2026-09-10', 32800.0, 33340.0, 308350.0), ('PHR', '2026-09-11', 32800.0, 33350.0, 308350.0), ('PHR', '2026-09-14', 31100.0, 32600.0, 314300.0), ('PHR', '2026-09-15', 31400.0, 30950.0, 315007.5), ('PHR', '2026-09-16', 31750.0, 31500.0, 318481.5), ('VHM', '2026-08-03', 74000.0, 74350.0, 4594817.5), ('VHM', '2026-08-04', 76450.0, 74100.0, 4594817.5), ('VHM', '2026-08-05', 76500.0, 77100.0, 4594817.5), ('VHM', '2026-08-06', 77100.0, 81700.0, 4594817.5), ('VHM', '2026-08-07', 73000.0, 75300.0, 4594817.5), ('DRI', '2026-09-18', 13800.0, 13800.0, 473803.0), ('DRI', '2026-09-21', 13890.0, 13800.0, 481345.0), ('DRI', '2026-09-22', 14000.0, 14600.0, 473803.0), ('DRI', '2026-09-23', 14500.0, 14000.0, 473803.0), ('DRI', '2026-09-24', 14800.0, 14600.0, 481345.0), ('TRC', '2026-09-14', 20150.0, 20500.0, 59150.0), ('TRC', '2026-09-15', 21550.0, 21550.0, 60527.5), ('TRC', '2026-09-16', 22400.0, 21600.0, 67290.5), ('TRC', '2026-09-17', 22300.0, 22400.0, 74646.5)]
FIX_OLD = [('PHR', '2026-09-09', 61400.0, 62100.0, 305200.0), ('PHR', '2026-09-10', 60400.0, 61400.0, 308350.0), ('PHR', '2026-09-11', 32800.0, 33350.0, 309043.5), ('PHR', '2026-09-15', 31400.0, 30950.0, 314300.0), ('PHR', '2026-09-16', 31750.0, 31500.0, 318000.0), ('VHM', '2026-08-03', 148000.0, 148700.0, 4584994.0), ('VHM', '2026-08-04', 152900.0, 148200.0, 4584994.0), ('VHM', '2026-08-05', 153000.0, 154200.0, 4584994.0), ('VHM', '2026-08-06', 77100.0, 81700.0, 4594817.5), ('VHM', '2026-08-07', 73000.0, 75300.0, 4594817.5), ('DRI', '2026-09-18', 14800.0, 14800.0, 473700.0), ('DRI', '2026-09-21', 14900.0, 14800.0, 480950.0), ('DRI', '2026-09-22', 14000.0, 14600.0, 473803.0), ('DRI', '2026-09-23', 14500.0, 14000.0, 473803.0), ('DRI', '2026-09-24', 14800.0, 14600.0, 481345.0), ('TRC', '2026-09-15', 21550.0, 21550.0, 60450.0), ('TRC', '2026-09-16', 22400.0, 21600.0, 66950.0), ('TRC', '2026-09-17', 22300.0, 22400.0, 73850.0)]
COLS = ["ticker", "time", "Close", "Open", "Volume_3M_P50", "Price"]
RES = []
def ok(name, cond, info=""):
    RES.append((name, bool(cond))); print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  [{info}]"))
def fr(rows): d = pd.DataFrame(rows, columns=COLS[:5]); d["time"] = pd.to_datetime(d.time); d["Price"] = d.Close * 2.0; return d   # fixture không có Price thật

def synth(tickers=80, start="2026-05-01", end="2026-09-30", seed=0):
    """Khung tổng hợp: `tickers` mã × mọi ngày thường, giá ngẫu nhiên dương."""
    rng = np.random.default_rng(seed); days = pd.bdate_range(start, end)
    d = pd.DataFrame([(f"T{i:03d}", t) for i in range(tickers) for t in days], columns=["ticker", "time"])
    d["Close"] = 10000 * np.exp(rng.normal(0, .01, len(d)).cumsum() * 0 + rng.normal(0, .01, len(d)))
    d["Open"] = d.Close * 1.001; d["Volume_3M_P50"] = 1e5; d["Price"] = d.Close * 1.5
    return d

def stub_q(frame, calls=None):
    def q(sql):
        if calls is not None: calls.append(sql)
        a, b = re.findall(r"DATE '([0-9-]+)'", sql)
        return frame[(frame.time >= a) & (frame.time <= b)].copy()
    return q

def unit():
    new, old = fr(FIX_NEW), fr(FIX_OLD)
    # 1 fixture: cú rơi giả ở bản cũ, biến mất ở bản điều chỉnh
    def maxdrop(d, tk): x = d[d.ticker == tk].sort_values("time"); return (x.Close.pct_change()).min()
    for tk in ("PHR", "VHM", "DRI", "TRC"):
        if tk != "TRC":   # TRC: bản cũ THIẾU phiên 09-14 (lỗi thưa), không có cú rơi trong fixture
            ok(f"fixture {tk}: bản cũ có cú rơi giả < -5%", maxdrop(old, tk) < -0.05, maxdrop(old, tk))
        ok(f"fixture {tk}: bản điều chỉnh không có ngày < -10%", maxdrop(new, tk) > -0.10, maxdrop(new, tk))
    ok("fixture PHR 09-11 cũ -45,7% / mới 0,0%", abs(maxdrop(old, "PHR") + 0.457) < 0.001)
    ok("fixture VHM 08-06 cũ -49,6%", abs(maxdrop(old, "VHM") + 0.4961) < 0.001)
    # 2 pull_adjusted: chia năm, alias, lọc universe, dedupe, ns
    s = synth(5, "2025-12-25", "2026-01-08"); s = pd.concat([s, s.iloc[:3], s.assign(ticker="ZZZ")], ignore_index=True)
    calls = []; out = L.pull_adjusted(stub_q(s, calls), "2025-12-25", "2026-01-08", ["T000", "T001", "T002", "T003", "T004"])
    ok("pull: 2 khúc năm (2025, 2026)", len(calls) == 2 and "2025-12-31" in calls[0] and "2026-01-01" in calls[1], calls)
    ok("pull: qualify alias t. (bẫy tên bảng = tên cột)", all("tav2_bq.ticker AS t" in c and "t.Close > 0" in c for c in calls))
    ok("pull: lọc universe + dedupe", set(out.ticker) == {f"T00{i}" for i in range(5)} and not out.duplicated(["ticker", "time"]).any())
    ok("pull: time datetime64[ns]", str(out.time.dtype) == "datetime64[ns]")
    try: L.pull_adjusted(stub_q(s.iloc[:0]), "2026-01-01", "2026-01-05", ["T000"]); ok("pull: năm rỗng ⇒ raise", False)
    except RuntimeError: ok("pull: năm rỗng ⇒ raise", True)
    # 3 validate
    base = synth(80); end = base.time.max()
    p, st = L.validate(base, base[["ticker", "time", "Close"]], end); ok("validate: khung sạch ⇒ 0 vấn đề", p == [], p)
    p, _ = L.validate(base[base.time < end], base, end); ok("validate: max < END ⇒ vấn đề", any("END" in x for x in p), p)
    p, _ = L.validate(base, base, end + pd.Timedelta(days=3)); ok("validate: END ≠ max ⇒ vấn đề", any("END" in x for x in p), p)
    d0 = base.time.unique()[-5]; thin = base[~((base.time == d0) & (base.ticker > "T030"))]
    p, _ = L.validate(thin, thin, end); ok("validate: phiên thưa (31/80) ⇒ vấn đề", any("thưa" in x for x in p), p)
    wk = pd.concat([base, pd.DataFrame([["T000", pd.Timestamp("2026-07-05"), 1.0, 1.0, 1.0, 1.0]], columns=COLS)])
    p, _ = L.validate(wk, wk, end); ok("validate: dòng rác Chủ nhật 1 mã KHÔNG bị coi là phiên thưa", p == [], p)
    hole = base[~((base.ticker == "T010") & (base.time >= "2026-06-01") & (base.time < "2026-07-27"))]  # 1 mã × 40 phiên = 0,46%, mỗi phiên chỉ mất 1/80
    p, st = L.validate(hole, base, end); ok("validate: mất cặp (mã,phiên) > 0,2% ⇒ vấn đề", any("cặp" in x for x in p), (p, st))
    ok("validate: lỗ 0,46% không phạm luật mất-theo-phiên (tách đúng 2 luật)", not any("phiên mất" in x for x in p), p)
    drop = base[~((base.ticker < "T008") & (base.time == d0))]
    p, _ = L.validate(drop, base, end); ok("validate: phiên mất 10% số mã so với bản cũ ⇒ vấn đề", any("phiên mất" in x for x in p), p)
    bad = base.copy(); bad.loc[5, "Close"] = 0; p, _ = L.validate(bad, base, end); ok("validate: Close<=0 ⇒ vấn đề", any("Close" in x for x in p), p)
    # 4 carry_truncated
    old_c = base.copy(); new_c = base[~((base.ticker == "T001") & (base.time < "2026-08-01"))]
    out, summ = L.carry_truncated(new_c, old_c, COLS)
    ok("carry: mã bị BQ cắt đầu ⇒ mang dòng cũ sang, đủ khoá", len(out) == len(base) and list(summ.ticker) == ["T001"], summ)
    new_h = base[~((base.ticker == "T002") & (base.time >= "2026-08-03") & (base.time <= "2026-08-05"))]
    out, summ = L.carry_truncated(new_h, old_c, COLS)
    ok("carry: lỗ hổng GIỮA chuỗi KHÔNG mang sang", len(summ) == 0 and len(out) == len(new_h))
    new_g = base[base.ticker != "T003"]; out, summ = L.carry_truncated(new_g, old_c, COLS)
    ok("carry: mã biến mất hẳn ⇒ mang sang", list(summ.ticker) == ["T003"])
    # 5 build: >CARRY_TICKERS_MAX mã bị cắt ⇒ vấn đề; build sạch ⇒ 0
    px_o, ov_o = base[L.PX_COLS], base[L.OV_COLS]
    _, _, p, st, _ = L.build(stub_q(base), px_o, ov_o, end); ok("build: nguồn sạch ⇒ 0 vấn đề", p == [], p)
    cut = base[~((base.ticker < "T025") & (base.time < "2026-06-01"))]
    _, _, p, st, c = L.build(stub_q(cut), px_o, ov_o, end)
    ok("build: 25 mã bị cắt lịch sử (>20) ⇒ vấn đề", any("cắt lịch sử" in x for x in p), (p, st))
    npx, nov, p, _, _ = L.build(stub_q(fr(FIX_NEW)), fr(FIX_OLD)[L.PX_COLS], fr(FIX_OLD)[L.OV_COLS], fr(FIX_NEW).time.max())
    ok("build: fixture ⇒ px cột Close = giá điều chỉnh BQ", np.allclose(npx.merge(fr(FIX_NEW), on=["ticker", "time"]).eval("Close_x - Close_y"), 0))
    ok("build: ov giữ Open+Volume_3M_P50 điều chỉnh", list(nov.columns) == L.OV_COLS and np.allclose(nov.merge(fr(FIX_NEW), on=["ticker", "time"]).eval("Open_x - Open_y"), 0))

    # 3b validate: bản mới LÙI NGÀY so với bản cũ (mutation sống #a)
    e2 = base.time.unique()[-3]; p, _ = L.validate(base[base.time <= e2], base, e2)
    ok("validate: bản mới lùi ngày so với bản cũ ⇒ vấn đề", any("lùi ngày" in x for x in p), p)
    # 3c thin_sessions: trung vị 60 phiên TRƯỚC (shift) — phiên đang xét không tự kéo trung vị (mutation sống #d)
    idx = pd.bdate_range("2020-01-01", periods=42)
    cnt = pd.Series([80] * 21 + [30] * 21, index=idx)
    ok("thin: phiên 42 (30 mã) bị gắn thưa nhờ trung vị phiên TRƯỚC (80), không tự kéo trung vị xuống", idx[41] in L.thin_sessions(cnt).index,
       list(L.thin_sessions(cnt).index[-3:]))
    # 3d build/validate so với BẢN CŨ (mutation sống #b: validate(new,new) mù với mất khoá)
    hole_src = base[~((base.ticker == "T010") & (base.time >= "2026-06-01") & (base.time < "2026-07-27"))]
    _, _, p, st, _ = L.build(stub_q(hole_src), base[L.PX_COLS], base[L.OV_COLS], end)
    ok("build: nguồn mất >0,2% cặp (mã,phiên) so với pkl cũ ⇒ vấn đề", any("cặp" in x for x in p), (p, st))
    d1 = base.time.unique()[-5]
    drop_src = base[~((base.ticker < "T008") & (base.time == d1))]
    _, _, p, st, _ = L.build(stub_q(drop_src), base[L.PX_COLS], base[L.OV_COLS], end)
    ok("build: nguồn mất >5% mã trong 1 phiên so với pkl cũ ⇒ vấn đề", any("phiên mất" in x for x in p), (p, st))
    # 3e carry giữ ĐỦ cột (mutation sống #c): Open/Volume_3M_P50/Price của dòng mang sang = bản cũ, không NaN
    cut1 = base[~((base.ticker == "T001") & (base.time < "2026-08-01"))]
    npx, nov, p, st, car = L.build(stub_q(cut1), base[L.PX_COLS], base[L.OV_COLS], end)
    chk = nov[(nov.ticker == "T001") & (nov.time < "2026-08-01")]
    ok("build: dòng mang sang giữ Open/Volume_3M_P50/Price (không NaN)", len(chk) > 0 and not chk[["Open", "Volume_3M_P50", "Price"]].isna().any().any()
       and np.allclose(chk.merge(base, on=["ticker", "time"]).eval("Open_x - Open_y"), 0), chk.head(2))
    # 3f trần CARRY chỉ tính mã MỚI, qua nhiều ngày (B1)
    days = list(base.time.unique())
    srcA = base[~((base.ticker < "T015") & (base.time < "2026-06-01"))]                     # ngày 1: 15 mã bị cắt (≤20)
    nA_px, nA_ov, p, st, cA = L.build(stub_q(srcA), base[L.PX_COLS], base[L.OV_COLS], end)
    ok("carry nhiều ngày: ngày 1, 15 mã mới bị cắt ⇒ qua trần", p == [] and st["carried_new"] == 15, (p, st))
    known = set(cA.ticker)
    srcB = base[~((base.ticker < "T015") & (base.time < "2026-06-01")) & ~((base.ticker >= "T015") & (base.ticker < "T025") & (base.time < "2026-06-01"))]
    _, _, p, st, cB = L.build(stub_q(srcB), nA_px, nA_ov, end, known_carried=known)          # ngày 2: +10 mã mới ⇒ tổng 25 nhưng MỚI chỉ 10
    ok("carry nhiều ngày: ngày 2, 15 mã đã mang + 10 mã mới (tổng 25) ⇒ KHÔNG chặn", p == [] and st["carried_new"] == 10 and st["carried_tickers"] == 25, (p, st))
    _, _, p, st, _ = L.build(stub_q(srcB), nA_px, nA_ov, end, known_carried=set())          # không có state ⇒ coi 25 đều mới ⇒ chặn
    ok("carry nhiều ngày: không state ⇒ 25 mã mới > 20 ⇒ chặn", any("MỚI" in x for x in p), (p, st))
    srcC = base[~((base.ticker < "T045") & (base.time < "2026-06-01"))]
    _, _, p, st, _ = L.build(stub_q(srcC), nA_px, nA_ov, end, known_carried=known)          # ngày 3: +30 mã mới ⇒ chặn
    ok("carry nhiều ngày: +30 mã mới ⇒ chặn", any("MỚI" in x for x in p), (p, st))
    # 3g một snapshot cho mọi khúc (B7)
    sl = synth(3, "2024-12-20", "2026-01-10"); calls = []
    L.build(stub_q(sl, calls), sl[L.PX_COLS], sl[L.OV_COLS], sl.time.max())
    stamps = {m for c in calls for m in re.findall(r"FOR SYSTEM_TIME AS OF TIMESTAMP '([0-9TZ:-]+)'", c)}
    ok("snapshot: mọi khúc năm cùng 1 mốc FOR SYSTEM_TIME AS OF", len(calls) >= 3 and len(stamps) == 1 and all("SYSTEM_TIME" in c for c in calls), (len(calls), stamps))
    ok("snapshot: alias t. đứng TRƯỚC FOR SYSTEM_TIME (cú pháp BQ)", all(re.search(r"ticker AS t FOR SYSTEM_TIME", c) for c in calls))
    # 3h copy_atomic: lỗi giữa chừng không để bản cụt ở đích
    d_ = tempfile.mkdtemp(prefix="lca_ca_"); src_ = d_ + "/s.bin"; open(src_, "wb").write(b"x" * 1000)
    real = shutil.copy2
    def bad(a, b, **k): open(b, "wb").write(b"xx"); raise OSError("killed")
    L.shutil.copy2 = bad
    try: L.copy_atomic(src_, d_ + "/dst.bin")
    except OSError: pass
    L.shutil.copy2 = real
    ok("copy_atomic: bị kill giữa chừng ⇒ không có đích cụt, không sót tmp", not os.path.exists(d_ + "/dst.bin") and os.listdir(d_) == ["s.bin"], os.listdir(d_))
    L.copy_atomic(src_, d_ + "/dst.bin"); ok("copy_atomic: chạy bình thường ⇒ đích đủ byte", os.path.getsize(d_ + "/dst.bin") == 1000)
    shutil.rmtree(d_)
    # 6 live_bq gỡ BQ_LOCAL_CACHE trong lúc gọi, khôi phục sau (kể cả khi lỗi)
    os.environ["BQ_LOCAL_CACHE"] = "data/bq_cache"; seen = []
    L.live_bq(lambda s: seen.append(os.environ.get("BQ_LOCAL_CACHE")))("x")
    ok("live_bq: gọi BQ khi KHÔNG có BQ_LOCAL_CACHE", seen == [None], seen)
    ok("live_bq: khôi phục BQ_LOCAL_CACHE", os.environ.get("BQ_LOCAL_CACHE") == "data/bq_cache")
    try: L.live_bq(lambda s: 1 / 0)("x")
    except ZeroDivisionError: pass
    ok("live_bq: khôi phục cả khi lỗi", os.environ.get("BQ_LOCAL_CACHE") == "data/bq_cache")
    # 3h độ phủ Price / Volume_3M_P50 ở COVER_SESSIONS phiên gần nhất (C2, 2026-11-13)
    sess = np.sort(base.time.unique()); last5 = sess[-5:]
    for c in ("Price", "Volume_3M_P50"):
        b = base.copy(); b.loc[b.time.isin(last5), c] = np.nan; p, _ = L.validate(b, base, end)
        ok(f"phủ: {c} NaN toàn bộ 5 phiên cuối ⇒ vấn đề", any(c in x and "phiên" in x for x in p), p)
    b = base.copy(); rng = np.random.default_rng(1); w = b.time.isin(sess[-60:])
    b.loc[w & (rng.random(len(b)) < 0.03), "Price"] = np.nan; p, st = L.validate(b, base, end)
    ok("phủ: Price NaN rải 3% cửa sổ 60 phiên ⇒ vấn đề cửa sổ", any("Price NaN" in x and "gần nhất" in x for x in p), (p, st))
    b = base.copy(); b.loc[(b.time == sess[-1]) & (b.ticker < "T003"), "Price"] = np.nan; p, st = L.validate(b, base, end)
    ok("phủ: 3/80 mã (3,75%) NaN 1 phiên ⇒ KHÔNG chặn (dưới ngưỡng phiên 5%)", p == [], (p, st))
    b = base.copy(); b.loc[(b.time == sess[-1]) & (b.ticker < "T005"), "Price"] = np.nan; p, _ = L.validate(b, base, end)
    ok("phủ: 5/80 mã (6,25%) NaN 1 phiên ⇒ chặn", any("Price NaN >5%" in x for x in p), p)
    b = base.copy(); b.loc[b.time < sess[-60], "Price"] = np.nan; p, _ = L.validate(b, base, end)
    ok("phủ: NaN chỉ TRƯỚC cửa sổ 60 phiên ⇒ KHÔNG chặn", p == [], p)
    p, _ = L.validate(base.drop(columns="Price"), base, end)
    ok("phủ: thiếu cột Price ⇒ vấn đề", any("thiếu cột" in x for x in p), p)
    old_nan = base.copy(); old_nan.loc[old_nan.ticker < "T005", "Price"] = np.nan   # 5 mã mang sang: cơ sở cũ, không có Price
    cut5 = base[~(base.ticker < "T005")]
    _, nov5, p, st, car5 = L.build(stub_q(cut5), old_nan[L.PX_COLS], old_nan[L.OV_COLS], end)
    ok("phủ: NaN Price chỉ ở mã MANG SANG ⇒ KHÔNG chặn (loại khỏi phép đo)", p == [] and len(car5) == 5 and nov5.Price.isna().any(), (p, st))
    cut5b = cut5.copy(); cut5b.loc[cut5b.time == sess[-1], "Price"] = np.nan
    _, _, p, _, _ = L.build(stub_q(cut5b), old_nan[L.PX_COLS], old_nan[L.OV_COLS], end)
    ok("phủ: qua build, BQ trả Price NULL phiên cuối ⇒ chặn", any("Price NaN" in x for x in p), p)

STUB = r'''
import os, re, pandas as pd
def bq(sql):
    mode = os.environ["STUB_MODE"]; f = pd.read_pickle(os.environ["STUB_SRC"])
    if mode == "error" and "t.Close, t.Open" in sql and "BETWEEN" in sql: raise RuntimeError("bq CLI error: boom")
    if "MAX(t.time)" in sql: return pd.DataFrame({"mx": [f.time.max()]})
    if "tav2_bq.ticker AS t" in sql:
        if os.environ.get("BQ_LOCAL_CACHE"): raise RuntimeError("bước [1+2] đọc BQ_LOCAL_CACHE thay vì BQ sống")
        a, b = re.findall(r"DATE '([0-9-]+)'", sql); g = f[(f.time >= a) & (f.time <= b)]
        if mode == "thin": g = g[~((g.time == f.time.max()) & (g.ticker > "T020"))]
        if mode == "nullprice": g = g.assign(Price=g.Price.where(g.time < f.time.max()))
        return g.copy()
    if "ticker_financial" in sql:
        d = pd.DataFrame({"ticker": ["T001"], "quarter": ["2026Q2"], "time": [pd.Timestamp("2026-06-30")],
             "Release_Date": [pd.Timestamp("2026-07-20")], "NP_R": [0.3], "Revenue_YoY_P0": [0.1]})
        for i in range(8): d[f"NP_P{i}"] = 1.0
        return d
    raise RuntimeError("stub: SQL lạ " + sql[:80])
'''

def integ():
    md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()
    root = tempfile.mkdtemp(prefix="lca_sc_"); os.makedirs(root + "/data")
    open(root + "/simulate_holistic_nav.py", "w").write(STUB)
    src = synth(80, "2026-03-02", "2026-09-30"); src.to_pickle(root + "/src.pkl")
    old = src[src.time < "2026-09-30"].copy(); old["Close"] *= 1.07   # bản cũ: thiếu phiên cuối, cơ sở khác
    PX, OV = root + "/data/earnings_px.pkl", root + "/data/lagged_pos_ov.pkl"
    def reset():
        for p_ in (PX, OV, PX + ".prev", OV + ".prev", PX + ".pre_adj", OV + ".pre_adj"):
            if os.path.exists(p_): os.remove(p_)
        old[L.PX_COLS].to_pickle(PX); old[L.OV_COLS].to_pickle(OV)
    script = os.path.join(MOD, "refresh_lagged_caches.py")
    def run(mode, srcp="/src.pkl", kill_copy=False, inject=None):
        env = {**os.environ, "LAGCACHE_WORKDIR": root, "STUB_MODE": mode, "STUB_SRC": root + srcp, "BQ_LOCAL_CACHE": "data/bq_cache"}
        cmd = [sys.executable, script]
        if kill_copy:   # shutil.copy2 ghi dở rồi chết — mô phỏng bị kill giữa lúc chép .pre_adj
            cmd = [sys.executable, "-c", "import shutil,runpy,sys\ndef bad(a,b,**k):\n open(b,'wb').write(b'xx'); raise OSError('killed')\n"
                   "import os; sys.path.insert(0, os.path.dirname(sys.argv[1])); shutil.copy2=bad; sys.argv=[sys.argv[1]]; runpy.run_path(sys.argv[0], run_name='__main__')", script]
        if inject:      # mã Python chạy trước script (giả lập bị kill ở một bước cụ thể)
            cmd = [sys.executable, "-c", "import runpy,sys,os\n" + inject + "\nsys.path.insert(0, os.path.dirname(sys.argv[1])); sys.argv=[sys.argv[1]]; runpy.run_path(sys.argv[0], run_name='__main__')", script]
        return subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=600)
    STATE = root + "/data/lagged_carried.json"
    reset(); m0 = (md5(PX), md5(OV)); r = run("good")
    ok("tích hợp good: exit 0", r.returncode == 0, r.stdout[-800:] + r.stderr[-800:])
    npx = pd.read_pickle(PX)
    ok("tích hợp good: pkl = nguồn điều chỉnh (Close khớp, có phiên cuối)", npx.time.max() == src.time.max()
       and np.allclose(npx.merge(src, on=["ticker", "time"]).eval("Close_x - Close_y"), 0))
    ok("tích hợp good: .prev = bản trước, .pre_adj = bản trước", md5(PX + ".prev") == m0[0] and md5(PX + ".pre_adj") == m0[0] and md5(OV + ".pre_adj") == m0[1])
    ok("tích hợp good: ghi state lagged_carried.json (0 mã mang sang)", os.path.exists(STATE) and __import__("json").load(open(STATE))["tickers"] == [])
    ok("tích hợp good: Price thô vào lagged_pos_ov.pkl", "Price" in pd.read_pickle(OV).columns)
    ok("tích hợp good: không sót .tmp", not [f for f in os.listdir(root + "/data") if f.endswith(".tmp")])
    m1 = md5(PX); r = run("good")
    ok("tích hợp good lần 2: .pre_adj KHÔNG bị ghi đè", md5(PX + ".pre_adj") == m0[0] and r.returncode == 0)
    import json
    src25 = src[~((src.ticker < "T025") & (src.time < "2026-06-01"))]; src25.to_pickle(root + "/src25.pkl")
    reset(); os.path.exists(STATE) and os.remove(STATE); r = run("good", "/src25.pkl")
    ok("tích hợp 25 mã bị cắt, KHÔNG state ⇒ exit 1, không ghi state", r.returncode == 1 and not os.path.exists(STATE), r.stdout[-500:])
    reset(); json.dump({"tickers": [f"T{i:03d}" for i in range(25)]}, open(STATE, "w")); r = run("good", "/src25.pkl")
    ok("tích hợp 25 mã bị cắt ĐÃ trong state ⇒ exit 0 (không chặn vĩnh viễn)", r.returncode == 0 and len(json.load(open(STATE))["tickers"]) == 25, r.stdout[-500:])
    r = run("good", "/src25.pkl"); ok("tích hợp ngày 2 cùng nguồn cắt ⇒ vẫn exit 0", r.returncode == 0, r.stdout[-300:])
    reset(); m0 = md5(PX); r = run("good", kill_copy=True)
    ok("tích hợp kill: lần chép bị chặn thật (exit≠0, 'killed')", r.returncode != 0 and "killed" in (r.stdout + r.stderr), (r.returncode, r.stderr[-400:]))
    ok("tích hợp kill giữa lúc chép .pre_adj ⇒ không có .pre_adj cụt, pkl không đổi", not os.path.exists(PX + ".pre_adj") and md5(PX) == m0, os.listdir(root + "/data"))
    # C2 mục 4: .prev nguyên tử — lần 2 (đã có .pre_adj) bị kill khi chép .prev ⇒ .prev cũ nguyên vẹn
    reset(); r = run("good"); mprev, mpx = md5(PX + ".prev"), md5(PX)
    r = run("good", kill_copy=True)
    ok("tích hợp kill khi chép .prev ⇒ .prev không cụt, pkl không đổi", r.returncode != 0 and md5(PX + ".prev") == mprev and md5(PX) == mpx,
       (r.returncode, r.stderr[-300:]))
    # C2 mục 4: CSV bước [4] nguyên tử — to_csv ghi dở rồi chết ⇒ CSV cũ nguyên vẹn
    CSV = root + "/data/earnings_events_classified.csv"
    reset(); r = run("good"); mcsv = md5(CSV)
    r = run("good", inject="import pandas as pd\ndef _bad(self, path, **k):\n open(path,'w').write('cut'); raise OSError('killed')\npd.DataFrame.to_csv=_bad")
    ok("tích hợp kill giữa to_csv ⇒ CSV cũ nguyên vẹn", r.returncode != 0 and "killed" in r.stderr and md5(CSV) == mcsv, (r.returncode, r.stderr[-300:]))
    # C2 mục 4: dọn tmp mồ côi của chính script, không đụng tmp lạ
    orph = [root + "/data/earnings_px.pkl.abc123.tmp", root + "/data/earnings_events_classified.csv.zz.tmp"]
    for f_ in orph + [root + "/data/khac.pkl.q.tmp"]: open(f_, "w").write("x")
    r = run("good")
    ok("tích hợp dọn *.tmp mồ côi của script, giữ tmp lạ", r.returncode == 0 and not any(os.path.exists(f_) for f_ in orph)
       and os.path.exists(root + "/data/khac.pkl.q.tmp"), os.listdir(root + "/data"))
    os.remove(root + "/data/khac.pkl.q.tmp")
    if os.path.exists(STATE): os.remove(STATE)
    for mode in ("thin", "error", "nullprice"):
        reset(); m0 = (md5(PX), md5(OV)); r = run(mode)
        ok(f"tích hợp {mode}: exit 1", r.returncode == 1, r.stdout[-600:] + r.stderr[-600:])
        ok(f"tích hợp {mode}: pkl KHÔNG đổi, không .prev/.pre_adj, không state", (md5(PX), md5(OV)) == m0 and not os.path.exists(PX + ".pre_adj") and not os.path.exists(STATE))
        ok(f"tích hợp {mode}: bước [3]/[4] vẫn chạy", "[4] earnings_events_classified" in r.stdout)
    reset(); m0 = md5(PX)
    lk = open(root + "/data/.refresh_lagged_caches.lock", "w"); fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
    r = run("good"); lk.close()
    ok("tích hợp lock bận: exit 3, không ghi", r.returncode == 3 and md5(PX) == m0, r.returncode)
    shutil.rmtree(root)

MUTATIONS = [
    ("bỏ lọc cuối tuần", "& (cnt.index.dayofweek < 5)", ""),
    ("DEPTH_FRAC 0", "DEPTH_FRAC = 0.50", "DEPTH_FRAC = 0.0"),
    ("LOST_KEYS_MAX nới", "LOST_KEYS_MAX = 0.002", "LOST_KEYS_MAX = 0.5"),
    ("SESSION_DROP_MAX nới", "SESSION_DROP_MAX = 0.05", "SESSION_DROP_MAX = 0.5"),
    ("carry lấy cả lỗ giữa", 'car = o[f.isna() | (o["time"] < f)]', "car = o"),
    ("carry không mang", 'car = o[f.isna() | (o["time"] < f)]', "car = o.iloc[:0]"),
    ("bỏ trần CARRY", "if len(new_carried) > CARRY_TICKERS_MAX:", "if False:"),
    ("live_bq không gỡ cache", 'saved = os.environ.pop("BQ_LOCAL_CACHE", None)', 'saved = os.environ.get("BQ_LOCAL_CACHE")'),
    ("pull lệch năm cuối", "range(start.year, end.year + 1)", "range(start.year, end.year)"),
    ("pull không lọc universe", 'd = d[d["ticker"].isin(set(tickers))]', "pass"),
    ("bỏ kiểm END", "if new[\"time\"].max() != end:", "if False:"),
    ("bỏ kiểm Close<=0", 'if new["Close"].isna().any() or (new["Close"] <= 0).any():', "if False:"),
    ("bỏ kiểm lùi ngày", 'if new["time"].max() < old["time"].max():', "if False:"),
    ("validate so với chính bản mới", "problems, stats = validate(new, old_px, end,", "problems, stats = validate(new, new, end,"),
    ("phủ: nới ngưỡng cửa sổ", "COVER_WIN_NAN_MAX = 0.02", "COVER_WIN_NAN_MAX = 0.5"),
    ("phủ: nới ngưỡng phiên", "COVER_SESS_NAN_MAX = 0.05", "COVER_SESS_NAN_MAX = 0.5"),
    ("phủ: chỉ kiểm Price", 'COVER_COLS = ("Price", "Volume_3M_P50")', 'COVER_COLS = ("Price",)'),
    ("phủ: không loại mã mang sang", '& ~new["ticker"].isin(set(carried_tickers))', ""),
    ("phủ: kiểm cả lịch sử (không cửa sổ)", "[-COVER_SESSIONS:]", "[:]"),
    ("phủ: không gọi", "    P.extend(cp); S.update(cs)\n", "\n"),
    ("phủ: build không truyền mã mang sang", 'carried_tickers=set(carried["ticker"]) if len(carried) else ()', "carried_tickers=()"),
    ("phủ: thiếu cột không chặn", 'return [f"thiếu cột {miss} trong bản mới"], S', "return [], S"),
    ("carry chỉ cột PX (mất Open/Volume/Price)", "new, carried = carry_truncated(new, old, PX_COLS + OV_COLS[2:])", "new, carried = carry_truncated(new, old, PX_COLS)"),
    ("trung vị không shift(1)", ".median().shift(1)", ".median()"),
    ("trần carry đếm DỒN", 'set(carried["ticker"]) - set(known_carried)', 'set(carried["ticker"])'),
    ("16 khúc không cùng snapshot", "asof = new_asof() if asof is None else asof", "asof = None"),
    ("copy_atomic ghi thẳng", "shutil.copy2(src, tmp); os.replace(tmp, dst)", "shutil.copy2(src, dst)"),
    ("pull rỗng không raise", 'raise RuntimeError(f"BQ trả rỗng', 'print(f"BQ trả rỗng'),
]
REFRESH_MUTATIONS = [
    ("refresh chép .pre_adj không nguyên tử", 'LCA.copy_atomic(full, full + ".pre_adj")', 'shutil.copy2(full, full + ".pre_adj")'),
    ("refresh không đọc state carry", "known_carried=_known", "known_carried=()"),
    ("refresh không lưu state carry", 'CARRY_STATE)\n    px, ov = npx, nov', 'CARRY_STATE + ".x")\n    px, ov = npx, nov'),
    ("refresh ghi dù có vấn đề", "if problems:\n    for p_", "if False:\n    for p_"),
    ("refresh không exit 1", "    sys.exit(1)\n", "    sys.exit(0)\n"),
    ("refresh .pre_adj ghi đè", 'if not os.path.exists(full + ".pre_adj"): ', ""),
    ("refresh đọc BQ_LOCAL_CACHE", "_lbq = LCA.live_bq(bq)", "_lbq = bq"),
    ("refresh .prev không nguyên tử", 'LCA.copy_atomic(path, path + ".prev")', 'shutil.copy2(path, path + ".prev")'),
    ("refresh CSV ghi thẳng", "_save_csv_atomic(evdf, out_csv)\nexcept", "evdf.to_csv(out_csv, index=False)\nexcept"),
    ("refresh không dọn tmp mồ côi", "os.remove(os.path.join(WORKDIR, \"data\", _f))", "pass"),
    ("refresh dọn cả tmp lạ", "and any(_f.startswith(b + \".\") for b in _OWN)", ""),
]

def mutate():
    caught = 0; allm = [("lagged_cache_adjusted.py",) + m for m in MUTATIONS] + [("refresh_lagged_caches.py",) + m for m in REFRESH_MUTATIONS]
    for fname, name, a, b in allm:
        d = tempfile.mkdtemp(prefix="lca_mut_")
        for f in ("lagged_cache_adjusted.py", "refresh_lagged_caches.py", "lagged_cache_adjusted_selfcheck.py"):
            shutil.copy(os.path.join(HERE, f), d)
        s = open(os.path.join(d, fname)).read()
        if a not in s: print(f"!! mutation '{name}': không tìm thấy chuỗi gốc"); caught = -999; continue
        open(os.path.join(d, fname), "w").write(s.replace(a, b, 1))
        r = subprocess.run([sys.executable, os.path.join(d, "lagged_cache_adjusted_selfcheck.py")], env={**os.environ, "LCA_MODULE_DIR": d},
                           capture_output=True, text=True, timeout=1200)
        hit = r.returncode != 0
        caught += hit; print(("BẮT  " if hit else "LỌT  ") + name + ("" if hit else "  <-- selfcheck không phát hiện"))
        shutil.rmtree(d)
    n = len(allm); print(f"\nMUTATION: {caught}/{n} bị bắt"); sys.exit(0 if caught == n else 1)

if __name__ == "__main__":
    if "--mutate" in sys.argv: mutate()
    unit(); integ()
    n_ok = sum(c for _, c in RES); print(f"\n{n_ok}/{len(RES)} PASS"); sys.exit(0 if n_ok == len(RES) else 1)
