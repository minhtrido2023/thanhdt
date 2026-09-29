"""Mutation: đổi ĐÚNG 1 giá trị trong feed đóng băng (hoặc bỏ 1 `_cache=`) ⇒ check tương ứng PHẢI đỏ.
Mỗi mutation chạy trong tiến trình con riêng (module sạch). Usage: OSH_WT=... python mutate.py"""
import json, os, re, shutil, subprocess, sys, tempfile
WT = os.environ["OSH_WT"]; PY = sys.executable
bump = lambda v: repr(float(v) + 1)
# (id, module, bảng, mã, khoá khớp (idx, value), idx đổi, hàm đổi, check phải đỏ)
M = [
 ("FPT", "live", "C", "FPT", (2, "2025-09-12"), 8, bump, "4."),
 ("HAH", "live", "Q", "HAH", (0, "2026-07-30"), 1, bump, "H5."),
 ("NAF", "live", "C", "NAF", (1, "2026-01-05"), 5, lambda v: "7083933", "P1."),
 ("DHG", "live", "Q", "DHG", (0, "2026-07-20"), 0, lambda v: "2026-08-13", "8d."),
 ("PVT", "live", "Q", "PVT", (0, "2026-07-29"), 1, lambda v: repr(float(v) + 1e6), "N6."),
 ("ACB", "live", "Q", "ACB", (0, "2026-07-22"), 1, lambda v: repr(float(v) + 1e8), "N6."),
 ("HDB", "live", "Q", "HDB", (0, "2026-07-31"), 1, lambda v: repr(float(v) + 1e8), "N6."),
 ("TCB", "live", "C", "TCB", (2, "2025-12-01"), 8, lambda v: repr(float(v) + 1e8), "N5."),
 ("MBB", "live", "C", "MBB", (5, "805499990"), 5, bump, "9."),
 ("IDC", "live", "C", "IDC", (2, "2020-05-28"), 7, lambda v: "2700000000", "N1."),
 ("VRE", "live", "Q", "VRE", (0, "2026-07-29"), 1, bump, "F1."),
 ("CC1", "live", "Q", "CC1", (0, "2026-07-31"), 1, bump, "F5."),
 ("HHV", "live", "Q", "HHV", (0, "2026-07-31"), 1, bump, "AB1."),
 ("VCI", "live", "Q", "VCI", (0, "2026-02-02"), 1, lambda v: repr(float(v) - 127_500_000), "AB1c."),
 ("ABB", "live", "Q", "ABB", (0, "2026-02-02"), 1, bump, "F6."),
 ("NVL", "live", "Q", "NVL", (0, "2026-02-02"), 1, bump, "F6."),
 ("KBC", "live", "Q", "KBC", (0, "2026-02-02"), 1, bump, "F6b."),
 ("KHP", "live", "C", "KHP", (2, "2026-09-14"), 8, lambda v: repr(float(v) + 1e7), "10b."),
 ("AAA", "pit", "C", "AAA", (2, "2019-06-03"), 8, bump, "A6."),
 ("VNM", "pit", "C", "VNM", (1, "2016-07-11"), 5, lambda v: "0", "A4b."),
]
CHILD = r'''
import io, contextlib, json, sys
sys.path.insert(0, WT)
import oshares_selfcheck_fixture as F
spec = json.loads(SPEC)
if spec.get("tbl"):
    rows = (F._Q if spec["tbl"] == "Q" else F._C)[spec["tk"]]
    hit = [i for i, r in enumerate(rows) if r[spec["ki"]] == spec["kv"]]
    assert len(hit) == 1, (spec, hit)
    r = list(rows[hit[0]]); old = r[spec["ci"]]; r[spec["ci"]] = spec["new_of"][old] if old in spec["new_of"] else spec["new"]; rows[hit[0]] = tuple(r)
    print("MUT", spec["tk"], old, "->", r[spec["ci"]], file=sys.stderr)
import oshares_live as L, oshares_pit as P
assert L.__file__.startswith(WT) and F.__file__.startswith(WT)
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    try: rc = (P if spec["mod"] == "pit" else L)._selfcheck()
    except Exception as e: print(f"CRASH {type(e).__name__}: {e}"); rc = 98
out = buf.getvalue()
fails = [l.split("FAIL", 1)[1].strip() for l in out.splitlines() if l.strip().startswith("FAIL ")]
print(json.dumps({"rc": rc, "fails": fails, "tail": out.strip().splitlines()[-1][:300]}))
'''
def run(spec, wt=WT):
    code = f"WT={wt!r}\nSPEC={json.dumps(json.dumps(spec))}\n" + CHILD
    r = subprocess.run([PY, "-c", code], capture_output=True, text=True, timeout=600, cwd="/tmp")
    try: return json.loads(r.stdout.strip().splitlines()[-1]), r.stderr.strip()[-300:]
    except Exception: return {"rc": r.returncode, "fails": [], "tail": (r.stdout + r.stderr)[-300:]}, ""
