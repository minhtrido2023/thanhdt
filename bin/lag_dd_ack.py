#!/usr/bin/env python3
"""Ghi/đọc xác nhận của USER cho gói DD LAG (`data/lag_dd/ack.json`) + trạng thái cổng DD theo mã.

Chỉ Mike ghi ack, và CHỈ khi user đã trả lời thật (coding_guidelines §20: decided_by="user" chỉ
khi user xác nhận real-time). lag_dd_pack.py KHÔNG BAO GIỜ ghi file này.

Mỗi mục: {ticker, release_date, decision: PROCEED|DROP|RESEARCH, decided_by: "user", at (ISO có
múi giờ), flags_hash (đóng dấu từ gói lúc ghi), note, source}. Append-only; mục MỚI NHẤT theo
(ticker, release_date) thắng. `flags_hash` khoá ack vào ĐÚNG bộ cờ user đã xem: gói sinh lại ra
bộ cờ khác ⇒ ack cũ KHÔNG còn hiệu lực (ACK_STALE) ⇒ phải hỏi lại.

    python3 bin/lag_dd_ack.py --ticker SCL --release-date 2026-10-19 --decision PROCEED \
        --decided-by user --at 2026-10-25T18:30:00+07:00 --note "..." --source "discord <link>"
    python3 bin/lag_dd_ack.py --show
    python3 bin/lag_dd_ack.py --gate SCL --plan-date 2026-10-26     # trạng thái cổng 1 mã

Mã thoát: 0 OK · 1 dữ liệu vào không hợp lệ / lỗi đọc-ghi.
"""
import argparse
import datetime as dt
import fcntl
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lag_dd_pack import dd_dir, write_atomic  # noqa: E402

DECISIONS = ("PROCEED", "DROP", "RESEARCH")
PACK_MAX_AGE_DAYS = 30     # gói có release_date cách plan_date > 30 ngày lịch ⇒ không phải sự kiện đang xét
_RE_PACK = re.compile(r"^([A-Z0-9]{3,5})_(\d{4}-\d{2}-\d{2}|NA)\.json$")
BUY_OK = ("CLEARED", "ACK_PROCEED")


def ack_path():
    return os.path.join(dd_dir(), "ack.json")


def load_acks(path=None):
    """list mục ack. File không có ⇒ []. File hỏng ⇒ raise (caller fail-closed)."""
    p = path or ack_path()
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as fh:
        d = json.load(fh)
    acks = d.get("acks") if isinstance(d, dict) else None
    if not isinstance(acks, list):
        raise ValueError(f"{p}: thiếu list 'acks'")
    return acks


def latest_ack(acks, ticker, release_date):
    hit = [a for a in acks if isinstance(a, dict) and str(a.get("ticker")).upper() == ticker
           and str(a.get("release_date")) == str(release_date)]
    return hit[-1] if hit else None


