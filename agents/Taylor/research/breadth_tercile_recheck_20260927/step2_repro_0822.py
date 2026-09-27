"""JOB E Buoc 2 -- tai lap so GOC cua quyet dinh 08-22 tu artifact goc.
Nguon: research/strategy_regime_matrix_20260822/{b2_breadth.csv, panel_daily.csv}
KHONG dung lai script goc (b2.py khong con) -- tai lap doc lap theo mo ta trong bao cao."""
import numpy as np, pandas as pd
SRC="/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/strategy_regime_matrix_20260822"

br=pd.read_csv(f"{SRC}/b2_breadth.csv",parse_dates=["time"]).sort_values("time").reset_index(drop=True)
pa=pd.read_csv(f"{SRC}/panel_daily.csv",low_memory=False)
pa=pa[pa.record_type=="DAILY"].copy()
pa["time"]=pd.to_datetime(pa["time"])
pa=pa[["time","r_comb","r_bal","r_lag","r_vni","regime","zone","cap_bal","cap_lag","combined_nav"]].dropna(subset=["r_vni"])
print(f"b2_breadth: {len(br)} phien {br.time.min().date()}->{br.time.max().date()}  n_univ median={br.n_univ.median():.0f} min={br.n_univ.min()} max={br.n_univ.max()}")
print(f"panel_daily DAILY: {len(pa)} phien {pa.time.min().date()}->{pa.time.max().date()}")

# --- VARIANT A: nhu bao cao goc §1 = phan vi cua breadth_t trong 252 phien TRUOC DO (khong gom t)
b=br.set_index("time")["breadth"]
prior=b.shift(1).rolling(252,min_periods=252)
# rank cua gia tri hom nay trong 252 gia tri truoc: dem bao nhieu gia tri truoc < breadth_t
cnt=pd.Series(np.nan,index=b.index)
vals=b.to_numpy()
for i in range(252,len(vals)):
    w=vals[i-252:i]
    cnt.iloc[i]=(w<vals[i]).sum()/253.0   # /253 = quy uoc TIE cua ban goc 08-22:
    # do 5 quy uoc, chi "(# trong 252 phien truoc < breadth_t)/253" tai lap DUNG
    # LOW 1232 / MID 897 (so goc). Xem step2_tie_probe trong bao cao §2.
br["pct_A"]=cnt.to_numpy()
# --- VARIANT B: nhu quy uoc da codify (context_pack) + h5_ic.py = phan vi cua breadth_{t-1}
#     trong 252 gia tri breadth_lag gan nhat  == chinh la "tre nhan 1 phien" (§5a cua bao cao goc)
br["pct_B"]=b.shift(1).rolling(252,min_periods=252).rank(pct=True).to_numpy()
# pd.cut([0,1/3,2/3,1]) BO ROI pct==0.0 (63 phien breadth thap nhat lich su) -> dung nguong
# tuong minh, 0.0 thuoc LOW. Day la lech duy nhat so voi lan chay dau, da xac nhan bang
# KHOI 1 (1169+63 = 1232 = dung so goc).
for v in ["A","B"]:
    p=br[f"pct_{v}"]
    br[f"ter_{v}"]=pd.Series(np.select([p<1/3,p<2/3,p<=1.0],["LOW","MID","HIGH"],default=None),
                             index=br.index).where(p.notna())

d=pa.merge(br[["time","breadth","ter_A","ter_B"]],on="time",how="left")
print(f"\nmerge: {len(d)} phien; thieu breadth={d.breadth.isna().sum()}; thieu ter_A={d.ter_A.isna().sum()}; thieu ter_B={d.ter_B.isna().sum()}")

print("\n=== KHOI 1: phan bo tercile (goc: LOW 1.232 / MID 897 / HIGH 978) ===")
for v in ["A","B"]:
    vc=d[f"ter_{v}"].value_counts()
    print(f"  variant {v}: LOW {vc.get('LOW',0)} / MID {vc.get('MID',0)} / HIGH {vc.get('HIGH',0)}  tong={vc.sum()}")

def episodes(lbl):
    s=lbl.dropna(); return int((s!=s.shift()).sum())
def dom_share(df,col):
    """% so nam bi MOT nhan chiem >=90% phien + share nhan troi trung binh"""
    rows=[]
    for y,g in df.dropna(subset=[col]).groupby(df.time.dt.year):
        sh=g[col].value_counts(normalize=True)
        rows.append((y,sh.max()))
    r=pd.DataFrame(rows,columns=["y","max_share"])
    return (r.max_share>=0.90).mean()*100, r.max_share.mean()*100, r

