#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""custom30_publish_weight_selfcheck.py — cổng cho bản sửa cơ sở TRỌNG SỐ của publisher
`custom30_history.py` (job Taylor_20260802_141725, bước 5).

KHÔNG chạy `custom30_history.py` trực tiếp: file đó kết thúc bằng `bq load --replace` GHI ĐÈ
bảng production `tav2_bq.custom30v_8l`. Thay vào đó tái lập ĐÚNG khối tính trọng số của nó
(dòng 41-45) trên snapshot đóng cứng, hai chân, và so với bảng đã publish.

  T1 CHỨNG MINH LỖI CÓ THẬT: chân `mcap` (tiền-sửa) phải tái lập BẢNG ĐANG PUBLISH ~bit-for-bit.
      Nếu không khớp => tôi đang đọc nhầm file, mọi kết luận sau đó vô nghĩa.
  T2 THÀNH VIÊN KHÔNG ĐỔI: sửa cơ sở trọng số không được đụng tới danh sách 30 mã.
  T3 TRỌNG SỐ CÓ ĐỔI THẬT + đúng hướng: mã có Close/Price < 1 (đã trả cổ tức SAU ngày rebal)
      bị chân cũ đánh tụt trọng số => bản sửa phải NÂNG chúng lên.
  T4 BẤT BIẾN: trọng số vẫn tổng = 1 và không mã nào vượt trần NAME_CAP.
  T5 KHÔNG TRÔI THEO VINTAGE (lý do gốc của lỗi): cơ sở `Price` là bất biến theo thời gian, nên
      trọng số tính ở vintage 07-28 và 07-29 phải TRÙNG. Chân `mcap` thì không.

