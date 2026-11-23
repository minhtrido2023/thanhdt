"""DCM rev9 (23/11/2026, job Taylor_20261123_100914, VÒNG 3 — cuối) — áp verdict fundamental-skeptic r3 (REFUTED, skeptic/r3.json) lên model_r8.
Dựng TRÊN model_r8.py (khoá LOCK_r8, KHÔNG sửa). Chạy từ dd_DCM_20261104/. MÙ GIÁ: file này không đọc giá; so giá ở compare_px_r9.py sau LOCK_r9.

T1 MỘT quy tắc cho quỹ KH&CN — cả SỐ DƯ lẫn DÒNG TRÍCH hằng năm (skeptic r3 killer objection):
   mỗi đồng trích GỘP có giá trị cho cổ đông v(t,L,r) = (1 − t·(1 + 2·Y5)) × ((1+d)/(1+r))^L
     t  = thuế suất KỲ TRÍCH (Luật 67/2025/QH15 Đ17 k2: thu hồi theo thuế suất kỳ trích lập)
     Y5 = lãi TPKB kỳ hạn 5 năm, tính 2 năm (Luật 67 Đ17 k2; NĐ 320/2025 Đ22 k2) — mức Y5 = 3,0% là ƯỚC LƯỢNG (chưa đọc lợi suất phát hành)
     L  = số năm tới khi đồng tiền được giải phóng (thu hồi chậm nhất 5 năm sau trích, Đ17 k2); d = lãi tiền gửi DEP_NOW (tiền quỹ nằm trong
          net cash, model không ghi lãi tiền mặt ⇒ tiền quỹ tích lãi d trong L năm, chiết khấu r)
   Phần chi ≥70% cho thiết bị/KH&CN (NĐ 265/2025 Đ13 k5 điểm a, c) = V4a NPV=0 ⇒ KHÔNG kém hơn v (quy tắc dùng v là cận thận trọng).
   (a) SỐ DƯ: tiền quỹ = 1.059,37 (mã 344 Q3/26) − 27,74 (phần đã hình thành TSCĐ, không phải tiền; số 31/12/2025, TM25 KT 2025 — ước lượng cho 30/9)
       mất (1 − v(10%, L_stock, r)); L_stock bình quân theo lớp trích (FIFO, xem STOCK_VINTAGES).
   (b) DÒNG: hồi quy lại trên LN TRƯỚC trích quỹ (NP + A_y×(1−TH)); tương lai trích A = RATE_FWD × LNTT trước trích, LNST báo cáo trừ A×(1−t),
       cổ đông nhận lại A×v(t,5,r). A_y: 2024 44,78 / 2025 187,99 (TM25 BCTC HN KT 2025, png_r7/kt25_p37); 2016–23 không có BCTC gốc
       ⇒ A = RATE_HIST × LNTT ước tính (ước lượng; độ nhạy 0% / 10%).
   Tỷ lệ trích quan sát (A/(LNTT+A)): 2024 2,86% · 2025 7,85% · 2023 7,98% (KQKD KT 2025 p12 / KT 2024 p12: LNTT 1.522,06 / 2.207,43 / 1.254,81) · 9T/25 5,25% · 9T/26 8,88%
   (TM34 BCTC Q3/26 p40: 95,41 / 249,63; KQKD Q3/26 p08 LNTT 1.720,66 / 2.562,94). RATE_FWD = RATE_HIST = TB 3 năm KT 2023–25 = 6,23%.
"""
import sys, json
sys.path.insert(0, 'calc'); sys.path.insert(0, '../dd_redo_20261105/_shared')
import numpy as np
import model as m
import model_r2 as r2
import model_r6 as r6
import model_r7 as r7
import model_r8 as r8          # áp S1 (sửa dòng BQ 2021Q4) lên r7

TH = r7.TH
A_KT = {2023: 108.885894155, 2024: 44.783820092, 2025: 187.993343011}   # TM25 KT 2025 + TM KT 2024 (năm trước) "Trích quỹ trong năm"
LNTT_KT = {2023: 1254.809583640, 2024: 1522.063488191, 2025: 2207.434991467}   # KQKD KT 2025 / KT 2024 mã 50
DA_KT23 = 1083.380698652      # LCTT mã 02 KT 2024 cột năm trước (src/web/DCM_Baocaotaichinh_2024_Kiemtoan_Hopnhat.pdf p13; md5 14e9746f…) — thay BQ 1.063
RATE_OBS = {y: A_KT[y]/(LNTT_KT[y]+A_KT[y]) for y in A_KT}
RATE_OBS_9T = {'9T25': 95.414376495/(1720.663147114+95.414376495), '9T26': 249.634803105/(2562.940760461+249.634803105)}
RATE_BASE = sum(RATE_OBS.values())/len(RATE_OBS)
P = dict(on=True, da23=True, rate_fwd=RATE_BASE, rate_hist=RATE_BASE, y5=0.03, lag=True, flow=True, stock=True)
KHCN_TOTAL = r7.KHCN                                                     # 1.059,37 mã 344 Q3/26
KHCN_FA = 27.740801048                                                   # phần đã hình thành TSCĐ 31/12/2025 (TM25)
KHCN_CASH = KHCN_TOTAL - KHCN_FA
# lớp trích còn trong số dư 30/9/2026 (FIFO; năm còn lại tới hạn 5 năm tính từ giữa năm trích; lớp ≤2023 ước lượng 1,0 năm)
_old = KHCN_CASH - 249.634803105 - A_KT[2025] - A_KT[2024]
STOCK_VINTAGES = [(249.634803105, 4.75), (A_KT[2025], 3.75), (A_KT[2024], 2.75), (_old, 1.0)]
L_STOCK = sum(a*l for a, l in STOCK_VINTAGES)/KHCN_CASH
D_DEP = r6.DEP_NOW/100

