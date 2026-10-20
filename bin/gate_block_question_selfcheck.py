#!/usr/bin/env python3
"""Selfcheck cho bin/gate_block_question.py + 3 điểm wire (run_bot / send_plan_report / cadence).

Chạy: python3 bin/gate_block_question_selfcheck.py            (3 TZ + mutation)
      python3 bin/gate_block_question_selfcheck.py --core [--no-wiring] [--target H]   (1 lượt)
Mọi I/O ra ngoài (append_event/notify/audit/close) là STUB trong fixture root tạm — KHÔNG chạm
bus/Telegram thật. Exit 0 = PASS.
"""
from __future__ import annotations

import datetime as _dt
import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
HELPER = HERE / "gate_block_question.py"
ICT = ZoneInfo("Asia/Ho_Chi_Minh")
FAILS: list[str] = []
TMP: list[Path] = []


def check(cond, name):
    print(("  ok   " if cond else "  FAIL ") + name)
    if not cond:
        FAILS.append(name)


STUB_APPEND = r'''#!/usr/bin/env python3
import json, os, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
agent, et, topic, payload = sys.argv[1:5]
if os.path.exists(os.path.join(root, "APPEND_FAIL")) or (
        et == "status" and os.path.exists(os.path.join(root, "APPEND_FAIL_STATUS"))):
    print("stub append fail", file=sys.stderr); sys.exit(1)
os.makedirs(os.path.join(root, "bus", "inbox"), exist_ok=True)
with open(os.path.join(root, "bus", "inbox", agent + ".jsonl"), "a") as f:
    f.write(json.dumps({"agent_id": agent, "event_type": et, "topic": topic,
                        "payload": json.loads(payload)}, ensure_ascii=False) + "\n")
'''
STUB_NOTIFY = r'''#!/usr/bin/env bash
echo "$(basename "$0") $*" >> "$(dirname "$0")/../calls.log"
[ -e "$(dirname "$0")/../NOTIFY_FAIL" ] && exit 1
exit 0
'''
STUB_AUDIT = r'''#!/usr/bin/env python3
import glob, json, os, sys
root = os.environ["BUS_AUDIT_ROOT"]
if os.path.exists(os.path.join(root, "AUDIT_BROKEN")):
    print("not json"); sys.exit(3)
qs, res = [], set()
for p in glob.glob(os.path.join(root, "bus", "inbox", "*.jsonl")):
    for line in open(p):
        e = json.loads(line)
        if e["event_type"] == "question":
            qs.append((e["agent_id"], e["topic"]))
        for r in (e.get("payload") or {}).get("resolves", []):
            res.add(r)
pend = [{"agent": a, "topic": t} for a, t in qs if f"{a}/{t}" not in res]
print(json.dumps({"pending": pend})); sys.exit(len(pend))
'''
STUB_CLOSE = r'''#!/usr/bin/env python3
import json, os, sys, subprocess
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
mode_f = os.path.join(root, "CLOSE_MODE")
mode = open(mode_f).read().strip() if os.path.exists(mode_f) else "ok"
ref = sys.argv[1]
if mode == "blocked5":
    print("close_bus_question: BLOCKED stub", file=sys.stderr); sys.exit(5)
if mode == "rc4_says_closed":
    print("close_bus_question: CLOSED " + ref); sys.exit(4)
if mode == "unknown":
    print("close_bus_question: ALREADY_CLOSED_OR_UNKNOWN " + ref); sys.exit(0)
args = sys.argv[2:]
ev = args[args.index("--evidence") + 1]; actor = args[args.index("--actor") + 1]
subprocess.run([os.path.join(root, "bin", "append_event.sh"), actor, "answer", ref.split("/", 1)[1],
                json.dumps({"resolves": [ref], "evidence": ev})], check=True)
with open(os.path.join(root, "calls.log"), "a") as f:
    f.write("close " + ref + " EVIDENCE=" + ev + "\n")
print("close_bus_question: CLOSED " + ref)
'''


def mkroot() -> Path:
    r = Path(tempfile.mkdtemp(prefix="gbq_sc_"))
    TMP.append(r)
    (r / "bin").mkdir()
    for name, body in (("append_event.sh", STUB_APPEND), ("notify.sh", STUB_NOTIFY),
                       ("notify_thread.sh", STUB_NOTIFY), ("bus_question_audit.py", STUB_AUDIT),
                       ("close_bus_question.py", STUB_CLOSE)):
        p = r / "bin" / name
        p.write_text(body)
        p.chmod(0o755)
    return r


def run(target, root, *args, now=None, extra_env=None):
    env = dict(os.environ, GATE_BLOCK_ROOT=str(root), GATE_BLOCK_WC_ROOT=str(root))
    if now:
        env["GATE_BLOCK_NOW"] = now
    env.update(extra_env or {})
    r = subprocess.run([sys.executable, str(target), *args], env=env, capture_output=True,
                       text=True, timeout=60)
    return r.returncode, r.stdout + r.stderr


def events(root, agent="Mike", etype=None):
    p = root / "bus" / "inbox" / f"{agent}.jsonl"
    if not p.exists():
        return []
    return [e for e in map(json.loads, p.read_text().splitlines()) if etype in (None, e["event_type"])]


def questions(root, agent="Mike"):
    return events(root, agent, "question")


def calls(root):
    p = root / "calls.log"
    return p.read_text() if p.exists() else ""


def st(root, rid="approval__2026-10-20-SpaceX"):
    return json.loads((root / "state" / "gate_blocks" / f"{rid}.json").read_text())


def set_st(root, rec, rid="approval__2026-10-20-SpaceX"):
    (root / "state" / "gate_blocks" / f"{rid}.json").write_text(json.dumps(rec))


def open_args(key="2026-10-20-SpaceX", probe="false", every="15", gate="approval",
              expires="2026-10-20T15:00", extra=()):
    return ["open", "--gate", gate, "--key", key, "--owner", "user; Mike",
            "--deadline", "2026-10-20T10:00", "--recover", "bin/run_bot.sh --account SpaceX",
            "--probe", probe, "--reason", "APPROVAL_GATE_BLOCK test", "--thread", "trading_daily",
            "--remind-every-min", every, "--expires-at", expires, "--extra", '{"account":"SpaceX"}',
            *extra]


def ts(s: str) -> float:
    return _dt.datetime.fromisoformat(s).timestamp()


