"""DCM r2 — áp đính chính skeptic S1-S4 + nhánh ADMIN + bất đối xứng chi phí khí. MÙ GIÁ (không đầu vào giá/vốn hoá/PE).
Chạy từ thư mục dd_DCM_20261104/. Dùng lại hồi quy/hằng số của calc/model.py (r1, đã khoá md5), chỉ ghi đè phần đính chính.
Đơn vị tỷ đồng. Giả định tự đặt gắn (ước lượng)."""
import sys, json, itertools
sys.path.insert(0, 'calc')
import model as m
ps, icpt, slope, spread_tc = m.ps, m.icpt, m.slope, m.spread_tc
R0, DEP0, rdep = m.R0, m.DEP0, m.rdep
TAX_HIST, NI_cash_pre = m.TAX_HIST, m.NI_cash_pre
# --- đo từ BCTC Q3/26 (trang gốc đã đọc lại 04/11) ---
TAX_LR = 0.20                      # S1: BCTC HN Q3/26 tr.17 (pdf p21): 2026 là năm thứ 15 hưởng 10% ⇒ 20% từ 2027
TAX_Y1 = 0.25*TAX_HIST + 0.75*0.20 # năm 1 = Q4/26 (10,8%) + Q1-Q3/27 (20%)
KTPL_RATE = 136.191473296/2282.089926625   # S2: TM37 (pdf p41) tạm trích quỹ KTPL / LNST 9T/26
KTPL_BAL = 265.344920662           # S2: CĐKT mã 323 (pdf p6 ảnh q326hn_p06) quỹ KTPL 30/9/2026
EXPORT_FY25 = 4051.6               # DT xuất khẩu urê FY25 (brief Mike, S-ADMIN i)
EXPORT_SAVE_NORM = 0.05*EXPORT_FY25   # = 202,6 tỷ/năm trước thuế (chuẩn hoá theo xuất khẩu FY25)
P_POLICY = 0.55                    # P nghị định thuế XK 0% trước 31/3/2027 (Bobby) — áp ĐỘC LẬP mọi nhánh
RESTRICTED = 332.0
NEAR = 222
WTS = dict(CYC=0.50, ADMIN=0.30, STRUCT=0.20)   # Bobby: cho "2-4 quý tới", KHÔNG phải trọng số vĩnh viễn (S3)
STRUCT_S = 125.0

def pbt_at(s): return (icpt + slope*s)/(1-TAX_HIST) - NI_cash_pre
def value(s_lr, r=R0, extra_pre_lr=0.0, extra_pre_y1=0.0, tax_y1=TAX_Y1, tax_lr=TAX_LR, k=KTPL_RATE, nc_adj=-KTPL_BAL,
          near=NEAR, tail_pv=0.0):
    y1 = (pbt_at(near)+extra_pre_y1)*(1-tax_y1)*(1-k)
    lr = (pbt_at(s_lr)+extra_pre_lr)*(1-tax_lr)*(1-k)
    return (y1/(1+r) + (lr/r)/(1+r) + m.net_cash + nc_adj + tail_pv), y1, lr

def ev_r2(r=R0, s_tc=None, near=NEAR, struct=STRUCT_S, nc_adj=-KTPL_BAL, extra_lr=0.0, extra_y1=0.0, p_policy=P_POLICY,
          tail_pv=0.0, tax_lr=TAX_LR):
    s_tc = spread_tc if s_tc is None else s_tc
    pol = p_policy*EXPORT_SAVE_NORM + extra_lr      # kỳ vọng tiết kiệm thuế XK, mọi nhánh
    kw = dict(r=r, near=near, nc_adj=nc_adj, extra_pre_lr=pol, extra_pre_y1=extra_y1, tail_pv=tail_pv, tax_lr=tax_lr)
    vc = value(s_tc, **kw)[0]; vs = value(struct, **kw)[0]
    va = vc   # ADMIN = CYC về biên; phần chính sách đã nằm ở pol cho MỌI nhánh ⇒ trùng CYC
    ev = WTS['CYC']*vc + WTS['ADMIN']*va + WTS['STRUCT']*vs
    return dict(CYC=ps(vc), ADMIN=ps(va), STRUCT=ps(vs), EV=ps(ev))

