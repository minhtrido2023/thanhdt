#!/usr/bin/env python3
"""work_ledger.py — sổ cái công việc fleet (append-only JSONL, upsert theo `id`).

File: kb/work_ledger.jsonl (override: env WT_LEDGER). Mỗi dòng = 1 bản ghi đầy đủ-hoặc-một-phần của
1 `id`; bản sau trường nào thắng trường đó; `notes` nối thêm (không xoá). Ghi qua CLI/hàm ở đây
(flock + 1 lần write O_APPEND = atomic), KHÔNG sửa tay.

Import được (server B gọi): upsert, add_note, set_priority, set_status, new_user_item, ack,
merge_ids, fold, inbox_items. Mọi mốc thời gian = ICT (ZoneInfo, luật §16).
"""
import argparse
import fcntl
import json
import os
import re
import sys
import unicodedata
from datetime import datetime
from zoneinfo import ZoneInfo

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.environ.get("WT_LEDGER") or os.path.join(ROOT, "kb", "work_ledger.jsonl")

ID_PREFIXES = ("proj:", "paper:", "busq:", "sbw:", "wl:", "user:")
TYPES = ("research", "ops", "portfolio", "watch")
STATUSES = ("idea", "active", "waiting", "GO", "NO-GO", "live", "closed")
VERDICT_LABELS = ("NO-GO", "GO", "INCONCLUSIVE", "IMPLEMENTED", "KHÔNG WIRE")
CONFIDENCE = ("high", "med", "low")
# trường scalar/JSON ghi đè nguyên; notes nối thêm; aliases hợp nhất
FIELDS = ("branch", "title", "summary", "detail", "type", "status", "priority", "owner", "opened",
          "updated", "due", "verdict", "waiting_on", "needs_user", "links", "depends_on", "aliases",
          "source", "ack", "confidence")


def now_iso():
    return datetime.now(ICT).isoformat(timespec="seconds")


def today_ict():
    return datetime.now(ICT).date().isoformat()


def slugify(text, maxlen=40):
    t = unicodedata.normalize("NFD", text.lower().replace("đ", "d"))
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:maxlen].strip("-") or "item"


def _validate(rec):
    if not isinstance(rec.get("id"), str) or not rec["id"].startswith(ID_PREFIXES) or len(rec["id"]) < 7:
        raise ValueError("id phải bắt đầu bằng một trong %s" % (ID_PREFIXES,))
    if "type" in rec and rec["type"] not in TYPES:
        raise ValueError("type ∉ %s" % (TYPES,))
    if "status" in rec and rec["status"] not in STATUSES:
        raise ValueError("status ∉ %s" % (STATUSES,))
    if "priority" in rec and rec["priority"] not in (1, 2, 3):
        raise ValueError("priority ∉ 1|2|3")
    if "confidence" in rec and rec["confidence"] not in CONFIDENCE:
        raise ValueError("confidence ∉ %s" % (CONFIDENCE,))
    v = rec.get("verdict")
    if v is not None and (not isinstance(v, dict) or v.get("label") not in VERDICT_LABELS):
        raise ValueError("verdict phải null hoặc {label∈%s, text}" % (VERDICT_LABELS,))
    if rec.get("due"):
        datetime.strptime(rec["due"], "%Y-%m-%d")
    if "summary" in rec and rec["summary"] and len(rec["summary"]) > 160:
        rec["summary"] = rec["summary"][:159] + "…"


