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
import hashlib
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


def run(block, records, label="", unreadable=False, resolved=None,
        inbox=None):
    """Chạy khối trên một wc_root giả.

    records=None ⇒ không tạo file. unreadable=True ⇒ tạo _rejected.jsonl là THƯ MỤC, tức
    os.path.exists() vẫn True nhưng open() ném IsADirectoryError — đường lỗi đọc file, thứ
    duy nhất trong khối này còn có nhánh `except` bao ngoài.

    resolved: danh sách bản ghi (hoặc chuỗi thô) coi như ĐÃ XỬ LÝ ⇒ ghi sidecar
    _rejected_resolved.jsonl với khoá sha256 dòng thô, y hệt bin/bus_rejected_resolve.py.
    resolved=[str] không-phải-JSON ⇒ mô phỏng sidecar HỎNG.
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
    if resolved is not None:
        with open(os.path.join(d, "mike", "bus", "_rejected_resolved.jsonl"), "w",
                  encoding="utf-8") as f:
            for r in resolved:
                if isinstance(r, str) and not r.startswith("{"):
                    f.write(r + "\n")          # dòng rác: sidecar hỏng
                    continue
                raw = r if isinstance(r, str) else json.dumps(r, ensure_ascii=False)
                f.write(json.dumps(
                    {"key": hashlib.sha256(raw.strip().encode("utf-8", "replace")
                                           ).hexdigest(), "by": "test",
                     "note": "test"}, ensure_ascii=False) + "\n")
    if inbox is not None:
        # bus/inbox/<agent>.jsonl — nguồn ỨNG VIÊN RETRY. Harness cũ KHÔNG tạo thư mục này,
        # nên các case cũ vẫn đi đúng nhánh "không có gợi ý" (đó là hành vi phải giữ).
        os.makedirs(os.path.join(d, "mike", "bus", "inbox"))
        for who, evs in inbox.items():
            with open(os.path.join(d, "mike", "bus", "inbox", who + ".jsonl"), "w",
                      encoding="utf-8") as f:
                for ev in evs:
                    f.write(json.dumps(ev, ensure_ascii=False) + "\n")
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

    # ── Sidecar ĐÃ-XỬ-LÝ (thêm 2026-08-18). Ca thật: bản ghi Taylor 08-17T16:49 đã được
    #    ghi lại lên bus 3 lần (Taylor tự retry sau 39s + Winston khôi phục từ _rejected),
    #    nhưng §5b không có cách nào biết ⇒ dựng lại y nguyên cảnh báo ở mọi lần chạy trong
    #    24h. Đây là nhóm lỗi "checker không phân biệt XONG với ĐANG MỞ" (§26/§28).
    print("\ncase_sidecar_da_xu_ly")
    _r_done = rec(fresh, who="Taylor")
    w, o, _l, e = run(block, [_r_done], resolved=[_r_done])
    check("bản ghi 24h ĐÃ đánh dấu xử lý ⇒ KHÔNG báo động, ra OK",
          e is None and not w and len(o) == 1, f"W={w} OK={o} exc={e!r}")
    check("OK vẫn nêu rõ có ca mới đã xử lý (không im lặng như thể không có gì)",
          bool(o) and "đã được đánh dấu xử lý" in o[0], o)

    _r_open = rec(fresh, who="Mike")
    w, o, _l, e = run(block, [_r_done, _r_open], resolved=[_r_done])
    check("1 đã xử lý + 1 chưa ⇒ vẫn W, và chỉ đếm 1 ca CHƯA xử lý",
          e is None and len(w) == 1 and "CÁCH LY 1 bản ghi trong 24h" in w[0], f"W={w}")
    check("W chỉ nêu agent của ca CHƯA xử lý (không đổ oan Taylor đã xong)",
          bool(w) and "Mike" in w[0] and "Taylor" not in w[0].split("Lý do")[0], w)

    w, o, _l, e = run(block, [_r_done], resolved=["dong-rac-khong-phai-json"])
    check("sidecar HỎNG ⇒ fail-loud: vẫn báo động (không nuốt event mất thật)",
          e is None and len(w) == 1, f"W={w} exc={e!r}")

    w, o, _l, e = run(block, [rec(old, who="Taylor")], resolved=[rec(old, who="Taylor")])
    check("bản ghi CŨ đã xử lý ⇒ vẫn chỉ là OK, không đếm vào 24h",
          e is None and not w and len(o) == 1, f"W={w} OK={o}")

    print("\ncase_ung_vien_retry")
    # rec() đặt argv[-1] = "quyet" ⇒ đó là trace_id mà khối 5b dùng để khớp (tham số CUỐI,
    # KHÔNG phải argv[4] — xem ca thật 2026-08-31 ở case_wordsplit_trace_o_cuoi bên dưới).
    t0 = now - dt.timedelta(minutes=30)
    rej = t0.strftime("%Y-%m-%dT%H:%M:%SZ")
    hit = (t0 + dt.timedelta(seconds=40)).strftime("%Y-%m-%dT%H:%M:%SZ")
    late = (t0 + dt.timedelta(minutes=40)).strftime("%Y-%m-%dT%H:%M:%SZ")
    ev = {"event_id": "abcd1234-x", "ts": hit, "agent_id": "Taylor",
          "event_type": "status", "topic": "chu-de-viet-lai", "trace_id": "quyet"}

    w, o, _l, e = run(block, [rec(rej, who="Taylor")], inbox={"Taylor": [ev]})
    check("có event cùng trace_id ≤15 phút sau ⇒ W nêu ỨNG VIÊN RETRY",
          bool(w) and "ỨNG VIÊN RETRY" in w[0] and "abcd1234" in w[0], w)
    check("vẫn là W (gợi ý KHÔNG được tự đóng báo động thay người)",
          len(w) == 1 and not o and e is None, f"W={w} OK={o} exc={e!r}")

    w, o, _l, e = run(block, [rec(rej, who="Taylor")],
                      inbox={"Taylor": [dict(ev, ts=late)]})
    check("event đến SAU 15 phút ⇒ KHÔNG tính là ứng viên",
          bool(w) and "KHÔNG tìm thấy ứng viên retry" in w[0], w)

    w, o, _l, e = run(block, [rec(rej, who="Taylor")],
                      inbox={"Taylor": [dict(ev, trace_id="job-khac")]})
    check("trace_id KHÁC ⇒ KHÔNG tính là ứng viên (không đổ oan event lạ)",
          bool(w) and "KHÔNG tìm thấy ứng viên retry" in w[0], w)

    w, o, _l, e = run(block, [rec(rej, who="Taylor")],
                      inbox={"Taylor": [{"ts": hit}, {"khong": "co ts"}, ev]})
    check("inbox có dòng méo (thiếu trace_id/thiếu ts) ⇒ vẫn tìm ra ứng viên, không nổ",
          e is None and bool(w) and "ỨNG VIÊN RETRY" in w[0], f"W={w} exc={e!r}")

    print("\ncase_wordsplit_trace_o_cuoi")
    # Ca THẬT 2026-08-31 (Taylor, 13 tham số): payload bọc nháy đơn có "'" bên trong ⇒ bash
    # tách thành 13 arg. trace_id vẫn ở CUỐI; argv[4] chỉ là một mảnh payload ("vi").
    ws = rec(rej, who="Taylor", argc=13,
             argv=["Taylor", "finding", "vn-jul2026-case", '{"a":1', "vi", "ket", "qua",
                   "kinh", "doanh", "that", "su", 'xau"}', "Taylor_20260831_042737"])
    ev_ws = {"event_id": "2ceafcdb-x", "ts": hit, "agent_id": "Taylor",
             "event_type": "finding", "topic": "vn-jul2026-case",
             "trace_id": "Taylor_20260831_042737"}
    w, o, _l, e = run(block, [ws], inbox={"Taylor": [ev_ws]})
    check("word-split 13 arg: trace_id ở CUỐI ⇒ VẪN tìm ra ứng viên (hồi quy 08-31)",
          e is None and bool(w) and "ỨNG VIÊN RETRY" in w[0] and "2ceafcdb" in w[0], w)

    w, o, _l, e = run(block, [ws], inbox={"Taylor": [
        dict(ev_ws, event_id="lac1234-x", topic="chu-de-khac", trace_id="job-khac")]})
    check("word-split: event khác cả trace lẫn topic ⇒ KHÔNG nhận bừa",
          bool(w) and "KHÔNG tìm thấy ứng viên retry" in w[0], w)

    w, o, _l, e = run(block, [ws], inbox={"Taylor": [
        dict(ev_ws, event_id="topic999-x", trace_id="")]})
    check("word-split: mất trace_id nhưng TRÙNG topic ⇒ vẫn là ứng viên",
          bool(w) and "ỨNG VIÊN RETRY" in w[0] and "topic999" in w[0], w)

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
