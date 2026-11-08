"""DCM r6 (= DD redo vòng 3, 08/11/2026, job Taylor_20261108_142018) — áp đính chính fundamental-skeptic TOP5_CORRECTIONS_20261108.md §DCM.
Dựng TRÊN calc/model.py, model_r2.py, model_r5.py (đã khoá md5, KHÔNG sửa). Chạy từ thư mục dd_DCM_20261104/ bằng python3.
Mô hình MÙ GIÁ: giá 06/11 chỉ được đọc ở khối so sánh cuối (PRICE), không vào hàm định giá.

Thay đổi so với r5 (mỗi mục kiểm lại bằng calc trong file này, xem out mục 1):
 C1 P10/P50/P90 ở MỨC KẾT CỤC: mỗi ô lưới = 1 kết cục tất định (không lấy kỳ vọng có điều kiện); wpct (_shared/wpct.py). Trục khí (V1/V2,
    cách đọc A/B, I_C 20/22/25) VÀO lưới.
 C2/C4 BỎ khỏi base: (a) P(thuế XK 0%)=0,55 (nhận định Bobby, không có cơ sở dữ liệu) ⇒ base = luật hiện hành (thuế XK 5% giữ);
    (b) nhánh STRUCT 125 USD/t trọng số 20% vĩnh viễn (Bobby gắn nhãn cho 2–4 quý; model_r2 ghi 'KHÔNG phải trọng số vĩnh viễn') ⇒
    base = biên TB chu kỳ đo được 2016–25. Cả hai sang biến thể song song / độ nhạy.
 C3 Hồi quy LNST~biên: 4 cửa sổ (2021–25 = r5; 2016–25; 2016–25 trừ 2022; 2021–25 trừ 2022) là TRỤC trong lưới, trọng số đều (ước lượng);
    không chọn một cửa sổ theo chiều.
 (thêm, tự rà theo STANDARD_r2 điều 3) Tiền gửi bị hạn chế 332 tỷ: BCTC không trích dự phòng (TM5) ⇒ base = sổ sách (0); lưới r5 gán 50% cho
    −332 không có cơ sở ⇒ sang độ nhạy.
 C5 Rủi ro giảm chưa vào base ⇒ độ nhạy: 2035+, hụt khí 2028–29 (đơn vị), capex thay thế (đơn vị), thuế hiệu dụng lịch sử 5% (ước lượng).
 Thanh khoản: luật căn bậc hai d = 1,0 × σ_ngày × sqrt(Q/ADV trung vị), Q 5 tỷ (tham chiếu) và 10/40 triệu (sleeve), ADV 250 & 60 phiên.
"""
import sys, json, itertools, csv, math, hashlib
sys.path.insert(0, 'calc'); sys.path.insert(0, '../dd_redo_20261105/_shared')
import numpy as np
import model as m
import model_r2 as r2
import model_r5 as r5
from wpct import wpct, weight_below

ps = m.ps
SH = m.SH
DEP_NOW = 7.40          # cctg_rate_vn.current_cctg_rate() = (7.4, 2026-11-02) — đọc 08/11/2026; r = 13,5% + 1,0×(7,40−7,40) = 13,5%
R_NOW = m.rdep(DEP_NOW)
PRICE, PRICE_DATE = 32100.0, '2026-11-06'   # BQ tav2_bq.ticker Close=Price 06/11/2026 (07/11 thứ Bảy) — CHỈ dùng ở khối so sánh
CODE_REG = {'r5_2021_25': [2021, 2022, 2023, 2024, 2025], 'all_2016_25': list(range(2016, 2026)),
            'all_ex22': [y for y in range(2016, 2026) if y != 2022], 'reg_ex22': [2021, 2023, 2024, 2025]}

def fit(years):
    xs = [m.proxy[y] for y in years]; ys = [m.np_[y] for y in years]; mx = sum(xs)/len(xs); my = sum(ys)/len(ys)
    b = sum((x-mx)*(y-my) for x, y in zip(xs, ys))/sum((x-mx)**2 for x in xs)
    return my-b*mx, b
