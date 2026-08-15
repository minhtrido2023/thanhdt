#!/usr/bin/env python3
"""Idempotently deliver one client-facing report to Discord and email.

Completion is fail-closed: the artifact must pass the return gate and both
destinations must have durable, hash-bound success evidence.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STATE = ROOT / "state" / "report_delivery.json"
LEGACY_EMAIL_STATE = ROOT / "state" / "report_emailed.json"


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_json(path: Path, missing):
    if not path.exists():
        return missing
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"state malformed: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"state malformed: {path}: root must be an object")
    return data


def save_atomic(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False, sort_keys=True)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(tmp)


def channel_done(record: dict, channel: str, sha: str) -> bool:
    value = record.get(channel)
    return (isinstance(value, dict) and value.get("status") == "delivered"
            and value.get("sha256") == sha and bool(value.get("delivered_at")))


def complete(record: dict, sha: str) -> bool:
    return (record.get("sha256") == sha
            and bool(record.get("artifact_validated_at"))
            and channel_done(record, "discord", sha)
            and channel_done(record, "email", sha))


def run_checked(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def deliver(report: Path, state_path: Path, topic: str, notify_script: Path,
            email_script: Path, skip_validation: bool = False) -> int:
    report = report.resolve()
    if not report.is_file() or report.suffix.lower() != ".md":
        print(f"report_delivery_gate: invalid report: {report}", file=sys.stderr)
        return 2

    state_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = state_path.with_suffix(state_path.suffix + ".lock")
    with lock_path.open("a+", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            state = load_json(state_path, {"version": 1, "reports": {}})
            reports = state.setdefault("reports", {})
            if not isinstance(reports, dict):
                raise RuntimeError("state malformed: reports must be an object")
            sha = digest(report)
            key = report.name
            record = reports.get(key, {})
            if not isinstance(record, dict) or record.get("sha256") != sha:
                record = {"path": str(report), "sha256": sha, "created_at": now()}
                reports[key] = record

            if complete(record, sha):
                print(f"report_delivery_gate: COMPLETE (idempotent) {key}")
                return 0

            if not record.get("artifact_validated_at"):
                if not skip_validation:
                    run_checked([sys.executable, str(ROOT / "bin" / "report_return_gate.py"),
                                 "--report", str(report)])
                record["artifact_validated_at"] = now()
                save_atomic(state_path, state)

            if not channel_done(record, "discord", sha):
                body = report.read_text(encoding="utf-8")
                run_checked([str(notify_script), body, topic])
                record["discord"] = {"status": "delivered", "delivered_at": now(),
                                     "sha256": sha, "topic": topic}
                save_atomic(state_path, state)

            if not channel_done(record, "email", sha):
                run_checked([sys.executable, str(email_script), str(report)])
                record["email"] = {"status": "delivered", "delivered_at": now(),
                                   "sha256": sha}
                save_atomic(state_path, state)
                # Keep the old email backstop idempotent during migration.
                legacy = load_json(LEGACY_EMAIL_STATE, {})
                legacy[key] = dt.datetime.now().astimezone().date().isoformat()
                save_atomic(LEGACY_EMAIL_STATE, legacy)

            record["completed_at"] = now()
            save_atomic(state_path, state)
            print(f"report_delivery_gate: COMPLETE {key} (validated + Discord + email)")
            return 0
        except (RuntimeError, OSError, subprocess.CalledProcessError) as exc:
            print(f"report_delivery_gate: INCOMPLETE — {exc}", file=sys.stderr)
            return 1


def status(report: Path, state_path: Path) -> int:
    try:
        sha = digest(report)
        state = load_json(state_path, {"reports": {}})
        record = state.get("reports", {}).get(report.name, {})
    except (OSError, RuntimeError) as exc:
        print(f"INCOMPLETE: {exc}", file=sys.stderr)
        return 1
    if complete(record, sha):
        print(f"COMPLETE {report.name}")
        return 0
    print(f"INCOMPLETE {report.name}")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("report", type=Path)
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--state", type=Path, default=DEFAULT_STATE)
    ap.add_argument("--topic", default="trading_report")
    ap.add_argument("--notify-script", type=Path, default=ROOT / "bin" / "notify_thread.sh")
    ap.add_argument("--email-script", type=Path, default=ROOT / "bin" / "send_report_email.py")
    ap.add_argument("--skip-validation", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args()
    return status(args.report.resolve(), args.state.resolve()) if args.status else deliver(
        args.report, args.state.resolve(), args.topic, args.notify_script.resolve(),
        args.email_script.resolve(), args.skip_validation)


if __name__ == "__main__":
    raise SystemExit(main())
