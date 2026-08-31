import csv, statistics as st

rows = list(csv.DictReader(open('breadth_12mo_raw.csv')))
episodes = sorted(set(r['episode'] for r in rows))

EXCLUDE = {'VNINDEX', 'VN30'}

print(f"{'episode':10s} {'n_stocks':>8s} {'pct_pos':>8s} {'median_ret':>11s} {'vnindex_ret':>11s} {'gap(idx-med)':>13s}")
summary = {}
for ep in episodes:
    stock_rets = [float(r['ret_12mo']) for r in rows if r['episode']==ep and r['ticker'] not in EXCLUDE and r['ret_12mo']]
    idx_row = [r for r in rows if r['episode']==ep and r['ticker']=='VNINDEX']
    idx_ret = float(idx_row[0]['ret_12mo']) if idx_row else None
    n = len(stock_rets)
    pct_pos = sum(1 for x in stock_rets if x>0)/n*100
    med = st.median(stock_rets)
    gap = (idx_ret - med) if idx_ret is not None else None
    summary[ep] = dict(n=n, pct_pos=pct_pos, med=med, idx_ret=idx_ret, gap=gap)
    print(f"{ep:10s} {n:8d} {pct_pos:7.1f}% {med*100:10.2f}% {idx_ret*100:10.2f}% {gap*100:12.2f}pp")
