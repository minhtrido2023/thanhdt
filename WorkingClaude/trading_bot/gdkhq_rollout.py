# -*- coding: utf-8 -*-
"""Rollout state and acceptance reporting for the GDKHQ D1-D3 execution gate.

Until one live, read-only broker trace passes, event-day orders are blocked per ticker.  Normal
orders remain untouched.  The state file is deliberately runtime data (gitignored), written only
by the explicit shadow command after every required live check succeeds.

Every shadow run must also write an acceptance report.  A report is created even on FAIL so a
broken or postponed run cannot be mistaken for "nothing to do".  A PASS report is only a
pending acceptance: the live marker is written by the explicit user acceptance command, never
by the shadow check itself.
"""
import datetime as dt
import json
import os
import tempfile


WC_ROOT = os.path.abspath(os.environ.get("TRADING_BOT_RUNTIME_ROOT") or
                          os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATE_PATH = os.path.join(WC_ROOT, "data", "gdkhq_d1d3_rollout.json")
ACCEPTANCE_STATE_PATH = os.path.join(WC_ROOT, "data", "gdkhq_shadow_acceptance.json")
REPORT_DIR = os.path.join(WC_ROOT, "data", "gdkhq_shadow")


def _now_iso():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def _atomic_write_json(path, value):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=os.path.basename(path) + ".", suffix=".tmp",
                               dir=os.path.dirname(path))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(value, f, ensure_ascii=False, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass


def read_state(path=STATE_PATH):
    try:
        with open(path, encoding="utf-8") as f:
            value = json.load(f)
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError, TypeError):
        return {}


def enabled(path=STATE_PATH):
    state = read_state(path)
    return (state.get("status") == "enabled"
            and state.get("shadow_passed") is True
            and state.get("acceptance_status") == "ACCEPTED"
            and bool(state.get("report_path")))


def read_acceptance(path=ACCEPTANCE_STATE_PATH):
    """Read the latest GDKHQ shadow acceptance state; missing/invalid -> {}."""
    return read_state(path)


def write_acceptance_report(trace, verdict, plan_date, trace_path, report_path=None,
                            state_path=ACCEPTANCE_STATE_PATH):
    """Write a human report plus machine-readable acceptance state for one run.

    FAIL is recorded as ``FAILED_REVIEW_REQUIRED`` so it is never left as an
    unlabelled pending state.  PASS starts as ``PENDING_ACCEPTANCE`` until the
    user signs off through ``accept_shadow``.
    """
    report_path = os.path.abspath(report_path or os.path.join(
        REPORT_DIR, f"gdkhq_shadow_acceptance_{plan_date}.md"))
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    errors = []
    for account in trace.get("accounts", []):
        label = account.get("label", "?")
        if account.get("error"):
            errors.append(f"{label}: {account['error']}")
        for ticker, frame in account.get("frames", {}).items():
            if not frame.get("ok"):
                reason = frame.get("reason") or frame.get("gate") or "frame failed"
                errors.append(f"{label}/{ticker}: {reason}")
        for adjustment in account.get("plan_adjustments", []):
            if adjustment.get("action") in ("BLOCKED", "CALENDAR_FAIL"):
                errors.append(f"{label}: {adjustment.get('ticker')} "
                              f"{adjustment.get('action')}: {adjustment.get('reason')}")
    if trace.get("calendar_missing"):
        errors.append("calendar_missing: " + ", ".join(trace["calendar_missing"]))

    passed = bool(trace.get("passed"))
    acceptance_status = "PENDING_ACCEPTANCE" if passed else "FAILED_REVIEW_REQUIRED"
    state = {
        "kind": "GDKHQ_SHADOW_ACCEPTANCE",
        "schema_version": 1,
        "plan_date": str(plan_date),
        "trace_passed": passed,
        "promoted": bool(trace.get("promoted")),
        "watch": list(trace.get("watch", [])),
        "account_count": len(trace.get("accounts", [])),
        "trace_path": os.path.abspath(trace_path),
        "report_path": report_path,
        "acceptance_status": acceptance_status,
        "accepted_by": None,
        "accepted_at": None,
        "reported_at": _now_iso(),
        "errors": errors,
        "verdict": str(verdict),
    }
    _atomic_write_json(state_path, state)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(_render_report(state))
        f.flush()
        os.fsync(f.fileno())
    return report_path, state


def _render_report(state):
    status = "PASS" if state["trace_passed"] else "FAIL"
    lines = [
        "# GDKHQ D1-D3 Shadow — Báo cáo nghiệm thu",
        "",
        f"- Plan date: `{state['plan_date']}`",
        f"- Kết quả trace: `{status}`",
        f"- Promoted rollout: `{'CÓ' if state['promoted'] else 'KHÔNG'}`",
        f"- Trạng thái nghiệm thu: `{state['acceptance_status']}`",
        f"- Trace: `{state['trace_path']}`",
        f"- Báo cáo: `{state['report_path']}`",
        f"- Báo cáo lúc: `{state['reported_at']}`",
    ]
    if state.get("watch"):
        lines += [f"- Watch: `{', '.join(state['watch'])}`"]
    if state.get("account_count") is not None:
        lines += [f"- Số account: `{state['account_count']}`"]
    if state.get("errors"):
        lines += ["", "## Lỗi / vi phạm", ""]
        lines += [f"- {error}" for error in state["errors"]]
    lines += ["", "## Hành động cần làm", ""]
    if state["acceptance_status"] == "FAILED_REVIEW_REQUIRED":
        lines.append("- Trace FAIL: giữ SHADOW_PENDING, xem log bên trên, sửa nguyên nhân rồi chạy lại.")
    elif state["acceptance_status"] == "PENDING_ACCEPTANCE":
        lines.append("- Trace PASS: chờ user nghiệm thu; xác nhận bằng command accept "
                     "hoặc trả lời thread vận hành.")
    else:
        lines.append(f"- Đã nghiệm thu bởi `{state.get('accepted_by')}` "
                     f"lúc `{state.get('accepted_at')}`.")
    return "\n".join(lines) + "\n"


