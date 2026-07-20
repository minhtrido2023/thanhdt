import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
X = pd.read_csv("/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_capitdcf/pool_dcf.csv")
K = 5
def select(g, v):
    g = g.sort_values(["pbz","ticker"], kind="mergesort")
    if v == "base": return g.head(K)
    if v == "hard":
        keep = g[~g.rich]; return (keep if len(keep) >= 3 else g).head(K)
    return g.sort_values(["rich"], kind="mergesort").head(K)

print("=== Events where HARD changes the basket ===")
for ev, g in X.groupby("event"):
    b, h = select(g,"base"), select(g,"hard")
    if set(b.ticker) != set(h.ticker):
        dropped = sorted(set(b.ticker)-set(h.ticker)); added = sorted(set(h.ticker)-set(b.ticker))
        print(f"{ev}: -{','.join(dropped)} +{','.join(added)}")
        for hh in (60,120,250):
            print(f"    h{hh}: base={b[f'r{hh}'].mean():+.3f} hard={h[f'r{hh}'].mean():+.3f} "
                  f"delta={h[f'r{hh}'].mean()-b[f'r{hh}'].mean():+.3f}")

print("\n=== Leave-one-event-out: mean(hard-base) delta ===")
print(f"{'drop_event':<14}{'h60':>9}{'h120':>9}{'h250':>9}")
per = {ev: {hh: select(g,"hard")[f'r{hh}'].mean()-select(g,"base")[f'r{hh}'].mean()
            for hh in (60,120,250)} for ev, g in X.groupby("event")}
allev = sorted(per)
print(f"{'(none)':<14}" + "".join(f"{np.mean([per[e][hh] for e in allev]):>9.4f}" for hh in (60,120,250)))
for drop in allev:
    rest = [e for e in allev if e != drop]
    print(f"{drop:<14}" + "".join(f"{np.mean([per[e][hh] for e in rest]):>9.4f}" for hh in (60,120,250)))

print("\n=== K-sensitivity of hard-base delta (h250) ===")
for k in (3,4,5,6,8):
    K = k
    ds = [select(g,"hard")['r250'].mean()-select(g,"base")['r250'].mean() for _, g in X.groupby("event")]
    ch = sum(1 for _, g in X.groupby("event") if set(select(g,'base').ticker)!=set(select(g,'hard').ticker))
    print(f"  K={k}: delta={np.mean(ds):+.4f}  changed_events={ch}/14")
