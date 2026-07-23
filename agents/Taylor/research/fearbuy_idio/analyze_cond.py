import pandas as pd, numpy as np
df = pd.read_csv('episodes_idio.csv')
def stat(sub,col='ex24m',rcol='r24m'):
    s=sub[sub[col].notna()]
    if len(s)<8: return f"N={len(s)} (thin)"
    return f"N={len(s):>4} med_ex={s[col].median()*100:>6.1f}% winr={ (s[col]>0).mean()*100:>3.0f}% med_r={s[rcol].median()*100:>6.1f}% mean_r={s[rcol].mean()*100:>6.1f}%"

print("=== CONDITIONAL CUTS on ex24m (finding the discriminator) ===")
print("ALL                :", stat(df))
print("\n-- Cheapness (PB) --")
for lo,hi in [(0,0.7),(0.7,1.0),(1.0,1.5),(1.5,99)]:
    print(f"PB [{lo},{hi})       :", stat(df[(df.PB>=lo)&(df.PB<hi)]))
print("\n-- Leverage (Debt_Eq_P0) --")
for lo,hi in [(0,0.5),(0.5,1.0),(1.0,2.5),(2.5,99)]:
    print(f"DE [{lo},{hi})       :", stat(df[(df.DE>=lo)&(df.DE<hi)]))
print("\n-- Net margin (NPM_P0) --")
for lo,hi in [(-99,0.05),(0.05,0.10),(0.10,0.20),(0.20,99)]:
    print(f"NPM [{lo},{hi})      :", stat(df[(df.NPM>=lo)&(df.NPM<hi)]))
print("\n-- Liquidity (ADV VND) --")
for lo,hi in [(0,1e9),(1e9,5e9),(5e9,20e9),(20e9,1e15)]:
    print(f"ADV [{lo:.0e},{hi:.0e}) :", stat(df[(df.adv_vnd>=lo)&(df.adv_vnd<hi)]))
print("\n-- COMBINED discriminator: PB<1.0 & DE<=2.5 & NPM>=0.05 & ADV>=5B --")
q=df[(df.PB<1.0)&(df.DE<=2.5)&(df.NPM>=0.05)&(df.adv_vnd>=5e9)]
print("QUALIFY-ish        :", stat(q))
for h in ['ex12m','ex18m','ex24m','ex36m']:
    print(f"   {h}: med={q[q[h].notna()][h].median()*100:.1f}% winr={(q[q[h].notna()][h]>0).mean()*100:.0f}% N={q[h].notna().sum()}")
print("\n-- Even tighter: PB<0.9 & DE<=1.5 & NPM>=0.08 & ADV>=10B --")
q2=df[(df.PB<0.9)&(df.DE<=1.5)&(df.NPM>=0.08)&(df.adv_vnd>=10e9)]
print("QUALIFY-tight      :", stat(q2))
print("names:", sorted(q2.ticker.unique().tolist()))
