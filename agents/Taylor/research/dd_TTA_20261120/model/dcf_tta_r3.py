"""DCF FCFE TTA r3 — áp đính chính cơ học vòng 2 lên r2. Đơn vị: tỷ VND. r1/r2 giữ nguyên.
Khác r2: (1) chiết khấu thanh khoản = nửa spread Corwin-Schultz (120 phiên) + 1,0·σ_ngày(250)·√(Q/ADV_trung vị), Q=5 tỷ
(quy ước fleet, cách làm SCL r3 compare_r3.py); 10% phẳng chỉ còn là độ nhạy. (2) tỷ lệ EPTC trả so cùng kỳ 9T/9T từ BCTC
(không còn phép tính ngược từ giả định 62%). (3) khai đường thử trọng số. (4) DSCR trừ thuế + chia LN HTKD (tiền mặt).
(5) biến thể bù trừ LAI (H): bù trừ ngay tới mức phải thu vượt, phần hồi tố còn lại trả góp 5 năm có lãi 8,4%.
(6) vùng giá cùng nền SAU thanh khoản.
Chạy: python3 -I model/dcf_tta_r3.py  (cwd = dd_TTA_20261120). Ghi model/out_r3.json.
"""
import csv, json, math, os, statistics as st
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SH = 178.559087
DEBT0 = 1554.5
FX_FWD = 25755
FIT1_USC, FIT2_USC = 9.35, 7.09
TRAN = 1184.90
BN_GWH, NM_GWH = 98.0, 85.0
POST_FIT = 1100.0
_fx = pd.read_csv('/home/trido/thanhdt/WorkingClaude/data/macro_usdvnd.csv', parse_dates=['time']).set_index('time').usdvnd
FXY = {y: float(_fx[str(y)].mean()) for y in range(2019, 2027)}
BN_FR = {2019: 49/365, **{y: 1.0 for y in range(2020, 2027)}}
NM_FR = {2020: 56/366, **{y: 1.0 for y in range(2021, 2027)}}
def price_vnd(usc, y): return usc/100*FXY[y]
def retro_bn_fit2(): return sum((price_vnd(FIT1_USC, y)-price_vnd(FIT2_USC, y))*BN_GWH*f/1000 for y, f in BN_FR.items())
def retro_nm_tran(): return sum((price_vnd(FIT2_USC, y)-TRAN)*NM_GWH*f/1000 for y, f in NM_FR.items())
def retro_bn_tran(): return sum((price_vnd(FIT1_USC, y)-TRAN)*BN_GWH*f/1000 for y, f in BN_FR.items())
FIT1, FIT2 = FIT1_USC*FX_FWD/100, FIT2_USC*FX_FWD/100
AR_EXCESS = 330.0


def year_flows(y, i, debt, bn_px, nm_px, hydro_shock, rate_add, hydro_post_cut=0.15, hydro_scale=1.0):
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
    return dict(ebitda=ebitda, capex=capex, interest=interest, tax=tax, bcc=bcc, funds=funds)


def model(r=0.135, bn_px=FIT1, nm_px=FIT2, retro=0.0, hydro_shock=0.0, rate_add=0.0, hydro_post_cut=0.15,
          phuoc_hoa=90.7, ar_excess=AR_EXCESS, hydro_scale=1.0, mode='V1', start=2027):
    """mode V1 = bù trừ ngay toàn bộ; V2 = phải thu thu ngay + hồi tố trả góp 5 năm lãi 8,4%;
    H = LAI: bù trừ ngay tới mức phải thu vượt, phần dư (retro−ar) trả góp 5 năm lãi 8,4%."""
    pv, debt = 0.0, DEBT0
    sched = {2027: 280.0}; rem = DEBT0-280.0
    for y in range(2028, 2034): sched[y] = rem/6
    if mode == 'V1': inst, other_ar = 0.0, ar_excess-retro
    elif mode == 'V2': inst, other_ar = retro, ar_excess
    else: inst, other_ar = max(retro-ar_excess, 0.0), ar_excess-min(retro, ar_excess)
    for i, y in enumerate(range(start, 2061)):
        f = year_flows(y, i, debt, bn_px, nm_px, hydro_shock, rate_add, hydro_post_cut, hydro_scale)
        princ = sched.get(y, 0.0); debt -= princ
        ret = 0.0
        if inst > 0 and start <= y < start+5:
            k = y-start; ret = inst/5 + inst*(1-k/5)*0.084
        fcfe = f['ebitda']-f['capex']-f['interest']-f['tax']-f['bcc']-f['funds']-princ-ret
        pv += fcfe/(1+r)**(i+0.5)
    eq = pv+34.9+116.0+99.4+15.0+phuoc_hoa+other_ar
    return eq, eq*1000/SH


