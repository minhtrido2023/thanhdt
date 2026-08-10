import csv, glob, os, datetime as dt
files = sorted(glob.glob("data/execution_logs/exec_main_*_journal.csv"))
def strict(side, w0, w1):
    out=[]
    for f in files:
        d=os.path.basename(f).replace("exec_main_","").replace("_journal.csv","")
        try: day=dt.date.fromisoformat(d)
        except: continue
        if day < dt.date(2026,7,1): continue
        rows=list(csv.DictReader(open(f,newline="",encoding="utf-8")))
        oids={r["child_oid"] for r in rows if r["event"]=="PLACE" and r["side"]==side
              and "ft:in-window" in (r.get("note") or "")
              and w0 <= dt.time.fromisoformat(r["ts"][11:19]) < w1}
        if oids and any(r["event"]=="FILL" and r["child_oid"] in oids for r in rows):
            out.append(d)
    return out
b=strict("buy", dt.time(10,45), dt.time(11,15))
s=strict("sell", dt.time(9,15), dt.time(9,45))
print(f"GATE 1  BUY  in-window fill sessions : {len(b)}/5  {b}")
print(f"GATE 2  SELL in-window fill sessions : {len(s)}/5  {s}")