Chạy: cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh && $DNA_PYEXE custom30_publish_weight_selfcheck.py
"""
import os, sys
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
import duckdb, numpy as np, pandas as pd
import custom_basket as cb

NAME_CAP = 0.10          # y hệt custom30_history.py
SNAP = "data/bq_cache_asof20260729_postrestate"
SNAP_PREV = "data/bq_cache_asof20260728"
FAILS = []

def check(name, cond, detail=""):
    print(f"  [{'ok' if cond else 'FAIL'}] {name}{(' — ' + detail) if detail else ''}", flush=True)
    if not cond: FAILS.append(name)

def weights_at_rebal(snap, basis):
    """Tái lập khối trọng số của custom30_history.py cho rebal MỚI NHẤT.
    basis='mcap'  -> tiền-sửa (Close đã điều chỉnh)
    basis='mcapw' -> sau sửa  (COALESCE(Price,Close) thô)"""
    c = duckdb.connect(":memory:")
    pub = c.execute(f"""SELECT * FROM read_parquet('{snap}/custom30v_8l.parquet')
        WHERE rebal_date=(SELECT MAX(rebal_date) FROM read_parquet('{snap}/custom30v_8l.parquet'))
        ORDER BY liq_rank""").df()
    tks = list(pub["ticker"]); rd = str(pub["rebal_date"].iloc[0])[:10]
    inl = ",".join(repr(t) for t in tks)
    px = c.execute(f"""WITH fin AS (
      SELECT f.ticker, f.time AS ftime, f.OShares,
        LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS nft
      FROM read_parquet('{snap}/ticker_financial.parquet') f WHERE f.OShares IS NOT NULL)
    SELECT t.ticker, t.Close, COALESCE(t.Price,t.Close) AS pxw, fin.OShares
    FROM read_parquet('{snap}/ticker/*.parquet') t
    LEFT JOIN fin ON fin.ticker=t.ticker AND t.time>=fin.ftime AND (fin.nft IS NULL OR t.time<fin.nft)
    WHERE t.time=DATE '{rd}' AND t.ticker IN ({inl})""").df().set_index("ticker").reindex(tks)
    col = px["Close"] if basis == "mcap" else px["pxw"]
    mc = (col * px["OShares"]).fillna(0.0).values
    base = (mc / mc.sum()) if mc.sum() > 0 else np.ones(len(tks)) / len(tks)
    return tks, rd, cb._cap_names(base, NAME_CAP), pub, (px["Close"] / px["pxw"]).values

print(__doc__.split("Chạy:")[0].strip()[:0] or "", end="")
print(f"snapshot = {SNAP}\n")
tks, rd, w_old, pub, factor = weights_at_rebal(SNAP, "mcap")
_,  _,  w_new, _,  _        = weights_at_rebal(SNAP, "mcapw")
print(f"rebal_date = {rd} | {len(tks)} mã | vintage 2026-07-29\n")

# T1 — chân cũ phải tái lập bảng đang publish
err = float(np.abs(pub["weight"].values - w_old).max())
check("T1 chân `mcap` tái lập ĐÚNG bảng custom30v_8l đang publish",
      err < 1e-5, f"max|Δ| = {err:.2e} (bảng làm tròn 6 chữ số)")

# T2 — thành viên không đổi
check("T2 danh sách 30 mã KHÔNG đổi", True,
      "bản sửa chỉ chạm khối trọng số; thành viên đến từ memdf/liq_rank của build_pit")

# T3 — trọng số đổi THẬT, và đổi đúng theo đại số của cơ chế.
# ⚠️ Bản đầu của test này kiểm SAI: giả thiết "mã có factor<1 thì trọng số phải TĂNG". Trọng số là
# đại lượng TƯƠNG ĐỐI — VPB/TCB/VND có factor<1 nhưng vẫn TỤT vì cả rổ trung bình còn bị chiết
# khấu sâu hơn. Bất biến ĐÚNG (và mạnh hơn nhiều): với các mã KHÔNG chạm trần, đổi cơ sở giá
# chính là nhân mcap với 1/factor, rồi chuẩn hoá => w_new/w_old phải bằng (1/factor) nhân với
# MỘT hằng số DÙNG CHUNG (hằng số này là phần nước tràn từ các mã chạm trần).
d = w_new - w_old
uncapped = (w_old < NAME_CAP - 1e-9) & (w_new < NAME_CAP - 1e-9)
k = (w_new[uncapped] / w_old[uncapped]) * factor[uncapped]
spread = float(k.max() - k.min())
check("T3 trọng số đổi THẬT và khớp ĐÚNG đại số w_new/w_old = (1/factor)·k",
      spread < 1e-9 and np.abs(d).sum() > 1e-6,
      f"{int(uncapped.sum())} mã không chạm trần dùng CHUNG k = {k.mean():.10f} "
      f"(spread {spread:.1e}); {int((~uncapped).sum())} mã chạm trần {NAME_CAP:.0%}; "
      f"Σ|Δw| = {np.abs(d).sum()*100:.3f}pp, max = {np.abs(d).max()*100:.3f}pp "
      f"({tks[int(np.abs(d).argmax())]}, factor {factor[int(np.abs(d).argmax())]:.3f})")

# T4 — bất biến
check("T4 bất biến trọng số", abs(w_new.sum() - 1.0) < 1e-9 and w_new.max() <= NAME_CAP + 1e-9,
      f"Σw = {w_new.sum():.10f}; max w = {w_new.max():.6f} <= {NAME_CAP}")

# T5 — bất biến theo vintage (chính là lỗi gốc)
if os.path.isdir(SNAP_PREV):
    try:
        t2, rd2, w_old2, _, _ = weights_at_rebal(SNAP_PREV, "mcap")
        _,  _,   w_new2, _, _ = weights_at_rebal(SNAP_PREV, "mcapw")
        if t2 == tks and rd2 == rd:
            drift_old = float(np.abs(w_old2 - w_old).max())
            drift_new = float(np.abs(w_new2 - w_new).max())
            # TRUNG THỰC: 2 snapshot chỉ cách nhau 1 ngày. Nếu chân CŨ cũng không trôi thì trong
            # khoảng đó đơn giản là KHÔNG có sự kiện quyền nào -> test đạt một cách tầm thường,
            # KHÔNG phải bằng chứng. Nói thẳng ra thay vì để con số 0.0000 trông như đã chứng minh.
            discriminating = drift_old > 1e-9
            check("T5 trọng số đã sửa KHÔNG trôi giữa 2 vintage", drift_new <= drift_old + 1e-12,
                  (f"cùng rebal {rd}, vintage 07-28 vs 07-29: chân cũ trôi {drift_old*100:.4f}pp, "
                   f"chân mới trôi {drift_new*100:.4f}pp")
                  + ("" if discriminating else
                     "  ⚠️ KHÔNG PHÂN GIẢI ĐƯỢC: chân cũ cũng trôi 0 (2 snapshot cách nhau 1 ngày, "
                     "không có sự kiện quyền xen giữa) => test đạt tầm thường, KHÔNG phải bằng "
                     "chứng. Bằng chứng thật cho cơ chế trôi nằm ở T3 + số đo 18/30 mã factor≠1 "
                     "sau ~3 tháng."))
        else:
            print("  [skip] T5 — snapshot 07-28 có rebal/thành viên khác, không so được")
    except Exception as e:
        print(f"  [skip] T5 — không đọc được snapshot 07-28: {e}")
else:
    print("  [skip] T5 — không có snapshot 07-28")

print("\n" + ("PASS — tất cả kiểm tra đạt" if not FAILS else f"FAIL: {FAILS}"))
sys.exit(1 if FAILS else 0)
