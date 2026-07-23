import pandas as pd, numpy as np
df=pd.read_csv("mike/agents/Taylor/research/fearbuy_blend/panel.csv")
df['adv_b']=df['adv_vnd']/1e9; df['s']=-df['mkt_dd']
def adaptive_mask(d,s_min=0.20,s0=0.20,pb_hi=1.0,pb_lo=0.40,slope=2.0):
    pbmax=np.clip(pb_hi - slope*(d.s - s0), pb_lo, pb_hi)
    return (d.s>=s_min)&(d.PB<=pbmax)

for advmin,lab in [(10,"ADV>=10B"),(20,"ADV>=20B")]:
    q=df[adaptive_mask(df)&(df.adv_b>=advmin)].copy().sort_values(['entry_date'])
    print("="*112); print(f"ADAPTIVE + {lab}  — N={len(q)} episodes"); print("="*112)
    print(f"{'ticker':<7}{'entry':<12}{'PB':>5}{'mkt_dd':>8}{'ADV_B':>8}{'DE':>5}{'ex12':>8}{'ex18':>8}{'ex24':>8}{'r24':>8}")
    for _,r in q.iterrows():
        print(f"{r.ticker:<7}{r.entry_date:<12}{r.PB:>5.2f}{r.mkt_dd:>8.2f}{r.adv_b:>8.1f}{r.DE:>5.1f}"
              f"{100*r.ex12 if pd.notna(r.ex12) else float('nan'):>7.0f}%{100*r.ex18 if pd.notna(r.ex18) else float('nan'):>7.0f}%"
              f"{100*r.ex24 if pd.notna(r.ex24) else float('nan'):>7.0f}%{100*r.r24 if pd.notna(r.r24) else float('nan'):>7.0f}%")
    # cluster by crisis-year
    print(f"\n  per-year: {q.groupby('yr').size().to_dict()}")
    print(f"  unique tickers: {q.ticker.nunique()}  | top by count: {q.ticker.value_counts().head(8).to_dict()}")