# --- cầu nối r1 -> r2 (cộng dồn, từng bước) ---
def r1_ev(): return m.base['EV']
def step(tax_y1=m.TAX_HIST, k=0.0, nc=0.0, mode='r1'):
    s_tc = spread_tc
    kw = dict(tax_y1=tax_y1, k=k, nc_adj=nc)
    if mode == 'r1':   # ADMIN lồng 0,30 × P 0,55 × 381
        vc = value(s_tc, extra_pre_lr=0.0, **kw)[0]; vs = value(STRUCT_S, **kw)[0]
        va = value(s_tc, extra_pre_lr=m.P_EXPORT_TAX0*m.EXPORT_TAX_SAVE_PRE, **kw)[0]
        return ps(.5*vc+.3*va+.2*vs)
    pol = P_POLICY*EXPORT_SAVE_NORM
    vc = value(s_tc, extra_pre_lr=pol, **kw)[0]; vs = value(STRUCT_S, extra_pre_lr=pol, **kw)[0]
    return ps(.8*vc+.2*vs)

# --- kịch bản chi phí khí (độc lập, KHÔNG vào base: nguồn thứ cấp CTCK) ---
USDVND = 26400.0                   # (ước lượng) ~5.000 tỷ / 189,44 triệu USD (TM27)
PROD_KT = 966.7                    # 2025 urê quy đổi sản xuất, NQ ĐHĐCĐ
BRENT_TC = sum(m.cm[y][1] for y in range(2016, 2026))/10   # đo: Brent TB 2016-25 (WB, BQ)
MMBTU_PER_T = 25                   # công thức proxy Bobby
def gas_scen():
    out = {}
    # Petronas 12,7% -> 13,7% Brent từ 2027: ΔUSD/t = 1pp × Brent × 50% khí Petronas × 25 MMBtu/t
    d_usd_t = 0.01*BRENT_TC*0.5*MMBTU_PER_T
    d_pre = d_usd_t*PROD_KT*1e3*USDVND/1e9      # tỷ/năm
    out['petronas_usd_t'] = d_usd_t; out['petronas_pre_ty'] = d_pre
    base = ev_r2()['EV']
    out['petronas'] = ev_r2(extra_lr=-d_pre, extra_y1=-0.75*d_pre)['EV'] - base
    # Nam Du 10,39 USD/MMBtu từ ~Q4/2028 (t=2,0 năm sau 30/9/2026), chiếm w, thay khí giá theo công thức ở Brent_ref; KHÔNG tính +2,25%/năm (nới tay có lợi)
    for w, bref in ((0.35, 90.0), (0.35, BRENT_TC), (0.60, BRENT_TC)):
        palt = 2.5 + 0.06*bref
        d_pre_nd = (10.39-palt)*MMBTU_PER_T*w*PROD_KT*1e3*USDVND/1e9
        r = R0
        loss_pv = d_pre_nd*(1-TAX_LR)*(1-KTPL_RATE)/r/(1+r)**2
        out[f'namdu_w{w}_brent{bref:.0f}'] = dict(pre_ty=d_pre_nd, d_dcp=-ps(loss_pv), palt=palt)
    return out
# --- NPK ưu đãi còn lại (PHÍA TĂNG): giảm 50% thuế (20% -> 10%) trên phần LNTT NPK trong N năm kể từ năm 2 ---
def npk_upside(share, n_years, r=R0):
    b = share*pbt_at(spread_tc)*(TAX_LR*0.5)*(1-KTPL_RATE)
    ann = (1-(1+r)**-n_years)/r
    return ps(b*ann/(1+r))
# --- bảng biên dài hạn -> giá trị (đối xứng, không dùng để dịch tâm) ---
def margin_table(ms=(150, 179, 220, 242, 260)):
    t = {}
    for s in ms:
        e = ev_r2(s_tc=s)
        t[s] = dict(CYC=round(e['CYC']), EV=round(e['EV']), pbt=round(pbt_at(s)))
    return t
