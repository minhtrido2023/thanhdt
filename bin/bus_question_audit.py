#!/usr/bin/env python3
"""bus_question_audit.py — liệt kê ĐẦY ĐỦ mọi event_type=question chưa được resolver
(answer/decision) đóng, quét cả bus/inbox/*.jsonl (hot) lẫn bus/inbox/archive/*.jsonl.gz.

Dùng cho báo cáo TUẦN (Friday KB editorial review, kb_nightly.sh) — KHÔNG dùng thay
bin/ops_health_check.sh check #5 (gate hàng ngày, đã hardening 4 vòng arch-review,
KHÔNG đụng vào để tránh regression). Script này PORT lại đúng thuật toán match đã
verify của check #5 (cross-agent answer, decision-là-resolver, substring+timestamp,
dedup theo (agent,topic,ts), quét archive) — nếu sửa thuật toán match ở 1 nơi, sửa
luôn nơi kia (xem comment "resolvers"/"_resolved" ở bin/ops_health_check.sh check #5).

Output: mỗi dòng PENDING = 1 câu hỏi, cũ nhất trước, KHÔNG cắt bớt (đây là điểm khác
AGED_SHOWN=5 của check #5 — báo cáo tuần cần thấy hết, không phải digest hàng ngày).
Exit code: số lượng PENDING (0 = sạch, không dùng exit>0 làm "lỗi" theo nghĩa thường —
đây là audit, không phải health-gate).
"""
import argparse
import datetime as dt
import glob
import gzip
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INBOX_DIR = os.path.join(ROOT, "bus", "inbox")


def iter_events(path):
    opener = (lambda p: gzip.open(p, "rt", encoding="utf-8")) if path.endswith(".gz") \
        else (lambda p: open(p, encoding="utf-8"))
    try:
        with opener(path) as f:
            for line in f:
                try:
                    yield json.loads(line)
                except Exception:
                    continue
    except Exception:
        return


def agent_of(path):
    name = os.path.basename(path).replace(".jsonl.gz", "").replace(".jsonl", "")
    return re.sub(r"_\d{4}-\d{2}$", "", name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="output JSON thay vì text")
    a = ap.parse_args()

    now = dt.datetime.now(dt.timezone.utc)
    files = sorted(glob.glob(os.path.join(INBOX_DIR, "*.jsonl"))) + \
        sorted(glob.glob(os.path.join(INBOX_DIR, "archive", "*.jsonl.gz")))

    resolvers = []
    for p in files:
        for rec in iter_events(p):
            if rec.get("event_type") in ("answer", "decision"):
                t = rec.get("topic")
                if not t:
                    continue
                try:
                    r_ts = dt.datetime.fromisoformat(rec.get("ts", "").replace("Z", "+00:00"))
                except Exception:
                    continue
                resolvers.append((t, r_ts))

    def resolved(q_topic, q_ts):
        if not q_topic:
            return False
        return any((r == q_topic or q_topic in r) and r_ts >= q_ts for r, r_ts in resolvers)

    seen = set()
    pending = []
    for p in files:
        agent = agent_of(p)
        for rec in iter_events(p):
            if rec.get("event_type") != "question":
                continue
            try:
                ts_dt = dt.datetime.fromisoformat(rec.get("ts", "").replace("Z", "+00:00"))
            except Exception:
                continue
            topic = rec.get("topic")
            key = (agent, topic, rec.get("ts"))
            if key in seen:
                continue
            seen.add(key)
            if resolved(topic, ts_dt):
                continue
            age_d = (now - ts_dt).days
            pending.append({"agent": agent, "topic": topic, "ts": rec.get("ts"), "age_days": age_d})

    pending.sort(key=lambda x: -x["age_days"])

    if a.json:
        print(json.dumps({"count": len(pending), "pending": pending}, ensure_ascii=False, indent=2))
    else:
        print(f"PENDING questions (hot+archive): {len(pending)}")
        for q in pending:
            print(f"  {q['age_days']:>4}d  {q['agent']}/{q['topic']}  ({q['ts']})")

    return len(pending)


if __name__ == "__main__":
    sys.exit(main())
