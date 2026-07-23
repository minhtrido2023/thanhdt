import numpy as np
# Kelly on the mechanical panel first (base rate, no DD skill)
import pandas as pd
df=pd.read_csv('episodes_idio.csv')
r24=df[df.r24m.notna()].r24m.values
def kelly_opt(payoffs, pos_frac=None):
    # numerically maximize E[log(1+f R)] over f in [0,1]
    best_f, best_v = 0, -1e9
    for f in np.linspace(0,1.0,2001):
        v=np.mean(np.log1p(f*payoffs))
        if np.isfinite(v) and v>best_v: best_v, best_f = v, f
    return best_f, best_v
f_mech,_=kelly_opt(r24)
print(f"MECHANICAL panel r24m: N={len(r24)} mean={r24.mean()*100:.0f}% median={np.median(r24)*100:.0f}% winr(>0)={(r24>0).mean()*100:.0f}%")
print(f"  -> full-Kelly f* on raw mechanical panel = {f_mech:.3f}  (of bankroll, per bet)")
print(f"  Interpretation: mechanical idiosyncratic bet Kelly ~ {f_mech:.2f} -> mechanical screen alone barely positive/zero\n")

# Case-library / DD-conditional: winner vs loser two-point, vary DD hit-rate p and winner magnitude
losers = -0.70   # mean NON (OGC/PVX/HVN/JVC/FIT/FLC blended)
print("=== DD-CONDITIONAL KELLY: f* as function of (win-rate p, winner payoff W) ===")
print("Assumes binary outcome per bet: prob p -> +W (24m), prob 1-p -> loser -70%.")
print(f"{'W(win)':>8} | " + " ".join(f"p={p:.2f}" for p in [0.30,0.40,0.50,0.60,0.70]))
for W in [0.50,0.80,1.20,2.49]:
    row=[]
    for p in [0.30,0.40,0.50,0.60,0.70]:
        payoffs=np.array([W]*int(p*10000)+[losers]*int((1-p)*10000))
        f,_=kelly_opt(payoffs)
        row.append(f"{f:>5.2f}")
    print(f"{W*100:>6.0f}% | "+" ".join(row))

print("\n=== BREAK-EVEN win-rate p* (EV=0): p*=|L|/(W+|L|), L=-70% ===")
for W in [0.22,0.50,0.80,1.20,2.49]:
    print(f"  W={W*100:>5.0f}% -> need p > {0.70/(W+0.70)*100:>4.0f}%")

print("\n=== RECOMMENDED SIZE (quarter-Kelly, conservative) at NAV=1.82B ===")
# take a 'central honest' scenario: p=0.50 (DD roughly coin-flip-plus), W=+100% blended winner
for p,W,lbl in [(0.45,0.80,'pessimistic'),(0.50,1.00,'central'),(0.60,1.50,'optimistic')]:
    payoffs=np.array([W]*int(p*10000)+[losers]*int((1-p)*10000))
    f,_=kelly_opt(payoffs)
    print(f"  {lbl:>11}: p={p} W={W*100:.0f}% -> full-Kelly f*={f:.2f}  half={f/2:.2f}  quarter={f/4:.3f} of NAV/name")