if __name__ == '__main__':
    L = []; base = ev_r2()
    L.append(f'0. Hằng số r2: TAX_LR {TAX_LR:.0%} · TAX_Y1 {TAX_Y1:.4f} (=0,25×10,8%+0,75×20%) · KTPL {KTPL_RATE:.4%} LNST (136,19/2.282,09) · quỹ KTPL trừ khỏi net cash {KTPL_BAL:.1f} · net cash gộp {m.net_cash:.1f} -> {m.net_cash-KTPL_BAL:.1f} ({ps(m.net_cash-KTPL_BAL):,.0f} đ/cp)')
    L.append(f'   tiết kiệm thuế XK chuẩn hoá = 5%×{EXPORT_FY25} = {EXPORT_SAVE_NORM:.1f} tỷ/năm trước thuế (r1: 285,4/0,75 = {m.EXPORT_TAX_SAVE_PRE:.1f}); kỳ vọng ×{P_POLICY} = {P_POLICY*EXPORT_SAVE_NORM:.1f}')
    L.append(f'1. Giá trị r2 (đ/cp): CYC {base["CYC"]:,.0f} · ADMIN {base["ADMIN"]:,.0f} (≡CYC, chính sách đã vào mọi nhánh) · STRUCT {base["STRUCT"]:,.0f} · KỲ VỌNG {base["EV"]:,.0f}')
    s0 = r1_ev(); s1 = step(tax_y1=TAX_Y1); s2 = step(tax_y1=TAX_Y1, k=KTPL_RATE, nc=-KTPL_BAL); s3 = step(TAX_Y1, KTPL_RATE, -KTPL_BAL, mode='r2')
    L.append(f'2. Cầu nối r1->r2 (cộng dồn): r1 {s0:,.0f} | +S1 thuế năm 1 {s1:,.0f} (Δ{s1-s0:+,.0f}; skeptic −187) | +S2 quỹ KTPL {s2:,.0f} (Δ{s2-s1:+,.0f}; skeptic −1.289) | +ADMIN {s3:,.0f} (Δ{s3-s2:+,.0f}; skeptic +479) | tổng Δ{s3-s0:+,.0f}')
    L.append(f'   (S2 tách: trừ LNST {(step(TAX_Y1,KTPL_RATE,0)-s1):+,.0f} · trừ quỹ số dư {(s2-step(TAX_Y1,KTPL_RATE,0)):+,.0f})')
    mt = margin_table()
    L.append('3. Biên dài hạn -> giá trị (đ/cp; CYC = 100% biên đó; EV = 0,8×biên + 0,2×STRUCT125): '+' | '.join(f'{s}: CYC {v["CYC"]:,} · EV {v["EV"]:,} (LNTT ht {v["pbt"]})' for s, v in mt.items()))
    sens = {}
    for d in (-1.0, -0.5, 0.5, 1.0):
        for b in (0.5, 1.0): sens[f'dep{d:+.1f}_b{b}'] = round(ev_r2(r=rdep(DEP0+d, b))['EV'])
    sens['restricted-332'] = round(ev_r2(nc_adj=-KTPL_BAL-RESTRICTED)['EV'])
    sens['near_170'] = round(ev_r2(near=170)['EV']); sens['near_285'] = round(ev_r2(near=285)['EV'])
    sens['tc_150'] = round(ev_r2(s_tc=150)['EV']); sens['tc_210'] = round(ev_r2(s_tc=210)['EV'])
    sens['struct_100'] = round(ev_r2(struct=100)['EV'])
    sens['policy_p0'] = round(ev_r2(p_policy=0)['EV']); sens['policy_p1'] = round(ev_r2(p_policy=1)['EV'])
    sens['export_r1_381_norm_off'] = round(ev_r2(extra_lr=P_POLICY*(m.EXPORT_TAX_SAVE_PRE-EXPORT_SAVE_NORM))['EV'])
    L.append('4. Độ nhạy kỳ vọng (đ/cp): '+json.dumps(sens, ensure_ascii=False))
    npk = {f'sh{int(sh*100)}_N{n}': round(npk_upside(sh, n)) for sh in (0.10, 0.20) for n in (5, 10)}
    L.append('5. NPK ưu đãi còn lại — PHÍA TĂNG (giảm 50% thuế = −10đ% LNTT NPK; share LNTT NPK {10%,20%} × N năm còn lại {5,10}; năm bắt đầu NPK KHÔNG nêu ⇒ ước lượng) (đ/cp cộng thêm): '+json.dumps(npk))
    g = gas_scen()
    L.append(f'6. Chi phí khí (độc lập; KHÔNG vào base — nguồn CTCK): Brent TB 2016-25 = {BRENT_TC:.1f}; Petronas +1pp×Brent×50%×25 MMBtu/t = {g["petronas_usd_t"]:.2f} USD/t -> {g["petronas_pre_ty"]:.0f} tỷ/năm trước thuế (×{PROD_KT} kt, {USDVND:.0f} đ/USD) ⇒ Δ kỳ vọng {g["petronas"]:+,.0f} đ/cp')
    for k_, v in g.items():
        if k_.startswith('namdu'): L.append(f'   Nam Du {k_}: giá thay thế {v["palt"]:.2f} USD/MMBtu, chi phí tăng {v["pre_ty"]:.0f} tỷ/năm trước thuế từ Q4/2028 ⇒ {v["d_dcp"]:+,.0f} đ/cp (chưa tính +2,25%/năm)')
    grid = []
    for r_, stc, near_, st_, rc in itertools.product([rdep(DEP0+d) for d in (-1, -.5, 0, .5, 1)], [150, spread_tc, 210], [170, 222, 285], [100, 125, 150], [0, -RESTRICTED]):
        grid.append(ev_r2(r=r_, s_tc=stc, near=near_, struct=st_, nc_adj=-KTPL_BAL+rc)['EV'])
    grid.sort(); n = len(grid); q = lambda f: grid[int(f*(n-1))]
    L.append(f'7. Lưới {n} (r±100bp × biên TC 150/{spread_tc:.0f}/210 × năm1 170/222/285 × STRUCT 100/125/150 × phong toả 0/−332; thuế 20%): P10 {q(.1):,.0f} · P25 {q(.25):,.0f} · P50 {q(.5):,.0f} · P75 {q(.75):,.0f} · P90 {q(.9):,.0f}')
    grid2 = []
    for r_, stc, near_, st_, rc in itertools.product([rdep(DEP0+d) for d in (-1, -.5, 0, .5, 1)], [150, spread_tc, 220, 260], [170, 222, 285], [100, 125, 150], [0, -RESTRICTED]):
        grid2.append(ev_r2(r=r_, s_tc=stc, near=near_, struct=st_, nc_adj=-KTPL_BAL+rc)['EV'])
    grid2.sort(); n2 = len(grid2); q2 = lambda f: grid2[int(f*(n2-1))]
    L.append(f'8. Lưới MỞ RỘNG (biên TC 150/{spread_tc:.0f}/220/260, {n2} ô; phụ — cho nhãn có điều kiện): P10 {q2(.1):,.0f} · P25 {q2(.25):,.0f} · P50 {q2(.5):,.0f} · P75 {q2(.75):,.0f} · P90 {q2(.9):,.0f}')
    print('\n'.join(L)); open('calc/model_r2_out.txt', 'w').write('\n'.join(L)+'\n')
    json.dump(dict(base=base, bridge=dict(r1=s0, s1=s1, s2=s2, r2=s3), sens=sens, npk=npk, margin_table=mt, gas={k: v for k, v in g.items()},
                   grid=dict(P10=q(.1), P25=q(.25), P50=q(.5), P75=q(.75), P90=q(.9)),
                   grid_wide=dict(P10=q2(.1), P25=q2(.25), P50=q2(.5), P75=q2(.75), P90=q2(.9)), net_cash_after_ktpl=m.net_cash-KTPL_BAL),
              open('calc/model_r2_out.json', 'w'), ensure_ascii=False, indent=1)