res = []
import importlib; sys.path.insert(0, WT); import oshares_selfcheck_fixture as F0
for mid, mod, tbl, tk, (ki, kv), ci, fn, want in M:
    rows = (F0._Q if tbl == "Q" else F0._C)[tk]
    old = [r[ci] for r in rows if r[ki] == kv]; assert len(old) == 1, (mid, old)
    spec = {"mod": mod, "tbl": tbl, "tk": tk, "ki": ki, "kv": kv, "ci": ci, "new": fn(old[0]), "new_of": {}}
    out, err = run(spec)
    red = any(f.startswith(want) for f in out["fails"])
    res.append({"id": mid, "module": mod, "mutation": f"{tbl}.{tk}[{kv}].col{ci}: {old[0]} -> {spec['new']}",
                "expect_red": want, "rc": out["rc"], "fails": out["fails"], "killed": red and out["rc"] != 0})
    print(("KILLED " if res[-1]["killed"] else "SURVIVED ") + mid, want, out["rc"], out["fails"][:4], flush=True)
# LEAK: bỏ 1 `_cache=` trong bản sao module ⇒ guard hermetic phải làm selfcheck đỏ (không lặng lẽ đọc BQ)
tmp = tempfile.mkdtemp(prefix="osh_leak_")
for f in ("oshares_live.py", "oshares_pit.py", "corp_action_lib.py", "oshares_selfcheck_fixture.py"):
    shutil.copy(os.path.join(WT, f), tmp)
src = open(os.path.join(tmp, "oshares_live.py")).read()
old = 'cc1 = oshares_at(["CC1"], "2026-08-19", _cache=frozen(["CC1"]))["CC1"]'
assert src.count(old) == 1
open(os.path.join(tmp, "oshares_live.py"), "w").write(src.replace(old, 'cc1 = oshares_at(["CC1"], "2026-08-19")["CC1"]'))
out, _ = run({"mod": "live"}, wt=tmp)
res.append({"id": "LEAK_no_cache_CC1", "module": "live", "mutation": "bỏ _cache= ở F5 (CC1)",
            "expect_red": "hermetic guard", "rc": out["rc"], "fails": out["fails"], "tail": out["tail"],
            "killed": out["rc"] != 0 and "HERMETIC" in out["tail"]})
print(("KILLED " if res[-1]["killed"] else "SURVIVED ") + "LEAK", out["rc"], out["tail"][:160])
srcp = open(os.path.join(tmp, "oshares_pit.py")).read()
oldp = 'dhg_live = oshares_at(["DHG"], "2026-08-12", _cache=frozen(["DHG"]))["DHG"]'
assert srcp.count(oldp) == 1
open(os.path.join(tmp, "oshares_live.py"), "w").write(src)  # khôi phục live
open(os.path.join(tmp, "oshares_pit.py"), "w").write(srcp.replace(oldp, 'dhg_live = oshares_at(["DHG"], "2026-08-12")["DHG"]'))
out, _ = run({"mod": "pit"}, wt=tmp)
res.append({"id": "LEAK_no_cache_DHG_pit", "module": "pit", "mutation": "bỏ _cache= ở A15 (DHG)",
            "expect_red": "L1-L3", "rc": out["rc"], "fails": out["fails"], "tail": out["tail"],
            "killed": out["rc"] != 0 and any("L1-L3" in f and "HERMETIC" in f for f in out["fails"])})
print(("KILLED " if res[-1]["killed"] else "SURVIVED ") + "LEAK_pit", out["rc"], out["fails"])
shutil.rmtree(tmp)
json.dump(res, open("mutation_result.json", "w"), ensure_ascii=False, indent=1)
print(f"{sum(r['killed'] for r in res)}/{len(res)} mutation bị giết")
