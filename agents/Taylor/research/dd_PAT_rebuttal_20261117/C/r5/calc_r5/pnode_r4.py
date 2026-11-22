import math
from statistics import NormalDist
N=NormalDist()
S0=27740.0
# F2 quantiles (sector_read line 136): P10 20500, P32 23000, P50 25000, P66 28466, P90 32000 (branch-defining; 80% interval top 31500 conflicts)
def fit(qpts, sig_lo_pt, sig_hi_pt):
    # piecewise log-linear CDF between quantile points; lognormal tails (median 25000, sigma fitted to outer quantile each side)
    med=25000.0
    sL=math.log(med/sig_lo_pt[0])/(-N.inv_cdf(sig_lo_pt[1]))
    sU=math.log(sig_hi_pt[0]/med)/(N.inv_cdf(sig_hi_pt[1]))
    mu=math.log(med)
    def tail_low_mean(x,s):  # E[S|S<x] lognormal
        return math.exp(mu+s*s/2)*N.cdf((math.log(x)-mu-s*s)/s)/N.cdf((math.log(x)-mu)/s)
    def tail_high_mean(x,s):
        return math.exp(mu+s*s/2)*(1-N.cdf((math.log(x)-mu-s*s)/s))/(1-N.cdf((math.log(x)-mu)/s))
    segs=[]  # (mass, mean)
    lo=qpts[0]; segs.append((lo[1], tail_low_mean(lo[0],sL), 'tailL'))
    for (a,pa),(b,pb) in zip(qpts[:-1],qpts[1:]):
        segs.append((pb-pa,(b-a)/(math.log(b)-math.log(a)),(a,b)))
    hi=qpts[-1]; segs.append((1-hi[1], tail_high_mean(hi[0],sU),'tailH'))
    return segs,sL,sU
def branch_means(segs, cuts=(23000,32000)):
    L=[s for s in segs if (s[2]=='tailL') or (isinstance(s[2],tuple) and s[2][1]<=cuts[0])]
    H=[s for s in segs if (s[2]=='tailH')]
    M=[s for s in segs if s not in L and s not in H]
    f=lambda g:(sum(m for m,_,_ in g), sum(m*v for m,v,_ in g)/sum(m for m,_,_ in g))
    return f(L),f(M),f(H)
for name,q in (('base all-F2 pts (P90=32000)',[(20500,.10),(23000,.32),(25000,.50),(28466,.66),(32000,.90)]),
               ('alt P90=31500',[(20500,.10),(23000,.32),(25000,.50),(28466,.66),(31500,.90)])):
    segs,sL,sU=fit(q,q[0],q[-1])
    (pL,mL),(pM,mM),(pH,mH)=branch_means(segs) if name.startswith('base') else branch_means(segs,(23000,31500))
    xL,xM,xH=mL/S0-1,mM/S0-1,mH/S0-1
    # eps least squares (prob-weighted) to reproduce r3 tails 0.937 / 1.063
    eps=(pL*xL*(-0.063)+pH*xH*0.063)/(pL*xL*xL+pH*xH*xH)
    print(name, f"sL {sL:.4f} sU {sU:.4f} | probs {pL:.2f}/{pM:.2f}/{pH:.2f} | means {mL:.0f}/{mM:.0f}/{mH:.0f} | x {xL:+.4f}/{xM:+.4f}/{xH:+.4f} | eps {eps:.4f}")
    print('  mapped p:', round(1+eps*xL,4), round(1+eps*xM,4), round(1+eps*xH,4), ' E[p]=', round(pL*(1+eps*xL)+pM*(1+eps*xM)+pH*(1+eps*xH),4))
# pessimist lognormal check (sigma 0.168 median 25000)
mu=math.log(25000); s=0.168
def cm(a,b):
    za=(math.log(a)-mu)/s if a>0 else -1e9; zb=(math.log(b)-mu)/s if b<1e12 else 1e9
    za2=za-s; zb2=zb-s
    return math.exp(mu+s*s/2)*(N.cdf(zb2)-N.cdf(za2))/(N.cdf(zb)-N.cdf(za)), N.cdf(zb)-N.cdf(za)
for a,b in ((1,23000),(23000,32000),(32000,1e13)):
    m,p=cm(a,b); print('lognorm .168',a,b,round(p,3),round(m),round(m/S0,4))
print('freight', 22.843840946/487.507728152, 66.866/1738.334, (66.866+22.844)/(1738.334+487.508))
print('HTK excess', 120.190-(84.700+67.712+74.843)/3, 'NVL', 49.738-(18.755+22.197+21.049)/3,'TP',70.448-(65.932+45.514+53.794)/3)
