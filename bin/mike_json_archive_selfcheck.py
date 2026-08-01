#!/usr/bin/env python3
"""Selfcheck cho bin/mike_json.py `trace` + `verify-coverage` — quét đủ hot + archive.

TẠI SAO tồn tại (2026-08-01, audit kiến trúc fleet §14/committee — Fable plan + Opus
critique, việc #4 đã duyệt): cả 2 lệnh trước đây CHỈ glob `bus/inbox/*.jsonl` (hot) và
`bus/jobs/<id>.json` (hot) — job/event nào cũ hơn ngưỡng archive (kb_nightly Phase 1b2 =
30 ngày cho bus event, fleet_housekeeping Phase 1b3 cho bus/jobs) âm thầm "không tìm
thấy" thay vì báo đã bị archive. Cùng lớp lỗi đã bắt được ở check #5 (kb/coding_guidelines.md
§17, `ops_health_check_selfcheck.py`) — script này áp dụng nguyên tắc reader-scope cho
2 reader còn thiếu.

Chạy CLI thật qua subprocess (không import hàm) — trace.sh/verify-coverage được người
gọi qua dòng lệnh, test phải đi đúng đường đó để không bỏ sót lỗi ở lớp argv/exit-code.

Chạy: python3 bin/mike_json_archive_selfcheck.py   (exit 0 = PASS, 1 = FAIL)
"""
import gzip
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MJ = os.path.join(ROOT, "bin", "mike_json.py")
FAILS = []


def check(name, cond, detail=""):
    if cond:
        print(f"  PASS  {name}")
    else:
        FAILS.append(f"{name} — {detail}")
        print(f"  FAIL  {name} — {detail}")


def mkbus():
    d = tempfile.mkdtemp(prefix="mike_json_archive_selfcheck_")
    os.makedirs(os.path.join(d, "inbox", "archive"), exist_ok=True)
    os.makedirs(os.path.join(d, "jobs", "archive"), exist_ok=True)
    return d


