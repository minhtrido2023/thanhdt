import sys, importlib.util, datetime, random, json
D=datetime.date
def load(dirname, name, alias):
    # isolated import: each tree gets own account_cash_flows
    import importlib
    sys.path.insert(0, dirname)
    for m in ("account_cash_flows","nav_unit_ledger","nav_period_returns"):
        sys.modules.pop(m, None)
    mod = importlib.import_module(name)
    acf = sys.modules["account_cash_flows"]
    sys.path.pop(0)
    for m in ("account_cash_flows","nav_unit_ledger","nav_period_returns"):
        sys.modules.pop(m, None)
    return mod, acf
old, old_acf = load("/tmp/archrev_fu/master_bin","nav_period_returns","old")
new, new_acf = load("/tmp/archrev_fu/branch_bin","nav_period_returns","new")
WC="/home/trido/thanhdt/WorkingClaude"
# 1. real data, every date, both accounts: legacy keys byte-identical?
nd=0; mism=[]
for acc in ("SpaceX","ZaloPay"):
    rows_o = old.load_nav_history(acc, WC+"/data/execution_logs"); rows_n = new.load_nav_history(acc, WC+"/data/execution_logs")
    assert [tuple(r) for r in rows_n]==rows_o
    inc = old.load_inception(acc, WC+"/data/account_inception.json")
    f0 = datetime.date.fromisoformat(inc["inception_date"])
    d = f0
    last = rows_o[-1][0] + datetime.timedelta(days=3)
    while d <= last:
        try: o = old.compute_period_returns(acc, d, rows_o, inc, [])
        except Exception as e: o = ("ERR", type(e).__name__, str(e)[:60])
        try: n = new.compute_period_returns(acc, d, rows_n, inc, [])
        except Exception as e: n = ("ERR", type(e).__name__, str(e)[:60])
        nd+=1
        if isinstance(o,tuple) or isinstance(n,tuple):
            if o!=n: mism.append((acc,d,o,n))
        else:
            for per in ("inception","wtd","mtd"):
                for k in o[per]:
                    if o[per][k]!=n[per].get(k,"<MISSING>"): mism.append((acc,d,per,k,o[per][k],n[per].get(k)))
        d += datetime.timedelta(days=1)
print("real-data dates compared:", nd, "mismatches:", len(mism)); print(mism[:8])
# raw unrounded factor bit-equality (no flows)
bit=0; tot=0; maxrel=0
for acc in ("SpaceX","ZaloPay"):
    rows = new.load_nav_history(acc, WC+"/data/execution_logs"); inc=new.load_inception(acc, WC+"/data/account_inception.json")
    f0,n0 = new._inception_baseline(rows, inc)
    led,_ = new.build_ledger(rows, [], f0, n0)
    for i,a in enumerate(led):
        for b in led[i+1:]:
            tot+=1
            fn = b["unit_price"]/a["unit_price"]; fo = b["nav"]/a["nav"]
            if fn==fo: bit+=1
            maxrel=max(maxrel, abs(fn/fo-1))
print(f"no-flow pairwise factor: bit-identical {bit}/{tot}, max rel diff {maxrel:.3e}")
# rounded 3dp pairwise
bad=0
for acc in ("SpaceX","ZaloPay"):
    rows = new.load_nav_history(acc, WC+"/data/execution_logs"); inc=new.load_inception(acc, WC+"/data/account_inception.json")
    f0,n0 = new._inception_baseline(rows, inc)
    led,_ = new.build_ledger(rows, [], f0, n0)
    for i,a in enumerate(led):
        for b in led[i+1:]:
            if round((b["unit_price"]/a["unit_price"]-1)*100,3)!=round((b["nav"]/a["nav"]-1)*100,3): bad+=1
print("no-flow pairwise rounded-3dp differences:", bad)
# 2. random flows: old vs new return_pct for same explicit timing
rng=random.Random(7)
INC={"inception_date":"2026-07-01","starting_capital":1_000_000_000}
diffs=[]; n=0; errs=0
for case in range(3000):
    nav=1e9; day=D(2026,7,1); rows=[]; flows=[]
    for _ in range(rng.randint(3,25)):
        day+=datetime.timedelta(days=rng.choice([1,1,1,3]))
        r=rng.uniform(-0.04,0.04); fb=fe=0
        if rng.random()<0.3:
            fb=float(round(nav*rng.uniform(-0.5,0.5))); 
            if fb: flows.append({"date":day,"amount_vnd":fb,"kind":"deposit" if fb>0 else "withdraw","evidence":"x","timing":"bod","time_ict":"10:00"})
        nav=(nav+fb)*(1+r)
        if rng.random()<0.3:
            fe=float(round(nav*rng.uniform(-0.5,0.5)))
            if fe: flows.append({"date":day,"amount_vnd":fe,"kind":"deposit" if fe>0 else "withdraw","evidence":"x","timing":"eod","time_ict":None})
        nav+=fe; rows.append((day,nav))
    rd = rows[rng.randrange(len(rows))][0]
    try:
        o=old.compute_period_returns("X",rd,rows,INC,flows); 
        nn=new.compute_period_returns("X",rd,[new.NavRow(*r) if hasattr(new,'NavRow') else r for r in rows],INC,flows)
    except Exception as e:
        errs+=1; continue
    n+=1
    for per in ("inception","wtd","mtd"):
        for k in ("from_date","to_date","nav0","nav1","return_pct","net_flow_vnd"):
            if o[per].get(k)!=nn[per].get(k): diffs.append((case,per,k,o[per].get(k),nn[per].get(k)))
        if o[per].get("cash_flows")!=nn[per].get("cash_flows"): diffs.append((case,per,"cash_flows"))
print("random flow cases:",n,"errs",errs,"diffs:",len(diffs)); print(diffs[:10])
