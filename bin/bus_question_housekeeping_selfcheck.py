#!/usr/bin/env python3
"""Regression checks for deterministic daily bus-question housekeeping."""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "bin" / "bus_question_housekeeping.py"
passes = failures = 0


def check(name, condition, detail=""):
    global passes, failures
    if condition:
        passes += 1
        print(f"  ok   {name}")
    else:
        failures += 1
        print(f"  FAIL {name} — {detail}")


def event(kind, topic, ts):
    return {"event_id": f"{kind}-{ts}-{topic}", "ts": ts, "agent_id": "Mike",
            "event_type": kind, "topic": topic, "payload": {}}


def fixture():
    td = tempfile.TemporaryDirectory()
    root = Path(td.name)
    for rel in ("bin", "bus/inbox", "bus/inbox/archive", "kb", "logs", "reports", "state"):
        (root / rel).mkdir(parents=True, exist_ok=True)
    for rel, size in (("kb/context_pack.md", 1024), ("MIKE.md", 1024),
                      ("kb/coding_guidelines.md", 1024),
                      ("kb/coding_guidelines_rationale.md", 1024)):
        (root / rel).write_text("x" * size, encoding="utf-8")
    (root / "bin/check_report_cadence.sh").write_text(
        "python3 bin/report_delivery_gate.py report --topic trading_report\n", encoding="utf-8")
    report = root / "reports/SpaceX_ZaloPay_daily_report_2026-08-14.md"
    report.write_text("verified fixture\n", encoding="utf-8")
    sha = hashlib.sha256(report.read_bytes()).hexdigest()
    proof = {"sha256": sha, "artifact_validated_at": "now",
             "discord": {"status": "delivered", "delivered_at": "now", "sha256": sha},
             "email": {"status": "delivered", "delivered_at": "now", "sha256": sha}}
    (root / "state/report_delivery.json").write_text(
        json.dumps({"reports": {report.name: proof}}), encoding="utf-8")
    (root / "logs/selfcheck_weekly_20260815.json").write_text(
        json.dumps({"raw": {"mike/bin/job_cancel_guard_selfcheck.py": "PASS"}}),
        encoding="utf-8")
    cron = root / "cron.txt"
    stable = root / "bin/check_report_cadence.sh"
    cron.write_text(f"0 2 * * 6 {stable} --scheduled-weekly\n"
                    f"0 2 1 * * {stable} --scheduled-monthly\n", encoding="utf-8")
    return td, root, cron, report


def run(root, cron):
    proc = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root),
                           "--crontab-file", str(cron), "--dry-run", "--json"],
                          capture_output=True, text=True, env=dict(os.environ))
    try:
        return proc.returncode, json.loads(proc.stdout), proc.stderr
    except ValueError:
        return proc.returncode, {}, proc.stdout + proc.stderr


topics = [
    "context-bloat-same-day",
    "eod-daily-report-chua-bao-gio-gui-email-vs-coding-guidelines-6.5",
    "2-dong-cron-chay-check_report_cadence-tu-worktree-phien",
    "selfcheck-red: mike/bin/job_cancel_guard_selfcheck.py",
    "can-user-quyet-mo-cong-CASH_VENDOR-va-kiem-freshness",
]

td, root, cron, report = fixture()
try:
    (root / "bus/inbox/Mike.jsonl").write_text(
        "".join(json.dumps(event("question", topic, "2026-08-15T01:00:00Z")) + "\n"
                for topic in topics), encoding="utf-8")
    rc, out, detail = run(root, cron)
    eligible = {item["topic"] for item in out.get("eligible", [])}
    check("four mechanically provable topics are eligible", eligible == set(topics[:4]), str(out))
    check("CASH_VENDOR decision is never auto-closed", topics[4] not in eligible, str(out))
    check("dry-run has no bus side effect", "\"event_type\": \"answer\"" not in
          (root / "bus/inbox/Mike.jsonl").read_text(encoding="utf-8"))

    # Break every proof independently; none may be rationalised into a closure.
    (root / "kb/coding_guidelines.md").write_text("x" * (40 * 1024 + 1), encoding="utf-8")
    state = json.loads((root / "state/report_delivery.json").read_text(encoding="utf-8"))
    state["reports"][report.name]["email"]["sha256"] = "wrong"
    (root / "state/report_delivery.json").write_text(json.dumps(state), encoding="utf-8")
    cron.write_text(f"0 2 * * 6 {root}/agents/wt-x/bin/check_report_cadence.sh --scheduled-weekly\n",
                    encoding="utf-8")
    (root / "logs/selfcheck_weekly_20260815.json").write_text(
        json.dumps({"raw": {"mike/bin/job_cancel_guard_selfcheck.py": "FAIL"}}),
        encoding="utf-8")
    rc, out, detail = run(root, cron)
    check("broken proofs close nothing", out.get("eligible") == [], str(out) or detail)

    # An old answer cannot resolve a later repeated question; the daily probe must see it.
    with (root / "bus/inbox/Mike.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event("answer", topics[0], "2026-08-15T02:00:00Z")) + "\n")
        handle.write(json.dumps(event("question", topics[0], "2026-08-15T03:00:00Z")) + "\n")
    (root / "kb/coding_guidelines.md").write_text("small", encoding="utf-8")
    rc, out, detail = run(root, cron)
    check("same topic asked again after old answer becomes eligible again",
          topics[0] in {item["topic"] for item in out.get("eligible", [])}, str(out))
finally:
    td.cleanup()

print(f"\n{passes}/{passes + failures} PASS")
sys.exit(1 if failures else 0)
