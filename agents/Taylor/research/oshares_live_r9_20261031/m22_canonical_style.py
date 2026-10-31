#!/usr/bin/env python3
"""R9/việc 7: M22 trên cây CANONICAL. Đặt HERE = PROD (cây canonical thật /home/trido/thanhdt/WorkingClaude)
⇒ HERE == PROD như khi selfcheck chạy sau merge. So check cũ (C4 _paths_ok, probe ghim HERE) với C18
(probe trên cây tạm symlink từ PROD) dưới PIN thật và PIN [""] (mutant M22).
Dùng: python m22_canonical_style.py <worktree WC chứa oshares_dcf_selfcheck.py R9>"""
import sys
wt = sys.argv[1]
sys.path.insert(0, wt)
import oshares_dcf_selfcheck as s
PROD = s.PROD
real_pin = list(s.PIN)
for label, pin in (("PIN thật", real_pin), ("M22 PIN=['']", [""])):
    s.PIN[:] = pin
    s.HERE = PROD                                         # canonical-style: cây test == PROD
    import json
    j = json.loads(s._subproc(s.probe_code("out = 'ok'; import oshares_dcf, oshares_pit", here=PROD)))
    old_ok = all(v == PROD for v in j["paths"].values())  # check kiểu C4/C6/C12 (so với HERE == PROD)
    out18, p18 = s.probe_on_tree(PROD)                    # C18: cây tạm ≠ PROD
    c18_ok = out18 == "ok" and "oshares_dcf" in p18 and all(v == p18["dcf_valuation"] for v in p18.values()) \
        and p18["dcf_valuation"] != PROD
    print(f"{label}: check cũ (HERE==PROD) {'PASS' if old_ok else 'FAIL'} | C18 {'PASS' if c18_ok else 'FAIL'} | C18 paths {p18}")
s.PIN[:] = real_pin
import shutil
for d in s._TMPDIRS:
    shutil.rmtree(d, ignore_errors=True)
