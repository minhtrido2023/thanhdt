"""DCM r8 (23/11/2026, job Taylor_20261122_234422, vòng sửa CUỐI) — áp verdict fundamental-skeptic r2 (INCONCLUSIVE, skeptic/r2.json) lên model_r7.
Dựng TRÊN model_r7.py (khoá trong LOCK_r7, KHÔNG sửa). Chạy từ dd_DCM_20261104/. MÙ GIÁ: không đọc giá; so giá ở calc/compare_px_r8.py sau LOCK_r8.

 S1 Dòng BQ 2021Q4 là bản chép 2021Q3 (EBITDA_P0/EBITM_P0 trùng hệt) ⇒ D&A 2021 = D&A TTM 2021Q3 (BQ) = 1.316,1 (skeptic r2 tự kiểm). Phát hiện tự động:
    quý 4 có EBITDA_P0 và EBITM_P0 trùng quý 3 ⇒ dùng quý 3.
 S2 Quỹ KH&CN: legal-vn 23/11 — Luật thuế TNDN 67/2025/QH15 Đ17 (hiệu lực 01/10/2025; khung cũ TT 67/2022): KHÔNG bắt buộc chi 100%;
    dùng <70% trong 5 năm/sai mục đích ⇒ nộp thuế TNDN THEO THUẾ SUẤT KỲ TRÍCH + lãi; được dùng mua máy móc thiết bị đổi mới công nghệ.
    ⇒ base trừ phần hoàn thuế: thuế suất kỳ trích = 10% (ưu đãi DCM tới hết 2026, BCTC Q3/26 tr.17) + lãi ≈ 1 điểm (ước lượng, trái phiếu KB 2 năm)
    = 11% số dư. Phần còn lại chi cho thiết bị/KH&CN ⇒ V4a NPV=0. Độ nhạy: 0% / 20% / 100% (cách đọc r7).
 S3 Khí 2035+: base GIỮ cấu trúc giá hợp đồng hiện hành (Đ9.1 HĐ 3918: PM3 = 50% quyền nhận PVN 46% MFO + 50% phần Malaysia 13,7% Brent, = cấu trúc
    năm 2028 đã cố định trong model_r5), nguồn PM3 tồn tại tới 2047 (PSC PM3-CAA gia hạn, src/gas/dl_1844450.txt:435). Khối lượng sau 24/4/2032 không
    cam kết ⇒ biến thể khai trọng số 0,5 hiện hành / 0,25 Nam Du phẳng 10,39 / 0,25 Nam Du leo thang (ước lượng, không có cơ sở chọn) chạy SONG SONG,
    mở rộng vùng đọc; KHÔNG vào tâm (cùng nguyên tắc thuế XK 5% = luật hiện hành ở r6).
 S4 VAT 5% từ 01/07/2025: kiểm năm có đủ chế độ VAT (TTM Q3/26) so với dự báo hồi quy tại biên proxy của chính kỳ đó — phần dư ≈ 0 ⇒ không có cơ sở
    cộng vào base (out mục 3).
"""
import sys, json, csv
sys.path.insert(0, 'calc'); sys.path.insert(0, '../dd_redo_20261105/_shared')
import numpy as np
import model as m
import model_r2 as r2
import model_r6 as r6
import model_r7 as r7
from wpct import wpct

# ---- S1: sửa dòng BQ chép ----
def _bq_da_fixed():
    rows = {r['quarter']: r for r in csv.DictReader(open('calc/bq_da_r7_out.csv'))}
    out, fixed = {}, []
    for q, r in rows.items():
        if not q.endswith('Q4') or not r['rev_ttm']: continue
        src = r; q3 = rows.get(q[:4]+'Q3')
        if q3 and q3['ebitda_ttm'] == r['ebitda_ttm'] and q3['ebitm_ttm_pct'] == r['ebitm_ttm_pct']:
            src = q3; fixed.append(q)
        out[int(q[:4])] = float(src['ebitda_ttm']) - float(src['ebitm_ttm_pct'])*float(src['rev_ttm'])
    return out, fixed
DA_BQ8, STALE = _bq_da_fixed()
r7.DA_BQ = DA_BQ8
r7.DA = r7.da_series()
r7.FITS_BD = {k: r7.fit_bd(v, r7.DA) for k, v in r6.CODE_REG.items()}
r7.FITS_BD_CAL = {k: r7.fit_bd(v, r7.da_series(True)) for k, v in r6.CODE_REG.items()}

# ---- S2 ----
KHCN_BASE = 0.11
# ---- S3 ----
LATE_W = (('base', 0.5), ('flat', 0.25), ('esc', 0.25))

def grid8(khcn=KHCN_BASE, late_axis=False, **kw):
    if not late_axis: return r7.grid7(khcn=khcn, **kw)
    vs, ws = [], []
    for mode, lw in LATE_W:
        r7_late = mode if mode != 'base' else None
        v, w = _grid_late(r7_late, khcn, **kw); vs.append(v); ws.append(w*lw)
    return np.concatenate(vs), np.concatenate(ws)

def _grid_late(late, khcn, **kw):
    import itertools
    regs = kw.get('regs', r7.HEAD_REGS); Ms = kw.get('Ms', r7.M_GRID)
    vals, ws = [], []
    for reg, r_, stc, nr, (gs, gw), I, M in itertools.product(regs, r6.RS, (138, None, 220), (170, 222, 285), r6.GAS_AB, (20.0, 22.0, 25.0), Ms):
        vals.append(r7.outcome7(reg, r_, stc, nr, gs, I, M, khcn, late=late)); ws.append(gw)
    w = np.array(ws); return np.array(vals), w/w.sum()

