#!/usr/bin/env python3
"""Close only bus questions whose resolution is mechanically provable.

This is a daily housekeeping routine, not a semantic classifier. Unknown topics and
decision/money questions remain open. Supported recurring classes:
  * context-bloat-same-day: all context files are back under their hard limits;
  * report email/delivery gap: a daily report has COMPLETE hash-bound delivery proof;
  * scheduled report cron in a worktree: both entries now point at the stable repo;
  * selfcheck-red: latest full-sweep artifact says that exact file is PASS.

Use --dry-run --json for audit/selfcheck. Normal mode appends exact-topic answers, so
bus_question_audit.py's timestamp-aware matcher closes the original question.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def complete_delivery(root, basename):
    report = root / "reports" / basename
    state_path = root / "state" / "report_delivery.json"
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
        rec = state.get("reports", {}).get(basename, {})
        sha = hashlib.sha256(report.read_bytes()).hexdigest()
    except (OSError, ValueError, TypeError, AttributeError):
        return False

    def channel(name):
        value = rec.get(name, {})
        return (isinstance(value, dict) and value.get("status") == "delivered"
                and value.get("sha256") == sha and value.get("delivered_at"))

    return (rec.get("sha256") == sha and rec.get("artifact_validated_at")
            and channel("discord") and channel("email"))


def context_bloat_resolved(root):
    limits = {"kb/context_pack.md": 45 * 1024,
              "MIKE.md": 40 * 1024,
              "kb/coding_guidelines.md": 40 * 1024}
    for rel, limit in limits.items():
        path = root / rel
        try:
            size = path.stat().st_size
        except OSError:
            return None
        if size <= 0 or size > limit:
            return None
    rationale = root / "kb" / "coding_guidelines_rationale.md"
    if not rationale.is_file() or rationale.stat().st_size == 0:
        return None
    sizes = ", ".join(f"{rel}={((root / rel).stat().st_size)}B" for rel in limits)
    return f"all hard limits pass; rationale split exists; {sizes}"


def report_delivery_resolved(root):
    candidates = sorted((root / "reports").glob("*_daily_report_*.md"),
                        key=lambda p: p.stat().st_mtime, reverse=True)
    for path in candidates:
        if path.name.startswith("paper_programs_daily_report_"):
            continue
        if complete_delivery(root, path.name):
            gate = root / "bin" / "check_report_cadence.sh"
            try:
                wired = "report_delivery_gate.py" in gate.read_text(encoding="utf-8")
            except OSError:
                wired = False
            if wired:
                return f"delivery COMPLETE and hash-bound for {path.name}; cadence backstop wired"
    return None


def cron_resolved(root, crontab_text):
    lines = [line.strip() for line in crontab_text.splitlines()
             if "check_report_cadence.sh" in line and not line.lstrip().startswith("#")]
    if any("/agents/wt-" in line for line in lines):
        return None
    stable = str(root / "bin" / "check_report_cadence.sh")
    weekly = any(stable in line and "--scheduled-weekly" in line for line in lines)
    monthly = any(stable in line and "--scheduled-monthly" in line for line in lines)
    if weekly and monthly:
        return "scheduled weekly/monthly entries both use stable repo path; no worktree path remains"
    return None


def selfcheck_resolved(root, topic):
    prefix = "selfcheck-red: "
    target = topic[len(prefix):].strip()
    files = sorted((root / "logs").glob("selfcheck_weekly_*.json"), reverse=True)
    if not target or not files:
        return None
    try:
        result = json.loads(files[0].read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return None
    if result.get("raw", {}).get(target) == "PASS":
        return f"latest full-sweep artifact {files[0].name} records {target}=PASS"
    return None


def pending(root):
    audit = ROOT / "bin" / "bus_question_audit.py"
    env = dict(os.environ, BUS_AUDIT_ROOT=str(root))
    run = subprocess.run([sys.executable, str(audit), "--json"], env=env,
                         capture_output=True, text=True)
    try:
        return json.loads(run.stdout).get("pending", [])
    except (ValueError, TypeError, AttributeError):
        raise RuntimeError(f"bus question audit failed: rc={run.returncode} {run.stderr[-300:]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--crontab-file", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    root = args.root.resolve()

    if args.crontab_file:
        cron_text = args.crontab_file.read_text(encoding="utf-8")
    else:
        proc = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        cron_text = proc.stdout if proc.returncode == 0 else ""

    shared = {
        "context-bloat-same-day": context_bloat_resolved(root),
        "eod-daily-report-chua-bao-gio-gui-email-vs-coding-guidelines-6.5":
            report_delivery_resolved(root),
        "2-dong-cron-chay-check_report_cadence-tu-worktree-phien":
            cron_resolved(root, cron_text),
    }
    actions = []
    for item in pending(root):
        topic = str(item.get("topic") or "")
        evidence = shared.get(topic)
        if topic.startswith("selfcheck-red: "):
            evidence = selfcheck_resolved(root, topic)
        if evidence:
            actions.append({"agent": item.get("agent"), "topic": topic,
                            "evidence": evidence})

    closed = []
    if not args.dry_run:
        append = root / "bin" / "append_event.sh"
        for action in actions:
            payload = json.dumps({"closed_by": "bus_question_housekeeping.py (daily)",
                                  "evidence": action["evidence"],
                                  "decided_by": "agent"}, ensure_ascii=False)
            run = subprocess.run([str(append), "Mike", "answer", action["topic"], payload],
                                 capture_output=True, text=True)
            if run.returncode != 0:
                print(f"housekeeping: REFUSED to claim closure for {action['topic']}: "
                      f"{run.stderr.strip()[-300:]}", file=sys.stderr)
                continue
            closed.append(action)

    result = {"eligible": actions, "closed": closed, "dry_run": args.dry_run}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        verb = "eligible" if args.dry_run else "closed"
        print(f"bus_question_housekeeping: {verb}={len(actions) if args.dry_run else len(closed)}")
        for item in (actions if args.dry_run else closed):
            print(f"  {item['topic']} — {item['evidence']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