def core(target: Path) -> None:
    T0 = "2026-10-20T09:06:00+07:00"
    # 1-3: mở + idempotent theo (gate,key) + ack triaged-needs-human (B4)
    R = mkroot()
    rc, out = run(target, R, *open_args(), now=T0)
    qs = questions(R)
    check(rc == 0 and "OPENED" in out and len(qs) == 1, "open: OPENED + đúng 1 question")
    check(st(R)["status"] == "open" and st(R)["ack_posted"] is True, "open: sổ status=open + ack_posted")
    p = qs[0]["payload"] if qs else {}
    check(p.get("owner") and p.get("deadline_ict") == "2026-10-20T10:00" and p.get("recover_cmd")
          and p.get("expires_ict") == "2026-10-20T15:00"
          and p.get("gate_block_id") == "approval__2026-10-20-SpaceX" and p.get("account") == "SpaceX",
          "payload có owner/deadline/expires/recover/gate_block_id + extra gộp")
    check(qs and qs[0]["topic"] == "gate-block-approval-2026-10-20-SpaceX", "topic mặc định gate-block-<gate>-<key>")
    acks = events(R, etype="status")
    check(len(acks) == 1 and acks[0]["topic"] == "triaged-needs-human: gate-block-approval-2026-10-20-SpaceX"
          and acks[0]["payload"].get("suppress_days") == 1,
          "B4: status 'triaged-needs-human: <topic>' + suppress_days=1 (hạn trong ngày)")
    ohc = (HERE / "ops_health_check.sh")
    if ohc.exists():
        check('ACK_PREFIX = "triaged-needs-human:"' in ohc.read_text(), "B4: ACK_PREFIX helper khớp ops_health_check.sh")
    rc, out = run(target, R, *open_args(), now=T0)
    check(rc == 0 and "ALREADY_OPEN" in out and len(questions(R)) == 1 and len(events(R, etype="status")) == 1,
          "open lặp cùng gate+key ⇒ KHÔNG mở trùng, không ack trùng")
    run(target, R, *open_args(key="2026-10-20-ZaloPay"), now=T0)
    check(len(questions(R)) == 2, "key khác (account khác) ⇒ question riêng")
    check(not list((R / "state/gate_blocks").glob(".tmp_*")), "claim tmp+link: không sót file .tmp_")

    # 4: bị kill giữa post và ghi sổ ⇒ sổ 'posting' + bus đã có ⇒ không post lại
    rec = st(R); rec["status"] = "posting"; set_st(R, rec)
    run(target, R, *open_args(), now=T0)
    check(len(questions(R)) == 2 and st(R)["status"] == "open",
          "kill sau post: sổ posting + bus đã có ⇒ không post lại, sổ về open")
    # 4b: bus có event cùng gate_block_id nhưng KHÁC topic ⇒ không tính là đã post
    Rb = mkroot()
    subprocess.run([str(Rb / "bin/append_event.sh"), "Mike", "question", "topic-khac",
                    json.dumps({"gate_block_id": "approval__2026-10-20-SpaceX"})], check=True)
    (Rb / "state/gate_blocks").mkdir(parents=True)
    rec = dict(st(R)); rec.update(status="posting", ack_posted=False); set_st(Rb, rec)
    run(target, Rb, *open_args(), now=T0)
    check([q["topic"] for q in questions(Rb)] == ["topic-khac", "gate-block-approval-2026-10-20-SpaceX"],
          "bus_has_question so cả topic: gate_block_id trùng ở topic khác ⇒ vẫn post")

    # 5: append hỏng ⇒ posting, sweep sau post đúng 1 lần; ack hỏng ⇒ sweep bù ack
    R2 = mkroot(); (R2 / "APPEND_FAIL").write_text("1")
    rc, out = run(target, R2, *open_args(), now=T0)
    check(rc != 0 and st(R2)["status"] == "posting" and not questions(R2),
          "append lỗi ⇒ rc≠0, sổ posting, chưa có question")
    rc, out = run(target, R2, "sweep", "--dry-run", now=T0)
    check(not questions(R2) and st(R2)["status"] == "posting" and "POSTING_RETRY_PENDING" in out,
          "N1: sweep --dry-run KHÔNG post bù")
    (R2 / "APPEND_FAIL").unlink(); (R2 / "APPEND_FAIL_STATUS").write_text("1")
    run(target, R2, "sweep", now=T0)
    check(len(questions(R2)) == 1 and st(R2)["status"] == "open" and not st(R2)["ack_posted"],
          "sweep post bù question; ack lỗi ⇒ ack_posted=False")
    (R2 / "APPEND_FAIL_STATUS").unlink()
    run(target, R2, "sweep", now=T0)
    check(len(questions(R2)) == 1 and len(events(R2, etype="status")) == 1 and st(R2)["ack_posted"],
          "sweep sau: không post question lần 2, bù ack đúng 1 lần")

    # 6: probe fail ⇒ nhắc, throttle (biên đúng 15'), quá hạn
    R3 = mkroot()
    run(target, R3, *open_args(probe="exit 1"), now=T0)
    rc, out = run(target, R3, "sweep", now="2026-10-20T09:10:00+07:00")
    check("REMIND" in out and "còn 50 phút" in out and calls(R3).count("notify.sh") == 1
          and "notify_thread.sh" in calls(R3) and st(R3)["reminders"] == 1,
          "probe rc≠0 ⇒ nhắc Telegram+thread, 'còn 50 phút' (ICT), reminders=1")
    rc, out = run(target, R3, "sweep", "--dry-run", now="2026-10-20T09:40:00+07:00")
    check("REMIND" in out and calls(R3).count("notify.sh") == 1 and st(R3)["reminders"] == 1,
          "N1: --dry-run in REMIND nhưng KHÔNG notify, không ghi sổ")
    rc, out = run(target, R3, "sweep", now="2026-10-20T09:24:59+07:00")
    check(calls(R3).count("notify.sh") == 1 and "STILL_OPEN" in out, "throttle: <15' không nhắc lại")
    rc, out = run(target, R3, "sweep", now="2026-10-20T09:25:00+07:00")
    check(calls(R3).count("notify.sh") == 2, "throttle: đúng 15' ⇒ nhắc lại (biên <, không <=)")
    rc, out = run(target, R3, "sweep", now="2026-10-20T03:20:00+00:00")  # = 10:20 ICT
    check(calls(R3).count("notify.sh") == 3 and "QUÁ HẠN 20 phút" in out and "còn -" not in out,
          "qua hạn ⇒ nhắc 'QUÁ HẠN 20 phút' (now nhập UTC, so theo ICT)")
    check(not events(R3, etype="answer"), "probe fail KHÔNG BAO GIỜ đóng question")

    # 6b: notify lỗi KHÔNG tính là đã nhắc (N4)
    (R3 / "NOTIFY_FAIL").write_text("1")
    n0 = st(R3)["reminders"]
    rc, out = run(target, R3, "sweep", now="2026-10-20T10:40:00+07:00")
    check("REMIND_UNDELIVERED" in out and st(R3)["reminders"] == n0, "notify lỗi ⇒ REMIND_UNDELIVERED, reminders không tăng")
    (R3 / "NOTIFY_FAIL").unlink()
    rc, out = run(target, R3, "sweep", now="2026-10-20T10:41:00+07:00")
    check(st(R3)["reminders"] == n0 + 1, "notify lỗi lượt trước ⇒ lượt sau (trong 15') vẫn nhắc lại")

    # 7: probe rc=0 ⇒ đóng qua close_bus_question, evidence chứa lệnh probe; probe nhận OPENED_AT
    flag = R3 / "RECOVERED"
    rec = st(R3)
    rec["probe"] = f'test -e {flag} && test "$GATE_BLOCK_OPENED_AT" = "{rec["opened_at"]}" && echo journal-ok'
    set_st(R3, rec)
    flag.write_text("1")
    rc, out = run(target, R3, "sweep", now="2026-10-20T10:50:00+07:00")
    check("CLOSED Mike/gate-block-approval" in out and st(R3)["status"] == "closed"
          and "journal-ok" in calls(R3) and "test -e" in calls(R3),
          "probe rc=0 (nhận GATE_BLOCK_OPENED_AT=opened_at) ⇒ CLOSED, evidence = lệnh + output probe")
    n = calls(R3).count("notify.sh")
    (R3 / "AUDIT_BROKEN").write_text("1")
    rec = st(R3); rec["probe"] = "exit 1"; set_st(R3, rec)
    run(target, R3, "sweep", now="2026-10-20T11:30:00+07:00")
    check(calls(R3).count("notify.sh") == n, "N1: record closed bị bỏ qua kể cả khi audit hỏng")
    (R3 / "AUDIT_BROKEN").unlink()
    rc, out = run(target, R3, *open_args(probe="exit 1"), now="2026-10-20T13:01:00+07:00")
    check("ALREADY_CLOSED" in out and len(questions(R3)) == 1, "block lại cùng ngày sau khi đóng ⇒ không mở câu mới")

    # 7b: probe tương đối chạy với cwd=WC_ROOT
    Rc = mkroot()
    run(target, Rc, *open_args(probe="test -e REL_FLAG"), now=T0)
    (Rc / "REL_FLAG").write_text("1")
    rc, out = run(target, Rc, "sweep", now=T0)
    check(st(Rc)["status"] == "closed", "probe đường dẫn tương đối chạy trong WC_ROOT")

    # 8: probe không chạy được / timeout ⇒ không đóng (N1)
    R4 = mkroot()
    run(target, R4, *open_args(probe="/nonexistent/probe_cmd"), now=T0)
    rc, out = run(target, R4, "sweep", now=T0)
    check("REMIND" in out and st(R4)["status"] == "open", "probe lỗi (rc127) ⇒ nhắc, không đóng")
    Rt = mkroot()
    run(target, Rt, *open_args(probe="sleep 5; true"), now=T0)
    rc, out = run(target, Rt, "sweep", now=T0, extra_env={"GATE_BLOCK_PROBE_TIMEOUT_S": "1"})
    check("probe timeout 1s" in out and "rc=124" in out and st(Rt)["status"] == "open",
          "N1: probe timeout ⇒ rc124, nhắc, KHÔNG đóng")
    Ro = mkroot()
    run(target, Ro, *open_args(probe="true"), now=T0)
    rc, out = run(target, Ro, "sweep", now=T0, extra_env={"GATE_BLOCK_WC_ROOT": str(Ro / "khong_ton_tai")})
    check("probe không chạy được" in out and "rc=127" in out and st(Ro)["status"] == "open",
          "N1: probe OSError (cwd không tồn tại) ⇒ rc127, KHÔNG đóng")

    # 9: người đóng trên bus ⇒ ngừng nhắc; câu cùng topic của agent KHÁC không giữ nó mở
    subprocess.run([str(R4 / "bin/append_event.sh"), "Winston", "question",
                    "gate-block-approval-2026-10-20-SpaceX", "{}"], check=True)
    subprocess.run([str(R4 / "bin/append_event.sh"), "Mike", "answer", "x",
                    json.dumps({"resolves": ["Mike/gate-block-approval-2026-10-20-SpaceX"]})], check=True)
    n = calls(R4).count("notify.sh")
    rc, out = run(target, R4, "sweep", now="2026-10-20T12:00:00+07:00")
    check("CLOSED_EXTERNALLY" in out and calls(R4).count("notify.sh") == n,
          "đóng tay trên bus ⇒ CLOSED_EXTERNALLY (lọc đúng agent), ngừng nhắc")

    # 10: audit hỏng ⇒ coi như còn mở (nhắc), không đóng
    R5 = mkroot()
    run(target, R5, *open_args(probe="exit 1"), now=T0)
    (R5 / "AUDIT_BROKEN").write_text("1")
    rc, out = run(target, R5, "sweep", now=T0)
    check("AUDIT_UNREADABLE" in out and "REMIND" in out and st(R5)["status"] == "open",
          "audit hỏng ⇒ fail-loud: vẫn nhắc, không tự đóng")

    # 11: close_bus_question chặn/không in đúng dòng CLOSED ⇒ không ép đóng (N5)
    for mode, want in (("blocked5", "close_bus_question rc=5"), ("rc4_says_closed", "close_bus_question rc=4"),
                       ("unknown", "ALREADY_CLOSED_OR_UNKNOWN")):
        R6 = mkroot()
        run(target, R6, *open_args(probe="true"), now=T0)
        (R6 / "CLOSE_MODE").write_text(mode)
        rc, out = run(target, R6, "sweep", now=T0)
        check(st(R6)["status"] == "open" and want in out, f"N5: close mode={mode} ⇒ giữ open + nhắc lý do")

    # 12-13: slug xấu / sổ hỏng / thiếu expiry
    R7 = mkroot()
    rc, out = run(target, R7, *open_args(key="2026-10-20 Space X"), now=T0)
    check(rc == 2 and not questions(R7), "key có ký tự lạ ⇒ rc2, không post")
    a = open_args(); i = a.index("--expires-at"); del a[i:i + 2]
    rc, out = run(target, R7, *a, now=T0)
    check(rc == 2 and "expires" in out and not questions(R7), "B1: thiếu --expires-at/--expires-in-days ⇒ rc2")
    (R7 / "state/gate_blocks").mkdir(parents=True, exist_ok=True)
    (R7 / "state/gate_blocks/approval__2026-10-20-SpaceX.json").write_text("{cut")
    rc, out = run(target, R7, *open_args(), now=T0)
    check(rc == 1 and "STATE_UNREADABLE" in out and not questions(R7), "sổ hỏng ⇒ không post (thà thiếu hơn trùng)")

    # 13b: một record hỏng không chặn record khác (N1)
    run(target, R7, *open_args(key="2026-10-20-ZaloPay", probe="exit 1"), now=T0)
    rc, out = run(target, R7, "sweep", now=T0)
    check(rc == 1 and "SWEEP_ERROR approval__2026-10-20-SpaceX.json" in out
          and "REMIND approval__2026-10-20-ZaloPay" in out,
          "N1: record hỏng ⇒ SWEEP_ERROR rc1 nhưng record khác vẫn được nhắc")

    # 14: --topic giữ topic cũ; reason cắt 400
    R8 = mkroot()
    args = open_args(gate="plan-t1-not-ready", key="2026-10-21-SpaceX") + ["--topic", "plan-t1-not-ready-SpaceX"]
    i = args.index("--reason"); args[i + 1] = "x" * 1000
    run(target, R8, *args, now=T0)
    check([q["topic"] for q in questions(R8)] == ["plan-t1-not-ready-SpaceX"], "--topic giữ topic cũ")
    check(len(st(R8, "plan-t1-not-ready__2026-10-21-SpaceX")["reason"]) == 400, "reason cắt 400 ký tự")

    # 14b: đồng hồ THẬT (không GATE_BLOCK_NOW) phải neo ICT, độc lập TZ host (§16)
    Rr = mkroot()
    now = _dt.datetime.now(ICT)
    a = open_args(probe="exit 1", expires=(now + _dt.timedelta(hours=6)).strftime("%Y-%m-%dT%H:%M"))
    a[a.index("--deadline") + 1] = (now + _dt.timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M")
    run(target, Rr, *a)
    rc, out = run(target, Rr, "sweep")
    m = re.search(r"còn (\d+) phút", out)
    check(bool(m) and 170 <= int(m.group(1)) <= 180,
          f"đồng hồ thật neo ICT: hạn +3h ⇒ 'còn ~179 phút' (thấy {m.group(0) if m else out[-80:]!r})")

    # 15: B1 — EXPIRED theo thời gian: 1 tin cuối rồi im hẳn
    R10 = mkroot()
    run(target, R10, *open_args(probe="exit 1"), now=T0)
    run(target, R10, "sweep", now="2026-10-20T14:50:00+07:00")
    n = calls(R10).count("notify.sh")
    rc, out = run(target, R10, "sweep", now="2026-10-20T15:00:00+07:00")
    check("EXPIRED" in out and "tin CUỐI" in calls(R10) and calls(R10).count("notify.sh") == n + 1
          and st(R10)["status"] == "expired", "B1: tới expires_at ⇒ EXPIRED + đúng 1 tin cuối")
    for t in ("2026-10-20T16:00:00+07:00", "2026-10-21T09:00:00+07:00"):
        run(target, R10, "sweep", now=t)
    check(calls(R10).count("notify.sh") == n + 1 and not events(R10, etype="answer"),
          "B1: sau EXPIRED sweep im lặng hẳn, không tự đóng question")
    rc, out = run(target, R10, *open_args(probe="exit 1"), now="2026-10-20T16:00:00+07:00")
    check("ALREADY_EXPIRED" in out and len(questions(R10)) == 1, "B1: open lại cùng key sau EXPIRED ⇒ không mở mới")
    # 15b: dry-run không expire
    R11 = mkroot()
    run(target, R11, *open_args(probe="exit 1"), now=T0)
    rc, out = run(target, R11, "sweep", "--dry-run", now="2026-10-20T15:30:00+07:00")
    check("EXPIRED" in out and st(R11)["status"] == "open" and "notify" not in calls(R11),
          "B1: --dry-run in EXPIRED nhưng không ghi sổ/không notify")
    # 15c: probe phục hồi đúng lúc hết hạn ⇒ ĐÓNG, không expire
    (R11 / "OK").write_text("1")
    rec = st(R11); rec["probe"] = f"test -e {R11 / 'OK'}"; set_st(R11, rec)
    run(target, R11, "sweep", now="2026-10-20T15:30:00+07:00")
    check(st(R11)["status"] == "closed", "B1: hết hạn nhưng probe rc=0 ⇒ CLOSED (ưu tiên đóng)")

    # 16: B1 — trần số lần nhắc
    R12 = mkroot()
    run(target, R12, *open_args(probe="exit 1", extra=("--max-reminders", "2")), now=T0)
    for t in ("09:10", "09:30", "09:50", "10:10", "10:30"):
        run(target, R12, "sweep", now=f"2026-10-20T{t}:00+07:00")
    c = calls(R12)
    check(c.count("notify.sh") == 3 and c.count("CỔNG CHẶN CHƯA PHỤC HỒI") == 4 and "đạt trần 2" in c
          and st(R12)["status"] == "expired" and st(R12)["reminders"] == 2,
          "B1: --max-reminders 2 ⇒ 2 lời nhắc + 1 tin cuối rồi dừng")

    # 17: --expires-in-days + suppress_days cho delivery
    R13 = mkroot()
    a = open_args(gate="delivery", key="X_weekly_report_2026-10-16.md")
    i = a.index("--expires-at"); a[i:i + 2] = ["--expires-in-days", "3"]
    run(target, R13, *a, now=T0)
    r13 = st(R13, "delivery__X_weekly_report_2026-10-16.md")
    check(r13["expires_at"] == "2026-10-23T09:06" and [e["payload"].get("suppress_days") for e in events(R13, etype="status")] == [4],
          "--expires-in-days 3 ⇒ expires +3 ngày, ack suppress_days=4")

    # 18: B3 — recover-kind instructions + next-step theo rc probe
    R14 = mkroot()
    pr = R14 / "prc"; pr.write_text("10")
    run(target, R14, *open_args(probe=f'exit $(cat {pr})', extra=(
        "--recover-kind", "instructions", "--next-step", "11=Mike: chạy run_bot.sh --auto-otp")), now=T0)
    p = questions(R14)[0]["payload"]
    check("recover_cmd" not in p and p.get("recover_instructions") and "CHỈ DẪN cho người" in p["question"]
          and p.get("next_step_when_probe_rc") == {"11": "Mike: chạy run_bot.sh --auto-otp"},
          "B3: instructions ⇒ payload KHÔNG có recover_cmd, có recover_instructions + next_step")
    rc, out = run(target, R14, "sweep", now="2026-10-20T09:10:00+07:00")
    check("BƯỚC KẾ" not in out and "phục hồi: bin/run_bot.sh" in out, "B3: probe rc=10 ⇒ nhắc chỉ dẫn duyệt, chưa có bước Mike")
    pr.write_text("11")
    rc, out = run(target, R14, "sweep", now="2026-10-20T09:30:00+07:00")
    check("BƯỚC KẾ: Mike: chạy run_bot.sh --auto-otp" in out, "B3: probe rc=11 ⇒ nhắc BƯỚC KẾ của Mike")
    rc, _ = run(target, R14, *open_args(key="k2", extra=("--next-step", "abc")), now=T0)
    check(rc == 2, "--next-step sai dạng ⇒ rc2")

    # 19: N2 flock — sweep đang chạy ⇒ lượt khác bỏ qua
    R15 = mkroot()
    run(target, R15, *open_args(probe="exit 1"), now=T0)
    with open(R15 / "state/gate_blocks/.sweep.lock", "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        rc, out = run(target, R15, "sweep", now=T0)
    check(rc == 0 and "SWEEP_BUSY" in out and "notify" not in calls(R15), "N2: flock — sweep song song bỏ lượt")

    # 20: N8 dọn record closed/expired > 30 ngày
    R16 = mkroot()
    run(target, R16, *open_args(probe="exit 1"), now=T0)
    run(target, R16, *open_args(key="old2", probe="exit 1"), now=T0)
    rec = st(R16); rec.update(status="closed", closed_at="2026-09-19T09:00:00+07:00"); set_st(R16, rec)
    rec = st(R16, "approval__old2"); rec.update(status="expired", expired_at="2026-09-21T09:00:00+07:00")
    set_st(R16, rec, "approval__old2")
    rc, out = run(target, R16, "sweep", "--dry-run", now="2026-10-20T09:30:00+07:00")
    check((R16 / "state/gate_blocks/approval__2026-10-20-SpaceX.json").exists(), "N8: dry-run không xoá")
    rc, out = run(target, R16, "sweep", now="2026-10-20T09:30:00+07:00")
    check(not (R16 / "state/gate_blocks/approval__2026-10-20-SpaceX.json").exists() and "PRUNED" in out
          and (R16 / "state/gate_blocks/approval__old2.json").exists(),
          "N8: closed 31 ngày ⇒ PRUNED; expired 29 ngày ⇒ giữ")

    # 20b: B4 tích hợp — chạy KHỐI CHECK5 THẬT của ops_health_check.sh trên bus giả: question có ack
    # của helper ⇒ dòng 'ĐÃ TRIAGE' [WARN-ONLY], KHÔNG nằm trong danh sách routable; control không ack ⇒ routable.
    ohc = HERE / "ops_health_check.sh"
    mb = re.search(r"^# CHECK5_BEGIN.*?\n(.*?)^# CHECK5_END", ohc.read_text(), re.S | re.M) if ohc.exists() else None
    check(bool(mb), "B4: trích được khối CHECK5 của ops_health_check.sh")
    if mb:
        Wr = Path(tempfile.mkdtemp(prefix="gbq_ohc_")); TMP.append(Wr)
        Rw = Wr / "mike"; Rw.mkdir()
        Rm = mkroot(); shutil.copytree(Rm / "bin", Rw / "bin")
        (Rw / "agents").mkdir()
        run(target, Rw, *open_args(key="2026-10-20-SpaceX", probe="exit 1"))
        three_h = (_dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
        inbox = Rw / "bus/inbox/Mike.jsonl"
        evs = [dict(e, ts=three_h, event_id=f"e{i}") for i, e in enumerate(map(json.loads, inbox.read_text().splitlines()))]
        evs.append({"agent_id": "Mike", "event_type": "question", "topic": "control-khong-ack", "ts": three_h,
                    "payload": {}, "event_id": "ctl"})
        inbox.write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in evs))
        lines = []
        ns = {"glob": __import__("glob"), "gzip": __import__("gzip"), "json": json, "os": os, "re": re,
              "wc_root": str(Wr), "W": lambda m: lines.append("⚠️ " + m), "OK": lambda m: lines.append("✅ " + m),
              "lines": lines}
        try:
            exec(compile(mb.group(1), str(ohc) + ":CHECK5", "exec"), ns)
        except Exception as exc:
            lines.append(f"EXC {type(exc).__name__}: {exc}")
        human = "\n".join(ln for ln in lines if "ĐÃ TRIAGE" in ln)
        pend = "\n".join(ln for ln in lines if "CHƯA thấy answer" in ln)
        check("gate-block-approval-2026-10-20-SpaceX" in human and "gate-block-approval-2026-10-20-SpaceX" not in pend
              and "control-khong-ack" in pend,
              "B4: CHECK5 thật — question có ack helper ⇒ ĐÃ TRIAGE (không dispatch Wags); control ⇒ routable "
              f"[{' | '.join(lines)[:300]!r}]")

    # 21: probe approval (module trading_bot giả) — B2 journal phải MỚI HƠN lúc mở
    R9 = mkroot()
    (R9 / "trading_bot").mkdir()
    (R9 / "trading_bot/__init__.py").write_text("")
    (R9 / "trading_bot/plan.py").write_text(
        "import os, types\n"
        "def load_plan(d, account):\n"
        "    m = os.environ.get('FAKE_PLAN')\n"
        "    return None if m == 'none' else types.SimpleNamespace(approved_by=(m in ('ok', 'hold')) and 'user' or None,\n"
        "                                                          orders=[] if m == 'hold' else [1])\n"
        "def approval_block_reason(p):\n"
        "    return None if p.approved_by else 'chua duyet'\n")
    since = "2026-10-20T09:06:00+07:00"
    pa = ["probe", "approval", "--account", "SpaceX", "--date", "2026-10-20", "--since", since]
    check(run(target, R9, *pa, extra_env={"FAKE_PLAN": "none"})[0] == 12, "probe approval: không có plan ⇒ 12 (≠ còn chặn)")
    rc, out = run(target, R9, *pa, extra_env={"FAKE_PLAN": "blocked"})
    check(rc == 10 and "VẪN CHẶN — chua duyet" in out, "probe approval: chưa duyệt ⇒ 10 + lý do thật")
    check(run(target, R9, *pa, extra_env={"FAKE_PLAN": "ok"})[0] == 11, "probe approval: duyệt nhưng chưa có journal ⇒ 11")
    check(run(target, R9, *pa, extra_env={"FAKE_PLAN": "hold"})[0] == 0, "probe approval: plan sửa thành HOLD (0 lệnh) ⇒ 0")
    j = R9 / "data/execution_logs/exec_SpaceX_2026-10-20_journal.csv"
    j.parent.mkdir(parents=True); j.write_text("x")
    os.utime(j, (ts("2026-10-20T09:05:30+07:00"),) * 2)
    check(run(target, R9, *pa, extra_env={"FAKE_PLAN": "ok"})[0] == 11,
          "B2: journal có TRƯỚC lúc mở (lượt bot sớm) ⇒ 11, KHÔNG phục hồi")
    check(run(target, R9, *pa[:-2], extra_env={"FAKE_PLAN": "ok"})[0] == 11,
          "B2: không có since/OPENED_AT ⇒ không chứng minh được ⇒ 11")
    os.utime(j, (ts("2026-10-20T09:25:00+07:00"),) * 2)
    check(run(target, R9, *pa, extra_env={"FAKE_PLAN": "ok"})[0] == 0, "probe approval: duyệt + journal SAU lúc mở ⇒ 0")
    check(run(target, R9, *pa[:-2], extra_env={"FAKE_PLAN": "ok", "GATE_BLOCK_OPENED_AT": since})[0] == 0,
          "probe approval: since lấy từ env GATE_BLOCK_OPENED_AT (sweep đặt)")

    # 22: B2 — probe plan-t1 (tái hiện /tmp/arch_mut/b2.py: marker 21:00 bản cũ KHÔNG được đóng)
    R17 = mkroot()
    md, pd = R17 / "plan_report_sent", R17 / "trade_plans"
    md.mkdir(); pd.mkdir()
    plan = pd / "plan_SpaceX_2026-10-21.json"
    plan.write_text(json.dumps({"orders": [{"t": "FPT"}], "approved_by": "x"}))
    sys.path.insert(0, str(target.parent))
    import importlib.util
    spec = importlib.util.spec_from_file_location("gbq_under_test", target)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    good = mod.plan_content_hash(plan)
    plan2 = json.dumps({"orders": [{"t": "FPT"}], "approved_by": "khac", "mafee_x": 1})
    check(mod.plan_content_hash(plan) == good and good == __import__("hashlib").md5(
        json.dumps({"orders": [{"t": "FPT"}]}, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        and plan2, "plan_content_hash khớp công thức send_plan_report (bỏ approv*/mafee*)")
    marker = md / "SpaceX_2026-10-21.json"
    marker.write_text(json.dumps({"sent_at": "2026-10-20 21:00 ICT", "content_md5": "OLD"}))
    os.utime(marker, (ts("2026-10-20T21:00:05+07:00"),) * 2)
    probe = f"python3 {target} probe plan-t1 --account SpaceX --date 2026-10-21 --marker-dir {md} --plan-dir {pd}"
    a = ["open", "--gate", "plan-t1-not-ready", "--key", "2026-10-21-SpaceX", "--topic", "plan-t1-not-ready-SpaceX",
         "--owner", "Mike", "--deadline", "2026-10-21T08:30", "--recover", "x", "--probe", probe,
         "--reason", "Plan T+1 chưa sẵn sàng (plan_unparseable)", "--thread", "plan_approval",
         "--remind-every-min", "60", "--expires-at", "2026-10-21T23:59", "--extra", "{}"]
    run(target, R17, *a, now="2026-10-20T23:00:30+07:00")
    rid = "plan-t1-not-ready__2026-10-21-SpaceX"
    rc, out = run(target, R17, "sweep", now="2026-10-20T23:15:00+07:00")
    check(st(R17, rid)["status"] == "open" and "marker CŨ" in out,
          "B2: marker có TRƯỚC lúc mở ⇒ KHÔNG đóng (tái hiện b2.py)")
    marker.write_text(json.dumps({"sent_at": "2026-10-20 23:20 ICT", "content_md5": "OLD"}))
    os.utime(marker, (ts("2026-10-20T23:20:05+07:00"),) * 2)
    rc, out = run(target, R17, "sweep", now="2026-10-21T00:20:00+07:00")
    check(st(R17, rid)["status"] == "open" and "≠ plan hiện tại" in out, "B2: marker mới nhưng md5 ≠ plan hiện tại ⇒ KHÔNG đóng")
    marker.write_text(json.dumps({"sent_at": "2026-10-20 23:00 ICT", "content_md5": good}))
    os.utime(marker, (ts("2026-10-20T23:00:20+07:00"),) * 2)
    rc, out = run(target, R17, "sweep", now="2026-10-21T01:30:00+07:00")
    check(st(R17, rid)["status"] == "open", "B2: md5 khớp nhưng mtime (23:00:20) ≤ lúc mở 23:00:30 ⇒ KHÔNG đóng")
    os.utime(marker, (ts("2026-10-20T23:00:50+07:00"),) * 2)
    rc, out = run(target, R17, "sweep", now="2026-10-21T02:40:00+07:00")
    check(st(R17, rid)["status"] == "closed" and "probe plan-t1: OK" in calls(R17),
          "B2: marker ghi SAU lúc mở (cùng phút) + md5 khớp plan ⇒ CLOSED")
    check(run(target, R17, "probe", "plan-t1", "--account", "SpaceX", "--date", "2026-10-21",
              "--marker-dir", str(md), "--plan-dir", str(pd))[0] == 11, "probe plan-t1: không có since ⇒ 11")
    plan.unlink()
    check(run(target, R17, "probe", "plan-t1", "--account", "SpaceX", "--date", "2026-10-21", "--since",
              "2026-10-20T23:00:30+07:00", "--marker-dir", str(md), "--plan-dir", str(pd))[0] == 11,
          "probe plan-t1: plan hiện tại biến mất ⇒ 11")


def extract(path: Path, begin: str, end: str) -> str:
    s = path.read_text()
    m = re.search(rf"^[^\n]*{begin}[^\n]*\n(.*?)^[^\n]*{end}", s, re.S | re.M)
    if not m:
        print(f"FATAL: marker {begin}/{end} không thấy trong {path.name}")
        sys.exit(2)
    return m.group(1)


STUB_HELPER = r'''#!/usr/bin/env python3
import os, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(root, "helper_calls.log"), "a") as f:
    f.write("\x1e".join(sys.argv[1:]) + "\n")
if sys.argv[1] == "probe":
    rc = int(os.environ.get("STUB_PROBE_RC", "10"))
    print({10: "probe approval: VẪN CHẶN — requires_user_approval chua duyet", 12: "probe approval: KHÔNG CÓ PLAN"}.get(rc, "probe x"))
    sys.exit(rc)
mode = os.environ.get("STUB_OPEN", "ok")
if mode == "ok":
    print("gate_block_question: OPENED x"); sys.exit(0)
if mode == "crash":
    print("Traceback boom", file=sys.stderr); sys.exit(2)
'''


def arg_of(call: str, flag: str) -> str:
    parts = call.split("\x1e")
    return parts[parts.index(flag) + 1] if flag in parts else ""


def wiring(bin_dir: Path) -> None:
    W = Path(tempfile.mkdtemp(prefix="gbq_wire_"))
    TMP.append(W)
    (W / "mike/bin").mkdir(parents=True)
    h = W / "mike/bin/gate_block_question.py"; h.write_text(STUB_HELPER); h.chmod(0o755)
    ap = W / "mike/bin/append_event.sh"
    ap.write_text('#!/usr/bin/env bash\necho "append $*" >> "$(dirname "$0")/../fallback.log"\n'); ap.chmod(0o755)
    log = W / "mike/helper_calls.log"
    botlog = W / "bot.log"

    blk = extract(bin_dir / "run_bot.sh", "GATE_BLOCK_APPROVAL_BEGIN", "GATE_BLOCK_APPROVAL_END")
    script = ("set -euo pipefail\nROOT=%s\nWC_ROOT=%s\nACCOUNT=SpaceX\nPLAN_DATE=2026-10-20\n"
              "LOG=%s\n_tid=trading_daily\nrc=$RC\n%s\necho FINAL_RC=$rc\n") % (W / "mike", W, botlog, blk)

    def rb(rc, probe_rc, open_mode="ok"):
        for f in (log, botlog):
            if f.exists():
                f.unlink()
        r = subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=60,
                           env=dict(os.environ, RC=str(rc), STUB_PROBE_RC=str(probe_rc), STUB_OPEN=open_mode))
        return r, (log.read_text() if log.exists() else ""), (botlog.read_text() if botlog.exists() else "")

    r, c, bl = rb(2, 10)
    op = [x for x in c.split("\n") if x.startswith("open")]
    o = op[0] if op else ""
    check("FINAL_RC=2" in r.stdout and arg_of(o, "--key") == "2026-10-20-SpaceX"
          and arg_of(o, "--deadline") == "2026-10-20T10:00" and arg_of(o, "--expires-at") == "2026-10-20T15:00",
          "run_bot: rc=2 + probe 10 ⇒ open (hạn 10:00, EXPIRED 15:00), rc giữ 2")
    rec_txt = arg_of(o, "--recover")
    check(arg_of(o, "--recover-kind") == "instructions" and "&&" not in rec_txt and "run_bot.sh" not in rec_txt
          and rec_txt.startswith("USER:") and arg_of(o, "--next-step").startswith("11=Mike:")
          and "run_bot.sh --account SpaceX --auto-otp" in arg_of(o, "--next-step"),
          "B3: recover = CHỈ DẪN user (không lệnh nối, không run_bot); bước Mike chỉ ở next-step rc=11")
    check("VẪN CHẶN — requires_user_approval chua duyet" in arg_of(o, "--reason")
          and "probe approval rc=10: probe approval: VẪN CHẶN" in bl and "OPENED" in bl,
          "N4: reason nội suy từ output probe; output probe + helper ghi vào LOG")
    r, c, bl = rb(2, 12)
    check("FINAL_RC=2" in r.stdout and "open" not in c and "probe rc=12" in bl,
          "N4: rc=2 + probe 12 (không có plan) ⇒ không open, ghi log tách biệt")
    r, c, bl = rb(2, 0)
    check("FINAL_RC=2" in r.stdout and "open" not in c, "run_bot: rc=2 nhưng probe≠10 (không phải approval) ⇒ không open")
    r, c, bl = rb(0, 10)
    check("FINAL_RC=0" in r.stdout and c == "", "run_bot: rc=0 ⇒ không probe/open")
    r, c, bl = rb(2, 10, "crash")
    check(r.returncode == 0 and "FINAL_RC=2" in r.stdout, "run_bot: helper crash dưới set -euo pipefail ⇒ không abort, rc giữ 2")

    blk = extract(bin_dir / "send_plan_report.sh", "GATE_BLOCK_PLAN_T1_BEGIN", "GATE_BLOCK_PLAN_T1_END")
    script2 = ("set -uo pipefail\nROOT=%s\nACCOUNT=ZaloPay\nEXPECTED_DATE=2026-10-21\nTODAY=2026-10-20\n"
               "REASON=missing\nMARKER_DIR=/m\nWORKDIR=/w\nDISCORD_PLAN_CHANNEL=plan_approval\n_QPAYLOAD='{}'\n%s\n") % (W / "mike", blk)
    fb = W / "mike/fallback.log"
    for mode, want_fb in (("ok", False), ("crash", True), ("silent", True)):
        for f in (fb, log):
            if f.exists():
                f.unlink()
        subprocess.run(["bash", "-c", script2], capture_output=True, text=True, timeout=60,
                       env=dict(os.environ, STUB_OPEN=mode))
        c = log.read_text() if log.exists() else ""
        check(fb.exists() == want_fb and arg_of(c, "--topic") == "plan-t1-not-ready-ZaloPay"
              and arg_of(c, "--key") == "2026-10-21-ZaloPay" and arg_of(c, "--expires-at") == "2026-10-21T23:59"
              and arg_of(c, "--probe").endswith("gate_block_question.py probe plan-t1 --account ZaloPay "
                                                 "--date 2026-10-21 --marker-dir /m --plan-dir /w/data/trade_plans"),
              f"send_plan_report: helper={mode} ⇒ fallback append={want_fb}, topic cũ, probe plan-t1, EXPIRED hết T+1")

    blk = extract(bin_dir / "check_report_cadence.sh", "GATE_BLOCK_DELIVERY_BEGIN", "GATE_BLOCK_DELIVERY_END")
    for tag, owner in (("VENDOR_MISMATCH_ALERT|x", "Winston"), ("❌ CHẶN — số sai", "Taylor")):
        if log.exists():
            log.unlink()
        script3 = ("set -uo pipefail\nROOT=%s\nFNAME=SpaceX_weekly_report_2026-10-16.md\n"
                   "f=/r/SpaceX_weekly_report_2026-10-16.md\nTRADING_REPORT_THREAD=trading_report\n"
                   "GATE_RC=1\nGATE_OUT=%s\n%s\n") % (W / "mike", json.dumps(tag), blk)
        subprocess.run(["bash", "-c", script3], capture_output=True, text=True, timeout=60)
        c = log.read_text() if log.exists() else ""
        check(arg_of(c, "--owner").startswith(owner) and arg_of(c, "--key") == "SpaceX_weekly_report_2026-10-16.md"
              and arg_of(c, "--expires-in-days") == "3"
              and "report_delivery_gate.py /r/SpaceX_weekly_report_2026-10-16.md --status" in arg_of(c, "--probe"),
              f"cadence: tag {tag.split('|')[0][:20]!r} ⇒ owner {owner}, probe --status, EXPIRED 3 ngày")


# (tên, đoạn gốc, đoạn thay). Gồm 8 mutant vòng 1 + 18 mutant harness arch-reviewer (/tmp/arch_mut/run.py,
# viết lại theo code vòng 2) + mutant cho B1-B4/N1-N5/N8.
MUTATIONS = [
    ("O_EXCL/claim bị bỏ (mở trùng)", "if rec.get(\"status\") != \"posting\":", "if False:"),
    ("đóng khi probe FAIL", "    if rc == 0:\n        if dry:", "    if rc != 0:\n        if dry:"),
    ("now theo TZ host", "return dt.datetime.now(ICT)", "return dt.datetime.now().replace(tzinfo=ICT)"),
    ("fake-now bỏ offset", ".astimezone(ICT)\n    return dt.datetime.now(ICT)", ".replace(tzinfo=ICT)\n    return dt.datetime.now(ICT)"),
    ("bỏ check bus khi post lại", "    if bus_has_question(rec[\"agent\"], rec[\"topic\"], rec[\"id\"]):\n        return True\n", ""),
    ("bỏ throttle nhắc", "< dt.timedelta(minutes=rec[\"remind_every_min\"])", "< dt.timedelta(minutes=0)"),
    ("audit hỏng ⇒ coi như đã đóng", "        return None\n    return any(", "        return False\n    return any("),
    ("probe approval bỏ check journal", "if not journal.exists() or since is None or mtime_ict(journal) <= since:", "if False:"),
    # harness arch-reviewer
    ("dry-run vẫn gửi notify", "    if dry:\n        return\n    if send(msg", "    if send(msg"),
    ("dry-run vẫn post bù", "    if dry and st == \"posting\":", "    if False:"),
    ("bỏ skip closed", "    if st in DONE:\n", "    if False:\n"),
    ("bỏ cô lập lỗi per-record", "        except Exception as exc:  # một bản ghi", "        except ZeroDivisionError as exc:  # một bản ghi"),
    ("đóng khi close rc≠0 nhưng in CLOSED", "if c.returncode == 0 and CLOSED_LINE.search(c.stdout or \"\"):", "if CLOSED_LINE.search(c.stdout or \"\"):"),
    ("bỏ check output CLOSED", "if c.returncode == 0 and CLOSED_LINE.search(c.stdout or \"\"):", "if c.returncode == 0:"),
    ("N5 khớp chuỗi con CLOSED", "if c.returncode == 0 and CLOSED_LINE.search(c.stdout or \"\"):", "if c.returncode == 0 and \"CLOSED\" in text:"),
    ("throttle < thành <=", "< dt.timedelta(minutes=rec[\"remind_every_min\"])", "<= dt.timedelta(minutes=rec[\"remind_every_min\"])"),
    ("CLOSED_EXTERNALLY khi audit None", "if still_pending(rec[\"agent\"], rec[\"topic\"]) is False:", "if not still_pending(rec[\"agent\"], rec[\"topic\"]):"),
    ("bỏ CLOSED_EXTERNALLY", "if still_pending(rec[\"agent\"], rec[\"topic\"]) is False:", "if False:"),
    ("still_pending bỏ lọc agent", "q.get(\"agent\") == agent and q.get(\"topic\") == topic", "q.get(\"topic\") == topic"),
    ("probe timeout ⇒ rc0", "return 124, f\"probe timeout", "return 0, f\"probe timeout"),
    ("probe OSError ⇒ rc0", "return 127, f\"probe", "return 0, f\"probe"),
    ("bus_has_question bỏ so topic", " and e.get(\"topic\") == topic)", ")"),
    ("open không đổi status open sau post", "        rec[\"status\"] = \"open\"\n        rec[\"posted_at\"]", "        rec[\"posted_at\"]"),
    ("probe approval: plan None ⇒ 0", "KHÔNG CÓ PLAN {a.account} {a.date}\")\n        return 12", "KHÔNG CÓ PLAN {a.account} {a.date}\")\n        return 0"),
    ("probe cwd bỏ WC_ROOT", "cwd=WC_ROOT, ", ""),
    ("reason không cắt 400", "[:400]", ""),
    ("mins âm vẫn ghi còn", "if mins >= 0 else", "if True else"),
    # B1
    ("B1 bỏ expire theo thời gian", "    if now >= parse_ict(rec[\"expires_at\"]):", "    if False:"),
    ("B1 bỏ trần số lần nhắc", "    elif int(rec.get(\"reminders\") or 0) >= cap:", "    elif False:"),
    ("B1 expire không đổi status", "    rec.update(status=\"expired\", expired_at", "    rec.update(expired_at"),
    ("B1 expire không gửi tin cuối", "    rec[\"final_notice_delivered\"] = send(msg, rec.get(\"thread\"))", "    rec[\"final_notice_delivered\"] = False"),
    ("B1 open không bắt buộc expiry", "    if bool(a.expires_at) == (a.expires_in_days is not None):", "    if False:"),
    # B2
    ("B2 approval bỏ so mtime journal", " or mtime_ict(journal) <= since:", ":"),
    ("B2 approval since None vẫn OK", "if not journal.exists() or since is None or mtime_ict", "if not journal.exists() or (since is not None and mtime_ict"),
    ("B2 plan-t1 bỏ so mtime", "    if mt <= since or sent <", "    if sent <"),
    ("B2 plan-t1 bỏ so md5", "    if not cur or m.get(\"content_md5\") != cur:", "    if False:"),
    ("B2 sweep không truyền OPENED_AT", "env = dict(os.environ, GATE_BLOCK_OPENED_AT=opened_at)", "env = dict(os.environ)"),
    ("B2 hash không bỏ approv*", "if not (k.startswith(\"approv\") or k.startswith(\"mafee\")", "if not (k.startswith(\"mafee\")"),
    # B3
    ("B3 instructions vẫn ghi recover_cmd", "payload[\"recover_instructions\" if human else \"recover_cmd\"]", "payload[\"recover_cmd\"]"),
    ("B3 bỏ next-step khi nhắc", "    how = f\"BƯỚC KẾ: {step}\" if step else", "    how = f\"BƯỚC KẾ: {step}\" if False else"),
    # B4
    ("B4 không post ack", "    if not rec.get(\"ack_posted\") and post_ack(rec):", "    if False:"),
    ("B4 ack sai prefix", "ACK_PREFIX = \"triaged-needs-human:\"", "ACK_PREFIX = \"triaged-needs-human\""),
    ("B4 ack không suppress_days", "\"suppress_days\": sd,", ""),
    # N4/N2/N8
    ("N4 notify lỗi vẫn tính đã nhắc", "            ok = ok or r.returncode == 0", "            ok = True"),
    ("N2 bỏ flock", "        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)", "        pass"),
    ("N8 không dọn", "            path.unlink()\n            print(f\"gate_block_question: PRUNED", "            print(f\"gate_block_question: PRUNED"),
    ("N8 dọn cả dry-run", "        if not dry and done_at and now", "        if done_at and now"),
    ("N3 claim không dọn tmp", "    finally:\n        os.unlink(tmp)", "    finally:\n        pass"),
]


def main() -> int:
    if "--core" in sys.argv:
        target = Path(sys.argv[sys.argv.index("--target") + 1]) if "--target" in sys.argv else HELPER
        try:
            core(target)
            if "--no-wiring" not in sys.argv:
                wiring(HERE)
        finally:
            for r in TMP:
                shutil.rmtree(r, ignore_errors=True)
        print(f"{'PASS' if not FAILS else 'FAIL'} ({len(FAILS)} fail) TZ={os.environ.get('TZ', '<unset>')}")
        return 1 if FAILS else 0
    rc_all = 0
    for tzenv in (None, "Pacific/Kiritimati", "America/Los_Angeles"):
        env = {k: v for k, v in os.environ.items() if k != "TZ"}
        if tzenv:
            env["TZ"] = tzenv
        r = subprocess.run([sys.executable, __file__, "--core"], env=env, capture_output=True, text=True)
        last = (r.stdout.strip().splitlines() or ["?"])[-1]
        print(f"[TZ={tzenv or 'env -u TZ'}] {last}")
        if r.returncode:
            print(r.stdout + r.stderr); rc_all = 1
    src = HELPER.read_text()
    killed, alive = 0, []
    for name, old, new in MUTATIONS:
        if src.count(old) < 1:
            print(f"[mutation] FATAL: không tìm thấy đoạn cho '{name}'"); rc_all = 1; alive.append(name); continue
        d = Path(tempfile.mkdtemp(prefix="gbq_mut_"))
        m = d / "gate_block_question.py"; m.write_text(src.replace(old, new, 1))
        env = {k: v for k, v in os.environ.items() if k != "TZ"}
        env["TZ"] = "Pacific/Kiritimati"
        r = subprocess.run([sys.executable, __file__, "--core", "--no-wiring", "--target", str(m)],
                           env=env, capture_output=True, text=True)
        dead = r.returncode != 0
        killed += dead
        if not dead:
            alive.append(name)
        print(f"[mutation] {'KILLED' if dead else 'SURVIVED'}: {name}")
        shutil.rmtree(d, ignore_errors=True)
    print(f"mutation {killed}/{len(MUTATIONS)} killed; sống: {alive}")
    if killed != len(MUTATIONS):
        rc_all = 1
    print("SELFCHECK", "PASS" if rc_all == 0 else "FAIL")
    return rc_all


if __name__ == "__main__":
    raise SystemExit(main())
