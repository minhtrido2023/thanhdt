"""Monthly attribution table (%NAV of prev month-end): ret, VNI, beta, selection vs VNI, park vs VNI, avg stock exposure. usage: TAG WINDOW(to1109|to1106)
Reads engine/partA_{TAG}_{WINDOW}_daily_{BAL,LAG}.csv written by part_a_v2.py. Regenerates (saved script) part_a_monthly_attr.txt."""
import sys, pandas as pd, numpy as np
R="/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/book_regime_fit_20261110"; TAG,W=sys.argv[1],sys.argv[2]
rows=[]
for b in ["BAL","LAG"]:
    d=pd.read_csv(f"{R}/engine/partA_{TAG}_{W}_daily_{b}.csv",parse_dates=["ymd"]).set_index("ymd")
    d["stk_cap"]=d.stk.shift(1).fillna(0)+d.buy_stk; d["etf_cap"]=d.etf.shift(1).fillna(0)+d.buy_etf
    w=d.loc["2026-07-01":]; 
    for mon,g in w.groupby(w.index.to_period("M")):
        prev=d.nav[d.index<g.index[0]].iloc[-1]; vprev=d.vni[d.index<g.index[0]].iloc[-1]
        rows.append(dict(book=b,month=str(mon),ret=100*(g.nav.iloc[-1]/prev-1),vni=100*(g.vni.iloc[-1]/vprev-1),
            beta=100*((g.stk_cap+g.etf_cap)*g.vni_r).sum()/prev,sel=100*(g.pnl_stk-g.stk_cap*g.vni_r).sum()/prev,
            park=100*(g.pnl_etf-g.etf_cap*g.vni_r).sum()/prev,fees=-100*g.fees.sum()/prev,expo_stk=100*(g.stk/g.nav).mean()))
t=pd.DataFrame(rows).round(2); s=t.to_string(index=False); open(f"{R}/engine/monthly_attr_{TAG}_{W}.txt","w").write(s); print(s)
