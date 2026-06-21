# -*- coding: utf-8 -*-
"""
orb_pt.py
=========
Paper-trade LIVE chien luoc ORB intraday VN30F. Chay daily SAU khi phien dong (>=15:00).
Tai dung ket qua moi phien tu bar 1m: sign(OR 09:00-09:30) -> giu den 14:30, no stop.
Config CHOT (validated): tat ca ngay (khong loc |OR|), size co dinh, net slip 1tick + fee.
Idempotent: dung lai tu vnstock moi lan chay. Window mo (tu STARTDATE, tich luy tien).
"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np, pandas as pd
from vnstock import Vnstock

WD = r"/home/trido/thanhdt/WorkingClaude"
STARTDATE   = "2026-06-09"
SLEEVE_BASE = 1_000_000_000     # 1B von danh rieng ORB
TICK        = 0.1
SLIP_TICKS  = 1                 # ~0.5bps/side thuc te VN30F thanh khoan cao
FEE         = 0.00006           # brokerage+tax round-trip ~0.6bps
MULT        = 100_000

# ---- fetch 1m, build per-day ORB result ----
f = Vnstock().stock(symbol="VN30F1M", source="VCI").quote.history(
        start="2026-05-15", end="2026-12-31", interval="1m")
f["time"]=pd.to_datetime(f["time"]); f=f.sort_values("time").reset_index(drop=True)
f["date"]=f["time"].dt.date; f["hm"]=f["time"].dt.strftime("%H:%M")
last_bar = f["time"].iloc[-1]
latest_px = float(f["close"].iloc[-1])

recs=[]
for d,g in f.groupby("date"):
    if str(d) < STARTDATE: continue
    g=g.sort_values("time")
    op=g[g["hm"]<="09:30"]
    seg=g[(g["hm"]>"09:30")&(g["hm"]<="14:30")]
    complete = len(op)>=10 and len(seg)>0 and g["hm"].iloc[-1]>="14:25"
    if not complete: continue          # phien chua dong -> bo qua, lan sau tinh
    entry=op["close"].iloc[-1]; exitpx=seg["close"].iloc[-1]
    or_ret=entry/g["close"].iloc[0]-1; sig=int(np.sign(or_ret))
    if sig==0: continue
    ef=entry+sig*SLIP_TICKS*TICK; xf=exitpx-sig*SLIP_TICKS*TICK
    net=sig*(xf/ef-1)-FEE
    recs.append({"date":str(d),"or_ret":or_ret,"sig":sig,"entry":entry,"exit":exitpx,"net":net})
R=pd.DataFrame(recs)

# ---- forward instruction (sizing for next session) ----
contracts = round(SLEEVE_BASE/(latest_px*MULT))

status={
    "asof_bar": str(last_bar), "latest_vn30f": round(latest_px,1),
    "rule": "09:30 lay dau cu 09:00-09:30 -> long/short giu den 14:30, no stop",
    "reco_contracts": int(contracts), "sleeve_base": SLEEVE_BASE,
    "window_start": STARTDATE, "n_days":0, "window_started": False,
    "last_date":None,"last_sig":None,"last_or":None,"last_net":None,
    "cum_ret":None,"wr":None,"sharpe":None,"nav":None,
}
def _write():
    with open(WD+"/data/orb_pt_status.json","w",encoding="utf-8") as fp:
        json.dump(status, fp, ensure_ascii=False, indent=2)

print("="*92)
print(f"  ORB intraday VN30F — PAPER-TRADE LIVE (tu {STARTDATE}) | sleeve {SLEEVE_BASE/1e9:.0f}B")
print(f"  Rule: sign(OR 09:00-09:30) giu den 14:30, no stop, net slip {SLIP_TICKS}tick + fee {FEE*1e4:.1f}bps")
print("="*92)
print(f"\n  Data den: {last_bar} | VN30F={latest_px:.1f}")
print(f"  >> Phien KE TIEP: {status['rule']}")
print(f"     Size = {contracts} HD VN30F (sleeve {SLEEVE_BASE/1e9:.0f}B / [{latest_px:.0f}x{MULT:,}])")

if len(R)==0:
    print(f"\n  [Chua co phien hoan chinh >= {STARTDATE}] (phien hom nay co the chua dong).")
    _write(); print("Done."); sys.exit()

R["nav"]=SLEEVE_BASE*(1+R["net"]).cumprod()
cum=R["nav"].iloc[-1]/SLEEVE_BASE-1; wr=(R["net"]>0).mean()
sh=R["net"].mean()/R["net"].std()*np.sqrt(252) if (len(R)>1 and R["net"].std()>0) else 0
last=R.iloc[-1]
print(f"\n  --- Lich su ORB tu {STARTDATE} ---")
print(f"  {'Date':<12}{'OR%':>8}{'Side':>6}{'net%':>8}{'NAV':>16}")
print("  "+"-"*52)
for _,r in R.iterrows():
    side="LONG" if r["sig"]>0 else "SHORT"
    print(f"  {r['date']:<12}{r['or_ret']*100:>+7.2f}%{side:>6}{r['net']*100:>+7.2f}%{r['nav']:>16,.0f}")
print("  "+"-"*52)
print(f"\n  TONG KET {len(R)} phien: WR {wr*100:.0f}% | cum {cum*100:+.2f}% | Sharpe {sh:.2f} | NAV {R['nav'].iloc[-1]:,.0f}")

status.update({"n_days":int(len(R)),"window_started":True,
               "last_date":last["date"],"last_sig":int(last["sig"]),
               "last_or":round(float(last["or_ret"]),4),"last_net":round(float(last["net"]),4),
               "cum_ret":round(float(cum),4),"wr":round(float(wr),3),
               "sharpe":round(float(sh),2),"nav":int(R["nav"].iloc[-1])})
_write()
R.to_csv(WD+"/data/orb_pt_log.csv", index=False)
print(f"\n  Log -> data/orb_pt_log.csv | status -> data/orb_pt_status.json")
print("Done.")