def pt8(**kw):
    kw.setdefault('khcn', KHCN_BASE)
    return sum(r7.pt7(M=M_, **kw) for M_ in r7.M_GRID)/3

if __name__ == '__main__':
    L, O = [], {}
    O['stale_fixed'] = STALE; O['da'] = {str(y): round(v, 1) for y, v in r7.DA.items()}
    L.append(f'1. S1 dòng BQ chép đã sửa: {STALE}; D&A dùng: '+json.dumps(O['da']))
    reg = {k: dict(bd_icpt=round(a, 1), bd_slope=round(b, 3), lnst179_M401=round(a-r7.M_BASE*(1-r7.TH)+b*m.spread_tc, 1),
                   resid_bd={y: round(m.np_[y]+r7.DA[y]*(1-r7.TH)-(a+b*m.proxy[y])) for y in r6.CODE_REG[k]}) for k, (a, b) in r7.FITS_BD.items()}
    O['regressions'] = reg
    for k, v in reg.items(): L.append(f'   {k}: '+json.dumps(v))
    # S4 kiểm VAT: TTM Q3/26 (Q4/25 + 9T/26, chế độ VAT 5% đủ 12 tháng) so với dự báo hồi quy tại biên proxy TTM
    np_ttm = 2282.089926625 + (m.np_[2025] - 1525.228572462)          # LNST mẹ TTM Q3/26 (BCTC Q3/26 + KT 2025 + 9T/25)
    da_ttm = r7.DA_9T26 + (r7.DA_KT[2025] - 246.045059287)             # D&A TTM Q3/26 (LCTT 9T/26 + KT 2025 − 9T/25)
    cm = m.cm; prox26 = m.proxy[2026]; prox25 = m.proxy[2025]
    prox_ttm = 0.75*prox26 + 0.25*prox25                                # (ước lượng) WB năm: 9T/26 ≈ năm 2026, Q4/25 ≈ năm 2025
    chk = {}
    for k in r7.HEAD_REGS:
        a, b = r7.FITS_BD[k]
        pred = a + b*prox_ttm - da_ttm*(1-r7.TH)
        chk[k] = dict(pred_np_ttm=round(pred, 1), actual_np_ttm=round(np_ttm, 1), resid=round(np_ttm-pred, 1), resid_pct=round(np_ttm/pred-1, 3))
    O['vat_check'] = dict(proxy_ttm=round(prox_ttm, 1), da_ttm=round(da_ttm, 1), **chk)
    L.append('3. S4 kiểm VAT 5% (TTM Q3/26): '+json.dumps(O['vat_check']))
    br = dict(r7_point=24809, s1_only=round(pt8(khcn=1.0)), s1_s2_point=round(pt8()))
    O['bridge_point'] = br; L.append('2. Cầu nối điểm: '+json.dumps(br))
    G = {}
    G['H_headline'] = r7.summ_pre(*grid8())
    G['V_late_axis_050_025_025'] = r7.summ_pre(*grid8(late_axis=True))
    G['V_khcn_0'] = r7.summ_pre(*grid8(khcn=0.0)); G['V_khcn_20'] = r7.summ_pre(*grid8(khcn=0.2)); G['V_khcn_100'] = r7.summ_pre(*grid8(khcn=1.0))
    G['V_4windows'] = r7.summ_pre(*grid8(regs=tuple(r6.CODE_REG)))
    G['V_M540'] = r7.summ_pre(*grid8(Ms=(540.0,))); G['V_M342'] = r7.summ_pre(*grid8(Ms=(r7.M_GRID[0],)))
    G['V_policy055'] = r7.summ_pre(*grid8(p_policy=r2.P_POLICY))
    O['grids'] = G
    for k, v in G.items(): L.append(f'4. {k}: '+json.dumps(v))
    base = pt8()
    def d(**kw): return round(pt8(**kw) - base)
    S = dict(base_point=round(base), dep_m100=d(r=m.rdep(r7.DEP_NOW-1)), dep_m50=d(r=m.rdep(r7.DEP_NOW-.5)), dep_p50=d(r=m.rdep(r7.DEP_NOW+.5)),
             dep_p100=d(r=m.rdep(r7.DEP_NOW+1)), beta05_p100=d(r=m.rdep(r7.DEP_NOW+1, .5)), Ke_123=d(r=0.123), Ke_134=d(r=0.134),
             late_flat=d(late='flat'), late_esc=d(late='esc'), life_2042=d(life_end=2042), life_2047=d(life_end=2047),
             khcn_0=d(khcn=0.0), khcn_20=d(khcn=0.2), khcn_100=d(khcn=1.0), policy055=d(p_policy=r2.P_POLICY), restricted=d(restricted=r2.RESTRICTED),
             w4=d(regs=tuple(r6.CODE_REG)), capex_per100=round(r7.pt7(M=r7.M_BASE+100, khcn=KHCN_BASE)-r7.pt7(M=r7.M_BASE, khcn=KHCN_BASE)))
    O['sens'] = S; L.append('5. Độ nhạy: '+json.dumps(S))
    print('\n'.join(L)); open('calc/model_r8_out.txt', 'w').write('\n'.join(L)+'\n')
    json.dump(O, open('calc/model_r8_out.json', 'w'), ensure_ascii=False, indent=1, sort_keys=True)
