"""DCF FCFE TTA r2 — áp đính chính fundamental-skeptic. Đơn vị: tỷ VND. Giữ nguyên dcf_tta.py (r1).
Khác r1: (1) kịch bản B' ; (2) hồi tố dùng tỷ giá lịch sử từng năm (data/macro_usdvnd.csv, TB năm — ước lượng cho tỷ giá EVN áp);
(3) hồi tố BÙ TRỪ NGAY với phải thu EPTC bị giữ (V1) hoặc trả góp 5 năm có lãi 8,4% + phải thu thu ngay t=0 (V2, cận lạc quan);
(4) Phước Hoà = sổ sách (NPV=0) trừ 5 tỷ vốn bên ngoài, độ nhạy =0; (5) bảng độ nhạy trọng số.
"""
import pandas as pd, itertools
SH = 178.559087
DEBT0 = 1554.5
FX_FWD = 25755                                  # tỷ giá cho dòng tiền TƯƠNG LAI (như r1)
FIT1_USC, FIT2_USC = 9.35, 7.09
TRAN = 1184.90
BN_GWH, NM_GWH = 98.0, 85.0
POST_FIT = 1100.0
_fx = pd.read_csv('/home/trido/thanhdt/WorkingClaude/data/macro_usdvnd.csv', parse_dates=['time']).set_index('time').usdvnd
FXY = {y: float(_fx[str(y)].mean()) for y in range(2019, 2027)}   # 2026: TB tới 29/4 (dữ liệu local dừng ở đó)
# số năm hưởng giá sai tới 31/12/2026: Bầu Ngứ COD 12/11/2019, Núi Một 1 COD 06/11/2020
BN_FR = {2019: 49/365, **{y: 1.0 for y in range(2020, 2027)}}
NM_FR = {2020: 56/366, **{y: 1.0 for y in range(2021, 2027)}}
def price_vnd(usc, y): return usc/100*FXY[y]
def retro_bn(to):   # Bầu Ngứ: FIT1 -> FIT2 (to='FIT2')
    return sum((price_vnd(FIT1_USC, y) - price_vnd(FIT2_USC, y))*BN_GWH*f/1000 for y, f in BN_FR.items())
def retro_nm_tran():  # Núi Một 1: FIT2 -> trần chuyển tiếp
    return sum((price_vnd(FIT2_USC, y) - TRAN)*NM_GWH*f/1000 for y, f in NM_FR.items())
def retro_bn_tran():
    return sum((price_vnd(FIT1_USC, y) - TRAN)*BN_GWH*f/1000 for y, f in BN_FR.items())
FIT1, FIT2 = FIT1_USC*FX_FWD/100, FIT2_USC*FX_FWD/100
def model(r=0.135, bn_px=FIT1, nm_px=FIT2, retro=0.0, hydro_shock=0.0, rate_add=0.0, hydro_post_cut=0.15,
          phuoc_hoa=90.7, ar_excess=330.0, hydro_scale=1.0, mode='V1', start=2027):
    pv, debt = 0.0, DEBT0
    sched = {2027: 280.0}; rem = DEBT0-280.0
    for y in range(2028, 2034): sched[y] = rem/6
    for i, y in enumerate(range(start, 2061)):
        t = i+0.5
        hyd = 330.0*hydro_scale*(1-(hydro_shock if y == 2027 else 0))*(1-(hydro_post_cut if y >= 2037 else 0))
        hyd_cost = 80.0*1.03**i
        deg = 0.995**(y-2026)
        bn = (BN_GWH*deg*(bn_px if y <= 2039 else POST_FIT)/1000) if y <= 2044 else 0
        nm = (NM_GWH*deg*(nm_px if y <= 2040 else POST_FIT)/1000) if y <= 2045 else 0
        sol_cost = (29.0*1.03**i) if y <= 2045 else 0
        ga = 22.0*1.03**i
        ebitda = hyd-hyd_cost+bn+nm-sol_cost-ga
        capex = 30.0+(60.0 if y == 2032 else 0)
        interest = debt*(0.084+rate_add)
        dep = 205.0 if y <= 2040 else 110.0
        pbt = ebitda-dep-interest
        tr = 0.06 if y <= 2030 else (0.10 if y <= 2034 else 0.20)
        tax = max(pbt, 0)*tr
        bcc = 0.12*max(hyd-hyd_cost, 0)
        funds = 0.06*max(pbt-tax, 0)+2.0
        princ = sched.get(y, 0.0); debt -= princ
        ret = 0.0
        if mode == 'V2' and start <= y < start+5:      # trả góp đều 5 năm + lãi 8,4% trên dư nợ hồi tố còn lại
            k = y-start; ret = retro/5 + retro*(1-k/5)*0.084
        fcfe = ebitda-capex-interest-tax-bcc-funds-princ-ret
        pv += fcfe/(1+r)**t
    if mode == 'V1': other_ar = ar_excess - retro           # bù trừ ngay t=0 (có thể âm = phải nộp thêm ngay)
    else: other_ar = ar_excess                              # V2: phải thu thu ngay, hồi tố trả góp
    eq = pv+34.9+116.0+99.4+15.0+phuoc_hoa+other_ar
    return eq, eq*1000/SH
