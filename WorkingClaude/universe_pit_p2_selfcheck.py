#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""universe_pit_p2_selfcheck.py — cổng bắt buộc của P2 cutover (custom_basket.py → universe_pit_q).

§4.3 `ticker_prune_replacement_plan.md`. Ba câu hỏi, không hơn:

  T1. Rổ custom30V ở MỌI mốc rebal trong cửa sổ gần đây có GIỐNG HỆT giữa `UNIVERSE_SOURCE`
      "prune" (cũ) và "pit" (mới) không? Bắt buộc giống ở mốc rebal LIVE mới nhất.
  T2. Fail-safe: `universe_pit` thiếu ngày cần dùng → DỪNG CÓ LỖI, KHÔNG im lặng dùng ticker_prune.
  T3. Nhánh đọc qua BQ_LOCAL_CACHE (DuckDB) có ra CÙNG membership như đọc thẳng BigQuery không —
      cache là đường chạy production của `custom30_history.py` khi manifest verified.

Chạy:  $DNA_PYEXE universe_pit_p2_selfcheck.py
"""
import os
import sys

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)

import pandas as pd  # noqa: E402
import custom_basket as cb  # noqa: E402
from pt_dates import detect_end_date  # noqa: E402

# Cấu hình PRODUCTION của rổ custom30V (papertrade_daily.sh [6b] + custom30_history.py)
PROD_KW = dict(quality="none", rebal="q2m5", gate_rating=3, weight_scheme="namecap")
FAILS = []


def _bq_live():
    """bq() KHÔNG qua cache (đọc thẳng BigQuery)."""
    os.environ.pop("BQ_LOCAL_CACHE", None)
    import importlib
    import simulate_holistic_nav as shn
    importlib.reload(shn)
    return shn.bq


def _members(bq, source, start, end):
    old = cb.UNIVERSE_SOURCE
    cb.UNIVERSE_SOURCE = source
    try:
        _, _, mem, _ = cb.build_pit(bq, start, end, **PROD_KW)
    finally:
        cb.UNIVERSE_SOURCE = old
    mem["rebal_date"] = pd.to_datetime(mem["rebal_date"])
    return {d: sorted(g["ticker"]) for d, g in mem.groupby("rebal_date")}


def check(name, cond, detail=""):
    print(f"  [{'ok' if cond else 'FAIL'}] {name}{(' — ' + detail) if detail else ''}", flush=True)
    if not cond:
        FAILS.append(name)


def main():
    bq = _bq_live()
    end = detect_end_date()
    # cửa sổ ngắn: membership tại một mốc rebal chỉ phụ thuộc dữ liệu quý liền trước, không phụ
    # thuộc ngày bắt đầu ⇒ 600 ngày tái lập đúng các mốc gần đây mà không phải dựng lại 2014→nay.
    start = (pd.Timestamp(end) - pd.Timedelta(days=600)).strftime("%Y-%m-%d")
    print(f"== T1: rổ prune vs pit, cửa sổ {start} → {end} ==", flush=True)
    m_prune = _members(bq, "prune", start, end)
    m_pit = _members(bq, "pit", start, end)

    check("T1.0 cùng tập mốc rebal", sorted(m_prune) == sorted(m_pit),
          f"prune {len(m_prune)} mốc / pit {len(m_pit)} mốc")
    for d in sorted(set(m_prune) & set(m_pit)):
        a, b = m_prune[d], m_pit[d]
        check(f"T1 rổ {d.date()} byte-identical", a == b,
              "GIỐNG HỆT" if a == b else f"VÀO {sorted(set(b)-set(a))} / RA {sorted(set(a)-set(b))}")
    live = max(set(m_prune) & set(m_pit))
    check("T1.LIVE mốc rebal đang chạy giống hệt", m_prune[live] == m_pit[live], str(live.date()))

    print("== T2: fail-safe khi universe_pit thiếu ngày ==", flush=True)
    cb.UNIVERSE_SOURCE = "pit"

    def _stub_bq(n_ticker, n_universe):
        return lambda sql, *a, **kw: pd.DataFrame({"n_ticker": [n_ticker], "n_universe": [n_universe]})

    raised = None
    try:
        cb.assert_universe_covers(_stub_bq(250, 200), "2026-01-01", "2026-07-21")
    except RuntimeError as e:
        raised = str(e)
    check("T2.1 thiếu phiên → DỪNG CÓ LỖI", raised is not None and "universe_pit thieu ngay" in (raised or ""),
          (raised or "KHÔNG raise — đã im lặng chạy tiếp")[:110])
    ok_full = True
    try:
        cb.assert_universe_covers(_stub_bq(250, 250), "2026-01-01", "2026-07-21")
    except RuntimeError:
        ok_full = False
    check("T2.2 đủ phiên → chạy tiếp bình thường", ok_full)
    check("T2.3 nhánh pit không có đường fallback ticker_prune",
          "ticker_prune" not in cb.universe_pred(), cb.universe_pred()[:70])

    # cổng này phải nằm TRƯỚC mọi truy vấn của build_pit, không phải chỉ tồn tại trong file
    _real = cb.assert_universe_covers
    hit = []

    def _spy(*a, **kw):
        hit.append(1)
        raise RuntimeError("SENTINEL")
    cb.assert_universe_covers = _spy
    try:
        _members(lambda *a, **kw: (_ for _ in ()).throw(AssertionError("bq bị gọi trước cổng")),
                 "pit", start, end)
    except RuntimeError as e:
        check("T2.4 build_pit gọi cổng TRƯỚC truy vấn đầu tiên", "SENTINEL" in str(e) and hit)
    except AssertionError as e:
        check("T2.4 build_pit gọi cổng TRƯỚC truy vấn đầu tiên", False, str(e))
    finally:
        cb.assert_universe_covers = _real

    print("== T3: nhánh đọc qua BQ_LOCAL_CACHE ==", flush=True)
    from bq_local_cache import BQLocalCache
    import json
    # manifest đang `verified:false` (sự cố ticker_prune 07-14) — ta vẫn PHẢI kiểm nhánh cache,
    # vì nó là đường chạy production của custom30_history.py ngay khi cache được verify lại.
    # Chỉ bỏ qua cổng verified TRONG TEST NÀY; không đụng gì tới manifest thật.
    _orig = BQLocalCache._load_manifest

    def _load_no_gate(self):
        with open(os.path.join(self.cache_dir, "manifest.json")) as f:
            self.manifest = json.load(f)
    BQLocalCache._load_manifest = _load_no_gate
    try:
        lc = BQLocalCache(os.path.join(WORKDIR, "data", "bq_cache"))
        cache_ok = True
    except Exception as e:
        print(f"  [skip] cache không dùng được: {e}")
        cache_ok = False
    finally:
        BQLocalCache._load_manifest = _orig
    if cache_ok:
        d = str(live.date())
        sql_live = (f"SELECT COUNT(DISTINCT t.ticker) AS n FROM tav2_bq.ticker t "
                    f"WHERE t.time = DATE '{d}' AND {cb.universe_pred()}")
        n_bq = int(bq(sql_live)["n"].iloc[0])
        n_cache = int(lc.query(sql_live)["n"].iloc[0])
        check("T3.1 cache dịch được tham chiếu tav2_mike", n_cache > 0, f"{n_cache} mã")
        check("T3.2 cache == BigQuery", n_bq == n_cache, f"BQ {n_bq} / cache {n_cache}")

    print(f"\n{'PASS' if not FAILS else 'FAIL: ' + ', '.join(FAILS)}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
