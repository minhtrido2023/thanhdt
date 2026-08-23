"""Q1 — TRONG episode da armed (dd52<=-20%), tin hieu PIT nao phan biet 'con giam tiep' vs 'gan kiet ban'?
Ky luat: percentile EXPANDING PIT (khong full-sample); danh gia theo EPISODE, khong theo so ngay."""
import pandas as pd, numpy as np
D="/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/extreme_bottom_recognition_20260823"
d=pd.read_csv(f"{D}/daily_panel.csv",parse_dates=["time"]).sort_values("time").reset_index(drop=True)
ep=pd.read_csv(f"{D}/episodes_dd52.csv")

# gan nhan episode cho tung ngay armed
d["ep"]=None
for _,r in ep.iterrows():
    m=(d["time"]>=r.arm_date)&(d["time"]<=r.end_date); d.loc[m,"ep"]=r.episode
A=d[d["ep"].notna()&d["fwd12"].notna()].copy()
print(f"Ngay armed co fwd12: {len(A)} | episode: {sorted(A['ep'].unique())}\n")

SIG={
 "pe_pit<=0.20":       lambda x: x["pe_med_pit"]<=0.20,
 "pe_pit<=0.35":       lambda x: x["pe_med_pit"]<=0.35,
 "pct_dd50>=0.50":     lambda x: x["pct_dd50"]>=0.50,
 "pct_ma200<=0.10":    lambda x: x["pct_ma200"]<=0.10,
 "pct_52wlow>=0.25":   lambda x: x["pct_52wlow"]>=0.25,
 "tv_ratio<=0.60":     lambda x: x["tv_ratio"]<=0.60,
 "pb_med<=0.80":       lambda x: x["pb_med"]<=0.80,
 "dd52<=-0.35":        lambda x: x["dd52"]<=-0.35,
 "pe_pit<=.35 & dd50>=.50": lambda x: (x["pe_med_pit"]<=0.35)&(x["pct_dd50"]>=0.50),
}
base=A["fwd12"]
print(f"BASELINE (moi ngay armed): n={len(base)} median fwd12={base.median():+.1%} mean={base.mean():+.1%} %>0={100*(base>0).mean():.0f}%")
print(f"  theo EPISODE (median cua median tung episode): {A.groupby('ep')['fwd12'].median().median():+.1%}\n")
rows=[]
for name,f in SIG.items():
    m=f(A); s=A[m]
    if len(s)==0: rows.append(dict(signal=name,n_days=0)); continue
    eps=sorted(s["ep"].unique())
    per_ep=s.groupby("ep")["fwd12"].median()
    # LOO theo episode: bo tung episode, median cua phan con lai
    loo=[per_ep.drop(e).median() for e in per_ep.index] if len(per_ep)>1 else [np.nan]
    rows.append(dict(signal=name, n_days=len(s), n_ep=len(eps),
        med_fwd12=round(s["fwd12"].median(),4), mean=round(s["fwd12"].mean(),4),
        pct_pos=round((s["fwd12"]>0).mean(),3),
        med_by_ep=round(per_ep.median(),4),
        loo_min=round(np.nanmin(loo),4), loo_max=round(np.nanmax(loo),4),
        eps=",".join(e[:7] for e in eps)))
R=pd.DataFrame(rows); pd.set_option("display.width",250,"display.max_columns",30)
print(R.to_string(index=False))
R.to_csv(f"{D}/q1_signal_summary.csv",index=False)

# --- BAO LAU sau khi signal fire moi toi day THAT (do 'som/muon')
print("\n=== Khoang cach tu lan FIRE DAU TIEN trong episode toi DAY THAT ===")
out=[]
for _,r in ep.iterrows():
    sub=d[(d["time"]>=r.arm_date)&(d["time"]<=r.end_date)]
    tro=pd.Timestamp(r.trough_date)
    row={"episode":r.episode,"arm->trough_d":r.lag_days}
    for name,f in SIG.items():
        hit=sub[f(sub)]
        row[name]=(pd.Timestamp(hit["time"].iloc[0])-tro).days if len(hit) else None
    out.append(row)
O=pd.DataFrame(out); print(O.to_string(index=False))
O.to_csv(f"{D}/q1_lead_lag.csv",index=False)
print("\n(so am = fire TRUOC day that bao nhieu ngay; duong = fire SAU day; None = khong fire trong episode)")
