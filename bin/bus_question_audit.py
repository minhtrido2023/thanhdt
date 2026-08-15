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

Thêm 2026-08-01 (saga "coord-" round-5/6, arch-reviewer killer_objection): PROVENANCE của
closure — bao nhiêu câu hỏi đóng gần đây có `decided_by=user` (quyết định NGƯỜI thật, real-
time) so với không có field đó (agent/Mike tự đóng bằng judgment call, dù có lý do chính đáng
vẫn KHÔNG phải xác nhận trực tiếp của user). Sự cố thật: 1 phiên Mike đóng 13-15 câu hỏi cũ
07-31 (đa số hợp lý, nhưng KHÔNG đánh dấu decided_by) đúng lúc Wags's coord- saga round-5 đang
tự-verify bằng cách đếm pool — pool tụt về 0 bị round-5 hiểu nhầm là "fix của mình có tác dụng"
thay vì "1 đợt dọn dẹp không liên quan trùng giờ". Không có field này thì KHÔNG CÁCH NÀO phân
biệt được 2 nguyên nhân đó chỉ bằng cách đếm số lượng. Quy ước (coding_guidelines.md §20): mọi
answer/decision đóng 1 câu hỏi money/decision-adjacent NÊN kèm `"decided_by": "user"` trong
payload khi thật sự có xác nhận real-time của user; thiếu field này được hiểu là "đóng bằng
judgment call" (agent hoặc Mike tự quyết, có lý do nhưng không phải user xác nhận trực tiếp) —
không sai, chỉ cần được ĐẾM RIÊNG để không lẫn vào "đã qua kiểm chứng người dùng thật".
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
# BUS_AUDIT_ROOT: trỏ sang một cây bus GIẢ để test. Thêm 2026-08-14 vì check_report_cadence.sh
# nay gọi script này làm matcher chính thống (thay vì tự nuôi bản copy thứ 3) — muốn khoá hồi
# quy cho ca "hỏi lại cùng topic sau answer cũ" và "question nằm trong archive .jsonl.gz" thì
# phải chạy được matcher trên bus dựng sẵn. Không set ⇒ hành vi y hệt trước.
ROOT = os.environ.get("BUS_AUDIT_ROOT") or ROOT
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
    ap.add_argument("--provenance-days", type=int, default=14,
                     help="cửa sổ ngày để đếm provenance closure gần đây (mặc định 14)")
    a = ap.parse_args()

    now = dt.datetime.now(dt.timezone.utc)
    files = sorted(glob.glob(os.path.join(INBOX_DIR, "*.jsonl"))) + \
        sorted(glob.glob(os.path.join(INBOX_DIR, "archive", "*.jsonl.gz")))

    # Pass 1: mọi topic TỪNG là 1 question thật (để lọc closure noise — phần lớn answer/decision
    # trong fleet là báo cáo thường lệ, KHÔNG đóng 1 question nào cả; provenance chỉ nên tính
    # closure THẬT SỰ đóng 1 backlog item, không phải mọi answer/decision trong 14 ngày).
    all_question_topics = set()
    for p in files:
        for rec in iter_events(p):
            if rec.get("event_type") == "question" and rec.get("topic"):
                all_question_topics.add(rec.get("topic"))

    resolvers = []          # (resolver_topic, ts, explicit question refs from payload.resolves)
    prov_cutoff = now - dt.timedelta(days=a.provenance_days)
    recent_closures = []   # (ts, agent_of_file, topic, decided_by_or_None)
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
                payload = rec.get("payload")
                if isinstance(payload, str):
                    try:
                        payload = json.loads(payload)
                    except Exception:
                        payload = {}
                raw_resolves = payload.get("resolves", []) if isinstance(payload, dict) else []
                if isinstance(raw_resolves, str):
                    raw_resolves = [raw_resolves]
                explicit = {str(x).strip() for x in raw_resolves
                            if isinstance(raw_resolves, list) and str(x).strip()}
                resolvers.append((t, r_ts, explicit))
                # chỉ đếm provenance nếu topic này THẬT SỰ đóng 1 question đã biết (exact hoặc
                # chứa nguyên topic câu hỏi gốc, cùng quy ước hậu-tố trạng thái đã dùng ở resolved())
                closes_real_question = any(t == qt or qt in t for qt in all_question_topics)
                if r_ts >= prov_cutoff and closes_real_question:
                    payload = rec.get("payload")
                    decided_by = payload.get("decided_by") if isinstance(payload, dict) else None
                    recent_closures.append((r_ts, agent_of(p), t, decided_by))

    def resolved(q_agent, q_topic, q_ts):
        if not q_topic:
            return False
        refs = {q_topic, f"{q_agent}/{q_topic}"}
        return any(r_ts >= q_ts and
                   ((r == q_topic or q_topic in r) or bool(refs & explicit))
                   for r, r_ts, explicit in resolvers)

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
            if resolved(agent, topic, ts_dt):
                continue
            age_d = (now - ts_dt).days
            pending.append({"agent": agent, "topic": topic, "ts": rec.get("ts"), "age_days": age_d})

    pending.sort(key=lambda x: -x["age_days"])

    n_user = sum(1 for _, _, _, db in recent_closures if db == "user")
    n_agent = len(recent_closures) - n_user

    if a.json:
        print(json.dumps({
            "count": len(pending), "pending": pending,
            "provenance": {"window_days": a.provenance_days, "decided_by_user": n_user,
                            "decided_by_agent_or_unmarked": n_agent,
                            "agent_or_unmarked_topics": [t for _, _, t, db in recent_closures if db != "user"]},
        }, ensure_ascii=False, indent=2))
    else:
        print(f"PENDING questions (hot+archive): {len(pending)}")
        for q in pending:
            print(f"  {q['age_days']:>4}d  {q['agent']}/{q['topic']}  ({q['ts']})")
        print(f"\nCLOSURE PROVENANCE (last {a.provenance_days}d, {len(recent_closures)} closure(s)): "
              f"{n_user} decided_by=user, {n_agent} agent/Mike judgment call (không đánh dấu"
              f" decided_by=user) — mục sau CẦN spot-review định kỳ, không phải lỗi tự nó,"
              f" chỉ là chưa được người xác nhận trực tiếp:")
        for ts, agent, topic, db in sorted(recent_closures, reverse=True):
            if db != "user":
                print(f"    {ts.strftime('%Y-%m-%d')}  {agent}/{topic}")

    return len(pending)


if __name__ == "__main__":
    sys.exit(main())
