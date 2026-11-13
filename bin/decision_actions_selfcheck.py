#!/usr/bin/env python3
"""decision_actions_selfcheck.py — whitelist on_answer + idempotent ledger + validate ở append_event.sh.

Mọi thứ chạy trong --root tmpdir với stub; bus/broker/crontab/BOT_STOP thật KHÔNG bao giờ bị chạm.
"""
from __future__ import annotations

import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import decision_actions as da  # noqa: E402
from decision_inbox_selfcheck import Env  # noqa: E402

ROOT = HERE.parent
N = [0, 0]

SCRIPT_STUB = """#!/usr/bin/env python3
import json, os, pathlib, sys
log = pathlib.Path(__file__).resolve().parents[1] / "calls.log"
with log.open("a", encoding="utf-8") as f:
    f.write(json.dumps({"script": pathlib.Path(__file__).name, "argv": sys.argv[1:],
                        "dispatch_from": os.environ.get("DISPATCH_FROM")}, ensure_ascii=False) + "\\n")
sys.exit(int(os.environ.get("STUB_RC_" + pathlib.Path(__file__).stem.upper(), "0")))
"""


def check(name, cond, detail=""):
    N[0] += 1
    if not cond:
        N[1] += 1
        print(f"FAIL {name}: {detail}", file=sys.stderr)


def mk_root(td: str) -> Path:
    root = Path(td)
    (root / "bin").mkdir(parents=True, exist_ok=True)
    (root / "kb").mkdir(exist_ok=True)
    (root / "decision_templates").mkdir(exist_ok=True)
    (root / "decision_templates" / "tpl_ok.md").write_text("Làm việc X. Không đụng tiền.\n", encoding="utf-8")
    (root / "kb" / "discord_channels.json").write_text(json.dumps({"channels": {"architecture": "x"}}), encoding="utf-8")
    (root / "kb" / "paper_programs_registry.json").write_text(json.dumps({"programs": [
        {"id": "prog_a", "end": None, "owner": "Taylor", "review_date": "2026-12-01"},
        {"id": "prog_b", "end": "2026-12-31", "owner": "Wags"}]}), encoding="utf-8")
    for n in ("remember.sh", "notify_thread.sh", "dispatch.sh", "append_event.sh"):
        p = root / "bin" / n
        p.write_text(SCRIPT_STUB, encoding="utf-8")
        p.chmod(0o755)
    return root


