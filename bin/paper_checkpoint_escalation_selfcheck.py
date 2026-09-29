#!/usr/bin/env python3
"""Regression selfcheck cho bin/paper_checkpoint_escalation.sh — HỢP ĐỒNG LIÊN-FILE giữa
script này (producer của ack `triaged-needs-human:`) và check #5 của bin/ops_health_check.sh
(consumer duy nhất của ack đó).

TẠI SAO tồn tại: commit c7d2a213 (coord-2026-08-05) cho script tự ack câu hỏi nó tự phát —
đúng ý định (câu hỏi đã được giao cho owner, chỉ chờ NGƯỜI), nhưng ack được phát TRƯỚC
dispatch và độc lập với exit status của nó, còn cooldown 7 ngày thì ghi vô điều kiện. Một
dispatch hỏng (circuit breaker OPEN…) khi đó biến thành ĐIỂM MÙ 7 NGÀY: không job owner, bus
lại khẳng định "đã dispatch", question tụt xuống WARN-ONLY nên không wags_autofix nào đi
triage. arch-reviewer NEEDS_CHANGES high 2026-08-05 (required_change #1 + #2) → file này.

Hai bất biến được canh:
  (A) chuỗi ack script phát phải khớp CHÍNH XÁC `_acked()` của check #5 — hai file, hai
      ngôn ngữ, ghép bằng một chuỗi literal; drift là im lặng.
  (B) dispatch THẤT BẠI ⇒ KHÔNG ack, KHÔNG cooldown, có event `error`, và câu hỏi phải ở
      lại nhánh ROUTABLE (Wags đi triage) — fail-closed.

CÁCH LÀM: KHÔNG copy logic. Chạy CHÍNH bin/paper_checkpoint_escalation.sh thật trong một
sandbox tmpdir (stub dispatch.sh/append_event.sh/notify_thread.sh), rồi đưa bus mà nó vừa
ghi vào KHỐI check #5 THẬT (trích qua marker CHECK5_BEGIN/END, tái dùng
ops_health_check_selfcheck.py). Mutation (đổi ACK_PREFIX hoặc đổi agent `Mike` ở dòng
question) phải làm test ĐỎ — có case chứng minh.

Chạy: python3 bin/paper_checkpoint_escalation_selfcheck.py   (exit 0 = PASS, 1 = FAIL)
Tự động nằm trong bin/run_selfchecks.sh (glob *selfcheck*.py).
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Env override CHỈ để mutation-test (chứng minh test này đỏ được với bản code cũ); prod luôn
# dùng file thật.
SRC = os.environ.get("PAPER_CKPT_SRC") or os.path.join(ROOT, "bin", "paper_checkpoint_escalation.sh")
sys.path.insert(0, os.path.join(ROOT, "bin"))
import ops_health_check_selfcheck as ohc  # noqa: E402  (tái dùng trích-khối check #5 THẬT)

FAILS = []
PID = "selfcheck_prog"

# check #5 có ÂN HẠN `QUESTION_GRACE_MIN` phút: câu hỏi mới hơn ngưỡng đó KHÔNG bao giờ vào
# nhánh routable. Stub bus phải lùi ts của event ra ngoài cửa sổ ân hạn, nếu không 3 ca
# "phải routable" đỏ oan VÀ — nguy hơn — các ca "KHÔNG routable" xanh vì SAI lý do (rơi vào
# ân hạn chứ không phải vì ack). Đọc thẳng hằng số THẬT, đừng chép cứng 60.
def _grace_min(default=60):
    try:
        src = open(os.path.join(ROOT, "bin", "ops_health_check.sh"), encoding="utf-8").read()
        m = re.search(r"^QUESTION_GRACE_MIN\s*=\s*(\d+)", src, re.M)
        return int(m.group(1)) if m else default
    except OSError:
        return default


STUB_EVENT_AGE_MIN = _grace_min() + 30
os.environ["SELFCHECK_EVENT_AGE_MIN"] = str(STUB_EVENT_AGE_MIN)

STUB_APPEND = r"""#!/usr/bin/env bash
# stub append_event.sh — ghi đúng shape bus mà check #5 đọc
AGENT="$1"; ETYPE="$2"; TOPIC="$3"; PAYLOAD="${4:-{}}"
BUS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/bus/inbox"
mkdir -p "$BUS"
python3 - "$BUS/$AGENT.jsonl" "$AGENT" "$ETYPE" "$TOPIC" "$PAYLOAD" <<'PY'
import json, os, sys, datetime
path, agent, etype, topic, payload = sys.argv[1:6]
try: payload = json.loads(payload)
except Exception: pass
age = datetime.timedelta(minutes=int(os.environ.get("SELFCHECK_EVENT_AGE_MIN", "90")))
rec = {"event_id": f"{agent}-{etype}-{topic}", "agent_id": agent, "event_type": etype,
       "topic": topic, "payload": payload,
       "ts": (datetime.datetime.now(datetime.timezone.utc) - age)
             .strftime("%Y-%m-%dT%H:%M:%SZ")}
