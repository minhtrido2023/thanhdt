#!/usr/bin/env python3
"""Selfcheck cho bin/gate_block_question.py + 3 điểm wire (run_bot / send_plan_report / cadence).

Chạy: python3 bin/gate_block_question_selfcheck.py            (3 TZ + mutation)
      python3 bin/gate_block_question_selfcheck.py --core [--target H]   (1 lượt, TZ hiện tại)
Mọi I/O ra ngoài (append_event/notify/audit/close) là STUB trong fixture root tạm — KHÔNG chạm
bus/Telegram thật. Exit 0 = PASS.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
HELPER = HERE / "gate_block_question.py"
FAILS: list[str] = []


def check(cond, name):
    print(("  ok   " if cond else "  FAIL ") + name)
    if not cond:
        FAILS.append(name)


STUB_APPEND = r'''#!/usr/bin/env python3
import json, os, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.exists(os.path.join(root, "APPEND_FAIL")):
    print("stub append fail", file=sys.stderr); sys.exit(1)
agent, et, topic, payload = sys.argv[1:5]
os.makedirs(os.path.join(root, "bus", "inbox"), exist_ok=True)
with open(os.path.join(root, "bus", "inbox", agent + ".jsonl"), "a") as f:
    f.write(json.dumps({"agent_id": agent, "event_type": et, "topic": topic,
                        "payload": json.loads(payload)}, ensure_ascii=False) + "\n")
'''
STUB_LOG = r'''#!/usr/bin/env bash
echo "$(basename "$0") $*" >> "$(dirname "$0")/../calls.log"
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
rc_file = os.path.join(root, "CLOSE_RC")
if os.path.exists(rc_file):
    print("close_bus_question: BLOCKED stub", file=sys.stderr); sys.exit(int(open(rc_file).read()))
ref = sys.argv[1]; args = sys.argv[2:]
ev = args[args.index("--evidence") + 1]; actor = args[args.index("--actor") + 1]
subprocess.run([os.path.join(root, "bin", "append_event.sh"), actor, "answer", ref.split("/", 1)[1],
                json.dumps({"resolves": [ref], "evidence": ev})], check=True)
with open(os.path.join(root, "calls.log"), "a") as f:
    f.write("close " + ref + " EVIDENCE=" + ev + "\n")
print("close_bus_question: CLOSED " + ref)
'''


def mkroot() -> Path:
    r = Path(tempfile.mkdtemp(prefix="gbq_sc_"))
    (r / "bin").mkdir()
    for name, body in (("append_event.sh", STUB_APPEND), ("notify.sh", STUB_LOG),
                       ("notify_thread.sh", STUB_LOG), ("bus_question_audit.py", STUB_AUDIT),
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


def questions(root, agent="Mike"):
    p = root / "bus" / "inbox" / f"{agent}.jsonl"
    if not p.exists():
        return []
    return [e for e in map(json.loads, p.read_text().splitlines()) if e["event_type"] == "question"]


def calls(root):
    p = root / "calls.log"
    return p.read_text() if p.exists() else ""


def open_args(key="2026-10-20-SpaceX", probe="false", every="15", gate="approval"):
    return ["open", "--gate", gate, "--key", key, "--owner", "user; Mike",
            "--deadline", "2026-10-20T10:00", "--recover", "bin/run_bot.sh --account SpaceX",
            "--probe", probe, "--reason", "APPROVAL_GATE_BLOCK test", "--thread", "trading_daily",
            "--remind-every-min", every, "--extra", '{"account":"SpaceX"}']


def core(target: Path) -> None:
    T0 = "2026-10-20T09:06:00+07:00"
    # 1-3: mở + idempotent theo (gate,key)
    R = mkroot()
    rc, out = run(target, R, *open_args(), now=T0)
    qs = questions(R)
    check(rc == 0 and "OPENED" in out and len(qs) == 1, "open: OPENED + đúng 1 question")
    p = qs[0]["payload"] if qs else {}
    check(p.get("owner") and p.get("deadline_ict") == "2026-10-20T10:00" and p.get("recover_cmd")
          and p.get("gate_block_id") == "approval__2026-10-20-SpaceX" and p.get("account") == "SpaceX",
          "payload có owner/deadline/recover/gate_block_id + extra gộp")
    check(qs and qs[0]["topic"] == "gate-block-approval-2026-10-20-SpaceX", "topic mặc định gate-block-<gate>-<key>")
    rc, out = run(target, R, *open_args(), now=T0)
    check(rc == 0 and "ALREADY_OPEN" in out and len(questions(R)) == 1, "open lặp cùng gate+key ⇒ KHÔNG mở trùng")
    run(target, R, *open_args(key="2026-10-20-ZaloPay"), now=T0)
    check(len(questions(R)) == 2, "key khác (account khác) ⇒ question riêng")

    # 4: bị kill giữa post và ghi sổ ⇒ sổ 'posting' + bus đã có ⇒ không post lại
    sp = R / "state" / "gate_blocks" / "approval__2026-10-20-SpaceX.json"
    rec = json.loads(sp.read_text()); rec["status"] = "posting"; sp.write_text(json.dumps(rec))
    rc, out = run(target, R, *open_args(), now=T0)
    check(len(questions(R)) == 2 and json.loads(sp.read_text())["status"] == "open",
          "kill sau post: sổ posting + bus đã có ⇒ không post lại, sổ về open")

    # 5: append hỏng ⇒ posting, sweep sau post đúng 1 lần
    R2 = mkroot(); (R2 / "APPEND_FAIL").write_text("1")
    rc, out = run(target, R2, *open_args(), now=T0)
    sp2 = R2 / "state" / "gate_blocks" / "approval__2026-10-20-SpaceX.json"
    check(rc != 0 and json.loads(sp2.read_text())["status"] == "posting" and not questions(R2),
          "append lỗi ⇒ rc≠0, sổ posting, chưa có question")
    (R2 / "APPEND_FAIL").unlink()
    run(target, R2, "sweep", now=T0)
    run(target, R2, "sweep", now=T0)
    check(len(questions(R2)) == 1, "sweep post bù đúng 1 lần")

    # 6: probe fail ⇒ nhắc, throttle, quá hạn
    R3 = mkroot()
    run(target, R3, *open_args(probe="exit 1"), now=T0)
    rc, out = run(target, R3, "sweep", now="2026-10-20T09:10:00+07:00")
    check("REMIND" in out and "còn 50 phút" in out and calls(R3).count("notify.sh") == 1
          and "notify_thread.sh" in calls(R3), "probe rc≠0 ⇒ nhắc Telegram+thread, 'còn 50 phút' (ICT)")
    rc, out = run(target, R3, "sweep", now="2026-10-20T09:15:00+07:00")
    check(calls(R3).count("notify.sh") == 1 and "STILL_OPEN" in out, "throttle: <15' không nhắc lại")
    rc, out = run(target, R3, "sweep", now="2026-10-20T03:20:00+00:00")  # = 10:20 ICT
    check(calls(R3).count("notify.sh") == 2 and "QUÁ HẠN 20 phút" in out,
          "qua hạn ⇒ nhắc 'QUÁ HẠN 20 phút' (now nhập UTC, so theo ICT)")
    check(not any(e["event_type"] == "answer" for e in map(json.loads, (R3 / "bus/inbox/Mike.jsonl").read_text().splitlines())),
          "probe fail KHÔNG BAO GIỜ đóng question")

    # 7: probe rc=0 ⇒ đóng qua close_bus_question, evidence chứa lệnh probe
    flag = R3 / "RECOVERED"
    rec = json.loads((R3 / "state/gate_blocks/approval__2026-10-20-SpaceX.json").read_text())
    rec["probe"] = f"test -e {flag} && echo journal-ok"
    (R3 / "state/gate_blocks/approval__2026-10-20-SpaceX.json").write_text(json.dumps(rec))
    flag.write_text("1")
    rc, out = run(target, R3, "sweep", now="2026-10-20T10:30:00+07:00")
    st = json.loads((R3 / "state/gate_blocks/approval__2026-10-20-SpaceX.json").read_text())
    check("CLOSED Mike/gate-block-approval" in out and st["status"] == "closed"
          and "journal-ok" in calls(R3) and "test -e" in calls(R3), "probe rc=0 ⇒ CLOSED, evidence = lệnh + output probe")
    n = calls(R3).count("notify.sh")
    run(target, R3, "sweep", now="2026-10-20T11:30:00+07:00")
    check(calls(R3).count("notify.sh") == n, "đã đóng ⇒ sweep sau im lặng")
    rc, out = run(target, R3, *open_args(probe="exit 1"), now="2026-10-20T13:01:00+07:00")
    check("ALREADY_CLOSED" in out and len(questions(R3)) == 1, "block lại cùng ngày sau khi đóng ⇒ không mở câu mới")

    # 8: probe không chạy được ⇒ không đóng
    R4 = mkroot()
    run(target, R4, *open_args(probe="/nonexistent/probe_cmd"), now=T0)
    rc, out = run(target, R4, "sweep", now=T0)
    check("REMIND" in out and "closed" != json.loads((R4 / "state/gate_blocks/approval__2026-10-20-SpaceX.json").read_text())["status"],
          "probe lỗi (rc127) ⇒ nhắc, không đóng")

    # 9: người đóng trên bus ⇒ ngừng nhắc
    subprocess.run([str(R4 / "bin/append_event.sh"), "Mike", "answer", "x",
                    json.dumps({"resolves": ["Mike/gate-block-approval-2026-10-20-SpaceX"]})], check=True)
    n = calls(R4).count("notify.sh")
    rc, out = run(target, R4, "sweep", now="2026-10-20T12:00:00+07:00")
    check("CLOSED_EXTERNALLY" in out and calls(R4).count("notify.sh") == n, "đóng tay trên bus ⇒ CLOSED_EXTERNALLY, ngừng nhắc")

    # 10: audit hỏng ⇒ coi như còn mở (nhắc), không đóng
    R5 = mkroot()
    run(target, R5, *open_args(probe="exit 1"), now=T0)
    (R5 / "AUDIT_BROKEN").write_text("1")
    rc, out = run(target, R5, "sweep", now=T0)
    check("AUDIT_UNREADABLE" in out and "REMIND" in out, "audit hỏng ⇒ fail-loud: vẫn nhắc, không tự đóng")

    # 11: close_bus_question chặn (rc=5) ⇒ không ép đóng, nhắc kèm lý do
    R6 = mkroot()
    run(target, R6, *open_args(probe="true"), now=T0)
    (R6 / "CLOSE_RC").write_text("5")
    rc, out = run(target, R6, "sweep", now=T0)
    st = json.loads((R6 / "state/gate_blocks/approval__2026-10-20-SpaceX.json").read_text())
    check(st["status"] == "open" and "close_bus_question rc=5" in out, "close bị chặn rc=5 ⇒ giữ open + nhắc lý do")

    # 12-13: slug xấu / sổ hỏng
    R7 = mkroot()
    rc, out = run(target, R7, *open_args(key="2026-10-20 Space X"), now=T0)
    check(rc == 2 and not questions(R7), "key có ký tự lạ ⇒ rc2, không post")
    (R7 / "state/gate_blocks").mkdir(parents=True)
    (R7 / "state/gate_blocks/approval__2026-10-20-SpaceX.json").write_text("{cut")
    rc, out = run(target, R7, *open_args(), now=T0)
    check(rc == 1 and "STATE_UNREADABLE" in out and not questions(R7), "sổ hỏng ⇒ không post (thà thiếu hơn trùng)")

    # 14: --topic giữ topic cũ của cổng
    R8 = mkroot()
    args = open_args(gate="plan-t1-not-ready", key="2026-10-21-SpaceX") + ["--topic", "plan-t1-not-ready-SpaceX"]
    run(target, R8, *args, now=T0)
    check([q["topic"] for q in questions(R8)] == ["plan-t1-not-ready-SpaceX"], "--topic giữ topic cũ")

    # 14b: đồng hồ THẬT (không GATE_BLOCK_NOW) phải neo ICT, độc lập TZ host (§16)
    import datetime as _dt
    from zoneinfo import ZoneInfo
    Rt = mkroot()
    dl = (_dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")) + _dt.timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M")
    a = open_args(probe="exit 1")
    a[a.index("--deadline") + 1] = dl
    run(target, Rt, *a)
    rc, out = run(target, Rt, "sweep")
    m = re.search(r"còn (\d+) phút", out)
    check(bool(m) and 170 <= int(m.group(1)) <= 180,
          f"đồng hồ thật neo ICT: hạn +3h ⇒ 'còn ~179 phút' (thấy {m.group(0) if m else out[-80:]!r})")
    shutil.rmtree(Rt, ignore_errors=True)

    # 15: probe approval (module trading_bot giả)
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
    pa = ["probe", "approval", "--account", "SpaceX", "--date", "2026-10-20"]
    check(run(target, R9, *pa, extra_env={"FAKE_PLAN": "none"})[0] == 10, "probe: không có plan ⇒ 10")
    check(run(target, R9, *pa, extra_env={"FAKE_PLAN": "blocked"})[0] == 10, "probe: chưa duyệt ⇒ 10")
    check(run(target, R9, *pa, extra_env={"FAKE_PLAN": "ok"})[0] == 11, "probe: duyệt nhưng chưa có journal ⇒ 11")
    check(run(target, R9, *pa, extra_env={"FAKE_PLAN": "hold"})[0] == 0, "probe: plan sửa thành HOLD (0 lệnh) ⇒ 0")
    (R9 / "data/execution_logs").mkdir(parents=True)
    (R9 / "data/execution_logs/exec_SpaceX_2026-10-20_journal.csv").write_text("x")
    check(run(target, R9, *pa, extra_env={"FAKE_PLAN": "ok"})[0] == 0, "probe: duyệt + journal ⇒ 0")
    for r in (R, R2, R3, R4, R5, R6, R7, R8, R9):
        shutil.rmtree(r, ignore_errors=True)


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
    f.write(" ".join(sys.argv[1:]) + "\n")
if sys.argv[1] == "probe":
    sys.exit(int(os.environ.get("STUB_PROBE_RC", "10")))
mode = os.environ.get("STUB_OPEN", "ok")
if mode == "ok":
    print("gate_block_question: OPENED x"); sys.exit(0)
if mode == "crash":
    print("Traceback boom", file=sys.stderr); sys.exit(2)
'''


def wiring(bin_dir: Path) -> None:
    W = Path(tempfile.mkdtemp(prefix="gbq_wire_"))
    (W / "mike/bin").mkdir(parents=True)
    h = W / "mike/bin/gate_block_question.py"; h.write_text(STUB_HELPER); h.chmod(0o755)
    ap = W / "mike/bin/append_event.sh"
    ap.write_text('#!/usr/bin/env bash\necho "append $*" >> "$(dirname "$0")/../fallback.log"\n'); ap.chmod(0o755)
    log = W / "mike/helper_calls.log"

    blk = extract(bin_dir / "run_bot.sh", "GATE_BLOCK_APPROVAL_BEGIN", "GATE_BLOCK_APPROVAL_END")
    script = ("set -euo pipefail\nROOT=%s\nWC_ROOT=%s\nACCOUNT=SpaceX\nPLAN_DATE=2026-10-20\n"
              "LOG=/tmp/x.log\n_tid=trading_daily\nrc=$RC\n%s\necho FINAL_RC=$rc\n") % (W / "mike", W, blk)

    def rb(rc, probe_rc, open_mode="ok"):
        if log.exists():
            log.unlink()
        r = subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=60,
                           env=dict(os.environ, RC=str(rc), STUB_PROBE_RC=str(probe_rc), STUB_OPEN=open_mode))
        return r, (log.read_text() if log.exists() else "")

    r, c = rb(2, 10)
    check("FINAL_RC=2" in r.stdout and "open --gate approval --key 2026-10-20-SpaceX" in c
          and "--deadline 2026-10-20T10:00" in c, "run_bot: rc=2 + probe 10 ⇒ open, rc giữ 2")
    r, c = rb(2, 0)
    check("FINAL_RC=2" in r.stdout and "open" not in c, "run_bot: rc=2 nhưng probe≠10 (không phải approval) ⇒ không open")
    r, c = rb(0, 10)
    check("FINAL_RC=0" in r.stdout and c == "", "run_bot: rc=0 ⇒ không probe/open")
    r, c = rb(2, 10, "crash")
    check(r.returncode == 0 and "FINAL_RC=2" in r.stdout, "run_bot: helper crash dưới set -euo pipefail ⇒ không abort, rc giữ 2")

    blk = extract(bin_dir / "send_plan_report.sh", "GATE_BLOCK_PLAN_T1_BEGIN", "GATE_BLOCK_PLAN_T1_END")
    script2 = ("set -uo pipefail\nROOT=%s\nACCOUNT=ZaloPay\nEXPECTED_DATE=2026-10-21\nTODAY=2026-10-20\n"
               "REASON=missing\nMARKER_DIR=/m\nDISCORD_PLAN_CHANNEL=plan_approval\n_QPAYLOAD='{}'\n%s\n") % (W / "mike", blk)
    fb = W / "mike/fallback.log"
    for mode, want_fb in (("ok", False), ("crash", True), ("silent", True)):
        if fb.exists():
            fb.unlink()
        if log.exists():
            log.unlink()
        subprocess.run(["bash", "-c", script2], capture_output=True, text=True, timeout=60,
                       env=dict(os.environ, STUB_OPEN=mode))
        c = log.read_text() if log.exists() else ""
        check(fb.exists() == want_fb and "--topic plan-t1-not-ready-ZaloPay" in c
              and "--key 2026-10-21-ZaloPay" in c and "test -s /m/ZaloPay_2026-10-21.json" in c,
              f"send_plan_report: helper={mode} ⇒ fallback append={want_fb}, topic cũ giữ, probe=marker")

    blk = extract(bin_dir / "check_report_cadence.sh", "GATE_BLOCK_DELIVERY_BEGIN", "GATE_BLOCK_DELIVERY_END")
    for tag, owner in (("VENDOR_MISMATCH_ALERT|x", "Winston"), ("❌ CHẶN — số sai", "Taylor")):
        if log.exists():
            log.unlink()
        script3 = ("set -uo pipefail\nROOT=%s\nFNAME=SpaceX_weekly_report_2026-10-16.md\n"
                   "f=/r/SpaceX_weekly_report_2026-10-16.md\nTRADING_REPORT_THREAD=trading_report\n"
                   "GATE_RC=1\nGATE_OUT=%s\n%s\n") % (W / "mike", json.dumps(tag), blk)
        subprocess.run(["bash", "-c", script3], capture_output=True, text=True, timeout=60)
        c = log.read_text() if log.exists() else ""
        check(f"--owner {owner}" in c and "--key SpaceX_weekly_report_2026-10-16.md" in c
              and "report_delivery_gate.py /r/SpaceX_weekly_report_2026-10-16.md --status" in c,
              f"cadence: tag {tag.split('|')[0][:20]!r} ⇒ owner {owner}, probe --status")
    shutil.rmtree(W, ignore_errors=True)


MUTATIONS = [
    ("O_EXCL bị bỏ (mở trùng)", "if rec.get(\"status\") != \"posting\":", "if False:"),
    ("đóng khi probe FAIL", "    if rc == 0:\n        if dry:", "    if rc != 0:\n        if dry:"),
    ("now theo TZ host", "return dt.datetime.now(ICT)", "return dt.datetime.now().replace(tzinfo=ICT)"),
    ("fake-now bỏ offset", ".astimezone(ICT)\n    return dt.datetime.now(ICT)", ".replace(tzinfo=ICT)\n    return dt.datetime.now(ICT)"),
    ("bỏ check bus khi post lại", "    if bus_has_question(rec[\"agent\"], rec[\"topic\"], rec[\"id\"]):\n        return True\n", ""),
    ("bỏ throttle nhắc", "< dt.timedelta(minutes=rec[\"remind_every_min\"])", "< dt.timedelta(minutes=0)"),
    ("audit hỏng ⇒ coi như đã đóng", "        return None\n    return any(", "        return False\n    return any("),
    ("probe approval bỏ check journal", "    if not journal.exists():", "    if False:"),
]


def main() -> int:
    if "--core" in sys.argv:
        target = Path(sys.argv[sys.argv.index("--target") + 1]) if "--target" in sys.argv else HELPER
        core(target)
        if "--no-wiring" not in sys.argv:
            wiring(HERE)
        print(f"{'PASS' if not FAILS else 'FAIL'} ({len(FAILS)} fail) TZ={os.environ.get('TZ', '<unset>')}")
        return 1 if FAILS else 0
    rc_all = 0
    for tzenv in (None, "Pacific/Kiritimati", "Asia/Ho_Chi_Minh"):
        env = {k: v for k, v in os.environ.items() if k != "TZ"}
        if tzenv:
            env["TZ"] = tzenv
        r = subprocess.run([sys.executable, __file__, "--core"], env=env, capture_output=True, text=True)
        last = (r.stdout.strip().splitlines() or ["?"])[-1]
        print(f"[TZ={tzenv or 'env -u TZ'}] {last}")
        if r.returncode:
            print(r.stdout); rc_all = 1
    src = HELPER.read_text()
    killed = 0
    for name, old, new in MUTATIONS:
        if old not in src:
            print(f"[mutation] FATAL: không tìm thấy đoạn cho '{name}'"); rc_all = 1; continue
        d = Path(tempfile.mkdtemp(prefix="gbq_mut_"))
        m = d / "gate_block_question.py"; m.write_text(src.replace(old, new, 1))
        env = {k: v for k, v in os.environ.items() if k != "TZ"}
        env["TZ"] = "Pacific/Kiritimati"
        r = subprocess.run([sys.executable, __file__, "--core", "--no-wiring", "--target", str(m)],
                           env=env, capture_output=True, text=True)
        dead = r.returncode != 0
        killed += dead
        print(f"[mutation] {'KILLED' if dead else 'SURVIVED'}: {name}")
        shutil.rmtree(d, ignore_errors=True)
    print(f"mutation {killed}/{len(MUTATIONS)} killed")
    if killed != len(MUTATIONS):
        rc_all = 1
    print("SELFCHECK", "PASS" if rc_all == 0 else "FAIL")
    return rc_all


if __name__ == "__main__":
    raise SystemExit(main())