def _read_pack(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def find_pack(ticker, plan_date, directory=None):
    """(path|None, lý do). Gói release_date ≤ plan_date, trong PACK_MAX_AGE_DAYS, mới nhất."""
    d0 = dt.date.fromisoformat(str(plan_date)[:10])
    best, na = None, None
    for p in glob.glob(os.path.join(directory or dd_dir(), f"{ticker}_*.json")):
        m = _RE_PACK.match(os.path.basename(p))
        if not m or m.group(1) != ticker:
            continue
        if m.group(2) == "NA":
            na = p
            continue
        rel = dt.date.fromisoformat(m.group(2))
        if rel <= d0 and (d0 - rel).days <= PACK_MAX_AGE_DAYS and (best is None or rel > best[0]):
            best = (rel, p)
    if best:
        return best[1], ""
    if na:
        return na, "chỉ có gói release=NA"
    return None, f"không có data/lag_dd/{ticker}_<release>.json với release ≤ {plan_date} trong {PACK_MAX_AGE_DAYS} ngày"


def dd_gate(ticker, plan_date, directory=None, acks=None):
    """Trạng thái cổng DD của 1 mã cho plan_date. KHÔNG raise.

    state ∈ CLEARED | ACK_PROCEED (được mua) · FLAG_NO_ACK | ACK_DROP | ACK_RESEARCH | ACK_STALE |
    ACK_NOT_USER | NO_PACK | PACK_UNREADABLE | ACK_UNREADABLE (KHÔNG được mua).
    """
    t = str(ticker or "").strip().upper()
    out = {"ticker": t, "plan_date": str(plan_date), "state": None, "pack": None,
           "release_date": None, "status": None, "flags": [], "ack": None, "evidence": ""}
    try:
        path, why = find_pack(t, plan_date, directory)
    except (ValueError, OSError) as e:
        path, why = None, f"{type(e).__name__}: {e}"
    if not path:
        out.update(state="NO_PACK", evidence=why)
        return out
    out["pack"] = path
    try:
        pk = _read_pack(path)
        status, fl, rel, fh = pk["status"], pk.get("flags") or [], pk.get("release_date"), pk["flags_hash"]
    except (OSError, ValueError, KeyError, TypeError) as e:
        out.update(state="PACK_UNREADABLE", evidence=f"{os.path.basename(path)}: {type(e).__name__}: {e}")
        return out
    out.update(release_date=rel, status=status, flags=[f.get("code") for f in fl if isinstance(f, dict)])
    if status == "CLEARED" and not fl:
        out.update(state="CLEARED", evidence=f"{os.path.basename(path)} CLEARED (0 cờ)")
        return out
    try:
        acks = load_acks(os.path.join(directory, "ack.json") if directory else None) if acks is None else acks
    except (OSError, ValueError) as e:
        out.update(state="ACK_UNREADABLE", evidence=f"ack.json: {type(e).__name__}: {e}")
        return out
    a = latest_ack(acks, t, rel)
    out["ack"] = a
    codes = ",".join(out["flags"]) or "-"
    if not a:
        out.update(state="FLAG_NO_ACK", evidence=f"{os.path.basename(path)} FLAG [{codes}], user chưa trả lời")
    elif a.get("decided_by") != "user":
        out.update(state="ACK_NOT_USER", evidence=f"ack decided_by={a.get('decided_by')!r} ≠ 'user'")
    elif a.get("flags_hash") != fh:
        out.update(state="ACK_STALE", evidence=f"ack {a.get('decision')} lúc {a.get('at')} cho bộ cờ "
                                               f"{a.get('flags_hash')} ≠ gói hiện tại {fh} [{codes}]")
    elif a.get("decision") == "PROCEED":
        out.update(state="ACK_PROCEED", evidence=f"user PROCEED lúc {a.get('at')} dù cờ [{codes}]")
    elif a.get("decision") in ("DROP", "RESEARCH"):
        out.update(state=f"ACK_{a['decision']}", evidence=f"user {a['decision']} lúc {a.get('at')} [{codes}]")
    else:
        out.update(state="ACK_NOT_USER", evidence=f"ack decision lạ {a.get('decision')!r}")
    return out


def _parse_at(s):
    v = dt.datetime.fromisoformat(str(s))
    if v.tzinfo is None:
        raise ValueError("--at phải có múi giờ (vd 2026-10-25T18:30:00+07:00)")
    return v


def record(ticker, release_date, decision, decided_by, at, note="", source="", directory=None):
    """Validate + append 1 ack. Trả mục đã ghi. Raise ValueError khi không hợp lệ."""
    t = str(ticker).strip().upper()
    if decision not in DECISIONS:
        raise ValueError(f"decision phải ∈ {DECISIONS}, nhận {decision!r}")
    if decided_by != "user":
        raise ValueError("decided_by phải là 'user' — ack chỉ ghi khi USER đã trả lời thật (§20)")
    at_v = _parse_at(at)
    dt.date.fromisoformat(str(release_date))
    dd = directory or dd_dir()
    pack_p = os.path.join(dd, f"{t}_{release_date}.json")
    try:
        pk = _read_pack(pack_p)
    except (OSError, ValueError) as e:
        raise ValueError(f"không đọc được gói {pack_p}: {e} — ack phải gắn với gói DD có thật")
    if pk.get("ticker") != t or str(pk.get("release_date")) != str(release_date):
        raise ValueError(f"gói {pack_p} ticker/release không khớp ({pk.get('ticker')}, {pk.get('release_date')})")
    entry = {"ticker": t, "release_date": str(release_date), "decision": decision,
             "decided_by": "user", "at": at_v.isoformat(), "flags_hash": pk.get("flags_hash"),
             "flags": [f.get("code") for f in pk.get("flags") or []], "pack_status": pk.get("status"),
             "note": note, "source": source,
             "recorded_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    ap = os.path.join(dd, "ack.json")
    os.makedirs(dd, exist_ok=True)
    with open(ap + ".lock", "a") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        acks = load_acks(ap)
        write_atomic(ap, {"acks": acks + [entry]})
    return entry


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ticker")
    ap.add_argument("--release-date")
    ap.add_argument("--decision", choices=DECISIONS)
    ap.add_argument("--decided-by")
    ap.add_argument("--at", help="ISO có múi giờ: lúc user trả lời")
    ap.add_argument("--note", default="")
    ap.add_argument("--source", default="", help="link/trích tin nhắn user")
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--gate", metavar="TICKER")
    ap.add_argument("--plan-date")
    a = ap.parse_args(argv)
    try:
        if a.show:
            print(json.dumps(load_acks(), ensure_ascii=False, indent=1))
            return 0
        if a.gate:
            if not a.plan_date:
                ap.error("--gate cần --plan-date")
            print(json.dumps(dd_gate(a.gate, a.plan_date), ensure_ascii=False, indent=1, default=str))
            return 0
        missing = [k for k in ("ticker", "release_date", "decision", "decided_by", "at") if not getattr(a, k)]
        if missing:
            ap.error("thiếu " + ", ".join("--" + m.replace("_", "-") for m in missing))
        e = record(a.ticker, a.release_date, a.decision, a.decided_by, a.at, a.note, a.source)
    except (ValueError, OSError) as e:
        print(f"❌ {e}", file=sys.stderr)
        return 1
    print(json.dumps(e, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
