import sys, os, importlib, re
W = sys.argv[1]; OLD = sys.argv[2]  # worktree mới, repo master cũ (mike)
sys.path[:0] = ["/home/trido/thanhdt/WorkingClaude"]
fails = 0
def ck(n, c):
    global fails; print("PASS" if c else "FAIL", n); fails += (not c)
def load(root):
    for m in [m for m in sys.modules if m in ("build", "data_sources") or m.startswith("report_v2")]: del sys.modules[m]
    sys.path.insert(0, f"{root}/bin/report_v2"); sys.path.insert(0, f"{root}/bin")
    import build; return build
class CX:  # chỉ cần .acct
    def __init__(s, a): s.acct = a
new = load(W); rn = {a: new.regime_rows(CX(a)) for a in ("SpaceX", "ZaloPay")}
old = load(OLD); ro = old.regime_rows(CX("SpaceX"))
print(rn["ZaloPay"][0][2] if len(rn["ZaloPay"][0]) > 2 else "NO norm5 row")
ck("SpaceX regime_rows byte-giống master cũ", rn["SpaceX"] == ro)
ck("SpaceX = đúng 2 hàng, không norm5", len(rn["SpaceX"][0]) == 2 and "chuẩn hoá" not in repr(rn["SpaceX"]))
ck("ZaloPay hàng 1-2 == SpaceX hàng 1-2", rn["ZaloPay"][0][:2] == rn["SpaceX"][0][:2])
ck("ZaloPay có hàng norm5 + nhãn không phải tín hiệu", len(rn["ZaloPay"][0]) == 3 and "không phải tín hiệu" in rn["ZaloPay"][0][2][1])
# cache thiếu => fail-safe
import value_radar as v
v.NORM5_CACHE = "/nonexistent/x.csv"; v._NORM5_NOW.update(t=0.0, val=None)
new = load(W)
r = new.regime_rows(CX("ZaloPay"))
ck("cache thiếu: ZaloPay == 2 hàng (chỉ mất dòng phụ)", r[0] == rn["SpaceX"][0] and r[1] is None)
# static
b = open(f"{W}/bin/report_v2/build.py").read()
ck("with_norm5 gắn account==ZaloPay", 'with_norm5=(cx.acct == "ZaloPay")' in b)
print("FAILS", fails); sys.exit(1 if fails else 0)
