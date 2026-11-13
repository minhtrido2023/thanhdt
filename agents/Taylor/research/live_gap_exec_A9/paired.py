"""A7: đọc bảng chi tiết boot_band.log (ledger L seed DD5 ...) -> tóm tắt DD5 trung vị [min;max] + chênh GHÉP CẶP cùng (L,seed).
Usage: paired.py boot_band.log A-B ...  (A,B = nhãn ledger)"""
import sys, re, numpy as np
R = {}
for ln in open(sys.argv[1], encoding="utf-8"):
    m = re.match(r"\s*(\S+)\s+(10|21|42)\s+(\d+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+([\d.]+)\s*$", ln)
    if m: R.setdefault(m[1], {})[(int(m[2]), int(m[3]))] = (float(m[4]), float(m[6]), float(m[7]))
print(f"{'ledger':>12} {'DD5 med':>8} {'min':>7} {'max':>7} | {'CAGR5 med':>9} | {'P(DD<-30%)':>10}")
for k, v in R.items():
    d = np.array([x[0] for x in v.values()]); c = np.array([x[1] for x in v.values()]); p = np.array([x[2] for x in v.values()])
    print(f"{k:>12} {np.median(d):8.2f} {d.min():7.2f} {d.max():7.2f} | {np.median(c):9.2f} | {np.median(p):10.2f}")
print("\nchênh ghép cặp DD5 (A − B), 15 cấu hình cùng (L,seed):")
for pr in sys.argv[2:]:
    a, b = pr.split("-", 1); ks = sorted(set(R[a]) & set(R[b]))
    x = np.array([R[a][k][0] - R[b][k][0] for k in ks])
    print(f"  {a:>12} − {b:<12} n={len(x)}  median {np.median(x):+6.2f} [{x.min():+6.2f}; {x.max():+6.2f}]")