def scen():
    rbn, rnm, rbt = retro_bn_fit2(), retro_nm_tran(), retro_bn_tran()
    return {'A': dict(), 'B': dict(bn_px=FIT2, retro=rbn), "B'": dict(bn_px=FIT2, nm_px=TRAN, retro=rbn+rnm),
            'C': dict(bn_px=TRAN, nm_px=TRAN, retro=rbt+rnm, hydro_shock=0.15, rate_add=0.01)}


def dscr_2027(kw):
    """DSCR 2027 = (EBITDA − capex − thuế − chia LN HTKD tiền mặt) / (lãi + gốc 280). Trước hồi tố."""
    f = year_flows(2027, 0, DEBT0, kw.get('bn_px', FIT1), kw.get('nm_px', FIT2), kw.get('hydro_shock', 0), kw.get('rate_add', 0))
    pre = (f['ebitda']-f['capex'])/(f['interest']+280.0)
    post = (f['ebitda']-f['capex']-f['tax']-f['bcc'])/(f['interest']+280.0)
    return round(pre, 2), round(post, 2), {k: round(v, 1) for k, v in f.items()}


def liquidity():
    rows = list(csv.DictReader(open(os.path.join(HERE, 'data', 'px_tta.csv'))))
    for x in rows:
        for k in ('Open', 'High', 'Low', 'Close', 'Price', 'Volume'): x[k] = float(x[k])
    out = dict(px_last=rows[-1]['Close'], px_date=rows[-1]['time'], n_rows=len(rows))
    w250 = rows[-250:]
    rets = [math.log(w250[i]['Close']/w250[i-1]['Close']) for i in range(1, len(w250))]
    sigma = st.pstdev(rets)
    adv250 = st.median([x['Price']*x['Volume'] for x in w250])
    adv68 = st.median([x['Price']*x['Volume'] for x in rows[-68:]])
    w120 = rows[-120:]; cs = []
    for a, b in zip(w120[:-1], w120[1:]):
        beta = math.log(a['High']/a['Low'])**2+math.log(b['High']/b['Low'])**2
        gam = math.log(max(a['High'], b['High'])/min(a['Low'], b['Low']))**2
        k = 3-2*math.sqrt(2)
        al = (math.sqrt(2*beta)-math.sqrt(beta))/k-math.sqrt(gam/k)
        cs.append(max(2*(math.exp(al)-1)/(1+math.exp(al)), 0.0))
    spread = st.mean(cs)
    out.update(sigma=sigma, adv250_med=adv250, adv68_med=adv68, spread_cs120=spread, first250=w250[0]['time'])
    for q in (1e9, 5e9, 10e9):
        for nm, adv in (('250', adv250), ('68', adv68)):
            out[f'd_{int(q/1e9)}ty_adv{nm}'] = spread/2+1.0*sigma*math.sqrt(q/adv)
            out[f'd_{int(q/1e9)}ty_adv{nm}_y05'] = spread/2+0.5*sigma*math.sqrt(q/adv)
            out[f'days20_{int(q/1e9)}ty_adv{nm}'] = q/(0.2*adv)
    return out


W_PATH = [  # đường thử trọng số (theo thứ tự đã chạy ở r2) — A/B/B'/C
    ('thử 1 (r2 dòng 83–86)', dict(A=.20, B=.25, **{"B'": .35}, C=.20)),
    ('thử 2', dict(A=.15, B=.25, **{"B'": .40}, C=.20)),
    ('CHỐT 0,15/0,25/0,35/0,25', dict(A=.15, B=.25, **{"B'": .35}, C=.25)),
]
W_SENS = [('lạc quan 0,25/0,30/0,30/0,15', dict(A=.25, B=.30, **{"B'": .30}, C=.15)),
          ('r1-style 0,25/0,50/0/0,25', dict(A=.25, B=.5, **{"B'": 0}, C=.25)),
          ("A/B'/C 0,25/0/0,50/0,25", dict(A=.25, B=0, **{"B'": .5}, C=.25)),
          ('đều 0,25×4', dict(A=.25, B=.25, **{"B'": .25}, C=.25)),
          ('bi quan 0,10/0,15/0,35/0,40', dict(A=.10, B=.15, **{"B'": .35}, C=.40)),
          ('0/0/0,5/0,5', dict(A=0, B=0, **{"B'": .5}, C=.5))]