print("\n=== KHOI 2: n_effective (goc: breadth 262 ep / radar 131; 0% vs 54% nam bi 1 nhan >=90%) ===")
for name,col in [("breadth ter_A","ter_A"),("breadth ter_B","ter_B"),("radar zone","zone")]:
    pc,avg,r=dom_share(d,col)
    # episode tinh tren O = regime x nhan
    cells=d.dropna(subset=[col,"regime"]).copy()
    cells["cell"]=cells["regime"].astype(str)+"|"+cells[col].astype(str)
    tot_ep=episodes(cells["cell"]); ncell=cells["cell"].nunique()
    yrs=cells.groupby("cell").apply(lambda g: g.time.dt.year.nunique(),include_groups=False)
    print(f"  {name:14s}: {pc:.0f}% nam bi 1 nhan >=90% | share troi TB {avg:.0f}% | o={ncell} | tong episode={tot_ep} | nam/o median={yrs.median():.0f}")

def cagr(r):
    r=r.dropna().to_numpy()
    if len(r)<10: return np.nan
    return (np.prod(1+r))**(252/len(r))-1

print("\n=== KHOI 3: marginal excess theo tercile (goc A: LOW +27,1 / MID +10,8 / HIGH +5,4 pp) ===")
for v in ["A","B"]:
    print(f"\n  --- variant {v} ---")
    print(f"  {'tile':5s} {'phien':>6s} {'ep':>4s} {'VNI':>8s} {'COMB':>8s} {'excess':>8s} {'IS_exc':>8s} {'OOS_exc':>8s}")
    for t in ["LOW","MID","HIGH"]:
        s=d[d[f"ter_{v}"]==t]
        ep=episodes(d[f"ter_{v}"].where(d[f"ter_{v}"]==t))
        ep=int(((d[f"ter_{v}"]==t)&(d[f"ter_{v}"].shift()!=t)).sum())
        vni,comb=cagr(s.r_vni),cagr(s.r_comb)
        isw=s[s.time<"2020-01-01"]; oos=s[s.time>="2020-01-01"]
        e_is=cagr(isw.r_comb)-cagr(isw.r_vni); e_oos=cagr(oos.r_comb)-cagr(oos.r_vni)
        print(f"  {t:5s} {len(s):6d} {ep:4d} {vni*100:+7.1f}% {comb*100:+7.1f}% {(comb-vni)*100:+7.1f}pp {e_is*100:+7.1f}pp {e_oos*100:+7.1f}pp")

print("\n=== KHOI 3b: LOO theo nam tren excess (goc A: LOW +23,4..+31,9 / MID +3,3..+11,1 / HIGH +0,4..+5,5; 13/13 nam khong dao dau) ===")
for v in ["A"]:
    yrs=sorted(d.time.dt.year.unique())
    for t in ["LOW","MID","HIGH"]:
        vs=[]
        for y in yrs:
            s=d[(d[f"ter_{v}"]==t)&(d.time.dt.year!=y)]
            vs.append(cagr(s.r_comb)-cagr(s.r_vni))
        vs=np.array(vs)*100
        print(f"  {t:5s} LOO n_nam={len(yrs)} min={vs.min():+.1f}pp max={vs.max():+.1f}pp  dao dau={'CO' if (vs>0).sum() not in (0,len(vs)) else 'KHONG'}")

print("\n=== KHOI 4: §5b khu beta (goc: alpha LOW +16,3 < MID +20,2 < HIGH +28,1 -- DAO thu tu) ===")
for v in ["A"]:
    print(f"  {'tile':5s} {'beta':>6s} {'COMB':>8s} {'VNI':>8s} {'excess':>8s} {'alpha':>8s}")
    for t in ["LOW","MID","HIGH"]:
        s=d[d[f"ter_{v}"]==t].dropna(subset=["r_comb","r_vni"])
        beta=np.cov(s.r_comb,s.r_vni)[0,1]/np.var(s.r_vni)
        comb,vni=cagr(s.r_comb),cagr(s.r_vni)
        print(f"  {t:5s} {beta:6.2f} {comb*100:+7.1f}% {vni*100:+7.1f}% {(comb-vni)*100:+7.1f}pp {(comb-beta*vni)*100:+7.1f}pp")

d.to_csv("step2_panel_labelled.csv",index=False)
print("\nSELF-CHECK no-look-ahead goc bao +0,109 = corr(pct252_t, r_vni_t):")
for v in ["A","B"]:
    m=d.dropna(subset=[f"pct_{v}"] if f"pct_{v}" in d else []) 
print("  (tinh tren br truc tiep)")
m=br.merge(pa[["time","r_vni"]],on="time",how="inner").dropna(subset=["pct_A","r_vni"])
print(f"  variant A: corr(pct_A_t, r_vni_t) = {m.pct_A.corr(m.r_vni):+.4f}   (goc: +0,1088)")
m2=br.merge(pa[["time","r_vni"]],on="time",how="inner").dropna(subset=["pct_B","r_vni"])
print(f"  variant B: corr(pct_B_t, r_vni_t) = {m2.pct_B.corr(m2.r_vni):+.4f}   (ky vong ~0 vi nhan tre 1 phien)")
