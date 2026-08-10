import csv, glob, os, datetime as dt
files = sorted(glob.glob("data/execution_logs/exec_main_*_journal.csv"))
W0,W1 = dt.time(10,45), dt.time(11,15)
print("STRICT gate-1 evidence = BUY PLACE with ts in [10:45,11:15) AND ft:in-window AND >=1 FILL")
sess=[]
for f in files:
    d = os.path.basename(f).replace("exec_main_","").replace("_journal.csv","")
    try: day = dt.date.fromisoformat(d)
    except: continue
    if day < dt.date(2026,7,1): continue
    rows=list(csv.DictReader(open(f,newline="",encoding="utf-8")))
    oids={}
    for r in rows:
        if r["event"]!="PLACE" or r["side"]!="buy": continue
        t=dt.time.fromisoformat(r["ts"][11:19])
        if W0<=t<W1 and "ft:in-window" in (r.get("note") or ""):
            oids[r["child_oid"]]=r["ticker"]
    if not oids: continue
    filled=set(r["child_oid"] for r in rows if r["event"]=="FILL" and r["child_oid"] in oids)
    if filled:
        sess.append(d); print(f"  {d} ({['T2','T3','T4','T5','T6'][day.weekday()]}): {len(filled)}/{len(oids)} in-window BUY orders FILLED")
print(f"\n>>> STRICT SESSION COUNT = {len(sess)} / 5 required   -> shortfall {max(0,5-len(sess))}")
print()
print("=== NON-strict false positives (ft:in-window BUY outside 10:45-11:15) ===")
for f in files:
    d = os.path.basename(f).replace("exec_main_","").replace("_journal.csv","")
    try: day = dt.date.fromisoformat(d)
    except: continue
    if day < dt.date(2026,7,1): continue
    for r in csv.DictReader(open(f,newline="",encoding="utf-8")):
        if r["event"]=="PLACE" and r["side"]=="buy" and "ft:in-window" in (r.get("note") or ""):
            t=dt.time.fromisoformat(r["ts"][11:19])
            if not (W0<=t<W1): print(f"  {d} {r['ts'][11:19]} {r['ticker']} note={r['note']}")
