"""Tinh lai Muc 3.2 / 4.2 / 5.3 bao cao tuan 03-07/08 sau khi cong co tuc RONG."""
DIV = {  # ticker -> (gross, ex_date)
    "MBB": (1000.0, "2026-07-09"), "BID": (450.0, "2026-07-17"),
    "CTG": (450.0, "2026-07-23"), "VCB": (450.0, "2026-07-23"),
    "NCT": (8000.0, "2026-07-27"), "SAB": (3000.0, "2026-07-28"),
}
TAX = 0.05
net = lambda t: DIV[t][0] * (1 - TAX) if t in DIV else 0.0

# ---- SpaceX 4.2 : (qty, cost_bao_cao, cost_dung, price_0708) ----
SPX = [
 ("SIP",1700,47058.8235,47058.8235,50900),("VHM",1000,74900,74900,73000),
 ("PVT",3500,17100,17100,18350),("VNM",900,58600,58600,62000),
 ("BID",1400,42991.3043,42991.3043,39050),("VCB",900,62300,62300,59700),
 ("SAB",1100,47368.1818,47368.1818,44750),("CTG",1500,34476.7857,34476.7857,32500),
 ("TCB",1400,33900,33900,29700),("NCT",500,94360,94360,82600),
 ("VPB",1500,27914.2857,27914.2857,25000),("MBB",1500,25850,25850,24150),
 ("LPB",500,52583.3333,51466.6667,52900),("ACB",1100,22650,22650,22400),
 ("HDB",900,26675,26675,26550),("SHB",1000,13550,13550,11700),
 ("TPB",600,16800,16800,14600),("TV1",400,19600,19600,19700),
 ("VIX",500,17000,17000,13600),("VND",300,17800,17800,16650),
]
print("=== SpaceX Muc 4.2 (cuoi ky 07/08) ===")
print(f"{'ma':5}{'KL':>6}{'gia von cu':>12}{'gia von dung':>13}{'D_net':>8}"
      f"{'P&L cu':>14}{'% cu':>8}{'P&L dung':>14}{'% dung':>8}{'delta pp':>9}")
oc=om=onp=nc=nnp=0.0
for t,q,c_old,c_new,p in SPX:
    d=net(t)
    pl_old=q*(p-c_old); pct_old=(p-c_old)/c_old*100
    pl_new=q*(p+d-c_new); pct_new=(p+d-c_new)/c_new*100
    oc+=q*c_old; om+=q*p; onp+=pl_old; nc+=q*c_new; nnp+=pl_new
    flag=" <<<" if abs(pct_new-pct_old)>0.01 else ""
    print(f"{t:5}{q:>6}{c_old:>12,.1f}{c_new:>13,.1f}{d:>8,.0f}"
          f"{pl_old:>14,.0f}{pct_old:>8.2f}{pl_new:>14,.0f}{pct_new:>8.2f}{pct_new-pct_old:>9.2f}{flag}")
print(f"{'TONG':5}{'':6}{oc:>12,.0f}{nc:>13,.0f}{'':8}{onp:>14,.0f}{onp/oc*100:>8.2f}"
      f"{nnp:>14,.0f}{nnp/nc*100:>8.2f}{nnp/nc*100-onp/oc*100:>9.2f}")
print(f"  mtm tong = {om:,.0f} | co tuc RONG cong vao (vi the dang giu) = {nnp-(om-nc):,.0f}")

# ---- SpaceX 3.2 : realized 13 lenh ban 07/08 ----
SELL=[("CTG",800,34476.7857,34476.7857,32600),("VCB",400,62300,62300,60500),
 ("MBB",900,25850,25850,24250),("LPB",400,52583.3333,51466.6667,52200),
 ("VPB",800,27914.2857,27914.2857,24850),("BID",500,42991.3043,42991.3043,39150),
 ("TCB",600,33900,33900,29200),("HDB",600,26675,26675,26600),
 ("ACB",400,22650,22650,22250),("SHB",500,13550,13550,11650),
 ("SHS",200,18900,18900,15700),("TPB",200,16800,16800,14500),
 ("VIX",200,17000,17000,13750)]
print("\n=== SpaceX Muc 3.2 (lai/lo THUC HIEN 13 lenh ban 07/08) ===")
o=n=0.0
for t,q,c_old,c_new,p in SELL:
    d=net(t); a=q*(p-c_old); b=q*(p+d-c_new); o+=a; n+=b
    flag=" <<<" if abs(b-a)>1 else ""
    print(f"{t:5}{q:>6}{c_old:>12,.1f}{c_new:>13,.1f}{d:>8,.0f}{a:>14,.0f}"
          f"{(p-c_old)/c_old*100:>8.2f}{b:>14,.0f}{(p+d-c_new)/c_new*100:>8.2f}{flag}")
print(f"TONG cu={o:,.0f}  dung={n:,.0f}  (chenh {n-o:,.0f})")
print(f"  rong sau phi 142.076 + thue 189.435: cu={o-142076-189435:,.0f}  dung={n-142076-189435:,.0f}")

# ---- ZaloPay 5.3 ----
ZLP=[("SIP",749,47140.0534,47140.0534,50900),("PVT",2071,17248.3100,17248.3100,18350),
 ("CSV",1000,19750,19750,22000),("VNM",601,58699.8336,58699.8336,62000),
 ("HDB",659,25891.0470,25891.0470,26550),("CTG",1050,32583.3333,32133.3333,32500),
 ("MBB",1102,24597.9128,24597.9128,24150),("LPB",352,54843.1818,54843.1818,52900),
 ("VHM",600,74316.6667,74316.6667,73000),("VCB",800,61362.5,60912.5,59700),
 ("BID",900,40766.6667,40316.6667,39050),("TCB",956,31610.8787,31610.8787,29700),
 ("SAB",744,47450.2016,44450.2016,44750),("NCT",373,94400,86400,82600)]
print("\n=== ZaloPay Muc 5.3 (14 ma bot) ===")
oc=om=onp=nc=nnp=0.0
for t,q,c_old,c_new,p in ZLP:
    d=net(t) if t!="MBB" else 0.0   # ZaloPay KHONG duoc huong co tuc MBB (xem doi soat receivable)
    a=q*(p-c_old); b=q*(p+d-c_new); oc+=q*c_old; om+=q*p; onp+=a; nc+=q*c_new; nnp+=b
    flag=" <<<" if abs(b-a)>1 else ""
    print(f"{t:5}{q:>6}{c_old:>12,.1f}{c_new:>13,.1f}{d:>8,.0f}{a:>14,.0f}"
          f"{(p-c_old)/c_old*100:>8.2f}{b:>14,.0f}{(p+d-c_new)/c_new*100:>8.2f}{flag}")
print(f"TONG cost cu={oc:,.0f} dung={nc:,.0f} mtm={om:,.0f}")
print(f"  P&L cu={onp:,.0f} ({onp/oc*100:.2f}%)   dung={nnp:,.0f} ({nnp/nc*100:.2f}%)")