def write_jsonl(path, events, gz=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    body = "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in events)
    if gz:
        with gzip.open(path, "wt", encoding="utf-8") as f:
            f.write(body)
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(body)


def ev(agent, etype, topic, ts, trace_id=None, payload=None):
    e = {"agent_id": agent, "event_type": etype, "topic": topic, "ts": ts,
         "payload": payload or {}, "event_id": f"{agent}-{etype}-{topic}-{ts}"}
    if trace_id:
        e["trace_id"] = trace_id
    return e


def run(*args):
    p = subprocess.run([sys.executable, MJ, *args], capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


# ── Ca 1: trace tìm event nằm TRONG archive (.jsonl.gz), không chỉ hot ──
def case_trace_finds_archived_event():
    root = mkbus()
    try:
        write_jsonl(os.path.join(root, "inbox", "archive", "Winston_2026-06.jsonl.gz"),
                    [ev("Winston", "finding", "old-finding", "2026-06-01T00:00:00Z",
                        trace_id="Winston_20260601_010101")], gz=True)
        write_jsonl(os.path.join(root, "inbox", "Mike.jsonl"),
                    [ev("Mike", "status", "noise", "2026-08-01T00:00:00Z")])
        rc, out, _ = run("trace", root, "Winston_20260601_010101")
        check("trace: exit 0 khi tìm thấy event trong archive", rc == 0, f"rc={rc} out={out}")
        check("trace: nội dung event archive hiện đúng", "old-finding" in out, out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 2: trace tìm job record trong bus/jobs/archive/, gắn nhãn "(archived)" ──
def case_trace_finds_archived_job_record():
    root = mkbus()
    try:
        job_id = "Winston_20260601_010101"
        with open(os.path.join(root, "jobs", "archive", job_id + ".json"), "w") as f:
            json.dump({"from": "Mike", "to": "Winston", "status": "done",
                       "exit_code": 0, "logfile": "/tmp/x.log"}, f)
        write_jsonl(os.path.join(root, "inbox", "archive", "Winston_2026-06.jsonl.gz"),
                    [ev("Winston", "finding", "old-finding", "2026-06-01T00:00:00Z",
                        trace_id=job_id)], gz=True)
        rc, out, _ = run("trace", root, job_id)
        check("trace: đọc được job record từ bus/jobs/archive/", "status" in out, out)
        check("trace: gắn nhãn (archived) để phân biệt hot/archive",
              "(archived)" in out, out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 3: trace KHÔNG regress hành vi hot-only cũ (baseline) ──
def case_trace_still_finds_hot_event():
    root = mkbus()
    try:
        write_jsonl(os.path.join(root, "inbox", "Winston.jsonl"),
                    [ev("Winston", "finding", "new-finding", "2026-08-01T00:00:00Z",
                        trace_id="Winston_20260801_000000")])
        rc, out, _ = run("trace", root, "Winston_20260801_000000")
        check("trace: baseline hot-only vẫn hoạt động (không regression)",
              rc == 0 and "new-finding" in out, out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 4: verify-coverage tìm finding của agent mà TOÀN BỘ lịch sử nằm trong archive
#    (không có file hot nào) — trước đây báo "no inbox" sai (file hot không tồn tại).
def case_verify_coverage_agent_only_in_archive():
    root = mkbus()
    try:
        write_jsonl(os.path.join(root, "inbox", "archive", "Wendy_2026-06.jsonl.gz"),
                    [ev("Wendy", "finding", "old-legal-review", "2026-06-15T00:00:00Z",
                        trace_id="Wendy_20260615_000000")], gz=True)
        rc, out, _ = run("verify-coverage", root, "Wendy", "9999")
        check("verify-coverage: KHÔNG báo sai 'no inbox' khi agent chỉ có archive",
              "no inbox for agent" not in out, out)
        check("verify-coverage: liệt kê được finding archived (days đủ rộng)",
              "old-legal-review" in out, out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 5: verify-coverage khớp verification NẰM TRONG archive của agent KHÁC ──
def case_verify_coverage_matches_archived_verification():
    root = mkbus()
    try:
        write_jsonl(os.path.join(root, "inbox", "Taylor.jsonl"),
                    [ev("Taylor", "finding", "backtest-x", "2026-06-20T00:00:00Z",
                        trace_id="Taylor_20260620_000000")])
        write_jsonl(os.path.join(root, "inbox", "archive", "quant-skeptic_2026-06.jsonl.gz"),
                    [ev("quant-skeptic", "verification", "ARCH-REVIEW: backtest-x",
                        "2026-06-20T01:00:00Z", trace_id="Taylor_20260620_000000",
                        payload={"verdict": "CONFIRMED"})], gz=True)
        rc, out, _ = run("verify-coverage", root, "Taylor", "9999")
        check("verify-coverage: khớp verification archived (không báo unverified sai)",
              "CONFIRMED" in out, out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 6: file .jsonl.gz hỏng không làm chết lệnh (fail-safe, cùng nguyên tắc check #5) ──
def case_corrupt_archive_does_not_crash():
    root = mkbus()
    try:
        bad = os.path.join(root, "inbox", "archive", "Winston_2026-06.jsonl.gz")
        write_jsonl(bad, [ev("Winston", "finding", "x", "2026-06-01T00:00:00Z")], gz=True)
        with open(bad, "r+b") as f:
            f.truncate(os.path.getsize(bad) // 2)
        write_jsonl(os.path.join(root, "inbox", "Mike.jsonl"),
                    [ev("Mike", "status", "noise", "2026-08-01T00:00:00Z",
                        trace_id="Mike_20260801_000000")])
        rc, out, err = run("trace", root, "Mike_20260801_000000")
        check("trace: gz hỏng không crash, event hot khác vẫn đọc được",
              rc == 0 and "noise" in out, f"rc={rc} out={out} err={err}")
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main():
    print("mike_json_archive_selfcheck: trace + verify-coverage hot+archive scope")
    for fn in (case_trace_finds_archived_event, case_trace_finds_archived_job_record,
               case_trace_still_finds_hot_event, case_verify_coverage_agent_only_in_archive,
               case_verify_coverage_matches_archived_verification,
               case_corrupt_archive_does_not_crash):
        fn()
    if FAILS:
        print(f"\nFAIL: {len(FAILS)} assertion hỏng")
        for f in FAILS:
            print(f"  - {f}")
        return 1
    print("\nOK: toàn bộ assertion PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
