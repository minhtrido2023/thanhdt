"""DCM r7 (23/11/2026, job Taylor_20261122_234422) — áp verdict fundamental-skeptic DD_GENERAL r1 (22/11, REFUTED, skeptic/r1.json).
Dựng TRÊN model.py / model_r2.py / model_r5.py / model_r6.py (đã khoá md5 trong LOCK_r6, KHÔNG sửa). Chạy từ dd_DCM_20261104/ bằng python3.
MÙ GIÁ: file này KHÔNG đọc giá/vốn hoá/P/E của DCM. So giá làm ở calc/compare_px_r7.py SAU khi khoá (LOCK_r7_md5.txt).

Hạng mục skeptic r1 → xử lý (chi tiết REPORT_rev7.md §1):
 K1 Nền LN trộn hai chế độ khấu hao. D&A KT: 2024 268,08 / 2025 342,07 tỷ (BCTC HN KT 2025, LCTT mã 02, png_r7/kt25_p13);
    9T/26 301,07 (BCTC HN Q3/26 LCTT mã 02, png_r7/q326_p09). 2018–23: suy từ BQ (EBITDA_P0 − EBITM_P0×DT TTM, quý 4; calc/bq_da_r7.sql)
    vì BCTC KT 2021–23 không tải được (pvcfc.com.vn chặn Cloudflare 23/11). 2016–17: BQ nhiễu ⇒ dùng TB 2018–20 (ước lượng).
    Hồi quy lại trên LN trước khấu hao: NP_bD = NP + DA×(1−TAX_HIST); LNST tại chế độ D&A = M: icpt_M = icpt_bD − M×(1−TAX_HIST).
 K2 Capex thay thế/duy trì cho dòng vĩnh viễn: M = capex duy trì chuẩn hoá = mức D&A thay thế ở trạng thái dừng (FCF = LNST(M) + D&A − capex = LNST(M)).
    Trục lưới M ∈ {342,07 (D&A 2025 KT), 401,4 (D&A 9T/26 năm hoá), 540 (cận trên khung TM16 9T/26 năm hoá)}, trọng số đều.
    Khung TM16: capex 9T/26 545,94; dự án tăng trưởng nhận diện được (Nhơn Trạch +31,4, khí CN +98,0, Thạnh Hoá +11,7 = 141,1) ⇒ duy trì ≤ 404,8 (9T) = 540 năm;
    phần chắc chắn là duy trì (HTS/LTS +152,4, công trình khác +18,7 = 171,1) ⇒ ≥ 228 năm (chưa gồm mua TSCĐ trực tiếp).
 K3 Quỹ KH&CN 1.059,37 tỷ (CĐKT Q3/26 mã 344, nợ dài hạn): tiền đã trích trước thuế, BẮT BUỘC dùng cho KH&CN trong 5 năm (Luật KH&CN 2013 Đ63;
    TT 67/2022), chi từ quỹ KHÔNG qua P&L ⇒ dòng tiền ra tương lai không có trong LN hồi quy ⇒ base TRỪ khỏi net cash như quỹ KTPL (V4b: chi
    tuân thủ = dòng tiền ra). Độ nhạy: chỉ mất phần hoàn thuế nếu không dùng (≈20%+lãi, ước lượng) / dùng tạo tài sản NPV=0.
 K4 Đầu vào mất (bq_np_hist_out.csv, bq_commod_out.csv): khôi phục từ git 906dfecd0^ (bản trước khi TRIM), md5 khớp LOCK_r6.
 K5 Phản biện bản cũ đã bị thay: rev7 thay r6 + báo cáo NĐT 05/11.
"""
import sys, json, itertools, csv, math
sys.path.insert(0, 'calc'); sys.path.insert(0, '../dd_redo_20261105/_shared')
import numpy as np
import model as m
import model_r2 as r2
import model_r5 as r5
import model_r6 as r6
from wpct import wpct

ps = m.ps
R_NOW = r6.R_NOW                       # 13,5% — lãi huy động 12T hiệu dụng 7,40% (deposit_rate_vn: cctg_12m 2026-11-02, cập nhật 16/11; đọc 23/11)
DEP_NOW = r6.DEP_NOW
TH = r2.TAX_HIST

# ---------- K1: D&A theo năm (tỷ) ----------
DA_KT = {2024: 268.081458415, 2025: 342.065274662}            # BCTC HN KT 2025 LCTT mã 02 (năm nay / năm trước)
DA_9T26 = 301.071352990                                         # BCTC HN Q3/26 LCTT mã 02
def _bq_da():
    out = {}
    for r in csv.DictReader(open('calc/bq_da_r7_out.csv')):
        q = r['quarter']
        if not q.endswith('Q4') or not r['rev_ttm']: continue
        e, mm, rv = float(r['ebitda_ttm']), float(r['ebitm_ttm_pct']), float(r['rev_ttm'])
        out[int(q[:4])] = e - mm*rv
    return out
