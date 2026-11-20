#!/usr/bin/env python3
"""Selfcheck dd_zone_candidates_block.build(): file tươi / cũ / thiếu / hỏng. Không mạng, không đụng production."""
import datetime as dt
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")
import dd_price_zone_watch as W            # noqa: E402
import dd_zone_candidates_block as B       # noqa: E402

NOW = dt.datetime(2026, 11, 20, 21, 0, tzinfo=W._ICT)      # T6 tối ⇒ phiên đóng gần nhất = 20/11
res = []
with tempfile.TemporaryDirectory() as td:
    def w(asof, name="c.json", cands=None):
        p = os.path.join(td, name)
        json.dump({"schema": W.CAND_SCHEMA, "asof": asof, "checked": 3, "total": 3,
                   "candidates": cands if cands is not None else [{"ticker": "AAA", "close": 1000, "center": 1500,
                                                                   "pct_center": -33.3, "dd_date": "2026-11-01"}]},
                  open(p, "w", encoding="utf-8"))
        return p
    fresh = B.build(w("2026-11-20"), NOW)
    res.append(("file tươi: có ứng viên, KHÔNG dòng cũ", "AAA" in fresh and "CŨ" not in fresh))
    stale = B.build(w("2026-11-19", "s.json"), NOW)
    res.append(("file cũ 1 phiên: mở bằng ⚠️ CŨ + vẫn liệt kê", stale.startswith("⚠️ Danh sách ứng viên CŨ") and "AAA" in stale))
    res.append(("cuối tuần: T7 đọc file T6 ⇒ không báo cũ", "CŨ" not in B.build(w("2026-11-20", "t.json"), dt.datetime(2026, 11, 21, 10, 0, tzinfo=W._ICT))))
    try:
        B.build(os.path.join(td, "none.json"), NOW); ok = False
    except FileNotFoundError:
        ok = True
    res.append(("thiếu file ⇒ ném FileNotFoundError (main trả rc=1)", ok))
    bad = os.path.join(td, "bad.json"); open(bad, "w").write("{hỏng")
    try:
        B.build(bad, NOW); ok = False
    except ValueError:
        ok = True
    res.append(("file hỏng ⇒ ném lỗi, không nuốt", ok))
for n, o in res:
    print(("PASS " if o else "FAIL ") + n)
sys.exit(0 if all(o for _, o in res) else 1)