FITS = {k: fit(v) for k, v in CODE_REG.items()}
def set_reg(k): r2.icpt, r2.slope = FITS[k]

def gas_pv(reading, I=22.0, r=R_NOW, B=r5.BRENT_TC):
    """reading: ('A','V1') / ('A','V2') / ('B','V1') hoặc ('ND', nd, var). PV đ/cp phần khí (model_r5.pv_gas)."""
    if reading[0] == 'A': pl, var = r5.nd_share_bao_tieu(I), reading[1]
    elif reading[0] == 'B': pl, var = r5.ND_CAP, reading[1]
    else: pl, var = reading[1], reading[2]
    return r5.pv_gas(B, var, I, r, plateau=pl)

def outcome(reg='r5_2021_25', r=R_NOW, s_lr=None, near=r2.NEAR, gas=('B', 'V1'), I=22.0, p_policy=0.0, restricted=0.0, B=r5.BRENT_TC, late=None):
    """Giá trị TẤT ĐỊNH (đ/cp, trước CK) của MỘT kết cục. Base: p_policy=0, không STRUCT, restricted=0."""
    set_reg(reg); s_lr = m.spread_tc if s_lr is None else s_lr
    pol = p_policy*r2.EXPORT_SAVE_NORM
    v = ps(r2.value(s_lr, r=r, extra_pre_lr=pol, near=near, nc_adj=-r2.KTPL_BAL-restricted)[0])
    if late: r5.LATE['mode'] = late
    g = gas_pv(gas, I, r, B)
    r5.LATE['mode'] = 'base'; set_reg('r5_2021_25')
    return v+g

GAS_AB = [(('A', 'V1'), .25), (('A', 'V2'), .25), (('B', 'V1'), .50)]     # tái lập ĐÚNG tâm r5 = 0,5·A(TB V1/V2) + 0,5·B
GAS_ND = [(('ND', nd, v), 1/8) for nd in (0.30, r5.nd_share_bao_tieu(22.0), r5.ND_CAP, 269.74/445.5) for v in ('V1', 'V2')]
RS = [m.rdep(DEP_NOW+d) for d in (-1, -.5, 0, .5, 1)]

def grid(regs=tuple(CODE_REG), stcs=(138, None, 220), nears=(170, 222, 285), gases=GAS_AB, Is=(20.0, 22.0, 25.0), p_policy=0.0,
         struct_w=0.0, structs=(100, 125, 150), restricted_w=0.0, Bs=(r5.BRENT_TC,)):
    """Mọi kết cục (giá trị, trọng số). struct_w>0: thêm nhánh STRUCT (biên 100/125/150) với tổng trọng số struct_w; restricted_w: xác suất −332."""
    vals, ws = [], []
    for reg, r_, stc, nr, (gs, gw), I, B in itertools.product(regs, RS, stcs, nears, gases, Is, Bs):
        base_w = gw/(len(regs)*len(RS)*len(stcs)*len(nears)*len(Is)*len(Bs))
        branches = [(stc, 1-struct_w)] + ([(s, struct_w/len(structs)) for s in structs] if struct_w else [])
        for s, bw in branches:
            for rc, rw in ((0.0, 1-restricted_w), (r2.RESTRICTED, restricted_w)):
                if rw == 0: continue
                vals.append(outcome(reg, r_, s, nr, gs, I, p_policy, rc, B)); ws.append(base_w*bw*rw)
    return np.array(vals), np.array(ws)

def summ(v, w, d_liq):
    post = v*(1-d_liq); q = wpct(post, w); qpre = wpct(v, w)
    return dict(n=int(len(v)), center_pre=round(float(np.average(v, weights=w))), center_post=round(float(np.average(post, weights=w))),
                p10_out=round(q[.1]), p50_out=round(q[.5]), p90_out=round(q[.9]), p10_pre=round(qpre[.1]), p90_pre=round(qpre[.9]),
                min_out=round(float(post.min())), max_out=round(float(post.max())), pct_weight_below_price=round(weight_below(post, w, PRICE), 4))

