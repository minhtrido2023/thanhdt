"""JOB E Buoc 3+4 -- IC dieu kien hoa tren CUA SO DAI NHAT + 3 truc cung khuon.
Phuong phap giu NGUYEN cua h5_ic.py (khong doi cong thuc), chi doi CUA SO va them 2 truc.
PAPER-ONLY. Prereg: PREREG.md §3-4."""
import numpy as np, pandas as pd, duckdb
WC="/home/trido/thanhdt/WorkingClaude"
H5=f"{WC}/mike/agents/Taylor/research/fiinprox_h4_h5_20260927"
B22=f"{WC}/mike/agents/Taylor/research/strategy_regime_matrix_20260822"
c=duckdb.connect()

# ---------- panel: chi thanh vien universe_pit PIT (§9b: khong dung danh sach toan lich su)
q=f"""
SELECT t.time AS date, t.ticker, t.Close, t.MA200, t.PE
FROM read_parquet('{WC}/data/bq_cache/ticker/*.parquet') t
JOIN read_parquet('{WC}/data/bq_cache/universe_pit_q/*.parquet') u
  ON u.time=t.time AND u.ticker=t.ticker AND u.in_universe
WHERE t.ticker<>'VNINDEX' AND t.Close>0
"""
p=c.execute(q).df(); p["date"]=pd.to_datetime(p["date"])
p=p.sort_values(["ticker","date"]).reset_index(drop=True)
print(f"panel rows={len(p):,}  tickers={p.ticker.nunique()}  {p.date.min().date()}->{p.date.max().date()}")

g=p.groupby("ticker",sort=False)["Close"]
p["mom_200"]=g.transform(lambda s: s/s.shift(200)-1)
p["fwd_1m"]=g.transform(lambda s: s.shift(-21)/s-1)
p["ey"]=np.where(p["PE"]>0, 1.0/p["PE"], np.nan)
p["above_ma200"]=(p["Close"]>p["MA200"]).astype(float)

# ---------- TRUC 1: breadth-tercile PIT (quy uoc 08-22 nhu da codify: nhan = breadth_{t-1})
# MAU SO breadth chi tinh ma co MA200 HOP LE. bq_cache/ticker co MA200=NULL cho phan lon
# ma trong 2015-2017 (median 137/ngay nam 2016, toi da 199/296) -- dem chung vao mau so nhu
# "khong above" lam breadth 2016 tut tu 0,73 xuong 0,24 (max|delta| 0,487 so voi ban goc).
# Ban 08-22 doc BQ live va loai san cac dong nay (n_univ 2016 = 89, dung bang so ma co MA200).
ma_ok=p["MA200"].notna()&(p["MA200"]>0)
nden=p[ma_ok].groupby("date").size()
br=p[ma_ok].groupby("date")["above_ma200"].mean().rename("breadth").to_frame()
br["n_den"]=nden
br["breadth_lag"]=br["breadth"].shift(1)
br["pctile"]=br["breadth_lag"].rolling(252,min_periods=252).rank(pct=True)
br["breadth_ter"]=pd.Series(np.select([br.pctile<1/3,br.pctile<2/3,br.pctile<=1.0],
                                      ["LOW","MID","HIGH"],default=None),
                            index=br.index).where(br.pctile.notna())

# SELF-CHECK 1 (prereg §3): chuoi breadth tu dung phai khop b2_breadth.csv tren doan chong lap
b0=pd.read_csv(f"{B22}/b2_breadth.csv",parse_dates=["time"]).set_index("time")["breadth"]
ov=br["breadth"].to_frame().join(b0.rename("b0"),how="inner").dropna()
print(f"  mau so breadth: median={br.n_den.median():.0f} min={br.n_den.min()} max={br.n_den.max()}; "
      f"so phien mau so <100: {(br.n_den<100).sum()}")
print(f"\nSELF-CHECK 1 breadth vs b2_breadth.csv ({len(ov)} phien chong lap "
      f"{ov.index.min().date()}->{ov.index.max().date()}): corr={ov.breadth.corr(ov.b0):.6f}  "
      f"max|delta|={np.abs(ov.breadth-ov.b0).max():.6f}  mean|delta|={np.abs(ov.breadth-ov.b0).mean():.6f}")

# ---------- TRUC 2: retail_net_share (H5; tran nguon 2016-04, nguon chet 28/09/2026)
mon=pd.read_csv(f"{H5}/h5_retail_monthly.csv",parse_dates=["date"]).set_index("date")
mon["lagged"]=mon["retail_net_share_m"].shift(1)
mon["pctile"]=mon["lagged"].rolling(24,min_periods=24).rank(pct=True)
mon["retail_ter"]=pd.Series(np.select([mon.pctile<1/3,mon.pctile<2/3,mon.pctile<=1.0],
                                      ["LOW","MID","HIGH"],default=None),
                            index=mon.index).where(mon.pctile.notna())

