import csv, glob, os, datetime as dt, re
files = sorted(glob.glob("data/execution_logs/exec_main_*_journal.csv"))
WD = ["T2","T3","T4","T5","T6","T7","CN"]
print(f"{'date':11} {'wd':3} {'cron':>6} | {'PLACE':>5} {'buy':>4} {'sell':>4} | {'buy_in':>6} {'buy_out':>7} | {'sell_in':>7} {'sell_out':>8} | first_ts   last_ts")
rows_out=[]
for f in files:
    d = os.path.basename(f).replace("exec_main_","").replace("_journal.csv","")
    try: day = dt.date.fromisoformat(d)
    except: continue
    if day < dt.date(2026,7,1): continue
    wd = day.weekday()
    cron = "10:46" if wd in (1,3) else ("09:10" if wd in (0,2,4) else "-")
    buy_in=buy_out=sell_in=sell_out=0; nb=ns=0; ts=[]
    with open(f, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["event"] != "PLACE": continue
            ts.append(r["ts"][11:19])
            note = r.get("note") or ""
            inw = "ft:in-window" in note
            if r["side"]=="buy":
                nb+=1
                buy_in += inw; buy_out += (not inw)
            elif r["side"]=="sell":
                ns+=1
                sell_in += inw; sell_out += (not inw)
    tot=nb+ns
    print(f"{d:11} {WD[wd]:3} {cron:>6} | {tot:5} {nb:4} {ns:4} | {buy_in:6} {buy_out:7} | {sell_in:7} {sell_out:8} | {min(ts) if ts else '-':9} {max(ts) if ts else '-'}")
    rows_out.append((d,wd,cron,nb,ns,buy_in,sell_in))
print()
# Gate-1 relevant: BUY placements tagged in-window (any time of day)
g1 = [r for r in rows_out if r[5]>0]
print(f"Sessions with >=1 BUY PLACE ft:in-window : {len(g1)} -> {[r[0] for r in g1]}")
g2 = [r for r in rows_out if r[6]>0]
print(f"Sessions with >=1 SELL PLACE ft:in-window: {len(g2)} -> {[r[0] for r in g2]}")
c1 = [r for r in rows_out if r[2]=='10:46']
print(f"\n10:46 (T3/T5 BUY-window) cron sessions with a journal: {len(c1)}")
print(f"  of which >=1 BUY placed at all : {len([r for r in c1 if r[3]>0])} -> {[r[0] for r in c1 if r[3]>0]}")
print(f"  of which >=1 BUY ft:in-window  : {len([r for r in c1 if r[5]>0])} -> {[r[0] for r in c1 if r[5]>0]}")
