#!/usr/bin/env python3
"""So byte: khối GHI macro_health.json của macro_healthcheck.py bản CŨ (main) vs bản MỚI, cùng
một `report`. Khối ghi được trích bằng ast từ file thật (các lệnh top-level nằm giữa phép gán
`report = {...}` và lệnh print đầu tiên sau nó) rồi exec với DATADIR = thư mục tạm.
KHÔNG chạy macro_healthcheck.py, KHÔNG ghi vào data/ thật (file thật chỉ được ĐỌC làm đầu vào).
Dùng: atomic_write_byte_proof.py <old.py> <new.py> <real macro_health.json>"""
import ast, hashlib, json, os, stat, sys, tempfile

def write_block(path):
    body = ast.parse(open(path, encoding="utf-8").read()).body
    i = next(k for k, n in enumerate(body) if isinstance(n, ast.Assign)
             and any(getattr(t, "id", None) == "report" for t in n.targets))
    j = next(k for k in range(i + 1, len(body)) if isinstance(body[k], ast.Expr)
             and isinstance(body[k].value, ast.Call) and getattr(body[k].value.func, "id", None) == "print")
    return body[i + 1:j]

def run(path, report, preexisting):
    d = tempfile.mkdtemp(prefix="hc_proof_")
    if preexisting is not None:
        open(os.path.join(d, "macro_health.json"), "wb").write(preexisting)
    nodes = write_block(path)
    exec(compile(ast.Module(nodes, []), path, "exec"), {"os": os, "json": json, "report": report, "DATADIR": d})
    p = os.path.join(d, "macro_health.json")
    return open(p, "rb").read(), sorted(os.listdir(d)), stat.S_IMODE(os.stat(p).st_mode), [ast.unparse(n) for n in nodes]

old, new, real = sys.argv[1:4]
real_bytes = open(real, "rb").read()
inputs = {"real": json.loads(real_bytes),
          "synthetic": {"ts": "2026-10-12T18:30:05+07:00", "status": "DEGRADED", "sev": "SEV2",
                        "recommended_state_source": "DT4_only",
                        "market_stress": {"flag": True, "detail": "VIX ≥ 30 — căng thẳng"},
                        "macro_now": None, "missed_runs_tdays": 0, "sources": [], "checks": [{"x": 1.5e-7}]}}
ok = True
for name, rep in inputs.items():
    for pre in (None, b"OLD CONTENT LONGER THAN NOTHING"):
        bo, lo, mo, so = run(old, rep, pre)
        bn, ln, mn, sn = run(new, rep, pre)
        same = bo == bn and lo == ln == ["macro_health.json"]
        ok &= same
        print(f"[{name}, file có sẵn={pre is not None}] old sha256={hashlib.sha256(bo).hexdigest()[:16]} "
              f"new sha256={hashlib.sha256(bn).hexdigest()[:16]} bytes={len(bn)} byte-identical={bo == bn} "
              f"dir_old={lo} dir_new={ln} mode_old={oct(mo)} mode_new={oct(mn)}")
    if name == "real":
        r = bn == real_bytes
        print(f"[real] output bản MỚI == byte file data/macro_health.json đang sống: {r} (ts={rep['ts']!r})")
        ok &= r
print("khối ghi CŨ :", so)
print("khối ghi MỚI:", sn)
print("RESULT:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
