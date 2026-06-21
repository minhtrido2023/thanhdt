# -*- coding: utf-8 -*-
"""
f_protect_v4v5_test.py
======================
Co the dung F-system (overlay VN30F1M, margin-funded, KHONG chiem von equity)
de BAO VE V4/V5 (da gated DT5G) khong?
Model: combined_ret = V_ret + lambda * F_sleeve_ret   (F = overlay notional = lambda x NAV)
F sleeves:
  F_hedge  : M_SHORT {CRISIS-1.0,BEAR-0.3,else 0}  = bao hiem khung hoang thuan
  F_full   : DT5G + Van B + deadband.10            = overlay long+short "ban nang cap sach"
Do: tuong quan V vs F (toan ky + nhung ngay V xau nhat), va frontier lambda.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np, pandas as pd
WD=r"/home/trido/thanhdt/WorkingClaude"

# ---- V4/V5 NAV (DT5G-gated prodspec) ----
v=pd.read_csv(WD+"/data/5sys_prodspec_201401_202605_dt5g.csv"); v["time"]=pd.to_datetime(v["time"])
v=v[["time","V4_V121_ENS_TQ34b","V5_V4_KellyQ2","VNI"]].rename(
    columns={"V4_V121_ENS_TQ34b":"V4","V5_V4_KellyQ2":"V5"})

# ---- VN30F1M + realized vol + DT5G state ----
f1=pd.read_csv(WD+"/vn30f1m_raw.csv"); f1["time"]=pd.to_datetime(f1["time"])
f1=f1.sort_values("time").reset_index(drop=True)
f1["lr"]=np.log(f1["close"]/f1["close"].shift(1)); f1["fret"]=f1["close"].pct_change()
SPYf=len(f1)/((f1.time.iloc[-1]-f1.time.iloc[0]).days/365.25)
f1["rv"]=f1["lr"].rolling(20).std()*np.sqrt(SPYf); TGT=float(np.nanmedian(f1["rv"]))
ds=pd.read_csv(WD+"/vnindex_5state_dt5g_live.csv"); ds["time"]=pd.to_datetime(ds["time"])
f1=f1.merge(ds[["time","state"]],on="time",how="left")

# ---- build F sleeve daily returns ----
M_SHORT={1:-1.00,2:-0.30,3:0.00,4:0.00,5:0.00}
M_LIVE ={1:-1.00,2:-0.20,3:0.70,4:1.00,5:1.30}
def sleeve_ret(mp, van=False):
    st=f1["state"].values; rv=f1["rv"].values; fr=f1["fret"].values
    out=np.full(len(f1),0.0); applied=1.0
    for t in range(1,len(f1)):
        s_=st[t-1]
        base=mp.get(int(s_),0.0) if not np.isnan(s_) else 0.0
        if van and not np.isnan(rv[t-1]) and rv[t-1]>0:
            des=min(1.5,max(0.0,TGT/rv[t-1]))
            if abs(des-applied)>=0.10: applied=des
            base=base*applied
        out[t]=base*(fr[t] if not np.isnan(fr[t]) else 0.0)
    f1["_r"]=out; return f1[["time","_r"]].copy()
F_hedge=sleeve_ret(M_SHORT,van=False).rename(columns={"_r":"F_hedge"})
F_full =sleeve_ret(M_LIVE, van=True ).rename(columns={"_r":"F_full"})

# ---- merge, restrict to VN30F era ----
m=v.merge(F_hedge,on="time").merge(F_full,on="time")
m["V4r"]=m["V4"].pct_change(); m["V5r"]=m["V5"].pct_change()
m=m.dropna(subset=["V4r","V5r"]).reset_index(drop=True)
SPY=len(m)/((m.time.iloc[-1]-m.time.iloc[0]).days/365.25)
print(f"Aligned {len(m)} days {m.time.min().date()}->{m.time.max().date()} SPY~{SPY:.0f}")

def met(r):
    r=np.asarray(r); yrs=len(r)/SPY
    nav=np.cumprod(1+r); cagr=nav[-1]**(1/yrs)-1
    sh=np.mean(r)*SPY/(np.std(r)*np.sqrt(SPY)) if np.std(r)>0 else 0
    rm=np.maximum.accumulate(nav); mdd=np.min(nav/rm-1)
    return cagr,sh,mdd,cagr/abs(mdd) if mdd else 0

# ---- correlation diagnostics ----
print("\n--- Tuong quan V vs F sleeve (overall + ngay V xau nhat decile) ---")
for V in ["V5r","V4r"]:
    worst=m[m[V]<=m[V].quantile(0.10)]
    for Fc in ["F_hedge","F_full"]:
        c_all=np.corrcoef(m[V],m[Fc])[0,1]
        c_bad=np.corrcoef(worst[V],worst[Fc])[0,1]
        f_on_bad=worst[Fc].mean()*100
        print(f"  {V} vs {Fc:8s}: corr_all {c_all:+.2f} | corr_worst10% {c_bad:+.2f} | "
              f"F mean ret nhung ngay V xau: {f_on_bad:+.3f}%")

# ---- lambda frontier ----
for V in ["V5","V4"]:
    Vr=m[V+"r"].values
    print(f"\n{'='*86}\n  {V}  +  lambda x F-sleeve   (overlay notional = lambda x NAV)\n{'='*86}")
    for Fc,fname in [("F_hedge","F_hedge (crisis short)"),("F_full","F_full (DT5G+Van overlay)")]:
        print(f"\n  [{fname}]")
        print(f"  {'lambda':>7}{'CAGR':>9}{'Sharpe':>8}{'MaxDD':>9}{'Calmar':>8}")
        print("  "+"-"*42)
        for lam in [0.0,0.1,0.2,0.3,0.5]:
            cr=Vr+lam*m[Fc].values
            cg,sh,md,ca=met(cr)
            star=" <-" if lam==0 else ""
            print(f"  {lam:>7.1f}{cg*100:>+8.1f}%{sh:>8.2f}{md*100:>+8.1f}%{ca:>8.2f}{star}")
print("\nDone.")
