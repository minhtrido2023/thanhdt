import pandas as pd, numpy as np
from scipy import stats
df=pd.read_csv("mike/agents/Taylor/research/fearbuy_blend/panel.csv")
df['adv_b']=df['adv_vnd']/1e9
df['s']=-df['mkt_dd']   # stress, positive; larger=worse

CRISIS_YEARS=[2008,2009,2010,2011,2012,2020,2022,2023,2025]  # deep-dd episodes cluster here

def summ(sub, col='ex24'):
    x=sub[col].dropna()
    if len(x)==0: return dict(N=0,med=np.nan,mean=np.nan,wr=np.nan)
    return dict(N=len(x), med=x.median()*100, mean=x.mean()*100, wr=(x>0).mean()*100)

def signtest(sub, col='ex24', years=None):
    years = years or sorted(sub.yr.unique())
    med=[]
    for y in years:
        xx=sub[sub.yr==y][col].dropna()
        if len(xx)>=2: med.append(xx.median())
    if len(med)<3: return None
    pos=sum(1 for m in med if m>0)
    p=stats.binomtest(pos,len(med),0.5,alternative='greater').pvalue
    return pos,len(med),p,[round(m*100) for m in med]

def report(name, sub, col='ex24'):
    s=summ(sub,col); st=signtest(sub,col)
    line=f"{name:<42} N={s['N']:<5} med={s['med']:+6.1f}%  mean={s['mean']:+7.1f}%  wr={s['wr']:4.0f}%"
    if st: line+=f"  sign {st[0]}/{st[1]} p={st[2]:.3f}"
    print(line)

print("="*110)
print("BASELINE gates (col=ex24, 24m excess vs VNINDEX)")
print("="*110)
report("ALL panel (dd<-15%,PB<1.6,gates)", df)
report("Binary v1 (dd<-30 & PB<0.7)", df[(df.mkt_dd<-0.30)&(df.PB<0.7)])
report("Binary v1 + DE<=2.5", df[(df.mkt_dd<-0.30)&(df.PB<0.7)&(df.DE<=2.5)])

print("\n"+"="*110)
print("ADAPTIVE THRESHOLD:  qualify if PB <= PBmax(s),  PBmax = clip(pb_hi - slope*(s-s0), pb_lo, pb_hi), s>=s_min")
print("  (worse market s bigger -> PBmax lower -> must be cheaper).  Grid, col=ex24")
print("="*110)
def adaptive_mask(df, s_min, s0, pb_hi, pb_lo, slope):
    pbmax=np.clip(pb_hi - slope*(df.s - s0), pb_lo, pb_hi)
    return (df.s>=s_min) & (df.PB<=pbmax)
grid=[
 # s_min, s0, pb_hi, pb_lo, slope
 (0.15,0.15,1.00,0.40,2.0),
 (0.15,0.15,1.00,0.40,1.5),
 (0.15,0.15,0.90,0.35,2.0),
 (0.20,0.20,1.00,0.40,2.0),
 (0.20,0.20,0.90,0.40,1.7),
 (0.20,0.15,0.85,0.40,1.5),
 (0.25,0.20,0.90,0.40,2.0),
]
for g in grid:
    m=adaptive_mask(df,*g)
    report(f"adapt s_min{g[0]} s0{g[1]} hi{g[2]} lo{g[3]} k{g[4]}", df[m])

print("\n"+"="*110)
print("BLUE-CHIP interaction (ADV floor).  Rule = Binary v1 (dd<-30&PB<0.7) then ADV cut")
print("="*110)
b=df[(df.mkt_dd<-0.30)&(df.PB<0.7)]
for adv in [0,2,5,10,20]:
    report(f"v1 + ADV>={adv}B", b[b.adv_b>=adv])

print("\n"+"="*110)
print("BLUE-CHIP + ADAPTIVE (chosen adaptive s_min.20 s0.20 hi1.0 lo.40 k2.0) x ADV floor")
print("="*110)
ad=df[adaptive_mask(df,0.20,0.20,1.00,0.40,2.0)]
for adv in [0,2,5,10,20]:
    report(f"adaptive + ADV>={adv}B", ad[ad.adv_b>=adv])
