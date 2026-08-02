# -*- coding: utf-8 -*-
"""Final correction table for the 3 published reports (dividend adjustment)."""
DIV = {"MBB":("2026-07-09",1000),"BID":("2026-07-17",450),"CTG":("2026-07-23",450),
       "VCB":("2026-07-23",450),"NCT":("2026-07-27",8000),"SAB":("2026-07-28",3000)}
# Entitlement verified against broker cashDividendReceiving (exact match, both accounts)
ENT = {"SpaceX":{"MBB","BID","CTG","VCB","NCT","SAB"},
       "ZaloPay":{"BID","CTG","VCB","NCT","SAB"}}   # ZaloPay bought MBB AFTER ex 09/07

def d_of(acc,t): return DIV[t][1] if (t in DIV and t in ENT[acc]) else 0

# ---------------- ZaloPay bot-bought basket, raw (pre-dividend) cost from broker ----------
ZLP_BROKER_31 = {"VCB":(800,60912.5),"VHM":(300,148633.3333),"PVT":(2071,17248.31),
 "VNM":(601,58699.8336),"SIP":(749,47140.0534),"BID":(900,40316.6667),"SAB":(744,44450.2016),
 "CTG":(1050,32133.3334),"NCT":(373,86400.0),"TCB":(956,31610.8786),"MBB":(1102,24597.9129),
 "CSV":(1000,19750.0),"LPB":(352,54843.1818),"HDB":(659,25891.047)}
P31 = {"VCB":59300,"VHM":148100,"PVT":18300,"VNM":60900,"SIP":48100,"BID":38000,"SAB":43550,
 "CTG":30800,"NCT":83400,"TCB":28950,"MBB":22500,"CSV":21200,"LPB":51800,"HDB":25200}

print("="*104)
print("C. ZALOPAY 31/07 — 14 ma bot mua  (gia von THO = costPrice broker + co tuc broker da tru)")
print("="*104)
print(f"{'Ma':5s}{'KL':>6s}{'VonTho':>11s}{'Gia31/07':>10s}{'Div/cp':>8s}{'PL_gia':>14s}{'CoTuc':>12s}{'%cu':>8s}{'%moi':>8s}{'Dpp':>7s}")
zc=zpl=zdiv=0
for t,(q,cb) in sorted(ZLP_BROKER_31.items()):
    d=d_of("ZaloPay",t); craw=cb+d; p=P31[t]
    plp=q*(p-craw); div=q*d; zc+=q*craw; zpl+=plp; zdiv+=div
    o=plp/(q*craw)*100; n=(plp+div)/(q*craw)*100
    print(f"{t:5s}{q:6d}{craw:11,.1f}{p:10,.0f}{d:8,d}{plp:14,.0f}{div:12,.0f}{o:8.1f}{n:8.1f}{n-o:7.2f}{'  <<<' if d else ''}")
print("-"*104)
print(f"TONG gia von tho = {zc:,.0f}   (bao cao cong bo 454.848.300 -> lech {zc-454848300:+,.0f})")
print(f"PL gia    = {zpl:,.0f} ({zpl/zc*100:+.2f}%)  [bao cao: -13.890.200 / -3,05%]")
print(f"Co tuc    = {zdiv:,.0f}   [broker cashDividendReceiving 31/07 = 6.453.500]")
print(f"TONG mới  = {zpl+zdiv:,.0f} ({(zpl+zdiv)/zc*100:+.2f}%)")

