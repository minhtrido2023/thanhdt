import re, pandas as pd, numpy as np
LOG="/home/trido/thanhdt/WorkingClaude/data/capit_sizing_20260731/capsz_ctrl.log"
CSV="/home/trido/thanhdt/WorkingClaude/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_exp_capsz_ctrl_univpit.csv"
rx=re.compile(r"\[capit-size (\w) E(\d+) ([\d-]+)\] size=([\d.]+) cash=([\d.]+) idle=([\d.]+) -> wt=([\d.]+)")
rec={}
for ln in open(LOG):
    m=rx.search(ln)
    if m:
        bk,ei,dt,sz,cf,idl,wt=m.groups()
        rec.setdefault((int(ei),dt),{})[bk]=(float(sz),float(cf),float(idl),float(wt))
df=pd.read_csv(CSV,low_memory=False)
d=df[df.record_type=="DAILY"].copy(); d["ymd"]=pd.to_datetime(d["ymd"])
d=d.set_index("ymd")[["nav_bal_ref","nav_lag_ref"]].astype(float)
print(f"{'E':>3} {'date':<11}{'st_size':>8}| {'cashB':>6}{'idleB':>6}{'cashL':>6}{'idleL':>6}| "
      f"{'%NAV_cash':>9}{'%NAV_idle':>9}{'%NAV_live':>9}")
print("-"*84)
tot={"cash":[],"idle":[],"live":[]}
for (ei,dt),v in sorted(rec.items()):
    t=pd.Timestamp(dt); pos=d.index.searchsorted(t); pos=min(pos,len(d)-1)
    nb,nl=d.iloc[pos]; N=nb+nl
    B=v.get("B",(0,0,0,0)); L=v.get("L",(0,0,0,0))
    sz=max(B[0],L[0])
    wcash=(B[3]*nb+L[3]*nl)/N
    widle=(B[0]*B[2]*nb+L[0]*L[2]*nl)/N
    wlive=(sz*nl)/N              # LIVE: size x NAV_book_LAG
    for k,val in (("cash",wcash),("idle",widle),("live",wlive)): tot[k].append(val)
    print(f"{ei:>3} {dt:<11}{sz:>8.3f}| {B[1]:>6.2f}{B[2]:>6.2f}{L[1]:>6.2f}{L[2]:>6.2f}| "
          f"{wcash*100:>8.1f}%{widle*100:>8.1f}%{wlive*100:>8.1f}%")
print("-"*84)
for k in tot:
    a=np.array(tot[k]); print(f"  {k:<5} %NAV tong: median={np.median(a)*100:5.1f}%  mean={a.mean()*100:5.1f}%  "
                              f"min={a.min()*100:4.1f}%  max={a.max()*100:5.1f}%  n_event_gan_0(<2%)={int((a<0.02).sum())}")
