#!/usr/bin/env python3
"""Gác hồi quy cho khối §5b của bin/ops_health_check.sh — người ĐỌC hàng đợi cách ly
bus/_rejected.jsonl (append_event.sh ghi arg bị chặn vào đó thay vì để event hỏng lên bus).

VÌ SAO CẦN FILE RIÊNG: §5b nằm cố ý NGOÀI marker CHECK5_BEGIN/END, vì khối CHECK5 có hợp
đồng namespace hạn chế với ops_health_check_selfcheck.py. Hệ quả là selfcheck thường trực
MÙ HOÀN TOÀN với 5b — arch-review round 2 (coord-2026-08-16) bắt đúng điểm này: 46 dòng
logic mới, 0 coverage commit, harness RED/GREEN của tác giả chỉ dùng một lần rồi vứt.

CÁCH LÀM: TRÍCH khối giữa marker `5b_BEGIN`/`5b_END` trong ops_health_check.sh rồi exec
trên namespace stub (os/json/wc_root/lines/W/OK) — KHÔNG chép lại logic sang đây, vì bản
chép sẽ trôi khỏi bản thật rồi gác một thứ không còn tồn tại.

Ba ca HOSTILE ở cuối là phần quan trọng nhất: file này chứa dữ liệu HỎNG theo thiết kế
(nó là hàng đợi pháp y cho arg đã bị chặn vì hỏng), nên "happy path xanh" không nói lên gì.
"""
import datetime as dt
import json
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.environ.get("OPS_HEALTH_CHECK_SRC", os.path.join(ROOT, "bin", "ops_health_check.sh"))

_fails = []