DA_BQ = _bq_da()
BQ_CALIB = {y: DA_BQ[y]/DA_KT[y] for y in DA_KT}                # BQ/KT: 2024 0,86 · 2025 0,80 ⇒ BQ đánh THẤP D&A
def da_series(calib=False):
    d = {}
    base1820 = sum(DA_BQ[y] for y in (2018, 2019, 2020))/3
    for y in range(2016, 2024):
        v = DA_BQ[y] if y >= 2018 else base1820                  # 2016–17: BQ nhiễu (952 / 1.870) ⇒ TB 2018–20 (ước lượng)
        if calib: v = v/(sum(BQ_CALIB.values())/len(BQ_CALIB))   # độ nhạy: hiệu chỉnh lệch BQ đo được ở 2024–25
        d[y] = v
    d.update(DA_KT)
    return d
DA = da_series()
M_GRID = (342.065274662, DA_9T26/0.75, 540.0)
M_BASE = DA_9T26/0.75
# Cửa sổ headline r7: chỉ 2 cửa sổ trong chế độ khí mà model_r5.bias_hist() hiệu chỉnh (HIST_B = 2021–25). Cơ sở: sau khi cộng D&A, 2 cửa sổ có
# 2016–20 cho phần dư 2024/2025 (năm KT) = −463/−651 và −350/−162 tỷ (dự báo quá cao năng lực hiện tại) — xem out mục 1. 4 cửa sổ = biến thể song song.
HEAD_REGS = ('r5_2021_25', 'reg_ex22')
KHCN = 1059.373520436                                           # CĐKT HN Q3/26 mã 344

def fit_bd(years, da):
    xs = [m.proxy[y] for y in years]; ys = [m.np_[y] + da[y]*(1-TH) for y in years]
    mx, my = sum(xs)/len(xs), sum(ys)/len(ys)
    b = sum((x-mx)*(y-my) for x, y in zip(xs, ys))/sum((x-mx)**2 for x in xs)
    return my-b*mx, b
FITS_BD = {k: fit_bd(v, DA) for k, v in r6.CODE_REG.items()}
FITS_BD_CAL = {k: fit_bd(v, da_series(True)) for k, v in r6.CODE_REG.items()}

def set_reg7(reg, M, cal=False):
    a, b = (FITS_BD_CAL if cal else FITS_BD)[reg]
    r2.icpt, r2.slope = a - M*(1-TH), b

def outcome7(reg='r5_2021_25', r=R_NOW, s_lr=None, near=r2.NEAR, gas=('B', 'V1'), I=22.0, M=M_BASE, khcn=1.0, restricted=0.0,
             p_policy=0.0, B=r5.BRENT_TC, late=None, cal=False, life_end=None):
    """Giá trị TẤT ĐỊNH (đ/cp, trước CK) của một kết cục r7. M=None ⇒ hồi quy LNST gốc (r6, để làm control)."""
    if M is None: r6.set_reg(reg)
    else: set_reg7(reg, M, cal)
    s_lr = m.spread_tc if s_lr is None else s_lr
    v_ty, y1, lr = r2.value(s_lr, r=r, extra_pre_lr=p_policy*r2.EXPORT_SAVE_NORM, near=near,
                            nc_adj=-r2.KTPL_BAL - restricted - khcn*KHCN)
    if life_end:   # độ nhạy: nhà máy dừng ở life_end, không tái đầu tư, không giá trị cuối (ước lượng; KHÔNG vào base)
        n = life_end - 2027 + 1
        v_ty -= (lr/r)/(1+r)**n/(1+r)
    v = ps(v_ty)
    if late: r5.LATE['mode'] = late
    g = r6.gas_pv(gas, I, r, B)
    r5.LATE['mode'] = 'base'; r6.set_reg('r5_2021_25')
    return v + g

def grid7(regs=HEAD_REGS, stcs=(138, None, 220), nears=(170, 222, 285), gases=r6.GAS_AB, Is=(20.0, 22.0, 25.0),
          Ms=M_GRID, khcn=1.0, cal=False, p_policy=0.0, restricted_w=0.0):
    vals, ws = [], []
    for reg, r_, stc, nr, (gs, gw), I, M in itertools.product(regs, r6.RS, stcs, nears, gases, Is, Ms):
        w = gw/(len(regs)*len(r6.RS)*len(stcs)*len(nears)*len(Is)*len(Ms))
        for rc, rw in ((0.0, 1-restricted_w), (r2.RESTRICTED, restricted_w)):
            if rw == 0: continue
            vals.append(outcome7(reg, r_, stc, nr, gs, I, M, khcn, rc, p_policy, cal=cal)); ws.append(w*rw)
    return np.array(vals), np.array(ws)

