"""Bằng chứng 'ngày thường y hệt từng byte': đoạn publish của bq_freshness_check.sh bản MASTER
(git show) vs bản nhánh, stub publisher ra DT5G_macro, stdout+stderr GỘP ra 1 file như cron
(`>> log 2>&1`). Chạy N lần mỗi bản, so md5."""
import hashlib, os, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, sys.argv[1])            # <worktree>/bin
import bq_freshness_check_selfcheck as sc
master, new, n = sys.argv[2], sys.argv[3], int(sys.argv[4])
def run(script, src):
    with tempfile.TemporaryDirectory() as td:
        sc.gs_sandbox(td)
        fn, seg = sc.gs_extract(script)
        body = (f'set -uo pipefail\nROOT="{td}/mike"\nWORKDIR="{td}/wc"\nPY=python3\nFAILED=0\nWARNED=0\n'
                f'{fn}\ncd "$WORKDIR"\n{seg}\necho "__END__ FAILED=$FAILED"\n')
        env = dict(os.environ, STUB_SRC=src, TMPDIR=td); env.pop("JOB_ID", None)
        log = Path(td) / "merged.log"
        with open(log, "wb") as f:
            rc = subprocess.run(["bash", "-c", body], stdout=f, stderr=subprocess.STDOUT, env=env, timeout=120).returncode
        data = log.read_bytes()
        return rc, hashlib.md5(data).hexdigest(), len(data), sc.gs_count(td), sc.gs_marker(td) is not None
for src in ("DT5G_macro", "DT4_only"):
    a = {run(master, src)[:3] for _ in range(n)}
    b = [run(new, src) for _ in range(n)]
    print(f"{src}: master {n} lượt -> {sorted(a)}")
    print(f"{src}: nhánh  {n} lượt -> (rc,md5,bytes)={sorted({x[:3] for x in b})} calls(discord,bus,telegram)={sorted({x[3] for x in b})} marker_ghi={sorted({x[4] for x in b})}")
    print(f"{src}: GIỐNG HỆT = {a == {x[:3] for x in b}}")
