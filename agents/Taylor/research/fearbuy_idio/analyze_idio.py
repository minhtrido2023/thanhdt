import pandas as pd, numpy as np
df = pd.read_csv('episodes_idio.csv')
print("Total episodes:", len(df))
print("Year range:", df.yr.min(), "-", df.yr.max())
# realized flags: need forward data present (non-null) for each horizon
hz = {'3m':'r3m','6m':'r6m','9m':'r9m','12m':'r12m','18m':'r18m','24m':'r24m','30m':'r30m','36m':'r36m'}
ehz= {'3m':'ex3m','6m':'ex6m','9m':'ex9m','12m':'ex12m','18m':'ex18m','24m':'ex24m','30m':'ex30m','36m':'ex36m'}
print("\n=== HOLDING-PERIOD CURVE (all quality-floor idiosyncratic, mkt within -15%) ===")
print(f"{'H':>4} {'N':>5} {'med_r':>8} {'mean_r':>8} {'med_ex':>8} {'mean_ex':>9} {'winr_ex':>8}")
for h in hz:
    sub = df[df[hz[h]].notna() & df[ehz[h]].notna()]
    n=len(sub)
    if n==0: continue
    print(f"{h:>4} {n:>5} {sub[hz[h]].median()*100:>7.1f}% {sub[hz[h]].mean()*100:>7.1f}% {sub[ehz[h]].median()*100:>7.1f}% {sub[ehz[h]].mean()*100:>8.1f}% {(sub[ehz[h]]>0).mean()*100:>7.0f}%")

# Risk-adjusted: excess return / intra-hold maxDD-from-entry (mdd is negative). Use median.
print("\n=== RISK-ADJUSTED (return vs intra-holding worst drawdown from entry) ===")
for h,mdd in [('12m','mdd12'),('24m','mdd24'),('36m','mdd36')]:
    sub=df[df[ehz[h]].notna() & df[mdd].notna()]
    # per-episode ratio r/|mdd|, guard mdd near 0
    dd = sub[mdd].clip(upper=-0.01)  # at least -1%
    ratio = sub[hz[h]]/dd.abs()
    print(f"{h}: N={len(sub)} median r/|maxDD|={ratio.median():.2f}  median maxDD-from-entry={sub[mdd].median()*100:.0f}%  mean maxDD={sub[mdd].mean()*100:.0f}%")
