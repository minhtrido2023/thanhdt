"""A4 việc 1(c): định nghĩa Volume_3M_P50 BQ vs rolling pit; ADV ratio tại mọi (mã, ngày) mua LAG; size diff vs ratio."""
import sys, pandas as pd, numpy as np, duckdb
def load(p):
    X = pd.read_csv(p, low_memory=False); X["ymd"] = pd.to_datetime(X["ymd"].astype(str).str[:10], errors="coerce"); return X
A, B = load(sys.argv[1]), load(sys.argv[2])
def lagbuys(X):
    t=X[(X.record_type=="TX")&(X.book=="LAG")&(X.action=="buy")].copy(); t["buy_amount"]=t.buy_amount.astype(float); return t
ba, bb = lagbuys(A), lagbuys(B)
tk=sorted(set(ba.ticker)|set(bb.ticker))
C="/home/trido/thanhdt/WorkingClaude/data/bq_cache_asof20260729_postrestate/ticker/*.parquet"
q=duckdb.sql(f"""SELECT ticker,time,Volume,Volume_3M_P50,COALESCE(Price,Close) px FROM read_parquet('{C}') WHERE ticker IN ({','.join("'"+t+"'" for t in tk)})""").df()
q["time"]=pd.to_datetime(q.time); q=q.sort_values(["ticker","time"]).reset_index(drop=True); g=q.groupby("ticker")
q["med_ex"]=g.Volume.transform(lambda s:s.shift(1).rolling(60,min_periods=20).median())      # t-60..t-1 (pit)
q["med_in"]=g.Volume.transform(lambda s:s.rolling(60,min_periods=60).median())               # t-59..t (gồm t)
q["med_in59"]=g.Volume.transform(lambda s:s.shift(1).rolling(59,min_periods=20).median())
q["pxl"]=g.px.shift(1); q["n"]=g.cumcount()
v=q[q.Volume_3M_P50.notna()&q.med_ex.notna()&(q.n>=60)]
for nm,c in (("ex t-60..t-1 (pit)","med_ex"),("incl t (t-59..t)","med_in")):
    m=v[c].notna(); r=(v.loc[m,"Volume_3M_P50"]-v.loc[m,c]).abs()<=1e-6*v.loc[m,"Volume_3M_P50"].abs().clip(lower=1)
    print(f"BQ Volume_3M_P50 == {nm}: {r.mean()*100:.2f}% trên {m.sum():,} dòng (n>=60)")
