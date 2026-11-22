#!/usr/bin/env python3
"""Selfcheck cho quiet_ok + ngưỡng weekday của cron_health_check.py (2026-11-22)."""
import importlib.util, json, os, sys, tempfile, time
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("chc", os.path.join(HERE, "cron_health_check.py"))
chc = importlib.util.module_from_spec(spec); spec.loader.exec_module(chc)
fails = []
def check(name, cond):
    print(("PASS  " if cond else "FAIL  ") + name)
    if not cond: fails.append(name)

# 1. ngưỡng: weekday-only frequent ≠ frequent 24/7
check("frequent 24/7 giữ 2h", chc.cadence_bucket("*/5 * * * *") == ("frequent", 7200))
b, t = chc.cadence_bucket("*/5 2-7 * * 1-5")
check("frequent chỉ ngày làm việc ⇒ 3,5 ngày", b == "frequent_wd" and t == int(3.5 * 86400))
check("daily/weekly/monthly không đổi",
      chc.cadence_bucket("0 1 * * *")[0] == "daily" and chc.cadence_bucket("0 1 * * 6")[0] == "weekly"
      and chc.cadence_bucket("0 1 5 * *")[0] == "monthly")

# 2. quiet_ok: cần reason, chưa hết hạn
now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(chc.NOW - 3600))
old = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(chc.NOW - 40 * 86400))
data = {"quiet_ok": [
    {"script": "a.sh", "reason": "ok", "acked_at": now, "expires_days": 30},
    {"script": "b.sh", "acked_at": now, "expires_days": 30},                       # thiếu reason
    {"script": "c.sh", "reason": "ok", "acked_at": old, "expires_days": 30},       # hết hạn
    {"reason": "ok", "acked_at": now},                                              # không khoá khớp
    {"script": "for_each.sh", "log": "egg.log", "reason": "ok", "acked_at": now},
]}
with tempfile.TemporaryDirectory() as d:
    p = os.path.join(d, "ack.json"); json.dump(data, open(p, "w"))
    chc.ACK_PATH = p
    q = chc.load_quiet_ok()
    check("giữ mục hợp lệ, loại thiếu-reason + hết hạn", len(q) == 3)
    check("khớp theo script", chc.find_quiet_ok("/x/a.sh", "* * * * *", "/l/a.log", q) is not None)
    check("thiếu reason ⇒ không khớp", chc.find_quiet_ok("/x/b.sh", "", "", q) is None)
    check("hết hạn ⇒ không khớp", chc.find_quiet_ok("/x/c.sh", "", "", q) is None)
    check("mục không khoá ⇒ không khớp bừa", chc.find_quiet_ok("/x/zzz.sh", "", "", q) is None)
    check("script chung phải khớp thêm log: sai log ⇒ không",
          chc.find_quiet_ok("/x/for_each.sh", "", "/l/other.log", q) is None)
    check("script chung + đúng log ⇒ khớp",
          chc.find_quiet_ok("/x/for_each.sh", "", "/l/egg.log", q) is not None)
    chc.ACK_PATH = os.path.join(d, "missing.json")
    check("file ack thiếu ⇒ [] (fail-open)", chc.load_quiet_ok() == [])
sys.exit(1 if fails else 0)
