# -*- coding: utf-8 -*-
"""
orb_pt.py
=========
Paper-trade LIVE chien luoc ORB intraday VN30F. Chay daily SAU khi phien dong (>=15:00).
Tai dung ket qua moi phien tu bar 1m: sign(OR 09:00-09:30) -> giu den 14:30, no stop.

CONFIG DANG DEPLOY -- CHUA DUOC VALIDATE RIENG (sua 2026-09-25; truoc do docstring nay ghi
"Config CHOT (validated)", la mot claim KHONG truy nguyen duoc):
  Dang chay : exit 14:30 | KHONG stop | tat ca ngay (khong loc |OR|) | size co dinh
              | net slip 1 tick + fee 0.6bps round-trip.
  Config GOC that su tung duoc validate (vn30f_orb_strategy.py grid A, tren 670 phien
              2023-09..2026-06): exit 14:00 | stop 0.7% | loc |OR| >= 0.2% | TC 2.5bps.
  Hai config lech nhau tren 4 truc. Do lai tren rieng nam 2024:
      config GOC (da validate)  : n=76  mean -5.93bps  Sharpe -1.84  cum  -4.50%
      config DANG CHAY          : n=250 mean +5.69bps  Sharpe +1.18  cum +14.43%
  => Khoan lo ca nam 2024 ma gate criterion #2 cua paper_programs_registry.json noi den
     KHONG duoc giai thich; no bi HOA TAN boi viec doi config. Khong co artifact nao trong
     repo validate to hop dang deploy.
  Artifact: mike/agents/Taylor/research/orb_reeval_20260925/FINDINGS.md (job
            Taylor_20260925_052050) muc 7 + C5; forward-test cua config GOC tren dung
            cua so live: .../orb_reeval_20260925/orig_config_forward.md

So paper data/orb_pt_log.csv la APPEND-ONLY: ngay da ghi khong bao gio bi ghi de, chi
append ngay moi; vendor revision tren ngay cu -> giu so cu + ghi data/orb_pt_revisions.log.
Window mo (tu STARTDATE, tich luy tien).
"""
import sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np, pandas as pd
from vnstock import Vnstock

# ORB_PT_WD chi de selfcheck tro vao sandbox (bin/orb_pt_appendonly_selfcheck.py); production bo trong.
WD = os.environ.get("ORB_PT_WD") or r"/home/trido/thanhdt/WorkingClaude"
STARTDATE   = "2026-06-09"
# --- SLEEVE 1B = NOTIONAL, KHONG phai margin (khai bao ro, item 4/6 job Taylor_20260925_095910)
# Cong thuc size la SLEEVE_BASE / (gia x MULT) => chia cho GIA TRI HOP DONG, nen 1B la
# NOTIONAL EXPOSURE muc tieu. Tien ky quy thuc te nho hon nhieu: initial margin VN30F ~17%
# => ~165M cho 5 HD. Con so 17% la tham so VSD/cong ty chung khoan, CHUA doi soat voi DNSE;
# no chi dung de in ra do lon ky quy, KHONG dung trong bat ky phep tinh loi nhuan nao.
SLEEVE_BASE = 1_000_000_000     # 1B NOTIONAL danh rieng ORB (khong phai von ky quy)
MARGIN_RATE_INIT_EST = 0.17     # ~17%, CHUA XAC NHAN voi broker -- chi de hien thi
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
COLS = ["date","or_ret","sig","entry","exit","net"]
if len(R): R = R[COLS]

# ---- SO PAPER APPEND-ONLY (item 3/6 job Taylor_20260925_095910) ----------------------
# Truoc day file nay bi GHI DE hoan toan moi lan chay: vnstock tra lai ca lich su, nen mot
# ban sua du lieu cua vendor se am tham viet lai lich su trial ma khong de lai dau vet.
# (Da quan sat that: request start=end=2026-08-26 tra ve bar tu 2026-08-24 14:02.)
# Luat bay gio: ngay DA CO trong log la BAT KHA XAM PHAM -- chi duoc APPEND ngay moi.
# Neu so tinh lai cho mot ngay cu khac so da luu => vendor revision: GIU so cu, in canh bao,
# ghi 1 dong vao data/orb_pt_revisions.log. KHONG tu dong sua.
LOG = WD+"/data/orb_pt_log.csv"
REVLOG = WD+"/data/orb_pt_revisions.log"
revisions = []
if os.path.exists(LOG):
    prev = pd.read_csv(LOG)
    prev["date"] = prev["date"].astype(str)
    if len(R):
        cur = R.set_index("date")
        for _, pr in prev.iterrows():
            if pr["date"] not in cur.index: continue
            c = cur.loc[pr["date"]]
            if abs(float(pr["net"]) - float(c["net"])) > 1e-12 or int(pr["sig"]) != int(c["sig"]):
                revisions.append((pr["date"], float(pr["net"]), float(c["net"]),
                                  int(pr["sig"]), int(c["sig"])))
        fresh = R[~R["date"].isin(set(prev["date"]))]
    else:
        fresh = R
    n_new = len(fresh)
    R = pd.concat([prev[COLS], fresh], ignore_index=True) if n_new else prev[COLS].copy()
    R = R.sort_values("date").reset_index(drop=True)
    if revisions:
        print(f"\n  !! VENDOR REVISION: {len(revisions)} ngay da luu co so tinh lai KHAC."
              f" GIU so cu (append-only). Chi tiet -> data/orb_pt_revisions.log")
        with open(REVLOG, "a", encoding="utf-8") as fp:
            for d, on, nn, osg, nsg in revisions:
                print(f"     {d}: net luu {on:+.6f} vs tinh lai {nn:+.6f} | sig {osg:+d} -> {nsg:+d}")
                fp.write(f"asof_bar={last_bar}\tdate={d}\tnet_stored={on:+.8f}"
                         f"\tnet_refetch={nn:+.8f}\tsig_stored={osg:+d}\tsig_refetch={nsg:+d}\n")
    print(f"  Log append-only: {len(prev)} ban ghi cu giu nguyen + {n_new} ngay moi = {len(R)}")

