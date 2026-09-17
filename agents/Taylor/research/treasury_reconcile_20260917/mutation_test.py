"""Mutation test: mỗi đột biến phải làm selfcheck FAIL (exit≠0). Chạy trong thư mục tạm, không đụng bản gốc."""
import subprocess, shutil, tempfile, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(f"{HERE}/treasury_adjust.py").read()
M = [
    ('return -1.0 if ev["action_type"] == "buy_done" else 1.0', 'return 1.0 if ev["action_type"] == "buy_done" else -1.0'),
    ('f_time < e["public_date"] <= asof', 'f_time <= e["public_date"] <= asof'),
    ('f_time < e["public_date"] <= asof', 'f_time < e["public_date"] < asof'),
    ('if unsized:', 'if False:'),
    ('if after and prev and abs', 'if False and abs'),
    ('return _ceiling(base, base + fwd, "TREASURY_FIN_FWD"', 'return _ceiling(base, base - fwd, "TREASURY_FIN_FWD"'),
    ('if any(f_time < d <= asof for d in listed_cuts):', 'if False:'),
    ('if any(f_time < d <= asof for d in listed_cuts):', 'if any(d <= asof for d in listed_cuts):'),
    ('if l_at_fin is None:', 'if False:'),
    ('if held < -TOL:', 'if False:'),
    ('if held > TOL and not any(e["public_date"] <= f_time for e in events):', 'if False:'),
    ('base - held + fwd', 'base + fwd'),
    ('base - held + fwd', 'base - held - fwd'),
    ('> CEILING_PCT', '>= CEILING_PCT'),
    ('CEILING_PCT = 15.0', 'CEILING_PCT = 50.0'),
    ('if base is None:', 'if False:'),
    ('if not fin:', 'if False:'),
    ('if anchor_source == "ticker_financial":', 'if anchor_source != "corporate_action.AIS" and False:'),
]
killed = 0
for i, (a, b) in enumerate(M, 1):
    assert a in SRC, f"mutation {i} không áp được: {a}"
    d = tempfile.mkdtemp()
    open(f"{d}/treasury_adjust.py", "w").write(SRC.replace(a, b, 1))
    shutil.copy(f"{HERE}/treasury_adjust_selfcheck.py", d)
    rc = subprocess.run([sys.executable, f"{d}/treasury_adjust_selfcheck.py"], capture_output=True).returncode
    killed += rc != 0
    print(f"  M{i:02d} {'KILLED' if rc else 'SURVIVED'}: {b[:70]}")
    shutil.rmtree(d)
print(f"\n{killed}/{len(M)} killed")
sys.exit(0 if killed == len(M) else 1)
