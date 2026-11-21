import json,glob,re,pandas as pd,subprocess,io
LOG='/home/trido/thanhdt/WorkingClaude/data/execution_logs/'
A={'0002023347':'SpaceX','0001743768':'ZaloPay'}
acct={}
for f in sorted(glob.glob(LOG+'dnse_raw_2026-*.jsonl')):
    for l in open(f):
        try: r=json.loads(l)
        except: continue
        if r.get('kind')!='orders': continue
        for o in r['payload'].get('orders',[]):
            an=str(o.get('accountNo') or r.get('account_no'))
            if an not in A: continue
            if (o.get('fillQuantity') or 0)>0 and '2026-07-01'<=str(o.get('transDate',''))<='2026-11-16': acct[(an,str(o['id']))]=o
def ict(s): return pd.Timestamp(s[:26].rstrip('Z')).tz_localize('UTC').tz_convert('Asia/Ho_Chi_Minh').strftime('%H:%M')
O=pd.DataFrame([dict(account=A[an],oid=i,date=o['transDate'],sym=o['symbol'],side='BUY' if o['side']=='NB' else 'SELL',type=o.get('orderType'),qty=o['fillQuantity'],avg=o.get('averagePrice'),created=ict(o['createdDate'])) for (an,i),o in acct.items()])
# journal PLACE
rows=[]
for f in sorted(glob.glob(LOG+'exec_*_2026-*_journal.csv')):
    m=re.match(r'.*exec_(SpaceX|ZaloPay)_(\d{4}-\d\d-\d\d)_journal.csv',f)
    if not m: continue
    d=pd.read_csv(f,dtype=str,on_bad_lines='skip'); d=d[d.event=='PLACE']
    d['account']=m.group(1); d['jdate']=m.group(2); rows.append(d[['account','jdate','parent_id','child_oid','ts','note']])
J=pd.concat(rows).drop_duplicates(['account','child_oid'],keep='last').rename(columns={'child_oid':'oid'})
M=O.merge(J,on=['account','oid'],how='left')
def cls(n):
    if pd.isna(n): return 'NO_JOURNAL_MATCH'
    if 'GAP_OPEN_OVERRIDE' in n: return 'GAP_OVERRIDE'
    if 'hyb:blk' in n: return 'HYB_IN_BLOCK'
    if 'ft:out' in n and n.rstrip().endswith('hyb') or '×' in n and 'hyb' in n: return 'HYB_OUT_OF_BLOCK'
    if 'ft:in-window' in n: return 'FT_BASE_IN'
    if 'ft:out' in n: return 'FT_BASE_OUT'
    return 'NO_FT_TAG'
M['cls']=M.note.map(cls)
M['post_0826']=M.date>='2026-08-26'
M.to_csv('orders_classified_raw.csv',index=False)
print(len(O),len(M),M.cls.value_counts().to_string())
print(pd.crosstab(M.post_0826,M.cls))
