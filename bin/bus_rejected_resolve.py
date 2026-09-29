#!/usr/bin/env python3
"""Đánh dấu một bản ghi trong hàng đợi cách ly `bus/_rejected.jsonl` là ĐÃ XỬ LÝ.

VÌ SAO CẦN: `_rejected.jsonl` là file PHÁP Y append-only — không ai được sửa/xoá dòng
trong đó. Nhưng §5b của `ops_health_check.sh` cảnh báo mọi bản ghi trong 24h qua mà KHÔNG
có cách nào biết event đã được khôi phục lên bus hay chưa ⇒ báo động lặp lại suốt 24h dù
việc đã xong (đúng nhóm lỗi "checker không phân biệt được XONG với ĐANG MỞ", §26/§28
coding_guidelines + skill close-the-loop).

CƠ CHẾ: sidecar `bus/_rejected_resolved.jsonl`, khoá = sha256 của DÒNG THÔ trong hàng đợi
(ổn định tuyệt đối, không phụ thuộc ts/thứ tự/parse được hay không). File pháp y không bị
đụng tới.

  bin/bus_rejected_resolve.py --list
  bin/bus_rejected_resolve.py --index 0 --by Winston \
      --note "đã ghi lại lên bus, event_id eb2d0da4…"
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import sys

BUS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bus")
QUEUE = os.path.join(BUS, "_rejected.jsonl")
RESOLVED = os.path.join(BUS, "_rejected_resolved.jsonl")


def key_of(raw_line):
    return hashlib.sha256(raw_line.strip().encode("utf-8", "replace")).hexdigest()


def load_queue():
    if not os.path.exists(QUEUE):
        return []
    out = []
    with open(QUEUE, encoding="utf-8", errors="replace") as f:
        for ln in f:
            if ln.strip():
                out.append(ln.strip())
    return out


def load_resolved():
    keys = set()
    if os.path.exists(RESOLVED):
        with open(RESOLVED, encoding="utf-8", errors="replace") as f:
            for ln in f:
                try:
                    keys.add(json.loads(ln)["key"])
                except Exception:
                    continue
    return keys


def describe(raw):
    try:
        r = json.loads(raw)
        argv = r.get("argv") if isinstance(r.get("argv"), list) else []
        who = str(argv[0]) if argv else "?"
        topic = str(argv[2]) if len(argv) > 2 else "?"
        return f"{r.get('ts', '?')}  {who}  {topic[:60]}"
    except Exception:
        return "(dòng không parse được) " + raw[:60]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true", help="liệt kê hàng đợi + trạng thái")
    ap.add_argument("--index", type=int, help="chỉ số bản ghi (theo --list) cần đánh dấu")
    ap.add_argument("--by", help="ai xử lý (agent id)")
    ap.add_argument("--note", help="bằng chứng đã xử lý: event_id đã ghi lại / commit / lý do bỏ qua")
    a = ap.parse_args()

    q = load_queue()
    resolved = load_resolved()

    if a.list or a.index is None:
        if not q:
            print("hàng đợi cách ly rỗng.")
            return 0
        for i, raw in enumerate(q):
            print(f"[{i}] {'ĐÃ XỬ LÝ' if key_of(raw) in resolved else 'CHƯA  '}  {describe(raw)}")
        return 0

    if not (a.by and a.note):
        print("cần --by và --note (bằng chứng), không đánh dấu suông.", file=sys.stderr)
        return 2
    if not 0 <= a.index < len(q):
        print(f"--index ngoài phạm vi 0..{len(q) - 1}", file=sys.stderr)
        return 2

    raw = q[a.index]
    k = key_of(raw)
    if k in resolved:
        print(f"[{a.index}] đã được đánh dấu từ trước — không ghi trùng.")
        return 0
    rec = {"key": k, "resolved_at": dt.datetime.now(dt.timezone.utc)
           .strftime("%Y-%m-%dT%H:%M:%SZ"), "by": a.by, "note": a.note,
           "orig": describe(raw)}
    with open(RESOLVED, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"[{a.index}] ĐÃ ĐÁNH DẤU XỬ LÝ  {describe(raw)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
