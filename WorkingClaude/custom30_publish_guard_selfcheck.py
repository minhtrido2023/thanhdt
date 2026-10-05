#!/usr/bin/env python3
"""Selfcheck custom30_publish_guard + wiring trong custom30_history.py (không chạm BQ)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import custom30_publish_guard as g

T_V, T_B = "lithe-record-440915-m9:tav2_bq.custom30v_8l", "lithe-record-440915-m9:tav2_bq.custom30_8l"
C_V, C_B = "custom30v_8l_publish.csv", "custom30_8l_publish.csv"
fails = 0
def chk(name, ok):
    global fails
    fails += (not ok); print(("PASS " if ok else "FAIL ") + name)

chk("custom30V đầy đủ ⇒ OK", g.inconsistencies(T_V, C_V, "yieldcombo") == [])
chk("blend mặc định ⇒ OK", g.inconsistencies(T_B, C_B, "blend") == [])
chk("sự cố 09-30: CSV custom30v + select blend ⇒ CHẶN", bool(g.inconsistencies(T_B, C_V, "blend")))
chk("TABLE custom30v + CSV blend ⇒ CHẶN", bool(g.inconsistencies(T_V, C_B, "yieldcombo")))
chk("yieldcombo nhưng TABLE/CSV blend ⇒ CHẶN", bool(g.inconsistencies(T_B, C_B, "yieldcombo")))
chk("select v3comp (audit) + CSV blend ⇒ OK (không phải yieldcombo)", g.inconsistencies(T_B, C_B, "v3comp") == [])
chk("hoa/thường: 'YieldCombo' ⇒ nhận ra (consumer chỉ .lower())", g.inconsistencies(T_V, C_V, "YieldCombo") == [])
chk("khoảng trắng 'yieldcombo ' ⇒ CHẶN (custom_basket không khớp nhánh yieldcombo)", bool(g.inconsistencies(T_V, C_V, "yieldcombo ")))
try:
    g.enforce({"CUSTOM30_CSV": C_V}); chk("enforce env lệch ⇒ SystemExit", False)
except SystemExit as e:
    chk("enforce env lệch ⇒ SystemExit có lý do", "TỪ CHỐI" in str(e))
chk("enforce env mặc định ⇒ không raise", g.enforce({}) is None)
# wiring (TĨNH, AST — KHÔNG chạy custom30_history.py: chạy thật sẽ ghi đè CSV park production nếu guard bị gỡ)
import ast
src = open(os.path.join(HERE, "custom30_history.py")).read()
tree = ast.parse(src)
def lineno_of(pred):
    for n in tree.body:
        for sub in ast.walk(n):
            if pred(sub): return sub.lineno
    return None
enf = lineno_of(lambda n: isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == "enforce" and getattr(n.func.value, "id", "") == "custom30_publish_guard")
first_side = min(x for x in (
    lineno_of(lambda n: isinstance(n, ast.Call) and getattr(n.func, "id", "") == "detect_end_date"),
    lineno_of(lambda n: isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "build_pit"),
    lineno_of(lambda n: isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "to_csv"),
) if x)
chk("custom30_history.py gọi custom30_publish_guard.enforce()", enf is not None)
chk("enforce() đứng TRƯỚC detect_end_date/build_pit/to_csv (chưa chạm BQ/ghi file)", enf is not None and enf < first_side)
print(f"{'FAIL' if fails else 'ALL PASS'} ({fails} fail)")
sys.exit(1 if fails else 0)