# ---- forward instruction (sizing for next session) ----
# Kiem lai 2026-09-25: 1 HD = latest_px*MULT ~ 194.5M = 19.45% sleeve => so HD ly tuong ~5.14,
# lam tron xuong 5 => notional thuc 97.2% muc tieu, tuc THIEU ~2.7% size. Day la gioi han
# NGUYEN cua don vi hop dong (khong chia nho duoc), khong phai loi cong thuc: round() da la
# lua chon gan muc tieu nhat. Nhung no PHAI duoc khai bao, vi:
#   cot `net`/`nav` trong log la LOI SUAT thuan (sig*(xf/ef-1)-FEE), KHONG tham chieu so HD
#   => no ngam dinh exposure = DUNG 1B notional (so HD chia nho duoc).
#   Ban trien khai duoc voi 5 HD chi an notional_pct x loi suat do.
# => NAV/cum trong log la GIOI HAN TREN, cao hon ban 5-HD khoang (1 - notional_pct).
contracts = round(SLEEVE_BASE/(latest_px*MULT))
notional_1ct   = latest_px*MULT
notional_actual= contracts*notional_1ct
notional_pct   = notional_actual/SLEEVE_BASE
margin_est     = notional_actual*MARGIN_RATE_INIT_EST

status={
    "asof_bar": str(last_bar), "latest_vn30f": round(latest_px,1),
    "rule": "09:30 lay dau cu 09:00-09:30 -> long/short giu den 14:30, no stop",
    "reco_contracts": int(contracts), "sleeve_base": SLEEVE_BASE,
    "sleeve_basis": "NOTIONAL",
    "notional_per_contract": round(notional_1ct),
    "notional_actual": round(notional_actual),
    "notional_pct_of_sleeve": round(notional_pct, 4),
    "size_error_pct": round(notional_pct-1, 4),
    "margin_required_est": round(margin_est),
    "margin_rate_init_est": MARGIN_RATE_INIT_EST,
    "margin_rate_verified": False,
    "nav_basis": "loi suat tren DUNG 1B notional (HD chia nho duoc) -> gioi han tren "
                 "cua ban 5-HD; nhan voi notional_pct de co ban trien khai duoc",
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
print(f"     Size = {contracts} HD VN30F (sleeve {SLEEVE_BASE/1e9:.0f}B NOTIONAL / [{latest_px:.0f}x{MULT:,}])")
print(f"     1 HD = {notional_1ct/1e6:,.1f}M = {notional_1ct/SLEEVE_BASE*100:.2f}% sleeve"
      f" -> {contracts} HD = {notional_actual/1e6:,.1f}M = {notional_pct*100:.1f}% muc tieu"
      f" ({(notional_pct-1)*100:+.1f}% size error do lam tron)")
print(f"     Ky quy uoc tinh {margin_est/1e6:,.0f}M (~{MARGIN_RATE_INIT_EST*100:.0f}% notional,"
      f" CHUA doi soat voi broker) — sleeve 1B la NOTIONAL, KHONG phai von ky quy")
print(f"     LUU Y: cot net/nav trong log la loi suat tren DUNG 1B notional (HD chia nho duoc)"
      f" => gioi han TREN; ban 5-HD an ~{notional_pct*100:.1f}% so do")

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
R.to_csv(LOG, index=False, float_format="%.17g")   # 17g = round-trip chinh xac float64:
#   log bi doc-roi-ghi lai moi lan chay, mac dinh cua pandas lam cut chu so cuoi va sai so
#   se tich luy dan qua nhieu nam. Voi %.17g thi read->write la bat bien.
print(f"\n  Log -> data/orb_pt_log.csv | status -> data/orb_pt_status.json")
print("Done.")
