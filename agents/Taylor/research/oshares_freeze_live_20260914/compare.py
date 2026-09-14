"""So chuỗi lời gọi tầng ngoài: baseline (BQ sống, code gốc) vs mới (fixture, BQ BỊ CHẶN).
Bỏ qua cờ `cached` (đó chính là thứ đã đổi). Usage: python compare.py base.json new.json"""
import json, sys
b, n = (json.load(open(f)) for f in sys.argv[1:3])
def strip(c): a = dict(c["args"]); a.pop("cached", None); a.pop("n_corp", None); return {**c, "args": a}
B, N = [strip(c) for c in b["calls"]], [strip(c) for c in n["calls"]]
diff = [i for i, (x, y) in enumerate(zip(B, N)) if x != y]
res = {"base_rc": b["rc"], "new_rc": n["rc"], "n_base": len(B), "n_new": len(N), "mismatch_idx": diff,
       "bq_blocked_hits": sum(1 for q in n["bq"] if q.get("blocked")),
       "pass_lines_equal": [l for l in b["stdout"].splitlines() if l.strip().startswith(("PASS", "FAIL"))]
                           == [l for l in n["stdout"].splitlines() if l.strip().startswith(("PASS", "FAIL"))]}
for i in diff[:5]:
    print("DIFF", i, json.dumps(B[i])[:400], "\n  vs", json.dumps(N[i])[:400])
print(json.dumps(res))
