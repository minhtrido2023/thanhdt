"""A6 việc 3: DD5 theo DẢI — bootstrap_nav.py (circular block, B=4000) CHẠY ĐÚNG mã gốc (exec phần định nghĩa,
trước `paths = sys.argv`), chỉ quét L ∈ {10,21,42} × SEED ∈ {12345,1,7,2026,31337} bằng cách đặt global của namespace.
Usage: boot_band.py label=ledger.csv[.gz] ...  → bảng chi tiết + tóm tắt trung vị/min/max DD5 theo ledger (và theo L)."""
import sys, gzip, io, hashlib, numpy as np
from multiprocessing import Pool
SRC = open("/home/trido/thanhdt/WorkingClaude/bootstrap_nav.py", encoding="utf-8").read()
LS, SEEDS = (10, 21, 42), (12345, 1, 7, 2026, 31337)
def ns_new():
    ns = {}; exec(SRC.split("\npaths = sys.argv")[0], ns); assert ns["B"] == 4000; return ns
def load(p):
    raw = open(p, "rb").read(); raw = gzip.decompress(raw) if p.endswith(".gz") else raw
    return io.BytesIO(raw), hashlib.md5(raw).hexdigest()
def job(a):
    lab, p, L, sd = a; ns = ns_new(); ns["L"], ns["SEED"] = L, sd
    buf, _ = load(p); s = ns["load_nav"](buf); N, yrs, A, C, S, D = ns["boot"](s); pc = ns["pct"]
    return lab, L, sd, pc(D, 5) * 100, pc(D, 50) * 100, pc(C, 5) * 100, (D < -0.30).mean() * 100
if __name__ == "__main__":
    items = [a.split("=", 1) for a in sys.argv[1:]]
    print(f"bootstrap_nav.py md5 {hashlib.md5(SRC.encode()).hexdigest()[:8]}  B=4000  L={LS}  seeds={SEEDS}")
    for lab, p in items: print(f"  {lab}: md5(data)={load(p)[1]}  {p.split('/')[-1]}")
    with Pool(8) as pool: res = pool.map(job, [(lab, p, L, sd) for lab, p in items for L in LS for sd in SEEDS])
    print(f"\n{'ledger':>12} {'L':>3} {'seed':>6} {'DD5':>7} {'DD50':>7} {'CAGR5':>7} {'P<-30':>6}")
    for r in res: print(f"{r[0]:>12} {r[1]:>3} {r[2]:>6} {r[3]:7.2f} {r[4]:7.2f} {r[5]:7.2f} {r[6]:6.2f}")
    print(f"\n{'ledger':>12} {'nhóm':>6} {'n':>3} {'DD5 trung vị':>12} {'min':>7} {'max':>7}")
    for lab, _ in items:
        for g in ("ALL",) + LS:
            v = np.array([r[3] for r in res if r[0] == lab and (g == "ALL" or r[1] == g)])
            print(f"{lab:>12} {('L=' + str(g)) if g != 'ALL' else 'ALL':>6} {len(v):>3} {np.median(v):12.2f} {v.min():7.2f} {v.max():7.2f}")
