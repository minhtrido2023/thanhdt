import csv, glob, os, datetime as dt
files = sorted(glob.glob("data/execution_logs/exec_main_*_journal.csv"))
print("=== BUY orders tagged ft:in-window, and whether they FILLED ===")
tot_sess=0
for f in files:
    d = os.path.basename(f).replace("exec_main_","").replace("_journal.csv","")
    try: day = dt.date.fromisoformat(d)
    except: continue
    if day < dt.date(2026,7,1): continue
    rows=list(csv.DictReader(open(f,newline="",encoding="utf-8")))
    inw_oids={}
    for r in rows:
        if r["event"]=="PLACE" and r["side"]=="buy" and "ft:in-window" in (r.get("note") or ""):
            inw_oids[r["child_oid"]]=(r["ticker"], r["ts"][11:19], int(r["qty"] or 0))
    if not inw_oids: continue
    fills={}
    for r in rows:
        if r["event"]=="FILL" and r["child_oid"] in inw_oids:
            fills[r["child_oid"]]=fills.get(r["child_oid"],0)+int(float(r["qty"] or 0))
    nfilled=sum(1 for o in inw_oids if fills.get(o,0)>0)
    tot_sess += 1 if nfilled>0 else 0
    print(f"{d}: {len(inw_oids)} BUY in-window PLACE @ {sorted(set(v[1] for v in inw_oids.values()))} | FILLED {nfilled}/{len(inw_oids)}")
print(f"\n>>> SESSIONS WITH >=1 BUY *FILL* IN WINDOW = {tot_sess}")
print()
print("=== FAIL / ERROR / REJECT events per session (gate 3) ===")
for f in files:
    d = os.path.basename(f).replace("exec_main_","").replace("_journal.csv","")
    try: day = dt.date.fromisoformat(d)
    except: continue
    if day < dt.date(2026,7,1): continue
    rows=list(csv.DictReader(open(f,newline="",encoding="utf-8")))
    bad=[r["event"] for r in rows if any(k in r["event"].upper() for k in ("FAIL","ERROR","REJECT"))]
    if bad:
        from collections import Counter
        print(f"{d}: {dict(Counter(bad))}")
