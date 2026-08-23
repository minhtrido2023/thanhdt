"""Q1b — Phase 0 do spread o do phan giai THANG. Kiem tra: co phai 2022 bi bo sot chi vi lay mau cuoi thang?"""
import pandas as pd, numpy as np
D="/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/extreme_bottom_recognition_20260823"
P="/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/margin_valuation_spread_20260823"
d=pd.read_csv(f"{D}/daily_panel.csv",parse_dates=["time"]).sort_values("time")
m=pd.read_csv(f"{P}/monthly_spread_series.csv",parse_dates=["time"])[["time","deposit_use","margin_rate"]]
# deposit/margin la ham BAC THANG theo su kien -> ffill tu moc thang gan nhat DA QUA (khong nhin truoc)
d=pd.merge_asof(d,m.sort_values("time"),on="time",direction="backward")
d["ey_med_pct"]=100/d["pe_med"]
d["sp_ey_mgn"]=d["ey_med_pct"]-d["margin_rate"]     # EY(median) - lai vay
d["sp_ey_dep"]=d["ey_med_pct"]-d["deposit_use"]
d.to_csv(f"{D}/daily_panel_spread.csv",index=False)

def episodes(mask,minlen=1,gap=90):
    s=d[mask&d["sp_ey_mgn"].notna()]
    if not len(s): return []
    out=[];cur=[s["time"].iloc[0],s["time"].iloc[0]]
    for t in s["time"].iloc[1:]:
        if (t-cur[1]).days<=gap: cur[1]=t
        else: out.append(cur);cur=[t,t]
    out.append(cur);return out

print("=== Episode 'EY(median) >= lai vay' — DAILY vs Phase-0 MONTHLY ===")
for lo,lab in [(0.0,"spread >= 0"),(1.0,"spread >= +1pp")]:
    eps=episodes(d["sp_ey_mgn"]>=lo)
    print(f"\n{lab}: {len(eps)} episode (daily, merge gap<=90d)")
    for a,b in eps:
        s=d[(d["time"]>=a)&(d["time"]<=b)]
        f=s["fwd12"].median()
        print(f"  {a:%Y-%m-%d} -> {b:%Y-%m-%d} ({len(s)} phien) | spread max {s['sp_ey_mgn'].max():+.2f}pp | fwd12 median {f:+.1%}" if pd.notna(f) else f"  {a:%Y-%m-%d} -> {b:%Y-%m-%d} ({len(s)} phien) | spread max {s['sp_ey_mgn'].max():+.2f}pp | fwd12 n/a")

print("\n=== Gia tri tai DAY THAT tung episode (daily, khong phai cuoi thang) ===")
ep=pd.read_csv(f"{D}/episodes_dd52.csv")
for _,r in ep.iterrows():
    row=d[d["time"]==r.trough_date]
    if not len(row): continue
    x=row.iloc[0]
    print(f"  {r.trough_date}  EY_med {x['ey_med_pct']:.2f}%  margin {x['margin_rate']:.1f}%  spread {x['sp_ey_mgn']:+.2f}pp  (cuoi thang do duoc o Phase0 -> lech)" if pd.notna(x["ey_med_pct"]) else f"  {r.trough_date} n/a")
