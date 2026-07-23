import numpy as np
def kelly_opt(payoffs):
    best_f,best_v=0,-1e9
    for f in np.linspace(0,1,2001):
        v=np.mean(np.log1p(f*payoffs))
        if np.isfinite(v) and v>best_v: best_v,best_f=v,f
    return best_f

print("=== TV1 asset-backed: loser payoff floored by SOTP (Song Bung 5 hydro) ===")
print("Pure-fear loser=-70%; asset-backed loser ~ -25% (physical-asset floor). Winner ~ +66% (SOTP close).")
for L,lbl in [(-0.70,'pure-fear'),(-0.35,'part-backed'),(-0.25,'asset-backed(TV1)')]:
    for p in [0.45,0.55,0.65]:
        W=0.66
        payoffs=np.array([W]*int(p*10000)+[L]*int((1-p)*10000))
        f=kelly_opt(payoffs)
        print(f"  L={L*100:>4.0f}% p={p} W=+66% -> full-Kelly={f:.2f} quarter={f/4:.3f} NAV")
    print()

print("=== SLEEVE-CAP worst-case (total NAV across simultaneous names) ===")
NAV=1.816e9
for cap_names,per in [(2,0.010),(3,0.010),(3,0.015),(4,0.0075)]:
    tot=cap_names*per
    # worst: all NON blended -70%; catastrophic all FLC -100%
    print(f"  {cap_names} names x {per*100:.2f}% = {tot*100:.1f}% NAV gross | all-NON(-70%): {-tot*0.70*100:.2f}pp | all-FLC(-100%): {-tot*100:.2f}pp")

print("\n=== FREQUENCY reconciliation: mechanical vs TRUE-qualified ===")
print("Mechanical -40%-idio quality-floor: ~64/yr (mostly value-traps + cyclicals, median LOSES).")
print("TRUE idiosyncratic-scandal-with-separable-core (case library 2014-2026):")
lib={'2015':['PNJ(win)','JVC(loss)'],'2019':['VEA(win)'],'2020':['DGC~(covid-blend)'],
     '2022':['FLC(loss)'],'2026':['TV1','DGC','PNJ','JVC?']}
tot=0
for y,c in lib.items(): print(f"   {y}: {c}"); tot+=len(c)
print(f"  ~{tot} labeled cases / ~12yr ≈ 0.7-1.5 genuine QUALIFY-grade/yr, often 0; clusters when a crackdown wave hits (2026).")