with open(path, "a", encoding="utf-8") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
PY
"""

STUB_NOTIFY = "#!/usr/bin/env bash\nexit 0\n"
# rc do biến môi trường quyết định → mô phỏng cả dispatch OK lẫn dispatch hỏng
STUB_DISPATCH = ('#!/usr/bin/env bash\n'
                 'echo "stub dispatch rc=${STUB_DISPATCH_RC:-0}"\n'
                 'exit "${STUB_DISPATCH_RC:-0}"\n')

REGISTRY = {"programs": [{
    "id": PID,
    "name": "Selfcheck program",
    "owner": "Taylor",
    "end": "2020-01-01",                      # quá hạn chắc chắn
    "review_short": "",
    "gate_criteria": [{"text": "gate A", "status": "pending"},
                      {"text": "gate B", "status": "pass"}],
}]}


def check(name, cond, detail=""):
    if cond:
        print(f"  PASS  {name}")
    else:
        FAILS.append(f"{name} — {detail}")
        print(f"  FAIL  {name} — {detail}")


def build_sandbox(mutate=None):
    """Dựng sandbox chứa BẢN THẬT của script (tuỳ chọn mutate nội dung) + các stub."""
    d = tempfile.mkdtemp(prefix="paper_ckpt_selfcheck_")
    mike = os.path.join(d, "mike")
    for sub in ("bin", "kb", "state", "bus/inbox"):
        os.makedirs(os.path.join(mike, sub), exist_ok=True)
    with open(SRC, encoding="utf-8") as f:
        body = f.read()
    if mutate:
        body = mutate(body)
    def w(rel, content, x=True):
        p = os.path.join(mike, rel)
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        if x:
            os.chmod(p, 0o755)
    w("bin/paper_checkpoint_escalation.sh", body)
    w("bin/append_event.sh", STUB_APPEND)
    w("bin/notify_thread.sh", STUB_NOTIFY)
    w("bin/dispatch.sh", STUB_DISPATCH)
    w("kb/paper_programs_registry.json", json.dumps(REGISTRY, ensure_ascii=False), x=False)
    return d, mike


def run_script(mike, rc):
    env = dict(os.environ, STUB_DISPATCH_RC=str(rc))
    return subprocess.run(["bash", os.path.join(mike, "bin", "paper_checkpoint_escalation.sh")],
                          capture_output=True, text=True, env=env, timeout=120)


def bus_events(mike):
    out = []
    inbox = os.path.join(mike, "bus", "inbox")
    for fn in sorted(os.listdir(inbox)) if os.path.isdir(inbox) else []:
        if not fn.endswith(".jsonl"):
            continue
        with open(os.path.join(inbox, fn), encoding="utf-8") as f:
            out += [json.loads(l) for l in f if l.strip()]
    return out


def state_of(mike):
    p = os.path.join(mike, "state", "paper_checkpoint_escalated.json")
    if not os.path.exists(p):
        return {}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def check5_on(mike):
    """Đưa bus sandbox qua KHỐI check #5 THẬT; trả về text báo cáo."""
    lines, _ = ohc.run_check5(os.path.dirname(mike))
    return "\n".join(lines)


