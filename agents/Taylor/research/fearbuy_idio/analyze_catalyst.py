import pandas as pd, numpy as np
df=pd.read_csv('episodes_idio.csv')
def line(sub,lbl):
    s=sub[sub.ex24m.notna()]
    if len(s)<8: print(f"{lbl:>32}: N={len(s)} thin"); return
    print(f"{lbl:>32}: N={len(s):>4}  med_r24={s.r24m.median()*100:>6.0f}%  med_ex24={s.ex24m.median()*100:>6.0f}%  winr24={(s.ex24m>0).mean()*100:>3.0f}%  mean_r24={s.r24m.mean()*100:>5.0f}%")

print("=== CATALYST-CONFIRMATION PROXY: does early recovery (by 6m) predict the 24m outcome? ===")
print("Rule tested: after entry, is the position UP at 6m (r6m>0)? = market beginning to re-rate / catalyst working.\n")
line(df, "ALL idiosyncratic")
line(df[df.r6m>0], "confirmed by 6m (r6m>0) -> HOLD")
line(df[df.r6m<=0], "NOT confirmed by 6m -> would ABANDON")
print()
print("=== stricter: confirmed by 9m ===")
line(df[df.r9m>0], "confirmed by 9m (r9m>0)")
line(df[df.r9m<=0], "not confirmed by 9m")
print()
# what % of eventual-winner 24m gain arrives after 12m? (late-payoff test -> supports LONG hold once confirmed)
w=df[(df.ex24m>0)&(df.r12m.notna())&(df.r24m.notna())]
print(f"=== Among eventual winners (ex24m>0, N={len(w)}): where does the gain arrive? ===")
print(f"  median r6m={w.r6m.median()*100:.0f}%  r12m={w.r12m.median()*100:.0f}%  r18m={w.r18m.median()*100:.0f}%  r24m={w.r24m.median()*100:.0f}%  r36m={w.r36m.median()*100:.0f}%")
print("  -> winners keep compounding 12->36m; gains arrive LATE and slow. Supports min ~18-24m hold ONCE confirmed.")
