#!/usr/bin/env python3
"""MỘT định nghĩa "plan có" cho tooling điều phối (arch-review vòng 2 việc B, 25/11/2026 — trước đây
4 bản lệch nhau: bq_freshness_check.sh chỉ `isfile`, plan_gate_recovery.plan_ok, daily_decision_topic,
late_plan_catchup.check_status).

classify(path, date) → "MISSING" | "INVALID" | "OK"
  OK      = JSON object, plan_date (hoặc date) == date, orders là list (HOLD = list rỗng vẫn OK).
  INVALID = file có nhưng hỏng/sai ngày/orders không phải list — KHÔNG phải "có plan", nhưng cũng KHÔNG
            được coi là "vắng" để ghi đè (có thể là bản người đang sửa / đã duyệt hỏng — cần người xem).
approval(wc, acct, date) → "APPROVED" | "NEEDS_APPROVAL" | "HOLD" | "NOT_REQUIRED" | "ERROR: …"
  dùng ĐÚNG trading_bot.plan.load_plan + approval_block_reason (gate của executor) — không tự đoán.

CLI (bash caller):
  plan_presence.py --date D [--wc WC] --list not-ok   # account live KHÔNG OK (MISSING+INVALID)
  plan_presence.py --date D [--wc WC] --list absent   # account live KHÔNG CÓ FILE (an toàn để lập mới)
  plan_presence.py --date D [--plan-dir DIR] --classify ACCT   # in MISSING|INVALID|OK
  In 1 dòng (account cách nhau dấu cách, có thể rỗng). rc 0 · rc 3 không đọc được account live/lỗi.
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

WC_DEFAULT = os.environ.get("WORKDIR_8L") or str(Path(__file__).resolve().parent.parent.parent)


def plan_path(wc, acct, date, plan_dir=None):
    return Path(plan_dir or Path(wc) / "data" / "trade_plans") / f"plan_{acct}_{date}.json"


def classify(path, date):
    try:
        j = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return "MISSING"
    except (OSError, ValueError):
        return "INVALID"
    if not isinstance(j, dict) or str(j.get("plan_date", j.get("date"))) != str(date) \
            or not isinstance(j.get("orders"), list):
        return "INVALID"
    return "OK"


def live_accounts(wc=WC_DEFAULT):
    r = subprocess.run([sys.executable, "-c", "from trading_bot.config import live_dnse_labels;"
                        "print(' '.join(live_dnse_labels()))"], cwd=str(wc), capture_output=True, text=True, timeout=60)
    labs = r.stdout.split()
    if r.returncode != 0 or not labs:
        raise RuntimeError(f"không đọc được account live (rc={r.returncode}): {(r.stderr or r.stdout).strip()[-200:]}")
    return labs


def not_ok(wc, date, accts=None):
    return [a for a in (accts or live_accounts(wc)) if classify(plan_path(wc, a, date), date) != "OK"]


_APPROVAL_CODE = r"""
import sys
from trading_bot.plan import load_plan, approval_block_reason
p = load_plan(sys.argv[2], sys.argv[1])
if p is None:
    print("ERROR: không có plan"); sys.exit(0)
r = approval_block_reason(p)
req = p.requires_user_approval
if isinstance(req, str):
    req = req.strip().lower() not in ("", "false", "no", "0", "none")
print("NEEDS_APPROVAL" if r else ("HOLD" if not p.orders else ("APPROVED" if req else "NOT_REQUIRED")))
"""


def approval(wc, acct, date):
    """Trạng thái duyệt theo đúng gate executor (bot_execute.py gọi approval_block_reason)."""
    try:
        r = subprocess.run([sys.executable, "-c", _APPROVAL_CODE, acct, str(date)], cwd=str(wc),
                           capture_output=True, text=True, timeout=60)
    except Exception as exc:  # noqa: BLE001
        return f"ERROR: {type(exc).__name__}"
    out = r.stdout.strip().splitlines()
    if r.returncode != 0 or not out:
        return f"ERROR: {(r.stderr or r.stdout).strip().splitlines()[-1:] or ['rc=%d' % r.returncode]}"
    return out[-1]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--date", required=True)
    ap.add_argument("--wc", default=WC_DEFAULT)
    ap.add_argument("--plan-dir")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--list", choices=["not-ok", "absent"])
    g.add_argument("--classify", metavar="ACCT")
    a = ap.parse_args(argv)
    try:
        if a.classify:
            print(classify(plan_path(a.wc, a.classify, a.date, a.plan_dir), a.date))
            return 0
        cls = {x: classify(plan_path(a.wc, x, a.date, a.plan_dir), a.date) for x in live_accounts(a.wc)}
        sel = [x for x, c in cls.items() if (c == "MISSING" if a.list == "absent" else c != "OK")]
        print(" ".join(sel))
        return 0
    except Exception as exc:  # noqa: BLE001 — bash caller cần rc rõ, không traceback
        print(f"plan_presence: ERROR {type(exc).__name__}: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