def liquidity():
    rows = list(csv.DictReader(open('calc/bq_liq_r6_out.csv')))[-251:]
    c = np.array([float(r['Close']) for r in rows]); p = np.array([float(r['Price']) for r in rows]); vol = np.array([float(r['Volume']) for r in rows])
    val = (p*vol)[1:]; sig = float(np.std(np.diff(np.log(c)), ddof=1)); adv = float(np.median(val)); adv60 = float(np.median(val[-60:]))
    d = lambda q, a: 1.0*sig*math.sqrt(q/a)
    return dict(window=f'{rows[1]["time"]}..{rows[-1]["time"]}', n=len(val), sigma_d=sig, adv250=adv, adv60=adv60,
                d_5bn_adv250=d(5e9, adv), d_5bn_adv60=d(5e9, adv60), q_over_adv250=5e9/adv,
                sleeve={f'{q/1e6:.0f}tr': dict(adv250=d(q, adv), adv60=d(q, adv60)) for q in (10e6, 40e6)}, price_last=float(p[-1]), date_last=rows[-1]['time'])

def implied_margin(price, d_liq, **kw):
    """Biên dài hạn s mà outcome(s)·(1−CK) = price (chia đôi). kw truyền vào outcome (giữ tham số trung tâm)."""
    lo, hi = 0.0, 600.0
    for _ in range(80):
        mid = (lo+hi)/2
        if outcome(s_lr=mid, **kw)*(1-d_liq) < price: lo = mid
        else: hi = mid
    return round((lo+hi)/2, 1)

