# -*- coding: utf-8 -*-
"""Recompute dividend-adjusted position returns for the 3 published reports."""

DIV = {  # ticker: (ex_date, cash dividend VND/share) — verified BQ ratio-jump + broker receivable
    "MBB": ("2026-07-09", 1000), "BID": ("2026-07-17", 450),
    "CTG": ("2026-07-23", 450),  "VCB": ("2026-07-23", 450),
    "NCT": ("2026-07-27", 8000), "SAB": ("2026-07-28", 3000),
}

# ---- SpaceX, portfolio at 31/07 (from weekly report 27-31/07 §4.2 / monthly §7.1) ----
SPX = [  # ticker, qty, verified cost/share (raw fill), price 31/07, group
    ("SIP",1700,47059,48100,"CAPIT"), ("VCB",1300,62300,59300,"Bank"),
    ("VHM",500,149800,148100,"RE"),   ("BID",1900,42991,38000,"Bank"),
    ("CTG",2300,34477,30800,"Bank"),  ("PVT",3500,17100,18300,"CAPIT"),
    ("TCB",2000,33900,28950,"Bank"),  ("VPB",2300,27914,24800,"Bank"),
    ("VNM",900,58600,60900,"CAPIT"),  ("MBB",2400,25850,22500,"Bank"),
    ("SAB",1100,47368,43550,"CAPIT"), ("LPB",900,52583,51800,"Bank"),
    ("NCT",500,94360,83400,"CAPIT"),  ("HDB",1500,26675,25200,"Bank"),
    ("ACB",1500,22650,21900,"Bank"),  ("SHB",1500,13550,11500,"Bank"),
    ("TPB",800,16800,14100,"Bank"),   ("VIX",700,17000,13000,"Broker"),
    ("TV1",400,19600,19600,"Other"),  ("VND",300,17800,16600,"Broker"),
    ("SHS",200,18900,15200,"Broker"),
]
# Reported figures in the published tables (VND P&L, %)
SPX_REPORTED = {"SIP":(1770000,2.2),"VCB":(-3900000,-4.8),"VHM":(-850000,-1.1),
 "BID":(-9483478,-11.6),"CTG":(-8456607,-10.7),"PVT":(4200000,7.0),"TCB":(-9900000,-14.6),
 "VPB":(-7162857,-11.2),"VNM":(2070000,3.9),"MBB":(-8040000,-13.0),"SAB":(-4200000,-8.1),
 "LPB":(-705000,-1.5),"NCT":(-5480000,-11.6),"HDB":(-2212500,-5.5),"ACB":(-1125000,-3.3),
 "SHB":(-3075000,-15.1),"TPB":(-2160000,-16.1),"VIX":(-2800000,-23.5),"TV1":(0,0.0),
 "VND":(-360000,-6.7),"SHS":(-740000,-19.6)}
SPX_COST_TOTAL = 986725443   # as published

# ---- ZaloPay, bot-bought 14 tickers at 31/07 (broker costPrice is ALREADY div-reduced) ----
ZLP = [  # ticker, qty, broker costPrice (div-adjusted), price 31/07
    ("VCB",800,60912.5,59300), ("VHM",300,148633.3333,148100),
    ("PVT",2071,17248.31,18300), ("VNM",601,58699.8336,60900),
    ("SIP",749,47140.0534,48100), ("BID",900,40316.6667,38000),
    ("SAB",744,44450.2016,43550), ("CTG",1050,32133.3334,30800),
    ("NCT",373,86400.0,83400),   ("TCB",956,31610.8786,28950),
    ("MBB",1102,24597.9129,22500),("CSV",1000,19750.0,21200),
    ("LPB",352,54843.1818,51800),("HDB",659,25891.047,25200),
]

def line(s): print(s)