def update_acceptance(plan_date, *, promoted=None, acceptance_status=None,
                      accepted_by=None, note=None, path=ACCEPTANCE_STATE_PATH):
    """Update the acceptance record for an existing report."""
    state = read_acceptance(path)
    if state.get("plan_date") != str(plan_date):
        raise ValueError(f"chưa có acceptance report cho {plan_date} tại {path}")
    if not state.get("trace_passed"):
        raise ValueError("không thể nghiệm thu/update một shadow trace FAIL")
    if promoted is not None:
        state["promoted"] = bool(promoted)
    if acceptance_status is not None:
        state["acceptance_status"] = acceptance_status
    if accepted_by:
        state["accepted_by"] = accepted_by
        state["accepted_at"] = _now_iso()
        state["acceptance_status"] = acceptance_status or "ACCEPTED"
    if note is not None:
        state["note"] = note
    _atomic_write_json(path, state)
    return state


def accept_shadow(plan_date, accepted_by, path=ACCEPTANCE_STATE_PATH,
                  rollout_path=STATE_PATH, note=None):
    """Sign off a passed shadow run and atomically enable the live marker.

    The caller performs the user nghiệm thu.  Until this succeeds, ``enabled()`` stays
    false and the per-ticker GDKHQ resolver keeps using ``pending_resolver``.
    """
    state = update_acceptance(plan_date, acceptance_status="ACCEPTED",
                              accepted_by=accepted_by, note=note, path=path)
    marker = read_state(rollout_path)
    if marker.get("trace_date") != str(plan_date):
        raise ValueError(f"chưa có shadow PASS marker cho {plan_date} tại {rollout_path}")
    if marker.get("status") == "enabled" and marker.get("acceptance_status") == "ACCEPTED":
        # Idempotent re-acceptance: keep the existing marker, refresh the report.
        state["promoted"] = True
        _atomic_write_json(path, state)
        _refresh_acceptance_report(state)
        return state
    if (marker.get("status") != "shadow_passed"
            or marker.get("shadow_passed") is not True
            or marker.get("acceptance_status") != "PENDING_ACCEPTANCE"):
        raise ValueError(f"marker {rollout_path} chưa ở trạng thái PENDING_ACCEPTANCE; "
                         "không thể bật live")
    marker.update({
        "status": "enabled",
        "acceptance_status": "ACCEPTED",
        "accepted_by": str(accepted_by),
        "accepted_at": state["accepted_at"],
        "enabled_at": _now_iso(),
    })
    if note is not None:
        marker["note"] = note
    _atomic_write_json(rollout_path, marker)
    state["promoted"] = True
    _atomic_write_json(path, state)
    _refresh_acceptance_report(state)
    return state


def record_shadow_pass(trace_path, trace_date, path=STATE_PATH, report_path=None,
                       acceptance_path=ACCEPTANCE_STATE_PATH):
    """Record a passed live shadow trace as PENDING_ACCEPTANCE without enabling live."""
    if not report_path:
        raise ValueError("Không thể ghi shadow PASS khi chưa có report acceptance")
    acceptance = read_acceptance(acceptance_path)
    if acceptance.get("plan_date") != str(trace_date):
        raise ValueError(f"acceptance report cho {trace_date} chưa có tại {acceptance_path}")
    if not acceptance.get("trace_passed"):
        raise ValueError("không thể ghi shadow PASS cho trace có kết quả FAIL")
    state = {
        "status": "shadow_passed",
        "shadow_passed": True,
        "trace_date": str(trace_date),
        "trace_path": os.path.abspath(trace_path),
        "report_path": os.path.abspath(report_path),
        "acceptance_path": os.path.abspath(acceptance_path),
        "acceptance_status": "PENDING_ACCEPTANCE",
        "accepted_by": None,
        "accepted_at": None,
        "approved_by": "user",
        "approved_decision": "one-session shadow then user acceptance before live enable",
        "recorded_at": _now_iso(),
    }
    _atomic_write_json(path, state)
    return state


def _refresh_acceptance_report(state):
    report_path = state.get("report_path")
    if not report_path:
        return
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(_render_report(state))
        f.flush()
        os.fsync(f.fileno())


def pending_resolver(_broker, ticker, session_date, **_kwargs):
    """Fail closed for an event ticker while the one-session shadow is still pending."""
    return {
        "ticker": str(ticker).upper(),
        "session_date": str(session_date),
        "ok": False,
        "gate": "ROLLOUT_PENDING",
        "ex_today": True,
        "reason": ("D1-D3 chưa qua live shadow trace đã được user duyệt; chặn RIÊNG lệnh mã "
                   "GDKHQ, không chặn các mã thường trong plan"),
    }
