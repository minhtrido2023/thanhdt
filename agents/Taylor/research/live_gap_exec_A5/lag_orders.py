"""A5 việc 2b: trích lệnh MUA book LAG trong plan chính tắc (SpaceX/ZaloPay) + fill từ journal per-account.
Nguồn: data/trade_plans/plan_{acct}_{date}.json (CANONICAL, registry trading-bot/trade_plans.md);
journal data/execution_logs/exec_{acct}_{date}_journal.csv (file riêng mỗi account ⇒ lọc account theo tên file + assert plan.account)."""
import json,glob,re,csv,os,sys
WC='/home/trido/thanhdt/WorkingClaude'; rows=[]
for f in sorted(glob.glob(f'{WC}/data/trade_plans/plan_*_*.json')):
    m=re.search(r'plan_(SpaceX|ZaloPay)_(\d{4}-\d\d-\d\d)\.json$',f)
    if not m: continue
    acct,dt=m.groups(); d=json.load(open(f))
    assert d.get('account',acct)==acct,(f,d.get('account'))
    for kind in ('orders','deferred_orders'):
        for o in d.get(kind,[]):
            if str(o.get('book','')).upper()!='LAG' or o.get('side')!='buy': continue
            note=o.get('adv_note') or o.get('dd_summary') or ''
            adv=re.search(r'ADV\w*\s*([\d.,]+)\s*B',note)
            oid=o.get('id'); j=f'{WC}/data/execution_logs/exec_{acct}_{dt}_journal.csv'; fq=0; ev=set()
            if oid and os.path.exists(j):
                for r in csv.DictReader(open(j)):
                    if r['parent_id']==oid:
                        ev.add(r['event'])
                        if r['event']=='FILL': fq+=float(r['qty'] or 0)
            rows.append(dict(acct=acct,date=dt,kind=kind,id=oid,tk=o.get('ticker'),qty=o.get('qty'),px=o.get('ref_price'),
                 adv_note_B=(float(adv.group(1).replace(',','.')) if adv else None),fillq=fq,ev='|'.join(sorted(ev)),
                 approved=bool(d.get('approved_by')),signal_date=d.get('signal_date')))
json.dump(rows,open(sys.argv[1],'w'),ensure_ascii=False,indent=0)
for x in rows: print(x['acct'][:2],x['date'],x['signal_date'],x['kind'][:3],x['id'],x['tk'],x['qty'],x['px'],x['adv_note_B'],x['fillq'],x['ev'],x['approved'])
print('N',len(rows))
