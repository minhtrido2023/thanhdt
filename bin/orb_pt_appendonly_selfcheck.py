# -*- coding: utf-8 -*-
"""
orb_pt_appendonly_selfcheck.py — kiem tra so paper ORB la APPEND-ONLY (item 3/6, job
Taylor_20260925_095910). Chay orb_pt.py THAT trong sandbox (ORB_PT_WD) voi 3 tinh huong:

  CA1  log da co day du            -> 0 append, so khong doi
  CA2  log thieu vai ngay cuoi     -> chi append dung so ngay thieu, ngay cu byte-identical
  CA3  1 ngay cu bi doi 'net'      -> GIU so cu, in canh bao, ghi data/orb_pt_revisions.log
  CA4  log rong (chua ton tai)     -> tao moi binh thuong (khong regression)

Moi ca chay 1 lan orb_pt.py (co goi vnstock that). Khong dung du lieu production ngoai viec
copy log hien tai lam diem khoi dau -- KHONG BAO GIO ghi vao data/ that.

KHONG dua vao run_selfchecks.sh: moi lan chay goi vnstock THAT 4 lan (phu thuoc mang + rate
limit cua vendor). Chay TAY khi sua orb_pt.py:  python3 mike/bin/orb_pt_appendonly_selfcheck.py
"""
import os, shutil, subprocess, sys, tempfile
import pandas as pd

WC = "/home/trido/thanhdt/WorkingClaude"
SRC_LOG = WC + "/data/orb_pt_log.csv"
PY = sys.executable
fails, checks = [], 0

def ck(cond, msg):
    global checks
    checks += 1
    if not cond: fails.append(msg)

def run(wd):
    env = dict(os.environ, ORB_PT_WD=wd)
    r = subprocess.run([PY, WC + "/orb_pt.py"], capture_output=True, text=True, env=env, timeout=300)
    return r.returncode, r.stdout + r.stderr

def sandbox(log_df=None):
    d = tempfile.mkdtemp(prefix="orb_pt_sc_")
    os.makedirs(d + "/data")
    if log_df is not None: log_df.to_csv(d + "/data/orb_pt_log.csv", index=False)
    return d

base = pd.read_csv(SRC_LOG); base["date"] = base["date"].astype(str)
print(f"baseline log: {len(base)} ban ghi, {base['date'].iloc[0]} -> {base['date'].iloc[-1]}")

# ---- CA1: day du -> khong append, khong doi
d1 = sandbox(base)
rc, out = run(d1)
after1 = pd.read_csv(d1 + "/data/orb_pt_log.csv"); after1["date"] = after1["date"].astype(str)
ck(rc == 0, "CA1 exit code != 0")
ck("+ 0 ngay moi" in out, "CA1 khong bao '+ 0 ngay moi'")
ck(len(after1) == len(base), f"CA1 so ban ghi doi {len(base)} -> {len(after1)}")
ck(after1["net"].round(12).tolist() == base["net"].round(12).tolist(), "CA1 cot net bi doi")
ck(not os.path.exists(d1 + "/data/orb_pt_revisions.log"), "CA1 khong duoc ghi revisions.log")

# ---- CA2: thieu 3 ngay cuoi -> append dung 3
trimmed = base.iloc[:-3].copy()
d2 = sandbox(trimmed)
rc, out = run(d2)
after2 = pd.read_csv(d2 + "/data/orb_pt_log.csv"); after2["date"] = after2["date"].astype(str)
ck(rc == 0, "CA2 exit code != 0")
ck("+ 3 ngay moi" in out, f"CA2 khong bao '+ 3 ngay moi' (out co: {[l for l in out.splitlines() if 'append-only' in l]})")
ck(len(after2) == len(base), f"CA2 tong ban ghi {len(after2)} != {len(base)}")
ck(after2.iloc[:len(trimmed)]["net"].round(12).tolist() == trimmed["net"].round(12).tolist(),
   "CA2 ban ghi cu khong giu nguyen")
ck(sorted(after2["date"]) == sorted(base["date"]), "CA2 tap ngay khac baseline")

# ---- CA3: sua 'net' 1 ngay cu -> phai GIU so cu + canh bao + revisions.log
poisoned = base.copy()
i = len(poisoned) // 2
bad_date = poisoned.at[i, "date"]; good_net = float(base.at[i, "net"])
poisoned.at[i, "net"] = good_net + 0.0123
d3 = sandbox(poisoned)
rc, out = run(d3)
after3 = pd.read_csv(d3 + "/data/orb_pt_log.csv"); after3["date"] = after3["date"].astype(str)
kept = float(after3[after3["date"] == bad_date]["net"].iloc[0])
ck(rc == 0, "CA3 exit code != 0")
ck("VENDOR REVISION" in out, "CA3 khong in canh bao VENDOR REVISION")
ck(any(bad_date in l and "net luu" in l for l in out.splitlines()),
   f"CA3 dong canh bao khong neu ngay {bad_date}")
ck(abs(kept - (good_net + 0.0123)) < 1e-12,
   f"CA3 so DA LUU bi ghi de: {kept} (phai giu {good_net+0.0123})")
ck(os.path.exists(d3 + "/data/orb_pt_revisions.log"), "CA3 khong ghi revisions.log")
if os.path.exists(d3 + "/data/orb_pt_revisions.log"):
    rl = open(d3 + "/data/orb_pt_revisions.log").read()
    ck(f"date={bad_date}" in rl and "net_stored=" in rl and "net_refetch=" in rl,
       "CA3 revisions.log thieu truong date/net_stored/net_refetch")

# ---- CA4: chua co log -> tao moi
d4 = sandbox(None)
rc, out = run(d4)
ck(rc == 0, "CA4 exit code != 0")
ck(os.path.exists(d4 + "/data/orb_pt_log.csv"), "CA4 khong tao duoc log moi")
if os.path.exists(d4 + "/data/orb_pt_log.csv"):
    a4 = pd.read_csv(d4 + "/data/orb_pt_log.csv")
    ck(len(a4) >= len(base), f"CA4 log moi {len(a4)} < baseline {len(base)}")

for d in (d1, d2, d3, d4): shutil.rmtree(d, ignore_errors=True)
print(f"\n{checks - len(fails)}/{checks} check PASS")
for f in fails: print("  FAIL:", f)
sys.exit(1 if fails else 0)