def append_record(rec, path=None):
    """Ghi 1 dòng: flock trên file .lock + os.write một lần với O_APPEND."""
    path = path or LEDGER
    os.makedirs(os.path.dirname(path), exist_ok=True)
    line = (json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
    with open(path + ".lock", "a") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
        try:
            os.write(fd, line)
            os.fsync(fd)
        finally:
            os.close(fd)
    return rec


def read_records(path=None):
    path = path or LEDGER
    out = []
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except ValueError:
                sys.stderr.write("work_ledger: bỏ qua dòng hỏng %s:%d\n" % (path, n))
                continue
            if isinstance(r, dict) and r.get("id"):
                out.append(r)
    return out


def fold(records=None, path=None):
    """Gộp bản ghi → {id: item_một_phần}. `merged_into` gộp alias vào id chuẩn."""
    records = read_records(path) if records is None else records
    items, redirect = {}, {}
    for r in records:
        if r.get("merged_into"):
            redirect[r["id"]] = r["merged_into"]
            continue
        it = items.setdefault(r["id"], {"id": r["id"], "notes": [], "aliases": []})
        for k in FIELDS:
            if k in r and k not in ("aliases",):
                it[k] = r[k]
        for n in r.get("notes") or []:
            it["notes"].append(n)
        for a in r.get("aliases") or []:
            if a not in it["aliases"]:
                it["aliases"].append(a)
        it["_ts"] = r.get("ts")
    for alias, canon in redirect.items():
        src = items.pop(alias, None)
        dst = items.setdefault(canon, {"id": canon, "notes": [], "aliases": []})
        if alias not in dst["aliases"]:
            dst["aliases"].append(alias)
        if src:
            dst["notes"] = sorted(dst["notes"] + src["notes"], key=lambda n: n.get("ts", ""))
            for a in src["aliases"]:
                if a not in dst["aliases"]:
                    dst["aliases"].append(a)
            for k, v in src.items():
                if k not in ("id", "notes", "aliases", "_ts") and k not in dst:
                    dst[k] = v
    return items


def upsert(item_id, by="mike", path=None, **fields):
    rec = {"id": item_id, "ts": now_iso(), "by": by}
    for k, v in fields.items():
        if k not in FIELDS and k != "notes":
            raise ValueError("trường lạ: %s" % k)
        rec[k] = v
    rec.setdefault("updated", today_ict())
    _validate(rec)
    return append_record(rec, path)


def add_note(item_id, text, by="mike", path=None):
    text = (text or "").strip()
    if not text:
        raise ValueError("ghi chú rỗng")
    ts = now_iso()
    rec = {"id": item_id, "ts": ts, "by": by, "updated": today_ict(),
           "notes": [{"ts": ts, "by": by, "text": text[:2000]}]}
    _validate(rec)
    return append_record(rec, path)


def set_priority(item_id, priority, by="mike", path=None):
    return upsert(item_id, by=by, path=path, priority=int(priority))


def set_status(item_id, status, verdict_label=None, verdict_text="", by="mike", path=None):
    f = {"status": status}
    if verdict_label:
        f["verdict"] = {"label": verdict_label, "text": verdict_text[:300]}
    return upsert(item_id, by=by, path=path, **f)


def close_item(item_id, status="closed", verdict_label=None, text="", by="mike", path=None):
    if status not in ("closed", "NO-GO", "GO"):
        raise ValueError("close chỉ nhận closed|NO-GO|GO")
    if status in ("NO-GO", "GO") and not verdict_label:
        verdict_label = status
    rec = set_status(item_id, status, verdict_label, text, by, path)
    if text:
        add_note(item_id, "Đóng (%s): %s" % (status, text), by, path)
    return rec


def new_user_item(branch, title, summary="", by="user", path=None):
    """Ý tưởng/hướng mới user gửi từ webapp: user:<slug>, idea, source=user, chưa ack."""
    title = title.strip()
    if not title or not branch.strip():
        raise ValueError("cần branch và title")
    base = "user:" + slugify(title)
    existing = fold(path=path)
    item_id, n = base, 2
    while item_id in existing:
        item_id, n = "%s-%d" % (base, n), n + 1
    return upsert(item_id, by=by, path=path, branch=branch.strip(), title=title[:120],
                  summary=summary.strip()[:160], type="research", status="idea", priority=3,
                  opened=today_ict(), owner="user", source="user", ack=False, needs_user=False)


def inbox_items(path=None):
    return [i for i in fold(path=path).values() if i.get("source") == "user" and not i.get("ack")]


def ack(item_id, by="mike", path=None):
    return upsert(item_id, by=by, path=path, ack=True)


def merge_ids(alias_id, canonical_id, by="mike", path=None):
    if alias_id == canonical_id:
        raise ValueError("alias == canonical")
    rec = {"id": alias_id, "ts": now_iso(), "by": by, "merged_into": canonical_id}
    _validate({"id": alias_id})
    _validate({"id": canonical_id})
    return append_record(rec, path)


def _kv(pairs):
    out = {}
    for p in pairs or []:
        k, _, v = p.partition("=")
        if k in ("priority",):
            v = int(v)
        elif k in ("needs_user", "ack"):
            v = v.lower() in ("1", "true", "yes")
        elif k in ("links", "depends_on", "aliases", "verdict", "waiting_on"):
            v = json.loads(v)
        elif v in ("null", ""):
            v = None
        out[k] = v
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--by", default="mike")
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("upsert"); s.add_argument("id"); s.add_argument("fields", nargs="*", help="k=v (links/verdict/waiting_on = JSON)")
    s = sp.add_parser("note"); s.add_argument("id"); s.add_argument("text")
    s = sp.add_parser("close"); s.add_argument("id"); s.add_argument("status", choices=["closed", "NO-GO", "GO"]); s.add_argument("text", nargs="?", default="")
    s = sp.add_parser("status"); s.add_argument("id"); s.add_argument("status"); s.add_argument("--verdict"); s.add_argument("--text", default="")
    s = sp.add_parser("inbox")
    s = sp.add_parser("ack"); s.add_argument("id")
    s = sp.add_parser("merge"); s.add_argument("alias"); s.add_argument("canonical")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "upsert":
            r = upsert(a.id, by=a.by, **_kv(a.fields))
        elif a.cmd == "note":
            r = add_note(a.id, a.text, a.by)
        elif a.cmd == "close":
            r = close_item(a.id, a.status, None, a.text, a.by)
        elif a.cmd == "status":
            r = set_status(a.id, a.status, a.verdict, a.text, a.by)
        elif a.cmd == "ack":
            r = ack(a.id, a.by)
        elif a.cmd == "merge":
            r = merge_ids(a.alias, a.canonical, a.by)
        else:
            for i in inbox_items():
                print("%s\t%s\t%s\t%s" % (i["id"], i.get("branch", ""), i.get("title", ""), i.get("opened", "")))
            return 0
    except (ValueError, KeyError) as e:
        sys.stderr.write("work_ledger: %s\n" % e)
        return 2
    print(json.dumps(r, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