def scen():
    rbn = retro_bn('FIT2'); rnm = retro_nm_tran(); rbt = retro_bn_tran()
    return {
      'A':  dict(),
      'B':  dict(bn_px=FIT2, retro=rbn),
      "B'": dict(bn_px=FIT2, nm_px=TRAN, retro=rbn+rnm),
      'C':  dict(bn_px=TRAN, nm_px=TRAN, retro=rbt+rnm, hydro_shock=0.15, rate_add=0.01),
    }
IMPL_PAY = {'A':1.00,'B':0.85,"B'":0.72,'C':0.55}
if __name__ == "__main__":
    print("FX TB năm:", {y: round(v) for y, v in FXY.items()})
    rbn, rnm, rbt = retro_bn('FIT2'), retro_nm_tran(), retro_bn_tran()
    print(f"hồi tố: BN→FIT2 {rbn:.0f} | NM1→trần {rnm:.0f} | BN→trần {rbt:.0f} | B' {rbn+rnm:.0f} | C {rbt+rnm:.0f}")
    S = scen(); V = {}
    for mode in ('V1', 'V2'):
        V[mode] = {k: model(mode=mode, **kw)[1] for k, kw in S.items()}
        print(mode, {k: round(v) for k, v in V[mode].items()})
    # kiểm: PH=0 (r1) V1
    print("PH=0:", {k: round(model(mode='V1', **{**kw, 'phuoc_hoa': 0})[1]) for k, kw in S.items()})
    print("ar_excess=0 V1:", {k: round(model(mode='V1', **{**kw, 'ar_excess': 0})[1]) for k, kw in S.items()})
    # tâm theo cấu trúc
    liq = 0.10
    def centre(w, vals): return sum(w[k]*vals[k] for k in w)
    W = {'r1 0,25/0,50/0,25 (A,B,C)': {'A':.25,'B':.5,'C':.25},
         "A/B'/C 0,25/0,50/0,25": {'A':.25,"B'":.5,'C':.25},
         "A/B/B'/C 0,20/0,25/0,35/0,20": {'A':.2,'B':.25,"B'":.35,'C':.2},
         "A/B/B'/C 0,15/0,25/0,40/0,20": {'A':.15,'B':.25,"B'":.4,'C':.2}}
    for mode in ('V1','V2'):
        for n, w in W.items():
            c = centre(w, V[mode]); print(mode, n, round(c), 'sau TK', round(c*(1-liq)), 'BAS(0,85)', round(c*(1-liq)*0.85))
    # độ nhạy PH & lãi r, hydro (B')
    for nm, kw in [("B' PH=0", {**S["B'"], 'phuoc_hoa': 0}), ("B' PH=95.7", {**S["B'"], 'phuoc_hoa': 95.7}),
                   ("B' hydro-20%", {**S["B'"], 'hydro_scale': .8}), ("B' hydro+20%", {**S["B'"], 'hydro_scale': 1.2}),
                   ("B' r+100bp", {**S["B'"], 'r': .145}), ("B' r-100bp", {**S["B'"], 'r': .125}), ("B' lãi+1pp", {**S["B'"], 'rate_add': .01})]:
        print(nm, round(model(mode='V1', **kw)[1]))
    # DSCR 2027 B' (r1 cách tính): EBITDA 2027 và lãi
    print("EBITDA2027 B' & A (tỷ):")
    for k in ('A','B',"B'",'C'):
        kw = S[k]; bn = BN_GWH*0.995*kw.get('bn_px', FIT1)/1000; nm = NM_GWH*0.995*kw.get('nm_px', FIT2)/1000
        hyd = 330*(1-kw.get('hydro_shock',0)) - 80 - 29 - 22 + bn + nm
        intr = DEBT0*(0.084+kw.get('rate_add',0)); print(k, round(hyd,1), 'lãi', round(intr,1), 'DSCR trước hồi tố', round((hyd-30)/(intr+280),2))
