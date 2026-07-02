# -*- coding: utf-8 -*-
"""Regression self-check for the per-(account, plan_date) execution lock.

Incident 2026-07-02: bot_heartbeat.sh's autoheal fired at 09:00:01 ICT (before
the scheduled 09:05 cron), launching a SECOND bot_execute.py for SpaceX while
the first was already running. Neither process knew about the other (separate
memory, separate participation-quota dict, cash-check against a broker
`availableCash` figure that didn't reflect the other's concurrent spend) — both
independently filled the ENTIRE 11-order plan, buying every ticker at exactly
2x the intended quantity (~456M -> ~912M VND) and pushing cash to ~-405M VND.

Fix: `_acquire_account_lock()` in bot_execute.py takes an exclusive fcntl flock
on `data/execution_logs/exec_{label}_{plan_date}.lock` before connecting the
broker for that account; a second process for the same (account, date) fails
to acquire it and skips that account instead of running a duplicate session.
flock is held by the OS per open-file-description and is released
automatically on process exit/crash, so a legitimate restart-after-crash still
works normally.

Run: python concurrent_lock_selfcheck.py   (exit 0 = all pass)
"""
import fcntl
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bot_execute import _acquire_account_lock, _LOCK_HANDLES  # noqa: E402
from trading_bot.config import EXEC_DIR  # noqa: E402

TAG = "selfcheck-lock"
for f in glob.glob(os.path.join(EXEC_DIR, f"exec_{TAG}*_.lock")):
    os.remove(f)

fails = []
def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)

# A. First process for (account, date) acquires the lock.
r1 = _acquire_account_lock(TAG, "2099-01-01")
check("A1 first acquire succeeds", r1 is True)

# B. A second, independent process (separate fd, simulating a second OS process
#    since flock is per-open-file-description) for the SAME account+date must be blocked.
path = os.path.join(EXEC_DIR, f"exec_{TAG}_2099-01-01.lock")
f2 = open(path, "a")
blocked = False
try:
    fcntl.flock(f2.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
except OSError:
    blocked = True
finally:
    f2.close()
check("B1 concurrent second process for same account+date is blocked", blocked)

# C. Different plan_date for the SAME account is an independent lock (no false blocking
#    across days — e.g. today's run must never be blocked by yesterday's stale process).
r3 = _acquire_account_lock(TAG, "2099-01-02")
check("C1 different plan_date is independent (not blocked)", r3 is True)

# D. Different account, SAME date is also independent (paper vs live must not block each other).
r4 = _acquire_account_lock(TAG + "-other", "2099-01-01")
check("D1 different account label is independent (not blocked)", r4 is True)

# E. After the holder releases (process exit == fd close), a fresh process can acquire it —
#    this is what makes legitimate restart-after-crash still work (OS auto-releases on exit).
_LOCK_HANDLES[0].close()
_LOCK_HANDLES.pop(0)
f5 = open(path, "a")
reacquired = False
try:
    fcntl.flock(f5.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    reacquired = True
except OSError:
    pass
finally:
    f5.close()
check("E1 lock releases on process exit -> legitimate restart can re-acquire", reacquired)

for h in _LOCK_HANDLES:
    h.close()
for f in glob.glob(os.path.join(EXEC_DIR, f"exec_{TAG}*.lock")):
    os.remove(f)

print()
if fails:
    print(f"FAILED {len(fails)} check(s): {fails}")
    sys.exit(1)
print("ALL CHECKS PASSED — concurrent same-account double-run is blocked;"
      " different account/date unaffected; crash-restart still works.")
sys.exit(0)
