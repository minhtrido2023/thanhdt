# TV2 DD v2 (01/11/2026) — dinh gia trung lap. Nguon ghi canh tung so; gia tri tu dat = (uoc luong).
# Chay: /home/trido/thanhdt/wc_venv/bin/python -I valuation.py > valuation_out.txt
N = 67.526165            # tr cp [Q3 tr.8; BCTC rieng TM20.1 von 675,26 ty]
PX = 27000               # dong cua 30/10/2026 [DNSE ohlc/latest_trade 14:45:07, calc/dnse_raw.json]
PX_PREV = 26050          # dong cua 27/10 (moc DD 28/10) [DNSE ohlc]
EQ_PARENT = 19708 * N / 1000   # VCSH me 30/09 [DD 28/10 out.txt BVPS 19.708]
mcap = PX * N / 1000
print(f"Von hoa @27.000: {mcap:,.0f} ty; VCSH me {EQ_PARENT:,.0f} ty; P/B {PX/19708:.2f}")

# --- Lich su (BQ ticker_financial, tong 4 quy; calc/hist_out.txt)
hist = {2017: 214.5, 2018: 224.1, 2019: 256.3, 2020: 262.2, 2021: 271.8, 2022: 76.6, 2023: 53.0, 2024: 64.7, 2025: 94.6}
print("EPS lich su tren so cp HIEN TAI (dong):", {y: round(v / N * 1000) for y, v in hist.items()})

# --- 2026E (uoc luong): 9T me 162,2 [BQ = BCTC]; Q4 55-80 (Q4/25 48,8; mua vu Q4; QL noi DT EPC don Q3-Q4 [BB DHDCD 2026 y kien 1])
for q4 in (55, 80):
    e = 162.2 + q4
    print(f"2026E Q4={q4}: LNST {e:.0f} ty, EPS {e/N*1000:,.0f}, P/E @27.000 {mcap/e:.1f}")

# --- Dinh gia nguoc
for pe in (7, 8, 9, 10, 11):
    print(f"Gia 27.000 o P/E {pe}x => LNST ben vung ngam dinh {mcap/pe:,.0f} ty")

# --- P/E hop ly tu Ke (khung skill due-diligence: Ke noi dia beta1,1 12,3-13,4%; dai 10,5-14,0)
def pe_just(roe, payout, ke):
    g = (1 - payout) * roe
    return payout * (1 + g) / (ke - g), g
for roe in (0.11, 0.127, 0.15):
    for ke in (0.123, 0.1285, 0.134):
        p, g = pe_just(roe, 0.40, ke)
        print(f"  ROE {roe:.1%} payout 40% Ke {ke:.2%}: g {g:.1%} -> P/E hop ly {p:.1f}x, P/B {p*roe:.2f}x")

# --- 3 kich ban (LNST binh quan 2027-28, ty, uoc luong) x P/E
#  Tieu cuc: EPC bien mong/vuot chi phi, lai float giam nhanh, CMC trich lap ~100 ty truoc thue (~80 sau thue) 1 lan
#  Co so  : 4 HD EPC chay dung tien do 2026-28 [BB DHDCD], tu van+O&M on dinh, TC rong giam con 50-70, LK 30
#  Tich cuc: lap lai chu ky EPC 2019-21 (LNST 256-272 [BQ]) nho HD moi (khi/LNG BOP, Philippines, hat nhan), CMC thu du
sc = {
    "Tieu cuc": dict(p=0.25, np=(100, 120), pe=(7.0, 8.0), oneoff=-80),
    "Co so":    dict(p=0.50, np=(165, 190), pe=(7.5, 10.0), oneoff=0),
    "Tich cuc": dict(p=0.25, np=(230, 270), pe=(8.0, 10.0), oneoff=0),
}
ev_lo = ev_mid = ev_hi = 0
for k, s in sc.items():
    lo = (s["np"][0] * s["pe"][0] + s["oneoff"]) / N * 1000
    hi = (s["np"][1] * s["pe"][1] + s["oneoff"]) / N * 1000
    mid = ((sum(s["np"]) / 2) * (sum(s["pe"]) / 2) + s["oneoff"]) / N * 1000
    ev_lo += s["p"] * lo; ev_hi += s["p"] * hi; ev_mid += s["p"] * mid
    print(f"{k:9s} p={s['p']:.2f} LNST {s['np']} P/E {s['pe']} -> {lo:,.0f} .. {hi:,.0f} (tam {mid:,.0f})")
print(f"Gia tri ky vong co trong so: {ev_lo:,.0f} .. {ev_hi:,.0f}, tam {ev_mid:,.0f}; gia 27.000 = {PX/ev_mid-1:+.1%} vs tam; 26.050 = {PX_PREV/ev_mid-1:+.1%}")

# Vung gia tri hop ly = dai kich ban co so (tam 50%)
b = sc["Co so"]
fv_lo = b["np"][0] * b["pe"][0] / N * 1000; fv_hi = b["np"][1] * b["pe"][1] / N * 1000
print(f"Vung gia tri hop ly (co so): {fv_lo:,.0f} .. {fv_hi:,.0f}; gia 27.000 o {(PX-fv_lo)/(fv_hi-fv_lo):.0%} chieu rong vung")

# Tham chieu boi so
print("Tham chieu (BQ ticker, thang, PE>0): TV2 PE trung vi 2014+ 8,7 / 2019+ 11,0; PB trung vi 1,81/1,77; PECC1/3/4 PE trung vi 2014+ 8,6/9,5/8,9")
print("Comp hien tai (BQ 29-30/10): TV1 PE 3,6 PB 1,04; TV3 PE 7,2 PB 0,76; TV4 PE 5,5 PB 1,00; TV2 PE 8,6 PB 1,37")
for pe in (3.6, 5.5, 7.2):
    print(f"  Neu ap P/E comp {pe}x len LNST co so 178: {178*pe/N*1000:,.0f} d/cp")

# Do nhay: LNST x P/E
print("Do nhay gia tri/cp (nghin dong): hang = LNST ben vung, cot = P/E 6..11")
for npat in (100, 130, 160, 190, 220, 250):
    print(f"  {npat:3d}: " + "  ".join(f"{npat*pe/N:5.1f}" for pe in (6, 7, 8, 9, 10, 11)))

# Phoi nhiem CMC
cmc_ar = (657.327, 666.374); cmc_inv = 188.6
for ar in cmc_ar:
    print(f"Phoi nhiem CMC (phai thu {ar} + dau tu {cmc_inv}) = {ar+cmc_inv:.1f} ty = {(ar+cmc_inv)/EQ_PARENT:.0%} VCSH me = {(ar+cmc_inv)/N*1000:,.0f} d/cp")
for loss in (0.15, 0.30, 0.50):
    hit = loss * (666.374 + cmc_inv) * 0.8
    print(f"  Ton that {loss:.0%} phoi nhiem, sau thue 20% (uoc luong): {hit:.0f} ty = {hit/N*1000:,.0f} d/cp")

# Lai float
print(f"Lai tien gui 9T 86,5 (me) / 87,1 (HN); co tuc nhan 9T me 13,3 [RIENG TM23]; TC rong me ~ {107.93+2.88:.1f}")
print(f"Co tuc 1.000 d/cp: ty suat {1000/PX:.1%} @27.000; tong 67,53 ty = {67.526/94.6:.0%} LNST HN 2025")
print(f"ADV20 DNSE 5,66 ty/ngay (213k cp); TV1 0,82; TV3 0,04; TV4 0,05")
