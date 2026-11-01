# TV2 DD v3 (01/11/2026) — dinh gia sau dinh chinh cua nguoi phan bien (CAO-1/CAO-2/TB-6).
# Ban v2 giu nguyen o calc/valuation_v2.py -> valuation_v2_out.txt.
# Chay: /home/trido/thanhdt/wc_venv/bin/python -I calc/valuation.py > calc/valuation_out.txt
# Nguon ghi canh tung so; gia tri tu dat = (uoc luong).
N = 67.526165            # tr cp [Q3 tr.8; BCTC rieng TM20.1 von 675,26 ty]
PX = 27000               # dong cua 30/10/2026 [DNSE ohlc/latest_trade 14:45:07, calc/dnse_raw.json]
BVPS = 19708             # VCSH me/cp 30/09 [DD 28/10 out.txt]
mcap = PX * N / 1000
print(f"Von hoa @27.000: {mcap:,.0f} ty; P/B {PX/BVPS:.2f}")

hist = {2017: 214.5, 2018: 224.1, 2019: 256.3, 2020: 262.2, 2021: 271.8, 2022: 76.6, 2023: 53.0, 2024: 64.7, 2025: 94.6}
print("EPS lich su tren so cp HIEN TAI (dong):", {y: round(v / N * 1000) for y, v in hist.items()})
for q4 in (55, 80):
    e = 162.2 + q4
    print(f"2026E Q4={q4}: LNST {e:.0f} ty, EPS {e/N*1000:,.0f}, P/E @27.000 {mcap/e:.1f}")
for pe in (7, 7.45, 8, 9, 10):
    print(f"Gia 27.000 o P/E {pe}x => LNST ben vung ngam dinh {mcap/pe:,.0f} ty")

# --- Neo P/E THEO PHA (calc/pe_by_phase.py -> pe_by_phase_out.txt; BQ ticker thang, pe>0)
print("Neo P/E TV2: pha LN DINH 2017-21 trung vi 7,45 (IQR 6,13-8,92, n=60); 2019-21 7,95; "
      "pha LN DAY 2022-25 trung vi 33,4 (KHONG DUNG: P/E tren LN day); 2014+ gop 8,75; 2019+ gop 10,99 (lan pha)")

# --- P/E hop ly tu Ke (khung domestic_v2: Ke 12,5-13,5%) — chi la phep thu, gia dinh ROE+g vinh vien
def pe_just(roe, payout, ke):
    g = (1 - payout) * roe
    return payout * (1 + g) / (ke - g), g
for roe in (0.11, 0.127):
    for ke in (0.125, 0.130, 0.135):
        p, g = pe_just(roe, 0.40, ke)
        print(f"  ROE {roe:.1%} payout 40% Ke {ke:.1%}: g {g:.1%} -> P/E hop ly {p:.1f}x")
print("  (luu y: gia dinh g vinh vien khong hop base rate LN sap ~70% khi het HD EPC 2022)")

def val(np_, pe, oneoff=0):
    return (np_ * pe + oneoff) / N * 1000

def run(sc, label, show=True):
    ev = 0
    for k, s in sc.items():
        mid = s.get("mid_override") or val(sum(s["np"]) / 2, sum(s["pe"]) / 2, s["oneoff"])
        ev += s["p"] * mid
        if show:
            lo = val(s["np"][0], s["pe"][0], s["oneoff"]); hi = val(s["np"][1], s["pe"][1], s["oneoff"])
            print(f"  {k:9s} p={s['p']:.2f} LNST {s['np']} P/E {s['pe']} -> {lo:,.0f} .. {hi:,.0f} (tam {mid:,.0f})")
    print(f"  [{label}] gia tri ky vong {ev:,.0f}; gia 27.000 = {PX/ev-1:+.1%} so voi ky vong")
    return ev

# --- 3 kich ban v3 (LNST binh quan 2027-28, ty, uoc luong). P/E neo pha LN DINH 7-9x (quanh trung vi 7,45 / 7,95)
SC = {
    "Tieu cuc": dict(p=0.25, np=(100, 120), pe=(7.0, 8.0), oneoff=-80),
    "Co so":    dict(p=0.50, np=(165, 190), pe=(7.0, 9.0), oneoff=0),
    "Tich cuc": dict(p=0.25, np=(230, 270), pe=(7.0, 9.0), oneoff=0),
}
print("KICH BAN v3:")
EV = run(SC, "v3 25/50/25")

b = SC["Co so"]
print("CACH DUNG VUNG CO SO (khai ro):")
print(f"  Goc-toi-goc (LN thap x P/E thap .. LN cao x P/E cao): {val(165,7):,.0f} .. {val(190,9):,.0f}")
print(f"  Mot chieu P/E 7-9 tai LN tam 177,5: {val(177.5,7):,.0f} .. {val(177.5,9):,.0f}")
print(f"  Mot chieu LN 165-190 tai P/E 8: {val(165,8):,.0f} .. {val(190,8):,.0f}")
print(f"  Tam co so {val(177.5,8):,.0f}; gia 27.000 = {PX/val(177.5,8)-1:+.1%} so tam, {PX/val(190,9)-1:+.1%} so dinh vung goc-toi-goc")
print(f"  Gia 27.000 chi nam trong vung co so neu LN>={mcap/9:,.0f} ty o P/E 9 (tren dinh LN co so 190)")

