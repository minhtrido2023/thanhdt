import csv, json, statistics as st, math
VN = {}
for x in "2026-08-28,1832.12 2026-08-31,1832.12 2026-09-03,1827.72 2026-09-04,1853.08 2026-09-07,1821.64 2026-09-08,1830.44 2026-09-09,1827.12 2026-09-10,1829.23 2026-09-11,1795.21 2026-09-14,1788.23 2026-09-15,1811.15 2026-09-16,1810.11 2026-09-17,1822.77 2026-09-18,1815.66 2026-09-21,1799.67 2026-09-22,1816.93 2026-09-23,1801.65 2026-09-24,1775.09 2026-09-25,1785.11 2026-09-28,1780.68 2026-09-29,1777.73 2026-09-30,1768.62".split():
    d, v = x.split(","); VN[d] = float(v)
out = {}
for acc in ["SpaceX", "ZaloPay"]:
    rows = [r for r in csv.DictReader(open(f"/home/trido/thanhdt/WorkingClaude/data/execution_logs/nav_history_{acc}.csv")) if "2026-08-31" <= r["date"] <= "2026-09-30"]
    dates = [r["date"] for r in rows]; nav = [float(r["nav"]) for r in rows]; vn = [VN[d] for d in dates]
    def m(series):
        rets = [series[i]/series[i-1]-1 for i in range(1, len(series))]
        sd = st.stdev(rets); peak = series[0]; mdd = 0
        for v in series:
            peak = max(peak, v); mdd = min(mdd, v/peak-1)
        return dict(sd_daily=round(sd*100,3), vol_ann=round(sd*math.sqrt(252)*100,2), mdd=round(mdd*100,2), best=round(max(rets)*100,2), worst=round(min(rets)*100,2), n=len(rets), up_days=sum(r>0 for r in rets))
    rets = [nav[i]/nav[i-1]-1 for i in range(1,len(nav))]; vr = [vn[i]/vn[i-1]-1 for i in range(1,len(vn))]
    mv, mn = st.mean(vr), st.mean(rets)
    beta = sum((a-mn)*(b-mv) for a,b in zip(rets,vr))/sum((b-mv)**2 for b in vr)
    corr = beta*st.stdev(vr)/st.stdev(rets)
    weeks = ["2026-09-04","2026-09-11","2026-09-18","2026-09-25","2026-09-30"]
    wk = [(w, nav[dates.index(w)], round((nav[dates.index(w)]/nav[0]-1)*100,2), VN[w], round((VN[w]/vn[0]-1)*100,2)) for w in weeks]
    last = rows[-1]
    out[acc] = dict(nav0=nav[0], nav1=nav[-1], pl=nav[-1]-nav[0], mtd=round((nav[-1]/nav[0]-1)*100,3), vn_mtd=round((vn[-1]/vn[0]-1)*100,3), port=m(nav), vnidx=m(vn), beta=round(beta,2), corr=round(corr,2), weeks=wk, last=last, dates=dates, nav=nav, vn=vn)
    print(acc, json.dumps({k:v for k,v in out[acc].items() if k not in ("dates","nav","vn")}, ensure_ascii=False))
json.dump(out, open("navstats.json","w"), indent=1)
