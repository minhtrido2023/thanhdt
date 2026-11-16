# -*- coding: utf-8 -*-
"""Self-check: bull_div_boost._q() phải truyền SQL tới `bq` (code-review 2026-11-15).

Lỗi gốc: subprocess.run(list, shell=True) — trên POSIX chỉ cmd[0]='bq' được chạy, các
phần tử sau (cờ + SQL) thành $0,$1… của /bin/sh và bị bỏ ⇒ detect_today() không bao giờ
query được. Không gọi BigQuery thật: `bq` giả đặt đầu PATH, in lại argv nó nhận.
Không ghi state/log: chỉ gọi _q(), không gọi update_state()/log_decision().
Mutant: nạp lại module với shell=True ⇒ `bq` giả KHÔNG thấy SQL.

Run: python bull_div_boost_q_selfcheck.py   (exit 0 = all pass)
"""
import os
import stat
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
FAILS = []


def check(name, cond, extra=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  — {extra}" if extra else ""))
    if not cond:
        FAILS.append(name)


tmp = tempfile.mkdtemp(prefix="fake_bq_")
fake = os.path.join(tmp, "bq")
with open(fake, "w") as fh:
    fh.write('#!/bin/sh\necho "argc=$#"\nfor a in "$@"; do echo "ARG:$a"; done\n')
os.chmod(fake, os.stat(fake).st_mode | stat.S_IEXEC)
os.environ["PATH"] = tmp + os.pathsep + os.environ.get("PATH", "")

import bull_div_boost as B  # noqa: E402

SQL = "SELECT 42 AS answer"
out = B._q(SQL)
check("fix: bq nhận SQL", f"ARG:{SQL}" in out, out.splitlines()[0] if out else "")
check("fix: bq nhận đủ 7 argv (query + 5 cờ + SQL)", "argc=7" in out)
check("fix: không còn shell=True trong source",
      "shell=True" not in open(B.__file__, encoding="utf-8").read().split("def _q", 1)[1].split("def ", 1)[0])

# Mutant: khôi phục shell=True
src = open(B.__file__, encoding="utf-8").read()
GOOD = "res = subprocess.run(cmd, capture_output=True, text=True)"
check("mutant: dòng fix tồn tại đúng 1 lần", src.count(GOOD) == 1)
mut = {"__name__": "bull_div_boost_mutant", "__file__": B.__file__}
exec(compile(src.replace(GOOD, "res = subprocess.run(cmd, capture_output=True, text=True, shell=True)"),
             B.__file__, "exec"), mut)
mout = mut["_q"](SQL)
check("mutant: bq KHÔNG thấy SQL (lỗi gốc tái hiện)", f"ARG:{SQL}" not in mout and "argc=0" in mout,
      mout.strip().replace("\n", " | "))

print(f"\n{'ALL PASS' if not FAILS else f'{len(FAILS)} FAIL'}")
sys.exit(1 if FAILS else 0)
