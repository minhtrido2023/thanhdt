#!/usr/bin/env python3
import json, os, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
rows = json.load(open(os.path.join(HERE, "bench_rows.json")))
N = len(rows)


def agg(rs, tag, k):
    return st.mean(r[tag][k] for r in rs) if rs else float("nan")


def block(title, rs):
    print(f"\n{'='*78}\n{title}   (N={len(rs)})\n{'='*78}")
    print(f"{'':22} {'Prec':>6} {'Recall':>7} {'F1':>6} {'tok':>8} {'giây':>7}")
    for tag, label in (("sw_call", "srcwalk scope=."),
                       ("swc_call", "srcwalk scope=đúng"),
                       ("gp_call", "grep")):
        print(f"  CALLERS {label:14} {agg(rs,tag,'prec'):6.3f} {agg(rs,tag,'rec'):7.3f} "
              f"{agg(rs,tag,'f1'):6.3f} {agg(rs,tag,'tok'):8.0f} {agg(rs,tag,'sec'):7.3f}")
    print()
    for tag, label in (("sw_def", "srcwalk scope=."),
                       ("swc_def", "srcwalk scope=đúng"),
                       ("gp_def", "grep")):
        print(f"  DEF     {label:14} {agg(rs,tag,'prec'):6.3f} {agg(rs,tag,'rec'):7.3f} "
              f"{agg(rs,tag,'f1'):6.3f} {agg(rs,tag,'tok'):8.0f} {agg(rs,tag,'sec'):7.3f}")


print(f"MẪU: N={N} symbol (top-level, def duy nhất), seed=20260803")
ign = [r for r in rows if r["gitignored"]]
vis = [r for r in rows if not r["gitignored"]]
print(f"  bị gitignore: {len(ign)} ({len(ign)/N:.0%})   |   không: {len(vis)} ({len(vis)/N:.0%})")
print(f"  có ≥1 caller thật: {sum(1 for r in rows if r['n_gt_calls'])}"
      f"  |  0 caller: {sum(1 for r in rows if not r['n_gt_calls'])}")

block("TOÀN MẪU", rows)
block("A. File KHÔNG bị gitignore (srcwalk nhìn thấy được)", vis)
block("B. File BỊ gitignore (mike/ — code của fleet)", ign)

# --- recall = 0 khi có caller thật: tần suất "im lặng bỏ sót" ---
print(f"\n{'='*78}\nBỎ SÓT HOÀN TOÀN (có caller thật nhưng công cụ trả 0)\n{'='*78}")
has = [r for r in rows if r["n_gt_calls"] > 0]
for tag, label in (("sw_call", "srcwalk scope=."), ("swc_call", "srcwalk scope=đúng"), ("gp_call", "grep")):
    miss = [r for r in has if r[tag]["tp"] == 0]
    mv = [r for r in miss if not r["gitignored"]]
    print(f"  {label:20} {len(miss):3}/{len(has)} ({len(miss)/len(has):5.1%})"
          f"   — trong đó KHÔNG do gitignore: {len(mv)}")

# --- phân tầng theo độ mơ hồ tên ---
print(f"\n{'='*78}\nTHEO ĐỘ MƠ HỒ CỦA TÊN (số file có nhắc tên đó)\n{'='*78}")
print(f"{'dải':>12} {'n':>4}  {'sw. P':>6} {'sw. R':>6} | {'grep P':>7} {'grep R':>7} | {'sw tok':>7} {'gp tok':>7}")
for lo, hi, lbl in ((0, 1, "1 file"), (2, 3, "2-3"), (4, 10, "4-10"), (11, 10**9, ">10")):
    s = [r for r in vis if lo <= r["amb_files"] <= hi]
    if not s:
        continue
    print(f"{lbl:>12} {len(s):4}  {agg(s,'swc_call','prec'):6.3f} {agg(s,'swc_call','rec'):6.3f} | "
          f"{agg(s,'gp_call','prec'):7.3f} {agg(s,'gp_call','rec'):7.3f} | "
          f"{agg(s,'swc_call','tok'):7.0f} {agg(s,'gp_call','tok'):7.0f}")

# --- exact vs file-level ---
print(f"\n{'='*78}\nQUY KẾT DÒNG có chuẩn không? (exact (file,dòng) vs chỉ file)\n{'='*78}")
for tag, label in (("swc_call", "srcwalk scope=đúng"), ("gp_call", "grep")):
    print(f"  {label:20} F1 exact={agg(vis,tag,'f1'):.3f}  F1 file-level={agg(vis,tag,'f1_file'):.3f}")
