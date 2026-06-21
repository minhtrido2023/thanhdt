#!/usr/bin/env python3
"""package_8l_full.py — assemble the COMPLETE 8L go-live system into a staging tree for zipping.

Collects: full local-import closure (.py) + every data/config file those scripts actually read
(resolved to its real location: WORKDIR root or data/), preserving layout. Excludes only the secret
telegram_config.json (template shipped instead). Prints the staged tree + total size for review.
"""
import os, re, ast, shutil
WORK = r"/home/trido/thanhdt/WorkingClaude"
STAGE = os.path.join(WORK, "release_8l_full", "8L_system_full")
ENTRY = [
    "rating_8l.py", "unified_screener.py", "rank_8l.py", "dna_card.py", "vn30_8l.py",
    "rank_8l_daily_alert.py", "cheap_pb_floor.py",
    "bank_lens_v3.py", "power_lens.py", "cash_machine_screen.py", "margin_cycle_detector.py",
    "saturation_detector.py", "cyclical_structural.py", "asset_play_detector.py", "moat_5f.py",
    "pt_8l_quarterly.py",
    "telegram_8l_bot.py", "bot_8l_commands.py", "dna_report.py", "telegram_recommend.py",
]
SECRET = {"secrets/telegram_config.json"}   # never ship real token; template shipped instead

local_mods = {f[:-3] for f in os.listdir(WORK) if f.endswith(".py")}

def imports_of(path):
    try: tree = ast.parse(open(path, encoding="utf-8").read())
    except Exception: return set()
    mods = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names: mods.add(a.name.split(".")[0])
        elif isinstance(n, ast.ImportFrom):
            if n.module and n.level == 0: mods.add(n.module.split(".")[0])
    return mods

# ── BFS python closure ──
seen, queue = set(), list(ENTRY)
while queue:
    f = queue.pop()
    if f in seen: continue
    p = os.path.join(WORK, f)
    if not os.path.exists(p): continue
    seen.add(f)
    for m in imports_of(p):
        if m in local_mods and (m + ".py") not in seen:
            queue.append(m + ".py")

# ── data/config files actually read (resolve to real path) ──
pat = re.compile(r'["\']([^"\']*?\.(?:csv|json|pkl|md|txt))["\']')
data_files = {}   # rel_path_in_pkg -> abs_src
for f in seen:
    txt = open(os.path.join(WORK, f), encoding="utf-8", errors="replace").read()
    for ref in pat.findall(txt):
        name = ref.replace("\\", "/").split("/")[-1]
        if "{" in name or name in SECRET: continue
        for rel in (os.path.join("data", name), name):     # prefer data/, fall back to root
            ap = os.path.join(WORK, rel)
            if os.path.isfile(ap):
                data_files[rel.replace("\\", "/")] = ap
                break

# ── stage ──
if os.path.exists(STAGE): shutil.rmtree(STAGE)
os.makedirs(os.path.join(STAGE, "data"), exist_ok=True)
for f in sorted(seen):
    shutil.copy2(os.path.join(WORK, f), os.path.join(STAGE, f))
for rel, ap in sorted(data_files.items()):
    dst = os.path.join(STAGE, rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(ap, dst)

# ── report ──
tot = 0; nfiles = 0
for r, _, fs in os.walk(STAGE):
    for x in fs:
        tot += os.path.getsize(os.path.join(r, x)); nfiles += 1
print(f"Python closure: {len(seen)} files")
print(f"Data/config files: {len(data_files)} files")
print(f"TOTAL staged: {nfiles} files, {tot/1e6:.1f} MB\n")
print("=== largest 15 data files ===")
sizes = sorted(((os.path.getsize(a), r) for r, a in data_files.items()), reverse=True)
for sz, r in sizes[:15]:
    print(f"  {sz/1e6:7.2f} MB  {r}")
print("\n=== python files ===")
for f in sorted(seen): print("  ", f)
