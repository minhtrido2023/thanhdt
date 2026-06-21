#!/usr/bin/env python3
"""trace_8l_deps.py — find the closure of local .py modules + data files the 8L go-live system needs."""
import os, re, ast, sys
WORK = r"/home/trido/thanhdt/WorkingClaude"
ENTRY = [
    # daily pipeline (pt_8l_daily.bat)
    "rating_8l.py", "unified_screener.py", "rank_8l.py", "dna_card.py", "vn30_8l.py",
    "rank_8l_daily_alert.py", "cheap_pb_floor.py",
    # pipeline-refresh feeders (8L_README)
    "bank_lens_v3.py", "power_lens.py", "cash_machine_screen.py", "margin_cycle_detector.py",
    "saturation_detector.py", "cyclical_structural.py", "asset_play_detector.py", "moat_5f.py",
    # monitoring
    "pt_8l_quarterly.py",
    # interactive bot
    "telegram_8l_bot.py", "bot_8l_commands.py", "dna_report.py", "telegram_recommend.py",
]
local_mods = {f[:-3] for f in os.listdir(WORK) if f.endswith(".py")}

def imports_of(path):
    try:
        tree = ast.parse(open(path, encoding="utf-8").read())
    except Exception as e:
        return set(), [f"PARSE-ERR {e}"]
    mods = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names: mods.add(a.name.split(".")[0])
        elif isinstance(n, ast.ImportFrom):
            if n.module and n.level == 0: mods.add(n.module.split(".")[0])
    return mods, []

# BFS over local imports
seen, queue, missing = set(), list(ENTRY), []
while queue:
    f = queue.pop()
    if f in seen: continue
    p = os.path.join(WORK, f)
    if not os.path.exists(p):
        missing.append(f); continue
    seen.add(f)
    mods, errs = imports_of(p)
    for m in mods:
        if m in local_mods and (m + ".py") not in seen:
            queue.append(m + ".py")

print("=== PYTHON CLOSURE (%d files) ===" % len(seen))
for f in sorted(seen): print(" ", f)
if missing:
    print("\n=== MISSING ENTRY FILES ===")
    for f in sorted(set(missing)): print(" ", f)

# data files referenced (string literals containing data/ or *.csv/json/pkl)
print("\n=== DATA / CONFIG FILES REFERENCED ===")
pat = re.compile(r'["\']([^"\']*?\.(?:csv|json|pkl|md|txt))["\']')
datarefs = {}
for f in sorted(seen):
    txt = open(os.path.join(WORK, f), encoding="utf-8", errors="replace").read()
    for m in pat.findall(txt):
        base = m.replace("\\", "/").split("/")[-1]
        datarefs.setdefault(base, set()).add(f)
for d in sorted(datarefs):
    exists = os.path.exists(os.path.join(WORK, d)) or os.path.exists(os.path.join(WORK, "data", d))
    print(f"  {'OK ' if exists else 'MISS'} {d:<42} <- {', '.join(sorted(datarefs[d]))[:80]}")
