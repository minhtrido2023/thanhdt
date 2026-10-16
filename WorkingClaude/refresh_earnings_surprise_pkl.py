# -*- coding: utf-8 -*-
"""refresh_earnings_surprise_pkl.py — làm mới CHỈ data/earnings_surprise_data.pkl từ BigQuery SỐNG.

VÌ SAO (audit sẵn sàng BCTC Q3, finding L1; user duyệt 2026-10-13, job Taylor_20261013_125149):
`golive_recommend_v23.py` (chuỗi 19:00) lấy danh tính sự kiện LAG mới từ pkl này
(`lag_live_schedule.live_lag_candidates`). pkl chỉ được làm mới lúc 15:30 bởi bước [3] của
`refresh_lagged_caches.py`, mà bước đó chạy dưới `BQ_LOCAL_CACHE` (papertrade_daily.sh source
wc_env.sh) ⇒ đọc cache DuckDB sync 23:45 ĐÊM TRƯỚC, không đọc BQ sống. Đo 2026-10-13: pkl 15:30 =
58.233 dòng, max Release_Date 2026-08-21 = y hệt data/bq_cache/ticker_financial.parquet (23:48
đêm 10-12), trong khi BQ sống đã có KBC 2026Q3 (release 10-12, ingest 16:36 ngày 10-13).
⇒ sự kiện ingest ngày D chỉ tới golive ở 19:00 ngày D+1: trễ 1 phiên. File này chạy NGAY TRƯỚC
golive trong chuỗi 19:00 và đọc BQ SỐNG ⇒ bỏ hẳn phiên trễ đó.

PHẠM VI: chỉ pkl sự kiện (bước [3]). KHÔNG đụng earnings_px.pkl / lagged_pos_ov.pkl /
earnings_events_classified.csv — `live_lag_candidates` chỉ dùng CSV đó cho prior (≥1 quý tuổi),
và các file kia thuộc đường paper-trade 15:30.

AN TOÀN:
  · Ghi NGUYÊN TỬ: dump ra file tạm cùng thư mục → fsync → đọc lại kiểm → os.replace. Bị kill
    (timeout) ở bất kỳ điểm nào thì pkl cũ còn nguyên; file tạm mồ côi được dọn ở lượt sau.
  · Thất bại / dữ liệu mới đáng ngờ (rỗng, thiếu cột, co >2% so với pkl cũ, max Release_Date lùi)
    ⇒ GIỮ pkl cũ, in lý do thật, exit 1. Caller (bq_freshness_check.sh) chỉ WARN, không chặn plan.
  · Idempotent: nội dung không đổi ⇒ không ghi (mtime giữ nguyên).
SQL + chuẩn hoá kiểu PHẢI giống bước [3] của refresh_lagged_caches.py (selfcheck so nguyên văn SQL).

Dùng:  $DNA_PYEXE refresh_earnings_surprise_pkl.py              (ghi data/earnings_surprise_data.pkl)
       $DNA_PYEXE refresh_earnings_surprise_pkl.py --out X.pkl  (ghi chỗ khác — đo thời gian/thử)
Self-check: refresh_earnings_surprise_pkl_selfcheck.py
"""
import argparse
import glob
import os
import pickle
import sys
import time

import pandas as pd

WORKDIR = os.path.dirname(os.path.abspath(__file__))
PKL_PATH = os.path.join(WORKDIR, "data", "earnings_surprise_data.pkl")

# Nguyên văn bước [3] của refresh_lagged_caches.py — selfcheck khẳng định 2 nơi trùng nhau.
SQL = """SELECT f.ticker, f.quarter, f.time, f.Release_Date,
       f.NP_P0, f.NP_P1, f.NP_P2, f.NP_P3, f.NP_P4, f.NP_P5, f.NP_P6, f.NP_P7,
       f.NP_R, f.Revenue_YoY_P0
FROM tav2_bq.ticker_financial AS f
WHERE f.Release_Date IS NOT NULL AND f.Release_Date >= '2009-01-01' AND f.NP_P0 IS NOT NULL"""
COLUMNS = ["ticker", "quarter", "time", "Release_Date", "NP_P0", "NP_P1", "NP_P2", "NP_P3", "NP_P4",
           "NP_P5", "NP_P6", "NP_P7", "NP_R", "Revenue_YoY_P0"]
MAX_SHRINK = 0.02     # bản mới ít hơn bản cũ quá 2% số dòng ⇒ nghi kéo thiếu, giữ bản cũ


def live_bq():
    """Accessor BQ SỐNG. wc_env.sh export BQ_LOCAL_CACHE toàn cục ⇒ phải gỡ TRƯỚC khi import
    (cùng mẫu golive_recommend_v23.py / publish_gated_state.py), nếu không sẽ đọc cache T-1."""
    os.environ.pop("BQ_LOCAL_CACHE", None)
    os.environ.pop("LOCAL_SNAPSHOT_DIR", None)
    sys.path.insert(0, WORKDIR)
    from simulate_holistic_nav import bq
    return bq