# shift: BQ(t) == med_ex(t+1)? tức BQ gồm t, pit(t+1) dùng t-59..t
q["med_ex_next"]=q.groupby("ticker").med_ex.shift(-1)
w=q[q.Volume_3M_P50.notna()&q.med_ex_next.notna()&(q.n>=60)]
print(f"BQ(t) == pit(t+1)  [cùng cửa sổ t-59..t]: {((w.Volume_3M_P50-w.med_ex_next).abs()<=1e-6*w.Volume_3M_P50.abs().clip(lower=1)).mean()*100:.2f}%")
# mọi (mã, ngày) mua LAG của 2 ledger
K=pd.concat([ba[["ticker","ymd"]],bb[["ticker","ymd"]]]).drop_duplicates()
m=K.merge(q,left_on=["ticker","ymd"],right_on=["ticker","time"],how="left")
m["bq"]=m.Volume_3M_P50*m.px; m["pit"]=m.med_ex*m.pxl
ok=(m.bq>0)&(m.pit>0)
r=np.log(m.bq[ok]/m.pit[ok])
print(f"(mã,ngày) mua LAG: {len(m)} | bq NULL {m.bq.isna().sum()} | bq<=0 {(m.bq<=0).sum()} | pit NULL {m.pit.isna().sum()} | pit<=0 {(m.pit<=0).sum()}")
print(f"log(bq/pit) cả hai>0 (n={ok.sum()}): mean {r.mean():+.4f} median {r.median():+.4f} p5 {r.quantile(.05):+.3f} p95 {r.quantile(.95):+.3f}; |r|<1% {(r.abs()<0.01).mean()*100:.1f}%")
# tách: phần volume (ex vs incl) và phần giá
m["pit_incl"]=m.med_in*m.px; ok2=(m.bq>0)&(m.pit_incl>0)
print(f"  bq vs median-incl-t x Price(t): |Δ|<1e-6: {(np.abs(np.log(m.bq[ok2]/m.pit_incl[ok2]))<1e-6).mean()*100:.1f}%")
m["vol_part"]=np.log(m.med_in/m.med_ex); m["px_part"]=np.log(m.px/m.pxl)
okp=(m.med_in>0)&(m.med_ex>0)&(m.px>0)&(m.pxl>0)
print(f"  log(Vol incl t / Vol ex t) mean {m.vol_part[okp].mean():+.4f} ; log(Px_t/Px_t-1) mean {m.px_part[okp].mean():+.4f}")
# size diff vs ratio, trên cặp (ticker,ymd) chung
sa=ba.groupby(["ticker","ymd"]).buy_amount.sum(); sb=bb.groupby(["ticker","ymd"]).buy_amount.sum()
z=pd.concat([sa.rename("a"),sb.rename("b")],axis=1).dropna()
print(f"cặp mua chung {len(z)}: Σ bq {z.a.sum()/1e9:.1f}B Σ pit {z.b.sum()/1e9:.1f}B ({(z.b.sum()/z.a.sum()-1)*100:+.2f}%); pit<bq: {(z.b<z.a*0.995).sum()}, pit>bq: {(z.b>z.a*1.005).sum()}, ≈: {((z.b-z.a).abs()<=0.005*z.a).sum()}")
zz=z.reset_index().merge(m[["ticker","ymd","bq","pit"]],on=["ticker","ymd"])
zz["lr"]=np.log(zz.bq/zz.pit); zz["ls"]=np.log(zz.b/zz.a)
ok=np.isfinite(zz.lr)&np.isfinite(zz.ls)&(zz.ls.abs()>0.005)
print(f"  tương quan(log ADV bq/pit, log size pit/bq) trên cặp có đổi size n={ok.sum()}: {np.corrcoef(zz.lr[ok],zz.ls[ok])[0,1]:.3f}; sign đúng chiều (ADV pit<bq ⇒ size pit<bq): {((zz.lr[ok]>0)==(zz.ls[ok]<0)).mean()*100:.1f}%")
print("  theo năm: Σ size pit/bq -1 (cặp chung):", " ".join(f"{y}:{(g.b.sum()/g.a.sum()-1)*100:+.1f}%" for y,g in zz.groupby(zz.ymd.dt.year)))
print("  theo năm: median log(bq/pit):", " ".join(f"{y}:{g.lr[np.isfinite(g.lr)].median():+.3f}" for y,g in zz.groupby(zz.ymd.dt.year)))
c=zz[ok]
print(f"  cặp đổi size n={len(c)}: mean log(bq/pit) {c.lr.mean():+.4f} median {c.lr.median():+.4f}; Σ size pit/bq-1 trên cặp này {(c.b.sum()/c.a.sum()-1)*100:+.2f}%; pit<bq {int((c.ls<0).sum())} (Σ Δ {(c.b-c.a)[c.ls<0].sum()/1e9:+.1f}B) vs pit>bq {int((c.ls>0).sum())} (Σ Δ {(c.b-c.a)[c.ls>0].sum()/1e9:+.1f}B)")
print(f"  Σ Δ size pit-bq toàn bộ cặp chung = {(z.b-z.a).sum()/1e9:+.1f}B; bq-only buys: {(ba.buy_amount.sum()-z.a.sum())/1e9:.1f}B, pit-only: {(bb.buy_amount.sum()-z.b.sum())/1e9:.1f}B")
big=c.assign(d=c.b-c.a).sort_values("d"); print("  5 cặp giảm size lớn nhất (pit-bq, tỷ; ADV bq/pit tỷ):"); 
for _,r in big.head(5).iterrows(): print(f"    {r.ticker} {r.ymd.date()} Δ{r.d/1e9:+.2f}B  ADV bq {r.bq/1e9:.2f} pit {r.pit/1e9:.2f}")
