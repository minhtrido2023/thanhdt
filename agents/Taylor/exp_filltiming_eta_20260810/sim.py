import sys, os, json, datetime as dt
sys.path.insert(0,"/home/trido/thanhdt/WorkingClaude")
os.environ.setdefault("TZ","Asia/Ho_Chi_Minh")
import importlib.util
spec=importlib.util.spec_from_file_location("ppp","/home/trido/thanhdt/WorkingClaude/mike/bin/paper_main_probe_plan.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

held=json.load(open(m.PAPER_STATE))["positions"]
held={k:int(v) for k,v in held.items() if v>0}
px,sig=m.latest_closes(sorted(set(m.BASKET)|set(held)))
print("held (paper state, sau phien 08-10):",held)
print("px:",{k:int(v) for k,v in px.items()}, "signal_date",sig)
print()

OLD={0:1.00,1:0.75,2:0.90,3:0.70,4:0.85}
NEW={0:0.85,1:1.00,2:0.75,3:0.90,4:0.70}   # rotate old map by ONE weekday

def net(day, factors, h):
    m.BUY_VALUE_FACTOR = factors
    p = m.build_plan(day, h, px, sig)
    buys={o.ticker:o.qty for o in p.orders if o.side=="buy"}
    sells={o.ticker:o.qty for o in p.orders if o.side=="sell"}
    res={t: buys.get(t,0)-sells.get(t,0) for t in sorted(set(buys)|set(sells))}
    return res, buys

WD=["T2","T3","T4","T5","T6"]
for label,F in (("OLD (hien tai)",OLD),("NEW (rotate 1 ngay)",NEW)):
    print(f"--- {label}: F={F} ---")
    h=dict(held)
    for d in ["2026-08-11","2026-08-12","2026-08-13","2026-08-14","2026-08-17","2026-08-18"]:
        day=dt.date.fromisoformat(d); 
        r,buys=net(d,F,h)
        nb=sum(1 for v in r.values() if v>0); ns=sum(1 for v in r.values() if v<0); nz=sum(1 for v in r.values() if v==0)
        cron = "10:46 BUY-win" if day.weekday() in (1,3) else "09:10 SELL-win"
        flag = ""
        if day.weekday() in (1,3):
            flag = "  <== GATE-1 EVIDENCE" if nb>0 else "  <== 0 BUY (khong co evidence)"
        print(f" {d} {WD[day.weekday()]} f={F[day.weekday()]:.2f} cron={cron:14} net: +{nb} buy / -{ns} sell / {nz} zero {dict(r)}{flag}")
        h=dict(buys)   # cuoi ngay giu dung qty mua
    print()
