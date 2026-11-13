"""A5 việc 2b: ADV live (due_diligence.adv_vnd: dòng mới nhất <= ngày đặt lệnh; cache sync 23:45 ⇒ dòng t-1)
vs pit engine (median Volume t-60..t-1 × Price t-1, min_periods 20) vs bq-ngày-fill (engine cũ: dòng t).
Trần live = 0,20 × ADV × share(1/2 account live). Nguồn: logs/lag_orders.json (lag_orders.py), logs/bq_px_vol.csv (tav2_bq.ticker)."""
import json, numpy as np, pandas as pd
o=pd.DataFrame(json.load(open('logs/lag_orders.json'))); o=o[(o.qty.fillna(0)>0)].copy()
px=pd.read_csv('logs/bq_px_vol.csv',parse_dates=['time']).sort_values(['ticker','time'])
px['P']=px.Price.fillna(px.Close)
px['pit']=px.groupby('ticker').Volume.transform(lambda v: v.shift(1).rolling(60,min_periods=20).median())*px.groupby('ticker').P.shift(1)
px['bqadv']=px.Volume_3M_P50*px.P
out=[]
for _,r in o.iterrows():
    g=px[px.ticker==r.tk]; t=pd.Timestamp(r.date)
    prev=g[g.time<t]; cur=g[g.time==t]
    live=prev.bqadv.iloc[-1] if len(prev) else np.nan; dd=prev.time.iloc[-1].date() if len(prev) else None
    pit=cur.pit.iloc[0] if len(cur) else np.nan; bqt=cur.bqadv.iloc[0] if len(cur) else np.nan
    val=(r.qty or 0)*(r.px or (prev.P.iloc[-1] if len(prev) else np.nan))
    cap=0.20*live*0.5
    out.append(dict(acct=r.acct[:2],date=r.date,kind=r.kind[:3],tk=r.tk,qty=r.qty,val_M=val/1e6,live_B=live/1e9,live_dd=dd,pit_B=pit/1e9,bqfill_B=bqt/1e9,
        lr_live_pit=np.log(live/pit),lr_bqfill_pit=np.log(bqt/pit),ord_over_cap=val/cap,note_B=r.adv_note_B,fillq=r.fillq))
d=pd.DataFrame(out); pd.set_option('display.width',250); pd.set_option('display.max_rows',100)
print(d.round(4).to_string(index=False))
u=d.drop_duplicates(['tk','date'])
print(f"\nN lệnh (qty>0) = {len(d)}; N cặp (mã,ngày) độc lập = {len(u)}; số mã = {u.tk.nunique()}; ngày = {u.date.nunique()}")
for c in ['lr_live_pit','lr_bqfill_pit']:
    x=u[c].dropna(); print(f"{c}: n={len(x)} median={x.median():+.4f} p5={x.quantile(.05):+.4f} p95={x.quantile(.95):+.4f} max|.|={x.abs().max():.4f} share|.|<1e-9={(x.abs()<1e-9).mean():.2f}")
print(f"ord/cap: max={d.ord_over_cap.max():.4f} median={d.ord_over_cap.median():.4f}; số lệnh > trần = {(d.ord_over_cap>1).sum()}")
n=d.dropna(subset=['note_B']); print('adv_note vs live recon:'); print(n[['date','tk','note_B','live_B','pit_B']].round(3).to_string(index=False))
