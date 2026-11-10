"""Part B v2 (saved script; also generates the Bayes-factor text that the first run produced ad hoc).
Same method as part_b.py. For each ledger x book x window-length H it builds the backtest distribution once, then scores several LIVE variants.
BF_gone_vs_intact = pdf(z_gone)/pdf(z_intact);  z_intact=(live-(alpha+beta*vni_live))/resid_sd (edge intact), z_gone=(live-beta*vni_live)/resid_sd (alpha=0).
Output: part_b_v2.json, part_b_v2_bayes.txt. Interpreter $DNA_PYEXE."""
import gzip, hashlib, io, json
from math import erf, sqrt, exp
import numpy as np, pandas as pd
WC="/home/trido/thanhdt/WorkingClaude"; OUT=f"{WC}/mike/agents/Taylor/research/book_regime_fit_20261110"
LEDGERS={"R3park0":"2026-10-08__R3-park0-pin0pct-SAN__537e349b.csv.gz","park70":"2026-09-28__LICHSU-V2.3A-E1VFVN30-park70-vintage20260625__65e7bb04.csv.gz"}
rng=np.random.default_rng(20261110)
def pa(tag,w): return json.load(open(f"{OUT}/engine/partA_{tag}_{w}.json"))
DIV_ADD = 0.0  # filled below from lag_div files
div = lambda tag,w: float(pd.read_csv(f"{OUT}/engine/lag_div_{tag}_{w}.csv").div_vnd.sum()/pa(tag,w)["LAG"]["nav0"])
# live variants: (label, window, H, LAG ret, BAL ret, VNI ret)
V=[]
for w,H in [("to1109",91),("to1106",90)]:
    for tag in (["ctrl","fixA","fixB"]):
        j=pa(tag,w); V.append((f"{tag}",w,H,j["LAG"]["ret"],j["BAL"]["ret"],j["BAL"]["vni_ret"]))
    j=pa("fixA",w); V.append(("fixA+cashdiv",w,H,j["LAG"]["ret"]+div("fixA",w),j["BAL"]["ret"],j["BAL"]["vni_ret"]))
def load(fn):
    raw=gzip.open(f"{WC}/data/pinned_ledgers/{fn}").read(); assert hashlib.md5(raw).hexdigest()[:8]==fn.split("__")[-1][:8]
    df=pd.read_csv(io.BytesIO(raw),low_memory=False); met=df[df.record_type=="METRIC"].set_index("key")["value"].astype(float)
    d=df[df.record_type=="DAILY"].copy(); d["ymd"]=pd.to_datetime(d["ymd"]); d=d.set_index("ymd")[["nav_bal_ref","nav_lag_ref","combined_nav","vni_close"]].astype(float)
    cagr=(d.combined_nav.iloc[-1]/d.combined_nav.iloc[0])**(365.25/((d.index[-1]-d.index[0]).days))-1
    return d,dict(cagr_recomputed=float(cagr),cagr_metric=float(met["cagr"]),diff=float(abs(cagr-met["cagr"])))
def sbb(r,L,H,B):
    n=len(r); out=np.empty(B)
    for b in range(B):
        idx=[]; i=rng.integers(n)
        while len(idx)<H:
            idx.append(i); i=(i+1)%n if rng.random()>1/L else rng.integers(n)
        out[b]=np.prod(1+r[idx])-1
    return out
Phi=lambda z:0.5*(1+erf(z/sqrt(2)))
res={}; lines=[]
for lab,fn in LEDGERS.items():
    d,chk=load(fn); res[lab]={"control":chk}; vr=d.vni_close.pct_change()
    for H in (90,91):
        for bk,col in [("BAL","nav_bal_ref"),("LAG","nav_lag_ref")]:
            nav=d[col]; r=nav.pct_change(); roll=nav.shift(-H)/nav-1; vroll=d.vni_close.shift(-H)/d.vni_close-1
            ov=pd.DataFrame({"b":roll,"v":vroll}).dropna(); no=ov.iloc[::H]
            X=np.c_[np.ones(len(no)),no.v]; beta=np.linalg.lstsq(X,no.b,rcond=None)[0]; resid=no.b-X@beta; rsd=float(resid.std())
            boot=sbb(r.dropna().values,21,H,20000); q05=np.quantile(no.b,0.05); sd=no.b.std(); mu_null=beta[1]*no.v.mean()
            for (name,w,Hv,lag,bal,vni) in V:
                if Hv!=H: continue
                live=lag if bk=="LAG" else bal
                cond=ov[(ov.v>=-0.12)&(ov.v<=-0.03)]
                lr=live-(beta[0]+beta[1]*vni); zi=lr/rsd; zg=(live-beta[1]*vni)/rsd
                key=f"{name}|{w}|{bk}"
                res[lab][key]=dict(live=float(live),vni=float(vni),H=H,n_nonoverlap=len(no),nonoverlap_min=float(no.b.min()),pct_nonoverlap=float((no.b<=live).mean()),
                    pct_boot=float((boot<=live).mean()),reg_alpha=float(beta[0]),reg_beta=float(beta[1]),live_pred=float(beta[0]+beta[1]*vni),live_resid=float(lr),
                    pct_resid=float((resid<=lr).mean()),z_intact=float(zi),z_gone=float(zg),BF_gone_vs_intact=float(exp(-0.5*(zg**2-zi**2))),
                    cond_pct=float((cond.b<=live).mean()),cond_n_indep=int(len(cond)/H),pct_excess_nonoverlap=float(((no.b-no.v)<=live-vni).mean()),
                    power_detect_edge_gone_5pct=float(Phi((q05-mu_null)/sd)))
                x=res[lab][key]; lines.append(f"{lab:8s} {key:28s} live {live*100:6.2f}% pred {x['live_pred']*100:6.2f}% pct_resid {x['pct_resid']*100:5.1f}% boot {x['pct_boot']*100:5.1f}% cond {x['cond_pct']*100:5.1f}% z_intact {zi:5.2f} z_alpha0 {zg:5.2f} BF {x['BF_gone_vs_intact']:.2f} power {x['power_detect_edge_gone_5pct']*100:.0f}%")
json.dump(res,open(f"{OUT}/part_b_v2.json","w"),indent=1); open(f"{OUT}/part_b_v2_bayes.txt","w").write("\n".join(lines)); print("\n".join(lines))
for lab in res: print(lab,res[lab]["control"])
