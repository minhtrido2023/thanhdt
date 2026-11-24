"""MVC — do 2 hang muc tai THAM SO TRUNG TAM (truoc CK; % tam khong phu thuoc CK) bang chinh engine r3 (khong sua file):
 (1) Trich quy tu LNST theo NQ DHDCD 2026 (KTPL 7% + thu lao HDQT/BKS 2% + thuong BDH 2% = 11%; VI_BienBan...NghiQuyet.txt:767-785) — chua tru trong mo hinh
     (NETFIN chi tru TON quy KTPL 6,52). Can bao thu = 11% x (A Tan Lap + BOT + gach/xang + Q4) ; can cao = them phan NNC (stake). He so so huu cheo 1/(1-s*c).
 (2) Truyen dan tam dieu chinh NNC (dd_adjcenter_20261124/NNC/adj.json) qua V_NNC: bo hang muc #4 NNC (chan MVC trong NNC dung engine MVC r6 — MVC r3 tu giai so huu cheo bang engine da va).
Chay: wc_venv python -I calc_items.py <root>/agents/Taylor/research <worktree>"""
import sys, os, json, hashlib, subprocess
ROOT, WT = map(os.path.abspath, sys.argv[1:3]); CALC = os.path.join(ROOT, 'dd_redo_20261105', 'MVC', 'calc_r3')
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
NADJ = os.path.join(WT, 'agents/Taylor/research/dd_adjcenter_20261124/NNC/adj.json'); assert md5(NADJ) == '6beb796cbc592884c96d76f0e8c8efb7'
assert md5(os.path.join(CALC, 'mvc_redo_r3.py')) == '0059fa899507a05bf4e85f5edb81b089' and md5(os.path.join(CALC, 'assumptions_r3.json')) == '6c70fdcac7ca3d96577ebd1a4e1577bf'
NA = json.load(open(NADJ)); i4 = [i for i in NA['items'] if i['name'].startswith('Chân MVC')]; assert len(i4) == 1; i4 = i4[0]
# NNC dung chay lai to hop (sum_pct_combo) — lay tong to hop TRU dong gop tuyen tinh cua #4; dai: dai NNC tru cuc tri #4 cung chieu
m_n = (NA['sum_pct_combo'] - i4['contrib_pct']) / 100
m_n_lo = (NA['range_low'] / NA['center_base'] - 1) - min(p * m for p in (i4['p_low'], i4['p_high']) for m in i4['mag_range_pct']) / 100
m_n_hi = (NA['range_high'] / NA['center_base'] - 1) - max(p * m for p in (i4['p_low'], i4['p_high']) for m in i4['mag_range_pct']) / 100
CHILD = r'''
import sys, os, json, __main__
CALC = sys.argv[1]; os.chdir(CALC); sys.path.insert(0, os.path.abspath('../..'))
src = open('mvc_redo_r3.py').read(); assert src.count("if __name__ == '__main__':") == 1
src = src.replace("if __name__ == '__main__':", "if False:")
__main__.__file__ = os.path.join(CALC, 'mvc_redo_r3.py'); exec(compile(src, 'mvc_redo_r3.py', 'exec'), __main__.__dict__)
g = __main__.__dict__; V8 = g['V8']; CW = g['CW']; NOD = g['NODELAY']
c0 = g['EVc'](); acc = dict(A=0, BOT=0, gach_xang=0, Q4=0, stake=0, VM=0); vn = 0
for n in CW:
    b = g['branch'](n, NOD); vn += CW[n] * b['vn']
    for (k, p), r in b['res'].items():
        w = CW[n] * V8.W0[k] * V8.PW0[p]
        for key in acc: acc[key] += w * r[key]
mn = [float(x) for x in sys.argv[2:5]]
vfix = {f'{m:+.5f}': g['EVc']({'VN_fix': vn * (1 + m)}) for m in [0.0] + mn}
print(json.dumps(dict(c0=c0, vn=vn, acc=acc, vfix=vfix, s=g['V8'].S.s_NNC if hasattr(g['V8'].S, 's_NNC') else None)))
'''
p = subprocess.run([sys.executable, '-B', '-c', CHILD, CALC, str(m_n), str(m_n_lo), str(m_n_hi)], capture_output=True, text=True); assert p.returncode == 0, p.stderr[-3000:]
R = json.loads(p.stdout.strip().splitlines()[-1])
c0, acc, vf = R['c0'], R['acc'], R['vfix']
assert abs(c0 - 17704) < 1 and abs(acc['VM'] * 10 - c0) < 1e-6, (c0, acc['VM'])
assert abs(vf['+0.00000'] - c0) < 1.0, ('VN_fix tai vn trung tam phai = c0', vf['+0.00000'], c0)
s, c = 9.659170 / 21.92, 0.103; xh = 1 / (1 - s * c)
ops = acc['A'] + acc['BOT'] + acc['gach_xang'] + acc['Q4']
k_lo = -0.11 * ops * 10 * xh / c0; k_hi = -0.11 * (ops + acc['stake']) * 10 * xh / c0
NP9T = 231.767152211   # LNST cong ty me 9T/2026 HN (hn_q3.txt:621-628) — nam trong tien rong, se trich 11% nam 2027
k_9t = -0.11 * NP9T * 10 * xh / c0
d = {k: (v / c0 - 1) for k, v in vf.items()}
out = dict(c0_pre=round(c0, 1), vn_central=round(R['vn'], 1), parts_ty={k: round(v, 2) for k, v in acc.items()}, cross_hold_factor=round(xh, 5),
           fund11=dict(rate=0.11, basis='NQ DHDCD 2026 (VI_BienBanHopDaiHoiDongCoDongThuongNien2026VaNghiQuyet.txt:767-785): KTPL 7% + HDQT/BKS 2% + BDH 2%',
                       m_low_pct=round(100 * (k_hi + k_9t), 3), m_cons_pct=round(100 * k_lo, 3), m_9t26_pct=round(100 * k_9t, 3), cons_abs_pre=round(k_lo * c0, 1), note='m_cons = chi tren A+BOT+gach/xang+Q4; m_low = them phan NNC (stake) + 11% LNST 9T/26 HN (231,77 ty, gom lai LK)'),
           nnc_flow=dict(nnc_adj_md5='6beb796cbc592884c96d76f0e8c8efb7', m_nnc=round(m_n, 5), m_nnc_lo=round(m_n_lo, 5), m_nnc_hi=round(m_n_hi, 5),
                         d_mvc_pct={k: round(100 * v, 3) for k, v in d.items()}, excluded='NNC #4 (chan MVC trong NNC, engine r6) — khong ap cho MVC r3'))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'calc_items_out.json'), 'w'), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
