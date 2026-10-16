import sys, os, subprocess, tempfile, time, hashlib
from pathlib import Path
sys.path.insert(0, "bin")
import bq_freshness_check_selfcheck as S
def run(script, pub, src="DT5G_macro"):
    with tempfile.TemporaryDirectory() as td:
        td = Path(td); S.gs_sandbox(td)
        (td/"wc"/"deploy_golive_dt5g_v4"/"publish_gated_state.py").write_text(pub, encoding="utf-8")
        fn, seg = S.gs_extract(script)
        body = (f'set -uo pipefail\nROOT="{td}/mike"\nWORKDIR="{td}/wc"\nPY=python3\nFAILED=0\nWARNED=0\n{fn}\ncd "$WORKDIR"\n{seg}\necho "__END__ FAILED=$FAILED"\n')
        env = dict(os.environ, STUB_SRC=src, TMPDIR=str(td)); env.pop("JOB_ID", None)
        log = td/"c.log"; t0 = time.monotonic()
        with open(log, "ab") as lf:
            try: rc = subprocess.run(["bash","-c",body], stdout=lf, stderr=subprocess.STDOUT, env=env, timeout=60).returncode
            except subprocess.TimeoutExpired: rc = "TIMEOUT"
        b = log.read_bytes()
        pid = td/"wc"/"orphan.pid"
        if pid.exists():
            try: os.kill(int(pid.read_text()), 9)
            except OSError: pass
        return rc, len(b), hashlib.md5(b).hexdigest(), round(time.monotonic()-t0, 1), S.gs_count(td)
quiet = S._STUB_PUBLISHER.replace('print("stub stderr line", file=sys.stderr)\n', "")
orphan = quiet + '\nimport subprocess\nsubprocess.Popen(["bash","-c","echo $$ > orphan.pid; exec sleep 20"], stderr=subprocess.DEVNULL)\n'
for label, pub in (("ngày thường, publisher không stderr", quiet), ("ngày thường + cháu mồ côi giữ stdout", orphan), ("ngày thường, publisher CÓ stderr", S._STUB_PUBLISHER)):
    for name, sc in (("master", "/tmp/gs_r2/master_bq.sh"), ("nhánh ", "bin/bq_freshness_check.sh")):
        print(f"{label:42s} {name}: rc/bytes/md5/giây/(discord,bus,tele) = {run(sc, pub)}")
