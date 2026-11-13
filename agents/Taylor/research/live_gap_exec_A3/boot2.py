"""A3: bootstrap_nav.py (circular block L=21, B=4000, seed 12345) — CHẠY ĐÚNG mã nguồn gốc (exec phần định nghĩa,
trước dòng `paths = sys.argv`), chỉ đổi định dạng in sang 2 chữ số thập phân. Usage: boot2.py ledger.csv ..."""
import sys, hashlib, numpy as np
src = open("/home/trido/thanhdt/WorkingClaude/bootstrap_nav.py", encoding="utf-8").read()
ns = {}; exec(src.split("\npaths = sys.argv")[0], ns)
assert (ns["L"], ns["B"], ns["SEED"]) == (21, 4000, 12345)
print(f"bootstrap_nav.py md5 {hashlib.md5(src.encode()).hexdigest()[:8]}  L={ns['L']} B={ns['B']} seed={ns['SEED']}")
print(f"{'tag':>14} {'md5':>8} {'CAGR_act':>9} {'CAGR_p5':>8} {'CAGR_med':>8} {'DD_act':>8} {'DD_med':>8} {'DD_p5':>8} {'P<-30':>6}")
for p in sys.argv[1:]:
    s = ns["load_nav"](p); N, yrs, A, C, S, D = ns["boot"](s); pc = ns["pct"]
    tag = p.split("_exp_")[1].split("_univpit")[0]; md5 = hashlib.md5(open(p, "rb").read()).hexdigest()[:8]
    print(f"{tag:>14} {md5:>8} {A[0]*100:8.2f}% {pc(C,5)*100:7.2f}% {pc(C,50)*100:7.2f}% {A[2]*100:7.2f}% "
          f"{pc(D,50)*100:7.2f}% {pc(D,5)*100:7.2f}% {(D<-0.30).mean()*100:5.2f}%", flush=True)