# ---------- TRUC 3: DT5G state (PRODUCTION table, KHONG dung vnindex_5state = v3.4b BASE)
dt=pd.read_csv(f"{WC}/data/vnindex_5state_dt5g_live.csv",parse_dates=["time"])
NAME={1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EXBULL"}
dt["dt5g"]=dt["state"].map(NAME)
dt["dt5g"]=dt["dt5g"].shift(1)            # PIT: phien t dung state cong bo cua t-1
dt=dt[["time","dt5g"]].rename(columns={"time":"date"})

ax=br.reset_index()[["date","breadth_ter"]].copy()
ax["ym"]=ax["date"].values.astype("datetime64[M]")
ax=ax.merge(mon.reset_index()[["date","retail_ter"]].rename(columns={"date":"ym"}),on="ym",how="left")
ax=ax.merge(dt,on="date",how="left")

# ---------- IC cross-sectional Spearman theo ngay
def daily_ic(df,fac):
    s=df.dropna(subset=[fac,"fwd_1m"])
    if len(s)<30: return np.nan
    return s[fac].corr(s["fwd_1m"],method="spearman")
ics=p.groupby("date").apply(lambda df: pd.Series({"ic_mom":daily_ic(df,"mom_200"),
                                                  "ic_ey":daily_ic(df,"ey"),
                                                  "n":len(df)}),include_groups=False).reset_index()
ics=ics.merge(ax[["date","breadth_ter","retail_ter","dt5g"]],on="date",how="left")
FWD_END="2026-08-26"      # cache het 2026-09-25, fwd_1m can +21 phien
ics=ics[(ics.date>="2014-01-01")&(ics.date<=FWD_END)]
ics.to_csv("step3_daily_ic.csv",index=False)
print(f"\nIC daily: {len(ics)} phien {ics.date.min().date()}->{ics.date.max().date()} "
      f"({(ics.date.max()-ics.date.min()).days/365.25:.1f} nam); ic_mom NaN={ics.ic_mom.isna().sum()}, ic_ey NaN={ics.ic_ey.isna().sum()}")

def block_boot(x, months, B=4000, seed=7):
    rng=np.random.default_rng(seed); um=months.unique(); idx={m:np.where(months.to_numpy()==m)[0] for m in um}
    out=np.empty(B)
    for b in range(B):
        take=np.concatenate([idx[m] for m in rng.choice(um,len(um),replace=True)])
        out[b]=np.nanmean(x[take])
    return out
def episodes(s):
    s=s.reset_index(drop=True); return int((s!=s.shift()).sum())

def cell_stats(w,col,order):
    rows=[]
    for t in order:
        s=w[w[col]==t]
        if not len(s): continue
        rows.append(dict(cell=t,n_day=len(s),n_mon=s.date.dt.to_period("M").nunique(),
                         n_ep=episodes(w[col].where(w[col]==t).dropna().reindex(w.index).dropna()
                                       if False else (w[col]==t).astype(int)[(w[col]==t)|(w[col]!=t)]),
                         ic_mom=np.nanmean(s.ic_mom),ic_ey=np.nanmean(s.ic_ey)))
    return pd.DataFrame(rows)

def hi_lo(w,col,hi_set,lo_set,fac):
    hi=w[w[col].isin(hi_set)]; lo=w[w[col].isin(lo_set)]
    if not len(hi) or not len(lo): return None
    diff=np.nanmean(hi[fac])-np.nanmean(lo[fac])
    bd=block_boot(hi[fac].to_numpy(),hi.date.dt.to_period("M")) - \
       block_boot(lo[fac].to_numpy(),lo.date.dt.to_period("M"))
    ci=np.percentile(bd,[2.5,97.5])
    p=2*min((bd<=0).mean(),(bd>=0).mean())
    return diff,ci,max(p,1/4000)

def bh(pv):
    pv=np.asarray(pv,float); m=len(pv); o=np.argsort(pv); adj=np.empty(m)
    prev=1.0
    for k in range(m-1,-1,-1):
        prev=min(prev,pv[o[k]]*m/(k+1)); adj[o[k]]=prev
    return adj

AXES=[("breadth",  "breadth_ter",["LOW","MID","HIGH"],                        ["HIGH"],["LOW"]),
      ("retail",   "retail_ter", ["LOW","MID","HIGH"],                        ["HIGH"],["LOW"]),
      ("dt5g",     "dt5g",       ["CRISIS","BEAR","NEUTRAL","BULL","EXBULL"], ["BULL","EXBULL"],["CRISIS","BEAR"])]
PERIODS=[("IS","2014-01-01","2019-12-31"),("OOS","2020-01-01",FWD_END)]

def run(tag,lo_date,hi_date,fout):
    print(f"\n{'#'*86}\n### {tag}  (cua so {lo_date} -> {hi_date})\n{'#'*86}")
    base=ics[(ics.date>=lo_date)&(ics.date<=hi_date)]
    recs=[]
    for per,a,b in PERIODS:
        a=max(a,lo_date); b=min(b,hi_date)
        w=base[(base.date>=a)&(base.date<=b)]
        if len(w)<60: print(f"\n  {per}: chi {len(w)} phien -> BO QUA"); continue
        print(f"\n=== {per} {a}..{b}  ({len(w)} phien, {w.date.dt.to_period('M').nunique()} thang) ===")
        for axn,col,order,hs,ls in AXES:
            sub=w.dropna(subset=[col])
            if len(sub)<60:
                print(f"  {axn:8s}: {len(sub)} phien co nhan -> BO QUA"); continue
            print(f"  --- truc {axn} ({len(sub)} phien co nhan) ---")
            print(f"    {'cell':8s} {'n_day':>6s} {'n_mon':>6s} {'n_ep':>5s} {'IC_mom':>8s} {'IC_ey':>8s}")
            ic_by={}
            for t in order:
                s=sub[sub[col]==t]
                if not len(s): continue
                lab=(sub[col]==t)
                ne=int((lab & ~lab.shift(1,fill_value=False)).sum())
                ic_by[t]=(np.nanmean(s.ic_mom),np.nanmean(s.ic_ey))
                print(f"    {t:8s} {len(s):6d} {s.date.dt.to_period('M').nunique():6d} {ne:5d} "
                      f"{ic_by[t][0]:8.4f} {ic_by[t][1]:8.4f}")
            for fi,fac in enumerate(["ic_mom","ic_ey"]):
                r=hi_lo(sub,col,hs,ls,fac)
                if r is None: continue
                diff,ci,pb=r
                seq=[ic_by[t][fi] for t in order if t in ic_by]
                mono=bool(np.all(np.diff(seq)>0) or np.all(np.diff(seq)<0))
                print(f"      HI-LO {fac}: {diff:+.4f}  CI95 [{ci[0]:+.4f},{ci[1]:+.4f}]  "
                      f"p_boot={pb:.4f}  {'CI loai 0' if ci[0]*ci[1]>0 else 'CI chua 0'}  don dieu={mono}")
                recs.append(dict(window=tag,period=per,axis=axn,factor=fac,hi_minus_lo=round(diff,4),
                                 ci_lo=round(ci[0],4),ci_hi=round(ci[1],4),p_boot=round(pb,4),
                                 monotonic=mono,ci_excl_0=bool(ci[0]*ci[1]>0),
                                 n_mon_lo=int(sub[sub[col].isin(ls)].date.dt.to_period('M').nunique()),
                                 n_mon_hi=int(sub[sub[col].isin(hs)].date.dt.to_period('M').nunique())))
    r=pd.DataFrame(recs)
    for per in r.period.unique():                       # BH trong TUNG KY (prereg §4)
        m=r.period==per; r.loc[m,"p_BH"]=bh(r.loc[m,"p_boot"].to_numpy()).round(4)
        r.loc[m,"n_bh"]=int(m.sum())
    # tieu chi (i) cung dau IS&OOS
    for (axn,fac),gg in r.groupby(["axis","factor"]):
        if set(gg.period)>={"IS","OOS"}:
            s=np.sign(gg.set_index("period").hi_minus_lo)
            r.loc[gg.index,"same_sign_IS_OOS"]=bool(s["IS"]*s["OOS"]>0)
    r["PASS_all4"]=(r.same_sign_IS_OOS.fillna(False)&r.ci_excl_0&r.monotonic&(r.p_BH<0.10))
    r.to_csv(fout,index=False); print(f"\n-> {fout}"); print(r.to_string(index=False))
    return r

r_long=run("LONG 2014-2026","2014-01-01",FWD_END,"step3_verdict_long.csv")
r_int =run("GIAO 2016-04-2026 (robustness, KHONG trial moi)","2016-04-01",FWD_END,"step3_verdict_intersect.csv")

# ---------- LOO theo nam tren HI-LO (prereg §3)
print(f"\n{'#'*86}\n### LOO theo nam tren HI-LO, cua so dai, TOAN KY 2014-2026\n{'#'*86}")
w=ics.copy(); rows=[]
for axn,col,order,hs,ls in AXES:
    sub=w.dropna(subset=[col])
    yrs=sorted(sub.date.dt.year.unique())
    for fac in ["ic_mom","ic_ey"]:
        vs=[]
        for y in yrs:
            s=sub[sub.date.dt.year!=y]
            vs.append(np.nanmean(s[s[col].isin(hs)][fac])-np.nanmean(s[s[col].isin(ls)][fac]))
        vs=np.array(vs); flip=(vs>0).sum() not in (0,len(vs))
        print(f"  {axn:8s} {fac:7s} n_nam={len(yrs):2d} min={vs.min():+.4f} max={vs.max():+.4f} "
              f"dao dau={'CO' if flip else 'KHONG'}")
        rows.append(dict(axis=axn,factor=fac,n_years=len(yrs),loo_min=round(vs.min(),4),
                         loo_max=round(vs.max(),4),sign_flip=flip))
pd.DataFrame(rows).to_csv("step3_loo.csv",index=False)