# ── Ca 1 (bất biến A): dispatch OK ⇒ có ack, có cooldown, và check #5 THẬT xếp câu hỏi vào
#    nhánh "ĐÃ TRIAGE, chờ NGƯỜI" — KHÔNG còn ở nhánh routable, KHÔNG bị ẩn khỏi báo cáo.
def case_dispatch_ok():
    d, mike = build_sandbox()
    try:
        r = run_script(mike, 0)
        evs = bus_events(mike)
        acks = [e for e in evs if e["event_type"] == "status"
                and e["topic"].startswith("triaged-needs-human:")]
        qs = [e for e in evs if e["event_type"] == "question"]
        check("rc=0: có đúng 1 question + 1 ack", len(qs) == 1 and len(acks) == 1,
              f"rc={r.returncode} events={[(e['agent_id'], e['event_type'], e['topic']) for e in evs]}")
        check("rc=0: ack trỏ đúng khoá 'Mike/<topic câu hỏi>'",
              bool(acks) and acks[0]["topic"] == f"triaged-needs-human:Mike/paper-checkpoint-overdue-{PID}",
              str(acks))
        check("rc=0: ack ghi dưới tác giả THẬT (Wags), không mạo danh Mike",
              bool(acks) and acks[0]["agent_id"] == "Wags", str(acks))
        check("rc=0: cooldown đã ghi cho program", PID in state_of(mike), str(state_of(mike)))
        out = check5_on(mike)
        check("rc=0: check #5 THẬT xếp vào nhánh needs-human (ack khớp _acked)",
              "ĐÃ TRIAGE" in out and f"paper-checkpoint-overdue-{PID}" in out, out)
        check("rc=0: KHÔNG còn ở nhánh routable (hết đốt job wags_autofix)",
              "CHƯA thấy answer" not in out, out)
        check("rc=0: câu hỏi vẫn HIỆN trong báo cáo (không tạo im lặng mới)",
              f"paper-checkpoint-overdue-{PID}" in out, out)
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── Ca 2 (bất biến B — killer_objection của arch-reviewer): dispatch HỎNG ⇒ không ack,
#    không cooldown, có event error, câu hỏi ở lại nhánh routable.
def case_dispatch_fails():
    d, mike = build_sandbox()
    try:
        run_script(mike, 1)
        evs = bus_events(mike)
        acks = [e for e in evs if e["event_type"] == "status"
                and e["topic"].startswith("triaged-needs-human:")]
        errs = [e for e in evs if e["event_type"] == "error"
                and e["topic"] == f"paper-checkpoint-dispatch-failed-{PID}"]
        check("rc≠0: KHÔNG phát ack (fail-closed)", acks == [], str(acks))
        check("rc≠0: có event error paper-checkpoint-dispatch-failed-<pid>", len(errs) == 1, str(evs))
        check("rc≠0: KHÔNG ghi cooldown 7 ngày (lần sau tự thử lại)",
              PID not in state_of(mike), str(state_of(mike)))
        out = check5_on(mike)
        check("rc≠0: check #5 THẬT giữ câu hỏi ở nhánh routable (Wags đi triage)",
              "CHƯA thấy answer" in out and f"paper-checkpoint-overdue-{PID}" in out, out)
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── Ca 3 (mutation): đổi ACK_PREFIX phía producer ⇒ hợp đồng gãy ⇒ test phải ĐỎ.
def case_mutation_ack_prefix():
    d, mike = build_sandbox(
        mutate=lambda s: s.replace("triaged-needs-human:Mike/", "triaged-needs-humans:Mike/"))
    try:
        run_script(mike, 0)
        out = check5_on(mike)
        check("mutation ACK_PREFIX: hợp đồng gãy ⇒ câu hỏi rơi lại nhánh routable (test đỏ được)",
              "CHƯA thấy answer" in out, out)
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── Ca 4 (mutation): đổi agent phát question (Mike → Winston) mà khoá trong ack vẫn "Mike/"
#    ⇒ _acked không khớp ⇒ test phải ĐỎ.
def case_mutation_question_agent():
    d, mike = build_sandbox(
        mutate=lambda s: s.replace('append_event.sh" Mike question', 'append_event.sh" Winston question'))
    try:
        run_script(mike, 0)
        out = check5_on(mike)
        check("mutation agent-hỏi: khoá ack lệch tác giả câu hỏi ⇒ routable (test đỏ được)",
              "CHƯA thấy answer" in out, out)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def main():
    print("paper_checkpoint_escalation_selfcheck — hợp đồng ack producer↔check #5")
    for fn in (case_dispatch_ok, case_dispatch_fails,
               case_mutation_ack_prefix, case_mutation_question_agent):
        fn()
    if FAILS:
        print(f"\nFAIL ({len(FAILS)}):")
        for f in FAILS:
            print("  -", f)
        return 1
    print("\nPASS — tất cả bất biến giữ nguyên.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