print("DO NHAY TRONG SO (P/E v3):")
for w in ((0.30, 0.50, 0.20), (0.25, 0.50, 0.25), (0.20, 0.50, 0.30)):
    sc = {k: dict(v, p=p) for (k, v), p in zip(SC.items(), w)}
    run(sc, f"{int(w[0]*100)}/{int(w[1]*100)}/{int(w[2]*100)}", show=False)

print("DO NHAY P/E (co so + tich cuc dung cung dai; tieu cuc giu 7-8):")
for pe in ((6.5, 8.5), (7.0, 9.0), (7.5, 10.0), (9.0, 11.0)):
    sc = {k: (dict(v, pe=pe) if k != "Tieu cuc" else v) for k, v in SC.items()}
    tag = {(7.5, 10.0): " (= dai v2, can can cu khac ngoai lich su pha dinh)", (9.0, 11.0): " (trung vi 2019+ 11,0 lan pha — tham khao)"}.get(pe, "")
    run(sc, f"P/E {pe}{tag}", show=False)

# Phia tich cuc can bang: kich ban tieu cuc o P/E 7-8 => P/B ~0,56, thap hon MOI thang tu 2014 (min P/B TV2 0,92; tu 2017 min 1,04)
bv_neg = BVPS - 80 / N * 1000
neg_mid = SC["Tieu cuc"]
print(f"Tieu cuc tam {val(110,7.5,-80):,.0f} = P/B {val(110,7.5,-80)/BVPS:.2f}; TV2 P/B min 2014+ 0,92, min 2017+ 1,04; comp P/B hien tai TV3 0,76 / TV4 1,00 / TV1 1,04 [BQ]")
for pb in ((0.8, 1.0),):
    m = bv_neg * sum(pb) / 2
    sc = {k: (dict(v, mid_override=m) if k == "Tieu cuc" else v) for k, v in SC.items()}
    print(f"  Neu tieu cuc dinh theo P/B {pb} tren BVPS sau trich lap {bv_neg:,.0f}: {bv_neg*pb[0]:,.0f} .. {bv_neg*pb[1]:,.0f} (tam {m:,.0f})")
    run(sc, "tieu cuc theo P/B san", show=False)

# Gia hien tai can gi: giu P(tieu cuc)=25%, tim P(tich cuc) de ky vong = 27.000
m = {k: val(sum(v["np"]) / 2, sum(v["pe"]) / 2, v["oneoff"]) for k, v in SC.items()}
p_need = (PX - 0.25 * m["Tieu cuc"] - 0.75 * m["Co so"]) / (m["Tich cuc"] - m["Co so"])
ev_max = 0.25 * m["Tieu cuc"] + 0.75 * m["Tich cuc"]
print(f"De ky vong = 27.000 (giu P tieu cuc 25%, P/E 7-9): P(tich cuc) can {p_need:.0%} > 75% kha dung => KHONG dat; tran ky vong (75% tich cuc) = {ev_max:,.0f}")
p_need2 = (PX - m["Co so"]) / (m["Tich cuc"] - m["Co so"])
print(f"  Neu bo han tieu cuc (0%): P(tich cuc) can {p_need2:.0%}")
print(f"Tich cuc o P/E 10x tai LN 250: {val(250,10):,.0f}")

print("Do nhay gia tri/cp (nghin dong): hang = LNST ben vung, cot = P/E 6,7,7.45,8,9,10")
pes = (6, 7, 7.45, 8, 9, 10)
for npat in (100, 130, 160, 178, 190, 220, 250):
    print(f"  {npat:3d}: " + "  ".join(f"{npat*pe/N:5.1f}" for pe in pes))

cmc = 666.374 + 188.6
print(f"Phoi nhiem CMC {cmc:.1f} ty = {cmc/(BVPS*N/1000):.0%} VCSH me")
for loss in (0.15, 0.30, 0.50):
    hit = loss * cmc * 0.8
    print(f"  Ton that {loss:.0%} sau thue 20% (uoc luong): {hit:.0f} ty = {hit/N*1000:,.0f} d/cp")

# CFO 9T (TB-1): gop -573 (tru toan bo tang tien ung) .. rong -225 (tru tang float rong)
cfo = 858.6; adv_inc = 2418.6 - 986.2
float_end = 2418.6 - 293.0 - 119.5
print(f"CFO 9T {cfo}; tru tang tien ung {adv_inc:.1f} => {cfo-adv_inc:,.1f} (gop); tru tang float rong +1.083,4 (nguoi phan bien tinh) => {cfo-1083.4:,.1f} (rong); float rong cuoi ky {float_end:.1f}")
