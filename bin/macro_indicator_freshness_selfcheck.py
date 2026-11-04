#!/usr/bin/env python3
"""Selfcheck cho macro_indicator_freshness.py + dây nối trong bq_freshness_check.sh.
Chạy dưới nhiều TZ (env -u TZ, America/Los_Angeles) vì 'hôm nay' phải neo ICT (§16)."""
import os, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "macro_indicator_freshness.py"
SH = HERE / "bq_freshness_check.sh"
DAILY = ["us_sp500", "us_bond_10y", "us_dxy", "vn_usdvnd", "vn_bond_10y", "cn_usdcny"]
F = 0


def run(csv_text, today, tz=None, path_prefix=None):
    env = {k: v for k, v in os.environ.items() if k not in ("TZ", "MACRO_FRESH_CSV", "MACRO_FRESH_TODAY")}
    if tz: env["TZ"] = tz
    if today: env["MACRO_FRESH_TODAY"] = today
    if csv_text is not None:
        d = tempfile.mkdtemp(); p = Path(d) / "x.csv"; p.write_text(csv_text); env["MACRO_FRESH_CSV"] = str(p)
    if path_prefix: env["PATH"] = path_prefix + ":" + env["PATH"]
    r = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, env=env)
    return r.returncode, r.stdout


def ok(name, cond, extra=""):
    global F
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  " + extra)); F += 0 if cond else 1


def csv(over=None, drop=()):
    m = {s: "2026-11-04" for s in DAILY}; m.update(over or {})
    return "series_key,mx\n" + "".join("%s,%s\n" % (k, v) for k, v in m.items() if k not in drop)


for tz in (None, "America/Los_Angeles", "UTC"):
    t = tz or "unset"
    rc, o = run(csv(), "2026-11-05", tz); ok("fresh→OK rc0 [%s]" % t, rc == 0 and o.startswith("OK   macro_indicator"), o)
    rc, o = run(csv({"us_sp500": "2026-11-01"}), "2026-11-05", tz)  # lag 4
    ok("stale lag4→WARN [%s]" % t, rc == 1 and "us_sp500" in o and o.startswith("WARN"), o)
    rc, o = run(csv({"us_sp500": "2026-11-02"}), "2026-11-05", tz)  # lag 3 = biên, vẫn OK
    ok("boundary lag3→OK [%s]" % t, rc == 0, o)
rc, o = run(csv(drop=("vn_bond_10y",)), "2026-11-05"); ok("thiếu series→WARN", rc == 1 and "vn_bond_10y" in o and "KHÔNG CÓ" in o, o)
rc, o = run("", "2026-11-05"); ok("output rỗng→WARN không phải OK", rc == 1 and o.startswith("WARN") and "header" in o, o)
rc, o = run(csv({"us_dxy": "garbage"}), "2026-11-05"); ok("ngày rác→WARN", rc == 1 and "us_dxy" in o, o)
# truy vấn lỗi: bq giả trả rc=1 + stderr; bằng chứng phải được trích nguyên văn (§29)
d = tempfile.mkdtemp(); b = Path(d) / "bq"; b.write_text("#!/bin/sh\necho 'Access Denied: boom123' >&2\nexit 1\n"); b.chmod(0o755)
rc, o = run(None, "2026-11-05", path_prefix=d); ok("bq lỗi→WARN trích nguyên văn", rc == 1 and "boom123" in o and "KHÔNG phải kết luận" in o, o)
# không có biến test: 'hôm nay' mặc định phải là ICT (không crash dưới TZ lạ)
rc, o = run(csv(), None, "America/Los_Angeles"); ok("today mặc định ICT chạy được (rc 0|1, có dòng OK/WARN)", rc in (0, 1) and o.split(" ")[0] in ("OK", "WARN"), o)
# dây nối trong bash
s = SH.read_text()
ok("bash gọi macro_indicator_freshness.py", "bin/macro_indicator_freshness.py" in s)
ok("bash WARN khi rc≠0 HOẶC thiếu dòng OK", "_mi_rc\" -ne 0 ] || ! printf" in s and "WARNED=$((WARNED + 1))" in s[s.index("_mi_out="):s.index("_mi_out=") + 900])
ok("không đụng FAILED trong khối macro", "FAILED=1" not in s[s.index("_mi_out="):s.index("_mi_out=") + 900])
print("FAILS=%d" % F); sys.exit(1 if F else 0)
