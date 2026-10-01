import json
A = json.load(open("attribution.json")); P = json.load(open("positions_20260930.json"))
SEC = {"Ngân hàng": "ACB BID CTG HDB LPB MBB MSB SHB TCB TPB VCB VIB VPB",
       "Chứng khoán & tài chính": "VIX VND EVF",
       "Bất động sản & KCN": "VHM VRE VPI SIP",
       "Hoá chất, vật liệu & công nghiệp": "DGC CSV HPG SCL",
       "Tiêu dùng & nông nghiệp": "VNM SAB DRI",
       "Vận tải, logistics & năng lượng": "PVT NCT TV1"}
s2 = {t: s for s, ts in SEC.items() for t in ts.split()}
DIV = {"SpaceX": {"DRI": 3700*1000*0.95}, "ZaloPay": {"DGC": 10000*8000*0.95, "DRI": 1900*1000*0.95}}
DIVG = {"SpaceX": {"DRI": 3700*1000}, "ZaloPay": {"DGC": 80_000_000, "DRI": 1_900_000}}
FEE = 0.00097; TAX = 0.001
NAVCH = {"SpaceX": 981599301-985617905, "ZaloPay": 958666279-952365940}
NAV1 = {"SpaceX": 981599301, "ZaloPay": 958666279}
for acc in ["SpaceX", "ZaloPay"]:
    rows = A[acc]["rows"]
    for r in rows: r["div"] = DIV[acc].get(r["tk"], 0); r["tot"] = r["pl_price"] + r["div"]
    agg = {}
    for r in rows:
        g = agg.setdefault(s2[r["tk"]], dict(tot=0, mv1=0, mv0=0, tks=[])); g["tot"] += r["tot"]; g["mv1"] += r["mv1"]; g["mv0"] += r["mv0"]; g["tks"].append(r["tk"])
    fees = (A[acc]["buy"] + A[acc]["sell"]) * FEE; tax = A[acc]["sell"] * TAX
    divg = sum(DIVG[acc].values()); divtax = divg*0.05
    other = NAVCH[acc] - A[acc]["pl_price"] - divg + divtax + fees + tax
    print(f"== {acc} navch {NAVCH[acc]:,} price {A[acc]['pl_price']:,.0f} divgross {divg:,.0f} divtax {-divtax:,.0f} fees {-fees:,.0f} tax {-tax:,.0f} other(interest) {other:,.0f}  buy {A[acc]['buy']:,.0f} sell {A[acc]['sell']:,.0f}")
    for s, g in sorted(agg.items(), key=lambda x: -x[1]["tot"]):
        print(f"   {s}: {g['tot']:,.0f}  mv0 {g['mv0']/ (NAVCH[acc]*0+ (NAV1[acc]-NAVCH[acc]))*100:.1f}%NAV0 mv1 {g['mv1']/NAV1[acc]*100:.1f}%NAV1  {' '.join(sorted(g['tks']))}")
    srt = sorted(rows, key=lambda r: -r["tot"])
    print("  top:", [(r["tk"], round(r["tot"]), round((r["p1"]/r["p0"]-1)*100,2)) for r in srt[:6]])
    print("  bot:", [(r["tk"], round(r["tot"]), round((r["p1"]/r["p0"]-1)*100,2)) for r in srt[-6:]])
    pr = P[acc]["rows"]
    inc = [r for r in pr if r["sym"] not in ("DRI","DGC")]
    print("  unreal (gate, excl DRI/DGC):", round(sum(r["pl"] for r in inc)), "on raw", round(sum(r["qty"]*r["raw_cost"] for r in inc)), round(sum(r["pl"] for r in inc)/sum(r["qty"]*r["raw_cost"] for r in inc)*100,2))