def calls(root: Path):
    p = root / "calls.log"
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines()] if p.exists() else []


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = mk_root(td)
        ok = {"A": [{"action": "remember", "agent": "Mike", "note": "giữ cảnh báo"},
                    {"action": "append_event", "agent": "Taylor", "type": "finding", "topic": "x-y", "payload": {"a": 1}},
                    {"action": "notify_thread", "channel": "architecture", "message": "đã chọn A"},
                    {"action": "dispatch_bg", "target": "Taylor", "template": "tpl_ok", "timeout": 600},
                    {"action": "paper_registry_set", "program": "prog_a", "field": "end", "value": "2027-01-31"}]}
        check("V1 spec hợp lệ (5 loại action) ⇒ không lỗi", da.validate_on_answer(ok, root) == [], str(da.validate_on_answer(ok, root)))

        def bad(name, spec):
            errs = da.validate_on_answer(spec, root)
            check(name, errs != [], "được chấp nhận: " + json.dumps(spec, ensure_ascii=False))

        # V2 — mọi 'đường tới tiền/hệ thống' đều không có trong whitelist
        for act in ("shell", "bash", "exec", "approve_plan", "approve_plan_simple", "bot_stop", "set_bot_stop",
                    "clear_bot_stop", "write_file", "crontab", "broker_order", "place_order", "edit_trading_rules",
                    "secrets_read", "curl", ""):
            bad(f"V2 action {act!r} bị từ chối", {"A": [{"action": act, "cmd": "x"}]})
        bad("V3 dispatch Mafee", {"A": [{"action": "dispatch_bg", "target": "Mafee", "template": "tpl_ok"}]})
        bad("V3 dispatch DollarBill", {"A": [{"action": "dispatch_bg", "target": "DollarBill", "template": "tpl_ok"}]})
        bad("V4 template không tồn tại", {"A": [{"action": "dispatch_bg", "target": "Taylor", "template": "nope"}]})
        bad("V4 template path traversal", {"A": [{"action": "dispatch_bg", "target": "Taylor", "template": "../kb/x"}]})
        bad("V4 prompt tự do không có chỗ đứng", {"A": [{"action": "dispatch_bg", "target": "Taylor", "template": "tpl_ok", "prompt": "rm -rf"}]})
        bad("V4 timeout ngoài khoảng", {"A": [{"action": "dispatch_bg", "target": "Taylor", "template": "tpl_ok", "timeout": 99999}]})
        for t in ("question", "answer", "decision", "error"):
            bad(f"V5 append_event type={t}", {"A": [{"action": "append_event", "agent": "Mike", "type": t, "topic": "x", "payload": {}}]})
        bad("V5 append_event topic retro-pattern-recurring-", {"A": [{"action": "append_event", "agent": "Mike", "type": "status", "topic": "retro-pattern-recurring-x", "payload": {}}]})
        bad("V5 append_event agent Mafee", {"A": [{"action": "append_event", "agent": "Mafee", "type": "status", "topic": "x", "payload": {}}]})
        bad("V6 remember key lạ", {"A": [{"action": "remember", "agent": "Mike", "note": "x", "cmd": "y"}]})
        bad("V6 remember agent DollarBill", {"A": [{"action": "remember", "agent": "DollarBill", "note": "x"}]})
        bad("V7 notify kênh không khai", {"A": [{"action": "notify_thread", "channel": "nope", "message": "x"}]})
        bad("V7 notify ID trần", {"A": [{"action": "notify_thread", "channel": "1" + "2" * 17, "message": "x"}]})
        bad("V8 paper field owner", {"A": [{"action": "paper_registry_set", "program": "prog_a", "field": "owner", "value": "x"}]})
        bad("V8 paper end sai ngày", {"A": [{"action": "paper_registry_set", "program": "prog_a", "field": "end", "value": "mai"}]})
        bad("V9 chữ cái ngoài A-H", {"Z": [{"action": "remember", "agent": "Mike", "note": "x"}]})
        bad("V9 on_answer rỗng", {})
        bad("V9 >5 action", {"A": [{"action": "remember", "agent": "Mike", "note": "x"}] * 6})
        bad("V9 action không phải object", {"A": ["remember"]})

        # R — chạy + idempotent
        res = da.run_actions(root, "qe-1", "A", ok["A"])
        check("R1 5 action ⇒ done", [r["status"] for r in res] == ["done"] * 5, str(res))
        c = calls(root)
        names = [x["script"] for x in c]
        check("R1 gọi đúng stub theo thứ tự (remember/append_event/notify/dispatch)", names == ["remember.sh", "append_event.sh", "notify_thread.sh", "dispatch.sh"], str(names))
        disp = [x for x in c if x["script"] == "dispatch.sh"][0]
        check("R1 dispatch: target + prompt từ template + --bg + DISPATCH_FROM=Mike",
              disp["argv"][0] == "Taylor" and "Làm việc X" in disp["argv"][1] and "--bg" in disp["argv"]
              and disp["dispatch_from"] == "Mike" and disp["argv"][-1] == "600", str(disp))
        reg = json.loads((root / "kb" / "paper_programs_registry.json").read_text(encoding="utf-8"))
        pa = {p["id"]: p for p in reg["programs"]}
        check("R1 paper_registry_set: chỉ đổi đúng field, program khác nguyên", pa["prog_a"]["end"] == "2027-01-31"
              and pa["prog_a"]["owner"] == "Taylor" and pa["prog_b"]["end"] == "2026-12-31", str(reg))
        check("R1 không còn file tmp của ghi nguyên tử", [x.name for x in (root / "kb").glob(".paper_reg_*")] == [])
        res = da.run_actions(root, "qe-1", "A", ok["A"])
        check("R2 chạy lại cùng khoá ⇒ already_done, không gọi thêm", [r["status"] for r in res] == ["already_done"] * 5
              and len(calls(root)) == 4, str(res))
        res = da.run_actions(root, "qe-1", "B", ok["A"][:1])
        check("R2b khác option ⇒ khoá khác ⇒ chạy", res[0]["status"] == "done" and len(calls(root)) == 5)

        # R3 — kill giữa chừng: có `started` không có kết quả ⇒ KHÔNG chạy lại
        led = root / "state" / "decision_inbox" / "actions.jsonl"
        led.parent.mkdir(parents=True, exist_ok=True)
        with led.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"question_event_id": "qe-2", "option": "A", "action_index": 0, "state": "started"}) + "\n")
        n0 = len(calls(root))
        (root / "bin" / "append_event.sh").write_text(
            "#!/usr/bin/env python3\nimport pathlib,sys\npathlib.Path(__file__).resolve().parents[1].joinpath('ae.log').open('a').write(' '.join(sys.argv[1:4])+'\\n')\n", encoding="utf-8")
        (root / "bin" / "append_event.sh").chmod(0o755)
        res = da.run_actions(root, "qe-2", "A", ok["A"][:1])
        check("R3 started không có kết quả ⇒ unknown_needs_human, KHÔNG chạy", res[0]["status"] == "unknown_needs_human"
              and len(calls(root)) == n0, str(res))
        check("R3 báo status decision-action-unknown", "decision-action-unknown" in (root / "ae.log").read_text(encoding="utf-8"))

        # R4 — action lỗi ⇒ ghi failed, không tự retry
        os.environ["STUB_RC_REMEMBER"] = "1"
        try:
            res = da.run_actions(root, "qe-3", "A", ok["A"][:1])
        finally:
            del os.environ["STUB_RC_REMEMBER"]
        check("R4 rc≠0 ⇒ failed", res[0]["status"] == "failed", str(res))
        res = da.run_actions(root, "qe-3", "A", ok["A"][:1])
        check("R4 chạy lại sau failed ⇒ already_done (không retry mù)", res[0]["status"] == "already_done", str(res))
        res = da.run_actions(root, "qe-4", "A", [{"action": "paper_registry_set", "program": "khong_co", "field": "end", "value": None}])
        check("R5 program không tồn tại ⇒ failed", res[0]["status"] == "failed", str(res))
        n1 = len(calls(root))
        res = da.run_actions(root, "qe-5", "A", [{"action": "bash", "cmd": "reboot"}])
        check("R6 action lạ lọt tới runner ⇒ rejected, không chạy gì", res[0]["status"] == "rejected"
              and len(calls(root)) == n1, str(res))

    # E — chốt ở append_event.sh THẬT (copy vào tmp root)
    with tempfile.TemporaryDirectory() as td:
        root = mk_root(td)
        for f in ("append_event.sh", "mike_json.py", "decision_actions.py", "decision_inbox.py", "bus_question_audit.py"):
            shutil.copy(HERE / f, root / "bin" / f)
        (root / "kb" / "version.txt").write_text("1\n", encoding="utf-8")

        def ae(topic, payload):
            r = subprocess.run([str(root / "bin" / "append_event.sh"), "Mike", "question", topic, json.dumps(payload, ensure_ascii=False)],
                               capture_output=True, text=True)
            return r.returncode, r.stdout + r.stderr

        inbox = root / "bus" / "inbox" / "Mike.jsonl"
        rc, _ = ae("docs-ok", {"options": ["A", "B"], "on_answer": {"A": [{"action": "remember", "agent": "Mike", "note": "x"}]}})
        check("E1 on_answer hợp lệ ⇒ ghi", rc == 0 and inbox.exists())
        n_lines = len(inbox.read_text(encoding="utf-8").splitlines())
        rc, out = ae("docs-bad", {"options": ["A", "B"], "on_answer": {"A": [{"action": "shell", "cmd": "x"}]}})
        check("E2 action lạ ⇒ rc=1, lý do nguyên văn, KHÔNG ghi", rc == 1 and "whitelist" in out
              and len(inbox.read_text(encoding="utf-8").splitlines()) == n_lines, out)
        check("E2 bản bị chặn nằm ở bus/_rejected.jsonl", (root / "bus" / "_rejected.jsonl").exists())
        rc, out = ae("plan-park-change", {"options": ["A", "B"], "on_answer": {"A": [{"action": "remember", "agent": "Mike", "note": "x"}]}})
        check("E3 câu money kèm on_answer ⇒ từ chối lúc ghi", rc == 1 and "risk=money" in out, out)
        rc, _ = ae("plan-park-change2", {"options": ["A", "B"], "risk": "normal", "on_answer": {"A": [{"action": "remember", "agent": "Mike", "note": "x"}]}})
        check("E4 risk=normal khai tường minh ⇒ qua", rc == 0)
        rc, _ = ae("plan-without-onanswer", {"options": ["A", "B"]})
        check("E5 câu money KHÔNG có on_answer ⇒ ghi bình thường (guard không đụng)", rc == 0)
        os.remove(root / "bin" / "decision_actions.py")
        rc, out = ae("docs-novalidator", {"options": ["A"], "on_answer": {"A": [{"action": "remember", "agent": "Mike", "note": "x"}]}})
        check("E6 validator vắng ⇒ từ chối fail-loud, nêu lỗi thật", rc == 1 and "decision_actions.py" in out, out)

    # I — tích hợp decision_inbox: câu normal chạy on_answer; money bỏ qua; shadow không chạy
    with tempfile.TemporaryDirectory() as td:
        e = Env(td)
        root = e.root
        for n in ("remember.sh", "notify_thread.sh", "dispatch.sh"):
            (root / "bin" / n).write_text(SCRIPT_STUB, encoding="utf-8")
            (root / "bin" / n).chmod(0o755)
        (root / "kb").mkdir(exist_ok=True)
        (root / "kb" / "discord_channels.json").write_text(json.dumps({"channels": {"architecture": "x"}}), encoding="utf-8")
        spec = {"A": [{"action": "remember", "agent": "Mike", "note": "user chọn A"}]}
        qn = e.q("Mike", "docs-onanswer", ["A: x", "B: y"], on_answer=spec)
        r = e.user("m0", "c1", "A #" + qn["tag"], mode="shadow")
        check("I1 shadow ⇒ KHÔNG chạy action", r["outcome"] == "shadow_would_close" and calls(root) == [], str(r))
        r = e.user("m1", "c1", "A #" + qn["tag"])
        check("I2 live + normal ⇒ chạy on_answer(A)", r["outcome"] == "closed" and r["actions"][0]["status"] == "done"
              and [x["script"] for x in calls(root)] == ["remember.sh"], str(r))
        qm = e.q("Mike", "nav-brake-decision", ["A: x", "B: y"], on_answer=spec)   # bỏ qua validator (ghi thẳng)
        n0 = len(calls(root))
        r = e.user("m2", "c1", "A #" + qm["tag"])
        check("I3 câu money bị lọt on_answer ⇒ đóng nhưng KHÔNG chạy action", r["outcome"] == "closed"
              and "actions" not in r and len(calls(root)) == n0, str(r))
        qo = e.q("Mike", "docs-onanswer-b", ["A: x", "B: y"], on_answer=spec)
        r = e.user("m3", "c1", "B #" + qo["tag"])
        check("I4 phương án không khai on_answer ⇒ actions=[]", r["outcome"] == "closed" and r["actions"] == [], str(r))

    # S — cưỡng chế tĩnh: mã nguồn runner không có chuỗi hằng nào nhắc tới bề mặt cấm
    tree = ast.parse((HERE / "decision_actions.py").read_text(encoding="utf-8"))
    doc_nodes = {id(n.body[0].value) for n in ast.walk(tree)
                 if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef)) and n.body
                 and isinstance(n.body[0], ast.Expr) and isinstance(getattr(n.body[0], "value", None), ast.Constant)}
    consts = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)
              and id(n) not in doc_nodes]
    forbidden = ("BOT_STOP", "trading_rules", "secrets", "approve_plan", "crontab", "Mafee/", "place_order")
    hits = [(c[:60], f) for c in consts for f in forbidden if f in c]
    # ngoại lệ có chủ đích: thông điệp lỗi/validate nhắc 'cấm Mafee/DollarBill' bằng chữ
    hits = [h for h in hits if not (h[1] == "Mafee/" and "cấm" in h[0])]
    check("S1 chuỗi hằng của runner không nhắc BOT_STOP/trading_rules/secrets/approve_plan/crontab", hits == [], str(hits))
    src_calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "run"
                 and getattr(getattr(n.func, "value", None), "id", "") == "subprocess"]
    check("S2 mọi subprocess.run dùng list-argv (không shell=True)", src_calls and all(
        not any(k.arg == "shell" for k in c.keywords) and c.args and isinstance(c.args[0], (ast.List, ast.Name))
        for c in src_calls))

    if N[1]:
        print(f"decision_actions_selfcheck: {N[0] - N[1]}/{N[0]} PASS, {N[1]} FAIL", file=sys.stderr)
        return 1
    print(f"decision_actions_selfcheck: {N[0]}/{N[0]} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
