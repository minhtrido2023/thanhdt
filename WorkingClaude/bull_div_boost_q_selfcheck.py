# -*- coding: utf-8 -*-
"""Self-check: bull_div_boost._q() VÀ bull_div_boost_tracker._bq() phải truyền SQL tới `bq`
(code-review 2026-11-15; vòng 2 arch-review 2026-11-16 thêm tracker — cùng lỗi, `tracker update`
ghi state+log rồi mới hỏng ở get_latest_vni() ⇒ ghi dở dang).

Lỗi gốc: subprocess.run(list, shell=True) — trên POSIX chỉ cmd[0]='bq' được chạy, các
phần tử sau (cờ + SQL) thành $0,$1… của /bin/sh và bị bỏ ⇒ detect_today() không bao giờ
query được. Không gọi BigQuery thật: `bq` giả đặt đầu PATH, in lại argv nó nhận.
Không ghi state/log: chỉ gọi _q(), không gọi update_state()/log_decision().
Mutant: nạp lại TỪNG module với shell=True ⇒ `bq` giả KHÔNG thấy SQL.
Thư mục `bq` giả (tempfile) được xoá khi thoát (atexit), kể cả khi FAIL.

Run: python bull_div_boost_q_selfcheck.py   (exit 0 = all pass)
"""
import atexit
import os
import shutil
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
atexit.register(shutil.rmtree, tmp, ignore_errors=True)
fake = os.path.join(tmp, "bq")
with open(fake, "w") as fh:
    fh.write('#!/bin/sh\necho "argc=$#"\nfor a in "$@"; do echo "ARG:$a"; done\n')
os.chmod(fake, os.stat(fake).st_mode | stat.S_IEXEC)
os.environ["PATH"] = tmp + os.pathsep + os.environ.get("PATH", "")

import bull_div_boost as B  # noqa: E402
import bull_div_boost_tracker as TR  # noqa: E402

SQL = "SELECT 42 AS answer"
# (module, tên hàm, số argv mong đợi: query + 5 cờ + SQL)
TARGETS = [(B, "_q", 7), (TR, "_bq", 7)]

for mod, fn, argc in TARGETS:
    tag = f"{os.path.basename(mod.__file__)}:{fn}"
    out = getattr(mod, fn)(SQL)
    check(f"fix [{tag}]: bq nhận SQL", f"ARG:{SQL}" in out, out.splitlines()[0] if out else "")
    check(f"fix [{tag}]: bq nhận đủ {argc} argv", f"argc={argc}" in out)
    src = open(mod.__file__, encoding="utf-8").read()
    body = src.split(f"def {fn}(", 1)[1].split("\ndef ", 1)[0]
    check(f"fix [{tag}]: không còn shell=True trong thân hàm", "shell=True" not in body)
    # Mutant: khôi phục shell=True ngay trong thân hàm
    GOOD = "capture_output=True, text=True)"
    check(f"mutant [{tag}]: điểm đột biến tồn tại đúng 1 lần trong thân hàm", body.count(GOOD) == 1)
    mbody = body.replace(GOOD, "capture_output=True, text=True, shell=True)")
    mut = {"__name__": mod.__name__ + "_mutant", "__file__": mod.__file__}
    exec(compile(src.replace(body, mbody), mod.__file__, "exec"), mut)
    mout = mut[fn](SQL)
    check(f"mutant [{tag}]: bq KHÔNG thấy SQL (lỗi gốc tái hiện)",
          f"ARG:{SQL}" not in mout and "argc=0" in mout, mout.strip().replace("\n", " | "))

print(f"\n{'ALL PASS' if not FAILS else f'{len(FAILS)} FAIL'}")
sys.exit(1 if FAILS else 0)
