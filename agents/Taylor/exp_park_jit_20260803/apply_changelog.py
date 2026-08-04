import json, io, os, tempfile
p = "data/trading_rules.json"
new = io.open("mike/agents/Taylor/exp_park_jit_20260803/v23_changelog.txt",
              encoding="utf-8").read().strip()
d = json.load(io.open(p, encoding="utf-8"))
cl = d["_meta"]["changelog"]
i = cl.index(" | v2.2 (2026-08-03)")
assert cl[:i].startswith("v2.3 (2026-08-04)"), cl[:60]
d["_meta"]["changelog"] = new + cl[i:]
s = json.dumps(d, ensure_ascii=False, indent=2) + "\n"
json.loads(s)
fd, tmp = tempfile.mkstemp(dir="data"); os.close(fd)
io.open(tmp, "w", encoding="utf-8").write(s)
os.chmod(tmp, 0o664)
os.replace(tmp, p)
print("v2.3 changelog replaced OK")
