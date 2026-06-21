#!/usr/bin/env python3
"""patch_portable.py — make the 8L runtime scripts portable (Linux server) while staying backward-compatible
with the Windows local setup (defaults preserved when os.name=='nt'). Idempotent."""
import os
WD=r"/home/trido/thanhdt/WorkingClaude"
WIN_WD=r"/home/trido/thanhdt/WorkingClaude"
WIN_BQ=r"bq"
WIN_PY=r"C:\Users\hotro\AppData\Local\Google\Cloud SDK\google-cloud-sdk\platform\bundledpython\python.exe"
REPL=[
  # WORKDIR / W  → env var WORKDIR_8L (Windows default preserved)
  (f'WORKDIR=r"{WIN_WD}"', f'WORKDIR=os.environ.get("WORKDIR_8L", r"{WIN_WD}")'),
  (f'W=r"{WIN_WD}"',       f'W=os.environ.get("WORKDIR_8L", r"{WIN_WD}")'),
  # bq binary → env BQ_BIN, platform default (bq on PATH for Linux)
  (f'BQ_BIN=r"{WIN_BQ}"',  f'BQ_BIN=os.environ.get("BQ_BIN", (r"{WIN_BQ}" if os.name=="nt" else "bq"))'),
  (f'BQ=r"{WIN_BQ}"',      f'BQ=os.environ.get("BQ_BIN", (r"{WIN_BQ}" if os.name=="nt" else "bq"))'),
  # bq() pipe: Windows 'type' vs Linux 'cat' (inline, no extra line)
  ('f\'type "{tmp}" |',   'f\'{"type" if os.name=="nt" else "cat"} "{tmp}" |'),
  # dna_card subprocess python (bot fallback)
  (f'PYEXE=r"{WIN_PY}"',   f'PYEXE=os.environ.get("DNA_PYEXE", (r"{WIN_PY}" if os.name=="nt" else "python3"))'),
]
FILES=["unified_screener.py","rank_8l.py","power_lens.py","dna_card.py","telegram_8l_bot.py",
       "rank_8l_daily_alert.py","pt_8l_quarterly.py","hydro_cycle_ic.py","power_lifecycle_ic.py"]
for fn in FILES:
    p=os.path.join(WD,fn)
    if not os.path.exists(p): print(f"skip (missing): {fn}"); continue
    s=open(p,encoding="utf-8").read(); orig=s; n=0
    # ensure 'import os' present
    if "import os" not in s and ("WORKDIR=" in s or "W=r" in s or "BQ" in s):
        s=s.replace("import sys","import sys, os",1) if "import sys" in s else "import os\n"+s
    for a,b in REPL:
        if a in s: s=s.replace(a,b); n+=1
    if s!=orig: open(p,"w",encoding="utf-8").write(s); print(f"patched {fn} ({n} repl)")
    else: print(f"no change {fn} (already portable or pattern absent)")
print("done.")