if __name__ == '__main__':
    S = scen(); ks = ['A', 'B', "B'", 'C']
    R = dict(retro={k: round(S[k].get('retro', 0), 1) for k in ks})
    V = {m: {k: model(mode=m, **S[k])[1] for k in ks} for m in ('V1', 'V2', 'H')}
    R['V'] = {m: {k: round(v) for k, v in V[m].items()} for m in V}
    c = lambda w, m='V1': sum(w[k]*V[m][k] for k in ks)
    L = liquidity(); R['liq'] = {k: (round(v, 5) if isinstance(v, float) else v) for k, v in L.items()}
    d5 = L['d_5ty_adv250']; d5b = L['d_5ty_adv68']
    R['d_ref'] = round(d5, 4); R['d_alt68'] = round(d5b, 4)
    R['w_path'] = {n: {m: round(c(w, m)) for m in ('V1', 'V2', 'H')} for n, w in W_PATH}
    R['w_sens'] = {n: dict(V1=round(c(w)), sau_TK=round(c(w)*(1-d5)), x085=round(c(w)*(1-d5)*.85)) for n, w in W_SENS}
    wc = W_PATH[-1][1]
    tam = c(wc); tamL = tam*(1-d5)
    R['center'] = dict(pre_liq=round(tam), post_liq=round(tamL), post_liq_adv68=round(tam*(1-d5b)), post_liq_flat10=round(tam*.9),
                       H_pre=round(c(wc, 'H')), H_post=round(c(wc, 'H')*(1-d5)), V2_pre=round(c(wc, 'V2')), V2_post=round(c(wc, 'V2')*(1-d5)))
    R['zones_post_liq'] = dict(margin_le=round(.85*tamL), fair_low=round(.85*tamL), fair_high=round(1.15*tamL), above_gt=round(1.15*tamL))
    px = L['px_last']; R['price'] = dict(px=px, date=L['px_date'], px_over_center_post=round(px/tamL, 2), px_over_center_pre=round(px/tam, 2))
    # lưới P(A) × P(C) sau TK (V1), B:B' = 1:1,4
    grid = {}
    for a in (0, .1, .15, .2, .25, .35):
        grid[str(a)] = [round(c(dict(A=a, B=(1-a-cc)*.417, **{"B'": (1-a-cc)*.583}, C=cc))*(1-d5)) for cc in (.1, .2, .25, .3, .4)]
    R['grid_post_liq_V1'] = grid; R['grid_max'] = max(max(v) for v in grid.values())
    # độ nhạy r (B' V1 và tâm)
    R['r_sens_center'] = {f'{bp:+d}bp': round(sum(wc[k]*model(mode='V1', r=.135+bp/1e4, **S[k])[1] for k in ks)*(1-d5)) for bp in (-100, -50, 0, 50, 100)}
    # DSCR
    R['dscr_2027'] = {k: dscr_2027(S[k]) for k in ks}
    # Phước Hoà độ nhạy
    R['ph_sens_center'] = {str(ph): round(sum(wc[k]*model(mode='V1', **{**S[k], 'phuoc_hoa': ph})[1] for k in ks)*(1-d5)) for ph in (0, 90.7, 95.7)}
    # tỷ lệ EPTC trả, cùng kỳ 9T (BCTC): DT khu vực Ninh Thuận × 1,08 VAT (ước lượng thuế suất) − Δ phải thu EPTC
    pay = {}
    for lab, rev, d_ar in (('9T/2025', 280.12, 211.94-77.11), ('9T/2026', 295.5, 399.63-237.66)):
        inv = rev*1.08; pay[lab] = dict(rev=rev, inv=round(inv, 1), d_ar=round(d_ar, 1), paid=round(inv-d_ar, 1), ratio=round((inv-d_ar)/inv, 3))
    pay['Q4/2025 d_ar'] = round(237.66-211.94, 1); R['eptc_pay'] = pay
    json.dump(R, open(os.path.join(HERE, 'out_r3.json'), 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(R, ensure_ascii=False, indent=1))