def check(label, cond, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {label}" + ("" if cond else f" — {detail}"))
    if not cond:
        _fails.append(label)


def extract_block():
    src = open(SRC, encoding="utf-8").read()
    m = re.search(r"\n# 5b_BEGIN\b.*?\n(.*?)\n# 5b_END\b", src, re.S)
    if not m:
        print("FAIL: không trích được khối giữa 5b_BEGIN/5b_END trong " + SRC)
        sys.exit(1)
    return m.group(1)


def run(block, records, label="", unreadable=False):
    """Chạy khối trên một wc_root giả.

    records=None ⇒ không tạo file. unreadable=True ⇒ tạo _rejected.jsonl là THƯ MỤC, tức
    os.path.exists() vẫn True nhưng open() ném IsADirectoryError — đường lỗi đọc file, thứ
    duy nhất trong khối này còn có nhánh `except` bao ngoài.
    """
    d = tempfile.mkdtemp(prefix="ophc_5b_")
    os.makedirs(os.path.join(d, "mike", "bus"))
    if unreadable:
        os.makedirs(os.path.join(d, "mike", "bus", "_rejected.jsonl"))
    elif records is not None:
        with open(os.path.join(d, "mike", "bus", "_rejected.jsonl"), "w",
                  encoding="utf-8") as f:
            for r in records:
                f.write(r if isinstance(r, str) else json.dumps(r, ensure_ascii=False))
                f.write("\n")
    warns, oks, lines = [], [], []
    ns = {"os": os, "json": json, "wc_root": d, "lines": lines,
          "W": lambda s: warns.append(s), "OK": lambda s: oks.append(s)}
    exc = None
    try:
        exec(compile(block, "5b", "exec"), ns)
    except Exception as e:               # noqa: BLE001 — đúng thứ đang đo
        exc = e
    return warns, oks, lines, exc


def rec(ts, who="Mike", why="nhan 6 tham so", **kw):
    r = {"ts": ts, "rejected_by": "append_event.sh", "reason": why, "argc": 6,
         "argv": [who, "status", "chu-de", "{}", "nguoi", "quyet"],
         "caller_pid": "1", "job_id": ""}
    r.update(kw)
    return r


def main():
    block = extract_block()
    now = dt.datetime.now(dt.timezone.utc)
    fresh = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    old = (now - dt.timedelta(days=9)).strftime("%Y-%m-%dT%H:%M:%SZ")

    print("case_happy_path")
    w, o, _l, e = run(block, None)
    check("không có file cách ly ⇒ im lặng hoàn toàn (không W, không OK)",
          not w and not o and e is None, f"W={w} OK={o} exc={e!r}")

    w, o, _l, e = run(block, [rec(old)])
    check("chỉ có bản ghi CŨ ⇒ OK, không báo động", not w and len(o) == 1 and e is None,
          f"W={w} OK={o} exc={e!r}")

    w, o, _l, e = run(block, [rec(old), rec(fresh, who="Taylor")])
    check("có bản ghi trong 24h ⇒ ĐÚNG 1 W", len(w) == 1 and e is None, f"W={w} exc={e!r}")
    check("W nêu tên agent gây ra (để biết call site nào cần sửa quote)",
          bool(w) and "Taylor" in w[0], w)
    check("W KHÔNG đếm nhầm bản ghi cũ vào con số 24h",
          bool(w) and "CÁCH LY 1 bản ghi trong 24h" in w[0], w)

    print("\ncase_HOSTILE_du_lieu_meo")
    # Toàn bộ nhóm này là hồi quy cho arch-review round 2: bản đầu của §5b để _r.get() và
    # _who/_why NGOÀI try ⇒ một bản ghi méo ném thẳng ra ngoài, giết CẢ heredoc (mất toàn
    # bộ 11 check của ops_health_check chứ không riêng 5b).
    w, o, _l, e = run(block, ["12345", rec(fresh, who="Wags")])
    check("dòng JSON không-phải-object KHÔNG làm đứt vòng quét (bản ghi SAU vẫn thấy)",
          e is None and len(w) == 1 and "Wags" in w[0], f"W={w} exc={e!r}")
    check("dòng đó được đếm là hỏng, không im lặng bỏ qua",
          bool(w) and "không parse được" in w[0], w)

    w, o, _l, e = run(block, [rec(fresh, why=["list", "chu-khong-phai-str"])])
    check("reason là LIST ⇒ không nổ, vẫn báo động", e is None and len(w) == 1,
          f"exc={e!r} W={w}")

    w, o, _l, e = run(block, [rec(fresh, argv={"khong": "phai list"})])
    check("argv là DICT ⇒ không nổ, vẫn báo động", e is None and len(w) == 1,
          f"exc={e!r} W={w}")

    _numeric_ts = rec(fresh)
    _numeric_ts["ts"] = 12345          # ts kiểu SỐ: str(_r.get("ts")) phải chịu được
    w, o, _l, e = run(block, [_numeric_ts])
    check("ts là SỐ ⇒ không nổ (không so sánh trực tiếp int với str)", e is None,
          f"exc={e!r}")

    w, o, _l, e = run(block, ["{khong-phai-json", "", "  "])
    check("dòng rác + dòng rỗng ⇒ W (không lines.append im lặng), không nổ",
          e is None and len(w) == 1, f"exc={e!r} W={w} lines={_l}")

    # ── Đường lỗi ĐỌC FILE (arch-review round 3 required_change #2). 8e9affc3 đổi nhánh này
    #    từ `lines.append` sang `W()` vì lines.append in ra ℹ️ mà KHÔNG tăng biến `warn` ⇒
    #    không escalate = đúng hình thái im lặng cả khối đi diệt. Nhưng KHÔNG có assertion
    #    nào khoá lại: reviewer mutation `W()` → `lines.append` VẪN PASS rc=0. Fix không có
    #    test thì lần refactor sau nó lặng lẽ quay về — chốt lại tại đây.
    print("\ncase_duong_loi_doc_file")
    w, o, _l, e = run(block, None, unreadable=True)
    check("file cách ly KHÔNG đọc được ⇒ W() (escalate), KHÔNG phải lines.append im lặng",
          e is None and len(w) == 1 and not _l, f"W={w} lines={_l} exc={e!r}")
    check("thông điệp nói rõ hàng đợi đang KHÔNG được giám sát (không chỉ in tên lỗi)",
          bool(w) and "KHÔNG được giám sát" in w[0], w)
    check("đường lỗi đọc KHÔNG ném ra ngoài (không giết 11 check còn lại)", e is None,
          f"exc={e!r}")

    print("\ncase_CONTROL_khong_duoc_keu_oan")
    w, o, _l, e = run(block, [])
    check("CONTROL: file RỖNG ⇒ không W, không OK", not w and not o and e is None,
          f"W={w} OK={o}")

    print()
    if _fails:
        print(f"FAIL: {len(_fails)} assertion hỏng")
        for f in _fails:
            print("  - " + f)
        sys.exit(1)
    print("OK: toàn bộ assertion PASS")


if __name__ == "__main__":
    main()
