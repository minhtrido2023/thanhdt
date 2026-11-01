"""HHS DD v2 (01/11/2026) — định giá theo CÙNG cơ sở thặng dư/PV của DD TCH v2 (C1 phản biện).
Chạy: /home/trido/thanhdt/wc_venv/bin/python -I valuation_v2.py > valuation_v2_out.txt
Mọi tham số NAV là ƯỚC LƯỢNG. Đơn vị: tỷ đồng, đ/cp.
"""
import json, datetime as dt
SH = 431.985968; PX = 9450; KE = 0.1285
pv = lambda y, ke=KE: 1 / (1 + ke) ** y
HHS = 0.5115
# BCTC [Q3HN] 30/09/2026
EQ_ME = 9152.94; NCI = 7726.98
CRV_FV = NCI / (1 - HHS)                     # CRV cơ sở GTHL (PPA) ngầm định từ NCI
STEP_AT = 2020.76 / 0.20 * 0.8               # thặng dư PPA còn lại sau thuế (HTK+BĐSĐT)
CRV_COST = CRV_FV - STEP_AT                  # CRV cơ sở giá gốc
OTHER = EQ_ME - HHS * CRV_FV - (694.84 - 310.74)   # tiền mẹ, Pruksa, Hoàng Giang...
print(f"CRV GTHL {CRV_FV:.0f} - thang du PPA sau thue {STEP_AT:.0f} = CRV gia goc {CRV_COST:.0f}; phan khac {OTHER:.0f}")
# Tham số DD TCH v2 (tch_valuation_v2.py): NMTT NC-II 3.099,2; VAT 1,08; HTK CRV còn lại 7.338,8; PV 0,886/0,617
NMTT = 3099.20; VAT = 1.08; REST_CRV = 7338.8
print(f"PV 1 nam {pv(1):.3f}, 4 nam {pv(4):.3f} (Ke {KE:.2%})")
def crv_tch(m, s, ke=KE):
    return CRV_COST + NMTT / VAT * m * pv(1, ke) + REST_CRV * s * pv(4, ke)
SC = {"Tieu cuc": dict(p=0.30, m=0.30, s=0.15, np=25, pe=5, hd=0.35, g=0.15, h=0.60),
      "Co so":    dict(p=0.50, m=0.335, s=0.40, np=35, pe=6, hd=0.25, g=0.10, h=0.40),
      "Tich cuc": dict(p=0.20, m=0.36, s=0.55, np=50, pe=8, hd=0.15, g=0.05, h=0.25)}
def val(c, s):
    return ((HHS * c) * (1 - s["hd"]) + OTHER + s["np"] * s["pe"]) * (1 - s["g"]) / SH * 1000
rt, rp = {}, {}
print("\n== Co so TCH (CHINH) ==")
for k, s in SC.items():
    c = crv_tch(s["m"], s["s"]); rt[k] = val(c, s)
    print(f"{k}: CRV100% {c:,.0f} (backlog m {s['m']:.1%}, thang du {s['s']:.0%}); o to {s['np']}x{s['pe']}={s['np']*s['pe']}; CK {s['hd']:.0%}/{s['g']:.0%} -> {rt[k]:,.0f} d/cp")
wt = sum(SC[k]["p"] * rt[k] for k in SC); print(f"Trong so 30/50/20: {wt:,.0f}; gia {PX} lech {PX/wt-1:+.1%}")
print("\n== Co so PPA cua HHS (THAM CHIEU; haircut thang du PPA 60/40/25%, o to da sua) ==")
for k, s in SC.items():
    c = CRV_FV - s["h"] * STEP_AT; rp[k] = val(c, s)
    print(f"{k}: CRV100% {c:,.0f} -> {rp[k]:,.0f} d/cp")
