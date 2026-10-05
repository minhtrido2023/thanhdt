#!/usr/bin/env python3
"""Selfcheck custom30_publish_guard + wiring trong custom30_history.py (không chạm BQ)."""
import os, subprocess, sys
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
chk("hoa/thường + khoảng trắng: ' YieldCombo ' ⇒ nhận ra", g.inconsistencies(T_V, C_V, " YieldCombo ") == [])
try:
    g.enforce({"CUSTOM30_CSV": C_V}); chk("enforce env lệch ⇒ SystemExit", False)
except SystemExit as e:
    chk("enforce env lệch ⇒ SystemExit có lý do", "TỪ CHỐI" in str(e))
chk("enforce env mặc định ⇒ không raise", g.enforce({}) is None)
# wiring: custom30_history.py PHẢI gọi guard trước khi chạm BQ (chạy thật với env lệch, kỳ vọng exit≠0 + thông điệp)
env = dict(os.environ, CUSTOM30_CSV=C_V); env.pop("BASKET_SELECT", None)
r = subprocess.run([sys.executable, os.path.join(HERE, "custom30_history.py")], env=env,
                   capture_output=True, text=True, timeout=120)
chk("custom30_history.py env lệch ⇒ exit≠0 + 'TỪ CHỐI CHẠY'", r.returncode != 0 and "TỪ CHỐI CHẠY" in (r.stderr + r.stdout))
chk("... và KHÔNG in dòng 'building 8L custom30' (chưa chạm BQ)", "building 8L custom30" not in r.stdout)
print(f"{'FAIL' if fails else 'ALL PASS'} ({fails} fail)")
sys.exit(1 if fails else 0)
