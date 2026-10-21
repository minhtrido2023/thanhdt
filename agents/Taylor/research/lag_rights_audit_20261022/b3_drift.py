#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B2b — plan_position_drift_check.py (REPLAY --sim-live-at, --no-bus --no-state) trên dnse_raw giả
3 ngày: (D1) giá tham chiếu SCL hạ quanh GDKHQ quyền, (D2) user nộp 62,5tr (vị thế không đổi),
(D3) 5.000cp quyền vào openQuantity tối hôm credit. Sandbox; MIKE_DRIFT_SELFCHECK=1 + mọi dir
override trỏ vào sandbox (paths() TỪ CHỐI nếu state/append_event trỏ production)."""
import contextlib
import io
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b3_common as C  # noqa: E402

td = tempfile.mkdtemp(prefix="lag_rights_drift_")
EX, PL, ST = (os.path.join(td, x) for x in ("exec", "plans", "state"))
for d in (EX, PL, ST):
    os.makedirs(d)
fake_append = os.path.join(td, "append_event.sh")
open(fake_append, "w").write("#!/bin/sh\nexit 0\n")
os.chmod(fake_append, 0o755)
os.environ.update({"MIKE_DRIFT_SELFCHECK": "1", "MIKE_DRIFT_EXEC_DIR": EX,
                   "MIKE_DRIFT_PLAN_DIR": PL, "MIKE_DRIFT_STATE_DIR": ST,
                   "MIKE_DRIFT_APPEND_EVENT": fake_append})
import plan_position_drift_check as pdc  # noqa: E402


def rows(scl_open, scl_trade, scl_mp, mod_utc):
    out = [{"accountNo": C.ACCOUNT_NO, "symbol": tk, "openQuantity": q, "tradeQuantity": q,
            "marketPrice": px, "status": "OPEN", "modifiedDate": mod_utc}
           for tk, (q, px) in C.PARK.items()]
    out.append({"accountNo": C.ACCOUNT_NO, "symbol": "SCL", "openQuantity": scl_open,
                "tradeQuantity": scl_trade, "marketPrice": scl_mp, "status": "OPEN",
                "modifiedDate": mod_utc})
    return out


def day(date, morning, plan, now):
    """morning/plan/now = (open, trade, mp) tại 04:50 / 19:05 / 20:45 ICT."""
    prev_batch = f"{date}T00:00:00Z"          # 07:00 ICT — trước 15:00 ⇒ 'chưa qua batch'
    batch = f"{date}T12:00:00Z"               # 19:00 ICT — đã qua batch hôm nay
    recs = [(f"{date}T04:50:00", rows(*morning, prev_batch)),
            (f"{date}T19:05:00", rows(*plan, batch)),
            (f"{date}T20:45:00", rows(*now, batch))]
    with open(os.path.join(EX, f"dnse_raw_{date}.jsonl"), "w") as f:
        for ts, r in recs:
            f.write(json.dumps({"ts": ts, "kind": "positions", "account_no": C.ACCOUNT_NO,
                                "payload": {"positions": r}}) + "\n")
            f.write(json.dumps({"ts": ts, "kind": "positions", "account_no": C.OTHER_NO,
                                "payload": {"positions": [{"accountNo": C.OTHER_NO,
                                                           "symbol": "SCL", "openQuantity": 1}]}})
                    + "\n")
        f.write(json.dumps({"ts": f"{date}T20:46:00", "kind": "orders",
                            "account_no": C.ACCOUNT_NO, "payload": {"orders": []}}) + "\n")


CASES = [
    ("D1 tối trước GDKHQ: batch DNSE hạ marketPrice SCL 30.000→25.400 sau 19:05", "2026-11-06",
     (14_000, 14_000, 30_000), (14_000, 14_000, 30_000), (14_000, 14_000, 25_400)),
    ("D2 ngày user nộp tiền quyền (vị thế không đổi)", "2026-11-16",
     (14_000, 14_000, 25_400), (14_000, 14_000, 25_400), (14_000, 14_000, 25_400)),
    ("D3 tối credit 5.000cp quyền (sau 19:05, chưa niêm yết)", "2026-12-03",
     (14_000, 14_000, 25_400), (14_000, 14_000, 25_400), (19_000, 14_000, 25_400)),
    ("D3b credit TRƯỚC 18:50 (bản 19:05 đã thấy 19.000)", "2026-12-04",
     (14_000, 14_000, 25_400), (19_000, 14_000, 25_400), (19_000, 14_000, 25_400)),
]
for name, d, m, p, n in CASES:
    day(d, m, p, n)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = pdc.main(["--account", C.ACCOUNT, "--account-no", C.ACCOUNT_NO, "--date", d,
                       "--sim-live-at", "20:50", "--no-bus", "--no-state"])
    print(f"\n== {name} ({d}) rc={rc}")
    print("   " + buf.getvalue().strip().replace("\n", "\n   ")[:900])
print(f"\nsandbox={td}  (state dir rỗng? {os.listdir(ST) == []})")
