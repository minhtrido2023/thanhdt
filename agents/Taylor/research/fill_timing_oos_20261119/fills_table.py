import json,glob,pandas as pd
acct={}
for f in sorted(glob.glob('/home/trido/thanhdt/WorkingClaude/data/execution_logs/dnse_raw_2026-*.jsonl')):
    for l in open(f):
        try: r=json.loads(l)
        except: continue
        if r.get('kind')!='orders': continue
        for o in r['payload'].get('orders',[]):
            an=str(o.get('accountNo') or r.get('account_no'))
            if an not in('0002023347','0001743768'): continue   # loc account_no (coding_guidelines §12)
            if (o.get('fillQuantity') or 0)>0 and str(o.get('transDate',''))>'2026-06-12': acct[(an,o['id'])]=o
def ict(s): return pd.Timestamp(s[:26].rstrip('Z')).tz_localize('UTC').tz_convert('Asia/Ho_Chi_Minh').strftime('%H:%M')
D=pd.DataFrame([dict(account='SpaceX' if an=='0002023347' else 'ZaloPay',date=o['transDate'],sym=o['symbol'],side='BUY' if o['side']=='NB' else 'SELL',type=o.get('orderType'),qty=o['fillQuantity'],avg=o.get('averagePrice'),created=ict(o['createdDate']),modified=ict(o['modifiedDate'])) for (an,i),o in acct.items()])
D.to_csv('real_fills_postjun12.csv',index=False)
D['blk']=D.created.map(lambda h:'<09:30' if h<'09:30' else '09:30-10:59' if h<'11:00' else '11:00-11:59' if h<'12:00' else '13:00-13:29' if h<'13:30' else '13:30-14:29' if h<'14:30' else '>=14:30')
print(len(D),D.date.nunique(),D.date.min(),D.date.max()); print(D.groupby(['account','side']).size())
print(pd.crosstab([D.account,D.side],D.blk).to_string())
print(D.groupby('side').type.value_counts())