def v_khcn(t, L, r):
    lam = ((1+D_DEP)/(1+r))**L if P['lag'] else 1.0
    return (1 - t*(1 + 2*P['y5']))*lam

def a_hist(y):
    if y in A_KT: return A_KT[y]
    lntt = m.np_[y]/(1-TH)                                               # LNTT sau trích (ước lượng từ LNST BQ)
    return P['rate_hist']/(1-P['rate_hist'])*lntt

def fit_bd9(years, da):
    xs = [m.proxy[y] for y in years]
    ys = [m.np_[y] + da[y]*(1-TH) + (a_hist(y)*(1-TH) if P['on'] and P['flow'] else 0.0) for y in years]
    mx, my = sum(xs)/len(xs), sum(ys)/len(ys)
    b = sum((x-mx)*(y-my) for x, y in zip(xs, ys))/sum((x-mx)**2 for x in xs)
    return my-b*mx, b

def da9():
    d = dict(r7.DA)
    if P['on'] and P['da23']: d[2023] = DA_KT23
    return d

def refit():
    r7.FITS_BD = {k: fit_bd9(v, da9()) for k, v in r6.CODE_REG.items()}

_orig_value = r2.value
def value9(s_lr, r=r2.R0, extra_pre_lr=0.0, extra_pre_y1=0.0, tax_y1=r2.TAX_Y1, tax_lr=r2.TAX_LR, k=r2.KTPL_RATE, nc_adj=-r2.KTPL_BAL,
           near=r2.NEAR, tail_pv=0.0):
    if P['on']:
        if P['flow']:
            a_lr = P['rate_fwd']*r2.pbt_at(s_lr); a_y1 = P['rate_fwd']*r2.pbt_at(near)
            extra_pre_lr += -a_lr + a_lr*v_khcn(tax_lr, 5, r)/(1-tax_lr)
            extra_pre_y1 += -a_y1 + a_y1*v_khcn(tax_y1, 5, r)/(1-tax_y1)
        if P['stock']:
            nc_adj += -(1 - v_khcn(0.10, L_STOCK, r))*KHCN_CASH
    return _orig_value(s_lr, r=r, extra_pre_lr=extra_pre_lr, extra_pre_y1=extra_pre_y1, tax_y1=tax_y1, tax_lr=tax_lr, k=k, nc_adj=nc_adj,
                       near=near, tail_pv=tail_pv)
r2.value = value9

def with_p(fn, **pk):
    old = dict(P); P.update(pk); refit()
    try: return fn()
    finally: P.clear(); P.update(old); refit()

def grid9(**kw): return r8.grid8(khcn=0.0, **kw)
def pt9(**kw): return sum(r7.pt7(M=M_, khcn=0.0, **kw) for M_ in r7.M_GRID)/3
refit()