# ---------------- period-end 24/07 (weekly report 20-24/07) ----------------
print()
print("="*104)
print("D. KY 20-24/07 — sua so TONG HOP (bao cao goc tron gia DIEU CHINH voi gia von THO)")
print("="*104)
# SpaceX: published table total (raw prices) = 863.930.000 ; published cost 950.720.443
spx_cost_24, spx_mv_raw_24, spx_mv_adj_24 = 950720443, 863930000, 856641000
spx_div_24 = 2400*1000 + 1900*450 + 2300*450 + 1300*450     # MBB paid + BID + CTG + VCB receivable
print("SpaceX:")
print(f"  BAO CAO GOC : von {spx_cost_24:,} -> thi gia {spx_mv_adj_24:,} (gia DIEU CHINH) = {spx_mv_adj_24-spx_cost_24:,} ({(spx_mv_adj_24-spx_cost_24)/spx_cost_24*100:.2f}%)  << SAI (tron 2 he quy chieu)")
print(f"  SUA B1 gia tho: von {spx_cost_24:,} -> thi gia {spx_mv_raw_24:,} = {spx_mv_raw_24-spx_cost_24:,} ({(spx_mv_raw_24-spx_cost_24)/spx_cost_24*100:.2f}%)")
print(f"  SUA B2 +co tuc da tach duoc ({spx_div_24:,}: MBB+BID+CTG+VCB) = {spx_mv_raw_24-spx_cost_24+spx_div_24:,} ({(spx_mv_raw_24-spx_cost_24+spx_div_24)/spx_cost_24*100:.2f}%)")
print(f"  (NCT 4.000.000 + SAB 3.300.000 CHUA tach duoc tai 24/07 — gia 24/07 van CO quyen)")
zlp_cost_24, zlp_mv_raw_24, zlp_mv_adj_24 = 435098300, 822474300-368500000-47405000, 401360740
zlp_div_24 = 900*450 + 1050*450 + 800*450
print("ZaloPay (13 ma bot mua):")
print(f"  BAO CAO GOC : von {zlp_cost_24:,} -> thi gia {zlp_mv_adj_24:,} (gia DIEU CHINH) = {zlp_mv_adj_24-zlp_cost_24:,} ({(zlp_mv_adj_24-zlp_cost_24)/zlp_cost_24*100:.2f}%)  << SAI")
print(f"  SUA B1 gia tho: von {zlp_cost_24:,} -> thi gia {zlp_mv_raw_24:,} = {zlp_mv_raw_24-zlp_cost_24:,} ({(zlp_mv_raw_24-zlp_cost_24)/zlp_cost_24*100:.2f}%)")
print(f"  SUA B2 +co tuc ({zlp_div_24:,}: BID+CTG+VCB) = {zlp_mv_raw_24-zlp_cost_24+zlp_div_24:,} ({(zlp_mv_raw_24-zlp_cost_24+zlp_div_24)/zlp_cost_24*100:.2f}%)")

# ---------------- NAV double-count on last-cum days ----------------
print()
print("="*104)
print("E. LOI THU HAI (doc lap) — NAV chuoi ngay DEM 2 LAN co tuc dung ngay CHOT QUYEN")
print("="*104)
print("Co che: DNSE ghi cashDividendReceiving vao ~19:00 ngay CUOI CUNG con huong quyen (T-1 cua ex-date),")
print("nhung mtm_stock cua ngay do van dung gia DONG CUA CO QUYEN. daily_nav_snapshot.py lay cash=totalCash")
print("(= availableCash + cashDividendReceiving + depositInterest) => cong 2 lan, tu triet tieu phien sau.")
print()
NAV = {"SpaceX":{"2026-07-16":(957558637,855000),"2026-07-24":(910995894,4000000),
                 "2026-07-27":(900428641,3300000)},
       "ZaloPay":{"2026-07-16":(953593885,405000),"2026-07-24":(849855112,2984000)}}
for acc,rows in NAV.items():
    for d,(nav,dbl) in sorted(rows.items()):
        print(f"  {acc:8s} {d}: NAV ghi {nav:,}  - dem trung {dbl:,}  = {nav-dbl:,}  ({-dbl/nav*100:+.2f}%)")
print()
print("Anh huong len % TUAN da cong bo:")
def wk(name,s,e,s_adj,e_adj,rep):
    o=(e-s)/s*100; n=((e+e_adj)-(s+s_adj))/(s+s_adj)*100
    print(f"  {name}: bao cao {rep:+.2f}%  ->  sau khu dem-trung {n:+.2f}%  (lech {n-o:+.2f}pp)")
wk("SpaceX  tuan 20-24/07", 951448674, 910995894, 0, -4000000, -4.25)
wk("ZaloPay tuan 20-24/07", 949864227, 849855112, 0, -2984000, -10.53)
wk("SpaceX  tuan 27-31/07", 910995894, 938435711, -4000000, 0, 3.01)
wk("ZaloPay tuan 27-31/07", 849855112, 888828498, -2984000, 0, 4.59)
wk("SpaceX  thang 07 (01->31/07)", 1000000000, 938435711, 0, 0, -6.16)
