"""Q3b — do nhay voi MAT XICH YEU NHAT (margin = deposit + Xpp) + block-bootstrap."""
import pandas as pd, numpy as np
D="/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/extreme_bottom_recognition_20260823"
d=pd.read_csv(f"{D}/daily_panel_spread.csv",parse_dates=["time"])
d=d[d["fwd12"].notna()&d["ey_med_pct"].notna()].copy()
d["armed"]=d["dd52"]<=-0.20; d["deep"]=d["dd52"]<=-0.35

def blocks_med(mask,fwd="fwd12",gap=90):
    s=d[mask]
    if not len(s): return np.array([])
    t=s["time"].values; b=[[0,0]]
    for i in range(1,len(t)):
        if (t[i]-t[b[-1][1]]).astype('timedelta64[D]').astype(int)<=gap: b[-1][1]=i
        else: b.append([i,i])
    return np.array([s[fwd].iloc[a:z+1].median() for a,z in b])

rng=np.random.default_rng(7)
def boot(m,cost):
    if len(m)<2: return np.nan
    dr=rng.choice(m,size=(20000,len(m)),replace=True)
    return (np.median(dr,axis=1)>cost).mean()

print("=== Do nhay: margin = deposit + Xpp (Phase 0 gia dinh +5,0pp) ===")
print(f"{'X':>5} {'nguong':>8} | {'spread>=0 (V8c)':^42} | {'armed & spread>=0':^42}")
print(f"{'':>5} {'':>8} | {'N':>3} {'net':>8} {'%khoi':>6} {'P(boot)':>8} | {'N':>3} {'net':>8} {'%khoi':>6} {'P(boot)':>8}")
for X in [3.0,4.0,5.0,6.0,7.0]:
    d["mr"]=d["deposit_use"]+X; d["sp"]=d["ey_med_pct"]-d["mr"]
    cost=d.loc[d["sp"]>=0,"mr"].median()/100 if (d["sp"]>=0).any() else np.nan
    row=[]
    for m in [d["sp"]>=0, d["armed"]&(d["sp"]>=0)]:
        v=blocks_med(m); c=d.loc[m,"mr"].median()/100 if m.any() else np.nan
        row.append((len(v), np.median(v)-c if len(v) else np.nan,
                    (v>c).mean() if len(v) else np.nan, boot(v,c)))
    print(f"{X:>5.1f} {'EY>=dep+X':>8} | {row[0][0]:>3d} {row[0][1]:>+8.1%} {row[0][2]:>6.0%} {row[0][3]:>8.2f} | "
          f"{row[1][0]:>3d} {row[1][1]:>+8.1%} {row[1][2]:>6.0%} {row[1][3]:>8.2f}")

print("\n=== Cung phep do cho cac ung vien khac (X=5,0pp) ===")
d["mr"]=d["deposit_use"]+5.0; d["sp"]=d["ey_med_pct"]-d["mr"]
for lab,m in [("armed dd52<=-20% [LIVE]",d["armed"]),
              ("deep dd52<=-35% [V8a]",d["deep"]),
              ("deep & spread>=0 [V8b]",d["deep"]&(d["sp"]>=0)),
              ("spread>=0 [V8c]",d["sp"]>=0),
              ("spread>=+1pp",d["sp"]>=1.0)]:
    v=blocks_med(m); c=d.loc[m,"mr"].median()/100
    print(f"  {lab:26s} N={len(v):2d} net={np.median(v)-c:+6.1%} %khoi={(v>c).mean():4.0%} P(boot median>cost)={boot(v,c):.2f}")
print("\nP(boot) = xac suat median-cua-khoi vuot chi phi vay, block-bootstrap 20k, KHOI la don vi lay mau.")
print("Nguong tham chieu quen dung cua fleet: DSR/P >= 0,95. Khong cai nao o day dat nguong do.")
