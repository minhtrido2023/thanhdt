#!/usr/bin/env python3
"""decision_actions.py — WHITELIST hành động `on_answer` của Decision Inbox (DESIGN §4).

Một câu hỏi bus có thể khai sẵn hậu quả theo từng phương án:
  "on_answer": {"A": [{"action":"remember","agent":"Mike","note":"…"}], "B": [{"action":"dispatch_bg",…}]}
Khi user trả lời "A", `decision_inbox.py` (script xác định, KHÔNG phải LLM) chạy các action của "A".

Whitelist cố định TRONG CODE (không đọc từ file cấu hình ⇒ LLM không mở rộng được):
  remember            → bin/remember.sh <agent> <note>          agent ∈ REMEMBER_AGENTS
  append_event        → bin/append_event.sh <agent> finding|status <topic> <payload>   (không question/answer/decision)
  notify_thread       → bin/notify_thread.sh <msg> <tên kênh trong kb/discord_channels.json>
  dispatch_bg         → bin/dispatch.sh <target> <prompt từ decision_templates/<tên>.md> --bg   target ∈ {Taylor,Winston,Wags}
  paper_registry_set  → ghi 1 field (end/review_date/status/end_or_trigger) của 1 program trong kb/paper_programs_registry.json

KHÔNG BAO GIỜ có (không có đường code nào dẫn tới): tạo/xoá data/BOT_STOP, sửa trading_rules.json, secrets/**,
approve_plan*, lệnh broker, crontab, shell tự do, dispatch Mafee/DollarBill. Câu risk=money bị bỏ qua toàn bộ
on_answer (decision_inbox.py) và bị TỪ CHỐI ngay lúc ghi (append_event.sh gọi --validate).

Idempotent (coding_guidelines §5): sổ `state/decision_inbox/actions.jsonl`, khoá (question_event_id, option,
action_index); ghi `started` TRƯỚC khi gọi, `done|failed` NGAY sau. Gặp `started` không có kết quả ⇒ KHÔNG chạy lại,
báo `status decision-action-unknown` (fail-safe pause cho người xem).

CLI: decision_actions.py --validate --agent A --topic T [--root R]   (payload JSON của câu hỏi qua stdin)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

ACTIONS = ("remember", "append_event", "notify_thread", "dispatch_bg", "paper_registry_set")
REMEMBER_AGENTS = {"Mike", "Taylor", "Wags", "Winston"}
EVENT_AGENTS = {"Mike", "Taylor", "Wags", "Winston"}
EVENT_TYPES = {"finding", "status"}
DISPATCH_TARGETS = {"Taylor", "Winston", "Wags"}          # cấm Mafee/DollarBill
PAPER_FIELDS = {"end", "review_date", "status", "end_or_trigger"}
LETTERS = set("ABCDEFGH")
MAX_ACTIONS = 5
ACTION_TIMEOUT = 30   # mỗi subprocess; decision_inbox.ACTIONS_BUDGET_S = MAX_ACTIONS × ACTION_TIMEOUT
TOPIC_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:\-]{0,119}$")
TEMPLATE_RE = re.compile(r"^[a-z0-9_]{1,60}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ALLOWED_KEYS = {
    "remember": {"action", "agent", "note"},
    "append_event": {"action", "agent", "type", "topic", "payload"},
    "notify_thread": {"action", "channel", "message"},
    "dispatch_bg": {"action", "target", "template", "timeout"},
    "paper_registry_set": {"action", "program", "field", "value"},
}


def _channels(root: Path) -> set[str]:
    try:
        return set(json.loads((root / "kb" / "discord_channels.json").read_text(encoding="utf-8"))["channels"])
    except (OSError, ValueError, KeyError):
        return set()


def validate_action(act, root: Path) -> list[str]:
    if not isinstance(act, dict):
        return ["action phải là object"]
    name = act.get("action")
    if name not in ACTIONS:
        return [f"action {name!r} không thuộc whitelist {list(ACTIONS)}"]
    errs = [f"{name}: key lạ {k!r}" for k in sorted(set(act) - ALLOWED_KEYS[name])]
    s = lambda k: act.get(k) if isinstance(act.get(k), str) else None  # noqa: E731
    if name == "remember":
        if act.get("agent") not in REMEMBER_AGENTS:
            errs.append(f"remember: agent phải ∈ {sorted(REMEMBER_AGENTS)}")
        if not s("note") or len(act["note"]) > 400:
            errs.append("remember: note bắt buộc, ≤400 ký tự")
        elif act["note"].lstrip().startswith("-"):   # remember.sh hiểu `--clear`/`--set` là cờ (vòng 2, mục 5)
            errs.append("remember: note không được bắt đầu bằng '-' (chặn tiêm cờ --clear/--set)")
    elif name == "append_event":
        if act.get("agent") not in EVENT_AGENTS:
            errs.append(f"append_event: agent phải ∈ {sorted(EVENT_AGENTS)}")
        if act.get("type") not in EVENT_TYPES:
            errs.append(f"append_event: type phải ∈ {sorted(EVENT_TYPES)} (cấm question/answer/decision)")
        if not s("topic") or not TOPIC_RE.match(act["topic"]) or act["topic"].startswith("retro-pattern-recurring-"):
            errs.append("append_event: topic không hợp lệ")
        if not isinstance(act.get("payload"), dict) or len(json.dumps(act["payload"], ensure_ascii=False)) > 2000:
            errs.append("append_event: payload phải là object ≤2000 ký tự")
    elif name == "notify_thread":
        if not s("message") or len(act["message"]) > 1500:
            errs.append("notify_thread: message bắt buộc, ≤1500 ký tự")
        elif act["message"].lstrip().startswith("-"):   # notify_thread.sh gửi cờ lạ thành text/diễn giải cờ
            errs.append("notify_thread: message không được bắt đầu bằng '-'")
        if act.get("channel") not in _channels(root):
            errs.append("notify_thread: channel phải là TÊN khai trong kb/discord_channels.json")
    elif name == "dispatch_bg":
        if act.get("target") not in DISPATCH_TARGETS:
            errs.append(f"dispatch_bg: target phải ∈ {sorted(DISPATCH_TARGETS)} (cấm Mafee/DollarBill)")
        t = s("template")
        if not t or not TEMPLATE_RE.match(t):
            errs.append("dispatch_bg: template phải là tên [a-z0-9_]+")
        elif not (root / "decision_templates" / f"{t}.md").is_file():
            errs.append(f"dispatch_bg: thiếu decision_templates/{t}.md")
        tm = act.get("timeout", 900)
        if not isinstance(tm, int) or isinstance(tm, bool) or not 60 <= tm <= 1800:
            errs.append("dispatch_bg: timeout phải là int 60..1800")
    elif name == "paper_registry_set":
        if act.get("field") not in PAPER_FIELDS:
            errs.append(f"paper_registry_set: field phải ∈ {sorted(PAPER_FIELDS)}")
        if not s("program") or not re.match(r"^[A-Za-z0-9_\-]{1,60}$", act["program"]):
            errs.append("paper_registry_set: program không hợp lệ")
        v = act.get("value")
        if act.get("field") in ("end", "review_date"):
            if v is not None and not (isinstance(v, str) and DATE_RE.match(v)):
                errs.append("paper_registry_set: end/review_date phải là YYYY-MM-DD hoặc null")
        elif not isinstance(v, str) or not v or len(v) > 300:
            errs.append("paper_registry_set: value phải là chuỗi 1..300 ký tự")
    return errs


def validate_on_answer(on_answer, root: Path = ROOT) -> list[str]:
    if not isinstance(on_answer, dict) or not on_answer:
        return ["on_answer phải là object không rỗng"]
    errs: list[str] = []
    for letter, acts in on_answer.items():
        if letter not in LETTERS:
            errs.append(f"on_answer: khoá {letter!r} không phải chữ cái A-H")
            continue
        if not isinstance(acts, list) or not acts or len(acts) > MAX_ACTIONS:
            errs.append(f"on_answer[{letter}]: phải là list 1..{MAX_ACTIONS} action")
            continue
        for i, a in enumerate(acts):
            errs += [f"on_answer[{letter}][{i}]: {e}" for e in validate_action(a, root)]
    return errs


# ───────────────────────── chạy ─────────────────────────
def _run(cmd: list[str], timeout: int = ACTION_TIMEOUT) -> tuple[bool, str]:
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return r.returncode == 0, ((r.stdout or "") + (r.stderr or ""))[-300:]


def _paper_set(root: Path, act: dict) -> tuple[bool, str]:
    p = root / "kb" / "paper_programs_registry.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    prog = next((x for x in data.get("programs", []) if x.get("id") == act["program"]), None)
    if prog is None:
        return False, f"không có program {act['program']!r}"
    old = prog.get(act["field"])
    prog[act["field"]] = act["value"]
    fd, tmp = tempfile.mkstemp(dir=str(p.parent), prefix=".paper_reg_", suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    os.replace(tmp, p)
    return True, f"{act['program']}.{act['field']}: {old!r} -> {act['value']!r}"


def _execute(root: Path, act: dict) -> tuple[bool, str]:
    b = root / "bin"
    n = act["action"]
    if n == "remember":
        return _run([str(b / "remember.sh"), act["agent"], act["note"]])
    if n == "append_event":
        return _run([str(b / "append_event.sh"), act["agent"], act["type"], act["topic"],
                     json.dumps(act["payload"], ensure_ascii=False)])
    if n == "notify_thread":
        return _run([str(b / "notify_thread.sh"), act["message"], act["channel"]])
    if n == "dispatch_bg":
        prompt = (root / "decision_templates" / f"{act['template']}.md").read_text(encoding="utf-8")
        env = dict(os.environ, DISPATCH_FROM="Mike")
        r = subprocess.run([str(b / "dispatch.sh"), act["target"], prompt, "--bg", "--no-followup", "--timeout",
                            str(act.get("timeout", 900))], capture_output=True, text=True, timeout=ACTION_TIMEOUT, env=env)
        return r.returncode == 0, ((r.stdout or "") + (r.stderr or ""))[-300:]
    return _paper_set(root, act)


def _ledger(root: Path) -> Path:
    d = root / "state" / "decision_inbox"
    d.mkdir(parents=True, exist_ok=True)
    return d / "actions.jsonl"


def _rows(path: Path) -> list[dict]:
    rows = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                rows.append(json.loads(line))
            except ValueError:
                continue
    return rows


def _append(path: Path, rec: dict) -> None:
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def run_actions(root: Path, question_event_id: str, option: str, actions: list) -> list[dict]:
    root = Path(root)
    led = _ledger(root)
    out = []
    for idx, act in enumerate(actions):
        key = {"question_event_id": question_event_id, "option": option, "action_index": idx}
        name = act.get("action") if isinstance(act, dict) else None
        prior = [r for r in _rows(led) if all(r.get(k) == v for k, v in key.items())]
        states = {r.get("state") for r in prior}
        if states & {"done", "failed"}:
            out.append({"action": name, "index": idx, "status": "already_done"})
            continue
        if "started" in states:   # killed giữa chừng: KHÔNG đoán, KHÔNG chạy lại
            _post_unknown(root, key, name)
            out.append({"action": name, "index": idx, "status": "unknown_needs_human"})
            continue
        errs = validate_action(act, root)
        if errs:
            _append(led, {**key, "state": "failed", "action": name, "detail": "; ".join(errs)})
            out.append({"action": name, "index": idx, "status": "rejected", "detail": errs})
            continue
        _append(led, {**key, "state": "started", "action": name})
        try:
            ok, detail = _execute(root, act)
        except Exception as exc:  # noqa: BLE001
            ok, detail = False, f"{type(exc).__name__}: {exc}"
        _append(led, {**key, "state": "done" if ok else "failed", "action": name, "detail": detail})
        out.append({"action": name, "index": idx, "status": "done" if ok else "failed", "detail": detail})
    return out


def _post_unknown(root: Path, key: dict, name) -> None:
    try:
        subprocess.run([str(root / "bin" / "append_event.sh"), "Mike", "status", "decision-action-unknown",
                        json.dumps({**key, "action": name, "note": "ledger có `started` mà không có kết quả; KHÔNG chạy lại, cần người kiểm",
                                    "measured_by": "state/decision_inbox/actions.jsonl"}, ensure_ascii=False)],
                       capture_output=True, text=True, timeout=ACTION_TIMEOUT)
    except (OSError, subprocess.SubprocessError):
        pass


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--validate", action="store_true", required=True)
    ap.add_argument("--agent", default="")
    ap.add_argument("--topic", default="")
    ap.add_argument("--root", type=Path, default=ROOT)
    a = ap.parse_args()
    try:
        payload = json.loads(sys.stdin.read())
    except ValueError as exc:
        print(f"decision_actions: payload không phải JSON: {exc}", file=sys.stderr)
        return 2
    if not isinstance(payload, dict) or "on_answer" not in payload:
        return 0
    errs = validate_on_answer(payload["on_answer"], a.root)
    import decision_inbox
    if decision_inbox.classify_risk(a.agent, a.topic, payload) == "money":
        errs.append("câu hỏi này được xếp risk=money ⇒ on_answer sẽ bị BỎ QUA khi trả lời; bỏ on_answer, "
                    "hoặc đặt \"risk\":\"normal\" nếu thật sự không chạm tiền/plan/lệnh")
    for e in errs:
        print(f"decision_actions: {e}", file=sys.stderr)
    return 2 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
