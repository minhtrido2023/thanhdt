import re, pandas as pd, numpy as np
o=pd.read_csv("orig_results_table.csv"); n=pd.read_csv("now/results_table.csv").set_index("metric"); c=pd.read_csv("control/results_table.csv").set_index("metric")
f=lambda x:"—" if pd.isna(x) else (f"{x:,.1f}" if abs(x)>=100 else f"{x:.4g}" if abs(x)>=1 else f"{x:+.4f}" if x<0 else f"{x:.4f}")
rows=[]
for _,a in o.iterrows():
    m=a.metric; b=n.loc[m]
    out="**NGOÀI**" if b.outside_5_95 else "trong"
    if m=="T3_quality_set_n": out="không kiểm được¹"
    rows.append([m, f"{f(a.pre60)} → {f(a.post)}", f(a.change), f"{f(a.plc_p5)} … {f(a.plc_p95)}", f"{f(b.pre60)} → {f(b.post)}", f(b.change), f"{f(b.plc_p5)} … {f(b.plc_p95)}", f"{b.pctile_of_actual:.1f}", out])
pat=re.compile(r"^(\S+)\s+pre\s+(\S+) post\s+(\S+) chg\s+(\S+) \| placebo N=(\d+) p5 (\S+) p50 \S+ p95 (\S+) pctile (\S+)",re.M)
og={x[0]:x for x in pat.findall(open("orig_out_fgn27.txt").read())}
for x in pat.findall(open("now/out_fgn27.txt").read()):
    k,pre,post,d,N,p5,p95,pc=x; a=og[k]
    rows.append([k, f"{f(float(a[1]))} → {f(float(a[2]))}", f(float(a[3])), f"{f(float(a[5]))} … {f(float(a[6]))}", f"{f(float(pre))} → {f(float(post))}", f(float(d)), f"{f(float(p5))} … {f(float(p95))}", pc, "**NGOÀI**" if not float(p5)<=float(d)<=float(p95) else "trong"])
assert len(rows)==24
h=["Đại lượng","10/13: trước → sau","Δ","Dải p5…p95 (10/13)","Nay: trước → sau","Δ","Dải p5…p95 (nay)","phân vị","Nay"]
t="\n".join("| "+" | ".join(r)+" |" for r in [h,["---"]*len(h)]+rows)
body=open("report_body.md").read().replace("{{TABLE}}",t).replace("{{DIFF}}",open("pull.diff").read())
open("REPORT.md","w").write(body)
