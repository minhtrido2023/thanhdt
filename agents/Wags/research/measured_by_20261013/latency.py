#!/usr/bin/env python3
"""Đo thời gian chạy append_event.sh TRƯỚC (git show <base>:bin/append_event.sh) vs SAU (cây này),
trong bus tạm. Xen kẽ trước/sau từng lượt để máy bận thì bận đều 2 bên.
    python3 latency.py [N=30] [base=master]
"""
import os, shutil, statistics, subprocess, sys, tempfile, time
N = int(sys.argv[1]) if len(sys.argv) > 1 else 30
BASE = sys.argv[2] if len(sys.argv) > 2 else "master"
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
def tree(old):
    d = tempfile.mkdtemp(prefix="ae_lat_"); os.makedirs(d + "/bin"); os.makedirs(d + "/kb")
    for f in ("mike_json.py", "json_payload_diag.py", "finding_measured_by.py", "append_event.sh"):
        shutil.copy2(os.path.join(ROOT, "bin", f), d + "/bin/" + f)
    if old:
        os.remove(d + "/bin/finding_measured_by.py")
        src = subprocess.run(["git", "-C", ROOT, "show", BASE + ":bin/append_event.sh"], capture_output=True, check=True).stdout
        open(d + "/bin/append_event.sh", "wb").write(src)
    open(d + "/kb/version.txt", "w").write("1\n"); return d
PAY = '{"selfcheck":"27 PASS / 0 FAIL","note":"' + "do lai so lieu " * 100 + '"}'   # ~1,6KB = median bus
CASES = {"finding thiếu measured_by (đường cảnh báo)": ["T", "finding", "lat", PAY],
         "finding có measured_by": ["T", "finding", "lat", PAY[:-1] + ',"measured_by":"x"}'],
         "heartbeat (loại khác)": ["T", "heartbeat", "lat", '{"status":"in_progress","note":"x"}'],
         "status (loại khác)": ["T", "status", "lat", PAY]}
env = {k: v for k, v in os.environ.items() if k != "JOB_ID"}
old, new = tree(True), tree(False)
try:
    for label, args in CASES.items():
        t = {"old": [], "new": []}
        for i in range(N + 3):
            for k, d in (("old", old), ("new", new)) if i % 2 == 0 else (("new", new), ("old", old)):
                t0 = time.perf_counter()
                rc = subprocess.run([d + "/bin/append_event.sh"] + args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env).returncode
                assert rc == 0
                if i >= 3: t[k].append((time.perf_counter() - t0) * 1000)   # 3 lượt đầu = làm nóng
        m = {k: statistics.median(v) for k, v in t.items()}
        p95 = {k: sorted(v)[int(0.95 * (len(v) - 1))] for k, v in t.items()}
        mn = {k: min(v) for k, v in t.items()}
        print("%-44s N=%d  trước min %.1f median %.1f p95 %.1f | sau min %.1f median %.1f p95 %.1f | Δmin %+.1fms Δmedian %+.1fms" % (
            label, N, mn["old"], m["old"], p95["old"], mn["new"], m["new"], p95["new"],
            mn["new"] - mn["old"], m["new"] - m["old"]))
finally:
    shutil.rmtree(old, ignore_errors=True); shutil.rmtree(new, ignore_errors=True)