if __name__ == '__main__':
    L, O = [], {}
    # 0. CONTROL: tắt T1, khcn 11% số dư ⇒ phải tái lập điểm rev8 26.776
    ctl = with_p(lambda: r8.pt8(), on=False)
    O['control_rev8_point'] = round(ctl, 3); L.append(f'0. CONTROL rev8 (T1 tắt, quỹ 11%): {ctl:,.3f} (rev8 báo 26.776)')
    O['inputs'] = dict(rate_obs={str(k): round(v, 4) for k, v in RATE_OBS.items()}, rate_obs_9t={k: round(v, 4) for k, v in RATE_OBS_9T.items()},
                       rate_base=round(RATE_BASE, 4), khcn_cash=round(KHCN_CASH, 2), stock_vintages=[(round(a, 1), l) for a, l in STOCK_VINTAGES],
                       L_stock=round(L_STOCK, 3), d=D_DEP, y5=P['y5'], v_stock_r135=round(v_khcn(0.10, L_STOCK, r7.R_NOW), 4),
                       v_flow20_r135=round(v_khcn(0.20, 5, r7.R_NOW), 4),
                       a_hist={str(y): round(a_hist(y), 1) for y in range(2016, 2026)}, da_used={str(y): round(v, 1) for y, v in da9().items()})
    L.append('1. Đầu vào T1: '+json.dumps(O['inputs'], ensure_ascii=False))
    reg = {k: dict(icpt=round(a, 1), slope=round(b, 3)) for k, (a, b) in r7.FITS_BD.items()}
    O['regressions'] = reg; L.append('   hồi quy trước trích: '+json.dumps(reg))
    base = pt9()
    br = dict(rev8_point=round(ctl),
              stock_only_lag=round(with_p(pt9, flow=False, da23=False)),
              stock_nolag_flow_off=round(with_p(pt9, flow=False, lag=False, da23=False)),
              stock_lag_da23=round(with_p(pt9, flow=False)),
              full_T1=round(base))
    O['bridge_point'] = br; L.append('2. Cầu nối điểm: '+json.dumps(br))
    G = {}
    G['H_headline'] = r7.summ_pre(*grid9())
    G['V_late_axis_050_025_025'] = r7.summ_pre(*grid9(late_axis=True))
    G['V_rev7_reading_100pct'] = with_p(lambda: r7.summ_pre(*r8.grid8(khcn=1.0)), on=False)
    G['V_rev8_hybrid'] = with_p(lambda: r7.summ_pre(*r8.grid8()), on=False)
    G['V_nolag'] = with_p(lambda: r7.summ_pre(*grid9()), lag=False)
    G['V_rate_2024'] = with_p(lambda: r7.summ_pre(*grid9()), rate_fwd=RATE_OBS[2024], rate_hist=RATE_OBS[2024])
    G['V_rate_9T26'] = with_p(lambda: r7.summ_pre(*grid9()), rate_fwd=RATE_OBS_9T['9T26'], rate_hist=RATE_OBS_9T['9T26'])
    G['V_4windows'] = r7.summ_pre(*grid9(regs=tuple(r6.CODE_REG)))
    G['V_M540'] = r7.summ_pre(*grid9(Ms=(540.0,))); G['V_M342'] = r7.summ_pre(*grid9(Ms=(r7.M_GRID[0],)))
    G['V_M738'] = r7.summ_pre(*grid9(Ms=(738.0,)))
    G['V_policy055'] = r7.summ_pre(*grid9(p_policy=r2.P_POLICY))
    O['grids'] = G
    for k, v in G.items(): L.append(f'4. {k}: '+json.dumps(v))
    def d(**kw): return round(pt9(**kw) - base)
    def dp(**pk): return round(with_p(pt9, **pk) - base)
    S = dict(base_point=round(base), dep_m100=d(r=m.rdep(r7.DEP_NOW-1)), dep_m50=d(r=m.rdep(r7.DEP_NOW-.5)), dep_p50=d(r=m.rdep(r7.DEP_NOW+.5)),
             dep_p100=d(r=m.rdep(r7.DEP_NOW+1)), beta05_p100=d(r=m.rdep(r7.DEP_NOW+1, .5)), Ke_123=d(r=0.123), Ke_134=d(r=0.134),
             late_flat=d(late='flat'), late_esc=d(late='esc'), life_2042=d(life_end=2042), life_2047=d(life_end=2047),
             policy055=d(p_policy=r2.P_POLICY), restricted=d(restricted=r2.RESTRICTED), w4=d(regs=tuple(r6.CODE_REG)),
             capex_per100=round(r7.pt7(M=r7.M_BASE+100, khcn=0.0)-r7.pt7(M=r7.M_BASE, khcn=0.0)),
             nolag=dp(lag=False), rate_2024=dp(rate_fwd=RATE_OBS[2024], rate_hist=RATE_OBS[2024]),
             rate_2025=dp(rate_fwd=RATE_OBS[2025], rate_hist=RATE_OBS[2025]),
             rate_9T26=dp(rate_fwd=RATE_OBS_9T['9T26'], rate_hist=RATE_OBS_9T['9T26']),
             rate_hist_0=dp(rate_hist=0.0), rate_hist_10=dp(rate_hist=0.10), rate_fwd_20cap=dp(rate_fwd=0.20),
             y5_0=dp(y5=0.0), y5_5=dp(y5=0.05), flow_off=dp(flow=False),
             da23_off=dp(da23=False), rate_2023=dp(rate_fwd=RATE_OBS[2023], rate_hist=RATE_OBS[2023]),
             rev7_reading=round(with_p(lambda: r8.pt8(khcn=1.0), on=False) - base))
    O['sens'] = S; L.append('5. Độ nhạy: '+json.dumps(S))
    print('\n'.join(L)); open('calc/model_r9_out.txt', 'w').write('\n'.join(L)+'\n')
    json.dump(O, open('calc/model_r9_out.json', 'w'), ensure_ascii=False, indent=1, sort_keys=True)