wp = sum(SC[k]["p"] * rp[k] for k in SC); print(f"Trong so: {wp:,.0f}; gia lech {PX/wp-1:+.1%}")
print("Bien thang du PPA ngam dinh (CRV100% PPA haircut 40% vs TCH co so):", f"{CRV_FV-0.4*STEP_AT:,.0f} vs {crv_tch(0.335,0.40):,.0f}")
# BĐSĐT: HHS HN 2.459,74 vs TCH HN 1.438,45 (cung 30/09/2026; TCH hop nhat HHS theo gia goc)
bds = (2459.74 - 1438.45) * 0.8 * HHS
print(f"\nThang du BDSDT (cận dưới, uoc luong): ({2459.74}-{1438.45}) x0,8 x51,15% = {bds:.0f} ty; sau CK co so 25%/10% = +{bds*0.75*0.9/SH*1000:,.0f} d/cp (KHONG dua vao tam)")
print("Loi suat cho thue toi thieu <=1 nam 57,20 / BDSDT 2.459,74 =", f"{57.20/2459.74:.1%}")
print("\nMa tran co so (CK 25%/10%, o to 210): thang du (dong) x bien rong backlog 33,5%")
for s_ in (0.10, 0.25, 0.40, 0.55, 0.70):
    g_ = (s_ + 0.08) / (s_ + 0.8)
    v = val(crv_tch(0.335, s_), SC["Co so"])
    print(f"  s {s_:.0%} (bien gop ~{g_:.1%}): {v:,.0f} d/cp; gia lech {PX/v-1:+.1%}")
print("\nDo nhay co so: ")
b = SC["Co so"]
for ke in (0.123, 0.134):
    print(f"  Ke {ke:.1%}: {((HHS*crv_tch(0.335,0.40,ke))*(1-b['hd'])+OTHER+210)*(0.9)/SH*1000:,.0f}")
for hd in (0.20, 0.30):
    print(f"  CK holding {hd:.0%}: {val(crv_tch(0.335,0.40), dict(b, hd=hd)):,.0f}")
for g in (0.05, 0.15):
    print(f"  CK quan tri {g:.0%}: {val(crv_tch(0.335,0.40), dict(b, g=g)):,.0f}")
for np_, pe in ((25, 5), (50, 8)):
    print(f"  O to {np_}x{pe}: {val(crv_tch(0.335,0.40), dict(b, np=np_, pe=pe)):,.0f}")
print(f"  O to cu (40x8=320) thay 210: {val(crv_tch(0.335,0.40), dict(b, np=40, pe=8)) - val(crv_tch(0.335,0.40), b):+,.0f} d/cp")
print("\nPhep thu cheo:")
BVC = 11617
for pb, lab in ((0.98, "TCH P/B VCSH me [TCH-DD]"), (0.72, "trung vi peer BQ (chua truy nguyen)")):
    print(f"  {pb} x BV gia goc {BVC} = {pb*BVC:,.0f} ({lab})")
print(f"  51,15% x VCSH CRV rieng 31/03/26 7.579 = {HHS*7579/SH*1000:,.0f} d/cp")
d = (wt - PX) * SH * 0.5831 / 1003.31
print(f"  SOTP TCH: thay dong HHS thi truong bang tam {wt:,.0f}: +{d:,.0f} d/cp TCH (tron co so: CRV truc tiep theo so gia goc, CRV qua HHS theo NAV TCH-basis)")
print("\nC10 thu moi NC-II (uoc luong): DT BDS 9T 1.875,89 x VAT 1,08 =", f"{1875.89*1.08:,.0f}", "; NMTT NC-II giam 354 ⇒ phan con lai", f"{1875.89*1.08-354:,.0f}", "den tu tra truoc moi/phai thu")
print("C7 bien BDS ex-PPA Q3 = (272,38 + 127,74/0,2)/1.746,23 =", f"{(272.38+127.74/0.2)/1746.23:.1%}")
print("C2 Q2 sau soat xet: LNST 62,95-(81,96-31,60) =", f"{62.95-(81.96-31.60):.2f}", "; me 43,32-(65,51-25,34) =", f"{43.32-(65.51-25.34):.2f}")
c = json.load(open('dnse_ohlc_CRV.json')); cl = c['c']; vv = c['v']; t = c['t']
dd = [dt.datetime.utcfromtimestamp(x + 7*3600).date() for x in t]
n = sum(1 for i in range(len(dd)) if dd[i] >= dt.date(2026, 8, 3) and vv[i] > 0)
print(f"CRV DNSE: dong cua cuoi {cl[-1]*1000:,.0f} ({dd[-1]}); phien co khop tu 03/08: {n}/{sum(1 for x in dd if x>=dt.date(2026,8,3))}")
