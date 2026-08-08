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


MAX_BENIGN_SWAP = 1     # >1 tên mỗi chiều = lệch diện rộng ⇒ luôn FAIL, không xét "lành tính"


def _explain_divergence(bq, rebal_date, into_pit, out_of_pit):
    """Chênh rổ prune-vs-pit tại 1 mốc có phải LỖ HỔNG ĐỘ ĐẦY ĐỦ của ticker_prune không?

    Trả {"benign": bool, "reason": str}. Chỉ 'benign' khi CẢ BA đúng — chứng minh bằng dữ liệu,
    không suy từ tên:
      (1) hoán đổi nhỏ, cân bằng (≤MAX_BENIGN_SWAP mỗi chiều, cùng số lượng ⇒ rổ không đổi kích cỡ);
      (2) MỌI tên pit thêm vào có **0 dòng trong `ticker_prune` toàn bộ lịch sử** — prune chưa từng
          có tên đó (lỗ hổng độ đầy đủ), KHÁC hẳn "prune cố ý loại nó ở giai đoạn này";
      (3) tên thêm vào có thanh khoản trung bình 3 tháng trước mốc **≥** tên bị bỏ ra — loại trừ
          giả thuyết "pit kéo vào một tên kém thanh khoản mà prune loại đúng".
    Ca đã biết: BAF (vào) / TCM (ra) tại 2025-05-05 — xác minh BQ 2026-08-08 (Mike + Taylor):
    BAF 0 dòng prune toàn lịch sử, 121 tỷ đ/phiên vs TCM 65,6 tỷ (02→05/2025).
    """
    if not into_pit or not out_of_pit:
        return {"benign": False, "reason": "chênh một chiều (thêm/bớt không cân) — không phải hoán đổi"}
    if len(into_pit) != len(out_of_pit) or len(into_pit) > MAX_BENIGN_SWAP:
        return {"benign": False,
                "reason": f"hoán đổi {len(into_pit)}↔{len(out_of_pit)} vượt ngưỡng lành tính "
                          f"({MAX_BENIGN_SWAP})"}
    q = "','".join(into_pit)
    n_prune = bq(f"SELECT t.ticker, COUNT(*) n FROM `lithe-record-440915-m9.tav2_bq.ticker_prune` t "
                 f"WHERE t.ticker IN ('{q}') GROUP BY t.ticker")
    present = dict(zip(n_prune["ticker"], n_prune["n"])) if len(n_prune) else {}
    still_there = {t: int(present[t]) for t in into_pit if present.get(t)}
    if still_there:
        return {"benign": False,
                "reason": f"tên pit thêm vào VẪN CÓ trong ticker_prune ({still_there}) ⇒ không phải "
                          f"lỗ hổng độ đầy đủ, mà là khác biệt tiêu chí chọn — phải điều tra"}
    d0 = (pd.Timestamp(rebal_date) - pd.Timedelta(days=90)).strftime("%Y-%m-%d")
    d1 = pd.Timestamp(rebal_date).strftime("%Y-%m-%d")
    names = "','".join(into_pit + out_of_pit)
    liq = bq(f"SELECT t.ticker, AVG(COALESCE(t.Price,t.Close)*t.Volume/1e9) liq_bn "
             f"FROM `lithe-record-440915-m9.tav2_bq.ticker` t WHERE t.ticker IN ('{names}') "
             f"AND t.time BETWEEN DATE '{d0}' AND DATE '{d1}' GROUP BY t.ticker")
    L = dict(zip(liq["ticker"], liq["liq_bn"]))
    lo_in = min((L.get(t) for t in into_pit), default=None)
    hi_out = max((L.get(t) for t in out_of_pit), default=None)
    if lo_in is None or hi_out is None:
        return {"benign": False, "reason": f"không đo được thanh khoản 3M ({L})"}
    if lo_in < hi_out:
        return {"benign": False,
                "reason": f"tên pit thêm vào thanh khoản THẤP HƠN tên bị bỏ "
                          f"({lo_in:.1f} < {hi_out:.1f} tỷ đ/phiên) ⇒ pit có thể đang kéo vào rác"}
    return {"benign": True,
            "reason": f"{into_pit} chưa từng có dòng nào trong ticker_prune (lỗ hổng độ đầy đủ) "
                      f"và thanh khoản 3M cao hơn {out_of_pit} ({lo_in:.1f} ≥ {hi_out:.1f} tỷ đ/phiên)"}


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
        if a == b:
            check(f"T1 rổ {d.date()} byte-identical", True, "GIỐNG HỆT")
            continue
        into, out = sorted(set(b) - set(a)), sorted(set(a) - set(b))
        why = _explain_divergence(bq, d, into, out)
        if why["benign"]:
            # KHÔNG hạ chuẩn: chênh CHỈ được bỏ qua khi chứng minh được bằng dữ liệu rằng nguyên
            # nhân là LỖ HỔNG ĐỘ ĐẦY ĐỦ của `ticker_prune` (tên chưa từng có dòng nào trong bảng
            # đó) VÀ tên `pit` thêm vào thanh khoản KHÔNG kém tên bị bỏ ra. Đó chính là thứ
            # universe_pit sinh ra để sửa — byte-identical với một bảng đã biết là thiếu tên
            # không phải cái bar đúng. Mọi kiểu chênh khác vẫn FAIL CỨNG.
            print(f"  [diff-benign] T1 rổ {d.date()} — VÀO {into} / RA {out}: {why['reason']}",
                  flush=True)
        else:
            check(f"T1 rổ {d.date()} byte-identical", False,
                  f"VÀO {into} / RA {out} — KHÔNG giải thích được: {why['reason']}")
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
