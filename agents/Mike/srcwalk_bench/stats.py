#!/usr/bin/env python3
"""Bootstrap CI cho các so sánh chính + phân tích tác vụ đọc file."""
import json, os, random, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
random.seed(20260803)
B = 5000


def boot_ci(vals, f=st.mean, lo=2.5, hi=97.5):
    n = len(vals)
    if n == 0:
        return (float("nan"),) * 3
    reps = sorted(f([vals[random.randrange(n)] for _ in range(n)]) for _ in range(B))
    return f(vals), reps[int(B * lo / 100)], reps[int(B * hi / 100)]


rows = json.load(open(os.path.join(HERE, "bench_rows.json")))
vis = [r for r in rows if not r["gitignored"]]
has = [r for r in rows if r["n_gt_calls"] > 0]
hasv = [r for r in has if not r["gitignored"]]

print("=" * 76)
print("SO SÁNH GHÉP CẶP — chênh lệch F1 (grep − srcwalk), bootstrap 95% CI")
print("=" * 76)
for label, rs, a, b in (
    ("CALLERS, file srcwalk nhìn thấy được", vis, "gp_call", "swc_call"),
    ("CALLERS, toàn mẫu (scope=. tự nhiên)", rows, "gp_call", "sw_call"),
    ("TÌM ĐỊNH NGHĨA, file nhìn thấy được", vis, "gp_def", "swc_def"),
):
    d = [r[a]["f1"] - r[b]["f1"] for r in rs]
    m, l, h = boot_ci(d)
    sig = "CÓ Ý NGHĨA" if (l > 0 or h < 0) else "không phân biệt được với 0"
    print(f"\n{label}  (N={len(rs)})")
    print(f"  Δ F1 = {m:+.3f}  CI[{l:+.3f}, {h:+.3f}]  → {sig}")

print("\n" + "=" * 76)
print("TỈ LỆ BỎ SÓT HOÀN TOÀN (recall=0 dù có caller thật) — CI")
print("=" * 76)
for tag, lbl in (("sw_call", "srcwalk scope=."), ("swc_call", "srcwalk scope=đúng"), ("gp_call", "grep")):
    v = [1.0 if r[tag]["tp"] == 0 else 0.0 for r in has]
    m, l, h = boot_ci(v)
    print(f"  {lbl:22} {m:6.1%}  CI[{l:.1%}, {h:.1%}]")
print("  (chỉ file srcwalk nhìn thấy được:)")
for tag, lbl in (("swc_call", "srcwalk scope=đúng"), ("gp_call", "grep")):
    v = [1.0 if r[tag]["tp"] == 0 else 0.0 for r in hasv]
    m, l, h = boot_ci(v)
    print(f"  {lbl:22} {m:6.1%}  CI[{l:.1%}, {h:.1%}]   N={len(hasv)}")

print("\n" + "=" * 76)
print("DOSE-RESPONSE: precision & token theo độ mơ hồ tên (chỉ file nhìn thấy được)")
print("=" * 76)
print(f"{'dải mơ hồ':>11} {'n':>4} | {'srcwalk P (CI)':>26} | {'grep P (CI)':>26} | {'sw tok':>7} {'gp tok':>7}")
for lo, hi, lbl in ((1, 1, "1 file"), (2, 3, "2-3"), (4, 10, "4-10"), (11, 10**9, ">10")):
    s = [r for r in vis if lo <= r["amb_files"] <= hi]
    if len(s) < 3:
        continue
    sm, sl, sh = boot_ci([r["swc_call"]["prec"] for r in s])
    gm, gl, gh = boot_ci([r["gp_call"]["prec"] for r in s])
    stk = st.mean(r["swc_call"]["tok"] for r in s)
    gtk = st.mean(r["gp_call"]["tok"] for r in s)
    print(f"{lbl:>11} {len(s):4} | {sm:.3f} [{sl:.3f},{sh:.3f}]{'':6} | "
          f"{gm:.3f} [{gl:.3f},{gh:.3f}]{'':6} | {stk:7.0f} {gtk:7.0f}")

# ---------------- tác vụ 3: đọc file ----------------
rd = json.load(open(os.path.join(HERE, "bench_read.json")))
print("\n" + "=" * 76)
print(f"TÁC VỤ 3 — ĐỌC FILE: srcwalk outline vs Read nguyên file   (N={len(rd)})")
print("=" * 76)
save = [1 - r["sw_tok"] / r["read_tok"] for r in rd if r["read_tok"] > 0]
m, l, h = boot_ci(save)
print(f"  Tiết kiệm token trung bình: {m:.1%}  CI[{l:.1%}, {h:.1%}]")
print(f"  Trung vị:                   {st.median(save):.1%}")
print(f"  Số file srcwalk ĐẮT HƠN Read: {sum(1 for s in save if s < 0)}/{len(save)}")

rec = [r["n_in_outline"] / r["n_toplevel"] for r in rd]
m, l, h = boot_ci(rec)
print(f"\n  Recall cấu trúc (top-level def có trong outline): {m:.1%}  CI[{l:.1%}, {h:.1%}]")
print(f"  File giữ ĐỦ 100% symbol: {sum(1 for x in rec if x == 1.0)}/{len(rec)} ({sum(1 for x in rec if x==1.0)/len(rec):.0%})")
print(f"  File mất >20% symbol:    {sum(1 for x in rec if x < 0.8)}/{len(rec)}")

print("\n  Theo kích thước file:")
print(f"  {'dải dòng':>12} {'n':>4} {'tiết kiệm':>11} {'recall cấu trúc':>16}")
for lo, hi, lbl in ((0, 100, "<100"), (101, 300, "100-300"), (301, 1000, "300-1k"), (1001, 10**9, ">1k")):
    s = [r for r in rd if lo <= r["lines"] <= hi]
    if not s:
        continue
    sv = st.mean(1 - r["sw_tok"] / r["read_tok"] for r in s)
    rc = st.mean(r["n_in_outline"] / r["n_toplevel"] for r in s)
    print(f"  {lbl:>12} {len(s):4} {sv:10.1%} {rc:15.1%}")

modes = {}
for r in rd:
    modes[r["outline_mode"]] = modes.get(r["outline_mode"], 0) + 1
print(f"\n  Chế độ output: {modes}")