def summ_pre(v, w):
    q = wpct(v, w, (.1, .25, .5, .75, .9))
    return dict(n=int(len(v)), center_pre=round(float(np.average(v, weights=w))), p10_pre=round(q[.1]), p25_pre=round(q[.25]),
                p50_pre=round(q[.5]), p75_pre=round(q[.75]), p90_pre=round(q[.9]), min_pre=round(float(v.min())), max_pre=round(float(v.max())))

def pt7(**kw):
    """Điểm tại tham số trung tâm: TB 4 cửa sổ hồi quy × tâm khí A/B, I_C 22."""
    regs = kw.pop('regs', HEAD_REGS)
    return sum(sum(w*outcome7(reg=k, gas=g, **kw) for g, w in r6.GAS_AB) for k in regs)/len(regs)

if __name__ == '__main__':
    L, O = [], {}
    # 0. control: M=None, khcn=0 ⇒ phải tái lập điểm base r6 (24.818) và headline r6 trước CK (24.964)
    ctl_pt = pt7(M=None, khcn=0.0, regs=tuple(r6.CODE_REG))
    O['control'] = dict(r6_point_reported=24818, r7_point_M_None_khcn0=round(ctl_pt, 3))
    L.append(f'0. CONTROL: điểm r6 (M=None, không trừ KH&CN) = {ctl_pt:,.3f} (r6 báo 24.818)')
    # 1. D&A + hồi quy
    O['da'] = {str(y): round(v, 1) for y, v in DA.items()}; O['da_bq_raw'] = {str(y): round(v, 1) for y, v in DA_BQ.items()}
    O['bq_calib'] = {str(y): round(v, 3) for y, v in BQ_CALIB.items()}
    L.append('1. D&A dùng (tỷ): '+json.dumps(O['da'])+' · BQ thô: '+json.dumps(O['da_bq_raw'])+' · BQ/KT: '+json.dumps(O['bq_calib']))
    reg = {}
    for k in r6.CODE_REG:
        a0, b0 = r6.FITS[k]; a, b = FITS_BD[k]
        reg[k] = dict(r6_icpt=round(a0, 1), r6_slope=round(b0, 3), bd_icpt=round(a, 1), bd_slope=round(b, 3),
                      lnst179_r6=round(a0+b0*m.spread_tc, 1), **{f'lnst179_M{int(M)}': round(a-M*(1-TH)+b*m.spread_tc, 1) for M in M_GRID},
                      resid_bd={y: round(m.np_[y]+DA[y]*(1-TH)-(a+b*m.proxy[y])) for y in r6.CODE_REG[k]})
    O['regressions'] = reg
    for k, v in reg.items(): L.append(f'   {k}: '+json.dumps(v))
    # 2. cầu nối điểm
    br = {}
    br['r6_point'] = round(ctl_pt)
    br['r6_point_2cuaso_2021+'] = round(pt7(M=None, khcn=0.0))
    br['+K1 chế độ D&A, M = D&A 2025 KT (342)'] = round(pt7(M=M_GRID[0], khcn=0.0))
    br['+K2 M = D&A 9T/26 năm hoá (401)'] = round(pt7(M=M_BASE, khcn=0.0))
    br['+K3 trừ quỹ KH&CN 1.059'] = round(pt7(M=M_BASE, khcn=1.0))
    br['(lưới M 342/401/540 TB, điểm)'] = round(sum(pt7(M=M_, khcn=1.0) for M_ in M_GRID)/3)
    O['bridge_point'] = br
    L.append('2. Cầu nối điểm (đ/cp, trước CK): '+json.dumps(br, ensure_ascii=False))
    # 3. lưới
    G = {}
    G['H_headline'] = summ_pre(*grid7())
    G['V_M342_only'] = summ_pre(*grid7(Ms=(M_GRID[0],)))
    G['V_M401_only'] = summ_pre(*grid7(Ms=(M_BASE,)))
    G['V_M540_only'] = summ_pre(*grid7(Ms=(540.0,)))
    G['V_M738_allcapex'] = summ_pre(*grid7(Ms=(738.0,)))
    G['V_da_bq_calibrated'] = summ_pre(*grid7(cal=True))
    G['V_khcn_20pct'] = summ_pre(*grid7(khcn=0.2))
    G['V_khcn_0'] = summ_pre(*grid7(khcn=0.0))
    G['V_policy055'] = summ_pre(*grid7(p_policy=r2.P_POLICY))
    G['V_restricted_half'] = summ_pre(*grid7(restricted_w=0.5))
    G['V_4windows_r6axis'] = summ_pre(*grid7(regs=tuple(r6.CODE_REG)))
    G['V_reg_r5_2021_25_only'] = summ_pre(*grid7(regs=('r5_2021_25',)))
    G['V_reg_ex22_only'] = summ_pre(*grid7(regs=('reg_ex22',)))
    G['V_r6basis_noDA_nokhcn_2win'] = summ_pre(*grid7(Ms=(None,), khcn=0.0))
    G['V_reg_all_ex22_only'] = summ_pre(*grid7(regs=('all_ex22',)))
    O['grids'] = G
    for k, v in G.items(): L.append(f'3. {k}: '+json.dumps(v))
    # 4. độ nhạy (điểm base = TB lưới M tại tham số trung tâm)
    base = sum(pt7(M=M_) for M_ in M_GRID)/3
    def d(**kw): return round(sum(pt7(M=M_, **kw) for M_ in M_GRID)/3 - base)
    S = dict(base_point=round(base))
    S['dep_-100bp'] = d(r=m.rdep(DEP_NOW-1)); S['dep_-50bp'] = d(r=m.rdep(DEP_NOW-.5))
    S['dep_+50bp'] = d(r=m.rdep(DEP_NOW+.5)); S['dep_+100bp'] = d(r=m.rdep(DEP_NOW+1))
    S['beta05_+100bp'] = d(r=m.rdep(DEP_NOW+1, 0.5)); S['beta05_-100bp'] = d(r=m.rdep(DEP_NOW-1, 0.5))
    S['Ke_12.3'] = d(r=0.123); S['Ke_13.4'] = d(r=0.134)
    S['capex_per_100bn_yr'] = round(sum(pt7(M=M_BASE+100) for _ in [0]) - pt7(M=M_BASE))
    S['life_end_2042'] = d(life_end=2042); S['life_end_2047'] = d(life_end=2047)
    S['late2035_flat'] = d(late='flat'); S['late2035_esc'] = d(late='esc')
    S['policy_p055'] = d(p_policy=r2.P_POLICY); S['policy_p1'] = d(p_policy=1.0)
    S['restricted_332'] = d(restricted=r2.RESTRICTED)
    S['khcn_20pct'] = d(khcn=0.2); S['khcn_0'] = d(khcn=0.0)
    S['da_bq_calibrated'] = d(cal=True)
    S['4windows'] = d(regs=tuple(r6.CODE_REG))
    S['struct125'] = d(s_lr=r2.STRUCT_S)
    th = r2.TAX_HIST; r2.TAX_HIST = 0.05; S['tax_hist_5pct'] = d(); r2.TAX_HIST = th
    O['sens'] = S
    L.append('4. Độ nhạy (Δ đ/cp so điểm base, trước CK): '+json.dumps(S))
    # 5. V6 hai nền — CHỈ HIỂN THỊ (g=0 ⇒ tái đầu tư 0; r = R_NOW). Nguồn: BCTC KT 2025 LCTT (CFO/capex 2024–25), BCTC Q3/26 (9T/26, 9T/25)
    cfo = {'2024': 77.549319891, '2025': -775.841653059, 'TTM_Q3_26': 2331.321729863 + (-775.841653059 - (-2016.900834517))}
    capex = {'2024': 791.149614699, '2025': 694.635379203, 'TTM_Q3_26': 545.936940673 + (694.635379203 - 323.065549904)}
    np_ttm = {'TTM_Q3_24': None, 'FY2024': m.np_[2024], 'FY2025': m.np_[2025], 'TTM_Q3_26': 2282.089926625 + (m.np_[2025] - 1525.228572462)}
    ni_norm = float(np.median([m.np_[2024], m.np_[2025], np_ttm['TTM_Q3_26']]))
    fcfe3 = sum(cfo[k]-capex[k] for k in cfo)/3
    c4 = sum(cfo[k]-min(capex[k], DA_KT.get(int(k), DA_9T26/0.75) if k.isdigit() else DA_9T26/0.75) for k in cfo)/3
    v_short = ps(ni_norm/R_NOW); v_long = ps(fcfe3/R_NOW) if fcfe3 > 0 else None
    O['v6'] = dict(ni_norm_median3=round(ni_norm, 1), fcfe3_avg=round(fcfe3, 1), v_short=round(v_short), v_long=(round(v_long) if v_long else None),
                   D=(round(abs(math.log(v_short/v_long)), 3) if v_long else None), v_c4=round(ps(c4/R_NOW)), cfo=cfo, capex=capex,
                   note='g=0; nền equity gồm lãi tiền gửi ⇒ KHÔNG cộng net cash; chỉ hiển thị')
    L.append('5. V6 (chỉ hiển thị): '+json.dumps(O['v6'], ensure_ascii=False))
    print('\n'.join(L)); open('calc/model_r7_out.txt', 'w').write('\n'.join(L)+'\n')
    json.dump(O, open('calc/model_r7_out.json', 'w'), ensure_ascii=False, indent=1, sort_keys=True)
