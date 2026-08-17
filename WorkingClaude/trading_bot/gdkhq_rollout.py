# -*- coding: utf-8 -*-
"""Rollout state for the GDKHQ D1-D3 execution gate.

Until one live, read-only broker trace passes, event-day orders are blocked per ticker.  Normal
orders remain untouched.  The state file is deliberately runtime data (gitignored), written only
by the explicit shadow command after every required live check succeeds.
"""
import datetime as dt
import json
import os
import tempfile


WC_ROOT = os.path.abspath(os.environ.get("TRADING_BOT_RUNTIME_ROOT") or
                          os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATE_PATH = os.path.join(WC_ROOT, "data", "gdkhq_d1d3_rollout.json")


def read_state(path=STATE_PATH):
    try:
        with open(path, encoding="utf-8") as f:
            value = json.load(f)
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError, TypeError):
        return {}


def enabled(path=STATE_PATH):
    state = read_state(path)
    return state.get("status") == "enabled" and state.get("shadow_passed") is True


def mark_enabled(trace_path, trace_date, path=STATE_PATH):
    """Atomically promote D1-D3 after a successful live shadow trace."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    state = {
        "status": "enabled",
        "shadow_passed": True,
        "trace_date": str(trace_date),
        "trace_path": os.path.abspath(trace_path),
        "approved_by": "user",
        "approved_decision": "dry-run one session, then rollout immediately on pass",
        "enabled_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
    }
    fd, tmp = tempfile.mkstemp(prefix=".gdkhq_rollout_", suffix=".json",
                               dir=os.path.dirname(path))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
    return state


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