def normalize(fin):
    """Giống refresh_lagged_caches.py bước [3] + _save_pickle: datetime → ns, StringDtype → object."""
    fin = fin.copy()
    fin["Release_Date"] = pd.to_datetime(fin["Release_Date"])
    fin["time"] = pd.to_datetime(fin["time"])
    for c in fin.columns:
        if pd.api.types.is_datetime64_any_dtype(fin[c]):
            fin[c] = fin[c].astype("datetime64[ns]")
        elif isinstance(fin[c].dtype, pd.StringDtype) or str(fin[c].dtype) in ("string", "StringDtype"):
            fin[c] = fin[c].astype(object)
    return fin


def _load(path):
    with open(path, "rb") as f:
        return pickle.load(f)


def validate(fin, old):
    """Trả lý do TỪ CHỐI (chuỗi) hoặc None nếu bản mới dùng được. `old` = pkl hiện có hoặc None."""
    if not isinstance(fin, pd.DataFrame):
        return f"BQ không trả DataFrame (kiểu {type(fin).__name__})"
    missing = [c for c in COLUMNS if c not in fin.columns]
    if missing:
        return f"thiếu cột {missing}"
    if not len(fin):
        return "0 dòng"
    new_max = pd.to_datetime(fin["Release_Date"], errors="coerce").max()   # BQ thô trả chuỗi/date
    if pd.isna(new_max):
        return "Release_Date toàn NaT"
    if old is not None:
        if len(fin) < len(old) * (1 - MAX_SHRINK):
            return f"co lại {len(old):,} → {len(fin):,} dòng (> {MAX_SHRINK:.0%})"
        old_max = pd.to_datetime(old["Release_Date"], errors="coerce").max()
        if pd.notna(old_max) and new_max < old_max:
            return f"max Release_Date lùi {old_max.date()} → {new_max.date()}"
    return None


def _same(a, b):
    try:
        return (list(a.columns) == list(b.columns) and len(a) == len(b)
                and a.reset_index(drop=True).equals(b.reset_index(drop=True)))
    except Exception:
        return False


def write_atomic(fin, path):
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "wb") as f:
        pickle.dump(fin, f)
        f.flush()
        os.fsync(f.fileno())
    back = _load(tmp)                       # đọc lại: file tạm phải unpickle được và đủ dòng
    if len(back) != len(fin):
        os.remove(tmp)
        raise RuntimeError(f"đọc lại file tạm lệch số dòng ({len(back)} ≠ {len(fin)})")
    os.replace(tmp, path)


def refresh(bq_fn, path=PKL_PATH, out=print):
    """Trả (mã kết quả, thông tin). Mã: 'updated' | 'unchanged' | 'kept_old'. Không raise."""
    info = {"path": path}
    for stale in glob.glob(f"{path}.tmp.*"):        # dọn file tạm của lượt bị kill trước đó
        try:
            os.remove(stale)
        except OSError:
            pass
    old, old_err = None, None
    if os.path.exists(path):
        try:
            old = _load(path)
            info["old_rows"] = len(old)
            info["old_max"] = str(pd.to_datetime(old["Release_Date"], errors="coerce").max().date())
        except Exception as ex:
            old, old_err = None, f"{type(ex).__name__}: {ex}"
            out(f"  pkl cũ KHÔNG đọc được ({old_err}) — sẽ thay bằng bản mới nếu bản mới hợp lệ")
    try:
        fin = bq_fn(SQL)
        reason = validate(fin, old)
        if reason is None:
            fin = normalize(fin)[COLUMNS + [c for c in fin.columns if c not in COLUMNS]]
            reason = validate(fin, old)
    except Exception as ex:
        reason = f"{type(ex).__name__}: {ex}"
    if reason is not None:
        info["reason"] = reason
        out(f"  GIỮ pkl cũ — bản mới bị từ chối. Lý do thật: {reason}")
        return "kept_old", info
    info["new_rows"], info["new_max"] = len(fin), str(fin["Release_Date"].max().date())
    if old is not None and _same(old, fin):
        return "unchanged", info
    try:
        write_atomic(fin, path)
    except Exception as ex:
        info["reason"] = f"ghi lỗi — {type(ex).__name__}: {ex}"
        out(f"  GIỮ pkl cũ — {info['reason']}")
        return "kept_old", info
    return "updated", info


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=PKL_PATH, help="đường dẫn pkl đích (mặc định: data/earnings_surprise_data.pkl)")
    args = ap.parse_args()
    t0 = time.monotonic()
    try:
        bq_fn = live_bq()
    except Exception as ex:
        print(f"refresh_earnings_surprise_pkl: KHÔNG nạp được accessor BQ — giữ pkl cũ. "
              f"Lỗi thật: {type(ex).__name__}: {ex}")
        return 1
    res, info = refresh(bq_fn, args.out)
    dt = time.monotonic() - t0
    print(f"refresh_earnings_surprise_pkl: {res} — {info.get('old_rows', '∅')} → {info.get('new_rows', '∅')} dòng, "
          f"max Release_Date {info.get('old_max', '∅')} → {info.get('new_max', '∅')} ({dt:.1f}s, BQ sống)"
          + (f" — {info['reason']}" if info.get("reason") else ""))
    return 1 if res == "kept_old" else 0


if __name__ == "__main__":
    sys.exit(main())
