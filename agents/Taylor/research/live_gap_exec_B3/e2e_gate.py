"""B3 e2e: dựng bản báo cáo tuần 06/11 THẬT có cột tiết kiệm, chạy deliver() của report_delivery_gate với
sổ tạm + notify/email giả (KHÔNG ghi sổ thật, KHÔNG gửi). Validation thật (return gate, period-return,
benchmark-table, artifact-lint, nav-flow). ROOT trỏ cây branch để CLI = code branch."""
import os, re, sys, tempfile
from pathlib import Path
TREE = Path(sys.argv[1]).resolve()                 # cây branch
sys.path.insert(0, str(TREE / "bin"))
import report_delivery_gate as rdg, period_table_32 as pt
assert Path(pt.__file__).resolve().parent == TREE / "bin", "module không từ cây branch"
rdg.ROOT = TREE if os.environ.get("E2E_ROOT_BRANCH", "1") == "1" else rdg.ROOT
src = Path(sys.argv[2]).read_text(encoding="utf-8")
rd = "2026-11-06"
rc, j, err = pt.run_cli("SpaceX", rd, False, bin_dir=str(rdg.ROOT / "bin"))
assert rc == 0, err
table = pt.render(j, None)
new, n = re.subn(r"(?ms)^\| Giai đoạn \| SpaceX .*?(?=^## )", table + "\n", src, count=1)
assert n == 1
td = Path(tempfile.mkdtemp(prefix="b3e2e_"))
rep = td / Path(sys.argv[2]).name
rep.write_text(new, encoding="utf-8")
(Path(sys.argv[3]) / rep.name).write_text(new, encoding="utf-8")
import shutil
v2 = Path(sys.argv[2]).parent / "v2" / rep.stem
if v2.is_dir():
    shutil.copytree(v2, td / "v2" / rep.stem)
calls = []
orig = rdg.run_checked
def fake(cmd):
    name = Path(cmd[1]).name if cmd[0] == sys.executable else Path(cmd[0]).name
    if name == "report_return_gate.py":
        return orig(cmd)
    calls.append(name)
rdg.run_checked = fake
rdg.LEGACY_EMAIL_STATE = td / "legacy.json"
rc = rdg.deliver(rep, td / "state.json", "trading_report", td / "notify", td / "email")
print("DELIVER_RC", rc, "stub_calls", calls, "ROOT", rdg.ROOT)
