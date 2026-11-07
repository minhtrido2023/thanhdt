import csv, statistics as st, sys
rows=[r for r in csv.DictReader(open(sys.argv[1]))]
DEV=["VHM","NLG","KDH","DXG","PDR","DIG","HDG","HDC","NTL","CEO","SCR","NVL","KHG","AGG"]
AUTO=["HAX","SVC","TMT"]
def f(x):
    try: return float(x)
    except: return None
def stats(grp, col, y0="2016Q4", y1="2025Q4"):
    per={}
    for t in grp:
        v=[f(r[col]) for r in rows if r['ticker']==t and y0<=r['quarter']<=y1 and r['quarter'].endswith('Q4') and f(r[col]) is not None]
        if len(v)>=5: per[t]=(st.mean(v), min(v), len(v))
    m=[a for a,_,_ in per.values()]
    return per, st.mean(m), st.median(m)
for name,grp in (("DEV",DEV),("AUTO",AUTO),("TCH",["TCH"])):
    for col in ("gpm","roe_tr"):
        per,mn,md=stats(grp,col)
        print(name,col,"mean-of-means %.1f median %.1f n=%d"%(mn,md,len(per)), {k:"%.1f/min%.1f"%(a,b) for k,(a,b,n) in per.items()})
# latest ROIC5Y / ROIC_Min5Y peer
for t in DEV+AUTO:
    r=[x for x in rows if x['ticker']==t]
    if r: print(t, r[-1]['quarter'], "ROIC5Y",r[-1]['roic5y'],"ROIC_Min5Y",r[-1]['roicmin5y'],"ROIC10Y",r[-1]['roic10y'])
