#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck §16: `bull_div_boost.detect_today` nhánh no_data phải ghi ngày theo ICT, không theo TZ host.

Đồng hồ giả: 2026-11-22T18:00Z = 01:00 ICT 23/11. Host TZ=America/Los_Angeles (ngày địa phương 22/11).
Kỳ vọng 'date' = '2026-11-23'. Mutant: đổi về datetime.today() ⇒ FAIL.
Chạy:  python3 bull_div_boost_tz_selfcheck.py ;  cd /tmp && env -u TZ python3 <path>
"""
import os, sys, time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bull_div_boost as B   # noqa: E402

_FIXED = datetime(2026, 11, 22, 18, 0, tzinfo=timezone.utc)


class FD(datetime):
    @classmethod
    def now(cls, tz=None):
        return _FIXED.astimezone(tz) if tz else _FIXED.astimezone().replace(tzinfo=None)

    @classmethod
    def today(cls):
        return cls.now()


def run(src_patch=None):
    os.environ["TZ"] = "America/Los_Angeles"; time.tzset()
    B.datetime = FD
    B._q = lambda sql: ""          # => no_data
    if src_patch:
        ns = dict(B.__dict__)
        src = open(os.path.join(HERE, "bull_div_boost.py"), encoding="utf-8").read().replace(*src_patch)
        exec(compile(src, "bull_div_boost_mut.py", "exec"), ns)
        ns["datetime"] = FD; ns["_q"] = lambda sql: ""
        return ns["detect_today"]()
    return B.detect_today()

ok = True
r = run()
c1 = r.get("date") == "2026-11-23" and r.get("error") == "no_data"
print(("  ✓ " if c1 else "  ✗ ") + f"REAL: date={r.get('date')} (kỳ vọng 2026-11-23)"); ok &= c1
m = run(("datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).date()), 'error'", "datetime.today().date()), 'error'"))
c2 = m.get("date") != "2026-11-23"
print(("  ✓ " if c2 else "  ✗ ") + f"MUTANT (today()) bị bắt: date={m.get('date')}"); ok &= c2
print("PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