line("="*100)
line("A. SPACEX — DANH MUC 31/07: % lai/lo DA CONG LAI CO TUC (total return tren gia von goc)")
line("="*100)
line(f"{'Ma':5s} {'KL':>5s} {'GiaVon':>9s} {'Gia31/07':>9s} {'Div/cp':>7s} {'PL_gia':>13s} {'CoTuc':>12s} {'PL_tong':>13s} {'%cu':>7s} {'%moi':>7s} {'Delta_pp':>8s}")
tot_cost=tot_div=tot_pl=0
for t,q,c,p,g in SPX:
    d = DIV[t][1] if t in DIV else 0
    plp = q*(p-c); div = q*d; tot = plp+div
    pct_old = plp/(q*c)*100; pct_new = tot/(q*c)*100
    rep = SPX_REPORTED[t]
    tot_cost += q*c; tot_div += div; tot_pl += plp
    flag = " <<<" if d else ""
    line(f"{t:5s} {q:5d} {c:9,.0f} {p:9,.0f} {d:7,d} {plp:13,.0f} {div:12,.0f} {tot:13,.0f} {rep[1]:7.1f} {pct_new:7.1f} {pct_new-rep[1]:8.2f}{flag}")
line("-"*100)
line(f"TONG gia von (tinh lai) = {tot_cost:,.0f}  (bao cao cong bo {SPX_COST_TOTAL:,.0f}, lech {tot_cost-SPX_COST_TOTAL:,.0f})")
line(f"TONG lai/lo GIA = {tot_pl:,.0f} | CO TUC = {tot_div:,.0f} | TONG = {tot_pl+tot_div:,.0f}")
line(f"% cu (bao cao)  = {tot_pl/SPX_COST_TOTAL*100:.2f}%   -> % moi (gom co tuc) = {(tot_pl+tot_div)/SPX_COST_TOTAL*100:.2f}%")

line("")
line("="*100)
line("B. SPACEX — attribution theo nhom (monthly §3.2)")
line("="*100)
grp={}
for t,q,c,p,g in SPX:
    d=DIV[t][1] if t in DIV else 0
    a=grp.setdefault(g,[0,0,0]); a[0]+=q*p; a[1]+=q*(p-c); a[2]+=q*d
G=sum(v[1] for v in grp.values()); Gn=sum(v[1]+v[2] for v in grp.values())
line(f"{'Nhom':8s} {'GiaTriTT':>14s} {'PL_gia(cu)':>14s} {'%tong_cu':>9s} {'CoTuc':>12s} {'PL+div':>14s} {'%tong_moi':>10s}")
for g,v in sorted(grp.items(), key=lambda x:x[1][1]):
    line(f"{g:8s} {v[0]:14,.0f} {v[1]:14,.0f} {v[1]/G*100:8.1f}% {v[2]:12,.0f} {v[1]+v[2]:14,.0f} {(v[1]+v[2])/Gn*100:9.1f}%")
line(f"{'TONG':8s} {sum(v[0] for v in grp.values()):14,.0f} {G:14,.0f} {'100.0%':>9s} {sum(v[2] for v in grp.values()):12,.0f} {Gn:14,.0f} {'100.0%':>10s}")

line("")
line("="*100)
line("C. ZALOPAY — 14 ma bot mua, 31/07 (gia von THO = broker costPrice + co tuc da tru)")
line("="*100)
line(f"{'Ma':5s} {'KL':>5s} {'Von_tho':>10s} {'Gia31/07':>9s} {'Div/cp':>7s} {'PL_gia':>13s} {'CoTuc':>12s} {'%cu':>7s} {'%moi':>7s}")
zc=zpl=zdiv=0
for t,q,cb,p in ZLP:
    d = DIV[t][1] if t in DIV else 0
    craw = cb + d           # broker cost is div-reduced -> add back to get raw fill cost
    plp = q*(p-craw); div = q*d
    zc += q*craw; zpl += plp; zdiv += div
    line(f"{t:5s} {q:5d} {craw:10,.1f} {p:9,.0f} {d:7,d} {plp:13,.0f} {div:12,.0f} {plp/(q*craw)*100:7.1f} {(plp+div)/(q*craw)*100:7.1f}")
line("-"*100)
line(f"TONG gia von tho = {zc:,.0f}  (bao cao cong bo 454.848.300, lech {zc-454848300:,.0f})")
line(f"PL_gia = {zpl:,.0f} ({zpl/454848300*100:.2f}%)  | CO TUC = {zdiv:,.0f}  | TONG = {zpl+zdiv:,.0f} ({(zpl+zdiv)/454848300*100:.2f}%)")
