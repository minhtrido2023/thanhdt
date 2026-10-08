#!/usr/bin/env python3
"""job_telemetry.py — token/turn/cost THEO JOB cho dispatch.sh (2026-10-08).

dispatch.sh truyen `--session-id <uuid>` cho moi lan chay claude (moi attempt 1 uuid), roi SAU
KHI trang thai job da chot (done/failed/timeout/pending-resume) goi:

  job_telemetry.py <uuid>[,<uuid>...]      -> in `key=value` tung dong de JSET len record

Nguon = transcript ~/.claude/projects/*/<uuid>.jsonl (hoac $CLAUDE_CONFIG_DIR/projects): dong
`cost-state` (CLI tu ghi khi phien ket thuc: totalCostUSD + modelUsage, da gom subagent); thieu
(phien bi kill truoc khi kip ghi) => cong usage tung assistant message, KHONG co cost.

KEY RA = WHITELIST (OUT_KEYS), gia tri da kiem kieu: so nguyen >=0 cho token/turn, so thuc >=0
cho cost, uuid chu thuong (noi dau phay) cho session_id. dispatch.sh kiem LAI bang regex truoc khi
JSET — 2 lop, vi day la duong T0 (moi dispatch) ma record job la nguon cua jobs.sh/watchdog.

total_cost_usd = tong cost cua cac phien CO cost-state => la CAN DUOI khi 1 attempt bi kill (vd
timeout roi retry). Khong co phien nao co cost => khong in key nay. Khong tim thay transcript nao
=> chi in session_id (report dem la "thieu").

FAIL-OPEN tuyet doi: moi loi => in rong (hoac phan da chac chan), exit 0. Telemetry khong bao gio
duoc phep lam hong 1 job.
"""
import glob
import json
import math
import os
import re
import sys

INT_FIELDS = ("num_turns", "input_tokens", "cache_read_tokens", "cache_creation_tokens", "output_tokens")
OUT_KEYS = INT_FIELDS + ("total_cost_usd", "session_id")
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
MAX_SESSIONS = 10  # khop regex phia dispatch.sh ({0,9} uuid phu)


def projects_root():
    base = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude")
    return os.path.join(base, "projects")


def to_int(v):
    """So nguyen >=0; bool/so am/rac => 0."""
    if isinstance(v, bool):
        return 0
    try:
        n = int(v)
    except (TypeError, ValueError):
        return 0
    return n if n >= 0 else 0


def to_cost(v):
    """So thuc huu han >=0, nguoc lai None."""
    if isinstance(v, bool):
        return None
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) and x >= 0 else None


def session_telemetry(session_id, root=None):
    """Token/turn/cost cua MOT phien. {} neu uuid sai / khong co transcript / khong doc duoc gi.

    num_turns = so assistant message (API round-trip) cua LUONG CHINH, dedupe theo message.id
    (roi requestId, roi uuid). Token fallback (khong co cost-state) cong CA sidechain (subagent)
    de cung pham vi voi cost-state; turn thi chi luong chinh.
    """
    if not UUID_RE.match(session_id or ""):
        return {}
    paths = glob.glob(os.path.join(root or projects_root(), "*", session_id + ".jsonl"))
    if not paths:
        return {}
    path = max(paths, key=os.path.getmtime)
    cost_state = None
    main_ids, usages = set(), {}
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if '"cost-state"' not in line and '"usage"' not in line:
                continue
            try:
                ev = json.loads(line)
            except Exception:
                continue
            if not isinstance(ev, dict):
                continue
            if ev.get("type") == "cost-state":
                cost_state = ev
                continue
            if ev.get("type") != "assistant":
                continue
            msg = ev.get("message")
            usage = msg.get("usage") if isinstance(msg, dict) else None
            if not isinstance(usage, dict):
                continue
            mid = msg.get("id") or ev.get("requestId") or ev.get("uuid")
            if not mid:
                continue
            usages[mid] = usage
            if not ev.get("isSidechain"):
                main_ids.add(mid)
    if not usages and cost_state is None:
        return {}
    out = {"num_turns": len(main_ids)}
    mu = cost_state.get("modelUsage") if isinstance(cost_state, dict) else None
    cost = to_cost(cost_state.get("totalCostUSD")) if isinstance(cost_state, dict) else None
    if isinstance(mu, dict) and mu and cost is not None:
        ms = [m for m in mu.values() if isinstance(m, dict)]
        out["input_tokens"] = sum(to_int(m.get("inputTokens")) for m in ms)
        out["cache_read_tokens"] = sum(to_int(m.get("cacheReadInputTokens")) for m in ms)
        out["cache_creation_tokens"] = sum(to_int(m.get("cacheCreationInputTokens")) for m in ms)
        out["output_tokens"] = sum(to_int(m.get("outputTokens")) for m in ms)
        out["total_cost_usd"] = cost
    else:
        us = list(usages.values())
        out["input_tokens"] = sum(to_int(u.get("input_tokens")) for u in us)
        out["cache_read_tokens"] = sum(to_int(u.get("cache_read_input_tokens")) for u in us)
        out["cache_creation_tokens"] = sum(to_int(u.get("cache_creation_input_tokens")) for u in us)
        out["output_tokens"] = sum(to_int(u.get("output_tokens")) for u in us)
    return out


def job_telemetry(session_ids, root=None):
    """Tong qua MOI attempt cua job. Tinh lai tu dau moi lan goi => idempotent (goi lai = ghi de
    cung gia tri). Chi tra key trong OUT_KEYS."""
    sids = []
    for s in session_ids:
        if UUID_RE.match(s or "") and s not in sids:
            sids.append(s)
    sids = sids[:MAX_SESSIONS]
    if not sids:
        return {}
    out = {"session_id": ",".join(sids)}
    found = [t for t in (session_telemetry(s, root) for s in sids) if t]
    if not found:
        return out
    for k in INT_FIELDS:
        out[k] = sum(t[k] for t in found)
    costs = [t["total_cost_usd"] for t in found if "total_cost_usd" in t]
    if costs:
        out["total_cost_usd"] = round(sum(costs), 6)
    return {k: v for k, v in out.items() if k in OUT_KEYS}


def fmt(v):
    if isinstance(v, float):
        s = f"{v:.6f}".rstrip("0").rstrip(".")
        return s or "0"
    return str(v)


def main(argv):
    try:
        if len(argv) != 1:
            return 0
        for k, v in job_telemetry(argv[0].split(",")).items():
            print(f"{k}={fmt(v)}")
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
