#!/usr/bin/env python3
"""Selfcheck cho bin/daily_dashboard.py — logic thuần (ngày/định dạng), không chạm BQ/DNSE/mạng."""
import os
import sys
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import daily_dashboard as dd  # noqa: E402

fails = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        fails.append(name)


T = date(2026, 10, 16)
reg = {"programs": [
    {"id": "overdue", "end": "2026-10-10"},
    {"id": "soon", "review_date": "2026-11-01"},
    {"id": "far", "end": "2027-03-01"},
    {"id": "grad", "status": "graduated-live 2026-08-22", "end": "2026-08-24"},
    {"id": "closed", "status": "closed 2026-10-14", "end": "2026-10-14"},
    {"id": "wait", "status": "review-done 2026-10-01 — chờ user quyết", "end": "2026-09-30"},
    {"id": "ev"},
    {"id": "ev_dated"},
    {"id": "quiet", "reporting": False},
]}
watch = {"milestones": [
    {"date": "2026-10-21", "label": "M1"},
    {"date": "2026-12-01", "label": "M-far"},
    {"date": "2026-11-30", "label": "M-ev", "program_ids": ["ev_dated"]},
    {"date": "2026-10-01", "label": "M-over"},
]}
items, ev, waiting = dd.due_items(T, reg, watch)
labels = [i[1] for i in items]
check("quá hạn có mặt, sắp xếp theo ngày", items[0][0] == date(2026, 10, 1) and labels[1].startswith("paper `overdue`"))
check("review trong 21 ngày có mặt", any("`soon`" in x for x in labels))
check("ngoài 21 ngày bị loại", not any("`far`" in x or "M-far" in x for x in labels))
check("graduated/closed/review-done không vào danh sách mốc",
      not any(k in " ".join(labels) for k in ("`grad`", "`closed`", "`wait`")))
check("review-done 'chờ user' vào waiting", waiting == ["wait"])
check("event-driven: có ev, loại ev_dated (đã có mốc watchlist), loại reporting:false không ngày",
      ev == ["ev"])
check("cửa sổ re-rate: 10/10 mở, 09/10 đóng, 10/11 mở, 11/11 đóng, 15/12 đóng",
      dd._in_window(date(2026, 10, 10)) and not dd._in_window(date(2026, 10, 9))
      and dd._in_window(date(2026, 11, 10)) and not dd._in_window(date(2026, 11, 11))
      and not dd._in_window(date(2026, 12, 15)))
check("định dạng số VN", dd._n(1719.42, ",.2f") == "1.719,42" and dd._pct(-0.09) == "-0,09%" and dd._pct(None) == "n/a")
check("_vnd_m", dd._vnd_m(969196007.0) == "969tr")

# --- season(): suy quý + cửa sổ từ ngày, không hardcode
s1 = dd.season(date(2026, 10, 16))
check("season 16/10/2026 → Q3/2026, 10/10→10/11, prev 2026Q2",
      s1["q"] == "2026Q3" and s1["start"] == date(2026, 10, 10) and s1["end"] == date(2026, 11, 10) and s1["prev_q"] == "2026Q2")
s2 = dd.season(date(2027, 1, 5))
check("season 05/01/2027 → Q4/2026, cửa sổ 10/01→10/02/2027, prev 2026Q3",
      s2["q"] == "2026Q4" and s2["start"] == date(2027, 1, 10) and s2["end"] == date(2027, 2, 10) and s2["prev_q"] == "2026Q3")
s3 = dd.season(date(2026, 12, 15))
check("season 15/12/2026 → vẫn Q3/2026 (cửa sổ đã đóng)", s3["q"] == "2026Q3" and s3["end"] < date(2026, 12, 15))
s4 = dd.season(date(2026, 4, 20))
check("season 20/04/2026 → Q1/2026, prev 2025Q4", s4["q"] == "2026Q1" and s4["prev_q"] == "2025Q4" and s4["end"] == date(2026, 5, 10))
check("season khớp _in_window ở mọi ngày 2026-2027",
      all((dd.season(d)["start"] <= d <= dd.season(d)["end"]) == dd._in_window(d)
          for d in (date(2026, 1, 1) + __import__("datetime").timedelta(days=i) for i in range(0, 420))))

# --- market_block: None từ dna_report
orig = dd._wc_python
dd._vnindex_line = lambda: "VN-Index (giả)"
dd._wc_python = lambda code, timeout=150: ("##build_dt_gate_line\nGate OK\n##build_value_radar_line\n\n##build_neutral_base_line\n", "boom radar")
txt = dd.market_block()
check("None của neutral_base bị bỏ, không in chữ 'None'", "None" not in txt)
check("radar None ⇒ cảnh báo kèm stderr thật", "build_value_radar_line" in txt and "boom radar" in txt)
check("gate có dòng", "Gate OK" in txt)
dd._wc_python = orig

# --- eightl_block với CSV tạm (có dòng hỏng) + releasers giả
import tempfile
td = tempfile.mkdtemp()
def w(name, rows):
    path = os.path.join(td, name)
    open(path, "w").write("ticker,rating\n" + "\n".join(rows) + "\n")
    return path
a = w("rating_8l_2026-10-08.csv", ["AAA,4", "BBB,3", "CCC,2"])
b = w("rating_8l_2026-10-15.csv", ["AAA,3", "BBB,3", "CCC,3", "DDD,1"])
dd._rating_snapshots = lambda: [a, b]
dd._releasers = lambda se: {"released": {"AAA": "2026-10-14"}, "universe": 4, "max_known": "2026-10-14"}
g = dd.eightl_block(date(2026, 10, 16))
check("eightl: nâng 1 (AAA 4→3) hạ 1 (CCC 2→3), cửa sổ ĐANG MỞ Q3/2026",
      "nâng hạng 1 · hạ hạng 1" in g and "ĐANG MỞ" in g and "Q3/2026" in g and "1/4 mã" in g)
bad = w("rating_8l_2026-10-16.csv", ["AAA,abc"])
dd._rating_snapshots = lambda: [a, bad]
check("dòng rating hỏng ⇒ KHÔNG văng ra ngoài build_sections (khối bị cô lập, in lỗi thật)",
      "khối lỗi" in dd._safe("G", dd.eightl_block, date(2026, 10, 16)))
def boom(*a_, **k_):
    raise KeyError("x")
check("_safe cô lập lỗi từng khối", dd._safe("X", boom).startswith("**X**: ⚠️ khối lỗi KeyError"))

# --- chunks() không cắt giữa khối
import importlib.util
spec = importlib.util.spec_from_file_location("ddt", os.path.join(os.path.dirname(os.path.abspath(__file__)), "daily_decision_topic.py"))
ddt = importlib.util.module_from_spec(spec); spec.loader.exec_module(ddt)
blk = lambda c: "\n".join([c * 100] * 8)          # ~800 ký tự/khối
cs = ddt.chunks("\n\n".join([blk("a"), blk("b"), blk("c")]))
check("chunks: mỗi chunk ≤ 1800, mỗi khối nguyên vẹn (8 dòng cùng chunk), không mất nội dung",
      len(cs) == 2 and all(len(c) <= 1800 for c in cs)
      and all(sum(c.count(ch * 100) for ch in "abc") % 8 == 0 for c in cs)
      and sum(c.count("a" * 100) + c.count("b" * 100) + c.count("c" * 100) for c in cs) == 24)
sys.exit(1 if fails else 0)