if __name__ == '__main__':
    L = []; O = {}
    liq = liquidity(); dl = liq['d_5bn_adv250']; O['liquidity'] = liq
    # 0. Control leg: tái lập r5 bằng hàm của r6
    set_reg('r5_2021_25'); r5c = r5.ev_r5()['EV']
    ctl = 0.8*sum(w*outcome(gas=g, p_policy=r2.P_POLICY) for g, w in GAS_AB) + 0.2*sum(w*outcome(gas=g, p_policy=r2.P_POLICY, s_lr=r2.STRUCT_S) for g, w in GAS_AB)
    O['control'] = dict(r5_ev_r5=round(r5c, 3), r6_reconstruct=round(ctl, 3), diff=round(ctl-r5c, 6))
    L.append(f'0. CONTROL: r5.ev_r5() = {r5c:,.3f}; tái lập bằng outcome() r6 (reg r5, policy .55, STRUCT 20%) = {ctl:,.3f}; lệch {ctl-r5c:+.6f} đ/cp')
    L.append(f'   r = {R_NOW:.4f} (lãi huy động 12T hiệu dụng {DEP_NOW}% @2026-11-02, cctg_rate_vn) · giá tham chiếu {PRICE:,.0f} ({PRICE_DATE}, BQ)')
    # 1. kiểm từng đính chính
    reg_tab = {k: dict(icpt=round(a, 1), slope=round(b, 3), lnst_at_179=round(a+b*m.spread_tc, 1), lnst_at_222=round(a+b*222, 1),
                       resid={y: round(m.np_[y]-(a+b*m.proxy[y])) for y in range(2016, 2026)}) for k, (a, b) in FITS.items()}
    O['regressions'] = reg_tab
    L.append('1. C3 hồi quy LNST năm ~ biên proxy (tỷ): '+json.dumps({k: (v['icpt'], v['slope'], v['lnst_at_179']) for k, v in reg_tab.items()}))
    pt = lambda **kw: sum(w*outcome(**kw, gas=g) for g, w in GAS_AB)
    steps = {}
    steps['r5'] = round(r5c)
    steps['bo_policy'] = round(0.8*pt(p_policy=0) + 0.2*pt(p_policy=0, s_lr=r2.STRUCT_S))
    steps['bo_policy_bo_struct'] = round(pt(p_policy=0))
    for k in CODE_REG: steps[f'+reg_{k}'] = round(pt(p_policy=0, reg=k))
    steps['+reg_TB4'] = round(sum(pt(p_policy=0, reg=k) for k in CODE_REG)/4)
    O['bridge_point'] = steps
    L.append('2. Cầu nối điểm (tham số trung tâm, I_C 22, tâm A/B; đ/cp): '+json.dumps(steps))
    # 2. lưới headline + biến thể song song
    G = {}
    G['H_headline'] = summ(*grid(), dl)
    G['V_reg_r5_only'] = summ(*grid(regs=('r5_2021_25',)), dl)
    for k in ('all_2016_25', 'all_ex22', 'reg_ex22'): G[f'V_reg_{k}_only'] = summ(*grid(regs=(k,)), dl)
    G['V_policy_055'] = summ(*grid(p_policy=r2.P_POLICY), dl)
    G['V_struct20'] = summ(*grid(struct_w=0.2), dl)
    G['V_r5conv_outcome'] = summ(*grid(regs=('r5_2021_25',), p_policy=r2.P_POLICY, struct_w=0.2, restricted_w=0.5, Is=(22.0,)), dl)
    G['V_restricted_half'] = summ(*grid(restricted_w=0.5), dl)
    G['V_sym5_margin'] = summ(*grid(stcs=(98, 138, None, 220, 260)), dl)
    G['V_gas_ND4xV1V2'] = summ(*grid(gases=GAS_ND), dl)
    G['V_brent4_upside_only'] = summ(*grid(Bs=(r5.BRENT_TC, 82, 90, 103), Is=(22.0,)), dl)
    O['grids'] = G
    for k, v in G.items(): L.append(f'3. {k}: '+json.dumps(v))
    # 3. giá ngụ ý
    imp = {}
    for k in CODE_REG: imp[f'CYC_nopolicy_{k}'] = round(sum(w*implied_margin(PRICE, dl, reg=k, gas=g) for g, w in GAS_AB), 1)
    imp['CYC_nopolicy_r5reg_at33000_nodisc'] = round(sum(w*implied_margin(33000, 0, gas=g) for g, w in GAS_AB), 1)
    imp['CYC_policy055_r5reg_at33000_nodisc'] = round(sum(w*implied_margin(33000, 0, gas=g, p_policy=r2.P_POLICY) for g, w in GAS_AB), 1)
    for k in ('r5_2021_25', 'all_2016_25'): imp[f'CYC_policy055_{k}_at32100'] = round(sum(w*implied_margin(PRICE, dl, reg=k, gas=g, p_policy=r2.P_POLICY) for g, w in GAS_AB), 1)
    def _avg4(s_):
        return sum(sum(w*outcome(reg=k, gas=g, s_lr=s_) for g, w in GAS_AB) for k in CODE_REG)/4*(1-dl)
    lo, hi = 0.0, 600.0
    for _ in range(80):
        mid = (lo+hi)/2
        if _avg4(mid) < PRICE: lo = mid
        else: hi = mid
    imp['HEADLINE_avg4reg_nopolicy'] = round((lo+hi)/2, 1)
    imp['note'] = 'biên dài hạn (USD/t, proxy urê−25×(2,5+0,06B)) để giá trị kết cục trung tâm sau CK = giá; TB có trọng số GAS_AB của biên hàm ý từng cách đọc'
    O['implied_margin'] = imp
    L.append('4. Biên hàm ý của giá (USD/t): '+json.dumps(imp, ensure_ascii=False))
    # 4. độ nhạy (điểm, tham số trung tâm, TB 4 hồi quy, tâm A/B)
    base_pt = sum(pt(p_policy=0, reg=k) for k in CODE_REG)/4
    def ptx(**kw): return sum(sum(w*outcome(reg=k, gas=g, **kw) for g, w in GAS_AB) for k in CODE_REG)/4
    S = dict(base_point=round(base_pt))
    S['policy_p055'] = round(ptx(p_policy=r2.P_POLICY)-base_pt); S['policy_p1'] = round(ptx(p_policy=1.0)-base_pt)
    S['struct125_w20'] = round(0.8*base_pt+0.2*ptx(s_lr=r2.STRUCT_S)-base_pt)
    S['restricted_332'] = round(ptx(restricted=r2.RESTRICTED)-base_pt)
    S['late2035_flat'] = round(ptx(late='flat')-base_pt); S['late2035_esc'] = round(ptx(late='esc')-base_pt)
    S['dep_-100bp'] = round(ptx(r=m.rdep(DEP_NOW-1))-base_pt); S['dep_+100bp'] = round(ptx(r=m.rdep(DEP_NOW+1))-base_pt)
    S['I_C20'] = round(ptx(I=20.0)-base_pt); S['I_C25'] = round(ptx(I=25.0)-base_pt)
    S['nd30_V1'] = round(sum(outcome(reg=k, gas=('ND', .30, 'V1')) for k in CODE_REG)/4-base_pt)
    S['nd605_V2'] = round(sum(outcome(reg=k, gas=('ND', 269.74/445.5, 'V2')) for k in CODE_REG)/4-base_pt)
    # thuế hiệu dụng lịch sử 5% (ước lượng: giai đoạn giảm 50% của ưu đãi 10%) thay 10,8% khi quy LNST hồi quy về LNTT
    th = r2.TAX_HIST; r2.TAX_HIST = 0.05; S['tax_hist_5pct'] = round(ptx()-base_pt); r2.TAX_HIST = th
    # đơn vị: 100 tỷ/năm FCF sau thuế mất vĩnh viễn từ năm 2 (capex thay thế > khấu hao) — ước lượng ĐƠN VỊ, không phải số đo
    S['capex_per_100bn_yr'] = round(-ps(100/R_NOW/(1+R_NOW)))
    # đơn vị: hụt 10% sản lượng 2028–29 (LNST mất = 10% × LNST dài hạn @179, TB 4 hồi quy)
    lr179 = 0.0
    for k in CODE_REG:
        set_reg(k); lr179 += r2.pbt_at(m.spread_tc)*(1-r2.TAX_LR)*(1-r2.KTPL_RATE)/4
    set_reg('r5_2021_25')
    S['gas_short_10pct_2028_29'] = round(-ps(sum(0.10*lr179/(1+R_NOW)**t for t in (2, 3))))
    S['lnst_lr_at179_avg4reg_ty'] = round(lr179, 1)
    O['sens'] = S
    L.append('5. Độ nhạy (Δ đ/cp so điểm base, trước CK): '+json.dumps(S))
    # 5. so giá
    H = G['H_headline']
    O['compare'] = dict(price=PRICE, price_date=PRICE_DATE, px_vs_center_post=round(PRICE/H['center_post']-1, 4),
                        px_vs_p10=round(PRICE/H['p10_out']-1, 4), px_vs_p90=round(PRICE/H['p90_out']-1, 4),
                        label=('DƯỚI vùng (<P10)' if PRICE < H['p10_out'] else ('TRÊN vùng (>P90)' if PRICE > H['p90_out'] else 'TRONG vùng')))
    L.append('6. So giá: '+json.dumps(O['compare'], ensure_ascii=False))
    L.append('7. Thanh khoản: '+json.dumps({k: (round(v, 5) if isinstance(v, float) else v) for k, v in liq.items()}, ensure_ascii=False))
    print('\n'.join(L)); open('calc/model_r6_out.txt', 'w').write('\n'.join(L)+'\n')
    json.dump(O, open('calc/model_r6_out.json', 'w'), ensure_ascii=False, indent=1, sort_keys=True)
